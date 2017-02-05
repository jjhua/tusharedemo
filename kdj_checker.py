# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 17:56:27 2017

@author: megahertz
"""

import lxml.html
import matplotlib.pyplot as plt
import matplotlib as mpl
import tushare as ts
import datetime
import time
import talib as ta
import numpy as np
import pandas as pd

from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY,YEARLY
from matplotlib.finance import fetch_historical_yahoo
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
from matplotlib.patches import Rectangle
from matplotlib.dates import date2num

begin_time = '2010-01-01'
begin_time_check_now = '2016-01-01'

default_name = 'kdj'
output_dir = './output/' + default_name + '/'


#通过KDJ判断买入卖出
def Get_KDJ(df):
    #参数9,3,3
    slowk, slowd = ta.STOCH(np.array(df['high']), np.array(df['low']), np.array(df['close']), fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
   
    slowkMA5 = ta.MA(slowk, timeperiod=5, matype=0)
    slowkMA10 = ta.MA(slowk, timeperiod=10, matype=0)
    slowkMA20 = ta.MA(slowk, timeperiod=20, matype=0)
    slowdMA5 = ta.MA(slowd, timeperiod=5, matype=0)
    slowdMA10 = ta.MA(slowd, timeperiod=10, matype=0)
    slowdMA20 = ta.MA(slowd, timeperiod=20, matype=0)
    # K,D      
    slowk_index = df.shape[1]
    df['slowk']=pd.Series(slowk,index=df.index) #K
    slowd_index = df.shape[1]
    df['slowd']=pd.Series(slowd,index=df.index)#D
    dflen = df.shape[0]
    MAlen = len(slowkMA5)
    operate = 0
    #1.K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；D大于80时，行情呈现超买现象。D小于20时，行情呈现超卖现象。
    if df.iat[(dflen-1),slowk_index]>=90:
        operate = operate - 3
    elif df.iat[(dflen-1),slowk_index]<=10:
        operate = operate + 3
       
    if df.iat[(dflen-1),slowd_index]>=80:
        operate = operate - 3
    elif df.iat[(dflen-1),slowd_index]<=20:
        operate = operate + 3
       
    #2.上涨趋势中，K值大于D值，K线向上突破D线时，为买进信号。#待修改
    if df.iat[(dflen-1),slowk_index]> df.iat[(dflen-1),slowd_index] and df.iat[(dflen-2),slowk_index]<=df.iat[(dflen-2),slowd_index]:
        operate = operate + 10
    #下跌趋势中，K小于D，K线向下跌破D线时，为卖出信号。#待修改
    elif df.iat[(dflen-1),slowk_index]< df.iat[(dflen-1),slowd_index] and df.iat[(dflen-2),slowk_index]>=df.iat[(dflen-2),slowd_index]:
        operate = operate - 10
   
       
    #3.当随机指标与股价出现背离时，一般为转势的信号。
    if df.iat[(dflen-1),7]>=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]>=df.iat[(dflen-1),9]:#K线上涨
        if (slowkMA5[MAlen-1]<=slowkMA10[MAlen-1] and slowkMA10[MAlen-1]<=slowkMA20[MAlen-1]) or \
           (slowdMA5[MAlen-1]<=slowdMA10[MAlen-1] and slowdMA10[MAlen-1]<=slowdMA20[MAlen-1]): #K,D下降
            operate = operate - 1
    elif df.iat[(dflen-1),7]<=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]<=df.iat[(dflen-1),9]:#K线下降
        if (slowkMA5[MAlen-1]>=slowkMA10[MAlen-1] and slowkMA10[MAlen-1]>=slowkMA20[MAlen-1]) or \
           (slowdMA5[MAlen-1]>=slowdMA10[MAlen-1] and slowdMA10[MAlen-1]>=slowdMA20[MAlen-1]): #K,D上涨
            operate = operate + 1
           
    return operate

def check_stock(code, name):
#    print name
    success_count = 0
    failed_count = 0
    
    df = ts.get_hist_data(code, start=begin_time)
    df = df.sort_index(0)
    dflen = df.shape[0]
    if dflen>35:
        last_operator_price_close = 0
        last_operator = 0
        df[default_name + '_SUM'] = pd.Series()
        df[default_name + '_result'] = pd.Series()
        for dflen in range(36, df.shape[0] + 1):
            curdf = pd.DataFrame(df[:dflen])

            operate = Get_KDJ(curdf)
                    
            if operate != 0:
                df[default_name + '_SUM'][dflen - 1] = operate
            
            if operate == 0:
                continue
            cur_operator_price_close = curdf['close'][dflen - 1]
            if last_operator * operate > 0:
                continue
#            print code, name, 'operate=', operate, '  last_operator=', last_operator,
#            print '   cur_operator_price_close=', cur_operator_price_close,
#            print '   last_operator_price_close=', last_operator_price_close
            if operate > 0:
                if operate < 10:
                    continue
#                print 'operate=买入 price=',cur_operator_price_close
                pass
            else:
                if operate > -9:
                    continue
#                print 'operate=卖出 ',
#                print '   success=', (cur_operator_price_close > last_operator_price_close)
#                print '   curprice=',cur_operator_price_close,
#                print '   last_operator_price_close=', last_operator_price_close
                if last_operator_price_close != 0:
                    if cur_operator_price_close > last_operator_price_close:
                        success_count += 1
                        df[default_name + '_result'][dflen - 1] = 1
                    else:
                        failed_count += 1
                        df[default_name + '_result'][dflen - 1] = -1
                
            last_operator = operate
            last_operator_price_close = cur_operator_price_close



    df.to_csv(output_dir + code + '.csv')
    return (success_count,failed_count)
    
    
def checkAll():
    all_stock = pd.read_csv('all.csv')
    all_stock[default_name + '_success'] = pd.Series()
    all_stock[default_name + '_fail'] = pd.Series()
    for index,row in all_stock.iterrows():
        code = row['code']
        name = row['name']
        code_str = str(code).zfill(6)
        print code_str, '=', name
        success_count,failed_count = check_stock(code_str, name)
        all_stock.loc[index, default_name + '_success'] = success_count
        all_stock.loc[index, default_name + '_fail'] = failed_count
        if (success_count > failed_count) and (success_count > 1) and (failed_count == 0):
            print code_str, name, '  success_count=', success_count,'  failed_count=', failed_count

    all_stock = all_stock.sort_values(default_name + '_success', 0, False)
    all_stock.to_csv(output_dir + 'summy.csv')

def check_stock_now(code, name):
    operate = 0
        
    
    df = ts.get_hist_data(code, start=begin_time_check_now)
    df = df.sort_index(0)
    dflen = df.shape[0]
    if dflen>35:
        df[default_name + '_SUM'] = pd.Series()
        curdf = pd.DataFrame(df[:dflen])
        operate = Get_KDJ(curdf)

    return operate

def checknow():
    all_stock = pd.read_csv('all.csv')
    for index,row in all_stock.iterrows():
        code = row['code']
        name = row['name']
        code_str = str(code).zfill(6)
#        print code_str, '=', name
        operate = check_stock_now(code_str, name)
        all_stock.loc[index, 'operate'] = operate
        if operate != 0:
            success_count,failed_count = check_stock(code_str, name)
            all_stock.loc[index, default_name + '_success'] = success_count
            all_stock.loc[index, default_name + '_fail'] = failed_count
            if (success_count >= 4):
                print code_str, name, '  operate=', operate,
                print '  success_count=', success_count,'  failed_count=', failed_count
            
    result_data = all_stock[all_stock.operate != 0].sort_values(default_name + '_success', 0, False)
    result_data.to_csv(output_dir + 'day/' + datetime.date.today().strftime('%Y-%m-%d') + '.csv')

def checkSome():
    codes = [
            300218
    ]
    for code in codes:
        code_str = str(code).zfill(6)
        print code_str
        check_stock(code_str, 'test')

if __name__ == '__main__':    
    checknow()
#    checkAll()
#    checkSome()
#    check_stock('600800', 'test')
    print 'finish'
