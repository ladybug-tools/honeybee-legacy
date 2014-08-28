# By Mostapha Sadeghipour Roudsari
# sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones based on zone program
-
Provided by Honeybee 0.0.54

    Args:
        _HBZones: List of HBZones

    Returns:
        zonePrograms: List of programs
        HBZones: Honeybee zones. Each branch represents a different program
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Program'
ghenv.Component.NickName = 'separateZonesByProgram'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
        zoneProgram = zone.bldgProgram + "::" + zone.zoneProgram
        
        if zoneProgram not in HBZones.keys():
            HBZones[zoneProgram] = []
        
        HBZones[zoneProgram].append(zone)
        
    return HBZones

if _HBZones and _HBZones!=None:
    
    orderedHBZones = main(_HBZones)
    
    if orderedHBZones!= -1:
        
        keys = orderedHBZones.keys()
        keys.sort()
        
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        HBZones = DataTree[Object]()
        zonePrograms = []
        
        for count, key in enumerate(keys):
            p = GH_Path(count)
            zonePrograms.append(key)
            
            zones = hb_hive.addToHoneybeeHive(orderedHBZones[key], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
            HBZones.AddRange(zones, p)
