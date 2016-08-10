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
Use this component to set the parameters of a HVAC cooling system that has been assigned with the "Honeybee_HVAC Systems" component.
_
Not all of the inputs on this component are assignable features of all HVAC systems.  However, most HVAC systems have these features and, if you assign a parameter that is not usable by a certain HVAC system, the "Honeybee_OpenStudio Systems" component will give you a warning to let you know.
-
Provided by Honeybee 0.0.60

    Args:
        _coolingAvailSched_: A text string representing the availability shcedule of the cooling system.  This can be either a shcedule from the schedule libirary or a CSV file path to a CSV schedule you created with the "Honeybee_Create CSV Schedule" component.  The default is set to 'ALWAYS ON.'
        _coolingCOP_ : A number (typically greater than 1) that sets the reference coefficient of performance (COP) of the primary cooling component (under design-day conditions). The COP is the ratio of heat removed by the cooling system per unit of electricity input.  For a large HVAC system, this input refers to the COP of the chiller compressor.  For a smaller system, this likely refers to the COP of the direct expansion cooling coil or equivalent.  Defaults range from 2 to 5.5 depending on the system type.
        supplyTemperature_: A number representing the temperature of the water leaving the chiller in degrees Celsius.  This input does not have an effect on direct expansion cooling systems.  If left blank, the default temperature is usually 6.67 degrees Celsius.
        pumpMotorEfficiency_: A number between 0 and 1 that represents the motor efficiency of the chilled water pump.  This input does not have an effect on direct expansion cooling systems.  If left blank, the defualt efficiency is usally 0.9.
        chillerType_: An integer or boolean (0/1) value that represents the type of chiller used.  This input does not have an effect on direct expansion cooling systems.  If left blank, the defualt efficiency is usally 0 = water cooled.  Choose from the following options:
            0 = Water Cooled - The chiller will be cooled using a condenser water loop with cooling tower and will use a higher default COP.
            1 = Air Cooled - The chiller will reject heat directly to the air and will have a lower default COP.
    Returns:
        coolingDetails: A description of the cooling system features, which can be plugged into "Honeybee_HVAC Systems" component.
"""

import scriptcontext as sc
import Grasshopper.Kernel as gh


ghenv.Component.Name = "Honeybee_HVAC Cooling Details"
ghenv.Component.NickName = 'CoolingDetails'
ghenv.Component.Message = 'VER 0.0.60\nAUG_10_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nMAY_09_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

w = gh.GH_RuntimeMessageLevel.Warning

def main(hb_coolingDetail):
    myCoolDetails = hb_coolingDetail(_coolingAvailSched_, _coolingCOP_, supplyTemperature_, \
    pumpMotorEfficiency_, chillerType_)
    
    success, coolDetails = myCoolDetails.class2Str()
    if success:
        return coolDetails
    else:
        for error in coolDetails:
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
        hb_coolingDetail = sc.sticky["honeybee_hvacCoolingDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck:
    coolingDetails = main(hb_coolingDetail)
