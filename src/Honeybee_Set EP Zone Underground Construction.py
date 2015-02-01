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
        undergroundWallEPConstruction_: Optional new construction for underground walls
        groundFloorEPConstruction_: Optional new construction for ground floors
        undergroundSlabEPConstruction_: Optional new construction for underground slabs
        undergroundCeilingEPConstruction_: Optional new construction for underground ceilings
    Returns:
        modifiedHBZone:  Honeybee zone with updated constructions

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Underground Construction"
ghenv.Component.NickName = 'setEPZoneUnderGroundCnstr'
ghenv.Component.Message = 'VER 0.0.55\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nFEB_01_2015
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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

def main(HBZone, ugWallEPCnst, gFlrEPCnst, ugSlabEPCnst, ugCeilEPCnst):
    
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
            if srf.type == 0.5 and ugWallEPCnst!=None:
                hb_EPObjectsAux.assignEPConstruction(srf, ugWallEPCnst, ghenv.Component)
                if srf.BCObject.name != "":
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, ugWallEPCnst, ghenv.Component)
                    checkAirWalls(ugWallEPCnst, srf)
            elif srf.type == 2.5 and gFlrEPCnst!=None:
                hb_EPObjectsAux.assignEPConstruction(srf, gFlrEPCnst, ghenv.Component)
                if srf.BCObject.name != "":
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, gFlrEPCnst, ghenv.Component)
                    checkAirWalls(gFlrEPCnst, srf)
            elif srf.type == 2.25 and ugSlabEPCnst!=None:
                hb_EPObjectsAux.assignEPConstruction(srf, ugSlabEPCnst, ghenv.Component)
                if srf.BCObject.name != "":
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, ugSlabEPCnst, ghenv.Component)
                    checkAirWalls(ugSlabEPCnst, srf)
            elif srf.type == 1.5 and ugCeilEPCnst!=None:
                hb_EPObjectsAux.assignEPConstruction(srf, ugCeilEPCnst, ghenv.Component)
                if srf.BCObject.name != "":
                    hb_EPObjectsAux.assignEPConstruction(srf.BCObject, ugCeilEPCnst, ghenv.Component)
                    checkAirWalls(ugCeilEPCnst, srf)
                
        # add zones to dictionary
        HBZones  = hb_hive.addToHoneybeeHive([HBZoneObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBZones
    
    else:
        return -1

if _HBZone:
    result = main(_HBZone, undergroundWallEPConstruction_, groundFloorEPConstruction_, \
            undergroundSlabEPConstruction_, undergroundCeilingEPConstruction_)
    
    if result!=-1: modifiedHBZone = result