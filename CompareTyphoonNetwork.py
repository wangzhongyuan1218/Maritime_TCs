import os
import glob
import pandas as pd
import geopandas as gpd
typhoon_line=gpd.read_file(r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp")
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")
typhoon_dataframe=pd.DataFrame(typhoon_line,columns=['SID','month'])
TEMP_16=r"D:\AIS_TEMP\16"

month_file_list=glob.glob(os.path.join(TEMP_16,'*.csv'))
MONTH = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'Septemper', 'October',
             'November', 'December','YEAR']
SHIPTYPE=["ALL","FISHING",'PASSENGER','CARGO','TANKER']
TEMP_17=r"D:\AIS_TEMP\17"
TEMP_18=r"D:\AIS_TEMP\18"

typhoon_file_list=glob.glob(os.path.join(TEMP_17,'*.csv'))
from shapely.geometry import LineString,Point
import pyproj
def get_conduct(before,after,destination):
    before=pd.read_csv(before)
    after=pd.read_csv(after)
    result=before.merge(after,on=['NAME','LON','LAT'],how='inner')
    result=result.drop(['geometry_x'], axis=1)
    result = result.drop(['geometry_y'], axis=1)
    result['TODEG_d']=result['TO_DEGREE_x']-result['TO_DEGREE_y']
    result['FROMDEG_d']=result['FROM_DEGREE_x']-result['FROM_DEGREE_y']
    result['DEG_d'] = result['DEGREE_x'] - result['DEGREE_y']
    result['CLU_d'] = result['CLUSTER_C_x'] - result['CLUSTER_C_y']
    result.to_csv(destination+".csv",index=False)

    xy = [Point(xy) for xy in zip(result.LON, result.LAT)]
    pointDataFrame = gpd.GeoDataFrame(result, geometry=xy)
    pointDataFrame.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影

    pointDataFrame.to_file(filename=destination, driver='ESRI Shapefile', encoding='utf-8')

print(len(typhoon_file_list))
for item in typhoon_file_list:
    print(item)
    temp=os.path.split(item)[1]
    temp=temp.split(".")[0]
    sid=temp.split("_")[1]
    shiptype = temp.split("_")[-1]
    temp=typhoon_dataframe[typhoon_dataframe['SID']==sid]
    month=temp.month.values[0]
    M=MONTH[month-1]
    filename="DEGREE_{0}_{1}.shp.csv".format(M,shiptype)
    filename=os.path.join(TEMP_16,filename)
    destination=os.path.split(item)[1]
    destination=os.path.join(TEMP_18,destination).split(".")[0]+".shp"
    get_conduct(filename,item,destination)


