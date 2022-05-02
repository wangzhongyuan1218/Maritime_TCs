import pandas as pd
import glob
import geopandas as gpd
import numpy as np
FISHING=[30,30]
PASSENGER=[60,69]
CARGO=[70,79]
TANKER=[80,89]
ALL=[-1,255]
SHIPTYPE=["ALL","FISHING",'PASSENGER','CARGO','TANKER']
Tyhphoon_sid=[]
Tyhphoon_name=[]
Typhoon_grade=[]
Typhoon_avg_speed=[]

typhoon=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp"
typhoon=gpd.read_file(typhoon)
columns=typhoon.columns
typhoon['WIND']=0
col=[]
for item in columns:
    if item.endswith("WIND"):
        col.append(item)

typhoon['WIND']=typhoon[col].max(axis=1)
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

PortName=r"D:\ZXK\portCenter.csv"
partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
print(len(partPD))
partPD_ini=partPD
import os
delay_file_list=glob.glob(os.path.join(R"D:\AIS_TEMP\14",'*.csv'))
TEMP_14=r"D:\AIS_TEMP\14"
WINDOW=['1','2','3','4','5','6','7']
for window in WINDOW:
    for i in range(len(Tyhphoon_sid)):
        path=Tyhphoon_sid[i]+"_"+window+"_"+Tyhphoon_name[i]+".csv"
        path=os.path.join(TEMP_14,path)
        if not os.path.exists(path):
            continue
        temp_dataframe=pd.read_csv(path)
        temp_dataframe['delay']=temp_dataframe[['delay_w1','delay_w2','delay_w3','delay_w4','delay_w5','delay_w6','delay_w7']].max(axis=1)
        temp_dataframe['is_fishing'] = temp_dataframe['SHIPTYPE'].between(FISHING[0],FISHING[1])
        temp_dataframe['is_cargo'] = temp_dataframe['SHIPTYPE'].between(CARGO[0], CARGO[1])
        temp_dataframe['is_tanker'] = temp_dataframe['SHIPTYPE'].between(TANKER[0],TANKER[1])
        temp_dataframe['is_passenger'] = temp_dataframe['SHIPTYPE'].between(PASSENGER[0], PASSENGER[1])
        port=[]
        all_delay=[]
        fishing_delay=[]
        cargo_delay=[]
        tanker_delay=[]
        passenger_delay=[]
        for index,row in temp_dataframe.groupby("FROM"):
            port.append(index)
            mean_delay=np.nanmean(row.delay.values)
            all_delay.append(mean_delay)
            fishing_frame=row[row['is_fishing']==True]
            if len(fishing_frame)==0:
                mean_fishing_delay=0
            else:
                mean_fishing_delay=np.nanmean(fishing_frame.delay.values)
            fishing_delay.append(mean_fishing_delay)
            cargo_frame = row[row['is_cargo'] == True]
            if len(cargo_frame)==0:
                mean_cargo_delay=0
            else:
                mean_cargo_delay = np.nanmean(cargo_frame.delay.values)
            cargo_delay.append(mean_cargo_delay)
            tanker_frame = row[row['is_tanker'] == True]
            if len(tanker_frame)==0:
                mean_tanker_delay=0
            else:
                mean_tanker_delay = np.nanmean(tanker_frame.delay.values)
            tanker_delay.append(mean_tanker_delay)
            passenger_frame = row[row['is_passenger'] == True]
            if len(passenger_frame)==0:
                mean_passenger_delay=0
            else:
                mean_passenger_delay = np.nanmean(passenger_frame.delay.values)
            passenger_delay.append(mean_passenger_delay)
        port2=[]
        all2_delay = []
        fishing2_delay = []
        cargo2_delay = []
        tanker2_delay = []
        passenger2_delay = []
        for index,row in temp_dataframe.groupby("DESTINATION"):
            port2.append(index)
            mean_delay=np.nanmean(row.delay.values)
            all2_delay.append(mean_delay)
            fishing_frame=row[row['is_fishing']==True]
            if len(fishing_frame)==0:
                mean_fishing_delay=0
            else:
                mean_fishing_delay=np.nanmean(fishing_frame.delay.values)
            fishing2_delay.append(mean_fishing_delay)
            cargo_frame = row[row['is_cargo'] == True]
            if len(cargo_frame)==0:
                mean_cargo_delay=0
            else:
                mean_cargo_delay = np.nanmean(cargo_frame.delay.values)
            cargo2_delay.append(mean_cargo_delay)
            tanker_frame = row[row['is_tanker'] == True]
            if len(tanker_frame)==0:
                mean_tanker_delay=0
            else:
                mean_tanker_delay = np.nanmean(tanker_frame.delay.values)
            tanker2_delay.append(mean_tanker_delay)
            passenger_frame = row[row['is_passenger'] == True]
            if len(passenger_frame)==0:
                mean_passenger_delay=0
            else:
                mean_passenger_delay = np.nanmean(passenger_frame.delay.values)
            passenger2_delay.append(mean_passenger_delay)
        dataframe=pd.DataFrame(port,columns=['NAME'])
        dataframe['from_delay']=all_delay

        dataframe=partPD.merge(dataframe,how='left',on='NAME')
        dataframe2 = pd.DataFrame(port2, columns=['NAME'])
        dataframe2['to_delay'] = all2_delay
        dataframe = dataframe.merge(dataframe2, how='left', on='NAME')
        key="DELAY_{0}_{1}_{2}_ALL.csv".format(Tyhphoon_sid[i],window,Tyhphoon_name[i])
        path=os.path.join(r"D:\AIS_TEMP\20",key)
        dataframe = dataframe.fillna(0)
        dataframe.to_csv(path,index=False)
        print(key)

        dataframe = pd.DataFrame(port, columns=['NAME'])
        dataframe['from_delay'] = fishing_delay
        dataframe = partPD.merge(dataframe, how='left', on='NAME')
        dataframe2 = pd.DataFrame(port2, columns=['NAME'])
        dataframe2['to_delay'] = fishing2_delay
        dataframe = dataframe.merge(dataframe2, how='left', on='NAME')
        key = "DELAY_{0}_{1}_{2}_FISHING.csv".format(Tyhphoon_sid[i], window, Tyhphoon_name[i])
        path = os.path.join(r"D:\AIS_TEMP\20", key)
        dataframe = dataframe.fillna(0)
        dataframe.to_csv(path, index=False)

        dataframe = pd.DataFrame(port, columns=['NAME'])
        dataframe['from_delay'] = passenger_delay
        dataframe = partPD.merge(dataframe, how='left', on='NAME')
        dataframe2 = pd.DataFrame(port2, columns=['NAME'])
        dataframe2['to_delay'] = passenger2_delay
        dataframe = dataframe.merge(dataframe2, how='left', on='NAME')
        key = "DELAY_{0}_{1}_{2}_PASSENGER.csv".format(Tyhphoon_sid[i], window, Tyhphoon_name[i])
        path = os.path.join(r"D:\AIS_TEMP\20", key)
        dataframe = dataframe.fillna(0)
        dataframe.to_csv(path, index=False)

        dataframe = pd.DataFrame(port, columns=['NAME'])
        dataframe['from_delay'] = tanker_delay
        dataframe = partPD.merge(dataframe, how='left', on='NAME')
        dataframe2 = pd.DataFrame(port2, columns=['NAME'])
        dataframe2['to_delay'] = tanker2_delay
        dataframe = dataframe.merge(dataframe2, how='left', on='NAME')
        key = "DELAY_{0}_{1}_{2}_TANKER.csv".format(Tyhphoon_sid[i], window, Tyhphoon_name[i])
        path = os.path.join(r"D:\AIS_TEMP\20", key)
        dataframe = dataframe.fillna(0)
        dataframe.to_csv(path, index=False)

        dataframe = pd.DataFrame(port, columns=['NAME'])
        dataframe['from_delay'] = cargo_delay
        dataframe = partPD.merge(dataframe, how='left', on='NAME')
        dataframe2 = pd.DataFrame(port2, columns=['NAME'])
        dataframe2['to_delay'] = cargo2_delay

        dataframe = dataframe.merge(dataframe2, how='left', on='NAME')
        key = "DELAY_{0}_{1}_{2}_CARGO.csv".format(Tyhphoon_sid[i], window, Tyhphoon_name[i])
        path = os.path.join(r"D:\AIS_TEMP\20", key)
        dataframe = dataframe.fillna(0)
        dataframe.to_csv(path, index=False)



