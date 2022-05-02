import pymssql #引入pymssql模块
import pandas as pd
from multiprocessing import Pool
import os
import glob
from sqlalchemy import create_engine
import pyproj
from pyproj import Transformer
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
import numpy as np
TABLE_NAME='Dynamic_AIS'
connection = create_engine(r"mssql+pymssql://sa:zhaixukun1997@127.0.0.1:1433/AIS_DATABASE?charset=utf8")


if __name__ == '__main__':
    #sql=' SELECT PosTime FROM Dynamic_AIS WHERE EXISTS (SELECT PosTime FROM Dynamic_AIS WHERE PosTime=1483267210.0)'

    #df = pd.read_sql_query(sql=sql, con=connection)  # 读取SQL数据库，并获得pandas数据帧。
    #print(df.PosTime)
    data=pd.read_csv("pandas_logs.csv")
    temp = pd.DataFrame(columns=['file', 'running_time'])
    b = {'file': 'TTfile', 'running_time': 'running_time'}
    temp = data.append(b, ignore_index=True)
    temp=temp[temp['file']!='file']
    print(temp)

