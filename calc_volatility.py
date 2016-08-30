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

all_stock = pd.read_csv('all.csv')


def calcOneVolatility(df):
    last = 0
    vol_mean = 0
    for index,item in df.iterrows():
        if last == 0:
            vol_percent = None
        else:
            vol_percent = (item['close'] - last) * 100 / last
        last = item['close']
        df.loc[index, 'volatility'] = vol_percent;
        if (vol_percent):
            vol_mean += abs(vol_percent)
    vol_mean = vol_mean / (len(df) - 1)
    return df,vol_mean

def calcOne(code, timeToMarket):
#    ts.get_h_data(str(code))    #前复权
#    ts.get_h_data(str(code), autype='hfq')    #后复权
    df = ts.get_h_data(str(code).zfill(6), autype=None)    #不复权
    df,vol_mean = calcOneVolatility(df)
    df.to_csv('output/vol' + str(code).zfill(6) + '.csv')
    fig = plt.figure();

    fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
    ax = df['volatility'].plot(kind='bar', title=code)
    xlabels = []
    last_month = 0
    for item in df.index.tolist():
        if item.month == last_month:
            xlabels.append('')
        else:
            last_month = item.month
            xlabels.append(item.strftime('%Y-%m'))
    ax.set_xticklabels(xlabels)
    ax.grid(axis='y')
    return vol_mean




for index,row in all_stock.iterrows():
    code = row['code']
    name = row['name']
    timeToMarket = row['timeToMarket']
    print index
    print code , "=" , name, '  time=' + str(timeToMarket)
    vol_mean = calcOne(code, timeToMarket)
    all_stock.loc[index, 'vol_mean'] = vol_mean;

all_stock.to_csv('output/vol_mean.csv')
