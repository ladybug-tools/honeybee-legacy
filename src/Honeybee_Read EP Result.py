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
        normByFloorArea_: Set to 'True' to normalize all zone energy data by floor area (note that the resulting units will be kWh/m2 as EnergyPlus runs in the metric system).
    Returns:
        zoneTotalEnergy: The total energy used by each zone in kWh.  This includes cooling, heating, lighting, and equipment.
        zoneTotalThermalEnergy: The total thermal energy used by each zone in kWh.  This includes cooling and heating.
        zoneEnergyBalance: The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative.
        zoneCooling: The ideal air load cooling energy needed for each zone in kWh.
        zoneHeating: The ideal air load heating energy needed for each zone in kWh.
        zoneElectricLight: The electric lighting energy needed for each zone in kWh.
        zoneElectricEquip: The electric equipment energy needed for each zone in kWh.
        zonePeopleGains: The internal heat gains in each zone resulting from people (kWh).
        zoneTotalSolarGain: The total solar gain in each zone(kWh).
        zoneBeamGains: The direct solar beam gain in each zone(kWh).
        zoneDiffGains: The diffuse solar gain in each zone(kWh).
        zoneInfiltrationEnergyFlow: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        zoneOperativeTemperature: The mean operative temperature of each zone (degrees Celcius).
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
ghenv.Component.Message = 'VER 0.0.53\nJUL_06_2014'
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
zoneNameList = []
floorAreaList = []
gotData = False

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
                zoneNameList.append(line.split(",")[1])
                floorAreaList.append(float(line.split(",")[areaIndex]))
                gotData = True
            else: pass
        eioResult.close()
    except:
        warning = 'No .eio file was found adjacent to the .csv _resultFileAddress.'+ \
                  'results cannot be read back into grasshopper without this file.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else: pass

#If no value is connected for normByFloorArea_, don't normalize the results.
if normByFloorArea_ == None:
    normByFlr = False
else:
    normByFlr = normByFloorArea_

# If the user has selected to normalize the results, make sure that we were able to pull the floor areas from the results file.
if normByFlr == True and floorAreaList != []:
    normByFlr == True
elif normByFlr == True:
    normByFlr == False
else: pass

# Make data tree objects for all of the outputs.
zoneTotalEnergy = DataTree[Object]()
zoneTotalThermalEnergy = DataTree[Object]()
zoneEnergyBalance = DataTree[Object]()
zoneCooling = DataTree[Object]()
zoneHeating = DataTree[Object]()
zoneElectricLight = DataTree[Object]()
zoneElectricEquip = DataTree[Object]()
zonePeopleGains = DataTree[Object]()
zoneTotalSolarGain = DataTree[Object]()
zoneBeamGains = DataTree[Object]()
zoneDiffGains = DataTree[Object]()
zoneInfiltrationEnergyFlow = DataTree[Object]()
zoneOperativeTemperature = DataTree[Object]()
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
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

#Make a list to keep track of the number of surfaces in each zone.
zoneSrfs = []
for zoneCount, zone in enumerate(floorAreaList):
    zoneSrfs.append([])
    for num in range(7):
        zoneSrfs[zoneCount].append([])

# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
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
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneCooling.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneCooling.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneCooling.Add("Cooling Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zoneCooling.Add("Floor Normalized Cooling Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneCooling.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneCooling.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneCooling.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneCooling.Add(start, GH_Path(int(path[columnCount])))
                    zoneCooling.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[3] = True
                
                elif 'Zone Air System Sensible Heating Energy' in column:
                    key.append(1)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneHeating.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneHeating.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneHeating.Add("Heating Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else:zoneHeating.Add("Floor Normalized Heating Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneHeating.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneHeating.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneHeating.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneHeating.Add(start, GH_Path(int(path[columnCount])))
                    zoneHeating.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[4] = True
                
                elif 'Zone Lights Electric Energy' in column:
                    key.append(2)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneElectricLight.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneElectricLight.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneElectricLight.Add("Electric Lighting Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zoneElectricLight.Add("Floor Normalized Electric Lighting Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneElectricLight.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneElectricLight.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneElectricLight.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneElectricLight.Add(start, GH_Path(int(path[columnCount])))
                    zoneElectricLight.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[5] = True
                
                elif 'Zone Electric Equipment Electric Energy' in column:
                    key.append(3)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneElectricEquip.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneElectricEquip.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneElectricEquip.Add("Electric Equipment Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zoneElectricEquip.Add("Floor Normalized Electric Equipment Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False:zoneElectricEquip.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneElectricEquip.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneElectricEquip.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneElectricEquip.Add(start, GH_Path(int(path[columnCount])))
                    zoneElectricEquip.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[6] = True
                
                elif 'Zone People Total Heating Energy' in column:
                    key.append(4)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zonePeopleGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zonePeopleGains.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zonePeopleGains.Add("People Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zonePeopleGains.Add("Floor Normalized People Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zonePeopleGains.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zonePeopleGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zonePeopleGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zonePeopleGains.Add(start, GH_Path(int(path[columnCount])))
                    zonePeopleGains.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[7] = True
                
                elif 'Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy' in column:
                    key.append(5)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneBeamGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneBeamGains.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False:zoneBeamGains.Add("Solar Beam Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zoneBeamGains.Add("Floor Normalized Solar Beam Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False:zoneBeamGains.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneBeamGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneBeamGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneBeamGains.Add(start, GH_Path(int(path[columnCount])))
                    zoneBeamGains.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[9] = True
                
                elif 'Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy' in column:
                    key.append(6)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneDiffGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneDiffGains.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False:zoneDiffGains.Add("Solar Diffuse Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    else: zoneDiffGains.Add("Floor Normalized Solar Diffuse Energy for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False:zoneDiffGains.Add("kWh", GH_Path(int(path[columnCount])))
                    else: zoneDiffGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneDiffGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneDiffGains.Add(start, GH_Path(int(path[columnCount])))
                    zoneDiffGains.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[10] = True
                
                elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                    key.append(7)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneInfiltrationEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneInfiltrationEnergyFlow.Add(location, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneInfiltrationEnergyFlow.Add("Infiltration Energy Loss/Gain for" + zoneName, GH_Path(int(path[columnCount])))
                    else:zoneInfiltrationEnergyFlow.Add("Floor Normalized Infiltration Energy Loss/Gain for" + zoneName, GH_Path(int(path[columnCount])))
                    if normByFlr == False: zoneInfiltrationEnergyFlow.Add("kWh", GH_Path(int(path[columnCount])))
                    else:zoneInfiltrationEnergyFlow.Add("kWh/m2", GH_Path(int(path[columnCount])))
                    zoneInfiltrationEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneInfiltrationEnergyFlow.Add(start, GH_Path(int(path[columnCount])))
                    zoneInfiltrationEnergyFlow.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[11] = True
                
                elif 'Zone Infiltration Total Heat Gain Energy' in column:
                    key.append(8)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            path.append(count)
                
                elif 'Zone Mean Air Temperature' in column:
                    key.append(9)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneAirTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add(location, GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add("Air Temperature for" + zoneName, GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add("C", GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add(start, GH_Path(int(path[columnCount])))
                    zoneAirTemperature.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[13] = True
                
                elif 'Zone Mean Radiant Temperature' in column:
                    key.append(10)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneMeanRadiantTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add(location, GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add("Radiant Temperature for" + zoneName, GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add("C", GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add(start, GH_Path(int(path[columnCount])))
                    zoneMeanRadiantTemperature.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[14] = True
                
                elif 'Zone Air Relative Humidity' in column:
                    key.append(11)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    zoneRelativeHumidity.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add(location, GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add("Relative Humidity for" + zoneName, GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add("%", GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add(start, GH_Path(int(path[columnCount])))
                    zoneRelativeHumidity.Add(end, GH_Path(int(path[columnCount])))
                    dataTypeList[15] = True
                
                elif 'Surface Inside Face Temperature' in column and "GLZ" not in column:
                    key.append(12)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][0])
                            zoneSrfs[count][0].append(1)
                            path.append([count, srfIndex])
                    surfaceOpaqueIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("Indoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[16] = True
                
                elif 'Surface Inside Face Temperature' in column and "GLZ" in column:
                    key.append(13)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][1])
                            zoneSrfs[count][1].append(1)
                            path.append([count, srfIndex])
                    surfaceGlazIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add("Indoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[17] = True
                
                elif 'Surface Outside Face Temperature' in column and "GLZ" not in column:
                    key.append(14)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][2])
                            zoneSrfs[count][2].append(1)
                            path.append([count, srfIndex])
                    surfaceOpaqueOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("Outdoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[18] = True
                
                elif 'Surface Outside Face Temperature' in column and "GLZ" in column:
                    key.append(15)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][3])
                            zoneSrfs[count][3].append(1)
                            path.append([count, srfIndex])
                    surfaceGlazOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add("Outdoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[19] = True
                
                elif 'Surface Average Face Conduction Heat Transfer Energy' in column and "GLZ" not in column:
                    key.append(16)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][4])
                            zoneSrfs[count][4].append(1)
                            path.append([count, srfIndex])
                    surfaceOpaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceOpaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[20] = True
                
                elif 'Surface Window Heat Gain Energy' in column and "GLZ" in column:
                    key.append(17)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][5])
                            zoneSrfs[count][5].append(1)
                            path.append([count, srfIndex])
                    surfaceGlazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add("Glazing Energy Loss/Gain for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    surfaceGlazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                    dataTypeList[21] = True
                
                elif 'Surface Window Heat Loss Energy' in column and "GLZ" in column:
                    key.append(18)
                    for count, name in enumerate(zoneNameList):
                        if name in " " + column.split(':')[0]:
                            zoneName = name
                            srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                            srfIndex = len(zoneSrfs[count][6])
                            zoneSrfs[count][6].append(1)
                            path.append([count, srfIndex])
                
                else:
                    key.append(-1)
                    path.append(-1)
                
            #print key
            #print path
        else:
            for columnCount, column in enumerate(line.split(',')):
                if key[columnCount] == 0:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneCooling.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 1:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneHeating.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 2:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneElectricLight.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 3:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneElectricEquip.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 4:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zonePeopleGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 5:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneBeamGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 6:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneDiffGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 7:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    zoneInfiltrationEnergyFlow.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                elif key[columnCount] == 8:
                    pass
                elif key[columnCount] == 9:
                    p = GH_Path(int(path[columnCount]))
                    zoneAirTemperature.Add(float(column), p)
                elif key[columnCount] == 10:
                    p = GH_Path(int(path[columnCount]))
                    zoneMeanRadiantTemperature.Add(float(column), p)
                elif key[columnCount] == 11:
                    p = GH_Path(int(path[columnCount]))
                    zoneRelativeHumidity.Add(float(column), p)
                elif key[columnCount] == 12:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueIndoorTemp.Add(float(column), p)
                elif key[columnCount] == 13:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceGlazIndoorTemp.Add(float(column), p)
                elif key[columnCount] == 14:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueOutdoorTemp.Add(float(column), p)
                elif key[columnCount] == 15:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceGlazOutdoorTemp.Add(float(column), p)
                elif key[columnCount] == 16:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceOpaqueEnergyFlow.Add((float(column)/3600000), p)
                elif key[columnCount] == 17:
                    p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    surfaceGlazEnergyFlow.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                elif key[columnCount] == 18:
                    pass
                
    result.close()


#Construct the total energy and energy balance outputs.  Also, construct the total solar and operative temperature outputs
coolingPyList = []
heatingPyList = []
lightingPyList = []
equipmentPyList = []
beamGainPyList = []
diffGainPyList = []
airTempPyList = []
mrtPyList = []
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
for i in range(zoneBeamGains.BranchCount):
    branchList = zoneBeamGains.Branch(i)
    beamval = []
    for item in branchList:
        beamval.append(item)
    beamGainPyList.append(beamval)
for i in range(zoneDiffGains.BranchCount):
    branchList = zoneDiffGains.Branch(i)
    diffval = []
    for item in branchList:
        diffval.append(item)
    diffGainPyList.append(diffval)
for i in range(zoneAirTemperature.BranchCount):
    branchList = zoneAirTemperature.Branch(i)
    airval = []
    for item in branchList:
        airval.append(item)
    airTempPyList.append(airval)
for i in range(zoneMeanRadiantTemperature.BranchCount):
    branchList = zoneMeanRadiantTemperature.Branch(i)
    mrtval = []
    for item in branchList:
        mrtval.append(item)
    mrtPyList.append(mrtval)


if len(coolingPyList) > 0 and len(heatingPyList) > 0 and len(lightingPyList) > 0 and len(equipmentPyList) > 0:
    for listCount, list in enumerate(coolingPyList):
        zoneTotalEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneTotalEnergy.Add(location, GH_Path(listCount))
        if normByFlr == False: zoneTotalEnergy.Add("Total Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: zoneTotalEnergy.Add("Floor Normalized Total Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False: zoneTotalEnergy.Add("kWh", GH_Path(listCount))
        else: zoneTotalEnergy.Add("kWh/m2", GH_Path(listCount))
        zoneTotalEnergy.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneTotalEnergy.Add(start, GH_Path(listCount))
        zoneTotalEnergy.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneTotalEnergy.Add((num + heatingPyList[listCount][7:][numCount] + lightingPyList[listCount][7:][numCount] + equipmentPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[0] = True

if len(coolingPyList) > 0 and len(heatingPyList) > 0:
    for listCount, list in enumerate(coolingPyList):
        zoneTotalThermalEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneTotalThermalEnergy.Add(location, GH_Path(listCount))
        if normByFlr == False:zoneTotalThermalEnergy.Add("Total Thermal Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: zoneTotalThermalEnergy.Add("Floor Normalized Total Thermal Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False:zoneTotalThermalEnergy.Add("kWh", GH_Path(listCount))
        else: zoneTotalThermalEnergy.Add("kWh/m2", GH_Path(listCount))
        zoneTotalThermalEnergy.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneTotalThermalEnergy.Add(start, GH_Path(listCount))
        zoneTotalThermalEnergy.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneTotalThermalEnergy.Add((num + heatingPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[1] = True
        
        zoneEnergyBalance.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneEnergyBalance.Add(location, GH_Path(listCount))
        if normByFlr == False:zoneEnergyBalance.Add("Heating - Cooling Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: zoneEnergyBalance.Add("Floor Normalized Heating - Cooling Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False:zoneEnergyBalance.Add("kWh", GH_Path(listCount))
        else: zoneEnergyBalance.Add("kWh/m2", GH_Path(listCount))
        zoneEnergyBalance.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneEnergyBalance.Add(start, GH_Path(listCount))
        zoneEnergyBalance.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneEnergyBalance.Add((heatingPyList[listCount][7:][numCount] - num), GH_Path(listCount))
        dataTypeList[2] = True

if len(beamGainPyList) > 0 and len(diffGainPyList) > 0:
    for listCount, list in enumerate(beamGainPyList):
        zoneTotalSolarGain.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneTotalSolarGain.Add(location, GH_Path(listCount))
        if normByFlr == False: zoneTotalSolarGain.Add("Total Solar Gain for" + zoneNameList[listCount], GH_Path(listCount))
        else: zoneTotalSolarGain.Add("Floor Normalized Total Solar Gain for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False: zoneTotalSolarGain.Add("kWh", GH_Path(listCount))
        else: zoneTotalSolarGain.Add("kWh/m2", GH_Path(listCount))
        zoneTotalSolarGain.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneTotalSolarGain.Add(start, GH_Path(listCount))
        zoneTotalSolarGain.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneTotalSolarGain.Add((num + diffGainPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[8] = True

if len(airTempPyList) > 0 and len(mrtPyList) > 0:
    for listCount, list in enumerate(airTempPyList):
        zoneOperativeTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        zoneOperativeTemperature.Add(location, GH_Path(listCount))
        zoneOperativeTemperature.Add("Operative Temperature for" + zoneNameList[listCount], GH_Path(listCount))
        zoneOperativeTemperature.Add("C", GH_Path(listCount))
        zoneOperativeTemperature.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        zoneOperativeTemperature.Add(start, GH_Path(listCount))
        zoneOperativeTemperature.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            zoneOperativeTemperature.Add((num + mrtPyList[listCount][7:][numCount])/2, GH_Path(listCount))
        dataTypeList[12] = True

#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["zoneTotalEnergy", "The total energy used by each zone in kWh.  This includes cooling, heating, lighting, and equipment."],
1: ["zoneTotalThermalEnergy", "The total thermal energy used by each zone in kWh.  This includes cooling and heating."],
2: ["zoneEnergyBalance", "The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative."],
3: ["zoneCooling", "The ideal air load cooling energy needed for each zone in kWh."],
4: ["zoneHeating", "The ideal air load heating energy needed for each zone in kWh."],
5: ["zoneElectricLight", "The electric lighting energy needed for each zone in kWh."],
6: ["zoneElectricEquip", "The electric equipment energy needed for each zone in kWh."],
7: ["zonePeopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
8: ["zoneTotalSolarGain", "The total solar gain in each zone(kWh)."],
9: ["zoneBeamGains", "The direct solar beam gain in each zone(kWh)."],
10: ["zoneDiffGains", "The diffuse solar gain in each zone(kWh)."],
11: ["zoneInfiltrationEnergyFlow", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
12: ["zoneOperativeTemperature", "The mean operative temperature of each zone (degrees Celcius)."],
13: ["zoneAirTemperature", "The mean air temperature of each zone (degrees Celcius)."],
14: ["zoneMeanRadiantTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
15: ["zoneRelativeHumidity", "The relative humidity of each zone (%)."],
16: ["surfaceOpaqueIndoorTemp", "The indoor surface temperature of each opaque surface (degrees Celcius)."],
17: ["surfaceGlazIndoorTemp", "The indoor surface temperature of each glazed surface (degrees Celcius)."],
18: ["surfaceOpaqueOutdoorTemp", "The outdoor surface temperature of each opaque surface (degrees Celcius)."],
19: ["surfaceGlazOutdoorTemp", "The outdoor surface temperature of each glazed surface (degrees Celcius)."],
20: ["surfaceOpaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
21: ["surfaceGlazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."]
}

if _resultFileAddress:
    for output in range(22):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(22):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
