# This component generates test points within a zone and calculates view factors of each of these points to the other surfaces of the zone.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate test points within a zone an calculate view factor from each of these points to the other zurfaces in a zone.
_
This component is a necessary step before creating an MRT map of a zone.
-
Provided by Honeybee 0.0.55
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component as surfaces may not align otherwise.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        gridSize_: A number in Rhino model units to make each cell of the view factor mesh.
        distFromFloorOrSrf_: A number in Rhino model units to set the distance of the view factor mesh from the ground.
        viewResolution_: An interger between 0 and 4 to set the number of times that the tergenza skyview patches are split.  A higher number will ensure a greater accuracy but will take longer.  The default is set to 0 for a quick calculation.
        removeAirWalls_: Set to "True" to remove air walls from the view factor calculation.  The default is set to "True" sinc you usually want to remove air walls from your view factor calculations.
        additionalShading_: Add in additional shading breps here for geometry that is not a part of the zone but can still block direct sunlight to occupants.  Examples include outdoor context shading and indoor furniture.
        parallel_: Set to "True" to run the calculation with multiple cores and "False" to run it with a single core.  Multiple cores can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.  The default is set to "True."
        _runIt: Set boolean to "True" to run the component and calculate viewFactors from each test point to surrounding surfaces.
    Returns:
        readMe!: ...
        ==========: ...
        viewFactorMesh: A data tree of meshes to be plugged into the "Annual Comfort Analysis Recipe" component.
        viewFactorInfo: A list of python data that carries essential numerical information for the Comfort Analysis Workflow, including the view factors from each test point to a zone's surfaces, the sky view factors of the test points, and information related to window plaement, used to estimate stratification in the zone.  This should be plugged into the "Annual Comfort Analysis Recipe" component.
        ==========: ...
        testPts: The test points, which lie in the center of the mesh faces at which comfort parameters are being evaluated.
        zoneWireFrame: A list of curves representing the outlines of the zones.  This is particularly helpful if you want to see the outline of the building in relation to the temperature and comfort maps that you might produce off of these results.
        viewVectors: The vectors that were used to caclulate the view factor (note that these will increase as the viewResolution increases).
        shadingContext: A list of meshes representing the opaque surfaces of the zone.  These are what were used to determine the sky view factor and the direct sun falling on occupants.
"""

ghenv.Component.Name = "Honeybee_Indoor View Factor Calculator"
ghenv.Component.NickName = 'IndoorViewFactor'
ghenv.Component.Message = 'VER 0.0.56\nMAR_22_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass


from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc
import operator
import System.Threading.Tasks as tasks

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance

def copyHBZoneData():
    checkZones = True
    hb_hive = sc.sticky["honeybee_Hive"]()
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
    
    for zoneCount, HZone in enumerate(_HBZones):
        surfaceNames.append([])
        srfBreps.append([])
        srfTypes.append([])
        srfInteriorList.append([])
        srfAirWallAdjList.append([])
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        zoneNames.append(zone.name)
        zoneNatVentArea.append(zone.windowOpeningArea)
        zoneVolumes.append(zone.getZoneVolume())
        
        for srf in zone.surfaces:
            surfaceNames[zoneCount].append(srf.name)
            srfTypes[zoneCount].append(srf.type)
            if srf.BC.lower() == "surface":
                if srf.type == 4:
                    try:
                        srfInteriorList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1])
                        srfAirWallAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
                    except:
                        checkZones = False
                        warning = "Connected zones contain an outdoor airwall, which is currently not supported by this workflow."
                        print warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                else:
                    srfInteriorList[zoneCount].append(None)
                    srfAirWallAdjList[zoneCount].append(str(srf.BCObject.parent).split('\n')[0].split(': ')[-1])
            else:
                srfInteriorList[zoneCount].append(None)
                srfAirWallAdjList[zoneCount].append(None)
            if srf.hasChild:
                srfBreps[zoneCount].append(srf.punchedGeometry)
                for srfCount, childSrf in enumerate(srf.childSrfs):
                    srfTypes[zoneCount].append(childSrf.type)
                    surfaceNames[zoneCount].append(childSrf.name)
                    srfBreps[zoneCount].append(childSrf.geometry)
                    if srf.type == 0 and srf.BC.lower() == "surface":
                        srfInteriorList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1] + '_glz_' + str(srfCount))
                        srfAirWallAdjList[zoneCount].append(None)
                    else:
                        srfInteriorList[zoneCount].append(None)
                        srfAirWallAdjList[zoneCount].append(None)
            else:
                srfBreps[zoneCount].append(srf.geometry)
    
    #Change the list of adjacent zones to be based on the list item of the zone
    srfAirWallAdjNumList = []
    for srfListCount, zoneSrfList in enumerate(srfAirWallAdjList):
        srfAirWallAdjNumList.append([])
        for surface in zoneSrfList:
            foundZone = False
            for zoneCount, zoneName in enumerate(zoneNames):
                if surface == zoneName:
                    srfAirWallAdjNumList[srfListCount].append(zoneCount)
                    foundZone = True
            if foundZone == False:
                srfAirWallAdjNumList[srfListCount].append(None)
    
    sc.sticky["Honeybee_ViewFacotrSrfData"] = [zoneBreps, surfaceNames, srfBreps, zoneCentPts, srfTypes, srfInteriorList, zoneNames, zoneNatVentArea, zoneVolumes, srfAirWallAdjNumList, checkZones]


def checkTheInputs():
    #Check the grid size and set a default based on the size of each zone if nothing is connected.
    rhinoModelUnits = str(sc.doc.ModelUnitSystem)
    checkData1 = False
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
            distFromFloor = distFromFloorOrSrf_[0]
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
            print "No value connected for distFromFloor_.  The distance from the floor has been set to " + str(distFromFloor) + " " + rhinoModelUnits + "."
    else:
        distFromFloor = 0.9
        sectionMesh, sectionBreps = lb_preparation.cleanAndCoerceList(distFromFloorOrSrf_)
    
    #Check to be sure that none of the zones are having the temperature map generated above them.
    checkData2 = True
    if _HBZones != []:
        for zone in _HBZones:
            zoneBBox = rc.Geometry.Box(zone.GetBoundingBox(rc.Geometry.Plane.WorldXY))
            zDist = zoneBBox.Z[1] - zoneBBox.Z[0]
            if zDist > distFromFloor: pass
            else: checkData2 = False
        if checkData2 == False:
            warning = "The distFromFloor_ is greater than the height of one or more of the zones."
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
    
    #Check the removeAirWalls_ option.
    if removeAirWalls_ == None: removeInt = True
    else: removeInt = removeAirWalls_
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True:
        checkData = True
    else: checkData = False
    
    return checkData, gridSize, distFromFloor, viewResolution, removeInt, sectionMethod, sectionBreps

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

def prepareGeometry(gridSize, distFromFloor, removeInt, sectionMethod, sectionBreps, hb_zoneData):
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
    
    
    #Make copies of the original zones in the event that some are combined as air walls are removed.
    oldZoneBreps = zoneBreps[:]
    oldZoneSrfs = zoneSrfs[:]
    oldZoneSrfTypes = zoneSrfTypes[:]
    
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
    zoneHasWindows = []
    zoneWeights = []
    zoneInletParams = []
    zoneBrepsNonSolid = []
    
    #Write a function to split breps with the zone and pull out the correctly split surface.
    def splitOffsetFloor(brep, zone):
        splitBrep = rc.Geometry.Brep.Split(brep, zone, tol)
        distToCent = []
        for element in splitBrep:
            distToCent.append(rc.Geometry.Point3d.DistanceTo(rc.Geometry.AreaMassProperties.Compute(element).Centroid, rc.Geometry.AreaMassProperties.Compute(zone).Centroid))
        distToCent, splitBrep = zip(*sorted(zip(distToCent, splitBrep)))
        finalBrep = splitBrep[0]
        
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
        
        adjacentList = []
        totalAdjList = []
        adjCounter = 0
        for zoneCount, srfList in enumerate(zoneSrfs):
            if allSame(srfInteriorList[zoneCount]) == False:
                for srfCount, srf in enumerate(srfList):
                    if srfInteriorList[zoneCount][srfCount] != None:
                        if len(adjacentList) == 0:
                            adjacentList.append([])
                            adjCounter += 1
                            adjacentList[adjCounter-1].append(zoneCount)
                        elif zoneCount in adjacentList[adjCounter-1]: pass
                        else:
                            adjacentList.append([])
                            adjCounter += 1
                            adjacentList[adjCounter-1].append(zoneCount)
                        
                        #Find the adjacent zone and append it to the list.
                        adjSrf = srfInteriorList[zoneCount][srfCount]
                        for zoneCount2, srfList in enumerate(surfaceNames):
                            for srfName in srfList:
                                if adjSrf == srfName: adjacentList[adjCounter-1].append(zoneCount2)
            else:
                adjCounter += 1
                adjacentList.append([zoneCount])
        
        #Order the list based on the most connected zones.
        lengthsList = []
        for zoneList in adjacentList:
            lengthsList.append(len(zoneList))
        lengthsList, adjacentList = zip(*sorted(zip(lengthsList, adjacentList)))
        
        #Remove duplicates found in the process of looking for adjacencies.
        fullAdjacentList = []
        newAjdacenList = []
        newCounter = 0
        for listCount, zoneList in enumerate(adjacentList):
            good2Go = True
            for zoneNum in zoneList:
                if zoneNum in fullAdjacentList: good2Go = False
            if good2Go == True:
                newAjdacenList.append(removeDup(zoneList))
                fullAdjacentList.extend(adjacentList[listCount])
                newCounter += 1
            else:
                newAjdacenList[newCounter-1] = removeDup(zoneList)
                fullAdjacentList.extend(adjacentList[listCount])
        adjacentList = newAjdacenList
        
        #Get all of the data of the new zone together.
        for listCount, list in enumerate(adjacentList):
            listMarker = len(newSurfaceNames)
            newSurfaceNames.append([])
            newZoneSrfs.append([])
            newZoneSolidSrfs.append([])
            newZoneSrfTypes.append([])
            zoneBrepsNonSolid.append([])
            
            for zoneCount in list:
                for srfCount, surface in enumerate(zoneSrfs[zoneCount]):
                    
                    if srfInteriorList[zoneCount][srfCount] == None and srfAirWallAdjList[zoneCount][srfCount] not in list:
                        newZoneSolidSrfs[listMarker].append(surface)
                        newZoneSrfs[listMarker].append(surface)
                        newSurfaceNames[listMarker].append(surfaceNames[zoneCount][srfCount])
                        newZoneSrfTypes[listMarker].append(zoneSrfTypes[zoneCount][srfCount])
                    elif srfInteriorList[zoneCount][srfCount] == None and srfAirWallAdjList[zoneCount][srfCount] in list:
                        newZoneSrfs[listMarker].append(surface)
                        newSurfaceNames[listMarker].append(surfaceNames[zoneCount][srfCount])
                        newZoneSrfTypes[listMarker].append(zoneSrfTypes[zoneCount][srfCount])
            
            zoneBrepsNonSolid.append(rc.Geometry.Brep.JoinBreps(newZoneSrfs[listMarker], tol))
            newZoneBreps.append(rc.Geometry.Brep.JoinBreps(newZoneSolidSrfs[listMarker], tol)[0])
        
        zoneBreps = newZoneBreps
        surfaceNames = newSurfaceNames
        zoneSrfs = newZoneSrfs
        zoneSrfTypes = newZoneSrfTypes
    
    #Make sure points are inside the zones.
    for brepCount, brep in enumerate(zoneBreps):
        if brep.IsSolid: pass
        else:
            attemptToCap = brep.CapPlanarHoles(tol)
            if attemptToCap != None: zoneBreps[brepCount] = attemptToCap
            if zoneBreps[brepCount].IsSolid: pass
            else:
                geoCheck = False
                warning = "Getting rid of interior walls has caused the connected zone geometry to not be closed.  Try connecting all zones of your building or all zones for each floor."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    
    geoCheck = True
    
    if geoCheck == True:
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
            surfaceNames.append([])
            
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
                            finalBreps.append(finalBrep)
                        except:
                            finalBreps.append([brep])
            else:
                for srfCount, srf in enumerate(srfList):
                    zoneSrfsMesh[zoneCount].append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
                finalBreps = [sectionBreps]
            
            #Generate the meshes and test points of the final surface.
            for brep in finalBreps:
                finalMesh = createMesh(brep, gridSize)
                for mesh in finalMesh:
                    finalTestPts = []
                    finalFaceBreps = []
                    deleteIndices = []
                    for faceCount, face in enumerate(mesh.Faces):
                        if face.IsQuad:
                            faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), rc.Geometry.Point3d(mesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
                        if face.IsTriangle:
                            faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
                        centPt = rc.Geometry.AreaMassProperties.Compute(faceBrep).Centroid
                        #Do a final check to be sure that the test point does not lie outside the zone and, if so, delete the mesh face, and don't append the point.
                        if zoneBreps[zoneCount].IsPointInside(centPt, tol, True) == False:
                            deleteIndices.append(faceCount)
                        else:
                            finalFaceBreps.append(faceBrep)
                            finalTestPts.append(centPt)
                    
                    finalMesh = rc.Geometry.Mesh()
                    for brepCt, brep in enumerate(finalFaceBreps):
                        if brep.Vertices.Count == 4:
                            facePt1 = rc.Geometry.Point3d(brep.Vertices[0].Location)
                            facePt2 = rc.Geometry.Point3d(brep.Vertices[1].Location)
                            facePt3 = rc.Geometry.Point3d(brep.Vertices[2].Location)
                            facePt4 = rc.Geometry.Point3d(brep.Vertices[3].Location)
                            
                            meshFacePts = [facePt1, facePt2, facePt3, facePt4]
                            mesh = rc.Geometry.Mesh()
                            for point in meshFacePts:
                                mesh.Vertices.Add(point)
                            
                            mesh.Faces.AddFace(0, 1, 2, 3)
                            finalMesh.Append(mesh)
                        else:
                            facePt1 = rc.Geometry.Point3d(brep.Vertices[0].Location)
                            facePt2 = rc.Geometry.Point3d(brep.Vertices[1].Location)
                            facePt3 = rc.Geometry.Point3d(brep.Vertices[2].Location)
                            
                            meshFacePts = [facePt1, facePt2, facePt3]
                            mesh = rc.Geometry.Mesh()
                            for point in meshFacePts:
                                mesh.Vertices.Add(point)
                            
                            mesh.Faces.AddFace(0, 1, 2)
                            finalMesh.Append(mesh)
                    
                    if len(finalTestPts) > 0:
                        if len(MRTMeshInit[zoneCount]) > 0: MRTMeshInit[zoneCount][0].Append(finalMesh)
                        else: MRTMeshInit[zoneCount].append(finalMesh)
                        
                        MRTMeshBreps[zoneCount].extend(finalFaceBreps)
                        testPts[zoneCount].extend(finalTestPts)
        
        #Make a list for the weighting of each zone value.
        zoneWeights = []
        heightWeights = []
        for falseZoneCount, falseZone in enumerate(testPts):
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
            
            #For each of the test points, weight them based on which zone they belong to.
            for falseZoneCount, falseZone in enumerate(testPts):
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
            #For each of the test points, give them a weight of 1 based on which zone they belong to.
            for falseZoneCount, falseZone in enumerate(testPts):
                for pointCount, point in enumerate(falseZone):
                    for orignalZoneCount, oirignalZone in enumerate(oldZoneBreps):
                        if oirignalZone.IsPointInside(point, tol, True) == True: zoneWeights[falseZoneCount][pointCount].append(1)
                        else: zoneWeights[falseZoneCount][pointCount].append(0)
        
        #Calculate height weights for each of the points.
        for falseZoneCount, falseZone in enumerate(testPts):
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
            
            #Calculate the height from the floor to the window mid-plane
            zoneGlzMesh = rc.Geometry.Mesh()
            glzTracker = 0
            for srfCt, srf in enumerate(oldZoneSrfs[orignalZoneCount]):
                if oldZoneSrfTypes[orignalZoneCount][srfCt] == 5:
                    zoneGlzMesh.Append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
                    glzTracker += 1
            if glzTracker != 0:
                glzBB = rc.Geometry.Brep.GetBoundingBox(zoneGlzMesh, rc.Geometry.Plane.WorldXY)
                glzMinHeight = glzBB.Min.Z
                glzCentPt = rc.Geometry.AreaMassProperties.Compute(zoneGlzMesh).Centroid
                glzMidHeight = glzCentPt.Z
                zoneInletParams[orignalZoneCount].append(glzMidHeight - glzMinHeight)
            else: zoneInletParams[orignalZoneCount].append(None)
            
            #Get the volume of each zone.
            zoneInletParams[orignalZoneCount].append(zoneVolumes[orignalZoneCount])
            
            #Get the area of operable glazing.
            opGlzArea = 0
            for val in zoneNatVentArea[orignalZoneCount]:
                if val != None: opGlzArea += float(val)
            zoneInletParams[orignalZoneCount].append(opGlzArea)
        
        # Pull out the geometry that can block sun vectors.
        for zCount, zoneSrfTList in enumerate(zoneSrfTypes):
            zoneOpaqueMesh.append([])
            if additionalShading_ != []:
                for item in additionalShading_:
                    opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(item, rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneOpaqueMesh[zCount].append(opaqueMesh)
            
            hasWindows = 0
            for sCount, srfT in enumerate(zoneSrfTList):
                if srfT != 5:
                    opaqueMesh = rc.Geometry.Mesh.CreateFromBrep(zoneSrfs[zCount][sCount], rc.Geometry.MeshingParameters.Coarse)[0]
                    zoneOpaqueMesh[zCount].append(opaqueMesh)
                else:
                    hasWindows = 1
            zoneHasWindows.append(hasWindows)
        
        
        return geoCheck, testPts, MRTMeshBreps, MRTMeshInit, zoneWires, zoneSrfsMesh, surfaceNames, zoneOpaqueMesh, zoneNames, zoneWeights, heightWeights, zoneInletParams, zoneHasWindows
    else:
        return -1

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
            minIndex, minValue = min(enumerate(list), key=operator.itemgetter(1))
            srfHits[minIndex].append(1)
        
        #Sum up the lists and divide by the total rays to get the view factor.
        for hitList in srfHits:
            pointIntList[i].append(sum(hitList)/divisor)
    
    tasks.Parallel.ForEach(range(len(pointList)), intersect)
    
    return pointIntList


def parallel_skyProjection(zoneOpaqueMesh, skyViewVecs, pointList):
    #Placeholder for the outcome of the parallel projection.
    pointIntList = []
    skyBlockedList = []
    for num in range(len(pointList)):
        pointIntList.append(0.0)
        skyBlockedList.append([])
    
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
        for rayList in finalIntersectList:
            if sum(rayList) == 0: finalViewCount.append(1)
            else: finalViewCount.append(0)
        
        #Sum up the lists and divide by the total rays to get the view factor.
        skyBlockedList[i] = finalViewCount
        pointIntList[i] = sum(finalViewCount)/divisor
    
    tasks.Parallel.ForEach(range(len(pointList)), intersect)
    
    return pointIntList, skyBlockedList


def skyViewCalc(testPts, zoneOpaqueMesh, skyViewVecs, zoneHasWindows):
    testPtSkyView = []
    testPtSkyBlockedList = []
    
    for zoneCount, pointList in enumerate(testPts):
        if zoneHasWindows[zoneCount] == True:
            if parallel_ == True or parallel_ == None:
                skyViewFactors, skyBlockedList = parallel_skyProjection(zoneOpaqueMesh[zoneCount], skyViewVecs, testPts[zoneCount])
                testPtSkyView.append(skyViewFactors)
                testPtSkyBlockedList.append(skyBlockedList)
            else:
                testPtSkyView.append([])
                testPtSkyBlockedList.append([])
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
                            if intersect == -1:
                                pointIntersectList[rayCount].append(0)
                            else: pointIntersectList[rayCount].append(1)
                    
                    #See if the ray passed all of the context meshes.
                    finalIntersectList = []
                    for ray in pointRays:
                        finalIntersectList.append([])
                    for listCt, rayList in enumerate(pointIntersectList):
                        for intersect in rayList:
                            finalIntersectList[listCt].append(intersect)
                    
                    finalViewCount = []
                    for rayList in finalIntersectList:
                        if sum(rayList) == 0: finalViewCount.append(1)
                        else: finalViewCount.append(0)
                    
                    #Sum up the lists and divide by the total rays to get the view factor.
                    testPtSkyBlockedList[zoneCount].append(finalViewCount)
                    testPtSkyView[zoneCount].append(sum(finalViewCount)/divisor)
        else:
            testPtSkyView.append(0)
            testPtSkyBlockedList.append([range(len(skyViewVecs))])
    
    return testPtSkyView, testPtSkyBlockedList


def main(testPts, zoneSrfsMesh, viewVectors):
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
                        minIndex, minValue = min(enumerate(list), key=operator.itemgetter(1))
                        srfHits[minIndex].append(1)
                    except: pass
                
                #Sum up the lists and divide by the total rays to get the view factor.
                for hitList in srfHits:
                    testPtViewFactor[zoneCount][pointCount].append(sum(hitList)/divisor)
    
    return testPtViewFactor




#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True and len(_HBZones) > 0:
    if _HBZones[0] != None:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_ViewFacotrSrfData"]
        initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == False:
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
elif _HBZones != [] and sc.sticky.has_key('ladybug_release') == False:
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    pass



#Check the data input.
checkData = False
if initCheck == True:
    if hb_zoneData[10] == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        checkData, gridSize, distFromFloor, viewResolution, removeInt, sectionMethod, sectionBreps = checkTheInputs()

#Create a mesh of the area to calculate the view factor from.
geoCheck = False
if checkData == True:
    goodGeo = prepareGeometry(gridSize, distFromFloor, removeInt, sectionMethod, sectionBreps, hb_zoneData)
    if goodGeo != -1:
        geoCheck, testPtsInit, viewFactorBrep, viewFactorMeshActual, zoneWireFrame, zoneSrfsMesh, zoneSrfNames, zoneOpaqueMesh, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, zoneHasWindows = goodGeo
    
    #Unpack the data trees of test pts and mesh breps so that the user can see them and get a sense of what to expect from the view factor calculation.
    if geoCheck == True:
        testPts = DataTree[Object]()
        viewFactorMesh = DataTree[Object]()
        shadingContext = DataTree[Object]()
        for brCount, branch in enumerate(testPtsInit):
            for item in branch:testPts.Add(item, GH_Path(brCount))
        for brCount, branch in enumerate(viewFactorBrep):
            for item in branch: viewFactorMesh.Add(item, GH_Path(brCount))
        for brCount, branch in enumerate(zoneOpaqueMesh):
            for item in branch: shadingContext.Add(item, GH_Path(brCount))

#If all of the data is good and the user has set "_runIt" to "True", run the shade benefit calculation to generate all results.
if checkData == True and _runIt == True and geoCheck == True:
    viewVectors, skyViewVecs = checkViewResolution(viewResolution, lb_preparation)
    testPtViewFactor = main(testPtsInit, zoneSrfsMesh, viewVectors)
    testPtSkyView, testPtBlockedVec = skyViewCalc(testPtsInit, zoneOpaqueMesh, skyViewVecs, zoneHasWindows)
    
    #Put all of the information into a list that will carry the data onto the next component easily.
    viewFactorInfo = [testPtViewFactor, zoneSrfNames, testPtSkyView, testPtBlockedVec, testPtZoneWeights, testPtZoneNames, ptHeightWeights, zoneInletInfo, zoneHasWindows]
    
    #Unpack the data trees of meshes.
    viewFactorMesh = DataTree[Object]()
    for brCount, branch in enumerate(viewFactorMeshActual):
        for item in branch: viewFactorMesh.Add(item, GH_Path(brCount))

ghenv.Component.Params.Output[5].Hidden = True
ghenv.Component.Params.Output[8].Hidden = True