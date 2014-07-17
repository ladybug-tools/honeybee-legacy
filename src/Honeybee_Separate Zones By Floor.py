# By Mostapha Sadeghipour Roudsari
# sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones based on floor height
-
Provided by Honeybee 0.0.53

    Args:
        _HBZones: List of HBZones

    Returns:
        floorHeights: List of floor heights
        HBZones: Honeybee zones. Each branch represents a different floor
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Floor'
ghenv.Component.NickName = 'separateZonesByFloor'
ghenv.Component.Message = 'VER 0.0.53\nJUL_17_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import uuid

import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(HBZones):
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    HBZones = {}
    
    for zone in HBZonesFromHive:
        floorH = "%.3f"%zone.getFloorZLevel()
        # print floorH
        if floorH not in HBZones.keys():
            HBZones[floorH] = []
        
        HBZones[floorH].append(zone)
        
        
    return HBZones

if _HBZones and _HBZones!=None:
    
    orderedHBZones = main(_HBZones)
    
    keys = orderedHBZones.keys()
    keys.sort()
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    HBZones = DataTree[Object]()
    floorHeights = []
    
    for count, key in enumerate(keys):
        p = GH_Path(count)
        floorHeights.append(key)
        
        zones = hb_hive.addToHoneybeeHive(orderedHBZones[key], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        HBZones.AddRange(zones, p)
