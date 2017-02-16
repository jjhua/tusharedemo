# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 12:38:50 2017

@author: megahertz
"""

import base
from base import *
import datetime
import talib as ta
import numpy as np
import pandas as pd
import os
from multiprocessing import Pool



MACD_FASTPERIOD=12
MACD_SLOWPERIOD=26
MACD_SIGNALPERIOD=9

MA_FAST = 5
MA_MIDDLE = 10
MA_SLOW = 20

def _calcAscDays(g):
    days = 0
    last = 0
    for _,cur in g.iteritems():
        if last != 0:
            if cur > last:
                days += 1
        last = cur
    return days

def _calcDescDays(g):
    days = 0
    last = 0
    for _,cur in g.iteritems():
        if last != 0:
            if cur < last:
                days += 1
        last = cur
    return days

def checkByYearMonth(code):
    results = pd.DataFrame()
    
    df = base.getOneStockData(code)

    print df
    if df.empty:
        return None

    for index,item in df.iterrows():
#        print item
        date_str = item['date']
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        year_month = date.strftime('%Y-%m')
        month = date.strftime('%m')
        df.loc[index, 'year_month'] = year_month
        df.loc[index, 'month'] = month

    df['close_avg'] = df['close']
    df['close_min'] = df['close']
    df['close_max'] = df['close']
    df['close_first'] = df['close']
    df['close_last'] = df['close']
    df['close_last'] = df['close']
    df['asc_days'] = df['close']
    df['desc_days'] = df['close']

    group_month = df.groupby('year_month')
    results = group_month.agg({'close_avg':lambda g: np.average(g),
                               'close_min':lambda g: np.min(g),
                               'close_max':lambda g: np.max(g),
                               'close_first':lambda g: g[g.first_valid_index()],
                               'close_last':lambda g: g[g.last_valid_index()],
                               'month':lambda g: g[g.first_valid_index()],
                               'asc_days': _calcAscDays,
                               'desc_days': _calcDescDays,
                               })

    return results


def calcMACD(code):
    success_count = 0
    failed_count = 0

    output_path = OUTPUT_DIR + 'macd2/' + code + '.csv'

    df = base.getOneStockData(code)

    if df.empty:
        return (success_count,failed_count)

    dflen = df.shape[0]
    if dflen<35:
        return (success_count,failed_count)

    last_operator_price_close = 0
    last_operator = 0
    df['macd_DIFF_DEA'] = pd.Series()
    df['macd_DEA_K'] = pd.Series()
    df['macd_MACD_SELF'] = pd.Series()
    df['macd_SUM'] = pd.Series()
    df['macd_result'] = pd.Series()

    macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=MACD_FASTPERIOD, slowperiod=MACD_SLOWPERIOD, signalperiod=MACD_SIGNALPERIOD)

    MA5_index = df.shape[1]
    df['MA5']=pd.Series(ta.MA(np.array(df['close']), timeperiod=MA_FAST, matype=0),index=df.index)
    MA10_index = df.shape[1]
    df['MA10']=pd.Series(ta.MA(np.array(df['close']), timeperiod=MA_MIDDLE, matype=0),index=df.index)
    MA20_index = df.shape[1]
    df['MA20']=pd.Series(ta.MA(np.array(df['close']), timeperiod=MA_SLOW, matype=0),index=df.index)

    macd_index = df.shape[1]
    df['macd']=pd.Series(macd,index=df.index) #DIFF
    macdsignal_index = df.shape[1]
    df['macdsignal']=pd.Series(macdsignal,index=df.index)#DEA
    macdhist_index = df.shape[1]
    df['macdhist']=pd.Series(macdhist,index=df.index)#DIFF-DEA

    SignalMA5 = ta.MA(macdsignal, timeperiod=MA_FAST, matype=0)
    SignalMA10 = ta.MA(macdsignal, timeperiod=MA_MIDDLE, matype=0)
    SignalMA20 = ta.MA(macdsignal, timeperiod=MA_SLOW, matype=0)

    for dflen in range(36, df.shape[0] + 1):
        curdf = pd.DataFrame(df[:dflen])
        operate = 0

        #在后面增加3列，对应的是 DIFF  DEA  DIFF-DEA       
        MAlen = dflen
        #2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
        #待修改
        if curdf.iat[(dflen-1),macd_index]>0:
            if curdf.iat[(dflen-1),macdsignal_index]>0:
                if curdf.iat[(dflen-1),macd_index]>curdf.iat[(dflen-1),macdsignal_index] and curdf.iat[(dflen-2),macd_index]<=curdf.iat[(dflen-2),macdsignal_index]:
#                        operate = operate + 10#买入
                    df.loc['macd_DIFF_DEA', dflen - 1] = 1
        else:
            if curdf.iat[(dflen-1),macdsignal_index]<0:
                if curdf.iat[(dflen-1),macd_index] == curdf.iat[(dflen-2),macdsignal_index]:
#                        operate = operate - 10#卖出
                    df.loc['macd_DIFF_DEA', dflen - 1] = -1

        #3.DEA线与K线发生背离，行情反转信号。
        if curdf.iat[(dflen-1),MA5_index]>=curdf.iat[(dflen-1),MA10_index] and curdf.iat[(dflen-1),MA10_index]>=curdf.iat[(dflen-1),MA20_index]:#K线上涨
            if SignalMA5[MAlen-1]<=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]<=SignalMA20[MAlen-1]: #DEA下降
                operate = operate - 1
                df.loc['macd_DEA_K', dflen - 1] = 1
        elif curdf.iat[(dflen-1),MA5_index]<=curdf.iat[(dflen-1),MA10_index] and curdf.iat[(dflen-1),MA10_index]<=curdf.iat[(dflen-1),MA20_index]:#K线下降
            if SignalMA5[MAlen-1]>=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]>=SignalMA20[MAlen-1]: #DEA上涨
                operate = operate + 1
                df.loc['macd_DEA_K', dflen - 1] = -1

        #4.分析MACD柱状线，由负变正，买入信号。
        if curdf.iat[(dflen-1),macdhist_index]>0 and dflen >30 :
            for i in range(1,26):
                if curdf.iat[(dflen-1-i),macdhist_index]<=0:#
#                        operate = operate + 5
                    df.loc['macd_MACD_SELF', dflen - 1] = 1
                    break
                #由正变负，卖出信号   
        if curdf.iat[(dflen-1),macdhist_index]<0 and dflen >30 :
            for i in range(1,26):
                if curdf.iat[(dflen-1-i),macdhist_index]>=0:#
#                        operate = operate - 5
                    df.loc['macd_MACD_SELF', dflen - 1] = -1
                    break

        if operate != 0:
            df.loc['macd_SUM', dflen - 1] = operate

        if operate == 0:
            continue
        cur_operator_price_close = curdf['close'][dflen - 1]
        if last_operator * operate > 0:
            continue
#            print code, name, 'operate=', operate, '  last_operator=', last_operator,
#            print '   cur_operator_price_close=', cur_operator_price_close,
#            print '   last_operator_price_close=', last_operator_price_close
        if operate > 0:
#                print 'operate=买入 price=',cur_operator_price_close
            pass
        else:
#                print 'operate=卖出 ',
#                print '   success=', (cur_operator_price_close > last_operator_price_close)
#                print '   curprice=',cur_operator_price_close,
#                print '   last_operator_price_close=', last_operator_price_close
            if last_operator_price_close != 0:
                if cur_operator_price_close > last_operator_price_close:
                    success_count += 1
                    df.loc['macd_result', dflen - 1] = 1
                else:
                    failed_count += 1
                    df.loc['macd_result', dflen - 1] = -1

        last_operator = operate
        last_operator_price_close = cur_operator_price_close


    df.to_csv(output_path)
    return (success_count,failed_count)

if __name__ == '__main__':

#    results = checkByYearMonth('300615')

#    print results

#    checkAll()

    calcMACD('603131')

    print 'finish'
