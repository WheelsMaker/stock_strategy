# coding=utf-8
'''
Created on Nov 7, 2017-12:40:31 AM

@author: yubangwei_pc
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tushare as ts
from datetime import datetime

# 考虑拟合20天均线，取导数？
m20_para = {'not_rising_days':5, #连续not_rising_days多天不上涨，说明20天均线横盘或者下跌
            'const_rising_days':3 # 连续const_rising_days多天上涨，说明20天均线开始上涨
            }
 
def is_rising(his_data_df, judge_para='ma20', const_times=3):
    '''
    连续not_rising_days次不增加，紧接着连续const_rising_days次递增，认为是增长的，出现拐点
    :功能要单一，只判断上升沿，或者下降沿
    '''
    if None is his_data_df:
        return False
    
    recent_risng_days_th = const_times
    if len(his_data_df) < recent_risng_days_th :
        return False
    
    for i in range(recent_risng_days_th):
        if his_data_df[judge_para][0+i] <= his_data_df[judge_para][1+i]:
            return False
        
    return True

def is_not_rising(his_data_df, judge_para='ma20', const_not_rising_times=5):
    if None is his_data_df:
        return False
    if len(his_data_df) < const_not_rising_times :
        return False
    for i in range(const_not_rising_times):
        if his_data_df[judge_para][0+i] > his_data_df[judge_para][1+i]:
            return False
        
    return True
    

def update_stock_code():
    with open('.\\stock_code.txt', 'r') as fid:
        try:
            stock_code_id = fid.readlines()
            record_date = stock_code_id[-1]

            record_date = pd.Timestamp(record_date)
            now_date = pd.Timestamp(datetime.now())
            diff_date = now_date - record_date
            if (diff_date.days < 20):
                return
        except:
            print("Cannot get date information from stock file")
    
    print("Updating the stocks id from network(...)")
    # 上次刷新股票编号的时间超过20天，重新再刷一次
    with open('.\\stock_code.txt', 'w+') as fid:
        stock_code_df = ts.get_today_all()
        for i in stock_code_df.index:
            fid.write('%s, %s\n'%(stock_code_df['code'][i], stock_code_df['name'][i]))
        fid.write(datetime.now().strftime('%Y-%m-%d'))

def get_all_stock_id_and_name():
    '''
    返回: id:name形式的字典
    '''
    update_stock_code()
    with open('.\\stock_code.txt', 'r') as fid:
        stock_code_id = fid.readlines()
        stock_code_id = stock_code_id[:len(stock_code_id)-1]# 最后一行保存的是刷新时间
    
    stock_id_name_info = dict()
    for stock_id_name in stock_code_id:
        stock_id = stock_id_name.strip().split(',')[0]
        stock_name = stock_id_name.strip().split(',')[1]
        stock_id_name_info[stock_id] = stock_name
    
    return stock_id_name_info
                
def Ma20_rising_strategy():
    '''根据ma20曲线拐点决定买入还是卖出：如果出现横盘或者下跌就卖出；如果出现上升，就买进。具体是否上升需要参数判断m20_para.
          将需要买入的股票编号及其20天均线保存
          参考 http://blog.sina.com.cn/s/blog_b598fcc90102xi1d.html
    '''
    with open('.\\stock_code.txt', 'r') as fid:
        stock_code_id = fid.readlines()
        stock_code_id = stock_code_id[:len(stock_code_id)-1]# 最后一行保存的是刷新时间
    
    print("The following stocks' 20ma are rising:")
    ma20_rising_file = open('.\\ma20\\m20_rising_stocks.txt', 'w+')
    for stock_id_name in stock_code_id:
            
        stock_id = stock_id_name.strip().split(',')[0]
        stock_name = stock_id_name.strip().split(',')[1]
        try:
            his_data_df = ts.get_hist_data(stock_id)# 获取的数据是从当前时间开始的倒叙
        except:
            print("Cannot get %s his data."%stock_id)
            continue

        if is_rising(his_data_df, 'ma20', m20_para['const_rising_days']) and \
            is_not_rising(his_data_df[m20_para['const_rising_days']:], 'ma20', m20_para['not_rising_days']):
            print('%s'%stock_id)
            plt.plot(his_data_df['ma20'][100:0:-1])# 获取的数据是从当前时间开始的倒叙
            #plt.show()
            fig_name = '.\\ma20\\%s_%s.png'%(stock_id, stock_name)
            plt.savefig(fig_name)
            plt.close()
            ma20_rising_file.write('%s\n'%stock_id_name)
            print('code: %s'%(stock_id_name))
            
    ma20_rising_file.close()    
    
    
if __name__ == '__main__':
    update_stock_code()
    Ma20_rising_strategy()