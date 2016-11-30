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
Use this component to change the occupancy, lighting, equipment, etc. loads for a given Honeybee zone or list of Honeybee zones.
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: Honeybee zones for which you want to change the loads.
        equipmentLoadPerArea_: The desired equipment load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 2 W/m2 (for just a laptop or two in the zone) to 15 W/m2 for an office filled with computers and appliances.
        infiltrationRatePerArea_: The desired rate of outside air infiltration into the zone per square meter of floor.  Values here should be in m3/s-m2 (Cubic meters per second per square meter of floor).  ASHRAE recommends the following general infiltration rates based on the area of the facade exposed to the outdoors (note that you have to use the "Honeybee_infOrVentPerArea" to convert):
            0.0001 (m3/s per m2 facade) - Tight building
            0.0003 (m3/s per m2 facade) - Average building
            0.0006 (m3/s per m2 facade) - Leaky building
        lightingDensityPerArea_: The desired lighting load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 3 W/m2 for efficeint LED bulbs to 15 W/m2 for incandescent heat lamps.
        numOfPeoplePerArea_: The desired number of per square meter of floor at peak occupancy.  Values here should be in ppl/m2 (People per square meter).  Typical values can range from 0.02 ppl/m2 for a lightly-occupied household to 0.5 ppl/m2 for a tightly packed auditorium.
        ventilationPerArea_: The desired minimum rate of outdoor air ventilation through the mechanical system into the zone in m3/s per m2 of floor.  Values here should be in m3/s-m2 (Cubic meters per second per square meter of floor).  Often, this total value over the zone should be much lower than the ventilation per person (below).  Typical values can range from 0.0002 m3/s-m2 for lightly-occupied houses to 0.0025 m3/s-m2 for spaces like laboratories and cleanrooms where dust contamination is a major concern.
        ventilationPerPerson_: The desired minimum rate of outdoor air ventilation through the mechanical system into the zone per person in the zone.  Values here should be in m3/s-person (Liters per second per person in the zone). In effect, an input here will mimic demand controlled ventilation, where the ventilation through the mechanical system will change depending upon the occupancy. Most standards suggest that you should have at least 0.001 m3/s for each person in the zone but this may be increased sometimes to avoid odors or exposure to indoor pollutants.
        recirculatedAirPerArea_: The desired minimum rate of recirculated air flow through the HVAC system in m3/s per m2 of floor.  Note that this input does not affect any models run with ideal air systems and only has an effect on OpenStudio models where recirculated air is required in addtion to outdoor ventilation (such as hostpital patient rooms that require additional ventilation to limit the spread of diseases).  The defult is always set to zero as most spaces do not require recirculated air.
    Returns:
        loads: The current loads of the HBZones.
        HBZones: Honeybee zones with modifided loads.
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Loads"
ghenv.Component.NickName = 'setEPZoneLoads'
ghenv.Component.Message = 'VER 0.0.60\nNOV_09_2016'
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

def duplicateData(input, length):
    il = len(input)
    if il == 0:
        return tuple(None for i in range(length))
    else:
        return tuple(input[i] if i < il else input[-1] for i in range(length))

def main(HBZones, equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea,
         numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson, recirculatedAirPerArea):
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
        return -1
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    length = len(HBObjectsFromHive)
    equipmentLoadPerArea = duplicateData(equipmentLoadPerArea, length)
    infiltrationRatePerArea = duplicateData(infiltrationRatePerArea, length) 
    lightingDensityPerArea = duplicateData(lightingDensityPerArea, length) 
    numOfPeoplePerArea = duplicateData(numOfPeoplePerArea, length) 
    ventilationPerArea = duplicateData(ventilationPerArea, length) 
    ventilationPerPerson = duplicateData(ventilationPerPerson, length) 
    recirculatedAirPerArea = duplicateData(recirculatedAirPerArea, length) 
    
    loads = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        
        # assign the default is there is no load assigned yet
        if not HBZone.isLoadsAssigned:
            HBZone.assignLoadsBasedOnProgram(ghenv.Component)
        
        if equipmentLoadPerArea[zoneCount] != None:
            HBZone.equipmentLoadPerArea = equipmentLoadPerArea[zoneCount]
        if infiltrationRatePerArea[zoneCount] != None:
            HBZone.infiltrationRatePerArea = infiltrationRatePerArea[zoneCount]
        if lightingDensityPerArea[zoneCount] != None:
            HBZone.lightingDensityPerArea = lightingDensityPerArea[zoneCount]
        if numOfPeoplePerArea[zoneCount] != None:
            HBZone.numOfPeoplePerArea = numOfPeoplePerArea[zoneCount]
        if ventilationPerArea[zoneCount] != None:
            HBZone.ventilationPerArea = ventilationPerArea[zoneCount]
        if ventilationPerPerson[zoneCount] != None:
            HBZone.ventilationPerPerson = ventilationPerPerson[zoneCount]
        if recirculatedAirPerArea[zoneCount] != None:
            HBZone.recirculatedAirPerArea = recirculatedAirPerArea[zoneCount]
        
        loads.append(HBZone.getCurrentLoads())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)

    return HBZones, loads
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones, equipmentLoadPerArea_, infiltrationRatePerArea_, lightingDensityPerArea_, numOfPeoplePerArea_, ventilationPerArea_, ventilationPerPerson_, recirculatedAirPerArea_)
    
    if results != -1: HBZones, loads = results