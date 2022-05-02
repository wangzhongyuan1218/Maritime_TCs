import geopandas as gpd
import pandas as pd
import  pyproj

from adjustText import adjust_text
import matplotlib.pyplot as plt
import os
import glob
from shapely.geometry import Point
basepath=r"D:\AIS_TEMP\21\Moran"
valuepath=r"D:\AIS_TEMP\21"
file_list=glob.glob(os.path.join(basepath,"*.shp"))
path=r"D:\ZXK\PORT_COUNTRY.csv"
portPD=pd.read_csv(path);
xy = [Point(xy) for xy in zip(portPD.LON,portPD.LAT)]
portPD = gpd.GeoDataFrame(portPD,geometry=xy)
portPD.crs = pyproj.CRS.from_user_input('EPSG:4326')  # 给输出的shp增加投影
portPD.to_crs(pyproj.CRS.from_user_input('epsg:3857'),inplace=True)
portPD['geometry']=portPD['geometry'].buffer(10)
legend_kwds={
    'orientation':'horizontal'
}
COLUMN='H'
for item in file_list:

    name=os.path.split(item)[1].split('.')[0].split('LL_')[1]
    """
    if(name!=COLUMN):
        continue
    """
    data=gpd.read_file(item)
    data=gpd.sjoin(data,portPD,how='inner')
    data.to_crs(pyproj.CRS.from_user_input('EPSG:4326'),inplace=True)
    data=data[data['COType']=='LH']
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world['name'] = world['name'].apply(lambda x: 'China' if x == 'Taiwan' else x)
    #ax = world.plot(color="white", edgecolor='0.5')
    column='H'
    if "H" in data.columns:
        column='H'
    elif 'H_deg' in data.columns:
        column='H_deg'
        continue
    elif 'H_clu' in data.columns:
        column='H_clu'
        continue
    elif 'H_T_DELAY' in data.columns:
        column='H_T_DELAY'
    else:
        column='H_F_DELAY'
    #data.plot(ax=ax,column=column,legend=True,legend_kwds=legend_kwds)
    #plt.title(name+":"+str(len(data)))
    #plt.show()


    """
    data_group=data.groupby('COUNTRY')
    for index,row in data_group:
        print(index)
        print(row['NAME'].values)
    """
    world1=world[world['name']=='India']
    ax = world1.plot(color="white", edgecolor='0.5')
    data_group=data[data['COUNTRY']=='India']

    data_group.plot(ax=ax, column=column, legend=True, legend_kwds=legend_kwds)

    x=data_group.geometry.x.values
    y=data_group.geometry.y.values
    name1=data_group.NAME.values
    print(name)
    print(name1)

    new_texts = [plt.text(x_, y_, text, fontsize=12) for x_, y_, text in zip(x, y, name1)]
    adjust_text(new_texts,
                only_move={'text': 'x'},
                arrowprops=dict(arrowstyle='-', color='grey'),
                save_steps=True)
    plt.title(name)
    plt.show()


