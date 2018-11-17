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
Use this component to create a custom THERM material, which can be plugged into the "Honeybee_Create Therm Polygons" component.
-
Provided by Honeybee 0.0.64
    
    Args:
        _materialName: A text name for your THERM Material.
        _conductivity: A number representing the conductivity of the THERM material in W/m-K.
        absorptivity_: A number between 0 and 1 that represents the solar absorptivity of the material. The default is set to 0.5.
        emissivity_: A number between 0 and 1 that represents the emissivity of the material. The default is set to 0.9.
        cavityModel_:  An integer that represents the cavity model to use for the material (if it is a gas).  If you are creating a solid material, just leave this input blank.  Cavity models (4 - ISO 15099) and (5 - ISO 15099 ventilated) are used for most situations.  Choose from the following options:
            0 - NFRC
            1 - CEN
            2 - CEN (slightly ventilated)
            3 - NFRC with user dimensions
            4 - ISO 15099
            5 - ISO 15099 ventilated
         RGBColor_: An optional color to set the color of the material when you import it into THERM.
    Returns:
        thermMaterial: A therm material that can be plugged into the "Honeybee_Create Therm Polygons" component.

"""

ghenv.Component.Name = "Honeybee_Therm Material"
ghenv.Component.NickName = 'ThermMaterial'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nJAN_14_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import System
import random
import scriptcontext as sc
w = gh.GH_RuntimeMessageLevel.Warning


def main(materialName, conductivity, absorptivity, emissivity, cavityModel, RGBColor):
    #Set some default values.
    materialName = materialName.replace(' ' , '_')
    conductivity = conductivity
    if absorptivity == None: absorptivity = 0.5
    if emissivity == None: emissivity = 0.9
    if cavityModel == None: type = 0
    else: type = 1
    if RGBColor == None:
        r = lambda: random.randint(0,255)
        RGBColor = ('#%02X%02X%02X' % (r(),r(),r()))
    else:
        RGBColor = System.Drawing.ColorTranslator.ToHtml(RGBColor)
        if not RGBColor.startswith('#'):
            color = System.Drawing.Color.FromName(RGBColor)
            RGBColor = System.String.Format("#{0:X2}{1:X2}{2:X2}", color.R, color.G, color.B)
    
    #Make the string.
    if type == 0:
        materialString = '<Material Name=' +materialName+ ' Type=' +str(type)+ ' Conductivity=' + str(conductivity) + ' Absorptivity=' + str(absorptivity) + ' Emissivity=' + str(emissivity) + ' RGBColor=' + str(RGBColor) + '/>'
    else:
        materialString = '<Material Name=' +materialName+ ' Type=' +str(type)+ ' Conductivity=' + str(conductivity) + ' Absorptivity=' + str(absorptivity) + ' Emissivity=' + str(emissivity) + ' RGBColor=' + str(RGBColor) + ' CavityModel=' + str(cavityModel) + '/>'
    
    return materialString

#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if initCheck == True and _materialName != None and _conductivity != None:
    result= main(_materialName, _conductivity, absorptivity_, emissivity_, cavityModel_, RGBColor_)
    
    if result!=-1:
        thermMaterial = result
