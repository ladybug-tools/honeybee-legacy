#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to adjust the U-value an EP construction without any thermal bridges to account for birdges by adjusting the condutivity of one of the materials.
-
Provided by Honeybee 0.0.64

    Args:
        _originalEPConstruction: An EP construction that does not have any thermal bridges associated with it.
        _thermBridgedUValue: The U-value in SI units (W/m2-K) that you would like the whole construction assembly to be adjusted to.  This U-value should include the resistance of air films on either side of the construction assembly, which is included by default in the output from THERM simulations.
        _materialToAdjust: The name of a material within the _originalEPConstruction that you would like to have the conductivity adjusted to meet the _thermBridgedUValue.
        _customName_: An optional custom name to be added to the new thermally bridged material and construction.
    Returns:
        readMe!:...
        bridgedConstruction: A thermally bridged construction that can be applied to HBZones and HBSurfaces for energy simulations.
        bridgedConstrText: The IDF text that defines the thermally bridged construction that has been written to the memory of the document.
        bridgedMaterialText: The IDF text that defines the thermally bridged material within the construction.
        bridgedMatRValue: The R-value of the newly created thermally bridged material.
"""


ghenv.Component.Name = 'Honeybee_Thermally Bridged EP Construction'
ghenv.Component.NickName = 'bridgedEPConstr'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh


def main(EPConstruction, thermBridgedUValue, materialToAdjust, customName, hb_EPMaterialAUX, hb_EPObjectsAux):
    # Set default name.
    if customName == None:
        customName = "_ThermallyBridged"
    
    # Check whether the construction is in the library.
    if len(EPConstruction.split("\n")) == 1:
        # if the construction is not in the library add it to the library
        if not hb_EPObjectsAux.isEPConstruction(EPConstruction):
            warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                        "Add the construction to the library and try again."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            return -1
    else:
        # it is a full string
        added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(EPConstruction, overwrite = True)
        
        if not added:
            msg = name + " cannot be added to the project library! Make sure it is an standard EP construction."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            print msg
            return -1
    
    # Get the U-value of the originalEPConstruction from the library.
    materials, constrComments, UValue_SI, UValue_IP = hb_EPMaterialAUX.decomposeEPCnstr(EPConstruction.upper())
    RValue_SI = 1/UValue_SI
    
    # Check to be sure that the materialToAdjust is in the originalEPConstruction.
    materialToAdjust = materialToAdjust.replace(',','').strip()
    if not materialToAdjust.upper() in materials:
        msg = "Could not find the materialToAdjust " + materialToAdjust.upper() + " in the construction " + EPConstruction.upper()
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        print msg
        return -1
    
    # Get the properties of the materialToAdjust.
    result = hb_EPMaterialAUX.decomposeMaterial(materialToAdjust.upper(), ghenv.Component)
    if result == -1:
        warning = "Failed to find " + materialToAdjust + " in the Honeybee material library."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    else:
        values, matComments, matUValue_SI, matUValue_IP = result
    matRValue_SI = 1/matUValue_SI
    
    # Remove air films from the thermBridgedUValue.
    thermBridgedRNoFilm = (1/thermBridgedUValue) - 0.17
    
    # Make sure that there is enough resistance in the materialToAdjust to meet the thermBridgedUValue.
    RValueDifference = RValue_SI - thermBridgedRNoFilm
    if matRValue_SI < RValueDifference:
        warning = "There is not enough thermal resistance in the material " + materialToAdjust + "(R-value = " + str(matRValue_SI) + ')\n' + \
            "to make up for the difference between the " + EPConstruction + "construction (R-value = " + str(RValue_SI) + ')\n' + \
            "and the _thermBridgedUValue (R-value = " + str(thermBridgedRNoFilm) + ').\n' + \
            "Try raising the _thermBridgedUValue or using a different _materialToAdjust within the _originalEPConstruction."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    # Create the new thermally bridged material.
    bridgedMatName = materialToAdjust + customName
    newRvalue = matRValue_SI - RValueDifference
    if values[0].upper() == 'MATERIAL:NOMASS':
        materialStr = "Material:NoMass,\n" + bridgedMatName.upper() + ",    !- Name\n"
        values[2] = newRvalue
    elif values[0].upper() == 'MATERIAL':
        # Calculate the conductivity of the new thermally bridged material.
        newUvalue = 1/newRvalue
        thickness = values[2]
        newConductivity = newUvalue * float(thickness)
        materialStr = "Material,\n" + bridgedMatName.upper() + ",    !- Name\n"
        values[3] = newConductivity
    else:
        warning = "The R-value of materials of type " + values[0].upper() + " cannot be adjusted with this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    
    for count, (value, comment) in enumerate(zip(values, matComments)):
        if count != 0:
            if count!= len(values) - 1:
                materialStr += str(value) + ",    !" + str(comment) + "\n"
            else:
                materialStr += str(value) + ";    !" + str(comment)
    
    # Add the new material to the library.
    added, newMatname = hb_EPObjectsAux.addEPObjectToLib(materialStr, True)
    if not added:
        msg = newMatname + " is not added to the project library!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    else: print newMatname + " is has been added to the project library!"
    
    # Create a new construction.
    matCount = materials.index(materialToAdjust.upper())
    materials[matCount] = newMatname
    constrStr = "Construction,\n" + EPConstruction + customName + ",    !- Name\n"
    for count, (value, comment) in enumerate(zip(materials, constrComments)):
        if count!= len(values) - 1:
            constrStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            constrStr += str(value) + ";    !" + str(comment)
    
    # Add the construction to the library.
    added, newConstrname = hb_EPObjectsAux.addEPObjectToLib(constrStr, True)
    if not added:
        msg = newConstrname + " is not added to the project library!"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    else: print newConstrname + " is has been added to the project library!"
    
    return newConstrname, constrStr, materialStr, newRvalue




#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Honeybee check.
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

if initCheck == True:
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()


#If the intital check is good, run the component.
if initCheck and _originalEPConstruction != None and _thermBridgedUValue != None and _materialToAdjust != None:
    result = main(_originalEPConstruction, _thermBridgedUValue, _materialToAdjust, _customName_, hb_EPMaterialAUX, hb_EPObjectsAux)
    if result != -1:
        bridgedConstruction, bridgedConstrText, bridgedMaterialText, bridgedMatRValue = result
