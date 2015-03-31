# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to change the occupancy, lighting, equipment, etc. loads for a given Honeybee zone or list of Honeybee zones.
-
Provided by Honeybee 0.0.56

    Args:
        _HBZones: Honeybee zones for which you want to change the loads.
        equipmentLoadPerArea_: The desired equipment load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 2 W/m2 (for just a laptop or two in the zone) to 15 W/m2 for an office filled with computers and appliances.
        infiltrationRatePerArea_: The desired rate of outside air infiltration into the zone per square meter of floor.  Values here should be in m3/s-m2 (Cubic meters per second per square meter of floor).  Typical values tend to be around 0.0002 m3/s-m2 for tightly sealed buildings but you can make this much higher if you want to simulate a lot of air entering the zone for ventilation. 
        lightingDensityPerArea_: The desired lighting load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 3 W/m2 for efficeint LED bulbs to 15 W/m2 for incandescent heat lamps.
        numOfPeoplePerArea_: The desired number of per square meter of floor at peak occupancy.  Values here should be in ppl/m2 (People per square meter).  Typical values can range from 0.02 ppl/m2 for a lightly-occupied household to 0.5 ppl/m2 for a tightly packed auditorium.
        ventilationPerArea_: The desired minimum rate of ventilation through the mechanical system into the zone per square meter of floor.  Values here should be in m3/s-m2 (Cubic meters per second per square meter of floor).  Often, this total value over the zone should be much lower than the ventilation per person (below).  Typical values can range from 0.0002 m3/s-m2 for lightly-occupied houses to 0.0025 m3/s-m2 for spaces like laboratories and cleanrooms where dust contamination is a major concern.
        ventilationPerPerson_: The desired minimum rate of ventilation through the mechanical system into the zone per person in the zone.  Values here should be in m3/s-person (Liters per second per person in the zone). In effect, an input here will mimic demand controlled ventilation, where the ventilation through the mechanical system will change depending upon the occupancy. Most standards suggest that you should have at least 0.001 m3/s for each person in the zone but this may be increased sometimes to avoid odors or exposure to indoor pollutants.
    Returns:
        loads: The current loads of the HBZones.
        HBZones: Honeybee zones with modifided loads.
"""

ghenv.Component.Name = "Honeybee_Set EnergyPlus Zone Loads"
ghenv.Component.NickName = 'setEPZoneLoads'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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