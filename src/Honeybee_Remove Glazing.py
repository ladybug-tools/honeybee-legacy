# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Remove Glazing

-
Provided by Honeybee 0.0.55

    Args:
        _HBZones: List of Honeybee Zones
        srfIndex_: Index of the surface to removeglazing
        pattern_: Pattern to remove glazings
    Returns:
        readMe!: Information about the Honeybee object
"""
ghenv.Component.Name = "Honeybee_Remove Glazing"
ghenv.Component.NickName = 'remGlz'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

def main(HBObjects, srfIndex, pattern):
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
        if HBO.objectType == "HBZone":
            for srfCount, surface in enumerate(HBO.surfaces):
                if srfCount in srfIndex and surface.hasChild:
                    #remove the glzing
                    surface.removeAllChildSrfs()
                elif pattern[srfCount] == True and surface.hasChild:
                    print srfCount
                    #remove the glzing
                    surface.removeAllChildSrfs()
                    
        HBObjs[count] = HBO
    
    return hb_hive.addToHoneybeeHive(HBObjs, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if (_HBZones and srfIndex_!=[]) or (_HBZones and pattern_!=[]):
    HBZones = main(_HBZones, srfIndex_, pattern_)
