# This is a component for visualizing the desirability of shading over a window by using the energy model results.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This is a component for visualizing the desirability of shade in terms of energy simulation results by using solar vectors, the outdoor temperature, and the simulation hating load, cooling load, and beam gain.
_
Solar vectors for hours when the building is heating contribute positively to shade desirability while solar vectors for hours when the building is cooling contribute negatively.  This conrtibution is weighted by how much the building is cooling or heating in realtion to the solar beam gain through the window in question.
_
The component outputs a colored mesh of the shade illustrating the net effect of shading each mesh face.  A higher saturation of blue indicates that shading the cell is very desirable.  A higher saturation of red indicates that shading the cell is harmful (blocking more winter sun than summer sun). Desaturated cells indicate that shading the cell will have relatively little effect on outdoor comfort or building performance.
_
The units for shade desirability are net kWh saved per unit area of shade if the test cell is blue.  If the test cell is red, the units are net heating kWh harmed per unit area of shade.
_
The method used by this component is based off of the Shaderade method developed by Christoph Reinhart, Jon Sargent, Jeffrey Niemasz.  This component uses Shaderade's method for evaluating shade and window geometry in terms of solar vectors.
_
A special thanks goes to them and their research.  A paper detailing the Shaderade method is available at:
http://web.mit.edu/tito_/www/Publications/BS2011_Shaderade.pdf

-
Provided by Honeybee 0.0.64
    
    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _coolingLoad: The hourly cooling load of the window's corresponding zone (including ladybug header).
        _heatingLoad: The hourly heating load of the window's corresponding zone (including ladybug header).
        _beamGain: The hourly beam gain through the window (including ladybug header).
        ============: ...
        _testShade: A brep or list of breps representing shading to be evaluated in terms of its benefit. Note that, in the case that multiple shading breps are connected, this component does not account for the interaction between the different shading surfaces. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        _testWindow: A brep representing a window for which shading is being considered. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        gridSize_: The length of each of the shade's test cells in model units.  Please note that, as this value gets lower, simulation times will increase exponentially even though this will give a higher resolution of shade benefit.
        context_: If there is static external context that could block sun vectors at certain hours, connect context breps here to account for them in the shade benefit evaluation. 
        ============: ...
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        skyResolution_: An interger equal to 0 or above to set the number of times that the tergenza sky patches are split.  A higher number will ensure a greater accuracy but will take longer.  At a sky resolution of 4, each hour's temperature is essentially matched with an individual sun vector for that hour.  At a resolution of 5, a sun vector is produced for every half-hour, at 6, every quarter hour, and so on. The default is set to 4, which should be high enough of a resolution to produce a meaningful reault in all cases.
        delNonIntersect_: Set to "True" to delete mesh cells with no intersection with sun vectors.  Mesh cells where shading will have little effect because an equal amount of warm and cool temperature vectors will still be left in white.
        legendPar_: Legend parameters that can be used to re-color the shade, change the high and low boundary, or sync multiple evaluated shades with the same colors and legend parameters.
        parallel_: Set to "True" to run the simulation with multiple cores.  This can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.
        _runIt: Set to 'True' to run the simulation.
    Returns:
        readMe!: ...
        ==========: ...
        sunVectors: The sun vectors that were used to evaluate the shade (note that these will increase as the sky desnity increases).
        windowTestPts: Points across the window surface from which sun vectors will be projected
        shadeMesh: A colored mesh of the _testShades showing where shading is helpful (in satuated blue), harmful (in saturated red), or does not make much of a difference (white or desaturated colors).
        legend: Legend showing the numeric values of degree-days that correspond to the colors in the shade mesh.
        ==========: ...
        shadeHelpfulness: The cumulative kWh/m2 of building operational energy helped by shading the given cell.
        shadeHarmfulness: The cumulative kWh/m2 of building operational energy harmed by shading the given cell.  Note that these values are all negative due to the fact that the shade is harmful. 
        shadeNetEffect: The sum of the helpfulness and harmfulness for each cell.  This will be negative if shading the cell has a net harmful effect and positive if the shade has a net helpful effect.  Values are in kWh/m2 of building operational energy helped/harmed by shading the given cell.
"""

ghenv.Component.Name = "Honeybee_Energy Shade Benefit Evaluator"
ghenv.Component.NickName = 'EnergyShadeBenefit'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nDEC_15_2017
#compatibleLBVersion = VER 0.0.59\nNOV_20_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import rhinoscriptsyntax as rs
import Rhino as rc
import collections
import System.Threading.Tasks as tasks
import System
import scriptcontext as sc
import math

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


w = gh.GH_RuntimeMessageLevel.Warning

def checkTheInputs():
    #Create a dictionary of all of the input heatingloads, coolingLoads and beam gains.
    checkData1 = True
    allDataDict = {}
    
    for i in range(_testWindow.BranchCount):
        path = []
        for index in _testWindow.Path(i):
            path.append(index)
        path = str(path)
        
        if not allDataDict.has_key(path):
            allDataDict[path] = {}
        
        if len(_testWindow.Branch(i)) == 1:
            allDataDict[path]["windowSrf"] = _testWindow.Branch(i)[0]
        else:
            checkData1 = False
            warning = "This component can only accept one window brep per branch.  Separate windows into different branches if you have multiple windows."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        allDataDict[path]["shadeSrfs"] = _testShades.Branch(i)
        allDataDict[path]["coolingLoad"] = _coolingLoad.Branch(i)
        allDataDict[path]["heatingLoad"] = _heatingLoad.Branch(i)
        allDataDict[path]["beamGain"] = _beamGain.Branch(i)
    
    
    #Check that both a window brep and test shade brep have only one surface.
    checkData2 = True
    if _testShades.BranchCount != 0 and _testWindow.BranchCount != 0:
        for path in allDataDict:
            if allDataDict[path]["windowSrf"].Faces.Count == 1:
                shadeCheck = True
                for srf in allDataDict[path]["shadeSrfs"]:
                    if srf.Faces.Count == 1: pass
                    else: shadeCheck = False
                if shadeCheck == False:
                    checkData2 = False
                    warning ='The _testShades must each be a brep with a single surface.  Polysurface or volumetric Breps are not supported at this time. Try breaking your Brep up into single surfaces.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                checkData2 = False
                warning ='The _testWindows must each be a brep with a single surface.  Polysurface or volumetric Breps are not supported at this time. Try breaking your Brep up into single surfaces.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        checkData2 = False
        print 'Connect a brep for both the _testWindow and the _testShade.'
    
    
    #Check to see if users have connected a grid size.  If not, assign a grid size based on a bounding box around the test shade.
    checkData3 = True
    if gridSize_:
            if gridSize_ > 0: gridSize = float(gridSize_)
            else:
                warning = 'Values for gridSize_ must be positive.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                gridSize = 0
                checkData3 = False
    else:
        for branch in allDataDict:
            testKey = branch
        boundBox = allDataDict[testKey]["shadeSrfs"][0].GetBoundingBox(False)
        box = rc.Geometry.Box(boundBox)
        if box.X[1] - box.X[0] < box.Y[1] - box.Y[0]:
            gridSize = (box.X[1] - box.X[0])/10
        else:
            gridSize = (box.Y[1] - box.Y[0])/10
        print "A default coarse grid size was chosen for your shades since you did not input a grid size."
    
    
    #Test to be sure that each window has a respective shade, heating load, cooling load, and beam gain. If not, take them out of the dictionary.
    newAllDataDict = {}
    for branch in allDataDict:
        if allDataDict[branch].has_key('windowSrf') and allDataDict[branch].has_key('shadeSrfs') and allDataDict[branch].has_key('coolingLoad') and allDataDict[branch].has_key('heatingLoad') and allDataDict[branch].has_key('beamGain'):
            if not newAllDataDict.has_key(branch):
                newAllDataDict[branch] = {}
                newAllDataDict[branch]["windowSrf"] = allDataDict[branch]["windowSrf"]
                newAllDataDict[branch]["shadeSrfs"] = allDataDict[branch]["shadeSrfs"]
                newAllDataDict[branch]["coolingLoad"] = allDataDict[branch]["coolingLoad"]
                newAllDataDict[branch]["heatingLoad"] = allDataDict[branch]["heatingLoad"]
                newAllDataDict[branch]["beamGain"] = allDataDict[branch]["beamGain"]
        else:
            print "One of the data tree branches of the input data does not have all 5 required inputs of window, shade, cooling load, heating load, and beam gain and has thus been disconted from the shade benefit evaluation."
    
    #Test to be sure that the correct headers are on the heating, cooling and beam gain and that the correct data type is referenced in these headers.  Also check to be sure that the data is hourly.
    checkData4 = True
    analysisPeriods = []
    locations = []
    zones = []
    
    def checkDataHeaders(dataBranch, dataType, dataName, bCount, numKey):
        if str(dataBranch[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
            try:
                analysisStart = dataBranch[5].split(')')[0].split('(')[-1].split(',')
                analysisEnd = dataBranch[6].split(')')[0].split('(')[-1].split(',')
                anaS = []
                anaE = []
                for item in analysisStart:anaS.append(int(item))
                for item in analysisEnd:anaE.append(int(item))
                analysisPeriods.append([tuple(anaS), tuple(anaE)])
            except:
                analysisPeriods.append([dataBranch[5], dataBranch[6]])
            locations.append(dataBranch[1])
            if dataType != "Beam":
                zones[bCount].append(dataBranch[2].split(' for ')[-1])
            if dataType in dataBranch[2] and dataBranch[4] == "Hourly":
                newList = []
                for itemCount, item in enumerate(dataBranch):
                    if itemCount > 6:
                        newList.append(item)
                newAllDataDict[branch][numKey] = newList
            else:
                checkData4 = False
                warning = "Data in the " + dataName + " input is not cooling load data or data is not hourly.  Data must be of the correct type and must be hourly."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        else:
            warning = 'Data in the ' + dataName + ' input does not possess a valid Ladybug header.  Data must have a header to use this component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    for branchCount, branch in enumerate(newAllDataDict):
        zones.append([])
        checkDataHeaders(newAllDataDict[branch]["coolingLoad"], "Cooling", "_coolingLoad", branchCount, "cooling")
        checkDataHeaders(newAllDataDict[branch]["heatingLoad"], "Heating", "_heatingLoad", branchCount, "heating")
        checkDataHeaders(newAllDataDict[branch]["beamGain"], "Beam", "_beamGain", branchCount, "beam")
    
    #Make sure that the analysis periods, zones and locations are all the same.
    checkData5 = True
    checkData6 = True
    checkData7 = True
    analysisPeriod = None
    location = None
    
    if checkData4 == True:
        if len(analysisPeriods) != 0:
            analysisPeriod = analysisPeriods[0]
            for period in analysisPeriods:
                if period  == analysisPeriod: pass
                else: checkData5 = False
        if checkData5 == False:
            warning = 'All of the analysis periods on the connected data are not the same.  Data must all be from the same analysis period.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if len(locations) != 0:
            location = locations[0]
            for loc in locations:
                if loc  == location: pass
                else: checkData6 = False
        if checkData6 == False:
            warning = 'All of the locations on the connected data are not the same.  Data must all be from the same location.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        for zoneList in zones:
            if len(zoneList) != 0:
                theZone = zoneList[0]
                for zone in zoneList:
                    if zone  == theZone: pass
                    else: checkData7 = False
        if checkData7 == False:
            warning = 'The branches of the data trees for _heatingLoad, _coolingLoad and _beamGain are not all for the same zone.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the sky resolution and set a default.
    checkData8 = True
    if skyResolution_ == None:
        skyResolution = 4
        print "Sky resolution has been set to 4 , which should be a high enough resolution to deal with almost all cases.\n You may want to decrease it for a faster simulation or increase it for a smoother gradient."
    else:
        if skyResolution_ >= 0:
            skyResolution = skyResolution_
            print "Sky resolution set to " + str(skyResolution)
        else:
            checkData8 = False
            warning = 'Sky resolution must be greater than 0.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the location, make sure that it matches the location of the inputData, and get the latitude, longitude, and time zone.
    checkData9 = True
    latitude = None
    longitude = None
    timeZone = None
    
    if _location != None:
        try:
            locList = _location.split('\n')
            for line in locList:
                if "Latitude" in line: latitude = float(line.split(',')[0])
                elif "Longitude" in line: longitude = float(line.split(',')[0])
                elif "Time Zone" in line: timeZone = float(line.split(',')[0])
        except:
            checkData9 = False
            warning = 'The connected _location is not a valid location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        checkData9 = False
        print 'Connect a _location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
    
    #Check the north direction and, if none is given, set a default to the Y-Axis.
    if north_ == None: north = 0
    else: north = north_
    
    #Check if all of the above Checks are True
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, gridSize, newAllDataDict, skyResolution, analysisPeriod, location, latitude, longitude, timeZone, north


def meshTheShade(gridSize, testShades):
    #Set the paramters for meshing the shade
    meshPar = rc.Geometry.MeshingParameters.Default
    meshPar.MinimumEdgeLength = gridSize
    meshPar.MaximumEdgeLength = gridSize
    
    #Create the lists of variables to be meshed.
    analysisBreps = []
    analysisAreasList = []
    analysisMeshList = []
    
    for testShade in testShades:
        analysisMesh = rc.Geometry.Mesh.CreateFromBrep(testShade, meshPar)[0]
        
        #Generate breps of the mesh faces so that users can see how the shade will be divided before they run the analysis
        
        for face in analysisMesh.Faces:
            if face.IsQuad:
                analysisBreps.append(rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(analysisMesh.Vertices[face.A]), rc.Geometry.Point3d(analysisMesh.Vertices[face.B]), rc.Geometry.Point3d(analysisMesh.Vertices[face.C]), rc.Geometry.Point3d(analysisMesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance))
            if face.IsTriangle:
                analysisBreps.append(rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(analysisMesh.Vertices[face.A]), rc.Geometry.Point3d(analysisMesh.Vertices[face.B]), rc.Geometry.Point3d(analysisMesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance))
        
        #Calculate the areas of the breps for later use in the normalization of shade benefit values.
        analysisAreas = []
        for brep in analysisBreps:
            area = rc.Geometry.AreaMassProperties.Compute(brep).Area*sc.sticky["honeybee_ConversionFactor"]*sc.sticky["honeybee_ConversionFactor"]
            analysisAreas.append(area)
        
        #Append the lists to the total list.
        analysisAreasList.append(analysisAreas)
        analysisMeshList.append(analysisMesh)
    
    return analysisMeshList, analysisBreps, analysisAreasList


def generateTestPoints(gridSize, testRegion):
    def getPts(gridSiz):
        #Generate a Grid of Points Along the Window
        regionMeshPar = rc.Geometry.MeshingParameters.Default
        regionMeshPar.MinimumEdgeLength = (gridSiz/1.75)
        regionMeshPar.MaximumEdgeLength = (gridSiz/1.75)
        regionMesh = rc.Geometry.Mesh.CreateFromBrep(testRegion, regionMeshPar)[0]
        
        vertices = regionMesh.Vertices
        
        # Convert window Point3f to Point3d
        regionTestPtsInit = []
        for item in vertices:
            regionTestPtsInit.append(rc.Geometry.Point3d(item))
        
        #Get rid of the points that lie along the boundary of the shape.
        regionTestPts = []
        edges = testRegion.DuplicateEdgeCurves()
        boundary = rc.Geometry.Curve.JoinCurves(edges)
        for point in regionTestPtsInit:
            closestPtInit =  rc.Geometry.Curve.ClosestPoint(boundary[0], point)
            closestPt = boundary[0].PointAt(closestPtInit[1])
            if point.DistanceTo(closestPt) < sc.doc.ModelAbsoluteTolerance: pass
            else: regionTestPts.append(point)
        
        #If there is a dense collection of points that are too close to each other, get rid of it.
        regionTestPtsFinal = []
        for pointCount, point in enumerate(regionTestPts):
            pointOK = True
            testPtsWihtout = list(regionTestPts)
            del testPtsWihtout[pointCount]
            for othPt in testPtsWihtout:
                if point.DistanceTo(othPt) < (gridSiz/4):
                    pointOK = False
                else:pass
            if pointOK == True:
                regionTestPtsFinal.append(point)
        return regionTestPtsFinal
    
    regionTestPtsFin = getPts(gridSize)
    
    if len(regionTestPtsFin) < 10:
        bbox = rc.Geometry.Box(testRegion.GetBoundingBox(False))
        bboxDim = [(bbox.X[1] - bbox.X[0]), (bbox.Y[1] - bbox.Y[0]), (bbox.Z[1] - bbox.Z[0])]
        bboxDim.sort()
        if bboxDim[0] < sc.doc.ModelAbsoluteTolerance: smallestDim = bboxDim[1]
        else: smallestDim = bboxDim[0]
        newGridSize = smallestDim/10
        regionTestPtsFin = getPts(newGridSize)
    
    return regionTestPtsFin


def prepareGeometry(gridSize, allDataDict):
    #Things to generate: shadeFaceAreas, allShadeBreps, windowTestPts, shadeMesh, shadeMeshBreps
    #Create the lists that will be filled.
    windowTestPts = []
    shadeMeshBreps = []
    
    for branchCount, branch in enumerate(allDataDict):
        #Mesh the shade.
        shadeMesh, shadeMeshBrepList, shadeMeshAreas = meshTheShade(gridSize, allDataDict[branch]["shadeSrfs"])
        shadeMeshBreps.append(shadeMeshBrepList)
        allDataDict[branch]["shadeMesh"] = shadeMesh
        allDataDict[branch]["shadeMeshAreas"] = shadeMeshAreas
        
        #Generate window test points.
        windowPoints = generateTestPoints(gridSize, allDataDict[branch]["windowSrf"])
        windowTestPts.append(windowPoints)
        allDataDict[branch]["windowPts"] = windowPoints
    
    return windowTestPts, shadeMeshBreps, allDataDict


def checkSkyResolution(skyResolution, allDataDict, analysisPeriod, latitude, longitude, timeZone, north, lb_sunpath, lb_preparation):
    # Make lists for all of the sun up hours of the data dictionary.
    for path in allDataDict:
        allDataDict[path]["coolingSun"] = []
        allDataDict[path]["heatingSun"] = []
        allDataDict[path]["beamSun"] = []
    
    #Get all of the sun vectors for the analysis period.
    sunVectors = []
    lb_sunpath.initTheClass(latitude, north, rc.Geometry.Point3d.Origin, 1, longitude, timeZone)
    
    if analysisPeriod != [(1,1,1), (12,31,24)]:
        HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
    else:
        HOYs = range(8760)
    HOYStart = HOYs[0]
    
    if skyResolution <= 4:
        for hoy in HOYs:
            d, m, h = lb_preparation.hour2Date(hoy, True)
            m += 1
            lb_sunpath.solInitOutput(m, d, h)
            if lb_sunpath.solAlt >= 0:
                sunVec = lb_sunpath.sunReverseVectorCalc()
                sunVectors.append(sunVec)
                for path in allDataDict:
                    allDataDict[path]["coolingSun"].append(allDataDict[path]["cooling"][hoy-HOYStart])
                    allDataDict[path]["heatingSun"].append(allDataDict[path]["heating"][hoy-HOYStart])
                    allDataDict[path]["beamSun"].append(allDataDict[path]["beam"][hoy-HOYStart])
    else:
        newHOYs = []
        hourDivisions = []
        dividend = 1/(math.pow(2, (skyResolution-4)))
        startVal = dividend
        while startVal < 1:
            hourDivisions.append(startVal)
            startVal += dividend
        for hoy in HOYs:
            for division in hourDivisions:
                newHOYs.append(hoy - 1 + division)
            newHOYs.append(hoy)
        for hoy in newHOYs:
            d, m, h = lb_preparation.hour2Date(hoy, True)
            m += 1
            lb_sunpath.solInitOutput(m, d, h)
            
            if lb_sunpath.solAlt >= 0:
                sunVec = lb_sunpath.sunReverseVectorCalc()
                sunVectors.append(sunVec)
                for path in allDataDict:
                    allDataDict[path]["coolingSun"].append(allDataDict[path]["cooling"][int(hoy)])
                    allDataDict[path]["heatingSun"].append(allDataDict[path]["heating"][int(hoy)])
                    allDataDict[path]["beamSun"].append(allDataDict[path]["beam"][int(hoy)])
    
    #Check to see if the user has requested the highest resolution and, if not, consolidate the sun vectors into sky patches.
    finalSunVecs = []
    finalPatchHOYs = []
    for path in allDataDict:
        allDataDict[path]["coolingFinal"] = []
        allDataDict[path]["heatingFinal"] = []
        allDataDict[path]["beamFinal"] = []
    
    if skyResolution < 4:
        newVecs = []
        skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, skyResolution, .5)
        skyPatchMeshes = []
        for patch in skyPatches:
            verts = patch.DuplicateVertices()
            if len(verts) == 4:
                patchBrep = rc.Geometry.Brep.CreateFromCornerPoints(verts[0], verts[1], verts[2], verts[3], sc.doc.ModelAbsoluteTolerance)
            else: patchBrep = patch
            skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patchBrep, rc.Geometry.MeshingParameters.Coarse)[0])
            patchPt = rc.Geometry.AreaMassProperties.Compute(patch).Centroid
            newVec = rc.Geometry.Vector3d(patchPt)
            newVecs.append(newVec)
            finalPatchHOYs.append([])
        
        
        for vecCount, vector in enumerate(sunVectors):
            ray = rc.Geometry.Ray3d(rc.Geometry.Point3d.Origin, vector)
            for patchCount, patch in enumerate(skyPatchMeshes):
                if rc.Geometry.Intersect.Intersection.MeshRay(patch, ray) >= 0:
                    finalPatchHOYs[patchCount].append(vecCount)
        
        vecCount = -1
        for patchCount, hourList in enumerate(finalPatchHOYs):
            if hourList != []:
                vecCount += 1
                finalSunVecs.append(newVecs[patchCount])
                for path in allDataDict:
                    allDataDict[path]["coolingFinal"].append(0)
                    allDataDict[path]["heatingFinal"].append(0)
                    allDataDict[path]["beamFinal"].append(0)
                
                for hour in hourList:
                    for path in allDataDict:
                        allDataDict[path]["coolingFinal"][vecCount] = allDataDict[path]["coolingFinal"][vecCount] + allDataDict[path]["coolingSun"][hour-HOYStart]
                        allDataDict[path]["heatingFinal"][vecCount] = allDataDict[path]["heatingFinal"][vecCount] + allDataDict[path]["heatingSun"][hour-HOYStart]
                        allDataDict[path]["beamFinal"][vecCount] = allDataDict[path]["beamFinal"][vecCount] + allDataDict[path]["beamSun"][hour-HOYStart]
    else:
        finalSunVecs = sunVectors
        for path in allDataDict:
            allDataDict[path]["coolingFinal"] = allDataDict[path]["coolingSun"]
            allDataDict[path]["heatingFinal"] = allDataDict[path]["heatingSun"]
            allDataDict[path]["beamFinal"] = allDataDict[path]["beamSun"]
    
    
    return allDataDict, finalSunVecs


def nonparallel_projection(analysisMesh, sunLines, windowTestPts):
    #Intersect the sun lines with the test mesh
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([])
    
    for ptCount, pt in enumerate(windowTestPts):
        try:
            for hour, sunLine in enumerate(sunLines[ptCount]):
                if sunLine != 0:
                    intPt, i = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                    if len(intPt)!=0: faceInt[i[0]].append(hour)
                else: pass
        except Exception, e:
            print `e`
    
    return faceInt


def parallel_projection(analysisMesh, sunLines, windowTestPts):
    #Intersect the sun lines with the test mesh using parallel processing
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([]) #place holder for result
    
    def intersect(i):
        try:
            for hour, sunLine in enumerate(sunLines[i]):
                if sunLine != 0:
                    intPt, indx = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                    if len(intPt)!=0: faceInt[indx[0]].append(hour)
                else: pass
        except Exception, e:
            print `e`
    
    tasks.Parallel.ForEach(range(len(windowTestPts)), intersect)
    
    return faceInt


def valCalc(percentBlocked, ECool, EBeam, cellArea, extraDivisor):
    #Multiply the Energy by the Percentage Blocked by the Shade
    ECoolPercent = [a*b for a,b in zip(ECool,percentBlocked)]
    EBeamPercent = [a*b for a,b in zip(EBeam,percentBlocked)]
    
    #Calculate the Thermal Effect of the Shade
    NegBeam = []
    for item in EBeamPercent:
        NegBeam.append(item*(-1))
    
    BeamEffectCool = [item1 for item1, item2 in zip(EBeamPercent , ECoolPercent) if item1 < item2]
    DeltaCool1 = sum(BeamEffectCool)
    
    BeamEffectHeat = [item1 for item1, item2 in zip(NegBeam , ECoolPercent) if item1 > item2]
    DeltaHeat1 = sum(BeamEffectHeat)
    
    BeamEffectMid = [item1 for item1, item2, item3 in zip(ECoolPercent , EBeamPercent , NegBeam) if item1 < item2 and item1 > item3]
    DeltaMidCoolList = []
    DeltaMidHeatList = []
    for item in BeamEffectMid:
        if item > 0: DeltaMidCoolList.append(item)
        else: DeltaMidHeatList.append(item)
    
    DeltaMidCool = sum(DeltaMidCoolList)
    DeltaMidHeat = sum(DeltaMidHeatList)
    
    deltaCooling = DeltaCool1 + DeltaMidCool
    deltaHeating = DeltaHeat1 + DeltaMidHeat
    
    netEffecting = deltaCooling + deltaHeating
    
    #Normalize the effects by the area of the cell such that there is a consistent metric between cells of different areas.
    coolEffect = (deltaCooling/cellArea)
    heatEffect = (deltaHeating/cellArea)
    netEffect = (netEffecting/cellArea)
    
    #If the sky resolution is greater than 4, divide the result by the number of additional timesteps that have been added.
    if extraDivisor != 0:
        coolEffect = coolEffect/extraDivisor
        heatEffect = heatEffect/extraDivisor
        netEffect = netEffect/extraDivisor
    
    return coolEffect, heatEffect, netEffect

def evaluateShade(coolingLoad, heatingLoad, beamGain, analysisMesh, analysisAreas, windowMesh, windowTestPts, sunVectors, skyResolution):
    #Determine the length to make the sun lines based on the scale of the bounding box around the input geometry.
    def joinMesh(meshList):
        joinedMesh = rc.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh
    
    joinedMesh = joinMesh([analysisMesh, windowMesh])
    
    boundBox = rc.Geometry.Mesh.GetBoundingBox(joinedMesh, rc.Geometry.Plane.WorldXY)
    
    #Multiply the largest dimension of the bounding box by 2 to ensure that the lines are definitely long enough to intersect the shade.
    lineLength = (max(boundBox.Max - boundBox.Min)) * 2
    
    #Generate the sun lines for intersection and discount the vector if it intersects a context.
    sunLines = []
    if context_:
        contextMeshes = []
        for brep in context_:
            contextMeshes.extend(rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Default))
        contextMesh = joinMesh(contextMeshes)
    else: pass
    
    for pt in windowTestPts: sunLines.append([]) 
    
    for ptCount, pt in enumerate(windowTestPts):
        for vec in sunVectors:
            if context_:
                if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh, rc.Geometry.Ray3d(pt, vec)) < 0:
                    sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
                else: sunLines[ptCount].append(0)
            else:
                sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
            
    
    #If parallel is true, then run the intersection through the parallel function.  If not, run it through the normal function.
    if parallel_ == True:
        faceInt = parallel_projection(analysisMesh, sunLines, windowTestPts)
    else:
        faceInt = nonparallel_projection(analysisMesh, sunLines, windowTestPts)
    
    #Convert the Number Of Intersections for Each Mesh Face into a Percent of Sun Blocked by Each Mesh Face for Each Hour of the Year.
    percentBlocked = []
    for face in range(analysisMesh.Faces.Count):
        percentBlocked.append(len(sunVectors) *[0])
    
    testPtsCount = len(windowTestPts) 
    # for each mesh surface,
    for faceCount, faceData in enumerate(faceInt):
        # check the number of intersections for each hour
        counter= collections.Counter(faceData)
        
        for hour in counter.keys():
             # store the result in the new percentBlocked list
             percentBlocked[faceCount][hour] = counter[hour]/testPtsCount
    
    #Calculate ECool and EBeam, which signify the cooling energy at stake and the solar energy at stake respectively.
    ECool = [a-b for a,b in zip(coolingLoad,heatingLoad)]
    EBeam = beamGain
    
    #Compare the percent blocked for each hour with the temperatre at that hour in relation to the balance point in order to determine the net value of shading.
    if skyResolution > 4: extraDivisor = (math.pow(2, (skyResolution-4)))
    else: extraDivisor = 0
    shadeHelpfulness = []
    shadeHarmfulness = []
    shadeNetEffect = []
    for cellCount, cell in enumerate(percentBlocked):
        shadeHelp, shadeHarm, shadeNet = valCalc(cell, ECool, EBeam, analysisAreas[cellCount], extraDivisor)
        shadeHelpfulness.append(shadeHelp)
        shadeHarmfulness.append(shadeHarm)
        shadeNetEffect.append(shadeNet)
    
    return shadeHelpfulness, shadeHarmfulness, shadeNetEffect



def main(allDataDict, sunVectors, skyResolution, legendPar, lb_preparation, lb_visualization):
    #Create lists to be filled.
    totalNetEffect = []
    totalShadeGeo = []
    shadeHelpfulnessList = []
    shadeHarmfulnessList = []
    shadeNetEffectList = []
    shadeMeshListInit = []
    shadeMeshList = []
    calcSuccess = True
    
    try:
        #Evaluate each shade.
        for windowCount, path in enumerate(allDataDict):
            # let the user cancel the process
            if gh.GH_Document.IsEscapeKeyDown(): assert False
            
            shadeHelpfulnessList.append([])
            shadeHarmfulnessList.append([])
            shadeNetEffectList.append([])
            shadeMeshListInit.append([])
            shadeMeshList.append([])
            
            coolingLoad = allDataDict[path]["coolingFinal"]
            heatingLoad = allDataDict[path]["heatingFinal"]
            beamGain = allDataDict[path]["beamFinal"]
            
            windowMesh = rc.Geometry.Mesh.CreateFromBrep(allDataDict[path]["windowSrf"])[0]
            windowPoints = allDataDict[path]["windowPts"]
            
            for shadeCount, shadeMesh in enumerate(allDataDict[path]["shadeMesh"]):
                totalShadeGeo.append(shadeMesh)
                shadeMeshListInit[windowCount].append(shadeMesh)
                shadeMeshAreas = allDataDict[path]["shadeMeshAreas"][shadeCount]
                shadeHelpfulness, shadeHarmfulness, shadeNetEffect = evaluateShade(coolingLoad, heatingLoad, beamGain, shadeMesh, shadeMeshAreas, windowMesh, windowPoints, sunVectors, skyResolution)
                
                
                for item in shadeNetEffect: totalNetEffect.append(item)
                shadeHelpfulnessList[windowCount].append(shadeHelpfulness)
                shadeHarmfulnessList[windowCount].append(shadeHarmfulness)
                shadeNetEffectList[windowCount].append(shadeNetEffect)
        
        #Sort the net effects to find the highest and lowest values which will be used to generate colors and a legend for the mesh.
        shadeNetSorted = totalNetEffect[:]
        shadeNetSorted.sort()
        mostHelp = shadeNetSorted[-1]
        mostHarm = shadeNetSorted[0]
        if abs(mostHelp) > abs(mostHarm): legendVal = abs(mostHelp)
        else: legendVal = abs(mostHarm)
        
        #Get the colors for the analysis mesh based on the calculated benefit values unless a user has connected specific legendPar.
        legendFont = 'Verdana'
        if legendPar:
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
            if legendPar[3] == []:
                customColors = lb_visualization.gradientLibrary[12]
                customColors.reverse()
        else:
            lowB = -1 * legendVal
            highB = legendVal
            numSeg = 11
            customColors = lb_visualization.gradientLibrary[12]
            customColors.reverse()
            legendBasePoint = None
            legendScale = 1
            legendFontSize = None
            legendBold = False
            decimalPlaces = 2
            removeLessThan = False
        
        #If the user has not input custom boundaries, automatically choose the boundaries for them.
        if lowB == "min": lowB = -1 * legendVal
        if highB == "max": highB = legendVal
        
        #Color each of the meshes with shade benefit.
        for windowCount, shadeMeshGroup in enumerate(shadeMeshListInit):
            for shadeCount, shadeMesh in enumerate(shadeMeshGroup):
                shadeMeshNetEffect = shadeNetEffectList[windowCount][shadeCount]
                colors = lb_visualization.gradientColor(shadeMeshNetEffect, lowB, highB, customColors)
                coloredShadeMesh = lb_visualization.colorMesh(colors, shadeMesh)
                shadeMeshList[windowCount].append(coloredShadeMesh)
        
        # If the user has set "delNonIntersect_" to True, delete those mesh values that do not have any solar intersections.
        if delNonIntersect_ == True:
            for windowCount, shadeMeshGroup in enumerate(shadeMeshList):
                for shadeCount, shadeMesh in enumerate(shadeMeshGroup):
                    deleteFaces = []
                    newShadeHelpfulness = []
                    newShadeHarmfulness = []
                    newShadeNetEffect = []
                    shadeMeshNetEffect = shadeNetEffectList[windowCount][shadeCount]
                    for cellCount, cell in enumerate(shadeMeshNetEffect):
                        if shadeHelpfulnessList[windowCount][shadeCount][cellCount] == 0.0 and shadeHarmfulnessList[windowCount][shadeCount][cellCount] == 0.0:
                            deleteFaces.append(cellCount)
                        else:
                            newShadeHelpfulness.append(shadeHelpfulnessList[windowCount][shadeCount][cellCount])
                            newShadeHarmfulness.append(shadeHarmfulnessList[windowCount][shadeCount][cellCount])
                            newShadeNetEffect.append(cell)
                    shadeMesh.Faces.DeleteFaces(deleteFaces)
                    shadeHelpfulnessList[windowCount][shadeCount] = newShadeHelpfulness
                    shadeHarmfulnessList[windowCount][shadeCount] = newShadeHarmfulness
                    shadeNetEffectList[windowCount][shadeCount] = newShadeNetEffect
    except:
        calcSuccess = False
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
    
    if calcSuccess == True:
        #Generate a legend for all of the meshes.
        lb_visualization.calculateBB(totalShadeGeo, True)
        
        units = sc.doc.ModelUnitSystem
        legendTitle = 'kWh Saved/(' + str(units) + ')2'
        analysisTitle = '\nShade Benefit Analysis'
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(shadeNetEffect, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        
        titlebasePt = lb_visualization.BoundingBoxPar[-2]
        titleTextCurve = lb_visualization.text2srf([analysisTitle], [titlebasePt], legendFont, legendScale * (lb_visualization.BoundingBoxPar[2]/20), legendBold)
        
        #Package the final legend together.
        legend = []
        legend.append(legendSrfs)
        for item in lb_preparation.flattenList(legendTextCrv + titleTextCurve):
            legend.append(item)
        
        #If we have got all of the outputs, let the user know that the calculation has been successful.
        print 'Shade benefit caclculation successful!'
        
        
        return shadeHelpfulnessList, shadeHarmfulnessList, shadeNetEffectList, shadeMeshList, legend, legendBasePoint
    else:
        return -1





#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")

#Check the inputs.
checkData = False
if _coolingLoad.BranchCount > 0 and _heatingLoad.BranchCount > 0 and _beamGain.BranchCount > 0 and _testShades.BranchCount > 0 and _testWindow.BranchCount > 0 and _location != None:
    if _coolingLoad.Branch(0)[0] != None and _heatingLoad.Branch(0)[0] != None and _beamGain.Branch(0)[0] != None and _testShades.Branch(0)[0] != None and _testWindow.Branch(0)[0] != None:
        checkData, gridSize, allDataDict, skyResolution, analysisPeriod, locationData, latitude, longitude, timeZone, north = checkTheInputs()

#If everything passes above, prepare the geometry for analysis.
if checkLB == True and checkData == True:
    windowTestPtsInit, shadeMeshInit, geoAllDataDict = prepareGeometry(gridSize, allDataDict)
    
    #Unpack the data trees of test pts and shade mesh breps so that the user can see them and get a sense of what to expect from the evaluation.
    windowTestPts = DataTree[Object]()
    shadeMesh = DataTree[Object]()
    for brCount, branch in enumerate(windowTestPtsInit):
        for item in branch:
            windowTestPts.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(shadeMeshInit):
        for item in branch:
            shadeMesh.Add(item, GH_Path(brCount))


#If all of the data is good and the user has set "_runIt" to "True", run the shade benefit calculation to generate all results.
if checkLB == True and checkData == True and _runIt == True:
    finalAllDataDict, sunVectors = checkSkyResolution(skyResolution, geoAllDataDict, analysisPeriod, latitude, longitude, timeZone, north, lb_sunpath, lb_preparation)
    result = main(finalAllDataDict, sunVectors, skyResolution, legendPar_, lb_preparation, lb_visualization)
    
    if result != -1:
        shadeHelpfulnessList, shadeHarmfulnessList, shadeNetEffectList, shadeMeshList, legend, legendBasePt = result
        shadeMesh = DataTree[Object]()
        shadeHelpfulness = DataTree[Object]()
        shadeHarmfulness = DataTree[Object]()
        shadeNetEffect = DataTree[Object]()
        
        for windowCount, path in enumerate(finalAllDataDict):
            for shadeCount, shade in enumerate(shadeMeshList[windowCount]):
                newPath = path.split(']')[0].split('[')[-1]
                finalPath = ()
                for item in newPath.split(','):
                    num = int(item)
                    finalPath = finalPath + (num,)
                b = shadeCount
                finalPath = finalPath + (b,)
                
                shadeMesh.Add(shade, GH_Path(finalPath))
                for item in shadeHelpfulnessList[windowCount][shadeCount]: shadeHelpfulness.Add(item, GH_Path(finalPath))
                for item in shadeHarmfulnessList[windowCount][shadeCount]: shadeHarmfulness.Add(item, GH_Path(finalPath))
                for item in shadeNetEffectList[windowCount][shadeCount]: shadeNetEffect.Add(item, GH_Path(finalPath))
        
        ghenv.Component.Params.Output[3].Hidden = True
        ghenv.Component.Params.Output[6].Hidden = True
else:
    ghenv.Component.Params.Output[3].Hidden = False
    ghenv.Component.Params.Output[6].Hidden = False
