# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus Window Material

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

ghenv.Component.Name = "Honeybee_EnergyPlus Window Material"
ghenv.Component.NickName = 'EPWindowMat'
ghenv.Component.Message = 'VER 0.0.53\nJUL_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

def main(name, U_Value, SHGC, VT):
    
    values = [name.upper(), U_Value, SHGC, VT]
    comments = ["Name", "U Value", "Solar Heat Gain Coeff", "Visible Transmittance"]
    
    materialStr = "WindowMaterial:SimpleGlazingSystem,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !-" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !-" + str(comment)
            
    return materialStr

if _name and _U_Value and _SHGC and _VT:
    EPMaterial = main(_name, _U_Value, _SHGC, _VT)