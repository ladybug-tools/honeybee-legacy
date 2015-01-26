# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to break down the geometry of your zone by the surface type.  This is useful for previewing your zones in the rhino scene and making sure that each surface of your zones has the correct surface type.
-
Provided by Honeybee 0.0.55

    Args:
        _HBZone: Honeybee Zones for which you want to preview the different surface types.
    Returns:
        walls: A list of the exterior walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        interiorWalls: A list of the interior walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        airWalls: A list of the air walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        windows: A list of windows of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        interiorWindows: A list of interior windows of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        skylights: A list of skylights of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        roofs: A list of roofs of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        ceilings: A list of ceilings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        floors: A list of floors of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        exposedFloors: A list of floors exposed to the outside air as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        groundFloors: A list of ground floors of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundWalls: A list of underground walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundSlabs: A list of underground floor slabs of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundCeilings: A list of underground ceilings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        shadings: A list of shadings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Type"
ghenv.Component.NickName = 'decomposeByType'
ghenv.Component.Message = 'VER 0.0.55\nJAN_11_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nJAN_11_2015
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
    undergroundSlabs = []
    undergroundCeilings = []
    shadings = []
    airWalls = []

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
        elif srf.type == 2.25: undergroundSlabs.append(srf.geometry)
        elif srf.type == 2.5: groundFloors.append(srf.geometry)
        elif srf.type == 2.75: exposedFloors.append(srf.geometry)
        elif srf.type == 3: ceilings.append(srf.geometry)
        elif srf.type == 4: airWalls.append(srf.geometry)
        elif srf.type == 6: shadings.append(srf.geometry)
        
        
    return walls, interiorWalls, airWalls, windows, interiorWindows, skylights, roofs, \
           ceilings, floors, exposedFloors, groundFloors, undergroundWalls, \
           undergroundSlabs, undergroundCeilings, shadings


#    # add to the hive
#    hb_hive = sc.sticky["honeybee_Hive"]()
#    HBSurface  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if _HBZone!= None:
    HBSurfaces = main(_HBZone)
    
    if HBSurfaces != -1:
        walls = HBSurfaces[0]
        interiorWalls = HBSurfaces[1]
        airWalls = HBSurfaces[2]
        windows = HBSurfaces[3]
        interiorWindows = HBSurfaces[4]
        skylights = HBSurfaces[5]
        roofs = HBSurfaces[6]
        ceilings = HBSurfaces[7]
        floors = HBSurfaces[8]
        exposedFloors = HBSurfaces[9]
        groundFloors = HBSurfaces[10]
        undergroundWalls = HBSurfaces[11]
        undergroundSlabs = HBSurfaces[12]
        undergroundCeilings = HBSurfaces[13]
        shadings = HBSurfaces[14]