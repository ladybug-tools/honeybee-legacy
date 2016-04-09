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
Use this component to set Zone Thresholds like daylighting thresholds and setpoints.
-
Provided by Honeybee 0.0.59

    Args:
        _HBZones: HBZones for which zone thresholds will be set.
        daylightThreshold_: A number or list of numbers that represent the minimum lux to be achieved in the zone.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        coolingSetPt_: A number or list of numbers that represent the thermostat cooling setpoint in degrees Celcius.  The cooling setpoint is effectively the indoor temperature above which the cooling system is turned on.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        coolingSetback_: A number or list of numbers that represent the thermostat cooling setback in degrees Celcius.  The cooling setback is the indoor temperature that the space will be kept at when it is unoccipied.  Note that not all building types have a setback.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        heatingSetPt_: A number or list of numbers that represent the thermostat heating setpoint in degrees Celcius.  The heating setpoint is effectively the indoor temperature below which the heating system is turned on.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        heatingSetback_: A number or list of numbers that represent the thermostat heating setback in degrees Celcius.  The heating setback is the indoor temperature that the space will be kept at when it is unoccipied.  Note that not all building types have a setback.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxHumidity_: A number or list of numbers that represent the maximum relative humidity allowed by a humidistat in %.  The HVAC will dehumidify the zone air  if the relative humidity goes above this threshold.  The default is set to 'no limit' or no humidistat. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        minHumidity_ : A number or list of numbers that represent the minimum relative humidity allowed by a humidistat in %.  The HVAC will humidify the zone air if the relative humidity goes below this threshold.  The default is set to 'no limit' or no humidistat. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
    Returns:
        HBZones: HBZones with thresolds set.
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Thresholds"
ghenv.Component.NickName = 'setEPZoneThresholds'
ghenv.Component.Message = 'VER 0.0.59\nMAR_01_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_18_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid


def checkTheInputs():
    #If the user puts in only one value, apply that value to all of the zones.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    if len(daylightThreshold_) == 1: daylightThreshold = duplicateData(daylightThreshold_, len(_HBZones))
    else: daylightThreshold = daylightThreshold_
    
    if len(coolingSetback_) == 1: coolingSetback = duplicateData(coolingSetback_, len(_HBZones))
    else: coolingSetback = coolingSetback_

    if len(coolingSetPt_) == 1: coolingSetPt = duplicateData(coolingSetPt_, len(_HBZones))
    else: coolingSetPt = coolingSetPt_
    
    if len(heatingSetPt_) == 1: heatingSetPt = duplicateData(heatingSetPt_, len(_HBZones))
    else: heatingSetPt = heatingSetPt_
    
    if len(heatingSetback_) == 1: heatingSetback = duplicateData(heatingSetback_, len(_HBZones))
    else: heatingSetback = heatingSetback_
    
    if len(maxHumidity_) == 1: maxHumidity = duplicateData(maxHumidity_, len(_HBZones))
    else: maxHumidity = maxHumidity_
    
    if len(minHumidity_) == 1: minHumidity = duplicateData(minHumidity_, len(_HBZones))
    else: minHumidity = minHumidity_
    
    return daylightThreshold, coolingSetPt, coolingSetback, heatingSetPt, heatingSetback, maxHumidity, minHumidity

def updateSetPoints(schName, setPt, setBk):
    """
    This function takes a setpoint schedule and change setPts and setbacks
    and return the new yearly schedule.
    
    The function is written for OpenStudioTemplate schedule and only works
    for schedules which are structured similat to the template
    """
    
    hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
    hb_EPObjectsAUX = sc.sticky["honeybee_EPObjectsAUX"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    setPt = str(setPt)
    setBk = str(setBk)
    
    if setPt=="" and setBk=="":
        return schName
    
    if hb_EPObjectsAUX.isSchedule(schName):
        values, comments = hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
    else:
        return schName
    
    scheduleType = values[0].lower()
    if scheduleType != "schedule:year": return schName
    
    # find all weekly schedules
    numOfWeeklySchedules = int((len(values)-2)/5)

    yearlyIndexes = []
    yearlyValues = []
        
    for i in range(numOfWeeklySchedules):
        yearlyIndexCount = 5 * i + 2
        
        weekDayScheduleName = values[yearlyIndexCount]
        # find name of schedules for every day of the week
        dailyScheduleNames, comments = hb_EPScheduleAUX.getScheduleDataByName(weekDayScheduleName.upper(), ghenv.Component)
        weeklyIndexes = []
        weeklyValues = []
        
        for itemCount, dailySchedule in enumerate(dailyScheduleNames[1:]):
            newName = ""
            indexes = []
            inValues = []
            
            hourlyValues, comments = hb_EPScheduleAUX.getScheduleDataByName(dailySchedule.upper(), ghenv.Component)
            numberOfSetPts = int((len(hourlyValues) - 3) /2)
            
            # check if schedule has setback and give a warning if it doesn't
            if numberOfSetPts == 1 and setBk!="":
                warning = dailySchedule + " has no setback. Only setPt will be changed."
                print warning
                
            # change the values in the list
            if setBk!="" and numberOfSetPts == 3:
                indexes.extend([5, 9])
                inValues.extend([setBk, setBk])
                newName += "setBk " + str(setBk) + " "
                
            if setPt!="" and numberOfSetPts == 3:
                indexes.append(7)
                inValues.append(setPt)
                newName += "setPt " + str(setPt) + " "
                
            elif setPt!="" and numberOfSetPts == 1:
                indexes.append(5)
                inValues.append(setPt)
                newName += "setPt " + str(setPt) + " "
            
            # assign new name to be changed
            indexes.append(1)
            inValues.append(dailySchedule + newName)
            
            # create a new object
            original, updated = hb_EPObjectsAUX.customizeEPObject(dailySchedule.upper(), indexes, inValues)
            
            # add to library
            added, name = hb_EPObjectsAUX.addEPObjectToLib(updated, overwrite = True)
            
            # collect indexes and names to update the weekly schedule
            if added:
                weeklyIndexes.append(itemCount + 2)
                weeklyValues.append(name)
        
        # modify the name of schedule
        weeklyIndexes.append(1)
        weeklyValues.append(newName + " {" + str(uuid.uuid4())+ "}")
        
        # update weekly schedule based on new names
        # create a new object
        originalWeekly, updatedWeekly = hb_EPObjectsAUX.customizeEPObject(weekDayScheduleName.upper(), weeklyIndexes, weeklyValues)
        
        # add to library
        added, name = hb_EPObjectsAUX.addEPObjectToLib(updatedWeekly, overwrite = True)
        
        if added:
            # collect the changes for yearly schedule
            yearlyIndexes.append(yearlyIndexCount + 1)
            yearlyValues.append(name)
    
    # update name
    yearlyIndexes.append(1)
    yearlyValues.append(schName + " " + newName)
    
    # update yearly schedule
    originalYear, updatedYear = hb_EPObjectsAUX.customizeEPObject(schName.upper(), yearlyIndexes, yearlyValues)
    
    # add to library
    added, name = hb_EPObjectsAUX.addEPObjectToLib(updatedYear, overwrite = True)
    
    return name

def main(HBZones, daylightThreshold, coolingSetPt, heatingSetPt, coolingSetback, heatingSetback, maxHumidity, minHumidity):
    
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
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    # assign the values
    for zoneCount, zone in enumerate(HBZonesFromHive):
        try:
            zone.daylightThreshold = str(daylightThreshold[zoneCount])
            print "Daylight threshold for " + zone.name + " is set to: " + zone.daylightThreshold
            
        except: pass
        
        try:
            zone.coolingSetPt = str(coolingSetPt[zoneCount])
            # print "Cooling setpoint for " + zone.name + " is set to: " + zone.coolingSetPt
        except: pass
        try:
            zone.coolingSetback = str(coolingSetback[zoneCount])
            # print "Cooling setback for " + zone.name + " is set to: " + zone.coolingSetback
        except: pass
        
        # update zone schedule based on new values
        zone.coolingSetPtSchedule = updateSetPoints(zone.coolingSetPtSchedule, \
                                                    zone.coolingSetPt, zone.coolingSetback)
        
        try:
            zone.heatingSetPt = str(heatingSetPt[zoneCount])
            # print "Heating setpoint for " + zone.name + " is set to: " + zone.heatingSetPt
        except: pass
        
        try:
            zone.heatingSetback = str(heatingSetback[zoneCount])
            # print "Heating setback for " + zone.name + " is set to: " + zone.heatingSetback
        except: pass
        
        # update zone schedule based on new values
        zone.heatingSetPtSchedule = updateSetPoints(zone.heatingSetPtSchedule, \
                                                    zone.heatingSetPt, zone.heatingSetback)
        
        try:
            zone.humidityMax = str(maxHumidity[zoneCount])
            # print "Heating setpoint for " + zone.name + " is set to: " + zone.humidityMax
        except: pass
        
        try:
            zone.humidityMin = str(minHumidity[zoneCount])
            # print "Heating setpoint for " + zone.name + " is set to: " + zone.minHumidity
        except: pass
        
        
    # send the zones back to the hive
    HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    return HBZones


if _HBZones:
    
    daylightThreshold_ = []
    
    daylightThreshold, coolingSetPt, coolingSetback, heatingSetPt, \
    heatingSetback, maxHumidity, minHumidity = checkTheInputs()
    
    zones = main(_HBZones, daylightThreshold, coolingSetPt, heatingSetPt, \
                   coolingSetback, heatingSetback, maxHumidity, minHumidity)
    
    if zones!=-1:
        HBZones = zones




