# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Customize EnergyPlus Objects [NOT READY YET!]

-
Provided by Honeybee 0.0.54
    
    Args:
        schName_: Schedule name
            
    Returns:
        name:
        schedule:
        comments:
"""

ghenv.Component.Name = "Honeybee_Customize EnergyPlus Objects"
ghenv.Component.NickName = 'customizeEPObjs'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
    
    HBEPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    objects = HBEPObjectsAux.customizeEPObject(EPObjectName, indexes, inValues)
    
    if objects:
        return objects
    else:
        return None, None


if _EPObjectName:
    originalObj, modifiedObj = main(_EPObjectName, indexes_, values_)
