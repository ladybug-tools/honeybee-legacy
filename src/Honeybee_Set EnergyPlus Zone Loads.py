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

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Loads"
ghenv.Component.NickName = 'setEPZoneLoads'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass
import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh


def main(HBZones, equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    loads = []
    for HBZone in HBObjectsFromHive:
        if equipmentLoadPerArea != None: HBZone.equipmentLoadPerArea = equipmentLoadPerArea
        if infiltrationRatePerArea != None: HBZone.infiltrationRatePerArea = infiltrationRatePerArea
        if lightingDensityPerArea != None: HBZone.lightingDensityPerArea = lightingDensityPerArea
        if numOfPeoplePerArea != None: HBZone.numOfPeoplePerArea = numOfPeoplePerArea
        if ventilationPerArea != None: HBZone.ventilationPerArea = ventilationPerArea
        if ventilationPerPerson != None: HBZone.ventilationPerPerson = ventilationPerPerson
        loads.append(HBZone.getCurrentLoads())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

    return HBZones, loads
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones, equipmentLoadPerArea_, infiltrationRatePerArea_, lightingDensityPerArea_, numOfPeoplePerArea_, ventilationPerArea_, ventilationPerPerson_)
    
    if results != -1: HBZones, loads = results