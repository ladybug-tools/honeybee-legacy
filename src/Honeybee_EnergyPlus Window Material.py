#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to create a custom window material that has no mass, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
It is important to note that this component creates a material with no mass and that is meant to represent an entire window element (including all panes of glass and the frame).  Because of this, when you plug this material into the "Honeybee_EnergyPlys Construction" component, it is important that this is the only material connected.  Otherwise, E+ will crash when you try to run it.
Also because of this, the accuracy of this material is not as great as a material that has mass.  However, this component is very useful if you only have a U-value, SHGC, and VT for a window construction and no other information.
_
If you want to create a material that accounts for mass, you should use the "Honeybee_EnergyPlus Glass Material" component and the "Honeybee_EnergyPlus Window Air Gap" to create a window construction with one or multiple panes.
-
Provided by Honeybee 0.0.64
    
    Args:
        _name: A text name for your NoMass Window Material.
        _U_Value: A number representing the U-value of the window in W/m2-K. This is the rated (NFRC) U-value under winter heating conditions. As a result, the U-Value input here should include the air films for a vertically-mounted product.
        _SHGC: A number between 0 and 1 that represents the solar heat gain coefficient (SHGC) of the window. The solar heat gain coeffieceint is essentially the fraction of solar radiation falling on the window that makes it through the glass (at normal incidence).  This number is usually very close to the visible transmittance (VT) for glass without low-e coatings but can be might lower for glass with low-e coatings.
        _VT: A number between 0 and 1 that represents the visible transmittance (VT) of the window. The visible transmittance is essentially the fraction of visible light falling on the window that makes it through the glass (at normal incidence).  This number is usually very close to the solar heat gain coefficent (SHGC) for glass without low-e coatings but can be might higher for glass with low-e coatings.
    Returns:
        EPMaterial: A no-mass window material that can be plugged into the "Honeybee_EnergyPlus Construction" component.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Window Material"
ghenv.Component.NickName = 'EPWindowMat'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def checkInputs():
    #Check to be sure that SHGC and VT are between 0 and 1.
    checkData = True
    
    def checkBtwZeroAndOne(variable, default, variableName, max=1, min=0):
        if variable == None: newVariable = default
        else:
            if variable <= max and variable >= min: newVariable = variable
            else:
                newVariable = 0
                checkData = False
                warning = variableName + " must be between " + str(min) + " and " + str(max)
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        return newVariable
    
    if _U_Value <0.5:
        infoMsg = "You probably input an imperial U value, please double check. If yes, please use uIP2uSI to convert it."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, infoMsg)
    SHGC = checkBtwZeroAndOne(_SHGC, None, "_SHGC")
    VT = checkBtwZeroAndOne(_VT, None, "_VT")
    U_Value = checkBtwZeroAndOne(_U_Value, None, "_U_Value", 5.8)
    
    return checkData


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

if _name is not None and _U_Value is not None and _SHGC is not None and _VT is not None :
    checkData = checkInputs()
    if checkData == True:
        EPMaterial = main(_name, _U_Value, _SHGC, _VT)