# coding=utf-8
'''
Created on March 6, 2018-00:18:31 am

@author: yubangwei_pc
'''
import pandas as pd
from pandas import DataFrame
from pandas import Series
import numpy as np
import tushare as ts
from analysis_stock_strage import is_not_rising, is_rising

def fill_buy_info(buy_in_method, const_buy_in_len, sell_out_method, const_sell_len, judege_key, df_data):
    '''
    仿照函数is_rising指定的参数，如果buy_in_method返回true，填买入；否则不操作
    '''
    for i in range(len(df_data[judege_key])):
        index = df_data.index[i]
        if buy_in_method(df_data[i:], judege_key, const_buy_in_len):
            if 'NAN' == df_data['buy_or_sell'][i]:
                df_data.loc[index,'buy_or_sell'] = 'buy'
            else:
                print('ERROR: There already has valid value.i = %d, %s'%(i, df_data['buy_or_sell'][i]))
                #return
        
        if sell_out_method(df_data[i:], judege_key, const_sell_len):
            if 'NAN' == df_data['buy_or_sell'][i]:
                df_data.loc[index, 'buy_or_sell'] = 'sell'
            else:
                print('ERROR: There already has valid value.i = %d, %s'%(i, df_data['buy_or_sell'][i]))
                #return
        
        if 'NAN' == df_data['buy_or_sell'][i]:
            print("Not need to buy in or sell out on %s"%(df_data.index[i]))
            
def test_strategy(buy_in_method, buy_in_len, sell_out_method, sell_out_len, judge_key, his_data):
    '''
    计算方法：
    1、使用买入和卖出函数，对历史数据进行处理，对每天应该买入还是卖出进行打点，添加一列。
    2、遇到操作拐点时，进行操作.
    3、以一手作为投入成本，计算收益率
    
    单点买入时间点：
    1、买入最高点，卖出最低点
    2、买卖都是收盘价附近  √
    待确认：
    1、每次买入多少?暂定一手。
    2、每次卖出：空仓
    '''
    if not isinstance(his_data, DataFrame):
        print('ERROR: The input his data is not DataFrame.')
        return
    
    his_data.loc[0:, 'buy_or_sell'] = ['NAN']*len(his_data)
    #buy_in_method(his_data)
    #sell_out_method(his_data)
    fill_buy_info(buy_in_method, buy_in_len, sell_out_method, sell_out_len,judge_key, his_data)
    
    original_cost = 10000;
    total_property = original_cost
    for index in range(len(his_data['buy_or_sell']))[::-1]:
        if his_data['buy_or_sell'][index] == 'buy':
            print("%s Buy in."%(his_data.index[index]))
            break
        
    if index == 0:
        print("ERROR: cannot get <buy_in> price!!")
        return
    
    current_stock_value = his_data['close'][index]*100
    current_cash = original_cost - current_stock_value
    max_value = 0
    min_value = original_cost*10
    current_operation = 'buy'
    index -= 1
    
    while index >= 0:
        if current_operation != his_data['buy_or_sell'][index] and his_data['buy_or_sell'][index] != 'NAN':
            if his_data['buy_or_sell'][index] == 'buy' and current_cash >= his_data['close'][index]*100:
                total_property = current_cash
                current_cash -= his_data['close'][index]*100
                current_stock_value = his_data['close'][index]*100# 每次只操作一手
                current_operation = 'buy'
                print("%s Buy in, and total_property = %d, stock_value = %d"%(his_data.index[index], \
                                                                              total_property, current_stock_value))
                
            if his_data['buy_or_sell'][index] == 'sell' and current_stock_value != 0:
                current_cash += his_data['close'][index]*100
                #total_property = current_cash
                current_stock_value = 0
                current_operation = 'sell'
                print("%s Sell out, total_property = %d, and make ￥%d"%(his_data.index[index], current_cash,\
                                                                        current_cash - total_property))
                total_property = current_cash
            
            max_value = max_value if max_value > current_cash + current_stock_value else current_cash + current_stock_value
            min_value = min_value if min_value < current_cash + current_stock_value else current_cash + current_stock_value        
        index -= 1
    print('The final value = %f, and max_value = %f, min_value = %f'%(current_cash + current_stock_value, max_value, min_value))
    
    
def unit_test1_ma20():
    his_data_df = ts.get_hist_data('002405')# 获取的数据是从当前时间开始的倒叙    
    #(buy_in_method, buy_in_len, sell_out_method, sell_out_len, judge_key, his_data):
    test_strategy( is_rising, 5, is_not_rising, 5, 'ma20', his_data_df[0:101])
    
    
if __name__ == '__main__':
    unit_test1_ma20()
    