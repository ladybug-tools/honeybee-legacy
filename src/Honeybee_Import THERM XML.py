#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to read the content of a THERM XML file into Grasshopper.  The component will extract both THERM polygons and boundary conditions along with all of their properties.
_
At this point in time, U-Factor tags are not supported but all other features should be imported.
-
Provided by Honeybee 0.0.60

    Args:
        _thermXMLFile: A filepath to a therm XML file on your machine.
        basePlane_: An optional plane or point to set the location and orientation of the THERM file geometry in the Rhino scene.  The default will seatch for location information within the THERM file and, if none is found, geomtry is brought into the World XY plane.
    Returns:
        readMe!:...
        thermPolygons: The therm polygons within the therm XML file.
        thermBCs: The therm boundary conditions within the therm XML file.
"""


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import copy
import uuid

ghenv.Component.Name = 'Honeybee_Import THERM XML'
ghenv.Component.NickName = 'importTHERM'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error


def main(thermXMLFile):
    #Call the relevant classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_thermPolygon = sc.sticky["honeybee_ThermPolygon"]
    hb_thermBC = sc.sticky["honeybee_ThermBC"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    thermDefault = sc.sticky["honeybee_ThermDefault"]()
    
    #Make a series of lists to be filled.
    thermPolygonsFinal = []
    thermBCs = []
    
    #Check if the result file exists.
    if not os.path.isfile(thermXMLFile):
        warning = "Cannot find the result file. Check the location of the file on your machine. \n If it is not there, make sure that you have opened THERM and run your .thmx file before using this component. \n Also, before you run the file in THERM, make sure that you go to Options > Preferences > Simulation and check 'Save Conrad results file (.O).'"
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Define some parameters to be changes while the file is open.
    materialsTrigger = False
    polygonTrigger = False
    newPolygonTrigger = False
    polygonVertices = []
    polygonMaterials = []
    thermPolygons = []
    BCTypes = []
    BCTypeTrigger = False
    BCTypeNames = []
    BCSegments = []
    BCSegmentsTrigger = False
    BCindex = 0
    grabPtData = False
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    
    #Establish some default information about the translations
    plane = rc.Geometry.Plane.WorldXY
    planeReorientation = None
    rhinoOrig = None
    conversionFactor = lb_preparation.checkUnits()
    conversionFactor = 1/(conversionFactor*1000)
    unitsScale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, conversionFactor, conversionFactor, conversionFactor)
    
    #Open the file and begin extracting the relevant bits of information.
    thermFi = open(thermXMLFile, 'r')
    for lineCount, line in enumerate(thermFi):
        if '<Materials>' in line: materialsTrigger = True
        elif '</Materials>' in line: materialsTrigger = False
        elif '<BoundaryConditions>' in line: BCTypeTrigger = True
        elif '</BoundaryConditions>' in line: BCTypeTrigger = False
        elif '<Polygons>' in line: polygonTrigger = True
        elif '</Polygons>' in line: polygonTrigger = False
        elif '<Boundaries>' in line: BCSegmentsTrigger = True
        elif '</Boundaries>' in line: BCSegmentsTrigger = False
        #Try to extract the transformations from the file header.
        elif '<Notes>' in line and '</Notes>' in line:
            if 'RhinoUnits-' in line and 'RhinoOrigin-' in line and 'RhinoXAxis-' in line:
                origRhinoUnits = line.split(',')[0].split('RhinoUnits-')[-1]
                origRhinoOrigin = line.split('),')[0].split('RhinoOrigin-(')[-1].split(',')
                origRhinoXaxis = line.split('),')[1].split('RhinoXAxis-(')[-1].split(',')
                origRhinoYaxis = line.split('),')[2].split('RhinoYAxis-(')[-1].split(',')
                origRhinoZaxis = line.split(')</Notes>')[0].split('RhinoZAxis-(')[-1].split(',')
                
                rhinoOrig = rc.Geometry.Point3d(float(origRhinoOrigin[0]), float(origRhinoOrigin[1]), float(origRhinoOrigin[2]))
                thermPlane = rc.Geometry.Plane(rhinoOrig, rc.Geometry.Plane.WorldXY.XAxis, rc.Geometry.Plane.WorldXY.YAxis)
                basePlane = rc.Geometry.Plane(rhinoOrig, rc.Geometry.Vector3d(float(origRhinoXaxis[0]), float(origRhinoXaxis[1]), float(origRhinoXaxis[2])), rc.Geometry.Vector3d(float(origRhinoYaxis[0]), float(origRhinoYaxis[1]), float(origRhinoYaxis[2])))
                basePlaneNormal = rc.Geometry.Vector3d(float(origRhinoZaxis[0]), float(origRhinoZaxis[1]), float(origRhinoZaxis[2]))
                planeReorientation = rc.Geometry.Transform.ChangeBasis(basePlane, thermPlane)
                plane = basePlane
            elif basePlane_ == None:
                warning = "Cannot find any transformation data in the header of the THERM file. \n Result geometry will be imported to the Rhino model origin."
                print warning
        
        #Extract the materials from the file header.
        elif materialsTrigger == True:
            materialStr = line.strip().replace('"', '')
            materialName = copy.copy(materialStr).split('Material Name=')[-1].split(' Type=')[0]
            if materialName.upper() not in sc.sticky["honeybee_thermMaterialLib"].keys():
                material = thermDefault.addThermMatToLib(materialStr)
        
        #Try to extract the types of Boundary Conditions.
        if BCTypeTrigger == True:
            if 'Adiabatic' in line or 'Frame Cavity Surface' in line: pass
            elif '<BoundaryCondition Name' in line:
                BCDict = {}
                BCDict['Name'] = line.split('Name="')[-1].split('" Type')[0]
                BCDict['Temperature'] = float(line.split('Temperature="')[-1].split('" ')[0])
                BCDict['filmCoefficient'] = float(line.split('H="')[-1].split('" ')[0])
                BCTypeNames.append(BCDict['Name'])
                BCTypes.append(BCDict)
                BCSegments.append([])
        
        #Try to extract the polygons from the file.
        if polygonTrigger == True:
            if '<Polygon ID' in line:
                newPolygonTrigger = True
                polygonVertices = []
                polygonMaterials.append(line.split('Material="')[-1].split('" ')[0].upper())
            elif '</Polygon>' in line:
                newPolygonTrigger = False
                #Make the vertices into a brep and append it to the list.
                polygonLineGeo = rc.Geometry.PolylineCurve(polygonVertices)
                closingLine = rc.Geometry.PolylineCurve([polygonLineGeo.PointAtStart, polygonLineGeo.PointAtEnd])
                allPolygonLine = rc.Geometry.PolylineCurve.JoinCurves([polygonLineGeo, closingLine], sc.doc.ModelAbsoluteTolerance)[0]
                finalPolygonGeo = rc.Geometry.Brep.CreatePlanarBreps(allPolygonLine)[0]
                thermPolygons.append(finalPolygonGeo)
            elif '<Point index=' in line:
                xCoord = float(line.split('x="')[-1].split('"')[0])
                yCoord = float(line.split('y="')[-1].split('"')[0])
                polygonVertex = rc.Geometry.Point3d(xCoord, yCoord, 0)
                polygonVertices.append(polygonVertex)
        
        #Try to extract the BC segments.
        if BCSegmentsTrigger == True:
            if 'Adiabatic' in line or 'Frame Cavity Surface' in line: grabPtData = False
            elif '<BCPolygon ID' in line:
                grabPtData = True
                BCTypeName = line.split('BC="')[-1].split('" units=')[0]
                for count, BCTpy in enumerate(BCTypeNames):
                    if BCTpy == BCTypeName: BCindex = count
            elif grabPtData == True and '<Point index="0"' in line:
                x1 = float(line.split('x="')[-1].split('" ')[0])
                y1 = float(line.split('y="')[-1].split('" />')[0])
            elif grabPtData == True and '<Point index="1"' in line:
                x2 = float(line.split('x="')[-1].split('" ')[0])
                y2 = float(line.split('y="')[-1].split('" />')[0])
                BCSegments[BCindex].append(rc.Geometry.LineCurve(rc.Geometry.Point3d(x1,y1,0), rc.Geometry.Point3d(x2,y2,0)))
        
    thermFi.close()
    
    #Check to see if there is a base plane override connected to the component.
    if basePlane_ != None:
        planeReorientation = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, rc.Geometry.Plane(rc.Geometry.Point3d.Origin, basePlane_.XAxis, basePlane_.YAxis))
        rhinoOrig = basePlane_.Origin
        plane = basePlane_
    
    #Transform the geometry to be at the correct scale in the Rhino scene.
    for geo in thermPolygons: geo.Transform(unitsScale)
    for geoList in BCSegments:
        for geo in geoList: geo.Transform(unitsScale)
    if planeReorientation != None:
        for geo in thermPolygons: geo.Transform(planeReorientation)
        for geoList in BCSegments:
            for geo in geoList: geo.Transform(planeReorientation)
        joinedPolygons = rc.Geometry.Brep.JoinBreps(thermPolygons, sc.doc.ModelAbsoluteTolerance)[0]
        thermBB = joinedPolygons.GetBoundingBox(rc.Geometry.Plane.WorldXY)
        thermOrigin = rc.Geometry.BoundingBox.Corner(thermBB, True, True, True)
        vecDiff = rc.Geometry.Point3d.Subtract(rhinoOrig, thermOrigin)
        planeTransl = rc.Geometry.Transform.Translation(vecDiff.X, vecDiff.Y, vecDiff.Z)
        for geo in thermPolygons: geo.Transform(planeTransl)
        for geoList in BCSegments:
            for geo in geoList: geo.Transform(planeTransl)
    
    #Create the THERM Polygons.
    for count, geo in enumerate(thermPolygons):
        guid = str(uuid.uuid4())
        polyName = "".join(guid.split("-")[:-1])
        HBThermPolygon = hb_thermPolygon(geo.Faces[0].DuplicateFace(False), polygonMaterials[count], polyName, plane, None)
        if HBThermPolygon.warning != None:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, HBThermPolygon.warning)
        else:
            thermPolygonsFinal.append(HBThermPolygon)
    #Add All THERM Polygons to the hive.
    thermPolygonsFin = hb_hive.addToHoneybeeHive(thermPolygonsFinal, ghenv.Component)
    
    #Create the THERM BCs.
    for bcCount, segList in enumerate(BCSegments):
        allSeg = rc.Geometry.PolylineCurve.JoinCurves(segList)
        for seg in allSeg:
            try:
                partsOfSeg = seg.DuplicateSegments()
                segPts =[partsOfSeg[0].PointAtStart]
                for part in partsOfSeg: segPts.append(part.PointAtEnd)
            except:
                segPts = [seg.PointAtStart, seg.PointAtEnd]
            finalGeo = rc.Geometry.PolylineCurve(segPts)
            HBThermBC = hb_thermBC(finalGeo, BCTypes[bcCount]['Name'].title(), BCTypes[bcCount]['Temperature'], BCTypes[bcCount]['filmCoefficient'], plane, None, None, None, None, None)
            thermBound  = hb_hive.addToHoneybeeHive([HBThermBC], ghenv.Component, False)
            thermBCs.extend(thermBound)
            
    
    return thermPolygonsFin, thermBCs


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
#Honeybee check.
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


#If the intital check is good, run the component.
if initCheck and _thermXMLFile:
    result = main(_thermXMLFile)
    if result != -1:
        thermPolygons, thermBCs = result
