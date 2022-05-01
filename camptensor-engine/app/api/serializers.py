from rest_framework import serializers
from django.db.models import fields
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'

class ShopProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProducts
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class AdGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdGroup
        fields = '__all__'

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

class NegativeKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeKeyword
        fields = '__all__'

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'

class NegativeTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeTarget
        fields = '__all__'

class CampaignNegativeKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignNegativeKeyword
        fields = '__all__'

class ProductAdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAds
        fields = '__all__'

class NegativeSearchtermLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeSearchtermLog
        fields = '__all__'

class DisableTargetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisableTargetLog
        fields = '__all__'

class OptimizeSearchtermLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizeSearchtermLog
        fields = '__all__'

class CampaignStructChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignStructChangeLog
        fields = '__all__'