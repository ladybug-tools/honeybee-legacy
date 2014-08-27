# Update EP
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Update EP construction of zone based on type

-
Provided by Honeybee 0.0.54
    
    Args:
        _HBZone: Honeybee zone
        intWallEPConstruction_: Optional new construction for interior walls
        intWindowEPConstruction_: Optional new construction for interior window 
        intFloorEPConstruction_: Optional new construction for interior floor
        intCeilingEPConstruction_: Optional new construction for interior ceiling
    Returns:
        modifiedHBZone:  Honeybee zone with update construction assigned

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Interior Construction"
ghenv.Component.NickName = 'setEPZoneIntCnstr'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def main(HBZone, wallEPCnst, windowEPCnst, flrEPCnst, ceilEPCnst):
    # Make sure Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        return -1
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try: HBZoneObject = hb_hive.callFromHoneybeeHive([HBZone])[0]
    except Exception, e: HBZoneObject = None
    
    # here I should check for each construction to be in the library
    EPConstructios = sc.sticky ["honeybee_constructionLib"]["List"]
    warning = ""
    if wallEPCnst not in EPConstructios:
        if wallEPCnst != None:
            warning += "Can't find wall construction in Honeybee library.\n"
            wallEPCnst = None
    if windowEPCnst not in EPConstructios:
        if windowEPCnst != None:
            warning += "Can't find window construction in Honeybee library.\n"
            windowEPCnst = None
    if flrEPCnst not in EPConstructios:
        if flrEPCnst != None:
            warning += "Can't find floor construction in Honeybee library.\n"
            flrEPCnst = None
    if ceilEPCnst not in EPConstructios:
        if ceilEPCnst != None:
            warning += "Can't find ceiling construction in Honeybee library.\n"
            ceilEPCnst = None
    
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    if HBZoneObject != None:
        for srf in HBZoneObject.surfaces:
            if srf.BCObject.name != "": # only internal surfaces
                if windowEPCnst!=None and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        childSrf.EPConstruction = windowEPCnst
                if srf.type == 0 and wallEPCnst!=None:
                    srf.EPConstruction = wallEPCnst
                    srf.BCObject.EPConstruction = wallEPCnst
                elif srf.type == 2 and flrEPCnst!=None:
                    srf.EPConstruction = flrEPCnst
                    srf.BCObject.EPConstruction = flrEPCnst
                elif srf.type == 3 and ceilEPCnst!=None:
                    srf.EPConstruction = ceilEPCnst
                    srf.BCObject.EPConstruction = ceilEPCnst
                    
        # add zones to dictionary
        HBZones  = hb_hive.addToHoneybeeHive([HBZoneObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBZones
    
    else:
        return -1

if _HBZone:
    result = main(_HBZone, intWallEPConstruction_, intWindowEPConstruction_, intFloorEPConstruction_, intCeilingEPConstruction_)
    if result!=-1: modifiedHBZone = result