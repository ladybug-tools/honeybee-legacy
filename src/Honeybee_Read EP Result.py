# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component

-
Provided by Honeybee 0.0.53
    
    Args:
        resultFileAddress: The result file address that comes out of the WriteIDF component.
    Returns:
        zoneCooling: The ideal air load cooling energy needed for each zone in kWh.
        zoneHeating: The ideal air load heating energy needed for each zone in kWh.
        zoneElectricLight: The electric lighting energy needed for each zone in kWh.
        zoneElectricEquip: The electric equipment energy needed for each zone in kWh.
        ====================: ...
        zonePeopleGains: The internal heat gains in each zone resulting from people (kWh).
        zoneBeamGains: The direct solar beam gain in each zone(kWh).
        zoneDiffGains: The diffuse solar gain in each zone(kWh).
        zoneInfiltrationEnergyFlow: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        ====================: ...
        zoneAirTemperature: The mean air temperature of each zone (degrees Celcius).
        zoneMeanRadiantTemperature: The mean radiant temperature of each zone (degrees Celcius).
        zoneRelativeHumidity: The relative humidity of each zone (%).
        ====================: ...
        surfaceOpaqueIndoorTemp: The indoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazIndoorTemp: The indoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueOutdoorTemp: The outdoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazOutdoorTemp: The outdoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueEnergyFlow: The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh).
        surfaceGlazEnergyFlow: The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains.
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readIdf'
ghenv.Component.Message = 'VER 0.0.53\nJUN_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


#Read the location and the analysis period info from the eio file, if there is one.
location = "NoLocation"
timeStep = "Unknown Timestep"
start = "NoDate"
end = "NoDate"

try:
    if resultFileAddress:
        eioFileAddress = resultFileAddress[0:-3] + "eio"
        eioResult = open(eioFileAddress, 'r')
        for lineCount, line in enumerate(eioResult):
            if "Site:Location," in line:
                location = line.split(",")[1].split("WMO")[0]
            elif "WeatherFileRunPeriod" in line:
                start = (int(line.split(",")[3].split("/")[0]), int(line.split(",")[3].split("/")[1]), 1)
                end = (int(line.split(",")[4].split("/")[0]), int(line.split(",")[4].split("/")[1]), 24)
            else: pass
        eioResult.close()
    else: pass
except: pass


# Make data tree objects for all of the outputs.
zoneCooling = DataTree[Object]()
zoneHeating = DataTree[Object]()
zoneElectricLight = DataTree[Object]()
zoneElectricEquip = DataTree[Object]()
zonePeopleGains = DataTree[Object]()
zoneBeamGains = DataTree[Object]()
zoneDiffGains = DataTree[Object]()
zoneInfiltrationEnergyFlow = DataTree[Object]()
zoneAirTemperature = DataTree[Object]()
zoneMeanRadiantTemperature = DataTree[Object]()
zoneRelativeHumidity = DataTree[Object]()
surfaceOpaqueIndoorTemp = DataTree[Object]()
surfaceGlazIndoorTemp = DataTree[Object]()
surfaceOpaqueOutdoorTemp = DataTree[Object]()
surfaceGlazOutdoorTemp = DataTree[Object]()
surfaceOpaqueEnergyFlow = DataTree[Object]()
surfaceGlazEnergyFlow = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, True, False, False, False, False, True, False, False, False, True, False, False, False, False, False, False]


# PARSE THE RESULT FILE.
if resultFileAddress:
    result = open(resultFileAddress, 'r')
    
    for lineCount, line in enumerate(result):
        if lineCount == 0:
            #ANALYZE THE FILE HEADING
            #cooling = 0
            #heating = 1
            #lights = 2
            #equipment = 3
            #people = 4
            #solar beam = 5
            #solar diffuse = 6
            #infiltration loss = 7
            #infiltration gain = 8
            #air temperature = 9
            #radiant temperature = 10
            #relative humidity = 11
            #inside opaque temperature = 12
            #inside glazing temperature = 13
            #outside opaque temperature = 14
            #outside glazing temperature = 15
            #opaque surface energy transfer = 16
            #glazing surface energy gain = 17
            #glazing surface energy loss = 18
            key = []; path = []
            for columnCount, column in enumerate(line.split(',')):
                if 'Zone' in column and 'System' in column and 'Cooling' in column:
                    key.append(0)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneCooling.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add("Cooling Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[0] = True
                
                elif 'Zone' in column and 'System' in column and 'Heating' in column:
                    key.append(1)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneHeating.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add("Heating Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[1] = True
                
                elif 'Zone' in column and 'Lights' in column:
                    key.append(2)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneElectricLight.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add("Electric Lighting Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[2] = True
                
                elif 'Zone' in column and 'Equipment' in column:
                    key.append(3)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneElectricEquip.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add("Electric Equipment Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[3] = True
                
                elif 'Zone' in column and 'People' in column:
                    key.append(4)
                    path.append([column.split(':')[0].split('_')[1]])
                    zonePeopleGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add("People Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[5] = True
                
                elif 'Zone' in column and 'Beam' in column:
                    key.append(5)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneBeamGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add("Solar Beam Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[6] = True
                
                elif 'Zone' in column and 'Diff' in column:
                    key.append(6)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneDiffGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add("Solar Diffuse Energy for Zone" + " " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[7] = True
                
                elif 'Zone' in column and 'Infiltration' in column and 'Loss' in column:
                    key.append(7)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneInfiltrationEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add("Infiltration Energy Loss/Gain for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[8] = True
                
                elif 'Zone' in column and 'Infiltration' in column and 'Gain' in column:
                    key.append(8)
                    path.append([column.split(':')[0].split('_')[1]])
                
                elif 'Zone' in column and 'Air Temperature' in column:
                    key.append(9)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneAirTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add("Air Temperature for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add("C", GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[10] = True
                
                elif 'Zone' in column and 'Radiant Temperature' in column:
                    key.append(10)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneMeanRadiantTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add("Radiant Temperature for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add("C", GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[11] = True
                
                elif 'Zone' in column and 'Relative Humidity' in column:
                    key.append(11)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneRelativeHumidity.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add("Relative Humidity for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add("%", GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(timeStep, GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[12] = True
                
                elif 'Inside' in column.split(' ') and 'Face' in column.split(' ') and 'Temperature' in column.split(' ') and len(column.split('_')) == 4:
                    key.append(12)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("Indoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[14] = True
                
                elif 'Inside' in column.split(' ') and 'Face' in column.split(' ') and 'Temperature' in column.split(' ') and len(column.split('_')) == 7:
                    key.append(13)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add("Indoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[15] = True
                
                elif 'Outside' in column.split(' ') and 'Face' in column.split(' ') and 'Temperature' in column.split(' ') and len(column.split('_')) == 4:
                    key.append(14)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("Outdoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[16] = True
                
                elif 'Outside' in column.split(' ') and 'Face' in column.split(' ') and 'Temperature' in column.split(' ') and len(column.split('_')) == 7:
                    key.append(15)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add("Outdoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[17] = True
                
                elif 'Conduction' in column.split(' ') and 'Face' in column.split(' ') and 'Transfer' in column.split(' ') and len(column.split('_')) == 4:
                    key.append(16)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[18] = True
                
                elif 'Surface' in column and 'Window' in column and 'Gain' in column and len(column.split('_')) == 7:
                    key.append(17)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add("Glazing Energy Loss/Gain for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(timeStep, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[19] = True
                
                elif 'Surface' in column and 'Window' in column and 'Loss' in column and len(column.split('_')) == 7:
                    key.append(18)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                
                else:
                    key.append(-1)
                    path.append(-1)
                
            #print key
            #print path
        else:
            for columnCount, column in enumerate(line.split(',')):
                if key[columnCount] == 0:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneCooling.Add((float(column)/3600000), p)
                elif key[columnCount] == 1:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneHeating.Add((float(column)/3600000), p)
                elif key[columnCount] == 2:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneElectricLight.Add((float(column)/3600000), p)
                elif key[columnCount] == 3:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneElectricEquip.Add((float(column)/3600000), p)
                elif key[columnCount] == 4:
                    p = GH_Path(int(path[columnCount][0]))
                    zonePeopleGains.Add((float(column)/3600000), p)
                elif key[columnCount] == 5:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneBeamGains.Add((float(column)/3600000), p)
                elif key[columnCount] == 6:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneDiffGains.Add((float(column)/3600000), p)
                elif key[columnCount] == 7:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneInfiltrationEnergyFlow.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000)), p)
                elif key[columnCount] == 8:
                    pass
                elif key[columnCount] == 9:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneAirTemperature.Add(float(column), p)
                elif key[columnCount] == 10:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneMeanRadiantTemperature.Add(float(column), p)
                elif key[columnCount] == 11:
                    p = GH_Path(int(path[columnCount][0]))
                    zoneRelativeHumidity.Add(float(column), p)
                elif key[columnCount] == 12:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueIndoorTemp.Add(float(column), p)
                elif key[columnCount] == 13:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2]))
                    surfaceGlazIndoorTemp.Add(float(column), p)
                elif key[columnCount] == 14:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueOutdoorTemp.Add(float(column), p)
                elif key[columnCount] == 15:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2]))
                    surfaceGlazOutdoorTemp.Add(float(column), p)
                elif key[columnCount] == 16:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueEnergyFlow.Add((float(column)/3600000), p)
                elif key[columnCount] == 17:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2]))
                    surfaceGlazEnergyFlow.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                elif key[columnCount] == 18:
                    pass
                
    result.close()


#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["zoneCooling", "The ideal air load cooling energy needed for each zone in kWh."],
1: ["zoneHeating", "The ideal air load heating energy needed for each zone in kWh."],
2: ["zoneElectricLight", "The electric lighting energy needed for each zone in kWh."],
3: ["zoneElectricEquip", "The electric equipment energy needed for each zone in kWh."],
4: ["====================", "..."],
5: ["zonePeopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
6: ["zoneBeamGains", "The direct solar beam gain in each zone(kWh)."],
7: ["zoneDiffGains", "The diffuse solar gain in each zone(kWh)."],
8: ["zoneInfiltrationEnergyFlow", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
9: ["====================", "..."],
10: ["zoneAirTemperature", "The mean air temperature of each zone (degrees Celcius)."],
11: ["zoneMeanRadiantTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
12: ["zoneRelativeHumidity", "The relative humidity of each zone (%)."],
13: ["====================", "..."],
14: ["surfaceOpaqueIndoorTemp", "The indoor surface temperature of each opaque surface (degrees Celcius)."],
15: ["surfaceGlazIndoorTemp", "The indoor surface temperature of each glazed surface (degrees Celcius)."],
16: ["surfaceOpaqueOutdoorTemp", "The outdoor surface temperature of each opaque surface (degrees Celcius)."],
17: ["surfaceGlazOutdoorTemp", "The outdoor surface temperature of each glazed surface (degrees Celcius)."],
18: ["surfaceOpaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
19: ["surfaceGlazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."]
}

if resultFileAddress:
    for output in range(20):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(20):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
