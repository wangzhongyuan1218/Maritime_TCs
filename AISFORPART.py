import os
import glob
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString,Point
from multiprocessing import Pool
import pyproj

name=['MMSI','a','Class_type','ReceiveTime','Lon','Lat','From','To','b']

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

    dataGroup = df.groupby('MMSI')
    # 构造数据
    tb = []
    geomList = []
    for name, group in dataGroup:
        # 分离出属性信息，取每组的第1行前5列作为数据属性
        # 把同一组的点打包到一个list中
        if len(group)<2:
            continue
        #temp=group.sort_values('ReceiveTime',ascending = True)
        temp=group
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
        id=str(id[0])
        from_ = [t for t in temp.From]
        from_ = str(from_[0])
        to = [t for t in temp.To]
        to = str(to[0])
        t1 = pd.Series([id,time,Lon,Lat,from_,to], index=["MMSI", "TIME",'Lon','Lat','From','To'])
        tb.append(t1)
        #tb.append(temp.iloc[0, :1])
        #print(tb)

    # 点转线
    geoDataFrame = gpd.GeoDataFrame(tb, geometry=geomList)
    geoDataFrame.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
    if geoDataFrame.size==0:
        print(despath+"  Empty!")
    else:
        geoDataFrame.to_file(despath, driver='ESRI Shapefile', encoding='utf-8')

    return geoDataFrame
if __name__ == '__main__':

    import shutil
    shutil.rmtree(r"D:\AIS_TEMP\3")

