#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari and Chris Mackey <Sadeghipour@gmail.com and chris@mackeyarchitecture.com> 
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
This component helps select simulation outputs that can be hooked into the WriteIDF component.  Outputs are taken from here:
http://apps1.eere.energy.gov/buildings/energyplus/pdfs/inputoutputreference.pdf

-
Provided by Honeybee 0.0.57
    
    Args:
        zoneEnergyUse_: Set to "True" to have EnergyPlus solve for basic building energy use such as heating, cooling, electricity for lights and electricity for plug loads for each zone.
        zoneGainsAndLosses_: Set to "True" to have EnergyPlus solve for building gains and losses such as people gains, solar gains and infiltration losses/gains.
        zoneComfortMetrics_: Set to "True" to have EnergyPlus solve for the mean air temperature, mean radiant temperature, operative temperature, and relative humidity of each zone.
        comfortMapVariables_: Set to "True" to have EnergyPlus solve for the air flow and air heat gain of each zone, which is needed for the comfort map air stratification calculation.
        zoneHVACParams_: Set to "True" to have EnergyPlus solve for the fractions of heating/cooling loads that are latent vs. sensible as well as the the flow rate and temperature of supply air into each zone.
        surfaceTempAnalysis_: Set to "True" to have EnergyPlus solve for the interior and exterior surface temperatures of the individual surfaces of each zone.
        surfaceEnergyAnalysis_: Set to "True" to have EnergyPlus solve for the gains and losses through the individual surfaces of each zone.
        glazingSolarAnalysis_: Set to "True" to have EnergyPlus solve for the transmitted beam, diffuse, and total solar gain through the individual window surfaces of each zone.  These outputs are needed for Energy Shade Benefit Analysis.
        HBgeneration_: Set to "True" to have EnergyPlus solve for variables related to HB generation objects like solar panels, wind turbines, batteries, etc.
        ____________________: ...
        timestep_: Specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annual'.  The default is set to hourly.
    Returns:
        report: Report!
        simulationOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "writeIDF" component.
"""

ghenv.Component.Name = "Honeybee_Generate EP Output"
ghenv.Component.NickName = 'EPOutput'
ghenv.Component.Message = 'VER 0.0.57\nOCT_27_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import Grasshopper.Kernel as gh


# A list of the Energy Plus simulation outputs for HB generators.
#HBgeneratorsimoutputs = ["Output:Variable,*,Facility Total Electric Demand Power, Hourly;","Output:Variable,*,Facility Net Purchased Electric Power, Hourly;"]



def main(zoneEnergyUse, zoneGainsAndLosses, zoneComfortMetrics, zoneHVACMetrics, surfaceTempAnalysis, surfaceEnergyAnalysis, glazingSolarAnalysis, timestep):
    simulationOutputs = []
    timePeriod = timestep + ";"
    
    simulationOutputs.append("OutputControl:Table:Style,Comma;")
    
    if zoneEnergyUse == True:
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Packaged Terminal Heat Pump Total Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Packaged Terminal Heat Pump Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Chiller Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Boiler Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Fan Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Fan Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Lights Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Electric Equipment Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Earth Tube Fan Electric Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Pump Electric Energy, "+ timePeriod)
    
    if zoneGainsAndLosses == True:
        simulationOutputs.append("Output:Variable,*,Zone Windows Total Transmitted Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone People Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Gain Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Total Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Total Heat Gain Energy, " + timePeriod)
    
    if zoneComfortMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Operative Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Air Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Radiant Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Relative Humidity, " + timePeriod)
    
    if comfortMapVariables_ == True:
        simulationOutputs.append("Output:Variable,*,Zone Ventilation Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mechanical Ventilation Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Earth Tube Air Flow Volume, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance Internal Convective Heat Gain Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance Surface Convection Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Heat Balance System Air Transfer Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window System Solar Transmittance, " + timePeriod)
    
    if zoneHVACMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Latent Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Latent Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Sensible Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Supply Air Sensible Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Standard Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Relative Humidity, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Earth Tube Zone Sensible Cooling Energy, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Earth Tube Zone Sensible Heating Energy, "+ timePeriod)
    
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
    
    if HBgeneration_ == True:
        simulationOutputs.append("Output:Variable,*,Facility Total Electric Demand Power, "+ timePeriod)
        simulationOutputs.append("Output:Variable,*,Facility Net Purchased Electric Energy, "+ timePeriod)
        
        # Facility Total Electric Demand Power - This is the total of the whole Building and HVAC electric demands.
        
        # Facility Net Purchased Electric Power - These outputs are the net electricity purchased in both Power and Energy units. This value can be either positive or negative. Positive values are defined as electricity purchased from the utility. Negative values are defined as surplus electricity fed back into the grid.
        
        # Electric Load Center Produced Electric Energy [J]
        # These outputs are the sum of electrical energy and power produced by the generators attached to a particular load center. The keywords for these reports are the unique names of ElectricLoadCenter:Distribution objects.
    
    return simulationOutputs



#Check the inputs to be sure that the right data types are selected.
initCheck = True
if timestep_ == "monthly" or timestep_ == "hourly" or timestep_ == "daily" or timestep_ == "annual" or timestep_.lower() == "timestep": pass
elif timestep_ == None:
    timestep_ = "hourly"
else:
    initCheck = False
    print "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Incorrect value connected for timestep_.  Allowable inputs include monthly, hourly, daily or annual.")


#Generate the simulation outputs if the above checks are sucessful.
if initCheck == True:
    simulationOutputs = main(zoneEnergyUse_, zoneGainsAndLosses_, zoneComfortMetrics_, zoneHVACParams_, surfaceTempAnalysis_, surfaceEnergyAnalysis_, glazingSolarAnalysis_, timestep_)
    print "Simulation outputs generated successfully!"