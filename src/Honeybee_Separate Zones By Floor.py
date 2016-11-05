#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <sadeghipour@gmail.com> 
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
Separate zones based on floor height
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: List of HBZones

    Returns:
        floorHeights: List of floor heights
        HBZones: Honeybee zones. Each branch represents a different floor
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Floor'
ghenv.Component.NickName = 'separateZonesByFloor'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import uuid

import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def main(HBZones):

    if not sc.sticky.has_key("honeybee_release"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
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
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.visualizeFromHoneybeeHive(HBZones)
    
    HBZones = {}
    
    for zone in HBZonesFromHive:
        floorH = "%.3f"%zone.getFloorZLevel()
        # print floorH
        if floorH not in HBZones.keys():
            HBZones[floorH] = []
        
        HBZones[floorH].append(zone)
    
    HBZones = sorted(HBZones.items(), key = lambda d: float(d[0]))
    
    return HBZones

if _HBZones and _HBZones!=None:
    
    HBSortedZones = main(_HBZones)
    
    if HBSortedZones != -1:
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        HBZones = DataTree[Object]()
        floorHeights = []
        
        for count, floorInfo in enumerate(HBSortedZones):
            p = GH_Path(count)
            flrH = floorInfo[0]
            zoneList = floorInfo[1]
            floorHeights.append(flrH)
            # item 0 is the heights
            zones = hb_hive.addToHoneybeeHive(zoneList, ghenv.Component, count==0)
            HBZones.AddRange(zones, p)
