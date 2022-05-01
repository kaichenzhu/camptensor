from rest_framework.authentication import BaseAuthentication
from django.core.cache import cache
from django.contrib.auth import get_user_model
User = get_user_model()
from .exception import AmzTokenException
from .models import Shop

class AmzTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # get parameters 
        user_id = request.query_params.get('userId')
        shop_id = user_id = request.query_params.get('shopId')

        # post data
        if not user_id:
            user_id = request.data['userId']
            shop_id = request.data['shopId']

        token = cache.get(user_id)
        if not token:
            shop = Shop.objects.get(id=shop_id)
            if not shop:
                raise AmzTokenException('tokenUnreachable')
            token = {
                "access_token": shop.accessToken,
                "refresh_token": shop.refreshToken,
                "token_type": shop.tokenType,
                "expir_time": shop.expirTime
            }
            cache.set(user_id, token, 60*50)
        return (User.objects.get(id=user_id), token)