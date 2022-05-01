from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.contrib.postgres.fields import ArrayField
import django.utils.timezone as timezone

class Shop(models.Model):
    accessToken = models.CharField(max_length=1000)
    expirTime = models.IntegerField(default=0)
    refreshToken = models.CharField(max_length=1000)
    tokenType = models.CharField(max_length=200)
    lastUpdateTime = models.IntegerField(default=0)
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(default=1)
    add_date = models.DateTimeField(default=timezone.now)
    region = models.CharField(max_length=200, default='NA')

    def __str__(self):
        return self.advertiser.username

class ShopProducts(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    countryCode = models.CharField(max_length=20)
    currencyCode = models.CharField(max_length=20)
    sku = models.CharField(max_length=50)
    asin = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    macs = models.DecimalField(max_digits=8, decimal_places=4)
    promotionTarget = models.IntegerField(default=0) # 0:测试 1:推广 2:盈利 3:清仓
    state = models.IntegerField(default=0) # 0:新店数据抓取中 1:测试中 2:表现不佳暂停 3:表现优秀，放量

class ProductsRecord(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    sku = models.CharField(max_length=50)
    start = models.CharField(max_length=50)
    end = models.CharField(max_length=50)
    impressions = models.IntegerField(default=-1)
    clicks = models.IntegerField(default=-1)
    orders = models.IntegerField(default=-1)
    cost = models.IntegerField(default=-1)
    sales = models.IntegerField(default=-1)
    points = models.FloatField(default=-1.0)
    add_date = models.DateTimeField(default=timezone.now)

class Profile(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    countryCode = models.CharField(max_length=200)
    currencyCode = models.CharField(max_length=200)
    dailyBudget = models.IntegerField(default=0)
    timezone = models.CharField(max_length=200)
    accountInfo = models.JSONField(null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    state = models.IntegerField(default=0)

    def __str__(self):
        return "%d: %s" % (self.profileid, self.accountName)

class Portfolio(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    portfolioId = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=200)
    budget = models.JSONField(null=True)
    inBudget = models.BooleanField(default=False)
    state = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Campaign(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    portfolioId = models.CharField(max_length=100, db_index=True, null=True)
    campaignId =models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=200)
    tags = models.JSONField(null=True)
    campaignType = models.CharField(max_length=200)
    targetingType = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    dailyBudget = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    startDate = models.CharField(max_length=200)
    endDate = models.CharField(max_length=200, null=True)
    premiumBidAdjustment = models.BooleanField(default=False)
    bidding = models.JSONField(null=True)
    deposite = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class AdGroup(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=200)
    defaultBid = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    state = models.CharField(max_length=200)
    type =models.CharField(max_length=20,null=True)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    keywordId = models.CharField(max_length=100)
    state = models.CharField(max_length=200)
    keywordText = models.CharField(max_length=200)
    matchType = models.CharField(max_length=200)
    keywordFormat = models.CharField(max_length=200, null=True)
    bid = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    
    def __str__(self):
        return self.keywordText

class Target(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    targetId = models.CharField(max_length=100)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50)
    expression = JSONBField(default=list,null=True,blank=True)
    resolvedExpression = JSONBField(default=list,null=True,blank=True)
    expressionType = models.CharField(max_length=50)
    expressionValue = models.CharField(max_length=50,null=True)
    bid = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    

class ProductAds(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    adId = models.CharField(max_length=100)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    sku = models.CharField(max_length=200)
    asin = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

class NegativeKeyword(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    keywordId = models.CharField(max_length=100)
    keywordText = models.CharField(max_length=200)
    matchType = models.CharField(max_length=200)
    state = models.CharField(max_length=50)

class NegativeTarget(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    targetId = models.CharField(max_length=100)
    expression = JSONBField(default=list,null=True,blank=True)
    resolvedExpression = JSONBField(default=list,null=True,blank=True)
    expressionType = models.CharField(max_length=50)
    expressionValue = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50)

class CampaignNegativeKeyword(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    keywordId = models.CharField(max_length=100)
    keywordText = models.CharField(max_length=200)
    matchType = models.CharField(max_length=200)
    state = models.CharField(max_length=50)

class NegativeSearchtermLog(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    targetId = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50)
    campaignName = models.CharField(max_length=200)
    adGroupName = models.CharField(max_length=200)
    query = models.CharField(max_length=200)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    orders = models.IntegerField(default=0)
    spends = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    sales = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    add_date = models.DateTimeField(default=timezone.now)

class DisableTargetLog(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    targetId = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50)
    campaignName = models.CharField(max_length=200)
    adGroupName = models.CharField(max_length=200)
    targetName = models.CharField(max_length=200)
    targetType = models.CharField(max_length=200, null=True)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    orders = models.IntegerField(default=0)
    spends = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    sales = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    add_date = models.DateTimeField(default=timezone.now)

class OptimizeSearchtermLog(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    campaignId = models.CharField(max_length=100, db_index=True)
    adGroupId = models.CharField(max_length=100, db_index=True)
    targetId = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50)
    campaignName = models.CharField(max_length=200)
    adGroupName = models.CharField(max_length=200)
    query = models.CharField(max_length=200)
    selectCampaignId = models.CharField(max_length=100)
    selectCampaignName = models.CharField(max_length=200)
    selectAdGroupId = models.CharField(max_length=100)
    selectAdGroupName = models.CharField(max_length=200)
    matchType = ArrayField(models.CharField(max_length=50),null=True)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    orders = models.IntegerField(default=0)
    spends = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    sales = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    add_date = models.DateTimeField(default=timezone.now)

class CampaignStructChangeLog(models.Model):
    profileId = models.CharField(max_length=100, db_index=True)
    changeLog = models.TextField()
    type = models.CharField(max_length=50, db_index=True, null=True)
    add_date = models.DateTimeField(default=timezone.now) 