# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus NoMass Opaque Material

-
Provided by Honeybee 0.0.53
    
    Args:
        _name: ...
        _U_Value: ...
        _SHGC: ...
        _VT: ...
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_EnergyPlus NoMass Opaque Material"
ghenv.Component.NickName = 'EPNoMassMat'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

def main(name, roughness, R_Value, thermAbsp, solAbsp, visAbsp):
    
    if roughness == None: roughness = "Rough"
    if thermAbsp == None: thermAbsp = 0.9
    if solAbsp == None: solAbsp = 0.7
    if visAbsp == None: visAbsp = 0.7
    
    values = [name, roughness, R_Value, thermAbsp, solAbsp, visAbsp]
    comments = ["Name", "Roughness", "Thermal Resistance {m2-K/W}", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance"]
    
    materialStr = "Material:NoMass,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !" + str(comment)
            
    return materialStr
    

if _name and _R_Value:
    EPMaterial = main(_name, _roughness_, _R_Value, _thermAbsp_, _solAbsp_, _visAbsp_)