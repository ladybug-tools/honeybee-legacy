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
Use this component to make your own EnergyPlus construction.  Inputs can be either the name of a matterial form the Openstudio construction library or a custom material made with any of the EnergyPlus Material components.
_
Note that the last layer in the component is always the innermost layer and _layer_1 is always the outermost layer.
_
To add more layers in the construction, simply zoom into the component and hit the lowest "+" sign that shows up on the input side.  To remove layers from the construction, zoom into the component and hit the lowest "-" sign that shows up on the input side.
-
Provided by Honeybee 0.0.59
    
    Args:
        _name: A text name for your custom construction. This is what you will use as an input to other components in order to reference your custom construction.
        _layer_1: The first and outer-most layer of your construction.
        _layer_2: The second outer-most layer of your construction.
        _layer_3: The third outer-most layer of your construction.
        _layer_4: The fourth outer-most layer of your construction.
        _layer_5: The fifth outer-most layer of your construction.
        _layer_6: The sixth outer-most layer of your construction.
    Returns:
        EPConstruction: An EnergyPlus construction that can be plugged into the "Honeybee_Add to EnergyPlus Library" component in order to write the construction into the project library.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Construction"
ghenv.Component.NickName = 'EPConstruction'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

# set the right names
numInputs = ghenv.Component.Params.Input.Count
for input in range(numInputs):
    if input == 0: inputName = '_name'
    else: inputName = '_layer_' + str(input)
    
    ghenv.Component.Params.Input[input].NickName = inputName
    ghenv.Component.Params.Input[input].Name = inputName
    
ghenv.Component.Attributes.Owner.OnPingDocument()
if numInputs > 11:
    err = "Maximum number of layers in an EnergyPlus construction is 10.\n" + \
          "Remove the last input you just added to the component"
    raise ValueError(err)

def main():
    
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    # check if all the layers are there
    # check if the material is already created in the library
    # if not then stop the process
    materialNames = []
    
    constructionStr = "Construction,\n" + _name.upper() + ",    !- Name\n"
    
    for inputCount in range(ghenv.Component.Params.Input.Count):
        if inputCount!=0 and inputCount < ghenv.Component.Params.Input.Count:
            layerName = ghenv.Component.Params.Input[inputCount].NickName
            exec('materialName = ' + layerName) #that's why I love Python. Yo!
            # check if it is only the name
            if materialName != None and len(materialName.split("\n")) == 1:
                materialName = materialName.upper()
            elif materialName!=None:
                # it is a full string
                added, materialName = hb_EPMaterialAUX.addEPConstructionToLib(materialName, overwrite = True)
                materialName = materialName.upper()
            
            # double check that everything is fine
            if materialName in sc.sticky ["honeybee_materialLib"].keys():
                pass
            elif materialName in sc.sticky ["honeybee_windowMaterialLib"].keys():
                pass
            else:
                msg = "layer_" + str(inputCount) + " is not a valid material name/definition.\n" + \
                    "Create the material first and try again."
                ghenv.Component.AddRuntimeMessage(w, msg)
                return
            
            if inputCount!= ghenv.Component.Params.Input.Count - 1:
                constructionStr += materialName + ",    !- Layer " + str(inputCount) + "\n"
            else:
                constructionStr += materialName + ";    !- Layer " + str(inputCount) + "\n"
                    
    return constructionStr

#if addToLibrary:
#    customLibPath = "C:/Ladybug/userCustomLibrary.idf"
#    if not os.path.isfile(customLibPath): modifier = 'w'
#    else: modifier = 'a'
#    with open(customLibPath, modifier) as libFile:
#        constructionStr = EPConstructionStr(name)
#        # Later I should add a check and avoid duplicates
#        libFile.write(constructionStr)

if _name and _layer_1:
    constr = main()
    
    if constr!=-1:
        EPConstruction = constr