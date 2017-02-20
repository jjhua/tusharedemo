# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 12:34:11 2017

@author: megahertz
"""

import pandas as pd
import traceback
import sys

OUTPUT_DIR = './output/'
STOCK_DATA_DIR = OUTPUT_DIR + 'kdata/'

def getOneStockData(code):
    df = pd.read_csv(STOCK_DATA_DIR + code + '.csv', index_col=0)
    return df


def getAllStock():    
    all_stock = pd.read_csv('all.csv', index_col=0)
    return all_stock

def getVolumePricePath(code):
    return OUTPUT_DIR + 'volume/' + code + '.csv'

def getMacdPath(code):
    return OUTPUT_DIR + 'macd_6_26_8_3_6_20/' + code + '.csv'


def logException():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print "*** print sys.exc_info:"
    print 'exc_type is: %s, exc_value is: %s, exc_traceback is: %s' % (exc_type, exc_value, exc_traceback)
    print "-" *  100

    print "*** print_tb:"
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print "-" *  100

    print "*** print_exception:"
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    print "-" *  100

    print "*** print_exc:"
    traceback.print_exc()
    print "-" *  100

    print "*** format_exc, first and last line:"
    formatted_lines = traceback.format_exc().splitlines()
    print formatted_lines[0]
    print formatted_lines[-1]
    print "-" *  100

    print "*** format_exception:"
    print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print "-" *  100

    print "*** extract_tb:"
    print repr(traceback.extract_tb(exc_traceback))
    print "-" *  100

    print "*** extract_stack:"
    print traceback.extract_stack()
    print "-" *  100

    print "*** format_tb:"
    print repr(traceback.format_tb(exc_traceback))
    print "-" *  100

    print "*** tb_lineno:", exc_traceback.tb_lineno

    print traceback.format_list([('spam.py', 3, '<module>', 'spam.eggs()'), ('eggs.py', 42, 'eggs', 'return "bacon"')])
