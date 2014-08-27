# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Decompose zone by type
-
Provided by Honeybee 0.0.54

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
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc



def main(HBZone):
    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return

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
        return
        
    walls = []
    interiorWalls = []
    windows = []
    interiorWindows = []
    skylights =[]
    roofs = []
    ceilings = []
    floors = []
    exposedFloors = []
    groundFloors = []
    undergroundWalls = []
    undergroundCeilings = []
    shadings = []

    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()

    zone = hb_hive.callFromHoneybeeHive([HBZone])[0]

    for srf in zone.surfaces:
        # WALL
        if srf.type == 0:
            if srf.BC.upper() == "SURFACE":
                if srf.hasChild:
                    interiorWalls.append(srf.punchedGeometry)
                    for childSrf in srf.childSrfs:
                        interiorWindows.append(childSrf.geometry)
                else:
                    interiorWalls.append(srf.geometry)
                    
            else:
                if srf.hasChild:
                    walls.append(srf.punchedGeometry)
                    
                    for childSrf in srf.childSrfs:
                        windows.append(childSrf.geometry)
                else:
                    walls.append(srf.geometry)
                        
        # underground wall
        elif srf.type == 0.5:
            undergroundWalls.append(srf.geometry)
        
        # Roof
        elif srf.type == 1:
            if srf.hasChild:
                roofs.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    skylights.append(childSrf.geometry)
            else:
                roofs.append(srf.geometry)
        
        # underground ceiling
        elif srf.type == 1.5:
            undergroundCeilings.append(srf.geometry)
            
        elif srf.type == 2: floors.append(srf.geometry)
        elif srf.type == 2.5: groundFloors.append(srf.geometry)
        elif srf.type == 2.75: exposedFloors.append(srf.geometry)
        elif srf.type == 3: ceilings.append(srf.geometry)
        elif srf.type == 4: airWalls.append(srf.geometry)
        elif srf.type == 6: shadings.append(srf.geometry)
        
        
    return walls, interiorWalls, windows, interiorWindows, skylights, roofs, \
           ceilings, floors, exposedFloors, groundFloors, undergroundWalls, \
           undergroundSlabs, undergroundCeilings, shadings


#    # add to the hive
#    hb_hive = sc.sticky["honeybee_Hive"]()
#    HBSurface  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if _HBZone!= None:
    HBSurfaces = main(_HBZone)
    
    if HBSurfaces:
        walls = HBSurfaces[0]
        interiorWalls = HBSurfaces[1]
        windows = HBSurfaces[2]
        interiorWindows = HBSurfaces[3]
        skylights = HBSurfaces[4]
        roofs = HBSurfaces[5]
        ceilings = HBSurfaces[6]
        floors = HBSurfaces[7]
        exposedFloors = HBSurfaces[8]
        groundFloors = HBSurfaces[9]
        undergroundWalls = HBSurfaces[10]
        undergroundSlabs = HBSurfaces[11]
        undergroundCeilings = HBSurfaces[12]
        shadings = HBSurfaces[13]