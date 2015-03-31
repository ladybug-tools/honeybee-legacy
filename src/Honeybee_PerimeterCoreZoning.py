# By Chien Si Harriman - Modified by Mostapha Sadeghipour Roudsari
# Chien.Harriman@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones into perimeter and core
-
Provided by Honeybee 0.0.56

    Args:
        _bldgMasses: A Closed brep representing a building or a list of closed Breps.
        bldgsFlr2FlrHeights_: A floor height in Rhino model units or list of building floor heights for the geometries.
        perimeterZoneDepth_: A perimeter zone dpeth in Rhino model units or list of bperimeter depths for the geometries.
        _createHoneybeeZones: Set Boolean to True to split up the building mass into zones.
    Returns:
        readMe!: ...
        _splitBldgMasses: A lot of breps that correspond to the recommended means of breaking up geometry into zones for energy simulations.
"""


ghenv.Component.Name = 'Honeybee_PerimeterCoreZoning'
ghenv.Component.NickName = 'PerimeterCore'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import uuid

import scriptcontext as sc
import Grasshopper.Kernel as gh


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
    print len(HBZonesFromHive)
    interiorzones = []
    perimeterzones = []
    for zone in HBZonesFromHive:
        
        for surface in zone.surfaces:
            if surface.type == 0 and surface.BC.upper() == "OUTDOORS":
                #this is a perimeter wall
                perimeterzones.append(zone)
                break
                
        if zone not in perimeterzones:
            interiorzones.append(zone)
    
    perims  = hb_hive.addToHoneybeeHive(perimeterzones, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    ints = hb_hive.addToHoneybeeHive(interiorzones, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return perims,ints


zones = main(_HBZones)

if zones!=-1:
    perimeters, interiors = zones