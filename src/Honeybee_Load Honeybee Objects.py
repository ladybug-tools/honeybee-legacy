#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Load Honeybee Objects

Use this component to load Honeybee objects from a file on your system.
The valid files are created by dump Honeybee objects component.
-
Provided by Honeybee 0.0.60

    Args:
        _HBObjects: A list of Honeybee objects
        _filePath: A valid path to a file on your drive (e.g. c:\ladybug\20ZonesExample.HB)
        _load: Set to True to load the objects from the file
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Honeybee_Load Honeybee Objects"
ghenv.Component.NickName = 'loadHBObjects'
ghenv.Component.Message = 'VER 0.0.60\nNOV_18_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.59\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import cPickle as pickle
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import uuid
from Rhino.Geometry import *

class outdoorBCObject(object):
    """
    BCObject for surfaces with outdoor BC
    """
    def __init__(self, name = ""):
        self.name = name


def loadHBObjects(HBData):
    
    hb_EPZone = sc.sticky["honeybee_EPZone"]
    hb_EPSrf = sc.sticky["honeybee_EPSurface"]
    hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
    hb_EPSHDSurface = sc.sticky["honeybee_EPShdSurface"]
    hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
    hb_EPHvac = sc.sticky["honeybee_EPHvac"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # a global dictonary to collect data
    ids = HBData["ids"]
    objs = HBData["objs"]
    HBObjects = {}
    
    def loadHBHvac(HBHvacData):
        HBHvac = hb_EPHvac(HBHvacData['GroupID'], HBHvacData['Index'], HBHvacData['airDetails'], HBHvacData['heatingDetails'], HBHvacData['coolingDetails'])
        # update fields in HBZone
        for key, value in HBHvacData.iteritems():
            HBHvac.__dict__[key] = value
        HBObjects[HBHvac.ID] = HBHvac
    
    def loadHBZone(HBZoneData):
        # programs is set to default but will be overwritten
        HBZone = hb_EPZone(HBZoneData['geometry'], \
                HBZoneData['num'], HBZoneData['name'], \
                ('Office', 'OpenOffice'), HBZoneData['isConditioned'])
                
        # update fields in HBZone
        for key, value in HBZoneData.iteritems():
            HBZone.__dict__[key] = value
        
        HBObjects[HBZone.ID] = HBZone
        
    def loadHBSurface(HBSurfaceData):
        # EPFenSurface
        if HBSurfaceData['type'] == 5:
            HBBaseSurface = HBObjects[HBSurfaceData['parent']]
            HBSurface = hb_EPFenSurface(HBSurfaceData['geometry'], \
                HBSurfaceData['num'], HBSurfaceData['name'], HBBaseSurface, 5)
                
        elif HBSurfaceData['type'] == 6:
            HBSurface = hb_EPSHDSurface(HBSurfaceData['geometry'], \
                HBSurfaceData['num'], HBSurfaceData['name'])
        else:
            HBSurface = hb_EPZoneSurface(HBSurfaceData['geometry'], \
                HBSurfaceData['num'], HBSurfaceData['name'])
        
        for key, value in HBSurfaceData.iteritems():
            HBSurface.__dict__[key] = value
        
        HBObjects[HBSurface.ID] = HBSurface
    
    def updateHoneybeeObjects():
        for id, HBObject in HBObjects.iteritems():
            
            if HBObject.objectType == 'HBZone':
                HBObject.surfaces = [HBObjects[id] for id in HBObject.surfaces]
                HBObject.HVACSystem = HBObjects[HBObject.HVACSystem]
                continue
                
            if HBObject.objectType == 'HBHvac':
                continue
            
            # replace parent ID with the object
            if HBObject.parent != None:
                # replace parent object with ID
                HBObject.parent = HBObjects[HBObject.parent]
                
            if not HBObject.isChild and HBObject.hasChild:
                HBObject.childSrfs = [HBObjects[id] for id in HBObject.childSrfs]
                HBObject.calculatePunchedSurface()
            
            if HBObject.type==6:
                HBObject.childSrfs = [HBObjects[id] for id in HBObject.childSrfs]
                
            if HBObject.type!=6 and HBObject.BCObject.lower() == "outdoors":
                HBObject.BCObject = outdoorBCObject()
                
            if HBObject.type!=6 and HBObject.BC.lower() == "surface":
                # replace parent object with ID
                HBObject.BCObject = HBObjects[HBObject.BCObject]
    
    for id, HBO in objs.iteritems():
        if HBO['objectType'] == 'HBSurface' and HBO['type'] == 5: continue
        if HBO['objectType'] == 'HBSurface' and HBO['type'] != 5:
            loadHBSurface(HBO)
        elif HBO['objectType'] == 'HBZone':
            loadHBZone(HBO)
        elif HBO['objectType'] == 'HBHvac':
            loadHBHvac(HBO)
        else:
            raise Exception("Unsupported object! Assure all objects are Honeybee objects")
    
    # create Fenestration surfaces
    for id, HBO in objs.iteritems():
        if HBO['objectType'] == 'HBSurface' and HBO['type'] == 5:
            loadHBSurface(HBO)
    
    #replace ids with objects in surfaces
    updateHoneybeeObjects()
    
    # return new Honeybee objects
    return hb_hive.addToHoneybeeHive([HBObjects[id] for id in HBData["ids"]], ghenv.Component)


def main(filePath, load):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1        
    if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    
    if not load: return -1
    
    if not os.path.isfile(filePath):
        raise ValueError("Can't find %s"%filePath)
    
    with open(filePath, "rb") as inf:
        return loadHBObjects(pickle.load(inf))
    

results = main(_filePath, _load)

HBObjects = results if results!= -1 else None
