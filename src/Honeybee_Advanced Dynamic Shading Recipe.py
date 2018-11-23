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
Advanced Shading Recipe for Annual Simulation with Daysim. This component prepares one shading group
You need to add sensor points later in the Daysim result reader.
-
Provided by Honeybee 0.0.64
    
    Args:
        SHDGroupName: Unique name of this shading group
        glareControlRecipe: Additional control for glare. Use Daysim glare control recipe to geneate the input
        coolingPeriod: Optional input for cooling priod. The blinds will be always down during the cooling period. Use Ladybug_Analysis Period component to create an input.
    Returns:
        dynamicShadingGroup: Dynamic shading group
"""

ghenv.Component.Name = "Honeybee_Advanced Dynamic Shading Recipe"
ghenv.Component.NickName = 'advancedDynamicSHDRecipe'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Grasshopper.Kernel as gh

# manage component inputs
numInputs = ghenv.Component.Params.Input.Count
for input in range(numInputs):
    if input == 0: inputName = 'SHDGorupName'
    elif input == numInputs - 1:
        inputName = 'coolingPeriod'
        ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.list
    elif input == numInputs - 2:
        inputName = 'glareControlRecipe'
    else:
        inputName = 'shading_state' + str(input)
        ghenv.Component.Params.Input[input].Description = "Shading State" + str(input) + " The states should start from the most open state to the most closed state. Detailes description is available on Daysim website:\nhttp://daysim.ning.com/page/daysim-header-file-keyword-advanced-dynamic-shading"
    
    ghenv.Component.Params.Input[input].NickName = inputName
    ghenv.Component.Params.Input[input].Name = inputName
#ghenv.Component.Attributes.Owner.ExpireSolution(True)
ghenv.Component.Attributes.Owner.OnPingDocument()


# read the layers
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os


class dynamicSHDRecipe(object):
    
    def __init__(self, type, name, shadingStates, glareControlRecipe, coolingPeriod, controlSystem):
        self.type = type
        self.name = name
        # self.sensorPts = sensors
        self.glareControlR = glareControlRecipe
        self.shadingStates = shadingStates
        self.controlSystem = controlSystem
        self.coolingPeriod = coolingPeriod

def main(SHDGorupName, glareControlRecipe, coolingPeriod):
    msg = None
    shadingStates = []
    
    for inputCount in range(ghenv.Component.Params.Input.Count):
        if inputCount!=0 and inputCount < ghenv.Component.Params.Input.Count-2:
            shadings = ghenv.Component.Params.Input[inputCount].NickName
            exec('shadingState = ' + shadings) #that's why I love Python. Yo!
            if inputCount==1 or shadingState != None:
                shadingStates.append(shadingState)
            else:
                msg = "Only the first shading state can be empty. " + \
                      "You need to provide a valid shading state for " + shadings + "."
                return msg, None
                
    if len(shadingStates)<2:
        msg = "At the minimum two shading stats should be provided. You can leave the first state empty for the open state."
        return msg, None
    
    controlSystem = None
    for shadingState in shadingStates:
        if shadingState!=None and controlSystem ==None:
            controlSystem = shadingState.controlSystem
        if shadingState!=None and shadingState.controlSystem != controlSystem:
            msg = "Control systems for all the shading stats should be the same.\n" + \
                  "Check the shading stats. You probably provided minimum and maximum illuminance values only for one of them."
            return msg, None
        elif shadingState!=None and shadingState.controlSystem == "ManualControl":
            if glareControlRecipe!=None or len(coolingPeriod)!=0:
                msg = "You cannot use glare control or cooling period when the shading control is manual.\n" + \
                      "Provide minimum and maximum illuminance level for shading state or disconnect glareControlRecipe and coolingPeriod."
                return msg, None
               
    dynamicShadingR = dynamicSHDRecipe(2, SHDGorupName, shadingStates, glareControlRecipe, coolingPeriod, controlSystem)
    
    return msg, dynamicShadingR


msg, dynamicShadingGroup = main(SHDGorupName, glareControlRecipe, coolingPeriod)

if msg!=None:
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
# manual control and cooling period can't happen together
