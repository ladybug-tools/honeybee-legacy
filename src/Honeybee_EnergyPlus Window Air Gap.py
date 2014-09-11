# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus Window Air Gap

-
Provided by Honeybee 0.0.55
    
    Args:
        _name: ...
        _U_Value: ...
        _SHGC: ...
        _VT: ...
    Returns:
        readMe!: ...

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Window Air Gap"
ghenv.Component.NickName = 'EPWindowAirGap'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(name, gasType, thickness):
    
    if name == None: name = "AIRGAP"
    if gasType == None: gasType = "AIR"
    if thickness == None: thickness = .0125
    
    values = [name.upper(), gasType, thickness]
    comments = ["Name", "Gas type", "Thickness {m}"]
    
    materialStr = "WindowMaterial:Gas,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !-" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !-" + str(comment)
            
    return materialStr

EPMaterial = main(_name_, _gasType_, _thickness_)
