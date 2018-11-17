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
Dump Honeybee Objects

Use this component to dump Honeybee objects to a file on your system.
You can use load Honeybee objects to load the file to Grasshopper.
WARNING: This component does not write custom schedules or materials within the file but it does write the names of the constructions and schedules.
Accordingly, to properly load objects agian, you must connect the full strings of these objects to a "Add to EnergyPlus Library" component in any GH cript that loads the HBZones from the file.

-
Provided by Honeybee 0.0.64

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
import Rhino as rc

def dumpHBObjects(HBObjects, fileName, workingDir=None):
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
    hb_ConstrLib = sc.sticky ["honeybee_constructionLib"]
    hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
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
    scheduleCollection = []
    shdCntrlCollection = []
    hvacIDs = []
    airIDs = []
    heatIDs = []
    coolIDs = []
    
    def dumpHBZone(HBZone):
        if HBZone.objectType != 'HBZone': return
        
        # Scale everything if the units system is not meters.
        if sc.sticky["honeybee_ConversionFactor"] != 1:
            fac = sc.sticky["honeybee_ConversionFactor"]
            NUscale = rc.Geometry.Transform.Scale(rc.Geometry.Plane(rc.Geometry.Plane.WorldXY),fac,fac,fac)
            HBZone.transform(NUscale, "", False)
        
        # dump all surfaces and replace surfaces with ids.
        surfaceIds = [srf.ID for srf in HBZone.surfaces]
        for surface in HBZone.surfaces:
            dumpHBSurface(surface)
        HBZone.surfaces = surfaceIds
        
        # dump the HVAC system.
        if HBZone.HVACSystem.ID not in hvacIDs:
            dumpHBhvac(HBZone.HVACSystem)
        HBZone.HVACSystem = HBZone.HVACSystem.ID
        
        # dump the schedules associated with the zone.
        schedules = HBZone.getCurrentSchedules(True)
        dumpAllSchedules(schedules)
        
        # dump any internal masses.
        if HBZone.internalMassConstructions != []:
            for massMat in HBZone.internalMassConstructions:
                if massMat.upper() not in constructions and massMat.upper() not in defaultEPConstrSet:
                    constructions.append(massMat.upper())
                    materials = dumpHBConstr(massMat.upper())
                    for mat in materials:
                        if mat.upper() not in EPmaterials:
                            EPmaterials.append(mat.upper())
                            dumpHBMat(mat.upper())
        
        # dump any earth tube schedules.
        if HBZone.earthtube == True:
            if HBZone.ETschedule != "Always On Discrete" and HBZone.ETschedule.upper() not in scheduleCollection:
                dumpAllSchedules([HBZone.ETschedule])
        
        # add the zone to the master dictionary.
        objs[HBZone.ID] = HBZone.__dict__
    
    def dumpHBSurface(HBSurface, checkTransform=False):
        # Scale everything if the units system is not meters.
        if checkTransform == True and sc.sticky["honeybee_ConversionFactor"] != 1:
            fac = sc.sticky["honeybee_ConversionFactor"]
            NUscale = rc.Geometry.Transform.Scale(rc.Geometry.Plane(rc.Geometry.Plane.WorldXY),fac,fac,fac)
            HBSurface.transform(NUscale, "", False)
        
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
        
        # dump blinds and shading control.
        if HBSurface.isChild and HBSurface.shadingControlName != []:
            for shadingCount, windowShading in enumerate(HBSurface.shadingControlName):
                if windowShading.upper() not in shdCntrlCollection:
                    dumpHBShdCntrl(windowShading)
                    shdCntrlCollection.append(windowShading.upper())
        
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
            if HBSurface.TransmittanceSCH != '' and HBSurface.TransmittanceSCH.upper() not in scheduleCollection:
                scheduleCollection.append(HBSurface.TransmittanceSCH.upper())
                dumpAllSchedules([HBSurface.TransmittanceSCH])
            HBSurface.childSrfs = [childSrf.ID for childSrf in HBSurface.childSrfs]
        
        # This needs to be set to outdoors at first but will be replaced by the correct object on loading
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
    
    def dumpAllSchedules(schedules):
        schedCollect = schedules.values()
        for schedule in schedCollect:
            if schedule.upper() not in scheduleCollection and schedule != '':
                scheduleCollection.append(schedule.upper())
                dumpHBSched(schedule)
                scheduleValues, comments = hb_EPScheduleAUX.getScheduleDataByName(schedule, ghenv.Component)
                
                if scheduleValues[0].lower() == "schedule:year":
                    numOfWeeklySchedules = int((len(scheduleValues)-2)/5)
                    for i in range(numOfWeeklySchedules):
                        weekDayScheduleName = scheduleValues[5 * i + 2]
                        if weekDayScheduleName not in schedCollect and not weekDayScheduleName == '':
                            schedCollect.append(weekDayScheduleName)
                # collect all the schedule items inside the schedule
                elif scheduleValues[0].lower() == "schedule:week:daily":
                    for value in scheduleValues[1:]:
                        if value not in schedCollect:
                            schedCollect.append(value)
    
    def dumpHBSched(scheduleName):
        scheduleData = None
        scheduleName= scheduleName.upper()
        if scheduleName.lower().endswith(".csv"):
            warning = "CSV schedule detected.  Make sure that the machine that\n  loads the HBZones has the CSV schedule in the same location."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        if scheduleName in sc.sticky ["honeybee_ScheduleLib"].keys():
            scheduleData = sc.sticky ["honeybee_ScheduleLib"][scheduleName]
        elif scheduleName in sc.sticky ["honeybee_ScheduleTypeLimitsLib"].keys():
            scheduleData = sc.sticky["honeybee_ScheduleTypeLimitsLib"][scheduleName]
        
        if scheduleData!=None:
            numberOfLayers = len(scheduleData.keys())
            scheduleStr = scheduleData[0] + ",\n"
            if numberOfLayers == 1:
                return scheduleStr  + "  " +  scheduleName + ";   !- name\n\n"
            # add the name
            scheduleStr =  scheduleStr  + "  " +  scheduleName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers - 1:
                    scheduleStr =  scheduleStr + "  " + scheduleData[layer][0] + ",   !- " +  scheduleData[layer][1] + "\n"
                else:
                    scheduleStr =  scheduleStr + "  " + str(scheduleData[layer][0]) + ";   !- " +  scheduleData[layer][1] + "\n\n"
            scheduleDict = {'objectType': 'HBsched', 'name': scheduleName, 'EPstr': scheduleStr}
            objs[scheduleName] = scheduleDict
    
    def dumpHBShdCntrl(windowShading):
        shdCntrlDict = {'objectType': 'HBShdCntrl', 'name': windowShading, 'EPstr': hb_EPObjectsAux.getEPObjectsStr(windowShading)}
        objs[windowShading] = shdCntrlDict
        
        values = hb_EPObjectsAux.getEPObjectDataByName(windowShading)
        if values[4][0] != '' and values[4][0].upper() not in scheduleCollection:
            dumpAllSchedules([values[4][0]])
        if values[2][0] != '':
            # Iniitalize for construction (for switchable glazing).
            constrName = values[2][0]
            constructions.append(constrName.upper())
            materials = dumpHBConstr(constrName.upper())
            for mat in materials:
                if mat.upper() not in EPmaterials:
                    EPmaterials.append(mat.upper())
                    dumpHBMat(mat.upper())
        else:
            # Iniitalize for material (for blinds and shades).
            materialName = values[8][0]
            EPmaterials.append(materialName.upper())
            dumpHBMat(materialName.upper())
    
    def dumpHBRad(radMatName):
        radStr =  hb_RADMaterialAUX.getRADMaterialString(radMatName)
        radMaterialDict = {'objectType': 'HBRadMat', 'name': radMatName, 'RADstr': radStr}
        objs[radMatName] = radMaterialDict
    
    def dumpHBViewFactor(viewFacInfo):
        # add the view factor to the master dictionary.
        objs[viewFacInfo.ID] = viewFacInfo.__dict__
    
    # cycle through the objects and dump everything.
    for id, HBO in zip(ids, HBObjects):
        if HBO.objectType == 'HBSurface':
            dumpHBSurface(HBO, True)
        elif HBO.objectType == 'HBZone':
            dumpHBZone(HBO)
        elif HBO.objectType == 'ViewFactorInfo':
            dumpHBViewFactor(HBO)
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
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Honeybee fly...")
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
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)



if initCheck == True and _dump == True and _fileName != None:
    filePath = dumpHBObjects(_HBObjects, _fileName, _workingDir_)