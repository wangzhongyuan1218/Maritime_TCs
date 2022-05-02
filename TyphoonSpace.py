import geopandas as gpd
import os
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import seaborn as sns
import glob
TYPHOON_GRID=r"D:\AIS_TEMP\Typhoon_context\\"
TYPHOON_DEMO=r"D:\AIS_TEMP\11"
SHIPTYPE=r"D:\AIS_TEMP\10\\"
c=0.5
window=[4,7,7]
#获取每期台风的影响的格网的ID
def getID_via_gpd(path):
    #path=os.path.join(TYPHOON_GRID,date+".shp")
    #data=gpd.read_file(path)
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
#window为最大分析的缓冲区，date为日期，ID为索引号
def get_via_ID(window,date,ID):
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date[6:8])
    date=datetime(year,month,day)
    day_del=window[0]
    lon_del = window[1]
    lat_del = window[2]
    temp_date = []

    for i in range(1, day_del + 1):
        temp_date.append(date)
        temp_date.append(date + timedelta(days=i))
        temp_date.append(date + timedelta(days=-i))
    temp_date = np.unique(temp_date)
    temp_date = np.sort(temp_date)
    temp_frame=[]
    date = []
    for item in temp_date:
        year=item.year
        month=item.month
        day=item.day
        path=os.path.join(TYPHOON_DEMO,'day_id='+str(year)+str(month).zfill(2)+str(day).zfill((2))+".csv")
        if os.path.exists(path):
            dataframe=pd.read_csv(path)
            #print(str(month) + "-" + str(day))
            temp_frame.append(dataframe)
            date.append(str(month) + "-" + str(day))
    date=np.array(date)
    SPEED=[]
    ORIENT=[]
    COUNT=[]
    for i in range(1,lon_del+1):
        win=[]
        win.append(i)
        win.append(i)
        speed=[]
        orient=[]
        count=[]
        temp_ID = getID_via_window(win, ID)
        for item in temp_frame:
            temp_data = item[item['ID'].isin(temp_ID)]
            if len(temp_data)==0:
                speed.append(0)
                orient.append(0)
                count.append(0)
                continue
            speed.append(np.nanmean(temp_data['speed'].values))
            orient.append(np.nanmean(temp_data['heading'].values))
            count.append(np.nansum(temp_data['count'].values))
        speed=np.array(speed)
        count=np.array(count)
        orient=np.array(orient)
        SPEED.append(speed)
        ORIENT.append(orient)
        COUNT.append(count)
    return SPEED,ORIENT,COUNT,date

def get_via_ID_shiptype(window,date,ID,shiptype):
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date[6:8])
    date=datetime(year,month,day)
    day_del=window[0]
    lon_del = window[1]
    lat_del = window[2]
    temp_date = []

    for i in range(1, day_del + 1):
        temp_date.append(date)
        temp_date.append(date + timedelta(days=i))
        temp_date.append(date + timedelta(days=-i))
    temp_date = np.unique(temp_date)
    temp_date = np.sort(temp_date)
    temp_frame=[]
    date = []
    for item in temp_date:
        year=item.year
        month=item.month
        day=item.day
        path=os.path.join(SHIPTYPE+str(shiptype),'day_id='+str(year)+str(month).zfill(2)+str(day).zfill((2))+"_"+str(shiptype)+".csv")
        if os.path.exists(path):
            dataframe=pd.read_csv(path)
            #print(str(month) + "-" + str(day))
            temp_frame.append(dataframe)
            date.append(str(month) + "-" + str(day))
    date=np.array(date)
    SPEED=[]
    ORIENT=[]
    COUNT=[]
    for i in range(1,lon_del+1):
        win=[]
        win.append(i)
        win.append(i)
        speed=[]
        orient=[]
        count=[]
        temp_ID = getID_via_window(win, ID)

        for item in temp_frame:
            temp_data = item[item['ID'].isin(temp_ID)]
            if len(temp_data)==0:
                speed.append(0)
                orient.append(0)
                count.append(0)
                continue
            speed.append(np.nanmean(temp_data['speed'].values))
            orient.append(np.nanmean(temp_data['heading'].values))
            count.append(np.nansum(temp_data['count'].values))

        speed=np.array(speed)

        count=np.array(count)
        orient=np.array(orient)
        SPEED.append(speed)
        ORIENT.append(orient)
        COUNT.append(count)
    return SPEED,ORIENT,COUNT,date

def F_yichang_orient(y):

    if len(y)==0:
        return np.array([-1])
    Q1, Q2 = np.percentile(y, [25, 75])
    QR = Q2 - Q1
    upper = Q2 + c * QR
    lower = Q1 - c * QR
    index = np.where((y < lower) | (y > upper))
    index = np.array(index)[0]
    index = index[(index != 0) ]
    index=index[index>4]
    if len(index)<1:
        index=np.array([-1])
    return index
def F_yichang_speed(y):

    if len(y)==0:
        return np.array([-1])
    Q1, Q2 = np.percentile(y, [25, 75])
    QR = Q2 - Q1
    upper = Q2 + c * QR
    lower = Q1 - c * QR
    index = np.where((y < lower) | (y > upper))
    index = np.array(index)[0]
    index = index[(index != 0) & (index!=len(index)-1)]
    #index=index[index>4]
    if len(index)<1:
        index=np.array([-1])
    return index


import matplotlib.pyplot as plt
def get_all():
   file_list=glob.glob(os.path.join(TYPHOON_GRID,"*.csv"))
   MEDIAN_SPEED=[]
   for item in file_list:
       print(item)
       ID=getID_via_gpd(item)
       date = os.path.split(item)[1].split(".")[0]

       SPEED, ORIENT, COUNT, date = get_via_ID(window, date, ID)

       median_speed=[]
       for i in range(0,len(SPEED)):
           y=SPEED[i]
           index=F_yichang_speed(y)
           median_speed.append(np.nanmean(index))
       MEDIAN_SPEED.append(median_speed)
   #np.save(r"D:\AIS_TEMP\7\median_temp.npy",MEDIAN_SPEED)
from scipy import stats
def checknorm(arr0):
    for i in range(0, arr0.shape[1]):
        arr = arr0[:, i]
        ii = np.argwhere(arr == -1)
        arr = np.delete(arr, ii, 0)
        u = arr.mean()  # 计算均值
        std = arr.std()  # 计算标准差
        print(u)
        print(std)
        result = stats.normaltest(arr)
        print(result)


if __name__ == '__main__':
    #get_all()
    file_list = glob.glob(os.path.join(TYPHOON_GRID, "*.csv"))

    for j in range(-1,256):
        MEDIAN_SPEED = []
        MEDIAN_ORIENT = []
        for item in file_list:
            ID = getID_via_gpd(item)
            date = os.path.split(item)[1].split(".")[0]
            SPEED, ORIENT, COUNT, date = get_via_ID_shiptype(window, date, ID,j)

            median_speed = []
            median_orient=[]
            for i in range(0,len(SPEED)):
                y = SPEED[i]
                index = F_yichang_speed(y)
                median_speed.append(np.nanmedian(index))
                y = ORIENT[i]
                index = F_yichang_orient(y)
                median_orient.append(np.nanmean(index))
            MEDIAN_SPEED.append(median_speed)
            MEDIAN_ORIENT.append(median_orient)
        MEDIAN_SPEED = np.array(MEDIAN_SPEED)
        MEDIAN_ORIENT=np.array(MEDIAN_ORIENT)
        print("shiptype:{0}".format(j))
        #checknorm(MEDIAN_SPEED)
        #checknorm(MEDIAN_ORIENT)
        #np.save(r"D:\AIS_TEMP\7\median_speed"+"_"+str(j)+".npy", MEDIAN_SPEED)
        #np.save(r"D:\AIS_TEMP\7\median_orient" + "_" + str(j) + ".npy", MEDIAN_ORIENT)