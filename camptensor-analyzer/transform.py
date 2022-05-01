from weights import *
from nlp import *
from operator import add, sub

def cvr_transform(targeting_type, targetings, ads_performance, weighted_performance, min_click):
    num1, num2, num3, num4, num5, num6 = 0, 0, 0, 0, 0, 0
    for targetId, target in targetings.items():
        num1 += 1
        if not target['sku'] or len(target['sku']) == 0:
            print('target %s has no sku' % targetId)
            continue
        impressions, clicks, orders, spends, sales, statistic = 0, 0, 0, 0, 0, []
        for sku in target['sku']:
            if sku not in weighted_performance:
                num2 += 1
                continue
            if target['type'] == 'auto': 
                num3 += 1
                continue
            if target['format'] not in weighted_performance[sku]:
                num4 += 1
                continue
            impression, click, order, spend, sale = weighted_performance[sku][target['format']]
            statistic += ads_performance['sku'][sku]['target_impressions_distribution'] if targeting_type == 'targeting' else ads_performance['sku'][sku]['search_impressions_distribution']

            # 同一个targeting绑定多组sku
            impressions = impression if impressions == 0 else min(impression, impressions)
            clicks = click if clicks == 0 else min(clicks, click)
            orders = order if orders == 0 else min(orders, order)
            spends = spend if spends == 0 else min(spends, spend)
            sales = sale if sales == 0 else min(sales, sale)

        if impressions == 0: 
            num5 += 1
            continue
        if clicks < min_click: 
            num6 += 1
            continue

        # 计算平均指标
        try:
            ctr, cvr, roi = clicks / impressions, orders / clicks, sales / spends
            impression_mean = remove_isolation(statistic) # 消除impression离群值, 方便计算impression均值
            impressions_total = sum([ads_performance['sku'][sku]['impressions'] for sku in target['sku']])
            clicks_total = sum([ads_performance['sku'][sku]['clicks'] for sku in target['sku']])
            orders_total = sum([ads_performance['sku'][sku]['orders'] for sku in target['sku']])
            spends_total = sum([ads_performance['sku'][sku]['spends'] for sku in target['sku']])
            sales_total = sum([ads_performance['sku'][sku]['sales'] for sku in target['sku']])
            ctr_mean, cvr_mean, roi_mean = clicks_total / impressions_total, orders_total / clicks_total, sales_total / spends_total
        except Exception as e:
            print(e)
            print(sku, impressions, clicks, orders, spends, sales, impressions_total, clicks_total, spends_total, ctr_mean)

        target['cvr'] = cvr
        target['spends'] = spends
        target['sales'] = sales
        target['clicks'] = clicks
        target['orders'] = orders
        target['impressions'] = impressions
        target['impressionMean'] = impression_mean
        # target['id'] = targetId

        if sales_total == 0:
            target['cvr_predict'] = DEFAULT_CVR
        else:
            # 将当前target各指标和平均指标带入模型, 计算出新的cvr(抽象)
            cvr_weighted, imrco, roico, cvrco, ctrco, co = cls_layer(ctr, cvr, roi, impressions, ctr_mean, cvr_mean, roi_mean, impression_mean)
            target['co'] = [imrco, roico, cvrco, ctrco, co]
            target['cvr_predict'] = cvr_weighted   
    print(num1, num2, num3, num4, num5, num6)

# def get_mean_cvr(sku_list, ads_performance):
#     orders, clicks = 0, 0
#     for sku in sku_list:
#         if sku not in ads_performance['sku']: continue
#         orders += ads_performance['sku'][sku]['orders']
#         clicks += ads_performance['sku'][sku]['clicks']
#     if clicks < DEFAULT_MINCLICK: return DEFAULT_CVR
#     return max(orders / clicks, DEFAULT_CVR)

# def bid_ctr_layer(x):
#     a, b, c, d, m = BID_CTR_LAYER
#     return d + (a-d) / (1+(x/c)**b)**m
# def bidder(targetings, ads_performance, target_performance, product_acos):
#     for targetId, target in targetings.items():
#         skus = target['sku']
#         found = True
#         # 如果一个活动包含我们不做的SKU, 则不为该活动做自动竞价
#         for sku in skus:
#             if sku not in product_acos: found = False
#         if not found: continue
#         target_type = target['type']
#         target_format = target['format']
#         basic_bid = 0
#         for sku in skus:
#             price, macs, promotionPurpose = product_acos[sku].values()
#             if target_type == 'auto': target_format = 'auto-%s' % targetId
#             if target_format not in target_performance[sku]: 
#                 # print(sku, '欠曝光',target_format)
#                 continue
#             impressions, clicks, orders, costs, sales = target_performance[sku][target_format]['total']
#             if clicks < TARGETING_MINCLICK:
#                 if sku not in ads_performance['sku'] or ads_performance['sku'][sku]['orders'] == 0:
#                     cvr = DEFAULT_CVR
#                 else:
#                     cvr = ads_performance['sku'][sku]['orders'] / ads_performance['sku'][sku]['clicks']
#             else:
#                 if orders == 0:
#                     cvr = MIN_CVR
#                 else:
#                     cvr = orders / clicks
#             if sku not in ads_performance['sku'] or ads_performance['sku'][sku]['impressions'] < 500:
#                 ctr_avg = DEFAULT_CTR
#             else:
#                 ctr_avg = ads_performance['sku'][sku]['clicks'] / ads_performance['sku'][sku]['impressions']
#             if clicks > 3 and impressions > 300:
#                 ctr = clicks / impressions
#             else:
#                 ctr = ctr_avg
#             new_price = price * macs * cvr * PROMOTION_CO[promotionPurpose] * bid_ctr_layer(ctr / ctr_avg)
#             print(sku, price, macs, target_format, 'cvr:%.2f%%' % (cvr * 100), promotionPurpose, 'ctr:%.2f%%' % (ctr * 100), 'ctr avg:%.2f%%' % (ctr_avg * 100), new_price)
#             basic_bid += new_price
#         basic_bid /= len(skus)
#         print('origin price:%s -> final price: %s' % (target['bid'], basic_bid))

def extract_good_performance_keywords(weighted_performance, ads_performance):
    res = {}
    for sku, keywords in weighted_performance.items():
        res[sku] = {}
        impressions_total = ads_performance['sku'][sku]['impressions']
        clicks_total = ads_performance['sku'][sku]['clicks']
        orders_total = ads_performance['sku'][sku]['orders']
        spends_total = ads_performance['sku'][sku]['spends']
        sales_total = ads_performance['sku'][sku]['sales']
        if clicks_total == 0 or orders_total == 0: continue
        ctr_mean = clicks_total / impressions_total
        cvr_mean = orders_total / clicks_total
        roi_mean = sales_total / spends_total
        for keyword, performance in keywords.items():
            if len(keyword) > 2 and keyword[:2] == 'b0': continue
            impressions, clicks, orders, spends, sales = performance
            # if impressions < 100: continue
            # if orders < 2: continue
            if clicks < SEARCHTERM_MINCLICK: continue
            ctr, cvr, roi = clicks / impressions, orders / clicks, sales / spends
            cvr_weighted, imrco, roico, cvrco, ctrco, co = cls_layer(ctr, cvr, roi, impressions, ctr_mean, cvr_mean, roi_mean, 1)
            if cvr_weighted > SEARCHTERM_MAXCVR:
                res[sku][keyword] = performance
    return res

def keywordAnalyze(weighted_performance):
    res = {}
    for sku, keywords_performance in weighted_performance.items():
        res[sku] = {}
        for keyword, performance in keywords_performance.items():
            if '-' in keyword and len(keyword) > 4 and keyword.split('-')[0] == 'auto': continue
            words, keyworType = format_phrase(keyword)
            performance = performance + [0, 0, 0]
            if keyworType== 'asin': continue
            word = words.split(' ')
            for w in word:
                if w not in res[sku]: res[sku][w] = performance
                else:
                    res[sku][w] = list(map(add, performance, res[sku][w]))

    for sku, word_performance in res.items():
        pop_word = []
        for word, performance in word_performance.items():
            if performance[2] < 2:
                pop_word.append(word)
                continue
            performance[5] = performance[1] / performance[0]
            performance[6] = performance[2] / performance[1]
            performance[7] = performance[4] / performance[3]
        
        for word in pop_word:
            word_performance.pop(word)
        
        # d = sorted(word_performance.items(), key=lambda d:d[1][6], reverse=True)
        # print(d)

    return res


if __name__ == '__main__':
    print(cls_acos_layer(3.5))