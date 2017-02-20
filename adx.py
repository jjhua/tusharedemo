# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 17:40:49 2017

@author: megahertz
"""

import talib as ta
import base
import numpy as np
import pandas as pd
import os

adx_timeperiod = 13

ADX_DIR = base.OUTPUT_DIR + 'adx' + str(adx_timeperiod) + '/'

def checkOne(code_str):
    df = base.getOneStockData(code_str)
    df['MINUS_DM_' + str(adx_timeperiod)] = ta.MINUS_DM(np.array(df['high']), np.array(df['low']), timeperiod=adx_timeperiod)
    df['PLUS_DM_' + str(adx_timeperiod)] = ta.PLUS_DM(np.array(df['high']), np.array(df['low']), timeperiod=adx_timeperiod)
    df['TR_' + str(adx_timeperiod)] = ta.TRANGE(np.array(df['high']), np.array(df['low']), np.array(df['close']))
    df['MINUS_DI_' + str(adx_timeperiod)] = ta.MINUS_DI(np.array(df['high']), np.array(df['low']), np.array(df['close']), timeperiod=adx_timeperiod)
    df['PLUS_DI_' + str(adx_timeperiod)] = ta.PLUS_DI(np.array(df['high']), np.array(df['low']), np.array(df['close']), timeperiod=adx_timeperiod)
    df['ADX_' + str(adx_timeperiod)] = ta.ADX(np.array(df['high']), np.array(df['low']), np.array(df['close']), timeperiod=adx_timeperiod)
    df['ADXR_' + str(adx_timeperiod)] = ta.ADXR(np.array(df['high']), np.array(df['low']), np.array(df['close']), timeperiod=adx_timeperiod)


    df.to_csv(ADX_DIR + code_str + '.csv')

if __name__ == '__main__':
    if not os.path.exists(ADX_DIR):
        os.makedirs(ADX_DIR)
    checkOne('000002')

