# This component creates shades for Honeybee Zones
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generate shades for Honeybee zone windows. The component has two main uses:
_
The first is that it can be used to assign blind objects to HBZones prior to simulation.  These blinds can be dynamically controlled via a schedule.  Note that shades created this way will automatically be assigned to the zone and the windowBreps and shadeBreps outputs are just for visualization.
_
The second way to use the component is to create test shade areas for shade benefit evaluation after an energy simulation has already been run.  In this case, the component helps keep the data tree paths of heating, cooling and beam gain synced with that of the zones and windows.  For this, you would take imported EnergyPlus results and hook them up to the "zoneData" inputs and use the output "zoneDataTree" in the shade benefit evaluation.
-
Provided by Honeybee 0.0.58
    
    Args:
        _HBObjects: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        blindsMaterial_: An optional blind material from the blind material component.  If no material is connected here, the component will automatically assign a material of 0.65 solar reflectance, 0 transmittance, 0.9 emittance, 0.25 mm thickness, 221 W/mK conductivity.
        blindsSchedule_: An optional schedule to raise and lower the blinds.  If no value is connected here, the blinds will assume the "ALWAYS ON" shcedule.
        north_: Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _depth: A number representing the depth of the shade to be generated on each window.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input.
        _numOfShds: The number of shades to generated for each glazed surface.
        _distBetween: An alternate option to _numOfShds where the input here is the distance in Rhino units between each shade.
        horOrVertical_: Set to "True" to generate horizontal shades or "False" to generate vertical shades. You can also input lists of horOrVertical_ input, which will assign different orientations based on cardinal direction.
        shdAngle_: A number between -90 and 90 that represents an angle in degrees to rotate the shades.  The default is set to "0" for no rotation.  If you have vertical shades, use this to rotate them towards the South by a certain value in degrees.  If applied to windows facing East or West, tilting the shades like this will let in more winter sun than summer sun.  If you have horizontal shades, use this input to angle shades downward.  You can also put in lists of angles to assign different shade angles to different cardinal directions.
        interiorOrExter_: Set to "True" to generate Shades on the interior and set to "False" to generate shades on the exterior.  The default is set to "False" to generate exterior shades.
        distToGlass_: A number representing the offset distance from the glass to make the shades.
        _runIt: Set boolean to "True" to run the component and generate shades.
        ---------------: ...
        zoneData1_: Optional zone data for the HBZones_ that will be aligned with the generated windows.  Use this to align data like heating load, cooling load or beam gain for a shade benefit simulation with the generated shades.
        zoneData2_: Optional zone data for the HBZones_ that will be aligned with the generated windows.  Use this to align data like heating load, cooling load or beam gain for a shade benefit simulation with the generated shades.
        zoneData3_: Optional zone data for the HBZones_ that will be aligned with the generated windows.  Use this to align data like heating load, cooling load or beam gain for a shade benefit simulation with the generated shades.
    Returns:
        readMe!: ...
        ---------------: ...
        HBZones: The HBZones with the assigned shading (ready to be simulated).
        ---------------: ...
        windowBreps: Breps representing each window of the zone.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree.
        shadeBreps: Breps representing each shade of the window.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree.  Alternatively, they can be plugged into an EnergyPlus simulation with the "Honeybee_EP Context Surfaces" component.
        ---------------: ...
        zoneData1Tree: Data trees of the zoneData1_, which align with the branches for each window above.
        zoneData2Tree: Data trees of the zoneData2_, which align with the branches for each window above.
        zoneData3Tree: Data trees of the izoneData3_, which align with the branches for each window above.
"""

ghenv.Component.Name = "Honeybee_EnergyPlus Window Shade Generator"
ghenv.Component.NickName = 'EPWindowShades'
ghenv.Component.Message = 'VER 0.0.58\nNOV_05_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


from System import Object
from System import Drawing
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import uuid
import math
import os


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs(zoneNames, windowNames, windowSrfs, isZone):
    #Check if the user has hooked up a distBetwee or numOfShds.
    if _distBetween == [] and _numOfShds == []:
        numOfShd = [1]
        print "No value is connected for number of shades.  The component will be run with one shade per window."
    else:
        numOfShd = _numOfShds
    
    #Check the depths.
    checkData2 = True
    if _depth == []:
        checkData2 = False
        print "You must provide a depth for the shades."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You must provide a depth for the shades.")
    
    #Check if there is a blinds material connected and, if not, set a default.
    checkData5 = True
    if blindsMaterial_ == None:
        print "No blinds material has been connected. A material will be used with 0.65 solar reflectance, 0 transmittance, 0.9 emittance, 0.25 mm thickness, 221 W/mK conductivity."
        blindsMaterial = ['DEFAULTBLINDSMATERIAL', 0.65, 0, 0.9, 0.00025, 221]
    else:
        try: blindsMaterial = deconstructBlindMaterial(blindsMaterial_)
        except:
            checkData5 = False
            warning = 'Blinds material is not a valid blinds material from the "Honeybee_EnergyPlus Blinds Material" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check if there is a blinds schedule connected and, if not, set a default.
    checkData4 = True
    if blindsSchedule_ == None:
        schedule = "ALWAYSON"
        print "No blinds schedule has been connected.  It will be assumed that the blinds are always drawn"
    else:
        schedule= blindsSchedule_.upper()
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()

        if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
            msg = "Cannot find " + schedule + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            checkData4 = False
        elif schedule!=None and schedule.lower().endswith(".csv"):
            # check if csv file is existed
            if not os.path.isfile(schedule):
                msg = "Cannot find the shchedule file: " + schedule
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                checkData4 = False
    
    #Create a Python list from the input data trees.
    def makePyTree(zoneData):
        dataPyList = []
        for i in range(zoneData.BranchCount):
            branchList = zoneData.Branch(i)
            dataVal = []
            for item in branchList:
                dataVal.append(item)
            dataPyList.append(dataVal)
        return dataPyList
    
    allData = []
    allData.append(makePyTree(zoneData1_))
    allData.append(makePyTree(zoneData2_))
    allData.append(makePyTree(zoneData3_))
    
    #Test to see if the data lists have a headers on them, which is necessary to match the data to a zone or window.  If there's no header, the data cannot be coordinated with this component.
    checkData3 = True
    checkBranches = []
    allHeaders = []
    allNumbers = []
    for branch in allData:
        checkHeader = []
        dataHeaders = []
        dataNumbers = []
        for list in branch:
            if str(list[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
                checkHeader.append(1)
                dataHeaders.append(list[:7])
                dataNumbers.append(list[7:])
        
        allHeaders.append(dataHeaders)
        allNumbers.append(dataNumbers)
        
        if sum(checkHeader) == len(branch):pass
        else:
            checkData3 = False
            warning = "Not all of the connected zoneData has a Ladybug/Honeybee header on it.  This header is necessary for data input to this component."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Align all of the lists to each window.
    windowNamesFinal = []
    windowBrepsFinal = []
    alignedDataTree = []
    for item in allData: alignedDataTree.append([])
    
    for zoneCount, windowList in enumerate(windowSrfs):
        if isZone == True:
            zoneName = zoneNames[zoneCount]
        for windowCount, window in enumerate(windowList):
            windowBrepsFinal.append(window)
            windowName = windowNames[zoneCount][windowCount]
            windowNamesFinal.append(windowName)
            
            for inputDataTreeCount, branch in enumerate(allHeaders):
                #Test to see if the data is for the zone level.
                zoneData = False
                if isZone == True:
                    for listCount, header in enumerate(branch):
                        if header[2].split(' for ')[-1] == zoneName.upper():
                            alignedDataTree[inputDataTreeCount].append(allData[inputDataTreeCount][listCount])
                            zoneData = True
                
                #Test to see if the data is for the window level.
                srfData = False
                if zoneData == False:
                    for listCount, header in enumerate(branch):
                        try: winNm = header[2].split(' for ')[-1].split(': ')[0]
                        except: winNm =  header[2].split(' for ')[-1]
                        if str(winNm) == str(windowName.upper()):
                            alignedDataTree[inputDataTreeCount].append(allData[inputDataTreeCount][listCount])
                            srfData = True
                
                if zoneData == False and srfData == False and alignedDataTree != [[], [], []]:
                    print "A window was not matched with its respective zone/surface data."
    
    if checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True: checkData = True
    else: checkData = False
    
    
    return checkData, windowNamesFinal, windowBrepsFinal, _depth, alignedDataTree, numOfShd, blindsMaterial, schedule



def analyzeGlz(glzSrf, distBetween, numOfShds, horOrVertical, lb_visualization, normalVector):
    # find the bounding box
    bbox = glzSrf.GetBoundingBox(True)
    if horOrVertical == None:
        horOrVertical = True
    if numOfShds == None and distBetween == None:
        numOfShds = 1
    
    if numOfShds == 0 or distBetween == 0:
        sortedPlanes = []
    
    elif horOrVertical == True:
        # Horizontal
        #Define a bounding box for use in calculating the number of shades to generate
        minZPt = bbox.Corner(False, True, True)
        minZPt = rc.Geometry.Point3d(minZPt.X, minZPt.Y, minZPt.Z)
        maxZPt = bbox.Corner(False, True, False)
        maxZPt = rc.Geometry.Point3d(maxZPt.X, maxZPt.Y, maxZPt.Z - sc.doc.ModelAbsoluteTolerance)
        centerPt = bbox.Center 
        #glazing hieghts
        glzHeight = minZPt.DistanceTo(maxZPt)
        
        # find number of shadings
        try:
            numOfShd = int(numOfShds)
            shadingHeight = glzHeight/numOfShd
            shadingRemainder = shadingHeight
        except:
            shadingHeight = distBetween
            shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
            if shadingRemainder == 0:
                shadingRemainder = shadingHeight
        
        # find shading base planes
        planeOrigins = []
        planes = []
        X, Y, z = minZPt.X, minZPt.Y, minZPt.Z
        zHeights = rs.frange(minZPt.Z + shadingRemainder, maxZPt.Z + 0.5*sc.doc.ModelAbsoluteTolerance, shadingHeight)
        try:
            for Z in zHeights:
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(X, Y, Z), rc.Geometry.Vector3d.ZAxis))
        except:
            # single shading
            planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxZPt), rc.Geometry.Vector3d.ZAxis))
        # sort the planes
        sortedPlanes = sorted(planes, key=lambda a: a.Origin.Z)
    
    elif horOrVertical == False:
        # Vertical
        # Define a vector to be used to generate the planes
        planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
        planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
        
        
        #Define a bounding box for use in calculating the number of shades to generate
        minXYPt = bbox.Corner(True, True, True)
        minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
        maxXYPt = bbox.Corner(False, False, True)
        maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
        centerPt = bbox.Center
        
        #Test to be sure that the values are parallel to the correct vector.
        testVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
        if testVec.IsParallelTo(planeVec) == 0:
            minXYPt = bbox.Corner(False, True, True)
            minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
            maxXYPt = bbox.Corner(True, False, True)
            maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
        
        #Adjust the points to ensure the creation of the correct number of shades starting from the northernmost side of the window.
        tolVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
        tolVec.Unitize()
        tolVec = rc.Geometry.Vector3d.Multiply(sc.doc.ModelAbsoluteTolerance*2, tolVec)
        
        if tolVec.X > 0 and  tolVec.Y > 0:
            tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
            norOrient = False
        if tolVec.X < 0 and  tolVec.Y > 0:
            tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
            norOrient = False
        if tolVec.X < 0 and  tolVec.Y < 0:
            tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
            norOrient = True
        else:
            tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
            norOrient = True
        
        maxXYPt = rc.Geometry.Point3d.Subtract(maxXYPt, tolVec)
        minXYPt = rc.Geometry.Point3d.Subtract(minXYPt, tolVec)
        
        #glazing distance
        glzHeight = minXYPt.DistanceTo(maxXYPt)
        
        # find number of shadings
        try:
            numOfShd = int(numOfShds)
            shadingHeight = glzHeight/numOfShd
            shadingRemainder = shadingHeight
        except:
            shadingHeight = distBetween
            shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
            if shadingRemainder == 0:
                shadingRemainder = shadingHeight
        
        # find shading base planes
        planeOrigins = []
        planes = []
        
        pointCurve = rc.Geometry.Curve.CreateControlPointCurve([maxXYPt, minXYPt])
        divisionParams = pointCurve.DivideByLength(shadingHeight, True)
        divisionPoints = []
        for param in divisionParams:
            divisionPoints.append(pointCurve.PointAt(param))
        
        planePoints = divisionPoints
        try:
            for point in planePoints:
                planes.append(rc.Geometry.Plane(point, planeVec))
        except:
            # single shading
            planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(minXYPt), planeVec))
        sortedPlanes = planes
    
    
    return sortedPlanes, shadingHeight


def makeShade(_glzSrf, depth, numShds, distBtwn):
    rotationAngle_ = 0
    # import the classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_mesh = sc.sticky["ladybug_Mesh"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    # find the normal of the surface in the center
    # note2developer: there might be cases that the surface is not planar and
    # the normal is changing from point to point, then I should sample the test surface
    # and test the normal direction for more point
    baseSrfCenPt = rc.Geometry.AreaMassProperties.Compute(_glzSrf).Centroid
    # sometimes the center point is not located on the surface
    baseSrfCenPt = _glzSrf.ClosestPoint(baseSrfCenPt)
    
    bool, centerPtU, centerPtV = _glzSrf.Faces[0].ClosestPoint(baseSrfCenPt)
    if bool:
        normalVector = _glzSrf.Faces[0].NormalAt(centerPtU, centerPtV)
        #return rc.Geometry.Plane(baseSrfCenPt,normalVector)
    else:
        print "Couldn't find the normal of the shading surface." + \
              "\nRebuild the surface and try again!"
        return -1
    
    shadingSurfaces =[]
    
    #Define a function that can get the angle to North of any surface.
    def getAngle2North(normalVector):
        if north_ != None:
            northVector = north_
        else:northVector = rc.Geometry.Vector3d.YAxis
        angle =  rc.Geometry.Vector3d.VectorAngle(northVector, normalVector, rc.Geometry.Plane.WorldXY)
        finalAngle = math.degrees(angle)
        return finalAngle
    
    # Define a function that can split up a list of values and assign it to different cardinal directions.
    def getValueBasedOnOrientation(valueList):
        angles = []
        if valueList == None or len(valueList) == 0: value = None
        if len(valueList) == 1:
            value = valueList[0]
        elif len(valueList) > 1:
            initAngles = rs.frange(0, 360, 360/len(valueList))
            for an in initAngles: angles.append(an-(360/(2*len(valueList))))
            angles.append(360)
            for angleCount in range(len(angles)-1):
                if angles[angleCount] <= (getAngle2North(normalVector))%360 <= angles[angleCount +1]:
                    targetValue = valueList[angleCount%len(valueList)]
            value = targetValue
        return value
    
    # If multiple shading depths are given, use it to split up the glazing by cardinal direction and assign different depths to different directions.
    depth = getValueBasedOnOrientation(depth)
    
    # If multiple number of shade inputs are given, use it to split up the glazing by cardinal direction and assign different numbers of shades to different directions.
    numShds = getValueBasedOnOrientation(numShds)
    
    # If multiple distances between shade inputs are given, use it to split up the glazing by cardinal direction and assign different distances of shades to different directions.
    distBtwn = getValueBasedOnOrientation(distBtwn)
    
    # If multiple horizontal or vertical inputs are given, use it to split up the glazing by cardinal direction and assign different horizontal or vertical to different directions.
    horOrVertical = getValueBasedOnOrientation(horOrVertical_)
    
    # If multiple shdAngle_ inputs are given, use it to split up the glazing by cardinal direction and assign different shdAngle_ to different directions.
    shdAngle = getValueBasedOnOrientation(shdAngle_)
    
    #If multiple interiorOrExter_ inputs are given, use it to split up the glazing by cardinal direction and assign different interiorOrExterior_ to different directions.
    interiorOrExter = getValueBasedOnOrientation(interiorOrExter_)
    
    #If multiple distToGlass_ inputs are given, use it to split up the glazing by cardinal direction and assign different distToGlass_ to different directions.
    distToGlass = getValueBasedOnOrientation(distToGlass_)
    
    # generate the planes
    planes, shadingHeight = analyzeGlz(_glzSrf, distBtwn, numShds, horOrVertical, lb_visualization, normalVector)
    
    # find the intersection crvs as the base for shadings
    intCrvs =[]
    for plane in planes:
        try: intCrvs.append(rc.Geometry.Brep.CreateContourCurves(_glzSrf, plane)[0])
        except: print "One intersection failed."
    
    if normalVector != rc.Geometry.Vector3d.ZAxis:
        normalVectorPerp = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
    angleFromNorm = math.degrees(rc.Geometry.Vector3d.VectorAngle(normalVectorPerp, normalVector))
    if normalVector.Z < 0: angleFromNorm = angleFromNorm*(-1)
    
    #If the user has set the shades to generate on the interior, flip the normal vector.
    if interiorOrExter == True:
        normalVectorPerp.Reverse()
    else: interiorOrExter = False
    
    normalVecOrignal = rc.Geometry.Vector3d(normalVectorPerp)
    
    #If a shdAngle is provided, use it to rotate the planes by that angle
    if shdAngle != None:
        if horOrVertical == True or horOrVertical == None:
            horOrVertical = True
            planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
            planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
            normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
        elif horOrVertical == False:
            planeVec = rc.Geometry.Vector3d.ZAxis
            if getAngle2North(normalVectorPerp) < 180:
                normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
            else: normalVectorPerp.Rotate((shdAngle*-0.01745329), planeVec)
    else:
        shdAngle = 0
    
    #Make EP versions of some of the outputs.
    EPshdAngleInint = angleFromNorm+shdAngle
    if EPshdAngleInint >= 0: EPshdAngle = 90 - EPshdAngleInint
    else: EPshdAngle = 90 + (EPshdAngleInint)*-1
    if EPshdAngle > 180 or EPshdAngle < 0:
        warning = "The input shdAngle_ value will cause EnergyPlus to crash."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if horOrVertical == True: EPSlatOrient = 'Horizontal'
    else: EPSlatOrient = 'Vertical'
    if interiorOrExter == True: EPinteriorOrExter = 'InteriorBlind'
    else: EPinteriorOrExter = 'ExteriorBlind'
    
    #Generate the shade curves based on the planes and extrusion vectors
    if intCrvs !=[]:
        for c in intCrvs:
            try:
                shdSrf = rc.Geometry.Surface.CreateExtrusion(c, float(depth) * normalVectorPerp).ToBrep()
                shadingSurfaces.append(shdSrf)
            except: pass
    
    #If the user has specified a distance to move the shades, move them along the normal vector.
    if distToGlass != None: pass
    else: distToGlass = depth/2
    
    transVec = normalVecOrignal
    transVec.Unitize()
    finalTransVec = rc.Geometry.Vector3d.Multiply(distToGlass, transVec)
    blindsTransform =  rc.Geometry.Transform.Translation(finalTransVec)
    
    for shdSrf in shadingSurfaces:
        shdSrf.Transform(blindsTransform)
    
    
    #Get the EnergyPlus distance to glass.
    EPDistToGlass = distToGlass + (depth)*(0.5)*math.cos(math.radians(EPshdAngle))
    if EPDistToGlass < 0.01: EPDistToGlass = 0.01
    elif EPDistToGlass > 1:
        warning = "The input distToGlass_ value is so large that it will cause EnergyPlus to crash."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the depth and the shadingHeight to see if E+ will crash.
    assignEPCheckInit = True
    if depth > 1:
        assignEPCheckInit = False
        warning = "Note that E+ does not like shading depths greater than 1. HBObjWShades will not be generated.  shadeBreps will still be produced and you can account for these shades using a 'Honeybee_EP Context Surfaces' component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, warning)
    if shadingHeight > 1:
        assignEPCheckInit = False
        warning = "Note that E+ does not like distances between shades that are greater than 1. HBObjWShades will not be generated.  shadeBreps will still be produced and you can account for these shades using a 'Honeybee_EP Context Surfaces' component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, warning)
    
    
    return shadingSurfaces, EPSlatOrient, depth, shadingHeight, EPshdAngle, EPDistToGlass, EPinteriorOrExter, assignEPCheckInit

def deconstructBlindMaterial(material):
    matLines = material.split('\n')
    
    name = matLines[1].split(',')[0]
    reflect = float(matLines[2].split(',')[0])
    transmit = float(matLines[3].split(',')[0])
    emiss = float(matLines[4].split(',')[0])
    thickness = float(matLines[5].split(',')[0])
    conduct = float(matLines[6].split(';')[0])
    
    return [name, reflect, transmit, emiss, thickness, conduct]

def createEPBlindMat(blindsMaterial, EPSlatOrient, depth, shadingHeight, EPshdAngle, distToGlass, name):
    EPBlindMat = "WindowMaterial:Blind,\n" + \
        '\t' + blindsMaterial[0] + "_" + name + ',           !- Name\n' + \
        '\t' + EPSlatOrient + ',              !- Slat Orientation\n' + \
        '\t' + str(depth) + ',                     !- Slat Width {m}\n' + \
        '\t' + str(shadingHeight) +',                     !- Slat Separation {m}\n' + \
        '\t' + str(blindsMaterial[4]) + ',                 !- Slat Thickness {m}\n' + \
        '\t' + str(EPshdAngle) + ',                      !- Slat Angle {deg}\n' + \
        '\t' + str(blindsMaterial[5]) + ',                     !- Slat Conductivity {W/m-K}\n' + \
        '\t' + str(blindsMaterial[2]) + ',                        !- Slat Beam Solar Transmittance\n' + \
        '\t' + str(blindsMaterial[1]) + ',                    !- Front Side Slat Beam Solar Reflectance\n' + \
        '\t' + str(blindsMaterial[1]) + ',                    !- Back Side Slat Beam Solar Reflectance\n' + \
        '\t' + str(blindsMaterial[2]) + ',                        !- Slat Diffuse Solar Transmittance\n' + \
        '\t' + str(blindsMaterial[1]) + ',                    !- Front Side Slat Diffuse Solar Reflectance\n' + \
        '\t' + str(blindsMaterial[1]) + ',                    !- Back Side Slat Diffuse Solar Reflectance\n' + \
        '\t' + str(blindsMaterial[2]) + ',                       !- Slat Beam Visible Transmittance\n' + \
        '\t' + ',                        !- Front Side Slat Beam Visible Reflectance\n' + \
        '\t' + ',                        !- Back Side Slat Beam Visible Reflectance\n' + \
        '\t' + str(blindsMaterial[2]) + ',                        !- Slat Diffuse Visible Transmittance\n' + \
        '\t' + ',                        !- Front Side Slat Diffuse Visible Reflectance\n' + \
        '\t' + ',                        !- Back Side Slat Diffuse Visible Reflectance\n' + \
        '\t' + ',                        !- Slat Infrared Hemispherical Transmittance\n' + \
        '\t' + str(blindsMaterial[3]) + ',                     !- Front Side Slat Infrared Hemispherical Emissivity\n' + \
        '\t' + str(blindsMaterial[3]) + ',                     !- Back Side Slat Infrared Hemispherical Emissivity\n' + \
        '\t' + str(distToGlass) + ',                    !- Blind to Glass Distance {m}\n' + \
        '\t' + '0.5,                     !- Blind Top Opening Multiplier\n' + \
        '\t' + ',                        !- Blind Bottom Opening Multiplier\n' + \
        '\t' + '0.5,                     !- Blind Left Side Opening Multiplier\n' + \
        '\t' + '0.5,                     !- Blind Right Side Opening Multiplier\n' + \
        '\t' + ',                        !- Minimum Slat Angle {deg}\n' + \
        '\t' + '180;                     !- Maximum Slat Angle {deg}\n'
    
    return EPBlindMat

def createEPBlindControl(blindsMaterial, schedule, EPinteriorOrExter, name):
    if schedule == 'ALWAYSON':
        schedCntrlType = 'ALWAYSON'
        schedCntrl = 'No'
        schedName = ''
    elif schedule.upper().endswith('CSV'):
        schedFileName = os.path.basename(schedule)
        schedName = "_".join(schedFileName.split(".")[:-1])
        schedCntrlType = 'OnIfScheduleAllows'
        schedCntrl = 'Yes'
    else:
        schedName = schedule
        schedCntrlType = 'OnIfScheduleAllows'
        schedCntrl = 'Yes'
    
    EPBlindControl = 'WindowProperty:ShadingControl,\n' + \
        '\t' + 'BlindCntrlFor_' + name +',            !- Name\n' + \
        '\t' + EPinteriorOrExter + ',           !- Shading Type\n' + \
        '\t' + ',                        !- Construction with Shading Name\n' + \
        '\t' + schedCntrlType + ',                !- Shading Control Type\n' + \
        '\t' + schedName + ',                        !- Schedule Name\n' + \
        '\t' + ',                        !- Setpoint {W/m2, W or deg C}\n' + \
        '\t' + schedCntrl + ',                      !- Shading Control Is Scheduled\n' + \
        '\t' + 'No,                      !- Glare Control Is Active\n' + \
        '\t' + blindsMaterial[0] + "_" + name + ',           !- Shading Device Material Name\n' + \
        '\t' + 'FixedSlatAngle,          !- Type of Slat Angle Control for Blinds\n' + \
        '\t' + ';                        !- Slat Angle Schedule Name\n'
    
    return EPBlindControl

def main():
    if _HBObjects != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True:
        #Import the classes
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        #Make the lists that will be filled up
        zoneNames = []
        windowNames = []
        windowSrfs = []
        windowObjects = []
        isZoneList = []
        assignEPCheck = True
        HBObjWShades = []
        EPSlatOrientList = []
        depthList = []
        shadingHeightList = []
        EPshdAngleList = []
        distToGlassList = []
        EPinteriorOrExterList = []
        
        #Call the objects from the hive.
        HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBObjects)
        
        #Find out what the object is and make sure that we can run it through this component's functions.
        for object in HBZoneObjects:
            if object.objectType == "HBZone":
                isZoneList.append(1)
                zoneNames.append(object.name)
                winBreps = []
                winNames = []
                for srf in object.surfaces:
                    if srf.hasChild:
                        if srf.BC == 'OUTDOORS' or srf.BC == 'Outdoors':
                            if srf.isPlanar == True:
                                for childSrf in srf.childSrfs:
                                    windowObjects.append(childSrf)
                                    winNames.append(childSrf.name)
                                    winBreps.append(childSrf.geometry)
                            else: print "One surface with a window is not planar. EenergyPlus shades will not be assigned to this window."
                        else: print "One surface with a window does not have an outdoor boundary condition. EenergyPlus shades will not be assigned to this window."
                windowNames.append(winNames)
                windowSrfs.append(winBreps)
            elif object.objectType == "HBSurface":
                isZoneList.append(0)
                warning = "Note that, when using this component for individual surfaces, you should make sure that the direction of the surface is facing the outdoors in order to be sure that your shades are previewing correctly."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, warning)
                
                if not hasattr(object, 'type'):
                    # find the type based on 
                    object.type = object.getTypeByNormalAngle()
                if not hasattr(object, 'angle2North'):
                    # find the type based on
                    object.getAngle2North()
                if not hasattr(object, "BC"):
                    object.BC = 'OUTDOORS'
                
                if object.hasChild:
                    if object.BC != 'OUTDOORS' and object.BC != 'Outdoors':
                        assignEPCheck = False
                        warning = "The boundary condition of the input object must be outdoors.  E+ cannot create shades for intdoor windows."
                        print warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                    elif object.isPlanar == False:
                        assignEPCheck = False
                        warning = "The surface must not be curved.  With the way that we mesh curved surfaces for E+, the program would just freak out with blinds."
                        print warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                    else:
                        for childSrf in object.childSrfs:
                            windowObjects.append(childSrf)
                            windowNames.append([childSrf.name])
                            windowSrfs.append([childSrf.geometry])
        
        #Make sure that all HBObjects are of the same type.
        checkSameType = True
        if sum(isZoneList) == len(_HBObjects): isZone = True
        elif sum(isZoneList) == 0: isZone = False
        else:
            checkSameType = False
            warning = "This component currently only supports inputs that are all HBZones or all HBSrfs but not both. For now, just grab another component for each of these inputs."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            isZone = False
        
        #Check the inputs and make sure that we have everything that we need to generate the shades.  Set defaults on things that are not connected.
        if checkSameType == True:
            checkData, windowNames, windowSrfsInit, depths, alignedDataTree, numOfShd, blindsMaterial, schedule = checkTheInputs(zoneNames, windowNames, windowSrfs, isZone)
        else: checkData == False
        
        #Generate the shades.
        if checkData == True:
            shadings = []
            for window in windowSrfsInit:
                shadeBreps, EPSlatOrient, depth, shadingHeight, EPshdAngle, distToGlass, EPinteriorOrExter, assignEPCheckInit = makeShade(window, depths, numOfShd, _distBetween)
                shadings.append(shadeBreps)
                EPSlatOrientList.append(EPSlatOrient)
                depthList.append(depth)
                shadingHeightList.append(shadingHeight)
                EPshdAngleList.append(EPshdAngle)
                distToGlassList.append(distToGlass)
                EPinteriorOrExterList.append(EPinteriorOrExter)
                if assignEPCheckInit == False: assignEPCheck = False
            
            #Create the EnergyPlus blinds material and assign it to the windows with shades.
            if assignEPCheck == True:
                for count, windowObj in enumerate(windowObjects):
                    windowObj.blindsMaterial = createEPBlindMat(blindsMaterial, EPSlatOrientList[count], depthList[count], shadingHeightList[count], EPshdAngleList[count], distToGlassList[count], windowObj.name)
                    windowObj.shadingControl = createEPBlindControl(blindsMaterial, schedule, EPinteriorOrExterList[count], windowObj.name)
                    windowObj.shadingControlName = 'BlindCntrlFor_' + windowObj.name
                    windowObj.shadingSchName = schedule
                
                ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
            else: ModifiedHBZones = []
            
            return checkData, windowSrfsInit, shadings, alignedDataTree, ModifiedHBZones
        else:
            return False, [], [], [], []
    else:
        print "You should first let both Honeybee and Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Honeybee and Ladybug fly...")
        return False, [], [], [], []




#Run the main functions.
checkData = False
if _HBObjects != [] and _runIt == True:
    checkData, windowSrfsInit, shadings, alignedDataTree, HBObjWShades = main()


#Unpack the data trees.
if checkData == True:
    windowBreps = DataTree[Object]()
    shadeBreps = DataTree[Object]()
    zoneData1Tree = DataTree[Object]()
    zoneData2Tree = DataTree[Object]()
    zoneData3Tree = DataTree[Object]()
    
    for count, brep in enumerate(windowSrfsInit):
        windowBreps.Add(brep, GH_Path(count))
    
    for count, brepList in enumerate(shadings):
        for brep in brepList: shadeBreps.Add(brep, GH_Path(count))
    
    for treeCount, finalTree in enumerate(alignedDataTree):
        if treeCount == 0:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData1Tree.Add(twig, GH_Path(bCount))
        elif treeCount == 1:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData2Tree.Add(twig, GH_Path(bCount))
        elif treeCount == 2:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData3Tree.Add(twig, GH_Path(bCount))

ghenv.Component.Params.Output[2].Hidden = True