from celery.schedules import crontab
import os

REDIS_HOST = os.environ.get("REDIS_HOST", 'redis')
REDIS_PASS = os.environ.get("REDIS_PASS", '123')
BROKER_URL = "redis://:%s@%s:6379/1" % (REDIS_PASS, REDIS_HOST)
CELERY_RESULT_BACKEND = BROKER_URL

# celery内容等消息的格式设置
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# 时区
CELERY_TIMEZONE = 'Asia/Shanghai'

CELERYBEAT_SCHEDULE = {
    # 'test1': {
    #     'task': 'api.tasks.dailyBid',
    #     'schedule': crontab(minute=1, hour="8"),
    #     'args': ()
    # },
    # 'test2': {
    #     'task': 'api.tasks.Optimization',
    #     'schedule': crontab(minute=25, hour="7"),
    #     'args': ('wordRecommend',)
    # }
    'SyncReport_optimize_bid_budget': {
        'task': 'api.tasks.SyncReport_optimize_bid_budget',
        'schedule': crontab(hour='1,7,13,19', minute=33),
        'args': (1,)
    },
    'SynchronizeReportBy_3_Date': {
        'task': 'api.tasks.SyncReport',
        'schedule': crontab(minute=0, hour="5", day_of_week=[0,1,2,3,4,5]),
        'args': (3,)
    },
    'SynchronizeReportBy_7_Date': {
        'task': 'api.tasks.SyncReport',
        'schedule': crontab(minute=0, hour="2", day_of_week=[6]),
        'args': (7,)
    },
    'BidOpt': {
        'task': 'api.tasks.Optimization',
        'schedule': crontab(minute=0, hour="4", day_of_week=[6]),
        'args': ('bidopt',) 
    },
    'KeywordOptimization': {
        'task': 'api.tasks.Optimization',
        'schedule': crontab(minute=40, hour="9", day_of_week=[0,2,4]),
        'args': ('searchtermOpt',)
    },
    'TargetOptimization': {
        'task': 'api.tasks.Optimization',
        'schedule': crontab(minute=30, hour="9", day_of_week=[0,2,4]),
        'args': ('targetOpt',)
    },
    'KeywordRecommendation': {
        'task': 'api.tasks.Optimization',
        'schedule': crontab(minute=20, hour="9", day_of_week=[1,3,6]),
        'args': ('wordRecommend',)
    },
    'CampaignCheck': {
        'task': 'api.tasks.Check',
        'schedule': crontab(minute=0, hour="2"),
        'args': ()
    }
}