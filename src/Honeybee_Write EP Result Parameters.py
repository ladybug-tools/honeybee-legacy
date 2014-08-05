# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component helps select simulation outputs that can be hooked into the WriteIDF component.  Outputs are taken from here:
http://apps1.eere.energy.gov/buildings/energyplus/pdfs/inputoutputreference.pdf

-
Provided by Honeybee 0.0.53
    
    Args:
        facilityProperties_: Set to "True" to have EnergyPlus solve for the total electricity consumed by the building, total CO2 impact, and number of occupants present.
        zoneEnergyUse_: Set to "True" to have EnergyPlus solve for basic building energy use such as heating, cooling, electricity for lights and electricity for plug loads.
        zoneGainsAndLosses_: Set to "True" to have EnergyPlus solve for building gains and losses such as people gains, solar gains, infiltration losses, and conduction losses through windows.
        zoneTemperatures_: Set to "True" to have EnergyPlus solve for the mean air temperatures and mean radiante temperatures of the zones.
        zoneHVACParams_: Set to "True" to have EnergyPlus solve for the flow rate of air into the zone and the nethalpy of this air.
        surfaceAnalysis_: Set to "True" to have EnergyPlus solve for an number of factors that relate to the individual surfaces bodering each zone, such as gains and losses through the opaque exterior envelope as well as surface temperatures for interior and exterior surfaces.
         ____________________: ...
        timestep_: Specify a timestep by inputing the words 'hourly', 'daily', 'monthly' or 'annually'.  The default is set to hourly.
    Returns:
        report: Report!
        simulationOutputs: EnergyPlus code that should be plugged into the "simulationOutputs" parameter of the "writeIDF" component.
"""

ghenv.Component.Name = "Honeybee_Write EP Result Parameters"
ghenv.Component.NickName = 'writeResultParameters'
ghenv.Component.Message = 'VER 0.0.53\nAUG_05_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "3"




def main(facilityProperties, zoneEnergyUse, zoneGainsAndLosses, zoneComfortMetrics, surfaceAnalysis, zoneHVACMetrics, timestep):
    simulationOutputs = []
    timePeriod = timestep + ";"
    
    simulationOutputs.append("OutputControl:Table:Style,Comma;")
    
    
    if facilityProperties == True:
        simulationOutputs.append("Output:Variable,*,Environmental Impact Total CO2 Emissions Carbon Equivalent Mass, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Facility Total Purchased Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,People Occupant Count, " + timePeriod)
    else:
        pass
    
    if zoneEnergyUse == True:
        simulationOutputs.append("Output:Variable,*,Zone Air System Sensible Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air System Sensible Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Outdoor Air Total Cooling Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Ideal Loads Outdoor Air Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Lights Electric Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Electric Equipment Electric Energy, " + timePeriod)
    else:
        pass
    
    if zoneGainsAndLosses == True:
        simulationOutputs.append("Output:Variable,*,Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone People Total Heating Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Infiltration Total Heat Gain Energy, " + timePeriod)
    else:
        pass
    
    if zoneComfortMetrics == True:
        simulationOutputs.append("Output:Variable,*,Zone Mean Air Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Mean Radiant Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Zone Air Relative Humidity, " + timePeriod)
    else:
        pass
    
    if zoneHVACMetrics == True:
        simulationOutputs.append("Output:Variable,*,System Node Mass Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Current Density Volume Flow Rate, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Relative Humidity, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,System Node Enthalpy, " + timePeriod)
    else:
        pass
    
    if surfaceAnalysis == True:
        simulationOutputs.append("Output:Variable,*,Surface Outside Face Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Inside Face Temperature, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Average Face Conduction Heat Transfer Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Heat Loss Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Heat Gain Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Beam Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Diffuse Solar Radiation Energy, " + timePeriod)
        simulationOutputs.append("Output:Variable,*,Surface Window Transmitted Solar Radiation Energy, " + timePeriod)
    else:
        pass
    
    return simulationOutputs



#Check the inputs to be sure that the right data types are selected.
if timestep_ == "monthly" or timestep_ == "hourly" or timestep_ == "daily" or timestep_ == "annually": pass
else:timestep_ = "hourly"


#Generate the simulation outputs if the above checks are sucessful.
simulationOutputs = main(facilityProperties_, zoneEnergyUse_, zoneGainsAndLosses_, zoneComfortMetrics_, surfaceAnalysis_, zoneHVACParams_, timestep_)
print "Simulation outputs generated successfully!"