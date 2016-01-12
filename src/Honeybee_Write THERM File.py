#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Provided by Honeybee 0.0.57

    Args:
        _polygons: A list of thermPolygons from one or more "Honeybee_Create Therm Polygons" components.
        _boundaries: A list of thermBoundaries from one or more "Honeybee_Create Therm Boundaries" components.
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
import sys
import System
import Grasshopper.Kernel as gh
import uuid
import math
import copy
import datetime

ghenv.Component.Name = 'Honeybee_Write THERM File'
ghenv.Component.NickName = 'writeTHERM'
ghenv.Component.Message = 'VER 0.0.57\nJAN_12_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nDEC_30_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error



def checkTheInputs():
    #Check the filename.
    xmlFileName = 'unnamed'
    if fileName_ != None:
        if fileName_.upper().endswith('.THMX'): xmlFileName = fileName_.upper().split('.THMX')[0]
        else: xmlFileName = fileName_
    
    #If there is a workingDir, make sure that it exists and, if not, try to make it.
    workingDir = None
    if workingDir_ != None:
        if not os.path.exists(workingDir_):
            try:
                os.makedirs(workingDir_)
                workingDir = workingDir_
            except:
                checkData3 = False
                warning =  'cannot create the working directory as: ', workingDir_ + \
                      '\nPlease set a new working directory.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                return -1
    else:
        if workingDir_ == None: workingDir = sc.sticky["Ladybug_DefaultFolder"] + xmlFileName + '\\THERM\\'
        else: workingDir = workingDir_
        if not os.path.exists(workingDir): os.makedirs(workingDir)
        print 'Current working directory is set to: ' + workingDir
    
    #Call the polygons from the hive.
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        thermPolygons = hb_hive.callFromHoneybeeHive(_polygons)
        thermBCs = hb_hive.callFromHoneybeeHive(_boundaries)
    except:
        warning = "Failed to call _polygons and _boundaries from the HB Hive. \n Make srue that connected geometry to _polygons is from the 'Create Therm Polygons' component \n and that geometry to _boundaries is from the 'Create Therm Boundaries' component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Make sure that the connected objects are of the right type.
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
        warning = "Geometry connected to _boundaries are not valid thermBoundaries from the 'Create Therm Bounrdaies' component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Make sure that all of the geometry is in the same plane.
    basePlaneNormal = copy.copy(thermPolygons[0].normalVector)
    if basePlaneNormal.Z < 0: basePlaneNormal.Reverse()
    
    allPolygonGeo = []
    for polygon in thermPolygons:
        allPolygonGeo.append(polygon.geometry)
    joinedPolygons = rc.Geometry.Brep.JoinBreps(allPolygonGeo, sc.doc.ModelAbsoluteTolerance)
    
    #Establish the reference plane for the THERM scene.
    rhinoZAxis = rc.Geometry.Vector3d(0,0,1)
    refrencePlane = None
    allGeoVertices = joinedPolygons[0].DuplicateVertices()
    allGeometryBB = rc.Geometry.BoundingBox(allGeoVertices)
    if basePlaneNormal == rhinoZAxis: basePlaneOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, False, False)
    else: basePlaneOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, True, False)
    thermFileOrigin = rc.Geometry.BoundingBox.Corner(allGeometryBB, True, True, True)
    basePlane = rc.Geometry.Plane(basePlaneOrigin, basePlaneNormal)
    
    #If the plane is not in the worldXY, rotate it so that the THERM y-axis and Rhino z-axis are aligned.
    def alignYtoZ(basePlane, basePlaneNormal):
        basePlaneNormal.Unitize()
        rhinoZAxis = rc.Geometry.Vector3d(0,0,1)
        if basePlaneNormal != rhinoZAxis:
            planeProject = rc.Geometry.Transform.PlanarProjection(basePlane)
            rhinoZAxis.Transform(planeProject)
            planeRotation = rc.Geometry.Transform.Rotation(basePlane.YAxis, rhinoZAxis, basePlaneOrigin)
            basePlane.Transform(planeRotation)
    
    alignYtoZ(basePlane, basePlaneNormal)
    
    #If the plane X-Axis is negative, flip it.
    if basePlane.XAxis.X < 0 or basePlane.XAxis.Y < 0 or basePlane.XAxis.Y < 0:
        basePlaneNormal.Reverse()
        basePlane.Flip()
        alignYtoZ(basePlane, basePlaneNormal)
    
    #Check the polygon geometry
    for polygon in thermPolygons:
        if not polygon.normalVector == basePlaneNormal:
            #Check if the normal is just facing the opposite direction.
            polyNormalRev = rc.Geometry.Vector3d(polygon.normalVector)
            polyNormalRev.Reverse()
            if polyNormalRev == basePlaneNormal:
                #print polygon.normalVector
                polygon.normalVector = polyNormalRev
                polygon.plane.Flip()
                polygon.geometry.Flip()
                polygon.polylineGeo.Reverse()
            else:
                checkData = False
                warning = "Geometry for polygon " + polygon.name + " with material " + polygon.material + " is not in the same plane as the other connected geometry."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        else:
            #Ensure vertices are counter-clockwise in order to align with the boundary condition segments.
            polygon.vertices.reverse()
    
    #Check the BC geometry
    for boundary in thermBCs:
        if boundary.geometry.SpanCount == 1:
            boundary.normalVector = basePlaneNormal
        elif not boundary.normalVector == basePlaneNormal:
            #Check if the normal is just facing the opposite direction.
            boundaryNormalRev = rc.Geometry.Vector3d(boundary.normalVector)
            boundaryNormalRev.Reverse()
            if boundaryNormalRev == basePlaneNormal:
                boundary.normalVector = boundaryNormalRev
                boundary.plane.Flip()
                boundary.geometry.Reverse()
                boundary.vertices.reverse()
            else:
                checkData = False
                warning = "Geometry for boundary " + boundary.name + " with temperature " + boundary.BCProperties['Temperature'] + " is not in the same plane as the other connected geometry."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    if checkData == False:
        return -1
    
    #Make sure that the Therm polygons form a single polysurface.
    allPolygonGeo = []
    for polygon in thermPolygons:
        allPolygonGeo.append(polygon.geometry)
    joinedPolygons = rc.Geometry.Brep.JoinBreps(allPolygonGeo, sc.doc.ModelAbsoluteTolerance)
    if len(joinedPolygons) != 1:
        warning = "Geometry connected to _polygons does not form a single polysurface when joined and thus will cause THERM to crash."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    #Make sure that the polysurface does not have any holes (only one set of naked edges).
    polygonBoundaries = joinedPolygons[0].DuplicateNakedEdgeCurves(True, True)
    allBoundary = rc.Geometry.PolylineCurve.JoinCurves(polygonBoundaries, sc.doc.ModelAbsoluteTolerance)
    if len(allBoundary) != 1:
        warning = "Geometry connected to _polygons does not have a single boundary (there are holes in the model). \n These holes will cause THERM to crash. \n Note that air gaps in your model whould be represented with a polygon having an 'air' material."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    else:
        #Check to be sure the curve is facing counter-clockwise.
        encircling = allBoundary[0]
        encricSrf = rc.Geometry.Brep.CreatePlanarBreps(encircling)[0]
        encricSrfPlane = encricSrf.Faces[0].TryGetPlane(sc.doc.ModelAbsoluteTolerance)[-1]
        encricSrfNormal = encricSrfPlane.Normal
        if encricSrfNormal != basePlaneNormal: encircling.Reverse()
        polygonBoundaries = encircling.DuplicateSegments()
    
    
    return workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, polygonBoundaries, thermFileOrigin


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


def main(workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin):
    #Call the needed classes.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    thermMatLib = sc.sticky["honeybee_thermMaterialLib"]
    thermDefault = sc.sticky["honeybee_ThermDefault"]()
    
    #From Rhino world coordinates, make a translatio to the origin of a Therm scene.
    #Check the units of the Rhino file and scale everything from meters to millimeters. Keep track of this transformation as well.
    planeReorientation = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, basePlane)
    conversionFactor = lb_preparation.checkUnits()*1000
    unitsScale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, conversionFactor, conversionFactor, conversionFactor)
    bufferTansl = rc.Geometry.Transform.Translation(250, -50, 0)
    numDecPlaces = len(list(str(sc.doc.ModelAbsoluteTolerance)))-2
    
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
                matFromLib = copy.copy(thermMatLib[polygon.material])
                matFromLib["Name"] = matFromLib["Name"].title()
                correctFormatCol = str(System.Drawing.ColorTranslator.ToHtml(matFromLib["RGBColor"]))
                matFromLib["RGBColor"] = '0x' + correctFormatCol.split('#')[-1]
                matFromLib["Name"] = checkAbbreviations(matFromLib["Name"])
                #Check for frame cavity materials.
                if matFromLib["Type"] == 1:
                    airCavityPolygons.append(polygon.geometry)
                    if 'Frame Cavity Slightly Ventilated NFRC' in matFromLib["Name"]: matFromLib["CavityModel"] = 5
                    elif 'Frame Cavity NFRC 100' in matFromLib["Name"]: matFromLib["CavityModel"] = 4
                    elif 'Frame Cavity - CEN Simplified' in matFromLib["Name"]: matFromLib["CavityModel"] = 1
                allMaterials.append(matFromLib)
            except:
                warning = "The material " + polygon.material + " could not be found in your material library. \n Make sure your HB_HB component is in the back of your GH canvas by selecting it and hitting Cntrl+B. \n Then, right click on the GH canvas and hit 'recompute.'"
                print warning
                ghenv.Component.AddRuntimeMessage(e, warning)
                return -1
        
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
            vertTrans = copy.copy(vertex)
            vertTrans.Transform(planeReorientation)
            vertTrans.Transform(unitsScale)
            vertTrans.Transform(bufferTansl)
            vertTransDict = {'index': str(vertCount), 'x': str(round(vertTrans.X, numDecPlaces)), 'y': str(round(vertTrans.Y, numDecPlaces))}
            polygonDesc.append(vertTransDict)
        
        allPolygon.append(polygonDesc)
    
    
    ###CHECK THE BOUNDARY CONDITIONS AND ASSEMBLE THEM INTO DICTIONARIES.
    boundConditions = []
    boundConditNames = []
    boundConditions.append(thermDefault.adiabaticBCProperties)
    for boundcondit in thermBCs:
        if boundcondit.BCProperties['Name'] not in boundConditNames:
            boundConditNames.append(boundcondit.BCProperties['Name'])
            boundFromLib = copy.copy(boundcondit.BCProperties)
            boundFromLib['Name'] = boundFromLib['Name'].title()
            boundConditions.append(boundFromLib)
    
    #Figure out the properties of the individual segments.
    allBound = []
    boundCount = (len(thermPolygons)*2)+1
    matchedBoundaries = []
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
        
        #Check if the boundary aligns with any of the connected _boundaries.
        for boundary in thermBCs:
            boundGeo = boundary.geometry
            closestEndPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segEndPt, sc.doc.ModelAbsoluteTolerance*2)[0]
            closestStartPt = rc.Geometry.PolylineCurve.ClosestPoint(boundGeo, segStartPt, sc.doc.ModelAbsoluteTolerance*2)[0]
            if closestEndPt and closestStartPt:
                boundType = boundary.BCProperties['Name'].title()
                boundGeoProp = copy.copy(boundary.BCGeo)
                boundGeoProp['Emissivity'] = matEmiss
                boundGeoProp['ID'] = str(boundCount)
                if boundType not in matchedBoundaries: matchedBoundaries.append(boundType)
                if boundary.uFactorTag != None: boundGeoProp['UFactorTag'] = boundary.uFactorTag
        
        #put all of the proerties into the dictionary.
        boundProp['ID'] = boundGeoProp['ID']
        boundProp['BC'] = boundType
        boundProp['units'] = "mm"
        boundProp['PolygonID'] = PolygonID
        boundProp['EnclosureID'] = boundGeoProp['EnclosureID']
        boundProp['UFactorTag'] = boundGeoProp['UFactorTag']
        boundProp['Emissivity'] = boundGeoProp['Emissivity']
        boundDesc.append(boundProp)
        
        #Put the transformed vertices into the dictionary.
        segStartPtTrans = copy.copy(segStartPt)
        segStartPtTrans.Transform(planeReorientation)
        segStartPtTrans.Transform(unitsScale)
        segStartPtTrans.Transform(bufferTansl)
        startPtDict = {'index': '0', 'x': str(round(segStartPtTrans.X, numDecPlaces)), 'y': str(round(segStartPtTrans.Y, numDecPlaces))}
        
        segEndPtTrans = copy.copy(segEndPt)
        segEndPtTrans.Transform(planeReorientation)
        segEndPtTrans.Transform(unitsScale)
        segEndPtTrans.Transform(bufferTansl)
        endPtDict = {'index': '1', 'x': str(round(segEndPtTrans.X, numDecPlaces)), 'y': str(round(segEndPtTrans.Y, numDecPlaces))}
        
        boundDesc.append(startPtDict)
        boundDesc.append(endPtDict)
        
        allBound.append(boundDesc)
        boundCount += 1
    
    #Check to be sure that all _boundaries have been matched with _polygons and, if not, give a warning that the BC is being left out.
    if len(thermBCs) != len(matchedBoundaries):
        allBndNames = []
        for b in thermBCs: allBndNames.append(b.name)
        for name in allBndNames:
            if name not in matchedBoundaries:
                warning = "The boundary '" + name + "' could not be matched with the rest of the connected geometry and is therefore being left out of the exported THERM file. \n To include it in the export, make sure that this boundary's geometry is flush with your the edges of your _polygons."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    #WRITE IN BOUNDARY CONDITIONS FOR AIR MATERIALS.
    #Find any air gaps in the window and, if found, make NFRC boundaries for the air gap.
    #For now, I m not icnluding this functionality until I understand it better.
    frameCavityBounds = []
    if len(airCavityPolygons) != 0:
        #Extract the boundary of all joined air polygons.
        joinedAirPolygons = rc.Geometry.Brep.JoinBreps(airCavityPolygons, sc.doc.ModelAbsoluteTolerance)
        for airPoly in joinedAirPolygons:
            polygonBoundaries = airPoly.DuplicateNakedEdgeCurves(True, True)
            allAirBoundary = rc.Geometry.PolylineCurve.JoinCurves(polygonBoundaries, sc.doc.ModelAbsoluteTolerance)
            for encircling in allAirBoundary:
                #Check to be sure the curve is facing counter-clockwise.
                encricSrf = rc.Geometry.Brep.CreatePlanarBreps(encircling)[0]
                encricSrfPlane = encricSrf.Faces[0].TryGetPlane(sc.doc.ModelAbsoluteTolerance)[-1]
                if encricSrfPlane.Normal != basePlane.Normal: encircling.Reverse()
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
                boundDesc.append(boundProp)
                
                #Put the transformed vertices into the dictionary.
                segStartPtTrans = copy.copy(segStartPt)
                segStartPtTrans.Transform(planeReorientation)
                segStartPtTrans.Transform(unitsScale)
                segStartPtTrans.Transform(bufferTansl)
                startPtDict = {'index': '0', 'x': str(round(segStartPtTrans.X, numDecPlaces)), 'y': str(round(segStartPtTrans.Y, numDecPlaces))}
                
                segEndPtTrans = copy.copy(segEndPt)
                segEndPtTrans.Transform(planeReorientation)
                segEndPtTrans.Transform(unitsScale)
                segEndPtTrans.Transform(bufferTansl)
                endPtDict = {'index': '1', 'x': str(round(segEndPtTrans.X, numDecPlaces)), 'y': str(round(segEndPtTrans.Y, numDecPlaces))}
                
                boundDesc.append(startPtDict)
                boundDesc.append(endPtDict)
                
                allBound.append(boundDesc)
        
        #Add the frame cavity surface to the BC types to write into the header.
        boundConditions.append(thermDefault.frameCavityBCProperties)
    
    #Check the orientation of the baseplane and specify it either as a sill or jamb.
    CrossSectionType = 'Sill'
    if basePlane.Normal.Z < -0.70710678118 or basePlane.Normal.Z > 0.70710678118: CrossSectionType = 'Jamb'
    
    
    
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
        '<MeshControl MeshLevel="6" ErrorCheckFlag="1" ErrorLimit="10.000000" MaxIterations="5" CMAflag="0" />\n'
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


#If the intital check is good, run the component.
if initCheck and _writeTHMFile:
    initInputs = checkTheInputs()
    if initInputs != -1:
        workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin = initInputs
        result = main(workingDir, xmlFileName, thermPolygons, thermBCs, basePlane, allBoundary, thermFileOrigin)
        if result != -1:
            thermFile, uFactorFile, resultFile = result


