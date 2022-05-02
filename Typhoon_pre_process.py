import geopandas as gpd
import pandas as pd
import numpy as np
if __name__ == '__main__':
    point=gpd.read_file(r"D:\AIS_TEMP\Typhoon\Typhoon_point_2017.shp")
    tempLON=[]
    tempLAT=[]
    point=point.drop_duplicates(['SID','LON','LAT'])
    for name,value in point.groupby(['SID','month','day']):
        if len(value)<2:
            continue
        tempLON.append(np.max(value['LON'].values)-np.min(value['LON'].values))
        tempLAT.append(np.max(value['LAT'].values) - np.min(value['LAT'].values))
        if np.max(value['LON'].values)-np.min(value['LON'].values)==0:
            print("精度")
            print(name)
            print(len(value))
        if np.max(value['LAT'].values) - np.min(value['LAT'].values) == 0:
            print("纬度")
            print(name)
            print(len(value))
    print(np.mean(tempLON))
    print(tempLAT)
    print(np.mean(tempLAT))