# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 07:39:44 2015

@author: Kyle Ellefsen
"""


import os, sys
import numpy as np
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import random
import bz2
from scipy.ndimage.filters import convolve
import cPickle as pickle



def pts2line(pts):
    line=list(pts[0].coords)
    for i in np.arange(1,len(pts)):
        line.extend(pts[i].coords)
    return LineString(line)
    
def getBoundaries(corners):
    tmp=corners[corners[:,0].argsort()]
    left=tmp[:2,:]
    right=tmp[2:,:]
    tmp=left[left[:,1].argsort()]
    top_left=tmp[0,:]
    bottom_left=tmp[1,:]
    tmp=right[right[:,1].argsort()]
    top_right=tmp[0,:]
    bottom_right=tmp[1,:]
    lines=[]
    lines.append(LineString([top_right,bottom_right]))
    lines.append(LineString([bottom_right,bottom_left]))
    lines.append(LineString([bottom_left,top_left]))
    lines.append(LineString([top_left,top_right]))
    return lines
    
def getPolygon(corners):
    tmp=corners[corners[:,0].argsort()]
    left=tmp[:2,:]
    right=tmp[2:,:]
    tmp=left[left[:,1].argsort()]
    top_left=tmp[0,:]
    bottom_left=tmp[1,:]
    tmp=right[right[:,1].argsort()]
    top_right=tmp[0,:]
    bottom_right=tmp[1,:]
    a=top_right
    b=bottom_right
    c=bottom_left
    d=top_left
    p=Polygon([a,b,c,d])
    return p
    
def getTopLeftPt(corners):
    tmp=corners[corners[:,0].argsort()]
    left=tmp[:2,:]
    tmp=left[left[:,1].argsort()]
    top_left=tmp[0,:]
    return top_left
    
def dist_to_nearest_corner(pt,corners):
    tmp=[]
    for corner in corners:
        tmp.append(Point(corner).distance(Point(pt)))
    distance_pixels=min(tmp)
    return distance_pixels
    
def dist_to_nearest_edge(pt,edges):
    tmp=[]
    for line in edges:
        tmp.append(line.distance(Point(pt)))
    distance_pixels=min(tmp)
    return distance_pixels

if os.environ['COMPUTERNAME']=='KE-PARKER-2014':
    sys.path.insert(1,r'C:\Users\Kyle Ellefsen\Documents\GitHub\Flika')
    from Flika import *
    directory=r'Y:\Medha\2015_04_29_Medha_square_SC27\Flika_analysis_mp_2015_09_29'
    os.chdir(directory)
    
else:
    #directory=r'Z:\Medha\2015_04_29_Medha_square_SC27\Flika_analysis_mp_2015_09_29'
    os.chdir(directory)

microns_per_pixel=.4   
trials=[os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1]=='.py']
try:
    trials.remove('trial14_2015_04_29') #this cell doesn't have 4 corners
except ValueError:
    pass
try:
    trials.remove('trial26_2015_04_29') #the edges of this cell were outside the FOV
    trials.remove('trial28_2015_04_29') #the edges of this cell were outside the FOV
except ValueError:
    pass


'''
Count the number of localization in all files
'''
nLocalizations=0
pts=[]
for trial in trials:
    #points_file=trial+'_flika_pts.txt'
    flika_file=trial+'.flika'
    with bz2.BZ2File(flika_file, 'rb') as f:
        print('Loading flika file: {}'.format(flika_file))
        persistentInfo=pickle.load(f)    
    
    for puff in persistentInfo.puffs.values():
        if puff['trashed']==False:
            k=puff['kinetics']
            if os.path.basename(directory)=='Flika_analysis_mp_2015_09_28': # This is the folder Medha analyzed before we started mean_filter(10) on the data_window.  Need to perform that operation now
                trace=convolve(puff['trace'],weights=np.full((10),1.0/10))
                start=k['t_start']-k['before']
                if start<0:
                    start=0
                end=k['t_end']-k['before']
                peak=np.max(trace[start:end])
                k['amplitude']=peak-trace[start]
            pts.append({'filename':trial,'t_peak':k['t_peak'],'x':k['x'],'y':k['y'],'amplitude':k['amplitude'],'sigma':k['sigma']})
            nLocalizations+=1
    #localizations=np.loadtxt(points_file)[:,1:]

'''
Now let's create the dataframe we will use to store our output data
'''
df=pd.DataFrame(index=np.arange(nLocalizations))
pd.options.mode.chained_assignment = None
df['filename']=np.nan
df['cell area (um2)']=np.nan
df['x']=np.nan
df['y']=np.nan
df['amplitude (df/f)']=np.nan
df['sigma for gaussian (pixels)']=np.nan
df['distance_to_corner (um)']=np.nan
df['distance_to_edge (um)']=np.nan
df['distance_to_corner (um) (simulated)']=np.nan
df['distance_to_edge (um) (simulated)']=np.nan
ii=0
for trial in trials:
    print(trial)
    corners_file=trial+'_corners.txt'
    corners=np.loadtxt(corners_file)[:,1:]
    edges=getBoundaries(corners)
    poly=getPolygon(corners)
    area_pixels=poly.area
    cell_area=area_pixels*microns_per_pixel**2
    
    #simulate a lot of points, get the mean distance to nearest corner and nearest edge
    j=0
    distance_to_corners=[]
    distance_to_edges=[]
    while j<1000:
        pt=Point([random.uniform(np.min(corners[:,0]),np.max(corners[:,0])),random.uniform(np.min(corners[:,1]),np.max(corners[:,1]))])
        if poly.contains(pt):
            j+=1
            distance_to_corners.append(dist_to_nearest_corner(pt,corners)*microns_per_pixel)
            distance_to_edges.append(dist_to_nearest_edge(pt,edges)*microns_per_pixel)
    df['distance_to_corner (um) (simulated)'][ii]=np.mean(distance_to_corners)
    df['distance_to_edge (um) (simulated)'][ii]=np.mean(distance_to_edges)
            
    # Get distance to nearest corner and nearest edge
    topLeftPt=getTopLeftPt(corners)
    for pt in pts:
        if pt['filename']==trial:
            df['filename'][ii]=pt['filename']
            df['cell area (um2)'][ii]=cell_area
            x=pt['x']; y=pt['y']
            df['x'][ii]=x-topLeftPt[0]
            df['y'][ii]=y-topLeftPt[1]
            df['distance_to_corner (um)'][ii]=dist_to_nearest_corner([x,y],corners)*microns_per_pixel
            df['distance_to_edge (um)'][ii]=dist_to_nearest_edge([x,y],edges)*microns_per_pixel
            df['sigma for gaussian (pixels)'][ii]=pt['sigma']
            df['amplitude (df/f)'][ii]=pt['amplitude']
            ii+=1
            
    #get area
    
'''
Finally, we can save the results in an Excel file.
'''
o_filename='Square_Cell_data.xlsx'
writer=pd.ExcelWriter(o_filename)
df.to_excel(writer,'Square_Cell_Data')
writer.save()









''' Probably not needed scrap code

import bz2
if sys.version_info.major==2:
    import cPickle as pickle # pickle serializes python objects so they can be saved persistantly.  It converts a python object into a savable data structure
else:
    import pickle
if os.environ['COMPUTERNAME']=='KE-PARKER-2014':
    os.chdir(r'C:\Users\Kyle Ellefsen\Documents\GitHub\Flika')
else:
    os.chdir(r'C:\Users\Medha\Documents\GitHub\Flika')
from FLIKA import *

'''