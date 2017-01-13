#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to zones.  For results related to surfaces, you should use the "Honeybee_Read EP Surface Result" component.

-
Provided by Honeybee 0.0.60
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
    Returns:
        totalThermalLoad: The total thermal energy used by each zone in kWh.  This includes cooling and heating.
        thermalLoadBalance: The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative.
        cooling: The cooling energy needed in kWh. For Ideal Air loads, this output is the sum of sensible and latent heat that must be removed from each zone.  For detailed HVAC systems (other than ideal air), this output will be electric energy needed to power each chiller/cooling coil.
        heating: The heating energy needed in kWh. For Ideal Air loads, this is the heat that must be added to each zone.  For detailed HVAC systems (other than ideal air), this will be fuel energy or electric energy needed for each boiler/heating element.
        electricLight: The electric lighting energy needed for each zone in kWh.
        electricEquip: The electric equipment energy needed for each zone in kWh.
        fanElectric: The fan electric energy in kWh for either a natural ventilation fan or a heating or cooling system fan.  This ouput will not appear when there is no fan in the model.
        pumpElectric: The water pump electric energy in kWh for a heating or cooling system.  This ouput will not appear when there is no water pump in the model.
        peopleGains: The internal heat gains in each zone resulting from people (kWh).
        totalSolarGain: The total solar gain in each zone(kWh).
        infiltrationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        mechVentilationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from the outdoor air coming through the HVAC System (kWh).
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
ghenv.Component.Message = 'VER 0.0.60\nOCT_05_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
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

#Check to be sure that the files exist.
csvExists = True
if _resultFileAddress and _resultFileAddress != None:
    if not os.path.isfile(_resultFileAddress):
        csvExists = False
        warning = 'The result file does not exist.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


#Read the location and the analysis period info from the eio file, if there is one.
#Also try to read the floor areas from this file to be used in EUI calculations.
location = "NoLocation"
start = "NoDate"
end = "NoDate"
zoneNameList = []
floorAreaList = []
gotData = False

if _resultFileAddress and csvExists == True:
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


# Make data tree objects for all of the outputs.
totalThermalLoad = DataTree[Object]()
thermalLoadBalance = DataTree[Object]()
cooling = DataTree[Object]()
heating = DataTree[Object]()
electricLight = DataTree[Object]()
electricEquip = DataTree[Object]()
fanElectric = DataTree[Object]()
pumpElectric = DataTree[Object]()
peopleGains = DataTree[Object]()
totalSolarGain = DataTree[Object]()
infiltrationEnergy = DataTree[Object]()
mechVentilationEnergy = DataTree[Object]()
natVentEnergy = DataTree[Object]()
operativeTemperature = DataTree[Object]()
airTemperature = DataTree[Object]()
meanRadTemperature = DataTree[Object]()
relativeHumidity = DataTree[Object]()
airFlowVolume = DataTree[Object]()
airHeatGainRate = DataTree[Object]()
otherZoneData = DataTree[Object]()

#Create py lists to hold the airflow data.
infiltrationFlow = []
natVentFlow = []
mechSysAirFlow = []
earthTubeFlow = []
zoneHeatingEnergy = []
zoneCoolingEnergy = []
internalAirGain = []
surfaceAirGain = []
systemAirGain = []
testTracker = []
try:
    for zone in zoneNameList:
        infiltrationFlow.append([])
        natVentFlow.append([])
        mechSysAirFlow.append([])
        earthTubeFlow.append([])
        zoneHeatingEnergy.append([])
        zoneCoolingEnergy.append([])
        internalAirGain.append([])
        surfaceAirGain.append([])
        systemAirGain.append([])
        testTracker.append([])
except: pass

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
parseSuccess = False

#If the energy values are set to be normalized, make the units in kWh/m2.
energyUnit = "kWh"
idealAirTrigger = False
centTrigger = False

#Make a function to add headers.
def makeHeader(list, path, zoneName, timestep, name, units, normable):
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    list.Add(location, GH_Path(path))
    list.Add(name + " for" + zoneName, GH_Path(path))
    list.Add(units, GH_Path(path))
    list.Add(timestep, GH_Path(path))
    list.Add(start, GH_Path(path))
    list.Add(end, GH_Path(path))

def makeHeaderAlt(list, path, zoneName, timestep, name, units, normable):
    thePath = GH_Path(int(path[0]), int(path[1]))
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", thePath)
    list.Add(location, thePath)
    list.Add(name + " for" + zoneName, thePath)
    list.Add(units, thePath)
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

def checkSys(sysInt, sysType):
    zoneName = " " + sysType + " " + str(sysInt)
    path.append(int(sysInt)-1+len(zoneNameList))
    return zoneName

customCount = 0
def checkCustomName(customInt):
    path.append(len(zoneNameList)+len(zoneNameList)+len(zoneNameList)+int(customInt))

def checkCentralSys(sysInt, sysType):
    if sysType == 0: zoneName = " Chiller " + str(sysInt)
    elif sysType == 1: zoneName = " Boiler " + str(sysInt)
    elif sysType == 2: zoneName = " Fan" + str(sysInt)
    elif sysType == 3: zoneName = " Pump" + str(sysInt)
    elif sysType == 4: zoneName = " Humidifier" + str(sysInt)
    elif sysType == 5: zoneName = " VRF Heat Pump" + str(sysInt)
    else: zoneName = 'Unknown'
    if sysType != 4:
        path.append(len(zoneNameList)+int(sysInt))
    else:
        path.append(len(zoneNameList)+len(zoneNameList)+int(sysInt))
    
    return zoneName

def checkZoneOther(dataIndex, csvName):
    zoneName = None
    for count, name in enumerate(zoneNameList):
        if name == csvName:
            zoneName = name
            path.append([count, dataIndex[count]])
            dataIndex[count] += 1
    return zoneName

otherCount = 0
def checkOther(name, otherCount):
    path.append([len(zoneNameList)+1,otherCount])
    return ' Site'

dataIndex = []
for name in zoneNameList:
    dataIndex.append(0)


# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True and csvExists == True:
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                key = []; path = []
                for columnCount, column in enumerate(line.split(',')):
                    
                    if 'Zone Ideal Loads Supply Air Total Cooling Energy' in column or 'Chiller Electric Energy' in column or 'Cooling Coil Electric Energy' in column or 'Zone VRF Air Terminal Cooling Electric Energy' in column or 'VRF Heat Pump Cooling Electric Energy' in column:
                        
                        if 'Zone Ideal Loads Supply Air Total Cooling Energy' in column and 'ZONE HVAC' in column:
                            zoneName = checkZoneSys(" " + (":".join(column.split(":")[:-1])).split('ZONE HVAC IDEAL LOADS AIR SYSTEM ')[-1])
                            idealAirTrigger = True
                        elif 'IDEAL LOADS AIR SYSTEM' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS AIR SYSTEM')[0])
                            idealAirTrigger = True
                        elif 'COIL COOLING DX SINGLE SPEED' in column:
                            zoneName = checkSys(" " + ":".join(column.split(":")[:-1]).split('COIL COOLING DX SINGLE SPEED ')[-1], 'DX Cooling Coil')
                            idealAirTrigger = False
                        elif 'COIL COOLING DX TWO SPEED' in column:
                            zoneName = checkSys(" " + ":".join(column.split(":")[:-1]).split('COIL COOLING DX TWO SPEED ')[-1], 'DX Cooling Coil')
                            idealAirTrigger = False
                        elif 'ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW ')[-1])
                            idealAirTrigger = False
                        elif 'VRF HEAT PUMP -' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('VRF HEAT PUMP - ')[-1], 5)
                            idealAirTrigger = False
                        elif 'Chiller Electric Energy' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('CHILLER ELECTRIC EIR ')[-1], 0)
                            idealAirTrigger = False
                        else:
                            zoneName = " " +column.split(":")[0]
                            checkCustomName(customCount)
                            customCount+=1
                        
                        try:
                            if idealAirTrigger == True:
                                makeHeader(cooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Cooling Load", energyUnit, True)
                            else:
                                makeHeader(cooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Cooling Electric Energy", energyUnit, True)
                            dataTypeList[2] = True
                            key.append(0)
                        except:
                            key.append(-1)
                    
                    elif 'Zone Ideal Loads Supply Air Total Heating Energy' in column  or 'Boiler Heating Energy' in column or 'Heating Coil Total Heating Energy' in column or 'Heating Coil Gas Energy' in column or 'Heating Coil Electric Energy' in column or 'Humidifier Electric Energy' in column or 'Zone VRF Air Terminal Heating Electric Energy' in column or 'VRF Heat Pump Heating Electric Energy' in column:
                        notFound = False
                        if 'Zone Ideal Loads Supply Air Total Heating Energy' in column and 'ZONE HVAC' in column:
                            zoneName = checkZoneSys(" " + (":".join(column.split(":")[:-1])).split('ZONE HVAC IDEAL LOADS AIR SYSTEM ')[-1])
                            idealAirTrigger = True
                        elif 'IDEAL LOADS AIR SYSTEM' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS AIR SYSTEM')[0])
                            idealAirTrigger = True
                        elif 'COIL HEATING DX SINGLE SPEED' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('COIL HEATING DX SINGLE SPEED ')[-1])
                            idealAirTrigger = 2
                        elif 'COIL HEATING GAS' in column and not 'Heating Coil Electric Energy' in column:
                            zoneName = checkSys(" " + ":".join(column.split(":")[:-1]).split('COIL HEATING GAS ')[-1], 'Gas Coil')
                            idealAirTrigger = False
                        elif 'COIL HEATING ELECTRIC' in column:
                            zoneName = checkSys(" " + ":".join(column.split(":")[:-1]).split('COIL HEATING ELECTRIC ')[-1], 'Electric Coil')
                            idealAirTrigger = 2
                        elif 'ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW' in column and not 'Heating Coil Total Heating Energy' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW ')[-1])
                            idealAirTrigger = 2
                        elif 'VRF HEAT PUMP -' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('VRF HEAT PUMP - ')[-1], 5)
                            idealAirTrigger = 2
                        elif 'Boiler Heating Energy' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('BOILER HOT WATER ')[-1], 1)
                            idealAirTrigger = False
                        elif 'HUMIDIFIER STEAM ELECTRIC' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('HUMIDIFIER STEAM ELECTRIC ')[-1], 4)
                            idealAirTrigger = 2
                        else:
                            zoneName = " " +column.split(":")[0]
                            checkCustomName(customCount)
                            customCount+=1
                        
                        try:
                            if idealAirTrigger == True:
                                makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Load", energyUnit, True)
                            elif idealAirTrigger == False:
                                makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Fuel Energy", energyUnit, False)
                            else:
                                makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Electric Energy", energyUnit, False)
                            dataTypeList[3] = True
                            key.append(1)
                        except:
                            key.append(-1)
                    
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
                            centTrigger = True
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('FAN CONSTANT VOLUME ')[-1], 2)
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        elif 'FAN VARIABLE VOLUME' in column:
                            fanNum = int(":".join(column.split(":")[:-1]).split('FAN VARIABLE VOLUME ')[-1])
                            if centTrigger == True:
                                fanNum = fanNum+len(zoneNameList)
                            zoneName = checkCentralSys(" " + str(fanNum), 2)
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        elif 'FAN ON OFF' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('FAN ON OFF ')[-1])
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        elif 'ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW'  in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(" FAN:")[:-1]).split('ZONE HVAC TERMINAL UNIT VARIABLE REFRIGERANT FLOW ')[-1])
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        elif 'Zone Ventilation Fan Electric Energy' in column:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        elif 'Earth Tube Fan Electric Energy' in column:
                            zoneName = checkZoneOther(dataIndex, " " + ":".join(column.split(":")[:-1]))
                            makeHeaderAlt(fanElectric, path[columnCount], zoneName, column.split('(')[-1].split(')')[0], "Earth Tube Fan Electric Energy", energyUnit, False)
                        else:
                            zoneName = " " +column.split(":")[0]
                            checkCustomName(customCount)
                            customCount+=1
                            makeHeader(fanElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Fan Electric Energy", energyUnit, False)
                        dataTypeList[6] = True
                    
                    elif 'Pump Electric Energy' in column:
                        key.append(25)
                        if 'PUMP CONSTANT SPEED' in column:
                            zoneName = checkZoneSys(" " + ":".join(column.split(":")[:-1]).split('PUMP CONSTANT SPEED ')[-1])
                            makeHeader(pumpElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Pump Electric Energy", energyUnit, True)
                        elif 'PUMP VARIABLE SPEED' in column:
                            zoneName = checkCentralSys(" " + ":".join(column.split(":")[:-1]).split('PUMP VARIABLE SPEED ')[-1], 3)
                            makeHeader(pumpElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Pump Electric Energy", energyUnit, True)
                        else:
                            zoneName = " " + column.split(":")[0]
                            checkCustomName(customCount)
                            customCount+=1
                            makeHeader(pumpElectric, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Pump Electric Energy", energyUnit, True)
                        dataTypeList[7] = True
                    
                    elif 'Zone People Total Heating Energy' in column:
                        key.append(4)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(peopleGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "People Energy", energyUnit, True)
                        dataTypeList[8] = True
                    
                    elif 'Zone Windows Total Transmitted Solar Radiation Energy' in column:
                        key.append(5)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(totalSolarGain, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Total Solar Gain", energyUnit, True)
                        dataTypeList[9] = True
                    
                    elif 'Zone Ventilation Sensible Heat Loss Energy ' in column:
                        key.append(6)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(natVentEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Natural Ventilation Energy", energyUnit, True)
                        dataTypeList[12] = True
                    
                    elif 'Zone Ventilation Sensible Heat Gain Energy' in column:
                        key.append(7)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                    
                    elif 'Zone Ideal Loads Zone Total Heating Energy' in column:
                        key.append(23)
                        if 'Zone Ideal Loads Zone Total Heating Energy' in column and 'ZONE HVAC' in column:
                            zoneName = checkZoneSys(" " + (":".join(column.split(":")[:-1])).split('ZONE HVAC IDEAL LOADS AIR SYSTEM ')[-1])
                        else:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS')[0])
                        zoneHeatingEnergy[int(path[-1])].append(zoneName)
                        zoneHeatingEnergy[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Ideal Loads Zone Total Cooling Energy' in column:
                        key.append(24)
                        if 'Zone Ideal Loads Zone Total Cooling Energy' in column and 'ZONE HVAC' in column:
                            zoneName = checkZoneSys(" " + (":".join(column.split(":")[:-1])).split('ZONE HVAC IDEAL LOADS AIR SYSTEM ')[-1])
                        else:
                            zoneName = checkZone(" " + ":".join(column.split(":")[:-1]).split(' IDEAL LOADS')[0])
                        zoneCoolingEnergy[int(path[-1])].append(zoneName)
                        zoneCoolingEnergy[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
                    elif 'Zone Infiltration Total Heat Loss Energy' in column:
                        key.append(8)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(infiltrationEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Infiltration Energy", energyUnit, True)
                        dataTypeList[10] = True
                    
                    elif 'Zone Infiltration Total Heat Gain Energy' in column:
                        key.append(9)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                    
                    elif 'Zone Operative Temperature' in column:
                        key.append(10)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(operativeTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Operative Temperature", "C", False)
                        dataTypeList[13] = True
                    
                    elif 'Zone Mean Air Temperature' in column:
                        key.append(11)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(airTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Air Temperature", "C", False)
                        dataTypeList[14] = True
                    
                    elif 'Zone Mean Radiant Temperature' in column:
                        key.append(12)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(meanRadTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Radiant Temperature", "C", False)
                        dataTypeList[15] = True
                    
                    elif 'Zone Air Relative Humidity' in column:
                        key.append(13)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        makeHeader(relativeHumidity, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Relative Humidity", "%", False)
                        dataTypeList[16] = True
                    
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
                    
                    elif 'Zone Mechanical Ventilation Standard Density Volume Flow Rate' in column:
                        key.append(22)
                        zoneName = checkZone(" " + ":".join(column.split(":")[:-1]))
                        mechSysAirFlow[int(path[-1])].append(zoneName)
                        mechSysAirFlow[int(path[-1])].append(column.split('(')[-1].split(')')[0])
                    
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
                    
                    elif ('Zone' in column or 'Site' in column) and not "Setpoint Not Met Time" in column or "Pump Electric Energy" in column:
                        if "Site" in column:
                            zoneName = checkOther(column, otherCount)
                            otherCount += 1
                        elif not "System" in column and not "SYSTEM" in column and not "ZONEHVAC" in column:
                            zoneName = checkZoneOther(dataIndex, (" " + ":".join(column.split(":")[:-1])))
                        elif 'IDEAL LOADS' in column and not "Supply Air Sensible" in column and not "Supply Air Latent" in column:
                            zoneName = checkZoneOther(dataIndex, (" " + column.split(" IDEAL LOADS")[0]))
                        else: zoneName = None
                        
                        if zoneName != None:
                            key.append(14)
                            otherDataName = column.split(':')[-1].split(' [')[0].upper()
                            if "ENERGY" in otherDataName or "GAIN" in otherDataName or "MASS" in otherDataName or "VOLUME" in otherDataName or "Loss" in otherDataName: normalizble = True
                            else: normalizble = False
                            makeHeaderAlt(otherZoneData, path[columnCount], zoneName, column.split('(')[-1].split(')')[0], column.split(':')[-1].split(' [')[0], column.split('[')[-1].split(']')[0], normalizble)
                            dataTypeList[19] = True
                        else:
                            key.append(-1)
                            path.append(-1)
                    
                    else:
                        key.append(-1)
                        path.append(-1)
            
            else:
                for columnCount, column in enumerate(line.split(',')):
                    if key[columnCount] != 14:
                        try: p = GH_Path(int(path[columnCount]))
                        except: p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    else:
                        p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                    
                    if key[columnCount] == 0:
                        try: cooling.Add((float(column)/3600000), p)
                        except: dataTypeList[2] = False
                    elif key[columnCount] == 1:
                        try: heating.Add((float(column)/3600000), p)
                        except: dataTypeList[3] = False
                    elif key[columnCount] == 2:
                        try: electricLight.Add((float(column)/3600000), p)
                        except: dataTypeList[4] = False
                    elif key[columnCount] == 3:
                        try: electricEquip.Add((float(column)/3600000), p)
                        except: dataTypeList[5] = False
                    elif key[columnCount] == 4:
                        try: peopleGains.Add((float(column)/3600000), p)
                        except: dataTypeList[6] = False
                    elif key[columnCount] == 5:
                        try: totalSolarGain.Add((float(column)/3600000), p)
                        except: dataTypeList[7] = False
                    elif key[columnCount] == 6:
                        try: natVentEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000)), p)
                        except: dataTypeList[11] = False
                    elif key[columnCount] == 7:
                        pass
                    elif key[columnCount] == 23:
                        try: zoneHeatingEnergy[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 24:
                        try: zoneCoolingEnergy[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 8:
                        try: infiltrationEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000)), p)
                        except: dataTypeList[9] = False
                    elif key[columnCount] == 9:
                        pass
                    elif key[columnCount] == 10:
                        try: operativeTemperature.Add(float(column), p)
                        except: dataTypeList[12] = False
                    elif key[columnCount] == 11:
                        try: airTemperature.Add(float(column), p)
                        except: dataTypeList[13] = False
                    elif key[columnCount] == 12:
                        try: meanRadTemperature.Add(float(column), p)
                        except: dataTypeList[14] = False
                    elif key[columnCount] == 13:
                        try: relativeHumidity.Add(float(column), p)
                        except: dataTypeList[15] = False
                    elif key[columnCount] == 14:
                        try:
                            otherZoneData.Add(float(column), p)
                        except: pass
                    elif key[columnCount] == 15:
                        try: fanElectric.Add((float(column)/3600000), p)
                        except: pass
                    elif key[columnCount] == 25:
                        try: pumpElectric.Add((float(column)/3600000), p)
                        except: pass
                    elif key[columnCount] == 16:
                        try: natVentFlow[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 17:
                        try: infiltrationFlow[int(path[columnCount])].append(float(column))
                        except: pass
                    elif key[columnCount] == 22:
                        try: mechSysAirFlow[int(path[columnCount])].append(float(column))
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
                  'If there is a file with no data in it (it is 0 kB), your simulation probably did not run correctly. \n' + \
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
if dataTypeList[2] == True and dataTypeList[3] == True and idealAirTrigger == True:
    coolingPyList = createPyList(cooling)
    heatingPyList = createPyList(heating)
    if len(coolingPyList) == len(heatingPyList):
        if len(coolingPyList) > 0 and len(heatingPyList) > 0:
            for listCount, list in enumerate(coolingPyList):
                makeHeader(totalThermalLoad, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Total Thermal Load", energyUnit, True)
                for numCount, num in enumerate(list[7:]):
                    totalThermalLoad.Add((num + heatingPyList[listCount][7:][numCount]), GH_Path(listCount))
                dataTypeList[0] = True
                
                makeHeader(thermalLoadBalance, listCount, list[2].split(' for')[-1], list[4].split('(')[-1].split(')')[0], "Thermal Load Balance", energyUnit, True)
                for numCount, num in enumerate(list[7:]):
                    thermalLoadBalance.Add((heatingPyList[listCount][7:][numCount] - num), GH_Path(listCount))
                dataTypeList[1] = True
            
            #If we have the cooling/heating coil energy and the heat energy added/removed from the zone, compute the portion of the energy balance that the outdoor air is responsible for.
            heatCoolTracker = 0
            if zoneHeatingEnergy != testTracker and zoneCoolingEnergy != testTracker:
                for listCount, list in enumerate(zoneHeatingEnergy):
                    try:
                        makeHeader(mechVentilationEnergy, listCount, list[0], list[1], "Mechanical Ventilation Energy", energyUnit, True)
                        for numCount, num in enumerate(list[2:]):
                            mechVentilationEnergy.Add((num/3600000) - (zoneCoolingEnergy[listCount][2:][numCount]/3600000) - heatingPyList[heatCoolTracker][7:][numCount] + coolingPyList[heatCoolTracker][7:][numCount], GH_Path(listCount))
                        heatCoolTracker += 1
                    except: pass
                dataTypeList[11] = True

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
        
        dataTypeList[18] = True

#If we have information on volumetric flow for infiltration, natural ventilation, and/or eartht tube flow, add them together.
if infiltrationFlow != testTracker:
    #Check if there is natural ventilation.
    natVentThere = []
    for natVentList in natVentFlow:
        if len(natVentList) != 0: natVentThere.append(1)
        else: natVentThere.append(0)
    
    #Check if there is mechanical veniltation.
    mechSysThere = []
    for mechList in mechSysAirFlow:
        if len(mechList) != 0: mechSysThere.append(1)
        else: mechSysThere.append(0)
    
    #Check if there are earth tubes.
    earthTubeThere = []
    for earthList in earthTubeFlow:
        if len(earthList) != 0: earthTubeThere.append(1)
        else: earthTubeThere.append(0)
    
    #Add everything together.
    for listCount, list in enumerate(infiltrationFlow):
        makeHeader(airFlowVolume, listCount, list[0], list[1], "Air Flow Volume", "m3/s", False)
        for numCount, num in enumerate(list[2:]):
            if earthTubeThere[listCount] == 1 and mechSysThere[listCount] == 1 and natVentThere[listCount] == 1: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount] + mechSysAirFlow[listCount][2:][numCount] + earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 1 and mechSysThere[listCount] == 0 and natVentThere[listCount] == 1: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]+ earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 0 and mechSysThere[listCount] == 1 and natVentThere[listCount] == 1: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]+ mechSysAirFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 1 and mechSysThere[listCount] == 1 and natVentThere[listCount] == 0: airFlowVolume.Add((num + mechSysAirFlow[listCount][2:][numCount] + earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 0 and mechSysThere[listCount] == 1 and natVentThere[listCount] == 0: airFlowVolume.Add((num + mechSysAirFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 1 and mechSysThere[listCount] == 0 and natVentThere[listCount] == 0: airFlowVolume.Add((num + earthTubeFlow[listCount][2:][numCount]), GH_Path(listCount))
            elif earthTubeThere[listCount] == 0 and mechSysThere[listCount] == 0 and natVentThere[listCount] == 1: airFlowVolume.Add((num + natVentFlow[listCount][2:][numCount]), GH_Path(listCount))
            else: airFlowVolume.Add(num, GH_Path(listCount))
        dataTypeList[17] = True


#If some of the component outputs are not in the result csv file, blot the variable out of the component.
outputsDict = {
     
0: ["totalThermalLoad", "The total thermal energy used by each zone in kWh.  This includes cooling and heating."],
1: ["thermalLoadBalance", "The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative. This is useful for computing balance points."],
2: ["cooling", "The cooling energy needed in kWh. For Ideal Air loads, this output is the sum of sensible and latent heat that must be removed from each zone.  For detailed HVAC systems (other than ideal air), this output will be electric energy needed to power each chiller/cooling coil."],
3: ["heating", "The heating energy needed in kWh. For Ideal Air loads, this is the heat that must be added to each zone.  For detailed HVAC systems (other than ideal air), this will be fuel energy or electric energy needed for each boiler/heating element."],
4: ["electricLight", "The electric lighting energy needed for each zone in kWh."],
5: ["electricEquip", "The electric equipment energy needed for each zone in kWh."],
6: ["fanElectric", "The fan electric energy in kWh for either a natural ventilation fan or a heating or cooling system fan.  This ouput will not appear when there is no fan in the model."],
7: ["pumpElectric", "The water pump electric energy in kWh for a heating or cooling system.  This ouput will not appear when there is no water pump in the model."],
8: ["peopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
9: ["totalSolarGain", "The total solar gain in each zone(kWh)."],
10: ["infiltrationEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
11: ["mechVentilationEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from the outdoor air coming through the HVAC System (kWh)."],
12: ["natVentEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from natural ventilation (kWh)."],
13: ["operativeTemperature", "The mean operative temperature of each zone (degrees Celcius)."],
14: ["airTemperature", "The mean air temperature of each zone (degrees Celcius)."],
15: ["meanRadTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
16: ["relativeHumidity", "The relative humidity of each zone (%)."],
17: ["airFlowVolume", "The total volume of air flowing into the room through both the windows and infiltration (m3/s).  This is voulme of air is at standard density (20 C and adjusted for the elevation above sea level of the weather file)."],
18: ["airHeatGainRate", "The total heat transfer rate to the air from lighting, equipment(appliances/pulg loads), people, the surfaces of the zone, and gains through the heating system.  This output is useful for the estimation of air stratification in the Comfort Analysis workflow."],
19: ["otherZoneData", "Other zone data that is in the result file (in no particular order). Note that this data cannot be normalized by floor area as the component does not know if it can be normalized."]
}

if _resultFileAddress and parseSuccess == True:
    for output in range(20):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
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
