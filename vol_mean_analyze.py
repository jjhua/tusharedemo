# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 19:59:06 2016

@author: megahertz
"""

import pandas as pd

def calcStock(df):
    vol_up = 0
    vol_down = 0
    vol_sum = 0
    last = 0
    for index,item in df.iterrows():
        if last == 0:
            vol_percent = None
        else:
            vol_percent = (item['close'] - last) * 100 / last
        last = item['close']
        if (vol_percent > 0):
            vol_up += 1
        elif (vol_percent < 0):
            vol_down += 1
        if vol_percent:
            vol_sum += vol_percent
#    print 'len=',len(df), ' vol_up=', vol_up, ' vol_down=', vol_down, ' vol_sum=',vol_sum
    return (vol_up,vol_down,vol_sum)


if __name__ == '__main__':
    all_stock = pd.read_csv('vol_mean.csv')
    for index,row in all_stock.iterrows():
        code = row['code']
        name = row['name']
        timeToMarket = row['timeToMarket']
        code_str = str(code).zfill(6)
        print index
        print code_str , "=" , name, '  time=' + str(timeToMarket)
        try:
            filename = 'output/vol' + code_str + '.csv'
            stock = pd.read_csv(filename)
            (vol_up,vol_down,vol_sum) = calcStock(stock)
#            stock.to_csv(filename)
            all_stock.loc[index, 'day_count'] = len(stock);
            all_stock.loc[index, 'vol_up'] = vol_up;
            all_stock.loc[index, 'vol_down'] = vol_down;
            all_stock.loc[index, 'vol_sum'] = vol_sum;
        except:
            pass
#        if index > 8:
#            break
    all_stock.to_csv('output/vol_mean.csv')
    df = all_stock[all_stock.vol_sum > 0]
    df = df.sort_values('vol_mean', ascending=False)
    df.to_csv('output/vol_mean_sel.csv')
