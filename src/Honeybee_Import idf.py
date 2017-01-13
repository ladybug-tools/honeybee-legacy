"""
import an idf file to gh
This version only imports the geometries
Constructions, schedules and systems will be neglected
    Args:
        _idfFile: File path to an idf file
        importEPObjects_: Set to True if you want Honeybee import constructions, materials and schedules from this file. You need to do it only once. In case there is an object with similar name already in Honeybee library object will not be imported and you need to rename it in the idf file.
    Returns:
        readMe!: ...
        HBZones: List of Honeybee zones imported from .idf file
        shadings: Shading objects if any
"""
ghenv.Component.Name = "Honeybee_Import idf"
ghenv.Component.NickName = 'importIdf'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "4"


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import uuid
import Grasshopper.Kernel as gh

tolerance = sc.doc.ModelAbsoluteTolerance
import math


def createEPObject(idfFile, resultDict, key, type = None):
    if key=="Zone,": key = "EPZONES"
    
    # This function creates a dictionary from EPObjects
    if key not in resultDict.keys():
        # create an empty dictionary for the key
        resultDict[key] = {}
    
    # store the data into the dictionary
    inLine = 0
    recounter = 0
    for lineCount, line in enumerate(idfFile):
        if line.strip().startswith("!"):
            recounter -= 1
            continue
        elif lineCount == 0:
            # first line is the name of the object
            nameKey = line.split("!")[0].strip()[:-1].strip()
            if nameKey in resultDict[key].keys():
                # this means the object is already in the library
                warning = "The " + key + ": " + nameKey + " already exists in the libaray.\n" + \
                          "You need to rename the " + key + "."
                print warning
                break
            else:
                # add the material to the library
                resultDict[key][nameKey] = {}
                if type!=None:
                    resultDict[key][nameKey][0] = type
                
        else:
            objValues = line.split("!")[0].strip().split(",")
            
            try: objDescription = line.split("!")[1].strip()
            except:  objDescription = ""
            objKey = lineCount + recounter #+ '_' + line.split("!-")[1].strip()
            for objCount, objValue in enumerate(objValues):
                if not objValue.endswith(";"):
                    if objCount == 0 or len(objValue.strip())!=0: # get rid of empty items
                        #print objValue
                        if objCount!=0:inLine+=1
                        resultDict[key][nameKey][objKey + inLine] = objValue, objDescription
                elif objValue.endswith(";"):
                    if objCount!=0: inLine+=1
                    resultDict[key][nameKey][objKey + inLine] = objValue[:-1], objDescription
                    
                    return resultDict

def createEPObjectDB(idfFile, resultDict, key, type = None, nameKey = None):
    if key=="Zone,": key = "EPZONES"
    
    # This function creates a dictionary from EPObjects
    if key not in resultDict.keys():
        # create an empty dictionary for the key
        resultDict[key] = {}
    
    if nameKey in resultDict[key].keys():
        # this means the object is already in the library
        warning = "The " + key + ": " + nameKey + " is already existed in the libaray.\n" + \
                  "You need to rename the " + key + "."
        print warning
    else:
        # add the material to the library
        resultDict[key][nameKey] = {}
        if type!=None: resultDict[key][nameKey][0] = type
    
    # store the data into the dictionary
    inLine = 0
    recounter = 0
    for lineCount, line in enumerate(idfFile):
        if line.strip().startswith("!"):
            recounter -= 1
            continue
        else:
            objValues = line.split("!")[0].strip().split(",")
            
            try: objDescription = line.split("!")[1].strip()
            except:  objDescription = ""
            objKey = lineCount + recounter #+ '_' + line.split("!-")[1].strip()
            if objKey == 0:
                recounter += 1
                objKey += 1
            for objCount, objValue in enumerate(objValues):
                if not objValue.endswith(";"):
                    if objCount == 0 or len(objValue.strip())!=0: # get rid of empty items
                        #print objValue
                        if objCount!=0:
                            inLine+=1
                            if lineCount == 1: recounter +=1
                        resultDict[key][nameKey][objKey + inLine] = objValue, objDescription
                elif objValue.endswith(";"):
                    if objCount!=0: inLine+=1
                    resultDict[key][nameKey][objKey + inLine] = objValue[:-1], objDescription
                    
                    return resultDict


# 4 represents an Air Wall
srfTypeDict = {0:'WALL',
   1:'ROOF',
   2:'FLOOR',
   3:'CEILING',
   4:'WALL',
   5:'WINDOW',
   6:'SHADING',
   'WALL': 0,
   'ROOF':1,
   'FLOOR': 2,
   'CEILING': 3,
   'WINDOW':5,
   'SHADING': 6}


def main(idfFile, importEPObjects = False):
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            " Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1        
        
        
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_runStudy_RAD = sc.sticky["ladybug_Export2Radiance"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_EPSHDSurface = sc.sticky["honeybee_EPShdSurface"]
        
        hb_GetEPLibs = sc.sticky["honeybee_GetEPLibs"]
        
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()
    
    # import libraries if needed
    if importEPObjects:
        EPLibs = hb_GetEPLibs()
        EPLibs.importEPLibrariesFromFile(idfFile, False, False, True)
    
        sc.sticky["honeybee_materialLib"].update(EPLibs.getEPMaterials())
        sc.sticky["honeybee_windowMaterialLib"].update(EPLibs.getEPWindowMaterial())
        sc.sticky ["honeybee_constructionLib"].update(EPLibs.getEPConstructions())
        sc.sticky["honeybee_ScheduleLib"].update(EPLibs.getEPSchedule())
        sc.sticky["honeybee_ScheduleTypeLimitsLib"].update(EPLibs.getEPScheduleTypeLimits())
    
    EPKeys = ["Zone,", "BuildingSurface:Detailed", "FenestrationSurface:Detailed", \
              "Shading:Site:Detailed", "Shading:Building:Detailed", "Shading:Zone:Detailed", \
              "Window,", "WindowMaterial:Blind", "WindowMaterial:Shade", "WindowProperty:ShadingControl"]
    EPKeys.extend(["Material,", "WindowMaterial,", "Construction,"])
    idfFileDict = {}
    
    with open(idfFile, 'r') as inf:
        for line in inf:
            for key in EPKeys:
                if line.strip().ToUpper().startswith(key.ToUpper()):
                    objTypeInit = line.strip()[:-1].split(',')
                    objType = objTypeInit[0] + ','
                    if (len(objTypeInit) == 2 and '!' in objTypeInit[1]) or (len(objTypeInit) == 1):
                        idfFileDict = createEPObject(inf, idfFileDict, key, objType)
                    else:
                        objName = objTypeInit[1].strip()
                        idfFileDict = createEPObjectDB(inf, idfFileDict, key, objType, objName)
    
    outputs = {"Material" : [],
            "WindowMaterial" : [],
            "Construction" : []}
    
    HBZones = {}
    # create HBZones
    # print idfFileDict.keys()
    for EPZoneName in idfFileDict["EPZONES"]:
        zoneData = idfFileDict["EPZONES"][EPZoneName]
        try: x = float(zoneData[2][0])
        except: x = 0
        try: y = float(zoneData[3][0])
        except: y = 0
        try: z = float(zoneData[4][0])
        except: z = 0
        
        movingVector = rc.Geometry.Vector3d(x, y, z)
        
        # initiate the zone
        zoneID = str(uuid.uuid4())
        thisZone = hb_EPZone(None, zoneID, EPZoneName, program = [None, None], isConditioned = True)
        # I can also set the zone origin here
        HBZones[EPZoneName.lower()] = [thisZone, movingVector]
        pass
    
    HBSurfaces = {}
    if idfFileDict.has_key("BuildingSurface:Detailed"):
        for surfaceName in idfFileDict["BuildingSurface:Detailed"]: #["BuildingSurface:Detailed"]:
            srfType = idfFileDict["BuildingSurface:Detailed"][surfaceName][1][0]
            EPConstruction = idfFileDict["BuildingSurface:Detailed"][surfaceName][2][0]
            parentZone = idfFileDict["BuildingSurface:Detailed"][surfaceName][3][0]
            srfBC = idfFileDict["BuildingSurface:Detailed"][surfaceName][4][0]
            BCObject = idfFileDict["BuildingSurface:Detailed"][surfaceName][5][0]
            sunExposure = idfFileDict["BuildingSurface:Detailed"][surfaceName][6][0]
            windExposure = idfFileDict["BuildingSurface:Detailed"][surfaceName][7][0]
            viewFactor = idfFileDict["BuildingSurface:Detailed"][surfaceName][8][0]
            numOfVertices = idfFileDict["BuildingSurface:Detailed"][surfaceName][9][0]
            numOfKeys = len(idfFileDict["BuildingSurface:Detailed"][surfaceName].keys())
            pts = []
            
            # find moving vector based on parent zone
            
            movingVector = HBZones[parentZone.lower()][1]
            try:
                for coordinate in range(10, numOfKeys, 3):
                    x = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate][0]
                    y = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 1][0]
                    z = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 2][0]
                    pts.append(rc.Geometry.Point3d.Add(rc.Geometry.Point3d(float(x), float(y), float(z)), movingVector))
            except:
                for coordinate in range(9, numOfKeys, 3):
                    x = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate][0]
                    y = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 1][0]
                    z = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 2][0]
                    pts.append(rc.Geometry.Point3d.Add(rc.Geometry.Point3d(float(x), float(y), float(z)), movingVector))
            pts.append(pts[0])
            polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
            try:
                geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
                #create the surface
                thisEPSrf = hb_EPZoneSurface(geometry, 1, surfaceName)
                #, parentZone, srfTypeDict[srfType.ToUpper()])
                
                #print parentZone
                
                #assign properties
                thisEPSrf.parent = HBZones[parentZone.lower()][0]
                thisEPSrf.type = srfTypeDict[srfType.ToUpper()]
                thisEPSrf.construction = thisEPSrf.cnstrSet[thisEPSrf.type]
                thisEPSrf.EPConstruction = EPConstruction
                thisEPSrf.setBC(srfBC, isUserInput= True)
                thisEPSrf.BCObject = BCObject
                thisEPSrf.sunExposure = sunExposure
                thisEPSrf.windExposure = windExposure
                thisEPSrf.groundViewFactor = viewFactor
                thisEPSrf.numOfVertices = numOfVertices
                
                # change type of surface if BC is set to ground
                if srfBC.lower()== "ground":
                    thisEPSrf.setType(int(thisEPSrf.type) + 0.5, isUserInput= True)
                
                
                if srfBC.lower()== "ground" or srfBC.lower()== "adiabatic":
                    thisEPSrf.setSunExposure('NoSun')
                    thisEPSrf.setWindExposure('NoWind')
                
                if srfBC.lower()== "outdoors" or srfBC.lower()== "ground":
                    thisEPSrf.setBCObjectToOutdoors()
                
                # add surface to the zone
                HBZones[parentZone.lower()][0].addSrf(thisEPSrf)
                # add to surfaces dictionary
                HBSurfaces[surfaceName] = thisEPSrf
            except:
                print "failed to build EP Srf"
    
    HBFenSurfaces = {}
    if idfFileDict.has_key("FenestrationSurface:Detailed"):
        # add child surfaces
        for surfaceName in idfFileDict["FenestrationSurface:Detailed"]: #["BuildingSurface:Detailed"]:
            try:
                srfType = idfFileDict["FenestrationSurface:Detailed"][surfaceName][1][0]
                EPConstruction = idfFileDict["FenestrationSurface:Detailed"][surfaceName][2][0]
                parentSrf = idfFileDict["FenestrationSurface:Detailed"][surfaceName][3][0]
                BCObject = idfFileDict["FenestrationSurface:Detailed"][surfaceName][4][0]
                viewFactor = idfFileDict["FenestrationSurface:Detailed"][surfaceName][5][0]
                shadingControlName = idfFileDict["FenestrationSurface:Detailed"][surfaceName][6][0]
                frameName = idfFileDict["FenestrationSurface:Detailed"][surfaceName][7][0]
                multiplier = idfFileDict["FenestrationSurface:Detailed"][surfaceName][8][0]
                numOfVertices = idfFileDict["FenestrationSurface:Detailed"][surfaceName][9][0]
                numOfKeys = len(idfFileDict["FenestrationSurface:Detailed"][surfaceName].keys())
                
                pts = []
                
                
                # let the user know that we don't support shading control right now and we are sorry
                if shadingControlName.strip()!="":
                    msg = "Currently Honeybee doesn't support importing shading controls!" +\
                          "\nSorry and it will be added soon!"
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, msg)
                    
                    shadingControlName = ""
                
                
                # find moving vector based on parent zone
                movingVector = HBZones[HBSurfaces[parentSrf].parent.name.lower()][1]
                
                for coordinate in range(10, numOfKeys, 3):
                    x = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate][0]
                    y = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate + 1][0]
                    z = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate + 2][0]
                    pts.append(rc.Geometry.Point3d.Add(rc.Geometry.Point3d(float(x), float(y), float(z)), movingVector))
                    
                pts.append(pts[0])
                polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
                geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
                
                #create the surface
                thisEPFenSrf = hb_EPFenSurface(geometry, 1, surfaceName, HBSurfaces[parentSrf], 5)
                
                #assign properties
                thisEPFenSrf.parent = HBSurfaces[parentSrf]
                thisEPFenSrf.construction = thisEPFenSrf.cnstrSet[thisEPFenSrf.type]
                thisEPFenSrf.EPConstruction = EPConstruction
                thisEPFenSrf.BCObject = BCObject
                thisEPFenSrf.shadingControlName = shadingControlName
                thisEPFenSrf.frameName = frameName
                thisEPFenSrf.multiplier = multiplier
                thisEPFenSrf.groundViewFactor = viewFactor
                thisEPFenSrf.numOfVertices = numOfVertices
                
                if thisEPFenSrf.parent.BC.lower()== "outdoors":
                    thisEPFenSrf.setBCObjectToOutdoors()
                    
                # add the child surface to the surface
                HBSurfaces[parentSrf].addChildSrf(thisEPFenSrf)
            except:
                print "failed to build fen srf"
    
    winPts = []
    if idfFileDict.has_key("Window,"):
        for windowName in idfFileDict["Window,"].keys():
            windowObject = idfFileDict["Window,"][windowName]
            srfType = 5
            EPConstruction = windowObject[1][0]
            parentSrfName = windowObject[2][0]
            viewFactor = windowObject[3][0]
            shadingControlName = windowObject[4][0]
            frameName = windowObject[5][0]
            numOfVertices = 4
            multiplier = windowObject[7][0]
            xCoor = float(windowObject[8][0])
            zCoor = float(windowObject[9][0])
            length = float(windowObject[10][0])
            height = float(windowObject[11][0])

            # let the user know that we don't support shading control right now and we are sorry
            if shadingControlName.strip()!="":
                msg = "Currently Honeybee doesn't support importing shading controls!" +\
                      "\nSorry and it will be added soon!"
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, msg)
                
                shadingControlName = ""

            # find surface plane
            parentSrf = HBSurfaces[parentSrfName]
            coordinates = parentSrf.extractPoints()
            SrfPlane = rc.Geometry.Plane(coordinates[0], coordinates[1], coordinates[3])
            
            # create four points on XZ Plane
            pt1 = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin, rc.Geometry.Vector3d(xCoor, zCoor, 0))
            pt2 = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin, rc.Geometry.Vector3d(xCoor + length, zCoor, 0))
            pt3 = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin, rc.Geometry.Vector3d(xCoor + length, zCoor + height, 0))
            pt4 = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin, rc.Geometry.Vector3d(xCoor, zCoor + height, 0))
            
            transform = rc.Geometry.Transform.PlaneToPlane(rc.Geometry.Plane.WorldXY, SrfPlane)
            polyline = rc.Geometry.Polyline([pt1, pt2, pt3, pt4, pt1]).ToNurbsCurve()
            polyline.Transform(transform)
            
            geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
            #create the surface
            thisEPFenSrf = hb_EPFenSurface(geometry, 1, windowName, parentSrf, 5)
            
            #assign properties
            thisEPFenSrf.parent = parentSrf
            thisEPFenSrf.construction = thisEPFenSrf.cnstrSet[thisEPFenSrf.type]
            thisEPFenSrf.EPConstruction = EPConstruction
            thisEPFenSrf.BCObject = BCObject
            thisEPFenSrf.shadingControlName = shadingControlName
            thisEPFenSrf.frameName = frameName
            thisEPFenSrf.multiplier = multiplier
            thisEPFenSrf.groundViewFactor = viewFactor
            thisEPFenSrf.numOfVertices = numOfVertices
            
            if thisEPFenSrf.parent.BC.lower()== "outdoors":
                thisEPFenSrf.setBCObjectToOutdoors()
                
            # add the child surface to the surface
            parentSrf.addChildSrf(thisEPFenSrf)
            
    shadingList = []
    if idfFileDict.has_key("Shading:Site:Detailed"):
        for shadingName in idfFileDict["Shading:Site:Detailed"].keys():
            shadingObj = idfFileDict["Shading:Site:Detailed"][shadingName]
            pts = []
            for coordinate in range(3, len(shadingObj.keys()), 3):
                x = shadingObj[coordinate][0]
                y = shadingObj[coordinate + 1][0]
                z = shadingObj[coordinate + 2][0]
                pts.append(rc.Geometry.Point3d(float(x), float(y), float(z)))
            pts.append(pts[0])
            polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
            geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
            thisShading = hb_EPSHDSurface(geometry, 1, shadingName)
    
    if idfFileDict.has_key("Shading:Building:Detailed"):
        for shadingName in idfFileDict["Shading:Building:Detailed"].keys():
            shadingObj = idfFileDict["Shading:Building:Detailed"][shadingName]
            pts = []
            for coordinate in range(3, len(shadingObj.keys()), 3):
                x = shadingObj[coordinate][0]
                y = shadingObj[coordinate + 1][0]
                z = shadingObj[coordinate + 2][0]
                pts.append(rc.Geometry.Point3d(float(x), float(y), float(z)))
            pts.append(pts[0])
            polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
            geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
            thisShading = hb_EPSHDSurface(geometry, 1, shadingName)
            
    
            shadingList.append(thisShading)
    
    # recalculate the zone
    zonesList = []
    for zoneName in HBZones.keys():
        HBZone = HBZones[zoneName.lower()][0]
        HBZone.createZoneFromSurfaces()
        
        # replace BCObjects with HBObjects
        for HBS in HBZone.surfaces:
            if HBS.BC.lower() == "surface":
                try:
                    HBS.BCObject = HBSurfaces[HBS.BCObject]
                except:
                    pass
        
        zonesList.append(HBZone)
        
    
    # add to the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZones  = hb_hive.addToHoneybeeHive(zonesList, ghenv.Component)
    shadings = hb_hive.addToHoneybeeHive(shadingList, ghenv.Component, False)
    
    return HBZones, shadings

if _idfFile!=None:
    results = main(_idfFile, importEPObjects_)
    if results!=-1:
        HBZones, shadings = results