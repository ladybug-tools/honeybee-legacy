# This component labels zones with their names in the Rhino scene.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to lablel zones with their names in the Rhino scene.  This can help ensure that the correct names are assigned to each zone and can help keep track of zones and zone data throughout analysis.
-
Provided by Honeybee 0.0.56
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        attribute_: A text string for the zone attribute that you are interested in lableing the zones with.  Possible inputs include "name", "zoneProgram", "isConditioned" or any other Honeybee attribute. Use the "Honeybee_Zone Attribute List" to see all possibilities.
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
        recallHBHive_: Set to "True" to recall the zones from the hive each time the input changes and "False" to simply copy the zones to memory.  Calling the zones from the hive can take some more time but this is necessary if you are making changes to the zones and you want to check them.  Otherwise, if you are just scrolling through attributes, it is nice to set this to "False" for speed.  The default is set to "True" as this is safer.
    Returns:
        zoneTxtLabels: The label names of each of the connected zones.  Connect this ouput and the one bleow to a Grasshopper "TexTag3D" component to make your own lables.
        labelBasePts: The basepoint of the text labels.  Use this along with the ouput above and a Grasshopper "TexTag3D" component to make your own lables.
        brepTxtLabels: A set of surfaces indicating the names of each zone as they correspond to the branches in the EP results and the name of the zone in the headers of data.
        zoneWireFrame: A list of curves representing the outlines of the zones.
"""

ghenv.Component.Name = "Honeybee_Label Zones"
ghenv.Component.NickName = 'LabelZones'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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
    
    sc.sticky["Honeybee_LabelZoneData"] = [zoneBreps, zones, zoneCentPts]


def setDefaults():
    #Check the font and set a default one.
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
    
    if attribute_ == None: attribute = "name"
    else: attribute = attribute_
    
    return zoneCentPts, textSize, font, attribute


def main(hb_zones, basePts, textSize, font, attribute):
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    #Make lists to be filled.
    zoneProperties =[]
    wireFrames =[]
    zoneNameLength = []
    
    #Get the zone properties.
    for count, HZone in enumerate(hb_zones):
        wireFrames.append(_HBZones[count].DuplicateEdgeCurves())
        theProp = ""
        try:
            theProp = getattr(HZone, attribute)
        except:
            if attribute == "zoneFloorArea":
                theProp = "%.3f"%HZone.getFloorArea()
            elif attribute == "zoneVolume":
                theProp = "%.3f"%HZone.getZoneVolume()
                
        if theProp == "":
            theProp = "Not Assigned"
        zoneProperties.append(str(theProp))
        zoneNameLength.append(len(list(str(theProp))))
    
    #Adjust the position of the label base points depending on the length of the length of the zone name.
    newPts = []
    for ptCount, length in enumerate(zoneNameLength):
        basePtMove = textSize*(length/2.1)
        newPt = rc.Geometry.Point3d(basePts[ptCount].X-basePtMove, basePts[ptCount].Y, basePts[ptCount].Z)
        newPts.append(newPt)
    
    #Make the zone labels.
    zoneLabels = lb_visualization.text2srf(zoneProperties, newPts, font, textSize)
    
    return zoneProperties, zoneLabels, wireFrames, newPts

if recallHBHive_ == None: recallHBHive = True
else: recallHBHive = recallHBHive_

#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if recallHBHive == True:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_LabelZoneData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True and sc.sticky.has_key('Honeybee_LabelZoneData') == False:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_LabelZoneData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_LabelZoneData') == True:
    hb_zoneData = sc.sticky["Honeybee_LabelZoneData"]
    checkZones = True
    if len(_HBZones) == len(hb_zoneData[0]):
        for count, brep in enumerate(_HBZones):
            boundBoxVert = brep.GetBoundingBox(False).Center
            if boundBoxVert.X <= hb_zoneData[2][count].X+tol and boundBoxVert.X >= hb_zoneData[2][count].X-tol and boundBoxVert.Y <= hb_zoneData[2][count].Y+tol and boundBoxVert.Y >= hb_zoneData[2][count].Y-tol and boundBoxVert.Z <= hb_zoneData[2][count].Z+tol and boundBoxVert.Z >= hb_zoneData[2][count].Z-tol: pass
            else: checkZones = False
    else: checkZones = False
    if checkZones == True: pass
    else:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_LabelZoneData"]
    initCheck = True
elif sc.sticky.has_key('honeybee_release') == False or sc.sticky.has_key('ladybug_release') == False:
    print "You should first let Honeybee amd Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Honeybee and Ladybug fly...")
else:
    pass




if _HBZones != [] and initCheck == True:
    labelCentPts, textSize, font, attribute = setDefaults()
    zoneTxtLabels, zoneTextLabels, wireFrames, labelBasePts = main(hb_zoneData[1], labelCentPts, textSize, font, attribute)
    
    #Unpack the data trees of curves and label text.
    brepTxtLabels = DataTree[Object]()
    zoneWireFrames = DataTree[Object]()
    for listCount, lists in enumerate(zoneTextLabels):
        for item in lists:
            brepTxtLabels.Add(item, GH_Path(listCount))
    for listCount, lists in enumerate(wireFrames):
        for item in lists:
            zoneWireFrames.Add(item, GH_Path(listCount))


#Hide unwanted outputs
ghenv.Component.Params.Output[1].Hidden = True