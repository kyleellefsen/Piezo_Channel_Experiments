# -*- coding: utf-8 -*-
"""
UPDATED JULY 18, 2015


Created on Mon Jun 15 10:58:06 2015

Run this file in spyder, after launching Flika.  Change the file names of the directory, points_file, force_file, and mask_file.  

@author: Kyle Ellefsen
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




''' This is the part that needs to be edited every time '''
directory=   r'E:\Data\Adrija_analysis\Results\2015_05_27_#1\19_2015_05_27_#1'
points_file= os.path.join(directory,'19_2015-05-27 NSCs C1 - 1in75syn dmemF12 10pctFBS_18_points4.txt')
force_file = os.path.join(directory,'18_2015-05-27 NSCs C1 - 1in75syn dmemF12 10pctFBS_17_analyzed16.tif')
mask_file  = os.path.join(directory,'19_2015-05-27_mask.tif') #Mask file is required for simulating points inside the cell and for determining the mean force value inside the cell.










###############################################################################
#############     DON'T EDIT BELOW THIS POINT   ###############################
###############################################################################













if os.environ['COMPUTERNAME']=='KE-PARKER-2014':
    os.chdir(r'C:\Users\Kyle Ellefsen\Documents\GitHub\Flika')
else:
    os.chdir(r'C:\Users\Medha\Dropbox\FLIKA_shared\WinPython-64bit-2.7.6.4\python-2.7.6.amd64\Lib\site-packages\flika')
from FLIKA import *
app = QApplication(sys.argv)
initializeMainGui()
open_file(force_file) # Open the image containing the force measurements
image=g.m.currentWindow.image


def radial_profile(data, center):
    ''' This function gives you the mean value of all the the pixels a given distance away from the 'center' point'''
    x, y = np.indices((data.shape))
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    r = np.round(r).astype(np.int)

    tbin = np.bincount(r.ravel(), data.ravel()) #Count number of occurrences of each value in array of non-negative ints.
    nr = np.bincount(r.ravel()) # the number of pixels at each distance.  This isn't perfectly smooth
    radialprofile = tbin / nr #calculates the average value for each distance
    return radialprofile 


''' 
First, we need to load the file containing points, show the points and create the mask we will use to get the values around each point
'''

pts=np.loadtxt(points_file)
for pt in pts:
    t=0
    g.m.currentWindow.scatterPoints[t].append([pt[1],pt[2]])
g.m.currentWindow.scatterPlot.setPoints(pos=g.m.currentWindow.scatterPoints[t])
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
    mx,my=image.shape
except ValueError: #This happens when there is more than one frame
    mt,mx,my=image.shape
    image=np.squeeze(image[0,:,:]) # Only use the first frame
    


Window(image)
gaussian_blur(2)
threshold(30300) #I came up with this number by looking at it... I don't think there is an emperical (good) way to do this.  Hopefully the values are the same across all the force maps.
#load_roi(roi_file)
#set_value(1,0,0,restrictToOutside=True) #Set everything outside the cell to a value of 1
distances=distance_transform_edt(g.m.currentWindow.image)

'''
Loop through every point, find the corresponding location in the force measurement image, cut out a circle around that point, and get all the values in that circle
'''
for i in np.arange(len(pts)):
    t,x,y=pts[i,:]
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
    cutout_image=image[x0:xf,y0:yf]
    values=cutout_image[np.where(mask2)]
    df['values_mean'][i]=np.mean(values)
    df['Number of Values'][i]=len(values)
    df['values_std'][i]=np.std(values)
    df['Minimum value'][i]=np.min(values)
    df['Distance to nearest dark region'][i]=distances[x,y]
    radial_profiles.append(radial_profile(image[:,10:240],pts[i,1:]-[0,10])) #cut out the top and bottom pixels which are too high and too low
    
    
'''Now let's simulate random points located inside our cell outline and compute values for those.'''
open_file(mask_file)
g.m.currentWindow.image[:,:10]=0
g.m.currentWindow.image[:,250:]=0

pts_inside=np.where(g.m.currentWindow.image)
xx,yy=pts_inside
values_mean=[]
values_std=[]
min_val=[]
dist_to_dark=[]
for i in np.arange(10000):  #Simulate 10000 points
    ii=random.randint(0,len(xx))
    x=xx[i]
    y=yy[i]
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
    cutout_image=image[x0:xf,y0:yf]
    values=cutout_image[np.where(mask2)]
    values_mean.append(np.mean(values))
    values_std.append(np.std(values))
    min_val.append(np.min(values))
    dist_to_dark.append(distances[x,y])

df['Simulated mean of mean values']=np.mean(values_mean)
df['Simulated mean of std of mean values']=np.mean(values_std)
df['Simulated mean of minimum values'] = np.mean(min_val)
df['Simulated mean of distances to nearest dark region'] = np.mean(dist_to_dark)
df['Mean value inside cell mask'] = np.mean(image[pts_inside])

df2=pd.DataFrame(index=np.arange(200)) #this will store all the radial profiles, up to 200 pixels away
for i in np.arange(len(pts)):
    pt=pts[i]
    df2[np.str(pt)]=radial_profiles[i][:200]
    
p=plot()
for i, profile in enumerate(radial_profiles):
    p.plot(profile, pen=pg.mkPen(pg.intColor(i)))
p.plot(len(profile)*[df['Mean value inside cell mask'][0]],pen=pg.mkPen('y'))
    
'''
Finally, we can save the results in an Excel file.
'''
o_filename=os.path.splitext(force_file)[0]+'.xlsx'
writer=pd.ExcelWriter(o_filename)
df.to_excel(writer,'Force Data')
df2.to_excel(writer,'Radial Profiles')
writer.save()