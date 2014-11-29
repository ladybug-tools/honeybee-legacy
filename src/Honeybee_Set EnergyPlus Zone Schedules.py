# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set Schedules
-
Provided by Honeybee 0.0.55

    Args:
        _HBZones:...
        occupancySchedule_: ...
        heatingSetPtSchedule_: ...
        coolingSetPtSchedule_: ...
        lightingSchedule_: ...
        equipmentSchedule_: ...
        infiltrationSchedule_: ...
    Returns:
        schedules:...
        HBZones:...
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Schedules"
ghenv.Component.NickName = 'setEPZoneSchedules'
ghenv.Component.Message = 'VER 0.0.55\nNOV_29_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os


def main(HBZones, occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule):
    # check for Honeybee
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
    
    # make sure schedules are in HB schedule 
    schedules = [occupancySchedule, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule]
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
    
    for scheduleList in schedules:
        for schedule in scheduleList: 
            
            if schedule!=None:
                schedule= schedule.upper()
            
            if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
                msg = "Cannot find " + schedule + " in Honeybee schedule library."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
            elif schedule!=None and schedule.lower().endswith(".csv"):
                # check if csv file is existed
                if not os.path.isfile(schedule):
                    msg = "Cannot find the shchedule file: " + schedule
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    schedules = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        if occupancySchedule != [] and occupancySchedule[0] != None:
            try: HBZone.occupancySchedule = occupancySchedule[zoneCount]
            except: HBZone.occupancySchedule = occupancySchedule[0]
        if occupancyActivitySch != [] and occupancyActivitySch[0] != None:
            try: HBZone.occupancyActivitySch = occupancyActivitySch[zoneCount]
            except: HBZone.occupancyActivitySch = occupancyActivitySch[0]
        if heatingSetPtSchedule != [] and heatingSetPtSchedule[0] != None:
            try: HBZone.heatingSetPtSchedule = heatingSetPtSchedule[zoneCount]
            except: HBZone.heatingSetPtSchedule = heatingSetPtSchedule[0]
        if coolingSetPtSchedule != [] and coolingSetPtSchedule[0] != None:
            try: HBZone.coolingSetPtSchedule = coolingSetPtSchedule[zoneCount]
            except: HBZone.coolingSetPtSchedule = coolingSetPtSchedule[0]
        if lightingSchedule != [] and lightingSchedule[0] != None:
            try: HBZone.lightingSchedule = lightingSchedule[zoneCount]
            except: HBZone.lightingSchedule = lightingSchedule[0]
        if equipmentSchedule != [] and equipmentSchedule[0] != None:
            try: HBZone.equipmentSchedule = equipmentSchedule[zoneCount]
            except: HBZone.equipmentSchedule = equipmentSchedule[0]
        if infiltrationSchedule != [] and infiltrationSchedule[0] != None:
            try: HBZone.infiltrationSchedule = infiltrationSchedule[zoneCount]
            except: HBZone.infiltrationSchedule = infiltrationSchedule[0]
        
        schedules.append(HBZone.getCurrentSchedules())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones, schedules
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones, occupancySchedules_, occupancyActivitySchs_, heatingSetPtSchedules_, coolingSetPtSchedules_, lightingSchedules_, equipmentSchedules_, infiltrationSchedules_)
    
    if results != -1: HBZones, schedules = results