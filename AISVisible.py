import os
import glob
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString,Point
from multiprocessing import Pool
import matplotlib.pyplot as plt
import matplotlib
import pyproj
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']

def read_dataframe(file):
    df = pd.read_csv(file,delimiter="~",names=name,low_memory=False)
    return df

def read_AIS(basepath,despath):
    file_list=glob.glob(os.path.join(basepath,"*.csv"))
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_dataframe, file_list)
    p.close()
    p.join()
    df = pd.concat(res, axis=0, ignore_index=True)
    df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
    df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
    df.dropna(subset=['MMSI', 'Lon', 'Lat'])
    df['Lon']=df['Lon'].apply(lambda x: x / 600000)
    df['Lat']=df['Lat'].apply(lambda x: x / 600000)

    dataGroup = df.groupby('MMSI')
    # 构造数据
    tb = []
    geomList = []
    for name, group in dataGroup:
        # 分离出属性信息，取每组的第1行前5列作为数据属性
        # 把同一组的点打包到一个list中
        if len(group)<2:
            continue
        temp=group.sort_values('ReceiveTime',ascending = True)
        xyList = [xy for xy in zip(temp.Lon, temp.Lat)]
        line = LineString(xyList)
        geomList.append(line)
        time= [t for t in temp.ReceiveTime]
        time=str(time)
        Lon = [t for t in temp.Lon]
        Lon = str(Lon)
        Lat = [t for t in temp.Lat]
        Lat = str(Lat)
        id= [t for t in temp.MMSI]
        id=str(id)
        t1 = pd.Series([id,time,Lon,Lat], index=["MMSI", "TIME",'Lon','Lat'])
        tb.append(t1)
        #tb.append(temp.iloc[0, :1])
        #print(tb)

    # 点转线
    geoDataFrame = gpd.GeoDataFrame(tb, geometry=geomList)
    geoDataFrame.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
    geoDataFrame.to_file(despath, driver='ESRI Shapefile', encoding='utf-8')

    return geoDataFrame
if __name__ == '__main__':
    """
    basepath=r"D:\AIS_2017\2017\dynamic\month_id=201707_7z\day_id=20170701\\"
    basepath="D:\wangzhongyuan\Test"
    df=read_AIS(basepath)
    print("finish")
    df.to_file(r'AISTEST.shp', driver='ESRI Shapefile',encoding='utf-8')
    """
    basepath=r"D:\AIS_2017\2017\dynamic\month_id="
    month=["201701","201702","201703","201704","201705","201706","201707_7z","201708_7z","201709_7z","201710","2017011","201712"]
    day=[31,28,31,30,31,30,31,31,30,31,30,31]
    for m in range(len(month)):
        for d in range(day[m]):
            path=""
            despath=''
            if d+1<10:
                path=basepath+month[m]+r"\day_id="+month[m]+"0"+str(d+1)
                despath=r"D:\wangzhongyuan\AIS-SHP\\day_id="+month[m]+"0"+str(d+1)+".shp"
            else:
                path = basepath + month[m] + r"\day_id=" + month[m]  + str(d + 1)
                despath = r"D:\wangzhongyuan\AIS-SHP\\day_id=" + month[m]  + str(d + 1) + ".shp"
            if os.path.exists(despath):
                print(despath)
                continue
            df=read_AIS(path,despath)
            print(despath)

