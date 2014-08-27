# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Radiance Default Materials
-
Provided by Honeybee 0.0.54

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
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh


def setToDefault(hb_RADMaterialAUX):
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', 'Context_Material', .35, .35, .35, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', 'Interior_Ceiling', .80, .80, .80, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', 'Interior_Floor', .2, .2, .2, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('glass', 'Exterior_Window', .60, .60, .60), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', 'Exterior_Roof', .35, .35, .35, 0, 0.1), True, True)
    hb_RADMaterialAUX.analyseRadMaterials(hb_RADMaterialAUX.createRadMaterialFromParameters('plastic', 'Exterior_Wall', .50, .50, .50, 0, 0.1), True, True)
    

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
        
        # reset to defaults
        if _resetToHBDefaults:
            setToDefault(hb_RADMaterialAUX)
            return
        
        RADMaterials = [_newWallMaterial_, _newGlassMaterial_, _newCeilingMaterial_, _newRoofMaterial_, _newFloorMaterial_]
        defaultMaterial = ['Exterior_Wall', 'Exterior_Window', 'Interior_Ceiling', 'Exterior_Roof', 'Interior_Floor']
        
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
        return -1
    
success = main()

if success!= -1:
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    currentWallMaterial = hb_RADMaterialAUX.getRADMaterialString('Exterior_Wall')
    currentGlassMaterial = hb_RADMaterialAUX.getRADMaterialString('Exterior_Window')
    currentCeilingMaterial = hb_RADMaterialAUX.getRADMaterialString('Interior_Ceiling')
    currentRoofMaterial = hb_RADMaterialAUX.getRADMaterialString('Exterior_Roof')
    currentFloorMaterial = hb_RADMaterialAUX.getRADMaterialString('Interior_Floor')

