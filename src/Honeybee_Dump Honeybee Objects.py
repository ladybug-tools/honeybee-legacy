#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
WARNING: This component does not write custom schedules or materials within the file but it does write the names of the constructions and schedules.
Accordingly, to properly load objects agian, you must connect the full strings of these objects to a "Add to EnergyPlus Library" component in any GH cript that loads the HBZones from the file.

-
Provided by Honeybee 0.0.61

    Args:
        _HBObjects: A list of Honeybee objects
        _fileName: A name for the file to which HBObjects will be written (e.g. 20ZonesExample.HB).
        _workingDir_: An optional working directory into which the HBZones will be written.  The default is set to C:\ladybug.
        _dump: Set to True to save the objects to file
    Returns:
        readMe!: ...
        filePath: The location of the file where the HBZones have been saved.
"""

ghenv.Component.Name = "Honeybee_Dump Honeybee Objects"
ghenv.Component.NickName = 'dumpHBObjects'
ghenv.Component.Message = 'VER 0.0.61\nMAY_19_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.59\nMAY_18_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import cPickle as pickle
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import uuid


def dumpHBObjects(HBObjects, fileName, workingDir=None):
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
    hb_ConstrLib = sc.sticky ["honeybee_constructionLib"]
    if workingDir == None:
        workingDir = sc.sticky["Honeybee_DefaultFolder"] 
    if not fileName.upper().endswith('.HB.'):
        fileName = fileName + '.HB'
    defaultEPConstrSet = ['INTERIOR CEILING', 'INTERIOR DOOR', 'INTERIOR FLOOR', 'INTERIOR PARTITION', \
        'INTERIOR WALL', 'INTERIOR WINDOW', 'EXTERIOR DOOR', 'EXTERIOR FLOOR', 'EXTERIOR ROOF', \
        'EXTERIOR WALL', 'EXTERIOR WINDOW']
    defaultRADmaterials = ['CONTEXT_MATERIAL', 'EXTERIOR_FLOOR', 'EXTERIOR_ROOF', 'EXTERIOR_WALL', \
        'EXTERIOR_WINDOW', 'INTERIOR_CEILING', 'INTERIOR_FLOOR', 'INTERIOR_WALL', 'INTERIOR_WINDOW']
    
    filePath = os.path.join(workingDir, fileName)
    
    if not os.path.isdir(os.path.split(filePath)[0]):
        raise ValueError("Can't find %s"%os.path.split(filePath)[0])
    
    HBObjects = hb_hive.callFromHoneybeeHive(HBObjects)
    ids = [HBObject.ID for HBObject in HBObjects]
    # a global dictonary to collect data
    objs = {}
    idsToBeChecked = {}
    
    # Objects to write back to the memory of the document.
    constructions = []
    EPmaterials = []
    RADmaterials = []
    hvacIDs = []
    airIDs = []
    heatIDs = []
    coolIDs = []
    
    def dumpHBZone(HBZone):
        if HBZone.objectType != 'HBZone': return
        
        # dump all surfaces and replace surfaces with ids
        surfaceIds = [srf.ID for srf in HBZone.surfaces]
        for surface in HBZone.surfaces:
            dumpHBSurface(surface)
        HBZone.surfaces = surfaceIds
        
        # dump the HVAC system.
        if HBZone.HVACSystem.ID not in hvacIDs:
            dumpHBhvac(HBZone.HVACSystem)
        HBZone.HVACSystem = HBZone.HVACSystem.ID
        
        # dump all other objects in the zone.
        objs[HBZone.ID] = HBZone.__dict__
    
    def dumpHBSurface(HBSurface):
        # replace parent object with it's ID
        if HBSurface.parent != None:
            # make sure parent object is also in the list
            idsToBeChecked[HBSurface.parent.ID] = HBSurface.parent.name
            # replace parent object with ID
            HBSurface.parent = HBSurface.parent.ID
        
        # dump windows
        if not HBSurface.isChild and HBSurface.hasChild:
            childIds = [childSrf.ID for childSrf in HBSurface.childSrfs]
            for childSrf in HBSurface.childSrfs:
                dumpHBSurface(childSrf)
            HBSurface.childSrfs = childIds
        
        # dump custom constructions.
        if HBSurface.EPConstruction != None and HBSurface.EPConstruction.upper() not in constructions and HBSurface.EPConstruction.upper() not in defaultEPConstrSet:
            constructions.append(HBSurface.EPConstruction.upper())
            materials = dumpHBConstr(HBSurface.EPConstruction.upper())
            for mat in materials:
                if mat.upper() not in EPmaterials:
                    EPmaterials.append(mat.upper())
                    dumpHBMat(mat.upper())
        
        # dump custom RAD materials.
        if HBSurface.RadMaterial != None and HBSurface.RadMaterial.upper() not in RADmaterials and HBSurface.RadMaterial.upper() not in defaultRADmaterials:
            RADmaterials.append(HBSurface.RadMaterial.upper())
            dumpHBRad(HBSurface.RadMaterial)
        
        # Shading surfaces.
        if HBSurface.type == 6:
            HBSurface.childSrfs = [childSrf.ID for childSrf in HBSurface.childSrfs]
        
        try:
            if HBSurface.BC.lower() in ["outdoors", "ground", "adiabatic"]:
                HBSurface.BCObject = "Outdoors" #This will be replaced by the correct object on loading
        except:
            pass
        
        # in case the surface is adjacent to another surface
        if hasattr(HBSurface.BCObject, "ID"):
            idsToBeChecked[HBSurface.BCObject.ID] = HBSurface.BCObject.name
            # replace parent object with ID
            HBSurface.BCObject = HBSurface.BCObject.ID
        
        objs[HBSurface.ID] = HBSurface.__dict__
    
    def dumpHBhvac(HBhvac):
        hvacID = HBhvac.ID
        if HBhvac.airDetails != None:
            airID = HBhvac.airDetails.ID
            airDetailsDict = HBhvac.airDetails.__dict__
            del airDetailsDict['sysProps']
            HBhvac.airDetails = airID
            if airID not in airIDs:
                airIDs.append(airID)
                objs[airID] = airDetailsDict
        
        if HBhvac.heatingDetails != None:
            heatID = HBhvac.heatingDetails.ID
            heatingDetailsDict = HBhvac.heatingDetails.__dict__
            del heatingDetailsDict['sysProps']
            HBhvac.heatingDetails = heatID
            if heatID not in heatIDs:
                heatIDs.append(heatID)
                objs[heatID] = heatingDetailsDict
        
        if HBhvac.coolingDetails != None:
            coolID = HBhvac.coolingDetails.ID
            coolingDetailsDict = HBhvac.coolingDetails.__dict__
            del coolingDetailsDict['sysProps']
            HBhvac.coolingDetails = coolID
            if coolID not in coolIDs:
                coolIDs.append(coolID)
                objs[coolID] = coolingDetailsDict
        
        if hvacID not in hvacIDs:
            hvacIDs.append(hvacID)
            objs[hvacID] = HBhvac.__dict__
    
    def dumpHBConstr(constructionName):
        constructionData = hb_ConstrLib[constructionName]
        constrMats = []
        numberOfLayers = len(constructionData.keys())
        constructionStr = constructionData[0] + ",\n"
        constructionStr =  constructionStr + "  " + constructionName + ",   !- name\n"
        for layer in range(1, numberOfLayers):
            if layer < numberOfLayers-1:
                constructionStr =  constructionStr + "  " + constructionData[layer][0] + ",   !- " +  constructionData[layer][1] + "\n"
            else:
                constructionStr =  constructionStr + "  " + constructionData[layer][0] + ";   !- " +  constructionData[layer][1] + "\n\n"
            constrMats.append(constructionData[layer][0])
        constructionDict = {'objectType': 'HBConstr', 'name': constructionName, 'EPstr': constructionStr}
        objs[constructionName] = constructionDict
        return constrMats
    
    def dumpHBMat(materialName):
        materialName = materialName.strip()
        materialData = None
        if materialName in sc.sticky ["honeybee_windowMaterialLib"].keys():
            materialData = sc.sticky ["honeybee_windowMaterialLib"][materialName]
        elif materialName in sc.sticky ["honeybee_materialLib"].keys():
            materialData = sc.sticky ["honeybee_materialLib"][materialName]
        if materialData!=None:
            numberOfLayers = len(materialData.keys())
            materialStr = materialData[0] + ",\n"
            materialStr =  materialStr + "  " + materialName + ",   !- name\n"
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    materialStr =  materialStr + "  " + str(materialData[layer][0]) + ",   !- " +  materialData[layer][1] + "\n"
                else:
                    materialStr =  materialStr + "  " + str(materialData[layer][0]) + ";   !- " +  materialData[layer][1] + "\n\n"
            materialDict = {'objectType': 'HBMat', 'name': materialName, 'EPstr': materialStr}
            objs[materialName] = materialDict
    
    def dumpHBRad(radMatName):
        radStr =  hb_RADMaterialAUX.getRADMaterialString(radMatName)
        radMaterialDict = {'objectType': 'HBRadMat', 'name': radMatName, 'RADstr': radStr}
        objs[radMatName] = radMaterialDict
    
    # cycle through the objects and dump everything.
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
            " InputError: Adjacent object %s is not in the list of HBObjects."%name
    
    HBData = {'ids':ids, 'objs': objs}
    with open(filePath, "wb") as outf:
        pickle.dump(HBData, outf)
        print "Saved file to %s"%filePath
    return filePath



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



if initCheck == True and _dump == True and _fileName != None:
    filePath = dumpHBObjects(_HBObjects, _fileName, _workingDir_)