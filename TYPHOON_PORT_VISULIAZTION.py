import geopandas as gpd
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
TYPHOON_PATH=r"D:\AIS_TEMP\Typhoon\Typhoon_line_2017.shp"
typhoon=gpd.read_file(TYPHOON_PATH)
TYPHOON=typhoon
typhoon=typhoon[typhoon['STORM_SPD']>=17.5]
SHIPTYPE=["ALL","FISHING",'PASSENGER','CARGO','TANKER']
SID=typhoon.SID.values
SID=np.unique(SID)
TEMP_18=r"D:\AIS_TEMP\18"
legend_kwds = {
        'bbox_to_anchor': (1.3, 1),
    }
for sid in SID:
    temp_typhoon=TYPHOON[TYPHOON['SID']==sid]
    name=temp_typhoon.NAME.values[0]
    for type in SHIPTYPE:
        filename="DEGREE_{0}_7_{1}_{2}.shp".format(sid,name,type)
        title=name+"_"+type
        filename=os.path.join(TEMP_18,filename)
        if not os.path.exists(filename):
            print(name+"bucunzai ")
            continue
        data=gpd.read_file(filename)
        data=data[data['DEG_d']>0]
        if len(data)==0:
            print(name)
            continue

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        plt.figure(figsize=(20, 10))
        ax=world.plot(color="white",edgecolor='0.5')
        data.plot(ax=ax,column="DEG_d",legend=False,scheme='NaturalBreaks',cmap='OrRd',legend_kwds=legend_kwds)
        temp_typhoon.plot(ax=ax,linewidth=5,color='red')
        plt.title(title)
        plt.xlim(-180,180)
        plt.ylim(-90,90)
        plt.show()

