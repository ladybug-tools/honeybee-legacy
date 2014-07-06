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
    Returns:
        HBZones:...
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Thresholds"
ghenv.Component.NickName = 'setEPZoneThresholds'
ghenv.Component.Message = 'VER 0.0.53\nJUL_06_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid


def main(HBZones, daylightThreshold, coolingSetPt, heatingSetPt):
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
    
    # send the zones back to the hive
    HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    return HBZones

if _HBZones:
    HBZones = main(_HBZones, daylightThreshold_, coolingSetPt_, heatingSetPt_)




