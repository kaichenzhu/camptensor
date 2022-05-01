from .models import *
from .serializers import *
from .exception import *
from .utils import *
from .weights import *

def CreateOrUpdatePortfolios(portfolios, profileId):
    for portfolio in portfolios:
        portfolio['profileId'] = profileId
        portfolioId = portfolio['portfolioId']
        print('update portfolio: %s %s' % (portfolioId, portfolio['name']))
        portfolio_model = Portfolio.objects.filter(
            portfolioId=portfolioId).first()
        if portfolio_model:
            portfolio_serializer = PortfolioSerializer(
                portfolio_model, data=portfolio)
        else:
            portfolio_serializer = PortfolioSerializer(data=portfolio)
        if portfolio_serializer.is_valid():
            portfolio_serializer.save()
        else:
            raise ServiceInternelException(portfolio_serializer.errors)


def CreateOrUpdateAdGroups(adGroups, profileId):
    for adGroup in adGroups:
        adGroup['profileId'] = profileId
        adGroupId = adGroup['adGroupId']
        print('update adGroup: %s %s' % (adGroupId, adGroup['name']))
        adGroup_model = AdGroup.objects.filter(adGroupId=adGroupId).first()
        if adGroup_model:
            adGroup_serializer = AdGroupSerializer(adGroup_model, data=adGroup)
        else:
            adGroup_serializer = AdGroupSerializer(data=adGroup)
        if adGroup_serializer.is_valid():
            adGroup_serializer.save()
        else:
            raise ServiceInternelException(adGroup_serializer.errors)


def CreateOrUpdateProductAds(productAds, profileId):
    for productAd in productAds:
        if 'asin' not in productAd:
            continue
        productAd['profileId'] = profileId
        adId = productAd['adId']
        print('update productAds: %s' % (adId))
        productAd_model = ProductAds.objects.filter(adId=adId).first()
        if productAd_model:
            productAds_serializer = ProductAdsSerializer(
                productAd_model, data=productAd)
        else:
            productAds_serializer = ProductAdsSerializer(data=productAd)
        if productAds_serializer.is_valid():
            productAds_serializer.save()
        else:
            print(productAd_model)
            print(productAd)
            raise ServiceInternelException(productAds_serializer.errors)


def CreateOrUpdateKeywords(keywords, profileId):
    for keyword in keywords:
        keyword['profileId'] = profileId
        keywordId = keyword['keywordId']
        adGroupId = keyword['adGroupId']
        keywordText = keyword['keywordText']
        adgroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        if not adgroup:
            print('adgroup %s for keyword %s not found' %
                  (adGroupId, keywordId))
        elif adgroup.type is None:
            adgroup.type = 'keyword'
            adgroup.save()
        print('update keyword: %s %s' % (keywordId, keywordText))
        keyword_model = Keyword.objects.filter(
            profileId=profileId, keywordId=keywordId).first()
        if keyword_model:
            if keyword_model.keywordFormat is None:
                keyword['keywordFormat'] = format_phrase(keywordText)[0]
            keyword_serializer = KeywordSerializer(keyword_model, data=keyword)
        else:
            keyword['keywordFormat'] = format_phrase(keywordText)[0]
            keyword_serializer = KeywordSerializer(data=keyword)
        if keyword_serializer.is_valid():
            keyword_serializer.save()
        else:
            raise ServiceInternelException(keyword_serializer.errors)


def CreateOrUpdateNegativeKeywords(negativeKeywords, profileId):
    for keyword in negativeKeywords:
        keyword['profileId'] = profileId
        keywordId = keyword['keywordId']
        keywordText = keyword['keywordText']
        print('update negative keyword: %s %s' % (keywordId, keywordText))
        keyword_model = NegativeKeyword.objects.filter(
            profileId=profileId, keywordId=keywordId).first()
        if keyword_model:
            keyword_serializer = NegativeKeywordSerializer(
                keyword_model, data=keyword)
        else:
            keyword_serializer = NegativeKeywordSerializer(data=keyword)
        if keyword_serializer.is_valid():
            keyword_serializer.save()
        else:
            raise ServiceInternelException(keyword_serializer.errors)


def CreateOrUpdateCampaignNegativeKeywords(campaignNegativeKeywords, profileId):
    for keyword in campaignNegativeKeywords:
        keyword['profileId'] = profileId
        keywordId = keyword['keywordId']
        keywordText = keyword['keywordText']
        print('update campaign negative keyword: %s %s' %
              (keywordId, keywordText))
        keyword_model = CampaignNegativeKeyword.objects.filter(
            profileId=profileId, keywordId=keywordId).first()
        if keyword_model:
            keyword_serializer = CampaignNegativeKeywordSerializer(
                keyword_model, data=keyword)
        else:
            keyword_serializer = CampaignNegativeKeywordSerializer(
                data=keyword)
        if keyword_serializer.is_valid():
            keyword_serializer.save()
        else:
            raise ServiceInternelException(keyword_serializer.errors)


def CreateOrUpdateTargetings(targets, profileId):
    for target in targets:
        target['profileId'] = profileId
        targetId = target['targetId']
        print('update target: %s' % (targetId))
        expressionType = target['expressionType']
        adGroupId = target['adGroupId']
        adgroup = AdGroup.objects.get(profileId=profileId, adGroupId=adGroupId)
        if expressionType == 'manual':
            target['expressionValue'] = target['expression'][0]['value'].lower()
        if not adgroup:
            print('adgroup %s for target %s not found' % (adGroupId, targetId))
        elif adgroup.type is None:
            adgroup.type = 'auto' if expressionType == 'auto' else 'product'
            adgroup.save()
        target_model = Target.objects.filter(
            profileId=profileId, targetId=targetId).first()
        if target_model:
            target_serializer = TargetSerializer(target_model, data=target)
        else:
            target_serializer = TargetSerializer(data=target)
        if target_serializer.is_valid():
            target_serializer.save()
        else:
            raise ServiceInternelException(target_serializer.errors)


def CreateOrUpdateNegativeTargets(negativeTargets, profileId):
    for target in negativeTargets:
        target['profileId'] = profileId
        targetId = target['targetId']
        print('update negative target: %s' % (targetId))
        expressionType = target['expressionType']
        if expressionType == 'manual':
            target['expressionValue'] = target['expression'][0]['value'].lower()
        target_model = NegativeTarget.objects.filter(
            profileId=profileId, targetId=targetId).first()
        if target_model:
            target_serializer = NegativeTargetSerializer(
                target_model, data=target)
        else:
            target_serializer = NegativeTargetSerializer(data=target)
        if target_serializer.is_valid():
            target_serializer.save()
        else:
            raise ServiceInternelException(target_serializer.errors)


def CreateOrUpdateCampaigns(campaigns, profileId):
    for campaign in campaigns:
        campaign['profileId'] = profileId
        campaignId = campaign['campaignId']
        print('update campaign: %s %s' % (campaignId, campaign['name']))
        campaign_model = Campaign.objects.filter(campaignId=campaignId).first()
        if campaign_model:
            campaign_serializer = CampaignSerializer(
                campaign_model, data=campaign)
        else:
            campaign_serializer = CampaignSerializer(data=campaign)
        if campaign_serializer.is_valid():
            campaign_serializer.save()
        else:
            raise ServiceInternelException(campaign_serializer.errors)


def saveChangeLog(profileId, logtxt, logType):
    data = {
        'profileId': profileId,
        'changeLog': logtxt,
        'type': logType
    }
    campaignStructChangeLog_serializer = CampaignStructChangeLogSerializer(
        data=data)
    if campaignStructChangeLog_serializer.is_valid():
        campaignStructChangeLog_serializer.save()
    else:
        raise ServiceInternelException(
            campaignStructChangeLog_serializer.errors)


def get_product_campaigns(profileId):
    res = []
    products = ShopProducts.objects.filter(profileId=profileId)
    for product in products:
        sku = product.sku
        ads = ProductAds.objects.filter(profileId=profileId, sku=sku)
        for ad in ads:
            campaignId = ad.campaignId
            campaign_ads = ProductAds.objects.filter(
                profileId=profileId, campaignId=campaignId)
            all_found = True
            for campaign_ad in campaign_ads:
                if ShopProducts.objects.filter(profileId=profileId, sku=campaign_ad.sku).exists():
                    continue
                all_found = False
            if not all_found:
                continue
            res.append(campaignId)
    return res

def percentToNum(num):
    return round(float(num[:-1])/100, 2)

def write_obj_to_json(obj, path):
    b = json.dumps(obj)
    f2 = open(path, 'w')
    f2.write(b)
    f2.close()
