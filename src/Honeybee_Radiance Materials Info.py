# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Materials Info
-
Provided by Honeybee 0.0.55

    Args:
        _RADMaterial: Radiance material name
    Returns:
        RADMaterialStr: Radiance material definition

"""

ghenv.Component.Name = "Honeybee_Radiance Materials Info"
ghenv.Component.NickName = 'RADMaterialsInfo'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main():
    
    if sc.sticky.has_key('honeybee_release'):
    
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        
        if _RADMaterial!= None:
            # check if the name is in the library
            addedToLib, materialName = hb_RADMaterialAUX.analyseRadMaterials(_RADMaterial, False)
            
            if materialName in sc.sticky["honeybee_RADMaterialLib"].keys():
                RADMaterialStr = hb_RADMaterialAUX.getRADMaterialString(materialName)
                
                return RADMaterialStr
            
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

RADMaterialStr = main()