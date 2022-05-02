import geopandas as gpd
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
import pyproj

import matplotlib as mpl
import pyproj
cmp = mpl.colors.ListedColormap(['b','r','g'])
"""
legend_kwds = {
        'loc': 'lower center',
        'title': 'LEGEND',
        'shadow': True,
        'ncol':7,
        #'markerscale':9,
        #'fontsize':5

    }
cmap = mpl.cm.get_cmap('OrRd')

basepath=r"D:\AIS_TEMP\21\Moran"
file_list=glob.glob(os.path.join(basepath,"*.shp"))
for item in file_list:
    data=gpd.read_file(item)
    #data.sort_values('Gi_Bin',ascending=True,inplace=True)
    #data['Gi_Bin']=data['Gi_Bin'].apply(str)
    data.crs=pyproj.CRS.from_user_input('EPSG:3857')
    data.to_crs(pyproj.CRS.from_user_input('EPSG:4326'),inplace=True)
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(color="white", edgecolor='0.5')
    data.plot(column='COType',ax=ax,legend=True,legend_kwds=legend_kwds,cmap=cmap)
    plt.title(os.path.split(item)[1])
    plt.show()
"""

trajectory=gpd.read_file(r"D:\AIS_TEMP\15\April_simple_shiptype.shp")
trajectory=trajectory.drop_duplicates(subset=['FROM','DESTINATIO'],keep='first')
COLUMN='H'
import numpy as np
basepath=r"D:\AIS_TEMP\19"
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(color="white", edgecolor='0.5')
data=gpd.read_file(os.path.join(basepath,"window=7,shiptype=ALL.shp"))
data.crs= pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
data1=data.to_crs(pyproj.CRS.from_user_input('EPSG:4326') )
moran=gpd.read_file(r"D:\AIS_TEMP\21\HotPoint\ALL_H.shp")
moran['Gi_Bin']=moran['Gi_Bin'].apply(lambda x: 'not' if x==0 else('cold' if x<0 else 'hot'))
data=moran
data.crs= pyproj.CRS.from_user_input('EPSG:3857')  # 给输出的shp增加投影
data=data.to_crs(pyproj.CRS.from_user_input('EPSG:4326') )
#data['H'] = (data['H']-data['H'].mean())/data['H'].std()
#data['H'] = (data['H']-data['H'].min())/(data['H'].max()-data['H'].min())
values=data[COLUMN].values

Q1=np.percentile(values,25)
Q2=np.percentile(values,50)
Q3=np.percentile(values,75)
Q4=np.percentile(values,95)
print("四分位数")
print(np.min(values))
print(Q1)
print(Q2)
print(Q3)
print(Q4)
print(np.max(values))
data['VIS']=data[COLUMN].apply(lambda x: 4 if x>Q4 else (3 if x> Q3 else (2 if x>Q2 else(1 if x>Q1 else 0))))


for index,row in data.groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))

data=data.sort_values(COLUMN,ascending=False);
trajectory.plot(ax=ax,color='gray',linewidth=0.1,alpha=0.1)
data[data['VIS']==4].plot(color='red', markersize=25,ax=ax,marker='.')
#data[data['VIS']==4].plot(column='Gi_Bin', markersize=25,ax=ax,marker='.',legend=True,cmap=cmp)
plt.title("Q4")
plt.show()
print("Q4")
for index,row in data[data['VIS']==4].groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))



#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(color="white", edgecolor='0.5')
#data=data.sort_values(COLUMN,ascending=False);
trajectory.plot(ax=ax,color='gray',linewidth=0.1,alpha=0.1)
data[data['VIS']==3].plot(color='yellow', markersize=25,ax=ax,marker='.')
#data[data['VIS']>=3].plot(column='Gi_Bin', markersize=25,ax=ax,marker='.',legend=True,cmap=cmp)
plt.title("Q3")
plt.show()
print("Q3")
for index,row in data[data['VIS']>=3].groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))
#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(color="white", edgecolor='0.5')
#data=data.sort_values(COLUMN,ascending=False);
trajectory.plot(ax=ax,color='gray',linewidth=0.1,alpha=0.1)
data[data['VIS']==2].plot(color='black', markersize=25,ax=ax,marker='.')
#data[data['VIS']==2].plot(column='Gi_Bin', markersize=25,ax=ax,marker='.',legend=True,cmap=cmp)
plt.title("Q2")
plt.show()
print("Q2")
for index,row in data[data['VIS']==2].groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))

#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(color="white", edgecolor='0.5')
#data=data.sort_values(COLUMN,ascending=False);
trajectory.plot(ax=ax,color='gray',linewidth=0.1,alpha=0.1)
data[data['VIS']==1].plot(color='green', markersize=25,ax=ax,marker='.')
#data[data['VIS']==1].plot(column='Gi_Bin', markersize=25,ax=ax,marker='.',legend=True,cmap=cmp)
plt.title("Q1")
plt.show()
print("Q1")
for index,row in data[data['VIS']==1].groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))




ax = world.plot(color="white", edgecolor='0.5')
#data=data.sort_values(COLUMN,ascending=False);
trajectory.plot(ax=ax,color='gray',linewidth=0.1,alpha=0.1)
data[data['VIS']==0].plot(color='blue', markersize=25,ax=ax,marker='.',legend=True)
#data[data['VIS']==0].plot(column='Gi_Bin', markersize=25,ax=ax,marker='.',legend=True,cmap=cmp)
plt.title("Q0")
plt.show()
print("Q0")
for index,row in data[data['VIS']==0].groupby("Gi_Bin"):
    print("hot {0}, lon_mean={1},lat_mean={2}".format(index,np.nanmean(row['geometry'].x),np.nanmean(row['geometry'].y)))



data=data1
ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F1",ax=ax,marker=".",legend=True)
plt.title("F1")
print(len(data[data['F1']>0]))
plt.show()

ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F2",ax=ax,marker=".",legend=True)
plt.title("F2")
print(len(data[data['F2']>0]))
plt.show()

ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F3",ax=ax,marker=".",legend=True)
plt.title("F3")
print(len(data[data['F3']>0]))
plt.show()

ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F4",ax=ax,marker=".",legend=True)
plt.title("F4")
print(len(data[data['F4']>0]))
plt.show()

ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F5",ax=ax,marker=".",legend=True)
plt.title("F5")
print(len(data[data['F5']>0]))
plt.show()

ax = world.plot(color="white", edgecolor='0.5')
data.plot(column="F6",ax=ax,marker=".",legend=True)
plt.title("F6")
print(len(data[data['F6']>0]))
plt.show()


typhoon=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp"
typhoon=gpd.read_file(typhoon)
columns=typhoon.columns
typhoon['WIND']=0
col=[]
for item in columns:
    if item.endswith("WIND"):
        col.append(item)
print(col)
typhoon['WIND']=typhoon[col].max(axis=1)


TEMP_14=r"D:\AIS_TEMP\14"
Tyhphoon_sid=[]
Tyhphoon_name=[]
Typhoon_grade=[]

for index, row in typhoon.groupby("SID"):
    speed=row['WIND'].values
    speed=speed*1852/3600
    max_speed=np.max(speed)
    Tyhphoon_name.append(row['NAME'].values[0])
    if max_speed>51:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("Super TY")
    elif max_speed>41.5:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("STY")
    elif max_speed>32.7:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TY")
    elif max_speed>24.5:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("STS")

    elif max_speed>17.2:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TS")
    else:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TD")
import pandas as pd
TYPHOON_GRADE=pd.DataFrame(Tyhphoon_sid,columns=['SID']);
TYPHOON_GRADE['grade']=Typhoon_grade;
for index,row in TYPHOON_GRADE.groupby("grade"):
    print(index)
    print(len(row))
typhoon=typhoon.merge(TYPHOON_GRADE,how="left",on='SID')
ax = world.plot(color="white", edgecolor='0.5')
data.plot(ax=ax,marker=".",legend=True,markersize=2,color='pink')
typhoon.plot(ax=ax,column='grade',legend=True,cmap='magma')
plt.show()


PortName=r"D:\ZXK\portCenter.csv"

dynamic_name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']
#获取地名
partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
print("包含港口数")
print(len(partPD))
partPD_ini=partPD