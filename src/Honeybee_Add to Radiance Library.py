# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add Radiance Materials to Library

-
Provided by Honeybee 0.0.56
    
    Args:
        _RADMaterial: Radiance material definition
        _addToProjectLib: Set to True to add the material to HB library for this project
        overwrite_: Set to True if you want to overwrite the material with similar name
        addToHoneybeeLib_: Set to True to Honeybee material libaray. Materials in addToHoneybeeLib library will be loaded anytime that you let the 'bee fly. You can add the materials manually to C:\ladybug\HoneybeeRadMaterials.mat
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_Add to Radiance Library"
ghenv.Component.NickName = 'addToLibrary'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


def updateRADMaterialList():
    # update the list of the materials in the call from library components
    for component in ghenv.Component.OnPingDocument().Objects:
        if  type(component)== type(ghenv.Component) and component.Name == "Honeybee_Call from Radiance Library":
            component.ExpireSolution(True)

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
        
        if _RADMaterial!=None:
            
            if addToHoneybeeLib_:
                hb_RADMaterialAUX.addToGlobalLibrary(_RADMaterial)
                updateRADMaterialList()
    
            if _addToProjectLib:
                added, name = hb_RADMaterialAUX.analyseRadMaterials(_RADMaterial, True, overwrite_)
                if not added:
                    msg = name + " is not added to the project library!"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                else:
                    print name + " is added to this project library!"
                    updateRADMaterialList()
            
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

main()