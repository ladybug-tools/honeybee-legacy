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
Use this component to set EnergyPlus Simulation Controls such as whether to run certain types of HVAC sizing calculations, etc.
-
Provided by Honeybee 0.0.64

    Args:
        doZoneSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the zones.  The default is set to "True."
        doSystemSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the HVAC system.  The default is set to "True."
        doPlantSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the HVAC plant (boiler and chiller).  The default is set to "True", although with ideal air loads, there is no plant as each zone has its own ideal air system and there is no central plant between zones.
        runSimForSizingPeriods_: Set to "True" to have EnergyPlus run a simulation for the Sizing periods specified in the IDF.  The default is set to "False."  By default, the sizing periods are set to the extreme hot and extreme cold weeks of the weather file but a custom ddy file can also be specified with the "Honeybee_Energy Simulation Par" component.
        runSimForRunPeriods_: Set to "True" to have EnergyPlus run the simulation for energy use over the entire year of the EPW.  The default is set to "True."
        maxWarmupDays_: The maximum number of warmup days that you want the energyplus simulation to run before recording result values.  The default is set to 25.
        maxWarmupDays_: The minimum number of warmup days that you want the energyplus simulation to run before recording result values.  The default is set to 6.
    Returns:
        simControls: A set of simulation controls tha can be plugged into the "Honeybee_Energy Simulation Par" component.
"""

ghenv.Component.Name = "Honeybee_Simulation Control"
ghenv.Component.NickName = 'simControl'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


def main(doZoneSizingCalc, doSystemSizingCalc, doPlantSizingCalc,runSimForSizing, runSimForRunPeriods, maxWarmupDays, minWarmupDays):
    # I will add check for inputs later
    if doZoneSizingCalc == None: doZoneSizingCalc = True
    if doSystemSizingCalc == None: doSystemSizingCalc = True
    if doPlantSizingCalc == None: doPlantSizingCalc = True
    if runSimForSizing == None: runSimForSizing = False
    if runSimForRunPeriods == None: runSimForRunPeriods = True
    if maxWarmupDays_ == None: maxWarmupDays = 25
    if minWarmupDays_ == None: minWarmupDays = 6

    return doZoneSizingCalc, doSystemSizingCalc, doPlantSizingCalc,runSimForSizing, runSimForRunPeriods, maxWarmupDays, minWarmupDays
    

simControls = main(doZoneSizingCalculation_,
                   doSystemSizingCalculation_,
                   doPlantSizingCalculation_,
                   runSimForSizingPeriods_,
                   runSimForRunPeriods_, maxWarmupDays_, minWarmupDays_)