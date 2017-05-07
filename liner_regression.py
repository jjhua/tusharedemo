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


import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

df_all = base.getOneStockData('000001')
df = df_all[['close']]
#X_train = [[6], [8], [10], [14], [18]]
#y_train = [[7], [9], [13], [17.5], [18]]
#X_test = [[6], [8], [11], [16]]
#y_test = [[8], [12], [15], [18]]
#print df.shape
count = df.shape[0] / 2 - 3
X_train = df[:count]
y_train = df[1:count+1]
X_test = df[count:count+count]
y_test = df[count+1:count+count+1]

def runplt():
    x_max = max(X_test.max()[0], X_test.max()[0])
    y_max = max(y_test.max()[0], y_train.max()[0])

    plt.figure()
    plt.title(u'diameter-cost curver')
    plt.xlabel(u'diameter')
    plt.ylabel(u'cost')
    plt.axis([0, x_max.max(), 0, y_max.max()])
    plt.grid(True)
    return plt
    


runplt()
plt.plot(X_train, y_train, 'k.')

# 建立线性回归，并用训练的模型绘图
regressor = LinearRegression()
regressor.fit(X_train, y_train)
yy = regressor.predict(y_train)
plt.plot(y_train, yy, 'y-')

quadratic_featurizer = PolynomialFeatures(degree=2)
X_train_quadratic = quadratic_featurizer.fit_transform(X_train)
X_test_quadratic = quadratic_featurizer.transform(X_test)
regressor_quadratic = LinearRegression()
regressor_quadratic.fit(X_train_quadratic, y_train)
xx_quadratic = quadratic_featurizer.transform(X_test)
plt.plot(X_test, regressor_quadratic.predict(xx_quadratic), 'r-')

cubic_featurizer = PolynomialFeatures(degree=3)
X_train_cubic = cubic_featurizer.fit_transform(X_train)
X_test_cubic = cubic_featurizer.transform(X_test)
regressor_cubic = LinearRegression()
regressor_cubic.fit(X_train_cubic, y_train)
xx_cubic = cubic_featurizer.transform(X_test)
plt.plot(X_test, regressor_cubic.predict(xx_cubic), 'g')


seventh_featurizer = PolynomialFeatures(degree=7)
X_train_seventh = seventh_featurizer.fit_transform(X_train)
X_test_seventh = seventh_featurizer.transform(X_test)
regressor_seventh = LinearRegression()
regressor_seventh.fit(X_train_seventh, y_train)
xx_seventh = seventh_featurizer.transform(X_test)
plt.plot(X_test, regressor_seventh.predict(xx_seventh), 'b')


plt.plot(X_test, y_test, 'm+')


plt.show()
#print(X_train_cubic)
#print(X_test_cubic)
#print(X_train_seventh)
#print(X_test_seventh)
print('2 r-squared', regressor_quadratic.score(X_test_quadratic, y_test))
print('3 r-squared', regressor_cubic.score(X_test_cubic, y_test))
print('7 r-squared', regressor_seventh.score(X_test_seventh, y_test))
#
#
