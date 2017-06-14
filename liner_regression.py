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
from matplotlib import pyplot
import pandas as pd

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from math import sqrt
from sklearn.metrics import mean_squared_error


# convert time series into supervised learning problem
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = pd.DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = pd.concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg


def runplt(X_train, y_train, X_test, y_test):
    x_max = max(X_test.max()[0], X_train.max()[0])
    y_max = max(y_test.max()[0], y_train.max()[0])
    x_min = min(X_test.min()[0], X_train.min()[0])
    y_min = min(y_test.min()[0], y_train.min()[0])

    plt.figure()
    plt.title(u'diameter-cost curver')
    plt.xlabel(u'diameter')
    plt.ylabel(u'cost')
    plt.axis([x_min, x_max, y_min, y_max])
    plt.grid(True)
    return plt

def test():
    df_all = base.getOneStockData('000002')
    df_all['volume_diff'] = df_all.volume.pct_change()
    for index,row in df_all[df_all.volume_diff < 0].iterrows():
        df_all.loc[index,'volume_diff'] = row['volume_diff'] / (1+row['volume_diff'])
    df_all['close_diff'] = df_all.close.pct_change() * 100
    df_all = df_all.dropna(subset=['volume_diff','close_diff'])
    df_all = df_all[df_all.close_diff < 11]
    df_all = df_all[df_all.close_diff > -11]
    df_all = df_all[abs(df_all.volume_diff) > 1]
    dfx = df_all[['volume_diff']]
    dfy = df_all[['close_diff']]
    #X_train = [[6], [8], [10], [14], [18]]
    #y_train = [[7], [9], [13], [17.5], [18]]
    #X_test = [[6], [8], [11], [16]]
    #y_test = [[8], [12], [15], [18]]
    print df_all.shape
    count = dfx.shape[0] / 2 - 3
    X_train = dfx[:count]
    y_train = dfy[1:count+1]
    X_test = dfx[count:count+count]
    y_test = dfy[count+1:count+count+1]

    runplt(X_train, y_train, X_test, y_test)
    plt.plot(X_train, y_train, 'k.')
    
    # 建立线性回归，并用训练的模型绘图
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    yy = regressor.predict(X_test)
    #df_all['LR1'] = pd.Series()
    #df_all['LR1'][count+1:count+count+1] = yy
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
    print('1 r-liner', regressor.score(X_test, y_test))
    print('2 r-squared', regressor_quadratic.score(X_test_quadratic, y_test))
    print('3 r-squared', regressor_cubic.score(X_test_cubic, y_test))
    print('7 r-squared', regressor_seventh.score(X_test_seventh, y_test))
    #
    #

# transform series into train and test sets for supervised learning
def prepare_data(series, n_test, n_lag, n_seq):
    # extract raw values
    raw_values = series.values
#    print 'raw_values=', raw_values
#    raw_values = raw_values.reshape(len(raw_values), 2)
#    print 'raw_values reshape=', raw_values
    # transform into supervised learning problem X, y
    supervised = series_to_supervised(raw_values, n_lag, n_seq)
    supervised_values = supervised.values
    # split into train and test sets
    train, test = supervised_values[0:-n_test], supervised_values[-n_test:]
    return train, test

# make a persistence forecast
def persistence(last_ob, n_seq):
	return [last_ob for i in range(n_seq)]

# evaluate the persistence model
def make_forecasts(train, test, n_lag, n_seq):
	forecasts = list()
	for i in range(len(test)):
		X, y = test[i, 0:n_lag], test[i, n_lag:]
		# make forecast
		forecast = persistence(X[-1], n_seq)
		# store the forecast
		forecasts.append(forecast)
	return forecasts

# evaluate the RMSE for each forecast time step
def evaluate_forecasts(test, forecasts, n_lag, n_seq):
	for i in range(n_seq):
		actual = test[:,(n_lag+i)]
		predicted = [forecast[i] for forecast in forecasts]
		rmse = sqrt(mean_squared_error(actual, predicted))
		print('t+%d RMSE: %f' % ((i+1), rmse))

# plot the forecasts in the context of the original dataset
def plot_forecasts(series, forecasts, n_test):
	# plot the entire dataset in blue
	pyplot.plot(series.values)
	# plot the forecasts in red
	for i in range(len(forecasts)):
		off_s = len(series) - n_test + i - 1
		off_e = off_s + len(forecasts[i]) + 1
		xaxis = [x for x in range(off_s, off_e)]
		yaxis = [series.values[off_s]] + forecasts[i]
		pyplot.plot(xaxis, yaxis, color='red')
	# show the plot
	pyplot.show()


def test2():
    df_all = base.getOneStockData('000002')
    n_lag = 3
    n_seq = 1
    n_test = 1000
    series = df_all[['close']]
#    out = series_to_supervised(df_all[['close','volume']], 3, 1, True)
#    print out
    train, test = prepare_data(series, n_test, n_lag, n_seq)
#    print(test)
    print('Train: %s, Test: %s' % (train.shape, test.shape))
    # make forecasts
    forecasts = make_forecasts(train, test, n_lag, n_seq)
    # evaluate forecasts
    evaluate_forecasts(test, forecasts, n_lag, n_seq)
    # plot forecasts
    plot_forecasts(series, forecasts, n_test+2)

if __name__ == '__main__':
    test()
#    test2()
