# -*- coding: utf-8 -*-
"""
Created on Sat May 06 18:35:03 2017

@author: megahertz
"""

import base
import datetime

from math import sqrt
import matplotlib.pyplot as plt
from matplotlib import pyplot
from multiprocessing import Pool
import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from sklearn.externals import joblib

import os


THREAD_POOL_SIZE = 6

OLD_DAYS = 30
FUTURE_DAYS = 10
TEST_DAYS = 10

DATA_Y_LEN = 1

#learn_model = LogisticRegression(C=1000.0, random_state=0)
#learn_model = SVC(kernel='linear', C=1.0, random_state=0)
learn_model = SVC(kernel='rbf', C=1.0, random_state=0, gamma=0.8)
#learn_model = KNeighborsClassifier(n_neighbors=3, p=2, metric='minkowski')

MODEL_NAME = 'svc_rbf_gamma_0.8'
MODELS_DIR = './output/sklearn/models/' + MODEL_NAME + '/'

# convert time series into supervised learning problem
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg

def calcOperate(row):
    if (row.high_future > row.close * 1.1):
        return 1
    if (row.high_future < row.close):
        return -1
    return 0

def prepareData(code):
    df_all = base.getOneStockData(code)
    if df_all.shape[0] < 300:
        raise Exception('data is short.' + str(df_all.shape[0]))
        
    in_columns = ['open','close','high','low','volume']
    indexes = []
    for i in range(OLD_DAYS):
        for in_column in in_columns:
            index = in_column + '__' + str(i)
            indexes.append(index)
            df_all[index] = df_all[in_column].shift(0 - i)
        

    futureIndexes = []
    for i in range(1, FUTURE_DAYS):
        index = 'high_' + str(i)
        futureIndexes.append(index)
        df_all[index] = df_all.high.shift(i)
    index = 'high_future'
    df_all[index] = df_all[futureIndexes].apply(max, 1)
    # indexes.append(index)

    index = 'operate'
    df_all[index] = df_all.apply(calcOperate, 1)
    indexes.append(index)

    # print df_all.head(10)
    df = df_all[indexes].dropna()
    return df


def check_stock(code, name):
    try:
        df = prepareData(code)
    except Exception, e:
        print(code + name)
        print(e)
        return 0
    print(code + name + ' days=' + str(df.shape))


    X = df[df.columns[:0-DATA_Y_LEN]]
    y = df[df.columns[0-DATA_Y_LEN:]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)

#    train = df.head(0-TEST_DAYS)
#    # print train.columns
#    X_train = train[train.columns[:0-DATA_Y_LEN]]
#    y_train = train[train.columns[0-DATA_Y_LEN:]]
#    # print trainX
#    # print trainY
#    test = df.tail(TEST_DAYS)
#    X_test = test[test.columns[:0-DATA_Y_LEN]]
#    y_test = test[test.columns[0-DATA_Y_LEN:]]

#    print y_train.values

    sc = StandardScaler()
    sc.fit(X_train)
    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)
#    X_test_std = sc.transform(X)
#    y_test = y

    learn_model.fit(X_train_std, y_train.operate.values)
    y_pred = learn_model.predict(X_test_std)

#    print('----------LogisticRegression-------------')
#    print('Misclassified samples: %d' % (y_test.operate.values != y_pred).sum())
#    print('Accuracy: %.2f' % accuracy_score(y_test.operate.values, y_pred))

    joblib.dump(learn_model, MODELS_DIR + code + '.m')
    

    return accuracy_score(y_test.operate.values, y_pred)

#def testAlgro():
#    iris = datasets.load_iris()
#    X = iris.data[:,[2,3]]
#    y = iris.target
#    np.unique(y)
#    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
#    print '------X_train--------'
#    print X_train
#    print '------X_test--------'
#    print X_test
#    # print type(X_train), type(X_train[0]), X_train[0], X_train[0][0]
#    # print type(X_test), type(X_test[0][0])
#    sc = StandardScaler()
#    sc.fit(X_train)
#    X_train_std = sc.transform(X_train)
#    X_test_std = sc.transform(X_test)
#    print '------X_train_std--------'
#    print X_train_std
#    print '------X_test_std--------'
#    print X_test_std

def checkStockInThread((index,row)):
    code = index
    name = row['name']
    code_str = str(code).zfill(6)
    score = check_stock(code_str, name)
    
    return (index,score)

def checkAll():
    all_stock = base.getAllStock()
    
    pool = Pool(THREAD_POOL_SIZE)
    results = pool.map(checkStockInThread, all_stock.iterrows())
    pool.close()
    pool.join()

    for index,score in results:
        all_stock.loc[index, 'score'] = score

    newdata = all_stock.sort_values('score', 0, False)
    newdata.to_csv(MODEL_NAME + '_test0.5_' + datetime.date.today().strftime('%Y-%m-%d') + '.csv')

if __name__ == '__main__':
#    check_stock('600318', '新力金融')
    os.makedirs(MODELS_DIR)

    start = datetime.datetime.now()
    checkAll()
    end = datetime.datetime.now()
    print("use time ", end - start)

#    testAlgro()