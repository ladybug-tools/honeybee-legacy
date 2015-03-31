# Set EP Zone Interior Construction
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set EP Zone Interior Construction

-
Provided by Honeybee 0.0.56
    
    Args:
        _HBZone: Honeybee zone
        intWallEPConstruction_: Optional new construction for interior walls
        intWindowEPConstruction_: Optional new construction for interior windows 
        intFloorEPConstruction_: Optional new construction for interior floors and ceilings
    Returns:
        modifiedHBZone:  Honeybee zone with updated constructions

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Interior Construction"
ghenv.Component.NickName = 'setEPZoneIntCnstr'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh


def updateZoneMixing(surface1, zone1, zone2):
    #Change the air mixing between the zone and other zones to "True"
    zone1.mixAir = True
    zone2.mixAir = True
    
    #Append the zone to be mixed with to the mixAirZoneList.
    zone1.mixAirZoneList.append(zone2.name)
    zone2.mixAirZoneList.append(zone1.name)
    
    #Calculate a rough flow rate of air based on the cross-sectional area of the surface between them.
    flowFactor = zone1.mixAirFlowRate
    flowRate = (rc.Geometry.AreaMassProperties.Compute(surface1.geometry).Area)*flowFactor
    
    #Append the flow rate of mixing to the mixAirFlowList
    zone1.mixAirFlowList.append(flowRate)
    zone2.mixAirFlowList.append(flowRate)
    
    return flowRate

def checkAirWalls(construction, srf):
    if construction.ToUpper() == "AIR WALL":
        srf.setType(4, isUserInput= True)
        updateZoneMixing(srf, srf.parent, srf.BCObject.parent)

def main(HBZone, wallEPCnst, windowEPCnst, flrEPCnst):
    
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
    
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()

    if HBZoneObject != None:
        for srf in HBZoneObject.surfaces:
            if srf.BCObject.name != "": # only internal surfaces
                print srf.BCObject.name
                print srf.BCObject
                if windowEPCnst!=None and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        hb_EPObjectsAux.assignEPConstruction(childSrf, windowEPCnst, ghenv.Component)
                        hb_EPObjectsAux.assignEPConstruction(childSrf.BCObject, windowEPCnst, ghenv.Component)
                        if windowEPCnst.ToUpper() == "AIR WALL":
                            updateZoneMixing(childSrf, srf.parent, srf.BCObject.parent)
                if srf.type == 0 and wallEPCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, wallEPCnst, ghenv.Component)
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, wallEPCnst, ghenv.Component)
                    checkAirWalls(wallEPCnst, srf)
                elif (srf.type == 2 or srf.type == 3) and flrEPCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, flrEPCnst, ghenv.Component)
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, flrEPCnst, ghenv.Component)
                    checkAirWalls(flrEPCnst, srf)
                    
        # add zones to dictionary
        HBZones  = hb_hive.addToHoneybeeHive([HBZoneObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBZones
    
    else:
        return -1

if _HBZone:
    result = main(_HBZone, intWallEPConstruction_, intWindowEPConstruction_, \
            intFloorEPConstruction_)
    if result!=-1: modifiedHBZone = result