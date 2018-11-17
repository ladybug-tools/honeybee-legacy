# This component creates a material for shades
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to create a custom material for shades, which can be plugged into the "Honeybee_EnergyPlus Window Shade Generator" component.
_
In order to apply the material to a window shade and adjust geometric characteristics of the shade, you should plug the output of this component into a "Honeybee_EnergyPlus Window Shade Generator" component.
_
Note that the material characteristics here can refer to either blind slats, roller shades, perforated exterior metal screens, or the properties of electrochromic glazing in an "on" state.
-
Provided by Honeybee 0.0.64
    
    Args:
        materialName_: An optional name for the shade material.
        reflectance_: A number between 0 and 1 that represents the front reflectance of the shade material.  The default value is set to 0.65.
        transmittance_: A number between 0 and 1 that represents the transmittance of the shade material. The default value is set to 0 for a perfectly opaque shade.
        emissivity_: A number between 0 and 1 that represents the emissivity of the shade material. The default value is set to 0.9 for a non-metalic shade.
        thickness_: An optional number representing the thickness of the shade in meters.  For blinds, this is the thickness of each blind slat and, for roller shades and screens, this is the thickness of the fabric or screen material.  For electrochromic windows, this variable is discounted since window materials with n mass are used. The default is set to 0.00025 m for a very thin shade.
        conductivity_: An optional number representing the conductivity of the shade material in W/m-K.  The default is set to 221 W/m-K.
    Returns:
        shadeMaterial: A shade material that can be plugged into the ZoneShades component.
"""

ghenv.Component.Name = "Honeybee_EnergyPlus Shade Material"
ghenv.Component.NickName = 'EPShadeMat'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import uuid
import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning

def setDefaults():
    checkData1 = True
    if reflectance_ == None: reflectance = 0.65
    else:
        if reflectance_ <= 1 and reflectance_ >= 0: reflectance = reflectance_
        else:
            reflectance = None
            checkData1 = False
            warning = "Reflectance must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData2 = True
    if transmittance_ == None: transmittance = 0
    else:
        if transmittance_ <= 1 and transmittance_ >= 0: transmittance = transmittance_
        else:
            transmittance = None
            checkData2 = False
            warning = "Transmittance must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData3 = True
    if emissivity_ == None: emissivity = 0.9
    else:
        if emissivity_ <= 1 and emissivity_ >= 0: emissivity = emissivity_
        else:
            emissivity = None
            checkData3 = False
            warning = "Emissivity must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData4 = True
    if (reflectance + transmittance) > 0.99: #!< 1:
        checkData4 = False
        warning = "reflectance_ + transmittance_ must be lower than 1."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    
    if thickness_ == None: thickness = 0.00025
    else: thickness = thickness_
    
    if conductivity_ == None: conductivity = 221
    else: conductivity = conductivity_
    
    
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True: checkData = True
    else: checkData = False
    
    if materialName_ == None: materialName = "ShadeMaterial"+ '-'+str(reflectance)+ '-' +str(transmittance)+ '-' +str(emissivity)+ '-' +str(thickness)+ '-' +str(conductivity)
    else: materialName = materialName_
    
    return checkData, materialName, reflectance, transmittance, emissivity, thickness, conductivity


def main(name, reflectance, transmittance, emissivity, thickness, conductivity):
    
    values = [name.upper(), reflectance, transmittance, emissivity, thickness, conductivity]
    comments = ["Name", "Reflectance", "Transmittance", "Emissivity", "Slat Thickness", "Conductivity"]
    
    materialStr = "WindowMaterial:Blind,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !-" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !-" + str(comment)
            
    return materialStr


checkData, materialName, reflectance, transmittance, emissivity, thickness, conductivity = setDefaults()
if checkData == True:
    shadeMaterial = main(materialName, reflectance, transmittance, emissivity, thickness, conductivity)