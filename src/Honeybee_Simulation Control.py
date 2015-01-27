# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to set EnergyPlus Simulation Controls such as whether to run certain types of HVAC sizing calculations, etc.
-
Provided by Honeybee 0.0.55

    Args:
        doZoneSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the zones.  The default is set to "True."
        doSystemSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the HVAC system.  The default is set to "True."
        doPlantSizingCalculation_: Set to "True" to have EnergyPlus do a sizing calculation for the HVAC plant (boiler and chiller).  The default is set to "True", although with ideal air loads, there is no plant as each zone has its own ideal air system and there is no central plant between zones.
        runSimForSizingPeriods_: Set to "True" to have EnergyPlus run a simulation for the Sizing periods specified in the IDF.  The default is set to "False."  By default, the sizing periods are set to the extreme hot and extreme cold weeks of the weather file but a custom ddy file can also be specified with the "Honeybee_Energy Simulation Par" component.
        runSimForRunPeriods_: Set to "True" to have EnergyPlus run the simulation for energy use over the entire year of the EPW.  The default is set to "True."
    Returns:
        simControls: A set of simulation controls tha can be plugged into the "Honeybee_Energy Simulation Par" component.
"""

ghenv.Component.Name = "Honeybee_Simulation Control"
ghenv.Component.NickName = 'simControl'
ghenv.Component.Message = 'VER 0.0.55\nJAN_11_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


def main(doZoneSizingCalc, doSystemSizingCalc, doPlantSizingCalc,runSimForSizing, runSimForRunPeriods):
    # I will add check for inputs later
    if doZoneSizingCalc == None: doZoneSizingCalc = True
    if doSystemSizingCalc == None: doSystemSizingCalc = True
    if doPlantSizingCalc == None: doPlantSizingCalc = True
    if runSimForSizing == None: runSimForSizing = False
    if runSimForRunPeriods == None: runSimForRunPeriods = True

    return doZoneSizingCalc, doSystemSizingCalc, doPlantSizingCalc,runSimForSizing, runSimForRunPeriods
    

simControls = main(doZoneSizingCalculation_,
                   doSystemSizingCalculation_,
                   doPlantSizingCalculation_,
                   runSimForSizingPeriods_,
                   runSimForRunPeriods_)