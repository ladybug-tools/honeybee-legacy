# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Call Radiance Materials from Library

-
Provided by Honeybee 0.0.53
    
    Args:
        keywords_: List of keywords to filter the list of materials
        materialTypes_: Material types to be shown (e.g. plastic, glass, trans, metal, mirror)
            
    Returns:
        material: List of materials

"""

ghenv.Component.Name = "Honeybee_Call from Radiance Library"
ghenv.Component.NickName = 'callFromLibrary'
ghenv.Component.Message = 'VER 0.0.53\nJUL_20_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


if sc.sticky.has_key('honeybee_release'):
    
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if len(keywords_)!=0 and keywords_[0]!=None or materialTypes_!=None:
        materials = hb_RADMaterialAUX.searchRadMaterials(keywords_, materialTypes_)
        materials.sort()
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
