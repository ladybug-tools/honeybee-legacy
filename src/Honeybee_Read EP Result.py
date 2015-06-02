# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to zones.  For results related to surfaces, you should use the "Honeybee_Read EP Surface Result" component.

-
Provided by Honeybee 0.0.56
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
        normByFloorArea_: Set to 'True' to normalize all zone energy data by floor area (note that the resulting units will be kWh/m2 as EnergyPlus runs in the metric system).  The default is set to "False."
    Returns:
        totalThermalEnergy: The total thermal energy used by each zone in kWh.  This includes cooling and heating.
        thermalEnergyBalance: The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative.
        cooling: The cooling energy needed in kWh. For Ideal Air loads, this is the sum of sensible and latent heat that must be removed from each zone.  For distributed OpenStudio systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone. For central OpenStudio systems, this ouput will be a single list for the whole building.
        heating: The heating energy needed in kWh. For Ideal Air loads, this is the sum of sensible heat that must be added to each zone.  For distributed OpenStudio Systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone. For central OpenStudio systems, this ouput will be a single list for the whole building.
        electricLight: The electric lighting energy needed for each zone in kWh.
        electricEquip: The electric equipment energy needed for each zone in kWh.
        fanElectric: The fan electric energy for a central heating or cooling system in kWh.  This ouput will not appear when there is no central system.
        peopleGains: The internal heat gains in each zone resulting from people (kWh).
        totalSolarGain: The total solar gain in each zone(kWh).
        infiltrationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        natVentEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from natural ventilation (kWh).
        operativeTemperature: The mean operative temperature of each zone (degrees Celcius).
        airTemperature: The mean air temperature of each zone (degrees Celcius).
        meanRadTemperature: The mean radiant temperature of each zone (degrees Celcius).
        relativeHumidity: The relative humidity of each zone (%).
        airFlowVolume: The total volume of air flowing into the room through both the windows and infiltration (m3/s).  This is voulme of air is at standard density (20 C and adjusted for the elevation above sea level of the weather file).
        airHeatGainRate: The total heat transfer rate to the air from lighting, equipment(appliances/pulg loads), people, the surfaces of the zone, and gains through the heating system.  This output is useful for the estimation of air stratification in the Comfort Analysis workflow.
        otherZoneData: Other zone data that is in the result file (in no particular order).  Note that this data cannot be normalized by floor area as the component does not know if it can be normalized.
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readEPResult'
ghenv.Component.Message = 'VER 0.0.56\nJUN_02_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nMAY_02_2015
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc
import copy
import os

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
        if not os.path.isfile(eioFileAddress):
            # try to find the file from the list
            studyFolder = os.path.dirname(_resultFileAddress)
            fileNames = os.listdir(studyFolder)
            for fileName in fileNames:
                if fileName.lower().endswith("eio"):
                    eioFileAddress = os.path.join(studyFolder, fileName)
                    break
                    
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
        try: eioResult.close()
        except: pass 
        warning = 'Your simulation probably did not run correctly. \n' + \
                  'Check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If there are no severe or fatal errors, the issue could just be that there is .eio file adjacent to the .csv _resultFileAddress. \n'+ \
                  'Check the folder of the file address you are plugging into this component and make sure that there is both a .csv and .eio file in the folder.'
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
totalThermalEnergy = DataTree[Object]()
thermalEnergyBalance = DataTree[Object]()
cooling = DataTree[Object]()
heating = DataTree[Object]()
electricLight = DataTree[Object]()
electricEquip = DataTree[Object]()
fanElectric = DataTree[Object]()
peopleGains = DataTree[Object]()
totalSolarGain = DataTree[Object]()
infiltrationEnergy = DataTree[Object]()
natVentEnergy = DataTree[Object]()
operativeTemperature = DataTree[Object]()
airTemperature = DataTree[Object]()
meanRadTemperature = DataTree[Object]()
relativeHumidity = DataTree[Object]()
airFlowVolume = DataTree[Object]()
airHeatGainRate = DataTree[Object]()
otherZoneData = DataTree[Object]()

#Create py lists to hold the sirflow data.
infiltrationFlow = []
natVentFlow = []
earthTubeFlow = []
internalAirGain = []
surfaceAirGain = []
systemAirGain = []
testTracker = []
try:
    for zone in zoneNameList:
        infiltrationFlow.append([])
        natVentFlow.append([])
        earthTubeFlow.append([])
        internalAirGain.append([])
        surfaceAirGain.append([])
        systemAirGain.append([])
        testTracker.append([])
except: pass

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
parseSuccess = False
centralSys = False

#If the energy values are set to be normalized, make the units in kWh/m2.
energyUnit = "kWh"

#Make a function to add headers.
def makeHeader(list, path, zoneName, timestep, name, units, normable):
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    list.Add(location, GH_Path(path))
    if normByFlr == False or normable == False: list.Add(name + " for" + zoneName, GH_Path(path))
    else: list.Add("Floor Normalized " + name + " for" + zoneName, GH_Path(path))
    if normByFlr == False or normable == False: list.Add(units, GH_Path(path))
    else: list.Add(units+"/m2", GH_Path(path))
    list.Add(timestep, GH_Path(path))
    list.Add(start, GH_Path(path))
    list.Add(end, GH_Path(path))

def makeHeaderAlt(list, path, zoneName, timestep, name, units, normable):
    thePath = GH_Path(int(path[0]), int(path[1]))
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", thePath)
    list.Add(location, thePath)
    if normByFlr == False or normable == False: list.Add(name + " for" + zoneName, thePath)
    else: list.Add("Floor Normalized " + name + " for" + zoneName, thePath)
    if normByFlr == False or normable == False: list.Add(units, thePath)
    else: list.Add(units+"/m2", thePath)
    list.Add(timestep, thePath)
    list.Add(start, thePath)
    list.Add(end, thePath)

#Make a function to check the zone name.
def checkZone(csvName):
    zoneName = None
    
    for count, name in enumerate(zoneNameList):
        if name == csvName:
            zoneName = name
            path.append(count)
    
    return zoneName

def checkZoneSys(sysInt):
    zoneName = zoneNameList[int(sysInt)-1]
    path.append(int(sysInt)-1)
    return zoneName

def checkCentralSys(sysInt, sysType):
    if sysType == 0: zoneName = " Chiller " + str(sysInt)
    elif sysType == 1: zoneName = " Boiler " + str(sysInt)
    elif sysType == 2: zoneName = " Fan" + str(sysInt)
    else: zoneName = 'Unknown'
    path.append(int(sysInt)-1)
    
    return zoneName

def checkZoneOther(dataIndex, csvName):
    zoneName = None
    for count, name in enumerate(zoneNameList):
        if name == csvName:
            zoneName = name
            path.append([count, dataIndex[count]])
            dataIndex[count] += 1
    return zoneName

dataIndex = []
for name in zoneNameList:
    dataIndex.append(0)


# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                key = []; path = []
                for columnCount, column in enumerate(line.split(',')):
                    if 'Zone Ideal Loads Supply Air Total Cooling Energy' in column or 'Zone Packaged Terminal Heat Pump Total Cooling Energy' in column or 'Chiller Electric Energy' in column:
                        key.append(0)
                        if 'Zone Ideal Loads Supply Air Total Cooling Energy' in column and 'ZONEHVAC' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split('ZONEHVAC')[0])
                            if zoneName == None: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' ZONEHVAC')[0])
                        elif 'IDEAL LOADS AIR SYSTEM' in column: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS AIR SYSTEM')[0])
                        elif 'ZONE HVAC PACKAGED TERMINAL HEAT PUMP' in column: zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('ZONE HVAC PACKAGED TERMINAL HEAT PUMP ')[-1])
                        elif 'Chiller Electric Energy' in column:
                            zoneName = checkCentralSys(1, 0)
                            centralSys = True
                        else: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(cooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Cooling Energy", energyUnit, True)
                        dataTypeList[2] = True
                    
                    elif 'Zone Ideal Loads Supply Air Total Heating Energy' in column or 'Zone Packaged Terminal Heat Pump Total Heating Energy' in column or 'Boiler Heating Energy' in column:
                        key.append(1)
                        if 'Zone Ideal Loads Supply Air Total Heating Energy' in column and 'ZONEHVAC' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split('ZONEHVAC')[0])
                            if zoneName == None: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' ZONEHVAC')[0])
                        elif 'IDEAL LOADS AIR SYSTEM' in column: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS AIR SYSTEM')[0])
                        elif 'ZONE HVAC PACKAGED TERMINAL HEAT PUMP' in column: zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('ZONE HVAC PACKAGED TERMINAL HEAT PUMP ')[-1])
                        elif 'Boiler Heating Energy' in column:
                            zoneName = checkCentralSys(1, 1)
                            centralSys = True
                        else: zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Energy", energyUnit, True)
                        dataTypeList[3] = True
                    
                    elif 'Zone Lights Electric Energy' in column:
                        key.append(2)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(electricLight, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Lighting Energy", energyUnit, True)
                        dataTypeList[4] = True
                    
                    elif 'Zone Electric Equipment Electric Energy' in column:
                        key.append(3)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(electricEquip, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Equipment Energy", energyUnit, True)
                        dataTypeList[5] = True
                    
                    elif 'Fan Electric Energy' in column:
                        key.append(15)
                        if 'FAN CONSTANT VOLUME' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('FAN CONSTANT VOLUME ')[-1])
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, True)
                        elif 'FAN VARIABLE VOLUME' in column:
                            centralSys = True
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('FAN VARIABLE VOLUME ')[-1], 2)
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, True)
                        elif 'Zone Ventilation Fan Electric Energy' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, True)
                        elif 'Earth Tube Fan Electric Energy' in column:
                            zoneName = checkZoneOther(dataIndex, " " + ":".join(column.split(":")[:-1]))
                            makeHeaderAlt(fanElectric, path[columnCount], zoneName, column.split('(')[-1].split(')')[0], "Earth Tube Fan Electric Energy", energyUnit, True)
                        dataTypeList[6] = True
                    
                    elif 'Zone People Total Heating Energy' in column:
                        key.append(4)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(peopleGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "People Energy", energyUnit, True)
                        dataTypeList[7] = True
                    
                    elif 'Zone Windows Total Transmitted Solar Radiation Energy' in column:
                        key.append(5)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(totalSolarGain, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Total Solar Gain", energyUnit, True)
                        dataTypeList[8] = True
                    
                    elif 'Zone Ventilation Total Heat Loss Energy ' in column:
                        key.append(6)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(natVentEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Natural Ventilation Energy", energyUnit, True)
                        dataTypeList[10] = True
                    
                    elif 'Zone Ventilation Total Heat Gain Energy' in column:
                        key.append(7)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                    
                    elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                        key.append(8)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(infiltrationEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Infiltration Energy", energyUnit, True)
                        dataTypeList[9] = True
                    
                    elif 'Zone Infiltration Total Heat Gain Energy' in column:
                        key.append(9)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                    
                    elif 'Zone Operative Temperature' in column:
                        key.append(10)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(operativeTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Operative Temperature", "C", False)
                        dataTypeList[11] = True
                    
                    elif 'Zone Mean Air Temperature' in column:
                        key.append(11)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(airTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Air Temperature", "C", False)
                        dataTypeList[12] = True
                    
                    elif 'Zone Mean Radiant Temperature' in column:
                        key.append(12)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(meanRadTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Radiant Temperature", "C", False)
                        dataTypeList[13] = True
                    
                    elif 'Zone Air Relative Humidity' in column:
                        key.append(13)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(relativeHumidity, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Relative Humidity", "%", False)
                        dataTypeList[14] = True
                    
                    elif 'Zone Ventilation Standard Density Volume Flow Rate' in column:
                        key.append(16)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        natVentFlow[int(path[-1])].append(zoneName)
                        natVentFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Infiltration Standard Density Volume Flow Rate' in column:
                        key.append(17)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        infiltrationFlow[int(path[-1])].append(zoneName)
                        infiltrationFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Earth Tube Air Flow Volume' in column:
                        key.append(21)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        earthTubeFlow[int(path[-1])].append(zoneName)
                        earthTubeFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Air Heat Balance Internal Convective Heat Gain Rate' in column:
                        key.append(18)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        internalAirGain[int(path[-1])].append(zoneName)
                        internalAirGain[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Air Heat Balance Surface Convection Rate' in column:
                        key.append(19)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        surfaceAirGain[int(path[-1])].append(zoneName)
                        surfaceAirGain[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Air Heat Balance System Air Transfer Rate' in column:
                        key.append(20)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        systemAirGain[int(path[-1])].append(zoneName)
                        systemAirGain[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone' in column and not "System" in column and not "SYSTEM" in column and not "ZONEHVAC" in column and not "Earth Tube" in column:
                        zoneName = checkZoneOther(dataIndex, (" " + ":".join(column.split(":")[:-1])))
                        if zoneName != None:
                            key.append(14)
                            makeHeaderAlt(otherZoneData, path[columnCount], zoneName, column.split('(')[-1].split(')')[0], column.split(':')[-1].split(' [')[0], column.split('[')[-1].split(']')[0], False)
                            dataTypeList[17] = True
                        else:
                            key.append(-1)
                            path.append(-1)
                    
                    else:
                        key.append(-1)
                        path.append(-1)
                    
                #print key
                #print path
            else:
                for columnCount, column in enumerate(line.split(',')):
                    if key[columnCount] != 14:
                        try: p = GH_Path(int(path[columnCount]))
                        except: p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    else:
                        p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    
                    if key[columnCount] == 0:
                        try: cooling.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[2] = False
                    elif key[columnCount] == 1:
                        try: heating.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[3] = False
                    elif key[columnCount] == 2:
                        try: electricLight.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[4] = False
                    elif key[columnCount] == 3:
                        try: electricEquip.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[5] = False
                    elif key[columnCount] == 4:
                        try: peopleGains.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[6] = False
                    elif key[columnCount] == 5:
                        try: totalSolarGain.Add((float(column)/3600000)/flrArea, p)
                        except: dataTypeList[7] = False
                    elif key[columnCount] == 6:
                        try: natVentEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                        except: dataTypeList[10] = False
                    elif key[columnCount] == 7:
                        pass
                    elif key[columnCount] == 8:
                        try: infiltrationEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                        except: dataTypeList[9] = False
                    elif key[columnCount] == 9:
                        pass
                    elif key[columnCount] == 10:
                        try: operativeTemperature.Add(float(column), p)
                        except: dataTypeList[11] = True
                    elif key[columnCount] == 11:
                        try: airTemperature.Add(float(column), p)
                        except: dataTypeList[12] = True
                    elif key[columnCount] == 12:
                        try: meanRadTemperature.Add(float(column), p)
                        except: dataTypeList[13] = True
                    elif key[columnCount] == 13:
                        try: relativeHumidity.Add(float(column), p)
                        except: dataTypeList[14] = True
                    elif key[columnCount] == 14:
                        try: otherZoneData.Add(float(column), p)
                        except: pass
                    elif key[columnCount] == 15:
                        try: fanElectric.Add((float(column)/3600000)/flrArea, p)
                        except: pass
                    elif key[columnCount] == 16:
                        try: natVentFlow[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 17:
                        try: infiltrationFlow[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 21:
                        try: earthTubeFlow[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 18:
                        try: internalAirGain[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 19:
                        try: surfaceAirGain[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 20:
                        try: systemAirGain[int(path[columnCount])].append(float(column))
                        except: pass
                    
        result.close()
        parseSuccess = True
    except:
        try: result.close()
        except: pass
        parseSuccess = False
        warn = 'Failed to parse the result file.  Check the folder of the file address you are plugging into this component and make sure that there is a .csv file in the folder. \n'+ \
                  'If there is no csv file or there is a file with no data in it (it is 0 kB), your simulation probably did not run correctly. \n' + \
                  'In this case, check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If the csv file is there and it seems like there is data in it (it is not 0 kB), you are probably requesting an output that this component does not yet handle well. \n' + \
                  'If you report this bug of reading the output on the GH forums, we should be able to fix this component to accept the output soon.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)



#Construct the total energy and energy balance outputs.  Also, construct the total solar and operative temperature outputs
def createPyList(ghTree):
    pyList = []
    for i in range(ghTree.BranchCount):
        branchList = ghTree.Branch(i)
        branchval = []
        for item in branchList:
            branchval.append(item)
        pyList.append(branchval)
    return pyList

#If we have both heating and cooling data, generate a list for total thermal energy and the thermal energy balance.
heatingPyList = None
if dataTypeList[2] == True and dataTypeList[3] == True:
    coolingPyList = createPyList(cooling)
    heatingPyList = createPyList(heating)
    
    if len(coolingPyList) > 0 and len(heatingPyList) > 0:
        for listCount, list in enumerate(coolingPyList):
            makeHeader(totalThermalEnergy, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Total Thermal Energy", energyUnit, True)
            for numCount, num in enumerate(list[7:]):
                totalThermalEnergy.Add((num + heatingPyList[listCount][7:][numCount]), GH_Path(listCount))
            dataTypeList[0] = True
            
            makeHeader(thermalEnergyBalance, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Thermal Energy Balance", energyUnit, True)
            for numCount, num in enumerate(list[7:]):
                thermalEnergyBalance.Add((heatingPyList[listCount][7:][numCount] - num), GH_Path(listCount))
            dataTypeList[1] = True

# If we have information on gains through the air, group them all into a total air gains list.
if internalAirGain != testTracker and surfaceAirGain != testTracker:
    for listCount, list in enumerate(internalAirGain):
        makeHeader(airHeatGainRate, listCount, list[0], list[1], "Air Heat Gain Rate", "W", False)
        if systemAirGain == testTracker:
            for numCount, num in enumerate(list[2:]):
                airHeatGainRate.Add((num + surfaceAirGain[listCount][2:][numCount]), GH_Path(listCount))
        else:
            for numCount, num in enumerate(list[2:]):
                airHeatGainRate.Add((num + surfaceAirGain[listCount][2:][numCount] + systemAirGain[listCount][2:][numCount]), GH_Path(listCount))
        
        dataTypeList[16] = True

#If we have information on volumetric flow for infiltration, natural ventilation, and/or eartht tube flow, add them together.
if infiltrationFlow != testTracker:
    #Check if there are earth tubes.
    earthTubeThere = []
    for earthList in earthTubeFlow:
        if len(earthList) != 0: earthTubeThere.append(1)
        else: earthTubeThere.append(0)
    
    #Add everything together.
    for listCount, list in enumerate(infiltrationFlow):
        makeHeader(airFlowVolume, listCount, list[0], list[1], "Air Flow Volume", "m3/s", False)
        for numCount, num in enumerate(list[2:]):
            try:
                if earthTubeThere[listCount] == 1: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]+ earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
                else: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]), GH_Path(listCount))
            except:
                if earthTubeThere[listCount] == 1: airFlowVolume.Add((num + earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
                else: airFlowVolume.Add(num, GH_Path(listCount))
        dataTypeList[15] = True


#If some of the component outputs are not in the result csv file, blot the variable out of the component.
outputsDict = {
     
0: ["totalThermalEnergy", "The total thermal energy used by each zone in kWh.  This includes cooling and heating."],
1: ["thermalEnergyBalance", "The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative."],
2: ["cooling", "The cooling energy needed in kWh. For Ideal Air loads, this is the sum of sensible and latent heat that must be removed from each zone.  For distributed OpenStudio systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone. For central OpenStudio systems, this ouput will be a single list of chiller electric energy for the whole building."],
3: ["heating", "The heating energy needed in kWh. For Ideal Air loads, this is the sum of sensible and latent heat that must be removed from each zone.  For distributed OpenStudio systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone.  For central OpenStudio systems, this ouput will be a single list of boiler heat energy for the whole building."],
4: ["electricLight", "The electric lighting energy needed for each zone in kWh."],
5: ["electricEquip", "The electric equipment energy needed for each zone in kWh."],
6: ["fanElectric", "The fan electric energy for a central heating or cooling system in kWh.  This ouput will not appear when there is no central system assigned in OpenStudio."],
7: ["peopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
8: ["totalSolarGain", "The total solar gain in each zone(kWh)."],
9: ["infiltrationEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
10: ["natVentEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from natural ventilation (kWh)."],
11: ["operativeTemperature", "The mean operative temperature of each zone (degrees Celcius)."],
12: ["airTemperature", "The mean air temperature of each zone (degrees Celcius)."],
13: ["meanRadTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
14: ["relativeHumidity", "The relative humidity of each zone (%)."],
15: ["airFlowVolume", "The total volume of air flowing into the room through both the windows and infiltration (m3/s).  This is voulme of air is at standard density (20 C and adjusted for the elevation above sea level of the weather file)."],
16: ["airHeatGainRate", "The total heat transfer rate to the air from lighting, equipment(appliances/pulg loads), people, the surfaces of the zone, and gains through the heating system.  This output is useful for the estimation of air stratification in the Comfort Analysis workflow."],
17: ["otherZoneData", "Other zone data that is in the result file (in no particular order). Note that this data cannot be normalized by floor area as the component does not know if it can be normalized."]
}

if _resultFileAddress and parseSuccess == True:
    for output in range(18):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(18):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
