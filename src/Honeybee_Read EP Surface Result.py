#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component reads only the results related to surfaces.  For results related to zones, you should use the "Honeybee_Read EP Result" component.

-
Provided by Honeybee 0.0.64
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.
        normBySrfArea_: Set to 'True' to normalize all surface energy data by the area of the suraces (note that the resulting units will be kWh/m2 as EnergyPlus runs in the metric system).  The default is set to "False."
    Returns:
        surfaceIndoorTemp: The indoor surface temperature of each surface (degrees Celcius).
        surfaceOutdoorTemp: The outdoor surface temperature of each surface (degrees Celcius).
        surfaceEnergyFlow: The heat loss (negative) or heat gain (positive) through each building surfaces (kWh).
        opaqueEnergyFlow: The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh).
        glazEnergyFlow: The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains.
        windowTotalSolarEnergy: The total solar energy transmitted through each of the glazing surfaces to the zone (kWh).
        windowBeamEnergy: The total direct solar beam energy transmitted through each of the glazing surfaces to the zone (kWh).
        windowDiffEnergy: The total diffuse solar energy transmitted through each of the glazing surfaces to the zone (kWh).
        windowTransmissivity: The hourly transmissivity of the exterior windows of the model.  This data is needed to align a comfort map with an energy model possessing shades.
"""

ghenv.Component.Name = "Honeybee_Read EP Surface Result"
ghenv.Component.NickName = 'readEPSrfResult'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nJAN_17_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc
import copy
import os


#Read the location and the analysis period info from the eio file, if there is one.
#Also try to read the names of the zones and the surfaces from this file.
location = "NoLocation"
start = "NoDate"
end = "NoDate"
zoneNameList = []
zoneSrfNameList = []
zoneSrfTypeList = []
zoneSrfAreaList = []
gotZoneData = False
gotSrfData = False
curvedGeometry = False

if _resultFileAddress:
    try:
        numZonesLine = 100000
        numShadesLine = 100000
        numZonesIndex = 0
        numSrfsIndex = 0
        numFixShdIndex = 0
        numBldgShdIndex = 0
        numAttShdIndex = 0
        zoneAreaLines = []
        srfAreaLines = []
        areaIndex = 0
        zoneCounter = -1
        srfCounter = -1
        numFixShd = 0
        numBldgShd = 0
        numAttShd = 0
        
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
            elif "Shading Summary" in line and "Number of Building Detached Shades" in line:
                for index, text in enumerate(line.split(",")):
                    numShadesLine = lineCount+1
                    if "Number of Fixed Detached Shades" in text: numFixShdIndex = index
                    elif "Number of Building Detached Shades" in text: numBldgShdIndex = index
                    elif "Number of Attached Shades" in text: numAttShdIndex = index
                    else: pass
            elif lineCount == numShadesLine:
                numFixShd = int(line.split(",")[numFixShdIndex])
                numBldgShd = int(line.split(",")[numBldgShdIndex])
                numAttShd = int(line.split(",")[numAttShdIndex])
            elif "Zone Summary" in line and "Number of Zones" in line:
                for index, text in enumerate(line.split(",")):
                    numZonesLine = lineCount+1
                    if "Number of Zones" in text: numZonesIndex = index
                    elif "Number of Zone Surfaces" in text: numSrfsIndex = index
                    else: pass
            elif lineCount == numZonesLine:
                numZones = line.split(",")[numZonesIndex]
                numSrfs = line.split(",")[numSrfsIndex]
                for num in range(int(numZones)):
                    zoneSrfNameList.append([])
                    zoneSrfTypeList.append([])
                    zoneSrfAreaList.append([])
            elif "Zone Information" in line and "Floor Area {m2}" in line:
                zoneAreaLines = range(lineCount+1, lineCount+1+int(numZones))
            elif lineCount in zoneAreaLines:
                zoneNameList.append(line.split(",")[1])
                gotZoneData = True
            elif "Surface Name" in line and "Area (Gross)" in line:
                if numFixShd>0 or numBldgShd>0 or numAttShd>0:
                    srfAreaLines = range(lineCount+3, lineCount+3+int(numZones)+int(numSrfs)+int(numFixShd)+int(numBldgShd)+int(numAttShd))
                else:
                    srfAreaLines = range(lineCount+2, lineCount+2+int(numZones)+int(numSrfs))
            elif '-FRAME' in line or 'Frame/Divider' in line:
                srfAreaLines.append(srfAreaLines[-1]+1)
            elif lineCount in srfAreaLines:
                if "Shading_Surface" in line or "Shading Surface" in line: pass
                elif "Zone_Surfaces" in line or "Zone Surfaces" in line:
                    zoneCounter += 1
                    srfCounter = -1
                else:
                    if "SRFP" in line or "GLZP" in line:
                        curvedGeometry = True
                        if "_GLZP_" in line: surfaceName = line.split(",")[1].split("_GLZP_")[0]
                        elif "_SRFP_" in line: surfaceName = line.split(",")[1].split("_SRFP")[0]
                        else: surfaceName = None
                        if surfaceName:
                            if surfaceName in zoneSrfNameList[zoneCounter]:
                                zoneSrfAreaList[zoneCounter][srfCounter] = zoneSrfAreaList[zoneCounter][srfCounter] + float(line.split(",")[9])
                            else:
                                srfCounter += 1
                                zoneSrfNameList[zoneCounter].append(surfaceName)
                                zoneSrfTypeList[zoneCounter].append(line.split(",")[2])
                                zoneSrfAreaList[zoneCounter].append(float(line.split(",")[9]))
                    elif '! <' not in line:
                        srfCounter += 1
                        zoneSrfNameList[zoneCounter].append(line.split(",")[1])
                        zoneSrfTypeList[zoneCounter].append(line.split(",")[2])
                        zoneSrfAreaList[zoneCounter].append(float(line.split(",")[9]))
                gotSrfData = True
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
else:
    gotSrfData =True

#If no surafce data was imported from the .eio file, give the user a warning and tell them that they cannot normalize by area.
if gotSrfData == False:
    warning = 'No surface information was found in the imported .eio file adjacent to the .csv _resultFileAddress.'+ \
              'Data cannot be normalized by surface area and the data tree outputs for surface data will not be grafted by zone.'
    print warning
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)

#If no value is connected for normBySrfArea_, don't normalize the results.
if normBySrfArea_ == None:
    normBySrf = False
else:
    normBySrf = normBySrfArea_

# If the user has selected to normalize the results, make sure that we were able to pull the surface areas from the results file.
if normBySrf == True and zoneSrfAreaList != []:
    normBySrf == True
elif normBySrf == True:
    normBySrf == False
else: pass

# Make data tree objects for all of the outputs.
surfaceIndoorTemp = DataTree[Object]()
surfaceOutdoorTemp = DataTree[Object]()
surfaceEnergyFlow = DataTree[Object]()
opaqueEnergyFlow = DataTree[Object]()
glazEnergyFlow = DataTree[Object]()
windowBeamEnergy = DataTree[Object]()
windowDiffEnergy = DataTree[Object]()
windowTotalSolarEnergy = DataTree[Object]()
windowTransmissivity = DataTree[Object]()

#Make a list to keep track of what outputs are in the result file.
dataTypeList = [False, False, False, False, False, False, False, False, False, False]
parseSuccess = False
normAreaWorked = True

# If zone names are not included, make numbers to keep track of the number of surfaces that have been imported so far.
InTemp = 0
OutTemp = 0
opaConduct = 0
glzGain = 0
glzLoss = 0
glzBeamGain = 0
glzDiffGain = 0
glzTotalGain = 0
glzTransmiss = 0

# If there are curved surfaces, make numbers to keep track of the number of surface pieces.
srfPiecesList = []
srfPieceDataList = []

if curvedGeometry == True:
    for dataType in range(9):
        srfPiecesList.append([])
        srfPieceDataList.append([])
        for zoneCount, zone in enumerate(zoneSrfNameList):
            srfPiecesList[dataType].append([])
            srfPieceDataList[dataType].append([])
            for srfCount, srf in enumerate(zone):
                srfPiecesList[dataType][zoneCount].append(0)
                srfPieceDataList[dataType][zoneCount].append([])

#Make functions to add headers.
def makeHeader(list, path, srfName, timestep, name, units):
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    list.Add(location, GH_Path(path))
    list.Add(name + " for " + srfName, GH_Path(path))
    list.Add(units, GH_Path(path))
    list.Add(timestep, GH_Path(path))
    list.Add(start, GH_Path(path))
    list.Add(end, GH_Path(path))

def makeHeaderGrafted(list, path1, path2, srfName, timestep, name, units, normable, typeName):
    if units == '': units = 'Fraction'
    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path1, path2))
    list.Add(location, GH_Path(path1, path2))
    if normBySrf == False or normable == False: list.Add(name + " for " + srfName + ": " + typeName, GH_Path(path1, path2))
    else: list.Add("Area Normalized " + name + " for " + srfName + ": " + typeName, GH_Path(path1, path2))
    if normBySrf == False or normable == False: list.Add(units, GH_Path(path1, path2))
    else: list.Add(units+"/m2", GH_Path(path1, path2))
    list.Add(timestep, GH_Path(path1, path2))
    list.Add(start, GH_Path(path1, path2))
    list.Add(end, GH_Path(path1, path2))

#Make a function to check the srf name and type Name.
def checkSrfName(csvName, dataType):
    srfFound = False
    srfName = None
    duplicate = False
    pieceNum = 1
    typeName = None
    
    if "SRFP" in csvName or "GLZP" in csvName:
        duplicate = True
        if "_GLZP_" in csvName: csvName = csvName.split("_GLZP")[0]
        elif "_SRFP" in csvName: csvName = csvName.split("_SRFP")[0]
        else: csvName = None
    
    if csvName:
        for branch, namelist in enumerate(zoneSrfNameList):
            for count, name in enumerate(namelist):
                if name == csvName:
                    srfFound = True
                    srfName = name
                    path.append([branch, count])
                    typeName = zoneSrfTypeList[branch][count]
                    if duplicate == True:
                        try:
                            srfPiecesList[dataType][branch][count] = srfPiecesList[dataType][branch][count] + 1
                            pieceNum = srfPiecesList[dataType][branch][count]
                        except Exception as e:
                            print e
                            pieceNum = 1
                    else:
                        pieceNum = 1
        if srfFound == False:
            path.append(-1)
    else:
        path.append(-1)
    
    
    return srfName, typeName, pieceNum, duplicate

#Make a function to check the srf name and type name when the data is going to go out the "otherSrfData" output.
def checkSrfNameOther(dataIndex, csvName):
    srfName = None
    
    for branch, list in enumerate(zoneSrfNameList):
        for count, name in enumerate(list):
            if name == csvName:
                srfName = name
                path.append([branch, count+(dataIndex[branch])])
                typeName = zoneSrfTypeList[branch][count]
                dataIndex[branch] += 1
    
    return srfName, typeName
dataIndex = []
for zone in range(len(zoneSrfNameList)): dataIndex.append(0)


# PARSE THE RESULT FILE.
if _resultFileAddress and gotZoneData == True and gotSrfData == True:
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                #ANALYZE THE FILE HEADING
                key = []; path = []; duplicateList = []; pieceNumList = []
                for columnCount, column in enumerate(line.split(',')):
                    srfName = column.split(':')[0]
                    if 'Surface Inside Face Temperature' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 0)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1:
                                makeHeaderGrafted(surfaceIndoorTemp, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Inner Surface Temperature", "C", False, typeName)
                        else:
                            path.append([InTemp])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(surfaceIndoorTemp, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Inner Surface Temperature", "C")
                            InTemp += 1
                        key.append(1)
                        dataTypeList[0] = True
                    
                    elif 'Surface Outside Face Temperature' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 1)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1:
                                makeHeaderGrafted(surfaceOutdoorTemp, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Outer Surface Temperature", "C", False, typeName)
                        else:
                            path.append([OutTemp])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(surfaceOutdoorTemp, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Outer Surface Temperature", "C")
                            OutTemp += 1
                        key.append(2)
                        dataTypeList[1] = True
                    
                    elif 'Surface Average Face Conduction Heat Transfer Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 2)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: makeHeaderGrafted(opaqueEnergyFlow, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Surface Energy Loss/Gain", "kWh", True, typeName)
                        else:
                            path.append([opaConduct])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(opaqueEnergyFlow, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Surface Energy Loss/Gain", "kWh")
                            opaConduct += 1
                        key.append(3)
                        dataTypeList[3] = True
                    
                    elif 'Surface Window Heat Gain Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 3)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: makeHeaderGrafted(glazEnergyFlow, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Surface Energy Loss/Gain", "kWh", True, typeName)
                        else:
                            path.append([glzGain])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(glazEnergyFlow, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Surface Energy Loss/Gain", "kWh")
                            glzGain += 1
                        key.append(4)
                        dataTypeList[4] = True
                    
                    elif 'Surface Window Heat Loss Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 4)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                        else:
                            path.append([glzLoss])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            glzLoss += 1
                        key.append(5)
                    
                    elif 'Surface Window Transmitted Beam Solar Radiation Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 5)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: makeHeaderGrafted(windowBeamEnergy, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Window Transmitted Beam Energy", "kWh", True, typeName)
                        else:
                            path.append([glzBeamGain])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(windowBeamEnergy, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Window Transmitted Beam Energy", "kWh")
                            glzBeamGain += 1
                        key.append(6)
                        dataTypeList[6] = True
                    
                    elif 'Surface Window Transmitted Diffuse Solar Radiation Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 6)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: makeHeaderGrafted(windowDiffEnergy, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Window Transmitted Diffuse Energy", "kWh", True, typeName)
                        else:
                            path.append([glzDiffGain])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(windowDiffEnergy, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Window Transmitted Diffuse Energy", "kWh")
                            glzDiffGain += 1
                        key.append(7)
                        dataTypeList[7] = True
                    
                    elif 'Surface Window Transmitted Solar Radiation Energy' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 7)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: makeHeaderGrafted(windowTotalSolarEnergy, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Window Total Transmitted Solar Energy", "kWh", True, typeName)
                        else:
                            path.append([glzTotalGain])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(windowTotalSolarEnergy, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Window Total Transmitted Solar Energy", "kWh")
                            glzTotalGain += 1
                        key.append(8)
                        dataTypeList[5] = True
                    
                    elif 'Surface Window System Solar Transmittance' in column:
                        if gotSrfData == True:
                            srfName, typeName, pieceNum, duplicate = checkSrfName(srfName, 8)
                            duplicateList.append(duplicate)
                            pieceNumList.append(pieceNum)
                            if pieceNum < 2 and path[columnCount] != -1: 
                                makeHeaderGrafted(windowTransmissivity, int(path[columnCount][0]), int(path[columnCount][1]), srfName, column.split('(')[-1].split(')')[0], "Surface Window System Solar Transmittance", "Fraction", True, typeName)
                        else:
                            path.append([glzTransmiss])
                            duplicateList.append(False)
                            pieceNumList.append(1)
                            makeHeader(windowTransmissivity, int(path[columnCount]), srfName, column.split('(')[-1].split(')')[0], "Surface Window System Solar Transmittance", "Fraction")
                            glzTransmiss += 1
                        key.append(10)
                        dataTypeList[8] = True
                    
                    else:
                        key.append(-1)
                        path.append(-1)
                        duplicateList.append(-1)
                        pieceNumList.append(-1)
            else:
                for columnCount, column in enumerate(line.split(',')):
                    if path[columnCount] != -1:
                        if gotSrfData == True and key[columnCount] != 9:
                            duplicate = duplicateList[columnCount]
                            pieceCount = pieceNumList[columnCount]
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                            if normBySrf == True:
                                try: srfArea = zoneSrfAreaList[int(path[columnCount][0])][int(path[columnCount][1])]
                                except:
                                    srfArea = 1
                                    normAreaWorked = False
                            else: srfArea = 1
                        elif gotSrfData == True and key[columnCount] == 9:
                            p = GH_Path(int(path[columnCount][0]), int(path[columnCount][1]))
                            srfArea = 1
                        else:
                            p = GH_Path(int(path[columnCount][0]))
                            srfArea = 1
                        
                        if key[columnCount] == 1:
                            if duplicate == False:
                                surfaceIndoorTemp.Add(float(column), p)
                            else:
                                if pieceCount == 1:
                                    srfPieceDataList[0][path[columnCount][0]][path[columnCount][1]].append(float(column))
                                else:
                                    srfPieceDataList[0][path[columnCount][0]][path[columnCount][1]][lineCount-1] = \
                                        (srfPieceDataList[0][path[columnCount][0]][path[columnCount][1]][lineCount-1] + float(column))/2
                        elif key[columnCount] == 2:
                            if duplicate == False:
                                surfaceOutdoorTemp.Add(float(column), p)
                            else:
                                if pieceCount == 1:
                                    srfPieceDataList[1][path[columnCount][0]][path[columnCount][1]].append(float(column))
                                else:
                                    srfPieceDataList[1][path[columnCount][0]][path[columnCount][1]][lineCount-1] = \
                                        (srfPieceDataList[1][path[columnCount][0]][path[columnCount][1]][lineCount-1] + float(column))/2
                        elif key[columnCount] == 3:
                            if duplicate == False: opaqueEnergyFlow.Add((float(column)/3600000)/srfArea, p)
                            else:
                                if pieceCount == 1: srfPieceDataList[2][path[columnCount][0]][path[columnCount][1]].append((float(column)/3600000)/srfArea)
                                else: srfPieceDataList[2][path[columnCount][0]][path[columnCount][1]][lineCount-1] = srfPieceDataList[2][path[columnCount][0]][path[columnCount][1]][lineCount-1] + (float(column)/3600000)/srfArea
                        elif key[columnCount] == 4:
                            if duplicate == False: glazEnergyFlow.Add((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000))/srfArea, p)
                            else:
                                if pieceCount == 1: srfPieceDataList[3][path[columnCount][0]][path[columnCount][1]].append((((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000))/srfArea)
                                else: srfPieceDataList[3][path[columnCount][0]][path[columnCount][1]][lineCount-1] = srfPieceDataList[3][path[columnCount][0]][path[columnCount][1]][lineCount-1] + (((float(column))/3600000) + ((float( line.split(',')[columnCount+1] ))*(-1)/3600000))/srfArea
                        elif key[columnCount] == 5:
                            pass
                        elif key[columnCount] == 6:
                            if duplicate == False: windowBeamEnergy.Add(((float(column))/3600000)/srfArea, p)
                            else:
                                if pieceCount == 1: srfPieceDataList[5][path[columnCount][0]][path[columnCount][1]].append((float(column)/3600000)/srfArea)
                                else: srfPieceDataList[5][path[columnCount][0]][path[columnCount][1]][lineCount-1] = srfPieceDataList[5][path[columnCount][0]][path[columnCount][1]][lineCount-1] + (float(column)/3600000)/srfArea
                        elif key[columnCount] == 7:
                            if duplicate == False: windowDiffEnergy.Add(((float(column))/3600000)/srfArea, p)
                            else:
                                if pieceCount == 1: srfPieceDataList[6][path[columnCount][0]][path[columnCount][1]].append((float(column)/3600000)/srfArea)
                                else: srfPieceDataList[6][path[columnCount][0]][path[columnCount][1]][lineCount-1] = srfPieceDataList[6][path[columnCount][0]][path[columnCount][1]][lineCount-1] + (float(column)/3600000)/srfArea
                        elif key[columnCount] == 8:
                            if duplicate == False:
                                windowTotalSolarEnergy.Add(((float(column))/3600000)/srfArea, p)
                            else:
                                if pieceCount == 1:
                                    srfPieceDataList[7][path[columnCount][0]][path[columnCount][1]].append((float(column)/3600000)/srfArea)
                                else:
                                    srfPieceDataList[7][path[columnCount][0]][path[columnCount][1]][lineCount-1] = \
                                        srfPieceDataList[7][path[columnCount][0]][path[columnCount][1]][lineCount-1] + (float(column)/3600000)/srfArea
                        elif key[columnCount] == 10:
                            if duplicate == False:
                                windowTransmissivity.Add(float(column), p)
                            else:
                                if pieceCount == 1:
                                    srfPieceDataList[8][path[columnCount][0]][path[columnCount][1]].append(float(column))
                                else:
                                    srfPieceDataList[8][path[columnCount][0]][path[columnCount][1]][lineCount-1] = (srfPieceDataList[8][path[columnCount][0]][path[columnCount][1]][lineCount-1] + float(column))/2
                    
        parseSuccess = True
    except Exception as e:
        print e
        parseSuccess = False
        warn = 'Failed to parse the result file.  Check the folder of the file address you are plugging into this component and make sure that there is a .csv file in the folder. \n'+ \
                  'If there is no csv file or there is a file with no data in it (it is 0 kB), your simulation probably did not run correctly. \n' + \
                  'In this case, check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If the csv file is there and it seems like there is data in it (it is not 0 kB), you are probably requesting an output that this component does not yet handle well. \n' + \
                  'If you report this bug of reading the output on the GH forums, we should be able to fix this component to accept the output soon.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)
    finally:
        result.close()
        
    
#Check to make sure that the normalization by surface worked.
if normAreaWorked == False:
    warn = 'Normalizing by surface area does not work if you have more than one type of otherSurfaceData.  All types after the first are not normailzed.'
    print warn
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

#If there was curved geometry, go through the data and see if there were any lists of curved pieces that should be added to the data trees.
def addCurvedDataToTree(zoneList, dataTree):
    for zoneCount, srfList in enumerate(zoneList):
        for srfCount, dataList in enumerate(srfList):
            for item in dataList:
                p = GH_Path(zoneCount, srfCount)
                dataTree.Add(item, p)

if curvedGeometry == True:
    for dataType, zoneList in enumerate(srfPieceDataList):
        if dataType == 0: addCurvedDataToTree(zoneList, surfaceIndoorTemp)
        elif dataType == 1: addCurvedDataToTree(zoneList, surfaceOutdoorTemp)
        elif dataType == 2: addCurvedDataToTree(zoneList, opaqueEnergyFlow)
        elif dataType == 3: addCurvedDataToTree(zoneList, glazEnergyFlow)
        elif dataType == 5: addCurvedDataToTree(zoneList, windowTotalSolarEnergy)
        elif dataType == 6: addCurvedDataToTree(zoneList, windowBeamEnergy)
        elif dataType == 7: addCurvedDataToTree(zoneList, windowDiffEnergy)
        elif dataType == 8: addCurvedDataToTree(zoneList, windowTransmissivity)


# If there is both a list for flow in and out of the surfaces, create a list with the energy flow of all surfaces.
if opaqueEnergyFlow.BranchCount > 0 and str(opaqueEnergyFlow) != "tree {0}" and glazEnergyFlow.BranchCount > 0 and str(glazEnergyFlow) != "tree {0}":
    for i in range(opaqueEnergyFlow.BranchCount):
        path = opaqueEnergyFlow.Path(i)
        branchList = opaqueEnergyFlow.Branch(i)
        for item in branchList:
            surfaceEnergyFlow.Add(item, path)
    for i in range(glazEnergyFlow.BranchCount):
        path = glazEnergyFlow.Path(i)
        branchList = glazEnergyFlow.Branch(i)
        for item in branchList:
            surfaceEnergyFlow.Add(item, path)
    dataTypeList[2] = True

#If some of the component outputs are not in the result csv file, blot the variable out of the component.

outputsDict = {
     
0: ["surfaceIndoorTemp", "The indoor surface temperature of each surface (degrees Celcius)."],
1: ["surfaceOutdoorTemp", "The outdoor surface temperature of each surface (degrees Celcius)."],
2: ["surfaceEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building surfaces (kWh)."],
3: ["opaqueEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building opaque surface (kWh)."],
4: ["glazEnergyFlow", "The heat loss (negative) or heat gain (positive) through each building glazing surface (kWh).  Note that the value here includes both solar gains and conduction losses/gains."],
5: ["windowTotalSolarEnergy", "The total solar energy transmitted through each of the glazing surfaces to the zone (kWh)."],
6: ["windowBeamEnergy", "The total direct solar beam energy transmitted through each of the glazing surfaces to the zone (kWh)."],
7: ["windowDiffEnergy", "The total diffuse solar energy transmitted through each of the glazing surfaces to the zone (kWh)."],
8: ["windowTransmissivity", "The hourly transmissivity of the exterior windows of the model.  This data is needed to align a comfort map with an energy model possessing shades."],
}


if _resultFileAddress and parseSuccess == True:
    for output in range(9):
        if dataTypeList[output] == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
else:
    for output in range(9):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
