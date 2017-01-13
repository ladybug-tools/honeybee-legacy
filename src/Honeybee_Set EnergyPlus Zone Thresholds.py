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
Provided by Honeybee 0.0.60

    Args:
        _HBZones: HBZones for which zone thresholds will be set.
        daylightThreshold_: A number or list of numbers that represent the minimum lux to be achieved in the zone.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        coolingSetPt_: A number or list of numbers that represent the thermostat cooling setpoint in degrees Celcius.  The cooling setpoint is effectively the indoor temperature above which the cooling system is turned on.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        coolingSetback_: A number or list of numbers that represent the thermostat cooling setback in degrees Celcius.  The cooling setback is the indoor temperature that the space will be kept at when it is unoccipied.  Note that not all building types have a setback.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        heatingSetPt_: A number or list of numbers that represent the thermostat heating setpoint in degrees Celcius.  The heating setpoint is effectively the indoor temperature below which the heating system is turned on.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        heatingSetback_: A number or list of numbers that represent the thermostat heating setback in degrees Celcius.  The heating setback is the indoor temperature that the space will be kept at when it is unoccipied.  Note that not all building types have a setback.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxHumidity_: A number or list of numbers that represent the maximum relative humidity allowed by a humidistat in %.  The HVAC will dehumidify the zone air  if the relative humidity goes above this threshold.  The default is set to 'no limit' or no humidistat. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        minHumidity_ : A number or list of numbers that represent the minimum relative humidity allowed by a humidistat in %.  The HVAC will humidify the zone air if the relative humidity goes below this threshold.  The default is set to 'no limit' or no humidistat. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        outdoorAirReq_: An integer or text string value that changes the outdoor air requirement of the zone (the default is set to "0 - Sum").  Choose from the following options:
            0 - Sum - The outdoor air coming through the mechnical system will be the sum of the specified flow/m2 of zone floor area and the flow/person.  This is the default and is the usual recommendation of ASHRAE.
            1 - Maximum - The outdoor air coming through the mechnical system will be either the specified flow/m2 of zone floor area or the flow/person (depending on which is larger at a given hour).   Choosing this option effectively implies that there is a demand-controlled ventilation system set up in the zone.
            2 - None - No outdoor air will come through the mechanical system and the heating/cooling will be applied only through re-circulation of indoor air.  Be careful as this option might not bring enough fresh air to occupants if the zone's infiltration is very low.
        daylightIllumSetPt_: A number of list of numbers that represent the illuminance threshold in lux beyond which electric lights will be dimmed if there is sufficent daylight.  The default has no dimming for daylight, meaning that lights will be on whenever the schedule states that they are on (regardless of daylight).  If you specify a daylightCntrlFract_ below, this component will automatically assume a setpoint of 300 lux.  Some other common setpoints are:
            50 lux - Corridors and hallways
            150 lux - Spaces where people are working on computer screens, which already provide their own light.
            300 lux - Spaces where people are reading and writing on paper, such as residences and offices.
            500 lux - Commerical or retail spaces where perception of particular objects is important.
            1000 lux - Reserved only for spaces where lighting is critical for human safety like workshops with power tools or operating rooms in hospitals.
        daylightCntrlPt_: A point that represents the location of a daylight senor within the zone.  If an illumance setpoint is specified above, the default is set to place the sensor in the center of the zone at 0.8 meters above the ground.
        daylightCntrlFract_: A number between 0 and 1 that represents the fraction of the zone lights that will be dimmed when the illimance at the daylightCntrlPt_ is at the specified daylightIllumSetPt_.  The default is set to 1 when there is an illuminace threshold to dim all of the lights of the zone.  If you have a deep zone, you probably want to decrease this number so that you don't dim the lights in the back of the space to be too dark.
    Returns:
        HBZones: HBZones with thresolds set.
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Thresholds"
ghenv.Component.NickName = 'setEPZoneThresholds'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid


def checkTheInputs():
    #If the user puts in only one value, apply that value to all of the zones.
    def duplicateData(input, length):
        il = len(input)
        if il == 0:
            return tuple(None for i in range(length))
        else:
            return tuple(input[i] if i < il else input[-1] for i in range(length))
    
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
    
    if len(outdoorAirReq_) == 1: outdoorAirReq = duplicateData(outdoorAirReq_, len(_HBZones))
    else: outdoorAirReq = outdoorAirReq_
    
    if len(daylightIllumSetPt_) == 1: daylightIllumSetPt = duplicateData(daylightIllumSetPt_, len(_HBZones))
    else: daylightIllumSetPt = daylightIllumSetPt_
    
    if len(daylightCntrlPt_) == 1: daylightCntrlPt = duplicateData(daylightCntrlPt_, len(_HBZones))
    else: daylightCntrlPt = daylightCntrlPt_
    
    if len(daylightCntrlFract_) == 1: daylightCntrlFract = duplicateData(daylightCntrlFract_, len(_HBZones))
    else: daylightCntrlFract = daylightCntrlFract_
    
    outdoorAirReqFinal = []
    checkData = True
    for outAirReq in outdoorAirReq:
        if outAirReq == "0" or outAirReq == "1" or outAirReq == "2" or outAirReq.upper() == "NONE" or outAirReq.upper() == "MAXIMUM" or outAirReq == "SUM":
            if outAirReq == "0": outdoorAirReqFinal.append("Sum")
            elif outAirReq == "1": outdoorAirReqFinal.append("Maximum")
            elif outAirReq == "2": outdoorAirReqFinal.append("None")
            else: outdoorAirReqFinal.append(outAirReq)
        else:
            checkData = False
            msg = "Invalid outdoorAirReq_ input."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    outdoorAirReq = outdoorAirReqFinal
    
    return coolingSetPt, coolingSetback, heatingSetPt, heatingSetback, maxHumidity, minHumidity, outdoorAirReq, daylightIllumSetPt, daylightCntrlPt, daylightCntrlFract

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

def main(HBZones, coolingSetPt, heatingSetPt, coolingSetback, heatingSetback, maxHumidity, minHumidity, outdoorAirReq, daylightIllumSetPt, daylightCntrlPt, daylightCntrlFract):
    
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
        except: pass
        
        try:
            zone.humidityMin = str(minHumidity[zoneCount])
        except: pass
        
        try:
            zone.outdoorAirReq = outdoorAirReq[zoneCount]
        except: pass
        
        try:
            zone.illumCntrlSensorPt = daylightCntrlPt[zoneCount]
        except: pass
        
        if daylightIllumSetPt != [] and daylightCntrlFract == []:
            zone.daylightCntrlFract = 1
            zone.illumSetPt = daylightIllumSetPt[zoneCount]
        elif daylightIllumSetPt == [] and daylightCntrlFract != []:
            zone.daylightCntrlFract = daylightCntrlFract[zoneCount]
            zone.illumSetPt = 300
        elif daylightIllumSetPt != [] and daylightCntrlFract != []:
            zone.daylightCntrlFract = daylightCntrlFract[zoneCount]
            zone.illumSetPt = daylightIllumSetPt[zoneCount]
        
    # send the zones back to the hive
    HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component)
        
    return HBZones


if _HBZones and _HBZones[0] != None:
    coolingSetPt, coolingSetback, heatingSetPt, \
    heatingSetback, maxHumidity, minHumidity, outdoorAirReq, \
    daylightIllumSetPt, daylightCntrlPt, daylightCntrlFract = checkTheInputs()
    
    zones = main(_HBZones, coolingSetPt, heatingSetPt, \
                   coolingSetback, heatingSetback, maxHumidity, minHumidity, outdoorAirReq, \
                   daylightIllumSetPt, daylightCntrlPt, daylightCntrlFract)
    
    if zones!=-1:
        HBZones = zones




