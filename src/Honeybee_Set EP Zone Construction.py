# Update EP
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Update EP construction of zone based on type

-
Provided by Honeybee 0.0.55
    
    Args:
        _HBZone: Honeybee zone
        wallEPConstruction_: Optional new construction for walls
        windowEPConstruction_: Optional new construction for window 
        roofEPConstruction_: Optional new construction for roof
        floorEPConstruction_: Optional new construction for floor
        ceilingEPConstruction_: Optional new construction for ceiling
    Returns:
        modifiedHBZone:  Honeybee zone with update construction assigned

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Construction"
ghenv.Component.NickName = 'setEPZoneCnstr'
ghenv.Component.Message = 'VER 0.0.55\nJAN_27_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def main(HBZone, wallEPCnst, windowEPCnst, roofEPCnst, flrEPCnst, ceilEPCnst):
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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try: HBZoneObject = hb_hive.callFromHoneybeeHive([HBZone])[0]
    except Exception, e: HBZoneObject = None
    
    #Have a function to check whether a construction is in a library.
    def checkConstruction(EPConstruction):
        # if it is just the name of the material make sure it is already defined
        if len(EPConstruction.split("\n")) == 1:
            # if the material is not in the library add it to the library
            if not hb_EPObjectsAux.isEPConstruction(EPConstruction):
                warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                            "Add the construction to the library and try again."
                print warningMsg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                return None
            else:
                return EPConstruction
        else:
            # it is a full string
            added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(EPConstruction, overwrite = True)
            
            if not added:
                msg = name + " is not added to the project library!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                print msg
                return None
            else:
                return EPConstruction
    
    # here I should check for each construction to be in the library
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    
    if wallEPCnst != None:
        wallEPCnst = checkConstruction(wallEPCnst)
    if windowEPCnst != None:
        windowEPCnst = checkConstruction(windowEPCnst)
    if roofEPCnst != None:
        roofEPCnst = checkConstruction(roofEPCnst)
    if flrEPCnst != None:
        flrEPCnst = checkConstruction(flrEPCnst)
    if ceilEPCnst != None:
        ceilEPCnst = checkConstruction(ceilEPCnst)
    
    if HBZoneObject != None:
        for srf in HBZoneObject.surfaces:
            if srf.BCObject.name == "": # not internal surfaces 
                if windowEPCnst!=None and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        childSrf.EPConstruction = windowEPCnst
                if srf.type == 0 and wallEPCnst!=None:
                    srf.EPConstruction = wallEPCnst
                elif srf.type == 1 and roofEPCnst!=None:
                    srf.EPConstruction = roofEPCnst
                elif srf.type == 2 and flrEPCnst!=None:
                    srf.EPConstruction = flrEPCnst
                elif srf.type == 3 and ceilEPCnst!=None:
                    srf.EPConstruction = ceilEPCnst
                
        # add zones to dictionary
        HBZones  = hb_hive.addToHoneybeeHive([HBZoneObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBZones
    
    else:
        return -1

if _HBZone:
    result = main(_HBZone, wallEPConstruction_, windowEPConstruction_, roofEPConstruction_, floorEPConstruction_, ceilingEPConstruction_)
    if result!=-1: modifiedHBZone = result