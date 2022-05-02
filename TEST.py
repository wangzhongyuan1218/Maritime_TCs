import geopandas as gpd
import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
"""
TEMP_14=r"D:\AIS_TEMP\19"
file_list=glob.glob(os.path.join(TEMP_14,'*.shp'))
for item in file_list:
    name=os.path.split(item)[1]
    if not name.startswith("window=7"):
        continue
    geodata=gpd.read_file(item)
    geodata=geodata.replace([np.inf, -np.inf], np.nan)
    geodata=geodata.fillna(0)
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax=world.plot(color="white",edgecolor='0.5')
    geodata.plot(column='H_T_DELAY',scheme="NaturalBreaks",cmap='OrRd',legend=True,ax=ax)
    plt.title(name)
    plt.show()

"""
"""
path="D:\AIS_TEMP\Typhoon\IBTrACS.ALL.list.v04r00.lines\lines.csv"

dataframe=pd.read_csv(path)
print(dataframe)
count=[]
year=[]
for index,row in dataframe.groupby('year'):
    print(index)
    if index<2001:
        continue
    year.append(index)
    sid=row.SID.values
    sid=np.unique(sid)
    count.append(len(sid))

plt.plot(year,count)
plt.show()
"""

TEMP_14=r"D:\AIS_TEMP\19"
file_list=glob.glob(os.path.join(TEMP_14,'*.csv'))
NUM=[]
for item in file_list:
    name=os.path.split(item)[1]
    if not name.startswith("window=7"):
        continue
    geodata=pd.read_csv(item)
    geodata=geodata.replace([np.inf, -np.inf], np.nan)
    geodata=geodata.fillna(0)
    H=geodata.sort_values('H_F_DELAY',ascending=False)
    H=H.head(4)
    values=H.NAME.values
    name=name.split("=")[-1].split(".")[0]
    str="{4}:1.{0};2.{1};3.{2};4.{3}".format(values[0],values[1],values[2],values[3],name)
    print(str)
    NUM.append(H.H_F_DELAY.values)

for i in range(1,5):
    print(np.nanmean(NUM[i]/NUM[0]))


from sklearn import linear_model
clf = linear_model.LinearRegression()
dataframe=pd.DataFrame(NUM[0],columns=['allship'])
dataframe['cargo']=NUM[1]
dataframe['fishing']=NUM[2]
dataframe['passenger']=NUM[3]
dataframe['tanker']=NUM[4]
x=dataframe[['cargo','fishing','passenger','tanker']]
y=dataframe['allship']
clf.fit(x,y)
regress_coefs = clf.coef_
regress_intercept = clf.intercept_
print(regress_coefs)
print(regress_intercept)
corr=dataframe.corr('spearman')
print(corr)

from sklearn import metrics
print(np.sqrt(metrics.mean_squared_error(NUM[0], NUM[1])))
print(np.sqrt(metrics.mean_squared_error(NUM[0], NUM[2])))
print(np.sqrt(metrics.mean_squared_error(NUM[0], NUM[3])))
print(np.sqrt(metrics.mean_squared_error(NUM[0], NUM[4])))

path=r"D:\AIS_TEMP\Typhoon\IBTrACS.ALL.list.v04r00.points\IBTrACS.ALL.list.v04r00.points.shp"
typhoon=gpd.read_file(path)
print("已经读取")
typhoon=pd.DataFrame(typhoon,columns=['SID','year'])
typhoon=typhoon[typhoon['year']>=2000]
typhoon=typhoon.drop_duplicates(subset=['SID'],keep='first')
typhoon=typhoon.groupby('year').count()
print(typhoon)
