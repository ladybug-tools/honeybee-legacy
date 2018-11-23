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
Use this component to edit the airflow between your zones's air walls and/or set natural ventilation.  The natural ventilation that this component models is mostly meant for single zones and cases where there is not much airflow between zones. Specifically, this component can model a few common types of natural ventilation:
    1 - Single-sided Ventilation - ventilation driven by the height difference across individual windows on a single side of a building.
    2 - Cross Ventilation - ventilation driven by the pressure difference across windows on two opposite sides of a building.
    3 - Chimney Ventilation - ventilation driven by a chimney/stack that is attached to a zone.
    4 - Cowl Ventilation - ventilation driven by wind through a cowl attached to a zone.
    5 - Fan-driven Ventilation - ventilation at a constant flow rate driven by a fan.
_
The component can model "multi-zone" natural ventilation so long as there are no major vertical differences in height over multiple zones and the user understands that "mixing objects" of constant air flow are used to dsitribute incoming air between zones that are connected by an air wall.  As such, this method is not meant to model atriums or any method relying on inter-zone buoyancy-driven flow.
_
Natural ventilation (that i nt fan-driven) is computed using the following formulas:
Ventilation Wind = Wind Coefficient * Opening Area * Schedule * WindSpd 
Ventilation Stack = Stack Discharge Coefficient * Opening Area * Schedule * SQRT(2 * Gravity * Operable Height * (|(Temp Zone - Temp Outdoors)| / Temp Zone)) 
Total Ventilation = SQRT((Ventilation Wind)^2 + (Ventilation Stack)^2)
-
Provided by Honeybee 0.0.64

    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.
        interZoneAirFlowRate_: An optional number that represents airflow in m3/s per square meter of air wall contatct surface area between zones.  By default, this value is set to 0.0963 m3/s for each square meter of air wall contact surface area, which is an assumption derived from the relatively low air velocities induced by typical HVAC systems.  In cases of higher indoor air velocity, such as those that might occur with consistent wind-driven ventilation or ventilation with fans, you will likely want to increase this number. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        interZoneAirFlowSched_: An optional schedule of fractional values to set when the air flows in between zones.  Use this option if your air walls represent operable partitions like doors.
        _naturalVentilationType: Choose from the following options:
            0 - NO NATURAL VENTILATION - Choose this option if you do not want to add any natrual ventilation objects to your zones with this component.
            1 - WINDOW NATURAL VENTILATION - Choose this to have the component automatically calculate natural ventilation airflow based on ALL of your zone's exterior windows, a specified fraction of operable glazing, and a specified fraction of the glazing height that is operable.  It will be assumed that each window has a single opening, that this window opening is sliding, and that the difference in the heights between the different windows is not great enough to induce bouyancy driven flow from one window to another. The default assumes an opening that extends the full window height with half of the total glazing area operable (a horizontal sliding window).  The default also assumes the presence of insect screens (discharge doefficient of 0.17).  Finally, the default negates wind-driven cross ventilation but this option should be set to True if there is roughly equal opeerable area on both sides of the zone or there is some other (non-window) opening in the zone.
            2 - CUSTOM STACK / WIND VENTILATION - Choose this option if you have window ventilation that does not fit the description above or if you are trying to model an object like a chimney or a cowl.  You will have to specify an effective window area for the object and the height between inlet and outlet. Note that you can eliminate either the wind or the stack part of the equation by setting the respective discharge coefficent to 0.
            3 - FAN-DRIVEN VENTILATION - Choose this option to have your zones ventilated at a constant volume flow rate, representing fan-driven ventilation.  You will have to specify the design flow rate in m3/s.  You can also change the default fan efficiency, which will affect the electic consumption of the fan in the output.
        minIndoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the minimum indoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxIndoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the maximum indoor temperature at which to naturally ventilate.  Use this to design mixed-mode buildings where you would like occupants to shut the windows and turn on a cooling system if it gets too hot inside.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        minOutdoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the minimum outdoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxOutdoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the maximum outdoor temperature at which to naturally ventilate.  Use this to design night flushed buildings where windows are closed for daytime temperatures and opened at cooler night time temperatures. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        deltaTempForNatVent_: A number or list of numbers between -100 and 100 that represents the temperature differential between indoor and outdoor below which ventilation is shutoff.  This should usually be a negative number so that you open the windows when the outdoors is cooler than the indoors. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        openingAreaFractionalSched_: An optional schedule to set the fraction of the window that is open at each hour.
        fractionOfGlzAreaOperable_: A number or list of numbers between 0.0 and 1.0 that represents the fraction of the window area that is operable.  By default, it will be assumed that this is 0.5 assuming sliding windows that slide horizontally.
        fractionOfGlzHeightOperable_: A number or list of numbers between 0.0 and 1.0 that represents the fraction of the distance from the bottom of the zones windows to the top that are operable.  By default, it will be assumed that this is 1.0 assuming sliding windows that slide horizontally.
        windDrivenCrossVent_: Set to "True" if there is operable area of roughly equal area on different sides of the zone such that wind-driven cross ventilation will be induced.  Set to "False" if the operable area is primarily on one side of the zone and there is no wind-driven ventilation.  The default will examine the difference in directions that the zone's windows are facing and, if this maximum difference is greater than 90 degrees, cross ventilation will be turned on.  This input overrides this default.
        stackDischargeCoeff_: A number between 0.0 and 1.0 that will be multipled by the area of the window to account for additional friction from window geometry, insect screens, etc.  This is the 'Stack Discharge Coefficient' variable in the equation of this component's description.  If left blank, this variable will be assumed to be 0.17 for single-sided ventilation with sliding windows and insect screens.  This value should be changed if windows are awning or casement. Some common values for this coefficient include the following:
            0.0 - Completely discounts stack ventilation from the natural ventilation calculation and only accounts for wind.
            0.17 - For buoyancy with ONE opening WITH an insect screen. In this case, the effective area should be the whole opening.
            0.25 - For buoyancy with ONE opening with NO insect screen. In this case, the effective area should be the whole opening.
            0.45 - For buoyancy with TWO openings of different heights, each of which HAVE insect screens. In this case, the effective area should be just the area of ONE of the two window openings (if opening areas are equal).
            0.65 - For buoyancy with TWO openings of different heights, each of which have NO insect screens.  In this case, the effective area should be just the area of ONE of the two window openings (if opening areas are equal).
        _windowAngle2North: A number between 0 and 360 that sets the angle in degrees counting from the North clockwise to the opening direction.  The Effective Angle is 0 if the opening outward normal faces North, 90 if faces East, 180 if faces South, and 270 if faces West.
    Returns:
        readMe:...
        HBZones: HBZones with their airflow modified.
"""

ghenv.Component.Name = "Honeybee_Set EP Air Flow"
ghenv.Component.NickName = 'setEPNatVent'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nDEC_15_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os
import Rhino as rc
import math

w = gh.GH_RuntimeMessageLevel.Warning

inputsDict = {
    
0: ["_HBZones", "The HBZones out of any of the HB components that generate or alter zones."],
1: ["interZoneAirFlowRate_", "An optional number that represents airflow in m3/s per square meter of air wall contatct surface area between zones.  By default, this value is set to 0.0963 m3/s for each square meter of air wall contact surface area, which is a decent assumption for conditions of relatively low indoor air velocity.  In cases of higher indoor air velocity, such as those that might occur with consistent wind-driven ventilation or ventilation with fans, you will likely want to increase this number. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
2: ["interZoneAirFlowSched_", "An optional schedule of fractional values to set when the air flows in between zones."],
3: ["_naturalVentilationType", "Choose from the following options:\n     0 - NO NATURAL VENTILATION - Choose this option if you do not want to add any natrual ventilation objects to your zones with this component.\n     1 - WINDOW NATURAL VENTILATION - Choose this to have the component automatically calculate natural ventilation airflow based on ALL of your zone's exterior windows, a specified fraction of operable glazing, and a specified fraction of the glazing height that is operable.  It will be assumed that each window has a single opening, that this window opening is sliding, and that the difference in the heights between the different windows is not great enough to induce bouyancy driven flow from one window to another. The default assumes an opening that extends the full window height with half of the total glazing area operable (a horizontal sliding window).  The default also assumes the presence of insect screens (discharge doefficient of 0.17).  Finally, the default negates wind-driven cross ventilation but this option should be set to True if there is roughly equal opeerable area on both sides of the zone or there is some other (non-window) opening in the zone.\n     2 - CUSTOM STACK / WIND VENTILATION - Choose this option if you have window ventilation that does not fit the description above or if you are trying to model an object like a chimney or a cowl.  You will have to specify an effective window area for the object and the height between inlet and outlet. Note that you can eliminate either the wind or the stack part of the equation by setting the respective discharge coefficent to 0.\n     3 - FAN-DRIVEN VENTILATION - Choose this option to have your zones ventilated at a constant volume flow rate, representing fan-driven ventilation.  You will have to specify the design flow rate in m3/s.  You can also change the default fan efficiency, which will affect the electic consumption of the fan in the output."],
4: ["minIndoorTempForNatVent_", "A number or list of numbers between -100 and 100 that represents the minimum indoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
5: ["maxIndoorTempForNatVent_", "A number or list of numbers between -100 and 100 that represents the maximum indoor temperature at which to naturally ventilate.  Use this to design mixed-mode buildings where you would like occupants to shut the windows and turn on a cooling system if it gets too hot inside.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
6: ["minOutdoorTempForNatVent_", "A number or list of numbers between -100 and 100 that represents the minimum outdoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
7: ["maxOutdoorTempForNatVent_", "A number or list of numbers between -100 and 100 that represents the minimum outdoor temperature at which to naturally ventilate.  Use this to design night flushed buildings where windows are closed for daytime temperatures and opened at night or a mixed-mode buildings where you would like occupants to shut the windows and turn on a cooling system if it gets too hot outside. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
8: ["deltaTempForNatVent_", "A number or list of numbers between -100 and 100 that represents the temperature differential between indoor and outdoor below which ventilation is shutoff.  This should usually be a negative number so that you open the windows when the outdoors is cooler than the indoors. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone."],
9: ["openingAreaFractionalSched_", "An optional schedule to set the fraction of the window that is open at each hour."],
10: ["fractionOfGlzAreaOperable_", "A number or list of numbers between 0.0 and 1.0 that represents the fraction of the window area that is operable.  By default, it will be assumed that this is 0.5 assuming sliding windows that slide horizontally."],
11: ["fractionOfGlzHeightOperable_", "A number or list of numbers between 0.0 and 1.0 that represents the fraction of the distance from the bottom of the zones windows to the top that are operable.  By default, it will be assumed that this is 1.0 assuming sliding windows that slide horizontally."],
12: ["windDrivenCrossVent_", "Set to 'True' if there is operable area of roughly equal area on different sides of the zone such that wind-driven cross ventilation will be induced.  Set to 'False' if the operable area is primarily on one side of the zone and there is no wind-driven ventilation.  The default will examine the difference in directions that the zone's windows are facing and, if this maximum difference is greater than 90 degrees, cross ventilation will be turned on.  This input overrides this default."],
13: ["stackDischargeCoeff_", "A number between 0.0 and 1.0 that will be multipled by the area of the window to account for additional friction from window geometry, insect screens, etc.  This is the 'Stack Discharge Coefficient' variable in the equation of this component's description.  If left blank, this variable will be assumed to be 0.17 for single-sided ventilation with sliding windows and insect screens.  This value should be changed if windows are awning or casement. Some common values for this coefficient include the following:\n     0.0 - Completely discounts stack ventilation from the natural ventilation calculation.\n     0.17 - For buoyancy with ONE opening WITH an insect screen. In this case, the effective area should be the whole opening.\n     0.25 - For buoyancy with ONE opening with NO insect screen. In this case, the effective area should be the whole opening.\n     0.45 - For buoyancy with TWO openings of different heights, each of which HAVE insect screens. In this case, the effective area should be just the area of ONE of the two window openings (if opening areas are equal).\n     0.65 - For buoyancy with TWO openings of different heights, each of which have NO insect screens.  In this case, the effective area should be just the area of ONE of the two window openings (if opening areas are equal)."],
14: ["_windowAngle2North", "A number between 0 and 360 that sets the angle in degrees from North counting clockwise to the direction the window faces.  An angle of 0 denotes that the opening faces North, 90 denotes East, 180 denotes South, and 270 denotes West."]
}


def checkNatVentMethod():
    #Check to make sure that the nat vent method is valid.
    if _naturalVentilationType >= -1 and _naturalVentilationType <= 3: natVentMethod = _naturalVentilationType
    else:
        natVentMethod = None
        warning = "_naturalVentilationType is not valid."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if natVentMethod == 0:
        for input in range(15):
            if input == 4 or input == 5 or input == 6 or input == 7 or input == 8 or input == 9 or input == 10 or input == 11 or input == 12 or input == 13 or input == 14:
                ghenv.Component.Params.Input[input].NickName = "__________"
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    elif natVentMethod == 1:
        for input in range(15):
            if input == 14:
                ghenv.Component.Params.Input[input].NickName = "__________"
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    elif natVentMethod == 2:
        for input in range(15):
            if input == 10:
                ghenv.Component.Params.Input[input].NickName = "_operableEffectiveArea"
                ghenv.Component.Params.Input[input].Name = "_operableEffectiveArea"
                ghenv.Component.Params.Input[input].Description = "A number representing the effective area of operable ventilation in square meters.  Note that effective area references both inlet and outlet area through the following formula: EffectiveArea = 1 / sqrt( (1/InletArea^2) + 1/OutletArea^2) ). This value will be decreased if there is further friction introduced by objects in between the inlet and outlet."
            elif input == 11:
                ghenv.Component.Params.Input[input].NickName = "_inletOutletHeight"
                ghenv.Component.Params.Input[input].Name = "_inletOutletHeight"
                ghenv.Component.Params.Input[input].Description = "A number representing the height between the midplanes of the inlet and outlet of the custom ventilation object in meters.  This is needed for the buoyancy calculation."
            elif input == 12:
                ghenv.Component.Params.Input[input].NickName = "windCoefficient_"
                ghenv.Component.Params.Input[input].Name = "windCoefficient_"
                ghenv.Component.Params.Input[input].Description = "A number between 0.0 and 1.0 that will be multipled by the area of the window to account for the angle of the wind from the direction that the window faces.  This is the 'Wind Coefficient' variable in the equation given in this component's description.  If no value is input here, it is autocalculated based on the angle of the cardinal direction from North and the hourly wind direction.  Set to 0 to completely discount wind from the natural ventilation calculation."
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    elif natVentMethod == 3:
        for input in range(15):
            if input == 13 or input == 14:
                ghenv.Component.Params.Input[input].NickName = "__________"
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            elif input == 10:
                ghenv.Component.Params.Input[input].NickName = "_fanFlowRate"
                ghenv.Component.Params.Input[input].Name = "_fanFlowRate"
                ghenv.Component.Params.Input[input].Description = "A number representing the flow rate of the fan in m3/s.  The flow rate of the fan will depend upon its size and can range from 0.05 m3/s for a small desk fan to 6.00 m3/s for a large industrial fan."
            elif input == 11:
                ghenv.Component.Params.Input[input].NickName = "fanEfficiency_"
                ghenv.Component.Params.Input[input].Name = "fanEfficiency_"
                ghenv.Component.Params.Input[input].Description = "A number between 0 and 1 that represents the efficiency of the fan.  It is the ratio of the power delivered to the fluid to the electrical input power. It is the product of the motor efficiency and the impeller efficiency.  The default is set to 0.7 but this can be lower for smaller fans and higher for industrial grade fans."
            elif input == 12:
                ghenv.Component.Params.Input[input].NickName = "fanPressureRise_"
                ghenv.Component.Params.Input[input].Name = "fanPressureRise_"
                ghenv.Component.Params.Input[input].Description = "A number that represents the fan pressure rise in Pa.  This will effect the energy use of the fan in the results.  The default is set to 70 for a relatively small fan with a flow rate of 0.05 m3/s but values can be as high as 400 Pa for large industrial fans."
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    return natVentMethod

def restoreInput():
    for input in range(15):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

def setDefaults(natVentMethod):
    #HAve a function to duplicate data.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #Have a function to check the ranges of a list.
    def checkRange(values, lowerBound, upperBound):
        checkAllRanges = True
        for item in values:
            if item < lowerBound or item > upperBound: checkAllRanges = False
        if checkAllRanges == False:
            warning = "One of the connected values is not in the acceptable range."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        return checkAllRanges
    
    #Have a function to check that a list matches the length of HBZones.
    def checkWithHBZone(listOfValues, name):
        checkListLen = True
        if len(listOfValues) > 1:
            if len(listOfValues) == len(_HBZones): goodData = listOfValues
            else:
                checkListLen = False
                warning = "The length of the " + name + " list does not match the number of _HBZones."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        elif len(listOfValues) == 1:
            goodData = duplicateData(listOfValues, len(_HBZones))
        else: goodData = []
        
        return checkListLen, goodData
    
    #Check to make sure that everything matches with the HBZones.
    checkData14, interZoneFlow = checkWithHBZone(interZoneAirFlowRate_, "interZoneAirFlowRate_")
    checkData26, interZoneFlowSched = checkWithHBZone(interZoneAirFlowSched_, "interZoneAirFlowSched_")
    
    #Check if the general inputs for natural ventilation match.
    if natVentMethod == 1 or natVentMethod == 2 or natVentMethod == 3:
        try:
            checkData1, minIndoorTemp = checkWithHBZone(minIndoorTempForNatVent_, "minIndoorTempForNatVent_")
            checkData2, maxIndoorTemp = checkWithHBZone(maxIndoorTempForNatVent_, "maxIndoorTempForNatVent_")
            checkData3, minOutdoorTemp = checkWithHBZone(minOutdoorTempForNatVent_, "minOutdoorTempForNatVent_")
            checkData4, maxOutdoorTemp = checkWithHBZone(maxOutdoorTempForNatVent_, "maxOutdoorTempForNatVent_")
            checkData27, deltaTemp = checkWithHBZone(deltaTempForNatVent_, "deltaTempForNatVent_")
            checkData7,areaSched = checkWithHBZone(openingAreaFractionalSched_, "openingAreaFractionalSched_")
            checkData8 = checkRange(minIndoorTemp, -100, 100)
            checkData9 = checkRange(maxIndoorTemp, -100, 100)
            checkData10 = checkRange(minOutdoorTemp, -100, 100)
            checkData11 = checkRange(maxOutdoorTemp, -100, 100)
            checkData28 = checkRange(deltaTemp, -100, 100)
        except:
            checkData1, minIndoorTemp = False, None
            checkData2, maxIndoorTemp = False, None
            checkData3, minOutdoorTemp = False, None
            checkData4, maxOutdoorTemp = False, None
            checkData27, deltaTemp = False, None
            checkData7, areaSched = False, None
            checkData8 = False
            checkData9 = False
            checkData10 = False
            checkData11 = False
            checkData28 = False
    else:
        checkData1, minIndoorTemp = True, None
        checkData2, maxIndoorTemp = True, None
        checkData3, minOutdoorTemp = True, None
        checkData4, maxOutdoorTemp = True, None
        checkData27, deltaTemp = True, None
        checkData7, areaSched = True, None
        checkData8 = True
        checkData9 = True
        checkData10 = True
        checkData11 = True
        checkData28 = True
    
    #Check the inputs related to window-driven or custom wind/stack ventilation.
    checkData17 = True
    checkData18 = True
    if natVentMethod == 1:
        try:
            windDisCoeff = windDrivenCrossVent_
            stackDisCoeff = stackDischargeCoeff_
            if windDisCoeff != None:
                checkData17 = checkRange([windDisCoeff], 0, 1)
            if stackDisCoeff != None:
                checkData18 = checkRange([stackDisCoeff], 0, 1)
        except:
            windDisCoeff = None
            stackDisCoeff = None
            checkData17 = False
            checkData18 = False
    elif natVentMethod == 2:
        try:
            windDisCoeff = windCoefficient_
            stackDisCoeff = stackDischargeCoeff_
            if windDisCoeff != None:
                checkData17 = checkRange([windDisCoeff], 0, 1)
            if stackDisCoeff != None:
                checkData18 = checkRange([stackDisCoeff], 0, 1)
        except:
            windDisCoeff = None
            stackDisCoeff = None
            checkData17 = False
            checkData18 = False
    else:
        windDisCoeff = None
        stackDisCoeff = None
        checkData17 = True
        checkData18 = True
    
    #Check the inputs related to window-driven ventilation.
    if natVentMethod == 1:
        try:
            checkData5, fractionOfArea = checkWithHBZone(fractionOfGlzAreaOperable_, "fractionOfGlzAreaOperable_")
            checkData6, fractionOfHeight = checkWithHBZone(fractionOfGlzHeightOperable_, "fractionOfGlzHeightOperable_")
            checkData12 = checkRange(fractionOfArea, 0, 1)
            checkData13 = checkRange(fractionOfHeight, 0, 1)
        except:
            checkData5, fractionOfArea = False, None
            checkData6, fractionOfHeight = False, None
            checkData12 = False
            checkData13 = False
    else:
        checkData5, fractionOfArea = True, None
        checkData6, fractionOfHeight = True, None
        checkData12 = True
        checkData13 = True
    
    #Check the inputs related to custom wind/stack ventilation.
    if natVentMethod == 2:
        try:
            if len(_operableEffectiveArea) > 0: checkData19, effectiveArea = checkWithHBZone(_operableEffectiveArea, "_operableEffectiveArea")
            else:checkData19, effectiveArea = False, None
            if len(_inletOutletHeight) > 0: checkData20, inletOutletHeight = checkWithHBZone(_inletOutletHeight, "_inletOutletHeight")
            else: checkData20, inletOutletHeight = False, None
            if len(_windowAngle2North) > 0: checkData25, windowAngle2North = checkWithHBZone(_windowAngle2North, "_windowAngle2North")
            else:
                if sum(windDisCoeff) == 0:
                    checkData25, windowAngle2North = True, range(len(_HBZones))
                else:
                    checkData25, windowAngle2North = False, None
                    print "Connect an input for '_windowAngle2North."
        except:
            checkData19, effectiveArea = False, None
            checkData20, inletOutletHeight = False, None
            checkData25, windowAngle2North = False, None
    else:
        checkData19, effectiveArea = True, None
        checkData20, inletOutletHeight = True, None
        checkData25, windowAngle2North = True, None
    
    #Check the inputs related to custom fan-driven ventilation.
    if natVentMethod == 3:
        try:
            if len(_fanFlowRate) > 0: checkData21, fanFlowRate = checkWithHBZone(_fanFlowRate, "_fanFlowRate")
            else: checkData21, fanFlowRate = False, None
            checkData22, fanEfficiency = checkWithHBZone(fanEfficiency_, "fanEfficiency_")
            checkData23 = checkRange(fanEfficiency, 0, 1)
            fanPressureRise = fanPressureRise_
        except:
            checkData21, fanFlowRate = False, None
            checkData22, fanEfficiency = False, None
            checkData23 = False
            fanPressureRise = None
    else:
        checkData21, fanFlowRate = True, None
        checkData22, fanEfficiency = True, None
        checkData23 = True
        fanPressureRise = None
    
    #Check to be sure all is ok.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True and checkData14 == True and checkData17 == True and checkData18 == True and checkData19 == True and checkData20 == True and checkData21 == True and checkData22 == True and checkData23 == True and checkData25 == True and checkData26 == True and checkData27 == True and checkData28 == True:
        checkData = True
    
    return checkData, interZoneFlow, interZoneFlowSched, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, deltaTemp, windDisCoeff, stackDisCoeff, fractionOfArea, fractionOfHeight, areaSched, effectiveArea, inletOutletHeight, fanFlowRate, fanEfficiency, fanPressureRise, windowAngle2North

def main(HBZones, natVentMethod, interZoneFlow, interZoneFlowSched, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, deltaTemp, windDisCoeff, stackDisCoeff, fractionOfArea, fractionOfHeight, areaSched, effectiveAreas, inletOutletHeight, fanFlowRate, fanEfficiency, fanPressureRise, windowAngle2North):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
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
    
    readMe = []
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    #If the user requests a change in inter-zone mixing, then do so.
    if len(interZoneFlow) > 0:
        for zoneCount, HBZone in enumerate(HBObjectsFromHive):
            originalFlow = [HBZone.mixAirFlowRate][:][0]
            newFlow = interZoneFlow[zoneCount]
            originNewRatio = newFlow/originalFlow
            if HBZone.mixAir == True:
                for flowCount, flowRate in enumerate(HBZone.mixAirFlowList):
                    readMe.append("Mixing flow rate between " + HBZone.name + " and " + HBZone.mixAirZoneList[flowCount] + " has been changed from " + str(flowRate) + " to " + str(flowRate*originNewRatio) + ".")
                    HBZone.mixAirFlowList[flowCount] = flowRate*originNewRatio
            HBZone.mixAirFlowRate = newFlow
    
    #If the user requests a change in inter-zone mixing schedule, then do so.
    if len(interZoneFlowSched) > 0:
        # Make sure zoneMixing schedules are in HB schedule library.
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        
        for schedule in interZoneFlowSched: 
            if schedule!=None:
                schedule= schedule.upper()
            
            if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
                msg = "Cannot find " + schedule + " in Honeybee schedule library."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
            elif schedule!=None and schedule.lower().endswith(".csv"):
                # check if csv file exists
                if not os.path.isfile(schedule):
                    msg = "Cannot find the shchedule file: " + schedule
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
        
        #Assign the shcedules to the zones
        for zoneCount, HBZone in enumerate(HBObjectsFromHive):
            newFlowSched = interZoneFlowSched[zoneCount]
            if HBZone.mixAir == True:
                for flowCount, flowRate in enumerate(HBZone.mixAirFlowList):
                    try:
                        readMe.append("Mixing flow schedule between " + HBZone.name + " and " + HBZone.mixAirZoneList[flowCount] + " has been changed from " + str(HBZone.mixAirFlowSched[flowCount]) + " to " + str(newFlowSched) + ".")
                        HBZone.mixAirFlowSched[flowCount] = newFlowSched
                    except:
                        pass
    
    if natVentMethod == 1 or natVentMethod == 2 or natVentMethod == 3 or natVentMethod == 0:
        # make sure area schedules are in HB schedule library.
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        
        if natVentMethod == 1 or natVentMethod == 2 or natVentMethod == 3:
            for schedule in areaSched: 
                if schedule!=None:
                    schedule= schedule.upper()
                
                if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
                    msg = "Cannot find " + schedule + " in Honeybee schedule library."
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
                elif schedule!=None and schedule.lower().endswith(".csv"):
                    # check if csv file is existed
                    if not os.path.isfile(schedule):
                        msg = "Cannot find the shchedule file: " + schedule
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return -1
        
        if natVentMethod == 1:
            for zoneCount, HBZone in enumerate(HBObjectsFromHive):
                #Get the glazed surfaces of the zone.
                srfCount = 0
                windows = []
                northAngles = []
                for srf in HBZone.surfaces:
                    if srf.type == 0:
                        if srf.BC.upper() == "OUTDOORS":
                            if srf.hasChild:
                                windows.append([])
                                if srf.angle2North == 0: northAngles.append(srf.angle2North)
                                else: northAngles.append(360 - srf.angle2North)
                                for childSrf in srf.childSrfs:
                                    windows[srfCount].append(childSrf.geometry)
                                srfCount += 1
                
                if len(windows) != 0:
                    HBZone.natVent = True
                    
                    #Calculate the total glazed area of the zone.
                    glazedAreas = []
                    for windowsList in windows:
                        glazedArea = 0.0
                        for srf in windowsList:
                            glazedArea = glazedArea + (rc.Geometry.AreaMassProperties.Compute(srf).Area*sc.sticky["honeybee_ConversionFactor"]*sc.sticky["honeybee_ConversionFactor"])
                        glazedAreas.append(glazedArea)
                    
                    #Calculate the height difference of the glazing across the surface.
                    glzHeights = []
                    for windowsList in windows:
                        fullWindowBrep = rc.Geometry.Brep()
                        for brep in windowsList:
                            rc.Geometry.Brep.Append(fullWindowBrep, brep)
                        glzBB = rc.Geometry.Brep.GetBoundingBox(fullWindowBrep, rc.Geometry.Plane.WorldXY)
                        glzHeight = glzBB.Max.Z - glzBB.Min.Z
                        glzHeights.append(glzHeight)
                    
                    #Assign the opening area and height to the zone.
                    for glzCount, glazedArea in enumerate(glazedAreas):
                        #Assign the natural ventilation type.
                        HBZone.natVentType.append(1)
                        
                        #Assign the operable area.
                        if fractionOfArea == []: fractArea = 0.5
                        else: fractArea = fractionOfArea[zoneCount]
                        openingArea = fractArea*glazedArea
                        HBZone.windowOpeningArea.append(str(openingArea))
                        readMe.append(HBZone.name + " has surface with a glazed area of " + str(glazedArea) + " m2, has an operable area of " + str(openingArea) + " m2.")
                        
                        #Assign the heights of the windows.
                        if fractionOfHeight == []: fractHeight = 1
                        else: fractHeight = fractionOfHeight[zoneCount]
                        effectiveHeight = fractHeight*glzHeights[glzCount]
                        HBZone.windowHeightDiff.append(str(effectiveHeight))
                        readMe.append(HBZone.name + " has a glazed height of " + str(round(glzHeights[glzCount], 1)) + " m and " + str(round(effectiveHeight, 1)) + " m of it can be used for buoyancy-driven flow.")
                        
                        #Assign the angles to north of the windows.
                        HBZone.windowAngle.append(str(northAngles[glzCount]))
                        
                        #Assign wind cross-ventilation.
                        if windDisCoeff == None:
                            northAnglesCopy = northAngles[:]
                            northAnglesCopy.sort()
                            angRange = northAnglesCopy[-1] - northAnglesCopy[0]
                            if math.degrees(angRange) > 90:
                                windDis = "autocalculate"
                            else:
                                windDis = "0"
                        elif windDisCoeff == 1:
                            windDis = "autocalculate"
                        else:
                            windDis = "0"
                        HBZone.natVentWindDischarge.append(windDis)
                        
                        #Assign the stack discharge values.
                        if stackDisCoeff == None: stackDis = '0.17'
                        else: stackDis = str(stackDisCoeff)
                        HBZone.natVentStackDischarge.append(stackDis)
                        
                        #Assign the nat vent temperature limits.
                        if minIndoorTemp != []: HBZone.natVentMinIndoorTemp.append(minIndoorTemp[zoneCount])
                        else: HBZone.natVentMinIndoorTemp.append("-100")
                        if maxIndoorTemp != []: HBZone.natVentMaxIndoorTemp.append(maxIndoorTemp[zoneCount])
                        else: HBZone.natVentMaxIndoorTemp.append("100")
                        if minOutdoorTemp != []: HBZone.natVentMinOutdoorTemp.append(minOutdoorTemp[zoneCount])
                        else: HBZone.natVentMinOutdoorTemp.append("-100")
                        if maxOutdoorTemp != []: HBZone.natVentMaxOutdoorTemp.append(maxOutdoorTemp[zoneCount])
                        else: HBZone.natVentMaxOutdoorTemp.append("100")
                        if deltaTemp != []: HBZone.natVentDeltaTemp.append(deltaTemp[zoneCount])
                        else: HBZone.natVentDeltaTemp.append("-100")
                        
                        #Assign the nat vent schedule,
                        if areaSched != []:
                            HBZone.natVentSchedule.append(areaSched[zoneCount])
                        else: HBZone.natVentSchedule.append(None)
                        
                        #Assign a null value for the other nat vent lists to keep things consistent.
                        HBZone.fanFlow.append(None)
                        HBZone.FanEfficiency.append(None)
                        HBZone.FanPressure.append(None)
                else:
                    warning = "One of the connected HBZones does not have any windows and so natural ventilation will not be assigned."
                    readMe.append(warning)
        elif natVentMethod == 2:
            for zoneCount, HBZone in enumerate(HBObjectsFromHive):
                HBZone.natVent = True
                #Assign the natural ventilation type.
                HBZone.natVentType.append(2)
                
                #Assign the operable area.
                effectiveArea = effectiveAreas[zoneCount]
                HBZone.windowOpeningArea.append(str(effectiveArea))
                readMe.append(HBZone.name + " has an effective area of " + str(effectiveArea) + " m2.")
                
                #Assign the heights of the windows.
                effectiveHeight = inletOutletHeight[zoneCount]
                HBZone.windowHeightDiff.append(str(effectiveHeight))
                readMe.append(HBZone.name + " has a difference between inlet and outlet height of " + str(round(effectiveHeight, 1)) + " m.")
                
                #Assign the angles to north of the windows.
                HBZone.windowAngle.append(str(windowAngle2North[zoneCount]))
                
                #Assign the wind discharge values.
                if windDisCoeff == None: windDis = "autocalculate"
                else: windDis = str(windDisCoeff)
                HBZone.natVentWindDischarge.append(windDis)
                
                #Assign the wind discharge values.
                if stackDisCoeff == None: stackDis = "0.17"
                else: stackDis = str(stackDisCoeff)
                HBZone.natVentStackDischarge.append(stackDis)
                
                #Assign the nat vent temperature limits.
                if minIndoorTemp != []: HBZone.natVentMinIndoorTemp.append(minIndoorTemp[zoneCount])
                else: HBZone.natVentMinIndoorTemp.append("-100")
                if maxIndoorTemp != []: HBZone.natVentMaxIndoorTemp.append(maxIndoorTemp[zoneCount])
                else: HBZone.natVentMaxIndoorTemp.append("100")
                if minOutdoorTemp != []: HBZone.natVentMinOutdoorTemp.append(minOutdoorTemp[zoneCount])
                else: HBZone.natVentMinOutdoorTemp.append("-100")
                if maxOutdoorTemp != []: HBZone.natVentMaxOutdoorTemp.append(maxOutdoorTemp[zoneCount])
                else: HBZone.natVentMaxOutdoorTemp.append("100")
                if deltaTemp != []: HBZone.natVentDeltaTemp.append(deltaTemp[zoneCount])
                else: HBZone.natVentDeltaTemp.append("-100")
                
                #Assign the nat vent schedule,
                if areaSched != []:
                    HBZone.natVentSchedule.append(areaSched[zoneCount])
                else: HBZone.natVentSchedule.append(None)
                
                #Assign a null value for the other nat vent lists to keep things consistent.
                HBZone.fanFlow.append(None)
                HBZone.FanEfficiency.append(None)
                HBZone.FanPressure.append(None)
        elif natVentMethod == 3:
            for zoneCount, HBZone in enumerate(HBObjectsFromHive):
                HBZone.natVent = True
                #Assign the natural ventilation type.
                HBZone.natVentType.append(3)
                
                #Assign the fan flow per zone.
                HBZone.fanFlow.append(str(fanFlowRate[zoneCount]))
                readMe.append(HBZone.name + " has an outdoor fan flow rate of " + str(round(fanFlowRate[zoneCount], 1)) + " m3/s.")
                
                #Assign the fan efficiency.
                if fanEfficiency == []: fanEff = "0.7"
                else: fanEff = str(fanEfficiency[zoneCount])
                HBZone.FanEfficiency.append(fanEff)
                
                #Assign the fan pressure rise.
                if fanPressureRise == None: fanPress = "70"
                else: fanPress = str(fanPressureRise[zoneCount])
                HBZone.FanPressure.append(fanPress)
                
                #Assign the nat vent temperature limits.
                if minIndoorTemp != []: HBZone.natVentMinIndoorTemp.append(minIndoorTemp[zoneCount])
                else: HBZone.natVentMinIndoorTemp.append("-100")
                if maxIndoorTemp != []: HBZone.natVentMaxIndoorTemp.append(maxIndoorTemp[zoneCount])
                else: HBZone.natVentMaxIndoorTemp.append("100")
                if minOutdoorTemp != []: HBZone.natVentMinOutdoorTemp.append(minOutdoorTemp[zoneCount])
                else: HBZone.natVentMinOutdoorTemp.append("-100")
                if maxOutdoorTemp != []: HBZone.natVentMaxOutdoorTemp.append(maxOutdoorTemp[zoneCount])
                else: HBZone.natVentMaxOutdoorTemp.append("100")
                if deltaTemp != []: HBZone.natVentDeltaTemp.append(deltaTemp[zoneCount])
                else: HBZone.natVentDeltaTemp.append("-100")
                
                #Assign the nat vent schedule,
                if areaSched != []:
                    HBZone.natVentSchedule.append(areaSched[zoneCount])
                else: HBZone.natVentSchedule.append(None)
                
                #Assign a null value for the other nat vent lists to keep things consistent.
                HBZone.windowOpeningArea.append(None)
                HBZone.windowHeightDiff.append(None)
                HBZone.natVentWindDischarge.append(None)
                HBZone.natVentStackDischarge.append(None)
                HBZone.windowAngle.append(None)
    else:
        for zoneCount, HBZone in enumerate(HBObjectsFromHive):
            HBZone.natVent = False
            HBZone.natventType = []
            HBZone.natVentMinIndoorTemp = []
            HBZone.natVentMaxIndoorTemp = []
            HBZone.natVentMinOutdoorTemp = []
            HBZone.natVentMaxOutdoorTemp = []
            HBZone.natVentDeltaTemp = []
            HBZone.windowOpeningArea = []
            HBZone.windowHeightDiff = []
            HBZone.natVentSchedule = []
            HBZone.natVentWindDischarge = []
            HBZone.natVentStackDischarge = []
            HBZone.windowAngle = []
            HBZone.fanFlow = []
            HBZone.FanEfficiency = []
            HBZone.FanPressure = []
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
    
    return HBZones, readMe
    

checkData = False
if _HBZones and _HBZones[0]!=None and _naturalVentilationType != None:
    natVentMethod = checkNatVentMethod()
    
    if natVentMethod != None:
        checkData, interZoneFlow, interZoneFlowSched, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, deltaTemp, windDisCoeff, stackDisCoeff, fractionOfArea, fractionOfHeight, areaSched, effectiveArea, inletOutletHeight, fanFlowRate, fanEfficiency, fanPressureRise, windowAngle2North = setDefaults(natVentMethod)
        if checkData == True:
            results = main(_HBZones, natVentMethod, interZoneFlow, interZoneFlowSched, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, deltaTemp, windDisCoeff, stackDisCoeff, fractionOfArea, fractionOfHeight, areaSched, effectiveArea, inletOutletHeight, fanFlowRate, fanEfficiency, fanPressureRise, windowAngle2North)
            
            if results != -1: HBZones, readMe = results
else:
    restoreInput()