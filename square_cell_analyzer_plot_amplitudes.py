# -*- coding: utf-8 -*-
"""
Created on Mon Oct 05 14:03:57 2015

@author: Kyle Ellefsen
"""

'''
1) load all data from the two excel spreadsheets
2) open and display template image
3) plot points on 

'''


import os, sys
import numpy as np
import pandas as pd
from matplotlib import cm
import pyqtgraph as pg

jet=cm.get_cmap('jet')
def getColor(amp):
    minAmp=.023
    maxAmp=.2
    if amp<minAmp:
        amp=minAmp
    if amp>maxAmp:
        amp=maxAmp
    norm_amp=(amp-minAmp)/(maxAmp-minAmp) 
    color_1=jet(norm_amp)
    color_255=255*np.array(color_1)
    return color_255

if os.environ['COMPUTERNAME']=='KE-PARKER-2014':
    sys.path.insert(1,r'C:\Users\Kyle Ellefsen\Documents\GitHub\Flika')
    from Flika import *
    app = QApplication(sys.argv)
    initializeMainGui()
    directory1=r'Y:\Medha\2015_04_29_Medha_square_SC27\Flika_analysis_mp_2015_09_28'
    directory2=r'Y:\Medha\2015_04_29_Medha_square_SC27\Flika_analysis_mp_2015_09_29'
    overlay_image_directory=r'D:\Dropbox\Kyle_Medha_share\Actin_images_for_overlay'

df1=pd.read_excel(os.path.join(directory1,'Square_Cell_data_2015_09_28.xlsx'))
df1=df1[df1.filename != 'trial19_2015_04_29'] # because trial19 is duplicated in df2
df2=pd.read_excel(os.path.join(directory2,'Square_Cell_data_2015_09_29.xlsx'))
df=pd.concat([df1,df2],ignore_index=True)

size_dict={ 'trial5_2015_04_29':  'small',
            'trial6_2015_04_29':  'small',
            'trial7_2015_04_29':  'small',
            'trial9_2015_04_29':  'small',
            'trial10_2015_04_29': 'small',
            'trial11_2015_04_29': 'medium',
            'trial12_2015_04_29': 'medium',
            'trial13_2015_04_29': 'medium',
            'trial16_2015_04_29': 'medium',
            'trial17_2015_04_29': 'medium',
            'trial18_2015_04_29': 'medium',
            'trial19_2015_04_29': 'large',
            'trial22_2015_04_29': 'large',
            'trial25_2015_04_29': 'large',
            'trial29_2015_04_29': 'small',
            'trial30_2015_04_29': 'small',
            }
trial_names=df.filename.unique()

small_window=open_file(os.path.join(overlay_image_directory,'Actin_ZProj_AVG_300um_2015_08_03.tif'))
medium_window=open_file(os.path.join(overlay_image_directory,'Actin_ZProj_AVG_1024um_2015_08_03.tif'))
large_window=open_file(os.path.join(overlay_image_directory,'Actin_ZProj_AVG_2025um_2015_08_03.tif'))

for trial in trial_names:
    if size_dict[trial]=='small':
        currentWindow=small_window
        expanding_factor=3.5
        offset=[14,12]
    elif size_dict[trial]=='medium':
        currentWindow=medium_window
        expanding_factor=3.8
        offset=[5,5]
    elif size_dict[trial]=='large':
        currentWindow=large_window
        expanding_factor=4.0
        offset=[0,0]
    df_trial=df[df.filename==trial]
    xs=np.array(df_trial.x)*expanding_factor+offset[0]
    ys=np.array(df_trial.y)*expanding_factor+offset[1]
    amps=np.array(df_trial['amplitude (df/f)'])
    brushes=[pg.mkBrush(getColor(amp)) for amp in amps]
    currentWindow.scatterPlot.addPoints(x=xs,y=ys,brush=brushes)
    








