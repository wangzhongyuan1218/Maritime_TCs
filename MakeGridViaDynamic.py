import pandas as pd
import os
import numpy as np
import glob
import pyproj
import traceback
from multiprocessing import Pool
import time
import geopandas as gpd
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
despath=r"D:\AIS_TEMP\11"
AIS_TEMP12=r"D:\AIS_TEMP\12"
AIS_TEMP10=r"D:\AIS_TEMP\10"
AIS_TEMP9=r"D:\AIS_TEMP\9"
AIS_TEMP8=r"D:\AIS_TEMP\8"
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



def read_AIS(basepath,day):
    file_list=glob.glob(os.path.join(basepath,"*.csv"))
    if len(file_list)==0:
        return
    if os.path.exists(os.path.join(despath,day+".shp")):
        return
    df1 = pd.read_hdf(os.path.join(AIS_TEMP12, name + '.h5'))
    df1['SHIPTYPE'] = df1['SHIPTYPE'].fillna(-1).astype(int)
    df1['COUNTRYCODE'] = df1['COUNTRYCODE'].fillna(-1).astype(int)
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_dataframe, file_list)
    p.close()
    p.join()
    res=pd.concat(res)
    res=res.merge(df1,on='MMSI',how='left')

    trueHeading=[]
    speed=[]
    count=[]
    ID=[]
    trueHeading_t=[]
    course=[]
    for index,row in res.groupby('ID'):
        ID.append(index)
        trueHeading.append(np.nanmean(row['TrueHeading'].values-row['Course'].values))
        count.append(len(row))
        speed.append(np.nanmean(row['Speed'].values))
        trueHeading_t.append(np.nanmean(row['TrueHeading'].values))
        course.append(np.nanmean(row['Course'].values))
    shape_file_ori=gpd.read_file(r"D:\AIS_TEMP\YUWANG\YUWANG4326.shp")
    property=pd.DataFrame(ID,columns=['ID'])
    property['speed']=speed
    property['orient']=trueHeading
    property['count']=count
    property['course'] = course
    property['heading'] = trueHeading_t
    #print(res.columns)
    #geometry=shape_file.geometry
    shape_file=shape_file_ori.merge(property,on='ID',how='left')
    #shape_file['geometry']=geometry
    shape_file.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
    shape_file.to_file(os.path.join(despath,day+".shp"), driver='ESRI Shapefile', encoding='utf-8')
    print("汇总文件已输出")

    res['SHIPTYPE'] = res['SHIPTYPE'].fillna(-1).astype(int)
    res['COUNTRYCODE'] = res['COUNTRYCODE'].fillna(-1).astype(int)
    for index,row in res.groupby('SHIPTYPE'):
        path = os.path.join(AIS_TEMP10, str(index))
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, day + "_" + str(index) + ".csv")
        trueHeading = []
        speed = []
        count = []
        ID = []
        trueHeading_t = []
        course=[]
        for key,content in row.groupby("ID"):
            ID.append(key)
            trueHeading.append(np.nanmean(content['TrueHeading'].values - content['Course'].values))
            count.append(len(content))
            speed.append(np.nanmean(content['Speed'].values))
            trueHeading_t.append(np.nanmean(content['TrueHeading'].values))
            course.append(np.nanmean(content['Course'].values))
        property = pd.DataFrame(ID, columns=['ID'])
        property['speed'] = speed
        property['orient'] = trueHeading
        property['count'] = count
        property['course']=course
        property['heading']=trueHeading_t
        #property.to_hdf(path, mode='w',key='ID')
        property.to_csv(path, index=False)

    print("SHIPTYPE已输出")
    for index, row in res.groupby('COUNTRYCODE'):
        path = os.path.join(AIS_TEMP9, str(index))
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, day + "_" + str(index) + ".csv")
        trueHeading = []
        speed = []
        count = []
        ID = []
        trueHeading_t = []
        course=[]
        for key, content in row.groupby("ID"):
            ID.append(key)
            trueHeading.append(np.nanmean(content['TrueHeading'].values - content['Course'].values))
            count.append(len(content))
            speed.append(np.nanmean(content['Speed'].values))
            trueHeading_t.append(np.nanmean(content['TrueHeading'].values))
            course.append(np.nanmean(content['Course'].values))
        property = pd.DataFrame(ID, columns=['ID'])
        property['speed'] = speed
        property['orient'] = trueHeading
        property['count'] = count
        property['course'] = course
        property['heading'] = trueHeading_t
        property.to_csv(path,index=False)

    print("COUNTRYCODE已输出")

    for index,row in res.groupby('NavigationStatus'):
        path = os.path.join(AIS_TEMP8, str(index))
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, day + "_" + str(index) + ".csv")
        count = []
        ID = []
        for key, content in row.groupby("ID"):
            ID.append(key)
            count.append(len(content))
        property = pd.DataFrame(ID, columns=['ID'])
        property['count'] = count
        property.to_csv(path, index=False)
    print("航行状态已输出")


if __name__ == '__main__':
    basepath=r"D:\AIS_2017\2017\dynamic"
    #basepath=r"D:\AIS_TEMP\8"
    for root, dirs, files in os.walk(basepath):
        for name in dirs:
            file_list = glob.glob(os.path.join(os.path.join(root,name), "*.csv"))
            path=os.path.join(root,name)
            try:
                print(path + "--->开始")
                time_start = time.time()
                read_AIS(path,name)
                time_end=time.time()
                run_time=time_end-time_start
                print(path+"--->已完成,消耗："+str(run_time))
            except:
                traceback.print_exc()
                print(path+"*****************************************出现问题")


    print("AIS_2017已完成")