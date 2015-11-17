# This component creates a material for blinds
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to create a cutom material for blinds, which can be plugged into the "Honeybee_Zone Shade Generator" component.
_
The output of this component can also be used in a construction but note that default values will be applied for blind thicknesses and angles of the slats.  In order to adjust these characteristics of the blind material, you should plug the output here into a "Honeybee_Zone Shades" component.
-
Provided by Honeybee 0.0.58
    
    Args:
        materialName_: An optional name for the blind material.
        reflectance_: A number between 0 and 1 that represents the front reflectance of the blind material.  The default value is set to 0.65.
        transmittance_: A number between 0 and 1 that represents the transmittance of the blind material. The default value is set to 0 for a perfectly opaque shade.
        emissivity_: A number between 0 and 1 that represents the emissivity of the blind material. The default value is set to 0.9 for a non-metalic shade.
        slatThickness_: An optional number representing the thickness of each blind slat in millimeters.  The default is set to 0.25 mm for a very thin shade.
        conductivity_: An optional number representing the conductivity of the blind material in W/m-K.  The default is set to 221 W/m-K.
    Returns:
        blindMaterial: A blind material that can be plugged into the ZoneShades component.
"""

ghenv.Component.Name = "Honeybee_EnergyPlus Blinds Material"
ghenv.Component.NickName = 'EPBlindsMat'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning

def setDefaults():
    if materialName_ == None: materialName = "DefaultBlindsMaterial"
    else: materialName = materialName_
    
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
    
    if slatThickness_ == None: slatThickness = 0.00025
    else: slatThickness = slatThickness_/1000
    
    if conductivity_ == None: conductivity = 221
    else: conductivity = conductivity_
    
    
    if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
    else: checkData = False
    
    
    return checkData, materialName, reflectance, transmittance, emissivity, slatThickness, conductivity


def main(name, reflectance, transmittance, emissivity, slatThickness, conductivity):
    
    values = [name.upper(), reflectance, transmittance, emissivity, slatThickness, conductivity]
    comments = ["Name", "Reflectance", "Transmittance", "Emissivity", "Slat Thickness", "Conductivity"]
    
    materialStr = "WindowMaterial:Blind,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !-" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !-" + str(comment)
            
    return materialStr


checkData, materialName, reflectance, transmittance, emissivity, slatThickness, conductivity = setDefaults()
if checkData == True:
    blindsMaterial = main(materialName, reflectance, transmittance, emissivity, slatThickness, conductivity)