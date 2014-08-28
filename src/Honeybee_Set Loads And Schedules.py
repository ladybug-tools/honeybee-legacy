# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set schedules and loads for zones based on program 
-
Provided by Honeybee 0.0.54

    Args:
        _HBZones:...
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        currentSchedules:...
        currentLoads:...
        HBZones:...
"""

ghenv.Component.Name = "Honeybee_Set Loads And Schedules"
ghenv.Component.NickName = 'SetLoadsAndSchedules'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

def main(HBZones, zonePrograms):
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
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    currentSchedules = []
    currentLoads = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        # zone programs
        try: bldgProgram, zoneProgram = zonePrograms[zoneCount].split("::")
        except: continue
        
        # make sure the combination is valid before changing it for the zone
        if bldgProgram!=None and bldgProgram not in bldgProgramDict.values():
            msg = "bldgProgram > [" + bldgProgram + "] is not a valid input.\n" + \
                  "Use ListSpacePrograms component to find the available programs."
            print msg
            if component != None:
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        if zoneProgram!=None:
            try:
                if zoneProgram not in zonesProgramDict[bldgProgram].values():
                    msg = "zoneProgram > [" + zoneProgram + "] is not a valid zone program for " + bldgProgram + ".\n" + \
                      "Use ListSpacePrograms component to find the available programs."
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
            except:
                msg = "Either your input for bldgProgram > [" + str(bldgProgram) + "] or " + \
                      "the input for zoneProgram > [" + str(zoneProgram) + "] is not valid.\n" + \
                      "Use ListSpacePrograms component to find the available programs."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
                
        HBZone.bldgProgram = bldgProgram
        HBZone.zoneProgram = zoneProgram
        HBZone.assignScheduleBasedOnProgram(ghenv.Component)
        HBZone.assignLoadsBasedOnProgram(ghenv.Component)
        if HBZone.isSchedulesAssigned:
            currentSchedules.append(HBZone.getCurrentSchedules())
        if HBZone.isLoadsAssigned:
            currentLoads.append(HBZone.getCurrentLoads())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return currentSchedules, currentLoads, HBZones


if _HBZones:
    results = main(_HBZones, zonePrograms_)
    
    if results != -1:
        currentSchedules, currentLoads, HBZones = results