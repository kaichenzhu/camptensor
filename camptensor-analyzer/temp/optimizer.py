import pandas as pd
from openpyxl import load_workbook
from config import *
from utils import *
from queue import PriorityQueue
import numpy as np
import os, sys
from nlp import singular_phrase
from models import *
import csv
class Optimizer:
    def __init__(self):
        self.searchterm_pd = pd.read_excel(searchterm_file)
        self.portfolio = pd.read_excel(bulk_file,sheet_name='Portfolios')
        self.bulk_pd = pd.read_excel(bulk_file,sheet_name='Sponsored Products Campaigns')
        self.template = pd.read_excel(template_file, sheet_name='Sponsored Products Campaigns')
        self.idx, _ = self.template.shape
        self.portfolio_info = {}
        self.port_camp_map = {}
        self.sku_camp_group_map = {}
        self.category_id_map = {}
        self.searchterm_info = {}
        self.campaign_info = {}
        self.campaign_queue = {}
        self.sku_data = {}
        self.disable_tg = []
        self.negative_st = []
        self.optimize_st = []
        self.model = Model()
        self.model.cls_impression_curvefit()

    def extract_portfolio_info(self):
        portfolio_info = self.portfolio[['Record ID', 'Portfolio Name']].drop_duplicates()
        for _, row in portfolio_info.iterrows():
            portfolio_id = row['Record ID']
            portfolio_name = row['Portfolio Name']
            if portfolio_id not in self.portfolio_info:
                self.portfolio_info[portfolio_id] = portfolio_name
                self.port_camp_map[portfolio_name] = {}
    
    def extract_campaign_info(self):
        current_campaign, current_group = {}, {}
        for _, row in self.bulk_pd.iterrows():
            record_type = row['Record Type']
            campaign_name = row['Campaign']
            if record_type == 'Campaign':
                if pd.isna(row['Portfolio ID']):
                    print("%s didn't bind to any portfolio" % (campaign_name))
                    portfolio_id, portfolio_name = None, None
                else:
                    portfolio_id = int(row['Portfolio ID'])
                    portfolio_name = self.portfolio_info[portfolio_id]
                    self.port_camp_map[portfolio_name] = campaign_name
                current_campaign = {
                    'name': campaign_name,
                    'id': row['Campaign ID'],
                    'portfolio_id': portfolio_id,
                    'portfolio_name': portfolio_name,
                    'type': row['Campaign Targeting Type'],
                    'daily budget': row['Campaign Daily Budget'],
                    'impressions': row['Impressions'],
                    'clicks': row['Clicks'],
                    'orders': row['Orders'],
                    'spend': row['Spend'],
                    'salse': row['Sales'],
                    'acos': row['ACoS'],
                    'bidding strategy': row['Bidding strategy'],
                    'status': row['Campaign Status'],
                    'groups': {}
                }
                self.campaign_info[campaign_name] = current_campaign
            elif record_type == 'Ad Group':
                group_name = row['Ad Group']
                current_group = {
                    'name': group_name,
                    'status': row['Ad Group Status'],
                    'max bid': row['Max Bid'],
                    'type': None,
                    'ads': {}
                }
                current_campaign['groups'][group_name] = current_group
            elif record_type == 'Ad':
                sku = row['SKU']
                ad = {
                    'sku': sku,
                    'status': row['Status']
                }
                current_group['ads'][sku] = ad
                if sku not in self.sku_camp_group_map:
                    self.sku_camp_group_map[sku] = []
                self.sku_camp_group_map[sku].append([current_campaign, current_group])
            elif record_type == 'Product Targeting' or record_type == 'Keyword':
                if not current_group['type']:     # 如果当前广告组还未确定类型
                    campaign_type = current_campaign['type']
                    current_group['type'] = campaign_type if campaign_type == 'Auto' else record_type
                if record_type == 'Product Targeting' and len(row['Keyword or Product Targeting']) > 9 and row['Keyword or Product Targeting'][:9] == 'category=':
                    category = row['Keyword or Product Targeting'][10:-1]
                    self.category_id_map[category] = row['Product Targeting ID'][10:-1]
                    

    def build_campaign_queue(self):
        for sku, groups in self.sku_camp_group_map.items():
            keyword_q = PriorityQueue()
            asin_q = PriorityQueue()
            self.campaign_queue[sku] = {
                'keyword': keyword_q,
                'asin': asin_q
            }
            for group_info in groups:
                campaign, group = group_info
                if campaign['status'] == 'enabled' and group['status'] == 'enabled' and campaign['type'] == 'Manual':
                    impressions = campaign['impressions']
                    group_type = group['type']
                    if group_type == 'Keyword':
                        keyword_q.put((impressions, [campaign['name'], group['name']]))
                    elif group_type == 'Product Targeting':
                        asin_q.put((impressions, [campaign['name'], group['name']]))
    
    def load_data_from_st(self):
        current_campaign, current_group, current_targeting, current_matchtype = None, None, None, None
        for _, row in self.searchterm_pd.iterrows():
            portfolio_name = row['Portfolio name']
            campaign_name = row['Campaign Name']
            if campaign_name not in self.campaign_info:
                print('campaign: %s is paused' % (campaign_name))
                continue
            group_name = row['Ad Group Name']
            match_type = row['Match Type']
            targeting = row['Targeting']
            searchterm = row['Customer Search Term']
            impressions = row['Impressions']
            clicks = row['Clicks']
            orders = row['7 Day Total Orders (#)']
            spends = row['Spend']
            sales = row['7 Day Total Sales ']
            campaign_type = self.campaign_info[campaign_name]['type']
            searchterm_type = 'Product Targeting' if self.isasin(searchterm) else 'Keyword'
            targeting_type = self.get_targeting_type(targeting, campaign_type)
            searchterm_processed = singular_phrase(searchterm) if searchterm_type == 'Keyword' else searchterm
            targeting_processed = singular_phrase(targeting) if targeting_type == 'Keyword' else targeting
            if group_name not in self.campaign_info[campaign_name]['groups']:
                print('campaign-group: %s -- %s is paused' % (campaign_name, group_name))
                continue
            ads = self.campaign_info[campaign_name]['groups'][group_name]['ads']
            for sku in ads.keys():
                if sku not in self.searchterm_info:
                    self.searchterm_info[sku] = {
                        'targetings':{},
                        'searchterms':{}
                    }
                if searchterm_processed not in self.searchterm_info[sku]['searchterms']:
                    self.searchterm_info[sku]['searchterms'][searchterm_processed] = {
                        'name': searchterm_processed,
                        'impressions': 0,
                        'clicks': 0,
                        'orders': 0,
                        'spends': 0,
                        'sales': 0,
                        'searchterm_type': searchterm_type,
                        'searchterm_list': []
                    }
                searchterm_grouped = self.searchterm_info[sku]['searchterms'][searchterm_processed]
                searchterm_grouped['impressions'] += impressions
                searchterm_grouped['clicks'] += clicks
                searchterm_grouped['orders'] += orders
                searchterm_grouped['spends'] += spends
                searchterm_grouped['sales'] += sales
                searchterm_obj = {
                    'portfolio_name': portfolio_name,
                    'campaign_name': campaign_name,
                    'campaign_type': campaign_type,
                    'group_name': group_name,
                    'searchterm': searchterm,
                    'searchterm_type': searchterm_type,
                    'impressions': impressions,
                    'clicks': clicks,
                    'orders': orders,
                    'spends': spends,
                    'sales': sales
                }
                searchterm_grouped['searchterm_list'].append(searchterm_obj)

                if targeting_processed not in self.searchterm_info[sku]['targetings']:
                    self.searchterm_info[sku]['targetings'][targeting_processed] = {
                        'name': targeting_processed,
                        'impressions': 0,
                        'clicks': 0,
                        'orders': 0,
                        'spends': 0,
                        'sales': 0,
                        'targeting_list': []
                    }
                targeting_grouped = self.searchterm_info[sku]['targetings'][targeting_processed]
                targeting_grouped['impressions'] += impressions
                targeting_grouped['clicks'] += clicks
                targeting_grouped['orders'] += orders
                targeting_grouped['spends'] += spends
                targeting_grouped['sales'] += sales
                if match_type != current_matchtype or targeting != current_targeting or group_name != current_group or campaign_name != current_campaign:
                    targeting_obj = {
                        'portfolio_name': portfolio_name,
                        'campaign_name': campaign_name,
                        'campaign_type': campaign_type,
                        'group_name': group_name,
                        'targeting': targeting,
                        'match_type': match_type,
                        'targeting_type': targeting_type,
                        'impressions': 0,
                        'clicks': 0,
                        'orders': 0,
                        'spends': 0,
                        'sales': 0
                    }
                    targeting_grouped['targeting_list'].append(targeting_obj)
                targeting_grouped['targeting_list'][-1]['impressions'] += impressions
                targeting_grouped['targeting_list'][-1]['clicks'] += clicks
                targeting_grouped['targeting_list'][-1]['orders'] += orders
                targeting_grouped['targeting_list'][-1]['spends'] += spends
                targeting_grouped['targeting_list'][-1]['sales'] += sales
            current_campaign, current_group, current_targeting, current_matchtype = campaign_name, group_name, targeting, match_type
        write_obj_local(searchterm_info_pickle_path, self.searchterm_info)

    def word_classification(self):
        for sku, info in self.searchterm_info.items():
            # pause targting with bad performance
            impression_avg = self.sku_data[sku]['impression_statistic']['isolation_removed_mean']
            targetings = info['targetings']
            for _, targeting_grouped in targetings.items():
                clicks = targeting_grouped['clicks']
                if clicks < min_click: continue
                orders = targeting_grouped['orders']
                impressions = targeting_grouped['impressions']
                cvr = orders / clicks
                cvr = self.model.cls_impression_co_model(impressions / impression_avg) * cvr
                if cvr < min_cvr:
                    for target in targeting_grouped['targeting_list']:
                        self.disable_tg.append([sku, target['campaign_name'], target['group_name'], target['targeting'], target['match_type'], target['targeting_type'], impressions, clicks, orders, cvr])

            searchterms = info['searchterms']
            for _, searchterm_grouped in searchterms.items():
                clicks = searchterm_grouped['clicks']
                if clicks < min_click: continue
                name = searchterm_grouped['name']
                orders = searchterm_grouped['orders']
                impressions = searchterm_grouped['impressions']
                searchterm_type = searchterm_grouped['searchterm_type']
                cvr = orders / clicks
                cvr = self.model.cls_impression_co_model(impressions / impression_avg) * cvr
                if cvr < min_cvr:
                    for st in searchterm_grouped['searchterm_list']:
                        self.negative_st.append([sku, st['campaign_name'], st['group_name'], st['searchterm'], st['searchterm_type'], impressions, clicks, orders, cvr])
                elif cvr > max_cvr:
                    if name in targetings:
                        for target in targetings[name]['targeting_list']:
                            self.optimize_st.append([sku, target['campaign_name'], target['group_name'], target['targeting'], target['match_type'], target['targeting_type'], 'launched', impressions, clicks, orders, cvr])
                    else:
                        self.optimize_st.append([sku, None, None, name, None, searchterm_type, 'ready to launch', impressions, clicks, orders, cvr])

    def analyse_result_to_local(self):
        list_to_csv(self.disable_tg, disable_tg_file, ['sku', 'campaign_name', 'group_name', 'targeting', 'match_type', 'targeting_type', 'impressions', 'clicks', 'orders', 'cvr'])
        list_to_csv(self.negative_st, negative_st_file, ['sku', 'campaign_name', 'group_name', 'searchterm', 'searchterm_type', 'impressions', 'clicks', 'orders', 'cvr'])
        list_to_csv(self.optimize_st, optimize_st_file, ['sku', 'campaign_name', 'group_name', 'targeting', 'match_type', 'searchterm_type', 'status', 'impressions', 'clicks', 'orders', 'cvr'])

    def disable_targeting(self):
        for target in self.disable_tg:
            sku, campaign, adgroup, targeting, match_type, targeting_type, impressions, clicks, orders, cvr = target
            if targeting_type == 'Auto': continue
            self.template.at[self.idx, 'Record Type'] = targeting_type
            self.template.at[self.idx, 'Campaign'] = campaign
            self.template.at[self.idx, 'Ad Group'] = adgroup
            if targeting_type == 'Product Targeting':
                if len(targeting) > 9 and targeting[:9] == 'category=':
                    self.template.at[self.idx, 'Product Targeting ID'] = 'category="%s"' % (self.category_id_map[targeting[10:-1]])
                elif len(targeting) > 5 and targeting[:5] == 'asin=':
                    self.template.at[self.idx, 'Product Targeting ID'] = targeting
                else:
                    print('error targeting at 269')
            self.template.at[self.idx, 'Keyword or Product Targeting'] = targeting
            self.template.at[self.idx, 'Match Type'] = match_type if targeting_type == 'Keyword' else 'Targeting Expression'
            self.template.at[self.idx, 'Status'] = 'paused'
            self.idx += 1
    
    def negative_searchterm(self):
        for st in self.negative_st:
            sku, campaign, adgroup, searchterm, searchterm_type, impressions, clicks, orders, cvr = st
            self.template.at[self.idx, 'Record Type'] = searchterm_type
            self.template.at[self.idx, 'Campaign'] = campaign
            self.template.at[self.idx, 'Ad Group'] = adgroup
            if searchterm_type == 'Product Targeting':
                searchterm = 'asin="%s"' % searchterm
                self.template.at[self.idx, 'Product Targeting ID'] = searchterm
            self.template.at[self.idx, 'Keyword or Product Targeting'] = searchterm
            self.template.at[self.idx, 'Match Type'] = 'negative exact' if searchterm_type == 'Keyword' else 'Negative Targeting Expression'
            self.template.at[self.idx, 'Status'] = 'enabled'
            self.idx += 1

    def optimize_searchterm(self):
        optimize_pd = pd.read_csv(optimize_st_file)
        for _, row in optimize_pd.iterrows():
            status = row['status']
            if status == 'launched': continue
            sku = row['sku']
            impressions = row['impressions']
            searchterm_type = row['searchterm_type']
            targeting = row['targeting']
            campaign_name, group_name = None, None
            if pd.isna(row['campaign_name']):
                if searchterm_type == 'Keyword':
                    q = self.campaign_queue[sku]['keyword']
                    if q.empty():
                        print('No manual keyword campaign for sku: %s' % (sku))
                        continue
                    weight, target_campaign_group = q.get()
                    campaign_name, group_name = target_campaign_group
                    self.campaign_queue[sku]['keyword'].put((weight+impressions, target_campaign_group))
                elif searchterm_type == 'Product Targeting':
                    q = self.campaign_queue[sku]['asin']
                    if q.empty():
                        print('No manual asin campaign for sku: %s' % (sku))
                        continue
                    weight, target_campaign_group = q.get()
                    campaign_name, group_name = target_campaign_group
                    self.campaign_queue[sku]['asin'].put((weight+impressions, target_campaign_group))
            else:
                campaign_name, group_name = row['campaign_name'], row['group_name']
            for match_type in ['exact', 'phrase', 'broad']:
                self.template.at[self.idx, 'Record Type'] = searchterm_type
                self.template.at[self.idx, 'Campaign'] = campaign_name
                self.template.at[self.idx, 'Ad Group'] = group_name
                if searchterm_type == 'Product Targeting':
                    targeting = 'asin="%s"' % targeting
                    self.template.at[self.idx, 'Product Targeting ID'] = targeting
                    self.template.at[self.idx, 'Keyword or Product Targeting'] = targeting
                    self.template.at[self.idx, 'Match Type'] = 'Targeting Expression'
                    self.template.at[self.idx, 'Status'] = 'enabled'
                    self.idx += 1
                    break
                self.template.at[self.idx, 'Keyword or Product Targeting'] = targeting
                self.template.at[self.idx, 'Match Type'] = match_type
                self.template.at[self.idx, 'Status'] = 'enabled'
                self.idx += 1

    def sku_statistic(self):
        for sku, st_info in self.searchterm_info.items():
            impression_list, click_list, order_list, spend_list, sale_list = [], [], [], [], []
            for _, tg in st_info['targetings'].items():
                impression_list.append(tg['impressions'])
                click_list.append(tg['clicks'])
                order_list.append(tg['orders'])
                spend_list.append(tg['spends'])
                sale_list.append(tg['sales'])
            self.sku_data[sku] = {
                'impressions_list': np.array(impression_list),
                'clicks_list': np.array(click_list),
                'orders_list': np.array(order_list),
                'spends_list': np.array(spend_list),
                'sales_list': np.array(sale_list)+0.001,
            }
            self.sku_data[sku]['ctr_list'] = np.divide(self.sku_data[sku]['clicks_list'], self.sku_data[sku]['impressions_list'])
            self.sku_data[sku]['cvr_list'] = np.divide(self.sku_data[sku]['orders_list'], self.sku_data[sku]['clicks_list'])
            self.sku_data[sku]['acos_list'] = np.divide(self.sku_data[sku]['spends_list'], self.sku_data[sku]['sales_list'])
            self.sku_data[sku]['cpc_list'] = np.divide(self.sku_data[sku]['spends_list'], self.sku_data[sku]['clicks_list'])

            self.sku_data[sku]['impressions'] = self.sku_data[sku]['impressions_list'].sum()
            self.sku_data[sku]['clicks'] = self.sku_data[sku]['clicks_list'].sum()
            self.sku_data[sku]['orders'] = self.sku_data[sku]['orders_list'].sum()
            self.sku_data[sku]['spends'] = self.sku_data[sku]['spends_list'].sum()
            self.sku_data[sku]['sales'] = self.sku_data[sku]['sales_list'].sum()
            self.sku_data[sku]['ctr'] = self.sku_data[sku]['clicks'] / self.sku_data[sku]['impressions']
            self.sku_data[sku]['cvr'] = self.sku_data[sku]['orders'] / self.sku_data[sku]['clicks']
            self.sku_data[sku]['acos'] = self.sku_data[sku]['spends'] / self.sku_data[sku]['sales']
            self.sku_data[sku]['cpc'] = self.sku_data[sku]['spends'] / self.sku_data[sku]['orders']

            impression_isolation_removed = self.model.remove_isolation(self.sku_data[sku]['impressions_list'])
            self.sku_data[sku]['impression_statistic'] = {
                'isolation_removed_list': impression_isolation_removed[0],
                'isolation_removed_sum': impression_isolation_removed[1],
                'isolation_removed_len': impression_isolation_removed[2],
                'isolation_removed_mean': impression_isolation_removed[3],
            }
        write_obj_local(skudata_info_pickle_path, self.sku_data)
        
    
    def write_to_template(self):
        book = load_workbook(template_file)
        writer = pd.ExcelWriter(template_file, engine='openpyxl')  # 使用openpyxl引擎的写表器
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)  
        self.template.to_excel(writer, sheet_name='Sponsored Products Campaigns', startrow=1, index=False, header=None)
        writer.save()
        writer.close()

    def sku_data_write_local(self):
        pass


    def isasin(self, value):
        if len(value) == 10:
            if value[:2] == 'b0': return True
            if value.isdigit(): return True
        return False
    
    def get_targeting_type(self, targeting, campaign_type):
        if campaign_type == 'Auto': return campaign_type
        if len(targeting) >5 and targeting[:5] == 'asin=': return 'Product Targeting'
        if len(targeting) > 9 and targeting[:9] == 'category=': return 'Product Targeting'
        return 'Keyword'

    def load_data(self):
        self.extract_portfolio_info()
        self.extract_campaign_info()
        self.build_campaign_queue()
        self.load_data_from_st()
        self.sku_statistic()

    def analyse(self):
        self.load_data()
        self.word_classification()
        self.analyse_result_to_local()

    def generate_template(self):
        self.disable_targeting()
        self.negative_searchterm()
        self.optimize_searchterm()
        self.write_to_template()

if __name__ == "__main__":
    o = Optimizer()
    o.analyse()
    o.generate_template()
