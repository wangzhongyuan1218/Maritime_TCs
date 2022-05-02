import pandas as pd
from multiprocessing import Pool
import os
import glob
import csv

static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE']
def read_static_dataframe(path):
    df = pd.read_csv(path, delimiter="~", names=static_name, low_memory=False,quoting=csv.QUOTE_NONE)
    df = pd.DataFrame(df, columns=subset_static_name)
    df = df.dropna(subset=['MMSI'])
    return df

def read_static(file_list):
    if len(file_list) == 0:
        return
    thread_num = len(file_list)
    p = Pool(thread_num)
    res = p.map(read_static_dataframe, file_list)
    p.close()
    p.join()
    try:
        res = pd.concat(res)
    except:
        res=res
    res = res.drop_duplicates(subset=['MMSI'], keep='last', inplace=False)
    return res
import time
if __name__ == '__main__':
    basepath1 = r"D:\AIS_2017\2017\static\\"
    despath=r"D:\AIS_TEMP\12\\"
    for root, dirs, files in os.walk(basepath1):
        for name in dirs:
            file_list = glob.glob(os.path.join(os.path.join(root, name), "*.csv"))
            if len(file_list)==0:
                continue
            start=time.time()
            res=read_static(file_list)
            res.to_hdf(os.path.join(despath,name+".h5"), key='MMSI', mode='w')
            print(name)
            print(time.time()-start)
