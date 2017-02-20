# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 15:18:29 2017

@author: megahertz
"""

import os
from multiprocessing import Pool
from base import *
from algrothm import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


MONTH_DIR = base.OUTPUT_DIR + 'month/'
YEAR_MONTH_DIR = base.OUTPUT_DIR + 'year_month/'

THREAD_POOL_SIZE = 6

def calcStockByMonth(code, yearmonthdf):
    if (yearmonthdf is None):
        return None
    results = None
    yearmonthdf['asc_days_more'] = yearmonthdf['asc_days'] - yearmonthdf['desc_days']
    yearmonthdf['desc_days_more'] = yearmonthdf['desc_days'] - yearmonthdf['asc_days']
    yearmonthdf['asc_price_more'] = yearmonthdf['close_last'] - yearmonthdf['close_first']
    yearmonthdf['desc_price_more'] = yearmonthdf['close_first'] - yearmonthdf['close_last']
#    asc_days_more = yearmonthdf[yearmonthdf.asc_days > yearmonthdf.desc_days]
    results = yearmonthdf.groupby(by='month').agg({
                                                'asc_days_more':lambda g: g[g > 0].count(),
                                                'desc_days_more':lambda g: g[g > 0].count(),
                                                'asc_price_more':lambda g: g[g > 0].count(),
                                                'desc_price_more':lambda g: g[g > 0].count(),
                                                })
    return results

def checkStock(code_str):
    month_file_path = MONTH_DIR + code_str + '.csv'
#    if os.path.exists(month_file_path):
#        return

    file_path = YEAR_MONTH_DIR + code_str + '.csv'
    if os.path.exists(file_path):
        results = pd.read_csv(file_path)
    else:
        results = checkByYearMonth(code_str)
        if results is not None:
            results.to_csv(file_path)

    results = calcStockByMonth(code_str, results)
    if results is not None:
        results.to_csv(month_file_path)

def makeSummy():
    all_stock = getAllStock()
    for (index,row) in all_stock.iterrows():
        code = row['code']
#        name = row['name']
        code_str = str(code).zfill(6)

#        print code_str

        month_file_path = MONTH_DIR + code_str + '.csv'
        if not os.path.exists(month_file_path):
            continue
        month_data = pd.read_csv(month_file_path)
        if month_data is None:
            continue
        if month_data.shape[0] < 12:
            continue
        for index_month,row_month in month_data.iterrows():
            all_stock.loc[index, 'asc_day_m' + str(int(row_month['month']))] = (row_month['asc_days_more'] - row_month['desc_days_more']) * 100 / (row_month['asc_days_more'] + row_month['desc_days_more'])
        for index_month,row_month in month_data.iterrows():
            all_stock.loc[index, 'asc_price_m' + str(int(row_month['month']))] = (row_month['asc_price_more'] - row_month['desc_price_more']) * 100 / (row_month['asc_price_more'] + row_month['desc_price_more'])

    all_stock[all_stock.asc_day_m1.isnull() == False].to_csv(MONTH_DIR + 'summy.csv')


def checkStockInThread((index,row)):
    code = row['code']
    name = row['name']
    code_str = str(code).zfill(6)

#    print code_str
    checkStock(code_str)

def checkAll():
    if not os.path.exists(MONTH_DIR):
        os.makedirs(MONTH_DIR)
    if not os.path.exists(YEAR_MONTH_DIR):
        os.makedirs(YEAR_MONTH_DIR)
    all_stock = getAllStock()
    pool = Pool(THREAD_POOL_SIZE)
    pool.map(checkStockInThread, all_stock.iterrows())
    pool.close()
    pool.join()


if __name__ == '__main__':
#    os.makedirs(MONTH_DIR)
#    os.makedirs(YEAR_MONTH_DIR)

#    checkStock('000001')
    checkAll()
    makeSummy()
    
    print 'finish'

