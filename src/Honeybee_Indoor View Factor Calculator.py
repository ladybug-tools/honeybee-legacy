# This component generates test points within a zone and calculates view factors of each of these points to the other surfaces of the zone.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generate test points within a zone and calculate the view factor from each of these points to the other zurfaces in a zone as well as the sky.
_
This component is a necessary step before creating an thermal map of an energy model.
-
Provided by Honeybee 0.0.60
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component as surfaces may not align otherwise.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        gridSize_: A number in Rhino model units to make each cell of the view factor mesh.
        distFromFloorOrSrf_: A number in Rhino model units to set the distance of the view factor mesh from the ground.
        additionalShading_: Add in additional shading breps here for geometry that is not a part of the zone but can still block direct sunlight to occupants.  Examples include outdoor context shading and indoor furniture.
        addShdTransmiss_: An optional transmissivity that will be used for all of the objects connected to the additionalShading_ input.  This can also be a list of transmissivities whose length matches the number of breps connected to additionalShading_ input, which will assign a different transmissivity to each object.  Lastly, this input can also accept a data tree with a number of branches equal to the number of objects connected to the additionalShading_ input with a number of values in each branch that march the number of hours in the simulated analysisPeriod (so, for an annual simulation, each branch would have 8760 values).  The default is set to assume that all additionalShading_ objects are completely opaque.  As one adds in transmissivities with this input, the calculation time will increase accordingly.
        ============: ...
        viewResolution_: An interger between 0 and 4 to set the number of times that the tergenza skyview patches are split.  A higher number will ensure a greater accuracy but will take longer.  The default is set to 0 for a quick calculation.
        removeAirWalls_: Set to "True" to remove air walls from the view factor calculation.  The default is set to "True" sinc you usually want to remove air walls from your view factor calculations.
        includeOutdoor_: Set to 'True' to have the final visualization take the parts of the input Srf that are outdoors and color them with temperatures representative of outdoor conditions.  Note that these colors of conditions will only approximate those of the outdoors, showing the assumptions of the Energy model rather than being a perfectly accurate representation of outdoor conditions.  The default is set to 'False' as the inclusion of outdoor conditions can often increase the calculation time.
        ============: ...
        parallel_: Set to "True" to run the calculation with multiple cores and "False" to run it with a single core.  Multiple cores can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.  The default is set to "True."
        _buildMesh: Set boolean to "True" to generate a mesh based on your zones and the input distFromFloorOrSrf_ and gridSize_.  This is a necessary step before calculating view factors from each test point to the surrounding zone surfaces.
        _runIt: Set boolean to "True" to run the component and calculate viewFactors from each test point to surrounding surfaces.
    Returns:
        readMe!: ...
        ==========: ...
        viewFactorMesh: A data tree of meshes to be plugged into the "Annual Comfort Analysis Recipe" component.
        viewFactorInfo: A list of python data that carries essential numerical information for the Comfort Analysis Workflow, including the view factors from each test point to a zone's surfaces, the sky view factors of the test points, and information related to window plaement, used to estimate stratification in the zone.  This should be plugged into a "Comfort Analysis Recipe" component.
        ==========: ...
        testPts: The test points, which lie in the center of the mesh faces at which comfort parameters are being evaluated.
        viewFactorMesh: A data tree of breps representing the split mesh faces of the view factor mesh.
        zoneWireFrame: A list of curves representing the outlines of the zones.  This is particularly helpful if you want to see the outline of the building in relation to the temperature and comfort maps that you might produce off of these results.
        viewVectors: The vectors that were used to caclulate the view factor (note that these will increase as the viewResolution increases).
        shadingContext: A list of meshes representing the opaque surfaces of the zone.  These are what were used to determine the sky view factor and the direct sun falling on occupants.
        closedAirVolumes: The closed Breps representing the zones of continuous air volume (when air walls are excluded).  Zones within the same breps will have the stratification calculation done together.
"""

ghenv.Component.Name = "Honeybee_Indoor View Factor Calculator"
ghenv.Component.NickName = 'IndoorViewFactor'
ghenv.Component.Message = 'VER 0.0.60\nDEC_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nJUN_25_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass


from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import operator
import System.Threading.Tasks as tasks
import time

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance

def copyHBZoneData():
    #Make a check for the zones.
    checkZones = True
    
    #Calls the zones and the libraries from the hive.
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    #Make lists to be filles
    surfaceNames = []
    srfBreps = []
    zoneBreps = []
    zoneCentPts = []
    srfTypes = []
    srfInteriorList = []
    zoneNames = []
    zoneNatVentArea = []
    zoneVolumes = []
    srfAirWallAdjList = []
    windowSrfTransmiss = []
    srfInteriorWindowList = []
    srfIntWindowAdjList = []
    modelHasIntWindows = False
    zoneFloorReflect = []
    zoneRoofReflect = []
    
    for zoneCount, HZone in enumerate(_HBZones):
        #Append lists to be filled.
        surfaceNames.append([])
        srfBreps.append([])
        srfTypes.append([])
        srfInteriorList.append([])
        srfAirWallAdjList.append([])
        srfInteriorWindowList.append([])
        srfIntWindowAdjList.append([])
        windowSrfTransmiss.append([])
        zoneFloorReflect.append([])
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        
        #Copy some of the basic zone properties.
        zone = hb_hive.visualizeFromHoneybeeHive([HZone])[0]
        zoneNames.append(zone.name)
        zoneNatVentArea.append(zone.windowOpeningArea)
        zoneVolumes.append(zone.getZoneVolume())
        
        #Copy surface properties, including the adjacencies.
        for srf in zone.surfaces:
            surfaceNames[zoneCount].append(srf.name)
            srfTypes[zoneCount].append(srf.type)
            if srf.BC.lower() == "surface":
                if srf.type == 4:
                    srfInteriorList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1])
                    srfAirWallAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
                    srfInteriorWindowList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1])
                    srfIntWindowAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
                else:
                    srfInteriorList[zoneCount].append(None)
                    srfAirWallAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
                    srfInteriorWindowList[zoneCount].append(None)
                    srfIntWindowAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
            else:
                srfInteriorList[zoneCount].append(None)
                srfAirWallAdjList[zoneCount].append(None)
                srfInteriorWindowList[zoneCount].append(None)
                srfIntWindowAdjList[zoneCount].append(None)
            if srf.hasChild:
                srfBreps[zoneCount].append(srf.punchedGeometry)
                windowSrfTransmiss[zoneCount].append(0)
                for srfCount, childSrf in enumerate(srf.childSrfs):
                    srfTypes[zoneCount].append(childSrf.type)
                    surfaceNames[zoneCount].append(childSrf.name)
                    srfBreps[zoneCount].append(childSrf.geometry)
                    
                    #Calculate the transmissivity of the window from the construction material properties.
                    windowCnstr = childSrf.EPConstruction
                    if windowCnstr == None:
                        if srf.BC.lower() == "surface": floorCnstr = 'INTERIOR WINDOW'
                        else: floorCnstr = 'EXTERIOR WINDOW'
                    windowLayers = hb_EPMaterialAUX.decomposeEPCnstr(windowCnstr.upper())[0]
                    winTrans = 1
                    for layer in windowLayers:
                        propNumbers = hb_EPMaterialAUX.decomposeMaterial(layer.upper(), ghenv.Component)[0]
                        if 'WindowMaterial:Glazing' in propNumbers[0]:
                            try:
                                winTrans = winTrans*float(propNumbers[4])
                            except:
                                winTrans = 0.4
                        elif 'WindowMaterial:SimpleGlazingSystem' in propNumbers[0]:
                            winTrans = winTrans*float(propNumbers[2])
                    windowSrfTransmiss[zoneCount].append(winTrans)
                    
                    if srf.BC.lower() == "surface":
                        modelHasIntWindows = True
                        srfInteriorList[zoneCount].append(None)
                        srfAirWallAdjList[zoneCount].append(None)
                        srfInteriorWindowList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1])
                        srfIntWindowAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
                    else:
                        srfInteriorList[zoneCount].append(None)
                        srfAirWallAdjList[zoneCount].append(None)
                        srfInteriorWindowList[zoneCount].append(None)
                        srfIntWindowAdjList[zoneCount].append(None)
                    zoneFloorReflect[zoneCount].append(None)
                    zoneRoofReflect.append(None)
            else:
                srfBreps[zoneCount].append(srf.geometry)
                windowSrfTransmiss[zoneCount].append(0)
            
            if srf.type == 2 or srf.type == 2.25 or srf.type == 2.5 or srf.type == 2.75 or srf.type == 1 or srf.type == 1.5:
                floorCnstr = srf.EPConstruction
                if floorCnstr == None:
                    if srf.type == 2 or srf.type == 2.25 or srf.type == 2.5 or srf.type == 2.75: floorCnstr = 'INTERIOR FLOOR'
                    else: floorCnstr = 'EXTERIOR ROOF'
                floorInnerMat = hb_EPMaterialAUX.decomposeEPCnstr(floorCnstr.upper())[0][-1]
                propNumbers = hb_EPMaterialAUX.decomposeMaterial(floorInnerMat.upper(), ghenv.Component)[0]
                if 'Material:NoMass' in propNumbers[0]:
                    solRef = 1 - float(propNumbers[4])
                elif 'Material' in propNumbers[0]:
                    solRef = 1 - float(propNumbers[7])
                if srf.type == 1 or srf.type == 1.5:
                    zoneRoofReflect.append(solRef)
                    zoneFloorReflect[zoneCount].append(None)
                else:
                    zoneFloorReflect[zoneCount].append(solRef)
                    zoneRoofReflect.append(None)
            else:
                zoneFloorReflect[zoneCount].append(None)
                zoneRoofReflect.append(None)
    
    zoneFloorReflect.append(zoneRoofReflect)
    
    #Change the list of adjacent zones to be based on the list item of the zone instead of the name of the zone.
    def changeName2Num(theAdjNameList):
        adjNumList = []
        for srfListCount, zoneSrfList in enumerate(theAdjNameList):
            adjNumList.append([])
            for surface in zoneSrfList:
                foundZone = False
                for zoneCount, zoneName in enumerate(zoneNames):
                    if surface == zoneName:
                        adjNumList[srfListCount].append(zoneCount)
                        foundZone = True
                if foundZone == False:
                    adjNumList[srfListCount].append(None)
        return adjNumList
    
    srfAirWallAdjNumList = changeName2Num(srfAirWallAdjList)
    srfIntWindowAdjNumList = changeName2Num(srfIntWindowAdjList)
    
    sc.sticky["Honeybee_ViewFacotrSrfData"] = [zoneBreps, surfaceNames, srfBreps, zoneCentPts, srfTypes, srfInteriorList, zoneNames, zoneNatVentArea, zoneVolumes, srfAirWallAdjNumList, checkZones, windowSrfTransmiss, modelHasIntWindows, srfInteriorWindowList, srfIntWindowAdjNumList, zoneFloorReflect]


def checkTheInputs():
    #Check to make sure that all connected zones are closed breps.
    checkData4 = True
    if _HBZones != []:
        for closedZone in _HBZones:
            if closedZone.IsSolid: pass
            else: checkData4 = False
    if checkData4 == False:
        warning = "One or more of your connected HBZones is not a closed brep. Zones must be closed in order to run this component correctly."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the grid size and set a default based on the size of each zone if nothing is connected.
    rhinoModelUnits = str(sc.doc.ModelUnitSystem)
    checkData1 = False
    gridSize = None
    if gridSize_ == None:
        if _HBZones != []:
            checkData1 = True
            dimensions = []
            for zone in _HBZones:
                zoneBBox = rc.Geometry.Box(zone.GetBoundingBox(rc.Geometry.Plane.WorldXY))
                dimensions.append(zoneBBox.X[1] - zoneBBox.X[0])
                dimensions.append(zoneBBox.Y[1] - zoneBBox.Y[0])
                dimensions.append(zoneBBox.Z[1] - zoneBBox.Z[0])
            dimensions.sort()
            shortestDim = dimensions[0]
            gridSize = shortestDim/5
            gridSzStatement = "No value connected for gridSize_.  A default gridsize of " + str(gridSize) + " " + rhinoModelUnits + " has been chosen based on the dimensions of your zone geometry."
            print gridSzStatement
    elif gridSize_ > 0:
        checkData1 = True
        gridSize = gridSize_
        gridSzStatement = "Gridsize has been set to " + str(gridSize) + " " + rhinoModelUnits + "."
        print gridSzStatement
    else:
        warning = "gridSize_ must be a value that is creater than 0."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the distFromFloorOrSrf_ and set a default based on the rhino model units if the user has not connected anything.
    sectionBreps = []
    if distFromFloorOrSrf_:
        try:
            floatTest = float(distFromFloorOrSrf_[0])
            sectionMethod = 0
        except:
            sectionMethod = 1
    else: sectionMethod = 0
    
    if sectionMethod == 0:
        if distFromFloorOrSrf_:
            distFromFloor = floatTest
        else:
            if rhinoModelUnits == 'Meters':
                distFromFloor = 0.9
            elif rhinoModelUnits == 'Centimeters':
                distFromFloor = 90
            elif rhinoModelUnits == 'Millimeters':
                distFromFloor = 900
            elif rhinoModelUnits == 'Feet':
                distFromFloor = 3
            elif rhinoModelUnits == 'Inches':
                distFromFloor = 72
            else:
                distFromFloor = 0.1
            print "No value connected for distFromFloorOrSrf_.  The distance from the floor has been set to " + str(distFromFloor) + " " + rhinoModelUnits + "."
    else:
        distFromFloor = None
        sectionMesh, sectionBreps = lb_preparation.cleanAndCoerceList(distFromFloorOrSrf_)
    
    #Check to be sure that none of the zones are having the temperature map generated above them.
    checkData2 = True
    if _HBZones != []:
        if sectionMethod == 0: pass
        else:
            for zone in _HBZones:
                zoneBBox = rc.Geometry.Box(zone.GetBoundingBox(rc.Geometry.Plane.WorldXY))
                zDist = zoneBBox.Z[1] - zoneBBox.Z[0]
                if zDist > distFromFloor: pass
                else: checkData2 = False
            if checkData2 == False:
                warning = "The distFromFloorOrSrf_ is greater than the height of one or more of the zones.  Try decreaseing the value or connecting a custom surface."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    else: checkData2 = False
    
    #Check the viewResolution.
    checkData3 = True
    if viewResolution_ == None:
        viewResolution = 0
        print "View resolution has been set to 0 for a fast calculation."
    else:
        if viewResolution_ <= 4 and viewResolution_ >= 0:
            viewResolution = viewResolution_
            print "Sky resolution set to " + str(viewResolution)
        else:
            checkData3 = False
            warning = 'Sky resolution must be a value between 0 and 4.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the additionalShading_ and addShdTransmiss_.
    checkData5 = True
    addShdTransmiss = []
    constantTransmis = True
    if addShdTransmiss_.BranchCount > 0:
        if addShdTransmiss_.BranchCount == 1:
            addShdTransmissInit = []
            for transmiss in addShdTransmiss_.Branch(0):
                addShdTransmissInit.append(transmiss)
            if len(addShdTransmissInit) == len(additionalShading_):
                allGood = True
                for transVal in addShdTransmissInit:
                    transFloat = transVal
                    if transFloat <= 1.0 and transFloat >= 0.0: addShdTransmiss.append(transFloat)
                    else: allGood = False
                if allGood == False:
                    checkData5 = False
                    warning = 'addShdTransmiss_ must be a value between 0 and 1.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            elif len(addShdTransmissInit) == 1:
                if addShdTransmissInit[0] <= 1.0 and addShdTransmissInit[0] >= 0.0:
                    for count in range(len(additionalShading_)):
                        addShdTransmiss.append(addShdTransmissInit[0])
                else:
                    checkData5 = False
                    warning = 'addShdTransmiss_ must be a value between 0 and 1.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                checkData5 = False
                warning = 'addShdTransmiss_ must be either a list of values that correspond to the number of breps in the additionalShading_ input or a single constant value for all additionalShading_ objects.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        elif addShdTransmiss_.BranchCount > 1:
            if addShdTransmiss_.BranchCount == len(additionalShading_):
                constantTransmis = False
                for i in range(addShdTransmiss_.BranchCount):
                    branchList = addShdTransmiss_.Branch(i)
                    dataVal = []
                    for item in branchList:
                        dataVal.append(item)
                    addShdTransmiss.append(dataVal)
            else:
                    checkData5 = False
                    warning = 'addShdTransmiss_ data trees must have a number of branches that equals the number of objects in additionaShading_.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            print "no value connected for addShdTransmiss_.  All breps connected to additionalShading_ will be assumed to be completely opaque,"
    
    #Check the removeAirWalls_ option.
    if removeAirWalls_ == None: removeInt = True
    else: removeInt = removeAirWalls_
    
    #Check the includeOutdoor_ option.
    if includeOutdoor_ == None: includeOutdoor = False
    else: includeOutdoor = includeOutdoor_
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True:
        checkData = True
    else: checkData = False
    
    return checkData, gridSize, distFromFloor, viewResolution, removeInt, sectionMethod, sectionBreps, includeOutdoor, constantTransmis, addShdTransmiss

def createMesh(brep, gridSize):
    ## mesh breps
    def makeMeshFromSrf(i, inputBrep):
        try:
            mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)[0]
            inputBrep.Dispose()
        except:
            print 'Error in converting Brep to Mesh...'
            pass
    
    # prepare bulk list for each surface
    mesh = [None] * len(brep)
    
    # set-up mesh parameters for each surface based on surface size
    meshParam = rc.Geometry.MeshingParameters.Default
    meshParam.MaximumEdgeLength = gridSize
    meshParam.MinimumEdgeLength = gridSize
    meshParam.GridAspectRatio = 1

    for i in range(len(mesh)): makeMeshFromSrf(i, brep[i])
    
    return mesh

def constructNewMesh(finalFaceBreps):
    finalMesh = rc.Geometry.Mesh()
    for brepCt, brep in enumerate(finalFaceBreps):
        brepVerts = brep.DuplicateVertices()
        if len(brepVerts) == 4:
            facePt1 = rc.Geometry.Point3d(brepVerts[0])
            facePt2 = rc.Geometry.Point3d(brepVerts[1])
            facePt3 = rc.Geometry.Point3d(brepVerts[2])
            facePt4 = rc.Geometry.Point3d(brepVerts[3])
            
            meshFacePts = [facePt1, facePt2, facePt3, facePt4]
            mesh = rc.Geometry.Mesh()
            for point in meshFacePts:
                mesh.Vertices.Add(point)
            
            mesh.Faces.AddFace(0, 1, 2, 3)
            finalMesh.Append(mesh)
        else:
            facePt1 = rc.Geometry.Point3d(brepVerts[0])
            facePt2 = rc.Geometry.Point3d(brepVerts[1])
            facePt3 = rc.Geometry.Point3d(brepVerts[2])
            
            meshFacePts = [facePt1, facePt2, facePt3]
            mesh = rc.Geometry.Mesh()
            for point in meshFacePts:
                mesh.Vertices.Add(point)
            
            mesh.Faces.AddFace(0, 1, 2)
            finalMesh.Append(mesh)
    
    return finalMesh

def prepareGeometry(gridSize, distFromFloor, removeInt, sectionMethod, sectionBreps, includeOutdoor, constantTransmis, addShdTransmiss, hb_zoneData):
    #Separate the HBZoneData.
    zoneBreps = hb_zoneData[0]
    surfaceNames = hb_zoneData[1]
    zoneSrfs = hb_zoneData[2]
    zoneSrfTypes = hb_zoneData[4]
    srfInteriorList = hb_zoneData[5]
    zoneNames = hb_zoneData[6]
    zoneNatVentArea = hb_zoneData[7]
    zoneVolumes = hb_zoneData[8]
    srfAirWallAdjList = hb_zoneData[9]
    windowSrfTransmiss = hb_zoneData[11]
    modelHasIntWindows = hb_zoneData[12]
    srfInteriorWindowList = hb_zoneData[13]
    srfIntWindowAdjNumList = hb_zoneData[14]
    zoneFloorReflect = hb_zoneData[15]
    
    #Make copies of the original zones in the event that some are combined as air walls are removed.
    oldZoneBreps = zoneBreps[:]
    oldZoneSrfs = zoneSrfs[:]
    oldZoneSrfTypes = zoneSrfTypes[:]
    oldSrfInteriorWindowList = srfInteriorWindowList[:]
    
    #Set meshing parameters to be used throughout the function.
    srfMeshPar = rc.Geometry.MeshingParameters.Coarse
    
    #Create the lists that will be filled.
    geoCheck = True
    testPts = []
    MRTMeshBreps = []
    MRTMeshInit = []
    zoneSrfsMesh = []
    zoneWires = []
    zoneOpaqueMesh = []
    zoneWindowMesh = []
    zoneWindowTransmiss = []
    zoneWindowNames = []
    zoneHasWindows = []
    zoneWeights = []
    zoneInletParams = []
    zoneBrepsNonSolid = []
    continuousDaylitVols = []
    outdoorPtHeightWeights = []
    
    #Make lists to keep track of all deleted faces to use if there are some parts of the connected surface that lie completely outside of the zone.
    allDeletedFaces = []
    deletedFaceBreps = []
    deletedTestPts = []
    if sectionMethod != 0 and includeOutdoor == True:
        for sect in sectionBreps:
            allDeletedFaces.append([])
            deletedFaceBreps.append([])
            deletedTestPts.append([])
    
    #If there is additional shading, check to be sure that the number of faces in each brep is 1.
    additionalShading = []
    newAddShdTransmiss = []
    if additionalShading_ != []:
        for shdCount, shdBrep in enumerate(additionalShading_):
            if shdBrep.Faces.Count == 1:
                additionalShading.append(shdBrep)
                if addShdTransmiss != []: newAddShdTransmiss.append(addShdTransmiss[shdCount])
            else:
                for face in shdBrep.Faces:
                    additionalShading.append(rc.Geometry.BrepFace.ToBrep(face))
                    if addShdTransmiss != []: newAddShdTransmiss.append(addShdTransmiss[shdCount])
        addShdTransmiss = newAddShdTransmiss
    
    #Write a function to split breps with the zone and pull out the correctly split surface.
    def splitOffsetFloor(brep, zone):
        splitBrep = rc.Geometry.Brep.Split(brep, zone, tol)
        distToCent = []
        for element in splitBrep:
            distToCent.append(rc.Geometry.Point3d.DistanceTo(rc.Geometry.AreaMassProperties.Compute(element).Centroid, rc.Geometry.AreaMassProperties.Compute(zone).Centroid))
        try:
            distToCent, splitBrep = zip(*sorted(zip(distToCent, splitBrep)))
            finalBrep = splitBrep[0]
        except:
            finalBrep = brep
        
        return finalBrep
    
    #If interior walls have ben removed, see which surfaces are adjacent and re-make the lists fo zones.
    if removeInt == True:
        #Make a function to remove duplicates from a list.
        def removeDup(seq):
            seen = set()
            seen_add = seen.add
            return [ x for x in seq if not (x in seen or seen_add(x))]
        
        #Make a function to tell if all items in a list are the same.
        def allSame(items):
            return all(x == items[0] for x in items)
        
        #Make blank lists that will re-create the original lists.
        newZoneBreps = []
        newSurfaceNames = []
        newZoneSrfs = []
        newZoneSrfTypes = []
        newZoneSolidSrfs = []
        newWindowSrfTransmiss = []
        newSrfIntWindowAdjNumList = []
        newFlrRefList = []
        newZoneFloorReflect = []
        newZoneFloorSrfs = []
        
        #Write a function that solves for the connections in a network of zones (needed to identify air wall and interior window networks).
        def FindAdjNetwork(adjDataTree):
            adjacentList = []
            totalAdjList = []
            
            for zoneCount, srfList in enumerate(zoneSrfs):
                if allSame(adjDataTree[zoneCount]) == False:
                    for srfCount, srf in enumerate(srfList):
                        if adjDataTree[zoneCount][srfCount] != None:
                            if len(adjacentList) == 0:
                                adjacentList.append([zoneCount])
                            else:
                                #Find the adjacent zone.
                                adjSrf = adjDataTree[zoneCount][srfCount]
                                for zoneCount2, srfList in enumerate(surfaceNames):
                                    for srfName in srfList:
                                        if adjSrf == srfName: adjZone = zoneCount2
                                
                                #Have a value to keep track of whether a match has been found for a zone.
                                matchFound = False
                                
                                #Check the current adjacencies list to find out where to place the zone.
                                for zoneAdjListCount, zoneAdjList in enumerate(adjacentList):
                                    #Maybe we already have both of the zones as adjacent.
                                    if zoneCount in zoneAdjList and adjZone in zoneAdjList:
                                        matchFound = True
                                    #If we have the zone but not the adjacent zone, append it to the list.
                                    elif zoneCount in zoneAdjList and adjZone not in zoneAdjList:
                                        adjacentList[zoneAdjListCount].append(adjZone)
                                        matchFound = True
                                    #If we have the adjacent zone but not the zone itself, append it to the list.
                                    elif zoneCount not in zoneAdjList and adjZone in zoneAdjList:
                                        adjacentList[zoneAdjListCount].append(zoneCount)
                                        matchFound = True
                                    else: pass
                                
                                #If no match was found, start a new list.
                                if matchFound == False:
                                    adjacentList.append([zoneCount])
                else:
                    #The zone is not adjacent to any other zones so we will put it in its own list.
                    adjacentList.append([zoneCount])
            
            
            #Remove duplicates found in the process of looking for adjacencies.
            fullAdjacentList = []
            newAjdacenList = []
            for listCount, zoneList in enumerate(adjacentList):
                good2Go = True
                listCheck = []
                notAccountedForCheck = []
                
                #Check if the zones are already accounted for
                for zoneNum in zoneList:
                    if zoneNum in fullAdjacentList: listCheck.append(zoneNum)
                    else: notAccountedForCheck.append(zoneNum)
                
                if len(listCheck) == len(zoneList):
                    #All zones in the list are already accounted for.
                    good2Go = False
                
                if good2Go == True and len(listCheck) == 0:
                    #All of the zones in the list are not yet accounted for.
                    newAjdacenList.append(zoneList)
                    fullAdjacentList.extend(adjacentList[listCount])
                elif good2Go == True:
                    #Find the existing zone list that contains the duplicates and append the non-duplicates to the list.
                    for val in listCheck:
                        for existingListCount, existingList in enumerate(newAjdacenList):
                            if val in existingList: thisIsTheList = existingListCount
                    newAjdacenList[thisIsTheList].extend(notAccountedForCheck)
                    fullAdjacentList.extend(notAccountedForCheck)
            
            return newAjdacenList
        
        
        #Calculate the air wall adjacencies.
        adjacentList = FindAdjNetwork(srfInteriorList)
        
        #If there are interior windows, use the AdjNetwork function to find the continuously daylit spaces.
        finaldaylitAdjList = []
        if modelHasIntWindows ==  True:
            daylitAdjList = FindAdjNetwork(srfInteriorWindowList)
            for airCount, airAdjList in enumerate(adjacentList):
                finaldaylitAdjList.append([])
                for windowList in daylitAdjList:
                    for airCount2, airAdjList2 in enumerate(adjacentList):
                        if airAdjList2[0] in windowList: finaldaylitAdjList[airCount].append(airCount2)
        
        #Create a new "super zone" from the zones that are continuously connected by air walls.
        for listCount, list in enumerate(adjacentList):
            listMarker = len(newSurfaceNames)
            newSurfaceNames.append([])
            newZoneSrfs.append([])
            newZoneSolidSrfs.append([])
            newZoneSrfTypes.append([])
            zoneBrepsNonSolid.append([])
            newWindowSrfTransmiss.append([])
            newSrfIntWindowAdjNumList.append([])
            newFlrRefList.append([])
            newZoneFloorReflect.append([])
            
            for zoneCount in list:
                for srfCount, surface in enumerate(zoneSrfs[zoneCount]):
                    if srfInteriorList[zoneCount][srfCount] == None and srfAirWallAdjList[zoneCount][srfCount] not in list:
                        newZoneSolidSrfs[listMarker].append(surface)
                        newZoneSrfs[listMarker].append(surface)
                        newSurfaceNames[listMarker].append(surfaceNames[zoneCount][srfCount])
                        newZoneSrfTypes[listMarker].append(zoneSrfTypes[zoneCount][srfCount])
                        newWindowSrfTransmiss[listMarker].append(windowSrfTransmiss[zoneCount][srfCount])
                        newSrfIntWindowAdjNumList[listMarker].append(srfIntWindowAdjNumList[zoneCount][srfCount])
                        newZoneFloorReflect[listMarker].append(zoneFloorReflect[zoneCount][srfCount])
                    elif srfInteriorList[zoneCount][srfCount] == None and srfAirWallAdjList[zoneCount][srfCount] in list:
                        newZoneSrfs[listMarker].append(surface)
                        newSurfaceNames[listMarker].append(surfaceNames[zoneCount][srfCount])
                        newZoneSrfTypes[listMarker].append(zoneSrfTypes[zoneCount][srfCount])
                        newWindowSrfTransmiss[listMarker].append(windowSrfTransmiss[zoneCount][srfCount])
                        newSrfIntWindowAdjNumList[listMarker].append(srfIntWindowAdjNumList[zoneCount][srfCount])
                        newZoneFloorReflect[listMarker].append(zoneFloorReflect[zoneCount][srfCount])
            
            joinedBrep = rc.Geometry.Brep.JoinBreps(newZoneSolidSrfs[listMarker], tol)
            
            
            zoneBrepsNonSolid[listCount].extend(joinedBrep)
            newZoneBreps.append(joinedBrep[0])
        
        #Remember to take the roofs and their reflectivity for possible outdoor solar radiation calculations.
        newZoneFloorReflect.append(zoneFloorReflect[-1])
        
        zoneBreps = newZoneBreps
        surfaceNames = newSurfaceNames
        zoneSrfs = newZoneSrfs
        zoneSrfTypes = newZoneSrfTypes
        windowSrfTransmiss = newWindowSrfTransmiss
        srfIntWindowAdjNumList = newSrfIntWindowAdjNumList
        zoneFloorReflect = newZoneFloorReflect
    else:
        for brep in zoneBreps:
            zoneBrepsNonSolid.append([brep])
    
    #Make sure that the zone volumes are closed.
    for brepCount, brep in enumerate(zoneBreps):
        if zoneBrepsNonSolid[brepCount][0].IsSolid: pass
        else:
            edgeCrv = rc.Geometry.Brep.DuplicateEdgeCurves(brep, True)
            buggyEdge = False
            for crv in edgeCrv:
                if crv.SpanCount == 1:
                    buggyEdge = True
            
            if buggyEdge == False:
                geoCheck = False
                warning = "Getting rid of interior walls has caused the connected zone geometry to not be closed.  Make sure that you do not have an airwall bounding the outdoors and, if not, make sure that all zones of your building are connected here."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                geoCheck = False
                warning = "One of your continuous closed air volumes has an overlapping edge that is causing it to not read as a solid. \n Bake the closedAirVolumes output and do a DupBorder command on the polysurface to see the buggy edge. \n Rhino's solid operations are buggy. Hopefully McNeel fix this one soon."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    finalSrfTypes = zoneSrfTypes[:]
    
    if geoCheck == True:
        
        #Check the section method and use this to decide whether to mesh the test surfaces now.
        if sectionMethod != 0:
            allTestPts = []
            allFaceBreps = []
            finalBreps = [sectionBreps]
            for brep in finalBreps:
                finalMesh = createMesh(brep, gridSize)
                
                for meshCount, mesh in enumerate(finalMesh):
                    allTestPts.append([])
                    allFaceBreps.append([])
                    for faceCount, face in enumerate(mesh.Faces):
                        if face.IsQuad:
                            faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), rc.Geometry.Point3d(mesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
                        if face.IsTriangle:
                            faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
                        centPt = rc.Geometry.AreaMassProperties.Compute(faceBrep).Centroid
                        allTestPts[meshCount].append(centPt)
                        allFaceBreps[meshCount].append(faceBrep)
        
        
        for zoneCount, srfList in enumerate(zoneSrfs):
            #Extract the wireframe.
            wireFrame = zoneBreps[zoneCount].DuplicateEdgeCurves()
            for crv in wireFrame:
                zoneWires.append(crv)
            
            #Add lists to the final lists.
            testPts.append([])
            MRTMeshBreps.append([])
            MRTMeshInit.append([])
            zoneSrfsMesh.append([])
            
            if sectionMethod == 0:
                #Select out just the floor geometry.
                floorBreps = []
                for srfCount, srf in enumerate(srfList):
                    zoneSrfsMesh[zoneCount].append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
                    if zoneSrfTypes[zoneCount][srfCount] == 2 or zoneSrfTypes[zoneCount][srfCount] == 2.25 or zoneSrfTypes[zoneCount][srfCount] == 2.5 or zoneSrfTypes[zoneCount][srfCount] == 2.75:
                        floorBreps.append(srf)
                
                #If there are multiple floor breps, join them together.
                dataCheck = True
                if len(floorBreps) > 0: floorBrep = floorBreps
                else:
                    dataCheck = False
                    floorBrep = []
                
                #Move the surface upwards by the offsetDist and keep track of planarity.
                floorBrepsMoved = []
                translation = rc.Geometry.Transform.Translation(0,0,distFromFloor)
                planarList = []
                if len(floorBrep) == 1: isPlanar = True
                else: isPlanar = False
                for brep in floorBrep:
                    for face in brep.Faces:
                        if not face.IsPlanar: isPlanar = False
                    planarList.append(isPlanar)
                    newBrep = brep.Duplicate()
                    newBrep.Transform(translation)
                    floorBrepsMoved.append(newBrep)
                
                finalBreps = []
                for count, brep in enumerate(floorBrepsMoved):
                    #If the surface is planar, intersect the surface with the walls of the zone and rebuild the surface from the curve.
                    if planarList[count] == True:
                        intersectLineList = rc.Geometry.Intersect.Intersection.BrepBrep(brep, zoneBreps[zoneCount], tol)[1]
                        try: intersectLineList = rc.Geometry.Curve.JoinCurves(intersectLineList, tol)
                        except: pass
                        if len(intersectLineList) == 1:
                            if intersectLineList[0].IsClosed:
                                finalBrep = rc.Geometry.Brep.CreatePlanarBreps(intersectLineList[0])
                                finalBreps.append(finalBrep)
                            else:
                                finalBrepInit = splitOffsetFloor(brep, zoneBreps[zoneCount])
                                edges = finalBrepInit.DuplicateEdgeCurves()
                                joinedEdges = rc.Geometry.Curve.JoinCurves(edges, tol)
                                finalBrep = rc.Geometry.Brep.CreatePlanarBreps(joinedEdges[0])
                                finalBreps.append(finalBrep)
                        elif len(intersectLineList) > 0:
                            finalBrepInit = splitOffsetFloor(brep, zoneBreps[zoneCount])
                            edges = finalBrepInit.DuplicateEdgeCurves()
                            joinedEdges = rc.Geometry.Curve.JoinCurves(edges, tol)
                            finalBrep = rc.Geometry.Brep.CreatePlanarBreps(joinedEdges[0])
                            finalBreps.append(finalBrep)
                        else:
                            #The intersection failed.  Just take the floors as they are.
                            finalBreps.append([brep])
                    else:
                        #If the surface is curved or has multiple elements, try to trim it with the closed zone brep.
                        try:
                            finalBrep = splitOffsetFloor(brep, zoneBreps[zoneCount])
                            finalBreps.append([finalBrep])
                        except:
                            finalBreps.append([brep])
            else:
                for srfCount, srf in enumerate(srfList):
                    zoneSrfsMesh[zoneCount].append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
            
            #Generate the meshes and test points of the final surface.
            if sectionMethod == 0:
                for brep in finalBreps:
                    finalMesh = createMesh(brep, gridSize)
                    
                    for meshCount, mesh in enumerate(finalMesh):
                        finalTestPts = []
                        finalFaceBreps = []
                        deleteIndices = []
                        deleteTestPts = []
                        deleteFaceBreps = []
                        for faceCount, face in enumerate(mesh.Faces):
                            if face.IsQuad:
                                faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), rc.Geometry.Point3d(mesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
                            if face.IsTriangle:
                                faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
                            centPt = rc.Geometry.AreaMassProperties.Compute(faceBrep).Centroid
                            #Do a final check to be sure that the test point does not lie outside the zone and, if so, delete the mesh face, and don't append the point.
                            if zoneBreps[zoneCount].IsPointInside(centPt, tol, False) == False:
                                deleteIndices.append(faceCount)
                                deleteFaceBreps.append(faceBrep)
                                deleteTestPts.append(centPt)
                            else:
                                finalFaceBreps.append(faceBrep)
                                finalTestPts.append(centPt)
                        
                        #Construct a new mesh from the breps that are inside each zone.
                        finalMesh = constructNewMesh(finalFaceBreps)
                        
                        if len(finalTestPts) > 0:
                            if len(MRTMeshInit[zoneCount]) > 0: MRTMeshInit[zoneCount][0].Append(finalMesh)
                            else: MRTMeshInit[zoneCount].append(finalMesh)
                            
                            MRTMeshBreps[zoneCount].extend(finalFaceBreps)
                            testPts[zoneCount].extend(finalTestPts)
            else:
                for meshCount, allPtList in enumerate(allTestPts):
                    finalTestPts = []
                    finalFaceBreps = []
                    deleteIndices = []
                    deleteTestPts = []
                    deleteFaceBreps = []
                    
                    for ptCount, meshPoint in enumerate(allPtList):
                        #Do a final check to be sure that the test point does not lie outside the zone and, if so, delete the mesh face, and don't append the point.
                        if zoneBreps[zoneCount].IsPointInside(meshPoint, tol, False) == False:
                            deleteIndices.append(ptCount)
                            deleteFaceBreps.append(allFaceBreps[meshCount][ptCount])
                            deleteTestPts.append(meshPoint)
                        else:
                            finalFaceBreps.append(allFaceBreps[meshCount][ptCount])
                            finalTestPts.append(meshPoint)
                    
                    #Append the deleted faces to the list.
                    if includeOutdoor == True:
                        allDeletedFaces[meshCount].append(deleteIndices)
                        deletedFaceBreps[meshCount].append(deleteFaceBreps)
                        deletedTestPts[meshCount].append(deleteTestPts)
                    
                    #Construct a new mesh from the breps that are inside each zone.
                    finalMesh = constructNewMesh(finalFaceBreps)
                    
                    if len(finalTestPts) > 0:
                        MRTMeshInit[zoneCount].append(finalMesh)
                        
                        MRTMeshBreps[zoneCount].extend(finalFaceBreps)
                        testPts[zoneCount].extend(finalTestPts)
        
        #If the user has selected to use the results for an outdoor calculation, pull out those parts of the mesh related to the outdoors using the deletedIndices list.
        if sectionMethod != 0 and includeOutdoor == True:
            outdoorTestPts = []
            outdoorFaceBreps = []
            
            for testSrfCount, testSrf in enumerate(allDeletedFaces):
                baseDelIndices = testSrf[0]
                totalTests = len(testSrf)
                indexCount = []
                
                for indCt, index in enumerate(baseDelIndices):
                    indexCount.append([])
                    for othDelIndices in testSrf:
                        if index in othDelIndices: indexCount[indCt].append(1)
                    
                    if sum(indexCount[indCt]) == totalTests:
                        
                        outdoorTestPts.append(deletedTestPts[testSrfCount][0][indCt])
                        outdoorFaceBreps.append(deletedFaceBreps[testSrfCount][0][indCt])
            
            #Construct a new mesh from the breps that are inside each zone.
            outdoorMesh = constructNewMesh(outdoorFaceBreps)
            
            #Append outdoor meshes to the complete list.
            if len(outdoorTestPts) > 0:
                MRTMeshInit.append([outdoorMesh])
                
                MRTMeshBreps.append(outdoorFaceBreps)
                testPts.append(outdoorTestPts)
            else:
                includeOutdoor = False
            
            
            #Make a list of all surfaces for the viewFactor calculation of the outdoor mesh.
            zoneSrfsMeshOutdoor = []
            surfaceNamesOutdoor = []
            surfaceTypesOutdoor = []
            zoneOpaqueMeshOutdoor = []
            zoneTranspMeshOutdoor = []
            zoneTranspMeshTransmiss = []
            zoneTranspMeshSrfName = []
            for zoneSrfListCount, zoneSrfList in enumerate(zoneSrfs):
                for srfName in surfaceNames[zoneSrfListCount]:
                    surfaceNamesOutdoor.append(srfName)
                for srfType in finalSrfTypes[zoneSrfListCount]:
                    surfaceTypesOutdoor.append(srfType)
                for srfCount, srf in enumerate(zoneSrfList):
                    srfMesh = rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0]
                    zoneSrfsMeshOutdoor.append(srfMesh)
                    if finalSrfTypes[zoneSrfListCount][srfCount] != 5:
                        zoneOpaqueMeshOutdoor.append(srfMesh)
                    else:
                        zoneTranspMeshOutdoor.append(srfMesh)
                        zoneTranspMeshTransmiss.append(windowSrfTransmiss[zoneSrfListCount][srfCount])
                        zoneTranspMeshSrfName.append(surfaceNames[zoneSrfListCount][srfCount])
            
            zoneSrfsMesh.append(zoneSrfsMeshOutdoor)
            surfaceNames.append(surfaceNamesOutdoor)
            finalSrfTypes.append(surfaceTypesOutdoor)
        
        
        #Make a list for the weighting of each zone value for the air temperature calculation.
        zoneWeights = []
        heightWeights = []
        for falseZoneCount, falseZone in enumerate(testPts):
            if sectionMethod != 0 and includeOutdoor == True:
                if falseZoneCount != len(testPts)-1:
                    zoneWeights.append([])
                    heightWeights.append([])
                    for point in falseZone:
                        zoneWeights[falseZoneCount].append([])
            else:
                zoneWeights.append([])
                heightWeights.append([])
                for point in falseZone:
                    zoneWeights[falseZoneCount].append([])
        
        if removeInt == True:
            #Get the centroids of each zone, which will represent the air node of the zone.
            zoneCentroids = []
            for oirignalZone in oldZoneBreps:
                centPt = rc.Geometry.VolumeMassProperties.Compute(oirignalZone).Centroid
                zoneCentroids.append(centPt)
            
            #For each of the test points, weight them based on the zone they belong to.
            for falseZoneCount, falseZone in enumerate(testPts):
                if sectionMethod != 0 and includeOutdoor == True:
                    if falseZoneCount != len(testPts)-1:
                        for pointCount, point in enumerate(falseZone):
                            initPointWeights = []
                            for orignalZoneCount, oirignalZoneCent in enumerate(zoneCentroids):
                                if orignalZoneCount in adjacentList[falseZoneCount]:
                                    ptDistance = rc.Geometry.Point3d.DistanceTo(point, oirignalZoneCent)
                                    ptWeight = 1/(ptDistance*ptDistance)
                                    initPointWeights.append(ptWeight)
                                else:
                                    initPointWeights.append(0)
                            for weight in initPointWeights:
                                zoneWeights[falseZoneCount][pointCount].append(weight/sum(initPointWeights))
                else:
                    for pointCount, point in enumerate(falseZone):
                        initPointWeights = []
                        for orignalZoneCount, oirignalZoneCent in enumerate(zoneCentroids):
                            if orignalZoneCount in adjacentList[falseZoneCount]:
                                ptDistance = rc.Geometry.Point3d.DistanceTo(point, oirignalZoneCent)
                                ptWeight = 1/(ptDistance*ptDistance)
                                initPointWeights.append(ptWeight)
                            else:
                                initPointWeights.append(0)
                        for weight in initPointWeights:
                            zoneWeights[falseZoneCount][pointCount].append(weight/sum(initPointWeights))
        else:
            #For each of the test points, give them a weight totalling to 1 based on which zone they belong to.
            for falseZoneCount, falseZone in enumerate(testPts):
                if sectionMethod != 0 and includeOutdoor == True:
                    if falseZoneCount != len(testPts)-1:
                        for pointCount, point in enumerate(falseZone):
                            for orignalZoneCount, oirignalZone in enumerate(oldZoneBreps):
                                if oirignalZone.IsPointInside(point, tol, False) == True: zoneWeights[falseZoneCount][pointCount].append(1)
                                else: zoneWeights[falseZoneCount][pointCount].append(0)
                else:
                    for pointCount, point in enumerate(falseZone):
                        for orignalZoneCount, oirignalZone in enumerate(oldZoneBreps):
                            if oirignalZone.IsPointInside(point, tol, False) == True: zoneWeights[falseZoneCount][pointCount].append(1)
                            else: zoneWeights[falseZoneCount][pointCount].append(0)
        
        #Calculate height weights for each of the points.
        for falseZoneCount, falseZone in enumerate(testPts):
            if sectionMethod != 0 and includeOutdoor == True:
                if falseZoneCount != len(testPts)-1:
                    zoneBB = rc.Geometry.Brep.GetBoundingBox(zoneBreps[falseZoneCount], rc.Geometry.Plane.WorldXY)
                    max = zoneBB.Max.Z
                    min = zoneBB.Min.Z
                    difference = max-min
                    for pointCount, point in enumerate(falseZone):
                        heightWeight = (point.Z-min)/difference
                        heightWeights[falseZoneCount].append(heightWeight)
            else:
                zoneBB = rc.Geometry.Brep.GetBoundingBox(zoneBreps[falseZoneCount], rc.Geometry.Plane.WorldXY)
                max = zoneBB.Max.Z
                min = zoneBB.Min.Z
                difference = max-min
                for pointCount, point in enumerate(falseZone):
                    heightWeight = (point.Z-min)/difference
                    heightWeights[falseZoneCount].append(heightWeight)
        
        
        #Calculate the heights of the original zones and the average heights of the windows (to be used in the stratification calculation).
        for orignalZoneCount, oirignalZone in enumerate(oldZoneBreps):
            zoneInletParams.append([])
            
            #Calculate the total height of the zone.
            zoneBB = rc.Geometry.Brep.GetBoundingBox(oirignalZone, rc.Geometry.Plane.WorldXY)
            zoneInletParams[orignalZoneCount].append(zoneBB.Min.Z)
            zoneInletParams[orignalZoneCount].append(zoneBB.Max.Z)
            
            #Calculate the heights from the floor to the window mid-plane (do this only for the windows along the walls and for exterior windows).
            zoneGlzMesh = rc.Geometry.Mesh()
            glzTracker = 0
            for srfCt, srf in enumerate(oldZoneSrfs[orignalZoneCount]):
                if oldZoneSrfTypes[orignalZoneCount][srfCt] == 5 and oldZoneSrfTypes[orignalZoneCount][srfCt-1] == 0 and oldSrfInteriorWindowList[orignalZoneCount][srfCt] == None:
                    zoneGlzMesh.Append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
                    glzTracker += 1
            if glzTracker != 0:
                glzBB = rc.Geometry.Brep.GetBoundingBox(zoneGlzMesh, rc.Geometry.Plane.WorldXY)
                glzMinHeight = glzBB.Min.Z
                glzCentPt = rc.Geometry.AreaMassProperties.Compute(zoneGlzMesh).Centroid
                glzMidHeight = glzCentPt.Z
                zoneInletParams[orignalZoneCount].append((glzMidHeight + glzMinHeight)/2) #Take the average height of the lower half of the glazing.
            else: zoneInletParams[orignalZoneCount].append(None)
            
            #Get the volume of each zone.
            zoneInletParams[orignalZoneCount].append(zoneVolumes[orignalZoneCount])
            
            #Get the area of operable glazing.
            opGlzArea = 0
            for val in zoneNatVentArea[orignalZoneCount]:
                if val != None: opGlzArea += float(val)
            zoneInletParams[orignalZoneCount].append(opGlzArea)
        
        
        # Pull out the geometry that can block sun vectors for the solar adjusted MRT calculation.
        for zCount, zoneSrfTList in enumerate(zoneSrfTypes):
            zoneOpaqueMesh.append([])
            zoneWindowMesh.append([])
            zoneWindowTransmiss.append([])
            zoneWindowNames.append([])
            
            #First add in any additional shading to the list.
            hasWindows = 0
            if additionalShading != [] and addShdTransmiss == []:
                for item in additionalShading:
                    opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(item, rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneOpaqueMesh[zCount].append(opaqueMesh)
            elif additionalShading != []:
                hasWindows = 1
                for itemCount, item in enumerate(additionalShading):
                    transpMesh = rc.Geometry.Mesh.CreateFromBrep(item, rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneWindowMesh[zCount].append(transpMesh)
                    zoneWindowTransmiss[zCount].append(addShdTransmiss[itemCount])
                    zoneWindowNames[zCount].append('AddShd' + str(itemCount))
            
            #Now, pull out all of the zones opaque and transparent geometry.
            for sCount, srfT in enumerate(zoneSrfTList):
                if srfT != 5:
                    opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[zCount][sCount], rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneOpaqueMesh[zCount].append(opaqueMesh)
                else:
                    hasWindows = 1
                    windowMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[zCount][sCount], rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneWindowMesh[zCount].append(windowMesh)
                    zoneWindowTransmiss[zCount].append(windowSrfTransmiss[zCount][sCount])
                    zoneWindowNames[zCount].append(surfaceNames[zCount][sCount])
            zoneHasWindows.append(hasWindows)
            
            #If there are interior windows, be sure to add the geometry of the other contiuously lit zones to the opaque and window geometry lists.
            if modelHasIntWindows ==  True:
                for contLightCount, contLightZone in enumerate(finaldaylitAdjList[zCount]):
                    intWindowCentroids = []
                    if contLightZone != zCount:
                        for sCount2, srfT2 in enumerate(zoneSrfTypes[contLightZone]):
                            if srfT2 != 5:
                                opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[contLightZone][sCount2], rc.Geometry.MeshingParameters.Coarse)[0]
                                zoneOpaqueMesh[zCount].append(opaqueMesh)
                            elif srfIntWindowAdjNumList[contLightZone][sCount2] != None:
                                #Check to see if the interior window is already in the list before deciding whether to add it.
                                alreadyThere = False
                                srfCentroid = rc.Geometry.AreaMassProperties.Compute(zoneSrfs[contLightZone][sCount2]).Centroid
                                for centroid in intWindowCentroids:
                                    if centroid.X < srfCentroid.X+tol and centroid.X > srfCentroid.X-tol and centroid.Y < srfCentroid.Y+tol and centroid.Y > srfCentroid.Y-tol and centroid.Z < srfCentroid.Z+tol and centroid.Z > srfCentroid.Z-tol: pass
                                    else:
                                        windowMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[contLightZone][sCount2], rc.Geometry.MeshingParameters.Coarse)[0]
                                        zoneWindowMesh[zCount].append(windowMesh)
                                        zoneWindowTransmiss[zCount].append(windowSrfTransmiss[contLightZone][sCount2])
                                        intWindowCentroids.append(srfCentroid)
                                        zoneWindowNames[zCount].append(surfaceNames[contLightZone][sCount2])
                            else:
                                windowMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[contLightZone][sCount2], rc.Geometry.MeshingParameters.Coarse)[0]
                                zoneWindowMesh[zCount].append(windowMesh)
                                zoneWindowTransmiss[zCount].append(windowSrfTransmiss[contLightZone][sCount2])
                                intWindowCentroids.append(rc.Geometry.AreaMassProperties.Compute(zoneSrfs[contLightZone][sCount2]).Centroid)
                                zoneWindowNames[zCount].append(surfaceNames[contLightZone][sCount2])
                    else:
                        for sCount2, srfT2 in enumerate(zoneSrfTypes[contLightZone]):
                            if srfT2 == 5 and srfIntWindowAdjNumList[contLightZone][sCount2] != None: intWindowCentroids.append(rc.Geometry.AreaMassProperties.Compute(zoneSrfs[contLightZone][sCount2]).Centroid)
        
        #If there are outdoor points included in the calculation, add them to the zoneOpaqueMesh.
        if sectionMethod != 0 and includeOutdoor == True:
            outdoorHasWindows = 2
            if additionalShading != [] and addShdTransmiss == []:
                for item in additionalShading:
                    opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(item, rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneOpaqueMeshOutdoor.append(opaqueMesh)
            elif additionalShading != []:
                outdoorHasWindows = 1
                for itemCount, item in enumerate(additionalShading):
                    transpMesh = rc.Geometry.Mesh.CreateFromBrep(item, rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneTranspMeshOutdoor.append(transpMesh)
                    if constantTransmis == True: zoneTranspMeshTransmiss.append(addShdTransmiss[itemCount])
                    else: zoneTranspMeshTransmiss.append(1)
                    zoneTranspMeshSrfName.append('AddShd' + str(itemCount))
            
            zoneOpaqueMesh.append(zoneOpaqueMeshOutdoor)
            zoneHasWindows.append(outdoorHasWindows)
            zoneWindowMesh.append(zoneTranspMeshOutdoor)
            zoneWindowTransmiss.append(zoneTranspMeshTransmiss)
            zoneWindowNames.append(zoneTranspMeshSrfName)
            
            #Get the absolute heights of the outdoor points in order to factor them in correctly in the wind speed calculation.
            for point in testPts[-1]:
                if point.Z >= 0: outdoorPtHeightWeights.append(point.Z)
                else: outdoorPtHeightWeights.append(0)
        
        #Add the additional shading to the wireframe.
        if additionalShading != []:
            for item in additionalShading:
                wireFrame = item.DuplicateEdgeCurves()
                for crv in wireFrame:
                    zoneWires.append(crv)
        
        return geoCheck, testPts, MRTMeshBreps, MRTMeshInit, zoneWires, zoneSrfsMesh, surfaceNames, zoneOpaqueMesh, zoneNames, zoneWeights, heightWeights, zoneInletParams, zoneHasWindows, zoneBrepsNonSolid, includeOutdoor, zoneWindowMesh, zoneWindowTransmiss, outdoorPtHeightWeights, zoneWindowNames, zoneFloorReflect, finalSrfTypes, addShdTransmiss
    else:
        return geoCheck, testPts, MRTMeshBreps, MRTMeshInit, zoneWires, zoneSrfsMesh, surfaceNames, zoneOpaqueMesh, zoneNames, zoneWeights, [], zoneInletParams, zoneHasWindows, zoneBrepsNonSolid, includeOutdoor, zoneWindowMesh, zoneWindowTransmiss, outdoorPtHeightWeights, zoneWindowNames, zoneFloorReflect, zoneSrfTypes, addShdTransmiss

def checkViewResolution(viewResolution, lb_preparation):
    newVecs = []
    skyViewVecs = []
    skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, viewResolution, 1)
    for patch in skyPatches:
        patchPt = rc.Geometry.AreaMassProperties.Compute(patch).Centroid
        Vec = rc.Geometry.Vector3d(patchPt.X, patchPt.Y, patchPt.Z)
        revVec = rc.Geometry.Vector3d(-patchPt.X, -patchPt.Y, -patchPt.Z)
        skyViewVecs.append(Vec)
        newVecs.append(Vec)
        newVecs.append(revVec)
    
    return newVecs, skyViewVecs

def allSame(items):
    return all(x == items[0] for x in items)

def parallel_projection(zoneSrfsMesh, viewVectors, pointList):
    #Placeholder for the outcome of the parallel projection.
    pointIntList = []
    for point in pointList: pointIntList.append([])
    
    #Keep track of the divisor.
    divisor = len(viewVectors)
    
    def intersect(i):
        point = pointList[i]
        #Create the rays to be projected from each point.
        pointRays = []
        for vec in viewVectors: pointRays.append(rc.Geometry.Ray3d(point, vec))
        
        #Create a list that will hold the intersection hits of each surface
        srfHits = []
        for srf in zoneSrfsMesh: srfHits.append([])
        
        #Perform the intersection of the rays with the mesh.
        pointIntersectList = []
        for rayCount, ray in enumerate(pointRays):
            pointIntersectList.append([])
            for srf in zoneSrfsMesh:
                intersect = rc.Geometry.Intersect.Intersection.MeshRay(srf, ray)
                if intersect == -1: intersect = "N"
                pointIntersectList[rayCount].append(intersect)
        
        #Find the intersection that was the closest for each ray.
        for list in pointIntersectList:
            if allSame(list) == False:
                minIndex, minValue = min(enumerate(list), key=operator.itemgetter(1))
                srfHits[minIndex].append(1)
        
        #Sum up the lists and divide by the total rays to get the view factor.
        for hitList in srfHits:
            pointIntList[i].append(sum(hitList)/divisor)
    
    tasks.Parallel.ForEach(range(len(pointList)), intersect)
    
    return pointIntList


def parallel_skyProjection(zoneOpaqueMesh, skyViewVecs, pointList, zoneWindowMesh, zoneWindowTransmiss, zoneHasWindows, zoneWindowNames):
    #Placeholder for the outcome of the parallel projection.
    pointIntList = []
    skyBlockedList = []
    skyBlockWindowNameCount = []
    for num in range(len(pointList)):
        pointIntList.append(0.0)
        skyBlockedList.append([])
        skyBlockWindowNameCount.append([])
    
    #Keep track of the divisor.
    divisor = len(skyViewVecs)
    
    def intersect(i):
        point = pointList[i]
        #Create the rays to be projected from each point.
        pointRays = []
        for vec in skyViewVecs: pointRays.append(rc.Geometry.Ray3d(point, vec))
        
        #Perform the intersection of the rays with the opaque mesh.
        pointIntersectList = []
        for rayCount, ray in enumerate(pointRays):
            pointIntersectList.append([])
            for srf in zoneOpaqueMesh:
                intersect = rc.Geometry.Intersect.Intersection.MeshRay(srf, ray)
                if intersect == -1: pass
                else: pointIntersectList[rayCount].append(1)
        
        #See if the ray passed all of the context meshes.
        finalIntersectList = []
        for ray in pointRays:
            finalIntersectList.append([])
        for listCt, rayList in enumerate(pointIntersectList):
            for intersect in rayList:
                finalIntersectList[listCt].append(intersect)
        
        finalViewCount = []
        finalWindowNameCount = []
        for rayListCount, rayList in enumerate(finalIntersectList):
            if sum(rayList) == 0:
                if zoneHasWindows == 2:
                    finalViewCount.append(1)
                    finalWindowNameCount.append(0)
                else:
                    transmiss = 1
                    winNameList = []
                    for winCount, winMesh in enumerate(zoneWindowMesh):
                        intersect = rc.Geometry.Intersect.Intersection.MeshRay(winMesh, pointRays[rayListCount])
                        if intersect == -1: pass
                        else:
                            transmiss = transmiss * zoneWindowTransmiss[winCount]
                            winNameList.append(zoneWindowNames[winCount].upper())
                    finalViewCount.append(transmiss)
                    finalWindowNameCount.append(winNameList)
            else:
                finalViewCount.append(0)
                finalWindowNameCount.append(0)
        
        #Sum up the lists and divide by the total rays to get the view factor.
        skyBlockedList[i] = finalViewCount
        skyBlockWindowNameCount[i] = finalWindowNameCount
        pointIntList[i] = sum(finalViewCount)/divisor
    
    tasks.Parallel.ForEach(range(len(pointList)), intersect)
    
    return pointIntList, skyBlockedList, skyBlockWindowNameCount

def checkOutdoorViewFac(outdoorTestPtViewFactor, testPtSkyView):
    outdoorNonSrfViewFac = []
    for ptCount, viewFac in enumerate(outdoorTestPtViewFactor):
        outdoorNonSrfViewFac.append(1-sum(viewFac)-(testPtSkyView[ptCount]/2))
    return outdoorNonSrfViewFac


def skyViewCalc(testPts, zoneOpaqueMesh, skyViewVecs, zoneHasWindows, zoneWindowMesh, zoneWindowTransmiss, zoneWindowNames):
    testPtSkyView = []
    testPtSkyBlockedList = []
    testPtBlockName = []
    
    for zoneCount, pointList in enumerate(testPts):
        if zoneHasWindows[zoneCount] > 0:
            if parallel_ == True or parallel_ == None:
                skyViewFactors, skyBlockedList, finalWindowNameCount = parallel_skyProjection(zoneOpaqueMesh[zoneCount], skyViewVecs, testPts[zoneCount], zoneWindowMesh[zoneCount], zoneWindowTransmiss[zoneCount], zoneHasWindows[zoneCount], zoneWindowNames[zoneCount])
                testPtSkyView.append(skyViewFactors)
                testPtSkyBlockedList.append(skyBlockedList)
                testPtBlockName.append(finalWindowNameCount)
            else:
                testPtSkyView.append([])
                testPtSkyBlockedList.append([])
                testPtBlockName.append([])
                for pointCount, point in enumerate(pointList):
                    #Make the list that will eventually hold the view factors of each surface.
                    divisor = len(skyViewVecs)
                    
                    #Create the rays to be projected from each point.
                    pointRays = []
                    for vec in skyViewVecs: pointRays.append(rc.Geometry.Ray3d(point, vec))
                    
                    #Perform the intersection of the rays with the opaque mesh.
                    pointIntersectList = []
                    for rayCount, ray in enumerate(pointRays):
                        pointIntersectList.append([])
                        for srf in zoneOpaqueMesh[zoneCount]:
                            intersect = rc.Geometry.Intersect.Intersection.MeshRay(srf, ray)
                            if intersect == -1: pointIntersectList[rayCount].append(0)
                            else: pointIntersectList[rayCount].append(1)
                    
                    #See if the ray passed all of the context meshes.
                    finalIntersectList = []
                    for ray in pointRays:
                        finalIntersectList.append([])
                    for listCt, rayList in enumerate(pointIntersectList):
                        for intersect in rayList:
                            finalIntersectList[listCt].append(intersect)
                    
                    finalViewCount = []
                    finalWindowNameCount = []
                    for rayListCount, rayList in enumerate(finalIntersectList):
                        if sum(rayList) == 0:
                            if zoneHasWindows[zoneCount] == 2:
                                finalViewCount.append(1) #This is the code to indicate that the point is outside and there is no need to calculate a window transmissivity.
                                finalWindowNameCount.append(0)
                            else:
                                #The ray is not blocked but it is hitting a window and so we need to factor in the window transmissivity.
                                transmiss = 1
                                winNameList = []
                                for winCount, winMesh in enumerate(zoneWindowMesh[zoneCount]):
                                    intersect = rc.Geometry.Intersect.Intersection.MeshRay(winMesh, pointRays[rayListCount])
                                    if intersect == -1: pass
                                    else:
                                        transmiss = transmiss * zoneWindowTransmiss[zoneCount][winCount]
                                        winNameList.append(zoneWindowNames[zoneCount][winCount].upper())
                                finalViewCount.append(transmiss)
                                finalWindowNameCount.append(winNameList)
                        else:
                            #The ray has been blocked by an opaque surface.
                            finalViewCount.append(0)
                            finalWindowNameCount.append(0)
                    
                    #Sum up the lists and divide by the total rays to get the view factor.
                    testPtSkyBlockedList[zoneCount].append(finalViewCount)
                    testPtSkyView[zoneCount].append(sum(finalViewCount)/divisor)
                    testPtBlockName[zoneCount].append(finalWindowNameCount)
        else:
            testPtSkyView.append(0)
            testPtSkyBlockedList.append([range(len(skyViewVecs))])
            testPtBlockName.append([range(len(skyViewVecs))])
    
    return testPtSkyView, testPtSkyBlockedList, testPtBlockName


def main(testPts, zoneSrfsMesh, viewVectors, includeOutdoor):
    testPtViewFactor = []
    
    for zoneCount, pointList in enumerate(testPts):
        if parallel_ == True  or parallel_ == None:
            viewFactors = parallel_projection(zoneSrfsMesh[zoneCount], viewVectors, testPts[zoneCount])
            testPtViewFactor.append(viewFactors)
        else:
            testPtViewFactor.append([])
            for pointCount, point in enumerate(pointList):
                #Make the list that will eventually hold the view factors of each surface.
                testPtViewFactor[zoneCount].append([])
                divisor = len(viewVectors)
                
                #Create the rays to be projected from each point.
                pointRays = []
                for vec in viewVectors: pointRays.append(rc.Geometry.Ray3d(point, vec))
                
                #Create a list that will hold the intersection hits of each surface
                srfHits = []
                for srf in zoneSrfsMesh[zoneCount]: srfHits.append([])
                
                #Perform the intersection of the rays with the mesh.
                pointIntersectList = []
                for rayCount, ray in enumerate(pointRays):
                    pointIntersectList.append([])
                    for srf in zoneSrfsMesh[zoneCount]:
                        intersect = rc.Geometry.Intersect.Intersection.MeshRay(srf, ray)
                        if intersect == -1: intersect = "N"
                        pointIntersectList[rayCount].append(intersect)
                
                #Find the intersection that was the closest for each ray.
                for list in pointIntersectList:
                    try:
                        if allSame(list) == False:
                            minIndex, minValue = min(enumerate(list), key=operator.itemgetter(1))
                            srfHits[minIndex].append(1)
                    except: pass
                
                #Sum up the lists and divide by the total rays to get the view factor.
                for hitList in srfHits:
                    testPtViewFactor[zoneCount][pointCount].append(sum(hitList)/divisor)
    
    
    return testPtViewFactor


def computeFloorReflect(testPts, testPtViewFactor, zoneSrfTypes, flrRefList):
    # Set defaults and a list to be filled.
    defaultRef = 0.2
    zoneFlrReflects = []
    includeOutdoor = False
    if len(testPts) == len(flrRefList): includeOutdoor = True
    
    #Compute the ground reflectivity from view factor calculations of ground surfaces.
    for zoneCount, zonePts in enumerate(testPts):
        zoneFlrReflects.append([])
        for ptCount, pt in enumerate(zonePts):
            ptViewFacs = []
            ptRefs = []
            
            if includeOutdoor == True:
                if zoneCount != len(testPts) - 1:
                    for srfCount, srf in enumerate(zoneSrfTypes[zoneCount]):
                        if srf == 2 or srf == 2.25 or srf == 2.5 or srf == 2.75:
                            ptRefs.append(flrRefList[zoneCount][srfCount])
                            ptViewFacs.append(testPtViewFactor[zoneCount][ptCount][srfCount])
                else:
                    for srfCount, srf in enumerate(zoneSrfTypes[zoneCount]):
                        if srf == 1 or srf == 1.5:
                            ptRefs.append(flrRefList[zoneCount][srfCount])
                            ptViewFacs.append(testPtViewFactor[zoneCount][ptCount][srfCount])
            else:
                for srfCount, srf in enumerate(zoneSrfTypes[zoneCount]):
                    if srf == 2 or srf == 2.25 or srf == 2.5 or srf == 2.75:
                        ptRefs.append(flrRefList[zoneCount][srfCount])
                        ptViewFacs.append(testPtViewFactor[zoneCount][ptCount][srfCount])
            
            missingViewFac = 0.5 - sum(ptViewFacs)
            ptViewFacs.append(missingViewFac)
            ptRefs.append(defaultRef)
            weightedFloorRef = 0
            for refCount, ref in enumerate(ptRefs):
                try:
                    weightedFloorRef = weightedFloorRef + ref*ptViewFacs[refCount]
                except: pass
            weightedFloorRef = weightedFloorRef * 2
            zoneFlrReflects[zoneCount].append(weightedFloorRef)
    
    return zoneFlrReflects




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
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)




#Start clocks to give a total calculation time report at the end
total_ms = None
total_fs = None


#Set the default to not generate the mesh.
buildMesh = False
if _buildMesh == None: pass
else: buildMesh = _buildMesh


#Check the data input.
checkData = False
if initCheck == True:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_ViewFacotrSrfData"]
    if hb_zoneData[10] == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        checkData, gridSize, distFromFloor, viewResolution, removeInt, sectionMethod, sectionBreps, includeOutdoor, constantTransmis, addShdTransmiss = checkTheInputs()

#Create a mesh of the area to calculate the view factor from.
geoCheck = False
if checkData == True and buildMesh == True:
    start = time.clock()
    goodGeo = prepareGeometry(gridSize, distFromFloor, removeInt, sectionMethod, sectionBreps, includeOutdoor, constantTransmis, addShdTransmiss, hb_zoneData)
    if goodGeo != -1:
        geoCheck, testPtsInit, viewFactorBrep, viewFactorMeshActual, zoneWireFrame, zoneSrfsMesh, zoneSrfNames, zoneOpaqueMesh, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, zoneHasWindows, zoneBrepsNonSolid, includeOutdoor, zoneWindowMesh, zoneWindowTransmiss, outdoorPtHeightWeights, zoneWindowNames, flrRefList, zoneSrfTypes, finalAddShdTransmiss = goodGeo
    total_ms = time.clock() - start
    
    #Unpack the data trees of test pts and mesh breps so that the user can see them and get a sense of what to expect from the view factor calculation.
    testPts = DataTree[Object]()
    viewFactorMesh = DataTree[Object]()
    shadingContext = DataTree[Object]()
    closedAirVolumes = DataTree[Object]()
    viewMeshFaces = DataTree[Object]()
    for brCount, branch in enumerate(testPtsInit):
        for item in branch:testPts.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(viewFactorMeshActual):
        for item in branch: viewFactorMesh.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(viewFactorBrep):
        for item in branch: viewMeshFaces.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(zoneOpaqueMesh):
        for item in branch: shadingContext.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(zoneBrepsNonSolid):
        for item in branch: closedAirVolumes.Add(item, GH_Path(brCount))

#If all of the data is good and the user has set "_runIt" to "True", run the shade benefit calculation to generate all results.
if checkData == True and _runIt == True and geoCheck == True and buildMesh == True:
    start = time.clock()
    viewVectors, skyViewVecs = checkViewResolution(viewResolution, lb_preparation)
    testPtViewFactor = main(testPtsInit, zoneSrfsMesh, viewVectors, includeOutdoor)
    testPtSkyView, testPtBlockedVec, testPtBlockName = skyViewCalc(testPtsInit, zoneOpaqueMesh, skyViewVecs, zoneHasWindows, zoneWindowMesh, zoneWindowTransmiss, zoneWindowNames)
    
    outdoorNonSrfViewFac = []
    if sectionMethod != 0 and includeOutdoor == True:
        outdoorIsThere = True
        outdoorNonSrfViewFac = checkOutdoorViewFac(testPtViewFactor[-1], testPtSkyView[-1])
    else: outdoorIsThere = False
    
    finalFloorRefList = computeFloorReflect(testPtsInit, testPtViewFactor, zoneSrfTypes, flrRefList)
    
    total_fs = time.clock() - start
    
    #Put all of the information into a list that will carry the data onto the next component easily.
    viewFactorInfo = [testPtViewFactor, zoneSrfNames, testPtSkyView, testPtBlockedVec, testPtZoneWeights, testPtZoneNames, ptHeightWeights, zoneInletInfo, zoneHasWindows, outdoorIsThere, outdoorNonSrfViewFac, outdoorPtHeightWeights, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, finalFloorRefList, constantTransmis, finalAddShdTransmiss]

#Print out a report of calculation time.
print "_"
if total_ms != None: print str(round(total_ms, 3)) + " seconds were spent creating the view factor mesh."
if total_fs != None: print str(round(total_fs, 3)) + " seconds were spent calculating view factors."

#Hide the outputs that are not highly important.
ghenv.Component.Params.Output[5].Hidden = True
ghenv.Component.Params.Output[9].Hidden = True
ghenv.Component.Params.Output[10].Hidden = True
if _runIt == True:
    ghenv.Component.Params.Output[6].Hidden = True
    ghenv.Component.Params.Output[2].Hidden = False
else:
    ghenv.Component.Params.Output[6].Hidden = False
    ghenv.Component.Params.Output[2].Hidden = True
