# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 21:01:21 2017

@author: megahertz

http://mp.weixin.qq.com/s?__biz=MzAwOTgzMDk5Ng==&mid=2650833972&idx=1&sn=4de9f9ee81bc8bf85d1e0a4a8f79b0de&chksm=80adb30fb7da3a19817c72ff6f715ee91d6e342eb0402e860e171993bb0293bc4097e2dc4fe9&mpshare=1&scene=1&srcid=1106BPAdPiPCnj6m2Xyt5p2M#wechat_redirect


"""

import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy import types
from multiprocessing import Pool
import pandas as pd


df_type_dic = {
'date':types.VARCHAR(20)
}

THREAD_POOL_SIZE = 33




def syncStock(code):
    for i in range(0, 10):
        df = ts.get_k_data(code, start='1980-01-01')
        if df is not None:
            break
        print 'retry ', i, code
    if df is None:
        return
#    print df
    df.to_csv('./output/kdata/' + code + '.csv')
    engine = create_engine('mysql://root:root@127.0.0.1/tushare?charset=utf8')
    df.to_sql(code,engine,if_exists='append',dtype=df_type_dic)

def syncStockInThread((index,row)):
    code = row['code']
    name = row['name']
    code_str = str(code).zfill(6)
    
    print code_str, '=', name
    syncStock(code_str)
    

if __name__ == '__main__':    
    all_stock = pd.read_csv('all.csv')
    
    pool = Pool(THREAD_POOL_SIZE)
    results = pool.map(syncStockInThread, all_stock.iterrows())
    pool.close()
    pool.join()



