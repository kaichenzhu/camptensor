from .tasks import *
import hashlib
import random
from .apiservice import *
from .amzapi import AmzapiHandler
from pytz import utc, timezone
from django.contrib.auth import get_user_model
User = get_user_model()

def GetBill(profileId, startBill, endBill):
    start_date = datetime(year=int(startBill[0:4]), month=int(startBill[4:6]), day=int(startBill[6:8]))
    end_date = datetime(year=int(endBill[0:4]), month=int(endBill[4:6]), day=int(endBill[6:8]))
    logs = CampaignStructChangeLog.objects.filter(profileId=profileId, add_date__range=(start_date, end_date), type='dailybid')
    for log in logs:
        print(log.changeLog)
    return 1


def GetAccountInfo(account, password):
    print(account, password)
    if password != 'Zkc87981523!': return 'not valid'
    user = User.objects.get(username=account)
    return user.password

def customFunc():
    adgroups = AdGroup.objects.all()
    for adgroup in adgroups:
        campaignId = adgroup.campaignId
        campaign = Campaign.objects.get(campaignId=campaignId)
        if 'ASIN' in campaign.name and adgroup.type != 'product':
            print('change %s adgroup type to product' % campaign.name)
            adgroup.type = 'product'
            adgroup.save()
        elif 'KEYWORD' in campaign.name and adgroup.type != 'keyword':
            print('change %s adgroup type to keyword' % campaign.name)
            adgroup.type = 'keyword'
            adgroup.save()

def deleteProduct(shopId, profileId, id):
    product = ShopProducts.objects.get(id=id)
    product.delete()


def getCampaignName(sku, profileId, campaignType, createdCampaignName):
    idx = 1
    if campaignType == 'auto':
        base = sku + '|AT|' + str(idx)
    elif campaignType == 'keyword':
        base = sku + '|KEYWORD|' + str(idx)
    elif campaignType == 'product':
        base = sku + '|ASIN|' + str(idx)
    while Campaign.objects.filter(profileId=profileId, name=base).exists() or base in createdCampaignName:
        idx += 1
        if campaignType == 'auto':
            base = sku + '|AT|' + str(idx)
        elif campaignType == 'keyword':
            base = sku + '|KEYWORD|' + str(idx)
        elif campaignType == 'product':
            base = sku + '|ASIN|' + str(idx)
    return base


def QuickCreateCampaign(data):
    shopId = data['shopId']
    region = Shop.objects.get(id=int(shopId)).region
    profileId = data['profileId']
    campaigns = data['campaigns']
    campaign_sku_target = {}
    Campaign_post_data = []
    AdGroup_post_data = []
    productAds_post_data = []
    keywords_post_data = []
    targets_post_data = []
    createdCampaignName = set()
    print(campaigns)
    for campaign in campaigns:
        sku = campaign['sku']
        budget = float(campaign['budget'])
        defaultBid = float(campaign['defaultBid'])
        campaignType = campaign['campaignType']
        exact = campaign['exact']
        phrase = campaign['phrase']
        broad = campaign['broad']
        campaignName = getCampaignName(
            sku, profileId, campaignType, createdCampaignName)
        createdCampaignName.add(campaignName)
        if campaignName not in campaign_sku_target:
            campaign_sku_target[campaignName] = {}
        campaign_sku_target[campaignName]['defaultBid'] = defaultBid
        campaign_sku_target[campaignName]['sku'] = sku
        campaign_sku_target[campaignName]['campaignType'] = campaignType
        if campaignType == 'keyword':
            campaign_sku_target[campaignName]['targets'] = {}
            if exact and len(exact) > 0:
                keyword_arr = exact.split('\n')
                campaign_sku_target[campaignName]['targets']['exact'] = [
                    x.strip() for x in keyword_arr if len(x.strip()) > 0]
            if phrase and len(phrase) > 0:
                keyword_arr = phrase.split('\n')
                campaign_sku_target[campaignName]['targets']['phrase'] = [
                    x.strip() for x in keyword_arr if len(x.strip()) > 0]
            if broad and len(broad) > 0:
                keyword_arr = broad.split('\n')
                campaign_sku_target[campaignName]['targets']['broad'] = [
                    x.strip() for x in keyword_arr if len(x.strip()) > 0]
        elif campaignType == 'product':
            target_arr = exact.split('\n')
            campaign_sku_target[campaignName]['targets'] = [
                x.strip() for x in target_arr if len(x.strip()) > 0]
        post = {}
        post['name'] = campaignName
        post['campaignType'] = 'sponsoredProducts'
        post['targetingType'] = 'auto' if campaignType == 'auto' else 'manual'
        post['dailyBudget'] = budget
        post['startDate'] = get_current_pst_time(region)
        post['state'] = 'enabled'
        post['bidding'] = {
            'strategy': 'legacyForSales',
            'adjustments': []
        }
        Campaign_post_data.append(post)
    amzapi = AmzapiHandler(shopId, profileId)

    print(Campaign_post_data)
    campaign_responses = amzapi.create_campaigns(Campaign_post_data)
    print(campaign_responses)
    campaigns = []
    for res in campaign_responses:
        if res['code'] == 'SUCCESS':
            campaignId = res['campaignId']
            camp = amzapi.get_campaign_byId(campaignId)
            campaigns.append(camp)
            campaignName = camp['name']
            log = '创建广告活动:%s, 活动类型:%s, 每日预算:%.2f' % (
                camp['name'], camp['targetingType'], camp['dailyBudget'])
            saveChangeLog(profileId, log, 'struct')
            post = {}
            post['name'] = 'adgroup'
            post['campaignId'] = campaignId
            post['defaultBid'] = campaign_sku_target[campaignName]['defaultBid']
            post['state'] = 'enabled'
            AdGroup_post_data.append(post)
    CreateOrUpdateCampaigns(campaigns, profileId)

    adGroup_responses = amzapi.create_adGroups(AdGroup_post_data)
    print(adGroup_responses)
    adGroups = []
    for res in adGroup_responses:
        if res['code'] == 'SUCCESS':
            adgroup = amzapi.get_adGroup_byId(res['adGroupId'])
            campaignId = adgroup['campaignId']
            campaignName = Campaign.objects.get(
                profileId=profileId, campaignId=campaignId).name
            adGroupId = adgroup['adGroupId']
            adgroup['type'] = campaign_sku_target[campaignName]['campaignType']
            adGroups.append(adgroup)
            log = '在广告活动:%s 内创建广告组: adgroup, 默认竞价为%.2f' % (
                campaignName, campaign_sku_target[campaignName]['defaultBid'])
            saveChangeLog(profileId, log, 'struct')
            post = {}
            post['sku'] = campaign_sku_target[campaignName]['sku']
            post['campaignId'] = campaignId
            post['adGroupId'] = adGroupId
            post['state'] = 'enabled'
            productAds_post_data.append(post)
    CreateOrUpdateAdGroups(adGroups, profileId)

    productAds_response = amzapi.create_productAds(productAds_post_data)
    print(productAds_response)
    productAdList = []
    for res in productAds_response:
        if res['code'] == 'SUCCESS':
            ad = amzapi.get_productAds_byId(res['adId'])
            campaignId = ad['campaignId']
            adGroupId = ad['adGroupId']
            campaign = Campaign.objects.get(
                profileId=profileId, campaignId=campaignId)
            campaignName = campaign.name
            # TODO: 自动广告添加更新4个targeting的任务
            productAdList.append(ad)
            log = '在广告活动:%s, 广告组: adgroup 内创建产品 SKU:%s' % (
                campaignName, ad['sku'])
            saveChangeLog(profileId, log, 'struct')
            produt = ShopProducts.objects.get(profileId=profileId, sku=sku)
            # bid = max(float(produt.price) * float(produt.macs) * 0.1, 0.3)
            bid = DEFUALT_PRICE[min(int(float(produt.price) / 30), 3)]
            if campaign_sku_target[campaignName]['campaignType'] == 'keyword':
                for matchType, keywords in campaign_sku_target[campaignName]['targets'].items():
                    for keyword in keywords:
                        keywords_post_data.append({
                            "campaignId": int(campaignId),
                            "adGroupId": int(adGroupId),
                            "state": "enabled",
                            "keywordText": keyword,
                            "matchType": matchType,
                            "bid": bid
                        })
                        log = '关键词 %s 放入广告活动:%s, 广告组: adgroup 下投放, 初始化竞价为%.2f' % (
                            keyword, campaignName, bid)
                        print(log)
                        saveChangeLog(profileId, log, 'struct')
            elif campaign_sku_target[campaignName]['campaignType'] == 'product':
                for target in campaign_sku_target[campaignName]['targets']:
                    targets_post_data.append({
                        "campaignId": int(campaignId),
                        "adGroupId": int(adGroupId),
                        "state": "enabled",
                        "expression": [
                            {
                                "value": target.upper(),
                                "type": "asinSameAs"
                            }
                        ],
                        "resolvedExpression": [
                            {
                                "value": target.upper(),
                                "type": "asinSameAs"
                            }
                        ],
                        "expressionType": "manual",
                        "bid": bid
                    })
                    log = 'ASIN %s 放入广告活动:%s, 广告组: adgroup 下投放, 初始化竞价:%.2f' % (
                        target.upper(), campaignName, bid)
                    print(log)
                    saveChangeLog(profileId, log, 'struct')
    CreateOrUpdateProductAds(productAdList, profileId)

    if len(keywords_post_data) > 0:
        print(keywords_post_data)
        res = amzapi.create_keywords(keywords_post_data)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateKeywordById(keywordIdList, shopId, profileId)
    if len(targets_post_data) > 0:
        print(targets_post_data)
        res = amzapi.create_taregets(targets_post_data)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        targetIdList = []
        for t in res:
            if t['code'] != 'SUCCESS':
                print(t)
                continue
            targetIdList.append(str(t['targetId']))
        if len(targetIdList) > 0:
            updateTargetById(targetIdList, shopId, profileId)
    return 'success'


def CreateCampaign(data):
    shopId = data['shopId']
    profileId = data['profileId']
    region = Shop.objects.get(id=int(shopId)).region
    amzapi = AmzapiHandler(shopId, profileId)
    Campaign_post_data = []
    AdGroup_post_data = []
    productAds_post_data = []
    campaign = data['campaign']
    print(campaign)
    budget = campaign['budget']
    campaignName = campaign['campaignName']
    campaignType = campaign['campaignType']
    defaultBid = campaign['defaultBid']
    groupName = campaign['groupName']
    sku = campaign['sku']
    campaignExist, adGroupExist, productExist = False, False, False
    campaignId, adGroupId = None, None
    campaignExist = Campaign.objects.filter(
        profileId=profileId, name=campaignName).exists()
    if campaignExist:
        campaignId = Campaign.objects.get(
            profileId=profileId, name=campaignName).campaignId
        adGroupExist = AdGroup.objects.filter(
            profileId=profileId, campaignId=campaignId, name=groupName).exists()
        if adGroupExist:
            adGroupId = AdGroup.objects.get(
                profileId=profileId, campaignId=campaignId, name=groupName).adGroupId
            productExist = ProductAds.objects.filter(
                profileId=profileId, campaignId=campaignId, adGroupId=adGroupId, sku=sku).exists()
            if productExist:
                raise DataValidationException(
                    '广告活动:%s,广告组:%s,sku:%s 已存在' % (campaignName, groupName, sku))
    if not campaignExist:
        post = {}
        post['name'] = campaignName
        post['campaignType'] = 'sponsoredProducts'
        post['targetingType'] = 'auto' if campaignType == 'auto' else 'manual'
        post['dailyBudget'] = budget
        post['startDate'] = get_current_pst_time(region)
        post['state'] = 'enabled'
        post['bidding'] = {
            'strategy': 'legacyForSales',
            'adjustments': []
        }
        Campaign_post_data.append(post)
        campaign_responses = amzapi.create_campaigns(Campaign_post_data)
        print(campaign_responses)
        campaigns = []
        for res in campaign_responses:
            if res['code'] == 'SUCCESS':
                campaignId = res['campaignId']
                camp = amzapi.get_campaign_byId(campaignId)
                campaigns.append(camp)
                log = '创建广告活动:%s, 活动类型:%s, 每日预算:%.2f' % (
                    camp['name'], camp['targetingType'], camp['dailyBudget'])
                saveChangeLog(profileId, log, 'struct')
        CreateOrUpdateCampaigns(campaigns, profileId)
    if not adGroupExist:
        post = {}
        post['name'] = groupName
        post['campaignId'] = campaignId
        post['defaultBid'] = defaultBid
        post['state'] = 'enabled'
        AdGroup_post_data.append(post)
        adGroup_responses = amzapi.create_adGroups(AdGroup_post_data)
        print(adGroup_responses)
        adGroups = []
        for res in adGroup_responses:
            if res['code'] == 'SUCCESS':
                adgroup = amzapi.get_adGroup_byId(res['adGroupId'])
                campaignName = Campaign.objects.get(
                    profileId=profileId, campaignId=adgroup['campaignId']).name
                adGroupName = adgroup['name']
                adGroupId = adgroup['adGroupId']
                adgroup['type'] = campaignType
                adGroups.append(adgroup)
                log = '在广告活动:%s 内创建广告组: %s, 默认竞价为%.2f' % (
                    campaignName, adGroupName, adgroup['defaultBid'])
                saveChangeLog(profileId, log, 'struct')
        CreateOrUpdateAdGroups(adGroups, profileId)
    if not productExist:
        post = {}
        post['sku'] = sku
        post['campaignId'] = campaignId
        post['adGroupId'] = adGroupId
        post['state'] = 'enabled'
        productAds_post_data.append(post)
        productAds_response = amzapi.create_productAds(productAds_post_data)
        print(productAds_response)
        productAdList = []
        for res in productAds_response:
            if res['code'] == 'SUCCESS':
                ad = amzapi.get_productAds_byId(res['adId'])
                campaignName = Campaign.objects.get(
                    profileId=profileId, campaignId=ad['campaignId']).name
                adGroupName = AdGroup.objects.get(
                    profileId=profileId, adGroupId=ad['adGroupId']).name
                productAdList.append(ad)
                log = '在广告活动:%s, 广告组:%s 内创建产品 SKU:%s' % (
                    campaignName, adGroupName, ad['sku'])
                saveChangeLog(profileId, log, 'struct')
        CreateOrUpdateProductAds(productAdList, profileId)

    if campaignType == 'auto':  # 更新自动广告下的targets
        adGroupIdFilter = {'adGroupIdFilter': adGroupId}
        targets = amzapi.get_targets(adGroupIdFilter)
        print(targets)
        CreateOrUpdateTargetings(targets, profileId)
    return


def CreateManualTargets(data):
    shopId = data['shopId']
    profileId = data['profileId']
    targets = data['targets']
    keywords = []
    asins = []
    for target in targets:
        keyword = target['keyword']
        if len(keyword) == 0:
            continue
        tg = target['target']
        if len(tg) == 0:
            continue
        sku, campaignId, adGroupId = tg
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId)
        adGroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        produt = ShopProducts.objects.get(profileId=profileId, sku=sku)
        bid = max(float(produt.price) * float(produt.macs) * 0.1, 0.3)
        target_type = adGroup.type
        if target_type == 'keyword':
            matchTypes = target['type']
            if len(matchTypes) == 0:
                continue
            for matchType in matchTypes:
                keywords.append({
                    "campaignId": int(campaignId),
                    "adGroupId": int(adGroupId),
                    "state": "enabled",
                    "keywordText": keyword,
                    "matchType": matchType,
                    "bid": bid
                })
                log = '关键词 %s 放入广告活动:%s, 广告组:%s 下投放, 初始化竞价为%.2f' % (
                    keyword, campaign.name, adGroup.name, bid)
                print(log)
                saveChangeLog(profileId, log, 'struct')
        elif target_type == 'product':
            asins.append({
                "campaignId": int(campaignId),
                "adGroupId": int(adGroupId),
                "state": "enabled",
                "expression": [
                    {
                        "value": keyword.upper(),
                        "type": "asinSameAs"
                    }
                ],
                "resolvedExpression": [
                    {
                        "value": keyword.upper(),
                        "type": "asinSameAs"
                    }
                ],
                "expressionType": "manual",
                "bid": bid
            })
            log = 'ASIN %s 放入广告活动:%s, 广告组:%s 下投放, 初始化竞价:%.2f' % (
                keyword.upper(), campaign.name, adGroup.name, bid)
            print(log)
            saveChangeLog(profileId, log, 'struct')
    amzapi = AmzapiHandler(shopId, data['profileId'])
    if len(keywords) > 0:
        print(keywords)
        res = amzapi.create_keywords(keywords)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateKeywordById(keywordIdList, shopId, profileId)
    if len(asins) > 0:
        print(asins)
        res = amzapi.create_taregets(asins)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        targetIdList = []
        for t in res:
            if t['code'] != 'SUCCESS':
                print(t)
                continue
            targetIdList.append(str(t['targetId']))
        if len(targetIdList) > 0:
            updateTargetById(targetIdList, shopId, profileId)
    return 'success'


def initShopData(shop):
    amzapi = AmzapiHandler(shop.id)
    profiles = amzapi.get_profiles()
    for profile in profiles:
        p = shop.profile_set.create(
            profileId=profile['profileId'],
            countryCode=profile['countryCode'],
            currencyCode=profile['currencyCode'],
            dailyBudget=int(profile['dailyBudget']),
            timezone=profile['timezone'],
            accountInfo=profile['accountInfo'])


def get_product_performance(profileId, shopId, product, sku_adId, dates):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    impressions, clicks, orders, costs, sales = 0, 0, 0, 0, 0
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        if not os.path.exists(data_dir):
            continue
        productads_data_path = os.path.join(data_dir, 'productAds.json')
        productads_data = json.load(open(productads_data_path))
        for data in productads_data:
            adId = str(data['adId'])
            if product['sku'] not in sku_adId or adId not in sku_adId[product['sku']]:
                continue
            impressions += data['impressions']
            clicks += data['clicks']
            orders += data['attributedUnitsOrdered7d']
            costs += round(data['cost'], 2)
            sales += data['attributedSales7d']
    product['impressions'] = impressions
    product['clicks'] = clicks
    product['orders'] = orders
    product['costs'] = costs
    product['sales'] = sales


def isDataFetchedDone(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    region = Shop.objects.get(id=int(shopId)).region
    dates = get_past_days(13, region)
    done = True
    for date in dates:
        date_dir = os.path.join(profile_dir, date)
        if not os.path.exists(date_dir) or not os.path.exists(os.path.join(date_dir, 'productAds.json')):
            done = False
            break
    return done


def get_sku_adId(profileId):
    res = {}
    products = ProductAds.objects.filter(profileId=profileId)
    for product in products:
        adId, sku = product.adId, product.sku
        if sku not in res:
            res[sku] = []
        if adId not in res[sku]:
            res[sku].append(adId)
    return res


def startProductAds(shopId, profileId, sku):
    shopProduct = ShopProducts.objects.get(profileId=profileId, sku=sku)
    shopProduct.state = 1
    shopProduct.save()
    params = []
    shopId = str(Profile.objects.get(profileId=profileId).shop.id)
    amzapi = AmzapiHandler(shopId, profileId)
    ads = ProductAds.objects.filter(profileId=profileId, sku=sku)
    for ad in ads:
        print(ad.state)
        if ad.state != 'paused':
            continue
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        saveChangeLog(profileId, '广告活动:%s 广告组内:%s sku:%s 状态由paused改成enabled' %
                      (campaign.name, adGroup.name, ad.sku), 'struct')
        params.append(
            {
                "adId": int(ad.adId),
                "state": 'enabled'
            }
        )
        ad.state = 'enabled'
        ad.save()
    if len(params) == 0:
        return 'fail'
    res = amzapi.update_productAds(params)
    print(res)
    return 'success'


def startProductTest(shopId, profileId, product):
    sku = product['sku']
    record = ProductsRecord.objects.filter(
        profileId=profileId, sku=product['sku']).order_by('-add_date')[0]
    if product['state'] == 3:
        save_record(product, record)
    date = (datetime.now(tz=utc) + timedelta(days=1)
            ).astimezone(timezone('US/Pacific')).strftime('%Y%m%d')
    createProductRecord(sku, profileId, date)
    product_model = ShopProducts.objects.get(profileId=profileId, sku=sku)
    product_model.state = 1
    product_model.promotiontarget = 0
    product_model.save()
    return 'success'


def pause_ads(shopId, profileId, ads):
    params = []
    for ad in ads:
        if ad.state != 'enabled':
            continue
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        saveChangeLog(profileId, '广告活动:%s 广告组内:%s sku:%s 状态由 enabled 改成 paused' %
                      (campaign.name, adGroup.name, ad.sku), 'struct')
        params.append(
            {
                "adId": int(ad.adId),
                "state": 'paused'
            }
        )
        ad.state = 'paused'
        ad.save()
    if len(params) == 0:
        return
    amzapi = AmzapiHandler(shopId, profileId)
    res = amzapi.update_productAds(params)
    print(res)
    return 'success'


def pauseProductAds(shopId, profileId, sku):
    params = []
    ads = ProductAds.objects.filter(profileId=profileId, sku=sku)
    for ad in ads:
        if ad.state != 'enabled':
            continue
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        saveChangeLog(profileId, '广告活动:%s 广告组内:%s sku:%s 状态由 enabled 改成 paused' %
                      (campaign.name, adGroup.name, ad.sku), 'struct')
        params.append(
            {
                "adId": int(ad.adId),
                "state": 'paused'
            }
        )
        ad.state = 'paused'
        ad.save()
    if len(params) == 0:
        return
    amzapi = AmzapiHandler(shopId, profileId)
    res = amzapi.update_productAds(params)
    print(res)
    return 'success'


def checkProfileDataCollected(dates, shopId, profileId):
    res = []
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    for date in dates:
        date_dir = os.path.join(profile_dir, date)
        if not os.path.exists(date_dir) or not os.path.exists(os.path.join(date_dir, 'campaign.json')) \
                or not os.path.exists(os.path.join(date_dir, 'keyword.json')) \
                or not os.path.exists(os.path.join(date_dir, 'targeting.json')) \
                or not os.path.exists(os.path.join(date_dir, 'keyword-query.json')) \
                or not os.path.exists(os.path.join(date_dir, 'targeting-query.json')) \
                or not os.path.exists(os.path.join(date_dir, 'productAds.json')):
            res.append(date)
    return res


def profileCollect(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    if not os.path.exists(os.path.join(profile_dir, 'adGroups.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'campaignNegativeKeywords.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'campaigns.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'keywords.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'negativeKeywords.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'productAds.json')) or \
            not os.path.exists(os.path.join(profile_dir, 'targets.json')):
        syncProfileData.delay(shopId, profileId)


def changeProfileState(shopId, profileId, state):
    profile = Profile.objects.get(profileId=profileId)
    region = Shop.objects.get(id=int(shopId)).region
    if profile.state == 0 and state == 'true':
        dates = get_past_days(59, region)
        allCollected = checkProfileDataCollected(dates, shopId, profileId)
        if len(allCollected) > 0:
            SynchronizeReportData.delay(shopId, profileId, allCollected)
        profileCollect(shopId, profileId)
    profile.state = 1 if state == 'true' else 0
    profile.save()
    return 'success'


def start_ads(shopId, profileId, ads):
    params = []
    for ad in ads:
        if ad.state != 'paused':
            continue
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        saveChangeLog(profileId, '广告活动:%s 广告组内:%s sku:%s 状态由 paused 改成 enabled' %
                      (campaign.name, adGroup.name, ad.sku), 'struct')
        params.append(
            {
                "adId": int(ad.adId),
                "state": 'enabled'
            }
        )
        ad.state = 'enabled'
        ad.save()
    if len(params) == 0:
        return
    amzapi = AmzapiHandler(shopId, profileId)
    res = amzapi.update_productAds(params)
    print(res)


def save_record(product, record):
    end_date = datetime.now(tz=utc).astimezone(
        timezone('US/Pacific')).strftime('%Y%m%d')
    record.end = end_date
    record.impressions = product['impressions']
    record.clicks = product['clicks']
    record.orders = product['orders']
    record.cost = product['costs']
    record.sales = product['sales']
    record.points = product['point']
    record.save()


def sku_ponint_ctr(x):
    a, b, c, d, m = WORD_POINT_CTR
    return d + (a-d) / (1+(x/c)**b)**m


def sku_ponint_cvr(x):
    a, b, c, d, m = WORD_POINT_CVR
    return d + (a-d) / (1+(x/c)**b)**m


def sku_ponint_acos(x):
    a, b, c, d, m = WORD_POINT_ACOS
    return d + (a-d) / (1+(x/c)**b)**m


def get_proper_cvr(x):
    if x <= 12: return 0.15
    if x >= 200: return 0.03
    return -0.0006383 * x + 0.15766

def get_product_point(product):
    impressions, clicks, orders, costs, sales = product['impressions'], product[
        'clicks'], product['orders'], product['costs'], product['sales']
    ctr = clicks / impressions if impressions > 0 else 0
    cvr = orders / clicks if clicks > 0 else 0
    acos = costs / sales if sales > 0 else 10
    ctr_co = sku_ponint_ctr(ctr/DEFAULT_CTR)
    cvr_co = sku_ponint_cvr(cvr/get_proper_cvr(float(product['price'])))
    acos_co = sku_ponint_acos(float(product['macs'])/acos)
    point = ctr_co * cvr_co * acos_co
    print(impressions, clicks, orders, costs, sales)
    print(product['sku'], product['price'], product['macs'])
    print("{0:.2f}%".format(ctr * 100), "{0:.2f}%".format(cvr * 100), "{0:.2f}%".format(acos * 100))
    print("{0:.2f}%".format(DEFAULT_CTR * 100),"{0:.2f}%".format(get_proper_cvr(float(product['price'])) * 100),"{0:.2f}%".format(float(product['macs']) * 100))
    print(ctr_co, cvr_co, acos_co, point)
    return point


def checkAdsState(shopId, profileId, ads):
    for ad in ads:
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        if ad.state == 'enabled' and campaign.state == 'enabled' and adGroup.state == 'enabled':
            return True
    return False


def getShopProductStatus(profileId):
    shopProducts = ShopProducts.objects.filter(profileId=profileId).values()
    shopId = str(Profile.objects.get(profileId=profileId).shop.id)
    region = Shop.objects.get(id=int(shopId)).region
    shop_dir = os.path.join(BASE_DIR, str(shopId))
    profile_dir = os.path.join(shop_dir, profileId)
    product_acos_path = os.path.join(profile_dir, 'product_acos.json')
    product_acos = json.load(open(product_acos_path))
    is_data_ready = False
    if len(shopProducts) > 0:
        if shopProducts[0]['state'] != 0:
            is_data_ready = True
        else:
            if isDataFetchedDone(shopId, profileId):
                is_data_ready = True
    sku_adId = get_sku_adId(profileId)
    for product in shopProducts:
        if not is_data_ready:
            continue
        record = ProductsRecord.objects.filter(
            profileId=profileId, sku=product['sku']).order_by('-add_date')[0]
        productAds_list = ProductAds.objects.filter(
            profileId=profileId, sku=product['sku'])
        ads_started = checkAdsState(shopId, profileId, productAds_list)
        dates, start_yet = get_recent_days(record.start, region)
        get_product_performance(profileId, shopId, product, sku_adId, dates)
        point = get_product_point(product)
        product['point'] = point
        if product['state'] in [0, 1]:
            test_state_action(shopId, profileId, productAds_list,
                              record, product, start_yet, dates, point)
        elif product['state'] == 2:
            bad_state_action(product, point)
        elif product['state'] in [3, 4, 5]:
            good_state_action(shopId, profileId, productAds_list,
                              record, product, point)
        if not ads_started:
            product['note'] = '广告活动暂未开启'
        product_model = ShopProducts.objects.get(
            profileId=profileId, sku=product['sku'])
        if product['state'] != product_model.state:
            product_model.state = product['state']
            if product['state'] in [1, 3]:
                product_model.promotionTarget = 0
            elif product['state'] == 4:
                product_model.promotionTarget = 1
            elif product['state'] == 5:
                product_model.promotionTarget = 2
            product_model.save()
            if product['sku'] not in product_acos:
                product_acos[product['sku']] = {
                    "price": round(float(product_model.price), 2),
                    "macs": round(float(product_model.macs), 2)
                }
            product_acos[product['sku']
                         ]['promotionTarget'] = product_model.promotionTarget
    write_obj_to_json(product_acos, product_acos_path)
    return shopProducts


def good_state_action(shopId, profileId, productAds_list, record, product, point):
    if point < PERFORMANCE_1:
        product['state'] = 2
        product['note'] = '表现不佳, 请重新测试'
        pause_ads(shopId, profileId, productAds_list)
        save_record(product, record)
    elif point < PERFORMANCE_3:
        product['state'] = 3
        product['note'] = '广告运行中'
    elif point >= PERFORMANCE_3:
        if product['state'] not in [4, 5]:
            product['state'] = 4


def bad_state_action(product, point):
    if product['clicks'] < TEST_CLICK_1:
        product['point'] = point * PERFORMANCE_1 / FULL_SCORE


def test_state_action(shopId, profileId, productAds_list, record, product, start_yet, dates, point):
    if not start_yet:
        product['note'] = '持续测试中...'
        product['state'] = 1
    else:
        clicks = product['clicks']
        if clicks < TEST_CLICK_1:
            if product['state'] == 1:
                if len(dates) >= TEST_DAY:
                    product['state'] = 2
                    product['note'] = '一周内积累的点击量过低, 已暂停相关广告, 请重新测试'
                    product['point'] = point * PERFORMANCE_1 / FULL_SCORE
                else:
                    product['note'] = '持续测试中...'
            elif product['state'] == 0:
                product['state'] = 2
                product['note'] = '过去60天内累计点击过低, 已暂停相关广告, 请重新开始测试'
                product['point'] = point * PERFORMANCE_1 / FULL_SCORE
        elif clicks >= TEST_CLICK_1 and clicks < TEST_CLICK_2:
            if point < PERFORMANCE_1:
                product['state'] = 2
            else:
                product['state'] = 1
                product['note'] = '持续测试中...'
        elif clicks >= TEST_CLICK_2:
            if point < PERFORMANCE_1:
                product['state'] = 2
                product['note'] = '表现不佳, 请重新测试'
            elif point > PERFORMANCE_1 and point < PERFORMANCE_3:
                product['state'] = 3
                product['note'] = '广告运行中'
            elif point >= PERFORMANCE_3:
                product['state'] = 4
    if product['state'] == 2:
        pause_ads(shopId, profileId, productAds_list)
        save_record(product, record)


def createProductRecord(sku, profileId, start_date):
    record = ProductsRecord(
        profileId=profileId,
        sku=sku,
        start=start_date
    )
    record.save()


def removeDuplicates(profileId):
    for row in ShopProducts.objects.all().reverse():
        if ShopProducts.objects.filter(profileId=profileId, sku=row.sku).count() > 1:
            row.delete()


def SaveProductList(shopId, profileId, productList):
    removeDuplicates(profileId)
    profile = Profile.objects.get(shop__id=int(shopId), profileId=profileId)
    if profile.state != 1:
        profile.state = 1
        profile.save()
    start_date = datetime.now(tz=utc) - timedelta(days=30)
    start_date = start_date.astimezone(
        timezone('US/Pacific')).strftime('%Y%m%d')
    for product in productList:
        product['macs'] = percentToNum(product['macs'])
        sku, asin, price, macs = product['sku'], product[
            'asin'], round(float(product['price']), 2), product['macs']
        id = product['id'] if 'id' in product else -1
        product_model = ShopProducts.objects.filter(
            profileId=profileId, sku=sku).first()
        if product_model:
            if sku != product_model.sku or asin != product_model.asin or abs(price - float(product_model.price)) > 1 or abs(macs - float(product_model.macs)) > 0.05:
                if product_model.state == 2:
                    record = ProductsRecord.objects.filter(
                        profileId=profileId, sku=product['sku']).order_by('-add_date')[0]
                    product_data = {}
                    product_data['impressions'] = record.impressions
                    product_data['clicks'] = record.clicks
                    product_data['orders'] = record.orders
                    product_data['costs'] = record.cost
                    product_data['sales'] = record.sales
                    product_data['macs'] = macs
                    point = get_product_point(product_data)
                    if point >= PERFORMANCE_3:
                        product['state'] = 3
                        product['promotionTarget'] = 1
                    record.points = point
                    record.save()
            product_serializer = ShopProductsSerializer(
                product_model, data=product)
        else:
            product_serializer = ShopProductsSerializer(data=product)
        if product_serializer.is_valid():
            product_serializer.save()
            if not ProductsRecord.objects.filter(profileId=profileId, sku=sku).exists():
                createProductRecord(product['sku'], profileId, start_date)
        else:
            raise ServiceInternelException(product_serializer.errors)
    return 'success', False


def GetDisabledTargeting(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, str(shopId), str(profileId))
    result_dir = os.path.join(data_dir, 'result')
    statistic_dir = os.path.join(data_dir, 'statistic')
    disable_targets = json.load(
        open(os.path.join(result_dir, 'disable_targeting.json')))
    campaign_performance = json.load(
        open(os.path.join(statistic_dir, 'campaign_performance.json')))
    res = []
    for disable_target in disable_targets:
        campaignId = disable_target['campaignId']
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId)
        campaignName = campaign.name
        campaignState = campaign.state
        if campaignState != 'enabled':
            continue
        adGroupId = disable_target['adGroupId']
        adGroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        adGroupName = adGroup.name
        adGroupState = adGroup.state
        if adGroupState != 'enabled':
            continue
        if 'keywordId' in disable_target:
            targetType = disable_target['matchType']
            targetId = disable_target['keywordId']
            targetName = disable_target['keywordText']
            targetState = disable_target['state']
        elif 'expressionType' in disable_target:
            targetId = disable_target['targetId']
            targetState = Target.objects.get(
                profileId=profileId, targetId=targetId).state
            if disable_target['expressionType'] == 'auto':
                targetType = '自动广告'
                targetName = disable_target['expression'][0]['type']
            elif disable_target['expressionType'] == 'manual':
                targetType = 'ASIN/品类'
                targetName = disable_target['resolvedExpression'][0]['value']
        if targetState != 'enabled':
            continue
        try:
            impressions, clicks, orders, spends, sales = campaign_performance[str(
                campaignId)]['groups'][str(adGroupId)]['targets'][str(targetId)]['data']
        except KeyError as e:
            print(e)
            continue
        res.append({
            'campaignId': campaignId,
            'adGroupId': adGroupId,
            'targetId': targetId,
            'type': targetType,
            'campaignName': campaignName,
            'adGroupName': adGroupName,
            'targetName': targetName,
            'targetType': targetType,
            'impressions': impressions,
            'clicks': clicks,
            'orders': orders,
            'spends': round(spends, 2),
            'sales': sales
        })
    return res


def GetBid(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, str(shopId), str(profileId))
    result_dir = os.path.join(data_dir, 'result')
    bids = json.load(open(os.path.join(result_dir, 'bid.json')))
    res = []
    for bid in bids:
        campaignId = bid['campaignId']
        campaignName = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId).name
        adGroupId = bid['adGroupId']
        adGroupName = AdGroup.objects.get(
            profileId=profileId, adGroupId=adGroupId).name
        if 'keywordId' in bid:
            targetId = bid['keywordId']
            targetName = bid['keywordText']
            targetType = bid['matchType']
        if 'targetId' in bid:
            targetId = bid['targetId']
            targetType = bid['expressionType']
            if targetType == 'auto':
                targetName = bid['expression'][0]['type']
            elif targetType == 'manual':
                targetName = bid['expression'][0]['value']
        res.append({
            'campaignId': campaignId,
            'adGroupId': adGroupId,
            'targetId': targetId,
            'campaignName': campaignName,
            'adGroupName': adGroupName,
            'targetName': targetName,
            'targetType': targetType,
            'bid': bid['bid'] if 'bid' in bid else None,
            'new_bid': bid['new_bid']
        })
    return res


def UpdateBid(data):
    shopId, profileId = data['shopId'], data['profileId']
    post_targets, post_keywords = [], []
    for target in data['targetings']:
        bid = target['bid']
        new_bid = target['new_bid']
        campaignName = target['campaignName']
        adGroupName = target['adGroupName']
        targetName = target['targetName']
        targetType = target['targetType']
        adGroupId = str(target['adGroupId'])
        targetId = target['targetId']
        if targetType in ['exact', 'phrase', 'broad']:
            post_keywords.append({
                "keywordId": targetId,
                "state": 'enabled',
                "bid": new_bid
            })
            keyword_obj = Keyword.objects.get(
                profileId=profileId, adGroupId=adGroupId, keywordId=str(targetId))
            keyword_obj.bid = new_bid
            keyword_obj.save()
        elif targetType in ['auto', 'manual']:
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
                                               adGroupName, targetName, targetType, bid, new_bid)
        print(log)
        saveChangeLog(profileId, log, 'bid')
    amzapi = AmzapiHandler(shopId, profileId)
    if len(post_keywords) > 0:
        res = amzapi.update_keywords(post_keywords)
        print(res)
        if 'code' in res and res['code'] != 207:
            return res['detail']
    if len(post_targets) > 0:
        res = amzapi.update_taregets(post_targets)
        print(res)
        if 'code' in res and res['code'] != 207:
            return res['detail']
    return 'success'


def PauseTargeting(data):
    keywords, targets = [], []
    shopId, profileId = data['shopId'], data['profileId']
    for target in data['targetings']:
        campaignName = target['campaignName']
        adGroupName = target['adGroupName']
        targetName = target['targetName']
        targetType = target['targetType']
        targetId = target['targetId']
        target_type = target['type']
        log = '将广告活动:%s 广告组:%s 内的投放目标%s - %s 暂停' % (
            campaignName, adGroupName, targetName, targetType)
        saveChangeLog(profileId, log, 'struct')
        if target_type in TARGETING_MATCHTYPE_CO:
            keywords.append({
                'keywordId': targetId,
                'state': 'paused'
            })
        else:
            targets.append({
                'targetId': targetId,
                'state': 'paused'
            })
    amzapi = AmzapiHandler(shopId, profileId)
    if len(keywords) > 0:
        res = amzapi.update_keywords(keywords)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateKeywordById(keywordIdList, shopId, profileId)
    if len(targets) > 0:
        res = amzapi.update_taregets(targets)
        print(res)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        targetIdList = []
        for t in res:
            if t['code'] != 'SUCCESS':
                print(t)
                continue
            targetIdList.append(str(t['targetId']))
        if len(targetIdList) > 0:
            updateTargetById(targetIdList, shopId, profileId)
    return 'success'


def GetNegativeSearchterm(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, shopId, profileId)
    result_dir = os.path.join(data_dir, 'result')
    statistic_dir = os.path.join(data_dir, 'statistic')
    searchterms = json.load(
        open(os.path.join(result_dir, 'negative_keywords.json')))
    campaign_performance = json.load(
        open(os.path.join(statistic_dir, 'campaign_performance.json')))
    res = []
    for idx, searchterm in enumerate(searchterms):
        campaignId = searchterm['campaignId']
        campaignName = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId).name
        adGroupId = searchterm['adGroupId']
        adGroupName = AdGroup.objects.get(
            profileId=profileId, adGroupId=adGroupId).name
        query = searchterm['query']
        target_type = searchterm['type']
        targetId = searchterm['targetId']
        matchType = searchterm['matchType']
        if target_type == 'keyword':
            if NegativeKeyword.objects.filter(profileId=profileId, campaignId=campaignId, adGroupId=adGroupId, keywordText=query, state='enabled').exists():
                continue
            if CampaignNegativeKeyword.objects.filter(profileId=profileId, campaignId=campaignId, keywordText=query, state='enabled').exists():
                continue
        elif target_type == 'asin':
            if NegativeTarget.objects.filter(profileId=profileId, campaignId=campaignId, adGroupId=adGroupId, expressionValue=query.lower(), state='enabled').exists():
                continue
        if matchType in ['EXACT', 'PHRASE', 'BROAD']:
            adTarget = Keyword.objects.get(profileId=profileId, keywordId=str(
                targetId)).keywordText + ' - ' + matchType
        else:
            adTarget = matchType
        impressions, clicks, orders, spends, sales = campaign_performance[str(
            campaignId)]['groups'][str(adGroupId)]['targets'][str(targetId)]['searchterms'][query]
        res.append({
            'campaignId': campaignId,
            'idx': idx,
            'adGroupId': adGroupId,
            'targetId': targetId,
            'type': target_type,
            'campaignName': campaignName,
            'adGroupName': adGroupName,
            'query': query,
            'adTarget': adTarget,
            'impressions': impressions,
            'clicks': clicks,
            'orders': orders,
            'spends': round(spends, 2),
            'sales': sales
        })
    return res


def PostNegativeKeywords(data):
    keywords, targets = [], []
    shopId, profileId = data['shopId'], data['profileId']
    # remove_idx = []
    for target in data['searchterms']:
        target_type = target['type']
        campaignId = target['campaignId']
        adGroupId = target['adGroupId']
        campaignName = target['campaignName']
        adGroupName = target['adGroupName']
        adTarget = target['campaignName']
        idx = target['idx']
        # remove_idx.append(idx)
        query = target['query']
        clicks = target['clicks']
        orders = target['orders']
        spends = target['spends']
        sales = target['sales']
        if target_type == 'asin':
            targets.append({
                'campaignId': campaignId,
                'adGroupId': adGroupId,
                'state': 'enabled',
                'expression': [{'value': query, 'type': 'asinSameAs'}],
                'expressionType': 'manual'
            })
            log = '广告活动:%s 广告组:%s 投放目标:%s 内的ASIN:%s表现不佳 (点击 %d,成交 %d,花费 %.2f,收入 %.2f) , 否定' % (
                campaignName, adGroupName, adTarget, query, clicks, orders, spends, sales)
            print(log)
            saveChangeLog(profileId, log, 'negative')
        elif target_type == 'keyword':
            keywords.append({
                'campaignId': campaignId,
                'adGroupId': adGroupId,
                'state': 'enabled',
                'keywordText': query,
                'matchType': 'negativeExact'
            })
            log = '广告活动:%s 广告组:%s 投放目标:%s 内的搜索词:%s表现不佳 (点击 %d,成交 %d,花费 %.2f,收入 %.2f) , 否定' % (
                campaignName, adGroupName, adTarget, query, clicks, orders, spends, sales)
            print(log)
            saveChangeLog(profileId, log, 'negative')
    amzapi = AmzapiHandler(shopId, profileId)
    if len(keywords) > 0:
        print(len(keywords))
        res = amzapi.create_negative_keywords(keywords)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateNegativeKeywordById(keywordIdList, shopId, profileId)
    if len(targets) > 0:
        print(len(targets))
        res = amzapi.create_negative_products(targets)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        targetIdList = []
        for t in res:
            if t['code'] != 'SUCCESS':
                print(t)
                continue
            targetIdList.append(str(t['targetId']))
        if len(targetIdList) > 0:
            updateNegativeProductById(targetIdList, shopId, profileId)
    # remove_from_json(shopId, profileId, remove_idx, 'negative_keywords.json')
    return 'success'


def product_exist(profileId, query, adGroupId):
    target_count = Target.objects.filter(
        profileId=profileId, adGroupId=adGroupId, expressionValue=query).count()
    return target_count > 0


def keyword_exist(profileId, query, adGroupId):
    keyword_count = Keyword.objects.filter(
        profileId=profileId, adGroupId=adGroupId, keywordText=query).count()
    return keyword_count > 0


def target_exist(profileId, query, sku_type, adGroupId):
    if sku_type == 'product':
        return product_exist(profileId, query, adGroupId)
    return keyword_exist(profileId, query, adGroupId)


def GetSkuManualCampaigns(shopId, profileId):
    shopProducts = ShopProducts.objects.filter(profileId=profileId)
    res = []
    for product in shopProducts:
        sku = product.sku
        campaignIds = list(set(ProductAds.objects.filter(
            profileId=profileId, sku=sku).values_list('campaignId', flat=True)))
        if len(campaignIds) == 0:
            continue
        target = {
            'value': sku,
            'label': sku,
            'children': []
        }
        for campaignId in campaignIds:
            campaign = Campaign.objects.get(
                profileId=profileId, campaignId=campaignId)
            targetingType = campaign.targetingType
            campaignState = campaign.state
            if targetingType == 'auto' or campaignState != 'enabled':
                continue
            adGroups = AdGroup.objects.filter(
                profileId=profileId, campaignId=campaignId)
            if len(adGroups) == 0:
                continue
            targetCampaign = {
                'value': campaignId,
                'label': campaign.name,
                'children': []
            }
            for adGroup in adGroups:
                adGroupId = adGroup.adGroupId
                groupType = adGroup.type
                groupState = adGroup.state
                if groupType == 'auto' or groupState != 'enabled':
                    continue
                targetCampaign['children'].append({
                    'value': adGroupId,
                    'label': adGroup.name
                })
            if len(targetCampaign['children']) > 0:
                target['children'].append(targetCampaign)
        if len(target['children']):
            res.append(target)
    return res


def get_skus_manual_campaign(profileId, skus):
    res = None
    for sku in skus:
        ads = ProductAds.objects.filter(profileId=profileId, sku=sku)
        if not res:
            res = ads
        else:
            res = res.intersection(ads)
    return res


def get_target_campaigns(profileId, adGroups):
    res = {}
    for adGroup in adGroups:
        campaignId = adGroup.campaignId
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId)
        if campaign.state != 'enabled':
            continue
        if campaignId not in res:
            res[campaignId] = {
                'targetCampaignId': campaignId,
                'targetCampaignName': campaign.name,
                'adGroups': []
            }
        res[campaignId]['adGroups'].append({
            'name': adGroup.name,
            'adGroupId': adGroup.adGroupId
        })
    res = list(res.values())
    camp_idx = 0
    for campaign in res:
        for idx, group in enumerate(campaign['adGroups']):
            group['id'] = '%s-%s' % (camp_idx, idx)
        camp_idx += 1
    return res


def list_hash(arr):
    arr_str = '.'.join(arr).encode('utf-8')
    hash_obj = hashlib.md5(arr_str)
    return hash_obj.hexdigest()


def get_seachterm_exclude_targeted(profileId, adGroupIds, searchterm_type, searchterm_format, targetMatchType):
    if searchterm_type == 'keyword':
        res = []
        for matchType in targetMatchType:
            if Keyword.objects.filter(profileId=profileId, adGroupId__in=adGroupIds, state='enabled', keywordFormat=searchterm_format, matchType=matchType).exists():
                continue
            res.append(matchType)
        return res, len(res) == 0
    else:  # check asin exist
        return targetMatchType, Target.objects.filter(profileId=profileId, adGroupId__in=adGroupIds, state='enabled', expressionValue=searchterm_format).exists()


def GetOptimizeSearchterm(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, shopId, profileId)
    result_dir = os.path.join(data_dir, 'result')
    statistic_dir = os.path.join(data_dir, 'statistic')
    searchterms = json.load(
        open(os.path.join(result_dir, 'good_performance_keywords.json')))
    campaign_performance = json.load(
        open(os.path.join(statistic_dir, 'campaign_performance.json')))
    res = {}
    for idx, searchterm in enumerate(searchterms):
        skus = searchterm['sku']
        skus_hash = list_hash(skus)
        searchterm_format = searchterm['format']
        searchterm_type = searchterm['type']
        targetMatchType = searchterm['targetMatchType'] if searchterm_type == 'keyword' else None
        if skus_hash not in res:
            res[skus_hash] = {}
        ads = get_skus_manual_campaign(profileId, skus)  # 包含了指定skus的广告
        adGroupIds = list(ads.values_list('adGroupId', flat=True))
        adGroups = AdGroup.objects.filter(
            profileId=profileId, adGroupId__in=adGroupIds, state='enabled')
        targetMatchType, allTargeted = get_seachterm_exclude_targeted(
            profileId, adGroupIds, searchterm_type, searchterm_format, targetMatchType)
        if allTargeted:
            continue
        target_campaigns = get_target_campaigns(profileId, adGroups)
        if searchterm_format not in res[skus_hash]:
            res[skus_hash][searchterm_format] = {
                'id': skus_hash+searchterm_format,
                'idx': [],
                'hasChild': True,
                'skus': skus,
                'query': searchterm_format,
                'clicks': 0,
                'orders': 0,
                'cost': 0,
                'sales': 0,
                'matchType': targetMatchType,
                'bid': searchterm['new_bid'],
                'children': [],
                'target': target_campaigns,
                'currentTarget': target_campaigns[0]['adGroups'][0]['id'] if len(target_campaigns) > 0 and len(target_campaigns[0]['adGroups']) > 0 else []
            }
        campaignId = searchterm['campaignId']
        adGroupId = searchterm['adGroupId']
        targetId = searchterm['targetId']
        query = searchterm['query']
        impressions, clicks, orders, spends, sales = campaign_performance[str(
            campaignId)]['groups'][str(adGroupId)]['targets'][str(targetId)]['searchterms'][query]
        matchType = searchterm['matchType']
        if matchType in ['EXACT', 'PHRASE', 'BROAD']:
            adTarget = Keyword.objects.get(profileId=profileId, keywordId=str(
                targetId)).keywordText + ' - ' + matchType
        else:
            adTarget = matchType
        child = {
            'id': str(searchterm['targetId'])+query,
            'hasChild': False,
            'query': query,
            'campaignName': searchterm['campaignName'],
            'adGroupName': searchterm['adGroupName'],
            'adTarget': adTarget,
            'clicks': clicks,
            'orders': orders,
            'cost': spends,
            'sales': sales,
        }
        res[skus_hash][searchterm_format]['clicks'] += clicks
        res[skus_hash][searchterm_format]['orders'] += orders
        res[skus_hash][searchterm_format]['cost'] += spends
        res[skus_hash][searchterm_format]['sales'] += sales
        res[skus_hash][searchterm_format]['children'].append(child)
        res[skus_hash][searchterm_format]['idx'].append(idx)
    result = []
    for k, v in res.items():
        for vk, vv in v.items():
            result.append(vv)
    return result


def PostOptimizeSearchterm(data):
    keywords, targets = [], []
    shopId, profileId = data['shopId'], data['profileId']
    # remove_idx = []
    for target in data['searchterms']:
        if len(target['currentTarget']) == 0 or '-' not in target['currentTarget']:
            continue  # 未指定投放目标
        matchTypes = target['matchType']
        query = target['query']
        bid = target['bid']
        clicks = target['clicks']
        orders = target['orders']
        cost = target['cost']
        sales = target['sales']
        idx1, idx2 = target['currentTarget'].split('-')
        idx1, idx2 = int(idx1), int(idx2)
        idx = target['idx']
        # remove_idx += idx
        selectTarget = target['target'][idx1]
        selectCampaignId, selectCampaignName = selectTarget[
            'targetCampaignId'], selectTarget['targetCampaignName']
        selecetAdGroup = target['target'][idx1]['adGroups'][idx2]
        selectAdGroupId, selectAdGroupName = selecetAdGroup['adGroupId'], selecetAdGroup['name']
        if not matchTypes:  # asin
            targets.append({
                "campaignId": int(selectCampaignId),
                "adGroupId": int(selectAdGroupId),
                "state": "enabled",
                "expression": [
                    {
                        "value": query,
                        "type": "asinSameAs"
                    }
                ],
                "resolvedExpression": [
                    {
                        "value": query,
                        "type": "asinSameAs"
                    }
                ],
                "expressionType": "manual",
                "bid": bid
            })
            log = 'ASIN %s (点击 %d,成交 %d,花费 %.2f,收入 %.2f) 放入广告活动:%s, 广告组:%s 下投放, 初始化竞价:%.2f' % (
                query, clicks, orders, cost, sales, selectCampaignName, selectAdGroupName, bid)
            print(log)
            saveChangeLog(profileId, log, 'positive')
        else:  # keyword
            for matchType in matchTypes:
                # new_bid = bid * TARGETING_MATCHTYPE_CO[matchType]
                keywords.append({
                    "campaignId": int(selectCampaignId),
                    "adGroupId": int(selectAdGroupId),
                    "state": "enabled",
                    "keywordText": query,
                    # "nativeLanguageKeyword": query,
                    # "nativeLanguageLocale": "zh_CN",
                    "matchType": matchType,
                    "bid": bid
                })
                log = '关键词 %s (点击 %d,成交 %d,花费 %.2f,收入 %.2f) 放入广告活动:%s, 广告组:%s 下投放, 匹配类型:%s 初始化竞价:%.2f' % (
                    query, clicks, orders, cost, sales, selectCampaignName, selectAdGroupName, matchType, bid)
                print(log)
                saveChangeLog(profileId, log, 'positive')
                # TODO 同步到数据库
    amzapi = AmzapiHandler(shopId, profileId)
    if len(keywords) > 0:
        print(keywords)
        res = amzapi.create_keywords(keywords)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateKeywordById(keywordIdList, shopId, profileId)
    if len(targets) > 0:
        print(targets)
        res = amzapi.create_taregets(targets)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        targetIdList = []
        for t in res:
            if t['code'] != 'SUCCESS':
                print(t)
                continue
            targetIdList.append(str(t['targetId']))
        if len(targetIdList) > 0:
            updateTargetById(targetIdList, shopId, profileId)
    return 'success'


def updateKeywordById(keywordIdList, shopId, profileId):
    amzapi = AmzapiHandler(shopId, profileId)
    keywordIdFilter = {'keywordIdFilter': ','.join(keywordIdList)}
    keywords = amzapi.get_keywords(keywordIdFilter)
    CreateOrUpdateKeywords(keywords, profileId)


def updateTargetById(targetIdList, shopId, profileId):
    amzapi = AmzapiHandler(shopId, profileId)
    targetIdFilter = {'targetIdFilter': ','.join(targetIdList)}
    targets = amzapi.get_targets(targetIdFilter)
    CreateOrUpdateTargetings(targets, profileId)


def updateNegativeKeywordById(keywordIdList, shopId, profileId):
    amzapi = AmzapiHandler(shopId, profileId)
    keywordIdFilter = {'keywordIdFilter': ','.join(keywordIdList)}
    negativeKeywords = amzapi.get_negative_keywords(keywordIdFilter)
    CreateOrUpdateNegativeKeywords(negativeKeywords, profileId)


def updateNegativeProductById(targetIdList, shopId, profileId):
    amzapi = AmzapiHandler(shopId, profileId)
    targetIdFilter = {'targetIdFilter': ','.join(targetIdList)}
    negativeTargets = amzapi.get_negative_products(targetIdFilter)
    CreateOrUpdateNegativeTargets(negativeTargets, profileId)


def GetRecommendation(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, shopId, profileId)
    result_dir = os.path.join(data_dir, 'result')
    recommendWords = json.load(
        open(os.path.join(result_dir, 'recommendWord.json')))
    res = []
    for sku, phrases in recommendWords.items():
        ads = ProductAds.objects.filter(profileId=profileId, sku=sku)
        adGroupIds = list(ads.values_list('adGroupId', flat=True))
        adGroups = AdGroup.objects.filter(
            profileId=profileId, adGroupId__in=adGroupIds, type='keyword', state='enabled')
        target_campaigns = get_target_campaigns(profileId, adGroups)
        for phrase in phrases:
            word, point = phrase.split('-')
            point = int(point)
            targetMatchType, allTargeted = get_seachterm_exclude_targeted(
                profileId, adGroupIds, 'keyword', word, ['broad'])
            if allTargeted:
                continue
            res.append({
                'sku': sku,
                'phrase': word,
                'point': point,
                'matchType': targetMatchType,
                'bid': 0.2,
                'target': target_campaigns,
                'currentTarget': target_campaigns[0]['adGroups'][0]['id'] if len(target_campaigns) > 0 and len(target_campaigns[0]['adGroups']) > 0 else []
            })
    return res


def PostRecommendation(data):
    keywords, targets = [], []
    shopId, profileId = data['shopId'], data['profileId']
    remove_list = []
    for target in data['searchterms']:
        if len(target['currentTarget']) == 0 or '-' not in target['currentTarget']:
            continue  # 未指定投放目标
        matchTypes = target['matchType']
        point = target['point']
        query = target['phrase']
        sku = target['sku']
        remove_list.append([sku, query, point])
        bid = target['bid']
        idx1, idx2 = target['currentTarget'].split('-')
        idx1, idx2 = int(idx1), int(idx2)
        selectTarget = target['target'][idx1]
        selectCampaignId, selectCampaignName = selectTarget[
            'targetCampaignId'], selectTarget['targetCampaignName']
        selecetAdGroup = target['target'][idx1]['adGroups'][idx2]
        selectAdGroupId, selectAdGroupName = selecetAdGroup['adGroupId'], selecetAdGroup['name']
        for matchType in matchTypes:
            # new_bid = bid * TARGETING_MATCHTYPE_CO[matchType]
            keywords.append({
                "campaignId": int(selectCampaignId),
                "adGroupId": int(selectAdGroupId),
                "state": "enabled",
                "keywordText": query,
                # "nativeLanguageKeyword": query,
                # "nativeLanguageLocale": "zh_CN",
                "matchType": matchType,
                "bid": bid
            })
            log = '关键词 %s 放入广告活动:%s, 广告组:%s 下投放, 匹配类型:%s 初始化竞价:%.2f' % (
                query, selectCampaignName, selectAdGroupName, matchType, bid)
            print(log)
            saveChangeLog(profileId, log, 'recommend')
            # TODO 同步到数据库
    amzapi = AmzapiHandler(shopId, data['profileId'])
    if len(keywords) > 0:
        print(keywords)
        res = amzapi.create_keywords(keywords)
        if 'code' in res and res['code'] != 207:
            return res['detail']
        print(res)
        keywordIdList = []
        for k in res:
            if k['code'] != 'SUCCESS':
                print(k)
                continue
            keywordIdList.append(str(k['keywordId']))
        if len(keywordIdList) > 0:
            updateKeywordById(keywordIdList, shopId, profileId)
        # data_dir = os.path.join(BASE_DIR, str(shopId), str(profileId))
        # result_dir = os.path.join(data_dir, 'result')
        # obj = json.load(open(os.path.join(result_dir, 'recommendWord.json')))
        # for data in remove_list:
        #     sku, query, point = data
        #     obj[sku].remove('%s-%s' % (query, point))
        # print(obj)
        # write_obj_to_json(obj, os.path.join(result_dir, 'recommendWord.json'))
    return 'success'


def GetBidLogs(shopId, profileId):
    data_dir = os.path.join(BASE_DIR, shopId, profileId)
    result_dir = os.path.join(data_dir, 'result')
    target_biddings = json.load(
        open(os.path.join(result_dir, 'biddings.json')))
    res = []
    for targetId, target in target_biddings.items():
        campaignId = target['campaignId']
        campaignName = Campaign.objects.get(
            profileId=profileId, campaignId=campaignId).name
        adGroupId = target['adGroupId']
        adGroup = AdGroup.objects.filter(
            profileId=profileId, adGroupId=adGroupId).first()
        if not adGroup:
            continue
        if target['bid'] and abs(target['bid'] - target['new_bid']) < 0.02:
            print('no need update bid for target: %s' % targetId)
            continue
        res.append({
            'campaignId': campaignId,
            'campaignName': campaignName,
            'adGroupId': adGroupId,
            'adGroupName': adGroup.name,
            'targetId': targetId,
            'targetName': target['format'],
            'bid': target['bid'],
            'new_bid': target['new_bid']
        })
    return res


def GetSkuCampaigns(profileId):
    shopProducts = ShopProducts.objects.filter(profileId=profileId)
    res = []
    for product in shopProducts:
        sku = product.sku
        price = product.price
        asin = product.asin
        currencyCode = product.currencyCode
        campaigns = ProductAds.objects.filter(asin=asin)
        if campaigns and len(campaigns) > 0:
            for campaign in campaigns:
                campaignId = campaign.campaignId
                camp = Campaign.objects.get(campaignId=campaignId)
                campaignName = camp.name
                campaignState = camp.state
                adGroupId = ProductAds.objects.get(
                    asin=asin, campaignId=campaignId).adGroupId
                if adGroupId:
                    group = AdGroup.objects.get(
                        profileId=profileId, adGroupId=adGroupId)
                    adGroupName = group.name
                    groupState = group.state
                res.append({
                    'sku': sku,
                    'asin': asin,
                    'price': price,
                    'currencyCode': currencyCode,
                    'adgroupId': adGroupId,
                    'adGroupName': adGroupName,
                    'groupState': groupState,
                    'campaignId': campaignId,
                    'campaignName': campaignName,
                    'campaignState': campaignState
                })
    return res


def getCampaignStructure(profileId, dataType, parentId):
    res = []
    if dataType == 'campaign':
        campaigns = Campaign.objects.filter(
            profileId=profileId).exclude(state='archived').order_by('startDate')
        for campaign in campaigns:
            res.append({
                'id': campaign.campaignId,
                'name': campaign.name,
                'state': campaign.state,
                'bid': campaign.dailyBudget,
                'bid_power': 1,
                'type': campaign.targetingType,
                'category': 'campaign',
                'show': False
            })
    elif dataType == 'adgroup':
        adgroups = AdGroup.objects.filter(
            profileId=profileId, campaignId=parentId).exclude(state='archived')
        for adgroup in adgroups:
            res.append({
                'id': adgroup.adGroupId,
                'name': adgroup.name,
                'state': adgroup.state,
                'bid': adgroup.defaultBid,
                'bid_power': 1,
                'type': None,
                'category': 'adgroup',
                'show': False
            })
    elif dataType == 'target':
        adGroupType = AdGroup.objects.get(
            profileId=profileId, adGroupId=parentId).type
        print(adGroupType)
        if adGroupType == 'keyword':
            keywords = Keyword.objects.filter(
                profileId=profileId, adGroupId=parentId).exclude(state='archived')
            print(keywords)
            for keyword in keywords:
                res.append({
                    'id': keyword.keywordId,
                    'name': keyword.keywordText + ' ' + keyword.matchType,
                    'state': keyword.state,
                    'bid': keyword.bid,
                    'bid_power': 1,
                    'type': keyword.matchType,
                    'category': 'keyword',
                    'show': False
                })
        else:
            targetings = Target.objects.filter(
                profileId=profileId, adGroupId=parentId).exclude(state='archived')
            for target in targetings:
                res.append({
                    'id': target.targetId,
                    'name': target.expression[0]['value'] if 'value' in target.expression[0] else target.expression[0]['type'],
                    'state': target.state,
                    'bid': target.bid,
                    'bid_power': 1,
                    'type': target.expressionType,
                    'category': 'target',
                    'show': False
                })
        groups_ads = ProductAds.objects.filter(
            profileId=profileId, adGroupId=parentId)
        for product in groups_ads:
            res.append({
                'id': product.adId,
                'name': 'SKU: %s' % product.sku,
                'state': product.state,
                'type': 'sku',
                'category': 'sku',
                'show': False
            })
    return res


def EditCampaign(data):
    shopId = data['shopId']
    profileId = data['profileId']
    amzapi = AmzapiHandler(shopId, profileId)
    data = data['data']
    campaignId = data['id']
    campaign = Campaign.objects.get(campaignId=campaignId)
    campaignName = campaign.name
    campaignState = campaign.state
    campaignBudget = campaign.dailyBudget
    isChanged = False
    if campaignName != data['name']:
        saveChangeLog(profileId, '广告活动:%s 名称修改为%s' %
                      (campaignName, data['name']), 'struct')
        isChanged = True
        campaign.name = data['name']
    if campaignState != data['state']:
        saveChangeLog(profileId, '广告活动:%s 状态由%s 改成%s' %
                      (data['name'], campaignState, data['state']), 'struct')
        isChanged = True
        campaign.state = data['state']
    if campaignBudget != data['bid']:
        saveChangeLog(profileId, '广告活动:%s 预算由%s 改成%s' %
                      (data['name'], campaignBudget, data['bid']), 'struct')
        isChanged = True
        campaign.dailyBudget = data['bid']
    if isChanged:
        params = [
            {
                "campaignId": int(data['id']),
                "name": data['name'],
                "state": data['state'],
                "dailyBudget": float(data['bid'])
            }
        ]
        print(params)
        res = amzapi.update_campaigns(params)
        campaign.save()
    else:
        res = '未检测到修改'
    return res


def EditAdGroup(data):
    shopId = data['shopId']
    profileId = data['profileId']
    amzapi = AmzapiHandler(shopId, profileId)
    data = data['data']
    adGroupId = data['id']
    adGroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
    adGroupName = adGroup.name
    adGroupState = adGroup.state
    adGroupBid = adGroup.defaultBid
    isChanged = False
    if adGroupName != data['name']:
        saveChangeLog(profileId, '广告组:%s 名称由%s 改成%s' %
                      (adGroupId, adGroupName, data['name']), 'struct')
        isChanged = True
        adGroup.name = data['name']
    if adGroupState != data['state']:
        saveChangeLog(profileId, '广告组:%s(%s) 状态由%s 改成%s' % (
            data['name'], adGroupId, adGroupState, data['state']), 'struct')
        isChanged = True
        adGroup.state = data['state']
    if abs(float(adGroupBid) - float(data['bid'])) > 0.01:
        print(adGroupBid, data['bid'])
        saveChangeLog(profileId, '广告组:%s(%s) 默认竞价由%s 改成%s' %
                      (data['name'], adGroupId, adGroupBid, data['bid']), 'bid')
        isChanged = True
        adGroup.defaultBid = data['bid']
    if isChanged:
        params = [
            {
                "adGroupId": int(data['id']),
                "name": data['name'],
                "defaultBid": float(data['bid']),
                "state": data['state']
            }
        ]
        print(params)
        res = amzapi.update_adGroups(params)
        adGroup.save()
    elif data['bid_power'] != 1:
        print(data['bid_power'])
        keywords = Keyword.objects.filter(
            profileId=profileId, adGroupId=adGroupId)
        if len(keywords) > 0:
            post_keywords = []
            for keyword in keywords:
                bid = float(data['bid_power']) * \
                    float(keyword.bid) * random.uniform(0.925, 1.0725)
                post_keywords.append({
                    "keywordId": int(keyword.keywordId),
                    "state": keyword.state,
                    "bid": bid
                })
                log = '关键词:%s-%s竞价由%s 改为%s' % (keyword.keywordText,
                                               keyword.matchType, keyword.bid, bid)
                print(log)
                saveChangeLog(profileId, log, 'bid')
                keyword.bid = bid
                keyword.save()
            print(post_keywords)
            res = amzapi.update_keywords(post_keywords)

        targets = Target.objects.filter(
            profileId=profileId, adGroupId=adGroupId)
        if len(targets) > 0:
            post_targets = []
            for target in targets:
                bid = float(data['bid_power']) * \
                    float(target.bid) * random.uniform(0.925, 1.0725)
                post_targets.append({
                    "targetId": int(target.targetId),
                    "state": target.state,
                    "bid": bid
                })
                camapignName = Campaign.objects.get(
                    profileId=profileId, campaignId=target.campaignId).name
                log = '广告活动%s下投放目标:%s竞价由%s 改为%s' % (camapignName, target.expression[0]['type'] if target.expressionType == 'auto'
                                                    else target.expression[0]['value'], target.bid, bid)
                target.bid = bid
                target.save()
                saveChangeLog(profileId, log, 'bid')
            print(post_targets)
            res = amzapi.update_taregets(post_targets)
    else:
        res = '未检测到修改'
    print(res)
    return res


def EditKeyword(data):
    shopId = data['shopId']
    profileId = data['profileId']
    amzapi = AmzapiHandler(shopId, profileId)
    data = data['data']
    keywordId = data['id']
    keyword = Keyword.objects.get(keywordId=keywordId)
    keywordState = keyword.state
    keywordBid = keyword.bid
    isChanged = False
    if keywordState != data['state']:
        saveChangeLog(profileId, '关键词:%s-%s状态由%s 改为%s' %
                      (data['name'], data['type'], keywordState, data['state']), 'struct')
        isChanged = True
        keyword.state = data['state']
    if keywordBid != data['bid']:
        saveChangeLog(profileId, '关键词:%s-%s竞价由%s 改为%s' %
                      (data['name'], data['type'], keywordBid, data['bid']), 'bid')
        isChanged = True
        keyword.bid = data['bid']
    if isChanged:
        params = [
            {
                "keywordId": int(data['id']),
                "state": data['state'],
                "bid": float(data['bid'])
            }
        ]
        print(params)
        res = amzapi.update_keywords(params)
        print(res)
        keyword.save()
    else:
        res = '未检测到修改'
    return res


def EditTargeting(data):
    shopId = data['shopId']
    profileId = data['profileId']
    amzapi = AmzapiHandler(shopId, profileId)
    data = data['data']
    targetId = data['id']
    target = Target.objects.get(targetId=targetId)
    targetState = target.state
    targetBudget = target.bid
    isChanged = False
    campaignId = target.campaignId
    adGroupId = target.adGroupId
    campaignName = Campaign.objects.get(
        profileId=profileId, campaignId=campaignId).name
    adGroupName = AdGroup.objects.get(
        profileId=profileId, adGroupId=adGroupId).name
    if targetState != data['state']:
        saveChangeLog(profileId, '广告活动%s, 广告组%s内目标: %s 状态由%s 改成%s' % (
            campaignName, adGroupName, data['name'], targetState, data['state']), 'struct')
        isChanged = True
        target.state = data['state']
    if targetBudget != data['bid']:
        saveChangeLog(profileId, '广告活动%s, 广告组%s内目标: %s 竞价由%s 改成%s' % (
            campaignName, adGroupName, data['name'], targetBudget, data['bid']), 'bid')
        isChanged = True
        target.dailyBudget = data['bid']
    if isChanged:
        params = [
            {
                "targetId": int(data['id']),
                "state": data['state'],
                "bid": float(data['bid'])
            }
        ]
        print(params)
        res = amzapi.update_taregets(params)
        target.save()
    else:
        res = '未检测到修改'
    return res


def EditSku(data):
    shopId = data['shopId']
    profileId = data['profileId']
    data = data['data']
    adId = data['id']
    state = data['state']
    ad = ProductAds.objects.get(profileId=profileId, adId=adId)
    if ad.state != state and state in ['enabled', 'paused', 'archived']:
        campaign = Campaign.objects.get(
            profileId=profileId, campaignId=ad.campaignId)
        adGroup = AdGroup.objects.get(
            profileId=profileId, adGroupId=ad.adGroupId)
        saveChangeLog(profileId, '广告活动:%s 广告组内:%s sku:%s 状态由%s改成%s' %
                      (campaign.name, adGroup.name, ad.sku, ad.state, state), 'struct')
        params = [(
            {
                "adId": int(ad.adId),
                "state": state
            }
        )]
        ad.state = state
        ad.save()
        amzapi = AmzapiHandler(shopId, profileId)
        res = amzapi.update_productAds(params)
        print(res)
        return res
    else:
        return '未检测到修改'


def getDate(start, end):
    dates = []
    yyyy, mm, dd = start[:4], start[4:6], start[7:] if start[6] == '0' else start[6:]
    start = datetime(int(yyyy), int(mm), int(dd))
    day = -1
    while len(dates) == 0 or dates[-1] != end:
        date = start + timedelta(days=day)
        day += 1
        dates.append(date.isoformat().replace('-', '')[:8])
    return dates[:-1]


def getCampainDataByDate(profileId, profile_dir, dates, campaignIds):
    res, source = {}, [['date'], ['曝光'], ['点击'], ['订单'], [
        '花费'], ['收入'], ['点击率'], ['转化率'], ['ACOS'], ['CPC']]
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        campaign_data_path = os.path.join(data_dir, 'campaign.json')
        if not os.path.exists(campaign_data_path):
            continue
        source[0].append(date)
        total_impressions, total_clicks, total_orders, total_cost, total_sales, totoal_ctr, total_cvr, total_acos = 0, 0, 0, 0, 0, 0, 0, 0
        campaign_data = json.load(open(campaign_data_path))
        for data in campaign_data:
            campaignId = str(data['campaignId'])
            if campaignId not in campaignIds:
                continue
            impressions, clicks, orders, cost, sales = data['impressions'], data['clicks'], data[
                'attributedUnitsOrdered7d'], data['cost'], data['attributedSales7d']
            total_impressions += impressions
            total_clicks += clicks
            total_orders += orders
            total_cost += cost
            total_sales += sales
            if campaignId not in res:
                res[campaignId] = {
                    'id': campaignId,
                    'name': data['campaignName'],
                    'state': STATUS[Campaign.objects.get(profileId=profileId, campaignId=campaignId).state],
                    'impressions': impressions,
                    'clicks': clicks,
                    'orders': orders,
                    'cost': cost,
                    'sales': sales
                }
            else:
                res[campaignId]['impressions'] += impressions
                res[campaignId]['clicks'] += clicks
                res[campaignId]['orders'] += orders
                res[campaignId]['cost'] += cost
                res[campaignId]['sales'] += sales
        totoal_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        total_cvr = total_orders / total_clicks if total_clicks > 0 else 0
        total_acos = total_cost / total_sales if total_sales > 0 else 'inf'
        total_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        source[1].append(total_impressions)
        source[2].append(total_clicks)
        source[3].append(total_orders)
        source[4].append(total_cost)
        source[5].append(total_sales)
        source[6].append(totoal_ctr)
        source[7].append(total_cvr)
        source[8].append(total_acos)
        source[9].append(total_cpc)
    return res, source


def getProductAdDataByDate(profileId, profile_dir, dates, products):
    res, source = {}, [['date'], ['曝光'], ['点击'], ['订单'], [
        '花费'], ['收入'], ['点击率'], ['转化率'], ['ACOS'], ['CPC']]
    adIds = list(set(list(products.values_list('adId', flat=True))))
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        productads_data_path = os.path.join(data_dir, 'productAds.json')
        if not os.path.exists(productads_data_path):
            continue
        source[0].append(date)
        total_impressions, total_clicks, total_orders, total_cost, total_sales, totoal_ctr, total_cvr, total_acos = 0, 0, 0, 0, 0, 0, 0, 0
        productads_data = json.load(open(productads_data_path))
        for data in productads_data:
            adId = str(data['adId'])
            if adId not in adIds:
                continue
            impressions, clicks, orders, cost, sales = data['impressions'], data['clicks'], data[
                'attributedUnitsOrdered7d'], data['cost'], data['attributedSales7d']
            total_impressions += impressions
            total_clicks += clicks
            total_orders += orders
            total_cost += cost
            total_sales += sales
            if adId not in res:
                res[adId] = {
                    'id': adId,
                    'name': data['campaignName'],
                    'state': STATUS[ProductAds.objects.get(profileId=profileId, adId=adId).state],
                    'impressions': impressions,
                    'clicks': clicks,
                    'orders': orders,
                    'cost': cost,
                    'sales': sales
                }
            else:
                res[adId]['impressions'] += impressions
                res[adId]['clicks'] += clicks
                res[adId]['orders'] += orders
                res[adId]['cost'] += cost
                res[adId]['sales'] += sales
        totoal_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        total_cvr = total_orders / total_clicks if total_clicks > 0 else 0
        total_acos = total_cost / total_sales if total_sales > 0 else 'inf'
        total_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        source[1].append(total_impressions)
        source[2].append(total_clicks)
        source[3].append(total_orders)
        source[4].append(total_cost)
        source[5].append(total_sales)
        source[6].append(totoal_ctr)
        source[7].append(total_cvr)
        source[8].append(total_acos)
        source[9].append(total_cpc)
    return res, source


def getAdGroupDataByDate(profile_dir, dates, campaignId):
    res, source = {}, [['date'], ['曝光'], ['点击'], ['订单'], [
        '花费'], ['收入'], ['点击率'], ['转化率'], ['ACOS'], ['CPC']]
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        keywords_path = os.path.join(data_dir, 'keyword.json')
        targets_path = os.path.join(data_dir, 'targeting.json')
        total_impressions, total_clicks, total_orders, total_cost, total_sales, totoal_ctr, total_cvr, total_acos = 0, 0, 0, 0, 0, 0, 0, 0
        source[0].append(date)
        for target_path in [keywords_path, targets_path]:
            if not os.path.exists(target_path):
                continue
            targetings = json.load(open(target_path))
            for targeting in targetings:
                if targeting['campaignId'] != campaignId:
                    continue
                adGroupId = targeting['adGroupId']
                impressions, clicks, orders, cost, sales = targeting['impressions'], targeting['clicks'], targeting[
                    'attributedUnitsOrdered7d'], targeting['cost'], targeting['attributedSales7d']
                total_impressions += impressions
                total_clicks += clicks
                total_orders += orders
                total_cost += cost
                total_sales += sales
                if adGroupId not in res:
                    res[adGroupId] = {
                        'id': adGroupId,
                        'name': targeting['adGroupName'],
                        'state': '',
                        'impressions': impressions,
                        'clicks': clicks,
                        'orders': orders,
                        'cost': cost,
                        'sales': sales
                    }
                else:
                    res[adGroupId]['impressions'] += impressions
                    res[adGroupId]['clicks'] += clicks
                    res[adGroupId]['orders'] += orders
                    res[adGroupId]['cost'] += cost
                    res[adGroupId]['sales'] += sales
        totoal_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        total_cvr = total_orders / total_clicks if total_clicks > 0 else 0
        total_acos = total_cost / total_sales if total_sales > 0 else 'inf'
        total_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        source[1].append(total_impressions)
        source[2].append(total_clicks)
        source[3].append(total_orders)
        source[4].append(total_cost)
        source[5].append(total_sales)
        source[6].append(totoal_ctr)
        source[7].append(total_cvr)
        source[8].append(total_acos)
        source[9].append(total_cpc)
    return res, source


def getTargetDataByDate(profile_dir, dates, adGroupId):
    res, source = {}, [['date'], ['曝光'], ['点击'], ['订单'], [
        '花费'], ['收入'], ['点击率'], ['转化率'], ['ACOS'], ['CPC']]
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        keywords_path = os.path.join(data_dir, 'keyword.json')
        targets_path = os.path.join(data_dir, 'targeting.json')
        total_impressions, total_clicks, total_orders, total_cost, total_sales, totoal_ctr, total_cvr, total_acos = 0, 0, 0, 0, 0, 0, 0, 0
        source[0].append(date)
        for target_path in [keywords_path, targets_path]:
            if not os.path.exists(target_path):
                continue
            targetings = json.load(open(target_path))
            for targeting in targetings:
                if targeting['adGroupId'] != adGroupId:
                    continue
                targetId = targeting['keywordId'] if 'keywordId' in targeting else targeting['targetId']
                impressions, clicks, orders, cost, sales = targeting['impressions'], targeting['clicks'], targeting[
                    'attributedUnitsOrdered7d'], targeting['cost'], targeting['attributedSales7d']
                total_impressions += impressions
                total_clicks += clicks
                total_orders += orders
                total_cost += cost
                total_sales += sales
                if targetId not in res:
                    res[targetId] = {
                        'id': targetId,
                        'name': targeting['keywordText'] + ' | ' + targeting['matchType'] if 'keywordId' in targeting else targeting['targetingText'],
                        'state': '',
                        'impressions': impressions,
                        'clicks': clicks,
                        'orders': orders,
                        'cost': cost,
                        'sales': sales,
                        'type': 'keyword' if 'keywordId' in targeting else 'target'
                    }
                else:
                    res[targetId]['impressions'] += impressions
                    res[targetId]['clicks'] += clicks
                    res[targetId]['orders'] += orders
                    res[targetId]['cost'] += cost
                    res[targetId]['sales'] += sales
        totoal_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        total_cvr = total_orders / total_clicks if total_clicks > 0 else 0
        total_acos = total_cost / total_sales if total_sales > 0 else 'inf'
        total_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        source[1].append(total_impressions)
        source[2].append(total_clicks)
        source[3].append(total_orders)
        source[4].append(total_cost)
        source[5].append(total_sales)
        source[6].append(totoal_ctr)
        source[7].append(total_cvr)
        source[8].append(total_acos)
        source[9].append(total_cpc)
    return res, source


def get_camapignId_by_product(profileId, products):
    campaignIds = list(
        set(list(products.values_list('campaignId', flat=True))))
    campaignId_list = []
    for campaignId in campaignIds:
        products = ProductAds.objects.filter(
            profileId=profileId, campaignId=campaignId)
        product_sku = list(products.values_list('sku', flat=True))
        allFound = True
        # for sku in product_sku:
        #     if not ShopProducts.objects.filter(profileId=profileId, sku=sku).exists():
        #         allFound = False
        if allFound and campaignId not in campaignId_list:
            campaignId_list.append(campaignId)
    return campaignId_list


def GetSkuDetail(profileId, shopId, start, end, promotionTarget):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    dates = getDate(start, end)
    shop_products = ShopProducts.objects.filter(
        profileId=profileId, promotionTarget__in=promotionTarget)
    skus = list(shop_products.values_list('sku', flat=True))
    products = ProductAds.objects.filter(profileId=profileId, sku__in=skus)
    products_data, source = getProductAdDataByDate(
        profileId, profile_dir, dates, products)
    res = {
        'detail': {},
        'total': {
            'impressions': 0,
            'clicks': 0,
            'orders': 0,
            'cost': 0,
            'sales': 0
        }
    }
    adId_set = set()
    total_data = res['total']
    for sku in skus:
        res['detail'][sku] = {
            'id': sku,
            'name': sku,
            'state': PROMOTIONSTATUS[ShopProducts.objects.get(profileId=profileId, sku=sku).promotionTarget],
            'impressions': 0,
            'clicks': 0,
            'orders': 0,
            'cost': 0,
            'sales': 0
        }
        sku_data = res['detail'][sku]
        product = ProductAds.objects.filter(profileId=profileId, sku=sku)
        adIds = list(set(list(product.values_list('adId', flat=True))))
        for adId in adIds:
            if adId not in products_data:
                continue
            ad_data = products_data[adId]
            impressions, clicks, orders, cost, sales = ad_data['impressions'], ad_data[
                'clicks'], ad_data['orders'], ad_data['cost'], ad_data['sales']
            sku_data['impressions'] += impressions
            sku_data['clicks'] += clicks
            sku_data['orders'] += orders
            sku_data['cost'] += cost
            sku_data['sales'] += sales
            if adId not in adId_set:
                adId_set.add(adId)
                total_data['impressions'] += impressions
                total_data['clicks'] += clicks
                total_data['orders'] += orders
                total_data['cost'] += cost
                total_data['sales'] += sales
    res['detail'] = res['detail'].values()
    res['source'] = source
    return res


def GetCampaignDetail(profileId, shopId, start, end, sku):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    dates = getDate(start, end)
    skus = [sku]
    products = ProductAds.objects.filter(profileId=profileId, sku__in=skus)
    campaignIds = get_camapignId_by_product(profileId, products)
    campaigns, source = getCampainDataByDate(
        profileId, profile_dir, dates, campaignIds)
    res = {
        'detail': {},
        'total': {
            'impressions': 0,
            'clicks': 0,
            'orders': 0,
            'cost': 0,
            'sales': 0
        }
    }
    total_data = res['total']
    for campaignId, campaign in campaigns.items():
        total_data['impressions'] += campaign['impressions']
        total_data['clicks'] += campaign['clicks']
        total_data['orders'] += campaign['orders']
        total_data['cost'] += campaign['cost']
        total_data['sales'] += campaign['sales']
    res['detail'] = campaigns.values()
    res['source'] = source
    return res


def GetAdGroupDetail(profileId, shopId, start, end, campaignId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    dates = getDate(start, end)
    adGroups, source = getAdGroupDataByDate(
        profile_dir, dates, int(campaignId))
    res = {
        'detail': {},
        'total': {
            'impressions': 0,
            'clicks': 0,
            'orders': 0,
            'cost': 0,
            'sales': 0
        }
    }
    total_data = res['total']
    for adGroupId, adGroup in adGroups.items():
        adGroup['state'] = STATUS[AdGroup.objects.get(
            profileId=profileId, adGroupId=adGroupId).state]
        total_data['impressions'] += adGroup['impressions']
        total_data['clicks'] += adGroup['clicks']
        total_data['orders'] += adGroup['orders']
        total_data['cost'] += adGroup['cost']
        total_data['sales'] += adGroup['sales']
    res['detail'] = adGroups.values()
    res['source'] = source
    return res


def GetTargetDetail(profileId, shopId, start, end, adGroupId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    dates = getDate(start, end)
    targets, source = getTargetDataByDate(profile_dir, dates, int(adGroupId))
    res = {
        'detail': {},
        'total': {
            'impressions': 0,
            'clicks': 0,
            'orders': 0,
            'cost': 0,
            'sales': 0
        }
    }
    total_data = res['total']
    for targetId, target in targets.items():
        if target['type'] == 'keyword':
            target['state'] = STATUS[Keyword.objects.get(
                profileId=profileId, keywordId=targetId).state]
        elif target['type'] == 'target':
            target['state'] = STATUS[Target.objects.get(
                profileId=profileId, targetId=targetId).state]
        total_data['impressions'] += target['impressions']
        total_data['clicks'] += target['clicks']
        total_data['orders'] += target['orders']
        total_data['cost'] += target['cost']
        total_data['sales'] += target['sales']
    res['detail'] = targets.values()
    res['source'] = source
    return res


def GetCampaignsData(profileId, shopId, start, end, dataType):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    dates = getDate(start, end)
    product_ads = ProductAds.objects.filter(profileId=profileId)
    shop_product = ShopProducts.objects.filter(
        profileId=profileId).values('sku')
    shop_skus = set([x['sku'] for x in shop_product])
    res, camp_sku = {}, {}
    for product in product_ads:
        sku = product.sku
        if sku not in shop_skus:
            continue
        campaignId = product.campaignId
        adId = product.adId
        if sku not in res:
            res[sku] = {
                'id': adId,
                'name': sku,
                'impressions': 0,
                "clicks": 0,
                "orders": 0,
                "costs": 0,
                "sales": 0,
                "type": 'SKU',
                'show': False,
                'status': '',
                'campaigns': {},
                'children': []
            }
        if campaignId not in camp_sku:
            camp_sku[campaignId] = []
        camp_sku[campaignId].append(sku)
    for sku, sku_data in res.items():
        campaignIds = ProductAds.objects.filter(
            profileId=profileId, sku=sku).values('campaignId')
        for campaignId in campaignIds:
            campaignId = campaignId['campaignId']
            campaign = Campaign.objects.get(
                profileId=profileId, campaignId=campaignId)
            campaignName = campaign.name
            campaignStatus = campaign.state
            campaignStatus = STATUS[campaignStatus]
            camp_data = {
                'id': sku + '-' + campaignId,
                'name': campaignName,
                'impressions': 0,
                "clicks": 0,
                "orders": 0,
                "costs": 0,
                "sales": 0,
                'status': campaignStatus,
                'show': False,
                'adGroups': {},
                'children': []
            }
            if campaignId in sku_data['campaigns']:
                continue
            sku_data['children'].append(camp_data)
            sku_data['campaigns'][campaignId] = len(sku_data['children']) - 1

            adGroups = AdGroup.objects.filter(
                profileId=profileId, campaignId=campaignId)
            for adGroup in adGroups:
                adGroupId = adGroup.adGroupId
                adGroupType = adGroup.type
                adgroup_data = {
                    'id': sku + '-' + adGroupId,
                    'name': adGroup.name,
                    'impressions': 0,
                    "clicks": 0,
                    "orders": 0,
                    "costs": 0,
                    "sales": 0,
                    "type": '广告组',
                    'show': False,
                    'status': STATUS[adGroup.state],
                    'targets': {},
                    'children': []
                }
                camp_data['children'].append(adgroup_data)
                camp_data['adGroups'][adGroupId] = len(
                    camp_data['children']) - 1
                if 'type' not in camp_data and adGroupType:
                    camp_data['type'] = CAMPAIGNTYPE[adGroupType]
                keywords = Keyword.objects.filter(
                    profileId=profileId, adGroupId=adGroupId)
                for keyword in keywords:
                    keyword_data = {
                        'id': sku + '-' + keyword.keywordId,
                        'name': keyword.keywordText + '-' + keyword.matchType,
                        'impressions': 0,
                        "clicks": 0,
                        "orders": 0,
                        "costs": 0,
                        "sales": 0,
                        "type": '关键词',
                        'status': STATUS[keyword.state],
                        'show': False
                    }
                    adgroup_data['children'].append(keyword_data)
                    adgroup_data['targets'][keyword.keywordId] = len(
                        adgroup_data['children']) - 1

                targets = Target.objects.filter(
                    profileId=profileId, adGroupId=adGroupId)
                for target in targets:
                    target_data = {
                        'id': sku + '-' + target.targetId,
                        'name': target.expression[0]['value'] if 'value' in target.expression[0] else target.expression[0]['type'],
                        'impressions': 0,
                        "clicks": 0,
                        "orders": 0,
                        "costs": 0,
                        "sales": 0,
                        "type": '投放目标',
                        'status': STATUS[target.state],
                        'show': False
                    }
                    adgroup_data['children'].append(target_data)
                    adgroup_data['targets'][target.targetId] = len(
                        adgroup_data['children']) - 1
    for date in dates:
        data_dir = os.path.join(profile_dir, date)
        campaign_data_path = os.path.join(data_dir, 'campaign.json')
        if not os.path.exists(campaign_data_path):
            continue
        campaign_data = json.load(open(campaign_data_path))
        for data in campaign_data:
            campaignName = data['campaignName']
            campaignId = str(data['campaignId'])
            if campaignId not in camp_sku:
                continue
            impressions = data['impressions']
            clicks = data['clicks']
            orders = data['attributedUnitsOrdered7d']
            costs = round(data['cost'], 2)
            sales = data['attributedSales7d']
            skus = camp_sku[campaignId]
            for sku in skus:
                if sku not in res:
                    continue
                idx = res[sku]['campaigns'][campaignId]
                res[sku]['children'][idx]['impressions'] += impressions
                res[sku]['children'][idx]['clicks'] += clicks
                res[sku]['children'][idx]['orders'] += orders
                res[sku]['children'][idx]['costs'] += costs
                res[sku]['children'][idx]['sales'] += sales

                res[sku]['impressions'] += impressions
                res[sku]['clicks'] += clicks
                res[sku]['orders'] += orders
                res[sku]['costs'] += costs
                res[sku]['sales'] += sales

        keyword_data = json.load(open(os.path.join(data_dir, 'keyword.json')))
        for data in keyword_data:
            campaignName = data['campaignName']
            campaignId = str(data['campaignId'])
            if campaignId not in camp_sku:
                continue
            adGroupId = str(data['adGroupId'])
            keywordId = str(data['keywordId'])
            impressions = data['impressions']
            clicks = data['clicks']
            orders = data['attributedUnitsOrdered7d']
            costs = round(data['cost'], 2)
            sales = data['attributedSales7d']
            skus = camp_sku[campaignId]
            for sku in skus:
                if sku not in res:
                    continue
                camp_idx = res[sku]['campaigns'][campaignId]
                adgroup_idx = res[sku]['children'][camp_idx]['adGroups'][adGroupId]
                adGroup = res[sku]['children'][camp_idx]['children'][adgroup_idx]
                if keywordId not in adGroup['targets']:
                    print('keywordId:%s not active' % keywordId)
                    continue
                target_idx = adGroup['targets'][keywordId]
                target = adGroup['children'][target_idx]
                target['impressions'] += impressions
                target['clicks'] += clicks
                target['orders'] += orders
                target['costs'] += costs
                target['sales'] += sales

                adGroup['impressions'] += impressions
                adGroup['clicks'] += clicks
                adGroup['orders'] += orders
                adGroup['costs'] += costs
                adGroup['sales'] += sales

        target_data = json.load(open(os.path.join(data_dir, 'targeting.json')))
        for data in target_data:
            campaignName = data['campaignName']
            campaignId = str(data['campaignId'])
            if campaignId not in camp_sku:
                continue
            adGroupId = str(data['adGroupId'])
            targetId = str(data['targetId'])
            impressions = data['impressions']
            clicks = data['clicks']
            orders = data['attributedUnitsOrdered7d']
            costs = round(data['cost'], 2)
            sales = data['attributedSales7d']
            skus = camp_sku[campaignId]
            for sku in skus:
                if sku not in res:
                    continue
                camp_idx = res[sku]['campaigns'][campaignId]
                adgroup_idx = res[sku]['children'][camp_idx]['adGroups'][adGroupId]
                adGroup = res[sku]['children'][camp_idx]['children'][adgroup_idx]
                target_idx = adGroup['targets'][targetId]
                target = adGroup['children'][target_idx]
                target['impressions'] += impressions
                target['clicks'] += clicks
                target['orders'] += orders
                target['costs'] += costs
                target['sales'] += sales

                adGroup['impressions'] += impressions
                adGroup['clicks'] += clicks
                adGroup['orders'] += orders
                adGroup['costs'] += costs
                adGroup['sales'] += sales

    return res.values()


def DataProcess(shopId, profileId, pilot):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    data_process_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    command = 'python %s %s dataprocess' % (data_process_path, profile_dir)
    print(command)
    res = os.system(command)
    return res


def GetBids(shopId, profileId):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    analyzer_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    command = 'python %s %s bid' % (analyzer_path, profile_dir)
    res = os.system(command)
    return res


def Optimize(shopId, profileId, opt_type):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    analyzer_path = os.path.join(ANALYSER_DIR, 'analyzer.py')
    command = 'python %s %s %s' % (analyzer_path, profile_dir, opt_type)
    print(command)
    res = os.system(command)
    return res


def changeDb(shopId, profileId):
    logs = CampaignStructChangeLog.objects.all()
    for log in logs:
        if '预算' in log.changeLog:
            log.type = 'struct'
        else:
            log.type = 'bid'
        log.save()


def getSearchtermReport(shopId, profileId, searchtermType, sort_col, reverse):
    shop_dir = os.path.join(BASE_DIR, shopId)
    profile_dir = os.path.join(shop_dir, profileId)
    statistic_dir = os.path.join(profile_dir, 'statistic')
    searchterm_performance = json.load(
        open(os.path.join(statistic_dir, 'searchterm_performance.json')))
    res = []
    for sku, searchterms in searchterm_performance.items():
        if not ShopProducts.objects.filter(profileId=profileId, sku=sku).exists():
            continue
        res.append({
            'id': sku,
            'searchterm': sku,
            'children': []
        })
        children = []
        for searchterm, performance in searchterms.items():
            if performance['type'] != searchtermType:
                continue
            if performance['total'][2] == 0:
                continue  # 没有订单的不考虑
            impressions, clicks, orders, cost, sales = performance['total']
            impressions = max(impressions, 1)
            clicks = max(clicks, 1)
            ctr, cvr, acos = clicks / impressions, orders / clicks, cost / sales
            children.append({
                'id': res[-1]['id'] + '-' + searchterm,
                'searchterm': searchterm,
                'impressions': impressions,
                'clicks': clicks,
                'orders': orders,
                'ctr': ctr,
                'cvr': cvr,
                'acos': acos,
                'cost': cost,
                'sales': sales
            })
        res[-1]['children'] = sorted(children,
                                     key=lambda k: k[sort_col], reverse=int(reverse))
    return res


if __name__ == '__main__':
    # getDate('20210501', '20210526')
    impressions, clicks, orders, cost, sales = 28552, 183, 5, 69, 119
    ctr, cvr, acos = clicks / impressions, orders / clicks, cost / sales
    ctr_co = sku_ponint_ctr(ctr/DEFAULT_CTR)
    cvr_co = sku_ponint_cvr(cvr/DEFAULT_CVR)
    acos_co = sku_ponint_acos(0.3/acos)
    print(ctr_co, cvr_co, acos_co)
