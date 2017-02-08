#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Anton Szilasi <ajszilas@gmail.com> 
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
Provided by Honeybee 0.0.61

Use this component to create your own horizontial axis wind turbine to use in Energyplus simulations. This component simulates wind turbines by using either the simple Power Calculation method which means that the Maximum Power coefficient must be calculated.
-
Or by using the analytical method. The difference between the simple and analytical method is that for the simple method, the maximum power coefficient must be calculated while in the analytical method 6 power coefficients must be specified instead of the maximum power coefficient.
-
Please see more information about wind turbines at: http://bigladdersoftware.com/epx/docs/8-3/input-output-reference/group-electric-load-center.html#generatorwindturbine
-
Wind turbines are assumed to have a life time of 25 years.
-
Provided by Honeybee 0.0.61

    Args:
        TemplateMediumTurbine_: If set to True a medium sized turbine will be created with pre-set values, the turbines values can be viewed from the ReadMe! output. Template values can be changed for each input below by entering a value for each input. Otherwise if no input is given template values will be used for each input.
        TemplateLargeTurbine_: If set to True a large sized turbine will be created with pre-set values, the turbines values can be viewed from the ReadMe! output. Template values can be changed for each input below by entering a value for each input. Otherwise if no input is given template values will be used for each input.
        _name: The name for this wind turbine
        _simpleOrAnalytical: An integer of 1 or 2 that defines whether the wind turbine is simple or analytical,
        the default is the simple model with a coefficient of 0.40 - The simple model uses one maximum power coefficient as a maximum fraction of power extraction from ambient wind.
        
        While the analytical model uses 6 with the default analytical coefficents (used only if turbine switched to analytical) being 0.5176,116,0.4,0,5 and 21 details of each model can be seen at http://bigladdersoftware.com/epx/docs/8-3/input-output-reference/group-electric-load-center.html#field-maximum-power-coefficient
        and http://bigladdersoftware.com/epx/docs/8-3/input-output-reference/group-electric-load-center.html#field-power-coefficient-parameter respectively. 
        rotor_type: This field is the type of axis of the wind turbine, a different algorithm is used in the calculation of the electrical power output of the wind turbine depending on the Rotor type. There are two types of turbines to select from, for a Horizontal axis wind turbine enter an integer input of 1 for a Vertical axis turbine enter an integer input of 2. The default is a Horizontial Axis Wind Turbine.
        _powerControl: This field is the type of rotor control for the wind turbine. This protects the system against the overloading for a system with no speed or pitch control and also to maximize the energy yield for the system. Four different control types are classified in the literature: 
        1-Fixed Speed Fixed Pitch (FSFP),
        2-Fixed Speed Variable Pitch (FSVP),
        3-Variable Speed Fixed Pitch (VSFP), and
        4-Variable Speed Variable Pitch (VSVP).
        enter an integer input of 1,2,3 and 4 to select these options respectively.
        _rotorSpeed: This field is the maximum rotational speed of the rotor at the rated power of the wind turbine in rev/min (revolution per minute). It is used to determine the tip speed ratio of the rotor and relative flow velocity incident on a single blade of the VAWT systems.
        _rotorDiameter: This field is the diameter of the rotor (in meters ). Note that this field is not the height of the blade, but the diameter of the perpendicular circle from the vertical pole in the VAWT systems. It determines the swept area of the rotor of the HAWT systems and the chordal velocity of the VAWT systems.
        overallHeight: This field is the height of the hub of the HAWT system, or of the pole of the VAWT system (in meters). It is necessary to estimate local air density and the wind speed at this particular height where the wind turbine system is installed.
        _numberOfBlades: This field is the number of blades of the wind turbine. The azimuth angle of the rotor of the VAWT system is determined by dividing 360 degree by this field so that the model determines the chordal velocity component and the normal velocity component of the system. The default value is 3.
        _powerOutput: This field is the nominal power output of the wind turbine system at the rated wind speed (in W or Btu/hr). Note that the maximum power of the system should be entered with no control, i.e. FSFP control type, can physically produce. Manufacturer data sometimes describes this as peak power or rated capacity. If the local wind speed is greater than the rated wind speed, the model assumes constant power output of this field.
        _ratedWindSpeed: This field is the wind speed that the wind turbine system indicates the peak in the power curve (in m/s ). The system produces the maximum power at this speed and the speed of the rotor is managed based on this wind speed.
        _cutInWindSpeed: This field is the lowest wind speed where the wind turbine system can be operated (in m/s). No power generation is achieved as long as the ambient wind speed is lower than this speed
        _cutOutWindspeed: This field is the greatest wind speed (in m/s). When the wind speed exceeds this value, the wind turbine system needs to be stopped because of inefficiencies in the system. All systems that have either pitch or speed control must be stopped when the ambient wind speed exceeds this speed. Note that the user should input a wind speed above which physical damage to the system might be caused in the case of a FSFP system. It appears as extreme/survival/design wind speed in the literature. The system will be turned off when the ambient wind speed is over this speed.
        _overallTurbineEfficiency: This field is the overall system efficiency of the wind turbine system. It includes all the conversion losses as well as transient losses during the dynamic control when the ambient wind speed is between the rated wind speed and cut-out wind speed (see previous fields). The user also has the ability to specify delivery losses from the system to the local area. If the user does not enter a fraction, the model assumes the default value of 0.835. Note that the fraction must be between zero and one.
        _maxTipSpeedRatio: This field is the maximum tip speed ratio between the rotor velocity and ambient wind velocity. The rotor speed varies with this ratio to maximize the power output when the rotor control types are variable speed ones. This field allows the user to adjust the power output from the particular system or to find the optimal tip speed ratio of the system. Optimal tip speed ratio is dependent on the number of blades. It is typically about 6, 5, and 3 for two-bladed, three-bladed, and four-bladed rotor, respectively. For the vertical axis wind turbine, it is smaller than horizontal axis wind turbine, and varies with the chord area. 
        _maxPowerCoefficient: Used only with the simple model, this is the maximum fraction of power extraction possible from the ambient wind. This value can be calculated from the power curve published in most manufacturers' specifications by using the kinetic energy equation as
        Cp = P/0.5**A*V^3  where: P = power production at the rated wind speed [W],  = density of air [kg/m3], A = swept area of rotor [m2], V = rated wind speed [m/s], Cp = power coefficient
        _powerCoefficients: Used only with the analytical model - Use a grasshopper panel set to multiline data to specify the 6 power coefficients - If none are specified the defaults outlined in the Energy Plus documentation will be used. More information can be found at: http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#field-power-coefficient-parameter
        
        _localAvWindspeed: This is the local annual average wind speed that represents a representative wind profile at the location of the system (in m/s ). It is used to factor the difference in wind speed between the weather file wind data and the locally measured wind data so that the model minimizes uncertainties caused by improper wind data at the particular location. Considerable differences between the weather file wind data and the local wind data typically appear so it is important to consider this carefully in order to use accurate local wind data in the simulation. The model internally determines a multiplier and it is multiplied by the weather file wind data adjusted at the height of the system
        _heightLocalMetrologicalStation: This is the height that the local wind speed is measured (in meters ). The annual average wind speed (see previous field) input by the user is internally recalculated by existing EnergyPlus functions at the height of the local station. This modified wind speed is then factored and applied to the weather file wind data. The minimum and default values are zero and 50 meters.
        _turbinecost: The cost of the turbine
        
        
    Returns:
        HBWindTurbine: A Honeybee wind turbine. To run this in an EnergyPlus system you must first add it to a Honeybee generation system - to do so connect this output to the HB_generationobjects input of the Honeybee_generationsystem component
        

"""

ghenv.Component.Name = "Honeybee_Generator_Wind_Horizontialaxis"
ghenv.Component.NickName = 'Generator:Wind:Horizontialaxis'
ghenv.Component.Message = 'VER 0.0.61\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP" #"06 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0" #"0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import itertools

def checktheinputs(_name,_simpleOrAnalytical,_powerCoefficients,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")

        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1    
    
    
    if _name == None:
        print "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!")
        return -1
        
    if (_simpleOrAnalytical != 1) and (_simpleOrAnalytical != 2):
        
        warn = "_simpleOrAnalytical must be the integer 1 or 2 \n"+\
        "1 will set the turbine to use the simple model, while entering 2 will set the turbine to a analytical model!"
        print warn
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
        
    if (TemplateMediumTurbine_ == True) and (TemplateLargeTurbine_== True):
        print "Only one template can be used at a time! Please set either TemplateLargeTurbine_ or TemplateMediumTurbine_ to true not both! "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only one template can be used at a time! Please set either TemplateLargeTurbine_ or TemplateMediumTurbine_ to true not both!")
        return -1

    if _powerControl == None:
        print "The field _powerControl must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _powerControl must be specified!")
        return -1

    if (_powerControl < 1) or (_powerControl > 4):
        print "The field _powerControl must be an integer between 1 and 4!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _powerControl must be an integer between 1 and 4")
        return -1

    if _rotorSpeed == None:
        print "The field _rotorSpeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _rotorSpeed must be specified!")
        return -1
        
    if _rotorDiameter == None:
        print "The field _rotorDiameter must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _rotorDiameter must be specified!")
        return -1
        
    if overallHeight == None:
        print "The field overallHeight must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field overallHeight must be specified!")
        return -1
        
    if _powerOutput == None:
        print "The field _powerOutput must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _powerOutput must be specified!")
        return -1
        
    if _ratedWindSpeed == None:
        print "The field _ratedWindSpeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _ratedWindSpeed must be specified!")
        return -1
        
    if _cutInWindSpeed == None:
        print "The field _cutInWindSpeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _cutInWindSpeed must be specified!")
        return -1
        
    if _cutOutWindspeed == None:
        print "The field _cutOutWindspeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _cutOutWindspeed must be specified!")
        return -1
        
    if _maxTipSpeedRatio == None:
        print "The field _maxTipSpeedRatio must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _maxTipSpeedRatio must be specified!")
        return -1
        
    if _maxPowerCoefficient == None:
        print "The field _maxPowerCoefficient must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _maxPowerCoefficient must be specified!")
        return -1
        
    if _localAvWindspeed == None:
        print "The field _localAvWindspeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _localAvWindspeed must be specified!")
        return -1

    if _turbinecost == None:
        print "The field _turbinecost must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field _turbinecost must be specified!")
        return -1
        
    if _powerCoefficients != []:
        if len(_powerCoefficients) != 6:
            print "The analytical wind turbine model requires 6 power coefficients!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The analytical wind turbine requires 6 power coefficients!")
            return -1
        
def main(_name,_simpleOrAnalytical,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_numberOfBlades,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost,_powerCoefficients):
        

    ## The following three if statements are used if templates are NOT used
    if _numberOfBlades == None:
        _numberOfBlades = 3
        print "The number of blades of this turbine has not been specified so the default of 3 blades will be used"
        
    if _overallTurbineEfficiency == None:
        _overallTurbineEfficiency = 0.835
        print "The overall efficiency of the turbine has not been specified so the default efficiency of 0.835 will be used"

    if _heightLocalMetrologicalStation == None:
        _heightLocalMetrologicalStation = 50
        print "The height of the metrological station was not specified so a default of 50 meters has been used"
    
    ##
    
    if _powerControl == 1:
        _powerControl = 'FixedSpeedFixedPitch'
        
    if _powerControl == 2:
        _powerControl = 'FixedSpeedVariablePitch'
        
    if _powerControl == 3:
        _powerControl = 'VariableSpeedFixedPitch'
        
    if _powerControl == 4:
        _powerControl = 'VariableSpeedVariablePitch'

    rotortype = 'HorizontalAxisWindTurbine'
    
    print " The power control of the turbine is " + str(_powerControl)
    
    print " The rotor speed for the turbine is " + str(_rotorSpeed) + " rev/min"
    
    print " The rotor diameter for the  turbine is " + str(_rotorDiameter) + " meters"
    
    print " The overall height for the turbine is " + str(overallHeight) + " meters"
    
    print " The number of blades for the turbine is " + str(_numberOfBlades ) + " blades"
    
    print " The power output for the turbine is " + str(_powerOutput) + " watts"
    
    print " The rated wind speed for the turbine is " + str(_ratedWindSpeed) + " m/s"
    
    print " The cut in wind speed for the turbine is " + str(_cutInWindSpeed) + " m/s"
    
    print " The cut out wind speed for the turbine is " + str(_cutOutWindspeed) + " m/s"
    
    print " The fraction system efficiency for the turbine is " + str(_overallTurbineEfficiency)
    
    print " The Maximum Tip Speed Ratio for the turbine is " + str(_maxTipSpeedRatio)
    
    print " The Local Average Wind Speed for the turbine is " + str(_localAvWindspeed) + " {m/s}"
    
    print " The Height for Local Average Wind Speed for the turbine is " + str(_heightLocalMetrologicalStation) + " meters"
    
    print " The cost for the turbine is " + str(_turbinecost) + " US dollars"
        
        
    if _simpleOrAnalytical == 1:
        
        print " This turbine is using the simple model and the Maximum Power Coefficient for the turbine is "+ str(_maxPowerCoefficient)
        
        powercoefficients = None
        
        HB_windturbines = []
    
        HB_windturbines.append(windgenerator(_name,rotortype,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_numberOfBlades,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost,powercoefficients))
        
        HBWindTurbine = hb_hivegen.addToHoneybeeHive(HB_windturbines, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
        return HBWindTurbine
        
        
    if _simpleOrAnalytical == 2:
        
        print " This turbine is using the analytical model and its power coefficients are...."
        
        _maxPowerCoefficient = None
        
        if _powerCoefficients == []:
        
            _powerCoefficients = [0.5176,116,0.4,0,5,21]
        
        for count,powercoefficient in enumerate(_powerCoefficients):
        
            print " Power coefficient " + str(count+1) + " is " + str(powercoefficient)
        
            HB_windturbines = []
        
        HB_windturbines.append(windgenerator(_name,rotortype,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_numberOfBlades,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost,_powerCoefficients))
        
        HBWindTurbine = hb_hivegen.addToHoneybeeHive(HB_windturbines, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
        return HBWindTurbine


def checktheinputs_template(TemplateMediumTurbine_,template_large_turbin,_simpleOrAnalytical):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1    
    
    if (TemplateMediumTurbine_ == True) and (TemplateLargeTurbine_== True):
        print "Only one template can be used at a time! Please set either TemplateLargeTurbine_ or TemplateMediumTurbine_ to true not both! "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only one template can be used at a time! Please set either TemplateLargeTurbine_ or TemplateMediumTurbine_ to true not both!")
        return -1
        

        
def checknametemplate(_name):
    
    if _name == None:
        print "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!")
        return -1

if checktheinputs_template(TemplateMediumTurbine_,TemplateLargeTurbine_,_simpleOrAnalytical) != -1:
    
    
    hb_hive = sc.sticky["honeybee_generationHive"]()
    windgenerator = sc.sticky["wind_generator"]
    EP_zone = sc.sticky["honeybee_EPZone"]
    hb_hivegen = sc.sticky["honeybee_generationHive"]()
    
    if TemplateMediumTurbine_ == True:
        
        if checknametemplate(_name) != -1:
            
            if _simpleOrAnalytical == None:
                _simpleOrAnalytical = 1
                
            if _powerControl == None:
                _powerControl = 1
                
            if _rotorSpeed == None:
                _rotorSpeed = 41
                
            if _rotorDiameter == None:
                _rotorDiameter = 19
                
            if overallHeight == None:
                overallHeight = 31
                
            if _numberOfBlades == None:
                _numberOfBlades = 3
                
                
            if _powerOutput == None:
                _powerOutput = 55000
                
    
            if _ratedWindSpeed == None:
                _ratedWindSpeed = 11
                
                
            if _cutInWindSpeed == None:
                _cutInWindSpeed = 3.50
                
                
            if _cutOutWindspeed == None:
                _cutOutWindspeed = 25.00
                
                
            if _overallTurbineEfficiency == None:
                _overallTurbineEfficiency = 0.835
                
               
            if _maxTipSpeedRatio == None:
                _maxTipSpeedRatio = 8
                
                
            if _maxPowerCoefficient == None:
                _maxPowerCoefficient = 0.40
                
                
            if _localAvWindspeed == None:
                _localAvWindspeed = 6.4
                
                
            if _heightLocalMetrologicalStation == None:
                _heightLocalMetrologicalStation = 50
                
                
            if _turbinecost == None:
                _turbinecost = 77000
            
    if TemplateLargeTurbine_ == True:
        
        if checknametemplate(_name) != -1:
            
            if _simpleOrAnalytical == None:
                _simpleOrAnalytical = 1
            
            if _powerControl == None:
                _powerControl = 1
                
            if _rotorSpeed == None:
                _rotorSpeed = 15
                
            if _rotorDiameter == None:
                _rotorDiameter = 95
                
            if overallHeight == None:
                overallHeight = 90
                
            if _numberOfBlades == None:
                _numberOfBlades = 3
                
            if _powerOutput == None:
                _powerOutput = 40000
    
            if _ratedWindSpeed == None:
                _ratedWindSpeed = 12
                
            if _cutInWindSpeed == None:
                _cutInWindSpeed = 3.50
                
            if _cutOutWindspeed == None:
                _cutOutWindspeed = 25.00
                
            if _overallTurbineEfficiency == None:
                _overallTurbineEfficiency = 0.835 
               
            if _maxTipSpeedRatio == None:
                _maxTipSpeedRatio = 5
                
            if _maxPowerCoefficient == None:
                _maxPowerCoefficient = 0.35
                
            if _localAvWindspeed == None:
                _localAvWindspeed = 6.4
                
            if _heightLocalMetrologicalStation == None:
                _heightLocalMetrologicalStation = 50
                
            if _turbinecost == None:
                _turbinecost = 39000

if checktheinputs(_name,_simpleOrAnalytical,_powerCoefficients,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost) != -1:
    
    HBWindTurbine = main(_name,_simpleOrAnalytical,_powerControl,_rotorSpeed,_rotorDiameter,overallHeight,_numberOfBlades,_powerOutput,_ratedWindSpeed,_cutInWindSpeed,_cutOutWindspeed,_overallTurbineEfficiency,_maxTipSpeedRatio,_maxPowerCoefficient,_localAvWindspeed,_heightLocalMetrologicalStation,_turbinecost,_powerCoefficients)

