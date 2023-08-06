# -*- coding: utf-8 -*-
from tradeTools import helpers
from tradeTools import Decorator
from frame import data_center #frame 软连接到trade模块的frame
from frame import stock_func
from datetime import datetime
import pandas as pd
import numpy as np
import os



QUERY_CONF = {} # 查询配置
QUERY_CONF["balance"] = {}
QUERY_CONF["balance"]["equitiesParentCompanyOwners"] = "归属于母公司股东权益合计"


class Mgr():
    def __init__(self):
        self.oldDc = data_center.use()

    def queryST(self, dateTime = 20210101) -> list:
        """ 
            扣除非经常性损益后的净利润 两年全负数，来判断ST
            无财报数据默认净利润为-1
        Args:
            dateTime (int, optional): 当前日期. Defaults to 20210101.

        Returns:
            list: st股列表
        """
       
        reportYear = dateTime // 10000 - 1 if dateTime % 10000 >= 430 else dateTime // 10000 - 2
        queryConf = {}
        queryConf["RecurringNetProfit"] = "扣除非经常性损益后的净利润"
        reportDate = reportYear * 10000 + 1231
        lastReportDate = (reportYear - 1) * 10000 + 1231
        sql = "SELECT "
        for key in queryConf.keys():
            sql += key + ","
        sql += f"symbol,reportDate FROM `income` WHERE reportDate in ({reportDate},{lastReportDate}) "
        df = pd.read_sql(sql, self.oldDc.database.conn)
        df = df.set_index("symbol")
        df = df.fillna(-1) 
        stSymbols = []
        for symbol in set(df.index.tolist()):
            _df = df.loc[symbol, ["RecurringNetProfit"]]
            __df = _df[_df.values > 0]  # 两年全负数，
            if __df.empty:
                stSymbols.append(symbol)
        return stSymbols
    
    # 获取上市满1年的股票
    # 过滤st股
    def getSymbols(self,dateTime = 20210101,years = -1,isFilterSt = True,isRealTime = False) -> list:
        """_summary_

        Args:
            dateTime (int, optional): _description_. Defaults to 20210101.
            years (int, optional): 上市时间约束，默认满一年. Defaults to -1.
            isFilterSt (bool, optional): 是否过滤st股,注意如果dateTime 大于5月会取最新年报期 Defaults to True.
            isRealTime (bool, optional): _description_. Defaults to False.

        Returns:
            list: _description_
        """
        if not hasattr(self, 'listDf') or isRealTime:
            self.listDf = helpers.getSymbolsInfo(isRealTime = isRealTime)
            self.listDf = self.listDf.drop_duplicates(subset=["symbol",],keep='first')
            self.listDf = self.listDf.set_index("symbol")
            listDf = self.listDf
        else:
            listDf = self.listDf
        start = datetime.strptime(str(dateTime), '%Y%m%d') + pd.tseries.offsets.DateOffset(years = years)
        symbols= listDf[listDf.listingDate <= str(start)].index.tolist()
        if isFilterSt:
            symbols = list(set(symbols) - set(self.queryST(dateTime =dateTime)))
        return symbols
    
    @Decorator.loadData(path="data")
    def genIDXData(self, indexSymbol,isRealTime = False,**kwargs):
        # 获取指数月度收益率数据
        # fileExtension ：间隔日
        if not hasattr(self, "oldDc"):
            self.oldDc = data_center.use()
        maxDate = 0
        fileName = kwargs["fileName"]
        if  os.path.exists(fileName):
            oldDf = pd.read_csv(fileName, index_col=0,)
            maxDate = oldDf["time"].max()
        sql = "SELECT "
        sql += f" code,time,close from `index_day_data` WHERE code = '{indexSymbol}'"
        if maxDate:
            sql+=f" and time>{maxDate}"
        df = pd.read_sql(sql, self.oldDc.database.conn)
        if df.empty:
            return oldDf
        
        df['date'] = pd.to_datetime(df['time'], format='%Y%m%d')
        df.set_index('date', inplace=True)

        if maxDate:
            df = oldDf.append(df)
        df[indexSymbol] = df.close / df.close.shift(1) - 1
        return df
    
    @Decorator.firstLoad
    @Decorator.loadData(path="data")
    def genSymbolRateData(self, symbol, isRealTime=False,**kwargs):
        # 生成间隔数据收益率数据
        if not hasattr(self, "oldDc"):
            self.oldDc = data_center.use()
        maxDate = 0
        fileName = kwargs["fileName"]
        if  os.path.exists(fileName): # 读取已有数据文件
            oldDf = pd.read_csv(fileName, index_col=0,)
            if not oldDf.empty:
                maxDate = oldDf["time"].max()
            
        sql = "SELECT "
        if symbol[-6:].startswith("1"):
            sql += f" code,time,close,volume from `bond_day_data` WHERE code = '{symbol}'"
        else:
            sql += f" code,time,close,volume from `tdx_day_data` WHERE code = '{symbol}'"
        if maxDate:
            sql+=f" and time >={maxDate}" # 多取一条历史数据
        df = pd.read_sql(sql, self.oldDc.database.conn)
        if df.empty:
            if maxDate:
                return oldDf
            return pd.DataFrame()

        df['date'] = pd.to_datetime(df['time'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        
        df["lastTime"] = df.time.shift()
        df["lastClose"] = df.close.shift()

        def _getRehabilitationClose(hang):  # 复权
            begTime = hang.lastTime
            endTime = hang.time
            symbol = hang.code
            dividends = self.oldDc.query_dividends(stock_id=symbol, begtime=begTime, endtime=endTime)
            pre_close = hang.lastClose
            if dividends[symbol]:
                for dividend in dividends[symbol]:
                    pre_close = stock_func.get_dividend_pre_price(pre_close, dividend[1])  # 前复权
            return (hang.close / pre_close) - 1

        df["rate"] = df.apply(_getRehabilitationClose, axis=1)
        if maxDate:
            df = df[df.time>maxDate]
            df = oldDf.append(df)
            df['date'] = pd.to_datetime(df['time'], format='%Y%m%d')
            df.set_index('date', inplace=True)
        return df
    
        # sql = "SELECT "
        # sql += f" id,datetime,total_capital as totalCapital,unlimited_sell_shares as unlimitedSellShares from `std_dzh_capital_report` WHERE id = '{symbol}'"
        # capital = pd.read_sql(sql, self.oldDc.database.conn)
        # capital['date'] = pd.to_datetime(capital['datetime'], format='%Y%m%d')
        # capital.set_index('date', inplace=True)
        # capital = capital[["totalCapital","unlimitedSellShares"]]/10**4
        # conDf = pd.concat([df, capital], join="outer", axis=1)
        # conDf["totalCapital"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
        # conDf["unlimitedSellShares"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充

        # conDf["MarketV"] = conDf["close"]*conDf["total_capital"]
        # conDf["MarketV"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
        # conDf["TurnOver"] = conDf["volume"]*100/conDf["unlimited_sell_shares"]*100
        # conDf = conDf.dropna(axis=0,subset = ["交易日"]) 
        # return conDf

    @Decorator.loadData(path="data")
    def genSymbolTScore(self, symbol, frequency,windows,):#滚动z分数
        allData = self.genSymbolRateData(symbol=symbol,frequency=frequency)
        if allData.empty:
            return pd.DataFrame()
        allData['mRate'].fillna(0, inplace=True) # 停牌的日期。收益率为设为0
        allData['mean'] = allData['mRate'].rolling(windows).mean()
        allData['std'] = allData['mRate'].rolling(windows).std(ddof = 1)
        allData["ZScore"] =  (allData['mRate'] - allData['mean'])/allData['std']
        allData["TScore"] =  50+10*allData["ZScore"]
        return allData[['mRate','mean','std','ZScore','TScore']]

    @Decorator.loadData(path="data")
    def genTradeDays(self,frequency :int = 20,isRealTime = False):
        # 根据换仓频率生成交易日列表
        # fileExtension 交易日间隔
        allTradeDays =  self.oldDc.trade_days
        # 切割交易日
        tradeDays = []
        for i in range(len(allTradeDays)//frequency+1):
            index =  (i+1)*frequency-1
            if index < len(allTradeDays):
                tradeDays.append(allTradeDays[index])
        df = pd.DataFrame(tradeDays,columns=["交易日"])
        df['date'] = pd.to_datetime(df['交易日'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        return df

    def getSymbolRateData(self,symbol,isRealTime=False):
        if not hasattr(self, 'symbolRateData'):
                self.symbolRateData = {}
        if symbol not in self.symbolRateData:
            symbolRateData = self.genSymbolRateData(symbol=symbol,
                                                isRealTime=isRealTime)
            if symbolRateData.empty:
                print(f"{symbol}无历史行情数据")
            self.symbolRateData[symbol] = symbolRateData
        return self.symbolRateData.get(symbol)
    
    def getSymbolsData(self,symbols,endDate):
        rates = []
        marketValues = []
        for symbol  in symbols:
            rateDf = self.genSymbolRateData(symbol=symbol)
            star = endDate.replace(endDate.year - 2)
            df = rateDf[(star<=rateDf.index)&(rateDf.index<=endDate)]
            rate = df["mRate"]
            marketValue = df["MarketV"]
            rate.name = symbol
            marketValue.name = symbol
            rates.append(pd.DataFrame(rate))
            marketValues.append(pd.DataFrame(marketValue))
        symbolsReturn = pd.concat(rates,axis=1) 
        marketValue = pd.concat(marketValues,axis=1) 
        marketValue["TOTAL"] = marketValue.sum(axis=1) 
        marketValue = (marketValue.T / marketValue.TOTAL).T # 求权重
        marketValue = marketValue.iloc[-1]
        marketValue = marketValue.drop("TOTAL")
        return symbolsReturn,marketValue  
    
    def genReturn(self,beg,end,symbols,weight = []):
        rate = []
        for symbol in symbols:
            df = self.genSymbolRateData(symbol=symbol,)
            # 计算累计收益率
            s = df.loc[(beg<df.index) & (df.index<=end)]["rate"] 
  
            s.name = symbol
            rate.append(s)
        rateDf = pd.concat(rate,axis=1)
        rateDf = rateDf.fillna(0)  # 停牌股。当日的收益率为0
        # 如果多个交易日。由初始交易日的权重和前一日的净值。得出前一日的权重比例。再和当日的收益率点积
        if rateDf.shape[0] <= 1:
            rate = np.dot(rateDf.iloc[-1],weight)  
        else :
            cumprodDf  =(1 + rateDf).cumprod()
            last = cumprodDf.iloc[-1]
            # 考虑如果总仓位累加不为1
            _p = 1- np.sum(weight) # 初始留存的净值
            rate = _p+np.dot(cumprodDf.iloc[-1],weight) # 当前净值
            rate/= _p+ np.dot(cumprodDf.iloc[-2],weight)# 上一日净值    
            rate -= 1       
        return rate
    
    # 计算symbols组合的收益率
    def genReturnMonthlys(self, dateTime, symbols, frequency, ):
        seriseMonthRate = []
        for symbol in symbols:
            if not hasattr(self, 'symbolRateData'):
                self.symbolRateData = {}

            if symbol not in self.symbolRateData:
                symbolRateData = self.genSymbolRateData(symbol=symbol, frequency=frequency,
                                                        isRealTime=False)
                if symbolRateData.empty:
                    continue
                symbolRateData["lastMarketV"] = symbolRateData["MarketV"].shift()
                symbolRateData['lastMarketV'].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
                self.symbolRateData[symbol] = symbolRateData
            df = self.symbolRateData.get(symbol)

            if dateTime not in df.index:
                print(f"{symbol} {dateTime}的数据为空 ")
                continue
            s = df.loc[dateTime]
            seriseMonthRate.append(s)
        monthDf = pd.DataFrame(seriseMonthRate)
        if monthDf.empty:
            return monthDf
        monthDf["市值权重"] = monthDf.lastMarketV / monthDf.lastMarketV.sum()
        monthDf["wRate"] = monthDf.mRate * monthDf["市值权重"]  # 加权收益率
        print(monthDf)
        sumWRate = monthDf.wRate.sum()
        meanRate = monthDf.mRate.mean()
        returnMonthlyDf = pd.DataFrame([[sumWRate, meanRate]], index=[dateTime], columns=['sumWRate', "meanRate"])
        return returnMonthlyDf

    def analyseReturn(self,df):
        tradays = df.shape[0]
        yearRtn = pow(df["cumprod"][-1],252/tradays)-1
        print("复合年化收益",yearRtn)
        r = self.calcSharpRatio(df = df) # 夏普率
        print("最大回撤",df["maximumDrawdown"].max())
        print("最大回撤日期",df["maximumDrawdown"].idxmax())
        print("近半年最大回撤",df["maximumDrawdown"][-120:].max())
        print("近半年最大回撤日期",df["maximumDrawdown"][-120:].idxmax())
        return yearRtn
    
    def calcRtnByYear(self, df,rule="Y",):
        s = {}
        for i ,_df in df.resample(rule):
            _s = (1+_df["return"]).cumprod()
            if rule == "Y":
                colname = i.year
            else:
                colname = f"{i.year}{i.month:0>2d}"
            s[colname] = _s[-1] - 1 # 每年收益率
        return pd.Series(s)
            
    def calcSharpRatio(self,df):
        # 无风险年化收益率为2%
        # 除非无风险利率波动较大（如在新兴市场中一样），否则超额收益和原始收益的标准差将相似
  
        r = round(df['return'].mean()/df['return'].std()*np.sqrt(252),3)
        print("夏普率",r)
        # 减去无风险利率
        df["rtn"] = df["return"] - 0.02/252
        # 由日频率转化为年化夏普
        # https://www.zhihu.com/question/27264526 不同周期选择参考优劣参考
        r = round(df['rtn'].mean()/df['rtn'].std()*np.sqrt(252),3)
        print("夏普率扣除无风险收益后",r)
        

    @Decorator.loadData(path="data")
    def qryShiborData(self,**kawgrs):
        if "year" not in kawgrs:
        # 汇总
            total = pd.DataFrame(columns=["曲线名称","日期","3月","6月","1年","3年","5年","7年","10年","30年"])
            for year in range(2006,2023):
                _df = self.qryShiborData(year = year)
                _df['date'] = pd.to_datetime(_df["日期"], format='%Y-%m-%d')
                _df.set_index('date', inplace=True)
                total = total.append(_df)
            return total
        
        import akshare as ak
        year = kawgrs["year"]
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        bond_china_yield_df = ak.bond_china_yield(start_date=start_date, end_date=end_date)
        return bond_china_yield_df
    
  
    
if __name__ == '__main__':
    m = Mgr()
    stSymbols = m.queryST(dateTime=20220601)
    print(len(stSymbols))

  