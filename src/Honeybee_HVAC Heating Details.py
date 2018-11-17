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
Use this component to set the parameters of a HVAC heating system that has been assigned with the "Honeybee_HVAC Systems" component.
_
Not all of the inputs on this component are assignable features of all HVAC systems.  However, most HVAC systems have these features and, if you assign a parameter that is not usable by a certain HVAC system, the "Honeybee_HVAC Systems" component will give you a warning to let you know.
-
Provided by Honeybee 0.0.64

    Args:
        _heatingAvailSched_: A text string representing the availability shcedule of the heating system.  This can be either a shcedule from the schedule libirary or a CSV file path to a CSV schedule you created with the "Honeybee_Create CSV Schedule" component.  The default is set to 'ALWAYS ON.'
        _heatingEffOrCOP_: A number that sets the reference efficiency of the primary heating component (under design-day conditions). For a system with a boiler, this is the fraction of energy contained within fuel that is converted into usable heat energy (default boiler efficiencies are typically between 0.7 and 0.9). For electric heat pump systems, this value is the coefficient of performance (COP) of the heat pump ot the ratio of heat added by the heat pump system per unit of electricity input. Defaults COPs typically range from 2 to 5 depending on the system type.
        supplyTemperature_: A number representing the temperature of the water leaving the boiler in degrees Celsius.  This input does not have an effect on direct expansion heat pump systems.  If left blank, the default temperature is usually 82.0 degrees Celsius.
        pumpMotorEfficiency_: A number between 0 and 1 that represents the motor efficiency of the hot water pump.  This input does not have an effect on direct expansion cooling systems.  If left blank, the defualt efficiency is usally 0.9.
        heatingHardSize_: A number in Watts that sets the maximum capacity of the heating system.  This will override the default, which is to autosize the heating system based on the design day.
        centralPlant_: Set to "True" to have all instances of this HVAC Type have a single central heating plant.  If set to False or left blank, each branch of a HBZone data tree that is plugged into this component will have a separate heating plant.
    Returns:
        heatingDetail: A description of the heating system features, which can be plugged into "Honeybee_HVAC Systems" component.
"""

import scriptcontext as sc
import Grasshopper.Kernel as gh


ghenv.Component.Name = "Honeybee_HVAC Heating Details"
ghenv.Component.NickName = 'HeatingDetails'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nJUL_17_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

w = gh.GH_RuntimeMessageLevel.Warning

def main(hb_heatingDetail):
    myHeatDetails = hb_heatingDetail(_heatingAvailSched_, _heatingEffOrCOP_, supplyTemperature_, \
    pumpMotorEfficiency_, heatingHardSize_, centralPlant_)
    
    success, heatDetails = myHeatDetails.class2Str()
    if success:
        return heatDetails
    else:
        for error in heatDetails:
            print error
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, error)
        return None


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
        hb_heatingDetail = sc.sticky["honeybee_hvacHeatingDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck:
    heatingDetails = main(hb_heatingDetail)

