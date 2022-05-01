import pandas as pd
from config import *
from utils import *
import numpy as np
from nlp import singular_phrase
from models import Model
import json
from openpyxl import load_workbook

class Bid:
    def __init__(self):
        self.bulk_pd = pd.read_excel(bulk_file,sheet_name='Sponsored Products Campaigns')
        self.searchterm_info = read_obj_local(searchterm_info_pickle_path)
        self.sku_data = read_obj_local(skudata_info_pickle_path)
        self.model = Model()
        self.model.ctr_co_curvefit()
        self.model.impression_co_curvefit()
        self.model.bid_price_curvefit()

    def get_acos_targeting(self):
        acos_targeting_pd = pd.read_csv(acos_targeting_file)
        for _, row in acos_targeting_pd.iterrows():
            sku, aocs, price = row['sku'], row['target_acos'], row['price']
            if sku not in self.sku_data:
                print('%s not in sku data' % (sku))
                continue
            self.sku_data[sku]['target_acos'] = aocs
            self.sku_data[sku]['price'] = price
    
    def set_bid_price(self):
        cur_sku, cur_sku_index, bid_result = [], [], []
        for idx, row in self.bulk_pd.iterrows():
            record_type = row['Record Type']
            if record_type == 'Ad':
                sku = row['SKU']
                if len(cur_sku_index) > 0 and cur_sku_index[-1] + 1 != idx:
                    cur_sku.clear()
                    cur_sku_index.clear()
                cur_sku.append(sku)
                cur_sku_index.append(idx)
            elif record_type not in ['Keyword', 'Product Targeting']: continue
            else:
                campaign_status, ad_group_status, target_status = row['Campaign Status'], row['Ad Group Status'], row['Status']
                if campaign_status == 'paused' or ad_group_status == 'paused' or target_status == 'paused': continue
                match_type = row['Match Type']
                if match_type in ['campaign negative exact', 'negative exact', 'Negative Targeting Expression']: continue
                basic_price = None
                target_parse = row['Keyword or Product Targeting']
                if record_type == 'Keyword':
                    target_parse = singular_phrase(target_parse)
                sku_units = len(cur_sku)
                sku_found = sku_units
                basic_price_co = 1 / sku_units
                basic_price = basic_price_default
                impression, click, order = 0, 0, 0
                for sku in cur_sku:
                    cur_impression, cur_click, cur_order = 0, 0, 0
                    if target_parse in self.searchterm_info[sku]['targetings'] and self.searchterm_info[sku]['targetings'][target_parse]['clicks'] > targeting_min_click:
                        cur_impression = self.searchterm_info[sku]['targetings'][target_parse]['impressions']
                        cur_click = self.searchterm_info[sku]['targetings'][target_parse]['clicks']
                        cur_order = self.searchterm_info[sku]['targetings'][target_parse]['orders']
                    elif target_parse in self.searchterm_info[sku]['searchterms'] and self.searchterm_info[sku]['searchterms'][target_parse]['clicks'] > min_click:
                        cur_impression = self.searchterm_info[sku]['searchterms'][target_parse]['impressions']
                        cur_click = self.searchterm_info[sku]['searchterms'][target_parse]['clicks']
                        cur_order = self.searchterm_info[sku]['searchterms'][target_parse]['orders']
                    else:
                        sku_found -= 1
                    impression += basic_price_co * cur_impression
                    click += basic_price_co * cur_click
                    order += basic_price_co * cur_order

                ads_spends_sku, impression_sku, click_sku, order_sku = 0, 0, 0, 0
                for sku in cur_sku:
                    ads_spends_sku += self.sku_data[sku]['price'] * self.sku_data[sku]['target_acos']
                    impression_sku += self.sku_data[sku]['impressions']
                    click_sku += self.sku_data[sku]['clicks']
                    order_sku += self.sku_data[sku]['orders']
                if sku_found / sku_units >= 0.5:
                    impression_sku, click_sku, order_sku = impression, click, order
                basic_price_predict = (ads_spends_sku / sku_units) * (order_sku / click_sku)
                basic_price = max(basic_price, basic_price_predict)

                impression_cur = row['Impressions']
                click_cur = row['Clicks']
                order_cur = row['Orders']
                avg_ctr = click_sku / impression_sku
                cur_ctr = click_cur / impression_cur
                ctr_predict_co = self.model.ctr_predict_model(cur_ctr / avg_ctr)

                impression_sku_isolated_sum, impression_sku_isolated_len = 0, 0
                for sku in cur_sku:
                    impression_sku_isolated_sum += self.sku_data[sku]['impression_statistic']['isolation_removed_sum']
                    impression_sku_isolated_len += self.sku_data[sku]['impression_statistic']['isolation_removed_len']
                impression_sku_isolated_mean = impression_sku_isolated_sum / impression_sku_isolated_len
                impression_predict_co = self.model.impression_predict_model(impression_cur / impression_sku_isolated_mean)

                bid_price_predict = basic_price * ctr_predict_co * impression_predict_co
                bid_price = self.model.bid_price_model(bid_price_predict)
                if match_type == 'broad': bid_price * broad_co
                elif match_type == 'exact': bid_price * exact_co
                bid_price = bid_price if bid_price > minimum_bid_price else minimum_bid_price
                self.bulk_pd.at[idx, 'Max Bid'] = bid_price
                bid_result.append([row['Campaign'], row['Ad Group'], row['Keyword or Product Targeting'], self.sku_data[cur_sku[0]]['price'], self.sku_data[cur_sku[0]]['target_acos'], impression_cur, click_cur, order_cur, order_cur/click_cur if click_cur > 0 else 0, basic_price_predict, basic_price, avg_ctr, cur_ctr, ctr_predict_co, impression_cur, impression_sku_isolated_mean, impression_predict_co, bid_price_predict, bid_price])
        list_to_csv(bid_result, target_bid_file, ['Campaign', 'Ad Group', 'Keyword or Product Targeting', 'Price', 'Target ACOS', 'Impression', 'Click', 'Order', 'CVR', 'Basic Price Predict', 'Basic Price', 'Average CTR', 'CTR', 'CTR Co', 'Impression Cur', 'Impression Average', 'Impression Co', 'Bid Price Predict', 'Bid Price'])

    def write_to_bulkfile(self):
        book = load_workbook(bulk_file)
        writer = pd.ExcelWriter(bulk_file, engine='openpyxl')  # 使用openpyxl引擎的写表器
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)  
        self.bulk_pd.to_excel(writer, sheet_name='Sponsored Products Campaigns', startrow=1, index=False, header=None)
        writer.save()
        writer.close()

    def print_sku_data(self):
        for sku, data in self.sku_data.items():
            print(sku)
            for k, v in data.items():
                print(k, np.min(v), np.median(v), np.max(v))
            print('------------------------------------------------')


if __name__ == "__main__":
    b = Bid()
    b.get_acos_targeting()
    # print(b.sku_data['balloon-macaron']['impression_statistic']['isolation_removed_mean'], b.sku_data['balloon-macaron']['impression_statistic']['isolation_removed_len'])
    # quit()
    b.set_bid_price()
    b.write_to_bulkfile()