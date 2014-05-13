# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set Schedules
-
Provided by Honeybee 0.0.53

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
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh


def main(HBZones, occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    # make sure schedules are in HB schedule 
    schedules = [occupancySchedule, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule]
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"]["List"]
    
    for schedule in schedules:
        if schedule!=None and schedule not in HBScheduleList:
            msg = "Cannot find " + schedule + " in Honeybee schedule library.\n" + \
                  "Schedule names are case sensitive."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    schedules = []
    for HBZone in HBObjectsFromHive:
        if occupancySchedule != None: HBZone.occupancySchedule = occupancySchedule
        if occupancyActivitySch != None:  HBZone.occupancyActivitySch = occupancyActivitySch
        if heatingSetPtSchedule != None: HBZone.heatingSetPtSchedule = heatingSetPtSchedule
        if coolingSetPtSchedule != None: HBZone.coolingSetPtSchedule = coolingSetPtSchedule
        if lightingSchedule != None: HBZone.lightingSchedule = lightingSchedule
        if equipmentSchedule != None: HBZone.equipmentSchedule = equipmentSchedule
        if infiltrationSchedule != None: HBZone.infiltrationSchedule = infiltrationSchedule
        schedules.append(HBZone.getCurrentSchedules())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones, schedules
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones, occupancySchedule_, occupancyActivitySch_, heatingSetPtSchedule_, coolingSetPtSchedule_, lightingSchedule_, equipmentSchedule_, infiltrationSchedule_)
    
    if results != -1: HBZones, schedules = results