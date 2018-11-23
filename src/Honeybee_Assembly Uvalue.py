#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to calculate the assembly U-Value for a window given an input window geometry, center of glass U-value, and frame+edge U-value.  This component can also add a frame to a EnergyPlus window construction that has the glass and spacing information.
-
Provided by Honeybee 0.0.64

    Args:
        _glazingSrf: A surface representing the window geomtry for which an assebly U-value is being calculated.  This should be the region of glass only (not frame) and it can be the same glazing geometry that is assigned to a Honeybee Zone for an energy simulation.
        _frameThickness: A number in Rhino model units representing the thickness of the window frame around the glazing surface. Specifically, this is the distance from where the glass starts to where the frame ends, projected into the plane of the glazing surface.
        _edgeThickness_: A number in Rhino model units that represents the distance from the start of the frame to the start of the 'center of glass' region of the window.  This 'edge of glass' zone typically has a U-Value that is higher than the rest of the glass. The default is set to 63.5 mm.
        _cogUvalue: A number representing the center of glass U-value for the glazing construction in SI units (W/m2-K).
        _jambUvalue: A number representing the U-value of the window frame+edge in SI units (W/m2-K).  If no value is input for the sillUvalue_ or headUvalue_ below, this input here will refer to all window frames of the calculated assembly.  Otherwise, it will refer to just the U-value of the jamb (sides of the window).
        sillUvalue_: A number representing the U-value of the window sill frame+edge in SI units (W/m2-K).  If no value is input here, this component will assume that the sill U-value is the same as the jamb above.
        headUvalue_: A number representing the U-value of the window head (top) frame+edge in SI units (W/m2-K).  If no value is input here, this component will assume that the head U-value is the same as the jamb above.
        glzConstruction_: An optional EnergyPlus window construction to which an EnergyPlus frame object will be added (matching the specification above). It is recommended that this be a construction from LBNL WINDOW that is imported with the "Honeybee_Import WINDOW IDF Report."  If no construction is input here, no glzConstrWFrame will be output from this component.
    Returns:
        readMe!:...
        assemblyUvalue: The U-Value of the entire window assembly in SI units (W/m2-K).  This U-value is per unit area of glass + frame, which is how assembly U-value is defined by ASHRAE and the building code.
        glzSrfUvalue: The assembly U-value normalized by the area of the input _glzSrf (W/m2-K).  In other words, this U-value is per unit area of glass only (not glass + frame).  This output is what should be plugged into the "Honeybee_EnergyPlus Window Material" component if using the assembly U-value in a Honeybee energy simulation.
        glzConstrWFrame: An EnergyPlus window construction that can be assigned to Honeybee Window Surfaces for EnergyPlus simulations.
        ---------------: ...
        cogSrf: A surface showing the region of the _glazingSrf that is interpreted as the Center of Glass.
        jambSrf: A surface showing the region of the _glazingSrf that is interpreted as the Jamb (or sides of the window).
        sillSrf: A surface showing the region of the _glazingSrf that is interpreted as the Sill.
        headSrf: A surface showing the region of the _glazingSrf that is interpreted as the Head (or top of the window).
"""


ghenv.Component.Name = 'Honeybee_Assembly Uvalue'
ghenv.Component.NickName = 'assemblyUvalue'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import copy
import math


w = gh.GH_RuntimeMessageLevel.Warning

def getSrfCenPtandNormal(surface):
    brepFace = surface.Faces[0]
    if brepFace.IsPlanar and brepFace.IsSurface:
        u_domain = brepFace.Domain(0)
        v_domain = brepFace.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = brepFace.PointAt(centerU, centerV)
        normalVector = brepFace.NormalAt(centerU, centerV)
    else:
        centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
        uv = brepFace.ClosestPoint(centroid)
        centerPt = brepFace.PointAt(uv[1], uv[2])
        normalVector = brepFace.NormalAt(uv[1], uv[2])
    
    return centerPt, normalVector

def getCurvePoints(curve):
    exploCurve = rc.Geometry.PolyCurve.DuplicateSegments(curve)
    individPts = []
    for line in exploCurve:
        individPts.append(line.PointAtStart)
    return individPts

#Define a function that cleans up curves by deleting out points that lie in a line and leaves the curved segments intact.  Also, have it delete out any segments that are shorter than the tolerance.
def cleanCurve(curve):
    curvePts = getCurvePoints(curve)
    tolerance = sc.doc.ModelAbsoluteTolerance
    
    #Test if any of the points lie in a line and use this to generate a new list of curve segments and points.
    newPts = []
    newSegments = []
    for pointCount, point in enumerate(curvePts):
        testLine = rc.Geometry.Line(point, curvePts[pointCount-2])
        if testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and len(newPts) == 0:
            newPts.append(curvePts[pointCount-1])
        elif testLine.DistanceTo(curvePts[pointCount-1], True) > tolerance and len(newPts) != 0:
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
    newCrv.MakeClosed(tolerance)
    
    #return the new curve and the list of points associated with it.
    return newCrv

def main(glazingSrf, frameThickness, edgeThickness, cogUvalue, jambUvalue, sillUvalue, headUvalue, glzConstruction, unitConverter, hb_EPObjectsAux):
    # Set a default edge thickness.
    if edgeThickness == None:
        edgeThickness = 63.5 / unitConverter
    if sillUvalue == None:
        sillUvalue = 0
    if headUvalue == None:
        headUvalue = 0
    
    # Check to be sure that there's only one surface per glazingSrf.
    if glazingSrf.Faces.Count > 1:
        warning = "_glazingSrf cannot have more than one surface.\n Deconstuct the brep into individual surfaces and re-connect them."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return-1
    
    # Define variables to use through the calculation.
    surface = glazingSrf.Faces[0]
    glzsurface = copy.deepcopy(glazingSrf)
    edges = glzsurface.DuplicateEdgeCurves(True)
    border = rc.Geometry.Curve.JoinCurves(edges)[0]
    
    # Check to be sure that the glazing surface is planar.
    if not surface.IsPlanar(sc.doc.ModelAbsoluteTolerance):
        warning = "_glazingSrf must be planar to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return-1
    planarGeo = True
    for segment in edges:
        if segment.IsLinear() == False:
            planarGeo = False
    if not planarGeo:
        warning = "_glazingSrf must not have any curved edges in order to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return-1
    
    # Get the curve that defines the border of the frame so that we can make edge+frame polygons.
    centerPt, normalVector = getSrfCenPtandNormal(glazingSrf)
    offsetPlane = rc.Geometry.Plane(centerPt, normalVector)
    if frameThickness != 0:
        frameCurve = border.Offset(offsetPlane, frameThickness, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)
        if frameCurve.Count == 1:
            frameCurve = frameCurve[0]
            frameCurve = cleanCurve(frameCurve)
        else:
            warning = "Offseting boundary for the window frame failed!"
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return-1
    else:
        frameCurve = border
    glzbrep = rc.Geometry.Brep.CreatePlanarBreps(frameCurve)[0]
    glzsurface = glzbrep.Faces[0]
    
    # Get the geometry of the center of glass.
    cogCurve = frameCurve.OffsetOnSurface(glzsurface, frameThickness+edgeThickness, sc.doc.ModelAbsoluteTolerance)
    if cogCurve!=None:
        splitBrep = glzsurface.Split(cogCurve, sc.doc.ModelAbsoluteTolerance)
        for srfCount in range(splitBrep.Faces.Count):
            cogSurface = splitBrep.Faces.ExtractFace(srfCount)
        cogCurve = cogCurve[0]
    else:
        warning = "Offseting boundary for the center of glass failed!"
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    
    # Loft curve segments to generate frame+ edge surfaces.
    failed = False
    try:
        if frameCurve.SegmentCount != cogCurve.SegmentCount:
            failed = True
    except:
        if frameCurve.SpanCount != cogCurve.SpanCount:
            failed = True
    if failed == True:
        warning = "Could not match the end of the frame to the center of glass segments"
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    exploFrameCurve = rc.Geometry.PolyCurve.DuplicateSegments(frameCurve)
    exploCogCurve = rc.Geometry.PolyCurve.DuplicateSegments(cogCurve)
    exploFramePts = [cr.PointAtStart for cr in exploFrameCurve]
    exploCogPts = [cr.PointAtStart for cr in exploCogCurve]
    edgeFrameBreps = []
    for i, crv in enumerate(exploFrameCurve):
        pt = exploFramePts[i]
        closePts = []
        for cgpt in exploCogPts:
            closePts.append(rc.Geometry.Point3d.DistanceTo(pt, cgpt))
        closesti= [x for _,x in sorted(zip(closePts,range(len(exploCogPts))))][0]
        edgeFrameBrep = rc.Geometry.Brep.CreateFromLoft([crv,exploCogCurve[closesti]], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
        edgeFrameBreps.append(edgeFrameBrep)
    
    # Sort the edge + frame surfaces into frame, edge and sill.
    jambSrf = []
    sillSrf = []
    headSrf = []
    windowCentroid = rc.Geometry.AreaMassProperties.Compute(cogSurface).Centroid
    zAxis = rc.Geometry.Vector3d.ZAxis
    for edgeSrf in edgeFrameBreps:
        edgeCentroid = rc.Geometry.AreaMassProperties.Compute(edgeSrf).Centroid
        directPt = rc.Geometry.Point3d.Subtract(edgeCentroid, windowCentroid)
        directVec = rc.Geometry.Vector3d(directPt)
        angleFromVert = math.degrees(rc.Geometry.Vector3d.VectorAngle(zAxis, directVec))
        if angleFromVert <= 45:
            headSrf.append(edgeSrf)
        elif 45 < angleFromVert < 135:
            jambSrf.append(edgeSrf)
        elif angleFromVert > 135:
            sillSrf.append(edgeSrf)
    
    # Compute the assembly U value assuming that the frame is part of the window area.
    totalAssemblyArea = rc.Geometry.AreaMassProperties.Compute(frameCurve).Area
    cogArea = rc.Geometry.AreaMassProperties.Compute(cogCurve).Area
    cogContrib = (cogArea*cogUvalue)/totalAssemblyArea
    assemUValue = cogContrib
    frameContribs = []
    frameAreas = []
    
    for brep in jambSrf:
        frameEdgeArea = rc.Geometry.AreaMassProperties.Compute(brep).Area
        frameEdgeContrib = (frameEdgeArea*jambUvalue)/totalAssemblyArea
        frameAreas.append(frameEdgeArea)
        frameContribs.append(frameEdgeContrib)
        assemUValue = assemUValue + frameEdgeContrib
    for brep in sillSrf:
        frameEdgeArea = rc.Geometry.AreaMassProperties.Compute(brep).Area
        if sillUvalue != 0:
            frameEdgeContrib = (frameEdgeArea*sillUvalue)/totalAssemblyArea
        else:
            frameEdgeContrib = (frameEdgeArea*jambUvalue)/totalAssemblyArea
        frameAreas.append(frameEdgeArea)
        frameContribs.append(frameEdgeContrib)
        assemUValue = assemUValue + frameEdgeContrib
    for brep in headSrf:
        frameEdgeArea = rc.Geometry.AreaMassProperties.Compute(brep).Area
        if headUvalue != 0:
            frameEdgeContrib = (frameEdgeArea*headUvalue)/totalAssemblyArea
        else:
            frameEdgeContrib = (frameEdgeArea*jambUvalue)/totalAssemblyArea
        frameAreas.append(frameEdgeArea)
        frameContribs.append(frameEdgeContrib)
        assemUValue = assemUValue + frameEdgeContrib
    
    # Correct the assembly U value so that it is per unit area of glazingSrf (excluding frame area).
    originalGlzSrfArea = rc.Geometry.AreaMassProperties.Compute(glazingSrf).Area
    areaRatio = totalAssemblyArea/originalGlzSrfArea
    glzSrfUvalue = assemUValue*areaRatio
    
    
    # If there's a glzConstruction_ connected, generate a new construction.
    framedGlzConstr = None
    if glzConstruction  != None:
        # Compute values needed for the EP frame object
        weightedFrameUvalue = (sum(frameContribs)*totalAssemblyArea)/sum(frameAreas)
        ratioToCog = weightedFrameUvalue/cogUvalue
        epFrameThick = (frameThickness / unitConverter) / 1000
        framedGlzConstr = str(glzConstruction) + "_Framed"
        
        # Create a copy of the glzConstruction_.
        constructionData = None
        if glzConstruction in sc.sticky ["honeybee_constructionLib"].keys():
            constructionData = sc.sticky ["honeybee_constructionLib"][glzConstruction]
        if constructionData!=None:
            numberOfLayers = len(constructionData.keys())
            constructionStr = constructionData[0] + ",\n"
            constructionStr =  constructionStr + "  " + glzConstruction + "_Framed,   !- name\n"
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ",   !- " +  constructionData[layer][1] + "\n"
                else:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ";   !- " +  constructionData[layer][1] + "\n\n"
            added, name = hb_EPObjectsAux.addEPObjectToLib(constructionStr, True)
            if not added:
                msg = name + " is not added to the project library!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
            else: print name + " is has been added to the project library!"
        else:
            warning = "Failed to find " + glzConstruction + " in library."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
        
        # Build the frame and divider object.
        frameStr = "WindowProperty:FrameAndDivider,\n" + \
            '\t' + str(glzConstruction) + "_Framed,  !- User Supplied Frame/Divider Name\n" + \
            '\t' + str(epFrameThick) + ",           !- Frame Width {m}\n" + \
            '\t' + ",                               !- Frame Outside Projection {m}\n" + \
            '\t' + ",                               !- Frame Insider Projection {m}\n" + \
            '\t' + str(weightedFrameUvalue) + ",    !- Frame Conductance {w/m2-K}\n" + \
            '\t' + str(ratioToCog) + ",             !- Ratio of Frame-Edge Glass Conductance to Center-of-glass Co\n" + \
            '\t' + "0.9,                            !- Frame Solar absorptance\n" + \
            '\t' + "0.9,                            !- Frame Visible absorptance\n" + \
            '\t' + "0.9,                            !- Frame Thermal hemispherical Emissivity\n" + \
            '\t' + ",                               !- Divider Type\n" + \
            '\t' + ",                               !- Divider Width {m}\n" + \
            '\t' + ",                               !- Number of Horizontal Dividers\n" + \
            '\t' + ",                               !- Number of Vertical Dividers\n" + \
            '\t' + ",                               !- Divider Outside Projection {m}\n" + \
            '\t' + ",                               !- Divider Insider Projection {m}\n" + \
            '\t' + ",                               !- Divider Conductance {w/m2-K}\n" + \
            '\t' + ",                               !- Ratio of Divider-Edge Glass Conductance to Center-Of-Glass\n" + \
            '\t' + ",                               !- Divider Solar Absorptance\n" + \
            '\t' + ",                               !- Divider Visible Absorptance\n" + \
            '\t' + ",                               !- Divider Thermal Hemispherical Emissivity\n" + \
            '\t' + ",                               !- Outside Reveal Solar Absorptance\n" + \
            '\t' + ",                               !- Inside Sill Depth (m)\n" + \
            '\t' + ",                               !- Inside Sill Solar Absorptance\n" + \
            '\t' + ",                               !- Inside Reveal Depth (m)\n" + \
            '\t' + ";                               !- Inside Reveal Solar Absorptance"
        
        added, name = hb_EPObjectsAux.addEPObjectToLib(frameStr, True)
        if not added:
            msg = name + " is not added to the project library!"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        else: print name + " is has been added to the project library!"
    
    
    
    return assemUValue, glzSrfUvalue, cogSurface, jambSrf, sillSrf, headSrf, framedGlzConstr



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

unitConverter = None
if initCheck == True:
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    unitConverter = lb_preparation.checkUnits()*1000


#If the intital check is good, run the component.
if initCheck and _jambUvalue != None and _cogUvalue != None and _glazingSrf != None and _frameThickness != None:
    result = main(_glazingSrf, _frameThickness, _edgeThickness_, _cogUvalue, _jambUvalue, sillUvalue_, headUvalue_, glzConstruction_, unitConverter, hb_EPObjectsAux)
    if result != -1:
        assemblyUvalue, glzSrfUvalue, cogSrf, jambSrf, sillSrf, headSrf, glzConstrWFrame = result