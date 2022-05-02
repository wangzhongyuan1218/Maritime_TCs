import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import traceback
import math
import pyproj
def get_orient(geom):
    orient=[]
    for item in geom:
        if str(item).startswith('MULTILINESTRING'):
            cor=item[0].coords
            x1=cor[0][0]
            y1=cor[0][1]
            cor = item[-1].coords
            x2 = cor[1][0]
            y2 = cor[1][1]
        elif str(item).startswith("None"):
            orient.append(np.nan)
            continue
        else:
            cor=item.coords
            x1=cor[0][0]
            x2=cor[1][0]
            y1=cor[0][1]
            y2=cor[1][1]
        arr_0 = np.array([(x2 - x1), (y1 - y2)])
        arr_1 = np.array([(0 - 0), (1 - 0)])
        cos_value = (float(arr_0.dot(arr_1)) / (np.sqrt(arr_0.dot(arr_0)) * np.sqrt(arr_1.dot(arr_1))))
        orient.append(cos_value)
    return orient

def get_valid(geom):
    result=[]
    for item in geom:
        flag=1
        if str(item).startswith('MULTILINESTRING'):
            for line in item:
                cor = line.coords
                x1 = cor[0][0]
                x2 = cor[1][0]
                y1 = cor[0][1]
                y2 = cor[1][1]
                if (np.abs(x1 - x2) < 0.000001) & ((np.abs(y1 - y2) < 0.000001)):
                    print(x1)
                    print(y1)
                    flag=0
        elif str(item).startswith("None"):
            flag=0
        else:
            cor = item.coords
            x1 = cor[0][0]
            x2 = cor[1][0]
            y1 = cor[0][1]
            y2 = cor[1][1]
            if (np.abs(x1 - x2) < 0.000001) & ((np.abs(y1 - y2) < 0.000001)):
                flag = 0
                print(x1)
                print(y1)
        result.append(flag)
    return result

def difference(geom,yuwang):
    result=[]
    for i in range(len(geom)):
        item=geom[i]
        if item is None:
            print(yuwang[i])
        #flag=item.buffer(0)
        #result.append(flag)
    return result

path=r"D:\AIS_TEMP\6\20170101_part_0.shp"
#path=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017_3857.shp"
gdf=gpd.read_file(path)
print(len(gdf))
#rectangles=gpd.read_file(r"D:\AIS_TEMP\YUWANG\TEMP.shp")
gdf['valid']=difference(gdf['geometry'].values,gdf['MMSI'].values)

print(gdf)
#gdf['valid']=gdf['geometry'].apply(lambda x: x.is_simple)
#print(gdf.valid.values)
print("轨迹文件已读入")
rectangles=gpd.read_file(r"D:\AIS_TEMP\YUWANG\YUWANG3857.shp")
print("渔网文件已读入")

gdf['v']=gdf['geometry'].length
print("速度计算完成")
gdf['orient']=get_orient(gdf['geometry'].values)
print("方向计算完成")
temp=[]
geometry=[]
orient=[]
v=[]
MMSI=[]
ID=[]
for index,row in gdf.groupby("MMSI"):
    error_MMSI=[]
    try:
        temp=gpd.overlay(df1=rectangles,df2=row,how="intersection",keep_geom_type=False)
        temp=row
        MMSI.extend(temp.MMSI.values)
        geometry.extend(temp.geometry.values)
        v.extend(temp.v.values)
        orient.extend(temp.v.values)
        #ID.extend(temp.ID.values)
        if False in row['valid'].values:
            print(index)
    except:
        error_MMSI.append(index)
        print(row['valid'])
        print(str(index)+"出现问题")
"""
for index, row in gdf.groupby('MMSI'):
    try:
        temp=gpd.overlay(df1=rectangles,df2=row,how="intersection",keep_geom_type=False)
        MMSI.extend(temp.MMSI.values)
        geometry.extend(temp.geometry.values)
        v.extend(temp.v.values)
        orient.extend(temp.v.values)
        ID.extend(temp.ID.values)
    except:
        traceback.print_exc()
        print(str(index)+"出现问题")
"""
property=pd.DataFrame(MMSI,columns=['MMSI'])
property['v']=v
property['orient']=orient
property['ID']=ID
gdf=gpd.GeoDataFrame(property=property,geometry=geometry)
gdf=gpd.overlay(df1=rectangles,df2=gdf,how="intersection",keep_geom_type=False)

g=gdf.groupby('ID')

count=0
#ax=gdf.plot()

mean_intensity=[]
for k,v in g:
    mean_intensity.append((k,len(v),v['v'].mean(),np.nanmean(v['orient'].values)))

data=pd.DataFrame(mean_intensity,columns=['ID','Intensity','Mean_v','Mean_dir'])
print(data)
rectangles2=rectangles.merge(data,on='ID',how='inner')
rectangles2.crs = pyproj.CRS.from_user_input('EPSG:3857')  # 给输出的shp增加投影
rectangles2.to_file(r"D:\AIS_TEMP\Test1.shp", driver='ESRI Shapefile', encoding='utf-8')
