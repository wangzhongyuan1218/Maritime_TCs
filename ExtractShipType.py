SHIPTYPEPATH=r"D:\AIS_TEMP\AIS_SHIPTYPE_COUNTRYCODE"
import pandas as pd
import os
import glob
static_name=['MMSI','IMO','CALLSIGN','SHIPNAME','SHIPTYPE','LENGTH','BREADTH','POS_FIXING_DEVICE','ETA','DRAUGHT','DESTINATION','CLASSTYPE','COUNTRYCODE','RECEIVETIME','TO_BOW','TO_STERN','TO_PORT','TO_STARBOARD']
subset_static_name=['MMSI','SHIPTYPE','COUNTRYCODE','RECEIVETIME','ETA','DESTINATION']
import csv
from multiprocessing import Pool
def read_static_dataframe(path):
    df = pd.read_csv(path, delimiter="~", names=static_name, low_memory=False,quoting=csv.QUOTE_NONE)
    df = pd.DataFrame(df, columns=subset_static_name)
    df = df.dropna(subset=['MMSI', 'SHIPTYPE'])
    df = df.drop_duplicates(subset=['MMSI', 'SHIPTYPE','COUNTRYCODE'], keep='first', inplace=False)
    return df
def get_static_file(date):
    month = date
    basepath = r"D:\AIS_2017\2017\static"
    basepath=basepath + r"\month_id=" + str(month) + "_7z"
    for root, dirs, files in os.walk(basepath):
        RES = []
        for name in dirs:
            print(name)
            file_list = glob.glob(os.path.join(os.path.join(root, name), "*.csv"))
            if len(file_list) == 0:
                continue
            thread_num = len(file_list)
            p = Pool(thread_num)
            res = p.map(read_static_dataframe, file_list)
            p.close()
            p.join()
            res = pd.concat(res)
            res = res.drop_duplicates(subset=['MMSI', 'SHIPTYPE', 'COUNTRYCODE'], keep='first', inplace=False)
            res.to_hdf(r"D:\AIS_TEMP\AIS_SHIPTYPE_COUNTRYCODE\\"+name+".h5",key='MMSI', mode='w')


if __name__ == '__main__':
    YEAR=2017
    for i in range(1,13):
        date=str(YEAR)+str(i).zfill(2)
        get_static_file(date)

