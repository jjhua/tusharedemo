# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 18:52:31 2016

@author: megahertz
"""

import tushare as ts
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY,YEARLY


def calcOneVolatility(df):
    last = 0
    for index,item in df.iterrows():
        if last == 0:
            vol_percent = None
        else:
            vol_percent = (item['close'] - last) * 100 / last
        last = item['close']
        df.loc[index, 'volatility'] = vol_percent;
        
    return df

def calcOne(code, timeToMarket):
#    ts.get_h_data(str(code))    #前复权
#    ts.get_h_data(str(code), autype='hfq')    #后复权
    df = ts.get_h_data(str(code).zfill(6), autype=None)    #不复权
    df = calcOneVolatility(df)
    df.to_csv('output/vol' + str(code).zfill(6) + '.csv')
    fig = plt.figure();

    fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
    ax = df['volatility'].plot(kind='bar', title=code)
#    ax.set_xticks(range(3));
#    ax.set_xticks(range(10))
#    ax.set_xlim()
    xlabels = []
    last_month = 0
    for item in df.index.tolist():
        if item.month == last_month:
            xlabels.append('')
        else:
            last_month = item.month
            xlabels.append(item)
    ax.set_xticklabels(xlabels)
#    mondays = WeekdayLocator(MONDAY)            # 主要刻度
##    alldays = DayLocator()                      # 次要刻度
#    mondayFormatter = DateFormatter('%Y-%m') # 如：2-29-2015
##    ax.xaxis.set_major_locator(mondays)
##    ax.xaxis.set_minor_locator(alldays)
#    ax.xaxis.set_major_formatter(mondayFormatter)
#    ax.xaxis_date()
##    ax.autoscale_view()
#    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.grid(True)








all_stock = pd.read_csv('all.csv')

#for code in all_stock['code']:
#    print code
#    break

i = 0
for index,row in all_stock.iterrows():
    code = row['code']
    name = row['name']
    timeToMarket = row['timeToMarket']
    print code , "=" , name, '  time=' + str(timeToMarket)
    calcOne(code, timeToMarket)
    if i >= 3:
        break
    i += 1
    
