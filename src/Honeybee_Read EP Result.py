# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to zones.  For results related to surfaces, you should use the "Honeybee_Read EP Surface Result" component.

-
Provided by Honeybee 0.0.53
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
        normByFloorArea_: Set to 'True' to normalize all zone energy data by floor area (note that the resulting units will be kWh/m2 as EnergyPlus runs in the metric system).
    Returns:
        totalEnergy: The total energy used by each zone in kWh.  This includes cooling, heating, lighting, and equipment.
        totalThermalEnergy: The total thermal energy used by each zone in kWh.  This includes cooling and heating.
        thermalEnergyBalance: The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative.
        cooling: The ideal air load cooling energy needed for each zone in kWh.
        heating: The ideal air load heating energy needed for each zone in kWh.
        electricLight: The electric lighting energy needed for each zone in kWh.
        electricEquip: The electric equipment energy needed for each zone in kWh.
        peopleGains: The internal heat gains in each zone resulting from people (kWh).
        totalSolarGain: The total solar gain in each zone(kWh).
        exterSolarBeamGains: The direct solar beam gain in each zone from exterior windows (kWh).
        exterSolarDiffuseGains: The diffuse solar gain in each zone from exterior windows (kWh).
        infiltrationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        operativeTemperature: The mean operative temperature of each zone (degrees Celcius).
        airTemperature: The mean air temperature of each zone (degrees Celcius).
        meanRadTemperature: The mean radiant temperature of each zone (degrees Celcius).
        relativeHumidity: The relative humidity of each zone (%).
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readEPResult'
ghenv.Component.Message = 'VER 0.0.53\nAUG_06_2014'
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
totalEnergy = DataTree[Object]()
totalThermalEnergy = DataTree[Object]()
thermalEnergyBalance = DataTree[Object]()
cooling = DataTree[Object]()
heating = DataTree[Object]()
electricLight = DataTree[Object]()
electricEquip = DataTree[Object]()
peopleGains = DataTree[Object]()
totalSolarGain = DataTree[Object]()
exterSolarBeamGains = DataTree[Object]()
exterSolarDiffuseGains = DataTree[Object]()
infiltrationEnergy = DataTree[Object]()
operativeTemperature = DataTree[Object]()
airTemperature = DataTree[Object]()
meanRadTemperature = DataTree[Object]()
relativeHumidity = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
parseSuccess = False

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


# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    #try:
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
            key = []; path = []
            for columnCount, column in enumerate(line.split(',')):
                if 'Zone Air System Sensible Cooling Energy' in column or 'Zone Ideal Loads Zone Total Cooling Energy' in column:
                    key.append(0)
                    for count, name in enumerate(zoneNameList):
                        if 'Zone Ideal Loads Zone Total Cooling Energy' in column:
                            if name == " " + column.split(':')[0].split('ZONEHVAC')[0]:
                                zoneName = name
                                path.append(count)
                        else:
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                    makeHeader(cooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Cooling Energy", "kWh", True)
                    dataTypeList[3] = True
                
                elif 'Zone Air System Sensible Heating Energy' in column or 'Zone Ideal Loads Zone Total Heating Energy' in column:
                    key.append(1)
                    for count, name in enumerate(zoneNameList):
                        if 'Zone Ideal Loads Zone Total Heating Energy' in column:
                            if name == " " + column.split(':')[0].split('ZONEHVAC')[0]:
                                zoneName = name
                                path.append(count)
                        else:
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                    makeHeader(heating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Heating Energy", "kWh", True)
                    dataTypeList[4] = True
                
                elif 'Zone Lights Electric Energy' in column:
                    key.append(2)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(electricLight, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Lighting Energy", "kWh", True)
                    dataTypeList[5] = True
                
                elif 'Zone Electric Equipment Electric Energy' in column:
                    key.append(3)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(electricEquip, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Electric Equipment Energy", "kWh", True)
                    dataTypeList[6] = True
                
                elif 'Zone People Total Heating Energy' in column:
                    key.append(4)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(peopleGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "People Energy", "kWh", True)
                    dataTypeList[7] = True
                
                elif 'Zone Windows Total Transmitted Solar Radiation Energy' in column:
                    key.append(5)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(totalSolarGain, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Total Solar Gain", "kWh", True)
                    dataTypeList[8] = True
                
                elif 'Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy' in column:
                    key.append(6)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(exterSolarBeamGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Solar Beam Energy", "kWh", True)
                    dataTypeList[9] = True
                
                elif 'Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy' in column:
                    key.append(7)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(exterSolarDiffuseGains, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Solar Diffuse Energy", "kWh", True)
                    dataTypeList[10] = True
                
                elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                    key.append(8)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(infiltrationEnergy, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Infiltration Energy", "kWh", True)
                    dataTypeList[11] = True
                
                elif 'Zone Infiltration Total Heat Gain Energy' in column:
                    key.append(9)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            path.append(count)
                
                elif 'Zone Operative Temperature' in column:
                    key.append(10)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(operativeTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Operative Temperature", "C", False)
                    dataTypeList[12] = True
                
                elif 'Zone Mean Air Temperature' in column:
                    key.append(11)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(airTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Air Temperature", "C", False)
                    dataTypeList[13] = True
                
                elif 'Zone Mean Radiant Temperature' in column:
                    key.append(12)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(meanRadTemperature, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Radiant Temperature", "C", False)
                    dataTypeList[14] = True
                
                elif 'Zone Air Relative Humidity' in column:
                    key.append(13)
                    for count, name in enumerate(zoneNameList):
                        if name == " " + column.split(':')[0]:
                            zoneName = name
                            path.append(count)
                    makeHeader(relativeHumidity, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Relative Humidity", "%", False)
                    dataTypeList[15] = True
                
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
                    cooling.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 1:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    heating.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 2:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    electricLight.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 3:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    electricEquip.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 4:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    peopleGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 5:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    totalSolarGain.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 6:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    exterSolarBeamGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 7:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    exterSolarDiffuseGains.Add((float(column)/3600000)/flrArea, p)
                elif key[columnCount] == 8:
                    if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                    else: flrArea = 1
                    p = GH_Path(int(path[columnCount]))
                    infiltrationEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                elif key[columnCount] == 9:
                    pass
                elif key[columnCount] == 10:
                    p = GH_Path(int(path[columnCount]))
                    operativeTemperature.Add(float(column), p)
                elif key[columnCount] == 11:
                    p = GH_Path(int(path[columnCount]))
                    airTemperature.Add(float(column), p)
                elif key[columnCount] == 12:
                    p = GH_Path(int(path[columnCount]))
                    meanRadTemperature.Add(float(column), p)
                elif key[columnCount] == 13:
                    p = GH_Path(int(path[columnCount]))
                    relativeHumidity.Add(float(column), p)
                
    result.close()
    parseSuccess = True
    #except:
    #    parseSuccess = False
    #    warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
    #              'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
    #    print warn
    #    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

#Construct the total energy and energy balance outputs.  Also, construct the total solar and operative temperature outputs
coolingPyList = []
heatingPyList = []
lightingPyList = []
equipmentPyList = []
beamGainPyList = []
diffGainPyList = []
airTempPyList = []
mrtPyList = []
for i in range(cooling.BranchCount):
    branchList = cooling.Branch(i)
    coolingval = []
    for item in branchList:
        coolingval.append(item)
    coolingPyList.append(coolingval)
for i in range(heating.BranchCount):
    branchList = heating.Branch(i)
    heatingval = []
    for item in branchList:
        heatingval.append(item)
    heatingPyList.append(heatingval)
for i in range(electricLight.BranchCount):
    branchList = electricLight.Branch(i)
    lightingval = []
    for item in branchList:
        lightingval.append(item)
    lightingPyList.append(lightingval)
for i in range(electricEquip.BranchCount):
    branchList = electricEquip.Branch(i)
    equipval = []
    for item in branchList:
        equipval.append(item)
    equipmentPyList.append(equipval)


if len(coolingPyList) > 0 and len(heatingPyList) > 0 and len(lightingPyList) > 0 and len(equipmentPyList) > 0:
    for listCount, list in enumerate(coolingPyList):
        totalEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        totalEnergy.Add(location, GH_Path(listCount))
        if normByFlr == False: totalEnergy.Add("Total Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: totalEnergy.Add("Floor Normalized Total Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False: totalEnergy.Add("kWh", GH_Path(listCount))
        else: totalEnergy.Add("kWh/m2", GH_Path(listCount))
        totalEnergy.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        totalEnergy.Add(start, GH_Path(listCount))
        totalEnergy.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            totalEnergy.Add((num + heatingPyList[listCount][7:][numCount] + lightingPyList[listCount][7:][numCount] + equipmentPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[0] = True

if len(coolingPyList) > 0 and len(heatingPyList) > 0:
    for listCount, list in enumerate(coolingPyList):
        totalThermalEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        totalThermalEnergy.Add(location, GH_Path(listCount))
        if normByFlr == False:totalThermalEnergy.Add("Total Thermal Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: totalThermalEnergy.Add("Floor Normalized Total Thermal Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False:totalThermalEnergy.Add("kWh", GH_Path(listCount))
        else: totalThermalEnergy.Add("kWh/m2", GH_Path(listCount))
        totalThermalEnergy.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        totalThermalEnergy.Add(start, GH_Path(listCount))
        totalThermalEnergy.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            totalThermalEnergy.Add((num + heatingPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[1] = True
        
        thermalEnergyBalance.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        thermalEnergyBalance.Add(location, GH_Path(listCount))
        if normByFlr == False:thermalEnergyBalance.Add("Heating - Cooling Energy for" + zoneNameList[listCount], GH_Path(listCount))
        else: thermalEnergyBalance.Add("Floor Normalized Heating - Cooling Energy for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False:thermalEnergyBalance.Add("kWh", GH_Path(listCount))
        else: thermalEnergyBalance.Add("kWh/m2", GH_Path(listCount))
        thermalEnergyBalance.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        thermalEnergyBalance.Add(start, GH_Path(listCount))
        thermalEnergyBalance.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            thermalEnergyBalance.Add((heatingPyList[listCount][7:][numCount] - num), GH_Path(listCount))
        dataTypeList[2] = True


#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["totalEnergy", "The total energy used by each zone in kWh.  This includes cooling, heating, lighting, and equipment."],
1: ["totalThermalEnergy", "The total thermal energy used by each zone in kWh.  This includes cooling and heating."],
2: ["thermalEnergyBalance", "The thermal energy used by each zone in kWh.  Heating values are positive while cooling values are negative."],
3: ["cooling", "The ideal air load cooling energy needed for each zone in kWh."],
4: ["heating", "The ideal air load heating energy needed for each zone in kWh."],
5: ["electricLight", "The electric lighting energy needed for each zone in kWh."],
6: ["electricEquip", "The electric equipment energy needed for each zone in kWh."],
7: ["peopleGains", "The internal heat gains in each zone resulting from people (kWh)."],
8: ["totalSolarGain", "The total solar gain in each zone(kWh)."],
9: ["exterSolarBeamGains", "The direct solar beam gain in each zone from exterior windows(kWh)."],
10: ["exterSolarDiffuseGains", "The diffuse solar gain in each zone from exterior windows(kWh)."],
11: ["infiltrationEnergy", "The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh)."],
12: ["operativeTemperature", "The mean operative temperature of each zone (degrees Celcius)."],
13: ["airTemperature", "The mean air temperature of each zone (degrees Celcius)."],
14: ["meanRadTemperature", "The mean radiant temperature of each zone (degrees Celcius)."],
15: ["relativeHumidity", "The relative humidity of each zone (%)."]
}

if _resultFileAddress and parseSuccess == True:
    for output in range(16):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(16):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
