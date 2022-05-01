from nltk.corpus.reader.propbank import PropbankInstance
from transform import *
import os
import json
import argparse
from processor import *
import csv
from weights import *
from util import *

def TargetOptimization(product_info, campaign_sku, ads_performance, keywords, targets, target_performance):
    res = []
    for ad_targets in [keywords, targets]:  # 遍历keywords 和 targets
        for target in ad_targets:
            campaignId, adGroupId, target_state = target['campaignId'], target['adGroupId'], target['state']
            if campaignId not in campaign_sku or target_state != 'enabled':
                continue
            skus = campaign_sku[campaignId]
            price, profit, avg_ctr, avg_cvr, target_acos, promotionTarget = get_ads_metric(
                skus, product_info, ads_performance)
            target_type = 'keyword' if 'keywordId' in target else 'target'
            if target_type == 'keyword':
                targetId, keywordText, matchType = target['keywordId'], target['keywordText'], target['matchType']
                target_format, _ = format_phrase(keywordText)
                targetType = matchType.upper()
            else:
                targetId, expressionType = target['targetId'], target['expressionType']
                target_format = 'auto-%s' % targetId if expressionType == 'auto' else target['expression'][0]['value'].lower(
                )
                targetType = 'total'
            impressions, clicks, orders, cost, sales = get_skus_data_from_target_performance(
                skus, target_format, targetType, target_performance)
            if clicks < TARGETOPT_MIN_CLICK: continue
            ctr, cvr, acos = clicks / impressions, orders / \
                clicks, cost / sales if sales > 0 else 3
            st_score = get_st_score(ctr, cvr, acos, avg_ctr, avg_cvr, target_acos)
            print(skus,target_format, ctr, cvr, acos, avg_ctr, avg_cvr, target_acos, st_score)
            if st_score < TARGETING_MIN_CVR[promotionTarget]:
                res.append(target)
    return res

def targetOpt(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    product_acos_path = os.path.join(opt.data_path, 'product_acos.json')
    if not os.path.exists(product_acos_path):
        return
    product_info, ads_performance, target_performance, searchterm_performance, keywords, targets, adGroup_info, campaign_info, campaign_sku = bid_preprocessc(
        opt, statistic_dir, product_acos_path)
    disable_targeting = TargetOptimization(product_info, campaign_sku, ads_performance, keywords, targets, target_performance)
    result_dir = os.path.join(opt.data_path, 'result')
    write_obj_to_json(disable_targeting, os.path.join(result_dir, 'disable_targeting.json'))

def searchtermOpt(opt):
    # 读取数据
    result_dir = os.path.join(opt.data_path, 'result')
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    searchterms = json.load(open(os.path.join(result_dir, 'searchterms.json')))
    product_acos_path = os.path.join(opt.data_path, 'product_acos.json')
    if not os.path.exists(product_acos_path):
        return
    product_info = json.load(
        open(os.path.join(opt.data_path, 'product_acos.json')))
    searchterm_performance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    ads_performance = json.load(
        open(os.path.join(statistic_dir, 'ads_performance.json')))
    sku_keywords = json.load(
        open(os.path.join(statistic_dir, 'sku_keywords.json')))
    # 关键词分类
    negative_searchterm, good_performance_keywords = st_classifier(
        searchterms, sku_keywords, ads_performance, searchterm_performance, product_info)

    # # 保存分类结果
    write_obj_to_json(good_performance_keywords, os.path.join(
        result_dir, 'good_performance_keywords.json'))
    write_obj_to_json(negative_searchterm, os.path.join(
        result_dir, 'negative_keywords.json'))
    


def get_skus_data_from_target_performance(skus, keyword_format, targetType, target_performance):
    impressions, clicks, orders, cost, sales = 2**32, 0, 0, 0, 0
    for sku in skus:
        if keyword_format not in target_performance[sku]:
            continue
        sku_impressions = target_performance[sku][keyword_format][targetType][0]
        if sku_impressions < impressions:
            impressions, clicks, orders, cost, sales = target_performance[
                sku][keyword_format][targetType]
    return impressions, clicks, orders, cost, sales


def get_skus_data_from_searchterm_performance(skus, keyword_format, searchterm_performance):
    impressions, clicks, orders, cost, sales = 2**32, 0, 0, 0, 0
    for sku in skus:
        if sku not in searchterm_performance or keyword_format not in searchterm_performance[sku]:
            continue
        sku_impressions = searchterm_performance[sku][keyword_format]['total'][0]
        if sku_impressions < impressions:
            impressions, clicks, orders, cost, sales = searchterm_performance[
                sku][keyword_format]['total']
    return impressions, clicks, orders, cost, sales


def get_skus_data_from_ads_performance(skus, ads_performance):
    impressions, clicks, orders, cost, sales = 0, 0, 0, 0, 0
    for sku in skus:
        if sku not in ads_performance[sku]:
            continue
        sku_impressions, sku_clicks, sku_orders, sku_cost, sku_sales = ads_performance[sku]['impressions'], ads_performance[
            sku]['clicks'], ads_performance[sku]['orders'], ads_performance[sku]['spends'], ads_performance[sku]['sales']
        impressions += sku_impressions
        clicks += sku_clicks
        orders += sku_orders
        cost += sku_cost
        sales += sku_sales
    return impressions, clicks, orders, cost, sales


def bidopt_ctr_layer(x):
    a, b, c, d, m = BIDOPT_CTR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def bidopt_cvr_layer(x):
    a, b, c, d, m = BIDOPT_CVR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def bidopt_acos_layer(x):
    a, b, c, d, m = BIDOPT_ACOS_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def bidopt_head_layer(ctr, cvr, acos, avg_ctr, avg_cvr, target_acos):
    ctr_co = bidopt_ctr_layer(ctr/avg_ctr)
    cvr_co = bidopt_cvr_layer(cvr/avg_cvr)
    acos_co = bidopt_acos_layer(acos/target_acos)
    return ctr_co * cvr_co * acos_co


def bidOptimization(product_info, campaign_sku, ads_performance, adGroup_info, keywords, targets, target_performance, searchterm_performance):
    res = []
    for ad_targets in [keywords, targets]:  # 遍历keywords 和 targets
        for target in ad_targets:
            campaignId, adGroupId, target_state = target['campaignId'], target['adGroupId'], target['state']
            if campaignId not in campaign_sku or target_state != 'enabled':
                continue
            bid = target['bid'] if 'bid' in target else adGroup_info[adGroupId]['defaultBid']
            skus = campaign_sku[campaignId]
            price, profit, avg_ctr, avg_cvr, target_acos, promotionTarget = get_ads_metric(
                skus, product_info, ads_performance)
            basic_price = price * target_acos / len(skus)
            target_type = 'keyword' if 'keywordId' in target else 'target'
            if target_type == 'keyword':
                targetId, keywordText, matchType = target['keywordId'], target['keywordText'], target['matchType']
                target_format, _ = format_phrase(keywordText)
                targetType = matchType.upper()
            else:
                targetId, expressionType = target['targetId'], target['expressionType']
                target_format = 'auto-%s' % targetId if expressionType == 'auto' else target['expression'][0]['value'].lower(
                )
                targetType = 'total'
            impressions, clicks, orders, cost, sales = get_skus_data_from_target_performance(
                skus, target_format, targetType, target_performance)
            ctr, cvr = None, None
            if clicks < BID_OPT_TARGET_MINCLICK:
                if target_type == 'target' and expressionType == 'auto':
                    new_bid = basic_price * avg_cvr
                else:
                    impressions, clicks, orders, cost, sales = get_skus_data_from_searchterm_performance(
                        skus, target_format, searchterm_performance)
                    if clicks < BID_OPT_SEARCHTERM_MINCLICK:
                        new_bid = basic_price * avg_cvr
                    else:
                        ctr, cvr, acos = clicks / impressions, orders / \
                            clicks, cost / sales if sales > 0 else 3
                        new_bid = basic_price * cvr * \
                            bidopt_head_layer(
                                ctr, cvr, acos, avg_ctr, avg_cvr, target_acos)
            else:
                ctr, cvr, acos = clicks / impressions, orders / \
                    clicks, cost / sales if sales > 0 else 3
                new_bid = basic_price * cvr * \
                    bidopt_head_layer(ctr, cvr, acos, avg_ctr,
                                      avg_cvr, target_acos)
            new_bid = BID_OPT_NEWBID_CO * new_bid + BID_OPT_ORIGINBID_CO * bid
            new_bid = max(new_bid, MIN_BID)
            ctr, cvr = DEFAULT_CTR if not ctr else ctr, get_proper_cvr(float(basic_price)) if not cvr else cvr
            new_bid = min(get_max_bid(skus, product_info, ctr, cvr), new_bid)
            if abs(new_bid - bid) < BID_CHANGE_MIN_STEP:
                continue
            target['new_bid'] = round(new_bid, 2)
            res.append(target)
    return res


def bidOpt(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    product_acos_path = os.path.join(opt.data_path, 'product_acos.json')
    if not os.path.exists(product_acos_path):
        return
    product_info, ads_performance, target_performance, searchterm_performance, keywords, targets, adGroup_info, campaign_info, campaign_sku = bid_preprocessc(
        opt, statistic_dir, product_acos_path)
    bid_result = bidOptimization(product_info, campaign_sku, ads_performance,
                                 adGroup_info, keywords, targets, target_performance, searchterm_performance)
    result_dir = os.path.join(opt.data_path, 'result')
    write_obj_to_json(bid_result, os.path.join(result_dir, 'bid.json'))


def bid_preprocessc(opt, statistic_dir, product_acos_path):
    product_info = json.load(open(product_acos_path))
    for sku, info in product_info.items():
        price, macs, promotionTarget = info.values()
        info['target_acos'] = macs * PROMOTION_CO[promotionTarget]
    ads_performance = json.load(
        open(os.path.join(statistic_dir, 'ads_performance.json')))
    target_performance = json.load(
        open(os.path.join(statistic_dir, 'target_performance.json')))
    searchterm_performance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    campaigns = json.load(open(os.path.join(opt.data_path, 'campaigns.json')))
    adGroups = json.load(open(os.path.join(opt.data_path, 'adGroups.json')))
    productAds = json.load(
        open(os.path.join(opt.data_path, 'productAds.json')))
    keywords = json.load(open(os.path.join(opt.data_path, 'keywords.json')))
    targets = json.load(open(os.path.join(opt.data_path, 'targets.json')))
    adGroup_info = extract_adGroup_data(adGroups)
    campaign_info = extract_campaign_data(campaigns)
    campaign_sku = {}
    for ad in productAds:
        state, sku, campaignId, adGroupId = ad['state'], ad['sku'], ad['campaignId'], ad['adGroupId']
        if state != 'enabled' or sku not in product_info or adGroup_info[adGroupId]['state'] != 'enabled':
            continue
        if campaignId not in campaign_sku:
            campaign_sku[campaignId] = []
        campaign_sku[campaignId].append(sku)
    for campaign in campaigns:
        state, campaignId = campaign['state'], campaign['campaignId']
        if campaignId not in campaign_sku:
            continue
        if state != 'enabled' and campaignId in campaign_sku:
            del campaign_sku[campaignId]
            continue
        foundAll = True
        for sku in campaign_sku[campaignId]:
            if sku not in product_info:
                foundAll = False
        if not foundAll:
            del campaign_sku[campaignId]
    return product_info, ads_performance, target_performance, searchterm_performance, keywords, targets, adGroup_info, campaign_info, campaign_sku


def analyse(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    searchterm_performance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    res = {}
    count = 5
    for sku, ad_performance in searchterm_performance.items():
        res[sku] = []
        for searchterm, performance in ad_performance.items():
            if performance['type'] != 'keyword':
                continue
            if performance['total'][0] < 100:
                continue
            item = [searchterm] + performance['total']
            i = 0
            while i < len(res[sku]) and i < count and item[1] < res[sku][i][1]:
                i += 1
            if i < count:
                res[sku].insert(i, item)

    path = os.path.join(statistic_dir, 'keywordsAnalyse.csv')
    with open(path, "w") as csvfile:
        writer = csv.writer(csvfile)
        # 先写入columns_name
        writer.writerow(["SKU", "关键词", "曝光", "点击", "订单",
                        "花费", "销售额", "点击率", "转化率", "ACOS"])
        for sku, performance in res.items():
            total = [0, 0, 0, 0, 0]
            for kw in performance:
                ctr = kw[2]/kw[1]
                cvr = kw[3]/kw[2] if kw[2] > 0 else 0
                acos = kw[4]/kw[5] if kw[5] > 0 else 'inf'
                writer.writerow([sku] + kw + [ctr, cvr, acos])
                total = [x + y for x, y in zip(total, kw[1:])]
            if len(performance) == 0:
                continue
            ctr = total[1]/total[0]
            cvr = total[2]/total[1] if total[1] > 0 else 0
            acos = total[3]/total[4] if total[4] > 0 else 'inf'
            total = total + [ctr, cvr, acos]
            writer.writerow([sku, 'total'] + total)


def getGoodperformance(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    weighted_performance = json.load(
        open(os.path.join(statistic_dir, 'weighted_performance.json')))
    ads_performance = json.load(
        open(os.path.join(statistic_dir, 'ads_performance.json')))
    good_performance_keyword = extract_good_performance_keywords(
        weighted_performance, ads_performance)
    write_obj_to_json(good_performance_keyword, os.path.join(
        statistic_dir, 'good_performance_keyword.json'))


def wordAnalyze(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    weighted_performance = json.load(
        open(os.path.join(statistic_dir, 'weighted_performance.json')))
    word_performance = keywordAnalyze(weighted_performance)
    write_obj_to_json(word_performance, os.path.join(
        statistic_dir, 'word_analyze.json'))


def stanalyze(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    searchtermPerformance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    path = os.path.join(statistic_dir, 'searchterm_analyze.csv')
    with open(path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        writer.writerow(["SKU", "关键词", "曝光", "点击", "订单", "花费", "销售额"])
        # 写入多行用writerows
        for sku, performance in searchtermPerformance.items():
            for keyword, kwperformance in performance.items():
                if kwperformance['total'][2] > 0:
                    writer.writerow([sku, keyword] + kwperformance['total'])


def tganalyze(opt):
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    searchtermPerformance = json.load(
        open(os.path.join(statistic_dir, 'target_performance.json')))
    path = os.path.join(statistic_dir, 'target_analyze.csv')
    with open(path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        writer.writerow(["SKU", "投放目标", "曝光", "点击", "订单", "花费", "销售额"])
        # 写入多行用writerows
        for sku, performance in searchtermPerformance.items():
            for target, tgperformance in performance.items():
                if tgperformance['total'][2] < 1:
                    continue
                if tgperformance['type'] == 'auto':
                    target = target.split('-')[1]
                writer.writerow([sku, target] + tgperformance['total'])


def budget_layer(x):
    a, b, c, d, m = BUDGET_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def half_round(x):
    y = int(x)
    z = x - y
    w = [0, 0.5, 0.5, 1]
    t = int(z / 0.25)
    c = y + w[t]
    return max(1, c)


def budgetOpt(opt):
    res, product_info, campaign_sku = budgetOpt_preprocess(opt)
    for campaignId, campaign in res.items():
        sale, cost, campaignBudget = campaign['attributedSales7d'], campaign['cost'], campaign['campaignBudget']
        budget_consume_rate, time_pass_rate = cost / \
            campaignBudget, get_time_pass_rate()
        if budget_consume_rate / time_pass_rate < CAMPAIGN_BUDGET_CONSUME_RATE and time_pass_rate < 1/2:
            continue
        product_acos, acos = get_product_acos(
            product_info, campaign_sku, campaignId, sale, cost)
        newBudget = budget_layer(product_acos / acos) * cost + campaignBudget - cost
        newBudget = half_round(newBudget)
        if abs(newBudget - campaignBudget) < 0.5 or newBudget < MIN_BUDGET:
            continue
        campaign['newBudget'] = newBudget
        print(campaign['campaignName'], budget_consume_rate,
              time_pass_rate, campaignBudget, newBudget)
    res_dir = os.path.join(opt.data_path, 'result')
    write_obj_to_json(res, os.path.join(res_dir, 'budgetOpt.json'))


def get_product_acos(product_info, campaign_sku, campaignId, sale, cost):
    price, profit, promotionTarget = 0, 0, 4
    for sku in campaign_sku[campaignId]:
        price += product_info[sku]['price']
        profit += product_info[sku]['price'] * product_info[sku]['macs']
        promotionTarget = min(
            promotionTarget, product_info[sku]['promotionTarget'])
    product_acos = profit / price * PROMOTION_CO[promotionTarget]
    acos = cost / sale if sale > 0 else 3
    return product_acos, acos


def budgetOpt_preprocess(opt):
    res = {}
    product_info = json.load(
        open(os.path.join(opt.data_path, 'product_acos.json')))
    for sku, info in product_info.items():
        price, macs, promotionTarget = info.values()
        info['target_acos'] = macs * PROMOTION_CO[promotionTarget]
    campaign_sku = {}
    adGroups = json.load(open(os.path.join(opt.data_path, 'adGroups.json')))
    adGroup_info = extract_adGroup_data(adGroups)
    productAds = json.load(
        open(os.path.join(opt.data_path, 'productAds.json')))
    for ad in productAds:
        state, sku, campaignId, adGroupId = ad['state'], ad['sku'], ad['campaignId'], ad['adGroupId']
        if state != 'enabled' or sku not in product_info or adGroup_info[adGroupId]['state'] != 'enabled':
            continue
        if campaignId not in campaign_sku:
            campaign_sku[campaignId] = []
        campaign_sku[campaignId].append(sku)
    today_dir = os.path.join(opt.data_path, get_past_days(1)[0])
    campaigns = json.load(open(os.path.join(today_dir, 'campaign.json')))
    for campaign in campaigns:
        status, campaignId = campaign['campaignStatus'], campaign['campaignId']
        if status != 'enabled' or campaignId not in campaign_sku:
            continue
        foundAll = True
        for sku in campaign_sku[campaignId]:
            if sku not in product_info:
                foundAll = False
        if not foundAll:
            continue
        if campaignId not in res:
            res[campaignId] = {}
        res[campaignId] = campaign
    return res, product_info, campaign_sku


def dailybid_ctr_layer(x):
    a, b, c, d, m = DAILYBID_CTR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def dailybid_cvr_layer(x):
    a, b, c, d, m = DAILYBID_CVR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def dailybid_acos_layer(x):
    a, b, c, d, m = DAILYBID_ACOS_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def dailybid_head_layer(ctr, cvr, acos, avg_ctr, avg_cvr, target_acos):
    ctr_co = dailybid_ctr_layer(ctr/avg_ctr)
    cvr_co = dailybid_cvr_layer(cvr/avg_cvr)
    acos_co = dailybid_acos_layer(acos/target_acos)
    return ctr_co * cvr_co * acos_co


def extract_campaign_data(campaign_data):
    res = {}
    for campaign in campaign_data:
        campaignId = campaign['campaignId']
        if campaignId not in res:
            res[campaignId] = campaign
    return res


def extract_adGroup_data(adGroup_data):
    res = {}
    for adGroup in adGroup_data:
        adGroupId = adGroup['adGroupId']
        if adGroupId not in res:
            res[adGroupId] = adGroup
    return res


def extract_keyword_data(keywords_data):
    res = {}
    for keyword in keywords_data:
        keywordId = keyword['keywordId']
        if keywordId not in res:
            res[keywordId] = keyword
    return res


def extract_target_data(traget_data):
    res = {}
    for target in traget_data:
        targetId = target['targetId']
        if targetId not in res:
            res[targetId] = target
    return res


def extract_adGroups_data(adGroups):
    res = {}
    for adgroup in adGroups:
        adGroupId = adgroup['adGroupId']
        if adGroupId not in res:
            res[adGroupId] = adgroup
    return res


def get_proper_cvr(x):
    if x <= 12: return 0.15
    if x >= 200: return 0.03
    return -0.0006383 * x + 0.15766

def get_ads_metric(skus, product_info, ads_performance):
    price, profit, promotionTarget = 0, 0, 4
    for sku in skus:
        if sku not in product_info: continue
        price += product_info[sku]['price']
        profit += product_info[sku]['price'] * product_info[sku]['macs']
        promotionTarget = min(
            promotionTarget, product_info[sku]['promotionTarget'])
    target_acos = PROMOTION_CO[promotionTarget] * profit / price
    impressions, clicks, orders = 0, 0, 0
    for sku in skus:
        if sku not in ads_performance['sku']:
            continue
        sku_data = ads_performance['sku'][sku]
        impressions += sku_data['impressions']
        clicks += sku_data['clicks']
        orders += sku_data['orders']
    if clicks < SKU_MIN_CLICK or orders < SKU_MIN_ORDER:
        ctr, cvr = DEFAULT_CTR, get_proper_cvr(float(price) / len(skus))
    else:
        ctr, cvr = clicks / impressions, orders / clicks
    return price, profit, ctr, cvr, target_acos, promotionTarget


def dailybidOpt(product_info, campaign_sku, ads_performance, target_performance, searchterm_performance, data_dir, keywords, targets, campaign_info, adGroup_info):
    res = []
    campaign_report, keyword_report, target_report = get_report(data_dir)
    for ad_targets in [keywords, targets]:  # 遍历keywords 和 targets
        for target in ad_targets:
            campaignId, adGroupId, target_state = target['campaignId'], target['adGroupId'], target['state']
            if campaignId not in campaign_sku or target_state != 'enabled':
                continue
            target_type = 'keyword' if 'keywordId' in target else 'target'
            if target_type == 'keyword':
                targetId, report, targetType = target['keywordId'], keyword_report, target['matchType'].upper(
                )
                target_format, _ = format_phrase(target['keywordText'])
            else:
                targetId, report, targetType = target['targetId'], target_report, 'total'
                target_format = 'auto-%s' % targetId if target['expressionType'] == 'auto' else target['expression'][0]['value'].lower(
                )
            if campaignId not in campaign_report:
                campaignCost, campaignBudget = 0, campaign_info[campaignId]['dailyBudget']
            else:
                campaignCost, campaignBudget = campaign_report[campaignId][
                    'cost'], campaign_report[campaignId]['campaignBudget']
            budget_consume_rate, time_pass_rate = campaignCost / \
                campaignBudget, get_time_pass_rate()
            bid_co, bid = 1, target['bid'] if 'bid' in target else adGroup_info[adGroupId]['defaultBid']
            skus = campaign_sku[campaignId]
            impressions, clicks, orders, cost, sales = get_skus_data_from_target_performance(
                skus, target_format, targetType, target_performance)
            price, profit, avg_ctr, avg_cvr, target_acos, promotionTarget = get_ads_metric(
                        skus, product_info, ads_performance)
            target_ctr = DEFAULT_CTR if clicks < BID_OPT_TARGET_MINCLICK else clicks / impressions
            target_cvr = get_proper_cvr(float(price) / len(skus)) if orders < SKU_MIN_ORDER else orders / clicks
            if budget_consume_rate / time_pass_rate < CAMPAIGN_BUDGET_CONSUME_RATE:
                bid_co = DAILYBID_NOT_FULL_BID_CO[min(int(bid/0.5), 3)]
            else:
                bid_co = DAILYBID_FULL_BID_CO[min(int(bid/0.5), 3)]
                impressions, clicks, orders, cost, sales = report[targetId]['impressions'], report[targetId]['clicks'], report[
                    targetId]['attributedUnitsOrdered7d'], report[targetId]['cost'], report[targetId]['attributedSales7d']
                if clicks >= DAILYBID_MINCLICK[min(int(time_pass_rate/0.25), 3)]:
                    ctr, cvr, acos = clicks / impressions, orders / \
                        clicks, cost / sales if sales > 0 else 3
                    bid_co = dailybid_head_layer(
                        ctr, cvr, acos, avg_ctr, avg_cvr, target_acos)
            new_bid = max(bid * bid_co, MIN_BID)
            new_bid = min(get_max_bid(skus, product_info,
                          target_ctr, target_cvr), new_bid)
            if abs(new_bid - bid) < BID_CHANGE_MIN_STEP:
                continue
            target['new_bid'] = round(new_bid, 2)
            res.append(target)
    return res


def get_report(data_dir):
    campaign_data = json.load(open(os.path.join(data_dir, 'campaign.json')))
    campaign_report = extract_campaign_data(campaign_data)
    keywords_data = json.load(open(os.path.join(data_dir, 'keyword.json')))
    keyword_report = extract_keyword_data(keywords_data)
    traget_data = json.load(open(os.path.join(data_dir, 'targeting.json')))
    target_report = extract_target_data(traget_data)
    return campaign_report, keyword_report, target_report


def max_bix_ctr_layer(x):
    a, b, c, d, m = MAX_BID_CTR
    return d + (a-d) / (1+(x/c)**b)**m


def max_bix_cvr_layer(x):
    a, b, c, d, m = MAX_BID_CVR
    return d + (a-d) / (1+(x/c)**b)**m


def max_bix_head_layer(x):
    a, b, c, d, m = MAX_BID_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def max_bid_layer(x, ctr, cvr):
    ctr_co = max_bix_ctr_layer(ctr)
    cvr_co = max_bix_cvr_layer(cvr)
    head_layer = max_bix_head_layer(x)
    return ctr_co * cvr_co * head_layer


def get_max_bid(skus, product_info, ctr, cvr):
    price, profit, promotionTarget = 0, 0, -1
    for sku in skus:
        if sku not in product_info: continue
        price += product_info[sku]['price']
        profit += product_info[sku]['price'] * product_info[sku]['macs']
        promotionTarget = min(
            promotionTarget, product_info[sku]['promotionTarget'])
    ads_fee = PROMOTION_CO[promotionTarget] * profit / len(skus)
    max_bid = max_bid_layer(ads_fee, ctr, cvr) * 0.68
    return max_bid


def cls_ctr_layer(x):
    a, b, c, d, m = CLASS_CTR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def cls_cvr_layer(x):
    a, b, c, d, m = CLASS_CVR_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def cls_acos_layer(x):
    a, b, c, d, m = CLASS_ACOS_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def get_st_score(ctr, cvr, acos, avg_ctr, avg_cvr, target_acos):
    ctr_co = cls_ctr_layer(ctr/avg_ctr)
    cvr_co = cls_cvr_layer(cvr/avg_cvr)
    acos_co = cls_acos_layer(acos/target_acos)
    return ctr_co * cvr_co * acos_co * cvr


def negative_minclick_layer(x):
    a, b, c, d, m = NEGATIVEMINCLICK_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def st_classifier(searchterms, sku_keywords, ads_performance, searchterm_performance, product_info):
    negative_searchterm, good_performance_keywords = [], []
    for searchtermId, searchterm in searchterms.items():
        skus = searchterm['sku']
        found = False
        for sku in skus:
            if sku in product_info:
                found = True
        if not found:
            continue
        price, profit, avg_ctr, avg_cvr, target_acos, promotionTarget = get_ads_metric(
            skus, product_info, ads_performance)
        searchterm_format = searchterm['format']
        impressions, clicks, orders, cost, sales = get_skus_data_from_searchterm_performance(
            skus, searchterm_format, searchterm_performance)
        if clicks == 0 or impressions == 0:
            continue
        ctr, cvr, acos = clicks / impressions, orders / \
            clicks, cost / sales if sales > 0 else 3
        st_score = get_st_score(ctr, cvr, acos, avg_ctr, avg_cvr, target_acos)
        if clicks > STOPTMINCLICK[promotionTarget] and st_score > SEARCHTERM_MAXCVR[promotionTarget]:
            print('positive', searchterm['campaignName'], skus, searchterm['query'], '{:.2%}'.format(st_score), '{:.2%}'.format(
                ctr), '{:.2%}'.format(cvr), '{:.2%}'.format(acos), clicks, orders, "%.2f" % cost, sales)
            if searchterm['type'] == 'keyword':
                targetMatchType = []
                if st_score > SEARCHTERM_BROADCVR[promotionTarget]:
                    targetMatchType = ['exact', 'broad']
                else:
                    targetMatchType = ['exact', 'phrase']
                if promotionTarget == 3:
                    targetMatchType = ['broad']  # 清仓的产品不考虑加权, 全部broad
                searchterm['targetMatchType'] = targetMatchType
            basic_price = price * target_acos / len(skus)
            bid_co = bidopt_head_layer(
                ctr, cvr, acos, avg_ctr, avg_cvr, target_acos)
            new_bid = round(basic_price * cvr * bid_co, 2)
            if new_bid < MIN_BID:
                new_bid = MIN_BID
            max_bid = get_max_bid(skus, product_info, ctr, cvr)
            if new_bid > max_bid:
                new_bid = max_bid
            searchterm['new_bid'] = new_bid
            good_performance_keywords.append(searchterm)
        elif clicks > negative_minclick_layer(ctr/avg_ctr) * STNEGATIVEMINCLICK[promotionTarget] and st_score < SEARCHTERM_MINCVR[promotionTarget]:
            print('negative', skus, searchterm['query'], '{:.2%}'.format(st_score), '{:.2%}'.format(
                ctr), '{:.2%}'.format(cvr), '{:.2%}'.format(acos), clicks, orders, "%.2f" % cost, sales)
            negative_searchterm.append(searchterm)
    return negative_searchterm, good_performance_keywords

def target_exist(skus, sku_keywords, searchterm_format, matchType):
    for sku in skus:
        if sku not in sku_keywords:
            return False
        if searchterm_format not in sku_keywords[sku]:
            return False
        if matchType != 'asin' and matchType not in sku_keywords[sku][searchterm_format]:
            return False
    return True


def dailybid(opt):
    today_dir = os.path.join(opt.data_path, get_past_days(1)[0])
    if not os.path.exists(today_dir):
        return 'not updated'
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    product_acos_path = os.path.join(opt.data_path, 'product_acos.json')
    if not os.path.exists(product_acos_path):
        return
    product_info, ads_performance, target_performance, searchterm_performance, keywords, targets, adGroup_info, campaign_info, campaign_sku = bid_preprocessc(
        opt, statistic_dir, product_acos_path)
    bid_result = dailybidOpt(product_info, campaign_sku, ads_performance, target_performance, searchterm_performance,
                             today_dir, keywords, targets, campaign_info, adGroup_info)
    result_dir = os.path.join(opt.data_path, 'result')
    write_obj_to_json(bid_result, os.path.join(result_dir, 'dailybid.json'))


def get_searchterm_impression_distribution(searchterms):
    res = []
    for searchterm, performance in searchterms.items():
        res.append(performance['total'][0])
    return res


def get_big_word(bid_words_min_impression, searchterms):
    res = []
    for searchterm, performance in searchterms.items():
        if performance['type'] != 'keyword':
            continue
        total = performance['total']
        if total[2] == 0:
            continue  # 如果没有成交
        if total[0] > bid_words_min_impression:
            res.append([searchterm]+performance['total'])
    return res


def get_big_words(searchterm_performance, product_info):
    res = {}
    for sku, searchterms in searchterm_performance.items():
        if sku not in product_info:
            continue
        res[sku] = []
        impression_distribution = get_searchterm_impression_distribution(
            searchterms)
        bid_words_min_impression = max(
            BID_WORD_MIN_IMPRESSION, np.percentile(impression_distribution, 80))
        res[sku] = get_big_word(bid_words_min_impression, searchterms)
    return res


def get_word_from_searchterms(searchterms):
    res = {
        'adj': {},
        'noun': {}
    }
    for searchterm, performance in searchterms.items():
        if performance['type'] != 'keyword':
            continue
        total = performance['total']
        if total[2] == 0:
            continue  # 如果没有成交
        adj, noun = get_parts_of_speech(searchterm)
        for word in adj:
            if word not in res['adj']:
                res['adj'][word] = [0, 0, 0, 0, 0]
            res['adj'][word] = list(map(add, res['adj'][word], total))
        for word in noun:
            if word not in res['noun']:
                res['noun'][word] = [0, 0, 0, 0, 0]
            res['noun'][word] = list(map(add, res['noun'][word], total))
    return res


def get_word_statistic(searchterm_performance, product_info):
    res = {}
    for sku, searchterms in searchterm_performance.items():
        if sku not in product_info:
            continue
        res[sku] = get_word_from_searchterms(searchterms)
    return res


def word_ponint_layer(x):
    a, b, c, d, m = WORD_POINT_LAYER
    return d + (a-d) / (1+(x/c)**b)**m


def word_point_head(x):
    a, b, c, d, m = WORD_POINT_HEAD
    return d + (a-d) / (1+(x/c)**b)**m


def calculate_word_point(performance):
    impressions, clicks, orders, spends, sales = performance
    ctr, cvr, acos = clicks / impressions if impressions > 0 else 1, orders / clicks if clicks > 0 else 1, spends / sales if spends > 0 else 0.01
    ctr_co = WORD_POINT_CTR_CO * word_ponint_layer(ctr/DEFAULT_CTR)
    cvr_co = WORD_POINT_CVR_CO * word_ponint_layer(cvr/get_proper_cvr(sales/orders))
    acos_co = WORD_POINT_ACOS_CO * word_ponint_layer(DEFAULT_ACOS/acos)
    return word_point_head((ctr_co * cvr_co * acos_co)/(WORD_POINT_CTR_CO*WORD_POINT_CVR_CO*WORD_POINT_ACOS_CO))


def get_recommend_word(big_words, word_statistic, sku_keywords):
    res = {}
    for sku, big_word_info in big_words.items():
        res[sku] = []
        if sku not in word_statistic:
            continue
        for word_info in big_word_info:
            word, info = word_info[0], word_info[1:]
            word_point = calculate_word_point(info)
            for a, performance in word_statistic[sku]['adj'].items():
                if a in word:
                    continue
                phrase = '%s %s' % (a, word)
                if sku in sku_keywords and phrase in sku_keywords[sku]:
                    continue
                adj_point = calculate_word_point(performance)
                point = round(word_point * adj_point)
                res[sku].append(phrase + '-' + str(point))
            for n, performance in word_statistic[sku]['noun'].items():
                if n in word:
                    continue
                phrase = '%s %s' % (word, n)
                if sku in sku_keywords and phrase in sku_keywords[sku]:
                    continue
                noun_point = calculate_word_point(performance)
                point = round(word_point * noun_point)
                res[sku].append(phrase + '-' + str(point))
    return res


def wordRecommend(opt):
    result_dir = os.path.join(opt.data_path, 'result')
    statistic_dir = os.path.join(opt.data_path, 'statistic')
    searchterm_performance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    sku_keywords = json.load(
        open(os.path.join(statistic_dir, 'sku_keywords.json')))
    product_acos_path = os.path.join(opt.data_path, 'product_acos.json')
    if not os.path.exists(product_acos_path):
        return
    product_info = json.load(
        open(os.path.join(opt.data_path, 'product_acos.json')))
    big_words = get_big_words(searchterm_performance, product_info)
    word_statistic = get_word_statistic(searchterm_performance, product_info)
    recommend_word = get_recommend_word(
        big_words, word_statistic, sku_keywords)
    write_obj_to_json(recommend_word, os.path.join(
        result_dir, 'recommendWord.json'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", help="data path", type=str)
    parser.add_argument("task", help="optimization or bid", type=str)
    opt = parser.parse_args()

    if opt.task == 'searchtermOpt':
        searchtermOpt(opt)
    elif opt.task == 'targetOpt':
        targetOpt(opt)
    elif opt.task == 'dailybid':
        dailybid(opt)
    elif opt.task == 'dataprocess':
        process(opt)
    elif opt.task == 'bidopt':
        bidOpt(opt)
    elif opt.task == 'budgetOpt':
        budgetOpt(opt)
    elif opt.task == 'wordRecommend':
        wordRecommend(opt)
