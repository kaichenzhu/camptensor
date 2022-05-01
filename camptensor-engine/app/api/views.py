import time
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from django.core.cache import cache
from django.contrib.auth import get_user_model
User = get_user_model()
from .authentication import AmzTokenAuthentication
from .amzapi import AmzapiHandler
from .dbservice import *
from .models import *
from .serializers import *
from .filters import *
from .tasks import *

class ProfileViewSet(viewsets.ModelViewSet):
    # authentication_classes = [AmzTokenAuthentication]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProfileFilter

class BindView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        userId = request.query_params['userId']
        code = request.query_params['code']
        region = request.query_params['region']
        token = AmzapiHandler.get_access_token(code, region)
        print(token)
        user = User.objects.get(id=userId)
        expir_time = int(time.time()) + token['expires_in'] - 600 # 10分钟安全期
        token['expir_time'] = expir_time
        accessToken = token['access_token']
        # create shop data
        s = user.shop_set.create(
            accessToken=accessToken,
            expirTime=expir_time,
            refreshToken=token['refresh_token'],
            tokenType=token['token_type'],
            region=region)
        cache.set(s.id, token, 60*50)
        initShopData(s)
        return Response(status.HTTP_201_CREATED)

class SynchronizeView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        syncProfileData.delay(shopId, profileId)
        return Response(status.HTTP_201_CREATED)

class SynchronizeReportView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        # profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        start = request.query_params['start']
        end = request.query_params['end']
        print('开始收集广告数据, %s - %s' % (start, end))
        profile_list = Profile.objects.filter(shop_id=int(shopId), state=1)
        for profile in profile_list:
            state = profile.state
            if state != 1: continue
            profileId = profile.profileId
            # print('开始处理广告报表%s-%s, profile:%s' % (start, end, profileId))
            # SynchronizeReportData.delay(shopId, profileId, start, end)
            print('开始处理广告结构, profile:%s' % profileId)
            syncProfileData.delay(shopId, profileId)
        return Response(status.HTTP_201_CREATED)

class CreateCampaignView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        CreateCampaign(data)
        return Response(status.HTTP_201_CREATED)

class CreateManualView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        CreateManualTargets(data)
        return Response(status.HTTP_201_CREATED)

class OptimizationTargeting(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        optimizeTarget = GetDisabledTargeting(shopId, profileId)
        return Response(optimizeTarget, status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        data = request.data
        res = PauseTargeting(data)
        return Response(res)

class RecommendationView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        recommendations = GetRecommendation(shopId, profileId)
        return Response(recommendations, status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        data = request.data
        res = PostRecommendation(data)
        return Response(res)

class OptimizationBid(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        optimizeBid = GetBid(shopId, profileId)
        return Response(optimizeBid, status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        data = request.data
        res = UpdateBid(data)
        return Response(res)

class OptimizationSearchterm(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        optimizeType = request.query_params['optimizeType']
        if optimizeType == 'negative':
            res = GetNegativeSearchterm(shopId, profileId)
        elif optimizeType == 'optimize':
            res = GetOptimizeSearchterm(shopId, profileId)
        return Response(res, status.HTTP_201_CREATED)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        optimizeType = data['optimizeType']
        if optimizeType == 'negative':
            res = PostNegativeKeywords(data)
        elif optimizeType == 'optimize':
            res = PostOptimizeSearchterm(data)
        return Response(res)

class SkuManualCampaigns(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        res = GetSkuManualCampaigns(shopId, profileId)
        return Response(res, status.HTTP_201_CREATED)

class LogBid(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        logbid = GetBidLogs(shopId, profileId)
        return Response(logbid, status.HTTP_201_CREATED)

class ShopProductsViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = ShopProducts.objects.all()
    serializer_class = ShopProductsSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ShopProductsFilter

class ProductDeleteView(APIView):

    def get(self, request, *args, **kwargs):
        shopId = request.query_params['shopId']
        profileId = request.query_params['profileId']
        id = request.query_params['id']
        res = deleteProduct(shopId, profileId, id)
        return Response(res)

class GetShopDataView(APIView):

    def get(self, request, *args, **kwargs):
        shopIds = request.query_params['shopIds']
        day = int(request.query_params['day'])
        shopIds = shopIds.strip().split(',')
        for shopId in shopIds:
            SyncShopReport.delay(shopId, day)
        return Response()

class GetProfileDataView(APIView):

    def get(self, request, *args, **kwargs):
        profileIds = request.query_params['profileIds']
        day = int(request.query_params['day'])
        profileIds = profileIds.strip().split(',')
        for profileId in profileIds:
            SyncProfileReport.delay(profileId, day)
        return Response()

class CustomView(APIView):

    def get(self, request, *args, **kwargs):
        customFunc()
        return Response()

class GetAccountInfoView(APIView):

    def get(self, request, *args, **kwargs):
        account = request.query_params['account']
        password = request.query_params['password']
        res = GetAccountInfo(account, password)
        return Response(res)

class GetBillView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        startBill = request.query_params['startBill']
        endBill = request.query_params['endBill']
        res = GetBill(profileId, startBill, endBill)
        return Response(res)
   

class ShopProductsListViewSet(APIView):

    def post(self, request, *args, **kwargs):
        shopId = request.data['shopId']
        profileId = request.data['profileId']
        productList = request.data['productList']
        res, if_bidOpt = SaveProductList(shopId, profileId, productList)
        if if_bidOpt:
            optimize.delay(shopId, profileId, 'bidopt')
        return Response(res)

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CampaignFilter

class AdgroupViewSet(viewsets.ModelViewSet):
    queryset = AdGroup.objects.all()
    serializer_class = AdGroupSerializer

class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

class SkuCampaignsView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        sku_campaigns = GetSkuCampaigns(profileId)
        return Response(sku_campaigns)

class CampaignStructView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        dataType = request.query_params['dataType']
        parentId = request.query_params['parentId']
        res = getCampaignStructure(profileId, dataType, parentId)
        return Response(res)

class CampaignStructChangeLogViewSet(viewsets.ModelViewSet):
    queryset = CampaignStructChangeLog.objects.all()
    serializer_class = CampaignStructChangeLogSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CampaignStructChangeLogFilter
    ordering_fields = ['-add_date']

class NegativeSearchtermLogViewSet(viewsets.ModelViewSet):
    queryset = NegativeSearchtermLog.objects.all()
    serializer_class = NegativeSearchtermLogSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = NegativeSearchtermLogFilter
    ordering_fields = ['-add_date']

class OptimizeSearchtermLogViewSet(viewsets.ModelViewSet):
    queryset = OptimizeSearchtermLog.objects.all()
    serializer_class = OptimizeSearchtermLogSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = OptimizeSearchtermLogFilter
    ordering_fields = ['-add_date']

class EditCampaignView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        res = EditCampaign(data)
        return Response(res)

class UpdateCampaignBudgetView(APIView):

    def get(self, request, *args, **kwargs):
        res = updateCampaignBudget.delay()
        return Response(res)

class DailyBidView(APIView):

    def get(self, request, *args, **kwargs):
        res = dailyBid.delay()
        return Response(res)

class ProductSkuView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        skus = ShopProducts.objects.filter(profileId=profileId).values('sku')
        res = list([{'value':x['sku'], 'lable':x['sku']} for x in skus])
        return Response(res)

class ProductStatusView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        res = getShopProductStatus(profileId)
        return Response(res)

class ProductTestView(APIView):

    def post(self, request, *args, **kwargs):
        shopId = request.data['shopId']
        profileId = request.data['profileId']
        product = request.data['product']
        res = startProductTest(shopId, profileId, product)
        return Response(res)

class AdsPausedView(APIView):

    def get(self, request, *args, **kwargs):
        shopId = request.query_params['shopId']
        profileId = request.query_params['profileId']
        sku = request.query_params['sku']
        res = pauseProductAds(shopId, profileId, sku)
        return Response(res)

class startAdsView(APIView):

    def get(self, request, *args, **kwargs):
        shopId = request.query_params['shopId']
        profileId = request.query_params['profileId']
        sku = request.query_params['sku']
        res = startProductAds(shopId, profileId, sku)
        return Response(res)

class ProductTargetView(APIView):

    def get(self, request, *args, **kwargs):
        shopId = request.query_params['shopId']
        profileId = request.query_params['profileId']
        sku = request.query_params['sku']
        state = int(request.query_params['state'])
        product = ShopProducts.objects.get(profileId=profileId, sku=sku)
        if state == 4:
            product.promotionTarget = 1
        elif state == 5:
            product.promotionTarget = 2
        product.state = state
        product.save()
        return Response('success')

class ProfileStateView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = str(Profile.objects.get(profileId=profileId).shop.id)
        state = request.query_params['state']
        res = changeProfileState(shopId, profileId, state)
        return Response(res)

class EditAdGroupView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        res = EditAdGroup(data)
        return Response(res)

class EditKeywordView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        res = EditKeyword(data)
        return Response(res)

class EditTargetingView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        res = EditTargeting(data)
        return Response(res)

class EditSkuView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        res = EditSku(data)
        return Response(res)

class CampaignDataView(APIView):

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        start = request.query_params['start']
        end = request.query_params['end']
        dataType = request.query_params['dataType']
        sku = request.query_params['sku']
        campaignId = request.query_params['campaignId']
        adGroupId = request.query_params['adGroupId']
        promotionTarget = request.query_params['promotionTarget'].split(',')
        if not promotionTarget or len(promotionTarget) == 0: return Response()
        if dataType == 'sku': return Response(GetSkuDetail(profileId, shopId, start, end, promotionTarget))
        elif dataType == 'campaign': return Response(GetCampaignDetail(profileId, shopId, start, end, sku))
        elif dataType == 'adgroup': return Response(GetAdGroupDetail(profileId, shopId, start, end, campaignId))
        elif dataType == 'target': return Response(GetTargetDetail(profileId, shopId, start, end, adGroupId))

class QuickCreateCampaignView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        res = QuickCreateCampaign(data)
        return Response(res)

class OptimizeView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        optType = request.query_params['optType']
        Optimization.delay(optType)
        return Response(status.HTTP_201_CREATED)

class ChangeView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        changeDb(shopId, profileId)
        return Response(status.HTTP_201_CREATED)

class SearchtermReportView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        searchtermType = request.query_params['searchtermType']
        sort_col = request.query_params['sort_col']
        reverse = request.query_params['reverse']
        searchtermReport = getSearchtermReport(shopId, profileId, searchtermType, sort_col, reverse)
        return Response(searchtermReport, status.HTTP_201_CREATED)

class GetBidsView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        GetBids(shopId, profileId)
        return Response(status.HTTP_201_CREATED)

class DataProcessView(APIView):
    # authentication_classes = [AmzTokenAuthentication]

    def get(self, request, *args, **kwargs):
        # profileId = request.query_params['profileId']
        shopId = request.query_params['shopId']
        pilot = request.query_params['pilot']
        profile_list = Profile.objects.filter(shop_id=int(shopId), state=1)
        for profile in profile_list:
            profileId = profile.profileId
            print('开始处理数据:%s' % profileId)
            DataProcess(shopId, profileId, pilot)
        return Response(status.HTTP_201_CREATED)