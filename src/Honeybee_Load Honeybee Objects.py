#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Provided by Honeybee 0.0.64

    Args:
        _HBObjects: A list of Honeybee objects
        _filePath: A valid path to a file on your drive (e.g. c:\ladybug\20ZonesExample.HB)
        _load: Set to True to load the objects from the file
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Honeybee_Load Honeybee Objects"
ghenv.Component.NickName = 'loadHBObjects'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.59\nDEC_15_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass

import cPickle as pickle
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import uuid
from Rhino.Geometry import *
import Rhino as rc

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
    hb_airDetail = sc.sticky["honeybee_hvacAirDetails"]
    hb_heatingDetail = sc.sticky["honeybee_hvacHeatingDetails"]
    hb_coolingDetail = sc.sticky["honeybee_hvacCoolingDetails"]
    hb_viewFac = sc.sticky["honeybee_ViewFactors"]
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # a global dictonary to collect data
    ids = HBData["ids"]
    objs = HBData["objs"]
    HBObjects = {}
    
    def loadHBviewFac(HBViewFacInfo):
        # programs is set to default but will be overwritten
        HBViewFac = hb_viewFac()
        # update fields in HBZone
        for key, value in HBViewFacInfo.iteritems():
            HBViewFac.__dict__[key] = value
        HBViewFac.calcNumPts()
        HBObjects[HBViewFac.ID] = HBViewFac
    
    def loadHBEPstr(HBconstrObj):
        EPObject = HBconstrObj['EPstr']
        added, name = hb_EPObjectsAux.addEPObjectToLib(EPObject, True)
    
    def loadHBradMat(HBradMat):
        added, name = hb_RADMaterialAUX.analyseRadMaterials(HBradMat['RADstr'], True, True)
    
    def loadHBHvac(HBHvacData):
        HBHvac = hb_EPHvac(HBHvacData['GroupID'], HBHvacData['Index'], HBHvacData['airDetails'], HBHvacData['heatingDetails'], HBHvacData['coolingDetails'])
        for key, value in HBHvacData.iteritems():
            HBHvac.__dict__[key] = value
        HBObjects[HBHvac.ID] = HBHvac
    
    def loadHBair(HBAirData):
        HBAir = hb_airDetail()
        for key, value in HBAirData.iteritems():
            HBAir.__dict__[key] = value
        HBObjects[HBAir.ID] = HBAir
    
    def loadHBheat(HBHeatData):
        HBHeat = hb_heatingDetail()
        for key, value in HBHeatData.iteritems():
            HBHeat.__dict__[key] = value
        HBObjects[HBHeat.ID] = HBHeat
    
    def loadHBcool(HBCoolData):
        HBCool = hb_coolingDetail()
        for key, value in HBCoolData.iteritems():
            HBCool.__dict__[key] = value
        HBObjects[HBCool.ID] = HBCool
    
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
            elif HBObject.objectType == 'HBHvac':
                if HBObject.airDetails != None:
                    HBObject.airDetails = HBObjects[HBObject.airDetails]
                if HBObject.heatingDetails != None:
                    HBObject.heatingDetails = HBObjects[HBObject.heatingDetails]
                if HBObject.coolingDetails != None:
                    HBObject.coolingDetails = HBObjects[HBObject.coolingDetails]
                continue
            elif HBObject.objectType == 'HBair' or HBObject.objectType == 'HBheat' or HBObject.objectType == 'HBcool':
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
        elif HBO['objectType'] == 'HBair':
            loadHBair(HBO)
        elif HBO['objectType'] == 'HBheat':
            loadHBheat(HBO)
        elif HBO['objectType'] == 'HBcool':
            loadHBcool(HBO)
        elif HBO['objectType'] == 'HBConstr' or HBO['objectType'] == 'HBMat' or HBO['objectType'] == 'HBsched' or HBO['objectType'] == 'HBShdCntrl':
            loadHBEPstr(HBO)
        elif HBO['objectType'] == 'HBRadMat':
            loadHBradMat(HBO)
        elif HBO['objectType'] == 'ViewFactorInfo':
            loadHBviewFac(HBO)
        else:
            print HBO['objectType']
            raise Exception("Unsupported object! Assure all objects are Honeybee objects")
    
    # create Fenestration surfaces
    for id, HBO in objs.iteritems():
        if HBO['objectType'] == 'HBSurface' and HBO['type'] == 5:
            loadHBSurface(HBO)
    
    #replace ids with objects in surfaces
    updateHoneybeeObjects()
    
    #Scale everything if units are not meters.
    if sc.sticky["honeybee_ConversionFactor"] != 1:
        fac = 1/sc.sticky["honeybee_ConversionFactor"]
        NUscale = rc.Geometry.Transform.Scale(rc.Geometry.Plane(rc.Geometry.Plane.WorldXY),fac,fac,fac)
        for obj in HBObjects.keys():
            if HBObjects[obj].objectType == 'HBSurface':
                if HBObjects[obj].type == 6:
                    HBObjects[obj].transform(NUscale, "", False)
            elif HBObjects[obj].objectType == 'HBZone':
                HBObjects[obj].transform(NUscale, "", False)
    
    # return new Honeybee objects
    try:
        return hb_hive.addToHoneybeeHive([HBObjects[id] for id in HBData["ids"]], ghenv.Component)
    except:
        return hb_hive.addNonGeoObjToHive([HBObjects[id] for id in HBData["ids"]][0], ghenv.Component)


def main(filePath):
    if not os.path.isfile(filePath):
        raise ValueError("Can't find %s"%filePath)
    
    with open(filePath, "rb") as inf:
        return loadHBObjects(pickle.load(inf))



#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if initCheck == True and _filePath != None and _load == True:
    results = main(_filePath)
    HBObjects = results if results!= -1 else None
