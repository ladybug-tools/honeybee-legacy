#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to take any list of closed breps and turn them into Honeybee Zones with all of the properties needed to run them through an energy simulation.
_
This includes constructions of the surfaces, boundary condtions of all of the surfaces (ie ground, exterior, etc), schedules+ loads for occupancy/internal electronics, and settings for an HVAC system if isContitioned_ is set to True.
-
Provided by Honeybee 0.0.59

    Args:
        _zoneMasses: A list of closed breps or a  single closed brep that represents the geometry of the zone(s) that will be output from this component.
        zoneNames_: A list of names for the zones that will be output from this component. Default names will be applied to zones based on their order in the list if this value is left empty.
        zonePrograms_: A list of zone programs from the Honeybee_ListZonePrograms component that matches the number of breps in the _zoneMasses list.  These zone programs will be applied to the zones that are output from this component and will be used to set the shcedules and loads of these programs. This input can also be a single zoneProgram to be applied to all of the coneected zones.  If no value is connected here, the zone program Office::OpenOffice will be applied to the zones.
        isConditioned_: A list of True/False values that matches the number of breps in the _zoneMasses list. These True/False values will be applied to the ouput zones to either condition them with an Ideal Air Loads System (True) or not condition them at all (False).  This input can also be a single True/False value that can be applied to all of the connected zones.  If no value is connected here, all zones will be conditioned with an Ideal Air Loads System by default.
        maximumRoofAngle_: A maximum angle from the z vector in degrees that will be used to decide whether a given surface in the connected _zoneMasses is assigned as a roof or a wall. The default is 30 degrees but you may want to increase this if you have a roof that is at a steeper slope (ie. 45 degrees).
        _createHBZones: Set to True to generate the zones and assign energy simulation properties to your connected _zoneMasses.
    Returns:
        readMe!: ...
        HBZones: Honeybee zones that have all of the properties necessary for an energy simulation assigned to them.  Connect these to a "Honeybee_Label Zones" component to see some of these properties.
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import uuid


ghenv.Component.Name = 'Honeybee_Masses2Zones'
ghenv.Component.NickName = 'Mass2Zone'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance
import math

################################################################################

def main(maximumRoofAngle, zoneMasses, zoneNames, zonePrograms, isConditioned):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
            
    # import the classes
    # don't customize this part
    hb_EPZone = sc.sticky["honeybee_EPZone"]
    hb_EPSrf = sc.sticky["honeybee_EPSurface"]
    hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
    
    #Have a function to duplicate data.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    zoneNumber = len(zoneMasses)
    
    #If the length of the zonePrograms_ is 1, duplicate it to apply it to all zones.  Give a warning if the length of the list does not match the number of zones.
    if len(zonePrograms) == 1:
        zonePrograms = duplicateData(zonePrograms, zoneNumber)
        print "Zone program " + str(zonePrograms[0]) + " has been applied to all " + str(zoneNumber) + " connected zones."
    elif len(zonePrograms) == 0:
        print "No value connected for zoneProgram_.  Office::OpenOffice has been assigned by default."
    elif len(zonePrograms) != zoneNumber:
        warning = "The number of items in the connected zonePrograms_ list does not match the number of connected _zoneMasses. Office::OpenOffice will be assigned by default to zones that have no program in the list."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        print "Zones will be assigned a zone program based on the list of connected zonePrograms_."
    
    #If the length of the isConditioned_ is 1, duplicate it to apply it to all zones.  Give a warning if the length of the list does not match the number of zones.
    if len(isConditioned) == 1:
        isConditioned = duplicateData(isConditioned, zoneNumber)
        print "An IsConditioned value of " + str(isConditioned[0]) + " has been applied to all " + str(zoneNumber) + " connected zones."
    elif len(isConditioned) == 0:
        print "No value connected for isConditioned_.  All zones will be conditioned by default."
    elif len(isConditioned) != zoneNumber:
        warning = "The number of items in the connected isConditioned_ list does not match the number of connected _zoneMasses. Zones will be conditioned by default to if there is not isConditioned_ value for them in the list."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        print "Zones will be assigned an isConditioned value based on the list of connected isConditioned_ list."
    
    #Give a warning if the length of the zoneNames_ list does not match the number of zones.
    if len(zoneNames) == 0:
        print "No value connected for zoneNames_.  All zones will be assigned a default name based on their order in the list."
    elif len(zoneNames) != zoneNumber:
        warning = "The number of items in the connected zoneNames_ list does not match the number of connected _zoneMasses. Zones without a name in the list will be be assigned a default name based on their order in the list."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        print "Zones will be assigned a zoneName based on the list of connected zoneName_ list."
    
    HBZones = []
    # create zones out of masses
    for zoneKey, zone in enumerate(zoneMasses):
        # zone name
        try: zoneName = zoneNames[zoneKey].strip().replace(" ","_")
        except: zoneName = "zone_" + str(zoneKey)
        # str(uuid.uuid4())
        
        # zone programs
        try: thisZoneProgram = zonePrograms[zoneKey].split("::")
        except: thisZoneProgram = 'Office', 'OpenOffice'

        try: isZoneConditioned = isConditioned[zoneKey]
        except: isZoneConditioned = True
        
        thisZone = hb_EPZone(zone, zoneKey, zoneName, thisZoneProgram, isZoneConditioned)
        
        # assign surface types and construction based on type
        thisZone.decomposeZone(maximumRoofAngle)
        
        # append this zone to other zones
        HBZones.append(thisZone)
                
    return HBZones
        
        ################################################################################################


if _createHBZones == True and len(_zoneMasses)!=0 and _zoneMasses[0]!=None:
    
    try:  maximumRoofAngle = float(maxRoofAngle_)
    except: maximumRoofAngle = 30
    
    result= main(maximumRoofAngle, _zoneMasses, zoneNames_, zonePrograms_,isConditioned_)
    
    if result!=-1:
        zoneClasses = result 
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBZones  = hb_hive.addToHoneybeeHive(zoneClasses, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
