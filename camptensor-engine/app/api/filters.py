from django_filters import rest_framework as filters
from .models import *

class ProfileFilter(filters.FilterSet):
    userId = filters.NumberFilter(field_name='shop__advertiser__id', lookup_expr='exact')

    class Meta:
        model = Profile
        fields = ['userId', ]

class CampaignFilter(filters.FilterSet):
    class Meta:
        model = Campaign
        fields = ['profileId', ]

class ShopProductsFilter(filters.FilterSet):
    class Meta:
        model = ShopProducts
        fields = ['id', 'profileId', 'sku', 'countryCode']

class CampaignStructChangeLogFilter(filters.FilterSet):
    add_date = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CampaignStructChangeLog
        fields = ['profileId', 'type', 'add_date']

class NegativeSearchtermLogFilter(filters.FilterSet):
    add_date = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = NegativeSearchtermLog
        fields = ['profileId', 'add_date']

class OptimizeSearchtermLogFilter(filters.FilterSet):
    add_date = filters.DateTimeFromToRangeFilter()
    
    class Meta:
        model = OptimizeSearchtermLog
        fields = ['profileId', 'add_date']