import pandas as pd
import numpy as np
data=pd.read_csv(r"D:\AIS_TEMP\19\window=7,shiptype=ALL.csv");
print(data.columns)

data['Data1']=(data['F1']*data['F__DELAY1'])/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])
data['Data2']=data['F2']*data['F__DELAY2']/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])
data['Data3']=data['F3']*data['F__DELAY3']/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])
data['Data4']=data['F4']*data['F__DELAY4']/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])
data['Data5']=data['F5']*data['F__DELAY5']/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])
data['Data6']=data['F6']*data['F__DELAY6']/(data['F1']*data['F__DELAY1']+data['F2']*data['F__DELAY2']+data['F3']*data['F__DELAY3']+data['F4']*data['F__DELAY4']+data['F5']*data['F__DELAY5']+data['F6']*data['F__DELAY6'])

#data.fillna(0,inplace=True)
print(np.nanmean(data.Data1.values))
print(np.nanmean(data.Data2.values))
print(np.nanmean(data.Data3.values))
print(np.nanmean(data.Data4.values))
print(np.nanmean(data.Data5.values))
print(np.nanmean(data.Data6.values))


