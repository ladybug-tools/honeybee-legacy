# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Select surfaces by type
-
Provided by Honeybee 0.0.56
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
ghenv.Component.NickName = 'selByType_'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

surfaces = []
HBSurfacestypezero = []
otherHBSurfaces = []
showCases = []
if _showWalls_: showCases.append(0)
if _showAirWalls_: showCases.append(4)
if _showFloors_: showCases.append(2)
if _showCeilings_: showCases.append(3)
if _showRoofs_: showCases.append(1)

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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)
    
    for zone in HBZoneObjects:
        
        # Extract surfaces from HBZones?
        for srf in zone.surfaces:
            try:
                if srf.type in showCases:
                    if srf.type == 0 and srf.hasChild:
                        surfaces.append(srf.punchedGeometry)
                        
                        HBSurfacestypezero.append(srf) # Added by Anton Szilasi for Honeybee PV generator component
                        
                    else:
                        surfaces.append(srf.geometry)

                        otherHBSurfaces.append(srf) # Added by Anton Szilasi for Honeybee PV generator component

                if _showWindows_ and srf.hasChild:
                    for childSrf in srf.childSrfs: surfaces.append(childSrf.geometry)
            except:
                pass
                
    HBSurfaces = hb_hive.addToHoneybeeHive(otherHBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    
    return surfaces,HBSurfaces
    
if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones)

    if results!=-1:
        surfaces,HBSurfaces = results
