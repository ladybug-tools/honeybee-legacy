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
Use this component to set the parameters of a HVAC ventilation system (or air side) that has been assigned with the "Honeybee_Assign HVAC System" component.
_
Not all of the inputs on this component are assignable features of all HVAC systems.  However, most HVAC systems have these features and, if you assign a parameter that is not usable by a certain HVAC system, the "Honeybee_Assign HVAC System" component will give you a warning to let you know.
-
Provided by Honeybee 0.0.60

    Args:
        _HVACAvailabiltySched_: A text string representing the HVAC availability that you want to use.  This can be either a shcedule from the schedule libirary or a CSV file path to a CSV schedule you created with the "Honeybee_Create CSV Schedule" component.
        _fanTotalEfficiency_: A number between 0 and 1 that represents the overall efficiency of the fan.  Specifically, this is the ratio between the power delivered to the air fluid and the electrical power intput to the fan. It is the product of the motor efficiency and the impeller efficiency.  The impeller efficiency is power delivered to the fluid (air) divided by the shaft power. The power delivered to the fluid is the mass flow rate of the air multiplied by the pressure rise divided by the air density.  The default is usually between 0.6 and 0.7.
        _fanMotorEfficiency_: A number between 0 and 1 that represents the efficiency of the fan electric motor.  The motor efficiency is the power delivered to the fan shaft divided by the electrical power input to the motor.  This value must be greater than the _fanTotalEfficiency_ above.  The default is usually around 0.9.
        _fanPressureRise_: A number representing the pressure rise across the fan in Pascals.  This is the pressure rise at full flow and standard (sea level) conditions (20C and 101325 Pa).  The default is usually around 500 Pa.
        _fanPlacement_: A boolean value that represents the placement of the fan in relation to cooling or heating coils.  The default is set to True to draw through.  Choose from the following options:
            True = Draw Through (the fan comes after the coils such that air is drawn by the fan across the heating/cooling coils).
            False = Blow Through (the fan comes before the coils such that air is blown through the heating/cooling coils).
        airSystemHardSize_: A number that represents airflow in m3/s and sets the maximum air flow through the HVAC air system including the fan and ducts.  This overrides the default autosizing of the air system is useful for evaluating strategies like larger ducts to minimize friction and decrease fan energy use.  It's particularly useful in cases of vetilation-dominated spaces like labs and hospital patient rooms.
        demandControlledVent_: A boolean value that represents whether system can vary its speed and the volume of air to match occupancy.  The default is False for all systems.  Choose from the following options:
            True = Demand Controlled Varialbe Minimum Air (the system can vary the volume of air to match occupancy).
            False = Constant Volume Minimum Air (the fan has only one miniumum flow rate when it is on).
        _heatingSupplyAirTemp_: A number representing the target temperature of the supply air when the system is in heating mode.  For large systems, this is the rated outlet air temperature of the heating coil.  Default for a VAV system is 35C. Default for ideal air is 40 C.
        _coolingSupplyAirTemp_: A number representing the target temperature of the supply air when the system is in cooling mode.  For large systems, this is the rated outlet air temperature of the cooling coil.  Default is typically around 12C, which is the coldest temperature before supply air can cause clear thermal discomfort issues. Default for ideal air is 13 C.
        airsideEconomizer_: An integer or boolean value (0/1) that sets the economizer on the HVAC system.  The default is set to "True" or "1" to include a Differential Dry Bulb air side economizer or "2" for a Differential Enthalpy economizer if the zone has humidity control.  Choose from the following options:
            0 - No Economizer - The HVAC system will constantly provide the same amount of minimum outdoor air and may run the cooling system to remove heat and meet thermostat setpoints.
            1 - Differential Dry Bulb - The HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air temperature is below the temperature of the return (or exhaust) air. 
            2 - Differential Enthalpy - The HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air enthalpy is below that of the return (or exhaust) air.
            3 - Fixed Dry Bulb - The HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air temperature is below a specified dry bulb temperature limit (default is 28C).
            4 - Fixed Enthalpy - The HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air enthalpy is below a specified enthalpy limit (default is 64000 J/kg).
            5 - Electronic Enthalpy - The HVAC system will calculate the humidity ratio limit of the outdoor air based on the dry-bulb temperature of outdoor air and a quadratic/cubic curve, and compare it to the actual outdoor air humidity ratio. If the actual outdoor humidity ratio is lower than the calculated humidity ratio limit and there is cooling load, then the outdoor airflow rate is increased.
            6 - Fixed Dew Point and Dry Bulb - The HVAC system will compare both the outdoor dewpoint temperature and the outdoor dry-bulb temperature to their specified high limit values (default of 28C).  The outdoor air flow rate will be increased when there is cooling load and the outdoor air is below both thresholds.
            7 - Differential Dry Bulb And Enthalpy - The HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air temperature is below a specified dry bulb temperature limit (default is 28C) AND enthalpy below a specified enthalpy limit (default is 64000 J/kg).
        heatRecovery_: An integer or boolean value (0/1) that sets the heat recovery on the HVAC system.  The default is set to "False" or 0 to NOT include heat recovery.  Choose from the following options:
             0 - None (The HVAC system will simply exhaust air without having it interact with incoming air).
             1 - Sensible (The HVAC system will pass the exhaust air through a sensible heat exchanger with the fresh outdoor air before exhausting it, helping recover heat that would normally be lost through the exhaust).
             2 - Enthalpy (The HVAC system will pass the exhaust air through a sensible and latent heat exchanger with the fresh outdoor air before exhausting it).
        recoveryEffectiveness_: If the above input has been set to "True", input a number between 0 and 1 here to set the fraction of heat that is recovered by the heat recovery system.  By default, this value is typically around 0.7.
    Returns:
        airDetails: A description of the HVAC ventilation system (or system air side), which can be plugged into "Honeybee_HVAC Systems" component.
"""


ghenv.Component.Name = "Honeybee_HVAC Air Details"
ghenv.Component.NickName = 'AirDetails'
ghenv.Component.Message = 'VER 0.0.60\nDEC_05_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nJUL_25_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

w = gh.GH_RuntimeMessageLevel.Warning

def main(hb_airDetail):
    myAirDetails = hb_airDetail(_HVACAvailabiltySched_, _fanTotalEfficiency_, _fanMotorEfficiency_, \
    _fanPressureRise_, _fanPlacement_, airSystemHardSize_, demandControlledVent_, _heatingSupplyAirTemp_, _coolingSupplyAirTemp_, \
    airsideEconomizer_, heatRecovery_, recoveryEffectiveness_)
    
    success, airDetails = myAirDetails.class2Str()
    if success:
        return airDetails
    else:
        for error in airDetails:
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
        hb_airDetail = sc.sticky["honeybee_hvacAirDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck:
    airDetails = main(hb_airDetail)