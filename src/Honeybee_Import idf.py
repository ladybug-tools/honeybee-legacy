"""
import an idf file to gh
This version only imports the geometries
Constructions, schedules and systems will be neglected
    Args:
        input1: ...
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Honeybee_Import idf"
ghenv.Component.NickName = 'importIdf'
ghenv.Component.Message = 'VER 0.0.53\nMAY_13_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import uuid
from clr import AddReference
AddReference('Grasshopper')
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
    for lineCount, line in enumerate(idfFile):
        if lineCount == 0:
            # first line is the name of the object
            nameKey = line.split("!")[0].strip()[:-1]
            if nameKey in resultDict[key].keys():
                # this means the object is already in the library
                warning = "The " + key + ": " + nameKey + " is already existed in the libaray.\n" + \
                          "You need to rename the " + key + "."
                print warning
                break
            else:
                # add the material to the library
                resultDict[key][nameKey] = {}
                if type!=None: resultDict[key][nameKey][0] = type
                
        else:
            objValues = line.split("!")[0].strip().split(",")
            
            try: objDescription = line.split("!")[1].strip()
            except:  objDescription = ""
            objKey = lineCount #+ '_' + line.split("!-")[1].strip()
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


def main(idfFile):
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
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
        
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()
    
    
    EPKeys = ["Zone,", "BuildingSurface:Detailed", "FenestrationSurface:Detailed", "Shading:Site:Detailed", "Shading:Building:Detailed", "Shading:Zone:Detailed"]
    EPKeys.extend(["Material", "WindowMaterial", "Construction"])
    idfFileDict = {}
    
    with open(idfFile, 'r') as inf:
        for line in inf:
            for key in EPKeys:
                if line.strip().ToUpper().startswith(key.ToUpper()):
                    objType = line.strip()[:-1]
                    idfFileDict = createEPObject(inf, idfFileDict, key, objType)
    
    outputs = {"Material" : [],
            "WindowMaterial" : [],
            "Construction" : []}
    
    HBZones = {}
    # create HBZones
    # print idfFileDict.keys()
    for EPZoneName in idfFileDict["EPZONES"]:
        # initiate the zone
        zoneID = str(uuid.uuid4())
        thisZone = hb_EPZone(None, zoneID, EPZoneName, program = [None, None], isConditioned = True)
        # I can also set the zone origin here
        HBZones[EPZoneName] = thisZone
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
            
            for coordinate in range(10, numOfKeys, 3):
                x = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate][0]
                y = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 1][0]
                z = idfFileDict["BuildingSurface:Detailed"][surfaceName][coordinate + 2][0]
                pts.append(rc.Geometry.Point3d(float(x), float(y), float(z)))
            pts.append(pts[0])
            polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
            geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
            #create the surface
            thisEPSrf = hb_EPZoneSurface(geometry, 1, surfaceName)
            #, parentZone, srfTypeDict[srfType.ToUpper()])
            
            #assign properties
            thisEPSrf.parent = HBZones[parentZone]
            thisEPSrf.type = srfTypeDict[srfType.ToUpper()]
            thisEPSrf.construction = thisEPSrf.cnstrSet[thisEPSrf.type]
            thisEPSrf.EPConstruction = EPConstruction
            thisEPSrf.BC = srfBC
            thisEPSrf.BCObject = BCObject
            thisEPSrf.sunExposure = sunExposure
            thisEPSrf.windExposure = windExposure
            thisEPSrf.groundViewFactor = viewFactor
            thisEPSrf.numOfVertices = numOfVertices
            
            # add surface to the zone
            HBZones[parentZone].addSrf(thisEPSrf)
            # add to surfaces dictionary
            HBSurfaces[surfaceName] = thisEPSrf
        
    HBFenSurfaces = {}
    if idfFileDict.has_key("FenestrationSurface:Detailed"):
        # add child surfaces
        for surfaceName in idfFileDict["FenestrationSurface:Detailed"]: #["BuildingSurface:Detailed"]:
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
            for coordinate in range(10, numOfKeys, 3):
                x = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate][0]
                y = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate + 1][0]
                z = idfFileDict["FenestrationSurface:Detailed"][surfaceName][coordinate + 2][0]
                pts.append(rc.Geometry.Point3d(float(x), float(y), float(z)))
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
            
            # add the child surface to the surface
            HBSurfaces[parentSrf].addChildSrf(thisEPFenSrf)
        
    # recalculate the zone
    zonesList = []
    for zoneName in HBZones.keys():
        HBZone = HBZones[zoneName]
        HBZone.createZoneFromSurfaces()
        zonesList.append(HBZone)
    
    # add to the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZones  = hb_hive.addToHoneybeeHive(zonesList, ghenv.Component.InstanceGuid.ToString())
    
    #for EPKey in EPKeys:
    #    if EPKey in resultDict.keys():
    #        try:
    #            for key in resultDict[EPKey].keys(): outputs[EPKey].append(key)
    #            print  `len(resultDict[EPKey].keys())` + " " + EPKey.lower() + " found in " + libFilePath
    #        except:
    #            outputs[key] = " 0 " + EPKey.lower() + " found in " + libFilePath
    
    
    return HBZones, None

if _idfFile!=None:
    results = main(_idfFile)

    if results!=-1:
        HBZones, shadings = results