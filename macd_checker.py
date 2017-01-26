# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 18:35:58 2017

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
        df['macd_DIFF_DEA'] = pd.Series()
        df['macd_DEA_K'] = pd.Series()
        df['macd_MACD_SELF'] = pd.Series()
        df['macd_SUM'] = pd.Series()
        for dflen in range(36, df.shape[0] + 1):
            curdf = pd.DataFrame(df[:dflen])
            macd, macdsignal, macdhist = ta.MACD(np.array(curdf['close']), fastperiod=12, slowperiod=26, signalperiod=9)

            operate = 0
            
            SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
            SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
            SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
            
            #在后面增加3列，分别是13-15列，对应的是 DIFF  DEA  DIFF-DEA       
            curdf['macd']=pd.Series(macd,index=curdf.index) #DIFF
            curdf['macdsignal']=pd.Series(macdsignal,index=curdf.index)#DEA
            curdf['macdhist']=pd.Series(macdhist,index=curdf.index)#DIFF-DEA
            MAlen = len(SignalMA5)
            
            #2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
            #待修改
            if curdf.iat[(dflen-1),13]>0:
                if curdf.iat[(dflen-1),14]>0:
                    if curdf.iat[(dflen-1),13]>curdf.iat[(dflen-1),14] and curdf.iat[(dflen-2),13]<=curdf.iat[(dflen-2),14]:
                        operate = operate + 10#买入
                        df['macd_DIFF_DEA'][dflen - 1] = 1
            else:
                if curdf.iat[(dflen-1),14]<0:
                    if curdf.iat[(dflen-1),13] == curdf.iat[(dflen-2),14]:
                        operate = operate - 10#卖出
                        df['macd_DIFF_DEA'][dflen - 1] = -1
            
            #3.DEA线与K线发生背离，行情反转信号。
            if curdf.iat[(dflen-1),7]>=curdf.iat[(dflen-1),8] and curdf.iat[(dflen-1),8]>=curdf.iat[(dflen-1),9]:#K线上涨
                if SignalMA5[MAlen-1]<=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]<=SignalMA20[MAlen-1]: #DEA下降
                    operate = operate - 1
                    df['macd_DEA_K'][dflen - 1] = 1
            elif curdf.iat[(dflen-1),7]<=curdf.iat[(dflen-1),8] and curdf.iat[(dflen-1),8]<=curdf.iat[(dflen-1),9]:#K线下降
                if SignalMA5[MAlen-1]>=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]>=SignalMA20[MAlen-1]: #DEA上涨
                    operate = operate + 1
                    df['macd_DEA_K'][dflen - 1] = -1
                       
               
            #4.分析MACD柱状线，由负变正，买入信号。
            if curdf.iat[(dflen-1),15]>0 and dflen >30 :
                for i in range(1,26):
                    if curdf.iat[(dflen-1-i),15]<=0:#
                        operate = operate + 5
                        df['macd_MACD_SELF'][dflen - 1] = 1
                        break
                    #由正变负，卖出信号   
            if curdf.iat[(dflen-1),15]<0 and dflen >30 :
                for i in range(1,26):
                    if curdf.iat[(dflen-1-i),15]>=0:#
                        operate = operate - 5
                        df['macd_MACD_SELF'][dflen - 1] = -1
                        break
                    
            df['macd_SUM'][dflen - 1] = operate
            
            if operate == 0:
                continue
            cur_operator_price_close = curdf['close'][dflen - 1]
#            print code, name, 'operate=', operate, '  last_operator=', last_operator,
#            print '   cur_operator_price_close=', cur_operator_price_close,
#            print '   last_operator_price_close=', last_operator_price_close
            if last_operator == operate:
                continue
            if operate > 0:
#                print 'operate=买入 price=',cur_operator_price_close
                pass
            else:
#                print 'operate=卖出 ',
#                print '   success=', (cur_operator_price_close > last_operator_price_close)
#                print '   curprice=',cur_operator_price_close,
#                print '   last_operator_price_close=', last_operator_price_close
                if last_operator_price_close == 0:
                    continue
                if cur_operator_price_close > last_operator_price_close:
                    success_count += 1
                else:
                    failed_count += 1
                
            last_operator = operate
            last_operator_price_close = cur_operator_price_close



    df.to_csv('./output/macd/' + code + '.csv')
    return (success_count,failed_count)
    
    
def checkAll():
    all_stock = pd.read_csv('vol_mean.csv')
    all_stock['macd_success'] = pd.Series()
    all_stock['macd_fail'] = pd.Series()
    for index,row in all_stock.iterrows():
        code = row['code']
        name = row['name']
        code_str = str(code).zfill(6)
#        print code_str, '=', name
        success_count,failed_count = check_stock(code_str, name)
        all_stock.loc[index, 'macd_success'] = success_count
        all_stock.loc[index, 'macd_fail'] = failed_count
        if (success_count > failed_count) and (success_count > 5) and (failed_count == 0):
            print code_str, name, '  success_count=', success_count,'  failed_count=', failed_count

    all_stock.to_csv('./output/macd/summy.csv')

def check_stock_now(code, name):
    operate = 0
        
    
    df = ts.get_hist_data(code, start=begin_time)
    df = df.sort_index(0)
    dflen = df.shape[0]
    if dflen>35:
        df['macd_DIFF_DEA'] = pd.Series()
        df['macd_DEA_K'] = pd.Series()
        df['macd_MACD_SELF'] = pd.Series()
        df['macd_SUM'] = pd.Series()
        curdf = pd.DataFrame(df[:dflen])
        macd, macdsignal, macdhist = ta.MACD(np.array(curdf['close']), fastperiod=12, slowperiod=26, signalperiod=9)

        SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
        SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
        SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
        
        #在后面增加3列，分别是13-15列，对应的是 DIFF  DEA  DIFF-DEA       
        curdf['macd']=pd.Series(macd,index=curdf.index) #DIFF
        curdf['macdsignal']=pd.Series(macdsignal,index=curdf.index)#DEA
        curdf['macdhist']=pd.Series(macdhist,index=curdf.index)#DIFF-DEA
        MAlen = len(SignalMA5)
        
        #2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
        #待修改
        if curdf.iat[(dflen-1),13]>0:
            if curdf.iat[(dflen-1),14]>0:
                if curdf.iat[(dflen-1),13]>curdf.iat[(dflen-1),14] and curdf.iat[(dflen-2),13]<=curdf.iat[(dflen-2),14]:
                    operate = operate + 10#买入
                    df['macd_DIFF_DEA'][dflen - 1] = 1
        else:
            if curdf.iat[(dflen-1),14]<0:
                if curdf.iat[(dflen-1),13] == curdf.iat[(dflen-2),14]:
                    operate = operate - 10#卖出
                    df['macd_DIFF_DEA'][dflen - 1] = -1
        
        #3.DEA线与K线发生背离，行情反转信号。
        if curdf.iat[(dflen-1),7]>=curdf.iat[(dflen-1),8] and curdf.iat[(dflen-1),8]>=curdf.iat[(dflen-1),9]:#K线上涨
            if SignalMA5[MAlen-1]<=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]<=SignalMA20[MAlen-1]: #DEA下降
                operate = operate - 1
                df['macd_DEA_K'][dflen - 1] = 1
        elif curdf.iat[(dflen-1),7]<=curdf.iat[(dflen-1),8] and curdf.iat[(dflen-1),8]<=curdf.iat[(dflen-1),9]:#K线下降
            if SignalMA5[MAlen-1]>=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]>=SignalMA20[MAlen-1]: #DEA上涨
                operate = operate + 1
                df['macd_DEA_K'][dflen - 1] = -1
                   
           
        #4.分析MACD柱状线，由负变正，买入信号。
        if curdf.iat[(dflen-1),15]>0 and dflen >30 :
            for i in range(1,26):
                if curdf.iat[(dflen-1-i),15]<=0:#
                    operate = operate + 5
                    df['macd_MACD_SELF'][dflen - 1] = 1
                    break
                #由正变负，卖出信号   
        if curdf.iat[(dflen-1),15]<0 and dflen >30 :
            for i in range(1,26):
                if curdf.iat[(dflen-1-i),15]>=0:#
                    operate = operate - 5
                    df['macd_MACD_SELF'][dflen - 1] = -1
                    break
                
        df['macd_SUM'][dflen - 1] = operate

    return operate

def checknow():
    all_stock = pd.read_csv('vol_mean.csv')
    for index,row in all_stock.iterrows():
        code = row['code']
        name = row['name']
        code_str = str(code).zfill(6)
#        print code_str, '=', name
        operate = check_stock_now(code_str, name)
        all_stock.loc[index, 'operate'] = operate
        if operate > 0:
            success_count,failed_count = check_stock(code_str, name)
            all_stock.loc[index, 'macd_success'] = success_count
            all_stock.loc[index, 'macd_fail'] = failed_count
            print code_str, name, '  operate=', operate,
            print '  success_count=', success_count,'  failed_count=', failed_count
            
    macddata = all_stock[all_stock.operate > 0].sort_values('macd_success', 0, False)
    macddata.to_csv('./output/macd/day/' + datetime.date.today().strftime('%Y-%m-%d') + '.csv')

if __name__ == '__main__':    
    checknow()
#    check_stock('000718', 'dd')
    print 'finish'
