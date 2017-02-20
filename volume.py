# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 14:30:40 2017

@author: megahertz
"""

import sys
from multiprocessing import Pool
from algrothm import calcVolumePrice


from base import getAllStock, logException


reload(sys)
sys.setdefaultencoding('utf-8')


THREAD_POOL_SIZE = 6

def checkStockInThread((index,row)):
    success_count = 0
    failed_count = 0

    code = index
    name = row['name']
    code_str = str(code).zfill(6)
    print code_str, '=', name.encode('gbk')
    try:
        success_count,failed_count = calcVolumePrice(code_str)
    except Exception, e:
        print code_str, '=', name.encode('gbk'),
        print e
        logException()

    return (index,code_str,name,success_count,failed_count)

def checkAll():
    all_stock = getAllStock()

    pool = Pool(THREAD_POOL_SIZE)
    results = pool.map(checkStockInThread, all_stock.iterrows())
    pool.close()
    pool.join()

    for index,code_str,name,success_count,failed_count in results:
#        print index, success_count, failed_count
        all_stock.loc[index, 'volume_success'] = success_count
        all_stock.loc[index, 'volume_fail'] = failed_count
        if (success_count > 3) and (failed_count == 0):
            print code_str, name.encode('gbk'), '  success_count=', success_count,'  failed_count=', failed_count

        
    all_stock.to_csv('./output/volume/summy.csv')


if __name__ == '__main__':    
    checkAll()
    print 'finish'
