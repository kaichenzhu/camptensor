from django.urls import re_path
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title="api API")

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet)
router.register(r'portfolio', views.PortfolioViewSet)
router.register(r'campaign', views.CampaignViewSet)
router.register(r'adgroup', views.AdgroupViewSet)
router.register(r'keyword', views.KeywordViewSet)
router.register(r'shopProducts', views.ShopProductsViewSet)
router.register(r'campaignStructLog', views.CampaignStructChangeLogViewSet)
router.register(r'negativeLog', views.NegativeSearchtermLogViewSet)
router.register(r'optimizeLog', views.OptimizeSearchtermLogViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    re_path(r'docs$', schema_view),
    re_path(r'bind$', views.BindView.as_view()),
    re_path(r'synchronize$', views.SynchronizeView.as_view()),
    re_path(r'createCampaign$', views.CreateCampaignView.as_view()),
    re_path(r'createManual$', views.CreateManualView.as_view()),
    re_path(r'synchronizeReport$', views.SynchronizeReportView.as_view()),
    re_path(r'optimization-targeting$', views.OptimizationTargeting.as_view()),
    re_path(r'optimization-bid$', views.OptimizationBid.as_view()),
    re_path(r'optimization-searchterm$', views.OptimizationSearchterm.as_view()),
    re_path(r'optimization-recommend$', views.RecommendationView.as_view()),
    re_path(r'getSkuManualCampaigns$', views.SkuManualCampaigns.as_view()),
    re_path(r'shopProductsList$', views.ShopProductsListViewSet.as_view()),
    re_path(r'log-bid$', views.LogBid.as_view()),
    re_path(r'sku-campaign$', views.SkuCampaignsView.as_view()),
    re_path(r'campaignStruct$', views.CampaignStructView.as_view()),
    re_path(r'editCampaign$', views.EditCampaignView.as_view()),
    re_path(r'editAdGroup$', views.EditAdGroupView.as_view()),
    re_path(r'editKeyword$', views.EditKeywordView.as_view()),
    re_path(r'editTargeting$', views.EditTargetingView.as_view()),
    re_path(r'editSku$', views.EditSkuView.as_view()),
    re_path(r'campaignData$', views.CampaignDataView.as_view()),
    re_path(r'quickCreateCampaign$', views.QuickCreateCampaignView.as_view()),
    re_path(r'updateCampaignBudget$', views.UpdateCampaignBudgetView.as_view()),
    re_path(r'dailyBid$', views.DailyBidView.as_view()),
    re_path(r'optimize$', views.OptimizeView.as_view()),
    re_path(r'getBids$', views.GetBidsView.as_view()),
    re_path(r'dataProcess$', views.DataProcessView.as_view()),
    re_path(r'change$', views.ChangeView.as_view()),
    re_path(r'searchtermReport$', views.SearchtermReportView.as_view()),
    re_path(r'productSku$', views.ProductSkuView.as_view()),
    re_path(r'getProductsStatus$', views.ProductStatusView.as_view()),
    re_path(r'startTest$', views.ProductTestView.as_view()),
    re_path(r'pauseAds$', views.AdsPausedView.as_view()),
    re_path(r'startAds$', views.startAdsView.as_view()),
    re_path(r'changeProductTarget$', views.ProductTargetView.as_view()),
    re_path(r'changeProfileState$', views.ProfileStateView.as_view()),
    re_path(r'deleteProduct$', views.ProductDeleteView.as_view()),
    re_path(r'getShopData$', views.GetShopDataView.as_view()),
    re_path(r'getProfileData$', views.GetProfileDataView.as_view()),
    re_path(r'custom$', views.CustomView.as_view()),
    re_path(r'getAccountInfo$', views.GetAccountInfoView.as_view()),
    re_path(r'getBill$', views.GetBillView.as_view()),
]