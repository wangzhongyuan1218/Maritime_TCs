import pandas as pd
#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
#设置value的显示长度为100，默认为50
pd.set_option('max_colwidth',100)
import numpy as np
import os
import geopandas as gpd
path=r"D:\ZXK\PORT_COUNTRY.csv"
portPD=pd.read_csv(path);
portPD=pd.DataFrame(portPD,columns=['NAME','COUNTRY'])
basepath=r"D:\AIS_TEMP\19"
data=gpd.read_file(os.path.join(basepath,"window=7,shiptype=ALL.shp"))
temp_data=data
print(data.columns)
COLUMN='H'
data=data.merge(portPD,how='left',on="NAME")
data_group=data.groupby("COUNTRY").agg({COLUMN : ['count', np.nanmean]}).reset_index()
data_group=data_group.replace([np.inf, -np.inf], np.nan)
data_group=data_group.fillna(0)
data_group=data_group[data_group[COLUMN]['count']>=10]
data_group=data_group.sort_values(by=(COLUMN,'nanmean'),ascending=False)
data_group=data_group[data_group[COLUMN]['nanmean']!=0]
df=data_group.head(10)
count=0;
value=df[(COLUMN,'nanmean')].values
for item in df.COUNTRY.values:
    print("{0}.{1}({2})".format(count+1,item,"{:.2f}".format(value[count])))
    count=count+1
data_group=data_group.sort_values(by=(COLUMN,'nanmean'),ascending=True)
data_group=data_group.head(len(data_group)-10)
print(data_group[(COLUMN,'nanmean')].values)

deduct=np.nanmean(df[(COLUMN,'nanmean')].values)-np.nanmean(data_group[(COLUMN,'nanmean')].values)
print(deduct)

deduct=(np.nanmean(df[(COLUMN,'nanmean')].values)-np.nanmean(data_group[(COLUMN,'nanmean')].values))/np.nanmean(data_group[(COLUMN,'nanmean')].values)
print(deduct)

import matplotlib.pyplot as plt
import seaborn as sns
sns.barplot(x=('COUNTRY',''), y=(COLUMN,'nanmean'), data=df)
plt.xticks(rotation=90)
plt.xlabel("Country")
plt.ylabel(COLUMN)
plt.show()

#df=data_group[data_group[(COLUMN,'nanmean')]>0]
df=data_group
countries=df.COUNTRY.values
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world['name']=world['name'].apply(lambda x: 'China' if x=='Taiwan' else x)
print(len(world.name.value_counts()))
ax=world.plot(color="white", edgecolor='0.5')
#world=world[world['name'].isin(countries)]

world=world.merge(df,left_on='name',right_on='COUNTRY',how="left")
print(world.columns)
legend_kwds={
    'orientation':'horizontal'
}
world.plot(ax=ax,column=(COLUMN,'nanmean'),cmap='coolwarm',legend=True,legend_kwds=legend_kwds)
Typhoon=r"D:\AIS_TEMP\Typhoon"
Typhoon=gpd.read_file(Typhoon)
Typhoon.plot(ax=ax,linewidth=1,color='gray')
plt.show()

"""
per_data=pd.DataFrame(data,columns=['H','H_deg','H_clu','H_F_DELAY','H_T_DELAY'])
per_data.corr("spearman").to_csv("temp.csv")
per_data=data
sns.regplot(x="H",y="H_F_DELAY",data=per_data)
plt.show()
sns.regplot(x="H",y="H_T_DELAY",data=per_data)
plt.show()
sns.regplot(x="H_deg",y="H_F_DELAY",data=per_data)
plt.show()
sns.regplot(x="H_deg",y="H_T_DELAY",data=per_data)
plt.show()

sns.regplot(x="H_clu",y="H_F_DELAY",data=per_data)

plt.show()
"""
