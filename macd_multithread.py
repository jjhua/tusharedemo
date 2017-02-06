# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:21:26 2017

@author: megahertz
"""

from multiprocessing import Pool
import time
import random

def getMacd(i):
    print i
    time.sleep(random.randint(0,1))
    return (i, i * 10)

pool = Pool(6)

nums = range(0, 100)
results = pool.map(getMacd, nums)
pool.close()
pool.join()
print results
