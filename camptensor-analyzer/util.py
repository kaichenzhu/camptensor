from datetime import datetime, timedelta
from pytz import utc, timezone
import numpy as np
import os

def get_past_days(days):
    """
    获取当前时间的太平洋时间（可能是夏令时，也可能是冬令时）
    """
    today = datetime.now(tz=utc)
    res = [ today ]
    for i in range(1, days):
        day = today - timedelta(days=i)
        res.append(day)
    for i in range(len(res)):
        res[i] = res[i].astimezone(timezone('US/Pacific')).strftime('%Y%m%d')
    return res

def get_time_pass_rate():
    pst_time = datetime.now(tz=utc).astimezone(timezone('US/Pacific'))
    return (pst_time.hour * 60 + pst_time.minute) / (24 * 60)

# 消除数组中的离群值
def remove_isolation(arr):
    if len(arr) < 6: return arr, sum(arr)/len(arr), len(arr)
    arr = np.array(arr)
    Percentile = np.percentile(arr,[0,25,50,75,100])
    IQR = Percentile[3] - Percentile[1]
    UpLimit = Percentile[3]+IQR*1.5
    DownLimit = Percentile[1]-IQR*1.5
    res = arr[np.logical_and(arr <= UpLimit, arr >= DownLimit)]
    return res.mean()

if __name__ == '__main__':
    print(get_time_pass_rate())