# -*- coding: utf-8 -*-
# 对策略的回测结果分析
import pandas as pd
import numpy as np
import json
import os
import re
import sys
import requests
import datetime
from  common import basefunc
from frame import data_center
from tradeTools import DataMgr
from tradeTools import Decorator


CON_NET_VALUE_FILENAME = "stock_day_net_value.log" # 要读取的日志文件名

path = r"F:\workspace_hc\IndexMarketVRotation\log"
full_path = path + os.sep + CON_NET_VALUE_FILENAME



class Mgr(DataMgr.Mgr):
    @Decorator.loadData()
    def addIndex(self,full_path,frequency = 1,**kwargs):
        df = self.load(full_path)
        begTime = df.iloc[0].name # 策略开始时间
        dfs = [df]
        for indexSymbol in ["SH.000300","SH.000905","SH.000001"]:
            idx = self.genIDXData(indexSymbol=indexSymbol, frequency=frequency)
            idx = idx[idx.index >= str(begTime)]
            dfs.append(idx[[indexSymbol]])
        total = pd.concat(dfs, axis=1, join='outer', )
        return total
    
    # df 每日收益率
    @Decorator.loadData()
    def qryAnalyse(self,df,strategy,frequency):
        begTime = df.iloc[0].name # 策略开始时间
        dfs = [df]
        for indexSymbol in ["SH.000300","SH.000905","SH.000001"]:
            idx = self.genIDXData(indexSymbol=indexSymbol, frequency=frequency)
            idx = idx[idx.index >= str(begTime)]
            dfs.append(idx[[indexSymbol]])
        total = pd.concat(dfs, axis=1, join='outer', )

        d = {}
        for name, s in total.items():
            tradeDays = s.size
            # todo:股票k线数据丢失或停牌，会导致收益率均值为0.加权为空，影响占用天数的统计
            keepTradeDays = tradeDays - s.isnull().sum() # 占用天数
            std = s[~s.isnull()].std()
            yearStd = std * pow(252, 0.5)  # 年化标准差

            avg = s[~s.isnull()].mean()
            std = s[s < avg].std()  # 每日收益率标准差
            SDRyearStd = 2* std * pow(252, 0.5)  # #补偿只有基准以下的收益率计算入标准差，需要再将标准差乘以2
            d[name] = [tradeDays,keepTradeDays,yearStd,SDRyearStd]
        ret = pd.DataFrame(d,index=["总天数","实际占用天数","年化标准差","SDR年化标准差"]).T
        total.fillna(0, inplace=True)  # 停牌的日期。收益率为设为0
        totalCumprod = (1 + total).cumprod()
        ret["累计净值"] = totalCumprod.iloc[-1,:].T

        ret["复合年收益率"] = pow(ret["累计净值"],252/ret["总天数"])-1
        ret["夏普率"] = (ret["复合年收益率"]-0.02)/ret["年化标准差"]
        ret["SDR夏普率"] = (ret["复合年收益率"]-0.02)/ret["SDR年化标准差"]

        ret["年收益率_根据实际占用天数"] =pow(ret["累计净值"],252/ret["实际占用天数"])-1
        ret["夏普率_根据实际占用天数"] = (ret["年收益率_根据实际占用天数"]-0.02)/ret["年化标准差"]
        ret["SDR夏普率_根据实际占用天数"] = (ret["年收益率_根据实际占用天数"] - 0.02) / ret["SDR年化标准差"]

        maximumDrawdown = 1-totalCumprod/np.maximum.accumulate(totalCumprod)
        ret["最大回撤"] = maximumDrawdown.max()
        ret["最大回撤日期"] = maximumDrawdown.idxmax()
        return ret
    
    @Decorator.loadData()
    def qryRateByYear(self,df,frequency,indexSymbol,strategyName):
        idx = self.genIDXData(indexSymbol=indexSymbol, frequency=frequency)
        begTime = df.iloc[0].name # 策略开始时间
        endTime = df.iloc[-1].name # 策略结束时间
        idx = idx[(idx.index >= begTime)&(idx.index <= endTime)]
        total = pd.concat([df,idx[[indexSymbol]]], axis=1, join='outer', )
        s = []
        for i ,y  in total.resample("Y"):
            _y = (1 + y).cumprod()
            _s = _y.iloc[-1]-1
            _s.name = i.year
            s.append(_s)
        r = pd.DataFrame(s)
        return r
    
    @Decorator.loadData()
    def qryDayNetValue(self,logName):
        STRATEGY_PATH_CONF = [os.path.dirname(os.path.dirname(__file__)),"FundFlow",logName]
        # LOG_FILE_NAME = [year for year in range(2010,2012)]
        CON_NET_VALUE_FILENAME = "stock_day_net_value {year}.log"  # 要读取的日志文件名
        dfs = []
        for year in range(2010, 2022):
            paths = []
            paths.extend(STRATEGY_PATH_CONF)
            paths.append(str(year))
            paths.append(CON_NET_VALUE_FILENAME.format(year = year))

            path = os.sep.join(paths)
            print(path)
            df = pd.read_csv(path, engine='python', encoding='gb2312', sep='\t',header=None)
            print(df)
            dfs.append(df)
        total  = pd.concat(dfs, axis=0, join='outer', )
        total.columns = ["日期","净值","回撤","上证指数","上证回撤","沪深300","沪深300回撤","上证50","上证50回撤","资产","利润","保证金","手续费","滑点损失"]

        total["每日收益率"] = total["净值"]/total["净值"].shift() -1
        return total
    #     print(max(1-totalCumprod["SH.000300"]/np.maximum.accumulate(totalCumprod["SH.000300"])))
    #     print(idmax(1-totalCumprod["SH.000300"]/np.maximum.accumulate(totalCumprod["SH.000300"])))
    # # def __init__(self):
    #     self.oldDc = data_center.use()
        # self.df = self.load()

    def load(self,full_path):
        # df = pd.read_csv(full_path,engine='python', encoding='gb2312', sep='\t')
        df = pd.read_csv(full_path,engine='python',encoding="UTF-8", sep='\t')
        df['date'] = pd.to_datetime(df['日期'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        df.drop_duplicates( keep='first',inplace=True)
        return df
    #
    # def concat(self):
    #     indexSymbol = "SH.000905"
    #     df = pd.concat([self.df,self.genIDXData()],axis = 1,join="inner")
    #     dateIdx = df[df['净值']!= 1].iloc[0].name # 首次开仓日期
    #     df = df[df.index>=dateIdx].copy()
    #     df["中证500"] = (1 + df[f"{indexSymbol}收益率"]).cumprod()
    #     name = path+os.sep+f"{STRATEGY_PATH_CONF[-1]}.xlsx"
    #     df.to_excel(name, sheet_name="数据源")
# def genYearReport():
#
#     df = df.resample('Y').last()
#     # Index(['日期', '净值', '回撤', '上证指数', '上证回撤', '沪深300', '沪深300回撤', '上证50', '上证50回撤',
#     #        '资产', '利润', '保证金', '手续费', '滑点损失'],
#     #       dtype='object')
#     df.to_excel("年度净值报告 .xlsx", sheet_name="数据源")

    def getPos(self,dateTime,fullPath):
        # path = f"F:\workspace_hc\Volatility\股息率_filter_0.00#rate_9_1#rank_rate#groupNum_1检查涨跌停False滑点0.0手续费0.0是否补足开仓数量[False]\stock_transection.log"
        df = pd.read_csv(fullPath,engine='python',encoding="utf-8", sep='\t')
        
        df["成交日期"] = pd.to_datetime(df["成交日期"].str.replace("-",""), format='%Y%m%d')
        df["成交数量"] = df.apply(lambda x:-x["成交数量"] if x["方向"] == "卖出" else x["成交数量"],axis=1)
        df = df[df["成交日期"]<=str(dateTime)][["证券代码","成交数量"]]
        df = df.groupby("证券代码").sum()
        df = df[df["成交数量"]>0]
        return df

    def analyseSlippage(self,path):
        # 读取rec文件。分析滑点
        orderRec = "stock_order_20220628.rec"
        # 日期 委托时间 股票代码 名称 交易类型（0:open 1:close） 方向(0:buy,1:sell) 委托价格 成交价格 委托数量 成交数量 撤单数量 委托编号 本地编号 委托状态
        names = ["日期","委托时间","股票代码","名称","交易类型","方向","委托价格","成交价格","委托数量","成交数量","撤单数量","委托编号","本地编号","委托状态",]
        df = pd.read_csv(path+f"\{orderRec}",encoding="utf-8", sep='\t',header=None,names = names )
        firstOrders = df.groupby("股票代码").apply(lambda x: x.iloc[0]) # 第一次委托
        print(firstOrders)
        transRec = "stock_transaction_all.rec"
        names = ["日期","成交时间","市场","股票代码","名称","操作名称","交易类型","方向","成交价格","成交数量","委托编号","成交编号","成交额","手续费"]
        transDf = pd.read_csv(path+f"\{transRec}",encoding="utf-8", sep='\t',header=None,names = names )
        total = transDf.groupby("股票代码").sum()
        total["平均成交价格"] = total["成交额"]/total["成交数量"]
        df = pd.concat([firstOrders,total[["平均成交价格"]]],axis=1)
        print(df)
        ordersum = (df["委托价格"]*df["委托数量"]).sum()

        transum = (df["平均成交价格"]*df["委托数量"]).sum()
        print("委托市值",ordersum)
        print("成交市值",transum)
        print((transum-ordersum)/ordersum)
        
        
    def calcProfit(self,path):
        transRec = "stock_transaction_all.rec"
        names = ["日期","成交时间","市场","股票代码","名称","操作名称","交易类型","方向","成交价格","成交数量","委托编号","成交编号","成交额","手续费"]
        transDf = pd.read_csv(path+f"\{transRec}",encoding="utf-8", sep='\t',header=None,names = names )
        total = transDf.groupby("股票代码").sum()
        
        total = total[["成交数量"]]
        print(total.loc[["SH.600373","SH.600919"]]) # 这两只股票重复报单了
        rates = []
        for dateTime in [20220630,20220701,20220704]:
            _rate =pd.Series(name = dateTime)
            for symbol in total.index.tolist():
                price,_ = self.oldDc.get_nearest_price(stock_id=symbol,datetime=dateTime)
                _rate[symbol] = price
            rates.append(_rate)
            
        df = pd.DataFrame(rates)
        total =  pd.concat([total,df.T],axis=1)
        total["当日盈亏"] = (total[20220701] - total[20220630])* total["成交数量"]
        print(total.loc["SH.601939"]) 
        print(total["当日盈亏"].sum()) # 和同花顺结果一致  20220704 3973
        
if __name__ == '__main__':
    mgr = Mgr()
    mgr.addIndex(full_path)
    # path = r"F:\实盘记录\20220628实盘开仓记录\rec\收盘后rec"
    # df = mgr.calcProfit(path= path)
    # df = mgr.analyseSlippage(path = path) # 计算滑点
    

