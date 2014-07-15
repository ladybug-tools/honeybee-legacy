# By Chien Si Harriman - Modified by Mostapha Sadeghipour Roudsari
# Chien.Harriman@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones into perimeter and core.
-
Provided by Honeybee 0.0.53

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
ghenv.Component.Message = 'VER 0.0.53\nJUL_15_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import uuid

import scriptcontext as sc
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(HBZones):
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


perimeters,interiors = main(_HBZones)