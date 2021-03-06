# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 20:57:32 2015

@author: Medha
"""

import os, sys
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


directories=[
          r'E:\Data\Force_analysis\Flika\NSC\4_2015_05_27_NSC'
          ]
          
          
directory=directories[0]
basename=os.path.basename(directory)
meta=dict()
meta['points_file']=os.path.join(directory,basename+'_flika_pts.txt')
meta['flika_file']=os.path.join(directory,basename+'.flika')


if  os.path.isfile(meta['flika_file']):
    print('Found .flika file.  Extracting points')
    with bz2.BZ2File(meta['flika_file'], 'rb') as f:
        persistentInfo=pickle.load(f)
pts=[]
for puff in persistentInfo.puffs.values():
    if puff['trashed']==False:
        k=puff['kinetics']
        pts.append(np.array([k['t_peak'], k['x'], k['y']]))
pts=np.array(pts)
np.savetxt(meta['points_file'],pts)
print('Saved points for {}'.format(basename))