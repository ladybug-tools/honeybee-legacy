# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set Zone Thresholds
-
Provided by Honeybee 0.0.53

    Args:
        _HBZones:...
        daylightThreshold_: ...
        coolingSetPt_: ...
        heatingSetPt_: ...
        coolSuplyAirTemp_: ...
        heatSupplyAirTemp_: ...
    Returns:
        HBZones:...
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Thresholds"
ghenv.Component.NickName = 'setEPZoneThresholds'
ghenv.Component.Message = 'VER 0.0.53\nJUL_20_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
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
    
    if len(coolingSetPt_) == 1: coolingSetPt = duplicateData(coolingSetPt_, len(_HBZones))
    else: coolingSetPt = coolingSetPt_
    
    if len(heatingSetPt_) == 1: heatingSetPt = duplicateData(heatingSetPt_, len(_HBZones))
    else: heatingSetPt = heatingSetPt_
    
    if len(coolSupplyAirTemp_) == 1: coolSupplyAirTemp = duplicateData(coolSupplyAirTemp_, len(_HBZones))
    else: coolSupplyAirTemp = coolSupplyAirTemp_
    
    if len(heatSupplyAirTemp_) == 1: heatSupplyAirTemp = duplicateData(heatSupplyAirTemp_, len(_HBZones))
    else: heatSupplyAirTemp = heatSupplyAirTemp_
    
    
    return daylightThreshold, coolingSetPt, heatingSetPt, coolSupplyAirTemp, heatSupplyAirTemp


def main(HBZones, daylightThreshold, coolingSetPt, heatingSetPt, coolSupplyAirTemp, heatSupplyAirTemp):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
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
            print "Cooling setpoint for " + zone.name + " is set to: " + zone.coolingSetPt
        except: pass
        
        try:
            zone.heatingSetPt = str(heatingSetPt[zoneCount])
            print "Heating setpoint for " + zone.name + " is set to: " + zone.heatingSetPt
        except: pass
        
        try:
            zone.coolSupplyAirTemp = str(coolSupplyAirTemp[zoneCount])
            print "Cooling supply air temperture for " + zone.name + " is set to: " + zone.coolSupplyAirTemp
        except: pass
        
        try:
            zone.heatSupplyAirTemp = str(heatSupplyAirTemp[zoneCount])
            print "Heating supply air temperture for " + zone.name + " is set to: " + zone.heatSupplyAirTemp
        except: pass
    
    # send the zones back to the hive
    HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    return HBZones

if _HBZones:
    daylightThreshold, coolingSetPt, heatingSetPt, coolSupplyAirTemp, heatSupplyAirTemp = checkTheInputs()
    HBZones = main(_HBZones, daylightThreshold, coolingSetPt, heatingSetPt, coolSupplyAirTemp, heatSupplyAirTemp)




