# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component helps select simulation outputs that can be hooked into the WriteIDF component

-
Provided by Honeybee 0.0.53
    
    Args:
        zoneEnergyUse: Set to "True" to have EnergyPlus solve for basic building energy use such as heating, cooling, electricity for lights and electricity for plug loads.
        zoneGainsAndLosses: Set to "True" to have EnergyPlus solve for building gains and losses such as people gains, solar gains, infiltration losses, and conduction losses through windows.
        zoneTemperatures: Set to "True" to have EnergyPlus solve for the mean air temperatures and mean radiante temperatures of the zones.
        surfaceAnalysis: Set to "True" to have EnergyPlus solve for an number of factors that relate to the individual surfaces bodering each zone, such as gains and losses through the opaque exterior envelope as well as surface temperatures for interior and exterior surfaces.
        ____________________: ...
        timestep: Specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annually'.
    Returns:
        report: Report!
        simulationOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "writeIDF" component.
"""

ghenv.Component.Name = "Honeybee_Write EP Result Parameters"
ghenv.Component.NickName = 'writeResultParameters'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "3"




def main(zoneEnergyUse, zoneGainsAndLosses, zoneTemperatures, surfaceAnalysis, timestep):
    simulationOutputs = []
    timePeriod = timestep + ";"
    
    simulationOutputs.append("OutputControl:Table:Style,Comma;")
    
    if zoneEnergyUse == True:
        simulationOutputs.append("Output:Meter,Heating:*, " + timePeriod)
        simulationOutputs.append("Output:Meter,Cooling:*, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Lights Total Heat Gain, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Electric Equipment Total Heat Gain, " + timePeriod)
    else:
        pass
    
    if zoneGainsAndLosses == True:
        simulationOutputs.append("Output:Variable,*,Zone Beam Solar from Exterior Windows Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Diff Solar from Exterior Windows Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone People Total Heat Gain, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Loss, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Window Heat Loss Energy, " + timePeriod)
    else:
        pass
    
    if zoneTemperatures == True:
        simulationOutputs.append("Output:Variable,*,Zone Mean Air Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Radiant Temperature, " + timePeriod)
    else:
        pass
    
    if surfaceAnalysis == True:
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Solar Radiation Heat Gain Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Net Thermal Radiation Heat Gain Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Convection Heat Gain Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Inside Face Temperature, " + timePeriod)
    else:
        pass
    
    return simulationOutputs



#Check the inputs to be sure that the right data types are selected.
if zoneEnergyUse == True or zoneEnergyUse == False:
    checkdata1 = True
else:
    checkdata1 = False
    print "Please connect a valid boolean value for zoneEnergyUse"

if zoneGainsAndLosses == True or zoneGainsAndLosses == False:
    checkdata2 = True
else:
    checkdata2 = False
    print "Please connect a valid boolean value for zoneGainsAndLosses"

if zoneTemperatures == True or zoneTemperatures == False:
    checkdata3 = True
else:
    checkdata3 = False
    print "Please connect a valid boolean value for zoneTemperatures"

if surfaceAnalysis == True or surfaceAnalysis == False:
    checkdata4 = True
else:
    checkdata4 = False
    print "Please connect a valid boolean value for surfaceAnalysis"

if timestep == "monthly" or timestep == "hourly" or timestep == "daily" or timestep == "annually":
    checkdata5 = True
else:
    checkdata5 = False
    print "Please specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annually'"


#Generate the simulation outputs if the above checks are sucessful.
if checkdata1 == True and checkdata2 == True and checkdata3 == True and checkdata4 == True and checkdata5 == True:
    simulationOutputs = main(zoneEnergyUse, zoneGainsAndLosses, zoneTemperatures, surfaceAnalysis, timestep)
    print "Simulation outputs generated successfully!"
else:
    simulationOutputs = []
    print "Simulation output generation unsuccessful"