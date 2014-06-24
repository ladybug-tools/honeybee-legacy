# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Decompose zone by type
-
Provided by Honeybee 0.0.53

    Args:
        _HBZone: Honeybee Zone
    Returns:
        walls: A list of walls as breps.
        windows: A list of windows as breps.
        skylights: A list of skylights as breps.
        roofs: A list of roofs as breps.
        floors: A list of floors as breps.
        groundFloors: A list of ground floors as breps.
        ceilings: A list of ceilings as breps.
        airWalls: A list of airWalls as breps.
        shadings: A list of shadings as breps.
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Type"
ghenv.Component.NickName = 'decomposeByType'
ghenv.Component.Message = 'VER 0.0.53\nJUN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc

walls = []
windows = []
skylights =[]
roofs = []
floors = []
groundFloors = []
ceilings = []
shadings = []


if _HBZone!= None:
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        zone = hb_hive.callFromHoneybeeHive([_HBZone])[0]
    
        for srf in zone.surfaces:
            if srf.type == 0:
                if srf.hasChild: walls.append(srf.punchedGeometry)
                else: walls.append(srf.geometry)
            elif srf.type == 1:
                if srf.hasChild: roofs.append(srf.punchedGeometry)
                else: roofs.append(srf.geometry)
            elif srf.type == 2: floors.append(srf.geometry)
            elif str(srf.type) == "2.5": groundFloors.append(srf.geometry)
            elif srf.type == 3: ceilings.append(srf.geometry)
            elif srf.type == 4: airWalls.append(srf.geometry)
            elif srf.type == 6: shadings.append(srf.geometry)
            if srf.hasChild and srf.type == 0:
                try:
                    for childSrf in srf.childSrfs:
                        windows.append(childSrf.geometry)
                except Exception, e:
                    print `e`
                    pass
            if srf.hasChild and srf.type == 1:
                try:
                    for childSrf in srf.childSrfs:
                        skylights.append(childSrf.geometry)
                except Exception, e:
                    print `e`
                    pass
    except:
        pass
