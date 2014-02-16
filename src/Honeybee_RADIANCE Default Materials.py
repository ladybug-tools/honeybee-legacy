
"""
Radiance Default Materials

-
Provided by Honybee 0.0.50
    
    Args:
        _newWallMaterial_: Optional wall material to overwrite the default wall material
        _newGlassMaterial_: Optional glass material to overwrite the default glass material
        _newCeilingMaterial_: Optional ceiling material to overwrite the default ceiling material
        _newRoofMaterial_: Optional roof material to overwrite the default roof material
        _newFloorMaterial_: Optional wall floor to overwrite the default floor material
        _resetToHBDefaults: Set to True to reset to default materials
    Returns:
        currentWallMaterial: Current wall material definition
        currentGlassMaterial: Current glass material definition
        currentCeilingMaterial: Current ceiling material definition
        currentRoofMaterial: Current roof material definition
        currentFloorMaterial: Current floor material definition

"""

ghenv.Component.Name = "Honeybee_RADIANCE Default Materials"
ghenv.Component.NickName = 'RADDefaultMaterials'
ghenv.Component.Message = 'VER 0.0.50\nFEB_15_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
import Grasshopper.Kernel as gh


def setToDefault(hb_RADMaterialAUX):
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', '000_Context_Material', .35, .35, .35, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', '000_Interior_Ceiling', .80, .80, .80, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', '000_Interior_Floor', .2, .2, .2, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('glass', '000_Exterior_Window', .60, .60, .60), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', '000_Exterior_Roof', .35, .35, .35, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', '000_Exterior_Wall', .50, .50, .50, 0, 0.1), True, True)
    

def main():
    
    if sc.sticky.has_key('honeybee_release'):
        
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        
        # reset to defaults
        if _resetToHBDefaults:
            setToDefault(hb_RADMaterialAUX)
            return
        
        RADMaterials = [_newWallMaterial_, _newGlassMaterial_, _newCeilingMaterial_, _newRoofMaterial_, _newFloorMaterial_]
        defaultMaterial = ['000_Exterior_Wall', '000_Exterior_Window', '000_Interior_Ceiling', '000_Exterior_Roof', '000_Interior_Floor']
        
        for materialCount, RADMaterial in enumerate(RADMaterials):
            if RADMaterial!=None:
                # if the material is not in the library add it to the library
                if RADMaterial not in sc.sticky ["honeybee_RADMaterialLib"].keys():
                    # if it is just the name of the material give a warning
                    if len(RADMaterial.split(" ")) == 1:
                        warningMsg = "Can't find " + RADMaterial + " in RAD Material Library.\n" + \
                                    "Add the material to the library and try again."
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                        return
                    else:
                        # try to add the material to the library
                        addedToLib, materialName = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
                
                # overwrite the default
                sc.sticky ["honeybee_RADMaterialLib"][defaultMaterial[materialCount]] = sc.sticky ["honeybee_RADMaterialLib"][materialName]
            
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
    
main()

currentWallMaterial = hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Wall')
currentGlassMaterial = hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Window')
currentCeilingMaterial = hb_RADMaterialAUX.getRADMaterialString('000_Interior_Ceiling')
currentRoofMaterial = hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Roof')
currentFloorMaterial = hb_RADMaterialAUX.getRADMaterialString('000_Interior_Floor')