# By Mostapha Sadeghipour Roudsari
# sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones based on floor height
-
Provided by Honeybee 0.0.56

    Args:
        _HBZones: List of HBZones

    Returns:
        floorHeights: List of floor heights
        HBZones: Honeybee zones. Each branch represents a different floor
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Floor'
ghenv.Component.NickName = 'separateZonesByFloor'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
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
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
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
            zones = hb_hive.addToHoneybeeHive(zoneList, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
            HBZones.AddRange(zones, p)
