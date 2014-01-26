"""
Decompose zone by type
-
Provided by Honeybee 0.0.42

    Args:
        _HBZone: Honeybee Zone
    Returns:
        walls: List of walls as breps
        windows: List of windows as breps
        skylights: List of skylights as breps
        roofs: List of roofs as breps
        floors: List of floors as breps
        ceilings: List of ceilings as breps
        airWalls: List of airWalls as breps
        shadings: List of shadings as breps
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Type"
ghenv.Component.NickName = 'decomposeByType'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import scriptcontext as sc

walls = []
windows = []
skylights =[]
roofs = []
floors = []
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