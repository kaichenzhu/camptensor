from datetime import datetime, timedelta
from pytz import utc, timezone
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet
import json


def json_to_local(data, file):
    b = json.dumps(data)
    f2 = open(file, 'w')
    f2.write(b)
    f2.close()

# 将词组中名词转为单数


def format_phrase(phrase):
    phrase = phrase.lower()
    if len(phrase) == 10:
        if phrase.isdigit() or phrase[:2] == 'b0':
            return phrase, 'asin'
        elif phrase[:2] == 'B0':
            return phrase.lower(), 'asin'
    tokenizer = RegexpTokenizer(r'\w+')  # 删除字母数字外其他字符
    tokens = tokenizer.tokenize(phrase)
    tagged_sent = pos_tag(tokens)     # 获取单词词性
    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for word, pos in tagged_sent:
        if pos.startswith('N'):
            word = wnl.lemmatize(word, pos=wordnet.NOUN)
        elif pos.startswith('J'):
            word = wnl.lemmatize(word, pos=wordnet.ADJ)
        elif pos.startswith('V'):
            word = wnl.lemmatize(word, pos=wordnet.VERB)
        elif pos.startswith('R'):
            word = wnl.lemmatize(word, pos=wordnet.ADV)
        lemmas_sent.append(word)
    return ' '.join(lemmas_sent).lower(), 'keyword'


def get_current_pst_time(region):
    """
    获取当前时间的太平洋时间（可能是夏令时，也可能是冬令时）
    """
    if region == 'NA': timez = 'US/Pacific'
    if region == 'EU': timez = 'Etc/GMT-1'
    pst_time = datetime.now(tz=utc).astimezone(
        timezone(timez)).strftime('%Y%m%d')
    return pst_time


def get_past_days(days, region):
    """
    获取当前时间的太平洋时间（可能是夏令时，也可能是冬令时）
    """
    if region == 'NA': timez = 'US/Pacific'
    if region == 'EU': timez = 'Etc/GMT-1'
    today = datetime.now(tz=utc)
    res = [today]
    for i in range(1, days):
        day = today - timedelta(days=i)
        res.append(day)
    for i in range(len(res)):
        res[i] = res[i].astimezone(timezone(timez)).strftime('%Y%m%d')
    return res


def get_recent_days(start, region):
    if region == 'NA': timez = 'US/Pacific'
    if region == 'EU': timez = 'Etc/GMT-1'
    today = datetime.now(tz=utc)
    res = [today.astimezone(timezone(timez)).strftime('%Y%m%d')]
    if datetime.strptime(start, "%Y%m%d") > datetime.strptime(res[0], "%Y%m%d"):
        return start, False
    i = 1
    while res[-1] != start:
        day = today - timedelta(days=i)
        res.append(day.astimezone(timezone(timez)).strftime('%Y%m%d'))
        i += 1
    return res, True


if __name__ == '__main__':
    print(get_past_days(1))
