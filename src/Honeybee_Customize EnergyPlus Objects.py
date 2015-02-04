# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Customize EnergyPlus Objects [NOT READY YET!]

-
Provided by Honeybee 0.0.56
    
    Args:
        schName_: Schedule name
            
    Returns:
        name:
        schedule:
        comments:
"""

ghenv.Component.Name = "Honeybee_Customize EnergyPlus Objects"
ghenv.Component.NickName = 'customizeEPObjs'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(EPObjectName, indexes, inValues):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
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

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    HBEPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    objects = HBEPObjectsAux.customizeEPObject(EPObjectName, indexes, inValues)
    
    if objects:
        return objects
    else:
        return None, None


if _EPObjectName:
    results = main(_EPObjectName, indexes_, values_)
    if results!=-1:
        originalObj, modifiedObj = results