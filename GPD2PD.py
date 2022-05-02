import geopandas as gpd
import glob
import os
import pandas as pd
TEMP11_PATH=r"D:\AIS_TEMP\11"
TEMP11_PATH=r"D:\AIS_TEMP\Typhoon_context"
file_list=glob.glob(os.path.join(TEMP11_PATH,'*.shp'))
for item in file_list:
    date=os.path.split(item)[1].split(".")[0]
    print(date)
    df=gpd.read_file((item))
    #df=pd.DataFrame(df,columns=['ID','speed','orient','count','course','heading'])
    df = pd.DataFrame(df, columns=['ID', 'COUNT', 'PRESS', 'SPEED', 'DIR'])
    df.dropna(axis=0, how='any',inplace=True)
    df.to_csv(os.path.join(TEMP11_PATH,date+'.csv'),index=False)