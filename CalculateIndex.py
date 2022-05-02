import geopandas as gpd
import numpy as np
import pyproj
from shapely.geometry import LineString,Point
import os
import pandas as pd
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
Typhoon_avg_speed=[]
for index, row in typhoon.groupby("SID"):
    speed=row['WIND'].values
    speed=speed*1852/3600
    max_speed=np.max(speed)
    Tyhphoon_name.append(row['NAME'].values[0])
    if max_speed>51:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("Super TY")
        Typhoon_avg_speed.append(55)
    elif max_speed>41.5:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("STY")
        Typhoon_avg_speed.append((41.5+50.9)/2)
    elif max_speed>32.7:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TY")
        Typhoon_avg_speed.append((32.7+41.4 )/2)
    elif max_speed>24.5:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("STS")
        Typhoon_avg_speed.append((24.5+32.6)/2)
    elif max_speed>17.2:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TS")
        Typhoon_avg_speed.append((17.2+24.4)/2)
    else:
        Tyhphoon_sid.append(index)
        Typhoon_grade.append("TD")
        Typhoon_avg_speed.append((10.8+17.1)/2)



Typhoon_avg_speed=np.array(Typhoon_avg_speed)
Typhoon_si=Typhoon_avg_speed/(55+(10.8+17.1)/2+(17.2+24.4)/2+(32.7+41.4 )/2+(41.5+50.9)/2)

#以上求出了每次台风的SI
WINDOW=['1','2','3','4','5','6','7']
SHIPTYPE=["ALL","FISHING",'PASSENGER','CARGO','TANKER']
TEMP_18=r"D:\AIS_TEMP\18"
TEMP_19=r"D:\AIS_TEMP\19"

PortName=r"D:\ZXK\portCenter.csv"

dynamic_name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']
#获取地名
partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
print(len(partPD))
partPD_ini=partPD
grade=['Super TY','STY','TY','STS','TS','TS']


TEMP_20=r"D:\AIS_TEMP\20"

for type in SHIPTYPE:
    print(type)
    for window in WINDOW:
        TOTAL_DEG_d=[]
        TOTAL_CLU_d = []
        TOTAL_is_affected=[]
        TOTAL_FROM_DELAY=[]
        TOTAL_TO_DELAY = []
        for i in range(len(Tyhphoon_sid)):
            key="DEGREE_{0}_{1}_{2}_{3}.shp.csv".format(Tyhphoon_sid[i],window,Tyhphoon_name[i],type)
            path=os.path.join(TEMP_18,key)
            if not os.path.exists(path):
                continue
            temp=pd.read_csv(path)
            DEG_d=temp.DEG_d.values
            DEG_d=np.abs(DEG_d)
            CLU_d=temp.CLU_d.values

            key2="DELAY_{0}_{1}_{2}_{3}.csv".format(Tyhphoon_sid[i],window,Tyhphoon_name[i],type)
            path = os.path.join(TEMP_20, key2)

            if not os.path.exists(path):
                continue
            temp=pd.read_csv(path)
            FROM_DELAY=temp.from_delay.values
            TO_DELAY=temp.to_delay.values
            is_affected= (DEG_d>0) | (CLU_d>0) | (TO_DELAY>0) | (FROM_DELAY>0)
            if Typhoon_grade[i]=="TD":
                is_affected = is_affected*6
            elif Typhoon_grade[i]=="TS":
                is_affected = is_affected*5
            elif Typhoon_grade[i]=="STS":
                is_affected = is_affected*4
            elif Typhoon_grade[i]=="TY":
                is_affected = is_affected*3
            elif Typhoon_grade[i]=="STY":
                is_affected = is_affected*2
            elif Typhoon_grade[i]=="Super TY":
                is_affected = is_affected*1
            TOTAL_is_affected.append(is_affected)

            TOTAL_CLU_d.append(CLU_d)
            TOTAL_DEG_d.append(DEG_d)
            TOTAL_FROM_DELAY.append(FROM_DELAY)
            TOTAL_TO_DELAY.append(TO_DELAY)

        TOTAL_DEG_d=np.array(TOTAL_DEG_d).T
        TOTAL_is_affected=np.array(TOTAL_is_affected).T
        TOTAL_CLU_d=np.array(TOTAL_CLU_d).T
        TOTAL_FROM_DELAY=np.array(TOTAL_FROM_DELAY).T
        TOTAL_TO_DELAY=np.array(TOTAL_TO_DELAY).T

        F=[]
        C=[]
        D=[]
        F_DELAY=[]
        TO_DELAY=[]
        H_F_delay=0
        H_T_delay=0
        H = 0
        H_deg=0
        H_clu = 0
        for i in range(0,6):
            array=np.array((TOTAL_is_affected==(i+1)).sum(axis=1))
            F.append(array)
            H= H+ array*Typhoon_si[i]

            temp_deg=TOTAL_DEG_d
            temp_deg[TOTAL_is_affected==(i+1)]=0

            mean=temp_deg.max(axis=1)
            #mean=temp_deg.sum(axis=1)/(temp_deg!=0).sum(axis=1)
            mean=temp_deg.sum(axis=1)/array
            H_deg=mean+H_deg
            D.append(mean)

            temp_clu = TOTAL_CLU_d
            temp_clu[TOTAL_is_affected == (i + 1)] = 0
            mean=temp_clu.max(axis=1)
            mean = temp_clu.sum(axis=1) / array
            #mean = temp_clu.sum(axis=1) / (temp_clu != 0).sum(axis=1)
            H_clu = mean*Typhoon_si[i] + H_clu
            C.append(mean)

            temp_from_delay=TOTAL_FROM_DELAY
            temp_from_delay[TOTAL_is_affected == (i + 1)] = 0
            mean=temp_from_delay.max(axis=1)
            mean = temp_from_delay.sum(axis=1) / array
            H_F_delay = mean*Typhoon_si[i] + H_F_delay
            F_DELAY.append(mean)



            temp_to_delay = TOTAL_TO_DELAY
            temp_to_delay[TOTAL_is_affected == (i + 1)] = 0
            mean = temp_to_delay.max(axis=1)
            mean = temp_to_delay.sum(axis=1) / array
            H_T_delay=mean*Typhoon_si[i]+H_T_delay
            TO_DELAY.append(mean)

        partPD=partPD_ini
        partPD['H']=H
        partPD['H_deg'] = H_deg
        partPD['H_clu'] = H_clu
        partPD['H_F_DELAY'] = H_F_delay
        partPD['H_T_DELAY'] = H_T_delay
        for i in range(0,6):
            #partPD['H'+str(i+1)]=H[i]
            partPD['C' + str(i + 1)] = C[i]
            partPD['D' + str(i + 1)] = D[i]
            partPD['F' + str(i + 1)] = F[i]
            partPD['F__DELAY' + str(i + 1)] = F_DELAY[i]
            partPD['T_DELAY' + str(i + 1)] = TO_DELAY[i]
        path = os.path.join(TEMP_19, "window={0},shiptype={1}.csv".format(window,type))
        partPD.to_csv(path,index=False)
        path = os.path.join(TEMP_19, "window={0},shiptype={1}.shp".format(window, type))

        xy = [Point(xy) for xy in zip(partPD.LON, partPD.LAT)]
        pointDataFrame = gpd.GeoDataFrame(partPD, geometry=xy)
        pointDataFrame.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影

        pointDataFrame.to_file(filename=path, driver='ESRI Shapefile', encoding='utf-8')









