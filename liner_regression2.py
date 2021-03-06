# -*- coding: utf-8 -*-
"""
Created on Sat May 06 18:35:03 2017

@author: megahertz
"""

#from sklearn import linear_model
#
#from sklearn.linear_model import LinearRegression
#X = [[6, 2], [8, 1], [10, 0], [14, 2], [18, 0]]
#y = [[7], [9], [13], [17.5], [18]]
#model = LinearRegression()
#model.fit(X, y)
#X_test = [[8, 2], [9, 0], [11, 2], [16, 2], [12, 0]]
#y_test = [[11], [8.5], [15], [18], [11]]
#predictions = model.predict(X_test)
#for i, prediction in enumerate(predictions):
#    print('Predicted: %s, Target: %s' % (prediction, y_test[i]))
#print('R-squared: %.2f' % model.score(X_test, y_test))
#

import base

import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

df_all = base.getOneStockData('000002')
columns = []
for i in range(1, 5):
    column = 'close(t-' + str(i) + ')'
    df_all[column] = df_all.close.shift(i)
    columns.append(column)
df_all = df_all.dropna(subset=columns)

#df_all = df_all[df_all.close_diff < 11]
#df_all = df_all[df_all.close_diff > -11]
#df_all = df_all[abs(df_all.volume_diff) > 1]
dfx = df_all[columns]
dfy = df_all[['close']]
#X_train = [[6], [8], [10], [14], [18]]
#y_train = [[7], [9], [13], [17.5], [18]]
#X_test = [[6], [8], [11], [16]]
#y_test = [[8], [12], [15], [18]]
print df_all.shape
count = dfx.shape[0] / 2
X_train = dfx[:count].values
y_train = dfy[:count].values
X_test = dfx[count:count+count].values
y_test = dfy[count:count+count].values

#print X_train
#print y_train

def runplt():
#    x_max = max(X_test.max()[0], X_test.max()[0])
#    y_max = max(y_test.max()[0], y_train.max()[0])
#    x_min = min(X_test.min()[0], X_test.min()[0])
#    y_min = min(y_test.min()[0], y_train.min()[0])

    plt.figure()
    plt.title(u'diameter-cost curver')
#    plt.xlabel(u'diameter')
    plt.ylabel(u'cost')
#    plt.axis([x_min, x_max, y_min, y_max])
    plt.grid(True)
    return plt
    



runplt()
plt.plot(y_test, 'k-')

## 建立线性回归，并用训练的模型绘图
regressor = LinearRegression()
regressor.fit(X_train, y_train)
yy = regressor.predict(X_test)
#df_all['LR1'] = pd.Series()
#df_all['LR1'][count+1:count+count+1] = yy
plt.plot(yy, 'y-')

quadratic_featurizer = PolynomialFeatures(degree=2)
X_train_quadratic = quadratic_featurizer.fit_transform(X_train)
X_test_quadratic = quadratic_featurizer.transform(X_test)
regressor_quadratic = LinearRegression()
regressor_quadratic.fit(X_train_quadratic, y_train)
xx_quadratic = quadratic_featurizer.transform(X_test)
plt.plot(regressor_quadratic.predict(xx_quadratic), 'r-')

cubic_featurizer = PolynomialFeatures(degree=3)
X_train_cubic = cubic_featurizer.fit_transform(X_train)
X_test_cubic = cubic_featurizer.transform(X_test)
regressor_cubic = LinearRegression()
regressor_cubic.fit(X_train_cubic, y_train)
xx_cubic = cubic_featurizer.transform(X_test)
plt.plot(regressor_cubic.predict(xx_cubic), 'g')


seventh_featurizer = PolynomialFeatures(degree=7)
X_train_seventh = seventh_featurizer.fit_transform(X_train)
X_test_seventh = seventh_featurizer.transform(X_test)
regressor_seventh = LinearRegression()
regressor_seventh.fit(X_train_seventh, y_train)
xx_seventh = seventh_featurizer.transform(X_test)
plt.plot(regressor_seventh.predict(xx_seventh), 'b')


#plt.plot(X_test, y_test, 'm+')


#print(X_train_cubic)
#print(X_test_cubic)
#print(X_train_seventh)
#print(X_test_seventh)
print('1 r-liner', regressor.score(X_test, y_test))
print('2 r-squared', regressor_quadratic.score(X_test_quadratic, y_test))
print('3 r-squared', regressor_cubic.score(X_test_cubic, y_test))
print('7 r-squared', regressor_seventh.score(X_test_seventh, y_test))
#
#
plt.show()
