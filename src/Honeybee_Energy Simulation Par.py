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
EnergyPlus Shadow Parameters
-
Provided by Honeybee 0.0.64

    Args:
        timestep_: It is the number of times simulation will be performed in an hour.
        -
        You can choose any number from 1,2,3,4,5,6,10,12,15,20,30, and 60 as the timestep. Generally speaking, the shorter the time step, the longer it takes to finish the simulation. The biggest timestep is 60 minutes. That will mean that the simulation will for every one hour for the year. 
        -
        It is advisable to use the timestep of 60 minutes only in a case when no HVAC system is envisaged, accuracy not a primary concern, and simulation run time is critical.
        -
        In summary, shorter timesteps improve how calculation models for surface temperature and zone air temperature are coupled together and therefore, shorter timesteps are recommended. On the other side, longer timesteps introduce more lag in temperature distribution and as a result, offers a less dynamic behavior.
        -
        The default is set to 6 timesteps per hour, which means that the energy balance calculation is run every 10 minutes of the year. This is a recommended default for simulations with HVAC.
        -
        Other suggested defaults are 4 for non-HVAC simulations. Simulating green roofs require more timesteps per hour. 
        shadowCalcPar_: An optional set of shadow calculation parameters from the "Honeybee_ShadowPar" component.
        solarDistribution_: An optional text string or integer that sets the solar distribution calculation.  Choose from the following options:
            0 = "MinimalShadowing" - In this case, exterior shadowing is only computed for windows and not for other opaque surfaces that might have their surface temperature affected by the sun. All beam solar radiation entering the zone is assumed to fall on the floor. A simple window view factor calculation will be used to distribute incoming diffuse solar energy between interior surfaces.
            1 = "FullExterior" - The simulation will perform the solar calculation in a manner that only accounts for direct sun and whether it is blocked by surrounding context geometry.  For the inside of the building, all beam solar radiation entering the zone is assumed to fall on the floor. A simple window view factor calculation will be used to distribute incoming diffuse solar energy between interior surfaces.
            2 = "FullInteriorAndExterior" - The simulation will perform the solar calculation in a manner that models the direct sun (and wheter it is blocked by outdoor context goemetry.  It will also ray trace the direct sun on the interior of zones to distribute it correctly between interior surfaces.  Any indirect sun or sun bouncing off of objects will not be modled.
            3 = "FullExteriorWithReflections" - The simulation will perform the solar calculation in a manner that accounts for both direct sun and the light bouncing off outdoor surrounding context.  For the inside of the building, all beam solar radiation entering the zone is assumed to fall on the floor. A simple window view factor calculation will be used to distribute incoming diffuse solar energy between interior surfaces.
            4 = "FullInteriorAndExteriorWithReflections" - The simulation will perform the solar calculation in a manner that accounts for light bounces that happen both outside and inside the zones.  This is the most accurate method and is the one assigned by default.  Note that, if you use this method, EnergyPlus will give Severe warnings if your zones have concave geometry (or are "L"-shaped).  Such geometries mess up this solar distribution calculation and it is recommeded that you either break up your zones in this case or not use this solar distribution method.
        holidays_: A list of integers, each between 1 and 365, that represent the days of the year on which a holiday occurs.  Alternatively, this can be a list of text strings (example: DEC 25).  Finally, this input can accept the "holidays" output from the "Honeybee_Convert EnergyPlus Schedule to Values" component.
        startDayOfWeek_: An integer or text descriptor to set the ssimulation start day of the week. The default is set to 0 - sun - sunday.
            -
            Choose from one of the following:
            0 - sun - sunday
            1 - mon - monday
            2 - tue - tuesday
            3 - wed - wednesday
            4 - thu - thursday
            5 - fri - friday
            6 - sat - saturday
        simulationControls_: An optional set of simulation controls from the "Honeybee_Simulation Control" component.
        ddyFile_: An optional file path to a .ddy file on your system.  This ddy file will be used to size the HVAC system before running the simulation.
        heatingSizingFactor_: An optional number that represents the 'saftey factor' to which the heating system will be sized.  A sizing factor of 1 means that the system is sized to perfectly meet the design day conditions.  The default is set to 1.25 as it is usually appropriate to oversize the system slightly to ensure that there are no unmet hours.  Specifying a factor here that is below 1.25 can result in more hours that do not meet the heating setpoint.
        coolingSizingFactor_: An optional number that represents the 'saftey factor' to which the cooling system will be sized.  A sizing factor of 1 means that the system is sized to perfectly meet the design day conditions.  The default is set to 1.15 as it is usually appropriate to oversize the system slightly to ensure that there are no unmet hours.  Specifying a factor here that is below 1.15 can result in more hours that do not meet the cooling setpoint.
        terrain_: An optional integer or text string to set the surrouning terrain of the building, which will be used to determine how wind speed around the building changes with height.  If no value is input here, the default is set to "City."  Choose from the following options:
            0 = City: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburbs: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Ocean: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        monthlyGrndTemps_: An optional list of 12 monthly ground temperatures to be used by those surfaces in contact with the ground in the simulation.  Please note that the EPW values out of the Import Ground Temp component are usually too extreme for a conditioned building.  If no values are input here, the model will attempt to estimate a reasonable starting base temperature from these results by using a value of 18C in cases of monthly ground temperatures below 18C, 24C in cases of monthly ground temperatures above 24C, and the actual ground temperature if the monthly average falls in between 18C and 24C.  Usually, ground temperatures will be about 2C lower than the overage indoor air temperature for a given month.
    Returns:
        energySimPar: Energy simulation parameters that can be plugged into the "Honeybee_ Run Energy Simulation" component.
"""

ghenv.Component.Name = "Honeybee_Energy Simulation Par"
ghenv.Component.NickName = 'EnergySimPar'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nAPR_11_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh

def main(timestep, shadowCalcPar, solarDistribution, simulationControls, ddyFile, terrain, monthlyGrndTemps, holidays, startDayOfWeek, heatingSizingFactor, coolingSizingFactor):
    solarDist = {
                "0" : "MinimalShadowing",
                "1" : "FullExterior",
                "2" : "FullInteriorAndExterior",
                "3" : "FullExteriorWithReflections",
                "4" : "FullInteriorAndExteriorWithReflections",
                "MinimalShadowing" : "MinimalShadowing",
                "FullExterior" : "FullExterior",
                "FullInteriorAndExterior" : "FullInteriorAndExterior",
                "FullExteriorWithReflections" : "FullExteriorWithReflections",
                "FullInteriorAndExteriorWithReflections" : "FullInteriorAndExteriorWithReflections"
                }
    
    terrainDict = {
                "0" : "City",
                "1" : "Suburbs",
                "2" : "Country",
                "3" : "Ocean",
                "City" : "City",
                "Suburbs" : "Suburbs",
                "Country" : "Country",
                "Ocean" : "Ocean"
                }
    
    # Check the start day of the week.
    daysOfWeek = {'0':'Sunday', '1':'Monday', '2':'Tuesday', '3':'Wednesday', '4':'Thursday', '5':'Friday', '6':'Saturday',
    'sun':'Sunday', 'mon':'Monday', 'tue':'Tuesday', 'wed':'Wednesday', 'thu':'Thursday', 'fri':'Friday', 'sat':'Saturday',
    'sunday':'Sunday', 'monday':'monday', 'tuesday':'Tuesday', 'wednesday':'Wednesday', 'thursday':'Thursday', 'friday':'Friday', 'saturday':'Saturday'}
    
    if startDayOfWeek != None:
        try:
            startDayOfWeek = daysOfWeek[startDayOfWeek.lower()]
        except:
            warning = 'Input for startDayOfWeek_ is not valid.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    if timestep == None: timestep = 6
    if shadowCalcPar == []:
        shadowCalcPar = ["AverageOverDaysInFrequency", 30, 3000]
    
    assert len(shadowCalcPar) == 3, "Wrong input for shadow calculation parameters."
        
    if solarDistribution == None:
        solarDistribution = solarDist["4"]
    else:
        solarDistribution = solarDist[solarDistribution]
    if simulationControls == []: simulationControls= [True, True, True, False, True, 25, 6]
    if terrain == None:
        terrain = terrainDict["0"]
    else:
        terrain = terrainDict[terrain]
    
    if heatingSizingFactor == None:
        heatingSizingFactor = 1.25
    if coolingSizingFactor == None:
        coolingSizingFactor = 1.15
    
    finalHoliday = []
    for holiday in holidays:
        if holiday == "" or holiday == None:
            pass
        else:
            finalHoliday.append(holiday)
    
    if (monthlyGrndTemps == [] or len(monthlyGrndTemps) == 12):
        return [timestep] + shadowCalcPar + [solarDistribution] + simulationControls + [ddyFile] + [terrain] + [monthlyGrndTemps] + [finalHoliday]  + [startDayOfWeek] + [heatingSizingFactor] + [coolingSizingFactor]
    else:
        if monthlyGrndTemps != [] and len(monthlyGrndTemps) != 12:
            warning = 'monthlyGrndTemps_ must either be left blank or contain 12 values representing the average ground temperature for each month.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return None

energySimPar = main(timestep_, shadowCalcPar_, solarDistribution_, simulationControls_,
                   ddyFile_, terrain_, monthlyGrndTemps_, holidays_, startDayOfWeek_,
                   heatingSizingFactor_, coolingSizingFactor_)