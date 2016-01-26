#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to create a custom opaque material, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
This component requires you to know a lot of the characteristics of the material and, you may want to borrow some characteristcs of a similar material in the library.  Use the "Honeybee_Call From EP Construction Library" and the "Honeybee_Decompose EP Material" to help with this.
_
If you are not able to find all of the necessary material characteristcs and your desired material is relatively light, it might be easier for you to use a "Honeybee_EnergyPlus NoMass Opaque Material."
-
Provided by Honeybee 0.0.59
    
    Args:
        _name: A text name for your Opaque Material.
        _roughness_: A text value that indicated the roughness of your material.  This can be either "VeryRough", "Rough", "MediumRough", "MediumSmooth", "Smooth", and "VerySmooth".  The default is set to "Rough".
        _thickness: A number that represents the thickness of the material in meters (m).
        _conductivity:  A number representing the conductivity of the material in W/m-K.  This is essentially the heat flow in Watts across one meter thick of the material when the temperature difference on either side is 1 Kelvin.
        _density:  A number representing the density of the material in kg/m3.  This is essentially the mass one cubic meter of the material.
        _specificHeat:  A number representing the specific heat capacity of the material in J/kg-K.  This is essentially the number of joules needed to raise one kg of the material by 1 degree Kelvin.
        _thermAbsp_: An number between 0 and 1 that represents the thermal abstorptance of the material.  The default is set to 0.9, which is common for most non-metallic materials.
        _solAbsp_: An number between 0 and 1 that represents the abstorptance of solar radiation by the material.  The default is set to 0.7, which is common for most non-metallic materials.
        _visAbsp_: An number between 0 and 1 that represents the abstorptance of visible light by the material.  The default is set to 0.7, which is common for most non-metallic materials.
    Returns:
        EPMaterial: An opaque material that can be plugged into the "Honeybee_EnergyPlus Construction" component.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Opaque Material"
ghenv.Component.NickName = 'EPOpaqueMat'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
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
    checkData = checkInputs()
    if checkData == True:
        EPMaterial = main(_name, _roughness_, _thickness, _conductivity, _density, _specificHeat, _thermAbsp_, _solAbsp_, _visAbsp_)