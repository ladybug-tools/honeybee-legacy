# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Decompose zone surfaces by boundary condition
-
Provided by Honeybee 0.0.55

    Args:
        _HBZone: Honeybee Zone
        
    Returns:
        outdoors: A list of surfaces which has outdoors boundary condition
        surface: A list of surfaces which has surface boundary condition
        adiabatic: A list of surfaces which has adiabatic boundary condition
        ground: A list of surfaces which has ground boundary condition
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Boundary Condition"
ghenv.Component.NickName = 'decomposeByBC'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | Honeybee"
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
    
    outdoors = []
    surface = []
    adiabatic = []
    ground = []

    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()

    zone = hb_hive.callFromHoneybeeHive([HBZone])[0]

    for srf in zone.surfaces:
        if srf.BC.lower() == "outdoors":
            if srf.hasChild:
                outdoors.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    outdoors.append(childSrf.geometry)
            else:
                outdoors.append(srf.geometry)
        elif srf.BC.lower() == "surface":
            if srf.hasChild:
                surface.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    surface.append(childSrf.geometry)
            else:
                surface.append(srf.geometry)
        elif srf.BC.lower() == "adiabatic":
            if srf.hasChild:
                adiabatic.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    adiabatic.append(childSrf.geometry)
            else:
                adiabatic.append(srf.geometry)
        elif srf.BC.lower() == "ground":
            ground.append(srf.geometry)
        
    return outdoors, surface, adiabatic, ground


#    # add to the hive
#    hb_hive = sc.sticky["honeybee_Hive"]()
#    HBSurface  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if _HBZone!= None:
    HBSurfaces = main(_HBZone)
    
    if HBSurfaces != -1:
        outdoors = HBSurfaces[0]
        surface = HBSurfaces[1]
        adiabatic = HBSurfaces[2]
        ground = HBSurfaces[3]