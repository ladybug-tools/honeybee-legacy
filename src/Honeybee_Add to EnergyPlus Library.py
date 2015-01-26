# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add EnergyPlus Material, Construction or Schedule to Library

-
Provided by Honeybee 0.0.55
    
    Args:
        _EPObject: EnergyPlus material, construction or schedule definition
        _addToProjectLib: Set to True to add the material to HB library for this project
        overwrite_: Set to True if you want to overwrite the material with similar name
        addToHoneybeeLib: Set to True to Honeybee material libaray. Materials in addToHoneybeeLib library will be loaded anytime that you let the 'bee fly. You can add the materials manually to C:\ladybug\HoneybeeRadMaterials.mat
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_Add to EnergyPlus Library"
ghenv.Component.NickName = 'addToEPLibrary'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


def main(EPObject, addToProjectLib, overwrite):
    
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
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
    
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    added, name = hb_EPObjectsAux.addEPObjectToLib(EPObject, overwrite)
    
    if not added:
        msg = name + " is not added to the project library!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        print msg
    else:
        print name + " is added to this project library!"
        
if _EPObject and _addToProjectLib:
    main(_EPObject, _addToProjectLib, overwrite_)