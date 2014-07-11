# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to surfaces.  For results related to zones, you should use the "Honeybee_Read EP Result" component.

-
Provided by Honeybee 0.0.53
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
    Returns:
        surfaceOpaqueIndoorTemp: The indoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazIndoorTemp: The indoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueOutdoorTemp: The outdoor surface temperature of each opaque surface (degrees Celcius).
        surfaceGlazOutdoorTemp: The outdoor surface temperature of each glazed surface (degrees Celcius).
        surfaceOpaqueEnergyFlow: The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh).
        surfaceGlazEnergyFlow: The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains.
"""

ghenv.Component.Name = "Honeybee_Read EP Surface Result"
ghenv.Component.NickName = 'readEPSrfResult'
ghenv.Component.Message = 'VER 0.0.53\nJUL_11_2014'
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


# Make data tree objects for all of the outputs.
surfaceOpaqueIndoorTemp = DataTree[Object]()
surfaceGlazIndoorTemp = DataTree[Object]()
surfaceOpaqueOutdoorTemp = DataTree[Object]()
surfaceGlazOutdoorTemp = DataTree[Object]()
surfaceOpaqueEnergyFlow = DataTree[Object]()
surfaceGlazEnergyFlow = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False]
parseSuccess = False

#Make a list to keep track of the number of surfaces in each zone.
zoneSrfs = []
for zoneCount, zone in enumerate(floorAreaList):
    zoneSrfs.append([])
    for num in range(7):
        zoneSrfs[zoneCount].append([])

# If zone names are not included, make lists to keep track of the number of surfaces that have been imported so far.
opaInTemp = 0
glzInTemp = 0
opaOutTemp = 0
glzOutTemp = 0
opaConduct = 0
glzGain = 0
glzLoss = 0

# PARSE THE RESULT FILE.
if _resultFileAddress and gotData == True:
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                #inside opaque temperature = 12
                #inside glazing temperature = 13
                #outside opaque temperature = 14
                #outside glazing temperature = 15
                #opaque surface energy transfer = 16
                #glazing surface energy gain = 17
                #glazing surface energy loss = 18
                key = []; path = []
                for columnCount, column in enumerate(line.split(',')):
                    if 'Surface Inside Face Temperature' in column and "GLZ" not in column:
                        foundNameOpaTemp = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][0])
                                zoneSrfs[count][0].append(1)
                                path.append([count, srfIndex])
                                foundNameOpaTemp = True
                        if foundNameOpaTemp == False:
                            path.append([opaInTemp])
                            surfaceOpaqueIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add("Indoor Surface Temperature for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueIndoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            opaInTemp += 1
                        else:
                            surfaceOpaqueIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add("Indoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(12)
                        dataTypeList[0] = True
                    
                    elif 'Surface Inside Face Temperature' in column and "GLZ" in column:
                        foundNameGlzTemp = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][1])
                                zoneSrfs[count][1].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzTemp = True
                        if foundNameGlzTemp == False:
                            path.append([glzInTemp])
                            surfaceGlazIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add("Indoor Surface Temperature for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceGlazIndoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            glzInTemp += 1
                        else:
                            surfaceGlazIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add("Indoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(13)
                        dataTypeList[1] = True
                    
                    elif 'Surface Outside Face Temperature' in column and "GLZ" not in column:
                        foundNameOutOpaTemp = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][2])
                                zoneSrfs[count][2].append(1)
                                path.append([count, srfIndex])
                                foundNameOutOpaTemp = True
                        if foundNameOutOpaTemp == False:
                            path.append([opaOutTemp])
                            surfaceOpaqueOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add("Outdoor Surface Temperature for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            opaOutTemp += 1
                        else:
                            surfaceOpaqueOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add("Outdoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(14)
                        dataTypeList[2] = True
                    
                    elif 'Surface Outside Face Temperature' in column and "GLZ" in column:
                        foundNameOutGlzTemp = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][3])
                                zoneSrfs[count][3].append(1)
                                path.append([count, srfIndex])
                                foundNameOutGlzTemp = True
                        if foundNameOutGlzTemp == False:
                            path.append([glzOutTemp])
                            surfaceGlazOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add("Outdoor Surface Temperature for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceGlazOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            glzOutTemp += 1
                        else:
                            surfaceGlazOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add("Outdoor Surface Temperature for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(15)
                        dataTypeList[3] = True
                    
                    elif 'Surface Average Face Conduction Heat Transfer Energy' in column and "GLZ" not in column:
                        foundNameOpaConduct = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][4])
                                zoneSrfs[count][4].append(1)
                                path.append([count, srfIndex])
                                foundNameOpaConduct = True
                        if foundNameOpaConduct == False:
                            path.append([opaConduct])
                            surfaceOpaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceOpaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                            opaConduct += 1
                        else:
                            surfaceOpaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOpaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(16)
                        dataTypeList[4] = True
                    
                    elif 'Surface Window Heat Gain Energy' in column and "GLZ" in column:
                        foundNameGlzGain = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][5])
                                zoneSrfs[count][5].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzGain = True
                        if foundNameGlzGain == False:
                            path.append([glzGain])
                            surfaceGlazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add("Glazing Energy Loss/Gain for" + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceGlazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                            glzGain += 1
                        else:
                            surfaceGlazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add("Glazing Energy Loss/Gain for" + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceGlazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(17)
                        dataTypeList[5] = True
                    
                    elif 'Surface Window Heat Loss Energy' in column and "GLZ" in column:
                        foundNameGlzLoss = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][6])
                                zoneSrfs[count][6].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzLoss = True
                                key.append(18)
                        if foundNameGlzLoss == False:
                            key.append(18)
                            path.append([glzLoss])
                            glzLoss += 1
                    
                    else:
                        key.append(-1)
                        path.append(-1)
                    
                #print key
                #print path
            else:
                for columnCount, column in enumerate(line.split(',')):
                    if key[columnCount] == 12:
                        if foundNameOpaTemp == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceOpaqueIndoorTemp.Add(float(column), p)
                    elif key[columnCount] == 13:
                        if foundNameGlzTemp == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceGlazIndoorTemp.Add(float(column), p)
                    elif key[columnCount] == 14:
                        if foundNameOutOpaTemp == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceOpaqueOutdoorTemp.Add(float(column), p)
                    elif key[columnCount] == 15:
                        if foundNameOutGlzTemp == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceGlazOutdoorTemp.Add(float(column), p)
                    elif key[columnCount] == 16:
                        if foundNameOpaConduct == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceOpaqueEnergyFlow.Add((float(column)/3600000), p)
                    elif key[columnCount] == 17:
                        if foundNameGlzGain == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceGlazEnergyFlow.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                    elif key[columnCount] == 18:
                        pass
                    
        result.close()
        parseSuccess = True
    except:
        parseSuccess = False
        warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
                  'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)


#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["surfaceOpaqueIndoorTemp", "The indoor surface temperature of each opaque surface (degrees Celcius)."],
1: ["surfaceGlazIndoorTemp", "The indoor surface temperature of each glazed surface (degrees Celcius)."],
2: ["surfaceOpaqueOutdoorTemp", "The outdoor surface temperature of each opaque surface (degrees Celcius)."],
3: ["surfaceGlazOutdoorTemp", "The outdoor surface temperature of each glazed surface (degrees Celcius)."],
4: ["surfaceOpaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
5: ["surfaceGlazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."]
}

if _resultFileAddress and parseSuccess == True:
    for output in range(6):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(6):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
