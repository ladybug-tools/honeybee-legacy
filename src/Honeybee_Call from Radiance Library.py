"""
Call Radiance Materials from Library

-
Provided by Honybee 0.0.36
    
    Args:
        keywords: List of keywords to filter the list of materials
        materialTypes: Material types to be shown (e.g. plastic, glass, trans, metal, mirror)
            
    Returns:
        material: List of materials

"""

ghenv.Component.Name = "Honeybee_Call from Radiance Library"
ghenv.Component.NickName = 'callFromLibrary'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
import Grasshopper.Kernel as gh


if sc.sticky.has_key('honeybee_release'):
    
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if len(keywords)!=0 and keywords[0]!=None or materialTypes!=None:
        materials = hb_RADMaterialAUX.searchRadMaterials(keywords, materialTypes)
        materials.sort()
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")