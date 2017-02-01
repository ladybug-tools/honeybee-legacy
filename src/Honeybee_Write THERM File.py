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
Use this component to write your THERM polygons and boundary conditions into a therm XML that can be opened ready-to-run in THERM.
-
Provided by Honeybee 0.0.60

    Args:
        _polygons: A list of thermPolygons from one or more "Honeybee_Create Therm Polygons" components.
        boundaries_: A list of thermBoundaries from one or more "Honeybee_Create Therm Boundaries" components.
        meshLevel_: An optional integer to set the mesh level of the resulting exported file.  The default is set to a coarse value of 6 but it may be necessary to increase this if THERM tells you to 'increase the quad tree mesh parameter in the file'.
        workingDir_: An optional working directory to a folder on your system, into which you would like to write the THERM XML and results.  The default will write these files in into your Ladybug default folder.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        fileName_: An optional text string which will be used to name your THERM XML.  Change this to aviod over-writing results of previous runs of this component.
        _writeXML: Set to "True" to have the component take your connected UWGParemeters and write them into an XML file.  The file path of the resulting XML file will appear in the xmlFileAddress output of this component.  Note that only setting this to "True" and not setting the output below to "True" will not automatically run the XML through the Urban Weather Generator for you.
    Returns:
        readMe!:...
        xmlFileAddress: The file path of the therm XML file that has been generated on your machine.  Open this file in THERM to see your exported therm model.
        resultFileAddress: The location where the THERM results will be written once you open the XML file above in THERM and hit "simulate."
"""

import Rhino as rc
import scriptcontext as sc
import os
import System
import Grasshopper.Kernel as gh
import uuid
import math
import copy
import datetime
import decimal

ghenv.Component.Name = 'Honeybee_Write THERM File'
ghenv.Component.NickName = 'writeTHERM'
ghenv.Component.Message = 'VER 0.0.60\nNOV_30_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nMAY_12_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    # Import Polygon class.
    hb_thermPolygon = sc.sticky["honeybee_ThermPolygon"]
    
    # Check the filename.
    xmlFileName = 'unnamed'
    if fileName_ != None:
        if fileName_.upper().endswith('.THMX'): xmlFileName = fileName_.upper().split('.THMX')[0]
        else: xmlFileName = fileName_
    
    # If there is a workingDir, make sure that it exists and, if not, try to make it.
    workingDir = None
    if workingDir_ != None:
        if not os.path.exists(workingDir_):
            try:
                os.makedirs(workingDir_)
                
            except:
                checkData3 = False
                warning =  'cannot create the working directory as: ', workingDir_ + \
                      '\nPlease set a new working directory.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                return -1
        else:
            workingDir = workingDir_
    else:
        if workingDir_ == None: workingDir = sc.sticky["Ladybug_DefaultFolder"] + xmlFileName + '\\THERM\\'
        else: workingDir = workingDir_
        if not os.path.exists(workingDir): os.makedirs(workingDir)
        print 'Current working directory is set to: ' + workingDir
    
    if not workingDir.endswith('\\'): workingDir = workingDir + '\\'
    
    # Call the polygons from the hive.
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        thermPolygons = hb_hive.callFromHoneybeeHive(_polygons)
        thermBCs = hb_hive.callFromHoneybeeHive(boundaries_)
    except:
        warning = "Failed to call _polygons and boundaries_ from the HB Hive. \n Make sure that connected geometry to _polygons is from the 'Create Therm Polygons' component \n and that geometry to boundaries_ is from the 'Create Therm Boundaries' component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # Make sure that the connected objects are of the right type.
    checkData = True
    for polygon in thermPolygons:
        try:
            if polygon.objectType == "ThermPolygon": pass
            else: checkData1 = False
        except:
            checkData = False
    if checkData == False:
        warning = "Geometry connected to _polygons are not valid thermPolygons from the 'Create Therm Polygons' component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        reutrn -1
    
    for boundary in thermBCs:
        try:
            if boundary.objectType == "ThermBC": pass
            else: checkData = False
        except:
            checkData = False
    if checkData == False:
        warning = "Geometry connected to boundaries_ are not valid thermBoundaries from the 'Create Therm Bounrdaies' component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    
    # Make sure that all of the geometry is in the same plane.
    basePlaneNormal = rc.Geometry.Vector3d(thermPolygons[0].normalVector)
    if basePlaneNormal.Z < 0: basePlaneNormal.Reverse()
    
    allPolygonGeo = []
    for polygon in thermPolygons:
        allPolygonGeo.append(polygon.geometry)
    joinedPolygons = rc.Geometry.Brep.JoinBreps(allPolygonGeo, sc.doc.ModelAbsoluteTolerance)
    
    # Establish the reference plane for the THERM scene.
    refrencePlane = None
    allGeometryBB = joinedPolygons[0].GetBoundingBox(rc.Geometry.Plane.WorldXY)
    if abs(basePlaneNormal.X) < tol and abs(basePlaneNormal.Y) < tol and abs(basePlaneNormal.Z - 1) < tol: basePlaneOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, False, False)
    else: basePlaneOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, True, False)
    thermFileOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, True, True)
    basePlane = rc.Geometry.Plane(basePlaneOrigin, basePlaneNormal)
    
    # If the plane is not in the worldXY, rotate it so that the THERM y-axis and Rhino z-axis are aligned.
    basePlaneNormal.Unitize()
    if abs(basePlaneNormal.X) < tol and abs(basePlaneNormal.Y) < tol and abs(basePlaneNormal.Z - 1) < tol:
        basePlaneNormal = rc.Geometry.Vector3d.ZAxis
        basePlane = rc.Geometry.Plane(basePlane.Origin, rc.Geometry.Vector3d.XAxis, rc.Geometry.Vector3d.YAxis)
    else:
        # Calculate the angle between the geometry plane an the projection of the Rhino Z-Axis into that plane.
        rhinoZAxis = rc.Geometry.Vector3d(0,0,1)
        planeProject = rc.Geometry.Transform.PlanarProjection(basePlane)
        rhinoZAxis.Transform(planeProject)
        rhinoZAxis.Unitize()
        rotationAngle = rc.Geometry.Vector3d.VectorAngle(basePlane.YAxis, rhinoZAxis)
        #Rotate the plane
        planeRotation = rc.Geometry.Transform.Rotation(-rotationAngle, basePlaneNormal, basePlane.Origin)
        basePlane.Transform(planeRotation)
    
    # If the plane X-Axis is negative, flip the X and Zaxis.
    if basePlane.XAxis.X < -tol:
        basePlaneNormal.Reverse()
        newXAxis = rc.Geometry.Vector3d(basePlane.XAxis)
        newXAxis.Reverse()
        basePlane = rc.Geometry.Plane(basePlane.Origin, newXAxis, basePlane.YAxis)
    
    # Caclulate a new origin that is based on the bouding box in the new plane.
    newAllGeometryBB = joinedPolygons[0].GetBoundingBox(basePlane)
    newBasePlaneOrigin = rc.Geometry.BoundingBox.Corner(newAllGeometryBB, True, False, False)
    changeBTrans = rc.Geometry.Transform.ChangeBasis(basePlane, rc.Geometry.Plane.WorldXY)
    newBasePlaneOrigin.Transform(changeBTrans)
    basePlane = rc.Geometry.Plane(newBasePlaneOrigin, basePlane.XAxis, basePlane.YAxis)
    
    # Check to see if any of the therm polygons have holes in them and need to be split into multiple geometries.
    # If so, split them and create new polygon objects.
    def splitWithPlane(splitPlane, geometry):
        allSplitGeo = []
        allSplitGeo.extend(geometry.Trim(splitPlane, sc.doc.ModelAbsoluteTolerance))
        splitPlane.Flip()
        allSplitGeo.extend(geometry.Trim(splitPlane, sc.doc.ModelAbsoluteTolerance))
        return allSplitGeo
    
    newThermPolygons = []
    for polygon in thermPolygons:
        if polygon.splitNeeded == True:
            outerMostCurve = polygon.polylineGeo[0]
            innerCurves = polygon.polylineGeo[1:]
            splitPlanes = []
            for inCurve in innerCurves:
                vert1 = inCurve.PointAtStart
                vert2Param = outerMostCurve.ClosestPoint(vert1)[1]
                vert2 = outerMostCurve.PointAt(vert2Param)
                planeX = rc.Geometry.Vector3d(vert2.X-vert1.X, vert2.Y-vert1.Y, vert2.Z-vert1.Z)
                splitPlane = rc.Geometry.Plane(vert1, planeX, basePlane.ZAxis)
                splitPlanes.append(splitPlane)
            
            finalSplitGeo = []
            allSplit = False
            badPolygons = [polygon.geometry]
            for plane in splitPlanes:
                if allSplit == False:
                    allSplitGeo = []
                    for geo2Split in badPolygons:
                        allSplitGeo.extend(splitWithPlane(plane, geo2Split))
                    goodPolygons = []
                    badPolygons = []
                    for geo in allSplitGeo:
                        pB = geo.Edges
                        allB = rc.Geometry.PolylineCurve.JoinCurves(pB, sc.doc.ModelAbsoluteTolerance)
                        if len(allB) == 1:
                            goodPolygons.append(geo)
                        else:
                            badPolygons.append(geo)
                    if len(goodPolygons) == len(allSplitGeo):
                        allSplit = True
                    finalSplitGeo.extend(goodPolygons)
            
            # Turn the split geometries into thermPolygons
            for splitGeo in finalSplitGeo:
                guid = str(uuid.uuid4())
                polyName = "".join(guid.split("-")[:-1])
                newPolygon = hb_thermPolygon(splitGeo, polygon.material, polyName, polygon.plane, None)
                newThermPolygons.append(newPolygon)
        else:
            newThermPolygons.append(polygon)
    thermPolygons = newThermPolygons
    
    
    # Check the polygon geometry
    for polygon in thermPolygons:
        # Check if the surface is in the same plane as the other geometry.
        if abs(polygon.normalVector.X - basePlaneNormal.X) < tol and abs(polygon.normalVector.Y - basePlaneNormal.Y) < tol and abs(polygon.normalVector.Z - basePlaneNormal.Z) < tol: pass
        else:
            polyNormalRev = rc.Geometry.Vector3d(polygon.normalVector)
            polyNormalRev.Reverse()
            if abs(polyNormalRev.X - basePlaneNormal.X)< tol and abs(polyNormalRev.Y - basePlaneNormal.Y) < tol and abs(polyNormalRev.Z - basePlaneNormal.Z) < tol:
                polygon.normalVector = polyNormalRev
                polygon.plane.Flip()
                polygon.geometry.Flip()
            else:
                checkData = False
                warning = "The geometry for polygon with material " + polygon.material + " is not in the same plane as the other connected geometry."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        # Check to be sure that the polyline geomtry is clockwise in the base plane.
        if str(polygon.polylineGeo.ClosedCurveOrientation(basePlane)) == 'CounterClockwise':
            polygon.polylineGeo.Reverse()
        # Remake the list of vertices so that we are sure they are oriented clockwise.
        polygon.vertices = []
        for segment in polygon.polylineGeo.DuplicateSegments():
            polygon.vertices.append(segment.PointAtStart)
    
    # Check the BC geometry
    for boundary in thermBCs:
        # Check if the surface is in the same plane as the other geometry.
        if boundary.geometry.SpanCount == 1: boundary.normalVector = basePlaneNormal
        elif abs(boundary.normalVector.X - basePlaneNormal.X) < tol and abs(boundary.normalVector.Y - basePlaneNormal.Y) < tol and abs(boundary.normalVector.Z - basePlaneNormal.Z) < tol:pass
        else:
            boundaryNormalRev = rc.Geometry.Vector3d(boundary.normalVector)
            boundaryNormalRev.Reverse()
            if abs(boundaryNormalRev.X - basePlaneNormal.X) < tol and abs(boundaryNormalRev.Y - basePlaneNormal.Y) < tol and abs(boundaryNormalRev.Z - basePlaneNormal.Z) < tol:
                boundary.normalVector = boundaryNormalRev
                boundary.plane.Flip()
            else:
                checkData = False
                warning = "Geometry for boundary " + boundary.name + " with temperature " + boundary.BCProperties['Temperature'] + " is not in the same plane as the other connected geometry."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    if checkData == False:
        return -1
    
    # Make sure that the Therm polygons form a single polysurface.
    allPolygonGeo = []
    for polygon in thermPolygons:
        allPolygonGeo.append(polygon.geometry)
    joinedPolygons = rc.Geometry.Brep.JoinBreps(allPolygonGeo, sc.doc.ModelAbsoluteTolerance)
    if len(joinedPolygons) != 1:
        warning = "Geometry connected to _polygons does not form a single polysurface and THERM does not like this. \n" + \
        "A thermFile will still be written but you will have to finish making the geometry in THERM."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    # Make sure that the polysurface does not have any holes (only one set of naked edges).
    polygonBoundaries = []
    polygonBoundariesEdges = joinedPolygons[0].Edges
    for edge in polygonBoundariesEdges:
        if str(edge.Valence) == 'Naked': polygonBoundaries.append(edge.ToNurbsCurve())
    # The DuplicateNakedEdgeCurves method does not work on everyone's machine and so I am using the code above for the time being.
    # polygonBoundaries = joinedPolygons[0].DuplicateNakedEdgeCurves(True, True)
    allBoundary = rc.Geometry.PolylineCurve.JoinCurves(polygonBoundaries, sc.doc.ModelAbsoluteTolerance)
    if len(allBoundary) != 1:
        boundLengths = []
        for bnd in allBoundary: boundLengths.append(bnd.GetLength())
        boundLengths, allBoundary = zip(*sorted(zip(boundLengths, allBoundary)))
        encircling = allBoundary[-1]
        warning = "Geometry connected to _polygons does not have a single boundary (there are holes in the model). \n You will have to fill in these gaps when you bring your model into THERM. \n Note that air gaps in your model can be represented with a polygon having an 'air' material."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        # Check to be sure the curve is facing counter-clockwise.
        encircling = allBoundary[0]
    if str(encircling.ClosedCurveOrientation(basePlane)) == 'CounterClockwise':
        encircling.Reverse()
    polygonBoundaries = encircling.DuplicateSegments()
    
    # Get the centroid of all geometry
    allGeoCentroid = rc.Geometry.AreaMassProperties.Compute(joinedPolygons[0]).Centroid
    
    return workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, polygonBoundaries, thermFileOrigin, allGeoCentroid

def calcBestFitVector(vertices, basePlane):
    #Transform all points into the XY Plane
    transformToXY = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, basePlane)
    for pt in vertices: pt.Transform(transformToXY)
    
    #Compute some things we need.
    sumx = 0
    sumy = 0
    sumx2 = 0
    sumy2 = 0
    sumxy = 0
    for pt in vertices:
        x = pt.X
        y = pt.Y
        sumx  = sumx  + x
        sumy  = sumy  + y
        sumx2 = sumx2 + (x * x)
        sumy2 = sumy2 + (y * y)
        sumxy = sumxy + (x * y)
    sxx = sumx2 - (sumx * sumx / len(vertices))
    syy = sumy2 - (sumy * sumy / len(vertices))
    sxy = sumxy - (sumx * sumy / len(vertices))
    
    #Compute a slope vector in the XY plane.
    if sxx < sc.doc.ModelAbsoluteTolerance: slopeVec = rc.Geometry.Vector3d.YAxis
    else:
        slopeVec = rc.Geometry.Vector3d(sxx, sxy, 0)
        slopeVec.Unitize()
    
    #Transform the slope vector back to the original plane
    transformFromXY = rc.Geometry.Transform.ChangeBasis(basePlane, rc.Geometry.Plane.WorldXY)
    slopeVec.Transform(transformFromXY)
    
    return slopeVec

def dictToXMLBC(dict, startTag, dataType):
    def makeStr(keys, xmlStr):
        for item in keys:
            xmlStr = xmlStr + str(item)
            xmlStr = xmlStr + '="'
            xmlStr = xmlStr + str(dict[item])
            xmlStr = xmlStr + '" '
        return xmlStr
    
    xmlStr = '\t<' + dataType + ' '
    keys1 = ['Name', 'Type', 'H', 'HeatFlux', 'Temperature', 'RGBColor']
    keys2 = ['Tr', 'Hr', 'Ei', 'Viewfactor', 'RadiationModel']
    keys3 = ['ConvectionFlag', 'FluxFlag', 'RadiationFlag', 'ConstantTemperatureFlag', 'EmisModifier']
    xmlStr = makeStr(keys1, xmlStr)
    xmlStr = xmlStr + '\n\t\t'
    xmlStr = makeStr(keys2, xmlStr)
    xmlStr = xmlStr + '\n\t\t'
    xmlStr = makeStr(keys3, xmlStr)
    xmlStr = xmlStr + '/>\n'
    return xmlStr

def dictToXMLSimple(dict, startTag, dataType):
    xmlStr = '\t<' + dataType + ' '
    if dataType == 'Material':
        try:
            test = dict["CavityModel"]
            keys = ['Name', 'Type', 'Conductivity', 'Absorptivity', 'Emissivity', 'RGBColor', 'CavityModel']
        except:
            keys = ['Name', 'Type', 'Conductivity', 'Absorptivity', 'Emissivity', 'RGBColor']
            dict['Type'] = 0
    elif dataType == 'BoundaryCondition': keys = ['Name', 'Type', 'H', 'HeatFlux', 'Temperature', 'RGBColor', 'Tr', 'Hr', 'Ei', 'Viewfactor', 'RadiationModel', 'ConvectionFlag', 'FluxFlag', 'RadiationFlag', 'ConstantTemperatureFlag', 'EmisModifier']
    elif dataType == 'Polygon': keys = ['ID', 'Material', 'NSides', 'Type', 'units']
    elif dataType == 'Point': keys = ['index', 'x', 'y']
    elif dataType == 'BCPolygon': keys = ['ID', 'BC', 'units', 'PolygonID', 'EnclosureID', 'UFactorTag', 'Emissivity']
    else: keys = dict.keys()
    for count, item in enumerate(keys):
        xmlStr = xmlStr + str(item)
        xmlStr = xmlStr + '="'
        xmlStr = xmlStr + str(dict[item])
        xmlStr = xmlStr + '" '
    if startTag: xmlStr = xmlStr[:-1] + '>'
    else: xmlStr = xmlStr + '/>'
    xmlStr = xmlStr + '\n'
    return xmlStr

def dictToXMLComplex(propList, dataType):
    xmlStr = ''
    for lineCount, line in enumerate(propList):
        if lineCount == 0: xmlStr = xmlStr + dictToXMLSimple(line, True, dataType)
        else: xmlStr = xmlStr + '\t' + dictToXMLSimple(line, False, 'Point')
    xmlStr = xmlStr + '\t</' + dataType + '>\n'
    return xmlStr

permittedAbbreviations = ['NFRC', 'CEN']
def checkAbbreviations(matName):
    for abbrev in permittedAbbreviations:
        if abbrev.title() in matName: matName = matName.replace(abbrev.title(), abbrev.upper())
    return matName


def main(workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin, allGeoCentroid, conversionFactor):
    #Call the needed classes.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    thermMatLib = sc.sticky["honeybee_thermMaterialLib"]
    thermDefault = sc.sticky["honeybee_ThermDefault"]()
    
    #Make a set of transformations from Rhino world coordinates to the Therm scene.
    #Check the units of the Rhino file and scale everything from meters to millimeters. Keep track of this transformation as well.
    planeReorientation = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, basePlane)
    unitsScale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, conversionFactor, conversionFactor, conversionFactor)
    bufferTansl = rc.Geometry.Transform.Translation(250, -50, 0)
    
    #Set the tolerance at the default THERM tolerance.
    numDecPlaces = 2
    
    
    ###CHECK THE POLYGONS AND ASSEMBLE THEM INTO DICTIONARIES.
    allMaterials = []
    materialNames = []
    allPolygon = []
    airCavityPolygons = []
    for pCount, polygon in enumerate(thermPolygons):
        #Check the material.
        if polygon.material not in materialNames:
            materialNames.append(polygon.material)
            try:
                matFromLib = copy.deepcopy(thermMatLib[polygon.material])
                matFromLib["Name"] = matFromLib["Name"].title()
                correctFormatCol = str(System.Drawing.ColorTranslator.ToHtml(matFromLib["RGBColor"]))
                if not correctFormatCol.startswith('#'):
                    color = System.Drawing.Color.FromName(correctFormatCol)
                    correctFormatCol = System.String.Format("#{0:X2}{1:X2}{2:X2}", color.R, color.G, color.B)
                matFromLib["RGBColor"] = correctFormatCol.replace('#', '0x')
                matFromLib["Name"] = checkAbbreviations(matFromLib["Name"])
                #Check for frame cavity materials.
                if matFromLib["Type"] == 1:
                    if 'Frame Cavity Slightly Ventilated NFRC' in matFromLib["Name"]: matFromLib["CavityModel"] = 5
                    elif 'Frame Cavity NFRC 100' in matFromLib["Name"]: matFromLib["CavityModel"] = 4
                    elif 'Frame Cavity - CEN Simplified' in matFromLib["Name"]: matFromLib["CavityModel"] = 1
                    else:
                        try:
                            matFromLib["CavityModel"] = matFromLib["CavityModel"]
                        except:
                            matFromLib["CavityModel"] = 4
                allMaterials.append(matFromLib)
            except:
                warning = "The material " + polygon.material + " could not be found in your material library. \n Make sure your HB_HB component is in the back of your GH canvas by selecting it and hitting Cntrl+B. \n Then, right click on the GH canvas and hit 'recompute.'"
                print warning
                ghenv.Component.AddRuntimeMessage(e, warning)
                return -1
        
        #Check if the polygon is an air material.
        matFromLib = copy.deepcopy(thermMatLib[polygon.material])
        if matFromLib["Type"] == 1:
            airCavityPolygons.append(polygon.geometry)
        
        #Build up a dictionary of properties.
        polygonDesc = []
        
        polygonProp = {}
        polygonProp['ID'] = str(pCount+1)
        matName = polygon.material.title()
        matName = checkAbbreviations(matName)
        polygonProp['Material'] = matName
        polygonProp['NSides'] = str(len(polygon.vertices))
        polygonProp['Type'] = "1"
        polygonProp['units'] = "mm"
        polygonDesc.append(polygonProp)
        
        #Write the transformed geometry into the dictionary.
        for vertCount, vertex in enumerate(polygon.vertices):
            vertTrans = rc.Geometry.Point3d(vertex)
            vertTrans.Transform(planeReorientation)
            vertTrans.Transform(unitsScale)
            vertTrans.Transform(bufferTansl)
            vertTransDict = {'index': str(vertCount), 'x': str(round(vertTrans.X, numDecPlaces)), 'y': str(round(vertTrans.Y, numDecPlaces))}
            polygonDesc.append(vertTransDict)
        
        allPolygon.append(polygonDesc)
    
    
    ###CHECK THE BOUNDARY CONDITIONS AND ASSEMBLE THEM INTO DICTIONARIES.
    matchedBoundaries = []
    boundConditions = []
    boundConditNames = []
    boundConditions.append(thermDefault.adiabaticBCProperties)
    for boundcondit in thermBCs:
        if boundcondit.BCProperties['Name'] not in boundConditNames:
            boundConditNames.append(boundcondit.BCProperties['Name'])
            boundFromLib = copy.deepcopy(boundcondit.BCProperties)
            boundFromLib['Name'] = boundFromLib['Name'].title()
            boundConditions.append(boundFromLib)
    
    #Figure out the properties of the individual segments.
    allBound = []
    boundCount = (len(thermPolygons)*2)+1
    boundForAirFilm = {'bTypeName' : [], 'geometry' : [], 'emissivity' : []}
    for boundSeg in allBoundary:
        #Set up a dictionary to hold the information on the segment.
        boundDesc = []
        boundProp =  {}
        segStartPt = boundSeg.PointAtStart
        segEndPt = boundSeg.PointAtEnd
        
        #Set a default BC of adiabatic.
        boundType = 'Adiabatic'
        boundGeoProp = {'UFactorTag': '', 'ID': str(boundCount), 'BC': 'Exterior', 'Emissivity': '0.900000', 'EnclosureID': '0'}
        matEmiss = 0.9
        
        #Find the Therm polygon associated with the boundary.
        PolygonID = None
        for pCount, polygon in enumerate(thermPolygons):
            polyGeo = polygon.polylineGeo
            if str(polyGeo.Contains(segEndPt, basePlane, sc.doc.ModelAbsoluteTolerance)) == 'Coincident' and str(polyGeo.Contains(segStartPt, basePlane, sc.doc.ModelAbsoluteTolerance)) == 'Coincident':
                PolygonID = pCount+1
                boundGeoProp['Emissivity'] = thermMatLib[polygon.material]['Emissivity']
                matEmiss = thermMatLib[polygon.material]['Emissivity']
        
        #Check if the boundary aligns with any of the connected boundaries_.
        for boundary in thermBCs:
            boundGeo = boundary.geometry
            closestEndPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
            closestStartPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segStartPt, sc.doc.ModelAbsoluteTolerance*2)[0]
            if closestEndPt and closestStartPt:
                boundType = boundary.BCProperties['Name'].title()
                boundGeoProp = copy.deepcopy(boundary.BCGeo)
                if boundary.emissivityOverride == None: boundGeoProp['Emissivity'] = matEmiss
                else: boundGeoProp['Emissivity'] = boundary.emissivityOverride
                boundGeoProp['ID'] = str(boundCount)
                if boundType not in matchedBoundaries: matchedBoundaries.append(boundType)
                if boundary.uFactorTag != None: boundGeoProp['UFactorTag'] = boundary.uFactorTag
        
        #put all of the properties into the dictionary.
        boundProp['ID'] = boundGeoProp['ID']
        boundProp['BC'] = boundType
        boundProp['units'] = "mm"
        boundProp['PolygonID'] = PolygonID
        boundProp['EnclosureID'] = boundGeoProp['EnclosureID']
        boundProp['UFactorTag'] = boundGeoProp['UFactorTag']
        boundProp['Emissivity'] = boundGeoProp['Emissivity']
        boundDesc.append(boundProp)
        
        #Put the transformed vertices into the dictionary.
        segStartPtTrans = rc.Geometry.Point3d(segStartPt)
        segStartPtTrans.Transform(planeReorientation)
        segStartPtTrans.Transform(unitsScale)
        segStartPtTrans.Transform(bufferTansl)
        startPtDict = {'index': '0', 'x': str(round(segStartPtTrans.X, numDecPlaces)), 'y': str(round(segStartPtTrans.Y, numDecPlaces))}
        
        segEndPtTrans = rc.Geometry.Point3d(segEndPt)
        segEndPtTrans.Transform(planeReorientation)
        segEndPtTrans.Transform(unitsScale)
        segEndPtTrans.Transform(bufferTansl)
        endPtDict = {'index': '1', 'x': str(round(segEndPtTrans.X, numDecPlaces)), 'y': str(round(segEndPtTrans.Y, numDecPlaces))}
        
        boundDesc.append(startPtDict)
        boundDesc.append(endPtDict)
        
        allBound.append(boundDesc)
        boundCount += 1
        
        #Add values to the airfilm dictionary.
        boundForAirFilm['bTypeName'].append(boundType)
        boundForAirFilm['geometry'].append(boundSeg)
        boundForAirFilm['emissivity'].append(boundProp['Emissivity'])
    
    #If someone has not specified a numerical value for air film, then auto-calculate the film coefficeint based on the Rhino geometry and emissivity of materials.
    for boundaryType in boundConditions:
        if boundaryType['H'] == 'OUTDOOR': boundaryType['H'] = '22.7'
        elif boundaryType['H'] == 'INDOOR':
            #Find all of the segments that this BCType references and get their average emissivity and slope in the Rhino scene.
            emissivities = []
            lengths = []
            lineSegs = []
            for bCount, boundName in enumerate(boundForAirFilm['bTypeName']):
                if boundName == boundaryType['Name']:
                    emissivities.append(boundForAirFilm['emissivity'][bCount])
                    lengths.append(boundForAirFilm['geometry'][bCount].GetLength())
                    lineSegs.append(boundForAirFilm['geometry'][bCount])
            #Compute an average emissivity that is wieghted by the length of the segments.
            totalLength = sum(lengths)
            emissWeights = []
            for count, val in enumerate(lengths): emissWeights.append((val*emissivities[count])/totalLength)
            weightAvgEmiss = sum(emissWeights)
            
            #Compute an average direction of heat flow across the boundary.
            segmentVertices = []
            fullPolylines = rc.Geometry.PolylineCurve.JoinCurves(lineSegs, sc.doc.ModelAbsoluteTolerance)
            for pLine in fullPolylines:
                curveParameters = pLine.DivideByCount(10, True)
                for param in curveParameters: segmentVertices.append(pLine.PointAt(param))
            segmentVerticesCopy = copy.deepcopy(segmentVertices)
            try:
                heatFlowDirect = calcBestFitVector(segmentVerticesCopy, basePlane)
            except:
                heatFlowDirect = rc.Geometry.Vector3d.XAxis
            heatFlowDirect.Rotate(math.radians(90), basePlane.Normal)
            #Compute the area centriod of the polylines and use the relationship between this area centriod and that of all geometry to determine whether heat flow needs to be flipped.
            xVals = []; yVals = []; zVals = []
            for pt in segmentVertices:
                xVals.append(pt.X)
                yVals.append(pt.Y)
                zVals.append(pt.Z)
            try:
                boundCentroid = rc.Geometry.Point3d(sum(xVals)/len(xVals), sum(yVals)/len(xVals), sum(zVals)/len(xVals))
            except:
                boundCentroid = rc.Geometry.Point3d.Origin
            roughHeatFlowDirect = rc.Geometry.Point3d.Subtract(allGeoCentroid, boundCentroid)
            if rc.Geometry.Vector3d.VectorAngle(heatFlowDirect, roughHeatFlowDirect) > 90: heatFlowDirect.Reverse()
            #Turn the heat flow direction into a dimensionless value for a linear interoplation.
            dimHeatFlow = 1 - (math.degrees(rc.Geometry.Vector3d.VectorAngle(heatFlowDirect, rc.Geometry.Vector3d.ZAxis))/180)
            
            #Compute a film coefficient from the emissivity, heat flow direction, and a paramterization of AHSHRAE fundemantals.
            heatFlowFactor = (-12.443 * (math.pow(dimHeatFlow,3))) + (24.28 * (math.pow(dimHeatFlow,2))) - (16.898 * dimHeatFlow) + 8.1275
            filmCoeff = (heatFlowFactor * dimHeatFlow) + (5.81176 * weightAvgEmiss) + 0.9629
            boundaryType['H'] = str(filmCoeff)
    allNotMatched = False
    if len(thermBCs) != len(matchedBoundaries): allNotMatched = True
    
    
    #WRITE IN BOUNDARY CONDITIONS FOR AIR MATERIALS.
    #Find any air gaps in the construction and, if found, make default NFRC boundaries for the air gap.
    frameCavityBounds = []
    if len(airCavityPolygons) != 0:
        #Extract the boundary of all joined air polygons.
        joinedAirPolygons = rc.Geometry.Brep.JoinBreps(airCavityPolygons, sc.doc.ModelAbsoluteTolerance)
        for airPoly in joinedAirPolygons:
            polygonBoundaries = []
            polygonBoundariesEdges = airPoly.Edges
            for edge in polygonBoundariesEdges:
                if str(edge.Valence) == 'Naked': polygonBoundaries.append(edge.ToNurbsCurve())
            #polygonBoundaries = airPoly.DuplicateNakedEdgeCurves(True, True)
            allAirBoundary = rc.Geometry.PolylineCurve.JoinCurves(polygonBoundaries, sc.doc.ModelAbsoluteTolerance)
            for encircling in allAirBoundary:
                #Check to be sure the curve is facing clockwise.
                if str(encircling.ClosedCurveOrientation(basePlane)) == 'Clockwise':
                    encircling.Reverse()
                frameCavityBounds.append(encircling.DuplicateSegments())
        
        for enclosureCount, enclosure in enumerate(frameCavityBounds):
            for airSegment in enclosure:
                #Define Default Parameters.
                boundDesc = []
                boundProp = {'UFactorTag': '', 'ID': str(boundCount), 'BC': 'Frame Cavity Surface', 'Emissivity': '0.900000', 'EnclosureID': str(enclosureCount+1), 'PolygonID': '0', 'units': "mm"}
                segEndPt = airSegment.PointAtEnd
                segStartPt = airSegment.PointAtStart
                boundCount += 1
                
                #Find the Therm polygon associated with the boundary.
                PolygonID = None
                for pCount, polygon in enumerate(thermPolygons):
                    polyGeo = polygon.polylineGeo
                    if str(polyGeo.Contains(segEndPt, basePlane, sc.doc.ModelAbsoluteTolerance)) == 'Coincident' and str(polyGeo.Contains(segStartPt, basePlane, sc.doc.ModelAbsoluteTolerance)) == 'Coincident':
                        if sc.sticky["honeybee_thermMaterialLib"][polygon.material]['Type'] == 1: boundProp['PolygonID'] = pCount+1
                        else: boundProp['Emissivity'] = thermMatLib[polygon.material]['Emissivity']
                
                #First, check if the user has specified any boundary conditions for the air cavity.
                if allNotMatched:
                    #Check if the boundary aligns with any of the connected boundaries_.
                    for boundary in thermBCs:
                        boundGeo = boundary.geometry
                        #print rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                        closestEndPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                        closestStartPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segStartPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                        if closestEndPt and closestStartPt:
                            if boundary.emissivityOverride != None: boundProp['Emissivity'] = boundary.emissivityOverride
                            if boundary.uFactorTag != None: boundProp['UFactorTag'] = boundary.uFactorTag
                            if boundary.name not in matchedBoundaries: matchedBoundaries.append(boundary.name)
                
                boundDesc.append(boundProp)
                
                #Put the transformed vertices into the dictionary.
                segStartPtTrans = rc.Geometry.Point3d(segStartPt)
                segStartPtTrans.Transform(planeReorientation)
                segStartPtTrans.Transform(unitsScale)
                segStartPtTrans.Transform(bufferTansl)
                startPtDict = {'index': '0', 'x': str(round(segStartPtTrans.X, numDecPlaces)), 'y': str(round(segStartPtTrans.Y, numDecPlaces))}
                
                segEndPtTrans = rc.Geometry.Point3d(segEndPt)
                segEndPtTrans.Transform(planeReorientation)
                segEndPtTrans.Transform(unitsScale)
                segEndPtTrans.Transform(bufferTansl)
                endPtDict = {'index': '1', 'x': str(round(segEndPtTrans.X, numDecPlaces)), 'y': str(round(segEndPtTrans.Y, numDecPlaces))}
                
                boundDesc.append(startPtDict)
                boundDesc.append(endPtDict)
                
                allBound.append(boundDesc)
        
        #Add the frame cavity surface to the BC types to write into the header.
        boundConditions.append(thermDefault.frameCavityBCProperties)
    
    
    if len(thermBCs) != len(matchedBoundaries):
        #Try one final attempt to see if the boundaries are specified at a finer resolution than that of the material polygons.
        boundsToRemove = []
        newMatchedBnds = []
        polygonToChange = []
        polygonNewSegments = []
        for boundar in thermBCs:
            if boundar.name.title() not in matchedBoundaries:
                segEndPt = boundar.geometry.PointAtEnd
                segStartPt = boundar.geometry.PointAtStart
                for segmentCount, segment in enumerate(allBoundary):
                    closestEndPt = rc.Geometry.PolylineCurve.ClosestPoint(segment, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                    closestStartPt = rc.Geometry.PolylineCurve.ClosestPoint(segment, segStartPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                    if closestEndPt and closestStartPt:
                        #Add the boundary to the lists to keep track of everything.
                        if boundar.name not in newMatchedBnds: newMatchedBnds.append(boundar.name)
                        if allBound[segmentCount][0]['ID'] not in boundsToRemove: boundsToRemove.append(allBound[segmentCount][0]['ID'])
                        if allBound[segmentCount][0]['PolygonID'] not in polygonToChange: polygonToChange.append(allBound[segmentCount][0]['PolygonID'])
                        #Define Default Parameters.
                        boundDesc = []
                        boundProp = {'UFactorTag': '', 'ID': str(boundCount), 'BC': boundar.name, 'Emissivity': allBound[segmentCount][0]['Emissivity'], 'EnclosureID': "0", 'PolygonID': allBound[segmentCount][0]['PolygonID'], 'units': "mm"}
                        #Change defaults if they are specified.
                        if boundar.uFactorTag != None: boundProp['UFactorTag'] = boundar.uFactorTag
                        if boundar.emissivityOverride != None: boundProp['Emissivity'] = boundar.emissivityOverride
                        boundDesc.append(boundProp)
                        #Check to make sure that the boundary is facing the direction of the full boundary line.
                        boundarLine = rc.Geometry.Line(segStartPt, segEndPt)
                        boundLineDir = boundarLine.Direction
                        boundLineDir.Unitize()
                        segDir = rc.Geometry.Line(segment.PointAtStart, segment.PointAtEnd).Direction
                        segDir.Unitize()
                        if boundLineDir != segDir:
                            segStartPtCopy = rc.Geometry.Point3d(segStartPt)
                            segStartPt = rc.Geometry.Point3d(segEndPt)
                            segEndPt = segStartPtCopy
                        polygonNewSegments.append(rc.Geometry.LineCurve(rc.Geometry.Point3d(segStartPt), rc.Geometry.Point3d(segEndPt)))
                        #Put the transformed vertices into the dictionary.
                        segStartPtTrans = rc.Geometry.Point3d(segStartPt)
                        segStartPtTrans.Transform(planeReorientation)
                        segStartPtTrans.Transform(unitsScale)
                        segStartPtTrans.Transform(bufferTansl)
                        startPtDict = {'index': '0', 'x': str(round(segStartPtTrans.X, numDecPlaces)), 'y': str(round(segStartPtTrans.Y, numDecPlaces))}
                        
                        segEndPtTrans = rc.Geometry.Point3d(segEndPt)
                        segEndPtTrans.Transform(planeReorientation)
                        segEndPtTrans.Transform(unitsScale)
                        segEndPtTrans.Transform(bufferTansl)
                        endPtDict = {'index': '1', 'x': str(round(segEndPtTrans.X, numDecPlaces)), 'y': str(round(segEndPtTrans.Y, numDecPlaces))}
                        
                        boundDesc.append(startPtDict)
                        boundDesc.append(endPtDict)
                        
                        allBound.append(boundDesc)
                        boundCount += 1
        #Remove the replaced boundaries from the list.
        newAllBound = []
        for currentBound in allBound:
            if currentBound[0]['ID'] not in boundsToRemove:newAllBound.append(currentBound)
        allBound = newAllBound
        matchedBoundaries.extend(newMatchedBnds)
        #Re-create polygons where the vertices have changed.
        newPolygons = []
        for pCount, polygon in enumerate(thermPolygons):
            if pCount+1 in polygonToChange:
                newLineSegments = []
                polyGeoSegments = polygon.polylineGeo.DuplicateSegments()
                for segm in polyGeoSegments:
                    replaceSeg = False
                    for pSeg in polygonNewSegments:
                        segStartPt = pSeg.PointAtStart
                        segEndPt = pSeg.PointAtEnd
                        closestEndPt = rc.Geometry.PolylineCurve.ClosestPoint(segm, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                        closestStartPt = rc.Geometry.PolylineCurve.ClosestPoint(segm, segStartPt, sc.doc.ModelAbsoluteTolerance*2)[0]
                        if closestEndPt and closestStartPt:
                            newLineSegments.append(pSeg)
                            replaceSeg = True
                    if replaceSeg == False: newLineSegments.append(segm)
                newPolyline = rc.Geometry.PolylineCurve.JoinCurves(newLineSegments, sc.doc.ModelAbsoluteTolerance, True)[0]
                if newPolyline.IsClosed == False:
                    closingLine = rc.Geometry.LineCurve(newPolyline.PointAtEnd, newPolyline.PointAtStart)
                    newPolyline = rc.Geometry.PolylineCurve.JoinCurves([newPolyline, closingLine], sc.doc.ModelAbsoluteTolerance, True)[0]
                polygonDesc = [allPolygon[pCount][0]]
                #Write the transformed geometry into the dictionary.
                for vertCount, vertex in enumerate(newPolyline.DuplicateSegments()):
                    vertTrans = rc.Geometry.Point3d(vertex.PointAtStart)
                    vertTrans.Transform(planeReorientation)
                    vertTrans.Transform(unitsScale)
                    vertTrans.Transform(bufferTansl)
                    vertTransDict = {'index': str(vertCount), 'x': str(round(vertTrans.X, numDecPlaces)), 'y': str(round(vertTrans.Y, numDecPlaces))}
                    polygonDesc.append(vertTransDict)
                
                newPolygons.append(polygonDesc)
            else:
                newPolygons.append(allPolygon[pCount])
        allPolygon = newPolygons
    
    #Check to be sure that all boundaries_ have been matched with _polygons and, if not, give a warning that the BC is being left out.
    if len(thermBCs) != len(matchedBoundaries):
        allBndNames = []
        for b in thermBCs: allBndNames.append(b.name)
        for name in allBndNames:
            if name.title() not in matchedBoundaries:
                warning = "The boundary '" + name + "' could not be matched with the rest of the connected geometry and is therefore being left out of the exported THERM file. \n To include it in the export, make sure that this boundary's geometry is flush with your the edges of your _polygons."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    
    #CHECK THE ORIENTATION OF THE PLANE IN THE RHINO SCENE.
    #Specify it either as a sill or jamb.
    CrossSectionType = 'Sill'
    if basePlane.Normal.Z < -0.70710678118 or basePlane.Normal.Z > 0.70710678118: CrossSectionType = 'Jamb'
    
    #CHECK THE MESH LEVEL.
    if meshLevel_:
        meshLevel = str(meshLevel_)
        if meshLevel_ > 8:
            meshLevel = "8"
            warning = "Therm cannot simulate a mesh level greater than 8. It will be automatically changed to 8 for you."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else: meshLevel = '6'
    
    
    ### WRITE EVERYTHING TO THERM FILE
    #Set up the file.
    xmlFilePath = workingDir + xmlFileName + '.thmx'
    uFactorFile = workingDir + xmlFileName + '_thmx.thmx'
    resultDataPath = workingDir + xmlFileName + '_thmx.o'
    xmlFile = open(xmlFilePath, "w")
    
    #HEADER
    #Keep track of the transformations used to convert between Rhino space and THERM space. Write it into the XML so that results can be read back onto the original geometry after running THERM.
    headerStr = '<?xml version="1.0"?>\n' + \
        '<THERM-XML xmlns="http://windows.lbl.gov">\n' + \
        '<ThermVersion>Version 7.3.2.0</ThermVersion>\n' + \
        '<SaveDate>' + str(datetime.datetime.now()) + '</SaveDate>\n' + \
        '\n' + \
        '<Title>' + xmlFileName + '</Title>\n' + \
        '<CreatedBy>' + os.getenv("USERNAME")+ '</CreatedBy>\n' + \
        '<Company></Company>\n' + \
        '<Client></Client>\n' + \
        '<CrossSectionType>'+ CrossSectionType + '</CrossSectionType>\n' + \
        '<Notes>RhinoUnits-' + str(sc.doc.ModelUnitSystem) + ', RhinoOrigin-'+ '(' + str(thermFileOrigin.X) + ',' + str(thermFileOrigin.Y) + ',' + str(thermFileOrigin.Z) + '), RhinoXAxis-'+ '(' + str(basePlane.XAxis.X) + ',' + str(basePlane.XAxis.Y) + ',' + str(basePlane.XAxis.Z) + '), RhinoYAxis-'+ '(' + str(basePlane.YAxis.X) + ',' + str(basePlane.YAxis.Y) + ',' + str(basePlane.YAxis.Z) + '), RhinoZAxis-'+ '(' + str(basePlane.ZAxis.X) + ',' + str(basePlane.ZAxis.Y) + ',' + str(basePlane.ZAxis.Z)+')</Notes>\n' + \
        '<Units>SI</Units>\n' + \
        '<MeshControl MeshLevel="' + meshLevel + '" ErrorCheckFlag="1" ErrorLimit="10.000000" MaxIterations="5" CMAflag="0" />\n'
    xmlFile.write(headerStr)
    
    
    #MATERIALS
    xmlFile.write('<Materials>\n')
    for material in allMaterials:
        xmlFile.write(dictToXMLSimple(material, False, 'Material'))
    xmlFile.write('</Materials>\n')
    
    
    #BOUNDARY CONDITIONS
    xmlFile.write('<BoundaryConditions>\n')
    for bound in boundConditions:
        xmlFile.write(dictToXMLBC(bound, False, 'BoundaryCondition'))
    xmlFile.write('</BoundaryConditions>\n')
    
    
    #POLYGONS
    xmlFile.write('<Polygons>\n')
    for polygon in allPolygon:
        xmlFile.write(dictToXMLComplex(polygon, 'Polygon'))
    xmlFile.write('</Polygons>\n')
    
    
    #BOUNDARIES
    xmlFile.write('<Boundaries>\n')
    for boundSeg in allBound:
        xmlFile.write(dictToXMLComplex(boundSeg, 'BCPolygon'))
    xmlFile.write('</Boundaries>\n')
    
    
    #RESULTS
    xmlFile.write('<Results>\n')
    xmlFile.write('\t<Case>\n')
    xmlFile.write('\t\t<FrameCavities>\n')
    xmlFile.write('\t\t</FrameCavities>\n')
    xmlFile.write('\t</Case>\n')
    xmlFile.write('</Results>\n')
    xmlFile.write('</THERM-XML>\n')
    
    xmlFile.close()
    
    return xmlFilePath, uFactorFile, resultDataPath




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

#If the Rhino model tolerance is not fine enough for THERM modelling, give a warning.
if initCheck == True:
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    conversionFactor = lb_preparation.checkUnits()*1000
    d = decimal.Decimal(str(sc.doc.ModelAbsoluteTolerance))
    numDecPlaces = abs(d.as_tuple().exponent)
    numConversionFacPlaces = len(list(str(int(conversionFactor))))-1
    numDecPlaces = numDecPlaces - numConversionFacPlaces
    if numDecPlaces < 2:
        zeroText = ''
        for val in range(abs(2-numDecPlaces)): zeroText = zeroText + '0'
        correctDecimal = '0.' + zeroText + str(sc.doc.ModelAbsoluteTolerance).split('.')[-1]
        warning = "Your Rhino model tolerance is coarser than the default tolerance for THERM. \n It is recommended that you decrease your Rhino model tolerance to " + correctDecimal + " " + str(sc.doc.ModelUnitSystem) + " \n by typing 'units' in the Rhino command bar and adding decimal places to the 'tolerance'."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)


#If the intital check is good, run the component.
if initCheck and _writeTHMFile:
    initInputs = checkTheInputs()
    if initInputs != -1:
        workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin, allGeoCentroid = initInputs
        result = main(workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin, allGeoCentroid, conversionFactor)
        if result != -1:
            thermFile, uFactorFile, resultFile = result


