import glob
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import os
from multiprocessing import Pool
#获取每期台风的影响的格网的ID
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']
def getID_via_gpd(path):
    data=pd.read_csv(path)
    data=data[data['COUNT']>0]
    return data['ID'].values

def getID_via_window(window,ID):
    temp_ID = []
    lon_del = window[0]
    lat_del = window[1]
    for item in ID:
        temp_ID.append(item)
        for i in range(1, lon_del + 1):
            temp_ID.append(item + i)
            temp_ID.append(item - i)
        for i in range(1, lat_del + 1):
            temp_ID.append(item + i * 360)
            temp_ID.append(item - i * 360)
    temp_ID = np.unique(temp_ID)
    return temp_ID

def get_ID(x):
    Lat=x['Lat']
    Lon=x['Lon']
    m=int(Lat+90)
    n=int(Lon+180)
    return n+m*360

def read_dataframe(file):
    temp_name = file.split("\\")
    temp_name = temp_name[-2] + "_" + temp_name[-1]
    df = pd.read_csv(file,delimiter="~",names=name,low_memory=False)
    #解决脏数据，如果某条数据中的经纬度、接受和测量时间是空的，那就直接删掉。
    df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
    df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
    df['PosTime'] = pd.to_datetime(df['PosTime'], errors='coerce',unit='s', origin='unix')
    df['ReceiveTime'] = pd.to_datetime(df['ReceiveTime'], errors='coerce',unit='s', origin='unix')
    df['MMSI'] = pd.to_numeric(df['MMSI'], errors='coerce')
    df = df.dropna(subset=['MMSI', 'Lon', 'Lat', 'PosTime', 'ReceiveTime'])
    df['MMSI']=df['MMSI'].astype(int)
    df['Lon']=df['Lon'].astype(int)
    df['Lat']=df['Lat'].astype(int)

    #保证剩下的字段中，不满足条件的，设置为nan，
    df['Course'] = pd.to_numeric(df['Course'], errors='coerce')
    df['NavigationStatus'] = pd.to_numeric(df['NavigationStatus'], errors='coerce')
    df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce')
    df['TrueHeading'] = pd.to_numeric(df['TrueHeading'], errors='coerce')
    df['Accuracy'] = pd.to_numeric(df['Accuracy'], errors='coerce')
    df['ROT'] = pd.to_numeric(df['ROT'], errors='coerce')
    # 为了保证可以进入数据库中，将nan处理为永远不可能发生的-1，
    df['Course']=df['Course'].fillna(-1).astype(int)
    df['TrueHeading']=df['TrueHeading'].fillna(-1).astype(int)
    df['Speed']=df['Speed'].fillna(-1).astype(int)
    df['NavigationStatus']=df['NavigationStatus'].fillna(-1).astype(int)
    df['Accuracy']=df['Accuracy'].fillna(-1).astype(int)
    df['ROT']=df['ROT'].fillna(-1).astype(int)
    df['Lon']=df['Lon']/600000
    df['Lat'] = df['Lat'] / 600000
    df['Course'] = df['Course'] / 10
    df=df[(df['Lon']<180) & (df['Lon']>-180)]
    df = df[(df['Lat'] < 90) & (df['Lat'] > -90)]
    df['ID']=df.apply(get_ID,axis=1)
    return df
def get_dynamic_file(date):
    basepath=r"D:\AIS_2017\2017\dynamic"
    month=date[0:6]
    basepath=basepath+r"\month_id="+month
    RES=[]
    for root, dirs, files in os.walk(basepath):
        for name in dirs:
            if name.split("=")[1]==date:
                file_list = glob.glob(os.path.join(os.path.join(root,name), "*.csv"))
                if len(file_list) == 0:
                    continue
                thread_num = len(file_list)
                p = Pool(thread_num)
                res = p.map(read_dataframe, file_list)
                p.close()
                p.join()
                res = pd.concat(res)
                return res

    return RES
PortName = r"D:\ZXK\portCenter.csv"
partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
part_name=partPD.NAME.values
part_lon=partPD.LON.values
part_lat=partPD.LAT.values
def get_from(x):
    temp = (x['Lon'] - part_lon) * (x['Lon'] - part_lon) + (x['Lat'] - part_lat) * (x['Lat'] - part_lat)
    min = np.argmin(temp)
    return part_name[min],part_lon[min],part_lat[min]

import csv
def read_static_dataframe(path):
    df = pd.read_csv(path, delimiter="~", names=static_name, low_memory=False,quoting=csv.QUOTE_NONE)
    df = pd.DataFrame(df, columns=subset_static_name)
    df = df.dropna(subset=['MMSI', 'SHIPTYPE'])
    df = df.drop_duplicates(subset=['MMSI', 'SHIPTYPE'], keep='First', inplace=False)
    return df
def get_static_file(date):
    month = date[0:6]
    RES = []
    basepath = r"D:\AIS_2017\2017\static"
    basepath=basepath + r"\month_id=" + month + "_7z"
    for root, dirs, files in os.walk(basepath):
        for name in dirs:
            if name.split("=")[1] == date:
                file_list = glob.glob(os.path.join(os.path.join(root, name), "*.csv"))
                if len(file_list) == 0:
                    return
                thread_num = len(file_list)
                p = Pool(thread_num)
                res = p.map(read_static_dataframe, file_list)
                p.close()
                p.join()
                res = pd.concat(res)
                RES.append(res)
    if len(RES) == 1:
        RES = RES[0]
    elif len(RES)==0:
        return None
    else:
        RES = pd.concat(RES)
        RES = RES.drop_duplicates(subset=['MMSI', 'SHIPTYPE'], keep='last', inplace=False)
    return RES

if __name__ == '__main__':
    NETWORK=r"D:\AIS_TEMP\STATIC_NETWORK"

    MONTH=['January','Feburary','March','April','May','June','July','August','Septemper','October','November','December']
    SHIPTYPE_COUNTRY=r"D:\AIS_TEMP\12"
    TYPHOON_CONTEXT=r"D:\AIS_TEMP\Typhoon_context"
    filelist=glob.glob(os.path.join(TYPHOON_CONTEXT,'*.csv'))
    MONTH_DATAFRAME=[]
    for item in MONTH:
        month_path = os.path.join(NETWORK, item + '.csv')
        dataframe = pd.read_csv(month_path)
        dataframe = dataframe[dataframe['LON'] < 180]
        dataframe = dataframe[dataframe['Lon'] < 180]
        dataframe = dataframe[dataframe['LAT'] < 90]
        dataframe = dataframe[dataframe['Lat'] < 90]
        dataframe[['FROM', 'Lon', 'Lat']] = dataframe.apply(get_from, axis=1, result_type="expand")
        MONTH_DATAFRAME.append(dataframe)
        print(item)
        print("计算结束")
    for item in filelist:
        print(item)
        ID=getID_via_gpd(item)
        ID1=getID_via_window([1,1],ID)
        ID2 = getID_via_window([2, 2], ID)
        ID3 = getID_via_window([3, 3], ID)
        ID4 = getID_via_window([4, 4], ID)
        ID5 = getID_via_window([5, 5], ID)
        ID6 = getID_via_window([6, 6], ID)
        ID7 = getID_via_window([7, 7], ID)
        date=os.path.split(item)[1].split('.')[0]
        print("ID号检索结束")
        path = os.path.join(SHIPTYPE_COUNTRY, "day_id=" + str(date) + ".h5")
        shiptype = pd.read_hdf(path, key="MMSI")
        print("静态检索(船舶类型)结束")

        month = int(date[4:6])
        day =int(date[6:8])
        """
        if month<8:
            continue
        if (month==8) & (day<15):
            continue
        """
        print(month)
        dataframe=MONTH_DATAFRAME[month-1]
        print("起点终点计算结束")


        RES=get_dynamic_file(date)
        print("动态数据读取结束")

        RES7 = RES[RES['ID'].isin(ID7)]
        RES6 = RES7[RES7['ID'].isin(ID6)]
        RES5 = RES6[RES6['ID'].isin(ID5)]
        RES4 = RES5[RES5['ID'].isin(ID4)]
        RES3 = RES4[RES4['ID'].isin(ID3)]
        RES2 = RES3[RES3['ID'].isin(ID2)]
        RES1 = RES2[RES2['ID'].isin(ID1)]
        print("动态数据检索结束")

        MMSI1 = RES1.MMSI.values
        MMSI2 = RES2.MMSI.values
        MMSI3 = RES3.MMSI.values
        MMSI4 = RES4.MMSI.values
        MMSI5 = RES5.MMSI.values
        MMSI6 = RES6.MMSI.values
        MMSI7 = RES7.MMSI.values
        print("动态数据MMSI检索结束")


        df=dataframe
        df1 = df[df['MMSI'].isin(MMSI1)]
        df2 = df[df['MMSI'].isin(MMSI2)]
        df3 = df[df['MMSI'].isin(MMSI3)]
        df4 = df[df['MMSI'].isin(MMSI4)]
        df5 = df[df['MMSI'].isin(MMSI5)]
        df6 = df[df['MMSI'].isin(MMSI6)]
        df7 = df[df['MMSI'].isin(MMSI7)]
        print(df1)
        #好的，现在已经得到哪些航线受到影响了，下面要求这些航线对应那种类型
        print("网络检索结束")
        s1 = df1.merge(shiptype, on='MMSI', how='inner')
        s2 = df2.merge(shiptype, on='MMSI', how='inner')
        s3 = df3.merge(shiptype, on='MMSI', how='inner')
        s4 = df4.merge(shiptype, on='MMSI', how='inner')
        s5 = df5.merge(shiptype, on='MMSI', how='inner')
        s6 = df6.merge(shiptype, on='MMSI', how='inner')
        s7 = df7.merge(shiptype, on='MMSI', how='inner')
        print("拼接结束")
        s1['window']=1
        s2['window'] = 2
        s3['window'] = 3
        s4['window'] = 4
        s5['window'] = 5
        s6['window'] = 6
        s7['window'] = 7
        s1=pd.concat([s1,s2,s3,s4,s5,s6,s7])
        path=r"D:\AIS_TEMP\13"
        path=os.path.join(path,date+".csv")
        s1.to_csv(path,index=False)
