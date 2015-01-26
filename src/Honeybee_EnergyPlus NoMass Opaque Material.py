# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create a custom opaque material that has no mass, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
It is important to note that this component creates a material with no mass and, because of this, the accuracy of the component is not as great as a material that has mass.  However, this component is very useful if you only have an R-value for a material (or a construction) and you know that the mass is relatively small.
_
If you want to create a material that accounts for mass, you should use the "Honeybee_EnergyPlus Window Material" component.

-
Provided by Honeybee 0.0.55
    
    Args:
        _name: A text name for your NoMass Opaque Material.
        _roughness_: A text value that indicated the roughness of your material.  This can be either "VeryRough", "Rough", "MediumRough", "MediumSmooth", "Smooth", and "VerySmooth".  The default is set to "Rough".
        _R-Value: A number representing the R-Value of the material in m2-K/W.
        _thermAbsp_: An number between 0 and 1 that represents the thermal abstorptance of the material.  The default is set to 0.9, which is common for most non-metallic materials.
        _solAbsp_: An number between 0 and 1 that represents the abstorptance of solar radiation by the material.  The default is set to 0.7, which is common for most non-metallic materials.
        _visAbsp_: An number between 0 and 1 that represents the abstorptance of visible light by the material.  The default is set to 0.7, which is common for most non-metallic materials.
    Returns:
        EPMaterial: A no-mass opaque material that can be plugged into the "Honeybee_EnergyPlus Construction" component.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus NoMass Opaque Material"
ghenv.Component.NickName = 'EPNoMassMat'
ghenv.Component.Message = 'VER 0.0.55\nOCT_24_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def checkInputs():
    #Check to be sure that SHGC and VT are between 0 and 1.
    checkData = True
    
    def checkBtwZeroAndOne(variable, default, variableName):
        if variable == None: newVariable = default
        else:
            if variable <= 1 and variable >= 0: newVariable = variable
            else:
                newVariable = 0
                checkData = False
                warning = variableName + " must be between 0 and 1."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        
        return newVariable
    
    thermAbs = checkBtwZeroAndOne(_thermAbsp_, None, "_thermAbsp_")
    solAbsp = checkBtwZeroAndOne(_solAbsp_, None, "_solAbsp_")
    visAbsp = checkBtwZeroAndOne(_visAbsp_, None, "_visAbsp_")
    
    #Check the Roughness value.
    if _roughness_ != None: _roughness = _roughness_.upper()
    else: _roughness = None
    if _roughness == None or _roughness == "VERYROUGH" or _roughness == "ROUGH" or _roughness == "MEDIUMROUGH" or _roughness == "MEDIUMSMOOTH" or _roughness == "SMOOTH" or _roughness == "VERYSMOOTH": pass
    else:
        checkData = False
        warning = "_roughness_ is not valid."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return checkData


def main(name, roughness, R_Value, thermAbsp, solAbsp, visAbsp):
    
    if roughness == None: roughness = "Rough"
    if thermAbsp == None: thermAbsp = 0.9
    if solAbsp == None: solAbsp = 0.7
    if visAbsp == None: visAbsp = 0.7
    
    values = [name.upper(), roughness, R_Value, thermAbsp, solAbsp, visAbsp]
    comments = ["Name", "Roughness", "Thermal Resistance {m2-K/W}", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance"]
    
    materialStr = "Material:NoMass,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !" + str(comment)
            
    return materialStr
    

if _name and _R_Value:
    checkData = checkInputs()
    if checkData == True:
        EPMaterial = main(_name, _roughness_, _R_Value, _thermAbsp_, _solAbsp_, _visAbsp_)