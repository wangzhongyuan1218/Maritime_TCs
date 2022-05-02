import pandas as pd;
import glob;
import numpy as np;
import geopandas as gpd;
import pyproj;
import os;
from shapely.geometry import LineString,Point
#读取港口国家数据
path=r"D:\ZXK\PORT_COUNTRY.csv";
portPD1=pd.read_csv(path);
portPD=pd.DataFrame(portPD1,columns=['NAME','COUNTRY']);
portPD1=pd.DataFrame(portPD1,columns=['COUNTRY','LAT','LON']);
portPD1=portPD1.drop_duplicates(subset='COUNTRY', keep='first', inplace=False)

#读取台风数据
typhoon=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp";
typhoon=gpd.read_file(typhoon);
columns=typhoon.columns;
typhoon['WIND']=0;
col=[];
for item in columns:
    if item.endswith("WIND"):
        col.append(item);

typhoon['WIND']=typhoon[col].max(axis=1);
Tyhphoon_sid=[];
Tyhphoon_name=[];
Typhoon_grade=[];
Typhoon_avg_speed=[];
for index, row in typhoon.groupby("SID"):
    speed=row['WIND'].values;
    speed=speed*1852/3600;
    max_speed=np.max(speed);
    Tyhphoon_name.append(row['NAME'].values[0]);
    if max_speed>51:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("Super TY");
        Typhoon_avg_speed.append(55);
    elif max_speed>41.5:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("STY");
        Typhoon_avg_speed.append((41.5+50.9)/2);
    elif max_speed>32.7:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("TY");
        Typhoon_avg_speed.append((32.7+41.4 )/2);
    elif max_speed>24.5:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("STS");
        Typhoon_avg_speed.append((24.5+32.6)/2);
    elif max_speed>17.2:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("TS");
        Typhoon_avg_speed.append((17.2+24.4)/2);
    else:
        Tyhphoon_sid.append(index);
        Typhoon_grade.append("TD");
        Typhoon_avg_speed.append((10.8+17.1)/2);

Typhoon_avg_speed=np.array(Typhoon_avg_speed);
Typhoon_si=Typhoon_avg_speed/(55+(10.8+17.1)/2+(17.2+24.4)/2+(32.7+41.4 )/2+(41.5+50.9)/2);

SI_dic={}
Grade_dic={};
for i in range(len(Tyhphoon_sid)):
    SI_dic[Tyhphoon_sid[i]]=Typhoon_si[i];
    Grade_dic[Tyhphoon_sid[i]]=Typhoon_grade[i];

print("预存储数据读取结束");

#读取航线数据
path=r"D:\AIS_TEMP\14";
file_list=glob.glob(os.path.join(path,"*_7_*.csv"));
lines=pd.DataFrame(columns=['MMSI', 'FROM','DESTINATION','COUNTRY_x','COUNTRY_y','DELAY','SHIPTYPE','COUNTRYCODE','ETA','PosTime']);
for item in file_list:
    name=os.path.split(item)[1];
    sid=name.split("_")[0];
    data=pd.read_csv(item);
    data['DELAY']=data[['delay_w1','delay_w2','delay_w3','delay_w4','delay_w5','delay_w6','delay_w7']].max(axis=1);
    data=data.merge(portPD,how="left",left_on="FROM",right_on="NAME");
    data=data.merge(portPD,how='left',left_on='DESTINATION',right_on='NAME');
    data=data[data['COUNTRY_x']!=data['COUNTRY_y']];
    data = pd.DataFrame(data, columns=['MMSI', 'FROM','DESTINATION','COUNTRY_x','COUNTRY_y','DELAY','SHIPTYPE','COUNTRYCODE','ETA','PosTime']);
    data['SI'] = SI_dic[sid];
    data['GRADE']=Grade_dic[sid];
    print("{0}读取完毕".format(sid));
    lines=lines.append(data);

print(lines);
#lines['DELAY_SI']=lines['DELAY']*lines['SI'];

print("开始分类数据");


#计算航线的风险
#countData=lines.groupby(['COUNTRY_x','COUNTRY_y','GRADE','SI'])['MMSI'].count();#按照台风等级进行分类
countData=lines.groupby(['COUNTRY_x','COUNTRY_y','GRADE','SI']).agg({'MMSI':['count'],'DELAY':['mean']});#按照台风等级进行分类
countData=countData.reset_index();#重新设置索引

countData.columns=['COUNTRY_x','COUNTRY_y','GRADE','SI','COUNT','DELAY'];

print(countData);
print(np.sum(countData['COUNT'].values)*1086.5)

countData['H0']=countData['COUNT']*countData['SI'];
countData['HDelay']=countData['DELAY']*countData['SI'];
HData=countData.groupby(['COUNTRY_x','COUNTRY_y'])['H0','HDelay'].sum();
HData=HData.reset_index();
HData.rename(columns={'H0':'H'},inplace=True);
print(HData)



#生成航线风险的矢量文件
portPD1.rename(columns={'COUNTRY':'COUN'},inplace=True);
HData=pd.merge(HData,portPD1,how='left',left_on='COUNTRY_x',right_on='COUN');
HData=pd.merge(HData,portPD1,how='left',left_on='COUNTRY_y',right_on='COUN');
HData=pd.DataFrame(HData,columns=['COUNTRY_x', 'COUNTRY_y', 'H', 'HDelay', 'LON_x', 'LAT_x', 'LON_y', 'LAT_y']);
geom_list = [];
for index, row in HData.iterrows():
    line = LineString([(row['LON_x'], row['LAT_x']), (row['LON_y'], row['LAT_y'])]);
    geom_list.append(line);


print("正在创建")
geodata = gpd.GeoDataFrame(HData, geometry=geom_list)
geodata.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
#geodata.to_file(filename=r"D:\AIS_TEMP\22\ALL.shp", driver='ESRI Shapefile', encoding='utf-8')



