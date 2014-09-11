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

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Loads"
ghenv.Component.NickName = 'setEPZoneLoads'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
        return -1
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    loads = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        
        # assign the default is there is no load assigned yet
        if not HBZone.isLoadsAssigned:
            HBZone.assignLoadsBasedOnProgram(ghenv.Component)
            
        if equipmentLoadPerArea!=[]:
            try:
                if equipmentLoadPerArea[zoneCount]!= None:
                    HBZone.equipmentLoadPerArea = equipmentLoadPerArea[zoneCount]
            except:
                if equipmentLoadPerArea[0]!= None:
                    HBZone.equipmentLoadPerArea = equipmentLoadPerArea[0]
        if infiltrationRatePerArea != []:
            try:
                if infiltrationRatePerArea[zoneCount]!= None:
                    HBZone.infiltrationRatePerArea = infiltrationRatePerArea[zoneCount]
            except:
                if infiltrationRatePerArea[0]!= None:
                    HBZone.infiltrationRatePerArea = infiltrationRatePerArea[0]
        if lightingDensityPerArea != []:
            try:
                if lightingDensityPerArea[zoneCount]!=None:
                    HBZone.lightingDensityPerArea = lightingDensityPerArea[zoneCount]
            except:
                if lightingDensityPerArea[0]!=None:
                    HBZone.lightingDensityPerArea = lightingDensityPerArea[0]
        if numOfPeoplePerArea != []:
            try:
                if numOfPeoplePerArea[zoneCount]!=None:
                    HBZone.numOfPeoplePerArea = numOfPeoplePerArea[zoneCount]
            except:
                if numOfPeoplePerArea[0]!=None:
                    HBZone.numOfPeoplePerArea = numOfPeoplePerArea[0]
        if ventilationPerArea != []:
            try:
                if ventilationPerArea[zoneCount] != None:
                    HBZone.ventilationPerArea = ventilationPerArea[zoneCount]
            except:
                if ventilationPerArea[0] != None:
                    HBZone.ventilationPerArea = ventilationPerArea[0]        
        if ventilationPerPerson != []:
            try:
                if ventilationPerPerson[zoneCount] != None:
                    HBZone.ventilationPerPerson = ventilationPerPerson[zoneCount]
            except:
                if ventilationPerPerson[0] != None:
                    HBZone.ventilationPerPerson = ventilationPerPerson[0]

        loads.append(HBZone.getCurrentLoads())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

    return HBZones, loads
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones, equipmentLoadPerArea_, infiltrationRatePerArea_, lightingDensityPerArea_, numOfPeoplePerArea_, ventilationPerArea_, ventilationPerPerson_)
    
    if results != -1: HBZones, loads = results