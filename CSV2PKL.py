import pandas as pd
TMEP3_PATH=r"D:\AIS_TEMP\3"#每条船存储一个MMSI
TMEP4_PATH=r"D:\AIS_TEMP\4"#每条船存储一个MMSI
import glob
import os
name=['MMSI','ROT','ClassType','PosTime','Lon','Lat','Course','TrueHeading','Speed','NavigationStatus','Accuracy','ReceiveTime','X','Y']
if __name__ == '__main__':
    file_list = glob.glob(os.path.join(TMEP3_PATH, "*.csv"))
    for item in file_list:
        data=pd.read_csv(item,names=name,low_memory=False)
        fname, fename = os.path.split(item)
        print(item)
        despath=os.path.join(TMEP4_PATH,fename.split('.')[0]+'.pkl')
        data.to_pickle(despath)