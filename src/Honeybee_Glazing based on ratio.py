# glazingCreator
# The main geometry-generating parts of this component are developed by Chris Mackey
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com - Sadeghipour@gmail.com> 
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
Use this component to generate windows for a HBSurface or HBZone based on a desired window-to-wall ratio. In addition to generating window geometry that corresponds with the input ratio, this component also allows you a fairly high level of control over the window geometry.
_
The first way in which you gain additional control over geometry is the option of whether you want to generate a single window for each surface, which is good for making energy simulations run fast, or you want to use the glazig ratio to create several windows distributed across the surfaces, which is often necessary to have accurate daylight simulations or high-resolution thermal maps.
If you break up the window into several ones, you also have the ability to set the distance between each of the windows along the surface.
_
If you input wall surfaces that have perfectly horizontal tops and/or bottoms, you also have access to a number of other other inputs such as window height, the sill height, and whether you want to split the glazing vertically into two windows.
-
Provided by Honeybee 0.0.59
    
    Args:
        _HBObjects: Honeybee thermal zones or surfaces for which glazing should be generated.
        _glzRatio: The fraction of the wall surface that should be glazed.  This input only accepts values between 0 and 0.95 (we don't go all of the way up to 1 because EnergyPlus does not like this).  This input can also accept lists of values and will assign different glazing ratios based on cardinal direction, starting with north and moving counter-clockwise.  Note that glazing ratio always takes priority over the windowHeight and sillHeight inputs below.
        breakUpWindow_: Set to "True" to generate a distributed set of multiple windows on walls and set to "False" to generate just a single window per rectangular wall surface.  This input can also accept lists of boolean values and will assign different 'BreakUpWindow' values based on cardinal direction, starting with north and moving counter-clockwise.  A single window for each surface is good for making energy simulations run fast while several distributed windows is often necessary to have accurate daylight simulations or high-resolution thermal maps. The default is set to "True" to generate multiple distributed windows.
        breakUpDist_: An optional number in Rhino model units that sets the distance between individual windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different sill heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios or window heights.  The default is set to 2 meters.
        windowHeight_: An optional number in Rhino model units that sets the height of your windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different window heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios. The default is set to 2 meters.
        sillHeight_: An optional number in Rhino model units that sets the distance from the floor to the bottom of your windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different sill heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios or window heights.  The default is set to 0.8 meters (or 80 centimeters).
        splitGlzVertDist_: An optional number in Rhino model units that splits the windows on rectangular surfaces into two with a vertical distance between them equal to this input when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different vertical distances based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios, high window heights, or high sill heights.
        skyLightRatio_: If you have input a full zone or list of zones as your HBObjects, use this input to generate skylights on the roof surfaces. A single window for each surface is good for making energy simulations run fast while several distributed windows is often necessary to have accurate daylight simulations or high-resolution thermal maps. The default is set to "True" to generate multiple distributed windows.
        breakUpSkylight_: Set to "True" to generate a distributed set of multiple windows for skylights and set to "False" to generate just a single window per roof surface.
        skyLightBreakUpDist_: An optional number in Rhino model units that sets the distance between individual skylights when the breakUpSkylight_ input above is set to 'True'.  The default is set to 3 meters.
        _runIt: set runIt to True to generate the glazing
    Returns:
        readMe!: ...
        HBObjWGLZ: Newhoneybee zones that contain glazing surfaces based on the parameters above. 
"""

ghenv.Component.Name = "Honeybee_Glazing based on ratio"
ghenv.Component.NickName = 'glazingCreator'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import math
import uuid

# all this only to graft the data at the end! booooooo
import Grasshopper.Kernel as gh
import System
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

tol = sc.doc.ModelAbsoluteTolerance
ang_tol = sc.doc.ModelAngleToleranceRadians

def getTopBottomCurves(brep):
    #Write a function to find if a given line is horizontal or vertical.
    def isEdgeHorizontal(edge):
        if edge.PointAtStart.Z < (edge.PointAtEnd.Z + sc.doc.ModelAbsoluteTolerance) and edge.PointAtStart.Z > (edge.PointAtEnd.Z - sc.doc.ModelAbsoluteTolerance):
            return True
        else: 
            return False
    
    def isEdgeVertical(edge):
        if edge.PointAtStart.X < (edge.PointAtEnd.X + sc.doc.ModelAbsoluteTolerance) and edge.PointAtStart.X > (edge.PointAtEnd.X - sc.doc.ModelAbsoluteTolerance) and edge.PointAtStart.Y < (edge.PointAtEnd.Y + sc.doc.ModelAbsoluteTolerance) and edge.PointAtStart.Y > (edge.PointAtEnd.Y - sc.doc.ModelAbsoluteTolerance):
            return True
        else:
            return False
    
    # duplicate the edges of the wall
    edges = brep.DuplicateEdgeCurves(True)
    
    # sort the edges based on the z of mid point of the edge and get the top and bottom edges.
    sortedEdges = sorted(edges, key=lambda edge: edge.PointAtNormalizedLength(0.5).Z)
    
    btmEdge = sortedEdges[0]
    isBtmHorizontal = isEdgeHorizontal(btmEdge)
    
    topEdge = sortedEdges[-1]
    isTopHorizontal = isEdgeHorizontal(topEdge)
    
    #Test to see if any of the side edges are vertical and, if there are two, there may be a rectangle that we can pull out.
    vertEdges = []
    nonVertEdge = []
    for edge in sortedEdges:
        if isEdgeVertical(edge) == True:
            vertEdges.append(edge)
        else: nonVertEdge.append(edge)
    if len(vertEdges) == 2:
        are2LinesVert = True
    else: are2LinesVert = False
    
    return btmEdge, isBtmHorizontal, topEdge, isTopHorizontal, vertEdges, are2LinesVert

def getCurvePoints(curve):
    exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
    individPts = []
    for line in exploCurve:
        individPts.append(line.PointAtStart)
    return individPts

#Define a function that cleans up curves by deleting out points that lie in a line and leaves the curved segments intact.  Also, have it delete out any segments that are shorter than the tolerance.
def cleanCurve(curve):
    #First check if there are any curved segements and make a list to keep track of this
    curveBool = False
    exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
    for segment in exploCurve:
        if segment.IsLinear() == False: curveBool = True
        else: pass
    
    # Get the curve points.
    curvePts = getCurvePoints(curve)
    
    if curveBool == False:
        #Test if any of the points lie in a line and use this to generate a new list of curve segments and points.
        newPts = []
        newSegments = []
        for pointCount, point in enumerate(curvePts):
            testLine = rc.Geometry.Line(point, curvePts[pointCount-2])
            if testLine.DistanceTo(curvePts[pointCount-1], True) > tol and len(newPts) == 0:
                newPts.append(curvePts[pointCount-1])
            elif testLine.DistanceTo(curvePts[pointCount-1], True) > tol and len(newPts) != 0:
                newSegments.append(rc.Geometry.LineCurve(newPts[-1], curvePts[pointCount-1]))
                newPts.append(curvePts[pointCount-1])
            else: pass
        
        #Add a segment to close the curves and join them together into one polycurve.
        newSegments.append(rc.Geometry.LineCurve(newPts[-1], newPts[0]))
        
        #Shift the lists over by 1 to ensure that the order of the points and curves match the input
        newCurvePts = newPts[1:]
        newCurvePts.append(newPts[0])
        newCurveSegments = newSegments[1:]
        newCurveSegments.append(newSegments[0])
        
        #Join the segments together into one curve.
        newCrv = rc.Geometry.PolyCurve()
        for seg in newCurveSegments:
            newCrv.Append(seg)
        newCrv.MakeClosed(tol)
    else:
        newCrv = curve
    
    #return the new curve and the list of points associated with it.
    return newCrv

def createGlazingTri(triSrf, glazingRatio, scalePt):
    #Calculate the center point if one is not provided.
    if scalePt:
        cenPt = scalePt
    else:
        cenPt = rc.Geometry.AreaMassProperties.Compute(triSrf).Centroid
    
    #Scale the wall geometry to get to the appropriate glazingRatio.
    scaleFactor = glazingRatio ** .5
    scaleT = rc.Geometry.Transform.Scale(cenPt, scaleFactor)
    glzSrfBrep = triSrf.DuplicateBrep()
    glzSrfBrep.Transform(scaleT)
    glzSrf = [glzSrfBrep]
    return glzSrf


def createGlazingQuad(quadSrf, glazingRatio, scalePt):
    #Calculate the center point if one is not provided.
    if scalePt:
        cenPt = scalePt
    else:
        cenPt = rc.Geometry.AreaMassProperties.Compute(quadSrf).Centroid
    
    #Check to see if the center point of the quadrilaterial is inside the quadrilateral (which means that we can just scale the quadrilateral and the result will be inside it).
    cenPt = rc.Geometry.AreaMassProperties.Compute(quadSrf).Centroid
    closestPt = quadSrf.ClosestPoint(cenPt)
    if cenPt.X < (closestPt.X + sc.doc.ModelAbsoluteTolerance) and cenPt.X > (closestPt.X - sc.doc.ModelAbsoluteTolerance) and cenPt.Y < (closestPt.Y + sc.doc.ModelAbsoluteTolerance) and cenPt.Y > (closestPt.Y - sc.doc.ModelAbsoluteTolerance) and cenPt.Z < (closestPt.Z + sc.doc.ModelAbsoluteTolerance) and cenPt.Z > (closestPt.Z - sc.doc.ModelAbsoluteTolerance):
        checkCent = True
    else:
        checkCent = False
    
    #If the polygon's center point lies within the polygon, use the typical scaling method to get the window.
    if checkCent == True:
        scaleFactor = glazingRatio ** .5
        scaleT = rc.Geometry.Transform.Scale(cenPt, scaleFactor)
        glzSrfBrep = quadSrf.DuplicateBrep()
        glzSrfBrep.Transform(scaleT)
        glzSrf = [glzSrfBrep]
    #If the polygon's center point lies outside of the polygon, split the polygon into two triangles and scale each to its own center.
    else:
        pts = quadSrf.DuplicateVertices()
        diagonal1 = rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], sc.doc.ModelAbsoluteTolerance)
        diagonal2 = rc.Geometry.Brep.CreateFromCornerPoints(pts[1], pts[2], pts[3], sc.doc.ModelAbsoluteTolerance)
        quadSrfSplit1 = rc.Geometry.Brep.Split(quadSrf, diagonal1, sc.doc.ModelAbsoluteTolerance)
        quadSrfSplit2 = rc.Geometry.Brep.Split(quadSrf, diagonal2, sc.doc.ModelAbsoluteTolerance)
        
        quadSrfSplit = quadSrfSplit1 + quadSrfSplit2
        
        glzSrf = []
        for brep in quadSrfSplit:
            glzSrf.append(createGlazingTri(brep, glazingRatio, None)[0])
    
    return glzSrf


def createGlazingOddPlanarGeo(baseSrf, glazingRatio):
    #Define the meshing paramters to break down the surface in a manner that produces only trinagles and quads.
    meshPar = rc.Geometry.MeshingParameters.Default
    
    #Create a mesh of the base surface.
    windowMesh = rc.Geometry.Mesh.CreateFromBrep(baseSrf, meshPar)[0]
    
    #Create breps of all of the mesh faces and use them to make each window.
    glzSrf = []
    srfFaceList = windowMesh.Faces
    srfVertList = windowMesh.Vertices
    srfFaceCen = []
    
    for faceNum, face in enumerate(srfFaceList):
        if face.IsQuad == True:
            glzSrf.append(createGlazingQuad(rc.Geometry.Brep.CreateFromCornerPoints(srfVertList[face[0]], srfVertList[face[1]], srfVertList[face[2]], srfVertList[face[3]], sc.doc.ModelAbsoluteTolerance), glazingRatio, windowMesh.Faces.GetFaceCenter(faceNum))[0])
        else:
            glzSrf.append(createGlazingTri(rc.Geometry.Brep.CreateFromCornerPoints(srfVertList[face[0]], srfVertList[face[1]], srfVertList[face[2]], sc.doc.ModelAbsoluteTolerance), glazingRatio, windowMesh.Faces.GetFaceCenter(faceNum))[0])
    
    return glzSrf


def createGlazingForRect(rectBrep, glazingRatio, windowHeight, sillHeight, breakUpDist, splitGlzVertDist, conversionFactor):
    #Define a default window height, sill height, breakup distance and vertical glazing dist of windows.
    if windowHeight != None: winHeight = windowHeight
    else: winHeight = 2
    winHeight = winHeight/conversionFactor
    if sillHeight != None: silHeight = sillHeight
    else: silHeight = 0.8
    silHeight = silHeight/conversionFactor
    if breakUpDist != None: distBreakup = breakUpDist
    else: distBreakup = 2
    distBreakup = distBreakup/conversionFactor
    if splitGlzVertDist != None: splitVertDist = splitGlzVertDist
    else: splitVertDist = 0
    splitVertDist = splitVertDist/conversionFactor
    
    
    if rectBrep:
        #Calculate the target area to make the glazing.
        targetArea = (rc.Geometry.AreaMassProperties.Compute(rectBrep).Area) * glazingRatio
        
        #Find the maximum acceptable area for breaking up the window into smaller, taller windows.
        rectBtmCurve = getTopBottomCurves(rectBrep)[0]
        rectTopCurve = getTopBottomCurves(rectBrep)[2]
        maxAreaBreakUp = (rectBtmCurve.GetLength() * 0.98) * winHeight
        
        #Find the maximum acceptable area for setting the glazing at the sill height.
        heightClosestPt = rc.Geometry.Curve.PointAt(rectTopCurve, rc.Geometry.LineCurve.ClosestPoint(rectTopCurve, rectBtmCurve.PointAtEnd)[1])
        rectHeight = rc.Geometry.Point3d.DistanceTo(heightClosestPt, rectBtmCurve.PointAtEnd)
        rectHeightVec = rc.Geometry.Vector3d(heightClosestPt.X - rectBtmCurve.PointAtEnd.X, heightClosestPt.Y - rectBtmCurve.PointAtEnd.Y, heightClosestPt.Z - rectBtmCurve.PointAtEnd.Z)
        maxWinHeightSill = rectHeight - silHeight
        
        #If the window height given from the formulas above is greater than the height of the wall, set the window height to be just under that of the wall.
        if winHeight > (0.98 * rectHeight): winHeightFinal = (0.98 * rectHeight)
        else: winHeightFinal = winHeight
        
        #If the sill height given from the formulas above is less than 1% of the wall height, set the sill height to be 1% of the wall height.
        if silHeight < (0.01 * rectHeight): silHeightFinal = (0.01 * rectHeight)
        else: silHeightFinal = silHeight
        
        #Find the window geometry in the case that the target area is below that of the maximum acceptable area for breaking up the window into smaller, taller windows.
        if targetArea < maxAreaBreakUp:
            #Divide up the rectangle into points on the bottom.
            rectBtmCurveLength = rectBtmCurve.GetLength()
            if rectBtmCurveLength > (distBreakup/2):
                numDivisions = round(rectBtmCurveLength/distBreakup, 0)
            else:
                numDivisions = 1
            
            btmDivPts = []
            rectBtmCurve.Reverse() 
            
            #print numDivisions
            for parameter in rectBtmCurve.DivideByCount(numDivisions, True):
                btmDivPts.append(rc.Geometry.Curve.PointAt(rectBtmCurve, parameter))
            
            #Connect the points to form lines to be used to generate the windows
            winLinesStart = []
            ptIndex = 0
            for point in btmDivPts:
                if ptIndex < numDivisions:
                    winLinesStart.append(rc.Geometry.Line(point, btmDivPts[ptIndex+1]))
                    ptIndex += 1
            
            #Move the lines to the appropriate sill height.
            sillUnitVec = rectHeightVec
            sillUnitVec.Unitize()
            
            maxSillHeight = (rectHeight*0.99) - winHeightFinal
            if silHeightFinal < maxSillHeight: sillVec = rc.Geometry.Vector3d.Multiply(silHeightFinal, sillUnitVec)
            else: sillVec = rc.Geometry.Vector3d.Multiply(maxSillHeight, sillUnitVec)
            
            transformMatrix = rc.Geometry.Transform.Translation(sillVec)
            
            for line in winLinesStart:
                rc.Geometry.Line.Transform(line, transformMatrix)
            
            #Scale the lines to their center points based on the width that they need to be to satisfy the glazing ratio.
            lineCentPt = []
            for line in winLinesStart:
                lineCentPt.append(line.PointAt(0.5))
            
            winLineBaseLength = winLinesStart[0].Length
            winLineReqLength = (targetArea / winHeightFinal) / numDivisions
            winLineScale = winLineReqLength / winLineBaseLength
            
            centPtIndex = 0
            for line in winLinesStart:
                transformMatrixScale = rc.Geometry.Transform.Scale(lineCentPt[centPtIndex], winLineScale)
                line.Transform(transformMatrixScale)
                centPtIndex += 1
            
            #Find the maximum acceptable area for splitting the glazing vertically.
            maxSplitVert = rectHeight - silHeightFinal - winHeightFinal - (0.02*rectHeight)
            #If the splitVertDist is beyond the maximum acceptable, set it to this maximum.
            if splitVertDist < 0 or maxSplitVert < 0: splitVertDist = 0
            elif splitVertDist != 0 and splitVertDist > maxSplitVert: splitVertDist = maxSplitVert
            
            #If there is a non-zero vertical breakup dist and the value is less than the maximum accpetable, break up the window surface verticaly.
            if splitVertDist != 0:
                #Extrude the lines to create the windows
                extruUnitVec = rectHeightVec
                extruUnitVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, (winHeightFinal/2))
                vertMovingVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, (winHeightFinal/2)+splitVertDist)
                vertMovingTransform = rc.Geometry.Transform.Translation(vertMovingVec)
                finalWinSrfs = []
                for line in winLinesStart:
                    finalWinSrfs.append(rc.Geometry.Surface.CreateExtrusion(line.ToNurbsCurve(), extruVec))
                    line.Transform(vertMovingTransform)
                    finalWinSrfs.append(rc.Geometry.Surface.CreateExtrusion(line.ToNurbsCurve(), extruVec))
            else:
                #Extrude the lines to create the windows
                extruUnitVec = rectHeightVec
                extruUnitVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, winHeightFinal)
                finalWinSrfs = []
                for line in winLinesStart:
                    finalWinSrfs.append(rc.Geometry.Surface.CreateExtrusion(line.ToNurbsCurve(), extruVec))
            
            rectWinBreps=[]
            for srf in finalWinSrfs:
                rectWinBreps.append(rc.Geometry.Surface.ToBrep(srf))
        
        
        #Find the window geometry in the case that the target area is above that of the maximum acceptable area for breaking up the window in which case we have to make one big window.
        if targetArea > maxAreaBreakUp:
            #Move the bottom curve of the window to the appropriate sill height.
            sillUnitVec = rectHeightVec
            sillUnitVec.Unitize()
            
            rectBtmCurveLength = rectBtmCurve.GetLength()
            maxSillHeight = (rectHeight*0.99) - (targetArea / (rectBtmCurveLength * 0.98))
            
            if silHeightFinal < maxSillHeight:
                sillVec = rc.Geometry.Vector3d.Multiply(silHeightFinal, sillUnitVec)
            else:
                sillVec = rc.Geometry.Vector3d.Multiply(maxSillHeight, sillUnitVec)
            
            #Move the window to the sill height.
            transformMatrix = rc.Geometry.Transform.Translation(sillVec)
            winStartLine = rectBtmCurve
            rc.Geometry.NurbsCurve.Transform(winStartLine, transformMatrix)
            
            #Scale the curve so that it is not touching the edges of the surface.
            lineCentPt = rc.Geometry.Point3d(((winStartLine.PointAtStart.X + winStartLine.PointAtEnd.X)/2), ((winStartLine.PointAtStart.Y + winStartLine.PointAtEnd.Y)/2), ((winStartLine.PointAtStart.Z + winStartLine.PointAtEnd.Z)/2))
            
            transformMatrixScale = rc.Geometry.Transform.Scale(lineCentPt, 0.98)
            winStartLine.Transform(transformMatrixScale)
            
            #Find the maximum acceptable area for splitting the glazing vertically.
            maxSplitVert = rectHeight - silHeightFinal - (targetArea / (rectBtmCurveLength * 0.98)) - (0.02*rectHeight)
            #If the splitVertDist is beyond the maximum acceptable, set it to this maximum.
            if splitVertDist < 0 or maxSplitVert < 0: splitVertDist = 0
            elif splitVertDist != 0 and splitVertDist > maxSplitVert: splitVertDist = maxSplitVert
            
            if splitVertDist != 0:
                #Extrude the line to create the window
                extruUnitVec = rectHeightVec
                extruUnitVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, (targetArea / (rectBtmCurveLength * 0.98))/2)
                vertMovingVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, ((targetArea / (rectBtmCurveLength * 0.98))/2)+splitVertDist)
                vertMovingTransform = rc.Geometry.Transform.Translation(vertMovingVec)
                finalWinSrf1 = rc.Geometry.Surface.CreateExtrusion(winStartLine.ToNurbsCurve(), extruVec)
                winStartLine.Transform(vertMovingTransform)
                finalWinSrf2 = rc.Geometry.Surface.CreateExtrusion(winStartLine.ToNurbsCurve(), extruVec)
                rectWinBreps = [rc.Geometry.Surface.ToBrep(finalWinSrf1), rc.Geometry.Surface.ToBrep(finalWinSrf2)]
            else:
                #Extrude the line to create the window
                extruUnitVec = rectHeightVec
                extruUnitVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(extruUnitVec, (targetArea / (rectBtmCurveLength * 0.98)))
                finalWinSrf = rc.Geometry.Surface.CreateExtrusion(winStartLine, extruVec)
                rectWinBreps = [rc.Geometry.Surface.ToBrep(finalWinSrf)]
    
    else:
        rectWinBreps = []
    return rectWinBreps


def createGlazingThatContainsRectangle(topEdge, btmEdge, baseSrf, glazingRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor):
    #Get the rectangle vertices points from the arrangement of closest points of the top and bottom curves.
    rectPt1 = rc.Geometry.Curve.PointAt(topEdge, rc.Geometry.LineCurve.ClosestPoint(topEdge, btmEdge.PointAtEnd)[1])
    rectPt2 = rc.Geometry.Curve.PointAt(btmEdge, rc.Geometry.LineCurve.ClosestPoint(btmEdge, topEdge.PointAtEnd)[1])
    rectPt3 = rc.Geometry.Curve.PointAt(topEdge, rc.Geometry.LineCurve.ClosestPoint(topEdge, btmEdge.PointAtStart)[1])
    rectPt4 = rc.Geometry.Curve.PointAt(btmEdge, rc.Geometry.LineCurve.ClosestPoint(btmEdge, topEdge.PointAtStart)[1])
    
    #Create the rectangle
    rectPlane = rc.Geometry.Plane(rectPt4, rectPt2, rectPt3)
    rect = rc.Geometry.Rectangle3d(rectPlane, rectPt2, rectPt1)
    rectBrep = rc.Geometry.Brep.CreateFromCornerPoints(rectPt1, rectPt3, rectPt2, rectPt4, sc.doc.ModelAbsoluteTolerance)
    
    
    def areEdgesLinear(brepList):
        for srf in brepList:
            for edge in srf.Edges:
                if not edge.IsLinear():
                    return False       
        return True
        
    #Split the base surface with the rectangle
    if rectBrep:
        srfSplit = rc.Geometry.Brep.Split(baseSrf, rectBrep, sc.doc.ModelAbsoluteTolerance)
        # make sure split doesn't generate curves shapes!
        # happens for some strange surfaces:
        # https://github.com/mostaphaRoudsari/Honeybee/issues/115
        if srfSplit!=[] and not areEdgesLinear(srfSplit): srfSplit =[]
    
    else:
        srfSplit = []
    
    if len(srfSplit) == 0:
        if rectBrep:
            srfSplit = [baseSrf]
        else:
            srfSplit = []
            middle = []
            sides = []
    
    #Determine which Breps are rectangular and which are not by testing their angles and number of sides.
    middle = []
    sides = []
    for srf in srfSplit:
        edges = srf.Edges
        joinedEdges = rc.Geometry.Curve.JoinCurves(edges)[0]
        joinedEdges = cleanCurve(joinedEdges)
        simplificationOpt = rc.Geometry.CurveSimplifyOptions.All
        joinedEdgesSimplified = joinedEdges.Simplify(simplificationOpt, sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAngleToleranceRadians)
        try:
            reconstructSrf = rc.Geometry.Brep.CreatePlanarBreps(joinedEdgesSimplified)[0]
        except:
            reconstructSrf = srf
        
        # On some systems there was an error with using Brep.Vertices
        # I assume this should be an issue with one of Rhinocommon versions
        # Hopefully this will fix it - 
        vertices = reconstructSrf.DuplicateVertices()
        angle1 = rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(vertices[0]), rc.Geometry.Vector3d(vertices[1])), rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(vertices[0]), rc.Geometry.Vector3d(vertices[len(vertices) - 1])))
        angle2 = rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(vertices[1]), rc.Geometry.Vector3d(vertices[2])), rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(vertices[1]), rc.Geometry.Vector3d(vertices[0])))
        numSides = reconstructSrf.Edges.Count
        rectBool = reconstructSrf.IsValid
        
        if rectBool and numSides == 4 and angle1 < 1.570796 + sc.doc.ModelAngleToleranceRadians and angle1 > 1.570796 - sc.doc.ModelAngleToleranceRadians and angle2 < 1.570796 + sc.doc.ModelAngleToleranceRadians and angle2 > 1.570796 - sc.doc.ModelAngleToleranceRadians:
            middle.append(reconstructSrf)
        else:
            sides.append(reconstructSrf)
    
    #Generate glazing for the non-rectangular surfaces.
    sideGlaz = []
    for srf in sides:
        if srf.Edges.Count == 3:
            sideGlaz.append(createGlazingTri(srf, glazingRatio, None))
        elif srf.Edges.Count == 4:
            sideGlaz.append(createGlazingQuad(srf, glazingRatio, None))
        else:
            sideGlaz.append(createGlazingOddPlanarGeo(srf, glazingRatio))
    
    #Find the glazing for the rectangle part of the wall
    rectWinBreps = []
    if breakUpWindow == True:
        for rect in middle:
            rectWinBreps.append(createGlazingForRect(rect, glazingRatio, windowHeight, sillHeight, breakUpDist, splitVertDist, conversionFactor))
    else:
        for rect in middle:
            rectWinBreps.append(createGlazingQuad(rect, glazingRatio, None))
    
    #Add all of the glazings together into one list.
    glzSrf = []
    for item in rectWinBreps:
        for window in item:
            glzSrf.append(window)
    for item in sideGlaz:
        for window in item:
            glzSrf.append(window)
    
    #If the surface failed to split and there was no rectangle, chances are that the surface is really oblique so I should get the glazing using the quad function or odd geo function. 
    if len(srfSplit) == 0 and rectBrep == None:
        try:
            glzSrf = createGlazingQuad(baseSrf, glazingRatio, None)
        except:
            glzSrf = createGlazingOddPlanarGeo(baseSrf, glazingRatio)
    
    return glzSrf

def createSkylightGlazing(baseSrf, glazingRatio, planarBool, edgeLinear, breakUpWindow, breakUpDist, conversionFactor):
    if breakUpWindow == True or breakUpWindow == None:
        #Define the meshing paramters to break down the surface in a manner that produces only trinagles and quads.
        meshPar = rc.Geometry.MeshingParameters.Default
        
        #Define the grid size break down based on the model units.
        if breakUpDist != None: distBreakup = breakUpDist
        else: distBreakup = 3
        distBreakup = distBreakup/conversionFactor
        
        meshPar.MinimumEdgeLength = (distBreakup)
        meshPar.MaximumEdgeLength = (distBreakup*2)
        
        #Create a mesh of the base surface.
        windowMesh = rc.Geometry.Mesh.CreateFromBrep(baseSrf, meshPar)[0]
        
        #Define all of the vairables that will be used in the following steps
        glzSrf = []
        srfFaceList = windowMesh.Faces
        srfVertList = windowMesh.Vertices
        curvedOk = True
        lastSuccessfulRestOfSrf = []
        
        #If the surface is curved, check to see if all of the faces are quads, in which case, the generated glazing should look pretty nice.  Otherwise, abandon this method and use the offset algorithm.
        if planarBool == False:
            for face in srfFaceList:
                if face.IsQuad == True: pass
                else: curvedOk = False
            if curvedOk == False:
                glzSrf, lastSuccessfulRestOfSrf = createGlazingCurved(baseSrf, glazingRatio, planarBool)
            else: pass
        else:pass
        
        #Create breps of all of the mesh faces and use them to make each window.
        if curvedOk == True:
            for faceNum, face in enumerate(srfFaceList):
                if face.IsQuad == True:
                    glzSrf.append(createGlazingQuad(rc.Geometry.Brep.CreateFromCornerPoints(srfVertList[face[0]], srfVertList[face[1]], srfVertList[face[2]], srfVertList[face[3]], sc.doc.ModelAbsoluteTolerance), glazingRatio, windowMesh.Faces.GetFaceCenter(faceNum))[0])
                else:
                    glzSrf.append(createGlazingTri(rc.Geometry.Brep.CreateFromCornerPoints(srfVertList[face[0]], srfVertList[face[1]], srfVertList[face[2]], sc.doc.ModelAbsoluteTolerance), glazingRatio, windowMesh.Faces.GetFaceCenter(faceNum))[0])
        
        #If the surface is curved and has not been generated using the offset method, project the quad breps onto the curved surface and split it.
        if planarBool == False and curvedOk == True:
            faceNormals = []
            curvedGlz = []
            surface = baseSrf.Faces[0]
            
            for faceNum, face in enumerate(srfFaceList):
                facePlane = rc.Geometry.Plane(srfVertList[face[0]], srfVertList[face[1]], srfVertList[face[2]])
                faceNormals.append(facePlane.Normal)
            for srfNum, srf in enumerate(glzSrf):
                edges = srf.Edges
                edge = rc.Geometry.Curve.JoinCurves(edges)
                projectEdge = rc.Geometry.Curve.ProjectToBrep(edge, [baseSrf], faceNormals[srfNum], sc.doc.ModelAbsoluteTolerance)[0]
                projectBrep = surface.Split([projectEdge], sc.doc.ModelAbsoluteTolerance)
                splSurface = projectBrep.Faces.ExtractFace(1)
                curvedGlz.append(splSurface)
            glzSrf = curvedGlz
    else:
        #Check to see if it is a triangle for which we can use a simple mathematical relation.
        if planarBool == True and baseSrf.Edges.Count == 3:
            glzSrf = createGlazingTri(baseSrf, glazingRatio, None)
            lastSuccessfulRestOfSrf = []
        
        #Since the surface does not seem to have a rectangle and is not a triangle, check to see if it is a just an odd-shaped quarilateral for which we can use a mathematical relation.
        elif planarBool == True and edgeLinear == True and baseSrf.Edges.Count == 4:
            glzSrf = createGlazingQuad(baseSrf, glazingRatio, None)
            lastSuccessfulRestOfSrf = []
        
        #Since the surface does not have a rectangle, is not a triangle, and is not a quadrilateral but still may be planar, we will break it into triangles and quads by meshing it such that we can use the previous formulas.
        elif planarBool == True and edgeLinear == True and breakUpWindow == True:
            glzSrf = createGlazingOddPlanarGeo(baseSrf, glazingRatio)
            lastSuccessfulRestOfSrf = []
        
        #If everything has failed up until this point, this means that the wall geometry is likely curved.  The best way forward is just to try to offset the curve on the surface to get the window.
        else:
            glzSrf, lastSuccessfulRestOfSrf = createGlazingCurved(baseSrf, glazingRatio, planarBool)
    
    
    return glzSrf, lastSuccessfulRestOfSrf


def createGlazingCurved(baseSrf, glzRatio, planar):
    
    def getOffsetDist(cenPt, edges):
        distList = []
        [distList.append(cenPt.DistanceTo(edge.PointAtNormalizedLength(0.5))) for edge in edges]
        return min(distList)/2
    
    def getAreaAndCenPt(surface):
        MP = rc.Geometry.AreaMassProperties.Compute(surface)
        if MP:
            area = MP.Area
            centerPt = MP.Centroid
            MP.Dispose()
            bool, centerPtU, centerPtV = surface.Faces[0].ClosestPoint(centerPt)
            normalVector = surface.Faces[0].NormalAt(centerPtU, centerPtV)
            return area, centerPt, normalVector
        else: return None, None, None
    
    
    def OffsetCurveOnSurface(border, glazingBrep, offsetDist, normalvector, planar):
        success = False
        glzArea = 0
        direction = 1
        splittedSrfs = []
        
        # Offset the curves on the surface with RhinoCommon
        surface = glazingBrep.Faces[0]
        glzCurve = border.OffsetOnSurface(surface, offsetDist, sc.doc.ModelAbsoluteTolerance)
        if glzCurve==None:
            glzCurve = border.OffsetOnSurface(surface, -offsetDist, sc.doc.ModelAbsoluteTolerance)
            direction = -1
        
        if glzCurve!=None:
            splitBrep = surface.Split(glzCurve, sc.doc.ModelAbsoluteTolerance)
            
            for srfCount in range(splitBrep.Faces.Count):
                splSurface = splitBrep.Faces.ExtractFace(srfCount)
                splittedSrfs.append(splSurface)
                edges = splSurface.DuplicateEdgeCurves(True)
                joinedEdges = rc.Geometry.Curve.JoinCurves(edges)
                
                if len(joinedEdges) == 1:
                    glzSrf = splSurface
                    glzArea = glzSrf.GetArea()
                    success = True
        else:
            print "Offseting boundary and spliting the surface failed!"
            splittedSrfs = None
            success = False
            
        
        return success, glzArea, glzCurve, splittedSrfs
    
    
    face = baseSrf
    edges = face.DuplicateEdgeCurves(True)
    border = rc.Geometry.Curve.JoinCurves(edges)[0]
    area, cenPt, normalvector = getAreaAndCenPt(face)
    targetArea = area * glzRatio
    offsetDist = getOffsetDist(cenPt, edges)
    
    i = 0
    glzArea = 2 * targetArea
    inwardDirection = 1 #define the inward direction for the surface
    success = False
    
    lastSuccessfulGlzSrf = None
    lastSuccessfulRestOfSrf = None
    lastSuccessfulSrf = None
    lastSuccessfulArea = area
    srfs = []
    
    
    try: coordinatesList = baseSrf.Vertices
    except: coordinatesList = baseSrf.DuplicateVertices()
    
    succ, glzArea, glzCurve, splittedSrfs = OffsetCurveOnSurface(border, face, offsetDist, normalvector, planar)
    if succ == False:
        pass
    else:
        while abs(targetArea-glzArea) > 0.01 * targetArea and i < 20:
            i += 1
            succ, glzArea, glzCurve, splittedSrfs = OffsetCurveOnSurface(border, face, offsetDist, normalvector, planar)
            if targetArea < glzArea:
                offsetDist = offsetDist + (offsetDist/(2*i))
            else:
                offsetDist = offsetDist - (offsetDist/(2*i))
            
            if succ:
                srfs.append(splittedSrfs)
                try:
                    lastSuccessfulGlzSrf = splittedSrfs[1]
                    lastSuccessfulRestOfSrf = splittedSrfs[0]
                    lastSuccessfulArea = glzArea
                except Exception, e:
                    lastSuccessfulGlzSrf = None
                    lastSuccessfulRestOfSrf = None
                    lastSuccessfulArea = 0
                    
    
    return lastSuccessfulGlzSrf, lastSuccessfulRestOfSrf


def findGlzBasedOnRatio(baseSrf, glzRatio, windowHeight, sillHeight, surfaceType, breakUpWindow, breakUpDist, splitVertDist, conversionFactor):
    lastSuccessfulRestOfSrf = []
    
    #Check if the surface is a planar surface
    planarBool = rc.Geometry.BrepFace.IsPlanar(baseSrf.Faces[0], sc.doc.ModelAbsoluteTolerance)
    
    #Rebuild and simplify the surface to ensure best results when generating the glazing.
    edgeLinear = True
    createdNew = False
    edges = baseSrf.Edges
    joinedEdges = rc.Geometry.Curve.JoinCurves(edges)
    simplificationOpt = rc.Geometry.CurveSimplifyOptions.All
    
    joinedEdgesSimplified = []
    for crv in joinedEdges:
        joinedEdgesSimplified.append(crv.Simplify(simplificationOpt, sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAngleToleranceRadians))
    
    originalSrfDir = baseSrf.Faces[0].NormalAt(0,0)
    if planarBool == True:
        try:
            baseSrf = rc.Geometry.Brep.CreatePlanarBreps(joinedEdgesSimplified)[0]
            createdNew = True
        except:
            createdNew = False
    newSrfDir = baseSrf.Faces[0].NormalAt(0,0)
    
    #If the direction of the rebuilt surface is not the same as that of the original surface, flip it around.
    if createdNew == True:
        if newSrfDir.X < originalSrfDir.X + tol and newSrfDir.X > originalSrfDir.X - tol and newSrfDir.Y < originalSrfDir.Y + tol and newSrfDir.Y > originalSrfDir.Y - tol and newSrfDir.Z < originalSrfDir.Z + tol and newSrfDir.Z > originalSrfDir.Z - tol:
            pass
        else:
            baseSrf.Flip()
    else: pass
    
    
    #Check if the surface has any curved edges to it
    for crv in joinedEdgesSimplified:
        if crv != None:
            for edge in crv.DuplicateSegments():
                if rc.Geometry.BrepEdge.IsLinear(edge, sc.doc.ModelAbsoluteTolerance):
                    pass
                else:
                    edgeLinear = False
        else: pass
    
    #Check if the surface is a planar skylight that can be broken up into quads and, if so, send it through the skylight generator
    if surfaceType == 1:
        glazing, lastSuccessfulRestOfSrf = createSkylightGlazing(baseSrf, glzRatio, planarBool, edgeLinear, breakUpWindow, breakUpDist, conversionFactor)
    
    #Check if the wall surface has horizontal top and bottom curves and contains a rectangle that can be extracted such that we can apply the windowHeight and sillHeight inputs to it.
    elif surfaceType == 0 and planarBool == True and edgeLinear == True and getTopBottomCurves(baseSrf)[1] == True and getTopBottomCurves(baseSrf)[3] == True:
        if breakUpWindow == False and baseSrf.Edges.Count == 4:
            glazing = createGlazingQuad(baseSrf, glzRatio, None)
        else:
            glazing = createGlazingThatContainsRectangle(getTopBottomCurves(baseSrf)[2], getTopBottomCurves(baseSrf)[0], baseSrf, glzRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor)
    
    #Check if the wall surface has vertical sides and contains a rectangle that can be extracted such that we can apply the windowheight and sill height inputs to it.
    elif surfaceType == 0 and planarBool == True and edgeLinear == True and getTopBottomCurves(baseSrf)[5] == True:
        if breakUpWindow == False and baseSrf.Edges.Count == 4:
            glazing = createGlazingQuad(baseSrf, glzRatio, None)
        else:
            glazing = createGlazingThatContainsRectangle(getTopBottomCurves(baseSrf)[4][0], getTopBottomCurves(baseSrf)[4][1], baseSrf, glzRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor)
    
    #Since the surface does not seem to have a rectangle that can be extracted, check to see if it is a triangle for which we can use a simple mathematical relation.
    elif surfaceType == 0 and planarBool == True and baseSrf.Edges.Count == 3:
        glazing = createGlazingTri(baseSrf, glzRatio, None)
    
    #Since the surface does not seem to have a rectangle and is not a triangle, check to see if it is a just an odd-shaped quarilateral for which we can use a mathematical relation.
    elif surfaceType == 0 and planarBool == True and edgeLinear == True and baseSrf.Edges.Count == 4:
        glazing = createGlazingQuad(baseSrf, glzRatio, None)
    
    #Since the surface does not have a rectangle, is not a triangle, and is not a quadrilateral but still may be planar, we will break it into triangles and quads by meshing it such that we can use the previous formulas.
    elif surfaceType == 0 and planarBool == True and edgeLinear == True and breakUpWindow == True:
        glazing = createGlazingOddPlanarGeo(baseSrf, glzRatio)
    
    #If the surface fits the criteria above but the user does not want to break up the window, we will offset the curve on the surface so that we hopefully end up with just one window.
    elif surfaceType == 0 and planarBool == True and edgeLinear == True:
        glazing, lastSuccessfulRestOfSrf = createGlazingCurved(baseSrf, glzRatio, planarBool)
    
    #If everything has failed up until this point, this means that the wall geometry is likely curved.  The best way forward is just to try to offset the curve on the surface to get the window.
    else:
        glazing, lastSuccessfulRestOfSrf = createGlazingCurved(baseSrf, glzRatio, planarBool)
    
    
    #Check to make sure that a window has been generated and, if so, check to make sure that the window that has been generated is facing the right direction.  If not, flip it.
    if glazing == None:
        print "Failed to calculate the glazing"
        pass
    else:
        try:
            len(glazing)
        except:
            glazing = [glazing]
        
        for window in glazing:
            windowDir = window.Faces[0].NormalAt(0,0)
            if windowDir.X < originalSrfDir.X + tol and windowDir.X > originalSrfDir.X - tol and windowDir.Y < originalSrfDir.Y + tol and windowDir.Y > originalSrfDir.Y - tol and windowDir.Z < originalSrfDir.Z + tol and windowDir.Z > originalSrfDir.Z - tol:
                pass
            else:
                window.Flip()
    
    def getRestOfSurfacePlanar(baseSrf, glazing):
        selfDir = baseSrf.Faces[0].NormalAt(0,0)
        glzCrvs = []
        for glzSrf in glazing:
            glzEdges = glzSrf.DuplicateEdgeCurves(True)
            jGlzCrv = rc.Geometry.Curve.JoinCurves(glzEdges)[0]
            glzCrvs.append(jGlzCrv)
        
        baseEdges = baseSrf.DuplicateEdgeCurves(True)
        
        jBaseCrv = rc.Geometry.Curve.JoinCurves(baseEdges)
        
        # convert array to list
        jBaseCrvList = []
        for crv in jBaseCrv: jBaseCrvList.append(crv)

        try:
            punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(glzCrvs + jBaseCrvList)
            
            if len(punchedGeometries)>1:
                crvDif = rc.Geometry.Curve.CreateBooleanDifference(jBaseCrvList[0], glzCrvs)
                punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(crvDif)
            
            punchedGeometryDir = punchedGeometries[0].Faces[0].NormalAt(0,0)
            if punchedGeometryDir.X < selfDir.X + tol and punchedGeometryDir.X > selfDir.X - tol and punchedGeometryDir.Y < selfDir.Y + tol and punchedGeometryDir.Y > selfDir.Y - tol and punchedGeometryDir.Z < selfDir.Z + tol and punchedGeometryDir.Z > selfDir.Z - tol:
                pass
            else: punchedGeometries[0].Flip()
            
            return punchedGeometries[0]
                
        except Exception, e:
            return []
            print "failed to calculate opaque part of the surface:\n" + `e`
        
    
    if lastSuccessfulRestOfSrf==[]:
        lastSuccessfulRestOfSrf = getRestOfSurfacePlanar(baseSrf, glazing)
    
    return glazing, lastSuccessfulRestOfSrf

def giveWarning(message):
    print message
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, message)

def main(windowHeight, sillHeight, glzRatio, skyLightRatio, breakUpWindow, breakUpDist, splitGlzVertDist):
    # check if honeybee is flying
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            " Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return [], []
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBObjects)
    
    #Get the conversion factor (for the future when HB is availble in other model units).
    conversionFactor = lb_preparation.checkUnits()
    
    #Set the final lists to be filled.
    joinedSrf = []
    zonesWithOpeningsGeometry =[]
    ModifiedHBZones = []
    
    #Check if the length of the glzRatio, windowHeight, and sillHeight lists are the same.
    numOfDivisions = []
    warningList = []
    listLenCheck = True
    
    if len(glzRatio) == 1:
        if len(windowHeight) != 1 and len(windowHeight) != 0: numOfDivisions.append(len(windowHeight))
        if len(sillHeight) != 1 and len(sillHeight) != 0: numOfDivisions.append(len(sillHeight))
        if len(breakUpDist) != 1 and len(breakUpDist) != 0: numOfDivisions.append(len(breakUpDist))
        if len(breakUpWindow) != 1 and len(breakUpWindow) != 0: numOfDivisions.append(len(breakUpWindow))
        if len(splitGlzVertDist) != 1 and len(splitGlzVertDist) != 0: numOfDivisions.append(len(splitGlzVertDist))
        if numOfDivisions != []:
            allValuesSame = True
            for val in numOfDivisions:
                if val == numOfDivisions[0]: pass
                else: allValuesSame = False
            if allValuesSame == True:
                glzRatioNew = []
                #duplicate the glazing ratio list.
                for val in range(numOfDivisions[-1]): glzRatioNew.append(glzRatio[0])
                glzRatio = glzRatioNew
            else:
                listLenCheck = False
                warning = "The lengths of the lists across your inputs do not match.  Please ensure that you put in only one value for each paremter or your values are lists with lengths that match across your inputs."
                giveWarning(warning)
    else:
        if len(windowHeight) != len(glzRatio) and len(windowHeight) != 1 and len(windowHeight) != 0: warningList.append("The number of items in the windowHeight list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single windowHeight value for all windows.")
        if len(sillHeight) != len(glzRatio) and len(sillHeight) != 1 and len(sillHeight) != 0: warningList.append("The number of items in the sillHeight list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single sillHeight value for all windows.")
        if len(breakUpDist) != len(glzRatio) and len(breakUpDist) != 1 and len(breakUpDist) != 0: warningList.append("The number of items in the breakUpDist list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single breakUpDist value for all windows.")
        if len(breakUpWindow) != len(glzRatio) and len(breakUpWindow) != 1 and len(breakUpWindow) != 0: warningList.append("The number of items in the breakUpWindow list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single breakUpWindow value for all windows.")
        if len(splitGlzVertDist) != len(glzRatio) and len(splitGlzVertDist) != 1 and len(splitGlzVertDist) != 0: warningList.append("The number of items in the splitGlzVertDist list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single splitGlzVertDist value for all windows.")
        if warningList != []:
            for warning in warningList:
                giveWarning(warning)
                listLenCheck = False
    
    # find the percentage of glazing for each direction based on the input list
    angles = []
    if len(glzRatio)!=0:
        for ratio in glzRatio:
            if ratio > 0.95:
                giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are not accepted.")
                return None, None
        initAngles = rs.frange(0, 360, 360/len(glzRatio))
    else: initAngles = []
    #Set up angles if the glazing ratio is greater than 1.
    if len(glzRatio) > 1:
        for an in initAngles: angles.append(an-(360/(2*len(glzRatio))))
        angles.append(360)
    else: angles = initAngles
    
    if HBZoneObjects and HBZoneObjects[0] != None and listLenCheck == True:
        # collect the surfaces
        HBSurfaces = []
        for HBObj in HBZoneObjects:
            if HBObj.objectType == "HBZone":
                for surface in HBObj.surfaces: HBSurfaces.append(surface)
            elif HBObj.objectType == "HBSurface":
                
                if not hasattr(HBObj, 'type'):
                    # find the type based on 
                    HBObj.type = HBObj.getTypeByNormalAngle()
                
                if not hasattr(HBObj, 'angle2North'):
                    # find the type based on
                    HBObj.getAngle2North()
                
                if not hasattr(HBObj, "BC"):
                    HBObj.BC = 'OUTDOORS'
                    
                HBSurfaces.append(HBObj)
                
        
        for surface in HBSurfaces:
            # print surface
            if surface.hasChild:
                surface.removeAllChildSrfs()
            targetPercentage = 0
            winHeight = None
            sill = None
            breakD = None
            breakWind = True #Best variable name ever!
            splitVertDist = None
            if surface.type == 0:
                srfType = 0
                if len(glzRatio) == 1: targetPercentage = glzRatio[0]
                if len(windowHeight) == 1: winHeight = windowHeight[0]
                if len(sillHeight) == 1: sill = sillHeight[0]
                if len(breakUpDist) == 1: breakD = breakUpDist[0]
                if len(breakUpWindow) == 1: breakWind = breakUpWindow[0]
                if len(splitGlzVertDist) == 1: splitVertDist = splitGlzVertDist[0]
                for angleCount in range(len(angles)-1):
                    if angles[angleCount]+(0.5*sc.doc.ModelAngleToleranceDegrees) <= surface.angle2North%360 <= angles[angleCount +1]+(0.5*sc.doc.ModelAngleToleranceDegrees):
                        #print surface.angle2North%360
                        targetPercentage = glzRatio[angleCount%len(glzRatio)]
                        if len(windowHeight) == len(glzRatio):
                            winHeight = windowHeight[angleCount%len(windowHeight)]
                        if len(sillHeight) == len(glzRatio):
                            sill = sillHeight[angleCount%len(sillHeight)]
                        if len(breakUpDist) == len(glzRatio):
                            breakD = breakUpDist[angleCount%len(breakUpDist)]
                        if len(breakUpWindow) == len(glzRatio):
                            breakWind = breakUpWindow[angleCount%len(breakUpWindow)]
                        if len(splitGlzVertDist) == len(glzRatio):
                            splitVertDist = splitGlzVertDist[angleCount%len(splitGlzVertDist)]
                        break
            elif surface.type == 1 and skyLightRatio:
                targetPercentage = skyLightRatio
                if breakUpSkylight_ != None: breakWind = breakUpSkylight_
                if skyLightBreakUpDist_ != None: breakD = skyLightBreakUpDist_
                srfType = 1
            
            if targetPercentage!=0 and surface.BC.upper() == 'OUTDOORS':
                face = surface.geometry # call surface geometry
                
                # This part of the code sends the parameters and surfaces to their respective methods of of galzing generation.  It is developed by Chris Mackey.
                lastSuccessfulGlzSrf, lastSuccessfulRestOfSrf = findGlzBasedOnRatio(face, targetPercentage, winHeight, sill, srfType, breakWind, breakD, splitVertDist, conversionFactor)
                
                if lastSuccessfulGlzSrf!= None:
                    if isinstance(lastSuccessfulGlzSrf, list):
                        for glzSrfCount, glzSrf in enumerate(lastSuccessfulGlzSrf):
                            fenSrf = hb_EPFenSurface(glzSrf, surface.num, surface.name + '_glz_' + `glzSrfCount`, surface, 5, lastSuccessfulRestOfSrf)
                            zonesWithOpeningsGeometry.append(glzSrf)
                            surface.addChildSrf(fenSrf)
                        if lastSuccessfulRestOfSrf==[]:
                            surface.calculatePunchedSurface()
                    else:
                        fenSrf = hb_EPFenSurface(lastSuccessfulGlzSrf, surface.num, surface.name + '_glz_0', surface, 5, lastSuccessfulRestOfSrf)
                        zonesWithOpeningsGeometry.append(lastSuccessfulGlzSrf)
                        surface.addChildSrf(fenSrf)
                        if lastSuccessfulRestOfSrf==[]: surface.calculatePunchedSurface()
            else:
                surface.hasChild = False
        #print HBZoneObjects
        #add zones to dictionary
        ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    return zonesWithOpeningsGeometry, ModifiedHBZones

if _runIt:
    results = main(windowHeight_, sillHeight_, _glzRatio, skyLightRatio_, breakUpWindow_, breakUpDist_, splitGlzVertDist_)
    if results!= -1:
        glazingSrf, HBObjWGLZ = results