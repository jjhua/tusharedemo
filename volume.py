# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 14:30:40 2017

@author: megahertz
"""

import sys
from multiprocessing import Pool
from algrothm import markVolumePrice


from base import getAllStock, logException


reload(sys)
sys.setdefaultencoding('utf-8')


THREAD_POOL_SIZE = 6

def checkStockInThread((index,row)):
    code = row['code']
    name = row['name']
    code_str = str(code).zfill(6)
    print code_str, '=', name.encode('gbk')
    try:
        markVolumePrice(code_str)
    except Exception, e:
        print code_str, '=', name.encode('gbk'),
        print e
        logException()


def checkAll():
    all_stock = getAllStock()

    pool = Pool(THREAD_POOL_SIZE)
    results = pool.map(checkStockInThread, all_stock.iterrows())
    pool.close()
    pool.join()

        
    all_stock.to_csv('./output/macd2/summy_DEA_K.csv')


if __name__ == '__main__':    
    checkAll()
    print 'finish'
