from __future__ import absolute_import, unicode_literals
 
from celery import Celery
from django.conf import settings
from .celeryconfig import BROKER_URL
import os

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# 实例化Celery

app = Celery('server')

# 使用django的settings文件配置celery
app.config_from_object("server.celeryconfig")
 
# Celery加载所有注册的应用
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)