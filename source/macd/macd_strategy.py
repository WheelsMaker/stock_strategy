# -*- coding:utf-8 -*- 
'''
Created on Mar 14, 2018-12:29:46 AM

@author: yubangwei_pc
'''
import tushare as ts
from pandas import DataFrame
from pandas import Series
import talib
import numpy as np
import matplotlib.pyplot as plt
import datetime
import analysis_stock
import filter_good_stocks
date_format = '%Y-%m-%d'

def get_EMA(df, N): 
    column_name =  'ema%d'%N
    close = [x for x in df['close']]# 由于数据是按照时间倒叙提供的，这里取倒叙
    for i in range(len(df)):  
        if i==0:  
            df.ix[i,column_name]= close[i]  
        if i>0:  
            df.ix[i,column_name]=(2*close[i]+ (N-1)*df.ix[i-1,column_name])/(N+1) 
            
    ema = list(df[column_name])  
    return ema  

def get_MACD(df, short=12, long=26, M=9):  
    a=get_EMA(df, short)  
    b=get_EMA(df, long)  
    df['diff']=np.array(a)-np.array(b)  
    #print(df['diff'])  
    for i in range(len(df)):  
        if i==0:  
            df.ix[i,'dea']=df.ix[i,'diff']  
        if i>0:  
            df.ix[i,'dea']=(2*df.ix[i,'diff']+(M-1)*df.ix[i-1,'dea'])/(M+1)  
    df['macd']=2*(df['diff']-df['dea'])  
    return df 



def get_MACD_with_Talib(df):
    close = [float(x) for x in df['close']]
    # 调用talib计算MACD指标
    df['MACD'],df['MACDsignal'],df['MACDhist'] = talib.MACD(np.array(close),
                                fastperiod=12, slowperiod=26, signalperiod=9)  

#stock_id = '000063'
def get_macd_by_time_order(stock_id, plot_enable = False):
    '''
    按照时间顺序进行计算，获取macd，diff，dea
    '''
    try:
        his_data = ts.get_hist_data(stock_id)    
        if his_data is None:
            return None
    except IOError as e:
        print(str(e))
        print('Cannot get %s stock his data'%stock_id)
        return None
        
    #get_MACD_with_Talib(his_data)
    his_data = his_data[::-1] #将数据按照时间顺序排序，方便计算
    get_MACD(his_data, 12, 26, 9)
    #his_data = his_data[::-1]
    
    if plot_enable:
        print(his_data.tail(5))
        x_label = [x for x in range(len(his_data))]
        ax = plt.subplot(2,1,1)
        plt.plot(x_label, his_data['ma10'], 'g|')
        ax.set_title('%s Ma10'%stock_id)
        
        ax = plt.subplot(2,1,2)
        plt.plot(x_label, his_data['macd'], 'r-', label=u'macd')
        plt.plot(x_label, his_data['dea'] , 'y-', label=u'dea')
        plt.plot(x_label, his_data['diff'], 'k-', label = u'diff')
        plt.plot(x_label, np.zeros(len(x_label)), 'k--')
        ax.set_title('%s MACD'%stock_id)
        plt.legend()
        plt.show()
        plt.close()
    return his_data

def has_golden_cross(his_data, begin_date, end_date):
    '''
    判断指定天数内是否有黄金交叉，并且返回出现黄金交叉, 并且出现黄金交叉的第二天依然上涨，
    的时间. 如果没有黄金交叉， 返回none
    输入的数据要求是：
    his_data: 按照时间顺序已经排序，并且已经有macd, diff, dea等信息
    begin_date: 查找开始时间，形式必须是:'xxxx-xx-xx'
    end_date: 查找结束时间，形式必须是:'xxxx-xx-xx'，比end_date更接近现在
    '''

    try:
        macd_slice = his_data[begin_date:end_date]
    except:
        print('\nERROR: please double check begin_date(%s) than end_date(%s)'%(begin_date, end_date))
        return None
    
    if len(macd_slice) < 3 :
        print("\nERROR: please double check begin_date(%s) than end_date(%s)"%(begin_date, end_date))
        return None
    
    for i in range(len(macd_slice) - 2):
        if macd_slice['macd'][i] < 0 and macd_slice['macd'][i+1] > 0 and \
            macd_slice['close'][i+1] < macd_slice['close'][i+2]:
            print('macd[0] = %f, macd[1] = %f and close[1] = %f, close[2] = %f'%(macd_slice['macd'][i],\
                macd_slice['macd'][i+1], macd_slice['close'][i+1], macd_slice['close'][i+2]))
            return (macd_slice.index[i:i+2])

    return None

def const_incr_macd(his_data, begin_date, end_date, const_incr_days):
    '''
    判断指定天数内最后const_incr_days天是否有连续增长，同时diff和dea都大于0，
    如果有，返回信息，； 如果没有黄金交叉， 返回none
    输入的数据要求是：
    his_data: 按照时间顺序已经排序，并且已经有macd, diff, dea等信息
    begin_date: 查找开始时间，形式必须是:'xxxx-xx-xx'
    end_date: 查找结束时间，形式必须是:'xxxx-xx-xx'，比end_date更接近现在
    const_incr_days:持续增长的时间
    '''
    
    try:
        macd_slice = his_data[begin_date:end_date]
    except:
        print('\nERROR: please double check begin_date(%s) than end_date(%s)'%(begin_date, end_date))
        return None
    
    if len(macd_slice) < 3 :
        print("\nERROR: please double check begin_date(%s) than end_date(%s)"%(begin_date, end_date))
        return None
    
    max_macd = macd_slice['macd'][-const_incr_days]
    beginIndex = -const_incr_days
    for i in range(const_incr_days-1):
        index = (beginIndex + i + 1)
        if macd_slice['macd'][index] < max_macd or macd_slice['diff'][index] < -0.0:
            print('max_macd = %f, cur_macd = %f and diff = %f'%(max_macd,\
                macd_slice['macd'][index], macd_slice['diff'][index]))
            return None
        else:
            max_macd = macd_slice['macd'][index]
    return macd_slice.index[-const_incr_days:]
    
    
    
def main_traversal():
    '''
    遍历所有股票编码，找到指定天数内，macd上升的股票编号;
    筛选出连续几天上涨或者出现金叉的股票
    '''
    gold_cross_stock = dict()
    stock_id_info = analysis_stock.get_all_stock_id_and_name()
    for stock_id in stock_id_info:
        print('%s'%stock_id, end=': ')
        his_data = get_macd_by_time_order(stock_id)
        if his_data is None:
            continue
        gold_date = has_golden_cross(his_data,  (datetime.datetime.now() - datetime.timedelta(7)).strftime(date_format), datetime.datetime.now().strftime(date_format))
        if gold_date is not None:
            print('%s:%s has the gold cross in %s~%s'%(stock_id, stock_id_info[stock_id], gold_date[0], gold_date[1]))
            gold_cross_stock[stock_id] = stock_id_info[stock_id]
            
        const_incr_date = const_incr_macd(his_data, (datetime.datetime.now() - datetime.timedelta(7)).strftime(date_format), datetime.datetime.now().strftime(date_format), 3)
        if const_incr_date is not None:
            print('%s:%s has the gold cross in %s~%s'%(stock_id, stock_id_info[stock_id], const_incr_date[0], const_incr_date[-1]))
            gold_cross_stock[stock_id] = stock_id_info[stock_id]
            
        del(his_data)
    
        
    print("The Gold cross stocks are:")
    for key in gold_cross_stock:
        print("%s,%s"%(key, gold_cross_stock[key]))
 
def main_with_pe_roe():
    '''
    遍历所有沪深300的股票，选择市盈率低，同时，净资产收益率高的公司股票。
    '''
    to_filter_stock = ts.get_hs300s()
    filtered_stock_info = filter_good_stocks.get_low_pe_high_roe(to_filter_stock['code'], 30, 10, 2017, 4)
    if len(filtered_stock_info) < 0:
        print('cannot find the stocks: pe<30, roe>10 in 2017-Q04')                                                                                                                                                                                                                                                                                                                                        
        return
    
    file_name = 'D:\\software\\Python\\DataAnalyze\\stock_proj\\macd\\1.code_range.csv'
    final_coe_name = 'D:\\software\\Python\\DataAnalyze\\stock_proj\\macd\\1.final_code.csv'
    filtered_stock_info.to_csv(file_name, sep='\t', index=True)
    
    gold_cross_stock = DataFrame({'code':[], 'name':[], 'macd':[], 'pe':[], 'roe':[]})
    for code in filtered_stock_info['code']:
        #code = '%s, %s'%(code, filtered_stock_info.loc[code, 'name'])
        print('%s'%code, end=': ')
        his_data = get_macd_by_time_order(code)
        if his_data is None:
            continue
        # 筛选出指定日期内，出现过黄金交叉的股票
        gold_date = has_golden_cross(his_data,  (datetime.datetime.now() - datetime.timedelta(7)).strftime(date_format), datetime.datetime.now().strftime(date_format))
        if gold_date is not None:
            print('%s:%s has the gold cross in %s~%s'%(code, filtered_stock_info.loc[code, 'name'], gold_date[0], gold_date[1]))
            gold_cross_stock.ix[code] = [code, filtered_stock_info.loc[code, 'name'], \
                                         his_data['macd'][-1], filtered_stock_info.loc[code,'pe'],\
                                         filtered_stock_info.loc[code,'roe']]
          
        # 筛选macd连续增长的股票    
        const_incr_date = const_incr_macd(his_data, (datetime.datetime.now() - datetime.timedelta(7)).strftime(date_format), datetime.datetime.now().strftime(date_format), 4)
        if const_incr_date is not None:
            print('%s:%s has the gold cross in %s~%s'%(code, filtered_stock_info.loc[code, 'name'], const_incr_date[0], const_incr_date[-1]))
            gold_cross_stock.ix[code] = [code, filtered_stock_info.loc[code, 'name'], \
                                         his_data['macd'][-1], filtered_stock_info.loc[code,'pe'],\
                                         filtered_stock_info.loc[code,'roe']]
            
        del(his_data)
    
    print("The Gold cross stocks are:")
    for key in gold_cross_stock:
        print("%s,%s"%(key, gold_cross_stock[key]))
    gold_cross_stock.to_csv(final_coe_name, sep='\t', index = False)
    
    
if __name__ == '__main__':
    main_with_pe_roe()
        