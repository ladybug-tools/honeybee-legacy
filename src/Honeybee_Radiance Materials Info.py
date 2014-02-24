# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Materials Info
-
Provided by Honeybee 0.0.51

    Args:
        RADMaterial: Radiance material name
    Returns:
        RADMaterialStr: Radiance material definition

"""

ghenv.Component.Name = "Honeybee_Radiance Materials Info"
ghenv.Component.NickName = 'RADMaterialsInfo'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


if sc.sticky.has_key('honeybee_release'):
    
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if RADMaterial!= None:
        # check if the name is in the library
        addedToLib, materialName = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, False)
        
        if materialName in sc.sticky["honeybee_RADMaterialLib"].keys():
            RADMaterialStr = hb_RADMaterialAUX.getRADMaterialString(materialName)
        
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

