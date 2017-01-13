#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to change the schedules of your HBZones.
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: HBZones for which you want to change shcedules.
        occupancySchedules_: A text string representing the occupancy shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.
        occupancyActivitySchs_: A text string representing the shceudle for the metabolic rate of the occupants that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component. If this is a custon schedule, the values in it should be Watts and the "units_" or "_schedTypeLimits_" input should be "ActivityLevel."
        heatingSetPtSchedules_: A text string representing the heating setpoint shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.  If this is a custon schedule, the values in it should be Watts and the "units_" or "_schedTypeLimits_" input should be "Temperature."
        coolingSetPtSchedules_: A text string representing the cooling setpoint shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.  If this is a custon schedule, the values in it should be Watts and the "units_" or "_schedTypeLimits_" input should be "Temperature."
        lightingSchedules_: A text string representing the lighting shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.
        equipmentSchedules_: A text string representing the equipment shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.
        infiltrationSchedules_: A text string representing the infiltration shceudle that you want to use.  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.
        ventilationSchedules_: A text string representing the ventilation shceudle that you want to use.  Note that this schedule overrides the typical ventilation that occurs based on the occupancy shcedule and the "ventilationPerPerson."  The ventilation will be hard-sized based on this schedule and the maximum combined flowrates of "ventilationPerPerson" and "ventilationPerarea."  This can be either a shcedule from the "Honeybee_Call from EP Schedule Library" component, a schedule from the "Honeybee_Annual Schedule" component, or a CSV schedule from the "Honeybee_Create CSV Schedule" component.
    Returns:
        schedules: A report of what shcedules are assigned to each zone.
        HBZones: HBZones that have had thier shcedules modified.
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Schedules"
ghenv.Component.NickName = 'setEPZoneSchedules'
ghenv.Component.Message = 'VER 0.0.60\nNOV_10_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os



def checkTheInputs():
    #If the user puts in only one value, apply that value to all of the zones.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    if len(occupancySchedules_) == 1: occupancySchedules = duplicateData(occupancySchedules_, len(_HBZones))
    else: occupancySchedules = occupancySchedules_
    
    if len(occupancyActivitySchs_) == 1: occupancyActivitySchs = duplicateData(occupancyActivitySchs_, len(_HBZones))
    else: occupancyActivitySchs = occupancyActivitySchs_

    if len(coolingSetPtSchedules_) == 1: coolingSetPtSchedules = duplicateData(coolingSetPtSchedules_, len(_HBZones))
    else: coolingSetPtSchedules = coolingSetPtSchedules_
    
    if len(heatingSetPtSchedules_) == 1: heatingSetPtSchedules = duplicateData(heatingSetPtSchedules_, len(_HBZones))
    else: heatingSetPtSchedules = heatingSetPtSchedules_
    
    if len(lightingSchedules_) == 1: lightingSchedules = duplicateData(lightingSchedules_, len(_HBZones))
    else: lightingSchedules = lightingSchedules_
    
    if len(equipmentSchedules_) == 1: equipmentSchedules = duplicateData(equipmentSchedules_, len(_HBZones))
    else: equipmentSchedules = equipmentSchedules_
    
    if len(infiltrationSchedules_) == 1: infiltrationSchedules = duplicateData(infiltrationSchedules_, len(_HBZones))
    else: infiltrationSchedules = infiltrationSchedules_
    
    if len(ventilationSchedules_) == 1: ventilationSchedules = duplicateData(ventilationSchedules_, len(_HBZones))
    else: ventilationSchedules = ventilationSchedules_
    
    
    return occupancySchedules, occupancyActivitySchs, coolingSetPtSchedules, heatingSetPtSchedules, lightingSchedules, equipmentSchedules, infiltrationSchedules, ventilationSchedules


def main(HBZones, occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule, ventilationSchedules):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # make sure schedules are in HB schedule library.
    schedules = [occupancySchedule, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule, ventilationSchedules]
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
        if ventilationSchedules != [] and ventilationSchedules[0] != None:
            try: HBZone.ventilationSched = ventilationSchedules[zoneCount]
            except: HBZone.ventilationSched = ventilationSchedules[0]
        
        schedules.append(HBZone.getCurrentSchedules())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
    
    return HBZones, schedules
    


if _HBZones and _HBZones[0]!=None:
    occupancySchedules, occupancyActivitySchs, coolingSetPtSchedules, heatingSetPtSchedules, lightingSchedules, equipmentSchedules, infiltrationSchedules, ventilationSchedules = checkTheInputs()
    
    results = main(_HBZones, occupancySchedules, occupancyActivitySchs, heatingSetPtSchedules, coolingSetPtSchedules, lightingSchedules, equipmentSchedules, infiltrationSchedules, ventilationSchedules)
    
    if results != -1: HBZones, schedules = results