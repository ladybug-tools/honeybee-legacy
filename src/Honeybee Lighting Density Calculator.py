# Light Load Calculator
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Abraham Yezioro <ayez@ar.technion.ac.il> 
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
Use this component to calculate the Lighting Density Per Area Load from information about your bulb, fixture type, mainteneance, and required lighting level.
Plug the result to the Honeybee setEPZoneLoads component, lightingDensityPerArea_ input

-
Provided by Honeybee 0.0.63
    
    Args:
        _lightLevel: A number representing the required light level in the room in lux. For instance, 500 lux for a typical office area or 300 lux for a typical residential space. Note that a lux value input here means that light level is reached everywhere on the room floor plan.
        luminousEfficacy_: A value between 0 and 100 that represents how well a light source produces visible light in lumens/Watt. More specifically, it is the ratio of luminous flux (in Lumens) coming from a buld to electrical power (in Watts) going into the bulb. Here are some common options:
            92 = Fluorescent (T5 tube)
            81 = 8.7 W LED screw base lamp (120 V)
            80 = Fluorescent (T8 tube)
            52 = Compact Flourescent
            13.8 = Incandescent
            0.3 = Candle
            The default is set to 80 lm/W for Fluorescent (T8), which is also close to LED lamps.
            Sources - http://en.wikipedia.org/wiki/Luminous_efficacy, http://sustainabilityworkshop.autodesk.com/buildings/electric-light-sources
        maintenanceFactor_: A number between 0 and 1 that represents how often the lights are cleaned and replaced (higher numbers mean more often). It takes into account such factors as decreased efficiency with age, accumulation of dust within the fitting itself and the depreciation of reflectance as walls and reflecting surfaces age. 
        For convenience, it is usually given as three options:
            0.70 = Good
            0.65 = Medium
            0.55 = Poor
        The default is set to 0.65 for Medium.
        Source - http://sustainabilityworkshop.autodesk.com/buildings/light-fixtures-and-layout
        coefficientOfUtilization_: A number between 0 and 1 that represents the fraction of the lumens from the bulb that finally find their way to the work plane (higher values indicate a more efficient fixture). This number depends on the particular fixture type, the number of lamps in it, the lens used, its beam pattern, the shape of the room (Room Cavity Ratio, RCR) and the reflectances of the ceiling (Rc), walls (Rw) and floor (Rf).
        Here are some common Examples:
            0.84 = Basic Fluorescent Strip
            0.72 = Deep-Cell Parabolic Louver
            0.55 = Small-Cell Parabolic Louver
        The default is set to 0.84 for a Basic Fluorescent Strip
        Source - http://www.gelighting.com/LightingWeb/na/resources/tools/epact-estimator/popup-cu-ratings.jsp
    Returns:
        lightingDensityPerArea: (W/m2)The lighting load per square meter of floor, which can be plugged into the "Set EnergyPlus Loads" component.
"""
ghenv.Component.Name = "Honeybee Lighting Density Calculator"
ghenv.Component.NickName = 'Lighting Density Per Area Calculator'
ghenv.Component.Message = 'VER 0.0.63\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning

###################################


def checkInputs():
    checkData1 = False # Check Light level
    if _lightLevel:
        try:
            if _lightLevel > 0:
                checkData1 = True
            else:
                warning = "Give a positive value for Light Level."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        except: pass
        
    checkData2 = False # Check luminous Efficacy
    luminousEfficacy = None
    if luminousEfficacy_:
        try:
            if luminousEfficacy_ >= 0 and luminousEfficacy_ <= 100:
                checkData2 = True
                luminousEfficacy = luminousEfficacy_
            else:
                warning = "Invalid value for luminousEfficacy_."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        except: pass
    else:
        print "Luminous Efficacy set to 80 lumens/Watt for Flourescent (T8 tubes)."
        luminousEfficacy = 80
        checkData2 = True
        
    checkData3 = False # Check maintenance factor
    maintenanceFactor = None
    if maintenanceFactor_:
        try:
            if maintenanceFactor_ >= 0 and maintenanceFactor_ <= 1:
                checkData3 = True
                maintenanceFactor = maintenanceFactor_
            else:
                warning = "Invalid value for maintenanceFactor_."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        except: pass
    else:
        print 'Maintenance Coefficient set to 0.65 for Medium maintenance.'
        maintenanceFactor = 0.65
        checkData3 = True
        
    checkData4 = False # Check coefficient of utilization
    if coefficientOfUtilization_:
        try:
            if coefficientOfUtilization_ >= 0 and coefficientOfUtilization_ <= 1:
                checkData4 = True
                coefficientOfUtilization = coefficientOfUtilization_
            else:
                warning = "Invalid value for coefficientOfUtilization_."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        except: pass
    else:
        print 'Coefficient of Utilization set to 0.84 for a basic flourescent strip.'
        coefficientOfUtilization = 0.84
        checkData4 = True
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        checkData = True
    else:
        checkData = False
        msg = "Connect a desired lighting level."
    
    
    return checkData, luminousEfficacy, maintenanceFactor, coefficientOfUtilization

def main(lightLevel, luminousEfficacy, maintenanceFactor, coefficientOfUtilization):
    
    #Calculate Light Load (W/m2).
    efficiencyCoefficient = maintenanceFactor * coefficientOfUtilization
    lightLoad = (lightLevel / luminousEfficacy) / efficiencyCoefficient
    lightingDensityPerArea = '%.1f' % (lightLoad)
    lightLoadRes = 'Light Load %s W/m2' % (lightingDensityPerArea)
    print lightLoadRes
    
    return lightingDensityPerArea
    
#Check the inputs.
checkData = False
checkData, luminousEfficacy, maintenanceFactor, coefficientOfUtilization = checkInputs()

#If the inputs are good, run the function.
if checkData == True:
    lightingDensityPerArea = main(_lightLevel, luminousEfficacy, maintenanceFactor, coefficientOfUtilization)
