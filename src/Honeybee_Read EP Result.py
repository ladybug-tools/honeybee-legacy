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
        totalIntHeatGain: The total heat gain into each zone in kWh (excluding possible conduction gains through the envelope or gains that might happen through natural ventilation or infiltration).  This includes lighting, equipment(appliances/pulg loads), people, solar gains, and gains through the heating system.  This output is useful for the estimation of air stratification in the Comfort Analysis workflow.
        peopleGains: The internal heat gains in each zone resulting from people (kWh).
        totalSolarGain: The total solar gain in each zone(kWh).
        infiltrationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        natVentEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from natural ventilation (kWh).
        operativeTemperature: The mean operative temperature of each zone (degrees Celcius).
        airTemperature: The mean air temperature of each zone (degrees Celcius).
        meanRadTemperature: The mean radiant temperature of each zone (degrees Celcius).
        relativeHumidity: The relative humidity of each zone (%).
        airFlowVolume: The total volume of air flowing into the room through both the windows and infiltration (m3/s).  This is voulme of air is at standard density (20 C and adjusted for the elevation above sea level of the weather file).
        otherZoneData: Other zone data that is in the result file (in no particular order).  Note that this data cannot be normalized by floor area as the component does not know if it can be normalized.
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readEPResult'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
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
totalThermalEnergy = DataTree[Object]()
thermalEnergyBalance = DataTree[Object]()
cooling = DataTree[Object]()
heating = DataTree[Object]()
electricLight = DataTree[Object]()
electricEquip = DataTree[Object]()
fanElectric = DataTree[Object]()
totalIntHeatGain = DataTree[Object]()
peopleGains = DataTree[Object]()
totalSolarGain = DataTree[Object]()
infiltrationEnergy = DataTree[Object]()
natVentEnergy = DataTree[Object]()
operativeTemperature = DataTree[Object]()
airTemperature = DataTree[Object]()
meanRadTemperature = DataTree[Object]()
relativeHumidity = DataTree[Object]()
airFlowVolume = DataTree[Object]()
otherZoneData = DataTree[Object]()

#Create py lists to hold the sirflow data.
infiltrationFlow = []
natVentFlow = []
testTracker = []
try:
    for zone in zoneNameList:
        infiltrationFlow.append([])
        natVentFlow.append([])
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
    if sysType == 0: zoneName = " Chiller" + sysInt
    elif sysType == 1: zoneName = " Boiler" + sysInt
    elif sysType == 2: zoneName = " Fan" + sysInt
    else: zoneName = 'Unknown'
    path.append(int(sysInt)-1)
    
    return zoneName

def checkZoneOther(dataIndex, csvName):
    zoneName = None
    for count, name in enumerate(zoneNameList):
        if name == csvName:
            zoneName = name
            path.append(count+dataIndex)
    return zoneName
dataIndex = 0


# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                key = []; path = []
                for columnCount, column in enumerate(line.split(',')):
                    if 'Zone Air System Sensible Cooling Energy' in column or 'Zone Ideal Loads Zone Total Cooling Energy' in column or 'Zone Packaged Terminal Heat Pump Total Cooling Energy' in column or 'Chiller Electric Energy' in column:
                        key.append(0)
                        if 'Zone Ideal Loads Zone Total Cooling Energy' in column and 'ZONEHVAC' in column:
                            zoneName = checkZone(" " + column.split(':')[0].split('ZONEHVAC')[0])
                            if zoneName == None: zoneName = checkZone(" " + column.split(':')[0].split(' ZONEHVAC')[0])
                        elif 'IDEAL LOADS AIR SYSTEM' in column: zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        elif 'ZONE HVAC PACKAGED TERMINAL HEAT PUMP' in column: zoneName = checkZoneSys(" " + column.split(':')[0].split('ZONE HVAC PACKAGED TERMINAL HEAT PUMP ')[-1])
                        elif 'CHILLER ELECTRIC EIR' in column:
                            zoneName = checkCentralSys(" " + column.split(':')[0].split('CHILLER ELECTRIC EIR ')[-1], 0)
                            centralSys = True
                        else: zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(cooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Cooling Energy", energyUnit, True)
                        dataTypeList[2] = True
                    
                    elif 'Zone Air System Sensible Heating Energy' in column or 'Zone Ideal Loads Zone Total Heating Energy' in column or 'Zone Packaged Terminal Heat Pump Total Heating Energy' in column or 'Boiler Heating Energy' in column:
                        key.append(1)
                        if 'Zone Ideal Loads Zone Total Heating Energy' in column and 'ZONEHVAC' in column:
                            zoneName = checkZone(" " + column.split(':')[0].split('ZONEHVAC')[0])
                            if zoneName == None: zoneName = checkZone(" " + column.split(':')[0].split(' ZONEHVAC')[0])
                        elif 'IDEAL LOADS AIR SYSTEM' in column: zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        elif 'ZONE HVAC PACKAGED TERMINAL HEAT PUMP' in column: zoneName = checkZoneSys(" " + column.split(':')[0].split('ZONE HVAC PACKAGED TERMINAL HEAT PUMP ')[-1])
                        elif 'BOILER HOT WATER' in column:
                            zoneName = checkCentralSys(" " + column.split(':')[0].split('BOILER HOT WATER ')[-1], 1)
                            centralSys = True
                        else: zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Energy", energyUnit, True)
                        dataTypeList[3] = True
                    
                    elif 'Zone Lights Electric Energy' in column:
                        key.append(2)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(electricLight, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Lighting Energy", energyUnit, True)
                        dataTypeList[4] = True
                    
                    elif 'Zone Electric Equipment Electric Energy' in column:
                        key.append(3)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(electricEquip, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Equipment Energy", energyUnit, True)
                        dataTypeList[5] = True
                    
                    elif 'Fan Electric Energy' in column:
                        key.append(15)
                        if 'FAN CONSTANT VOLUME' in column: zoneName = checkZoneSys(" " + column.split(':')[0].split('FAN CONSTANT VOLUME ')[-1])
                        elif 'FAN VARIABLE VOLUME' in column:
                            centralSys = True
                            zoneName = checkCentralSys(" " + column.split(':')[0].split('FAN VARIABLE VOLUME ')[-1], 2)
                        elif 'Zone Ventilation Fan Electric Energy' in column:
                            zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, True)
                        dataTypeList[6] = True
                    
                    elif 'Zone People Total Heating Energy' in column:
                        key.append(4)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(peopleGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "People Energy", energyUnit, True)
                        dataTypeList[8] = True
                    
                    elif 'Zone Windows Total Transmitted Solar Radiation Energy' in column:
                        key.append(5)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(totalSolarGain, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Total Solar Gain", energyUnit, True)
                        dataTypeList[9] = True
                    
                    elif 'Zone Ventilation Total Heat Loss Energy ' in column:
                        key.append(6)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(natVentEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Natural Ventilation Energy", energyUnit, True)
                        dataTypeList[11] = True
                    
                    elif 'Zone Ventilation Total Heat Gain Energy' in column:
                        key.append(7)
                        zoneName = checkZone(" " + column.split(':')[0])
                    
                    elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                        key.append(8)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(infiltrationEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Infiltration Energy", energyUnit, True)
                        dataTypeList[10] = True
                    
                    elif 'Zone Infiltration Total Heat Gain Energy' in column:
                        key.append(9)
                        zoneName = checkZone(" " + column.split(':')[0])
                    
                    elif 'Zone Operative Temperature' in column:
                        key.append(10)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(operativeTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Operative Temperature", "C", False)
                        dataTypeList[12] = True
                    
                    elif 'Zone Mean Air Temperature' in column:
                        key.append(11)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(airTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Air Temperature", "C", False)
                        dataTypeList[13] = True
                    
                    elif 'Zone Mean Radiant Temperature' in column:
                        key.append(12)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(meanRadTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Radiant Temperature", "C", False)
                        dataTypeList[14] = True
                    
                    elif 'Zone Air Relative Humidity' in column:
                        key.append(13)
                        zoneName = checkZone(" " + column.split(':')[0])
                        makeHeader(relativeHumidity, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Relative Humidity", "%", False)
                        dataTypeList[15] = True
                    
                    elif 'Zone Ventilation Standard Density Volume Flow Rate' in column:
                        key.append(16)
                        zoneName = checkZone(" " + column.split(':')[0])
                        natVentFlow[int(path[-1])].append(zoneName)
                        natVentFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Infiltration Standard Density Volume Flow Rate' in column:
                        key.append(17)
                        zoneName = checkZone(" " + column.split(':')[0])
                        infiltrationFlow[int(path[-1])].append(zoneName)
                        infiltrationFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone' in column and not "System" in column and not "SYSTEM" in column and not "ZONEHVAC" in column:
                        key.append(14)
                        zoneName = checkZoneOther(dataIndex, (" " + column.split(':')[0]))
                        makeHeader(otherZoneData, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], column.split(':')[-1].split(' [')[0], column.split('[')[-1].split(']')[0], False)
                        dataTypeList[17] = True
                        dataIndex += 1
                    
                    else:
                        key.append(-1)
                        path.append(-1)
                    
                #print key
                #print path
            else:
                for columnCount, column in enumerate(line.split(',')):
                    p = GH_Path(int(path[columnCount]))
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    
                    if key[columnCount] == 0:
                        cooling.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 1:
                        heating.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 2:
                        electricLight.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 3:
                        electricEquip.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 4:
                        peopleGains.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 5:
                        totalSolarGain.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 6:
                        natVentEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                    elif key[columnCount] == 7:
                        pass
                    elif key[columnCount] == 8:
                        infiltrationEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                    elif key[columnCount] == 9:
                        pass
                    elif key[columnCount] == 10:
                        operativeTemperature.Add(float(column), p)
                    elif key[columnCount] == 11:
                        airTemperature.Add(float(column), p)
                    elif key[columnCount] == 12:
                        meanRadTemperature.Add(float(column), p)
                    elif key[columnCount] == 13:
                        relativeHumidity.Add(float(column), p)
                    elif key[columnCount] == 14:
                        otherZoneData.Add(float(column), p)
                    elif key[columnCount] == 15:
                        fanElectric.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 16:
                        natVentFlow[int(path[columnCount])].append(float(column))
                    elif key[columnCount] == 17:
                        infiltrationFlow[int(path[columnCount])].append(float(column))
                    
        result.close()
        parseSuccess = True
    except:
        try: result.close()
        except: pass
        parseSuccess = False
        warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
                  'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
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
            dataTypeList[1] = True
            
            makeHeader(thermalEnergyBalance, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Thermal Energy Balance", energyUnit, True)
            for numCount, num in enumerate(list[7:]):
                thermalEnergyBalance.Add((heatingPyList[listCount][7:][numCount] - num), GH_Path(listCount))
            dataTypeList[2] = True

# If we have information on lighting, equipment(appliances/pulg loads), people, solar gains, and gains through the heating system, group them all into a total gains list.
if dataTypeList[4] == True and dataTypeList[5] == True and dataTypeList[8] == True and dataTypeList[9] == True:
    lightingPyList = createPyList(electricLight)
    equipPyList = createPyList(electricEquip)
    peoplePyList = createPyList(peopleGains)
    solarPyList = createPyList(totalSolarGain)
    
    if len(lightingPyList) > 0 and len(equipPyList) > 0 and len(peoplePyList) > 0 and len(solarPyList) > 0:
        for listCount, list in enumerate(lightingPyList):
            makeHeader(totalIntHeatGain, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Total Internal Heat Gain", "kWh", True)
            if heatingPyList == None:
                for numCount, num in enumerate(list[7:]):
                    totalIntHeatGain.Add((num + equipPyList[listCount][7:][numCount] + peoplePyList[listCount][7:][numCount] + solarPyList[listCount][7:][numCount]), GH_Path(listCount))
            else:
                for numCount, num in enumerate(list[7:]):
                    totalIntHeatGain.Add((num + equipPyList[listCount][7:][numCount] + peoplePyList[listCount][7:][numCount] + solarPyList[listCount][7:][numCount] + heatingPyList[listCount][7:][numCount]), GH_Path(listCount))
            
            dataTypeList[7] = True

#If we have information on volumetric flow for infiltration and natural ventilation, add them together.
if infiltrationFlow != testTracker and natVentFlow != testTracker:
    for listCount, list in enumerate(infiltrationFlow):
        makeHeader(airFlowVolume, listCount, list[0], list[1], "Air Flow Volume", "m3/s", False)
        for numCount, num in enumerate(list[2:]):
            try:
                airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]), GH_Path(listCount))
            except:
                airFlowVolume.Add(num, GH_Path(listCount))
        dataTypeList[16] = True


#If some of the component outputs are not in the result csv file, blot the variable out of the component.
outputsDict = {
     
0: ["totalThermalEnergy", "The total thermal energy used by each zone in kWh.  This includes cooling and heating."],
1: ["thermalEnergyBalance", "The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative."],
2: ["cooling", "The cooling energy needed in kWh. For Ideal Air loads, this is the sum of sensible and latent heat that must be removed from each zone.  For distributed OpenStudio systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone. For central OpenStudio systems, this ouput will be a single list of chiller electric energy for the whole building."],
3: ["heating", "The heating energy needed in kWh. For Ideal Air loads, this is the sum of sensible and latent heat that must be removed from each zone.  For distributed OpenStudio systems like Packaged Terminal Heat Pumps (PTHP), this will be electric energy for each zone.  For central OpenStudio systems, this ouput will be a single list of boiler heat energy for the whole building."],
4: ["electricLight", "The electric lighting energy needed for each zone in kWh."],
5: ["electricEquip", "The electric equipment energy needed for each zone in kWh."],
6: ["fanElectric", "The fan electric energy for a central heating or cooling system in kWh.  This ouput will not appear when there is no central system assigned in OpenStudio."],
7: ["totalIntHeatGain", "The total heat gain into each zone in kWh (excluding possible conduction gains through the envelope or gains that might happen through natural ventilation or infiltration).  This includes lighting, equipment(appliances/pulg loads), people, solar gains, and gains through the heating system.  This output is useful for the estimation of air stratification in the Comfort Analysis workflow."],
8: ["peopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
9: ["totalSolarGain", "The total solar gain in each zone(kWh)."],
10: ["infiltrationEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
11: ["natVentEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from natural ventilation (kWh)."],
12: ["operativeTemperature", "The mean operative temperature of each zone (degrees Celcius)."],
13: ["airTemperature", "The mean air temperature of each zone (degrees Celcius)."],
14: ["meanRadTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
15: ["relativeHumidity", "The relative humidity of each zone (%)."],
16: ["airFlowVolume", "The total volume of air flowing into the room through both the windows and infiltration (m3/s).  This is voulme of air is at standard density (20 C and adjusted for the elevation above sea level of the weather file)."],
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
