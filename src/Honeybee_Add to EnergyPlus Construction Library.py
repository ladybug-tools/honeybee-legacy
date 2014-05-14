# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add EnergyPlus Material and construction to Library

-
Provided by Honeybee 0.0.53
    
    Args:
        _EPMatOrConstr: EnergyPlus material or construction definition
        _addToProjectLib: Set to True to add the material to HB library for this project
        overwrite_: Set to True if you want to overwrite the material with similar name
        addToHoneybeeLib: Set to True to Honeybee material libaray. Materials in addToHoneybeeLib library will be loaded anytime that you let the 'bee fly. You can add the materials manually to C:\ladybug\HoneybeeRadMaterials.mat
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_Add to EnergyPlus Construction Library"
ghenv.Component.NickName = 'addToEPConstrLibrary'
ghenv.Component.Message = 'VER 0.0.53\nMAY_13_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


def main(EPMatOrConstr, addToProjectLib, overwrite):
    
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    added, name = hb_EPMaterialAUX.addEPConstructionToLib(EPMatOrConstr, overwrite)
    
    if not added:
        msg = name + " is not added to the project library!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        print msg
    else:
        print name + " is added to this project library!"
        
if _EPMatOrConstr and _addToProjectLib:
    main(_EPMatOrConstr, _addToProjectLib, overwrite_)