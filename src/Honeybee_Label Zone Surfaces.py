# This component labels zones with their names in the Rhino scene.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to lablel zones with their names in the Rhino scene.  This can help ensure that the correct names are assigned to each zone and can help keep track of zones and zone data throughout analysis.
-
Provided by Honeybee 0.0.53
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        windows_: Set to "True" to have the component label the window surfaces in the model instead of the opaque surfaces.  By default, this is set to False to label just the opaque surfaces.
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
    Returns:
        surfaceNames: The names of each of the connected zone surfaces.
        labelBasePts: The basepoint of the text labels.  Use this along with the surfaceNames ouput above and a GH "TexTag3D" component to make your own lables.
        surfaceLabels: A set of surfaces indicating the names of each zone surface as they correspond to the branches in the EP surface results.
        surfaceWireFrame: A list of curves representing the outlines of the surfaces.
"""

ghenv.Component.Name = "Honeybee_Label Zone Surfaces"
ghenv.Component.NickName = 'LabelSurfaces'
ghenv.Component.Message = 'VER 0.0.57\nAUG_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


from System import Object
from System import Drawing
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc

tol = sc.doc.ModelAbsoluteTolerance

def setDefaults():
    #Check tthe inputs and set defaults.
    if font_ == None: font = "Verdana"
    else: font = font_
    
    if textHeight_ == None: textSize = None
    else: textSize = textHeight_
    
    if windows_ == None: windows = False
    else: windows = windows_
    
    return textSize, font, windows


def main(textSize, font, windows):
    #import the classes.
    if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key('ladybug_release'):
        hb_hive = sc.sticky["honeybee_Hive"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #Make lists to be filled.
        srfBreps = []
        srfCentPts = []
        srfPlanes = []
        shortestDimensions = []
        surfaceNames =[]
        wireFrames =[]
        surfaceNameLength = []
        
        #Get the surface names and geometry.
        for HZone in _HBZones:
            zone = hb_hive.callFromHoneybeeHive([HZone])[0]
            for srf in zone.surfaces:
                if windows == False:
                    surfaceNames.append(srf.name)
                    surfaceNameLength.append(len(list(str(srf.name))))
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
                            surfaceNames.append(childSrf.name)
                            surfaceNameLength.append(len(list(str(childSrf.name))))
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
        surfaceLabels = lb_visualization.text2srf(surfaceNames, newPts, font, textSize)
        
        #Orient the labels to the planes of the surfaces
        for count, plane in enumerate(srfPlanes):
            startPlane = rc.Geometry.Plane(rc.Geometry.Point3d(srfCentPts[count].X, srfCentPts[count].Y, srfCentPts[count].Z), rc.Geometry.Vector3d.ZAxis)
            orient = rc.Geometry.Transform.PlaneToPlane(startPlane, plane)
            for textSrf in surfaceLabels[count]:
                textSrf.Transform(orient)
        
        return surfaceNames, surfaceLabels, wireFrames, newPts
    else:
        return [], [], []
        print "You should first let both Ladybug and Honeybee  fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee  fly...")


if _HBZones != []:
    textSize, font, windows = setDefaults()
    surfaceNames, srfTextLabels, wireFrames, labelBasePts = main(textSize, font, windows)
    
    #Unpack the data trees of curves and label text.
    surfaceLabels = DataTree[Object]()
    surfaceWireFrames = DataTree[Object]()
    for listCount, lists in enumerate(srfTextLabels):
        for item in lists:
            surfaceLabels.Add(item, GH_Path(listCount))
    for listCount, lists in enumerate(wireFrames):
        for item in lists:
            surfaceWireFrames.Add(item, GH_Path(listCount))


#Hide unwanted outputs
ghenv.Component.Params.Output[1].Hidden = True