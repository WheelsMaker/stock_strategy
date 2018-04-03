# coding=utf-8
'''
Created on Mar 22, 2018-1:12:17 AM

@author: yubangwei_pc
'''

import tushare as ts
import pandas as pd
from pandas import DataFrame

def get_low_pe_high_roe(to_filter_stock, highest_pe, lowest_roe, year, quart):
    '''
    获取指定年和季度市盈率小于highest_pe， 同时收益率大于lowest_roe的股票
    入参：hightest_pe: 市盈率的最大值
    lowest_roe:收益率的最小值
    year: 统计年度 
    quart:统计季度
    输出：市盈率小于highest_pe，同时，收益率大于lowest_roe的股票信息。
    形式为:({'name':[], 'pe':[], 'roe':[]}), index = 股票编号
    '''
    basics_data = ts.get_stock_basics();
    
    #basics_data.index = basics_data['code']
    
    profit_data = ts.get_profit_data(year,quart)
    profit_data.index = profit_data['code']
    
    df = DataFrame({'code':[], 'name':[], 'pe':[], 'roe':[]})
    
    for code in to_filter_stock:
        try:
            if basics_data.loc[code, 'pe'] < highest_pe and profit_data.loc[code, 'roe'] > lowest_roe:
                item = DataFrame({'code':code, 'name':profit_data.loc[code, 'name'], 'pe':basics_data.loc[code, 'pe'], \
                                  'roe':profit_data.loc[code, 'roe']},index = [code])
                df = pd.concat([df.loc[:], item])
        except ValueError as e:
            print('ERROR CODE:', e)
            print('ERROR: code = %s,%s'%(code, profit_data.loc[code, 'name']))   
            print('basics_data = ',end = '')
            print(basics_data.loc[code, :])
            print('profit_data = ',end = '')
            print(profit_data.loc[code, :])
            print('\n')
        except KeyError as e:
            print('ERROR CODE:', e)
            print('ERROR: code = %s,%s'%(code, basics_data.loc[code, 'name']))   
            print('basics_data = ',end = '')
            print(basics_data.loc[code, :])
            print('profit_data = ',end = '')
            print(basics_data.loc[code, :])
            print('\n')
            

    return df