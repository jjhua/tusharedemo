# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 12:34:11 2017

@author: megahertz
"""

import pandas as pd

OUTPUT_DIR = './output/'
STOCK_DATA_DIR = OUTPUT_DIR + 'kdata/'

def getOneStockData(code):
    df = pd.read_csv(STOCK_DATA_DIR + code + '.csv')
    return df


def getAllStock():    
    all_stock = pd.read_csv('all.csv')
    return all_stock

