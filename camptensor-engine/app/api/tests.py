from datetime import datetime, timedelta

def getDate(start, end):
    dates = []
    yyyy, mm, dd = start[:4], start[4:6], start[7:] if start[6] == '0' else start[6:]
    start = datetime(int(yyyy), int(mm), int(dd))
    day = -1
    while len(dates) == 0 or dates[-1] != end:
        date = start + timedelta(days=day)
        day += 1
        dates.append(date.isoformat().replace('-','')[:8])
    return dates[:-1]

if __name__ == '__main__':
    print(getDate('20210430', '20210526'))