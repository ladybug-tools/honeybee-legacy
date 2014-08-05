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
        surfaceIndoorTemp: The indoor surface temperature of each surface (degrees Celcius).
        surfaceOutdoorTemp: The outdoor surface temperature of each surface (degrees Celcius).
        opaqueEnergyFlow: The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh).
        glazEnergyFlow: The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains.
        windowTotalSolarEnergy: The total solar energy transmitted through each of the glazing surfaces to the zone (kWh).
        windowBeamEnergy: The total direct solar beam energy transmitted through each of the glazing surfaces to the zone (kWh).
        windowDiffEnergy: The total diffuse solar energy transmitted through each of the glazing surfaces to the zone (kWh).
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
surfaceIndoorTemp = DataTree[Object]()
surfaceOutdoorTemp = DataTree[Object]()
opaqueEnergyFlow = DataTree[Object]()
glazEnergyFlow = DataTree[Object]()
windowBeamEnergy = DataTree[Object]()
windowDiffEnergy = DataTree[Object]()
windowTotalSolarEnergy = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False]
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
glzBeamGain = 0
glzDiffGain = 0
glzTotalGain = 0

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
                    if 'Surface Inside Face Temperature' in column:
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
                            surfaceIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add("Indoor Surface Temperature for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceIndoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            opaInTemp += 1
                        else:
                            surfaceIndoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add("Indoor Surface Temperature for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceIndoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(12)
                        dataTypeList[0] = True
                    
                    elif 'Surface Outside Face Temperature' in column:
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
                            surfaceOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add("Outdoor Surface Temperature for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0])))
                            surfaceOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0])))
                            opaOutTemp += 1
                        else:
                            surfaceOutdoorTemp.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add("Outdoor Surface Temperature for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add("C", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            surfaceOutdoorTemp.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(14)
                        dataTypeList[1] = True
                    
                    elif 'Surface Average Face Conduction Heat Transfer Energy' in column:
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
                            opaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                            opaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                            opaConduct += 1
                        else:
                            opaqueEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add("Opaque Conductive Energy Loss/Gain for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            opaqueEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(16)
                        dataTypeList[2] = True
                    
                    elif 'Surface Window Heat Gain Energy' in column:
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
                            glazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add("Glazing Energy Loss/Gain for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0])))
                            glazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0])))
                            glzGain += 1
                        else:
                            glazEnergyFlow.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add("Glazing Energy Loss/Gain for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            glazEnergyFlow.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(17)
                        dataTypeList[3] = True
                    
                    elif 'Surface Window Heat Loss Energy' in column:
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
                    
                    elif 'Surface Window Transmitted Beam Solar Radiation Energy' in column:
                        foundNameGlzBeamGain = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][5])
                                zoneSrfs[count][5].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzBeamGain = True
                        if foundNameGlzBeamGain == False:
                            path.append([glzBeamGain])
                            windowBeamEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add(location, GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add("Window Transmitted Beam Energy for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add("kWh", GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add(start, GH_Path(int(path[columnCount][0])))
                            windowBeamEnergy.Add(end, GH_Path(int(path[columnCount][0])))
                            glzBeamGain += 1
                        else:
                            windowBeamEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add("Window Transmitted Beam Energy for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowBeamEnergy.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(1)
                        dataTypeList[4] = True
                    
                    elif 'Surface Window Transmitted Diffuse Solar Radiation Energy' in column:
                        foundNameGlzDiffGain = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][5])
                                zoneSrfs[count][5].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzDiffGain = True
                        if foundNameGlzDiffGain == False:
                            path.append([glzDiffGain])
                            windowDiffEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add(location, GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add("Window Transmitted Diffuse Energy for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add("kWh", GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add(start, GH_Path(int(path[columnCount][0])))
                            windowDiffEnergy.Add(end, GH_Path(int(path[columnCount][0])))
                            glzDiffGain += 1
                        else:
                            windowDiffEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add("Window Transmitted Diffuse Energy for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowDiffEnergy.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(2)
                        dataTypeList[5] = True
                    
                    elif 'Surface Window Transmitted Solar Radiation Energy' in column:
                        foundNameGlzTotalGain = False
                        for count, name in enumerate(zoneNameList):
                            if name in " " + column.split(':')[0]:
                                zoneName = name
                                srfName = column.split(':')[0].split(name.split(" ")[-1])[-1]
                                srfIndex = len(zoneSrfs[count][5])
                                zoneSrfs[count][5].append(1)
                                path.append([count, srfIndex])
                                foundNameGlzTotalGain = True
                        if foundNameGlzTotalGain == False:
                            path.append([glzTotalGain])
                            windowTotalSolarEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add(location, GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add("Window Total Transmitted Solar Energy for " + column.split(':')[0], GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add("kWh", GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add(start, GH_Path(int(path[columnCount][0])))
                            windowTotalSolarEnergy.Add(end, GH_Path(int(path[columnCount][0])))
                            glzTotalGain += 1
                        else:
                            windowTotalSolarEnergy.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add(location, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add("Window Total Transmitted Solar Energy for " + zoneName + srfName, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add("kWh", GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add(column.split('(')[-1].split(')')[0], GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add(start, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                            windowTotalSolarEnergy.Add(end, GH_Path(int(path[columnCount][0]), int(path[columnCount][1])))
                        key.append(3)
                        dataTypeList[6] = True
                    
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
                        surfaceIndoorTemp.Add(float(column), p)
                    elif key[columnCount] == 14:
                        if foundNameOutOpaTemp == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        surfaceOutdoorTemp.Add(float(column), p)
                    elif key[columnCount] == 16:
                        if foundNameOpaConduct == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        opaqueEnergyFlow.Add((float(column)/3600000), p)
                    elif key[columnCount] == 17:
                        if foundNameGlzGain == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        glazEnergyFlow.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                    elif key[columnCount] == 18:
                        pass
                    elif key[columnCount] == 1:
                        if foundNameGlzBeamGain == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        windowBeamEnergy.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                    elif key[columnCount] == 2:
                        if foundNameGlzDiffGain == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        windowDiffEnergy.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                    elif key[columnCount] == 3:
                        if foundNameGlzTotalGain == True:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                        else: p = GH_Path(int(path[columnCount][0]))
                        windowTotalSolarEnergy.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000)), p)
                    
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
     
0: ["surfaceIndoorTemp", "The indoor surface temperature of each surface (degrees Celcius)."],
1: ["surfaceOutdoorTemp", "The outdoor surface temperature of each surface (degrees Celcius)."],
2: ["opaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
3: ["glazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."],
4: ["windowTotalSolarEnergy", "The total solar energy transmitted through each of the glazing surfaces to the zone (kWh)."],
5: ["windowBeamEnergy", "The total direct solar beam energy transmitted through each of the glazing surfaces to the zone (kWh)."],
6: ["windowDiffEnergy", "The total diffuse solar energy transmitted through each of the glazing surfaces to the zone (kWh)."]
}

if _resultFileAddress and parseSuccess == True:
    for output in range(7):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "............................"
            ghenv.Component.Params.Output[output].Name = "............................"
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
