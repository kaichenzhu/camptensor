import os
import json
import argparse
import csv
from posixpath import join
from db import *
from datetime import datetime, timedelta
from pytz import utc, timezone
from weights import *

def sku_ponint_ctr(x):
    a, b, c, d, m = WORD_POINT_CTR
    return d + (a-d) / (1+(x/c)**b)**m

def sku_ponint_cvr(x):
    a, b, c, d, m = WORD_POINT_CVR
    return d + (a-d) / (1+(x/c)**b)**m

def sku_ponint_acos(x):
    a, b, c, d, m = WORD_POINT_ACOS
    return d + (a-d) / (1+(x/c)**b)**m

def sku_stock_co(x):
    a, b, c, d, m = SKU_STOCK_CO
    return d + (a-d) / (1+(x/c)**b)**m

def get_recent_days(start):
    today = datetime.now(tz=utc)
    res = [ today.astimezone(timezone('US/Pacific')).strftime('%Y%m%d') ]
    if datetime.strptime(start, "%Y%m%d") > datetime.strptime(res[0], "%Y%m%d"):
        return start, False
    i = 1
    while res[-1] != start:
        day = today - timedelta(days=i)
        res.append(day.astimezone(timezone('US/Pacific')).strftime('%Y%m%d'))
        i += 1
    return res, True

def write_obj_arr_to_json(d, path):
    with open(path, "w") as f:
        wr = csv.DictWriter(f,fieldnames=list(d[0].keys()))
        wr.writeheader()
        wr.writerows(d)

def write_obj_to_json(d, path):
    with open(path, "w") as outfile:
        json.dump(d, outfile)

def read_csv(file):
    a = []
    with open(file) as f:
        a = list(csv.DictReader(f))
    return a

def get_date(start, end, data_path):
    files=os.listdir(data_path)
    files = [x for x in files if len(x) == 8 and x.isdigit()]
    files.sort()
    dates, collected = [], False
    for x in files:
        if x == start: collected = True
        if collected: dates.append(os.path.join(data_path, x))
        if x == end: collected = False
    return dates

def calculate_data(data):
    for campaign in data:
        impressions, clicks, orders, cost, sales = campaign['impressions'], campaign['clicks'], campaign['attributedUnitsOrdered7d'], campaign['cost'], campaign['attributedSales7d']
        campaign['ctr'] = clicks / impressions if impressions > 0 else 0
        campaign['cvr'] = orders / clicks if clicks > 0 else 0
        campaign['acos'] = cost / sales if sales > 0 else 0

    grouped = {
        "attributedSales7d": 0,
        "cost": 0,
        "attributedUnitsOrdered7d": 0,
        "attributedSales7dSameSKU": 0,
        "campaignId": 000000000000000,
        "impressions": 0,
        "attributedConversions7d": 0,
        "campaignBudget": 0,
        "campaignStatus": "enabled",
        "clicks": 0,
        "attributedConversions7dSameSKU": 0,
        "attributedUnitsOrdered7dSameSKU": 0,
        "campaignName": "汇总"
    }

    for campaign in data:
        grouped['attributedSales7d'] += campaign['attributedSales7d']
        grouped['cost'] += campaign['cost']
        grouped['attributedUnitsOrdered7d'] += campaign['attributedUnitsOrdered7d']
        grouped['attributedSales7dSameSKU'] += campaign['attributedSales7dSameSKU']
        grouped['impressions'] += campaign['impressions']
        grouped['attributedConversions7d'] += campaign['attributedConversions7d']
        grouped['clicks'] += campaign['clicks']
        grouped['attributedConversions7dSameSKU'] += campaign['attributedConversions7dSameSKU']
        grouped['attributedUnitsOrdered7dSameSKU'] += campaign['attributedUnitsOrdered7dSameSKU']
    
    impressions, clicks, orders, cost, sales = grouped['impressions'], grouped['clicks'], grouped['attributedUnitsOrdered7d'], grouped['cost'], grouped['attributedSales7d']
    grouped['ctr'] = clicks / impressions if impressions > 0 else 0
    grouped['cvr'] = orders / clicks if clicks > 0 else 0
    grouped['acos'] = cost / sales if sales > 0 else 0
    data.append(grouped)
    return data

def get_sku_statistic(start, end, data_path):
    dates = get_date(start, end, data_path)
    res1, res2 = {}, {}
    for date in dates:
        campaigns = json.load(open(os.path.join(date, 'campaign.json')))
        for campaign in campaigns:
            name = campaign['campaignName']
            id = campaign['campaignId']
            target_group = res1 if '|KEYWORD|' in name or '|ASIN|' in name else res2
            if id not in target_group: target_group[id] = campaign
            else:
                target_group[id]['attributedSales7d'] += campaign['attributedSales7d']
                target_group[id]['cost'] += campaign['cost']
                target_group[id]['attributedUnitsOrdered7d'] += campaign['attributedUnitsOrdered7d']
                target_group[id]['attributedSales7dSameSKU'] += campaign['attributedSales7dSameSKU']
                target_group[id]['impressions'] += campaign['impressions']
                target_group[id]['attributedConversions7d'] += campaign['attributedConversions7d']
                target_group[id]['clicks'] += campaign['clicks']
                target_group[id]['attributedConversions7dSameSKU'] += campaign['attributedConversions7dSameSKU']
                target_group[id]['attributedUnitsOrdered7dSameSKU'] += campaign['attributedUnitsOrdered7dSameSKU']
    res1 = calculate_data(list(res1.values()))
    res2 = calculate_data(list(res2.values()))
    write_obj_arr_to_json(res1, '/root/data/78/4116463299964550/new.csv')
    write_obj_arr_to_json(res2, '/root/data/78/4116463299964550/origin.csv')

def get_date_statistic(start, end, data_path):
    dates = get_date(start, end, data_path)
    res = {}
    for date in dates:
        campaigns = json.load(open(os.path.join(date, 'campaign.json')))
        k = date[-8:]
        res[k] = {
            "attributedSales7d": 0,
            "cost": 0,
            "attributedUnitsOrdered7d": 0,
            "attributedSales7dSameSKU": 0,
            "impressions": 0,
            "attributedConversions7d": 0,
            "clicks": 0,
            "attributedConversions7dSameSKU": 0,
            "attributedUnitsOrdered7dSameSKU": 0,
        }
        for campaign in campaigns:
            res[k]['attributedSales7d'] += campaign['attributedSales7d']
            res[k]['cost'] += campaign['cost']
            res[k]['attributedUnitsOrdered7d'] += campaign['attributedUnitsOrdered7d']
            res[k]['attributedSales7dSameSKU'] += campaign['attributedSales7dSameSKU']
            res[k]['impressions'] += campaign['impressions']
            res[k]['attributedConversions7d'] += campaign['attributedConversions7d']
            res[k]['clicks'] += campaign['clicks']
            res[k]['attributedConversions7dSameSKU'] += campaign['attributedConversions7dSameSKU']
            res[k]['attributedUnitsOrdered7dSameSKU'] += campaign['attributedUnitsOrdered7dSameSKU']
        impressions, clicks, orders, cost, sales = res[k]['impressions'], res[k]['clicks'], res[k]['attributedUnitsOrdered7d'], res[k]['cost'], res[k]['attributedSales7d']
        res[k]['ctr'] = clicks / impressions if impressions > 0 else 0
        res[k]['cvr'] = orders / clicks if clicks > 0 else 0
        res[k]['acos'] = cost / sales if sales > 0 else 0
    write_obj_arr_to_json(list(res.values()), '/root/data/78/4116463299964550/date_detail_data.csv')

def get_sku_points(profile_dir):
    start_date = datetime.now(tz=utc)- timedelta(days=30)
    start_date = start_date.astimezone(timezone('US/Pacific')).strftime('%Y%m%d')
    dates, _ = get_recent_days(start_date)

    # get sku performance
    res = {}
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        if not os.path.exists(data_dir): continue
        productads_data_path = os.path.join(data_dir, 'productAds.json')
        productads_data = json.load(open(productads_data_path))
        for data in productads_data:
            sku = data['sku']
            if sku not in res: res[sku] = {
                'impressions': 0,
                'clicks': 0,
                'orders': 0,
                'cost': 0,
                'sales': 0,
            }
            res[sku]['impressions'] += data['impressions']
            res[sku]['clicks'] += data['clicks']
            res[sku]['orders'] += data['attributedUnitsOrdered7d']
            res[sku]['cost'] += round(data['cost'], 2)
            res[sku]['sales'] += data['attributedSales7d']

    # calculate points
    result = {}
    for sku, performance in res.items():
        impressions, clicks, orders, costs, sales = performance['impressions'], performance['clicks'], performance['orders'], performance['cost'], performance['sales']
        if clicks < 30:
            result[sku] = [1, 0.5]
            continue
        ctr = clicks / impressions
        cvr = orders / clicks if clicks > 0 else 0
        acos = costs / sales if sales > 0 else 10
        ctr_co = sku_ponint_ctr(ctr/DEFAULT_CTR)
        cvr_co = sku_ponint_cvr(cvr/DEFAULT_CVR)
        acos_co = sku_ponint_acos(float(0.3)/acos)
        point = ctr_co * cvr_co * acos_co
        stock_co = sku_stock_co(point)
        result[sku] = [point, stock_co]
    return result

def get_sales_from_days(sales_path, days):
    res = {}
    for day in days:
        sales_data = read_csv(os.path.join(sales_path, day))
        for data in sales_data:
            sku = data['SKU']
            sales = int(data['已订购商品数量'])
            if sku not in res: res[sku] = 0
            res[sku] += sales
    return res

def get_sales_from_week(sales_path, date):
    res = {}
    sales_data = read_csv(os.path.join(sales_path, date))
    for data in sales_data:
        sku = data['SKU']
        sales = int(data['已订购商品数量'])
        if sku not in res: res[sku] = 0
        res[sku] += sales
    return res

def get_sku_sale_speed(sales_path):
    days = ['8.2.csv', '8.3.csv', '8.4.csv']
    recent_2_week = '7.26-8.1.csv'
    recent_3_week = '7.19-7.25.csv'
    recent_4_week = '7.12-7.18.csv'
    recent_days_data = get_sales_from_days(sales_path, days)
    recent_2_week_data = get_sales_from_week(sales_path, recent_2_week)
    recent_3_week_data = get_sales_from_week(sales_path, recent_3_week)
    recent_4_week_data = get_sales_from_week(sales_path, recent_4_week)
    recent_days_data_skus = list(recent_days_data.keys())
    recent_2_week_data_skus = list(recent_2_week_data.keys())
    recent_3_week_data_skus = list(recent_3_week_data.keys())
    recent_4_week_data_skus = list(recent_4_week_data.keys())
    skus = list(set(recent_days_data_skus + recent_2_week_data_skus + recent_3_week_data_skus + recent_4_week_data_skus))
    res = {}
    for sku in skus:
        if sku not in res: res[sku] = {
            'sku': sku,
            'week sales': 0
        }
        if sku in recent_days_data:
            res[sku]['week sales'] += recent_days_data[sku] * 0.4 * 7/len(days)
        if sku in recent_2_week_data:
            res[sku]['week sales'] += recent_2_week_data[sku] * 0.3
        if sku in recent_3_week_data:
            res[sku]['week sales'] += recent_3_week_data[sku] * 0.2
        if sku in recent_4_week_data:
            res[sku]['week sales'] += recent_4_week_data[sku] * 0.1
    return res

def calculate_stock():
    sku_ad_performance = get_sku_points('/root/data/78/4116463299964550')
    sku_sale_speed = get_sku_sale_speed('/root/data/78/4116463299964550/sales')
    res = {}
    for sku, sales_performance in sku_sale_speed.items():
        co = 1 if sku not in sku_ad_performance else sku_ad_performance[sku][1]
        print(sku, int(sales_performance['week sales'] * 4 + 0.5), co)
        res[sku] = {
            'sku': sku,
            '月销量预估': int(sales_performance['week sales'] * co * 4 + 0.5)
        }
    write_obj_arr_to_json(list(res.values()), '/root/data/78/4116463299964550/stock.csv')

def mergedata(path):
    files=os.listdir(path)
    res = {}
    for file in files:
        sales_data = read_csv(os.path.join(path, file))
        for data in sales_data:
            sku = data['SKU']
            if '已订购商品数量' in data:
                sales = int(data['已订购商品数量'])
            else:
                sales = int(data['Units Ordered'])
            if sku not in res: res[sku] = 0
            res[sku] += sales
    return res
    
def mergeAdsdata(dates):
    res = {}
    for date in dates:
        ads = json.load(open(os.path.join(date, 'productAds.json')))
        for data in ads:
            sku, impressions, clicks, orders, cost, sales = data['sku'], data['impressions'], data['clicks'], data[
                'attributedUnitsOrdered7d'], data['cost'], data['attributedSales7d']
            if sku not in res:
                res[sku] = {
                    'impressions': 0,
                    'clicks': 0,
                    'orders': 0,
                    'cost': 0,
                    'sales': 0
                }
            res[sku]['impressions'] += impressions
            res[sku]['clicks'] += clicks
            res[sku]['orders'] += orders
            res[sku]['cost'] += cost
            res[sku]['sales'] += sales
    return res

def merger_shop_data(before_data, after_data):
    res = {}
    for sku, sales in before_data.items():
        if sku not in after_data: continue
        res[sku] = {
            'sku': sku,
            'before_30': int(sales * 30 / 56 + 0.5),
            'after_30': int(after_data[sku] * 30 / 28 + 0.5)
        }
    return res

def merge_ads_data(before_ads_data, after_15_ads_data, after_30_ads_data):
    res = {}
    for sku, data in before_ads_data.items():
        impressions, clicks, orders, cost, sales = data['impressions'], data['clicks'], data['orders'], data['cost'], data['sales']
        ctr = clicks / impressions if impressions > 0 else 0
        cvr = orders / clicks if clicks > 0 else 0
        acos = cost / sales if sales > 0 else 99.99
        res[sku] = {
            'sku': sku,
            'before_impressions': int(impressions * 30 / 56 + 0.5),
            'before_clicks': int(clicks * 30 / 56 + 0.5),
            'before_orders': int(orders * 30 / 56 + 0.5),
            'before_cost': cost * 30 / 56,
            'before_sales': sales * 30 / 56,
            'before_ctr': ctr,
            'before_cvr': cvr,
            'before_acos': acos,
            'after_15_impressions': 0,
            'after_15_clicks': 0,
            'after_15_orders': 0,
            'after_15_cost': 0,
            'after_15_sales': 0,
            'after_15_ctr': 0,
            'after_15_cvr': 0,
            'after_15_acos': 0,
            'after_30_impressions': 0,
            'after_30_clicks': 0,
            'after_30_orders': 0,
            'after_30_cost': 0,
            'after_30_sales': 0,
            'after_30_ctr': 0,
            'after_30_cvr': 0,
            'after_30_acos': 0,
        }
        if sku in after_15_ads_data:
            data = after_15_ads_data[sku]
            impressions, clicks, orders, cost, sales = data['impressions'], data['clicks'], data['orders'], data['cost'], data['sales']
            ctr = clicks / impressions if impressions > 0 else 0
            cvr = orders / clicks if clicks > 0 else 0
            acos = cost / sales if sales > 0 else 99.99
            res[sku]['after_15_impressions'] = int(impressions * 30 / 15 + 0.5)
            res[sku]['after_15_clicks'] = int(clicks * 30 / 15 + 0.5)
            res[sku]['after_15_orders'] = int(orders * 30 / 15 + 0.5)
            res[sku]['after_15_cost'] = cost * 30 / 15
            res[sku]['after_15_sales'] = sales * 30 / 15
            res[sku]['after_15_ctr'] = ctr
            res[sku]['after_15_cvr'] = cvr
            res[sku]['after_15_acos'] = acos
        if sku in after_30_ads_data:
            data = after_30_ads_data[sku]
            impressions, clicks, orders, cost, sales = data['impressions'], data['clicks'], data['orders'], data['cost'], data['sales']
            ctr = clicks / impressions if impressions > 0 else 0
            cvr = orders / clicks if clicks > 0 else 0
            acos = cost / sales if sales > 0 else 99.99
            res[sku]['after_30_impressions'] = int(impressions * 30 / 28 + 0.5)
            res[sku]['after_30_clicks'] = int(clicks * 30 / 28 + 0.5)
            res[sku]['after_30_orders'] = int(orders * 30 / 28 + 0.5)
            res[sku]['after_30_cost'] = cost * 30 / 28
            res[sku]['after_30_sales'] = sales * 30 / 28
            res[sku]['after_30_ctr'] = ctr
            res[sku]['after_30_cvr'] = cvr
            res[sku]['after_30_acos'] = acos
        res[sku]['rate_15'] = res[sku]['after_15_orders'] / res[sku]['before_orders'] if res[sku]['before_orders'] > 0 else 9999
        res[sku]['rate_30'] = res[sku]['after_30_orders'] / res[sku]['before_orders'] if res[sku]['before_orders'] > 0 else 9999
    return res


def calculate_sku_performance(dates, data_path):
    res = {}
    for date in dates:
        ads = json.load(open(os.path.join(data_path, date, 'productAds.json')))
        for ad in ads:
            sku = ad['sku']
            if sku not in res: res[sku] = {
                'sku': sku,
                'asin': ad['asin'],
                'impressions': 0,
                'clicks': 0,
                'orders': 0,
                'cost': 0,
                'sales': 0
            }
            impressions, clicks, orders, cost, sales = ad['impressions'], ad['clicks'], ad[
                'attributedUnitsOrdered7d'], ad['cost'], ad['attributedSales7d']
            res[sku]['impressions'] += impressions
            res[sku]['clicks'] += clicks
            res[sku]['orders'] += orders
            res[sku]['cost'] += cost
            res[sku]['sales'] += sales
    product_acos = {}
    for sku, performance in res.items():
        impressions, clicks, orders, cost, sales = performance['impressions'],performance['clicks'],performance['orders'],performance['cost'],performance['sales']
        performance['price'] = round(sales/orders,2) if orders > 0 else ''
        performance['ctr'] = clicks/impressions if impressions > 0 else 0
        performance['cvr'] = orders/clicks if clicks > 0 else 0
        performance['acos'] = cost/sales if sales > 0 else 9999
        if orders > 20:
            product_acos[sku] = {
                "price": performance['price'],
                "macs": 0.25,
                "promotionTarget": 0
            }
    return res, product_acos

def get_sales(dates, data_path):
    product_acos_path = os.path.join(data_path, 'product_acos.json')
    product_acos = json.load(open(product_acos_path))
    res = {}
    for date in dates:
        productAds_path = os.path.join(data_path, date, 'productAds.json')
        ads = json.load(open(productAds_path))
        for ad in ads:
            sku = ad['sku']
            if sku not in product_acos: continue
            if sku not in res: res[sku] = {
                'sku': sku,
                'sales': 0
            }
            res[sku]['sales'] += ad['attributedSales7d']
    return res


if __name__ == '__main__':
    # data_path = "/root/data/78/4116463299964550"
    # parser = argparse.ArgumentParser()
    # parser.add_argument("start", help="start date", type=str)
    # parser.add_argument("end", help="end date", type=str)
    # opt = parser.parse_args()
    # get_sku_statistic(opt.start, opt.end)
    # get_date_statistic(opt.start, opt.end)
    # calculate_stock()

    # before_path, after_path = '/root/data/78/4116463299964550/before', '/root/data/78/4116463299964550/after'
    # before_data = mergedata(before_path)
    # after_data = mergedata(after_path)
    # shop_data = merger_shop_data(before_data, after_data)
    # before_date = get_date('20210531', '20210725', data_path)
    # after_15_date = get_date('20210726', '20210808', data_path)
    # after_30_date = get_date('20210726', '20210829', data_path)
    # before_ads_data = mergeAdsdata(before_date)
    # after_15_ads_data = mergeAdsdata(after_15_date)
    # after_30_ads_data = mergeAdsdata(after_30_date)
    # ads_data = merge_ads_data(before_ads_data, after_15_ads_data, after_30_ads_data)
    # write_obj_arr_to_json(list(shop_data.values()), '/root/data/78/4116463299964550/shop_sale.csv')
    # write_obj_arr_to_json(list(ads_data.values()), '/root/data/78/4116463299964550/ad_sale.csv')

    data_path = ['/root/data/125/1693533674946572', '/root/data/125/4430648297578102', '/root/data/125/3353096139223248']
    for path in data_path:
        dates = get_date('20210710', '20210908', path)
        sku_performance, product_acos = calculate_sku_performance(dates, path)
        write_obj_arr_to_json(list(sku_performance.values()), os.path.join(path, 'sku_performance.csv'))
        write_obj_to_json(product_acos, os.path.join(path, 'product_acos.json'))
    # data_path = '/root/data/78/4116463299964550'
    # dates = get_date('20210725', '20210731', data_path)
    # sales = get_sales(dates, data_path)
    # write_obj_arr_to_json(list(sales.values()), os.path.join(data_path, '20210725_20210731.csv'))
    # dates = get_date('20210801', '20210831', data_path)
    # sales = get_sales(dates, data_path)
    # write_obj_arr_to_json(list(sales.values()), os.path.join(data_path, '20210801_20210831.csv'))