import pandas as pd
import os
import glob
from multiprocessing import Pool
import numpy as np
import csv
import time
import traceback
import pyproj
import geopandas as gpd
from shapely.geometry import LineString


PortName=r"D:\ZXK\portCenter.csv"

dynamic_name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']
#获取地名
partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
part_lon=partPD.LON.values
part_lat=partPD.LAT.values
part_name=partPD.NAME.values

def read_dynamic_dataframe(file):
    df = pd.read_csv(file,delimiter="~",names=dynamic_name,low_memory=False)
    df = pd.DataFrame(df, columns=['MMSI', 'Lon', 'Lat','PosTime'])
    #df = df.dropna(subset=['MMSI', 'Lon', 'Lat','PosTime'])
    #解决脏数据，如果某条数据中的经纬度、接受和测量时间是空的，那就直接删掉。
    df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
    df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
    df['PosTime'] = pd.to_datetime(df['PosTime'], errors='coerce',unit='s', origin='unix')
    #df['ReceiveTime'] = pd.to_datetime(df['ReceiveTime'], errors='coerce',unit='s', origin='unix')
    df['MMSI'] = pd.to_numeric(df['MMSI'], errors='coerce')
    #df = df.dropna(subset=['MMSI', 'Lon', 'Lat', 'PosTime', 'ReceiveTime'])
    df = df.dropna(subset=['MMSI', 'Lon', 'Lat', 'PosTime'])
    df['MMSI']=df['MMSI'].astype(int)
    df['Lon']=df['Lon'].astype(int)
    df['Lat']=df['Lat'].astype(int)
    """
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
    """
    df['Lon']=df['Lon']/600000
    df['Lat'] = df['Lat'] / 600000

    return df

def read_Dynamic(file_list):
    #file_list = glob.glob(os.path.join(basepath, "*.csv"))
    if len(file_list) == 0:
        return
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_dynamic_dataframe, file_list)
    p.close()
    p.join()
    try:
        res = pd.concat(res)
    except:
        res=res
    res=res.sort_values(by='PosTime',ascending=True)
    res = res.drop_duplicates(subset=['MMSI'], keep='first', inplace=False)
    return res


def read_static_dataframe(path):
    df = pd.read_csv(path, delimiter="~", names=static_name, low_memory=False,quoting=csv.QUOTE_NONE)
    df = pd.DataFrame(df, columns=subset_static_name)
    df = df.dropna(subset=['MMSI', 'DESTINATION', 'ETA'])

    df['ETA'] = df['ETA'].apply(lambda x: '2017-' + x)
    df['ETA'] = pd.to_datetime(df['ETA'], errors='coerce')
    df = df.dropna(subset=['ETA'])
    return df

def read_static(file_list):
    #file_list = glob.glob(os.path.join(basepath, "*.csv"))
    if len(file_list) == 0:
        return
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_static_dataframe, file_list)
    p.close()
    p.join()
    try:
        res = pd.concat(res)
    except:
        res=res
    res = res.drop_duplicates(subset=['MMSI', 'DESTINATION', 'ETA'], keep='last', inplace=False)
    return res


def get_from(x):
    temp = (x['Lon'] - part_lon) * (x['Lon'] - part_lon) + (x['Lat'] - part_lat) * (x['Lat'] - part_lat)
    min = np.argmin(temp)
    return part_name[min],part_lon[min],part_lat[min]


def to_shapefile(dataframe,shapefile,csv_file):
    # 数据预处理
    dataframe = pd.DataFrame(dataframe, columns=['MMSI', 'LON', 'LAT', 'Lat', 'Lon', 'DESTINATION','SHIPTYPE','COUNTRYCODE','PosTime','ETA'])
    dataframe = dataframe[dataframe['LON'] < 180]
    dataframe = dataframe[dataframe['Lon'] < 180]
    dataframe = dataframe[dataframe['LAT'] < 90]
    dataframe = dataframe[dataframe['Lat'] < 90]
    dataframe[['FROM', 'Lon', 'Lat']] = dataframe.apply(get_from, axis=1, result_type="expand")

    dataframe = dataframe.set_index(keys=['MMSI'])
    dataframe.to_csv(csv_file)
    dataframe['count'] = 0
    df = dataframe.groupby(["FROM", 'DESTINATION', 'LON', 'LAT', 'Lon', 'Lat','SHIPTYPE']).count()
    df = pd.DataFrame(df)

    df = df.reset_index()
    df = pd.DataFrame(df, columns=['FROM', 'DESTINATION','SHIPTYPE','count','Lon', 'Lat', 'LON', 'LAT'])

    geom_list = []
    for index, row in df.iterrows():
        line = LineString([(row['Lon'], row['Lat']), (row['LON'], row['LAT'])])
        geom_list.append(line)
    df.to_csv(shapefile+".csv")
    #df['PosTime'] = df['PosTime'].apply(str)
    #df['ETA'] = df['ETA'].apply(str)
    geodata = gpd.GeoDataFrame(df, geometry=geom_list)
    geodata.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
    geodata.to_file(filename=shapefile, driver='ESRI Shapefile', encoding='utf-8')





def bulk_process(month):
    basepath1 = r"D:\AIS_2017\2017\static\month_id=201701_7z"
    basepath2 = r"D:\AIS_2017\2017\dynamic\month_id=201701"
    shp_path = r"D:\ZXK\STATIC_NETWORK\January_simple_shiptype.shp"
    csv_path = r'D:\ZXK\STATIC_NETWORK\January_static_network_shiptype.csv'
    monthpath = r'D:\ZXK\STATIC_NETWORK\January_shiptype.csv'

    MONTH=['January','Feburary','March','April','May','June','July','August','Septemper','October','November','December']
    basepath1 = r"D:\AIS_2017\2017\static\month_id=2017{0}_7z".format(str(month).zfill(2))
    basepath2 = r"D:\AIS_2017\2017\dynamic\month_id=2017{0}".format(str(month).zfill(2))
    shp_path = r"D:\AIS_TEMP\15\{0}_simple_shiptype.shp".format(MONTH[month-1])
    csv_path = r'D:\AIS_TEMP\15\{0}_static_network_shiptype.csv'.format(MONTH[month-1])
    monthpath = r'D:\AIS_TEMP\15\{0}_shiptype.csv'.format(MONTH[month-1])

    static_res = []
    for root, dirs, files in os.walk(basepath1):
        for name in dirs:
            file_list = glob.glob(os.path.join(os.path.join(root, name), "*.csv"))
            path = os.path.join(root, name)
            try:
                print(path + "--->开始")
                time_start = time.time()
                res = read_static(file_list)
                static_res.append(res)
                time_end = time.time()
                run_time = time_end - time_start
                print(path + "--->已完成,消耗：" + str(run_time))
            except:
                traceback.print_exc()
                print(path + "*****************************************出现问题")

    dynamic_res = []
    for root, dirs, files in os.walk(basepath2):
        for name in dirs:
            file_list = glob.glob(os.path.join(os.path.join(root, name), "*.csv"))

            path = os.path.join(root, name)
            try:
                print(path + "--->开始")
                time_start = time.time()
                res = read_Dynamic(file_list)
                dynamic_res.append(res)
                time_end = time.time()
                run_time = time_end - time_start
                print(path + "--->已完成,消耗：" + str(run_time))
            except:
                traceback.print_exc()
                print(path + "*****************************************出现问题")

    df_st = pd.concat(static_res)
    df_st = df_st.drop_duplicates(subset=['MMSI', 'DESTINATION', 'ETA'], keep='last', inplace=False)
    df = df_st.set_index(keys=['MMSI'])

    df_dy = pd.concat(dynamic_res)
    df = df_dy.set_index(keys=['MMSI'])

    df = pd.merge(df_st, partPD, how='inner', left_on='DESTINATION', right_on='NAME')
    df = pd.merge(df, df_dy, how='inner', left_on='MMSI', right_on='MMSI')
    df = df[df['PosTime'] < df['ETA']]
    df = df.set_index(keys=['MMSI'])
    df.to_csv(monthpath)
    to_shapefile(df, shp_path, csv_path)

if __name__ == '__main__':
    for i in range(1,13):
        bulk_process(i)



