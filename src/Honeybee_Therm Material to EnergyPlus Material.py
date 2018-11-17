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
Use this component to create a custom opaque material, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
This component requires you to know a lot of the characteristics of the material and, you may want to borrow some characteristcs of a similar material in the library.  Use the "Honeybee_Call From EP Construction Library" and the "Honeybee_Decompose EP Material" to help with this.
_
If you are not able to find all of the necessary material characteristcs and your desired material is relatively light, it might be easier for you to use a "Honeybee_EnergyPlus NoMass Opaque Material."
-
Provided by Honeybee 0.0.64
    
    Args:
        _thermMaterial: The name of a Therm material from the ThermMaterials output from the from the "Call from EP Construction Library" component.
        _roughness_: A text value that indicated the roughness of your material.  This can be either "VeryRough", "Rough", "MediumRough", "MediumSmooth", "Smooth", and "VerySmooth".  The default is set to "Rough".
        _thickness: A number that represents the thickness of the material in meters (m).
        _density:  A number representing the density of the material in kg/m3.  This is essentially the mass one cubic meter of the material.
        _specificHeat:  A number representing the specific heat capacity of the material in J/kg-K.  This is essentially the number of joules needed to raise one kg of the material by 1 degree Kelvin.
    Returns:
        EPMaterialStr: An opaque material that can be plugged into the "Honeybee_EnergyPlus Construction" component.
        matName: The name of the generated EP Material.

"""

ghenv.Component.Name = "Honeybee_Therm Material to EnergyPlus Material"
ghenv.Component.NickName = 'ThermMat2EPMat'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
w = gh.GH_RuntimeMessageLevel.Warning


def checkInputs():
    #Get the material from the THERM Library.
    ThermMaterials = sc.sticky["honeybee_thermMaterialLib"].keys()
    thermMaterial = None
    if _thermMaterial.startswith("<Material"):
        thermMaterial = addThermMatToLib(_thermMaterial)
    elif not _thermMaterial.upper() in ThermMaterials:
        warning = "Cannot find _thermMaterial in THERM Material library."
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    thermMaterial = sc.sticky["honeybee_thermMaterialLib"][_thermMaterial.upper()]
    
    #Make sure that the thickness is reasonalbe.
    if _thickness > 1:
        warning = "Material thicknesses greater than 1 will cause EnergyPlus to crash."
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    return thermMaterial


def addThermMatToLib(materialString):
    #Parse the string.
    materialName = materialString.split('Name=')[-1].split(' ')[0].replace('_', ' ').upper()
    type = int(materialString.split('Type=')[-1].split(' ')[0])
    conductivity = float(materialString.split('Conductivity=')[-1].split(' ')[0])
    absorptivity = float(materialString.split('Absorptivity=')[-1].split(' ')[0])
    emissivity = float(materialString.split('Emissivity=')[-1].split(' ')[0])
    RGBColor = System.Drawing.ColorTranslator.FromHtml(materialString.split('RGBColor=')[-1].split('/>')[0])
    
    #Make a sub-dictionary for the material.
    sc.sticky["honeybee_thermMaterialLib"][materialName] = {}
    
    #Create the material with values from the original material.
    sc.sticky["honeybee_thermMaterialLib"][materialName]["Name"] = materialName
    sc.sticky["honeybee_thermMaterialLib"][materialName]["Type"] = type
    sc.sticky["honeybee_thermMaterialLib"][materialName]["Conductivity"] = conductivity
    sc.sticky["honeybee_thermMaterialLib"][materialName]["Absorptivity"] = absorptivity
    sc.sticky["honeybee_thermMaterialLib"][materialName]["Emissivity"] = emissivity
    sc.sticky["honeybee_thermMaterialLib"][materialName]["RGBColor"] = RGBColor
    
    return materialName

def main(thermMaterial, roughness, thickness, density, specificHeat):
    
    name = thermMaterial['Name'].replace(',', '')
    conductivity = float(thermMaterial['Conductivity'])
    thermAbsp = thermMaterial['Emissivity']
    solAbsp = thermMaterial['Absorptivity']
    visAbsp = thermMaterial['Absorptivity']
    if roughness == None: roughness = "Rough"
    
    values = [name.upper()+'-EP', roughness, thickness, conductivity, density, specificHeat, thermAbsp, solAbsp, visAbsp]
    comments = ["Name", "Roughness", "Thickness {m}", "Conductivity {W/m-K}", "Density {kg/m3}", "Specific Heat {J/kg-K}", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance"]
    
    materialStr = "Material,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !" + str(comment)
            
    return materialStr, name.upper()+'-EP'


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


if initCheck == True and _thermMaterial and _thickness and _density and _specificHeat:
    thermMaterial = checkInputs()
    if thermMaterial != -1:
        EPMaterialStr, matName = main(thermMaterial, _roughness_, _thickness, _density, _specificHeat)