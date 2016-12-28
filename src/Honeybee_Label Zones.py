# This component labels zones with their names in the Rhino scene.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to lablel zones with their names in the Rhino scene.  This can help ensure that the correct names are assigned to each zone and can help keep track of zones and zone data throughout analysis.
-
Provided by Honeybee 0.0.60
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        attribute_: A text string for the zone attribute that you are interested in lableing the zones with.  Possible inputs include "name", "zoneProgram", "isConditioned" or any other Honeybee attribute. Use the "Honeybee_Zone Attribute List" to see all possibilities.
        textHeight_: An optional number for text height in Rhino model units that can be used to change the size of the label text in the Rhino scene.  The default is set based on the dimensions of the zones.
        font_: An optional number that can be used to change the font of the label in the Rhino scene. The default is set to "Verdana".
    Returns:
        zoneTxtLabels: The label names of each of the connected zones.  Connect this ouput and the one bleow to a Grasshopper "TexTag3D" component to make your own lables.
        labelBasePts: The basepoint of the text labels.  Use this along with the ouput above and a Grasshopper "TexTag3D" component to make your own lables.
        brepTxtLabels: A set of surfaces indicating the names of each zone as they correspond to the branches in the EP results and the name of the zone in the headers of data.
        zoneWireFrame: A list of curves representing the outlines of the zones.
"""

ghenv.Component.Name = "Honeybee_Label Zones"
ghenv.Component.NickName = 'LabelZones'
ghenv.Component.Message = 'VER 0.0.60\nDEC_28_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
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
    
    for HZone in _HBZones:
        zone = hb_hive.visualizeFromHoneybeeHive([HZone])[0]
        zones.append(zone)
    
    sc.sticky["Honeybee_LabelZoneData"] = zones


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
    hb_hvac = sc.sticky["honeybee_hvacProperties"]()
    
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
        if attribute == "HVACSystem":
            theProp = hb_hvac.sysDict[theProp.Index]
        
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
    
    # Make the zone labels.
    zoneLabels = lb_visualization.text2srf(zoneProperties, newPts, font, textSize)
    
    # If people are requesting to see the illuminace point, output a sphere for this point instead of the pt location text.
    if attribute == "illumCntrlSensorPt":
        zoneLabels = []
        for count, pointText in enumerate(zoneProperties):
            if pointText == 'None':
                hb_zones[count].atuoPositionDaylightSensor()
                sensPt = hb_zones[count].illumCntrlSensorPt
                hb_zones[count].illumCntrlSensorPt = None
            else:
                ptCoordList = pointText.split(',')
                sensPt = rc.Geometry.Point3d(float(ptCoordList[0]),float(ptCoordList[1]),float(ptCoordList[2]))
            sensSphere = rc.Geometry.Sphere(sensPt, 0.1)
            zoneLabels.append([sensSphere])
    
    return zoneProperties, zoneLabels, wireFrames, newPts


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


if _HBZones != [] and initCheck == True:
    if _HBZones[0] != None:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_LabelZoneData"]
        
        labelCentPts, textSize, font, attribute = setDefaults()
        zoneTxtLabels, zoneTextLabels, wireFrames, labelBasePts = main(hb_zoneData, labelCentPts, textSize, font, attribute)
        
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