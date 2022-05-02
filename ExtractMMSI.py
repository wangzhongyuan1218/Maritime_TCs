import numpy as np
from multiprocessing import Pool
import glob
import os
TMEP2_PATH=r"D:\AIS_TEMP\2"#存储唯一MMSI号信息
TMEP2_PATH=r"D:\AIS_TEMP\1"#存储唯一MMSI号信息
"""
file_list=glob.glob(os.path.join(TMEP2_PATH,"*.npy"))
MMSI=[0]
MMSI=np.array(MMSI)
print(file_list)

for item in file_list:
    print(item)
    temp=np.load(item)
    MMSI=np.union1d(MMSI,temp)

np.save(os.path.join(TMEP2_PATH,'MMSI_ALL'),MMSI)
"""