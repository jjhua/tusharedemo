# -*- coding: utf-8 -*-
"""
http://blog.sina.com.cn/s/blog_620987bf0102vlmz.html
"""

import tushare as ts
import talib as ta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os,time,sys,re,datetime
import csv
import scipy
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
#import urllib2
 
#首先是获取沪深两市的股票列表
#这里得到是对应的dataframe数据结构，它是类似于excel中一片数据的数据结构，有这些列：code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产 fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期
def Get_Stock_List():
    df = ts.get_stock_basics()
    return df
 
 #修改了的函数，按照多个指标进行分析
#按照MACD，KDJ等进行分析
def Get_TA(df_Code,Dist):
    operate_array1=[]
    operate_array2=[]
    operate_array3=[]
   
    count = 0
    for code in df_Code.index:
# index,0 - 6 date：日期 open：开盘价 high：最高价 close：收盘价 low：最低价 volume：成交量 price_change：价格变动 p_change：涨跌幅
# 7-12 ma5：5日均价 ma10：10日均价 ma20:20日均价 v_ma5:5日均量v_ma10:10日均量 v_ma20:20日均量
        operate1 = 0
        operate2 = 0
        operate3 = 0
        try:
            df = ts.get_hist_data(code,start='2014-11-20')
            dflen = df.shape[0]
    #        print 'dflen=', dflen
            count = count + 1
            if dflen>35:
                try:
                    (df,operate1) = Get_MACD(df)
    #                print operate1
                    (df,operate2) = Get_KDJ(df)
    #                print operate2
                    (df,operate3) = Get_RSI(df)
    #                print operate3
                except Exception, e:
                     Write_Blog(e,Dist)
                     pass
        except Exception, e:
            Write_Blog(df_Code,Dist)
            Write_Blog(e,Dist)
            pass
        operate_array1.append(operate1)  #round(df.iat[(dflen-1),16],2)
        operate_array2.append(operate2)
        operate_array3.append(operate3)
        if count == 0:
            Write_Blog(str(count),Dist)
    df_Code['MACD']=pd.Series(operate_array1,index=df_Code.index)
    df_Code['KDJ']=pd.Series(operate_array2,index=df_Code.index)
    df_Code['RSI']=pd.Series(operate_array3,index=df_Code.index)
    return df_Code


#通过MACD判断买入卖出
def Get_MACD(df):
    #参数12,26,9
    macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)
                   
    SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
    SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
    SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
    #13-15 DIFF  DEA  DIFF-DEA       
    df['macd']=pd.Series(macd,index=df.index) #DIFF
    df['macdsignal']=pd.Series(macdsignal,index=df.index)#DEA
    df['macdhist']=pd.Series(macdhist,index=df.index)#DIFF-DEA
    dflen = df.shape[0]
    MAlen = len(SignalMA5)
    operate = 0
    #2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
    #待修改
    if df.iat[(dflen-1),13]>0:
        if df.iat[(dflen-1),14]>0:
            if df.iat[(dflen-1),13]>df.iat[(dflen-1),14] and df.iat[(dflen-2),13]<=df.iat[(dflen-2),14]:
                operate = operate + 10#买入
    else:
        if df.iat[(dflen-1),14]<0:
            if df.iat[(dflen-1),13] == df.iat[(dflen-2),14]:
                operate = operate - 10#卖出
       
    #3.DEA线与K线发生背离，行情反转信号。
    if df.iat[(dflen-1),7]>=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]>=df.iat[(dflen-1),9]:#K线上涨
        if SignalMA5[MAlen-1]<=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]<=SignalMA20[MAlen-1]: #DEA下降
            operate = operate - 1
    elif df.iat[(dflen-1),7]<=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]<=df.iat[(dflen-1),9]:#K线下降
        if SignalMA5[MAlen-1]>=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]>=SignalMA20[MAlen-1]: #DEA上涨
            operate = operate + 1
               
       
    #4.分析MACD柱状线，由负变正，买入信号。
    if df.iat[(dflen-1),15]>0 and dflen >30 :
        for i in range(1,26):
            if df.iat[(dflen-1-i),15]<=0:#
                operate = operate + 5
                break
            #由正变负，卖出信号   
    if df.iat[(dflen-1),15]<0 and dflen >30 :
        for i in range(1,26):
            if df.iat[(dflen-1-i),15]>=0:#
                operate = operate - 5
                break
            
    return (df,operate)

 
 
#通过KDJ判断买入卖出
def Get_KDJ(df):
    #参数9,3,3
    slowk, slowd = ta.STOCH(np.array(df['high']), np.array(df['low']), np.array(df['close']), fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
   
    slowkMA5 = ta.MA(slowk, timeperiod=5, matype=0)
    slowkMA10 = ta.MA(slowk, timeperiod=10, matype=0)
    slowkMA20 = ta.MA(slowk, timeperiod=20, matype=0)
    slowdMA5 = ta.MA(slowd, timeperiod=5, matype=0)
    slowdMA10 = ta.MA(slowd, timeperiod=10, matype=0)
    slowdMA20 = ta.MA(slowd, timeperiod=20, matype=0)
    #16-17 K,D      
    df['slowk']=pd.Series(slowk,index=df.index) #K
    df['slowd']=pd.Series(slowd,index=df.index)#D
    dflen = df.shape[0]
    MAlen = len(slowkMA5)
    operate = 0
    #1.K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；D大于80时，行情呈现超买现象。D小于20时，行情呈现超卖现象。
    if df.iat[(dflen-1),16]>=90:
        operate = operate - 3
    elif df.iat[(dflen-1),16]<=10:
        operate = operate + 3
       
    if df.iat[(dflen-1),17]>=80:
        operate = operate - 3
    elif df.iat[(dflen-1),17]<=20:
        operate = operate + 3
       
    #2.上涨趋势中，K值大于D值，K线向上突破D线时，为买进信号。#待修改
    if df.iat[(dflen-1),16]> df.iat[(dflen-1),17] and df.iat[(dflen-2),16]<=df.iat[(dflen-2),17]:
        operate = operate + 10
    #下跌趋势中，K小于D，K线向下跌破D线时，为卖出信号。#待修改
    elif df.iat[(dflen-1),16]< df.iat[(dflen-1),17] and df.iat[(dflen-2),16]>=df.iat[(dflen-2),17]:
        operate = operate - 10
   
       
    #3.当随机指标与股价出现背离时，一般为转势的信号。
    if df.iat[(dflen-1),7]>=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]>=df.iat[(dflen-1),9]:#K线上涨
        if (slowkMA5[MAlen-1]<=slowkMA10[MAlen-1] and slowkMA10[MAlen-1]<=slowkMA20[MAlen-1]) or \
           (slowdMA5[MAlen-1]<=slowdMA10[MAlen-1] and slowdMA10[MAlen-1]<=slowdMA20[MAlen-1]): #K,D下降
            operate = operate - 1
    elif df.iat[(dflen-1),7]<=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]<=df.iat[(dflen-1),9]:#K线下降
        if (slowkMA5[MAlen-1]>=slowkMA10[MAlen-1] and slowkMA10[MAlen-1]>=slowkMA20[MAlen-1]) or \
           (slowdMA5[MAlen-1]>=slowdMA10[MAlen-1] and slowdMA10[MAlen-1]>=slowdMA20[MAlen-1]): #K,D上涨
            operate = operate + 1
           
    return (df,operate)
 
#通过RSI判断买入卖出
def Get_RSI(df):
    #参数14,5
    slowreal = ta.RSI(np.array(df['close']), timeperiod=14)
    fastreal = ta.RSI(np.array(df['close']), timeperiod=5)
    slowrealMA5 = ta.MA(slowreal, timeperiod=5, matype=0)
    slowrealMA10 = ta.MA(slowreal, timeperiod=10, matype=0)
    slowrealMA20 = ta.MA(slowreal, timeperiod=20, matype=0)
    fastrealMA5 = ta.MA(fastreal, timeperiod=5, matype=0)
    fastrealMA10 = ta.MA(fastreal, timeperiod=10, matype=0)
    fastrealMA20 = ta.MA(fastreal, timeperiod=20, matype=0)
    #18-19 慢速real，快速real      
    df['slowreal']=pd.Series(slowreal,index=df.index) #慢速real 18
    df['fastreal']=pd.Series(fastreal,index=df.index)#快速real 19
    dflen = df.shape[0]
    MAlen = len(slowrealMA5)
    operate = 0
    #RSI>80为超买区，RSI<20为超卖区
    if df.iat[(dflen-1),18]>80 or df.iat[(dflen-1),19]>80:
        operate = operate - 2
    elif df.iat[(dflen-1),18]<20 or df.iat[(dflen-1),19]<20:
        operate = operate + 2
       
    #RSI上穿50分界线为买入信号，下破50分界线为卖出信号
    if (df.iat[(dflen-2),18]<=50 and df.iat[(dflen-1),18]>50) or (df.iat[(dflen-2),19]<=50 and df.iat[(dflen-1),19]>50):
        operate = operate + 4
    elif (df.iat[(dflen-2),18]>=50 and df.iat[(dflen-1),18]<50) or (df.iat[(dflen-2),19]>=50 and df.iat[(dflen-1),19]<50):
        operate = operate - 4
       
    #RSI掉头向下为卖出讯号，RSI掉头向上为买入信号
    if df.iat[(dflen-1),7]>=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]>=df.iat[(dflen-1),9]:#K线上涨
        if (slowrealMA5[MAlen-1]<=slowrealMA10[MAlen-1] and slowrealMA10[MAlen-1]<=slowrealMA20[MAlen-1]) or \
           (fastrealMA5[MAlen-1]<=fastrealMA10[MAlen-1] and fastrealMA10[MAlen-1]<=fastrealMA20[MAlen-1]): #RSI下降
            operate = operate - 1
    elif df.iat[(dflen-1),7]<=df.iat[(dflen-1),8] and df.iat[(dflen-1),8]<=df.iat[(dflen-1),9]:#K线下降
        if (slowrealMA5[MAlen-1]>=slowrealMA10[MAlen-1] and slowrealMA10[MAlen-1]>=slowrealMA20[MAlen-1]) or \
           (fastrealMA5[MAlen-1]>=fastrealMA10[MAlen-1] and fastrealMA10[MAlen-1]>=fastrealMA20[MAlen-1]): #RSI上涨
            operate = operate + 1
   
    #慢速线与快速线比较观察，若两线同向上，升势较强；若两线同向下，跌势较强；若快速线上穿慢速线为买入信号；若快速线下穿慢速线为卖出信号
    if df.iat[(dflen-1),19]> df.iat[(dflen-1),18] and df.iat[(dflen-2),19]<=df.iat[(dflen-2),18]:
        operate = operate + 10
    elif df.iat[(dflen-1),19]< df.iat[(dflen-1),18] and df.iat[(dflen-2),19]>=df.iat[(dflen-2),18]:
        operate = operate - 10      
    return (df,operate)
def Output_Csv(df,Dist):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    reload(sys)
    sys.setdefaultencoding( "gbk" )
    df.to_csv(Dist+CURRENTDAY+'stock.csv',encoding='gbk')#选择保存   
 
def Close_machine():
    o="c:\\windows\\system32\\shutdown -s"#########
    os.system(o)#########
   

#日志记录
def Write_Blog(strinput,Dist):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    TIME = time.strftime("%H:%M:%S")
    #写入本地文件
    fp = open(Dist+'blog.txt','a') 
    fp.write('------------------------------\n'+CURRENTDAY +" "+TIME+" "+ str(strinput)+'  \n')
    fp.close()
    time.sleep(1)
    print 'Write_Blog'
    print strinput


#发送邮件
def Send_Mail (Message,Dist):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    msg = MIMEMultipart()
   
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    att = MIMEText(open(Dist+CURRENTDAY+'stock.csv', 'rb').read(), 'base64', 'gb2312') #设置附件的目录
    att['content-type'] = 'application/octet-stream'
    att['content-disposition'] = 'attachment;filename="stock.csv"' #设置附件的名称
    msg.attach(att)
   
    content = str(Message) #正文内容
    body = MIMEText(content,'plain','GBK') #设置字符编码
    msg.attach(body)
    msgto = ['xx@126.com'] # 收件人地址多个联系人，格式['aa@163.com'; 'bb@163.com']
    msgfrom = 'xx@126.com' # 寄信人地址 ,
    msg['subject'] = 'Finish at '+CURRENTDAY  #主题
    msg['date']=time.ctime() #时间
    #msg['Cc']='bb@junbao.net' #抄送人地址 多个地址不起作用

    mailuser = 'xx'  # 用户名
    mailpwd = 'xx' #密码
    try:
        smtp = smtplib.SMTP()
        smtp.connect(r'smtp.126.com')# smtp设置
        smtp.login(mailuser, mailpwd) #登录
        smtp.sendmail(msgfrom, msgto, msg.as_string()) #发送
        smtp.close()
        print "success mail"
    except Exception, e:
        print e




       
df = Get_Stock_List()
#print df
Dist = 'output/'
df_ta = Get_TA(df, Dist)
print df_ta


Output_Csv(df,Dist)
#生成的csv文件中，macd列大于0的就是可以买入的，小于0的就是卖出的
