# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add Radiance Materials to Library

-
Provided by Honeybee 0.0.50
    
    Args:
        RADMaterial: Radiance material definition
        addToProjectLib: Set to True to add the material to HB library for this project
        overwrite: Set to True if you want to overwrite the material with similar name
        addToHoneybeeLib: Set to True to Honeybee material libaray. Materials in addToHoneybeeLib library will be loaded anytime that you let the 'bee fly. You can add the materials manually to C:\ladybug\HoneybeeRadMaterials.mat
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_Add to Radiance Library"
ghenv.Component.NickName = 'addToLibrary'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
import Grasshopper.Kernel as gh


def updateRADMaterialList():
    # update the list of the materials in the call from library components
    for component in ghenv.Component.OnPingDocument().Objects:
        if  type(component)== type(ghenv.Component) and component.Name == "Honeybee_Call from Radiance Library":
            component.ExpireSolution(True)

if sc.sticky.has_key('honeybee_release'):
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if RADMaterial!=None:
        
        if addToHoneybeeLib:
            hb_RADMaterialAUX.addToGlobalLibrary(RADMaterial)
            updateRADMaterialList()

        if addToProjectLib:
            added, name = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True, overwrite)
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
