# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tushare as ts

all_stock = ts.get_stock_basics()
all_stock.to_csv('all.csv')