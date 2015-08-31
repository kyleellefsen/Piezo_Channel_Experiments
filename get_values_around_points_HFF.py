# -*- coding: utf-8 -*-
"""
UPDATED by Kyle on AUGUST 27, 2015
UPDATED JULY 18, 2015
Created on Mon Jun 15 10:58:06 2015
@author: Kyle Ellefsen


Run this file in spyder.  The threshold is set to 0, so don't use that data.
"""
from __future__ import division
import numpy as np
from skimage.morphology import disk
from scipy.ndimage.morphology import distance_transform_edt
import pandas as pd
import os
from skimage.draw import polygon
import random
import pyqtgraph as pg
import sys
import bz2
import matplotlib.pylab as plt



''' This is the part that needs to be edited every time '''
directories=[
          r'E:\Data\Force_analysis\Flika\11_2015_05_22_HFF',     
          r'E:\Data\Force_analysis\Flika\14_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\17_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\19_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\22_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\27_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\29_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\31_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\33_2015_05_22_HFF',
          r'E:\Data\Force_analysis\Flika\36_2015_05_22_HFF', 
          ]
          
directory=directories[5]
        

###############################################################################
#############     DON'T EDIT BELOW THIS POINT   ###############################
###############################################################################
'''
with open(values_metadata_file, 'r') as f:
    metadata_txt = f.read()
meta=dict()
for line in metadata_txt.splitlines():
    key,value=line.split('=')
    meta[key]=value'''
meta=dict()
basename=os.path.basename(directory)
meta['points_file']=os.path.join(directory,basename+'_flika_pts.txt')
meta['mask_file']=os.path.join(directory,basename+'_Mask.tif')
meta['force_file']=os.path.join(directory,basename+'_Force.tif')
meta['flika_file']=os.path.join(directory,basename+'.flika')
meta['threshold_value']=0 #float(meta['threshold_value'])

if os.environ['COMPUTERNAME']=='KE-PARKER-2014':
    os.chdir(r'C:\Users\Kyle Ellefsen\Documents\GitHub\Flika')
else:
    os.chdir(r'C:\Users\Medha\Documents\GitHub\Flika')
from FLIKA import *
app = QApplication(sys.argv)
initializeMainGui()
open_file(meta['force_file']) # Open the image containing the force measurements
force_image=g.m.currentWindow.image


def radial_profile(data, center):
    ''' This function gives you the mean value of all the the pixels a given distance away from the 'center' point'''
    x, y = np.indices((data.shape))
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    r = np.round(r).astype(np.int)

    tbin = np.bincount(r.ravel(), data.ravel()) #Count number of occurrences of each value in array of non-negative ints.
    nr = np.bincount(r.ravel()) # the number of pixels at each distance.  This isn't perfectly smooth
    #radialprofile = tbin / nr #calculates the average value for each distance
    #return radialprofile #this was the old way, not cumulative average
    tbin=np.cumsum(tbin)
    nr = np.cumsum(nr)
    radialprofile=tbin/nr
    return radialprofile #this returns the average value in the series of circles

''' 
First, we need to load the file containing points, show the points and create the mask we will use to get the values around each point
'''
pts=None
if os.path.isfile(meta['points_file']): #load the points if they exist
    pts=np.loadtxt(meta['points_file'])
    if pts.shape[1]==3:
        print("You are using an old points file that is missing amplitude info.")
        os.remove(meta['points_file'])
        pts=None
if pts is None:
    if  os.path.isfile(meta['flika_file']): #if the points file doesn't exist, load the flika file and create the points file
        print('Found persistentInfo file.  Extracting points')
        with bz2.BZ2File(meta['flika_file'], 'rb') as f:
            persistentInfo=pickle.load(f)
    pts=[]
    for puff in persistentInfo.puffs.values():
        if puff['trashed']==False:
            k=puff['kinetics']
            pts.append(np.array([k['t_peak'], k['x'], k['y'],k['amplitude']]))
    pts=np.array(pts)
    np.savetxt(meta['points_file'],pts)

#
if pts.shape[0]==1:
    pts=np.array([pts])
for pt in pts:
    g.m.currentWindow.scatterPoints[0].append([pt[1],pt[2]])
    
scat=g.m.currentWindow.scatterPlot
maxValue=2
colors=plt.cm.jet(pts[:,3]/maxValue)*255
brushes=[pg.mkBrush(colors[i,:3]) for i in np.arange(pts.shape[0])]
scat.setPoints(pos=pts[:,1:3],brush=brushes)
radius=5 # radius in pixels
mask=disk(radius=radius)










'''
Now let's create the dataframe we will use to store our output data
'''
df=pd.DataFrame(index=np.arange(len(pts)))
df['t']=pts[:,0]
df['x']=pts[:,1]
df['y']=pts[:,2]
df['values_mean']=np.nan
df['values_std']=np.nan
df['Number of Values']=np.nan
df['Minimum value']=np.nan
df['Distance to nearest dark region']=np.nan
radial_profiles=[]



try:
    mx,my=force_image.shape
except ValueError: #This happens when there is more than one frame
    mt,mx,my=force_image.shape
    force_image=np.squeeze(force_image[0,:,:]) # Only use the first frame

f_image_tmp=np.copy(force_image)
f_image_tmp[:,:10]=np.max(f_image_tmp)
f_image_tmp[:,250:]=np.max(f_image_tmp)
Window(f_image_tmp)
gaussian_blur(2)
threshold(meta['threshold_value']) 
#load_roi(roi_file)
#set_value(1,0,0,restrictToOutside=True) #Set everything outside the cell to a value of 1
distances=distance_transform_edt(g.m.currentWindow.image)
Window(distances)
'''
Loop through every point, find the corresponding location in the force measurement image, cut out a circle around that point, and get all the values in that circle
'''
for i in np.arange(len(pts)):
    t,x,y,amp=pts[i,:]
    x=int(np.round(x))
    y=int(np.round(y))
    x0=x-radius
    xf=x+radius+1
    y0=y-radius
    yf=y+radius+1
    mask2=np.copy(mask)
    center2=[radius,radius]
    if x0<0:
        mask2=mask2[center2[0]-x:,:]
        center2[0]=x
        x0=0
    elif xf>mx:
        crop=-(xf-mx)
        if crop<0:
           mask2=mask2[:crop,:]
        xf=mx
    if y0<0:
        mask2=mask2[:,center2[1]-y:]
        center2[1]=y
        y0=0
    elif yf>my:
        crop=-(yf-my)
        if crop<0:
           mask2=mask2[:,:crop]
        yf=my
    cutout_image=force_image[x0:xf,y0:yf]
    values=cutout_image[np.where(mask2)]
    df['values_mean'][i]=np.mean(values)
    df['Number of Values'][i]=len(values)
    df['values_std'][i]=np.std(values)
    df['Minimum value'][i]=np.min(values)
    df['Distance to nearest dark region'][i]=distances[x,y]
    radial_profiles.append(radial_profile(force_image[:,10:240],pts[i,1:3]-[0,10])) #cut out the top and bottom pixels which are too high and too low
    
    
'''Now let's simulate random points located inside our cell outline and compute values for those.'''
if os.path.isfile(meta['mask_file']):
    open_file(meta['mask_file'])
    g.m.currentWindow.image[:,:10]=0
    g.m.currentWindow.image[:,250:]=0
    
    pts_inside=np.where(g.m.currentWindow.image)
    xx,yy=pts_inside
    values_mean=[]
    values_std=[]
    min_val=[]
    dist_to_dark=[]
    for i in np.arange(10000):  #Simulate 10000 points
        ii=random.randint(0,len(xx)-1)
        x=xx[ii]
        y=yy[ii]
        #g.m.currentWindow.scatterPlot.addPoints(pos=[[x,y]], brush=pg.mkBrush('r'))
        x0=x-radius
        xf=x+radius+1
        y0=y-radius
        yf=y+radius+1
        mask2=np.copy(mask)
        center2=[radius,radius]
        if x0<0:
            mask2=mask2[center2[0]-x:,:]
            center2[0]=x
            x0=0
        elif xf>mx:
            crop=-(xf-mx)
            if crop<0:
               mask2=mask2[:crop,:]
            xf=mx
        if y0<0:
            mask2=mask2[:,center2[1]-y:]
            center2[1]=y
            y0=0
        elif yf>my:
            crop=-(yf-my)
            if crop<0:
               mask2=mask2[:,:crop]
            yf=my
        cutout_image=force_image[x0:xf,y0:yf]
        values=cutout_image[np.where(mask2)]
        values_mean.append(np.mean(values))
        values_std.append(np.std(values))
        min_val.append(np.min(values))
        dist_to_dark.append(distances[x,y])
    
    df['Simulated mean of mean values']=np.mean(values_mean)
    df['Simulated mean of std of mean values']=np.mean(values_std)
    df['Simulated mean of minimum values'] = np.mean(min_val)
    df['Simulated mean of distances to nearest dark region'] = np.mean(dist_to_dark)
    df['Mean value inside cell mask'] = np.mean(force_image[pts_inside])




df2=pd.DataFrame(index=np.arange(200)) #this will store all the radial profiles, up to 200 pixels away
for i in np.arange(len(pts)):
    pt=pts[i]
    df2[np.str(pt)]=radial_profiles[i][:200]
    
p=plot()
for i, profile in enumerate(radial_profiles):
    p.plot(profile, pen=pg.mkPen(pg.intColor(i)))
if os.path.isfile(meta['mask_file']):
    p.plot(len(profile)*[df['Mean value inside cell mask'][0]],pen=pg.mkPen('y'))
    
'''
Finally, we can save the results in an Excel file.
'''
o_filename=os.path.splitext(meta['force_file'])[0]+'.xlsx'
writer=pd.ExcelWriter(o_filename)
df.to_excel(writer,'Force Data')
df2.to_excel(writer,'Radial Profiles')
writer.save()