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
        gridSize_: A number in Rhino model units to make each cell of the radiant temperature mesh.
        distFromFloor_: A number in Rhino model units to set the distance of the radiant temperature mesh from the ground.
        viewResolution_: An interger between 0 and 4 to set the number of times that the tergenza skyview patches are split.  A higher number will ensure a greater accuracy but will take longer.  The default is set to 0 for a quick calculation.
        removeInteriorWalls_: Set to "True" to remove interior walls from the view factor calculation.  This is useful if your interior walls are air walls.  The default is set to "False" and will treat each surface as opaque.
        parallel_: Set to "True" to run the calculation with multiple cores.  This can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.
        _runIt: Set boolean to "True" to run the component and calculate viewFactors from each test point to surrounding surfaces.
    Returns:
        readMe!: ...
        viewFactorMesh: A list of meshes to be fed into the "Honeybee_Indoor Radiant Temperature Map".
        testPtsViewFactor: A branched data tree with the view factors of each test point to a corresponding surface in the list below.
        zoneSrfNames: A branched data tree with the names of each of the surfaces for each zone.
        ==========: ...
        testPts: The test points, which correspond with the view factors below.
        zoneWireFrame: A list of curves representing the outlines of the zones.  This is particularly helpful if you want to see the outline of the building in relation to the radiant temperature map that you might produce off of these results.
        viewVectors: The vectors that were used to caclulate the view factor (note that these will increase as the viewResolution increases).
"""

ghenv.Component.Name = "Honeybee_Indoor View Factor Calculator"
ghenv.Component.NickName = 'IndoorViewFactor'
ghenv.Component.Message = 'VER 0.0.55\nSEP_22_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
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
    hb_hive = sc.sticky["honeybee_Hive"]()
    surfaceNames = []
    srfBreps = []
    zoneBreps = []
    zoneCentPts = []
    srfTypes = []
    srfInteriorList = []
    
    for zoneCount, HZone in enumerate(_HBZones):
        surfaceNames.append([])
        srfBreps.append([])
        srfTypes.append([])
        srfInteriorList.append([])
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        for srf in zone.surfaces:
            surfaceNames[zoneCount].append(srf.name)
            srfTypes[zoneCount].append(srf.type)
            if srf.type == 0 and srf.BC.lower() == "surface":
                srfInteriorList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1])
            else: srfInteriorList[zoneCount].append(None)
            if srf.hasChild:
                srfBreps[zoneCount].append(srf.punchedGeometry)
                for srfCount, childSrf in enumerate(srf.childSrfs):
                    srfTypes[zoneCount].append(childSrf.type)
                    surfaceNames[zoneCount].append(childSrf.name)
                    srfBreps[zoneCount].append(childSrf.geometry)
                    if srf.type == 0 and srf.BC.lower() == "surface":
                        srfInteriorList[zoneCount].append(str(srf.BCObject).split('\n')[0].split(': ')[-1] + '_glz_' + str(srfCount))
                    else: srfInteriorList[zoneCount].append(None)
            else:
                srfBreps[zoneCount].append(srf.geometry)
    
    sc.sticky["Honeybee_ViewFacotrSrfData"] = [zoneBreps, surfaceNames, srfBreps, zoneCentPts, srfTypes, srfInteriorList]


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
    
    #Check the distFromFloor_ and set a default based on the rhino model units if the user has not connected anything.
    if distFromFloor_:
        distFromFloor = distFromFloor_
    elif rhinoModelUnits == 'Meters':
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
    
    #Check the removeInteriorWalls_ option.
    if removeInteriorWalls_ == None: removeInt = False
    else: removeInt = removeInteriorWalls_
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True:
        checkData = True
    else: checkData = False
    
    return checkData, gridSize, distFromFloor, viewResolution, removeInt

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

def prepareGeometry(gridSize, distFromFloor, removeInt, hb_zoneData):
    #Separate the HBZoneData.
    zoneBreps = hb_zoneData[0]
    surfaceNames = hb_zoneData[1]
    zoneSrfs = hb_zoneData[2]
    zoneSrfTypes = hb_zoneData[4]
    srfInteriorList = hb_zoneData[5]
    srfMeshPar = rc.Geometry.MeshingParameters.Coarse
    
    #Create the lists that will be filled.
    geoCheck = True
    testPts = []
    MRTMeshBreps = []
    MRTMeshInit = []
    zoneSrfsMesh = []
    zoneWires = []
    
    #Write a function to split breps with the zone and pull out the correctly split surface.
    def splitOffsetFloor(brep, zone):
        splitBrep = brep.split(zone, tol)
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
        
        #Make blank lists that will re-create the original lists.
        newZoneBreps = []
        newSurfaceNames = []
        newZoneSrfs = []
        newZoneSrfTypes = []
        
        adjacentList = []
        adjCounter = 0
        for zoneCount, srfList in enumerate(zoneSrfs):
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
        for listCount, list in enumerate(adjacentList):
            adjacentList[listCount] = removeDup(list)
        
        for listCount, list in enumerate(adjacentList):
            newSurfaceNames.append([])
            newZoneSrfs.append([])
            newZoneSrfTypes.append([])
            
            for zoneCount in list:
                for srfCount, surface in enumerate(zoneSrfs[zoneCount]):
                    if srfInteriorList[zoneCount][srfCount] == None:
                        newZoneSrfs[listCount].append(surface)
                        newSurfaceNames[listCount].append(surfaceNames[zoneCount][srfCount])
                        newZoneSrfTypes[listCount].append(zoneSrfTypes[zoneCount][srfCount])
        
        for srfList in newZoneSrfs:
            newZoneBreps.append(rc.Geometry.Brep.JoinBreps(srfList, tol)[0])
        
        zoneBreps = newZoneBreps
        surfaceNames = newSurfaceNames
        zoneSrfs = newZoneSrfs
        zoneSrfTypes = newZoneSrfTypes
    
    for brep in zoneBreps:
        if brep.IsSolid: pass
        else:
            geoCheck = False
            warning = "Getting rid of interior walls has caused the connected zone geometry to not be closed.  Try connecting all zones of your building or all zones for each floor."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
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
            
            #Select out just the floor geometry.
            floorBreps = []
            for srfCount, srf in enumerate(srfList):
                zoneSrfsMesh[zoneCount].append(rc.Geometry.Mesh.CreateFromBrep(srf, srfMeshPar)[0])
                if zoneSrfTypes[zoneCount][srfCount] == 2 or zoneSrfTypes[zoneCount][srfCount] == 2.25 or zoneSrfTypes[zoneCount][srfCount] == 2.5 or zoneSrfTypes[zoneCount][srfCount] == 2.75:
                    floorBreps.append(srf)
            
            #If there are multiple floor breps, join them together.
            dataCheck = True
            if len(floorBreps) == 1: floorBrep = floorBreps
            elif len(floorBreps) > 1: floorBrep = rc.Geometry.Brep.JoinBreps(floorBreps, tol)
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
                    else:
                        finalBrepInit = splitOffsetFloor(brep, zoneBreps[zoneCount])
                        edges = finalBrepInit.DuplicateEdgeCurves()
                        joinedEdges = rc.Geometry.Curve.JoinCurves(edges, tol)
                        finalBrep = rc.Geometry.Brep.CreatePlanarBreps(joinedEdges[0])
                        finalBreps.append(finalBrep)
                else:
                    #If the surface is curved or has multiple elements, try to trim it with the closed zone brep.
                    try:
                        finalBrep = splitOffsetFloor(brep, zoneBreps[zoneCount])
                        finalBreps.append(finalBrep)
                    except: finalBreps.append(brep)
            
            #Generate the meshes and test points of the final surface.
            for brep in finalBreps:
                finalMesh = createMesh(brep, gridSize)[0]
                finalTestPts = []
                finalFaceBreps = []
                deleteIndices = []
                for faceCount, face in enumerate(finalMesh.Faces):
                    if face.IsQuad:
                        faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(finalMesh.Vertices[face.A]), rc.Geometry.Point3d(finalMesh.Vertices[face.B]), rc.Geometry.Point3d(finalMesh.Vertices[face.C]), rc.Geometry.Point3d(finalMesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
                    if face.IsTriangle:
                        faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(finalMesh.Vertices[face.A]), rc.Geometry.Point3d(finalMesh.Vertices[face.B]), rc.Geometry.Point3d(finalMesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
                    centPt = rc.Geometry.AreaMassProperties.Compute(faceBrep).Centroid
                    #Check to be sure that the test point does not lie outside the zone and, if so, delete the mesh face, and don't append the point.
                    if zoneBreps[zoneCount].IsPointInside(centPt, tol, True) == False:
                        deleteIndices.append(faceCount)
                        print "One of the gnerated test points was not inside the zone."
                    else:
                        finalFaceBreps.append(faceBrep)
                        finalTestPts.append(centPt)
                finalMesh = rc.Geometry.Mesh()
                for brep in finalFaceBreps:
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
                
                if len(deleteIndices) > 0:
                    finalMesh.Faces.DeleteFaces(deleteIndices)
                
                MRTMeshInit[zoneCount].append(finalMesh)
                MRTMeshBreps[zoneCount].extend(finalFaceBreps)
                testPts[zoneCount].extend(finalTestPts)
    else: pass
    
    return geoCheck, testPts, MRTMeshBreps, MRTMeshInit, zoneWires, zoneSrfsMesh, surfaceNames

def checkViewResolution(viewResolution, lb_preparation):
    newVecs = []
    skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, viewResolution, 1)
    for patch in skyPatches:
        patchPt = rc.Geometry.AreaMassProperties.Compute(patch).Centroid
        Vec = rc.Geometry.Vector3d(patchPt.X, patchPt.Y, patchPt.Z)
        revVec = rc.Geometry.Vector3d(-patchPt.X, -patchPt.Y, -patchPt.Z)
        newVecs.append(Vec)
        newVecs.append(revVec)
    
    return newVecs

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
    
    #for i in range(len(pointList)):
    #    intersect(i)
    
    tasks.Parallel.ForEach(range(len(pointList)), intersect)
    
    return pointIntList


def main(testPts, zoneSrfsMesh, viewVectors):
    testPtViewFactor = []
    
    for zoneCount, pointList in enumerate(testPts):
        if parallel_ == True:
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
                    minIndex, minValue = min(enumerate(list), key=operator.itemgetter(1))
                    srfHits[minIndex].append(1)
                
                #Sum up the lists and divide by the total rays to get the view factor.
                for hitList in srfHits:
                    testPtViewFactor[zoneCount][pointCount].append(sum(hitList)/divisor)
    
    
    
    return testPtViewFactor




#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True and sc.sticky.has_key('Honeybee_ViewFacotrSrfData') == False and len(_HBZones) > 0:
    if _HBZones[0] != None:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_ViewFacotrSrfData"]
        initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True and sc.sticky.has_key('Honeybee_ViewFacotrSrfData') == True and len(_HBZones) > 0:
    if _HBZones[0] != None:
        hb_zoneData = sc.sticky["Honeybee_ViewFacotrSrfData"]
        checkZones = True
        if len(_HBZones) == len(hb_zoneData[0]):
            for count, brep in enumerate(_HBZones):
                boundBoxVert = brep.GetBoundingBox(False).Center
                if boundBoxVert.X <= hb_zoneData[3][count].X+tol and boundBoxVert.X >= hb_zoneData[3][count].X-tol and boundBoxVert.Y <= hb_zoneData[3][count].Y+tol and boundBoxVert.Y >= hb_zoneData[3][count].Y-tol and boundBoxVert.Z <= hb_zoneData[3][count].Z+tol and boundBoxVert.Z >= hb_zoneData[3][count].Z-tol: pass
                else:
                    checkZones = False
        else: checkZones = False
        if checkZones == True: pass
        else:
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
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    checkData, gridSize, distFromFloor, viewResolution, removeInt = checkTheInputs()

#Create a mesh of the area to calculate the view factor from.
geoCheck = False
if checkData == True:
    geoCheck, testPtsInit, viewFactorBrep, viewFactorMeshActual, zoneWireFrame, zoneSrfsMesh, surfaceNames = prepareGeometry(gridSize, distFromFloor, removeInt, hb_zoneData)
    
    #Unpack the data trees of test pts and mesh breps so that the user can see them and get a sense of what to expect from the view factor calculation.
    testPts = DataTree[Object]()
    viewFactorMesh = DataTree[Object]()
    zoneSrfNames = DataTree[Object]()
    for brCount, branch in enumerate(testPtsInit):
        for item in branch:testPts.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(viewFactorBrep):
        for item in branch: viewFactorMesh.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(surfaceNames):
        for item in branch: zoneSrfNames.Add(item, GH_Path(brCount))

#If all of the data is good and the user has set "_runIt" to "True", run the shade benefit calculation to generate all results.
if checkData == True and _runIt == True and geoCheck == True:
    viewVectors = checkViewResolution(viewResolution, lb_preparation)
    testPtViewFactorInit = main(testPtsInit, zoneSrfsMesh, viewVectors)
    
    #Unpack the data trees of meshes and view factors.
    testPtViewFactor = DataTree[Object]()
    viewFactorMesh = DataTree[Object]()
    for brCount, branch in enumerate(viewFactorMeshActual):
        for item in branch: viewFactorMesh.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(testPtViewFactorInit):
        for listCount, list in enumerate(branch):
            for item in list: testPtViewFactor.Add(item, GH_Path(brCount, listCount))

