# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Create EP Plenum Zone
-
Provided by Honeybee 0.0.56

    Args:
        _HBZones:...
        
    Returns:
        HBZPlenumones:...
"""

ghenv.Component.Name = "Honeybee_Create EP Plenum"
ghenv.Component.NickName = 'createEPPlenum'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os


def main(HBZones):
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
    
    schedules = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        
        # add Plenum to name (maily for OpenStudio)
        # https://github.com/mostaphaRoudsari/Honeybee/issues/140#issuecomment-51018021
        
        if "plenum" not in HBZone.name.lower():
            HBZone.name = "Plenum " + HBZone.name 
        
        # change loads to 0
        if not HBZone.isLoadsAssigned:
            HBZone.assignLoadsBasedOnProgram(ghenv.Component)
        
        HBZone.equipmentLoadPerArea = 0
        HBZone.infiltrationRatePerArea = 0
        HBZone.lightingDensityPerArea = 0
        HBZone.numOfPeoplePerArea = 0
        HBZone.ventilationPerArea = 0
        HBZone.ventilationPerPerson = 0
        
        # This is for EP component to the area won't be included in the total area
        HBZone.isPlenum = True
        
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones)
    
    if results != -1: HBPlenumZones = results