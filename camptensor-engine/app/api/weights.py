import os
BASE_DIR = os.environ.get("REPORT_DATA", "/root/data")
ANALYSER_DIR = os.environ.get("ANALYSER_DIR")

# amzapi
CALL_MIN_TIME = 4
CALL_TIME = 2
CALL_MAX_TIME = 128

TARGETING_MATCHTYPE_CO = {
    'broad': 0.7,
    'phrase': 0.85,
    'exact': 1,
    'BROAD': 0.7,
    'PHRASE': 0.85,
    'EXACT': 1
}
STATUS = {
    'enabled': '运行',
    'paused': '暂停',
    'archived': '存档'
}
PROMOTIONSTATUS = {
    0: '测试',
    1: '推广',
    2: '盈利',
    3: '清仓'
}
CAMPAIGNTYPE = {
    'AUTO': 'auto',
    'KEYWORDS': 'keyword',
    'ASIN': 'product'
}
CAMPAIGNTYPE = {
    'auto': '自动广告',
    'keyword': '关键词广告',
    'product': '商品广告'
}

DEFAULT_CTR = 0.004
DEFAULT_ACOS = 0.35

TEST_CLICK_1 = 20
TEST_CLICK_2 = 60
TEST_DAY = 7
PERFORMANCE_1 = 4
PERFORMANCE_2 = 6.5
PERFORMANCE_3 = 8
FULL_SCORE = 10

WORD_POINT_CTR = [0.44170693, 2.5198298, 0.66554102, 0.99833884, 1.52838946]
WORD_POINT_CVR = [1.16715955, 4.44685412, 0.50580596, 2.47324923, 0.68486095]
WORD_POINT_ACOS = [1.86128753, 4.06296966, 0.58468287, 3.95402198, 1.08574716]

DEFUALT_PRICE = [0.3, 0.4, 0.5, 0.6]