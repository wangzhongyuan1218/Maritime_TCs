import pymssql #引入pymssql模块
import traceback
import time
import pandas as pd

from multiprocessing import Pool
import os
import glob
from sqlalchemy import create_engine
import pyproj
from pyproj import Transformer
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
import numpy as np
import shutil
TABLE_NAME='Dynamic_201701'
TEMP_PATH=r"D:\AIS_TEMP\1"#存储投影信息
TMEP2_PATH=r"D:\AIS_TEMP\2"#存储唯一MMSI号信息
connect = create_engine(r"mssql+pymssql://sa:zhaixukun1997@127.0.0.1:1433/AIS_DATABASE?charset=utf8")
tf = Transformer.from_crs(4326, 3857)



def is_exist(logs,file):
    if os.path.exists(logs):
        data=pd.read_csv(logs)
        data=data[data['file']==file]
        if len(data)>0:
            #print(file+"-->已经存在")
            return True
        else:
            return False
    else:
        return False
def project(lon,lat):
    lon=lon/600000
    lat=lat/600000
    # 取一个经纬度进行转换，并设为基准值，纬度是36.649这个， 经度是117.022
    utm_x, utm_y = tf.transform(lat, lon)
    if np.isinf(utm_x) or np.isinf(utm_y):
        utm_x=np.nan
        utm_y=np.nan
    return utm_x,utm_y

def getBulkInsertScript(table,csvpath):
    script="BULK insert {0} from \'{1}\' WITH(FIRSTROW = 2,FIELDTERMINATOR = ',',ROWTERMINATOR = '\\n', TABLOCK)".format(table,csvpath)
    #print(script)
    return script

def read_dataframe(file):
    temp_name = file.split("\\")
    temp_name = temp_name[-2] + "_" + temp_name[-1]
    if os.path.exists(os.path.join(TEMP_PATH,temp_name)):
        return
    start_time=time.time()
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

    #地图投影
    pd_X = []
    pd_Y = []
    for i in range(len(df.Lon.values)):
        x1, y1 = project(df.Lon.values[i], df.Lat.values[i])
        pd_X.append(x1)
        pd_Y.append(y1)
    df['X'] = pd_X
    df['Y'] = pd_Y
    #print(df.columns)
    df = df.dropna(subset=['X', 'Y'])
    #print("开始写入数据库")
    #df.to_sql(name=TABLE_NAME, con=connect, if_exists='append', index=False)
    df.to_csv(os.path.join(TEMP_PATH,temp_name),index=False)
    MMSI=np.unique(df['MMSI'].values)
    np.save(os.path.join(TMEP2_PATH,temp_name),MMSI)
    end_time=time.time()
    """
    while(True):
        try:
            run_log("pandas_logs.csv",file,end_time-start_time);
            break;
        except:
            continue;
    """
    return df
def BatchInput(path):
    while(True):
        try:
            if is_exist("Database_logs.csv",path):

                return
            else:
                break
        except:
            continue

    start_time=time.time()
    #conn = pymssql.connect('127.0.0.1:1433', 'sa', 'zhaixukun1997', 'AIS_DATABASE')
    #cursor = conn.cursor()
    #script=getBulkInsertScript(TABLE_NAME, csvpath=path)

    #cursor.execute(script)
    #conn.commit()
    #os.remove(path)
    shutil.move(path,TMEP2_PATH)
    #conn.close()
    end_time=time.time()
    """
    while(True):
        try:
            run_log("Database_logs.csv",path,end_time-start_time)
            break
        except:
            continue
    """
def read_AIS(basepath):

    file_list=glob.glob(os.path.join(basepath,"*.csv"))
    if len(file_list)==0:
        return
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_dataframe, file_list)
    p.close()
    p.join()

    print(basepath+"---投影文件已生成")
    """
    file_list = glob.glob(os.path.join(TEMP_PATH, "*.csv"))
    if len(file_list)==0:
        return
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(BatchInput, file_list)
    p.close()
    p.join()
    print(basepath + "--->数据库已输入")
    """

def run_log(logs,file,running_time):
    b = {'file': file, 'running_time': running_time}
    temp = pd.DataFrame(columns=['file', 'running_time'])
    temp=temp.append(b,ignore_index=True)
    temp.to_csv(logs,mode='a',index=False)


if __name__ == '__main__':
    basepath=r"D:\AIS_2017\2017\dynamic"
    #basepath=r"D:\AIS_TEMP"
    for root, dirs, files in os.walk(basepath):
        for name in dirs:
            file_list = glob.glob(os.path.join(os.path.join(root,name), "*.csv"))
            path=os.path.join(root,name)
            try:
                print(path + "--->开始")
                time_start = time.time()
                read_AIS(path)
                time_end=time.time()
                run_time=time_end-time_start
                print(path+"--->已完成,消耗："+str(run_time))
            except:
                traceback.print_exc()
                print(path+"*****************************************出现问题")


    print("AIS_2017已完成")