# -*- coding: utf-8 -*-
# @Time    : 2018/8/10 14:01
# @Author  : hc
# @Site    : 
# @File    : Decorator.py
# @Software: PyCharm
from functools import wraps
import os
import pandas as pd
from datetime import datetime
import csv
# from gevent import monkey; 
# monkey.patch_all()
def singleton(cls, *args, **kwargs):
    instance = {}  # 创建字典来保存实例

    def get_instance(*args, **kwargs):
        if cls not in instance:  # 若实例不存在则新建
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return get_instance

# 装饰器 对实例方法的首次加载
def firstLoad(func): # 装饰器不带函数的写法
    @wraps(func)
    def inner_wrapper(*args, **kwargs): # 被装饰的函数的参数
        # print (args,kwargs)
        _obj = args[0] # 实例对象
        attrname = func.__name__[3:]
        if not hasattr(_obj, attrname):
            setattr(_obj,attrname,{})
        symbol = kwargs["symbol"]
        if symbol not in getattr(_obj,attrname):
            getattr(_obj,attrname)[symbol] =  func(*args, **kwargs)
        return getattr(_obj,attrname)[symbol]
    return inner_wrapper

# 装饰器，优先加载静态文件
def loadData(*dargs, **dkargs):
    def outer(func,*args, **kwargs):
        @wraps(func)
        def inner(*args, **kwargs):
            # print(f"beg {kwargs}",datetime.now().time())
            
            nodeFileName = func.__name__[3:] # 构造文件夹名称
            excelName = f"{nodeFileName}"
            isRealTime = kwargs['isRealTime'] if "isRealTime" in kwargs else False
            parse_dates = kwargs['parse_dates'] if "parse_dates" in kwargs else -1
            excelNames = []
            for k,v in kwargs.items(): # 参数的键值对作为补充文件名
                if k == "isRealTime" or k=="df" or k == "parse_dates":
                    continue
                excelNames.append(k)
            excelNames.sort()
            for k in excelNames:
                excelName += f"_{k}[{str(kwargs[k])}]"
            co_filename = os.path.normcase(func.__code__.co_filename)
            # 定位到工作空间目录 workspace
            filePath = os.path.dirname(os.path.dirname(__file__))
            _paths = filePath.split("\\")

            _paths.append("data")

            if "path" in dkargs and dkargs["path"] == "data":
                # 装饰器传参 path：设置为"data".则读取data路径。用于可复用的数据
                dataPath =""
            else:
                # 获取函数代码所在的文件名称。用于构造读取静态文件的路径
                # 取函数代码所在文件名中 _ 分割的第二个关键字
                dataPath = co_filename.split("\\")[-1].split(".")[0].split("_")[0:1]
                dataPath = "_".join(dataPath)
                _paths.append(dataPath)
            _paths.append(nodeFileName)
            _paths.append(excelName+".csv")
            fileName = os.sep.join(_paths)  #
            path = os.path.dirname(fileName)
            if not os.path.exists(path):os.makedirs(path)
            if not os.path.exists(fileName) or isRealTime:
                print(func.__name__ + f"\033[32m开始生成数据[{fileName}]\033[0m")
                df =  func(fileName = fileName,*args,**kwargs )
                # df.to_excel(fileName, sheet_name="数据源")
                df.to_csv(fileName, encoding="UTF-8")
            print(func.__name__ + f"读取数据[{fileName}]")
            # df = pd.read_excel(fileName, sheet_name="数据源", index_col=0,engine="openpyxl")
            if parse_dates == -1:
                df = pd.read_csv(fileName, index_col=0)#注意解析csv异常 第一列作为索引
            else:
                df = pd.read_csv(fileName, index_col=0,parse_dates=parse_dates) #parse_dates尝试指定转化时间格式的列
            try:
                df.index =pd.to_datetime(df.index)
            except:
                pass
            return df
        return inner
    return outer