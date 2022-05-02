import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import geopandas as gpd
import os
import glob
import matplotlib.pyplot as plt
TEMP_16=r"D:\AIS_TEMP\16"
file_list=glob.glob(os.path.join(TEMP_16,"*.shp"))
print(file_list)
legend_kwds = {
        'loc': 'lower center',
        'title': 'LEGEND',
        'shadow': True,
        'ncol':5,
        #'markerscale':9,
        #'fontsize':5

    }
for item in file_list:
    file=gpd.read_file(item)
    file.plot(column='DEGREE',scheme='NaturalBreaks', legend=True)
    title=os.path.split(item)[1].split(".")[0]
    title="DEGREE_"+title.split("_")[1]+"_"+title.split("_")[2]
    plt.title(title)
    plt.savefig(os.path.join(r"D:\AIS_TEMP\IMAGES", title + ".jpg"))
    plt.show()
    file.plot(column='CLUSTER_C', scheme='NaturalBreaks', legend=True)
    title = os.path.split(item)[1].split(".")[0]
    title = "CLUSTER_" + title.split("_")[1] + "_" + title.split("_")[2]
    plt.title(title)
    plt.savefig(os.path.join(r"D:\AIS_TEMP\IMAGES",title+".jpg"))
    plt.show()