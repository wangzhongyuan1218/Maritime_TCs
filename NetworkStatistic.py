import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#待统计的不同类型船舶的shiptype代号
FISHING=[30,30]
PASSENGER=[60,69]
CARGO=[70,79]
TANKER=[80,89]
ALL=[-1,255]
from shapely.geometry import LineString,Point
import geopandas as gpd
import pandas as pd
import pyproj
import os
import numpy as np
PortName=r"D:\ZXK\portCenter.csv"

dynamic_name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime']
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']

def calculate_degree(type,dataframe,partPD):
    dataframe=dataframe[dataframe['FROM']!=dataframe['DESTINATION']]
    dataframe = dataframe[(dataframe['SHIPTYPE'] <= type[1])]
    dataframe = dataframe[(dataframe['SHIPTYPE'] >= type[0])]
    #求节点的入度
    INDEX_NAME=[]
    TO_DEGREE=[]
    for index,row in dataframe.groupby('DESTINATION'):
        INDEX_NAME.append(index)
        temp=pd.DataFrame(row)
        temp=row.drop_duplicates(subset=['FROM', 'DESTINATION'], keep='first', inplace=False)
        TO_DEGREE.append(len(temp))
    result = pd.DataFrame(INDEX_NAME, columns=['NAME'])
    result['TO_DEGREE'] = TO_DEGREE
    partPD = partPD.merge(result, how='left', on="NAME")
    #求节点的出度
    INDEX_NAME=[]
    FROM_DEGREE=[]
    for index,row in dataframe.groupby('FROM'):
        INDEX_NAME.append(index)
        temp = pd.DataFrame(row)
        temp = row.drop_duplicates(subset=['FROM', 'DESTINATION'], keep='first', inplace=False)
        FROM_DEGREE.append(len(temp))
    result = pd.DataFrame(INDEX_NAME, columns=['NAME'])
    result['FROM_DEGREE'] = FROM_DEGREE
    partPD = partPD.merge(result, how='left', on="NAME")
    partPD['FROM_DEGREE'] = partPD['FROM_DEGREE'].fillna(0)
    partPD['TO_DEGREE'] = partPD['TO_DEGREE'].fillna(0)
    partPD['FROM_DEGREE']= partPD['FROM_DEGREE'].apply(int)
    partPD['TO_DEGREE'] = partPD['TO_DEGREE'].apply(int)
    #求节点的度
    intersect_part=dataframe.merge(dataframe,left_on=['FROM','DESTINATION'],right_on=['DESTINATION','FROM'],how='inner')
    INDEX_NAME=[]
    DEDUCT_DEGREE = []
    for index, row in intersect_part.groupby('FROM_x'):
        INDEX_NAME.append(index)
        temp = pd.DataFrame(row)
        temp = row.drop_duplicates(subset=['FROM_x', 'DESTINATION_x'], keep='first', inplace=False)
        DEDUCT_DEGREE.append(len(temp))
    result = pd.DataFrame(INDEX_NAME, columns=['NAME'])
    result['DEDUCT_DEGREE'] = DEDUCT_DEGREE
    partPD = partPD.merge(result, how='left', on="NAME")
    partPD['DEDUCT_DEGREE'] = partPD['DEDUCT_DEGREE'].fillna(0)
    partPD['DEDUCT_DEGREE'] = partPD['DEDUCT_DEGREE'].apply(int)
    partPD['DEGREE']=partPD['TO_DEGREE']+partPD['FROM_DEGREE']-partPD['DEDUCT_DEGREE']
    partPD=partPD.drop('DEDUCT_DEGREE',axis=1)

    #求节点的聚类系数
    PORT=partPD.NAME.values
    CLUSTER_C=[]
    dataframe = dataframe.drop_duplicates(subset=['FROM', 'DESTINATION'], keep='first', inplace=False)
    count=0
    for port in PORT:
        count=count+1
        print("{0}:{1}:{2}".format(port,len(PORT),count))
        port_data=dataframe[(dataframe['FROM']==port) |(dataframe['DESTINATION']==port)]#找到相邻节点
        link_node=port_data.FROM.values.tolist()
        link_node2=port_data.DESTINATION.values.tolist()
        link_node.extend(link_node2)
        link_node=np.unique(link_node)
        ii = np.argwhere(link_node == port)
        link_node = np.delete(link_node, ii)
        if len(link_node)==0:
            CLUSTER_C.append(0)
            continue
        temp=dataframe[(dataframe['FROM'].isin(link_node))]
        temp=temp[temp['DESTINATION'].isin(link_node)]
        cluster_c=(2*len(temp))/(len(link_node)*(len(link_node)+1))
        CLUSTER_C.append(cluster_c)
    partPD['CLUSTER_C']=CLUSTER_C
    return partPD

def read_static_network():
    MONTH = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'Septemper', 'October',
             'November', 'December']
    static_network=[]
    for month in range(1,13):
        basepath = r"D:\AIS_TEMP\15\{0}_simple_shiptype.shp.csv".format(MONTH[month - 1])
        temp=pd.read_csv(basepath)
        static_network.append(temp)
    return static_network
if __name__ == '__main__':
    # 获取地名
    partPD = pd.read_csv(PortName, sep=',', names=['NAME', 'LON', 'LAT'])
    partPD['NAME'] = partPD['NAME'].apply(lambda x: x.lstrip('0123456789. \t'))
    partPD = partPD.drop_duplicates(subset=['NAME'], keep='last', inplace=False)  # 去重复
    part_lon = partPD.LON.values
    part_lat = partPD.LAT.values
    part_name = partPD.NAME.values

    static_network=read_static_network()
    network=pd.concat(static_network)
    static_network.append(network)
    MONTH = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'Septemper', 'October',
             'November', 'December','YEAR']
    SHIPTYPE=["ALL","FISHING",'PASSENGER','CARGO','TANKER']
    PARTPD_ini=partPD
    for i in range(0,13):
        for item in SHIPTYPE:
            print(MONTH[i])
            print(item)
            if item=="ALL":
                TYPE=ALL
            elif item=="FISHING":
                TYPE=FISHING
            elif item=="CARGO":
                TYPE=CARGO
            elif item=="TANKER":
                TYPE=TANKER
            elif item=='PASSENGER':
                TYPE=PASSENGER
            partPD = calculate_degree(TYPE, static_network[i], PARTPD_ini)
            xy = [Point(xy) for xy in zip(partPD.LON, partPD.LAT)]
            pointDataFrame = gpd.GeoDataFrame(partPD, geometry=xy)
            pointDataFrame.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
            shapefile = r"D:\AIS_TEMP\16\DEGREE_{0}_{1}.shp".format(MONTH[i], item)
            pointDataFrame.to_file(filename=shapefile, driver='ESRI Shapefile', encoding='utf-8')
            partPD.to_csv(shapefile+".csv",index=False)



