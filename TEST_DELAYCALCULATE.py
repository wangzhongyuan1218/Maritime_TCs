import numpy as np
from scipy import stats
import matplotlib.mlab as mlab
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas as pd
def getU(speed):
    U=[]
    STD=[]
    for i in range(0, speed.shape[1]):
        arr = speed[:, i]
        ii = np.argwhere(arr == -1)
        arr = np.delete(arr, ii, 0)
        if arr.shape[0]==0:
            u=0
            std=0
        else:
            u = arr.mean()  # 计算均值
            std = arr.std()  # 计算标准差
        U.append(u)
        STD.append(std)
    """
    result=stats.kstest(arr, 'norm', (u, std))
    result = stats.normaltest(arr)
    print(result)
    samples = np.random.normal(u, std,1000)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    n,bins,patches=ax.hist(samples,30,color='orange')
    y = norm.pdf(bins, u, std)
    ax2 = ax.twinx()
    ax2.plot(bins, y, 'r--', color='black')
    plt.title("{0}*{0}——mean:{1},std:{2}".format(i+1,u,std))
    plt.show()
    #print(samples)
    """
    U=np.array(U)
    return U,STD
orientpath=r"D:\AIS_TEMP\7\median_orient_"
speedpath=r"D:\AIS_TEMP\7\median_speed_"
U_shiptype=[]
STD_shiptype=[]
ship=np.arange(60,90,1)
ship=ship.tolist()
ship.append(30)
ship=np.sort(ship)
ship=np.arange(-1,256,1)
for i in ship:
    op=orientpath+str(i)+".npy"
    sp=speedpath+str(i)+".npy"
    U1,STD1=getU(np.load(op))
    U2, STD2 = getU(np.load(sp))
    T=U1-U2
    T[T<0]=2
    U_shiptype.append(T)


dataframe=pd.DataFrame(U_shiptype,columns=['w1','w2','w3','w4','w5','w6','w7'])
dataframe['shiptype']=np.arange(-1,256,1)
#dataframe.set_index('shiptype',inplace=True)
print(dataframe)
df=dataframe[dataframe['shiptype']==30]
con="Fish:{0},{1},{2},{3},{4},{5},{6}".format(np.nanmean(df.w1.values),np.nanmean(df.w2.values),np.nanmean(df.w3.values),np.nanmean(df.w4.values),np.nanmean(df.w5.values),np.nanmean(df.w6.values),np.nanmean(df.w7.values))
print(con)

df=dataframe[(dataframe['shiptype']<=89) & (dataframe['shiptype']>=80)]
con="Tanker:{0},{1},{2},{3},{4},{5},{6}".format(np.nanmean(df.w1.values),np.nanmean(df.w2.values),np.nanmean(df.w3.values),np.nanmean(df.w4.values),np.nanmean(df.w5.values),np.nanmean(df.w6.values),np.nanmean(df.w7.values))
print(con)
df=dataframe[(dataframe['shiptype']<=79) & (dataframe['shiptype']>=70)]
con="Cargo:{0},{1},{2},{3},{4},{5},{6}".format(np.nanmean(df.w1.values),np.nanmean(df.w2.values),np.nanmean(df.w3.values),np.nanmean(df.w4.values),np.nanmean(df.w5.values),np.nanmean(df.w6.values),np.nanmean(df.w7.values))
print(con)

df=dataframe[(dataframe['shiptype']<=69) & (dataframe['shiptype']>=60)]
con="Passenger:{0},{1},{2},{3},{4},{5},{6}".format(np.nanmean(df.w1.values),np.nanmean(df.w2.values),np.nanmean(df.w3.values),np.nanmean(df.w4.values),np.nanmean(df.w5.values),np.nanmean(df.w6.values),np.nanmean(df.w7.values))
print(con)

df=dataframe[(dataframe['shiptype']<=49) & (dataframe['shiptype']>=40)]
con="High speed craft:{0},{1},{2},{3},{4},{5},{6}".format(np.nanmean(df.w1.values),np.nanmean(df.w2.values),np.nanmean(df.w3.values),np.nanmean(df.w4.values),np.nanmean(df.w5.values),np.nanmean(df.w6.values),np.nanmean(df.w7.values))
print(con)
"""
U_shiptype=np.array(U_shiptype).T
for i in range(0,8):
    sns.barplot(x=ship,y=U_shiptype[1])
    plt.title("{0}*{0}".format((i+1)))
    plt.ylim(0.5,4)
    plt.show()
"""
#plt.imshow(U_shiptype)

#sns.heatmap(U_shiptype,cmap="RdPu")
import glob
import os
TYPHOON_GRID=r"D:\AIS_TEMP\Typhoon_context\\"
file_list = glob.glob(os.path.join(TYPHOON_GRID, "*.csv"))
DATE=[]
for item in file_list:
    date=os.path.split(item)[1].split('.')[0]
    DATE.append(date)
print(len(DATE))
for i in range(-1,256):
    op = orientpath + str(i) + ".npy"
    sp = speedpath + str(i) + ".npy"
    op=(np.load(op))
    sp=np.load(sp)
    op=pd.DataFrame(op,columns=['o_w1','o_w2','o_w3','o_w4','o_w5','o_w6','o_w7'])
    sp=pd.DataFrame(sp,columns=['s_w1','s_w2','s_w3','s_w4','s_w5','s_w6','s_w7'])
    res = pd.concat([op,sp],axis=1)
    res['date']=DATE
    res=res[(res['o_w1']>0) |(res['o_w2']>0)|(res['o_w3']>0)|(res['o_w4']>0)|(res['o_w5']>0)|(res['o_w6']>0)|(res['o_w7']>0)]
    res = res[(res['s_w1'] >0) | (res['s_w2'] >0) | (res['s_w3']>0) | (res['s_w4'] >0) | (res['s_w5'] >0) | (res['s_w6'] >0) | (res['s_w7'] >0)]
    res['delay_w1']=res['o_w1']-res['s_w1']
    res['delay_w2'] = res['o_w2'] - res['s_w2']
    res['delay_w3'] = res['o_w3'] - res['s_w3']
    res['delay_w4'] = res['o_w4'] - res['s_w4']
    res['delay_w5'] = res['o_w5'] - res['s_w5']
    res['delay_w6'] = res['o_w6'] - res['s_w6']
    res['delay_w7'] = res['o_w7'] - res['s_w7']
    #print(res)
    #print(i)
    #res.to_csv(os.path.join(r"D:\AIS_TEMP\7","SHIPTYPE_"+str(i)+".csv"),index=False)



