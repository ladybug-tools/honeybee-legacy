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
Use this component to divide up a brep (polysurface) representative of a complete building massing into smaller volumes that roughly correspond to how a generic EnergyPlus model should be zoned.
This generic zoning will divide the input mass into seprate floors based on an input floor height.
This zoning can also divide up each floor into a core and perimeter zones, which helps account for the different microclimates you would get on each of the different orientations of a building.
_
If you have a single mass representing two towers off of a podium, the two towers are not a continuous mass and you should therefore send each tower and the podium in as a separate Brep into this component.  The component will work for courtyard buildings.
Core and perimeter zoneing should work for almost all masses where all walls are planar.  It works in a limited number of cases that have both curved and planar walls.  Also, it is important to note that, if your offset depth is so large in comparison to your building depth as to create perimeter zones that intersect one another, the whole floor will be returned as a single zone.
While this component can usually get you the most of the way there, it is still recommended that you bake the output and check the geometry in Rhino before turning the breps into HBZones.
_
The assumption about an E+ zone is that the air is well mixed and all at the same temperature.
Therefore, it is usually customary to break up a building depending on the areas where you would expect different building microclimates to exist.
This includes breaking up the building into floors (since each floor can have a different microclimate) and breanking up each floor into a core zone and perimeter zones (since each side of the buidling gets a different amount of solar gains and losses/gains through the envelope).
This component helps break up building masses in such a manner.
-
Provided by Honeybee 0.0.60

    Args:
        _bldgMasses: A Closed brep or list of closed breps representing a building massing.
        bldgsFlr2FloorHeights_: A list of floor heights in Rhino model units that will be used to make each floor of the building.  The list should run from bottom floor to top floor.  Alternatively, you can input a text string that codes for how many floors of each height you want.  For example, inputting "2@4" (without quotations) will make two ground floors with a height of 4 Rhino model units.  Simply typing "@3" will make all floors 3 Rhino model units.  Putting in lists of these text strings will divide up floors accordingly.  For example, the list "1@5   2@4   @3"  will make a ground floor of 5 units, two floors above that at 4 units and all remaining floors at 3 units.
        perimeterZoneDepth_: A list of perimeter zone depths in Rhino model units that will be used to divide up each floor of the building into core and perimeter zones.  The list should run from bottom floor to top floor.  Alternatively, you can input a text string that codes for which floors you want at which zone depth.  For example, inputting "2@4" (without quotations) will divide up the two ground floors with a perimeter zone depth of 4 Rhino model units.  Simply typing "@3" will divide up all floors with a zone depth of 3 Rhino model units.  Putting in lists of these text strings will divide up floors accordingly.  For example, the list "1@5   2@4   @3"  will make a ground floor divided up with a zone depth of 5 units, two floors divided at 4 units and all remaining floors at 3 units.
        _createHoneybeeZones: Set Boolean to "True" to split up the building mass into geometries for zones.
    Returns:
        readMe!: ...
        _splitBldgMasses: A series of breps that correspond to the recommended means of breaking up building geometry into zones for energy simulations.  Results are grafted based on floor and building mass (if multiple masses are input).  If a floor fails to generate core and perimeter zones, the floor is returned as a single brep.
"""


ghenv.Component.Name = 'Honeybee_SplitBuildingMass'
ghenv.Component.NickName = 'SplitMass'
ghenv.Component.Message = 'VER 0.0.60\nNOV_18_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import rhinoscriptsyntax as rs


tolerance = sc.doc.ModelAbsoluteTolerance

def checkTheInputs():
    if len(_bldgMasses) != 0 and _bldgMasses[0]!=None :
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
    else:
        checkData1 = False
        print "Connect closed solid building masses to split them up into zones."
    
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


def getFloorHeights(flr2flrHeights, maxHeights, firstFloorHeight = 0, rep = True):
    flrHeights = [firstFloorHeight]
    for height in flr2flrHeights:
        if '@' in height:
            floorH = float(height.split('@')[1])
            try: numOfFlr = int(height.split('@')[0])
            except:  numOfFlr = int((maxHeights - flrHeights[-1])/floorH)
        else:
            numOfFlr = 1
            floorH = float(height)
        if floorH!=0:
            if numOfFlr != 1 and rep:
                print 'There are ' + `numOfFlr` + ' floors with height of ' + `floorH` + ' m.'
            elif rep:
                print 'There is a floor with height of ' + `floorH` + ' m.'
            
            for floors in range(numOfFlr): flrHeights.append(flrHeights[-1] + floorH)
    
    return flrHeights # list of floor heights

def getFloorCrvs(buildingMass, floorHeights, maxHeights):
    #Draw a bounding box around the mass and use the lowest Z point to set the base point.
    massBB = buildingMass.GetBoundingBox(rc.Geometry.Plane.WorldXY)
    minZ = massBB.Min.Z
    
    basePoint = rc.Geometry.Point3d.Origin
    cntrCrvs = []; splitters = []
    bbox = buildingMass.GetBoundingBox(True)
    for count, h in enumerate(floorHeights):
        crvList = []
        floorBasePt = rc.Geometry.Point3d.Add(basePoint, rc.Geometry.Vector3d(0,0,h + minZ))
        sectionPlane = rc.Geometry.Plane(floorBasePt, rc.Geometry.Vector3d.ZAxis)
        crvList = rc.Geometry.Brep.CreateContourCurves(buildingMass, sectionPlane)
        
        #If the crvList cointains multiple curves, this probably means that it's a courtyard building.  Order the curves from greatest area to least area and create different lists of curves for the interior and exterior.
        if len(crvList) > 1 and count == 0:
            areaList = []
            for curve in crvList:
                try: areaList.append(rc.Geometry.AreaMassProperties.Compute(curve).Area)
                except: areaList.append(0.0)
            crvList = [x for (y,x) in sorted(zip(areaList, crvList))]
            crvList.reverse()
            for curve in crvList:
                cntrCrvs.append([curve])
        elif len(crvList) > 1 and count != 0:
            areaList = []
            for curve in crvList:
                try: areaList.append(rc.Geometry.AreaMassProperties.Compute(curve).Area)
                except: areaList.append(0.0)
            crvList = [x for (y,x) in sorted(zip(areaList, crvList))]
            crvList.reverse()
            for crvCount, curve in enumerate(crvList):
                try: cntrCrvs[crvCount].append(curve)
                except: pass
        elif len(crvList) == 1 and count == 0:
            cntrCrvs.append([crvList[0]])
        elif len(crvList) == 1 and count != 0:
            try: cntrCrvs[0].append(crvList[0])
            except: cntrCrvs.append([crvList[0]])
        else: pass
        
        if crvList != []:
            # This part is based on one of David Rutten's script
            bool, extU, extV = sectionPlane.ExtendThroughBox(bbox)
            # extend the plane for good measure
            extU.T0 -= 1.0
            extU.T1 += 1.0
            extV.T0 -= 1.0
            extV.T1 += 1.0
            splitters.append(rc.Geometry.PlaneSurface(sectionPlane, extU, extV))
    
    finalCrvsList = []
    finaltopIncList = []
    finalNurbsList = []
    
    for courtyrdCount, contourCrvs in enumerate(cntrCrvs):
        
        #Check if the operation has generated a single nurbs curve for a floor (like a circle) and, if so, segment it.
        goodContourCrvs = []
        nurbsList = []
        for curve in contourCrvs:
            try:
                segCount = curve.SegmentCount
                goodContourCrvs.append(curve)
                nurbsList.append(False)
            except:
                #If the curve has failed the operation above, then it is a single NURBS Curve.  Test to see if offsetting it will generate segments and, if not, it should be segemented into a polycurve.
                curveLength = curve.GetLength()
                divisionParams = curve.DivideByLength((curveLength/4), False)[0:3]
                splitCurve = curve.Split(divisionParams)
                newCrv = rc.Geometry.PolyCurve()
                for segment in splitCurve:
                    newCrv.Append(segment)
                goodContourCrvs.append(newCrv)
                nurbsList.append(True)
        contourCrvs = goodContourCrvs
        
        #Check if any of the generated curves have no area and, if so, discount them from the list. Make a note if the curves are at the top, which happens a lot with gabled roofs.  This can be corrected later.
        newContourCrvs = []
        problemIndices = []
        problem = False
        for crvCount, crv in enumerate(contourCrvs):
            if crv.SegmentCount == 2:
                segments = crv.DuplicateSegments()
                if segments[0].IsLinear and segments[1].IsLinear:
                    problem = True
                    problemIndices.append(crvCount)
                else: newContourCrvs.append(crv)
            else: newContourCrvs.append(crv)
        if problem == True:
            if problemIndices[-1] == len(contourCrvs)-1: topProblem = True
            else: topProblem = False
        else: topProblem = False
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
        
        lastFloorHeight = (maxHeights)  - floorHeights[-1]
        
        if is_near_zero(lastFloorHeight): 
            lastFloorInc = True
        else:
            if lastFloorHeight < maxHeight:
                lastFloorInc = False
            else: lastFloorInc = True
        
        #Check to see if the top surface is horizontal + planar and, if so, include it in the curve process below.
        if lastFloorInc == True:
            #First find the top surface
            massSurfaces = []
            faceLen = buildingMass.Faces.Count
            for surfaceCount in range(faceLen):
                massSurfaces.append(buildingMass.DuplicateSubBrep([surfaceCount]))
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
                #If the building is a courtyard one, select out the curve with the same area order.
                if len(edgeCurves) > 1:
                    areaList = []
                    for curve in edgeCurves:
                        try: areaList.append(rc.Geometry.AreaMassProperties.Compute(curve).Area)
                        except: areaList.append(0.0)
                    edgeCurvesSorted = [x for (y,x) in sorted(zip(areaList, edgeCurves))]
                    edgeCurves = [edgeCurvesSorted[courtyrdCount]]
                else: pass
                
                isNurbCurve = []
                for count, curve in enumerate(edgeCurves):
                    try:
                        segCount = edgeCurves.SegmentCount
                        isNurbCurve.append(False)
                    except:
                        isNurbCurve.append(True)
                        curveLength = curve.GetLength()
                        divisionParams = curve.DivideByLength((curveLength/4), False)[0:3]
                        splitCurve = curve.Split(divisionParams)
                        newCrv = rc.Geometry.PolyCurve()
                        for segment in splitCurve:
                            newCrv.Append(segment)
                        edgeCurves[count] = newCrv
                    for curve in edgeCurves:
                        contourCrvs.append(curve)
                    for bool in isNurbCurve:
                        nurbsList.append(bool)
            else:
                topInc = False
        else:
            if lastFloorHeight < maxHeight:
                topInc = True
            else: topInc = False
        
        if topProblem == True:
            topInc = False
        else: pass
        
        # Match the curve directions.
        if len(contourCrvs)!= 0:
            refCrv = contourCrvs[0]
            crvDir = []
            for crv in contourCrvs:
                crvDir.append(rc.Geometry.Curve.DoDirectionsMatch(refCrv, crv))
            for count, dir in enumerate(crvDir):
                if dir == True:
                    contourCrvs[count].Reverse()
        
        #Check if there are any curved segments in the polycurve and if so, make a note of it
        curveSegmentList = []
        for curve in contourCrvs:
            curved = False
            for segment in curve.DuplicateSegments():
                if segment.IsLinear(): pass
                else: curved = True
            curveSegmentList.append(curved)
        
        
        #Match the curve seams in order to ensure proper zone splitting later.
        if len(contourCrvs)!= 0:
            crvCentPt = rc.Geometry.AreaMassProperties.Compute(contourCrvs[-1]).Centroid
            # get a point from the center of the contour curve to a seam in order to adjust the seam of all other curves.
            curveLengths = []
            for curve in contourCrvs:
                curveLengths.append(curve.GetLength())
            curveLengths.sort()
            longestCurveLength = curveLengths[-1]
            factor = ((longestCurveLength)/(contourCrvs[-1].PointAtStart.X - crvCentPt.X))*2
            seamVectorPt = rc.Geometry.Vector3d((contourCrvs[-1].PointAtStart.X - crvCentPt.X)*factor, (contourCrvs[-1].PointAtStart.Y - crvCentPt.Y)*factor, 0)
            
            # Try to adjust the seam of the curves.
            crvAdjust = []
            try:
                for nurbCount, curve in enumerate(contourCrvs):
                    if curve.IsClosed:
                        if nurbsList[nurbCount] == False and curveSegmentList[nurbCount] == False:
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
                        else:
                            crvAdjust.append(curve)
                    else:
                        crvAdjust.append(curve)
                        warning = 'The top or bottom of your mass geometry is composed of multiple surfaces and this is causing the algorithm to mess up.\n  If you re-make your top and/or bottom of your mass to be a single surface, this component should work.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except: crvAdjust = contourCrvs
        
        #Simplify the contour curves to ensure that they do not mess up the next few steps.
        for curve in crvAdjust:
            curve.Simplify(rc.Geometry.CurveSimplifyOptions.All, tolerance, sc.doc.ModelAngleToleranceRadians)
        
        #Append the results to the list.
        finalCrvsList.append(crvAdjust)
        finaltopIncList.append(topInc)
        finalNurbsList.append(nurbsList)
    
    return splitters, finalCrvsList, finaltopIncList, finalNurbsList, lastFloorInc



def splitFloorHeights(bldgMasses, bldgsFlr2FlrHeights, lb_preparation, lb_visualization):
    if len(bldgMasses)!=0:
        # clean the geometries 
        analysisMesh, initialMasses = lb_preparation.cleanAndCoerceList(bldgMasses)
        
        splitZones = []
        floorCurves = []
        topIncluded = []
        nurbsCurveList = []
        lastFloorInclud = []
        for bldgCount, mass in enumerate(initialMasses):
            
            # 0- split the mass vertically [well, it is actually horizontally! so confusing...]
            # 0-1 find the boundingBox
            massBB = rc.Geometry.Brep.GetBoundingBox(mass, rc.Geometry.Plane.WorldXY)
            # SPLIT MASS TO FLOORS
            # 0-2 get floor curves and split surfaces based on floor heights
            # I don't use floor curves here. It is originally developed for upload Rhino2Web
            maxHeights = massBB.Max.Z - massBB.Min.Z
            floorHeights = getFloorHeights(bldgsFlr2FlrHeights, maxHeights)
            
            if floorHeights!=[0]:
                splitterSrfs, crvAdjust, topInc, nurbsList, lastFloorInc = getFloorCrvs(mass, floorHeights, maxHeights)
                
                floorCurves.append(crvAdjust)
                topIncluded.append(topInc)
                nurbsCurveList.append(nurbsList)
                lastFloorInclud.append(lastFloorInc)
                
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
                    else:
                        if srfCount == len(splitterSrfs) - 1:
                            pass
                        else:
                            msg = 'One of the masses is causing a problem. Check the output for the mass that causes the problem. You should consider breaking up this mass into smaller pieces.'
                            print msg
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return [[[restOfmass]], -1, -1, -1]
                if restOfmass != None:
                    massZones.append(restOfmass)
                else: pass
                
                splitZones.append(massZones)
        
        return splitZones, floorCurves, topIncluded, nurbsCurveList, lastFloorInclud

#Define a function that will extract the points from a polycurve line
def getCurvePoints(curve):
    exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
    individPts = []
    for line in exploCurve:
        individPts.append(line.PointAtStart)
    return individPts

#Define a function that cleans up curves by deleting out points that lie in a line and leaves the curved segments intact.  Also, have it delete out any segments that are shorter than the tolerance.
def cleanCurve(curve, curvePts, offsetDepth):
    #First check if there are any curved segements and make a list to keep track of this
    curveBool = []
    exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
    for segment in exploCurve:
        if segment.IsLinear() == False: curveBool.append(True)
        else: curveBool.append(False)
    
    #Test if any of the points lie in a line and use this to generate a new list of curve segments and points.
    newPts = []
    newSegments = []
    for pointCount, point in enumerate(curvePts):
        testLine = rc.Geometry.Line(point, curvePts[pointCount-2])
        if testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and len(newPts) == 0:
            newPts.append(curvePts[pointCount-1])
        elif testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and curveBool[pointCount-2] == False and len(newPts) != 0:
            newSegments.append(rc.Geometry.LineCurve(newPts[-1], curvePts[pointCount-1]))
            newPts.append(curvePts[pointCount-1])
        elif curveBool[pointCount-2] == True and exploCurve[pointCount-2].GetLength()>offsetDepth/25:
            newPts.append(curvePts[pointCount-1])
            newSegments.append(exploCurve[pointCount-2])
        elif curveBool[pointCount-2] == True and curveBool[pointCount-1] == True and exploCurve[pointCount-2].GetLength()<offsetDepth/25:
            for counting, curve in enumerate(exploCurve):
                if counting == pointCount-1:
                    transformMatrix = rc.Geometry.Transform.Translation(exploCurve[pointCount-1].PointAtStart.X - exploCurve[pointCount-2].PointAtEnd.X, exploCurve[pointCount-1].PointAtStart.Y - exploCurve[pointCount-2].PointAtEnd.Y, exploCurve[pointCount-1].PointAtStart.Z - exploCurve[pointCount-2].PointAtEnd.Z)
                    curve.PointAtStart.Transform(transformMatrix)
                else: pass
        else: pass
    
    #Add a segment to close the curves and join them together into one polycurve.
    if curveBool[-2] == True and exploCurve[-2].GetLength()>offsetDepth/25:
        newSegments.append(exploCurve[-2])
    elif curveBool[-2] == False:
        newSegments.append(rc.Geometry.LineCurve(newPts[-1], newPts[0]))
    else:
        pass
    
    #Shift the lists over by 1 to ensure that the order of the points and curves match the input
    newCurvePts = newPts[1:]
    newCurvePts.append(newPts[0])
    newCurveSegments = newSegments[1:]
    newCurveSegments.append(newSegments[0])
    
    #Join the segments together into one curve.
    newCrv = rc.Geometry.PolyCurve()
    for seg in newCurveSegments:
        newCrv.Append(seg)
    newCrv.MakeClosed(tolerance)
    
    #return the new curve and the list of points associated with it.
    return newCrv, newCurvePts, newCurveSegments


def splitPerimZones(mass, zoneDepth, floorCrvList, topInc, totalNurbsList):
    finalZones = []
    coreZoneWallList = []
    genFailure = False
    
    #define a value to keep track of whether this is a courtyard building.
    if len(floorCrvList) > 1: doNotGenCore = True
    else: doNotGenCore = False
    
    for listCount, floorCrvs in enumerate(floorCrvList):
        nurbsList = totalNurbsList[listCount]
        
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
        
        #Clean up the input curves, This involves testing to see if any 3 points on the floor or ceiling curves lie in a line and, if so, deleting out the redundant mid point.
        newFloorCrv = []
        newFloorPts = []
        for count, curve in enumerate(floorCrv):
            newFCrv, newFCrvPts, newFCrvSeg = cleanCurve(curve, floorPts[count], flrDepths[0])
            newFloorCrv.append(newFCrv)
            newFloorPts.append(newFCrvPts)
        floorCrv = newFloorCrv
        floorPts = newFloorPts
        
        newCeilingCrv = []
        newCeilingPts = []
        for count, curve in enumerate(ceilingCrv):
            newCCrv, newCCrvPts, newCCrvSeg  = cleanCurve(curve, ceilingPts[count], flrDepths[0])
            newCeilingCrv.append(newCCrv)
            newCeilingPts.append(newCCrvPts)
        ceilingCrv = newCeilingCrv
        ceilingPts = newCeilingPts
        
        
        #Offset the curve for each floor and use the results to create new core and perimeter zones
        
        for curveCount, curve in enumerate(floorCrv):
            try:
                #If the curves are originally Nurbs curves, Offset them with "None", corners.  Otherwise, offset them with sharp corners.
                #Offset the curves and check to be sure that they are being offset in the right direction.
                if nurbsList[curveCount] == True and listCount == 0:
                    offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    offsetFloorCrv.MakeClosed(tolerance)
                    if str(offsetFloorCrv.Contains(floorPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                        offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    else: pass
                elif listCount == 0:
                    offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    offsetFloorCrv.MakeClosed(tolerance)
                    if str(offsetFloorCrv.Contains(floorPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                        offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    else: pass
                elif nurbsList[curveCount] == True and listCount != 0:
                    offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    offsetFloorCrv.MakeClosed(tolerance)
                    if str(offsetFloorCrv.Contains(floorPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Outside":
                        offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    else: pass
                else:
                    offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    offsetFloorCrv.MakeClosed(tolerance)
                    if str(offsetFloorCrv.Contains(floorPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Outside":
                        offsetFloorCrv = curve.Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    else: pass
                
                offsetFloorPts = getCurvePoints(offsetFloorCrv)
                
                if nurbsList[curveCount] == True and listCount == 0:
                    offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    offsetCeilingCrv.MakeClosed(tolerance)
                    if str(offsetCeilingCrv.Contains(ceilingPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                        offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    else: pass
                elif listCount == 0:
                    offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    offsetCeilingCrv.MakeClosed(tolerance)
                    if str(offsetCeilingCrv.Contains(ceilingPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Inside":
                        offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    else: pass
                elif nurbsList[curveCount] == True and listCount != 0:
                    offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    offsetCeilingCrv.MakeClosed(tolerance)
                    if str(offsetCeilingCrv.Contains(ceilingPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Outside":
                        offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
                    else: pass
                else:
                    offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, -flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    offsetCeilingCrv.MakeClosed(tolerance)
                    if str(offsetCeilingCrv.Contains(ceilingPts[curveCount][0], rc.Geometry.Plane.WorldXY, tolerance)) == "Outside":
                        offsetCeilingCrv = ceilingCrv[curveCount].Offset(rc.Geometry.Plane.WorldXY, flrDepths[curveCount], tolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
                    else: pass
                
                offsetCeilingPts = getCurvePoints(offsetCeilingCrv)
                
                #Clean up the offset curves, This involves testing to see if any 3 points on the floor or ceiling curves lie in a line and, if so, deleting out the redundant mid point.
                offsetFloorCrv, offsetFloorPts, offsetFloorCrvSegments = cleanCurve(offsetFloorCrv, offsetFloorPts, flrDepths[0])
                offsetCeilingCrv, offsetCeilingPts, offsetCeilingCrvSegments = cleanCurve(offsetCeilingCrv, offsetCeilingPts, flrDepths[0])
                
                #Test to see if the number of segments of the offset curve is the same as that of the original curve.  If not, this component cannot handle such a calculation.
                checkCurveSeg = False
                if len(rc.Geometry.PolyCurve.DuplicateSegments(offsetFloorCrv)) == len(rc.Geometry.PolyCurve.DuplicateSegments(floorCrv[curveCount])) and len(rc.Geometry.PolyCurve.DuplicateSegments(offsetCeilingCrv)) == len(rc.Geometry.PolyCurve.DuplicateSegments(ceilingCrv[curveCount])):
                    checkCurveSeg = True
                else: pass
                
                #If the geometry fails the segment count test above but was originally a single nurbs curve, it is still possible to generate zones for it.
                #We just have to split up the outside curve into the same number of segments using the closest points.
                if checkCurveSeg == False and nurbsList[curveCount] == True:
                    closestOuterPointParams = []
                    for point in offsetFloorPts:
                        closestOuterPointParams.append(floorCrv[curveCount].ClosestPoint(point)[1])
                    closestOuterPointParamsFinal = closestOuterPointParams[1:]
                    outerFloorPts = []
                    for param in closestOuterPointParamsFinal:
                        outerFloorPts.append(floorCrv[curveCount].PointAt(param))
                    splitCurve = floorCrv[curveCount].Split(closestOuterPointParamsFinal)
                    finalJoinedCurve = rc.Geometry.PolyCurve()
                    for curveSeg in splitCurve:
                        finalJoinedCurve.Append(curveSeg)
                    finalJoinedCurve.MakeClosed(tolerance)
                    if finalJoinedCurve.SegmentCount == offsetFloorCrv.SegmentCount:
                        floorCrv[curveCount] = finalJoinedCurve
                        floorPts[curveCount] = getCurvePoints(finalJoinedCurve)
                        checkCurveSeg1 = True
                    else: checkCurveSeg1 = False
                    
                    closestOuterPointParams = []
                    for point in offsetCeilingPts:
                        closestOuterPointParams.append(ceilingCrv[curveCount].ClosestPoint(point)[1])
                    closestOuterPointParamsFinal = closestOuterPointParams[1:]
                    splitCurve = ceilingCrv[curveCount].Split(closestOuterPointParamsFinal)
                    finalJoinedCurve = rc.Geometry.PolyCurve()
                    for curveSeg in splitCurve:
                        finalJoinedCurve.Append(curveSeg)
                    finalJoinedCurve.MakeClosed(tolerance)
                    if finalJoinedCurve.SegmentCount == offsetCeilingCrv.SegmentCount:
                        ceilingCrv[curveCount] = finalJoinedCurve
                        ceilingPts[curveCount] = getCurvePoints(finalJoinedCurve)
                        checkCurveSeg2 = True
                    else: checkCurveSeg2 = False
                    
                    if checkCurveSeg1 == True and checkCurveSeg2 == True:
                        checkCurveSeg = True
                    else: pass
                
                
                if checkCurveSeg == True:
                    #Test to see which points on the inside of the floor and ceiling curves are closest to those on the outside.
                    floorConnectionPts = []
                    for point in offsetFloorPts:
                        pointDist = []
                        floorEdgePts = floorPts[curveCount][:]
                        for perimPoint in floorEdgePts:
                            pointDist.append(rc.Geometry.Point3d.DistanceTo(point, perimPoint))
                        sortDist = [x for (y,x) in sorted(zip(pointDist, floorEdgePts))]
                        pointDist.sort()
                        floorConnectionPts.append(sortDist[0])
                    
                    ceilingConnectionPts = []
                    for point in offsetCeilingPts:
                        pointDist = []
                        ceilingEdgePts = ceilingPts[curveCount][:]
                        for perimPoint in ceilingEdgePts:
                            pointDist.append(rc.Geometry.Point3d.DistanceTo(point, perimPoint))
                        sortDist = [x for (y,x) in sorted(zip(pointDist, ceilingEdgePts))]
                        ceilingConnectionPts.append(sortDist[0])
                    
                    #Create lines from the points of the offset curve to the closest point on the outside curve in order to split up the the offset boundary into different perimeter zones.
                    zoneFloorCurves = []
                    for pointCount, point in enumerate(offsetFloorPts):
                        floorZoneCurve = rc.Geometry.LineCurve(point, floorConnectionPts[pointCount])
                        zoneFloorCurves.append(floorZoneCurve)
                    
                    zoneCeilingCurves = []
                    for pointCount, point in enumerate(offsetCeilingPts):
                        ceilingCurves = rc.Geometry.LineCurve(point, ceilingConnectionPts[pointCount])
                        zoneCeilingCurves.append(ceilingCurves)
                    
                    #Determine which of the lines on the ceiling are closest to those on the floor and vice-versa.  This will determine which lines should be lofted to create interior partitions.
                    ceilingConnectionLines = []
                    for line in zoneFloorCurves:
                        lineDist = []
                        ceilingConnectors = zoneCeilingCurves[:]
                        for connectLine in ceilingConnectors:
                            lineDist.append(rc.Geometry.Point3d.DistanceTo(line.PointAt(0.5), connectLine.PointAt(0.5)))
                        sortDist = [x for (y,x) in sorted(zip(lineDist, ceilingConnectors))]
                        ceilingConnectionLines.append(sortDist[0])
                    
                    floorConnectionLines = []
                    for line in zoneCeilingCurves:
                        lineDist = []
                        floorConnectors = zoneFloorCurves[:]
                        for connectLine in floorConnectors:
                            lineDist.append(rc.Geometry.Point3d.DistanceTo(line.PointAt(0.5), connectLine.PointAt(0.5)))
                        sortDist = [x for (y,x) in sorted(zip(lineDist, floorConnectors))]
                        floorConnectionLines.append(sortDist[0])
                    
                    #Loft the floor and ceiling curves together in order to get walls that divide up the perimeter zones.
                    floorWalls = []
                    ceilingWalls = []
                    for lineCount, line in enumerate(zoneFloorCurves):
                        floorWalls.append(rc.Geometry.Brep.CreateFromLoft([line, ceilingConnectionLines[lineCount]], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0])
                    for lineCount, line in enumerate(zoneCeilingCurves):
                        ceilingWalls.append(rc.Geometry.Brep.CreateFromLoft([floorConnectionLines[lineCount], line], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0])
                    
                    #Make a function that pulls out the interior and exterior points of each perimeter wall brep.
                    def getIntAndExtVert(brep):
                        vert = brep.DuplicateVertices()
                        intVert = []
                        extVert = []
                        for point in vert:
                            for otherPoint in offsetFloorPts:
                                if point.X < otherPoint.X + tolerance and  point.X > otherPoint.X - tolerance and point.Y < otherPoint.Y + tolerance and  point.Y > otherPoint.Y - tolerance and point.Z < otherPoint.Z + tolerance and  point.Z > otherPoint.Z - tolerance:
                                    intVert.append(point)
                                else: pass
                            for otherPoint in offsetCeilingPts:
                                if point.X < otherPoint.X + tolerance and  point.X > otherPoint.X - tolerance and point.Y < otherPoint.Y + tolerance and  point.Y > otherPoint.Y - tolerance and point.Z < otherPoint.Z + tolerance and  point.Z > otherPoint.Z - tolerance:
                                    intVert.append(point)
                                else: pass
                        for point in vert:
                            for otherPoint in floorPts[curveCount]:
                                if point.X < otherPoint.X + tolerance and  point.X > otherPoint.X - tolerance and point.Y < otherPoint.Y + tolerance and  point.Y > otherPoint.Y - tolerance and point.Z < otherPoint.Z + tolerance and  point.Z > otherPoint.Z - tolerance:
                                    extVert.append(point)
                                else: pass
                            for otherPoint in ceilingPts[curveCount]:
                                if point.X < otherPoint.X + tolerance and  point.X > otherPoint.X - tolerance and point.Y < otherPoint.Y + tolerance and  point.Y > otherPoint.Y - tolerance and point.Z < otherPoint.Z + tolerance and  point.Z > otherPoint.Z - tolerance:
                                    extVert.append(point)
                                else: pass
                        return intVert, extVert
                    
                    #Test whetther all of the curves in the floor and ceiling are curved.
                    nurbTestList = []
                    for nurb in nurbsList:
                        if nurb == True: nurbTestList.append(1)
                        else: pass
                    if sum(nurbTestList) == len(nurbsList): totalNurbTest = True
                    else: totalNurbTest = False
                    
                    #Get a list of the exterior curves, which will be used to remove bad walls in the next step.
                    testEdgeCurves = []
                    edgeCurves = mass[curveCount].DuplicateEdgeCurves(False)
                    zHeight = []
                    for edgeCrv in edgeCurves:
                        zHeight.append((edgeCrv.PointAtStart.Z +edgeCrv.PointAtEnd.Z)/2)
                    edgeCurves = [x for (y,x) in sorted(zip(zHeight, edgeCurves))]
                    zHeight.sort()
                    zMin = zHeight[0]
                    zMax = zHeight[-1]
                    for heightCount, height in enumerate(zHeight):
                        if height > zMin + tolerance and height < zMax - tolerance:
                            testEdgeCurves.append(edgeCurves[heightCount])
                        else: pass
                    #for wall in floorWalls:
                    #    print rc.Geometry.AreaMassProperties.Compute(wall).Area
                    #Make the list of perimeter zone walls.
                    perimZoneWalls = []
                    
                    #If the geometry is all planar, check the perimeter walls against the exterior curves.
                    if totalNurbTest == False:
                        for wallCount, wall in enumerate(floorWalls):
                            wallIntVert, wallExtVert = getIntAndExtVert(wall)
                            foundIt = False
                            for testLine in testEdgeCurves:
                                if testLine.PointAtStart.X > wallExtVert[0].X - tolerance and testLine.PointAtStart.X < wallExtVert[0].X + tolerance and testLine.PointAtEnd.X > wallExtVert[1].X - tolerance and testLine.PointAtEnd.X < wallExtVert[1].X + tolerance and testLine.PointAtStart.Y > wallExtVert[0].Y - tolerance and testLine.PointAtStart.Y < wallExtVert[0].Y + tolerance and testLine.PointAtEnd.Y > wallExtVert[1].Y - tolerance and testLine.PointAtEnd.Y < wallExtVert[1].Y + tolerance and testLine.PointAtStart.Z > wallExtVert[0].Z - tolerance and testLine.PointAtStart.Z < wallExtVert[0].Z + tolerance and testLine.PointAtEnd.Z > wallExtVert[1].Z - tolerance and testLine.PointAtEnd.Z < wallExtVert[1].Z + tolerance:
                                    foundIt = True
                                elif testLine.PointAtStart.X > wallExtVert[1].X - tolerance and testLine.PointAtStart.X < wallExtVert[1].X + tolerance and testLine.PointAtEnd.X > wallExtVert[0].X - tolerance and testLine.PointAtEnd.X < wallExtVert[0].X + tolerance and testLine.PointAtStart.Y > wallExtVert[1].Y - tolerance and testLine.PointAtStart.Y < wallExtVert[1].Y + tolerance and testLine.PointAtEnd.Y > wallExtVert[0].Y - tolerance and testLine.PointAtEnd.Y < wallExtVert[0].Y + tolerance and testLine.PointAtStart.Z > wallExtVert[1].Z - tolerance and testLine.PointAtStart.Z < wallExtVert[1].Z + tolerance and testLine.PointAtEnd.Z > wallExtVert[0].Z - tolerance and testLine.PointAtEnd.Z < wallExtVert[0].Z + tolerance:
                                    foundIt = True
                                else:pass
                            if foundIt == True:
                                perimZoneWalls.append(wall)
                        
                        insertIndex = 0
                        lastTri = False
                        for wallCount, wall in enumerate(ceilingWalls):
                            wallIntVert, wallExtVert = getIntAndExtVert(wall)
                            foundIt = False
                            for testLine in testEdgeCurves:
                                if testLine.PointAtStart.X > wallExtVert[0].X - tolerance and testLine.PointAtStart.X < wallExtVert[0].X + tolerance and testLine.PointAtEnd.X > wallExtVert[1].X - tolerance and testLine.PointAtEnd.X < wallExtVert[1].X + tolerance and testLine.PointAtStart.Y > wallExtVert[0].Y - tolerance and testLine.PointAtStart.Y < wallExtVert[0].Y + tolerance and testLine.PointAtEnd.Y > wallExtVert[1].Y - tolerance and testLine.PointAtEnd.Y < wallExtVert[1].Y + tolerance and testLine.PointAtStart.Z > wallExtVert[0].Z - tolerance and testLine.PointAtStart.Z < wallExtVert[0].Z + tolerance and testLine.PointAtEnd.Z > wallExtVert[1].Z - tolerance and testLine.PointAtEnd.Z < wallExtVert[1].Z + tolerance:
                                    foundIt = True
                                elif testLine.PointAtStart.X > wallExtVert[1].X - tolerance and testLine.PointAtStart.X < wallExtVert[1].X + tolerance and testLine.PointAtEnd.X > wallExtVert[0].X - tolerance and testLine.PointAtEnd.X < wallExtVert[0].X + tolerance and testLine.PointAtStart.Y > wallExtVert[1].Y - tolerance and testLine.PointAtStart.Y < wallExtVert[1].Y + tolerance and testLine.PointAtEnd.Y > wallExtVert[0].Y - tolerance and testLine.PointAtEnd.Y < wallExtVert[0].Y + tolerance and testLine.PointAtStart.Z > wallExtVert[1].Z - tolerance and testLine.PointAtStart.Z < wallExtVert[1].Z + tolerance and testLine.PointAtEnd.Z > wallExtVert[0].Z - tolerance and testLine.PointAtEnd.Z < wallExtVert[0].Z + tolerance:
                                    foundIt = True
                                else:pass
                            #Check to see if the wall is a duplicate on the floor walls.
                            if foundIt == True:
                                isDulpicate = False
                                for otherCount, otherWall in enumerate(perimZoneWalls):
                                    if wall.IsDuplicate(otherWall, tolerance) == True:
                                        isDulpicate = True
                                        insertIndex = otherCount + 1
                                        lastTri = False
                                    else:pass
                            else:
                                isDulpicate = True
                                lastTri = False
                            if foundIt == True and isDulpicate == False:
                                if lastTri == True:
                                    insertIndex = insertIndex + 1
                                else: pass
                                perimZoneWalls.insert(insertIndex, wall)
                                lastTri = True
                    else:
                        #If the geometry is all curved, just generate the list starting with the floor curves and checking for duplicates.
                        perimZoneWalls = floorWalls[:]
                        insertIndex = 0
                        for wallCount, wall in enumerate(ceilingWalls):
                            isDulpicate = False
                            for otherCount, otherWall in enumerate(perimZoneWalls):
                                if wall.IsDuplicate(otherWall, tolerance) == True:
                                    isDulpicate = True
                                    insertIndex = otherCount + 1
                                else:pass
                            if isDulpicate == False:
                                perimZoneWalls.insert(insertIndex, wall)
                            else: pass
                    
                    
                    #Test to see if the core zone wall should be made by lofting a floor + ceiling curve or should be a triangle.
                    #Pair up the perimeter zone walls and check the condition between them to see if a triangle or a lofted surface should be generated for either the interior or exterior condition.
                    coreZoneWalls = []
                    exteriorZoneWalls = []
                    
                    perimWallsPairList = []
                    for wallCount, wall in enumerate(perimZoneWalls):
                        perimWallsPairList.append([perimZoneWalls[wallCount-1], wall])
                    
                    for pair in perimWallsPairList:
                        interiorTriangle = False
                        exteriorTriangle = False
                        intTriPts = []
                        extTriPts = []
                        intVertOne, extVertOne = getIntAndExtVert(pair[0])
                        intVertTwo, extVertTwo = getIntAndExtVert(pair[1])
                        
                        for pointCount, point in enumerate(intVertOne):
                            for otherPointCount, otherPoint in enumerate(intVertTwo):
                                if point.X < otherPoint.X + (0.5*tolerance) and  point.X > otherPoint.X - (0.5*tolerance) and point.Y < otherPoint.Y + (0.5*tolerance) and  point.Y > otherPoint.Y - (0.5*tolerance) and point.Z < otherPoint.Z + (0.5*tolerance) and  point.Z > otherPoint.Z - (0.5*tolerance):
                                    interiorTriangle = True
                                    intTriPts = [point, intVertOne[pointCount-1], intVertTwo[otherPointCount-1]]
                                else: pass
                        for pointCount, point in enumerate(extVertOne):
                            for otherPointCount, otherPoint in enumerate(extVertTwo):
                                if point.X < otherPoint.X + (0.5*tolerance) and  point.X > otherPoint.X - (0.5*tolerance) and point.Y < otherPoint.Y + (0.5*tolerance) and  point.Y > otherPoint.Y - (0.5*tolerance) and point.Z < otherPoint.Z + (0.5*tolerance) and  point.Z > otherPoint.Z - (0.5*tolerance):
                                    exteriorTriangle = True
                                    extTriPts = [point, extVertOne[pointCount-1], extVertTwo[otherPointCount-1]] 
                                else: pass
                        
                        #Make the core zone wall and append it to the list.
                        if interiorTriangle == True:
                            coreZoneWall = rc.Geometry.Brep.CreateFromCornerPoints(intTriPts[0], intTriPts[1], intTriPts[2], tolerance)
                        else:
                            #Find the line on the floor that is closest to both floor vertices.
                            distanceToLine = []
                            offsetFloorSegments = rc.Geometry.PolyCurve.DuplicateSegments(offsetFloorCrv)
                            for line in offsetFloorSegments:
                                lineDist = rc.Geometry.Point3d.DistanceTo(line.PointAtStart, intVertOne[0]) + rc.Geometry.Point3d.DistanceTo(line.PointAtEnd, intVertTwo[0])
                                distanceToLine.append(lineDist)
                            sortLineDist = [x for (y,x) in sorted(zip(distanceToLine, offsetFloorSegments))]
                            floorLine = sortLineDist[0]
                            #Find the line on the ceiling that is closest to both ceiling vertices.
                            distanceToLine = []
                            offsetCeilingSegments = rc.Geometry.PolyCurve.DuplicateSegments(offsetCeilingCrv)
                            for line in offsetCeilingSegments:
                                lineDist = rc.Geometry.Point3d.DistanceTo(line.PointAtStart, intVertOne[1]) + rc.Geometry.Point3d.DistanceTo(line.PointAtEnd, intVertTwo[1])
                                distanceToLine.append(lineDist)
                            sortLineDist = [x for (y,x) in sorted(zip(distanceToLine, offsetCeilingSegments))]
                            ceilingLine = sortLineDist[0]
                            #Loft the floor and ceiling together.
                            coreZoneWall = rc.Geometry.Brep.CreateFromLoft([floorLine, ceilingLine], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
                        coreZoneWalls.append(coreZoneWall)
                        
                        # Make the exterior wall and append it to the list.
                        if exteriorTriangle == True:
                            exteriorZoneWall = rc.Geometry.Brep.CreateFromCornerPoints(extTriPts[0], extTriPts[1], extTriPts[2], tolerance)
                        else:
                            #Find the line on the floor that is closest to both floor vertices.
                            distanceToLine = []
                            floorSegments = rc.Geometry.PolyCurve.DuplicateSegments(floorCrv[curveCount])
                            for line in floorSegments:
                                lineDist = rc.Geometry.Point3d.DistanceTo(line.PointAtStart, extVertOne[0]) + rc.Geometry.Point3d.DistanceTo(line.PointAtEnd, extVertTwo[0])
                                distanceToLine.append(lineDist)
                            sortLineDist = [x for (y,x) in sorted(zip(distanceToLine, floorSegments))]
                            floorLine = sortLineDist[0]
                            #Find the line on the ceiling that is closest to both ceiling vertices.
                            distanceToLine = []
                            ceilingSegments = rc.Geometry.PolyCurve.DuplicateSegments(ceilingCrv[curveCount])
                            for line in ceilingSegments:
                                lineDist = rc.Geometry.Point3d.DistanceTo(line.PointAtStart, extVertOne[1]) + rc.Geometry.Point3d.DistanceTo(line.PointAtEnd, extVertTwo[1])
                                distanceToLine.append(lineDist)
                            sortLineDist = [x for (y,x) in sorted(zip(distanceToLine, ceilingSegments))]
                            ceilingLine = sortLineDist[0]
                            #Loft the floor and ceiling together.
                            exteriorZoneWall = rc.Geometry.Brep.CreateFromLoft([floorLine, ceilingLine], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
                        exteriorZoneWalls.append(exteriorZoneWall)
                    
                    #Group the walls together by floor.
                    floorZones = []
                    #floorZones = perimZoneWalls
                    #floorZones.extend(exteriorZoneWalls)
                    
                    #Join the walls together to make zones.
                    joinedWalls = rc.Geometry.Brep.JoinBreps(coreZoneWalls, tolerance)[0]
                    if doNotGenCore == False:
                        coreZone = joinedWalls.CapPlanarHoles(tolerance)
                        floorZones.append(coreZone)
                    elif listCount == 0:
                        coreZoneWallList.append([joinedWalls])
                    else:
                        coreZoneWallList[curveCount].append(joinedWalls)
                    
                    perimZones = []
                    for wallCount, wall in enumerate(perimZoneWalls):
                        brepList = [wall, perimZoneWalls[wallCount-1], exteriorZoneWalls[wallCount], coreZoneWalls[wallCount]]
                        joinedWalls = rc.Geometry.Brep.JoinBreps(brepList, tolerance)[0]
                        cappedZone = joinedWalls.CapPlanarHoles(tolerance)
                        perimZones.append(cappedZone)
                    floorZones.extend(perimZones)
                    
                    
                    #Test to see if all of the generated zones are null and, if so, return the full floor mass.
                    noneTest = []
                    for zone in floorZones:
                        if zone == None:
                            noneTest.append(1)
                            warning = "The script has failed to create one of the zones because of a tolerance issue.  Try changing your Rhino Model's tolerance (prorbably try increasing) and recompute the GH definition to generate zones correctly."
                            print warning
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                        else: pass
                    
                    #Append the group to the full zone list.
                    if sum(noneTest) == len(floorZones):
                        genFailure = True
                        finalZones.append(mass[curveCount])
                        warning = "Failed to generate the perimieter zones for one floor as the geometry broke the script.  The problematic floor will be returned as a single zone."
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    elif listCount == 0:
                        finalZones.append(floorZones)
                    else:
                        finalZones[curveCount].extend(floorZones)
                else:
                    finalZones.append(mass[curveCount])
                    print "One floor did not generate perimeter and core zones because the offsetting of the boundary causes part of the core to dissappear.  The floor will be returned as a single zone.  If perimeter zones are desired, try decreasing the perimeter depth."
            except:
                if len(floorCrvList) > 1 and listCount > 0: pass
                else:
                    try:
                        finalZones.append(mass[curveCount])
                        warning = "Failed to generate the perimieter zones for one floor as the floor's geometry is not accomodated by the script.  The floor will be returned as a single zone."
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    except: pass
    
    # If the building is a courtyard building, generate the core zones and append them to the final zones.
    if len(coreZoneWallList) != 0 and genFailure == False:
        for floorCount, floor in enumerate(coreZoneWallList):
            coreZoneSurfaces = floor
            floorCurves = []
            ceilingCurves = []
            for brep in floor:
                edgeCurves = brep.DuplicateEdgeCurves(True)
                joinedEdgeCurves = rc.Geometry.Curve.JoinCurves(edgeCurves, tolerance, True)
                floorCurves.append(joinedEdgeCurves[0])
                ceilingCurves.append(joinedEdgeCurves[1])
            coreZoneSurfaces.append(rc.Geometry.Brep.CreatePlanarBreps(floorCurves)[0])
            coreZoneSurfaces.append(rc.Geometry.Brep.CreatePlanarBreps(ceilingCurves)[0])
            coreZone = rc.Geometry.Brep.JoinBreps(coreZoneSurfaces, tolerance)[0]
            finalZones[floorCount].append(coreZone)
    else: pass
    
    #If the top floor has not been included in the analysis above, append on the top floor mass.
    if topInc[0] == False:
        finalZones.append([mass[-1]])
    else: pass
    
    return finalZones


def is_near_zero(num,eps=1E-10):
    return abs(float(num)) < eps

def main(mass, floorHeights, perimDepth):
    #Import the Ladybug Classes.
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #If the user has specified a floor height, split the mass up by floor.
        if floorHeights != []:
            splitFloors, floorCrvs, topInc, nurbsList, lastFloorInclud = splitFloorHeights(mass, floorHeights, lb_preparation, lb_visualization)
        else:
            splitFloors = [mass]
            floorCrvs = []
            topInc = []
            nurbsList = []
            for item in mass:
                bbBox = item.GetBoundingBox(rc.Geometry.Plane.WorldXY)
                maxHeights = bbBox.Max.Z
                minHeights = bbBox.Min.Z
                splitters, flrCrvs, topIncl, nurbL, lastInclu = getFloorCrvs(item, [0, maxHeights-minHeights], maxHeights)
                
                floorCrvs.append(flrCrvs)
                topInc.append(topIncl)
                nurbsList.append(nurbL)
        
        #If the user had specified a perimeter zone depth, offset the floor curves to get perimeter and core.
        splitZones = []
        if perimeterZoneDepth_ != []:
            for count, mass in enumerate(splitFloors):
                splitZones.append(splitPerimZones(mass, perimDepth, floorCrvs[count], topInc[count], nurbsList[count]))
        else:
            for count, mass in enumerate(splitFloors):
                if topInc[count][0] == True and lastFloorInclud[count] == True:
                    splitZones.append(mass)
                elif topInc[count][0] == False and lastFloorInclud[count] == False:
                    splitZones.append(mass)
                else:
                    splitZones.append(mass[:-1])
        
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
    
    if splitBldgMassesLists!= -1:
        splitBldgMasses = DataTree[Object]()
        names = DataTree[Object]()
        for i, buildingMasses in enumerate(splitBldgMassesLists):
            for j, mass in enumerate(buildingMasses):
                p = GH_Path(i,j)
                
                # in case mass is not a list change it to list
                try: mass[0]
                except: mass = [mass]
                
                
                newMass = []
                for brep in mass:
                    if brep != None:
                        #Bake the objects into the Rhino scene to ensure that surface normals are facing the correct direction
                        sc.doc = rc.RhinoDoc.ActiveDoc #change target document
                        rs.EnableRedraw(False)
                        guid1 = [sc.doc.Objects.AddBrep(brep)]
                        
                        if guid1:
                            a = [rs.coercegeometry(a) for a in guid1]
                            for g in a: g.EnsurePrivateCopy() #must ensure copy if we delete from doc
                            
                            rs.DeleteObjects(guid1)
                        
                        sc.doc = ghdoc #put back document
                        rs.EnableRedraw()
                        newMass.append(g)
                    mass = newMass
                
                try:
                    splitBldgMasses.AddRange(mass, p)
                    #zoneNames = [str(i) + "_" + str(m) for m in range(len(mass))]
                    #names.AddRange(zoneNames, p)
                except:
                    splitBldgMasses.Add(mass, p)
                    #names.Add(str(i) + "_" + str(j), p)