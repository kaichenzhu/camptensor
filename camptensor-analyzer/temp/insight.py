import pandas as pd
import numpy as np
from config import *
import matplotlib.pyplot as plt  

def sku_date_grouped():
    impressions, clicks, orders, spends, sales, sku = [], [], [], [], [], {}
    searchterm_data = pd.read_excel(searchterm_date_grouped_file)
    current_time, current_portfolio = None, None
    t_impression, t_clicks, t_orders, t_spends, t_sales, dates = [], [], [], [], [], []
    for _, row in searchterm_data.iterrows():
        date = row['Date']
        portfolio = row['Portfolio name']
        impressions = row['Impressions']
        clicks = row['Clicks']
        orders = row['7 Day Total Orders (#)']
        spends = row['Spend']
        sales = row['7 Day Total Sales ']
        if date != current_time:
            t_impression.append(impressions)
            t_clicks.append(clicks)
            t_orders.append(orders)
            t_spends.append(spends)
            t_sales.append(sales)
            dates.append(date)
            current_time = date
        else:
            t_impression[-1] += impressions
            t_clicks[-1] += clicks
            t_orders[-1] += orders
            t_spends[-1] += spends
            t_sales[-1] += sales

    acos = []
    for i in range(len(t_spends)):
        if t_sales[i] == 0:
            print(i)
            acos.append(0)
        else: acos.append(t_spends[i]/t_sales[i])
    

    cur_spend, cur_sales = 0, 0
    new_acos, new_date = [], []
    for i in range(len(t_spends)):
        cur_spend += t_spends[i]
        cur_sales += t_sales[i]
        if i % 5 == 0 and i != 0:
            new_acos.append(cur_spend / cur_sales)
            new_date.append(dates[i])
            cur_spend, cur_sales = 0, 0

    l1=plt.scatter(new_date,new_acos,alpha=0.8)
    plt.xlabel('date')
    plt.ylabel('acos')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    sku_date_grouped()