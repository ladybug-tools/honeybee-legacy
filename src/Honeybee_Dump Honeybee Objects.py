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
Dump Honeybee Objects

Use this component to dump Honeybee objects to a file on your system.
You can use load Honeybee objects to load the file to Grasshopper.
WARNING: The component is WIP and it doesn't currently save the following properites:
    1) custom schedules
    2) custom materials
    3) hvac airDetails, heatingDetails, coolingDetails
    4) adjacencies between zones
-
Provided by Honeybee 0.0.60

    Args:
        _HBObjects: A list of Honeybee objects
        _filePath: A valid path to a file on your drive (e.g. c:\ladybug\20ZonesExample.HB)
        _dump: Set to True to save the objects to file
    Returns:
        readMe!: ...
        filePath: The location of the file where the HBZones have been saved.
"""

ghenv.Component.Name = "Honeybee_Dump Honeybee Objects"
ghenv.Component.NickName = 'dumpHBObjects'
ghenv.Component.Message = 'VER 0.0.60\nNOV_18_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.59\nFEB_12_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import cPickle as pickle
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
from pprint import pprint

def dumpHBObjects(HBObjects):
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjects = hb_hive.callFromHoneybeeHive(HBObjects)
    ids = [HBObject.ID for HBObject in HBObjects]
    # a global dictonary to collect data
    objs = {}
    idsToBeChecked = {}
    
    def dumpHBZone(HBZone):
        if HBZone.objectType != 'HBZone': return
        
        # dump all surfaces and replace surfaces with ids
        surfaceIds = [srf.ID for srf in HBZone.surfaces]
        for surface in HBZone.surfaces:
            dumpHBSurface(surface)
        HBZone.surfaces = surfaceIds
        
        # dump the HVAC system.
        hvacID = HBZone.HVACSystem.ID
        HBZone.HVACSystem.airDetails = None
        HBZone.HVACSystem.heatingDetails = None
        HBZone.HVACSystem.coolingDetails = None
        objs[hvacID] = HBZone.HVACSystem.__dict__
        HBZone.HVACSystem = hvacID
        
        objs[HBZone.ID] = HBZone.__dict__
    
    def dumpHBSurface(HBSurface):
        
        # replace parent object with it's ID
        if HBSurface.parent != None:
            # make sure parent object is also in the list
            idsToBeChecked[HBSurface.parent.ID] = HBSurface.parent.name
            # replace parent object with ID
            HBSurface.parent = HBSurface.parent.ID
            
        if not HBSurface.isChild and HBSurface.hasChild:
            childIds = [childSrf.ID for childSrf in HBSurface.childSrfs]
            for childSrf in HBSurface.childSrfs:
                dumpHBSurface(childSrf)
            
            HBSurface.childSrfs = childIds
        
        if HBSurface.type == 6:
            HBSurface.childSrfs = [childSrf.ID for childSrf in HBSurface.childSrfs]
            
        try:
            if HBSurface.BC.lower() in ["outdoors", "ground", "adiabatic"]:
                HBSurface.BCObject.name
                HBSurface.BCObject = "Outdoors" #This will be replaced by Outdoor object in loading
        except:
            # print HBSurface.BC.lower()
            # not out outdoor BC
            pass
        
        # in case the surface is adjacent to another surface
        if hasattr(HBSurface.BCObject, "ID"):
            idsToBeChecked[HBSurface.BCObject.ID] = HBSurface.BCObject.name
            # replace parent object with ID
            HBSurface.BCObject = HBSurface.BCObject.ID
            
        objs[HBSurface.ID] = HBSurface.__dict__
        
    for id, HBO in zip(ids, HBObjects):
        if HBO.objectType == 'HBSurface':
            dumpHBSurface(HBO)
        elif HBO.objectType == 'HBZone':
            dumpHBZone(HBO)
        else:
            raise Exception("Unsupported object! Assure all objects are Honeybee objects")
    
    # make sure all the parent objects and boundary condition objects are included
    # in the file
    keys = objs.keys()
    for id, name in idsToBeChecked.iteritems():
        assert id in keys,\
            " InputError: Parent/Adjacent object %s is not in the list of HBObjects."%name
            
    return {'ids':ids, 'objs': objs}

def main(HBObjects, filePath, dump):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1        
    if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    
    if not dump: return -1
    
    if not os.path.isdir(os.path.split(filePath)[0]):
        raise ValueError("Can't find %s"%os.path.split(filePath)[0])
    
    HBData = dumpHBObjects(HBObjects)
    
    with open(filePath, "wb") as outf:
        pickle.dump(HBData, outf)
        print "Saved file to %s"%filePath
    return filePath

filePath = main(_HBObjects, _filePath, _dump)