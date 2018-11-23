#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari and Chris Mackey <mostapha@ladybug.tools and chris@mackeyarchitecture.com> 
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
This component helps select simulation outputs that can be hooked into the "Honyebee_Export to OpenStudio" component.  Outputs are taken from here:
http://bigladdersoftware.com/epx/docs/8-3/input-output-reference/
_
You can also use the "Honeybee_Read Result Dictionary" component after running a simulation to get a list of all possible outputs that you can request from a given simulation.
-
Provided by Honeybee 0.0.64
    
    Args:
        zoneEnergyUse_: Set to "True" to have EnergyPlus solve for basic building energy use such as heating, cooling, electricity for lights and electricity for plug loads for each zone.
        zoneGainsAndLosses_: Set to "True" to have EnergyPlus solve for building gains and losses such as people gains, solar gains and infiltration losses/gains.
        zoneComfortMetrics_: Set to "True" to have EnergyPlus solve for the mean air temperature, mean radiant temperature, operative temperature, and relative humidity of each zone.
        comfortMapVariables_: Set to "True" to have EnergyPlus solve for the air flow and air heat gain of each zone, which is needed for the comfort map air stratification calculation.
        zoneHVACParams_: Set to "True" to have EnergyPlus solve for the fractions of heating/cooling loads that are latent vs. sensible as well as the the flow rate and temperature of supply air into each zone.
        surfaceTempAnalysis_: Set to "True" to have EnergyPlus solve for the interior and exterior surface temperatures of the individual surfaces of each zone.
        surfaceEnergyAnalysis_: Set to "True" to have EnergyPlus solve for the gains and losses through the individual surfaces of each zone.
        glazingSolarAnalysis_: Set to "True" to have EnergyPlus solve for the transmitted beam, diffuse, and total solar gain through the individual window surfaces of each zone.  These outputs are needed for Energy Shade Benefit Analysis.
        _loadType_: An integer or text value to set the type of load outputs requested (sensible, latent, total).  The default is set to "0 = Total" but you may want to change this to "1 = Sensible" for zone HVAC sizing, etc.  Choose from the following options:
            0 = Total
            1 = Sensible
            2 = Latent
        timestep_: Specify a timestep by inputing the words 'timestep', 'hourly', 'daily', 'monthly' or 'annual'.  The default is set to hourly.
    Returns:
        report: Report!
        simulationOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "Honeybee_Export to OpenStudio" component.
"""

ghenv.Component.Name = "Honeybee_Generate EP Output"
ghenv.Component.NickName = 'EPOutput'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import Grasshopper.Kernel as gh


# A list of the Energy Plus simulation outputs for HB generators.
#HBgeneratorsimoutputs = ["Output:Variable,*,Facility Total Electric Demand Power, Hourly;","Output:Variable,*,Facility Net Purchased Electric Power, Hourly;"]



def main(zoneEnergyUse, zoneGainsAndLosses, zoneComfortMetrics, zoneHVACMetrics, surfaceTempAnalysis, surfaceEnergyAnalysis, glazingSolarAnalysis, loadType, timestep):
    loadTypeDict = {
    '0': 0,
    '1': 1,
    '2': 2,
    'total': 0,
    'sensible': 1,
    'latent': 2
    }
    
    timePeriod = timestep + ";"
    if loadType == None:
        loadType = 0
    else:
        try:
            loadType = loadTypeDict[loadType.lower()]
        except:
            warning = '_loadType_ is not valid.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    simulationOutputs = []
    simulationOutputs.append("OutputControl:Table:Style,Comma;")
    
    if zoneEnergyUse == True:
        if loadType == 0:
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Total Heating Energy, " + timePeriod)
        elif loadType == 1:
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Sensible Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Sensible Heating Energy, " + timePeriod)
        elif loadType == 2:
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Latent Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Latent Heating Energy, " + timePeriod)
        
        simulationOutputs.append("Output:Variable,*,Cooling Coil Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Chiller Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Boiler Gas Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Heating Coil Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Heating Coil Gas Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Heating Coil Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Humidifier Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Fan Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Fan Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Lights Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Electric Equipment Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Earth Tube Fan Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Pump Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone VRF Air Terminal Cooling Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone VRF Air Terminal Heating Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,VRF Heat Pump Cooling Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,VRF Heat Pump Heating Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Chiller Heater System Cooling Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Chiller Heater System Heating Electric Energy, "+ timePeriod)
    
    if zoneGainsAndLosses == True:
        simulationOutputs.append("Output:Variable,*,Zone Windows Total Transmitted Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Sensible Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Sensible Heat Gain Energy, " + timePeriod)
        if loadType == 0:
            simulationOutputs.append("Output:Variable,*,Zone People Total Heating Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Heating Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Loss Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Gain Energy, " + timePeriod)
        elif loadType == 1:
            simulationOutputs.append("Output:Variable,*,Zone People Sensible Heating Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Sensible Heating Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Sensible Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Sensible Heat Loss Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Sensible Heat Gain Energy, " + timePeriod)
        elif loadType == 2:
            simulationOutputs.append("Output:Variable,*,Zone People Latent Gain Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Latent Heating Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Latent Cooling Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Latent Heat Loss Energy, " + timePeriod)
            simulationOutputs.append("Output:Variable,*,Zone Infiltration Latent Heat Gain Energy, " + timePeriod)
    
    if zoneComfortMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Operative Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Air Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Radiant Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Relative Humidity, " + timePeriod)
    
    if comfortMapVariables_ == True:
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mechanical Ventilation Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance Internal Convective Heat Gain Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance Surface Convection Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance System Air Transfer Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window System Solar Transmittance, " + timePeriod)
    
    if zoneHVACMetrics == True:
        simulationOutputs.append("Output:Variable,*,System Node Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Relative Humidity, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Cooling Setpoint Not Met Time, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Heating Setpoint Not Met Time, "+ timePeriod)
    
    if surfaceTempAnalysis == True:
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Inside Face Temperature, " + timePeriod)
    
    if surfaceEnergyAnalysis == True:
        simulationOutputs.append("Output:Variable,*,Surface Average Face Conduction Heat Transfer Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Heat Gain Energy, " + timePeriod)
    
    if glazingSolarAnalysis_ == True:
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Beam Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Diffuse Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Solar Radiation Energy, " + timePeriod)
    
    return simulationOutputs



#Check the inputs to be sure that the right data types are selected.
initCheck = True
try:
    if timestep_.lower() == "monthly" or timestep_.lower() == "hourly" or timestep_.lower() == "daily" or timestep_.lower() == "annual" or timestep_.lower() == "timestep": pass
except:
    if timestep_ == None: timestep_ = "hourly"
    else:
        initCheck =False
        print "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual.")


#Generate the simulation outputs if the above checks are sucessful.
if initCheck == True:
    simulationOutputs = main(zoneEnergyUse_, zoneGainsAndLosses_, zoneComfortMetrics_, zoneHVACParams_, surfaceTempAnalysis_, surfaceEnergyAnalysis_, glazingSolarAnalysis_, _loadType_, timestep_)
    print "Simulation outputs generated successfully!"