from celery import shared_task, group, chain
from .apiservice import *
from .amzapi import AmzapiHandler
from .models import *
from .weights import *
from .utils import *

MAXRETRY = 7
FILTER = {'stateFilter': 'enabled,paused,archived'}


@shared_task
def SyncReport_optimize_bid_budget_byProfile(shopId, profileId, profile_dir, reportDates):
    struct = group(syncProfilePortfolioData.si(shopId, profileId), syncProfileCampaignData.si(shopId, profileId, profile_dir),
                   syncProfileAdGroupData.si(shopId, profileId, profile_dir), syncProfileProductAdData.si(
                       shopId, profileId, profile_dir),
                   syncProfileKeywordData.si(shopId, profileId, profile_dir), syncProfileTargetData.si(
                       shopId, profileId, profile_dir),
                   syncProfileNegativeKeywordData.si(
                       shopId, profileId, profile_dir), syncProfileCampaignNegativeKeywordData.si(shopId, profileId, profile_dir),
                   syncProfileNegativeTargetsData.si(shopId, profileId, profile_dir))

    report = group(group(getCampaignReport.si(shopId, profileId, date, os.path.join(profile_dir, date)),
                         getKeywordReport.si(
                             shopId, profileId, date, os.path.join(profile_dir, date)),
                         getTargetReprot.si(
                             shopId, profileId, date, os.path.join(profile_dir, date)),
                         getProductAdsReport.si(shopId, profileId, date, os.path.join(profile_dir, date))) for date in reportDates)

    syncData = group(struct, report)

    opt = group(updateCampaignBudgetByProfile.si(shopId, profileId),
                dailyBidByProfile.si(shopId, profileId))

    res = chain(syncData, optimize.si(shopId, profileId, 'dataprocess'), opt)()
    return res


@shared_task
def SyncReport_optimize_bid_budget(day):
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        region = shop.region
        reportDates = get_past_days(day, region)
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        shop_dir = os.path.join(BASE_DIR, str(shopId))
        if not os.path.exists(shop_dir):
            os.mkdir(shop_dir)
        for profile in profiles:
            profileId = profile.profileId
            profile_dir = os.path.join(shop_dir, profileId)
            if not os.path.exists(profile_dir):
                os.mkdir(profile_dir)
            for date in reportDates:
                date_dir = os.path.join(profile_dir, date)
                if not os.path.exists(date_dir):
                    os.mkdir(date_dir)
            SyncReport_optimize_bid_budget_byProfile.delay(
                str(shopId), profileId, profile_dir, reportDates)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfilePortfolioData(self, shopId, profileId):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        portfolios = amzapi.get_portfolios()
        CreateOrUpdatePortfolios(portfolios, profileId)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileCampaignData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        campaigns_snapshot = amzapi.get_snapshot('campaigns', FILTER)
        CreateOrUpdateCampaigns(campaigns_snapshot, profileId)
        json_to_local(campaigns_snapshot, os.path.join(
            profile_dir, 'campaigns.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileAdGroupData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        adgroups_snapshot = amzapi.get_snapshot('adGroups', FILTER)
        CreateOrUpdateAdGroups(adgroups_snapshot, profileId)
        json_to_local(adgroups_snapshot, os.path.join(
            profile_dir, 'adGroups.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileProductAdData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        productads_snapshot = amzapi.get_snapshot('productAds', FILTER)
        json_to_local(productads_snapshot, os.path.join(
            profile_dir, 'productAds.json'))
        CreateOrUpdateProductAds(productads_snapshot, profileId)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileKeywordData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        keywords_snapshot = amzapi.get_snapshot('keywords', FILTER)
        CreateOrUpdateKeywords(keywords_snapshot, profileId)
        json_to_local(keywords_snapshot, os.path.join(
            profile_dir, 'keywords.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileTargetData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        targetings_snapshot = amzapi.get_snapshot('targets', FILTER)
        CreateOrUpdateTargetings(targetings_snapshot, profileId)
        json_to_local(targetings_snapshot, os.path.join(
            profile_dir, 'targets.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileNegativeKeywordData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        negativeKeywords_snapshot = amzapi.get_snapshot(
            'negativeKeywords', FILTER)
        CreateOrUpdateNegativeKeywords(negativeKeywords_snapshot, profileId)
        json_to_local(negativeKeywords_snapshot, os.path.join(
            profile_dir, 'negativeKeywords.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileCampaignNegativeKeywordData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        campaignNegativeKeywords_snapshot = amzapi.get_snapshot(
            'campaignNegativeKeywords', FILTER)
        CreateOrUpdateCampaignNegativeKeywords(
            campaignNegativeKeywords_snapshot, profileId)
        json_to_local(campaignNegativeKeywords_snapshot, os.path.join(
            profile_dir, 'campaignNegativeKeywords.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def syncProfileNegativeTargetsData(self, shopId, profileId, profile_dir):
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        negativeTargets_snapshot = amzapi.get_snapshot(
            'negativeTargets', FILTER)
        CreateOrUpdateNegativeTargets(negativeTargets_snapshot, profileId)
        json_to_local(negativeTargets_snapshot, os.path.join(
            profile_dir, 'negativeTargets.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def syncProfileData(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    if not os.path.exists(shop_dir):
        os.mkdir(shop_dir)
    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)

    # create or update portfolio
    syncProfilePortfolioData.delay(shopId, profileId)

    # create or update campaigns
    syncProfileCampaignData.delay(shopId, profileId, profile_dir)

    # create or update adGroups
    syncProfileAdGroupData.delay(shopId, profileId, profile_dir)

    # create or update productAds
    syncProfileProductAdData.delay(shopId, profileId, profile_dir)

    # create or update keywords
    syncProfileKeywordData.delay(shopId, profileId, profile_dir)

    # create or update targetings
    syncProfileTargetData.delay(shopId, profileId, profile_dir)

    # get negativeKeywords
    syncProfileNegativeKeywordData.delay(shopId, profileId, profile_dir)

    # get negativeCampaignKeywords
    syncProfileCampaignNegativeKeywordData.delay(
        shopId, profileId, profile_dir)

    # get negativeTargets
    syncProfileNegativeTargetsData.delay(shopId, profileId, profile_dir)


def save_product_info(profileId, profile_dir):
    product_acos = {}
    profile_product = ShopProducts.objects.filter(profileId=profileId).exclude(state=2)
    for product in profile_product:
        sku = product.sku
        if sku not in product_acos:
            product_acos[sku] = {
                'price': round(float(product.price), 2),
                'macs': round(float(product.macs),2),
                'promotionTarget': product.promotionTarget
            }
    json_to_local(product_acos, os.path.join(profile_dir, 'product_acos.json'))


@shared_task
def SyncReport(day):
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        region = shop.region
        dates = get_past_days(day, region)
        if day > 1:
            dates = dates[1:]
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        for profile in profiles:
            shopId = str(shopId)
            profileId = profile.profileId
            SynchronizeReportData.delay(shopId, profileId, dates)

@shared_task
def SyncShopReport(shopId, day):
    region = Shop.objects.get(id=int(shopId)).region
    dates = get_past_days(day, region)
    profiles = Profile.objects.filter(shop_id=shopId, state=1)
    for profile in profiles:
        shopId = str(shopId)
        profileId = profile.profileId
        print(shopId, profileId, dates)
        SynchronizeReportData.delay(shopId, profileId, dates)


@shared_task
def SyncProfileReport(profileId, day):
    shopId = Profile.objects.get(profileId=str(profileId)).shop.id
    region = Shop.objects.get(id=int(shopId)).region
    dates = get_past_days(day, region)
    print(shopId, region, dates)
    SynchronizeReportData.delay(shopId, profileId, dates)

@shared_task(bind=True, max_retries=MAXRETRY)
def getCampaignReport(self, shopId, profileId, date, data_dir):
    data = {
        'reportDate': date,
        'metrics': ','.join(
            ['campaignName',
             'campaignId',
             'campaignStatus',
             'campaignBudget',
             'campaignRuleBasedBudget',
             'impressions',
             'clicks',
             'cost',
             'attributedConversions7d',
             'attributedUnitsOrdered7d',
             'attributedSales7d',
             'attributedConversions7dSameSKU',
             'attributedSales7dSameSKU',
             'attributedUnitsOrdered7dSameSKU']
        )
    }
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        campaign_report = amzapi.get_report('campaigns', data)
        json_to_local(campaign_report, os.path.join(data_dir, 'campaign.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def getKeywordReport(self, shopId, profileId, date, data_dir):
    data = {
        'reportDate': date,
        'metrics': ','.join(
            ['campaignName',
             'campaignId',
             'adGroupName',
             'adGroupId',
             'keywordId',
             'keywordText',
             'matchType',
             'impressions',
             'clicks',
             'cost',
             'attributedConversions7d',
             'attributedUnitsOrdered7d',
             'attributedSales7d',
             'attributedConversions7dSameSKU',
             'attributedSales7dSameSKU',
             'attributedUnitsOrdered7dSameSKU']
        )
    }
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        keyword_report = amzapi.get_report('keywords', data)
        data['segment'] = 'query'
        keyword_query_report = amzapi.get_report('keywords', data)
        json_to_local(keyword_report, os.path.join(data_dir, 'keyword.json'))
        json_to_local(keyword_query_report, os.path.join(
            data_dir, 'keyword-query.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def getTargetReprot(self, shopId, profileId, date, data_dir):
    # campaign data
    data = {
        'reportDate': date,
        'metrics': ','.join(
            ['campaignName',
             'campaignId',
             'adGroupName',
             'adGroupId',
             'targetId',
             'targetingExpression',
             'targetingText',
             'targetingType',
             'impressions',
             'clicks',
             'cost',
             'attributedConversions7d',
             'attributedUnitsOrdered7d',
             'attributedSales7d',
             'attributedConversions7dSameSKU',
             'attributedSales7dSameSKU',
             'attributedUnitsOrdered7dSameSKU']
        )
    }
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        targeting_report = amzapi.get_report('targets', data)
        data['segment'] = 'query'
        targeting_query_report = amzapi.get_report('targets', data)
        json_to_local(targeting_report, os.path.join(
            data_dir, 'targeting.json'))
        json_to_local(targeting_query_report, os.path.join(
            data_dir, 'targeting-query.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=MAXRETRY)
def getProductAdsReport(self, shopId, profileId, date, data_dir):
    data = {
        'reportDate': date,
        'metrics': ','.join(
            ['campaignName',
             'campaignId',
             'adGroupName',
             'adGroupId',
             'impressions',
             'clicks',
             'cost',
             'asin',
             'sku',
             'attributedConversions7d',
             'attributedUnitsOrdered7d',
             'attributedSales7d',
             'attributedConversions7dSameSKU',
             'attributedSales7dSameSKU',
             'attributedUnitsOrdered7dSameSKU']
        )
    }
    try:
        amzapi = AmzapiHandler(shopId, profileId)
        productAds_report = amzapi.get_report('productAds', data)
        json_to_local(productAds_report, os.path.join(
            data_dir, 'productAds.json'))
        # data['segment'] = 'query'
        # productAds_query_report = amzapi.get_report('productAds', data)
        # json_to_local(productAds_query_report, os.path.join(data_dir, 'productAds-query.json'))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def SynchronizeReportData(shopId, profileId, reportDates):
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    shop_dir = os.path.join(BASE_DIR, shopId)
    if not os.path.exists(shop_dir):
        os.mkdir(shop_dir)
    profile_dir = os.path.join(shop_dir, profileId)
    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)

    for date in reportDates:
        date_dir = os.path.join(profile_dir, date)
        if not os.path.exists(date_dir):
            os.mkdir(date_dir)
    print(reportDates)
    for date in reportDates:
        print('fetching data at %s for shop: %s profile: %s' %
              (date, shopId, profileId))
        data_dir = os.path.join(profile_dir, date)
        getCampaignReport.delay(shopId, profileId, date, data_dir)
        getKeywordReport.delay(shopId, profileId, date, data_dir)
        getTargetReprot.delay(shopId, profileId, date, data_dir)
        getProductAdsReport.delay(shopId, profileId, date, data_dir)


def getUpdatedCampaign(profileId, campaigns):
    res = []
    for campaignId, campaign in campaigns.items():
        if 'newBudget' not in campaign:
            continue
        campaign_obj = Campaign.objects.get(campaignId=campaignId)
        if not campaign_obj.deposite:
            continue
        newBudget = campaign['newBudget']
        campaignId = campaign['campaignId']
        res.append({
            "campaignId": int(campaignId),
            "dailyBudget": newBudget
        })
        campaign_obj.dailyBudget = newBudget
        campaign_obj.save()
        saveChangeLog(profileId, '广告活动:%s 预算由%s 改成%s' % (
            campaign_obj.name, campaign['campaignBudget'], newBudget), 'campaignBudget')
    return res


@shared_task
def updateCampaignBudgetByProfile(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    result_dir = os.path.join(profile_dir, 'result')
    analyzer_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    command = 'python %s %s budgetOpt' % (analyzer_path, profile_dir)
    print(command)
    os.system(command)
    amzapi = AmzapiHandler(shopId, profileId)
    campaigns = json.load(open(os.path.join(result_dir, 'budgetOpt.json')))
    updatedCampaigns = getUpdatedCampaign(profileId, campaigns)
    if len(updatedCampaigns) == 0:
        return 'no need to update'
    res = amzapi.update_campaigns(updatedCampaigns)
    return res


@shared_task
def updateCampaignBudget():
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        region = shop.region
        date = get_current_pst_time(region)
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        for profile in profiles:
            shopId = str(shopId)
            profileId = profile.profileId
            print('开始优化预算 shop:%s, profiles:%s 日期:%s' %
                  (shopId, profileId, date))
            res = updateCampaignBudgetByProfile.delay(shopId, profileId)
            print(res)
    return res


def getUpdatedTarget(profileId, targets):
    post_targets, post_keywords = [], []
    for target in targets:
        if 'new_bid' not in target:
            continue
        campaignId = target['campaignId']
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=str(campaignId))
        if not campaign.deposite:
            continue
        campaignName = campaign.name
        adGroupId = target['adGroupId']
        ads = ProductAds.objects.filter(
            profileId=profileId, adGroupId=adGroupId)
        allFound = True
        for ad in ads:
            sku = ad.sku
            shopproduct = ShopProducts.objects.filter(
                profileId=profileId, sku=sku).first()
            if not shopproduct or shopproduct.state not in [1, 3, 4, 5]:
                allFound = False
        if not allFound:
            continue
        new_bid = target['new_bid']
        bid = target['bid'] if 'bid' in target else 'None'
        adgroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        adGroupName = adgroup.name
        if 'matchType' in target:
            targetId = target['keywordId']
            post_keywords.append({
                "keywordId": targetId,
                "state": 'enabled',
                "bid": new_bid
            })
            keyword_obj = Keyword.objects.get(
                profileId=profileId, adGroupId=adGroupId, keywordId=str(targetId))
            keyword_obj.bid = new_bid
            keyword_obj.save()
            targetType = target['matchType']
            targetName = target['keywordText']
        else:
            targetId = target['targetId']
            post_targets.append({
                "targetId": targetId,
                "state": 'enabled',
                "bid": new_bid
            })
            target_obj = Target.objects.get(
                profileId=profileId, adGroupId=adGroupId, targetId=str(targetId))
            target_obj.bid = new_bid
            target_obj.save()
            targetType = target['expressionType']
            targetName = target['expression'][0]['value'] if targetType == 'manual' else target['expression'][0]['type']
        log = '%s %s %s %s竞价由%s -> %s' % (campaignName,
                                          adGroupName, targetName, targetType, bid, new_bid)
        print(log)
        saveChangeLog(profileId, log, 'dailybid')
    return post_targets, post_keywords


@shared_task
def dailyBidByProfile(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    save_product_info(profileId, profile_dir)
    result_dir = os.path.join(profile_dir, 'result')
    analyzer_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    command = 'python %s %s dailybid' % (analyzer_path, profile_dir)
    print(command)
    os.system(command)
    amzapi = AmzapiHandler(shopId, profileId)
    targets = json.load(open(os.path.join(result_dir, 'dailybid.json')))
    post_targets, post_keywords = getUpdatedTarget(profileId, targets)
    if len(post_keywords) > 0:
        res1 = amzapi.update_keywords(post_keywords)
        print(res1)
    else:
        print('no keyword need to update')
    if len(post_targets) > 0:
        res2 = amzapi.update_taregets(post_targets)
        print(res2)
    else:
        print('no target need to update')


@shared_task
def dailyBid():
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        region = shop.region
        date = get_current_pst_time(region)
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        for profile in profiles:
            shopId = str(shopId)
            profileId = profile.profileId
            print('开始优化投放目标竞价 shop:%s, profiles:%s 日期:%s' %
                  (shopId, profileId, date))
            dailyBidByProfile.delay(shopId, profileId)


@shared_task
def bidopt(shopId, profileId, profile_dir):
    post_targets, post_keywords = [], []
    bid_result = json.load(
        open(os.path.join(profile_dir, 'result', 'bid.json')))
    for target in bid_result:
        campaignId = target['campaignId']
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId)
        if not campaign.deposite:
            continue
        campaignName = campaign.name
        adGroupId = target['adGroupId']
        adgroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        ads = ProductAds.objects.filter(profileId=profileId, adGroupId=adGroupId)
        allFound = True
        for ad in ads:
            sku = ad.sku
            shopproduct = ShopProducts.objects.get(
                profileId=profileId, sku=sku)
            if shopproduct.state not in [1, 3, 4, 5]:
                allFound = False
        if not allFound:
            continue
        adGroupName = adgroup.name
        bid = target['bid'] if 'bid' in target else None
        new_bid = target['new_bid']
        target_type = ''
        targetId = ''
        if 'matchType' in target:
            target_type = target['matchType']
            targetId = target['keywordId']
            targetName = target['keywordText']
        elif 'expressionType' in target:
            targetId = target['targetId']
            if target['expressionType'] == 'manual':
                target_type = 'asin'
                targetName = target['expression'][0]['value']
            elif target['expressionType'] == 'auto':
                target_type = 'auto'
                targetName = target['expression'][0]['type']
            else:
                print('type error')
        if target_type in ['exact', 'phrase', 'broad']:
            post_keywords.append({
                "keywordId": targetId,
                "state": 'enabled',
                "bid": new_bid
            })
            keyword_obj = Keyword.objects.get(
                profileId=profileId, adGroupId=adGroupId, keywordId=str(targetId))
            keyword_obj.bid = new_bid
            keyword_obj.save()
        elif target_type in ['asin', 'auto']:
            post_targets.append({
                "targetId": targetId,
                "state": 'enabled',
                "bid": new_bid
            })
            target_obj = Target.objects.get(
                profileId=profileId, adGroupId=adGroupId, targetId=str(targetId))
            target_obj.bid = new_bid
            target_obj.save()
        log = '%s: %s: %s - %s竞价由%s 调整为 %s' % (campaignName,
                                               adGroupName, targetName, target_type, bid, new_bid)
        saveChangeLog(profileId, log, 'bid')
    amzapi = AmzapiHandler(shopId, profileId)
    if len(post_keywords) > 0:
        res = amzapi.update_keywords(post_keywords)
        print(res)
        if 'code' in res and res['code'] != 200:
            return res['detail']
    if len(post_targets) > 0:
        res = amzapi.update_taregets(post_targets)
        print(res)
        if 'code' in res and res['code'] != 200:
            return res['detail']
    return 'success'


@shared_task
def optimize(shopId, profileId, OptType):
    shop_dir = os.path.join(BASE_DIR, str(shopId))
    profile_dir = os.path.join(shop_dir, str(profileId))
    analyzer_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    save_product_info(profileId, profile_dir)
    command = 'python %s %s %s' % (analyzer_path, profile_dir, OptType)
    print(command)
    os.system(command)
    print('%s %s, task done' % (shopId, profileId))
    if OptType == 'bidopt':
        bidopt.delay(shopId, profileId, profile_dir)


@shared_task
def Optimization(OptType):
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        for profile in profiles:
            shopId = str(shopId)
            profileId = profile.profileId
            optimize.delay(shopId, profileId, OptType)


@shared_task
def ShopInit(shopId):
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    profiles = Profile.objects.filter(shop_id=shopId, state=1)
    for profile in profiles:
        shopId = str(shopId)
        profileId = profile.profileId
        profileInit.delay(shopId, profileId)


@shared_task
def profileInit(shopId, profileId):
    syncProfileData.delay(shopId, profileId)
    region = Shop.objects.get(id=int(shopId)).region
    dates = get_past_days(59, region)
    SynchronizeReportData.delay(shopId, profileId, dates)


@shared_task
def Check():
    shops = Shop.objects.filter(state=1)
    date = get_current_pst_time('NA')
    print('太平洋时间为%s' % date)
    for shop in shops:
        shopId = shop.id
        profiles = Profile.objects.filter(shop_id=shopId, state=1)
        for profile in profiles:
            shopId = str(shopId)
            profileId = profile.profileId
            checkCampaign.delay(shopId, profileId)


@shared_task
def checkCampaign(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    campaign_path = os.path.join(profile_dir, 'campaigns.json')
    if not os.path.exists(campaign_path):
        return
    campaign_list = json.load(open(campaign_path))
    campaignIds = get_product_campaigns(profileId)
    updated_campaigns = []
    # check campaign bidding strategy
    for campaign in campaign_list:
        if campaign['state'] == 'archived':
            continue
        campaignId = str(campaign['campaignId'])
        if campaignId not in campaignIds:
            continue
        strategy = campaign['bidding']['strategy']
        if strategy != 'legacyForSales':
            updated_campaigns.append({
                'campaignId': campaignId,
                'bidding': {
                    'strategy': 'legacyForSales',
                    'adjustments': []
                }
            })
    if len(updated_campaigns) == 0:
        return 'no need to update'
    amzapi = AmzapiHandler(shopId, profileId)
    campaigns = []
    campaign_responses = amzapi.update_campaigns(updated_campaigns)
    print(campaign_responses)
    for res in campaign_responses:
        if res['code'] == 'SUCCESS':
            campaignId = res['campaignId']
            camp = amzapi.get_campaign_byId(campaignId)
            campaigns.append(camp)
            log = '将广告活动:%s 的竞价策略调整为:动态调整-只降低' % camp['name']
            saveChangeLog(profileId, log, 'struct')
    CreateOrUpdateCampaigns(campaigns, profileId)
    return res
