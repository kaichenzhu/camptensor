from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class AmzTokenException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('amazon api authentication credentials.')

class ServiceInternelException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('ServiceInternelException')

class DataValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('request data is not accept')