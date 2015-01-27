# This component labels zones with their names in the Rhino scene.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to lablel zones with their names in the Rhino scene.  This can help ensure that the correct names are assigned to each zone and can help keep track of zones and zone data throughout analysis.
-
Provided by Honeybee 0.0.55
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        attribute_: A text string for the surface attribute that you are interested in lableing the surfaces with.  Possible inputs include "name", "construction" or any other Honeybee attribute.  Use the "Honeybee_Surface Attribute List" to see all possibilities.
        windows_: Set to "True" to have the component label the window surfaces in the model instead of the opaque surfaces.  By default, this is set to "False" to label just the opaque surfaces.
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
        recallHBHive_: Set to "True" to recall the zones from the hive each time the input changes and "False" to simply copy the zones to memory.  Calling the zones from the hive can take some more time but this is necessary if you are making changes to the zones and you want to check them.  Otherwise, if you are just scrolling through attributes, it is nice to set this to "False" for speed.  The default is set to "True" as this is safer.
    Returns:
        surfaceAttributes: The names of each of the connected zone surfaces.
        labelBasePts: The basepoint of the text labels.  Use this along with the surfaceAttributes ouput above and a GH "TexTag3D" component to make your own lables.
        surfaceLabels: A set of surfaces indicating the names of each zone surface as they correspond to the branches in the EP surface results.
        surfaceWireFrame: A list of curves representing the outlines of the surfaces.
"""

ghenv.Component.Name = "Honeybee_Label Zone Surfaces"
ghenv.Component.NickName = 'LabelSurfaces'
ghenv.Component.Message = 'VER 0.0.55\nOCT_03_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
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

tol = sc.doc.ModelAbsoluteTolerance


def copyHBZoneData():
    hb_hive = sc.sticky["honeybee_Hive"]()
    zones = []
    zoneBreps = []
    zoneCentPts = []
    
    for HZone in _HBZones:
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        zones.append(zone)
    
    sc.sticky["Honeybee_LabelSrfData"] = [zoneBreps, zones, zoneCentPts]


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


def main(hb_zones, textSize, font, windows, attribute):
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    #Make lists to be filled.
    srfBreps = []
    srfCentPts = []
    srfPlanes = []
    shortestDimensions = []
    surfaceAttributes =[]
    wireFrames =[]
    surfaceNameLength = []
    
    #Get the surface names and geometry.
    for zone in hb_zones:
        for srf in zone.surfaces:
            if windows == False:
                try: theProp = getattr(srf, attribute)
                except: theProp = "N/A"
                if theProp == "":
                    theProp = "Not Assigned"
                surfaceAttributes.append(str(theProp))
                surfaceNameLength.append(len(list(str(theProp))))
                srfBreps.append(srf.geometry)
                wireFrames.append(srf.geometry.DuplicateEdgeCurves())
                bBox = rc.Geometry.Box(srf.geometry.GetBoundingBox(False))
                shortestDimensions.extend([bBox.X[1]-bBox.X[0], bBox.Y[1]-bBox.Y[0], bBox.Z[1]-bBox.Z[0]])
                srfCentPts.append(bBox.Center)
                if srf.geometry.IsSurface and srf.geometry.Surfaces[0].IsPlanar():
                    planarBool, plane = srf.geometry.Surfaces[0].TryGetPlane(tol)
                    plane.Origin = bBox.Center
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
                        if theProp == "":
                            theProp = "Not Assigned"
                        surfaceAttributes.append(str(theProp))
                        surfaceNameLength.append(len(list(str(theProp))))
                        srfBreps.append(childSrf.geometry)
                        wireFrames.append(childSrf.geometry.DuplicateEdgeCurves())
                        bBox = rc.Geometry.Box(childSrf.geometry.GetBoundingBox(False))
                        shortestDimensions.extend([bBox.X[1]-bBox.X[0], bBox.Y[1]-bBox.Y[0], bBox.Z[1]-bBox.Z[0]])
                        srfCentPts.append(bBox.Center)
                        if childSrf.geometry.IsSurface and childSrf.geometry.Surfaces[0].IsPlanar():
                            planarBool, plane = childSrf.geometry.Surfaces[0].TryGetPlane(tol)
                            plane.Origin = bBox.Center
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

if recallHBHive_ == None: recallHBHive = True
else: recallHBHive = recallHBHive_

#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if recallHBHive == True:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_LabelSrfData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True and sc.sticky.has_key('Honeybee_LabelSrfData') == False:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_LabelSrfData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_LabelSrfData') == True:
    hb_zoneData = sc.sticky["Honeybee_LabelSrfData"]
    checkZones = True
    if len(_HBZones) == len(hb_zoneData[0]):
        for count, brep in enumerate(_HBZones):
            boundBoxVert = brep.GetBoundingBox(False).Center
            if boundBoxVert.X <= hb_zoneData[2][count].X+tol and boundBoxVert.X >= hb_zoneData[2][count].X-tol and boundBoxVert.Y <= hb_zoneData[2][count].Y+tol and boundBoxVert.Y >= hb_zoneData[2][count].Y-tol and boundBoxVert.Z <= hb_zoneData[2][count].Z+tol and boundBoxVert.Z >= hb_zoneData[2][count].Z-tol: pass
            else:
                checkZones = False
    else: checkZones = False
    if checkZones == True: pass
    else:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_LabelSrfData"]
    initCheck = True
elif sc.sticky.has_key('honeybee_release') == False or sc.sticky.has_key('ladybug_release') == False:
    print "You should first let Honeybee amd Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Honeybee and Ladybug fly...")
else:
    pass




if _HBZones != [] and initCheck == True:
    textSize, font, windows, attribute = setDefaults()
    surfaceTxtLabels, srfTextLabels, wireFrames, labelBasePts = main(hb_zoneData[1], textSize, font, windows, attribute)
    
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