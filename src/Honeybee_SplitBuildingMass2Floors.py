#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Honeybee.
#
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> and Saeran Vasanthakumar <saeranv@gmail.com>
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
Use this component to divide up a brep (polysurface) representative of a complete building massing into floors.
This generic zoning will divide the input mass into seprate floors based on an input floor height.
_
If you have a single mass representing two towers off of a podium, the two towers are not a continuous mass and you should therefore send each tower and the podium in as a separate Brep into this component.  The component will work for courtyard buildings.
Core and perimeter zoneing should work for almost all masses where all walls are planar.  It works in a limited number of cases that have both curved and planar walls.  Also, it is important to note that, if your offset depth is so large in comparison to your building depth as to create perimeter zones that intersect one another, the whole floor will be returned as a single zone.
While this component can usually get you the most of the way there, it is still recommended that you bake the output and check the geometry in Rhino before turning the breps into HBZones.
_
The assumption about an E+ zone is that the air is well mixed and all at the same temperature.
Therefore, it is usually customary to break up a building depending on the areas where you would expect different building microclimates to exist.
This includes breaking up the building into floors (since each floor can have a different microclimate) and breaking up each floor into a core zone and perimeter zones (since each side of the buidling gets a different amount of solar gains and losses/gains through the envelope).
This component helps break up building masses into floors, and can be used in conjunction with the Honeybee_SplitBuildingFloor2ThermalZones component to genreate core zone and perimeter zones.
-
Provided by Honeybee 0.0.64

    Args:
        _bldgMasses: A Closed brep or list of closed breps representing a building massing.
        _bldgsFlr2FlrHeights: A list of floor heights in Rhino model units that will be used to make each floor of the building.  The list should run from bottom floor to top floor.  Alternatively, you can input a text string that codes for how many floors of each height you want.  For example, inputting "2@4" (without quotations) will make two ground floors with a height of 4 Rhino model units.  Simply typing "@3" will make all floors 3 Rhino model units.  Putting in lists of these text strings will divide up floors accordingly.  For example, the list "1@5   2@4   @3"  will make a ground floor of 5 units, two floors above that at 4 units and all remaining floors at 3 units.
    Returns:
        readMe!: ...
        splitBldgFloors: A series of breps that correspond to inputted floor heights. These can be inserted into the Honeybee_SplitBuildingFloor2ThermalZones component to further split the floors into thermal zones for energy simulation.
"""


ghenv.Component.Name = 'Honeybee_SplitBuildingMass2Floors'
ghenv.Component.NickName = 'Split2Floors'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
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
        print "Connect closed solid building masses to split them up into floors."

    if _bldgsFlr2FlrHeights != []:
        checkData2 = True
    else:
        print "A value must be connected for floor heights in _bldgsFlr2FlrHeights in order to run."
        checkData2 = False

    if checkData1 == True and checkData2 == True:
        checkData = True
    else:
        checkData = False
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
            #if numOfFlr != 1 and rep:
            #    print 'There are ' + `numOfFlr` + ' floors with height of ' + `floorH` + ' m.'
            #elif rep:
            #    print 'There is a floor with height of ' + `floorH` + ' m.'

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

    finaltopIncList = []

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

        #Adding is_near_zero function due
        #to rounding/precision issues with equality of floats
        if is_near_zero(lastFloorHeight):
            lastFloorInc = True
        else:
            if lastFloorHeight < maxHeight:
                lastFloorInc = False
            else:
                lastFloorInc = True
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
            else:
                topInc = False
        else:
            if lastFloorHeight < maxHeight:
                topInc = True
            else: topInc = False

        if topProblem == True:
            topInc = False
        else: pass

        #Append the results to the list.
        finaltopIncList.append(topInc)
    return splitters, finaltopIncList, lastFloorInc
def splitFloorHeights(bldgMasses, bldgsFlr2FlrHeights, lb_preparation, lb_visualization):
    #Input: mass, floorHeights, lb_preparation, lb_visualization
    #Output: splitFloors, floorCrvs, topInc, nurbsList, lastFloorInclud
    debug = sc.sticky['debug']

    if len(bldgMasses)!=0:
        # clean the geometries
        analysisMesh, initialMasses = lb_preparation.cleanAndCoerceList(bldgMasses)

        splitZones = []
        topIncluded = []
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
                splitterSrfs, topInc,lastFloorInc = getFloorCrvs(mass, floorHeights, maxHeights)

                topIncluded.append(topInc)
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

        return splitZones, topIncluded, lastFloorInclud
def is_near_zero(num, eps=1E-10):
    return abs(float(num)) < eps
def main(mass, floorHeights):
    #Import the Ladybug Classes.
    #debug = sc.sticky['debug']
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        #If the user has specified a floor height, split the mass up by floor.
        #Input: mass, floorHeights, lb_preparation, lb_visualization
        #Output: splitFloors, floorCrvs, topInc, nurbsList, lastFloorInclud
        splitFloors = []
        topInc = []
        lastFloorInclud = []
        if floorHeights != []:
            splitFloors, topInc,lastFloorInclud = splitFloorHeights(mass, floorHeights, lb_preparation, lb_visualization)
        #debug.extend(map(lambda n: n[0],splitFloors))
        #Sort the floors into a list
        splitZones = []
        for count, mass in enumerate(splitFloors):
            #print count, mass, topInc[count], lastFloorInclud[count]
            if topInc[count][0] == True and lastFloorInclud[count] == True:
                splitZones.append(mass)
            elif topInc[count][0] == False and lastFloorInclud[count] == False:
                splitZones.append(mass)
            else:
                debug.append(mass[0])
                splitZones.append(mass[:-1])

        #return list of list of each floor zones
        return splitZones
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1

checkData = False

sc.sticky['debug']=[]
if _runIt == True:
    checkData = checkTheInputs()
if checkData == True:
    splitBldgMassesLists = main(_bldgMasses, _bldgsFlr2FlrHeights)
    if splitBldgMassesLists!= -1:
        splitBldgFloors = DataTree[Object]()
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
                    splitBldgFloors.AddRange(mass, p)
                    #zoneNames = [str(i) + "_" + str(m) for m in range(len(mass))]
                    #names.AddRange(zoneNames, p)
                except:
                    splitBldgFloors.Add(mass, p)
                    #names.Add(str(i) + "_" + str(j), p)
debug = sc.sticky['debug']