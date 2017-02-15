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
#    asc_days_more = yearmonthdf[yearmonthdf.asc_days > yearmonthdf.desc_days]
    results = yearmonthdf.groupby(by='month').agg({
                                                'asc_days_more':lambda g: g[g > 0].count(),
                                                'desc_days_more':lambda g: g[g > 0].count(),
                                                })
    return results

def checkStock(code_str):
    month_file_path = MONTH_DIR + code_str + '.csv'
    if os.path.exists(month_file_path):
        return

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

def checkStockInThread((index,row)):
    code = row['code']
    name = row['name']
    code_str = str(code).zfill(6)

#    print code_str
    checkStock(code_str)

def checkAll():
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
    
    print 'finish'

