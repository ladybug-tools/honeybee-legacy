# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component helps select simulation outputs that can be hooked into the WriteIDF component.  Outputs are taken from here:
http://apps1.eere.energy.gov/buildings/energyplus/pdfs/inputoutputreference.pdf

-
Provided by Honeybee 0.0.55
    
    Args:
        zoneEnergyUse_: Set to "True" to have EnergyPlus solve for basic building energy use such as heating, cooling, electricity for lights and electricity for plug loads for each zone.
        zoneGainsAndLosses_: Set to "True" to have EnergyPlus solve for building gains and losses such as people gains, solar gains and infiltration losses/gains.
        zoneComfortMetrics_: Set to "True" to have EnergyPlus solve for the mean air temperature, mean radiant temperature, operative temperature, and relative humidity of each zone.
        zoneHVACParams_: Set to "True" to have EnergyPlus solve for the fractions of heating/cooling loads that are latent vs. sensible as well as the the flow rate and temperature of supply air into each zone.
        surfaceAnalysis_: Set to "True" to have EnergyPlus solve for the interior and exterior surface temperatures of the individual surfaces of each zone.
        surfaceAnalysis_: Set to "True" to have EnergyPlus solve for the gains and losses through the individual surfaces of each zone.
        surfaceAnalysis_: Set to "True" to have EnergyPlus solve for the transmitted beam, diffuse, and total solar gain through the individual window surfaces of each zone.
        ____________________: ...
        timestep_: Specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annually'.  The default is set to hourly.
    Returns:
        report: Report!
        simulationOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "writeIDF" component.
"""

ghenv.Component.Name = "Honeybee_Write EP Result Parameters"
ghenv.Component.NickName = 'writeResultParameters'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
ghenv.Component.AdditionalHelpFromDocStrings = "3"




def main(zoneEnergyUse, zoneGainsAndLosses, zoneComfortMetrics, zoneHVACMetrics, surfaceTempAnalysis, surfaceEnergyAnalysis, glazingSolarAnalysis, timestep):
    simulationOutputs = []
    timePeriod = timestep + ";"
    
    simulationOutputs.append("OutputControl:Table:Style,Comma;")
    
    if zoneEnergyUse == True:
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Lights Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Electric Equipment Electric Energy, " + timePeriod)
    
    if zoneGainsAndLosses == True:
        simulationOutputs.append("Output:Variable,*,Zone Windows Total Transmitted Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone People Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Gain Energy, " + timePeriod)
    
    if zoneComfortMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Operative Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Air Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Radiant Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Relative Humidity, " + timePeriod)
    
    if zoneHVACMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Latent Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Latent Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Sensible Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Zone Sensible Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Mass Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Relative Humidity, " + timePeriod)
    
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
if timestep_ == "monthly" or timestep_ == "hourly" or timestep_ == "daily" or timestep_ == "annually": pass
else:timestep_ = "hourly"


#Generate the simulation outputs if the above checks are sucessful.
simulationOutputs = main(zoneEnergyUse_, zoneGainsAndLosses_, zoneComfortMetrics_, zoneHVACParams_, surfaceTempAnalysis_, surfaceEnergyAnalysis_, glazingSolarAnalysis_, timestep_)
print "Simulation outputs generated successfully!"