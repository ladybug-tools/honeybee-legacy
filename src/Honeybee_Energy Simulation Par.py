# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
EnergyPlus Shadow Parameters
-
Provided by Honeybee 0.0.53

    Args:
        timestep_:...
        shadowCalcPar_: ...
        doPlantSizingCalculation_: ...
        solarDistribution_: ...
        simulationControls_: ...
        ddyFile_: ...
    Returns:
        energySimPar:...
"""

ghenv.Component.Name = "Honeybee_Energy Simulation Par"
ghenv.Component.NickName = 'EnergySimPar'
ghenv.Component.Message = 'VER 0.0.53\nAUG_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


def main(timestep, shadowCalcPar, solarDistribution, simulationControls, ddyFile):
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
    
    # I will add check for inputs later
    if timestep == None: timestep = 6
    if shadowCalcPar == []: shadowCalcPar = ["AverageOverDaysInFrequency", 30, 3000]
    if solarDistribution == None:
        solarDistribution = solarDist["4"]
    else:
        solarDistribution = solarDist[solarDistribution]
    if simulationControls == []: simulationControls= [True, True, True, False, True]
    
    return [timestep] + shadowCalcPar + [solarDistribution] + simulationControls + [ddyFile]

energySimPar = main(timestep_,
                   shadowCalcPar_,
                   solarDistribution_,
                   simulationControls_,
                   ddyFile_)