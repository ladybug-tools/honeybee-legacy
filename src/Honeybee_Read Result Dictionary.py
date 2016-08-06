#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component parses an .rdd file from an energy simulation to show all possible outputs that could be requested.
-
Provided by Honeybee 0.0.59
    
    Args:
        _rddFile: The file address of the rdd file that comes out of the "Honeybee_Lookup EnergyPlus Folder" component.
        timestep_: Specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annual'.  The default is set to hourly.
    Returns:
        simOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "Honeybee_Export to OpenStudio" component.
"""

ghenv.Component.Name = "Honeybee_Read Result Dictionary"
ghenv.Component.NickName = 'readRDD'
ghenv.Component.Message = 'VER 0.0.59\nAUG_06_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nMAY_02_2015
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import Grasshopper.Kernel as gh
import scriptcontext as sc
import os



#Check to be sure that the files exist and the timestep is valid
initCheck = False
if _rddFile and _rddFile != None:
    initCheck = True
    if not os.path.isfile(_rddFile):
        initCheck = False
        warning = 'The .rdd file does not exist.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
try:
    if timestep_.lower() == "monthly" or timestep_.lower() == "hourly" or timestep_.lower() == "daily" or timestep_.lower() == "annual" or timestep_.lower() == "timestep": pass
except:
    if timestep_ == None: timestep_ = "hourly"
    else:
        initCheck =False
        print "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual.")


simOutputs = []
if _rddFile and initCheck == True:
    try:
        result = open(_rddFile, 'r')
        for line in result:
            if not line.startswith('!'):
                simOutputs.append(line.replace("hourly",timestep_).replace('\n',''))
    except:
        warning = 'Fauled to parse .rdd file.  Make sure that it is the correct type of file.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


