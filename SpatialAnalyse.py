import geopandas as gpd
import glob
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import pyproj

"""
typhoon=r"D:\AIS_TEMP\Typhoon\Typhoon_point_2017.shp"
typhoon=gpd.read_file(typhoon)
columns=typhoon.columns
typhoon['WIND']=0
col=[]
for item in columns:
    if item.endswith("WIND"):
        col.append(item)
print(col)
typhoon['WIND']=typhoon[col].max(axis=1)
typhoon.crs = pyproj.CRS.from_user_input('EPSG:4326')
typhoon.to_crs(pyproj.CRS.from_user_input('EPSG:3857'), inplace=True)
path = r"D:\AIS_TEMP\Typhoon\Typhoon_point_2017_3857.shp"
typhoon.to_file(filename=path, driver='ESRI Shapefile', encoding='utf-8')

"""

COL_NAME="H_clu"
basepath=r"D:\AIS_TEMP\19";
file_list=glob.glob(os.path.join(basepath,"*,shiptype=ALL.shp"));
COLOR=['red','gray','blue','pink','yellow','orange','black']
count=0;
DATA=[]
for i in range(len(file_list)):
    item=file_list[i]
    data=gpd.read_file(item)
    data[COL_NAME]=data[COL_NAME].fillna(0);

    #data.crs = pyproj.CRS.from_user_input('EPSG:4326')
    #data.to_crs(pyproj.CRS.from_user_input('EPSG:3857'), inplace=True)
    #path = os.path.join(r"D:\AIS_TEMP\19", os.path.split(item)[1].split(".")[0] + "_3857.shp")
    #data.to_file(filename=path, driver='ESRI Shapefile', encoding='utf-8')



    values=data[COL_NAME].values;
    ci=np.percentile(values, (90));
    data=data[data[COL_NAME]>ci]
    data['window']=str(i+1)
    DATA.append(data)

DATA=pd.concat(DATA)
DATA=DATA.sort_values("window",ascending=True)

DATA=DATA.drop_duplicates(subset=['NAME','LON','LAT'],keep='last')
DATA.crs=pyproj.CRS.from_user_input('EPSG:4326')
legend_kwds = {
        'loc': 'lower center',
        'title': 'LEGEND',
        'shadow': True,
        'ncol':7,
        #'markerscale':9,
        #'fontsize':5

    }

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(color="white", edgecolor='0.5')
DATA.plot(column='window',ax=ax,legend=True,legend_kwds=legend_kwds)
plt.show()
DATA.to_crs(pyproj.CRS.from_user_input('EPSG:3857'),inplace=True)
path=os.path.join(r"D:\AIS_TEMP\21",COL_NAME+".shp")
DATA.to_file(filename=path, driver='ESRI Shapefile', encoding='utf-8')