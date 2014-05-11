# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Select surfaces by type
-
Provided by Honeybee 0.0.52
    Args:
        _HBZones: Honeybee Zones
        _showWalls_: Set to true to output the walls
        _showWindows_: Set to true to output the windows
        _showAirWalls_: Set to true to output the air walls
        _showFloors_: Set to true to output the floors
        _showCeiling_: Set to true to output the cieling
        _showRoofs_: Set to true to output the roofs
    Returns:
        surfaces: Output surfaces as Grasshopper objects
"""
ghenv.Component.Name = "Honeybee_Select by Type"
ghenv.Component.NickName = 'selByType'
ghenv.Component.Message = 'VER 0.0.52\nMAY_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc

surfaces = []
showCases = []
if _showWalls_: showCases.append(0)
if _showAirWalls_: showCases.append(4)
if _showFloors_: showCases.append(2)
if _showCeilings_: showCases.append(3)
if _showRoofs_: showCases.append(1)

if _HBZones and _HBZones[0]!=None:
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)
    
    for zone in HBZoneObjects:
        for srf in zone.surfaces:
            try:
                if srf.type in showCases:
                    if srf.type == 0 and srf.hasChild:
                        surfaces.append(srf.punchedGeometry)
                    else:
                        surfaces.append(srf.geometry)
                        
                if _showWindows_ and srf.hasChild:
                    for childSrf in srf.childSrfs: surfaces.append(childSrf.geometry)
            except:
                pass
