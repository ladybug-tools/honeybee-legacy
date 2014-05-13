# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus Shadow Parameters
-
Provided by Honeybee 0.0.53

    Args:
        doZoneSizingCalculation_:...
        doSystemSizingCalculation_: ...
        doPlantSizingCalculation_: ...
        runSimForSizingPeriods_: ...
        runSimForRunPeriods_: ...
    Returns:
        simControls:...
"""

ghenv.Component.Name = "Honeybee_Simulation Control"
ghenv.Component.NickName = 'simControl'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
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