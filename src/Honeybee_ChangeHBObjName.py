# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Change Honeybee Object Names

-
Provided by Honeybee 0.0.55

    Args:
        HBObjects: Any valid Honeybee object
        _names: List of new names for HBObjects
    Returns:
        readMe!: Information about the Honeybee object
"""
ghenv.Component.Name = "Honeybee_ChangeHBObjName"
ghenv.Component.NickName = 'changeHBObjName'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

def main(HBObjects, names):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBObjects)
    
    HBObjs = range(len(HBObjectsFromHive))
    
    for count, HBO in enumerate(HBObjectsFromHive):
        try:
            HBO.setName(names[count])
        except:
            pass
        
        HBObjs[count] = HBO
    
    return hb_hive.addToHoneybeeHive(HBObjs, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if _HBObjects and _names:
    HBObjects = main(_HBObjects, _names)