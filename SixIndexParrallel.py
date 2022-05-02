import pandas as pd;
import geopandas as gpd;
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
import numpy as np
import os


H=pd.read_csv(r"D:\AIS_TEMP\19\window=7,shiptype=ALL.csv")
data=gpd.read_file(r"D:\AIS_TEMP\21\Port_CONTINEL.shp")
data=pd.DataFrame(data,columns=['NAME','CONTINENT']);

H=H.merge(data,how='left',on='NAME');
H=pd.DataFrame(H,columns=['CONTINENT','H', 'H_deg', 'H_clu', 'H_F_DELAY', 'H_T_DELAY'])
H=H.replace(np.nan,0);
H=H.replace(np.inf,0);
H=H.replace(-np.inf,0);
print(H)
#H['H']=(H['H']-H['H'].min())/(H['H'].max()-H['H'].min())
#H['H_deg']=(H['H_deg']-H['H_deg'].min())/(H['H_deg'].max()-H['H_deg'].min())
#H['H_clu']=(H['H_clu']-H['H_clu'].min())/(H['H_clu'].max()-H['H_clu'].min())
#H['H_F_DELAY']=(H['H_F_DELAY']-H['H_F_DELAY'].min())/(H['H_F_DELAY'].max()-H['H_F_DELAY'].min())
#H['H_T_DELAY']=(H['H_T_DELAY']-H['H_T_DELAY'].min())/(H['H_T_DELAY'].max()-H['H_T_DELAY'].min())
H['H']=H['H']*10;
H['H_clu']=H['H_clu']*100;
H['H_F_DELAY']=H['H_F_DELAY']*10;
H['H_T_DELAY']=H['H_T_DELAY']*10;
print(H.columns)
parallel_coordinates(H,'CONTINENT',colormap='summer',alpha=0.3);
plt.show()
title='Asia';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Orange'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()
print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

title='Europe';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Green'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()

print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

title='Africa';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Blue'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()

print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

title='South America';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Pink'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()
print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

title='North America';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Gray'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()

print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());


title='Australia';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['Brown'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()
print(title);
print(D.H.mean());
print(D.H_deg.median());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

title='Oceania';
D=H[H['CONTINENT']==title]
parallel_coordinates(D,'CONTINENT',color=['limegreen'],alpha=0.3);
plt.title(title);
path=r"D:\wangzhongyuan\NC图片绘制\SVG"
plt.savefig(os.path.join(path,title+".svg"));
plt.show()
print(title);
print(D.H.mean());
print(D.H_deg.mean());
print(D.H_clu.mean());
print(D.H_F_DELAY.mean());
print(D.H_T_DELAY.mean());

H=H.replace(0,np.nan);
H=H.dropna();
H=H.groupby('CONTINENT').median();
print(H)


#显示所有列
pd.set_option('display.max_columns', None)

#显示所有行
pd.set_option('display.max_rows', None)
H=H.T
print(H)
