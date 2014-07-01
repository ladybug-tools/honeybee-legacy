# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component

-
Provided by Honeybee 0.0.53
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
    Returns:
        zoneEndUseIntensity: The total energy per unit floor area used by each zone in kWh/m2.
        zoneTotalEnergy: The total energy used by each zone in kWh.
        zoneCooling: The ideal air load cooling energy needed for each zone in kWh.
        zoneHeating: The ideal air load heating energy needed for each zone in kWh.
        zoneElectricLight: The electric lighting energy needed for each zone in kWh.
        zoneElectricEquip: The electric equipment energy needed for each zone in kWh.
        zonePeopleGains: The internal heat gains in each zone resulting from people (kWh).
        zoneBeamGains: The direct solar beam gain in each zone(kWh).
        zoneDiffGains: The diffuse solar gain in each zone(kWh).
        zoneInfiltrationEnergyFlow: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        zoneAirTemperature: The mean air temperature of each zone (degrees Celcius).
        zoneMeanRadiantTemperature: The mean radiant temperature of each zone (degrees Celcius).
        zoneRelativeHumidity: The relative humidity of each zone (%).
        surfaceOpaqueIndoorTemp: The indoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazIndoorTemp: The indoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueOutdoorTemp: The outdoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazOutdoorTemp: The outdoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueEnergyFlow: The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh).
        surfaceGlazEnergyFlow: The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains.
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readIdf'
ghenv.Component.Message = 'VER 0.0.53\nJUL_01_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc
import copy


#Read the location and the analysis period info from the eio file, if there is one.
#Also try to read the floor areas from this file to be used in EUI calculations.
location = "NoLocation"
start = "NoDate"
end = "NoDate"
floorAreaList = []
gotFloors = False

if _resultFileAddress:
    try:
        numZonesLine = 0
        numZonesIndex = 0
        zoneAreaLines = []
        areaIndex = 0
        
        eioFileAddress = _resultFileAddress[0:-3] + "eio"
        eioResult = open(eioFileAddress, 'r')
        for lineCount, line in enumerate(eioResult):
            if "Site:Location," in line:
                location = line.split(",")[1].split("WMO")[0]
            elif "WeatherFileRunPeriod" in line:
                start = (int(line.split(",")[3].split("/")[0]), int(line.split(",")[3].split("/")[1]), 1)
                end = (int(line.split(",")[4].split("/")[0]), int(line.split(",")[4].split("/")[1]), 24)
            elif "Zone Summary" in line and "Number of Zones" in line:
                for index, text in enumerate(line.split(",")):
                    numZonesLine = lineCount+1
                    if "Number of Zones" in text: numZonesIndex = index
                    else: pass
            elif lineCount == numZonesLine:
                numZones = line.split(",")[numZonesIndex]
            elif "Zone Information" in line and "Floor Area {m2}" in line:
                zoneAreaLines = range(lineCount+1, lineCount+1+int(numZones))
                for index, text in enumerate(line.split(",")):
                    if "Floor Area {m2}" in text: areaIndex = index
                    else: pass
            elif lineCount in zoneAreaLines:
                floorAreaList.append(float(line.split(",")[areaIndex]))
                gotFloors = True
            else: pass
        eioResult.close()
    except:
        warning = 'No .eio file was found adjacent to the .csv _resultFileAddress.'+ \
                  'EUI cannot be calculated and headers will be made with no location or run period data.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else: pass


# Make data tree objects for all of the outputs.
zoneEndUseIntensity = DataTree[Object]()
zoneTotalEnergy = DataTree[Object]()
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
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]


# PARSE THE RESULT FILE.
if _resultFileAddress:
    result = open(_resultFileAddress, 'r')
    
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
                if 'Zone Air System Sensible Cooling Energy' in column:
                    key.append(0)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneCooling.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add("Cooling Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneCooling.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[2] = True
                
                elif 'Zone Air System Sensible Heating Energy' in column:
                    key.append(1)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneHeating.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add("Heating Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneHeating.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[3] = True
                
                elif 'Zone Lights Electric Energy' in column:
                    key.append(2)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneElectricLight.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add("Electric Lighting Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneElectricLight.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[4] = True
                
                elif 'Zone Electric Equipment Electric Energy' in column:
                    key.append(3)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneElectricEquip.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add("Electric Equipment Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneElectricEquip.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[5] = True
                
                elif 'Zone People Total Heating Energy' in column:
                    key.append(4)
                    path.append([column.split(':')[0].split('_')[1]])
                    zonePeopleGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add("People Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zonePeopleGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[6] = True
                
                elif 'Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy' in column:
                    key.append(5)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneBeamGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add("Solar Beam Energy for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneBeamGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[7] = True
                
                elif 'Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy' in column:
                    key.append(6)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneDiffGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add("Solar Diffuse Energy for Zone" + " " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneDiffGains.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[8] = True
                
                elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                    key.append(7)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneInfiltrationEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add("Infiltration Energy Loss/Gain for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneInfiltrationEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[9] = True
                
                elif 'Zone Infiltration Total Heat Gain Energy' in column:
                    key.append(8)
                    path.append([column.split(':')[0].split('_')[1]])
                
                elif 'Zone Mean Air Temperature' in column:
                    key.append(9)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneAirTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add("Air Temperature for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add("C", GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneAirTemperature.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[10] = True
                
                elif 'Zone Mean Radiant Temperature' in column:
                    key.append(10)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneMeanRadiantTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add("Radiant Temperature for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add("C", GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneMeanRadiantTemperature.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[11] = True
                
                elif 'Zone Air Relative Humidity' in column:
                    key.append(11)
                    path.append([column.split(':')[0].split('_')[1]])
                    zoneRelativeHumidity.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(location, GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add("Relative Humidity for Zone " + str(path[columnCount][0]), GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add("%", GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(start, GH_Path(int(path[columnCount][0])))
                    zoneRelativeHumidity.Add(end, GH_Path(int(path[columnCount][0])))
                    dataTypeList[12] = True
                
                elif 'Surface Inside Face Temperature' in column and len(column.split('_')) == 4:
                    key.append(12)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("Indoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[13] = True
                
                elif 'Surface Inside Face Temperature' in column and 'Face' in column.split(' ') and 'Temperature' in column.split(' ') and len(column.split('_')) == 7:
                    key.append(13)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add("Indoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[14] = True
                
                elif 'Surface Outside Face Temperature' in column and len(column.split('_')) == 4:
                    key.append(14)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("Outdoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[15] = True
                
                elif 'Surface Outside Face Temperature' in column and len(column.split('_')) == 7:
                    key.append(15)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add("Outdoor Surface Temperature for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[16] = True
                
                elif 'Surface Average Face Conduction Heat Transfer Energy' in column and len(column.split('_')) == 4:
                    key.append(16)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3]])
                    surfaceOpaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[17] = True
                
                elif 'Surface Window Heat Gain Energy' in column and len(column.split('_')) == 7:
                    key.append(17)
                    path.append([column.split(':')[0].split('_')[1], column.split(':')[0].split('_')[3], column.split(':')[0].split('_')[5]])
                    surfaceGlazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add("Glazing Energy Loss/Gain for Zone " + str(path[columnCount][0]) + " Surface " + str(path[columnCount][1]) + " Window " + str(path[columnCount][2]), GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    surfaceGlazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1]), int(path[columnCount][2])))
                    dataTypeList[18] = True
                
                elif 'Surface Window Heat Loss Energy' in column and len(column.split('_')) == 7:
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


#Construct the total energy and EUI outputs.
coolingPyList = []
heatingPyList = []
lightingPyList = []
equipmentPyList = []
for i in range(zoneCooling.BranchCount):
    branchList = zoneCooling.Branch(i)
    coolingval = []
    for item in branchList:
        coolingval.append(item)
    coolingPyList.append(coolingval)
for i in range(zoneHeating.BranchCount):
    branchList = zoneHeating.Branch(i)
    heatingval = []
    for item in branchList:
        heatingval.append(item)
    heatingPyList.append(heatingval)
for i in range(zoneElectricLight.BranchCount):
    branchList = zoneElectricLight.Branch(i)
    lightingval = []
    for item in branchList:
        lightingval.append(item)
    lightingPyList.append(lightingval)
for i in range(zoneElectricEquip.BranchCount):
    branchList = zoneElectricEquip.Branch(i)
    equipval = []
    for item in branchList:
        equipval.append(item)
    equipmentPyList.append(equipval)

if len(coolingPyList) > 0 and len(heatingPyList) > 0 and len(lightingPyList) > 0 and len(equipmentPyList) > 0:
    for listCount, list in enumerate(coolingPyList):
        zoneTotalEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneTotalEnergy.Add(location, GH_Path(listCount))
        zoneTotalEnergy.Add("Total Energy for Zone " + str(listCount), GH_Path(listCount))
        zoneTotalEnergy.Add("kWh", GH_Path(listCount))
        zoneTotalEnergy.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneTotalEnergy.Add(start, GH_Path(listCount))
        zoneTotalEnergy.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneTotalEnergy.Add((num + heatingPyList[listCount][7:][numCount] + lightingPyList[listCount][7:][numCount] + equipmentPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[1] = True

if len(coolingPyList) > 0 and len(heatingPyList) > 0 and len(lightingPyList) > 0 and len(equipmentPyList) > 0 and gotFloors == True:
    for listCount, list in enumerate(coolingPyList):
        zoneEndUseIntensity.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneEndUseIntensity.Add(location, GH_Path(listCount))
        zoneEndUseIntensity.Add("Total Energy per Floor Area for Zone " + str(listCount), GH_Path(listCount))
        zoneEndUseIntensity.Add("kWh/m2", GH_Path(listCount))
        zoneEndUseIntensity.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneEndUseIntensity.Add(start, GH_Path(listCount))
        zoneEndUseIntensity.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneEndUseIntensity.Add(((num + heatingPyList[listCount][7:][numCount] + lightingPyList[listCount][7:][numCount] + equipmentPyList[listCount][7:][numCount])/floorAreaList[listCount]), GH_Path(listCount))
        dataTypeList[0] = True


#If some of the component outputs are not in the result csv file, blot the variable out of the component.
outputsDict = {
     
0: ["zoneEndUseIntensity", "The total energy per unit floor area used by each zone in kWh per square Rhino model units."],
1: ["zoneTotalEnergy", "The total energy used by each zone in kWh."],
2: ["zoneCooling", "The ideal air load cooling energy needed for each zone in kWh."],
3: ["zoneHeating", "The ideal air load heating energy needed for each zone in kWh."],
4: ["zoneElectricLight", "The electric lighting energy needed for each zone in kWh."],
5: ["zoneElectricEquip", "The electric equipment energy needed for each zone in kWh."],
6: ["zonePeopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
7: ["zoneBeamGains", "The direct solar beam gain in each zone(kWh)."],
8: ["zoneDiffGains", "The diffuse solar gain in each zone(kWh)."],
9: ["zoneInfiltrationEnergyFlow", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
10: ["zoneAirTemperature", "The mean air temperature of each zone (degrees Celcius)."],
11: ["zoneMeanRadiantTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
12: ["zoneRelativeHumidity", "The relative humidity of each zone (%)."],
13: ["surfaceOpaqueIndoorTemp", "The indoor surface temperature of each opaque surface (degrees Celcius)."],
14: ["surfaceGlazIndoorTemp", "The indoor surface temperature of each glazed surface (degrees Celcius)."],
15: ["surfaceOpaqueOutdoorTemp", "The outdoor surface temperature of each opaque surface (degrees Celcius)."],
16: ["surfaceGlazOutdoorTemp", "The outdoor surface temperature of each glazed surface (degrees Celcius)."],
17: ["surfaceOpaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
18: ["surfaceGlazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."]
}

if _resultFileAddress:
    for output in range(19):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(19):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
