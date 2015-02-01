# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Decompose Honeybee Zone

-
Provided by Honeybee 0.0.56

    Args:
        _HBZone: Honeybee Zone
    Returns:
        HBSurfaces: Honeybee Surfaces
"""
ghenv.Component.Name = "Honeybee_DecomposeHBZone"
ghenv.Component.NickName = 'Decompose Honeybee Zone'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import uuid

def main(HBZone):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first Honeybee to fly...")
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
    
    HBO = hb_hive.callFromHoneybeeHive([HBZone])[0]
    
    HBSurfaces  = hb_hive.addToHoneybeeHive(HBO.surfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBSurfaces

if _HBZone:
    HBSurfaces = main(_HBZone)
