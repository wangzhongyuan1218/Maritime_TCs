import pandas as pd
import geopandas as gpd
import numpy as np
import os
import glob
import pyproj
from shapely.geometry import LineString

TEMP14 = r"D:\AIS_TEMP\14"
def get_date_of_typhoon():
    dateframe=[]
    basepath=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp"
    geodata=gpd.read_file(basepath)
    geodata["ISO_TIME"] = pd.to_datetime(geodata["ISO_TIME"])
    geodata['date'] = geodata['ISO_TIME'].apply(lambda x: x.strftime("%Y%m%d"))
    geodata=pd.DataFrame(geodata,columns=['SID','NAME','date'])
    geodata=geodata.drop_duplicates('date',keep='first')
    SID=np.unique(geodata.SID.values)
    for item in SID:
        temp=geodata[geodata['SID']==item]
        dateframe.append(temp)
    return dateframe
def read_affected_ais(file_list):
    dataframe=[]
    for item in file_list:
        temp = pd.read_csv(item)
        date = os.path.split(item)[1].split('.')[0]
        temp['date'] = date
        dataframe.append(temp)
    static_dataframe = pd.concat(dataframe)
    static_dataframe['SHIPTYPE'] = static_dataframe['SHIPTYPE'].fillna(-1)
    static_dataframe['SHIPTYPE'] = static_dataframe['SHIPTYPE'].apply(int)
    static_dataframe['date'] = static_dataframe['date'].apply(int)
    return static_dataframe

def window_to_shp_and_csv(wdataframe,window,sid,name):
    o_wn=['o_w1','o_w2','o_w3','o_w4','o_w5','o_w6','o_w7']
    s_wn = ['s_w1', 's_w2', 's_w3', 's_w4', 's_w5', 's_w6', 's_w7']
    delay_wn = ['delay_w1', 'delay_w2', 'delay_w3', 'delay_w4', 'delay_w5', 'delay_w6', 'delay_w7']
    dataframe=wdataframe
    dataframe=dataframe[dataframe['window']==window]

    dataframe = dataframe[dataframe[o_wn[window-1]] >0]
    dataframe = dataframe[dataframe[s_wn[window-1]] >0]
    dataframe = dataframe[dataframe[delay_wn[window - 1]] > 0]

    dataframe.to_csv(os.path.join(TEMP14,sid+"_"+str(window)+"_"+name+".csv"))
    property = pd.DataFrame(columns=['FROM', 'DES', 'FROM_X', 'FROM_Y', 'TO_X', 'TO_Y', 'M_DELAY', 'COUNT', 'SHIPTYPE'])
    for index, row in dataframe.groupby(['FROM', 'DESTINATION', 'SHIPTYPE']):
        dic = {'FROM': index[0], 'DES': index[1], 'FROM_X': row.Lon.values[0], 'FROM_Y': row.Lat.values[0],
               'TO_X': row.LON.values[0], 'TO_Y': row.LAT.values[0], 'M_DELAY': np.nanmean(row[delay_wn].values),
               'SHIPTYPE': index[2], 'COUNT': len(row)}
        property = property.append(dic, ignore_index=True)
    FROM_X = property.FROM_X.values
    TO_X = property.TO_X.values
    FROM_Y = property.FROM_Y.values
    TO_Y = property.TO_Y.values
    line = [LineString([(x1, y1), (x2, y2)]) for (x1, y1, x2, y2) in zip(FROM_X, FROM_Y, TO_X, TO_Y)]

    if len(line)>0:
        geodata = gpd.GeoDataFrame(property, geometry=line)
        geodata.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
        geodata.to_file(os.path.join(TEMP14,sid+"_"+str(window)+"_"+name+".shp"), driver='ESRI Shapefile', encoding="utf-8")
if __name__ == '__main__':
    basepath=r"D:\AIS_TEMP\7"
    file_list = glob.glob(os.path.join(basepath, "*.csv"))
    dataframe = []
    for item in file_list:
        shiptype = os.path.split(item)[1].split(".")[0].split('_')[1]
        shiptype = int(shiptype)
        temp = pd.read_csv(item)
        temp['SHIPTYPE'] = shiptype
        dataframe.append(temp)
    shiptype_dataframe = pd.concat(dataframe)

    TEMP13=r"D:\AIS_TEMP\13"
    TYPHOON=get_date_of_typhoon()
    for i in range(len(TYPHOON)):
        item=TYPHOON[i]
        date=item.date.values
        name=item.NAME.values[0]
        sid = item.SID.values[0]
        file_list=[]
        for day in date:
            file_list.append(os.path.join(TEMP13,str(day)+".csv"))
        static_dataframe=read_affected_ais(file_list)
        dataframe = static_dataframe.merge(shiptype_dataframe, on=["date", 'SHIPTYPE'], how='left')
        #dataframe.to_csv("temp.csv")
        for window in range(1,8):
            print(os.path.join(TEMP14,sid+"_"+str(window)+"_"+name+".csv"))
            if os.path.exists(os.path.join(TEMP14,sid+"_"+str(window)+"_"+name+".csv")):
                continue
            window_to_shp_and_csv(dataframe, window, sid,name)


