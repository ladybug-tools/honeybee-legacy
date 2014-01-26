"""
Add Radiance Materials to Library

-
Provided by Honybee 0.0.36
    
    Args:
        RADMaterial: Radiance material definition
        addToProjectLib: Set to True to add the material to HB library for this project
        overwrite: Set to True if you want to overwrite the material with similar name
        addToGlonalLib: Set to True to Honeybee material libaray. Materials in global library will be loaded anytime that you let the 'bee fly.
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_Add to Radiance Library"
ghenv.Component.NickName = 'addToLibrary'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
import Grasshopper.Kernel as gh


if sc.sticky.has_key('honeybee_release'):
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if RADMaterial!=None:
        
        if addToGlobalLib:
            hb_RADMaterialAUX.addToGlobalLibrary(RADMaterial)
        
        if addToProjectLib:
            added, name = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True, overwrite)
            if not added:
                msg = name + " is not added to the library!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                print msg
            else:
                print name + " is added to this project library!"
        
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")