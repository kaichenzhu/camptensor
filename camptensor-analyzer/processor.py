import json
import os
from nlp import *
from operator import add, sub
from weights import *


def get_sku_info(path):
    productAds_path = os.path.join(path, 'productAds.json')
    productAds = json.load(open(productAds_path))
    group_sku, sku_group = {}, {}
    for product in productAds:
        campId, groupId, sku = product['campaignId'], product['adGroupId'], product['sku']
        if groupId not in group_sku:
            group_sku[groupId] = []
        group_sku[groupId].append(sku)
        if sku not in sku_group:
            sku_group[sku] = { 'product':{}, 'auto':{}, 'keyword':{} }
    return group_sku, sku_group

def set_sku_group_data(path, group_sku, sku_group):
    groups = json.load(open(os.path.join(path, 'adGroups.json')))
    keywords = json.load(open(os.path.join(path, 'keywords.json')))
    targets = json.load(open(os.path.join(path, 'targets.json')))
    auto_target = set()
    keyword_target = set()
    for keyword in keywords:
        keyword_target.add(keyword['adGroupId'])
        groupId = keyword['adGroupId']
        campaignId = keyword['campaignId']
        if groupId not in group_sku: continue
        skus = group_sku[groupId]
        for sku in skus:
            if groupId in sku_group[sku]['keyword']: continue
            sku_group[sku]['keyword'][groupId] = campaignId
    for target in targets:
        if target['expression'][0]['type'] in AUTO_CAMPAIGN_TYPE:
            auto_target.add(target['adGroupId'])
            groupId = target['adGroupId']
            campaignId = target['campaignId']
            if groupId not in group_sku: continue
            skus = group_sku[groupId]
            for sku in skus:
                if groupId in sku_group[sku]['auto']: continue
                sku_group[sku]['auto'][groupId] = campaignId
    auto_and_keyword = auto_target | keyword_target
    for group in groups:
        groupId = group['adGroupId']
        campaignId = group['campaignId']
        if groupId in auto_and_keyword: continue
        if groupId not in group_sku: continue
        skus = group_sku[groupId]
        for sku in skus:
            if groupId in sku_group[sku]['product']: continue
            sku_group[sku]['product'][groupId] = campaignId


def get_negative_info(data_path):
    negative_targeting = {}
    negative_targeting_path = os.path.join(data_path, 'negativeTargets.json')
    negative_targeting_data = json.load(open(negative_targeting_path))
    for data in negative_targeting_data:
        campaignId = data['campaignId']
        adGroupId = data['adGroupId']
        if campaignId not in negative_targeting: negative_targeting[campaignId] = {}
        if adGroupId not in negative_targeting[campaignId]: negative_targeting[campaignId][adGroupId] = {}
        target_value = data['expression'][0]['value'].lower()
        negative_targeting[campaignId][adGroupId][target_value] = data['expression']
    
    negative_keyword = {}
    negative_keyword_path = os.path.join(data_path, 'negativeKeywords.json')
    negative_keyword_data = json.load(open(negative_keyword_path))
    for data in negative_keyword_data:
        campaignId = data['campaignId']
        adGroupId = data['adGroupId']
        if campaignId not in negative_keyword: negative_keyword[campaignId] = {}
        if adGroupId not in negative_keyword[campaignId]: negative_keyword[campaignId][adGroupId] = {}
        keyword = data['keywordText'].lower()
        negative_keyword[campaignId][adGroupId][keyword] = data['matchType']

    negative_campaign_keyword = {}
    negative_campaign_keyword_path = os.path.join(data_path, 'campaignNegativeKeywords.json')
    negative_campaign_keyword_data = json.load(open(negative_campaign_keyword_path))
    for data in negative_campaign_keyword_data:
        campaignId = data['campaignId']
        if campaignId not in negative_campaign_keyword: negative_campaign_keyword[campaignId] = {}
        keyword = data['keywordText'].lower()
        negative_campaign_keyword[campaignId][keyword] = data['matchType']
    
    return negative_targeting, negative_keyword, negative_campaign_keyword

def get_searchterm_performance(data_path, group_sku):
    files = os.listdir(data_path)
    files.sort()
    searchterm_performance = {}
    for path in files:
        # 遍历历史数据, 每日报表
        data_dir = os.path.join(data_path, path)
        if not os.path.isdir(data_dir): continue
        if len(path) != 8: continue
        if not path.isdigit(): continue
        # if int(path) < start or int(path) > end: continue
        print(data_dir)
        # keyword-query.json 获取manual keyword 中的 searchterm
        # target-query.json 获取auto中的searchterm 和 asin
        for target_file in ['keyword-query.json', 'targeting-query.json']:
            target_path = os.path.join(data_dir, target_file)
            target_data = json.load(open(target_path))
            data_type = 'keyword' if target_file == 'keyword-query.json' else 'target'
            searchterm_origin_type = 'manual' if data_type == 'keyword' else 'auto' # searchterm 来自自动广告还是手动广告
            for data in target_data:
                adGroupId = data['adGroupId']
                if adGroupId not in group_sku: continue
                query = data['query']
                target_format, target_type = format_phrase(query)
                skus = group_sku[adGroupId]
                targetId = data['keywordId'] if data_type == 'keyword' else data['targetId']
                targetId = str(targetId)
                ad_data = [data['impressions'], data['clicks'], data['attributedUnitsOrdered7d'], data['cost'], data['attributedSales7d']]
                for sku in skus:
                    if sku not in searchterm_performance:
                        searchterm_performance[sku] = {}
                    if target_format not in searchterm_performance[sku]:
                        searchterm_performance[sku][target_format] = {
                            'total': [0, 0, 0, 0, 0],
                            'auto': [0, 0, 0, 0, 0],
                            'manual': [0, 0, 0, 0, 0],
                            'type': target_type,
                            'detail': {}
                        }
                    if targetId not in searchterm_performance[sku][target_format]['detail']:
                        searchterm_performance[sku][target_format]['detail'][targetId] = {}
                    if query not in searchterm_performance[sku][target_format]['detail'][targetId]:
                        searchterm_performance[sku][target_format]['detail'][targetId][query] = [0, 0, 0, 0, 0]

                    # 更新total
                    total_data = searchterm_performance[sku][target_format]['total']
                    total_data = list(map(add, ad_data, total_data))
                    searchterm_performance[sku][target_format]['total'] = total_data
                    # 更新自/手动广告
                    searchterm_origin_data = searchterm_performance[sku][target_format][searchterm_origin_type]
                    searchterm_origin_data = list(map(add, ad_data, searchterm_origin_data))
                    searchterm_performance[sku][target_format][searchterm_origin_type] = searchterm_origin_data
                    # 更新detail
                    detail_data = searchterm_performance[sku][target_format]['detail'][targetId][query]
                    detail_data = list(map(add, ad_data, detail_data))
                    searchterm_performance[sku][target_format]['detail'][targetId][query] = detail_data
    return searchterm_performance

def get_target_performance(data_path, group_sku):
    files = os.listdir(data_path)
    files.sort()
    target_performance = {}
    for path in files:
        # 遍历历史数据, 每日报表
        data_dir = os.path.join(data_path, path)
        if not os.path.isdir(data_dir): continue
        if len(path) != 8: continue
        if not path.isdigit(): continue
        # if int(path) < start or int(path) > end: continue
        print(data_dir)
        # keyword-query.json 获取manual keyword 中的 searchterm
        # target-query.json 获取auto中的searchterm 和 asin
        for target_file in ['keyword.json', 'targeting.json']:
            target_path = os.path.join(data_dir, target_file)
            target_data = json.load(open(target_path))
            data_type = 'keyword' if target_file == 'keyword.json' else 'target'
            for data in target_data:
                adGroupId = data['adGroupId']
                if adGroupId not in group_sku: continue
                targetId = data['keywordId'] if data_type == 'keyword' else data['targetId']
                if data_type == 'keyword':
                    target_value = data['keywordText']
                    target_format, target_type = format_phrase(target_value)
                elif data_type == 'target':
                    target_value = data['targetingText']
                    if target_value in ['loose-match', 'close-match', 'substitutes', 'complements']:
                        target_format = 'auto-%s' % targetId
                        target_type = 'auto'
                    else:
                        target_type = target_value.split('=')[0]
                        target_format = target_value.split('=')[1].strip('\"').lower()
                skus = group_sku[adGroupId]
                ad_data = [data['impressions'], data['clicks'], data['attributedUnitsOrdered7d'], data['cost'], data['attributedSales7d']]
                if ad_data[0] < 1: continue
                for sku in skus:
                    if sku not in target_performance:
                        target_performance[sku] = {} 
                    if target_format not in target_performance[sku]:
                        target_performance[sku][target_format] = {
                            'total': [0, 0, 0, 0, 0],
                            'EXACT': [0, 0, 0, 0, 0],
                            'PHRASE': [0, 0, 0, 0, 0],
                            'BROAD': [0, 0, 0, 0, 0],
                            'type': target_type,
                            'detail': {}
                        }
                    if targetId not in target_performance[sku][target_format]['detail']:
                        target_performance[sku][target_format]['detail'][targetId] = {
                            'data': [0, 0, 0, 0, 0],
                            'matchType': data['matchType'] if target_type == 'keyword' else None
                        }
                    # 更新total
                    total_data = target_performance[sku][target_format]['total']
                    total_data = list(map(add, ad_data, total_data))
                    target_performance[sku][target_format]['total'] = total_data
                    # 更新手动keyword不同的matchtype
                    if data_type == 'keyword':
                        matchType = data['matchType']
                        keyword_data = target_performance[sku][target_format][matchType]
                        keyword_data = list(map(add, ad_data, keyword_data))
                        target_performance[sku][target_format][matchType] = keyword_data
                    # 更新detail
                    detail_data = target_performance[sku][target_format]['detail'][targetId]['data']
                    detail_data = list(map(add, ad_data, detail_data))
                    target_performance[sku][target_format]['detail'][targetId]['data'] = detail_data
    return target_performance

def get_target_info(path, group_sku):
    '''
    targeting 类型: auto(自动广告) | asin | category | keyword
    '''
    targetings = {}
    for target_file in ['targets.json', 'keywords.json']:
        targets_data = json.load(open(os.path.join(path, target_file)))
        data_type = 'keyword' if target_file == 'keywords.json' else 'target'
        for data in targets_data:
            adGroupId = data['adGroupId']
            if adGroupId not in group_sku: continue
            targetId = data['keywordId'] if data_type == 'keyword' else data['targetId']
            if targetId in targetings: continue # 跳过重复统计
            if data_type == 'keyword':
                matchType = data['matchType']
                target_value = data['keywordText']
                target_format, target_type = format_phrase(target_value)
            elif data_type == 'target':
                expressionType = data['expressionType']
                expression = data['expression'][0]
                if  expressionType == 'auto':
                    target_type = 'auto'
                    target_value = expression['type']
                elif expressionType == 'manual':
                    target_type = MANUAL_CAMPAIGN_TYPE[expression['type']]
                    target_value = expression['value']
                target_format = target_value.lower()
                matchType = None
            targetings[targetId] = {
                'sku': group_sku[adGroupId],
                'bid': data['bid'] if 'bid' in data else None,
                'campaignId': data['campaignId'],
                'adGroupId': adGroupId,
                'targetId': targetId,
                'type': target_type,
                'targetValue': target_value,
                'matchType': matchType,
                'targetValue': target_value,
                'format': target_format
            }

    return targetings

def get_searchterm_info(data_path, group_sku):
    searchterms = {}
    files = os.listdir(data_path)
    files.sort()
    for path in files:
        # 遍历历史数据, 每日报表
        data_dir = os.path.join(data_path, path)
        if not os.path.isdir(data_dir): continue
        if len(path) != 8: continue
        if not path.isdigit(): continue

        print(data_dir)
        # keyword-query.json 获取manual keyword 中的 searchterm
        # target-query.json 获取auto中的searchterm 和 asin
        for target_file in ['keyword-query.json', 'targeting-query.json']:
            target_path = os.path.join(data_dir, target_file)
            target_data = json.load(open(target_path))
            data_type = 'keyword' if target_file == 'keyword-query.json' else 'target'

            for data in target_data:
                adGroupId = data['adGroupId']
                if adGroupId not in group_sku: continue
                targetId = data['keywordId'] if data_type == 'keyword' else data['targetId']
                query = data['query'].lower()
                searchtermId = '%s-%s' % (targetId, query)
                if searchtermId in searchterms: continue # 跳过重复统计
                query_format, query_type = format_phrase(query)
                campaignId = data['campaignId']
                campaignName = data['campaignName']
                adGroupName = data['adGroupName']
                match_type = data['matchType'] if data_type == 'keyword' else data['targetingExpression']
                searchterms[searchtermId] = {
                    'sku': group_sku[adGroupId],
                    'query': query,
                    'format': query_format,
                    'type': query_type,
                    'campaignId': campaignId,
                    'campaignName': campaignName,
                    'adGroupId': adGroupId,
                    'adGroupName': adGroupName,
                    'targetId': targetId,
                    'matchType': match_type
                }
    return searchterms

def write_obj_to_json(obj, path):
    b = json.dumps(obj)
    f2 = open(path, 'w')
    f2.write(b)
    f2.close()

def get_ads_performance(target_performance, searchterm_performance):
    ads_performance = {
        'sku': {},
        "impressions": 0,
        "clicks": 0,
        "orders": 0,
        "spends": 0,
        "sales": 0
    }
    for sku, target in target_performance.items():
        if sku not in ads_performance: 
            ads_performance['sku'][sku] = {
                "impressions": 0,
                "clicks": 0,
                "orders": 0,
                "spends": 0,
                "sales": 0,
                "target_impressions_distribution": [],
                "search_impressions_distribution": []
            }
        for key, value in target.items():
            impressions, clicks, orders, spends, sales = value['total']
            impression_distribution = [x['data'][0] for x in value['detail'].values()]
            ads_performance['sku'][sku]['impressions'] += impressions
            ads_performance['sku'][sku]['clicks'] += clicks
            ads_performance['sku'][sku]['orders'] += orders
            ads_performance['sku'][sku]['spends'] += spends
            ads_performance['sku'][sku]['sales'] += sales
            ads_performance['sku'][sku]['target_impressions_distribution'] += impression_distribution
        ads_performance['impressions'] += ads_performance['sku'][sku]['impressions']
        ads_performance['clicks'] += ads_performance['sku'][sku]['clicks']
        ads_performance['orders'] += ads_performance['sku'][sku]['orders']
        ads_performance['spends'] += ads_performance['sku'][sku]['spends']
        ads_performance['sales'] += ads_performance['sku'][sku]['sales']

    for sku, searchterm in searchterm_performance.items():
        for _, value in searchterm.items():
            for _, detail in value['detail'].items():
                for _, data in detail.items():
                    ads_performance['sku'][sku]['search_impressions_distribution'].append(data[0])
    return ads_performance

def get_campaign_performance(target_performance, targetings, searchterm_performance, searchterms):
    campaign_performance = {}
    for sku, target in target_performance.items():
        for target_format, data in target.items():
            for targetId, detail in data['detail'].items():
                ads_data = detail['data']
                targetId = int(targetId)
                if targetId not in targetings:
                    print(targetId)
                    continue
                target_info = targetings[targetId]
                adGroupId, campaignId = target_info['adGroupId'], target_info['campaignId']
                if campaignId not in campaign_performance:
                    campaign_performance[campaignId] = {
                        'data': [0, 0, 0, 0, 0],
                        'groups': {}
                    }
                if adGroupId not in campaign_performance[campaignId]['groups']:
                    campaign_performance[campaignId]['groups'][adGroupId] = {
                        'data': [0, 0, 0, 0, 0],
                        'targets': {}
                    }
                if targetId not in campaign_performance[campaignId]['groups'][adGroupId]['targets']:
                    campaign_performance[campaignId]['groups'][adGroupId]['targets'][targetId] = {
                        'data': [0, 0, 0, 0, 0],
                        'searchterms': {}
                    }
                ads_target_data = campaign_performance[campaignId]['groups'][adGroupId]['targets'][targetId]['data']
                campaign_performance[campaignId]['groups'][adGroupId]['targets'][targetId]['data'] = list(map(add, ads_data, ads_target_data))
                ads_group_data = campaign_performance[campaignId]['groups'][adGroupId]['data']
                campaign_performance[campaignId]['groups'][adGroupId]['data'] = list(map(add, ads_data, ads_group_data))
                ads_campaign_data = campaign_performance[campaignId]['data']
                campaign_performance[campaignId]['data'] = list(map(add, ads_data, ads_campaign_data))

    for sku, searchterm in searchterm_performance.items():
        for searchterm_format, data in searchterm.items():
            for targetId, detail in data['detail'].items():
                targetId = int(targetId)
                if targetId not in targetings:
                    print(targetId)
                    continue
                target_info = targetings[targetId]
                adGroupId, campaignId = target_info['adGroupId'], target_info['campaignId']
                for query, query_data in detail.items():
                    campaign_performance[campaignId]['groups'][adGroupId]['targets'][targetId]['searchterms'][query] = query_data

    return campaign_performance

def get_sku_keywords(group_sku, keywords, targets):
    res = {}
    for keyword in keywords:
        adGroupId = keyword['adGroupId']
        keywordText = keyword['keywordText']
        matchType = keyword['matchType']
        skus = group_sku[adGroupId]
        for sku in skus:
            if sku not in res: res[sku] = {}
            keyword_format, _ = format_phrase(keywordText)
            if keyword_format not in res[sku]: res[sku][keyword_format] = []
            res[sku][keyword_format].append(matchType)
    for target in targets:
        expressionType = target['expressionType']
        if expressionType == 'auto': continue
        adGroupId = target['adGroupId']
        expressionValue = target['expressionValue']
        skus = group_sku[adGroupId]
        for sku in skus:
            if sku not in res: res[sku] = {}
            if expressionValue not in res[sku]: res[sku][expressionValue] = []
    return res

def process(opt):
    data_path = opt.data_path
    print('start build campaign, adgroup, sku relation map')
    group_sku, sku_group = get_sku_info(data_path)
    set_sku_group_data(data_path, group_sku, sku_group)
    statistic_dir = os.path.join(data_path, 'statistic')
    if not os.path.exists(statistic_dir): os.mkdir(statistic_dir)
    write_obj_to_json(sku_group, os.path.join(statistic_dir, 'sku_groups.json'))
    print('phrase-1: done!')

    # 获取当前的searchterm, targeting的表现
    print('start get ads keyword/targeting performance')
    searchterm_performance = get_searchterm_performance(data_path, group_sku)
    write_obj_to_json(searchterm_performance, os.path.join(statistic_dir, 'searchterm_performance.json'))
    target_performance = get_target_performance(data_path, group_sku)
    write_obj_to_json(target_performance, os.path.join(statistic_dir, 'target_performance.json'))
    print('phrase-2: done!')

    # 统计各sku的数据
    print('start post process ads performance')
    ads_performance = get_ads_performance(target_performance, searchterm_performance)
    write_obj_to_json(ads_performance, os.path.join(statistic_dir, 'ads_performance.json'))
    print('phrase-3: done!')

    result_dir = os.path.join(data_path, 'result')
    if not os.path.exists(result_dir): os.mkdir(result_dir)

    # 获取targeting信息: manual keyword, asin, auto campaign
    print('start extract targeting info')
    targetings = get_target_info(data_path, group_sku)
    write_obj_to_json(targetings, os.path.join(result_dir, 'targetings.json'))
    print('phrase-4: done!')

    # 获取manual keywor searchterm, auth campaign searchterm/asin
    print('start extract searchterm info')
    searchterms = get_searchterm_info(data_path, group_sku)
    write_obj_to_json(searchterms, os.path.join(result_dir, 'searchterms.json'))
    print('phrase-5: done!')

    # 获取campaign统计
    print('start get campaign performance')
    campaign_performance = get_campaign_performance(target_performance, targetings, searchterm_performance, searchterms)
    write_obj_to_json(campaign_performance, os.path.join(statistic_dir, 'campaign_performance.json'))
    print('phrase-6: done!')

    # 统计每个sku下包含哪些关键词/ASIN
    print('start get sku keywords')
    keywords_path = os.path.join(data_path, 'keywords.json')
    keywords = json.load(open(keywords_path))
    targets_path = os.path.join(data_path, 'targets.json')
    targets = json.load(open(targets_path))
    sku_keywords = get_sku_keywords(group_sku, keywords, targets)
    write_obj_to_json(sku_keywords, os.path.join(statistic_dir, 'sku_keywords.json'))
    print('phrase-7: done!')