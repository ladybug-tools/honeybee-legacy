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
Use this component to create a custom THERM material, which can be plugged into the "Honeybee_Create Therm Polygons" component.
-
Provided by Honeybee 0.0.58
    
    Args:
        _materialName: A text name for your THERM Material.
        _conductivity: A number representing the conductivity of the THERM material in W/m-K.
        absorptivity_: A number between 0 and 1 that represents the solar absorptivity of the material. The default is set to 0.5.
        emissivity_: A number between 0 and 1 that represents the emissivity of the material. The default is set to 0.9.
        type_:  An integer that represents the type of material.  The defaul is set to 0 - solid.  Choose from the following options:
            0 - Solid material
            1 - Gas material
         RGBColor_: An optional color to set the color of the material when you import it into THERM.
    Returns:
        thermMaterial: A therm material that can be plugged into the "Honeybee_Create Therm Polygons" component.

"""

ghenv.Component.Name = "Honeybee_Therm Material"
ghenv.Component.NickName = 'ThermMaterial'
ghenv.Component.Message = 'VER 0.0.58\nJAN_14_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nJAN_14_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import Grasshopper.Kernel as gh
import System
w = gh.GH_RuntimeMessageLevel.Warning


def main(materialName, conductivity, absorptivity, emissivity, type, RGBColor):
    #Set some default values.
    materialName = materialName.replace(' ' , '_')
    conductivity = conductivity/1.73
    if absorptivity == None: absorptivity = 0.5
    if emissivity == None: emissivity = 0.9
    if type == None: type = 0
    if RGBColor == None:
        r = lambda: random.randint(0,255)
        RGBColor = ('#%02X%02X%02X' % (r(),r(),r()))
    else:
        RGBColor = System.Drawing.ColorTranslator.ToHtml(RGBColor)
    
    #Make the string.
    materialString = '<Material Name=' +materialName+ ' Type=' +str(type)+ ' Conductivity=' + str(conductivity) + ' Absorptivity=' + str(absorptivity) + ' Emissivity=' + str(emissivity) + ' RGBColor=' + str(RGBColor) + '/>'
    
    return materialString



if _materialName != None and _conductivity != None:
    result= main(_materialName, _conductivity, absorptivity_, emissivity_, type_, RGBColor_)
    
    if result!=-1:
        thermMaterial = result
