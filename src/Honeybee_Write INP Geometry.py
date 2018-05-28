# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
This is a component for translating the geometry of an OSM file to an EQuest INP file.

-
Provided by Ladybug 0.0.45
    
    Args:
        _osmFilePath: A file path of the an OpemStdio file
        _runIt: Set to "True" to have the component generate an INP file.
    Returns:
        report: Report!
        inpFileAddress: The address of the Equest inp file.
"""

ghenv.Component.Name = "Honeybee_Write INP Geometry"
ghenv.Component.NickName = 'Write INP'
ghenv.Component.Message = 'VER 0.0.62\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nJUL_24_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
import Rhino as rc
import System

def checkTheInputs(osmFileName):
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not os.path.isfile(osmFileName):
        msg = "OSM file does not exist in the specified location!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    if not osmFileName.lower().endswith('.osm'):
        msg = "OSM file is not a valid OSM!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    return True

def findDiscontinuity(curve, style):
    # copied and modified from rhinoScript (@Steve Baer @GitHub)
    """Search for a derivatitive, tangent, or curvature discontinuity in
    a curve object.
    Parameters:
      curve_id = identifier of curve object
      style = The type of continuity to test for. The types of
          continuity are as follows:
          Value    Description
          1        C0 - Continuous function
          2        C1 - Continuous first derivative
          3        C2 - Continuous first and second derivative
          4        G1 - Continuous unit tangent
          5        G2 - Continuous unit tangent and curvature
    Returns:
      List 3D points where the curve is discontinuous
    """
    dom = curve.Domain
    t0 = dom.Min
    t1 = dom.Max
    points = []
    get_next = True
    while get_next:
        get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
        if get_next:
            points.append(curve.PointAt(t))
            t0 = t # Advance to the next parameter
    return points

def isAntiClockWise(pts):
    faceNormal = rc.Geometry.Vector3d(0,0,1)
    def crossProduct(vector1, vector2):
        return vector1.X * vector2.X + vector1.Y * vector2.Y + vector1.Z * vector2.Z
    
    # check if the order if clock-wise
    vector0 = rc.Geometry.Vector3d(pts[1]- pts[0])
    vector1 = rc.Geometry.Vector3d(pts[-1]- pts[0])
    ptsNormal = rc.Geometry.Vector3d.CrossProduct(vector0, vector1)
    
    # in case points are anti-clockwise then normals should be parallel
    if crossProduct(ptsNormal, faceNormal) > 0:
        return True
    return False


def main(osmFile):
    # Preparation
    workingDir, fileName = os.path.split(osmFile)
    inpFilePath = osmFile.replace('.osm', '.inp')
    osmPath = ops.Path(osmFile)
    model = ops.Model().load(ops.Path(osmPath)).get()
    
    # Create inp strings for all of the polygons in the OpenStudio model.
    mToFt = 3.28084
    mToFt = 1
    rhinoPolygons = []
    inpPolygons = []
    spaceLabels = []
    zoneLabels = []
    exteriorWallSrfs = []
    polyCount = 32
    surfaces = model.getSurfaces()
    
    for srf in surfaces:
        if str(srf.surfaceType()) == 'Floor':
            srfPts = []
            spaceStr = '"Polygon ' + str(polyCount) + '" = POLYGON\n'
            
            # create the space polygon
            spaceName = str(srf.getString(4))
            for count, vert in enumerate(srf.vertices()):
                pt = rc.Geometry.Point3d(vert.x()*mToFt, vert.y()*mToFt, vert.z()*mToFt)
                srfPts.append(pt)
            if not isAntiClockWise(srfPts):
                srfPts.reverse()
            for count, vert in enumerate(srfPts):
                spaceStr = spaceStr + '    V' + str(count+1) + '               = ( ' + \
                    str(round(vert.X*mToFt,2)) + ', ' + str(round(vert.Y*mToFt,2)) + ' )\n'
            spaceStr = spaceStr + '    ..\n'
            inpPolygons.append(spaceStr)
            labelStr = '"' + str(spaceName) + '" = SPACE\n' + \
                '    SHAPE            = POLYGON\n' + \
                '    POLYGON          = "Polygon ' + str(polyCount) + '"\n' + \
                '    ..\n'
            spaceLabels.append(labelStr)
            
            # grab any exterior surfaces.
            space = model.getSpaceByName(spaceName).get()
            spaceSrfs = space.surfaces
            for wallSrf in spaceSrfs:
                if str(wallSrf.surfaceType()) == 'Wall' and wallSrf.outsideBoundaryCondition() == 'Outdoors':
                    srfName = wallSrf.name()
                    wallPts = []
                    for vert in wallSrf.vertices():
                        wallPts.append(rc.Geometry.Point3d(vert.x(), vert.y(), vert.z()))
                    wallPts.append(wallPts[0])
                    polyline = rc.Geometry.Polyline(wallPts).ToNurbsCurve()
                    geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
                    exteriorWallSrfs.append(geometry)
                    srfVert = 1
                    hits = 0
                    for i, vert in enumerate(srfPts):
                        for wallVert in wallPts:
                            if round(wallVert.X,2) == round(vert.X,2) and round(wallVert.Y,2) == round(vert.Y,2):
                                srfVert = i
                                hits += 1
                    if hits != 5:
                        srfVert += 1
                        print hits
                    if srfVert == 0:
                        srfVert = len(srfPts)
                    
                    labelSStr = '"' + str(srfName) + '" = EXTERIOR-WALL\n' + \
                        '    LOCATION            = SPACE-V' + str(srfVert) + '\n' + \
                        '    ..\n'
                    #spaceLabels.append(labelSStr)
            
            
            # create the zone.
            try:
                zoneName = spaceName.replace('space', 'zone')
            except:
                zoneName = spaceName
            labelZStr = '"' + str(zoneName) + '" = ZONE\n' + \
                '    TYPE            = CONDITIONED\n' + \
                '    SPACE          = "' + str(spaceName) + '"\n' + \
                '    ..\n'
            zoneLabels.append(labelZStr)
            
            polyCount += 1
            srfPts.append(srfPts[0])
            polyline = rc.Geometry.Polyline(srfPts).ToNurbsCurve()
            try:
                geometry = rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]
                rhinoPolygons.append(geometry)
            except:
                print "failed to build rhino surface."
    
    # create polygons for the entire floors.
    levelPolygonStrs = []
    levelLabels = []
    levelCount = 1
    
    joinedPoly = rc.Geometry.Brep.JoinBreps(rhinoPolygons, sc.doc.ModelAbsoluteTolerance)
    meshPar = rc.Geometry.MeshingParameters.Coarse
    meshPar.SimplePlanes = True
    for levelBrep in joinedPoly:
        levelMesh = rc.Geometry.Mesh()
        for m in rc.Geometry.Mesh.CreateFromBrep(levelBrep, meshPar):
            levelMesh.Append(m)
        plSegments = levelMesh.GetNakedEdges()[0]
        segments = plSegments.ToNurbsCurve()
        pts = []
        pts.append(segments.PointAtStart)
        restOfpts = findDiscontinuity(segments, style = 4)
        pts.extend(restOfpts)
        
        if isAntiClockWise(pts):
            pts.reverse()
            segments.Reverse()
        
        levelStr = '"LEVEL ' + str(levelCount) + ' POLY" = POLYGON\n'
        for count, vert in enumerate(pts):
            levelStr = levelStr + '    V' + str(count+1) + '               = ( ' + \
                str(round(vert.X*mToFt,2)) + ', ' + str(round(vert.Y*mToFt,2)) + ' )\n'
        levelStr = levelStr + '    ..\n'
        levelPolygonStrs.append(levelStr)
        
        labelStr = '"Level ' + str(levelCount) + '" = FLOOR\n' + \
            '    POLYGON          = "LEVEL ' + str(levelCount) + ' POLY"\n' + \
            '    SHAPE            = POLYGON\n' + \
            '    FLOOR-HEIGHT     = 10.5\n' + \
            '    SPACE-HEIGHT     = 9\n' + \
            '    C-DIAGRAM-DATA   = *Detailed UI DiagData*\n' + \
            '    ..\n'
        levelLabels.append(labelStr)
        
        levelCount += 1
    
    # write the inp polygons into a file.
    with open(inpFilePath,'w') as inpFile:
        headerTxt = '\n\n$ *********************************************************\n' + \
            '$ **                                                     **\n' + \
            '$ **                     Polygons                        **\n' + \
            '$ **                                                     **\n' + \
            '$ *********************************************************\n\n\n'
        inpFile.write(headerTxt)
        for poly in levelPolygonStrs:
            inpFile.write(poly)
        for poly in inpPolygons:
            inpFile.write(poly)
        
        headerTxt = '\n\n$ *********************************************************\n' + \
            '$ **                                                     **\n' + \
            '$ **     Floors / Spaces / Walls / Windows / Doors       **\n' + \
            '$ **                                                     **\n' + \
            '$ *********************************************************\n\n\n'
        inpFile.write(headerTxt)
        for level in levelLabels:
            inpFile.write(level)
        for space in spaceLabels:
            inpFile.write(space)
        
        headerTxt = '\n\n$ *********************************************************\n' + \
            '$ **                                                     **\n' + \
            '$ **               HVAC Systems / Zones                  **\n' + \
            '$ **                                                     **\n' + \
            '$ *********************************************************\n\n\n'
        inpFile.write(headerTxt)
        for zone in zoneLabels:
            inpFile.write(zone)
    
    return inpFilePath, rhinoPolygons, segments, exteriorWallSrfs


#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
        hb_hvacProperties = sc.sticky['honeybee_hvacProperties']()
        hb_airDetail = sc.sticky["honeybee_hvacAirDetails"]
        hb_heatingDetail = sc.sticky["honeybee_hvacHeatingDetails"]
        hb_coolingDetail = sc.sticky["honeybee_hvacCoolingDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if sc.sticky.has_key('honeybee_release'):
    if sc.sticky["honeybee_folders"]["OSLibPath"] != None:
        # openstudio is there
        openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
        
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
        
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg1 = "You do not have OpenStudio installed on Your System.\n" + \
            "You wont be able to use this component until you install it.\n" + \
            "Download the latest OpenStudio for Windows from:\n"
        msg2 = "https://www.openstudio.net/downloads"
        print msg1
        print msg2
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False


if initCheck == True and openStudioIsReady == True and _runIt ==True and _osmFilePath:
    fileCheck = checkTheInputs(_osmFilePath)
    if fileCheck != -1:
        result = main(_osmFilePath)
        if result != -1:
            inpFileAddress, spacePolygons, floorPolygons, exteriorWalls = result