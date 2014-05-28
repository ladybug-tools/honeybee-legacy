# By Chris Mackey
# Chris@MackeyArchitecture.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Divide up a building mass into smaller smaller geometries that correspond to recommended zones.
-
Provided by Honeybee 0.0.53

    Args:
        _bldgMasses: A Closed brep representing a building or a list of closed Breps.
        bldgsFlr2FlrHeights_: A floor height in Rhino model units or list of building floor heights for the geometries.
        perimeterZoneDepth_: A perimeter zone dpeth in Rhino model units or list of bperimeter depths for the geometries.
        _createHoneybeeZones: Set Boolean to True to split up the building mass into zones.
    Returns:
        readMe!: ...
        _splitBldgMasses: A lot of breps that correspond to the recommended means of breaking up geometry into zones for energy simulations.
"""


ghenv.Component.Name = 'Honeybee_SplitBuildingMass'
ghenv.Component.NickName = 'SplitMass'
ghenv.Component.Message = 'VER 0.0.53\nMAY_28_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


tolerance = sc.doc.ModelAbsoluteTolerance

def checkTheInputs():
    if len(_bldgMasses) != 0:
        brepSolid = []
        for brep in _bldgMasses:
            if brep.IsSolid == True:
                brepSolid.append(1)
            else:
                warning = "Building masses must be closed solids!"
                print warning
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        if sum(brepSolid) == len(_bldgMasses):
            checkData1 = True
    else: print "Connect closed solid building masses to split them up into zones."
    
    if bldgsFlr2FloorHeights_ == []:
        print "No value is connected for floor heights and so the model will not be divided up into floors"
    else: pass
    
    if perimeterZoneDepth_ == []:
        print "No value is connected for zone depth and so the model will not be divided up into perimeter and core zones."
    else: pass
    
    if bldgsFlr2FloorHeights_ != [] or perimeterZoneDepth_ != []:
        checkData2 = True
    else:
        checkData2 = False
        print "A value must be conneted for either Flr2FloorHeights_ or perimeterZoneDepth_ in order to run."
    
    if checkData1 == True and checkData2 == True:
        checkData = True
    else: checkData = False
    
    return checkData


def getFloorHeights(flr2flrHeights, totalHeights, maxHeights, conversionFac = 1, firstFloorHeight = 0, rep = False):
    flrHeights = [firstFloorHeight]
    for height in flr2flrHeights:
        if '@' in height:
            floorH = float(height.split('@')[1])
            try: numOfFlr = int(height.split('@')[0])
            except:  numOfFlr = int((totalHeights - flrHeights[-1])/floorH)
        else:
            numOfFlr = 1
            floorH = float(height)
        if floorH!=0:
            if numOfFlr != 1 and rep:
                print 'There are ' + `numOfFlr` + ' floors with height of ' + `floorH` + ' m.'
            elif rep:
                print 'There is a floor with height of ' + `floorH` + ' m.'
            
            for floors in range(numOfFlr): flrHeights.append(flrHeights[-1] + floorH)
    
    #if maxHeights - flrHeights[-1] < (0.5/conversionFac): flrHeights.pop()
    return flrHeights # list of floor heights

def getFloorCrvs(buildingMass, floorHeights, maxHeights):
    #Draw a bounding box around the mass and use the lowest Z point to set the base point.
    massBB = buildingMass.GetBoundingBox(rc.Geometry.Plane.WorldXY)
    minZ = massBB.Min.Z
    
    basePoint = rc.Geometry.Point3d.Origin
    contourCrvs = []; splitters = []
    bbox = buildingMass.GetBoundingBox(True)
    for h in floorHeights:
        floorBasePt = rc.Geometry.Point3d.Add(basePoint, rc.Geometry.Vector3d(0,0,h + minZ))
        sectionPlane = rc.Geometry.Plane(floorBasePt, rc.Geometry.Vector3d.ZAxis)
        crvList = rc.Geometry.Brep.CreateContourCurves(buildingMass, sectionPlane)
        
        if crvList:
            [contourCrvs.append(crv) for crv in crvList]
            
            # This part is based on one of David Rutten's script
            bool, extU, extV = sectionPlane.ExtendThroughBox(bbox)
            # extend the plane for good measure
            extU.T0 -= 1.0
            extU.T1 += 1.0
            extV.T0 -= 1.0
            extV.T1 += 1.0
            splitters.append(rc.Geometry.PlaneSurface(sectionPlane, extU, extV))
    
    #Check if any of the generated curves have no area and, fi so, discount them from the list.
    newContourCrvs = []
    for crv in contourCrvs:
        if crv.SegmentCount == 2:
            segments = crv.DuplicateSegments()
            if segments[0].IsLinear and segments[0].IsLinear:
                pass
            else: newContourCrvs.append(crv)
        else: newContourCrvs.append(crv)
    contourCrvs = newContourCrvs
    
    #Check to see if the top floor is shorter than 2 meters and, if so, discount it.
    units = sc.doc.ModelUnitSystem
    
    #Define a default max height for a floor based on the model units and typical building dimensions.
    if `units` == 'Rhino.UnitSystem.Meters':
        maxHeight = 2
    elif `units` == 'Rhino.UnitSystem.Centimeters':
        maxHeight = 200
    elif `units` == 'Rhino.UnitSystem.Millimeters':
        maxHeight = 2000
    elif `units` == 'Rhino.UnitSystem.Feet':
        maxHeight = 6
    elif `units` == 'Rhino.UnitSystem.Inches':
        maxHeight = 72
    else:
        warning = "What model units are you using? Use either meters, centimeters, millimeters, feet or inches"
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    lastFloorHeight = (maxHeights - minZ)  - floorHeights[-1]
    if lastFloorHeight < maxHeight:
        lastFloorInc = False
    else: lastFloorInc = True
    
    #Check to see if the top surface is horizontal + planar and, if so, include it in the curve process below.
    if lastFloorInc == True:
        #First find the top surface
        massSurfaces = []
        for surface in buildingMass.Surfaces:
            massSurfaces.append(surface.ToBrep())
        srfAvgZValue = []
        for brep in massSurfaces:
            vertices = brep.DuplicateVertices()
            zValues = []
            for vertex in vertices:
                zValues.append(vertex.Z)
            zAvg = (sum(zValues))/(len(zValues))
            srfAvgZValue.append(zAvg)
        maxIndex = max(enumerate(srfAvgZValue),key=lambda x: x[1])[0]
        topSurface = massSurfaces[maxIndex]
        #Check the Z-Values of the vertices to see if they are equal and check for planarity
        topZValues = []
        for vertex in topSurface.DuplicateVertices():
            topZValues.append(vertex.Z)
        refZ = topZValues[0]
        zCheckList = []
        for Z in topZValues:
            if Z < refZ + tolerance and Z > refZ - tolerance:
                zCheckList.append(1)
            else:pass
        if sum(zCheckList) == len(topZValues): tophoriz = True
        else: tophoriz = False
        topPlanar = topSurface.Surfaces[0].IsPlanar()
        #If it's both horizontal and planar, take the boundary curve and include it in the rest of the process.
        if tophoriz == True and topPlanar == True:
            topInc = True
            edgeCurves = rc.Geometry.Curve.JoinCurves(topSurface.DuplicateEdgeCurves())
            edgeLen = len(edgeCurves)
            for curve in edgeCurves:
                contourCrvs.append(curve)
        else:
            topInc = False
    else:
        if lastFloorHeight < maxHeight:
            topInc = True
        else: topInc = False
    
    #Simplify the contour curves to ensure that they do not mess up the next few steps.
    for curve in contourCrvs:
        curve.Simplify(rc.Geometry.CurveSimplifyOptions.All, tolerance, sc.doc.ModelAngleToleranceRadians)
    
    # Match the curve directions.
    if len(contourCrvs)!= 0:
        refCrv = contourCrvs[0]
        crvDir = []
        for crv in contourCrvs:
            crvDir.append(rc.Geometry.Curve.DoDirectionsMatch(refCrv, crv))
        for count, dir in enumerate(crvDir):
            if dir == True:
                contourCrvs[count].Reverse()
    
    #Match the curve seams in order to ensure proper zone splitting later.
    if len(contourCrvs)!= 0:
        crvCentPt = rc.Geometry.AreaMassProperties.Compute(contourCrvs[0]).Centroid
        # get a point from the center of the contour curve to a seam in order to adjust the seam of all other curves.
        curveLengths = []
        for curve in contourCrvs:
            curveLengths.append(curve.GetLength())
        curveLengths.sort()
        longestCurveLength = curveLengths[-1]
        factor = ((longestCurveLength)/(contourCrvs[0].PointAtStart.X - crvCentPt.X))*2
        seamVectorPt = rc.Geometry.Vector3d((contourCrvs[0].PointAtStart.X - crvCentPt.X)*factor, (contourCrvs[0].PointAtStart.Y - crvCentPt.Y)*factor, 0)
        # adjust the seam of the curves.
        crvAdjust = []
        for curve in contourCrvs:
            curveParameter = curve.ClosestPoint(rc.Geometry.Intersect.Intersection.CurveCurve(curve, rc.Geometry.Line(rc.Geometry.AreaMassProperties.Compute(curve).Centroid, seamVectorPt).ToNurbsCurve(), sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAbsoluteTolerance)[0].PointA)[1]
            curveParameterRound = round(curveParameter)
            curveParameterTol = round(curveParameter, (len(list(str(sc.doc.ModelAbsoluteTolerance)))-2))
            if curveParameterRound + sc.doc.ModelAbsoluteTolerance > curveParameter and curveParameterRound - sc.doc.ModelAbsoluteTolerance < curveParameter:
                curve.ChangeClosedCurveSeam(curveParameterRound)
                crvAdjust.append(curve)
            else:
                curve.ChangeClosedCurveSeam(curveParameter)
                if curve.IsClosed == True:
                    crvAdjust.append(curve)
                else:
                    curve.ChangeClosedCurveSeam(curveParameter+sc.doc.ModelAbsoluteTolerance)
                    if curve.IsClosed == True:
                        crvAdjust.append(curve)
                    else:
                        curve.ChangeClosedCurveSeam(curveParameter-sc.doc.ModelAbsoluteTolerance)
                        if curve.IsClosed == True:
                            crvAdjust.append(curve)
                        else:
                            curve.ChangeClosedCurveSeam(curveParameter)
                            curve.MakeClosed(sc.doc.ModelAbsoluteTolerance)
                            crvAdjust.append(curve)
    
    #If the top surface curve has been included in the analysis above, remove it from one of the returned lists so that it doesn't mess up the floor splitting algorithm.
    if topInc == True and lastFloorInc == True:
        contourCrvs = crvAdjust[:(len(crvAdjust)-edgeLen)]
    else: contourCrvs = crvAdjust
    
    
    return contourCrvs, splitters, crvAdjust, topInc



def splitFloorHeights(bldgMasses, bldgsFlr2FlrHeights, lb_preparation, lb_visualization):
    if len(bldgMasses)!=0:
        # clean the geometries 
        analysisMesh, initialMasses = lb_preparation.cleanAndCoerceList(bldgMasses)
        
        conversionFac = lb_preparation.checkUnits()
        
        splitZones = []
        floorCurves = []
        topIncluded = []
        for bldgCount, mass in enumerate(initialMasses):
            
            # 0- split the mass vertically [well, it is actually horizontally! so confusing...]
            # 0-1 find the boundingBox
            lb_visualization.calculateBB([mass])
            
            # SPLIT MASS TO FLOORS
            # 0-2 get floor curves and split surfaces based on floor heights
            # I don't use floor curves here. It is originally developed for upload Rhino2Web
            maxHeights = lb_visualization.BoundingBoxPar[-1].Z
            bldgHeights = lb_visualization.BoundingBoxPar[-1].Z - lb_visualization.BoundingBoxPar[0].Z
            floorHeights = getFloorHeights(bldgsFlr2FlrHeights, bldgHeights, maxHeights, conversionFac)
            
            if floorHeights!=[0]:
                floorCrvs, splitterSrfs, crvAdjust, topInc = getFloorCrvs(mass, floorHeights, maxHeights)
                
                floorCurves.append(crvAdjust)
                topIncluded.append(topInc)
                
                # well, I'm pretty sure that something like this is smarter to be written
                # as a recursive fuction but I'm not comfortable enough to write it that way
                # right now. Should be fixed later!
                restOfmass = mass
                massZones = []
                for srfCount, srf in enumerate(splitterSrfs):
                    lastPiece = []
                    lastPiece.append(restOfmass)
                    pieces = restOfmass.Split(srf.ToBrep(), tolerance)
                    
                    if len(pieces)== 2 and lb_visualization.calculateBB([pieces[0]], True)[-1].Z < lb_visualization.calculateBB([pieces[1]], True)[-1].Z:
                        try: 
                            zone = pieces[0].CapPlanarHoles(tolerance);
                            if zone!=None:
                                massZones.append(zone)
                            restOfmass = pieces[1].CapPlanarHoles(tolerance)
                        except Exception, e:
                            print 'error 1: ' + `e`

                    #elif len(pieces)== 2:
                    #    massZones.append(pieces[1].CapPlanarHoles(tolerance))
                    #    restOfmass = pieces[0].CapPlanarHoles(tolerance)
                    #    try:
                    #        zone = pieces[1].CapPlanarHoles(tolerance)
                    #        if zone!=None:
                    #            massZones.append(zone)
                    #        restOfmass = pieces[0].CapPlanarHoles(tolerance)
                    #    except Exception, e:
                    #        print 'error 2: ' + `e`
                    else:
                        if srfCount == len(splitterSrfs) - 1:
                            pass
                        else:
                            msg = 'One of the masses is causing a problem. Check HBZones output for the mass that causes the problem.'
                            print msg
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return [restOfmass, -1]
                if restOfmass != None:
                    massZones.append(restOfmass)
                else: pass
                
                splitZones.append(massZones)
        
        return splitZones, floorCurves, topIncluded


def splitPerimZones(mass, zoneDepth, floorCrvs, topInc):
    #Define a function that will extract the points from a polycurve line
    def getCurvePoints(curve):
        exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
        individPts = []
        for line in exploCurve:
            individPts.append(line.PointAtStart)
        return individPts
    
    #Define a function that cleans up curves by deleting out points that lie in a line and leaves the curved segments intact.
    def cleanCurve(curve, curvePts):
        #First check if there are any curved segements and make a list to keep track of this
        curveBool = []
        exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
        for segment in exploCurve:
            if segment.IsLinear == False: curveBool.append(True)
            else: curveBool.append(False)
        
        #Test if any of the points lie in a line and use this to generate a new list of curve segments and points.
        newPts = []
        newSegments = []
        for pointCount, point in enumerate(curvePts):
            testLine = rc.Geometry.Line(point, curvePts[pointCount-2])
            if testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and curveBool[pointCount-1] == False and len(newPts) == 0:
                newPts.append(curvePts[pointCount-1])
            elif testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and curveBool[pointCount-1] == False and len(newPts) != 0:
                newSegments.append(rc.Geometry.LineCurve(newPts[-1], curvePts[pointCount-1]))
                newPts.append(curvePts[pointCount-1])
            elif curveBool[pointCount-1] == True:
                newPts.append(curvePts[pointCount-1])
                newSegments.append(exploCurve[pointCount-1])
            else: pass
        
        #Add a segment to close the curves and join them together into one polycurve.
        if curveBool[-1] == True:
            newSegments.append(exploCurve[-1])
        else:
            newSegments.append(rc.Geometry.LineCurve(newPts[-1], newPts[0]))
        
        #Shift the lists over by 1 to ensure that the order of the points and curves match the input
        newCurvePts = newPts[1:]
        newCurvePts.append(newPts[0])
        newCurveSegments = newSegments[1:]
        newCurveSegments.append(newSegments[0])
        
        
        #Join the segments together into one curve.
        newCrv = rc.Geometry.PolyCurve.JoinCurves(newCurveSegments, tolerance, True)[0]
        
        #return the new curve and the list of points associated with it.
        return newCrv, newCurvePts, newCurveSegments
    
    #Get a list of cuves that represent the ceiling (without the top floor). Generate a list of points for each and a brep for the ceiling surface.
    ceilingCrv = floorCrvs[1:]
    ceilingPts = []
    for curveCount, curve in enumerate(ceilingCrv):
        ceilingPts.append(getCurvePoints(curve))
    
    #Get a list of curves that represent the floors (without the top floor). Generate a list of points for each and a brep for the ceiling surface.
    floorCrv = floorCrvs[:-1]
    floorPts = []
    for curveCount, curve in enumerate(floorCrv):
        floorPts.append(getCurvePoints(curve))
    
    #Clean up the input curves, This involves testing to see if any 3 points on the floor or ceiling curves lie in a line and, if so, deleting out the redundant mid point.
    newFloorCrv = []
    newFloorPts = []
    for count, curve in enumerate(floorCrv):
        newFCrv, newFCrvPts, newFCrvSeg = cleanCurve(curve, floorPts[count])
        newFloorCrv.append(newFCrv)
        newFloorPts.append(newFCrvPts)
    floorCrv = newFloorCrv
    floorPts = newFloorPts
    
    newCeilingCrv = []
    newCeilingPts = []
    for count, curve in enumerate(ceilingCrv):
        newCCrv, newCCrvPts, newCCrvSeg  = cleanCurve(curve, ceilingPts[count])
        newCeilingCrv.append(newCCrv)
        newCeilingPts.append(newCCrvPts)
    ceilingCrv = newCeilingCrv
    ceilingPts = newCeilingPts
    
    #Find the offset depth for each of the floors.
    numOfFlr = len(floorCrv)
    flrDepths = []
    for depth in zoneDepth:
        if '@' in depth:
            zoneD = float(depth.split('@')[1])
            try: numFlr = int(depth.split('@')[0])
            except: numFlr = numOfFlr
            for floors in range(numFlr): flrDepths.append(zoneD)
        else:
            zoneD = float(depth)
            flrDepths.append(zoneD)
    
    #Offset the curve for each floor and get the points for those offsets
    finalZones = []
    for curveCount, curve in enumerate(floorCrv):
        try:
            offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
            if str(offsetFloorCrv.Contains(floorPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
            else: pass
            offsetFloorPts = getCurvePoints(offsetFloorCrv)
            
            offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
            if str(offsetCeilingCrv.Contains(ceilingPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
            else: pass
            offsetCeilingPts = getCurvePoints(offsetCeilingCrv)
            
            #Clean up the offset curves, This involves testing to see if any 3 points on the floor or ceiling curves lie in a line and, if so, deleting out the redundant mid point.
            offsetFloorCrv, offsetFloorPts, offsetFloorCrvSegments = cleanCurve(offsetFloorCrv, offsetFloorPts)
            offsetCeilingCrv, offsetCeilingPts, offsetCeilingCrvSegments = cleanCurve(offsetCeilingCrv, offsetCeilingPts)
            
            #Test to see which points on the inside are closest to those on the outside.
            floorConnectionPts = []
            for point in offsetFloorPts:
                pointDist = []
                floorEdgePts = floorPts[curveCount][:]
                for perimPoint in floorEdgePts:
                    pointDist.append(rc.Geometry.Point3d.DistanceTo(point, perimPoint))
                sortDist = [x for (y,x) in sorted(zip(pointDist, floorEdgePts))]
                floorConnectionPts.append(sortDist[0])
            
            ceilingConnectionPts = []
            for point in offsetCeilingPts:
                pointDist = []
                ceilingEdgePts = ceilingPts[curveCount][:]
                for perimPoint in ceilingEdgePts:
                    pointDist.append(rc.Geometry.Point3d.DistanceTo(point, perimPoint))
                sortDist = [x for (y,x) in sorted(zip(pointDist, ceilingEdgePts))]
                ceilingConnectionPts.append(sortDist[0])
            
            #Create lines from the collected points of the offset curves in order to split up the different perimeter zones.
            zoneFloorCurves = []
            for pointCount, point in enumerate(offsetFloorPts):
                floorZoneCurve = rc.Geometry.LineCurve(point, floorConnectionPts[pointCount])
                zoneFloorCurves.append(floorZoneCurve)
            
            zoneCeilingCurves = []
            for pointCount, point in enumerate(offsetCeilingPts):
                ceilingCurves = rc.Geometry.LineCurve(point, ceilingConnectionPts[pointCount])
                zoneCeilingCurves.append(ceilingCurves)
            
            #Loft the floor and ceiling curves together in order to get walls
            perimZoneWalls = []
            for lineCount, line in enumerate(zoneFloorCurves):
                floorWall = rc.Geometry.Brep.CreateFromLoft([line, zoneCeilingCurves[lineCount]], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
                perimZoneWalls.append(floorWall)
            
            coreZoneWalls = []
            exploFloorCrv = rc.Geometry.PolyCurve.DuplicateSegments(offsetFloorCrv)
            exploCeilingCrv = rc.Geometry.PolyCurve.DuplicateSegments(offsetCeilingCrv)
            for lineCount, line in enumerate(exploFloorCrv):
                floorCoreWall = rc.Geometry.Brep.CreateFromLoft([line, exploCeilingCrv[lineCount]], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
                coreZoneWalls.append(floorCoreWall)
            
            #Loft the exterior curves to get a list that matches all of the other generated data.
            exteriorWalls = []
            exploFloorCrv = rc.Geometry.PolyCurve.DuplicateSegments(floorCrv[curveCount])
            exploCeilingCrv = rc.Geometry.PolyCurve.DuplicateSegments(ceilingCrv[curveCount])
            for lineCount, line in enumerate(exploFloorCrv):
                floorExtWall = rc.Geometry.Brep.CreateFromLoft([line, exploCeilingCrv[lineCount]], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
                exteriorWalls.append(floorExtWall)
            
            #Join the walls together to make zones.
            joinedWalls = rc.Geometry.Brep.JoinBreps(coreZoneWalls, tolerance)[0]
            coreZone = joinedWalls.CapPlanarHoles(tolerance)
            perimZones = []
            for wallCount, wall in enumerate(perimZoneWalls):
                brepList = [wall, perimZoneWalls[wallCount-1], exteriorWalls[wallCount-1], coreZoneWalls[wallCount-1]]
                joinedWalls = rc.Geometry.Brep.JoinBreps(brepList, tolerance)[0]
                cappedZone = joinedWalls.CapPlanarHoles(tolerance)
                perimZones.append(cappedZone)
            
            #Group the walls together by floor.
            floorZones = []
            floorZones.append(coreZone)
            floorZones.extend(perimZones)
            
            #Test to see if all of the generated zones are null and, if so, return the full floor mass.
            noneTest = []
            for zone in floorZones:
                if zone == None:
                    noneTest.append(1)
                else: pass
            
            
            #Append the group to the full zone list.
            if sum(noneTest) == len(floorZones):
                finalZones.append(mass[curveCount])
                print "Failed to generate the perimieter zones for one floor.  The problematic floor will be returned as a single zone.  If perimeter zones are desired, try decreasing the perimeter depth."
            else:
                finalZones.append(floorZones)
        except:
            finalZones.append(mass[curveCount])
            print "Failed to generate the perimieter zones for one floor.  The problematic floor will be returned as a single zone.  If perimeter zones are desired, try decreasing the perimeter depth."
    
    #If the top floor has not been included in the analysis above, append on the top floor mass.
    if topInc == False:
        finalZones.append([mass[-1]])
    else: pass
    
    return finalZones



def main(mass, floorHeights, perimDepth):
    #Import the Ladybug Classes.
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #If the user has specified a floor height, split the mass up by floor.
        if floorHeights != []:
            splitFloors, floorCrvs, topInc = splitFloorHeights(mass, floorHeights, lb_preparation, lb_visualization)
        else:
            splitFloors = mass
            floorCrvs = []
            topInc = []
            for item in mass:
                bbBox = item.GetBoundingBox(rc.Geometry.Plane.WorldXY)
                maxHeights = bbBox.Max.Z
                minHeights = bbBox.Min.Z
                contCrvs, splitters, flrCrvs, topIncl = getFloorCrvs(item, [0, maxHeights-minHeights], maxHeights)
                floorCrvs.append(flrCrvs)
                topInc.append(True)
        
        #If the user had specified a perimeter zone depth, offset the floor curves to get perimeter and core.
        if perimeterZoneDepth_ != []:
            splitZones = []
            for count, mass in enumerate(splitFloors):
                splitZones.append(splitPerimZones(mass, perimDepth, floorCrvs[count], topInc[count]))
        else: splitZones = splitFloors
        
        return splitZones
        
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1



checkData = False
if _runIt == True:
    checkData = checkTheInputs()
if checkData == True:
    splitBldgMassesLists = main(_bldgMasses, bldgsFlr2FloorHeights_, perimeterZoneDepth_)
    
    splitBldgMasses = DataTree[Object]()
    for i, buildingMasses in enumerate(splitBldgMassesLists):
        for j, mass in enumerate(buildingMasses):
            p = GH_Path(i,j)
            try: splitBldgMasses.AddRange(mass, p)
            except: splitBldgMasses.Add(mass, p)