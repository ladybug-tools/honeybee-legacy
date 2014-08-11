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
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
    Returns:
        zoneNames: The names of each of the connected zones.
        labelBasePts: The basepoint of the text labels.  Use this along with the zoneNames ouput above and a GH "TexTag3D" component to make your own lables.
        zoneLabels: A set of surfaces indicating the names of each zone as they correspond to the branches in the EP results and the name of the zone in the headers of data.
        zoneWireFrame: A list of curves representing the outlines of the zones.
"""

ghenv.Component.Name = "Honeybee_Label Zones"
ghenv.Component.NickName = 'LabelZones'
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


def setDefaults():
    #Check the font and seta a default one.
    if font_ == None: font = "Verdana"
    else: font = font_
    
    #Get the base points and come up with a default text size.
    zoneCentPts = []
    shortestDimensions = []
    for HZone in _HBZones:
        bBox = rc.Geometry.Box(HZone.GetBoundingBox(False))
        shortestDimensions.extend([bBox.X[1]-bBox.X[0], bBox.Y[1]-bBox.Y[0], bBox.Z[1]-bBox.Z[0]])
        zoneCentPts.append(bBox.Center)
    
    if textHeight_ == None:
        shortestDimensions.sort()
        shortDim = None
        for dim in shortestDimensions:
            if dim > sc.doc.ModelAbsoluteTolerance*50 and shortDim == None: shortDim = dim
            else: pass
        roughZoneNameLen = 10
        textSize = shortDim/roughZoneNameLen
    else:
        textSize = textHeight_
    
    
    return zoneCentPts, textSize, font


def main(basePts, textSize, font):
    #import the classes.
    if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key('ladybug_release'):
        hb_hive = sc.sticky["honeybee_Hive"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #Make lists to be filled.
        zoneNames =[]
        wireFrames =[]
        zoneNameLength = []
        
        #Get the zone names.
        for HZone in _HBZones:
            wireFrames.append(HZone.DuplicateEdgeCurves())
            zone = hb_hive.callFromHoneybeeHive([HZone])[0]
            theName = zone.name
            zoneNames.append(theName)
            zoneNameLength.append(len(list(str(theName))))
        
        #Adjust the position of the label base points depending on the length of the length of the zone name.
        newPts = []
        for ptCount, length in enumerate(zoneNameLength):
            basePtMove = textSize*(length/2.1)
            newPt = rc.Geometry.Point3d(basePts[ptCount].X-basePtMove, basePts[ptCount].Y, basePts[ptCount].Z)
            newPts.append(newPt)
        
        #Make the zone labels.
        zoneLabels = lb_visualization.text2srf(zoneNames, newPts, font, textSize)
        
        return zoneNames, zoneLabels, wireFrames, newPts
    else:
        return [], [], []
        print "You should first let both Ladybug and Honeybee  fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee  fly...")


if _HBZones != []:
    labelCentPts, textSize, font = setDefaults()
    zoneNames, zoneTextLabels, wireFrames, labelBasePts = main(labelCentPts, textSize, font)
    
    #Unpack the data trees of curves and label text.
    zoneLabels = DataTree[Object]()
    zoneWireFrames = DataTree[Object]()
    for listCount, lists in enumerate(zoneTextLabels):
        for item in lists:
            zoneLabels.Add(item, GH_Path(listCount))
    for listCount, lists in enumerate(wireFrames):
        for item in lists:
            zoneWireFrames.Add(item, GH_Path(listCount))


#Hide unwanted outputs
ghenv.Component.Params.Output[1].Hidden = True