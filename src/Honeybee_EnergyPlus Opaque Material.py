# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus Opaque Material

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

ghenv.Component.Name = "Honeybee_EnergyPlus Opaque Material"
ghenv.Component.NickName = 'EPOpaqueMat'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(name, roughness, thickness, conductivity, density, specificHeat, thermAbsp, solAbsp, visAbsp):
    
    if roughness == None: roughness = "Rough"
    if thermAbsp == None: thermAbsp = 0.9
    if solAbsp == None: solAbsp = 0.7
    if visAbsp == None: visAbsp = 0.7
    
    values = [name.upper(), roughness, thickness, conductivity, density, specificHeat, thermAbsp, solAbsp, visAbsp]
    comments = ["Name", "Roughness", "Thickness {m}", "Conductivity {W/m-K}", "Density {kg/m3}", "Specific Heat {J/kg-K}", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance"]
    
    materialStr = "Material,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !" + str(comment)
            
    return materialStr
    

if _name and _thickness and _conductivity and _density and _specificHeat:
    EPMaterial = main(_name, _roughness_, _thickness, _conductivity, _density, _specificHeat, _thermAbsp_, _solAbsp_, _visAbsp_)