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

MACD_FASTPERIOD=12
MACD_SLOWPERIOD=26
MACD_SIGNALPERIOD=9

MA_FAST = 5
MA_MIDDLE = 10
MA_SLOW = 20

class UnicodeStreamFilter:  
    def __init__(self, target):  
        self.target = target  
        self.encoding = 'utf-8'  
        self.errors = 'replace'  
        self.encode_to = self.target.encoding  
    def write(self, s):  
        if type(s) == str:  
            s = s.decode("utf-8")  
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)  
        self.target.write(s)

if sys.stdout.encoding == 'cp936':  
    sys.stdout = UnicodeStreamFilter(sys.stdout)


def getOneStockData(code):
    df = pd.read_csv(STOCK_DATA_DIR + code + '.csv', index_col=0, infer_datetime_format=True, parse_dates=[1])
    return df


def getAllStock():    
    all_stock = pd.read_csv('all.csv', index_col=0)
    return all_stock

def getVolumePricePath(code):
    return OUTPUT_DIR + 'volume/' + code + '.csv'

def getMacdDir():
    return OUTPUT_DIR + 'macd_' + str(MACD_FASTPERIOD) + '_' + str(MACD_SLOWPERIOD) + '_' + str(MACD_SIGNALPERIOD) + '_' + str(MA_FAST) + '_' + str(MA_MIDDLE) + '_' + str(MA_SLOW) + '/'

def getMacdPath(code):
    return getMacdDir() + code + '.csv'


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
