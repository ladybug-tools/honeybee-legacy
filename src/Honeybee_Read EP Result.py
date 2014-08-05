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
        solarBeamGains: The direct solar beam gain in each zone(kWh).
        solarDiffuseGains: The diffuse solar gain in each zone(kWh).
        infiltrationEnergy: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        operativeTemperature: The mean operative temperature of each zone (degrees Celcius).
        airTemperature: The mean air temperature of each zone (degrees Celcius).
        meanRadTemperature: The mean radiant temperature of each zone (degrees Celcius).
        relativeHumidity: The relative humidity of each zone (%).
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readEPResult'
ghenv.Component.Message = 'VER 0.0.53\nAUG_04_2014'
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
solarBeamGains = DataTree[Object]()
solarDiffuseGains = DataTree[Object]()
infiltrationEnergy = DataTree[Object]()
operativeTemperature = DataTree[Object]()
airTemperature = DataTree[Object]()
meanRadTemperature = DataTree[Object]()
relativeHumidity = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
parseSuccess = False

#Make a list to keep track of the number of surfaces in each zone.
zoneSrfs = []
for zoneCount, zone in enumerate(floorAreaList):
    zoneSrfs.append([])
    for num in range(7):
        zoneSrfs[zoneCount].append([])

# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    try:
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
                    if 'Zone Air System Sensible Cooling Energy' in column:
                        key.append(0)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        cooling.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        cooling.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: cooling.Add("Cooling Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: cooling.Add("Floor Normalized Cooling Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False: cooling.Add("kWh", GH_Path(int(path[columnCount])))
                        else: cooling.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        cooling.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        cooling.Add(start, GH_Path(int(path[columnCount])))
                        cooling.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[3] = True
                    
                    elif 'Zone Air System Sensible Heating Energy' in column:
                        key.append(1)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        heating.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        heating.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: heating.Add("Heating Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else:heating.Add("Floor Normalized Heating Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False: heating.Add("kWh", GH_Path(int(path[columnCount])))
                        else: heating.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        heating.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        heating.Add(start, GH_Path(int(path[columnCount])))
                        heating.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[4] = True
                    
                    elif 'Zone Lights Electric Energy' in column:
                        key.append(2)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        electricLight.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        electricLight.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: electricLight.Add("Electric Lighting Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: electricLight.Add("Floor Normalized Electric Lighting Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False: electricLight.Add("kWh", GH_Path(int(path[columnCount])))
                        else: electricLight.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        electricLight.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        electricLight.Add(start, GH_Path(int(path[columnCount])))
                        electricLight.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[5] = True
                    
                    elif 'Zone Electric Equipment Electric Energy' in column:
                        key.append(3)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        electricEquip.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        electricEquip.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: electricEquip.Add("Electric Equipment Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: electricEquip.Add("Floor Normalized Electric Equipment Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False:electricEquip.Add("kWh", GH_Path(int(path[columnCount])))
                        else: electricEquip.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        electricEquip.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        electricEquip.Add(start, GH_Path(int(path[columnCount])))
                        electricEquip.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[6] = True
                    
                    elif 'Zone People Total Heating Energy' in column:
                        key.append(4)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        peopleGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        peopleGains.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: peopleGains.Add("People Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: peopleGains.Add("Floor Normalized People Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False: peopleGains.Add("kWh", GH_Path(int(path[columnCount])))
                        else: peopleGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        peopleGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        peopleGains.Add(start, GH_Path(int(path[columnCount])))
                        peopleGains.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[7] = True
                    
                    elif 'Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy' in column:
                        key.append(5)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        solarBeamGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        solarBeamGains.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False:solarBeamGains.Add("Solar Beam Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: solarBeamGains.Add("Floor Normalized Solar Beam Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False:solarBeamGains.Add("kWh", GH_Path(int(path[columnCount])))
                        else: solarBeamGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        solarBeamGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        solarBeamGains.Add(start, GH_Path(int(path[columnCount])))
                        solarBeamGains.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[9] = True
                    
                    elif 'Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy' in column:
                        key.append(6)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        solarDiffuseGains.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        solarDiffuseGains.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False:solarDiffuseGains.Add("Solar Diffuse Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        else: solarDiffuseGains.Add("Floor Normalized Solar Diffuse Energy for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False:solarDiffuseGains.Add("kWh", GH_Path(int(path[columnCount])))
                        else: solarDiffuseGains.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        solarDiffuseGains.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        solarDiffuseGains.Add(start, GH_Path(int(path[columnCount])))
                        solarDiffuseGains.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[10] = True
                    
                    elif 'Zone Infiltration Total Heat Loss Energy ' in column:
                        key.append(7)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        infiltrationEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        infiltrationEnergy.Add(location, GH_Path(int(path[columnCount])))
                        if normByFlr == False: infiltrationEnergy.Add("Infiltration Energy Loss/Gain for" + zoneName, GH_Path(int(path[columnCount])))
                        else:infiltrationEnergy.Add("Floor Normalized Infiltration Energy Loss/Gain for" + zoneName, GH_Path(int(path[columnCount])))
                        if normByFlr == False: infiltrationEnergy.Add("kWh", GH_Path(int(path[columnCount])))
                        else:infiltrationEnergy.Add("kWh/m2", GH_Path(int(path[columnCount])))
                        infiltrationEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        infiltrationEnergy.Add(start, GH_Path(int(path[columnCount])))
                        infiltrationEnergy.Add(end, GH_Path(int(path[columnCount])))
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
                        airTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        airTemperature.Add(location, GH_Path(int(path[columnCount])))
                        airTemperature.Add("Air Temperature for" + zoneName, GH_Path(int(path[columnCount])))
                        airTemperature.Add("C", GH_Path(int(path[columnCount])))
                        airTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        airTemperature.Add(start, GH_Path(int(path[columnCount])))
                        airTemperature.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[13] = True
                    
                    elif 'Zone Mean Radiant Temperature' in column:
                        key.append(10)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        meanRadTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add(location, GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add("Radiant Temperature for" + zoneName, GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add("C", GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add(start, GH_Path(int(path[columnCount])))
                        meanRadTemperature.Add(end, GH_Path(int(path[columnCount])))
                        dataTypeList[14] = True
                    
                    elif 'Zone Air Relative Humidity' in column:
                        key.append(11)
                        for count, name in enumerate(zoneNameList):
                            if name == " " + column.split(':')[0]:
                                zoneName = name
                                path.append(count)
                        relativeHumidity.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount])))
                        relativeHumidity.Add(location, GH_Path(int(path[columnCount])))
                        relativeHumidity.Add("Relative Humidity for" + zoneName, GH_Path(int(path[columnCount])))
                        relativeHumidity.Add("%", GH_Path(int(path[columnCount])))
                        relativeHumidity.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount])))
                        relativeHumidity.Add(start, GH_Path(int(path[columnCount])))
                        relativeHumidity.Add(end, GH_Path(int(path[columnCount])))
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
                        solarBeamGains.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 6:
                        if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                        else: flrArea = 1
                        p = GH_Path(int(path[columnCount]))
                        solarDiffuseGains.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 7:
                        if normByFlr == True: flrArea = floorAreaList[int(path[columnCount])]
                        else: flrArea = 1
                        p = GH_Path(int(path[columnCount]))
                        infiltrationEnergy.Add((((float(column))*(-1)/3600000) + ((float( line.split(',')[columnCount+1] ))/3600000))/flrArea, p)
                    elif key[columnCount] == 8:
                        pass
                    elif key[columnCount] == 9:
                        p = GH_Path(int(path[columnCount]))
                        airTemperature.Add(float(column), p)
                    elif key[columnCount] == 10:
                        p = GH_Path(int(path[columnCount]))
                        meanRadTemperature.Add(float(column), p)
                    elif key[columnCount] == 11:
                        p = GH_Path(int(path[columnCount]))
                        relativeHumidity.Add(float(column), p)
                    
        result.close()
        parseSuccess = True
    except:
        parseSuccess = False
        warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
                  'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

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
for i in range(solarBeamGains.BranchCount):
    branchList = solarBeamGains.Branch(i)
    beamval = []
    for item in branchList:
        beamval.append(item)
    beamGainPyList.append(beamval)
for i in range(solarDiffuseGains.BranchCount):
    branchList = solarDiffuseGains.Branch(i)
    diffval = []
    for item in branchList:
        diffval.append(item)
    diffGainPyList.append(diffval)
for i in range(airTemperature.BranchCount):
    branchList = airTemperature.Branch(i)
    airval = []
    for item in branchList:
        airval.append(item)
    airTempPyList.append(airval)
for i in range(meanRadTemperature.BranchCount):
    branchList = meanRadTemperature.Branch(i)
    mrtval = []
    for item in branchList:
        mrtval.append(item)
    mrtPyList.append(mrtval)


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

if len(beamGainPyList) > 0 and len(diffGainPyList) > 0:
    for listCount, list in enumerate(beamGainPyList):
        totalSolarGain.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        totalSolarGain.Add(location, GH_Path(listCount))
        if normByFlr == False: totalSolarGain.Add("Total Solar Gain for" + zoneNameList[listCount], GH_Path(listCount))
        else: totalSolarGain.Add("Floor Normalized Total Solar Gain for" + zoneNameList[listCount], GH_Path(listCount))
        if normByFlr == False: totalSolarGain.Add("kWh", GH_Path(listCount))
        else: totalSolarGain.Add("kWh/m2", GH_Path(listCount))
        totalSolarGain.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        totalSolarGain.Add(start, GH_Path(listCount))
        totalSolarGain.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            totalSolarGain.Add((num + diffGainPyList[listCount][7:][numCount]), GH_Path(listCount))
        dataTypeList[8] = True

if len(airTempPyList) > 0 and len(mrtPyList) > 0:
    for listCount, list in enumerate(airTempPyList):
        operativeTemperature.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
        operativeTemperature.Add(location, GH_Path(listCount))
        operativeTemperature.Add("Operative Temperature for" + zoneNameList[listCount], GH_Path(listCount))
        operativeTemperature.Add("C", GH_Path(listCount))
        operativeTemperature.Add(list[4].split('(')[-1].split(')')[0], GH_Path(listCount))
        operativeTemperature.Add(start, GH_Path(listCount))
        operativeTemperature.Add(end, GH_Path(listCount))
        for numCount, num in enumerate(list[7:]):
            operativeTemperature.Add((num + mrtPyList[listCount][7:][numCount])/2, GH_Path(listCount))
        dataTypeList[12] = True

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
9: ["solarBeamGains", "The direct solar beam gain in each zone(kWh)."],
10: ["solarDiffuseGains", "The diffuse solar gain in each zone(kWh)."],
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
