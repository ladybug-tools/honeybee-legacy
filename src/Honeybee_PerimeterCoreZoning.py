# By Chien Si Harriman
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
ghenv.Component.Message = 'VER 0.0.53\nMAY_18_2014'
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
            
            coordinatesList = surface.extractPoints()
            if not isinstance(coordinatesList[0], list) and not isinstance(coordinatesList[0], tuple):
                coordinatesList = [coordinatesList]
            
            #do the work to map the coordinatesList appropriately, 
            #this will change as the honeybee object changes
            #for now, here is the test for an unmeshed surface
            try:
                #meshed surface
                #unwrap the meshed surfaces to get a list of each on
                print surface.type, surface.BC
                if surface.type == 0 and surface.BC == "Outdoors":
                    #this is a perimeter wall
                    perimeterzones.append(zone)
            except:
                print "not meshed"
        if zone in perimeterzones:
            pass
        else:
            interiorzones.append(zone)
    perims  = hb_hive.addToHoneybeeHive(perimeterzones, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    ints = hb_hive.addToHoneybeeHive(interiorzones, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    return perims,ints


perimeters,interiors = main(_HBZones)

print len(perimeters)
