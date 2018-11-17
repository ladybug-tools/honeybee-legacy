# This component labels zones with their names in the Rhino scene.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to lablel HBSurfaces or HBZones with their names or energy/daylight properties in the Rhino scene.  This is useful for checking whether certain properties have been assigned correctly.
-
Provided by Honeybee 0.0.64
    
    Args:
        _HBObjects: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        attribute_: A text string for the surface attribute that you are interested in lableing the surfaces with.  Possible inputs include "name", "construction" or any other Honeybee attribute.  Use the "Honeybee_Surface Attribute List" to see all possibilities.
        windows_: Set to "True" to have the component label the window surfaces in the model instead of the opaque surfaces.  By default, this is set to "False" to label just the opaque surfaces.
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
    Returns:
        surfaceAttributes: The names of each of the connected zone surfaces.
        labelBasePts: The basepoint of the text labels.  Use this along with the surfaceAttributes ouput above and a GH "TexTag3D" component to make your own lables.
        surfaceLabels: A set of surfaces indicating the names of each zone surface as they correspond to the branches in the EP surface results.
        surfaceWireFrame: A list of curves representing the outlines of the surfaces.
"""

ghenv.Component.Name = "Honeybee_Label Zone Surfaces"
ghenv.Component.NickName = 'LabelSurfaces'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc

tol = sc.doc.ModelAbsoluteTolerance


def copyHBZoneData():
    hb_hive = sc.sticky["honeybee_Hive"]()
    zones = []
    
    for HZone in _HBObjects:
        zone = hb_hive.visualizeFromHoneybeeHive([HZone])[0]
        zones.append(zone)
    
    sc.sticky["Honeybee_LabelSrfData"] = zones


def setDefaults():
    #Check tthe inputs and set defaults.
    if font_ == None: font = "Verdana"
    else: font = font_
    
    if textHeight_ == None: textSize = None
    else: textSize = textHeight_
    
    if windows_ == None: windows = False
    else: windows = windows_
    
    if attribute_ == None: attribute = "name"
    else: attribute = attribute_
    
    return textSize, font, windows, attribute

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

def main(HBZoneObjects, textSize, font, windows, attribute):
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    hb_EPTypes = sc.sticky["honeybee_EPTypes"]
    
    #Make lists to be filled.
    srfBreps = []
    srfCentPts = []
    srfPlanes = []
    shortestDimensions = []
    surfaceAttributes =[]
    wireFrames =[]
    surfaceNameLength = []
    
    #Extract HBSrfs.
    HBSurfaces = []
    for HBObj in HBZoneObjects:
        if HBObj.objectType == "HBZone":
            for surface in HBObj.surfaces: HBSurfaces.append(surface)
        elif HBObj.objectType == "HBSurface": HBSurfaces.append(HBObj)
    
    #Get the surface names and geometry.
    for srf in HBSurfaces:
        if windows == False:
            try: theProp = getattr(srf, attribute)
            except: theProp = "N/A"
            
            if attribute == 'type':
                theProp = hb_EPTypes.srfType[theProp]
            elif attribute == 'EPConstruction' and theProp == None:
                try:
                    theProp = getattr(srf, 'construction')
                except: theProp = "Not Assigned"
            elif attribute == 'RadMaterial' and theProp == None:
                try:
                    theProp = getattr(srf, 'construction')
                except: theProp = "Not Assigned"
            elif theProp == "" or theProp == None:
                theProp = "Not Assigned"
            
            if attribute == "BCObject":
                theProp = theProp.name
                if theProp == '':
                    theProp = "N/A"
            
            surfaceAttributes.append(str(theProp))
            surfaceNameLength.append(len(list(str(theProp))))
            srfBreps.append(srf.geometry)
            wireFrames.append(srf.geometry.DuplicateEdgeCurves())
            bBox = rc.Geometry.Box(srf.geometry.GetBoundingBox(False))
            shortestDimensions.extend([bBox.X[1]-bBox.X[0], bBox.Y[1]-bBox.Y[0], bBox.Z[1]-bBox.Z[0]])
            srfCentPts.append(bBox.Center)
            if srf.geometry.Surfaces[0].IsPlanar():
                centPt, normal = getSrfCenPtandNormal(srf.geometry)
                plane = rc.Geometry.Plane(centPt, normal)
                if rc.Geometry.Vector3d.VectorAngle(plane.ZAxis, rc.Geometry.Plane.WorldXY.ZAxis) > sc.doc.ModelAngleToleranceRadians and rc.Geometry.Vector3d.VectorAngle(plane.ZAxis, rc.Geometry.Vector3d(0,0,-1)) > sc.doc.ModelAngleToleranceRadians:
                    angle2Z = rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Plane.WorldXY.ZAxis, plane.YAxis, plane)
                    planeRotate = rc.Geometry.Transform.Rotation(-angle2Z, plane.ZAxis, plane.Origin)
                    plane.Transform(planeRotate)
                srfPlanes.append(plane)
            else:
                plane = rc.Geometry.Plane.WorldXY
                plane.Origin = bBox.Center
                srfPlanes.append(plane)
        
        if srf.hasChild:
            if windows == True:
                for childSrf in srf.childSrfs:
                    try: theProp = getattr(childSrf, attribute)
                    except: theProp = "N/A"
                    if theProp == "" or theProp == None:
                        theProp = "Not Assigned"
                    surfaceAttributes.append(str(theProp))
                    surfaceNameLength.append(len(list(str(theProp))))
                    srfBreps.append(childSrf.geometry)
                    wireFrames.append(childSrf.geometry.DuplicateEdgeCurves())
                    bBox = rc.Geometry.Box(childSrf.geometry.GetBoundingBox(False))
                    shortestDimensions.extend([bBox.X[1]-bBox.X[0], bBox.Y[1]-bBox.Y[0], bBox.Z[1]-bBox.Z[0]])
                    srfCentPts.append(bBox.Center)
                    if childSrf.geometry.IsSurface and childSrf.geometry.Surfaces[0].IsPlanar():
                        centPt, normal = getSrfCenPtandNormal(childSrf.geometry)
                        plane = rc.Geometry.Plane(centPt, normal)
                        if rc.Geometry.Vector3d.VectorAngle(plane.ZAxis, rc.Geometry.Plane.WorldXY.ZAxis) > sc.doc.ModelAngleToleranceRadians and rc.Geometry.Vector3d.VectorAngle(plane.ZAxis, rc.Geometry.Vector3d(0,0,-1)) > sc.doc.ModelAngleToleranceRadians:
                            angle2Z = rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Plane.WorldXY.ZAxis, plane.YAxis, plane)
                            planeRotate = rc.Geometry.Transform.Rotation(-angle2Z, plane.ZAxis, plane.Origin)
                            plane.Transform(planeRotate)
                        srfPlanes.append(plane)
                    else:
                        plane = rc.Geometry.Plane.WorldXY
                        plane.Origin = bBox.Center
                        srfPlanes.append(plane)
    
    #Get the shortest dimension of the bounding boxes (used to size the text).
    if textSize == None:
        shortestDimensions.sort()
        shortDim = None
        for dim in shortestDimensions:
            if dim > tol*50 and shortDim == None: shortDim = dim
            else: pass
        roughSrfNameLen = sum(surfaceNameLength)/len(surfaceNameLength)
        textSize = shortDim/roughSrfNameLen
    else: pass
    
    #Adjust the position of the label base points depending on the length of the length of the srf name and whether there are overlapping base Pts.
    initPts = []
    newPts = []
    for ptCount, length in enumerate(surfaceNameLength):
        overlap = False
        for point in initPts:
            if srfCentPts[ptCount].X > point.X-tol and srfCentPts[ptCount].X < point.X+tol and srfCentPts[ptCount].Y > point.Y-tol and srfCentPts[ptCount].Y < point.Y+tol and srfCentPts[ptCount].Z > point.Z-tol and srfCentPts[ptCount].Z < point.Z+tol:
                overlap = True
            else: pass
        
        if overlap == True:
            shiftVector = srfPlanes[ptCount].YAxis
            shiftVector.Unitize()
            shiftVector = rc.Geometry.Vector3d.Multiply(textSize*1.5, shiftVector)
            srfCentPts[ptCount] = rc.Geometry.Point3d.Add(srfCentPts[ptCount], shiftVector)
            srfPlanes[ptCount].Origin = srfCentPts[ptCount]
        
        initPts.append(srfCentPts[ptCount])
        
        basePtMove = textSize*(length/2.1)
        newPt = rc.Geometry.Point3d(srfCentPts[ptCount].X-basePtMove, srfCentPts[ptCount].Y, srfCentPts[ptCount].Z)
        newPts.append(newPt)
    
    #Make the zone labels.
    surfaceLabels = lb_visualization.text2srf(surfaceAttributes, newPts, font, textSize)
    
    #Orient the labels to the planes of the surfaces
    for count, plane in enumerate(srfPlanes):
        startPlane = rc.Geometry.Plane(rc.Geometry.Point3d(srfCentPts[count].X, srfCentPts[count].Y, srfCentPts[count].Z), rc.Geometry.Vector3d.ZAxis)
        orient = rc.Geometry.Transform.PlaneToPlane(startPlane, plane)
        for textSrf in surfaceLabels[count]:
            textSrf.Transform(orient)
    
    return surfaceAttributes, surfaceLabels, wireFrames, newPts


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True
w = gh.GH_RuntimeMessageLevel.Warning

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
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


if initCheck== True and _HBObjects != [] and _HBObjects[0] != None and initCheck == True:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_LabelSrfData"]
    
    textSize, font, windows, attribute = setDefaults()
    surfaceTxtLabels, srfTextLabels, wireFrames, labelBasePts = main(hb_zoneData, textSize, font, windows, attribute)
    
    #Unpack the data trees of curves and label text.
    brepTxtLabels = DataTree[Object]()
    surfaceWireFrames = DataTree[Object]()
    for listCount, lists in enumerate(srfTextLabels):
        for item in lists:
            brepTxtLabels.Add(item, GH_Path(listCount))
    for listCount, lists in enumerate(wireFrames):
        for item in lists:
            surfaceWireFrames.Add(item, GH_Path(listCount))


#Hide unwanted outputs
ghenv.Component.Params.Output[1].Hidden = True