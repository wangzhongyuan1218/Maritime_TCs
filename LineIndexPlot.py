import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
column='H';
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world['name']=world['name'].apply(lambda x: 'China' if x=='Taiwan' else x)
ax=world.plot(color="white", edgecolor='black')

data=gpd.read_file("D:\AIS_TEMP\da0711ce\continent_line.shp")
ax=data.plot(color='black',linewidth=0.1)
data=gpd.read_file(r"D:\AIS_TEMP\22\all.shp");

data=data.sort_values(column,ascending=False);
#data=data.head(10);
#data=data[data['COUNTRY_x']=='China'];
data['result']=data['COUNTRY_x'].apply(lambda x: x+"→")
data['result']=data['result']+data['COUNTRY_y']
temp=data.head(10)
import pandas as pd
temp=pd.DataFrame(temp,columns=['result',column])
print(temp)
data=data.sort_values(column,ascending=True);
data=data.head(len(data)-10)
deduct=np.nanmean(temp[column].values)-np.nanmean(data[column].values)
print(deduct)
deduct=(np.nanmean(temp[column].values)-np.nanmean(data[column].values))/np.nanmean(data[column].values)
print(deduct)
"""
values=data[column].values;
Q0=0;
Q1=np.percentile(values,25)
Q2=np.percentile(values,50)
Q3=np.percentile(values,75)
Q4=np.percentile(values,95)

import matplotlib.pyplot as plt


tempdata=data[(data[column]>=0) & (data[column]<Q1)]
#tempdata.plot(ax=ax,column=column,scheme='NaturalBreaks',cmap='Reds',alpha = 0.2);
tempdata.plot(alpha=0.1,ax=ax,color='lightblue',legend=True)

tempdata=data[(data[column]>=Q1) & (data[column]<Q2)]
tempdata.plot(alpha=0.1,ax=ax,color='lightblue',legend=True)

tempdata=data[(data[column]>=Q2) & (data[column]<Q3)]
tempdata.plot(alpha=0.1,ax=ax,color='lightblue',legend=True)

tempdata=data[(data[column]>=Q3) & (data[column]<Q4)]
tempdata.plot(alpha=0.1,ax=ax,color='lightgreen',legend=True)

tempdata=data[(data[column]>=6) ]
tempdata.plot(alpha=0.1,ax=ax,color='red',legend=True)

data=gpd.read_file("D:\AIS_TEMP\da0711ce\continent_line.shp")
data.plot(color='black',ax=ax,linewidth=0.3)
plt.title(column)
plt.show();


print(Q1)
print(Q2)
print(Q3)
print(Q4)
print(np.max(values))

"""