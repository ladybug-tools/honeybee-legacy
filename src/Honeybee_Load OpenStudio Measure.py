#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
This component loads OpenStudio measureds into Honeybee. The measure can be applied to an OpenStudio model.
Read more about OpenStudio measures here: http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/
You can download several measures from here: https://bcl.nrel.gov/nrel/types/measure

-
Provided by Honeybee 0.0.58

    Args:
        _OSMeasure: Path to measure directory [NOT THE FILE]. This input will be removed once measure is loaded
    Returns:
        OSMeasure: Loaded OpenStudio measure
"""
ghenv.Component.Name = "Honeybee_Load OpenStudio Measure"
ghenv.Component.NickName = 'importOSMeasure'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import Grasshopper.Kernel as gh
import scriptcontext as sc
from pprint import pprint

class OPSChoice:
    
    def __init__(self, originalString):
        self.originalString = originalString
        self.value = self.get_value()
        self.display_name = self.get_display_name()
    
    def get_display_name(self):
        return self.originalString.split("<display_name>")[-1].split("</display_name>")[0]
    
    def get_value(self):
        return self.originalString.split("<value>")[-1].split("</value>")[0]
    
    def __repr__(self):
        return self.display_name

class OPSMeasureArg:
    def __init__(self, originalString):
        self.originalString = originalString
        self.name = self.get_name()
        self.display_name = self.get_display_name()
        self.description = self.get_description()
        self.type = self.get_type()
        self.required = self.get_required()
        self.model_dependent = self.get_model_dependent()
        self.default_value = self.get_default_value()
        self.choices = self.get_choices()
        self.validChoices = [choice.value.lower() for choice in self.choices]
        self.userInput = None
        
    def get_name(self):
        return self.originalString.split("<name>")[-1].split("</name>")[0]
    
    def get_display_name(self):
        return self.originalString.split("</display_name>")[0].split("<display_name>")[-1]

    def get_description(self):
        return self.originalString.split("<description>")[-1].split("</description>")[0]
        
    def get_type(self):
        return self.originalString.split("<type>")[-1].split("</type>")[0]
    
    def get_required(self):
        req = self.originalString.split("<required>")[-1].split("</required>")[0]
        return True if req.strip() == "true" else False
        
    def get_model_dependent(self):
        depends = self.originalString.split("<model_dependent>")[-1].split("</model_dependent>")[0]
        return True if depends.strip() == "true" else False
    
    def get_default_value(self):
        value = self.originalString.split("<default_value>")[-1].split("</default_value>")[0]
        if self.type.lower() != "boolean": return value
        return True if value.strip() == "true" else False
        
    def get_choices(self):
        choicesContainer = self.originalString.split("<choices>")[-1].split("</choices>")[0]
        choices = [arg.split("<choice>")[-1] for arg in choicesContainer.split("</choice>")][:-1]
        return [OPSChoice(choice) for choice in choices]
    
    def update_value(self, userInput):
        #currently everything is string
        if str(userInput).lower() not in self.validChoices:
            #give warning
            msg = str(userInput) + " is not a valid input for " + self.display_name + ".\nValid inputs are: " + str(self.choices)
            give_warning(msg)
        else:
            self.userInput = userInput
            
    def __repr__(self):
        return (self.display_name + "<" + self.type + "> " + str(self.choices) + \
               " Current Value: %s")%(self.default_value if not self.userInput else self.userInput)

def give_warning(msg):
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, msg)
    
def get_measureArgs(xmlFile):
    # there is no good XML parser for IronPython
    # here is parsing the file
    with open(xmlFile, "r") as measure:
        lines = measure.readlines()
        argumentsContainer = "".join(lines).split("<arguments>")[-1].split("</arguments>")[0]
    
    arguments = [arg.split("<argument>")[-1] for arg in argumentsContainer.split("</argument>")][:-1]
    
    #collect arguments in a dictionary so I can map the values on update
    args = dict()
    for count, arg in enumerate(arguments):
        args[count+1] = OPSMeasureArg(arg)
    return args

def addInputParam(arg, path):
    param = gh.Parameters.Param_ScriptVariable()
    param.NickName = arg.display_name
    param.Name = arg.name
    param.Description = str(arg)
    param.Optional = True # even if it is required it has a default value
    param.AllowTreeAccess = False
    #gh.Parameters.Param_ScriptVariable.
    param.Access = gh.GH_ParamAccess.item # I assume this can't be a list
    param.AddVolatileData(path, 0, arg.default_value)
    index = ghenv.Component.Params.Input.Count
    ghenv.Component.Params.RegisterInputParam(param,index)
    ghenv.Component.Params.OnParametersChanged()

def cleanInputNames():
    # I couldn't find a clean way to remove the input so I just change the name
    for paramCount in range(1,ghenv.Component.Params.Input.Count):
        param = ghenv.Component.Params.Input[paramCount]
        param.NickName = "."
        param.Name = "."
        param.Description = "."
        param.Optional = False
        ghenv.Component.Params.OnParametersChanged()

def cleanFirstInput():
    ghenv.Component.Params.Input[0].NickName = "."
    ghenv.Component.Params.Input[0].Name = "."
    ghenv.Component.Params.Input[0].RemoveAllSources()    

def updateComponentDescription(xmlFile):
    # get name of measure and description
    nickName = os.path.normpath(xmlFile).split("\\")[-2]
    ghenv.Component.NickName = nickName
    with open(xmlFile, "r") as measure:
        lines = "".join(measure.readlines())
        ghenv.Component.Name = lines.split("</display_name>")[0].split("<display_name>")[-1]
        ghenv.Component.Description = lines.split("</description>")[0].split("<description>")[-1]
    
    # change it to name so user can see the name
    ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.name

class OpenStudioMeasure:
    
    def __init__(self, name, nickName, description, measurePath, args):
        self.name = name
        self.nickName = nickName
        self.description = description
        self.path = os.path.normpath(measurePath)
        self.args = args
    
    def updateArguments(self):
        #iterate over inputs and assign the new values in case there is any new values
        for i in range(1, ghenv.Component.Params.Input.Count):
            
            try:
                value = ghenv.Component.Params.Input[i].VolatileData[0][0]
            except:
                value = self.args[i].default_value
                
            self.args[i].update_value(value)
    
    def __repr__(self):
        return "OpenStudio " + self.name


if _OSMeasure:

    xmlFile = os.path.join(_OSMeasure, "measure.xml")
    if not os.path.isfile(xmlFile): raise Exception("Can't find measure at " + xmlFile)
    
    # load arguments
    args = get_measureArgs(xmlFile)
    
    # add arguments to component
    path = gh.Data.GH_Path(0)
    for key in sorted(args.keys()): addInputParam(args[key], path)
    
    updateComponentDescription(xmlFile)
    
    # create an OSMeasure based on default values
    OSMeasure = OpenStudioMeasure(ghenv.Component.Name, ghenv.Component.NickName, ghenv.Component.Description, _OSMeasure, args)
    
    # add the measure to sticky to be able to load and update it
    key = ghenv.Component.InstanceGuid.ToString()
    if "osMeasures" not in sc.sticky.keys():
        sc.sticky["osMeasures"] = dict()
    
    sc.sticky["osMeasures"][key] = OSMeasure
    
    _OSMeasure = False
    
    # clean first input
    cleanFirstInput()
    
else:
    try:
        key = ghenv.Component.InstanceGuid.ToString()
        OSMeasure = sc.sticky["osMeasures"][key]
        OSMeasure.updateArguments()
        ghenv.Component.Name = OSMeasure.name
        ghenv.Component.NickName =  OSMeasure.nickName
        ghenv.Component.Description = OSMeasure.description
        pprint(OSMeasure.args)
    except Exception , e:
        print "Couldn't load the measure!"
        pass