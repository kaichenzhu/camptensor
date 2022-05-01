import requests
import json
import gzip
import time
import os
from django.core.cache import cache
from .models import Shop
from .exception import AmzTokenException
from .weights import *

DOMAIN_HOST_ADD = os.environ.get("DOMAIN_HOST_ADD", 'localhost')
CALLBACK_ADD = '%s/console/callback' % DOMAIN_HOST_ADD
AMZ_CLIENT_ID = os.environ.get("AMZ_CLIENT_ID", 'djangodefaultid')
AMZ_CLIENT_SECRET = os.environ.get("AMZ_CLIENT_SECRET", 'djangodefualtsecret')
NA_ENDPOINT_URL = 'https://advertising-api.amazon.com'
EU_ENDPOINT_URL = 'https://advertising-api-eu.amazon.com'
FE_ENDPOINT_URL = 'https://advertising-api-fe.amazon.com'
NA_TOKEN_URL = 'https://api.amazon.com/auth/o2/token'
EU_TOKEN_URL = 'https://api.amazon.co.uk/auth/o2/token'
FE_TOKEN_URL = 'https://api.amazon.co.jp/auth/o2/token'


class RequestHandler:
    def __init__(self):
        self.session = requests.session()

    def visit(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        return self.session.request(
            method, url, params=params, data=data, json=json, headers=headers, **kwargs)

    def close_session(self):
        self.session.close()


class AmzapiHandler:
    def __init__(self, shopId=None, profileid=None):
        self.shopId = shopId
        self.region = Shop.objects.get(id=int(shopId)).region
        if self.region == 'NA':
            self.TOKEN_URL = NA_TOKEN_URL
            self.ENDPOINT_URL = NA_ENDPOINT_URL
        elif self.region == 'EU':
            self.TOKEN_URL = EU_TOKEN_URL
            self.ENDPOINT_URL = EU_ENDPOINT_URL
        elif self.region == 'FE':
            self.TOKEN_URL = FE_TOKEN_URL
            self.ENDPOINT_URL = FE_ENDPOINT_URL
        self.profileid = profileid
        self.headers = {
            'Content-Type': 'application/json',
            'Amazon-Advertising-API-ClientId': AMZ_CLIENT_ID,
            'Amazon-Advertising-API-Scope': profileid
        }
        self.data = {}
        self.request = RequestHandler()
        print(self.region, self.TOKEN_URL, self.ENDPOINT_URL)

    @staticmethod
    def get_access_token(code, region):
        request = RequestHandler()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': CALLBACK_ADD,
            'client_id': AMZ_CLIENT_ID,
            'client_secret': AMZ_CLIENT_SECRET
        }
        if region == 'NA':
            url = NA_TOKEN_URL
        elif region == 'EU':
            url = EU_TOKEN_URL
        elif region == 'FE':
            url = FE_TOKEN_URL
        return request.visit(method='post', url=url, headers=headers, data=data).json()

    def refresh_token(self, refresh_token):
        request = RequestHandler()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        data = {
            'grant_type': 'refresh_token',
            'client_id': AMZ_CLIENT_ID,
            'refresh_token': refresh_token,
            'client_secret': AMZ_CLIENT_SECRET
        }
        return request.visit(method='post', url=self.TOKEN_URL, headers=headers, data=data).json()

    def get_profiles(self):
        request = RequestHandler()
        accessToken = self.getAccessToken()
        headers = {
            'Authorization': 'bearer %s' % accessToken,
            'Amazon-Advertising-API-ClientId': AMZ_CLIENT_ID
        }
        url = '%s/v2/profiles' % self.ENDPOINT_URL
        return request.visit(method='get', url=url, headers=headers).json()

    def call(self, url, method, data=None, params=None, wait=5):
        accessToken = self.getAccessToken()
        self.headers['Authorization'] = 'bearer %s' % accessToken
        if self.headers['Content-Type'] == 'application/json':
            res = self.request.visit(
                method=method, url=url, headers=self.headers, json=data, params=params).json()
        else:
            res = self.request.visit(
                method=method, url=url, headers=self.headers, data=data, params=params).json()
        if type(res) is not list:
            print(res)
            if 'code' in res and res['code'] in ['429', '500']:
                time.sleep(wait)
                print('retry: ', url, method, data, params, wait*2)
                return self.call(url, method, data, params, wait*2)
        return res

    def getAccessToken(self):
        shopId = self.shopId
        token = cache.get(shopId)
        if not token:
            shop = Shop.objects.get(id=shopId)
            if not shop:
                raise AmzTokenException('tokenUnreachable')
            expir_time = shop.expirTime
            refresh_token = shop.refreshToken
            token = {
                "access_token": shop.accessToken,
                "refresh_token": refresh_token,
                "token_type": shop.tokenType,
                "expir_time": expir_time
            }
            cache.set(shopId, token, 60*50)
        else:
            expir_time = token['expir_time']
            refresh_token = token['refresh_token']
        if expir_time < int(time.time()):
            new_token = self.refresh_token(refresh_token)
            expirTime = int(time.time()) + \
                new_token['expires_in'] - 600  # 10分钟安全期
            Shop.objects.filter(id=shopId).update(
                accessToken=new_token['access_token'],
                expirTime=expirTime
            )
            new_token['expir_time'] = expirTime
            cache.set(shopId, new_token, 60*50)
            return new_token['access_token']
        return token['access_token']

    def get_manageaccounts(self):
        return self.call('%s/managerAccounts' % self.ENDPOINT_URL, 'get')

    def get_portfolios(self):
        return self.call('%s/v2/portfolios/extended' % self.ENDPOINT_URL, 'get')

    def create_portfolio(self, data):
        return self.call('%s/v2/portfolios' % self.ENDPOINT_URL, 'get')

    def get_campaigns(self, params=None):
        return self.call('%s/v2/sp/campaigns/extended' % self.ENDPOINT_URL, 'get', params=params)

    def get_campaign_byId(self, campaignId):
        return self.call('%s/v2/sp/campaigns/%s' % (self.ENDPOINT_URL, campaignId), 'get')

    def create_campaigns(self, data):
        return self.call('%s/v2/sp/campaigns' % self.ENDPOINT_URL, 'post', data=data)

    def update_campaigns(self, data):
        return self.call('%s/v2/sp/campaigns' % self.ENDPOINT_URL, 'put', data=data)

    def get_adGroups(self, params):
        return self.call('%s/v2/sp/adGroups/extended' % self.ENDPOINT_URL, 'get', params=params)

    def get_adGroup_byId(self, adGroupId):
        return self.call('%s/v2/sp/adGroups/%s' % (self.ENDPOINT_URL, adGroupId), 'get')

    def create_adGroups(self, data):
        return self.call('%s/v2/sp/adGroups' % self.ENDPOINT_URL, 'post', data=data)

    def update_adGroups(self, data):
        return self.call('%s/v2/sp/adGroups' % self.ENDPOINT_URL, 'put', data=data)

    def get_productAds(self, params):
        return self.call('%s/v2/sp/productAds/extended' % self.ENDPOINT_URL, 'get', params=params)

    def update_productAds(self, data):
        return self.call('%s/v2/sp/productAds' % self.ENDPOINT_URL, 'put', data=data)

    def get_productAds_byId(self, adId):
        return self.call('%s/v2/sp/productAds/%s' % (self.ENDPOINT_URL, adId), 'get')

    def create_productAds(self, data):
        return self.call('%s/v2/sp/productAds' % self.ENDPOINT_URL, 'post', data=data)

    def get_keywords(self, params):
        return self.call('%s/v2/sp/keywords/extended' % self.ENDPOINT_URL, 'get', params=params)

    def update_keywords(self, data):
        return self.call('%s/v2/sp/keywords' % self.ENDPOINT_URL, 'put', data=data)

    def create_keywords(self, data):
        return self.call('%s/v2/sp/keywords' % self.ENDPOINT_URL, 'post', data=data)

    def get_targets(self, params):
        return self.call('%s/v2/sp/targets/extended' % self.ENDPOINT_URL, 'get', params=params)

    def update_taregets(self, data):
        return self.call('%s/v2/sp/targets' % self.ENDPOINT_URL, 'put', data=data)

    def create_taregets(self, data):
        return self.call('%s/v2/sp/targets' % self.ENDPOINT_URL, 'post', data=data)

    def get_negative_keywords(self, params):
        return self.call('%s/v2/sp/negativeKeywords/extended' % self.ENDPOINT_URL, 'get', params=params)

    def create_negative_keywords(self, data):
        return self.call('%s/v2/sp/negativeKeywords' % self.ENDPOINT_URL, 'post', data=data)

    def create_negative_products(self, data):
        return self.call('%s/v2/sp/negativeTargets' % self.ENDPOINT_URL, 'post', data=data)

    def get_negative_products(self, params):
        return self.call('%s/v2/sp/negativeTargets/extended' % self.ENDPOINT_URL, 'get', params=params)

    def get_product_targeting(self, campaignid):
        params = {
            'campaignIdFilter': campaignid
        }
        return self.call('%s/v2/sp/targets' % self.ENDPOINT_URL, 'get', params=params)

    def get_report(self, report_type, data, max_waiting_time=CALL_MAX_TIME):
        report = self.call('%s/v2/sp/%s/report' %
                           (self.ENDPOINT_URL, report_type), 'post', data=data)
        if 'reportId' not in report:
            print(report)
        report_id = report['reportId']
        report = {}
        waiting_time = CALL_MIN_TIME
        while 'location' not in report and waiting_time <= max_waiting_time:
            print('waiting_time is %d' % waiting_time)
            time.sleep(waiting_time)
            waiting_time *= CALL_TIME
            report = self.call('%s/v2/reports/%s' %
                               (self.ENDPOINT_URL, report_id), 'get')
        assert 'location' in report, 'report request is overtime for record_type:%s report_date:%s' % (
            report_type, data['reportDate'])
        report = self.request.visit(
            method='get', url=report['location'], headers=self.headers)
        return json.loads(gzip.decompress(report.content))

    def get_snapshot(self, record_type, stateFilter=None, max_waiting_time=CALL_MAX_TIME):
        snapshot = self.call('%s/v2/sp/%s/snapshot' %
                             (self.ENDPOINT_URL, record_type), 'post', data=stateFilter)
        snapshot_id = snapshot['snapshotId']
        snapshot = {}
        waiting_time = CALL_MIN_TIME
        while 'location' not in snapshot and waiting_time <= max_waiting_time:
            print('waiting_time is %d' % waiting_time)
            time.sleep(waiting_time)
            waiting_time *= CALL_TIME
            snapshot = self.call('%s/v2/sp/snapshots/%s' %
                                 (self.ENDPOINT_URL, snapshot_id), 'get')
        assert 'location' in snapshot, 'snapshot request is overtime for record_type:%s' % record_type
        report = self.request.visit(
            method='get', url=snapshot['location'], headers=self.headers)
        return json.loads(report.content)
