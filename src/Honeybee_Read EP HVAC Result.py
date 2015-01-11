# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to zone ideal air HVAC systems.  For other results related to zones, you should use the "Honeybee_Read EP Result" component and, for results related to surfaces, you should use the "Honeybee_Read EP Surface Result" component.

-
Provided by Honeybee 0.0.55
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
        normByFloorArea_: Set to 'True' to normalize all zone energy data by floor area (note that the resulting units will be kWh/m2 as EnergyPlus runs in the metric system). The default is set to "False."
    Returns:
        sensibleCooling: The sensible energy removed by the ideal air cooling load for each zone in kWh.
        latentCooling: The latent energy removed by the ideal air cooling load for each zone in kWh.
        sensibleHeating: The sensible energy added by the ideal air heating load for each zone in kWh.
        latentHeating: The latent energy added by the ideal air heating load for each zone in kWh.
        supplyMassFlow: The mass of supply air flowing into each zone in kg/s.
        supplyAirTemp: The mean air temperature of the supply air for each zone (degrees Celcius).
        supplyAirHumidity: The relative humidity of the supply air for each zone (%).
"""

ghenv.Component.Name = "Honeybee_Read EP HVAC Result"
ghenv.Component.NickName = 'readEP_HVAC_Result'
ghenv.Component.Message = 'VER 0.0.55\nJAN_10_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
ghenv.Component.AdditionalHelpFromDocStrings = "0"


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
sensibleCooling = DataTree[Object]()
latentCooling = DataTree[Object]()
sensibleHeating = DataTree[Object]()
latentHeating = DataTree[Object]()
supplyMassFlow = DataTree[Object]()
supplyAirTemp = DataTree[Object]()
supplyAirHumidity = DataTree[Object]()


#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False]
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

#Make a function to check the zone name.
def checkZone(csvName):
    zoneName = None
    for count, name in enumerate(zoneNameList):
        if name == csvName:
            zoneName = name
            path.append(count)
    return zoneName


# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    #try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                key = []; path = []
                for columnCount, column in enumerate(line.split(',')):
                    if 'Zone Ideal Loads Zone Sensible Cooling Energy' in column:
                        key.append(0)
                        zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        makeHeader(sensibleCooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Sensible Cooling Energy", "kWh", True)
                        dataTypeList[0] = True
                    
                    elif 'Zone Ideal Loads Zone Latent Cooling Energy' in column:
                        key.append(1)
                        zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        makeHeader(latentCooling, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Latent Cooling Energy", "kWh", True)
                        dataTypeList[1] = True
                    
                    elif 'Zone Ideal Loads Zone Sensible Heating Energy' in column:
                        key.append(2)
                        zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        makeHeader(sensibleHeating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Sensible Heating Energy", "kWh", True)
                        dataTypeList[2] = True
                    
                    elif 'Zone Ideal Loads Zone Latent Heating Energy' in column:
                        key.append(3)
                        zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS AIR SYSTEM')[0])
                        makeHeader(latentHeating, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Latent Heating Energy", "kWh", True)
                        dataTypeList[3] = True
                    
                    elif 'System Node Mass Flow Rate' in column:
                        if column.startswith("NODE") or "RETURN" in column or "OUTDOOR AIR" in column or "ZONE AIR NODE" in column:
                            key.append(-1)
                            path.append(-1)
                        else:
                            key.append(4)
                            zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS SUPPLY INLET')[0])
                            makeHeader(supplyMassFlow, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Supply Air Mass Flow Rate", "kg/s", True)
                            dataTypeList[4] = True
                    
                    elif 'System Node Temperature' in column:
                        if column.startswith("NODE") or "RETURN" in column or "OUTDOOR AIR" in column or "ZONE AIR NODE" in column:
                            key.append(-1)
                            path.append(-1)
                        else:
                            key.append(5)
                            zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS SUPPLY INLET')[0])
                            makeHeader(supplyAirTemp, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Supply Air Temperature", "C", False)
                            dataTypeList[5] = True
                    
                    elif 'System Node Relative Humidity' in column:
                        if column.startswith("NODE") or "RETURN" in column or "OUTDOOR AIR" in column or "ZONE AIR NODE" in column:
                            key.append(-1)
                            path.append(-1)
                        else:
                            key.append(6)
                            zoneName = checkZone(" " + column.split(':')[0].split(' IDEAL LOADS SUPPLY INLET')[0])
                            makeHeader(supplyAirHumidity, int(path[columnCount]), zoneName, column.split('(')[-1].split(')')[0], "Supply Air Relative Humidity", "%", False)
                            dataTypeList[6] = True
                    
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
                        sensibleCooling.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 1:
                        latentCooling.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 2:
                        sensibleHeating.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 3:
                        latentHeating.Add((float(column)/3600000)/flrArea, p)
                    elif key[columnCount] == 4:
                        supplyMassFlow.Add((float(column))/flrArea, p)
                    elif key[columnCount] == 5:
                        supplyAirTemp.Add(float(column), p)
                    elif key[columnCount] == 6:
                        supplyAirHumidity.Add(float(column), p)
                    
        result.close()
        parseSuccess = True
    #except:
    #    try: result.close()
    #    except: pass
    #    parseSuccess = False
    #    warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
    #              'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
    #    print warn
    #    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)




#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["sensibleCooling", "The sensible energy removed by the ideal air cooling load for each zone in kWh."],
1: ["latentCooling", "The latent energy removed by the ideal air cooling load for each zone in kWh."],
2: ["sensibleHeating", "The sensible energy added by the ideal air heating load for each zone in kWh."],
3: ["latentHeating", "The latent energy added by the ideal air heating load for each zone in kWh."],
4: ["supplyMassFlow", "The mass of supply air flowing into each zone in kg/s."],
5: ["supplyAirTemp", "The mean air temperature of the supply air for each zone (degrees Celcius)."],
6: ["supplyAirHumidity", "The relative humidity of the supply air for each zone (%)."]
}


if _resultFileAddress and parseSuccess == True:
    for output in range(7):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(7):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
