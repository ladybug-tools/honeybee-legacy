# This component creates an air temperature map based on an energy simulation output.
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
Use this component to calculate 'Occupied Thermal Comfort Percent' (occTCP) and 'Thermal Autonomy' (TA) from the resultd of a Microclimate Map Analysis.
_
'Occupied Thermal Comfort Percent' (occTCP) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria.
Precedents for Thermal Comfort Percent (TCP) as a metric to spatially evaluate the desirability of a given space can be found in the PhD thesis of Tarek Rakha (http://www.tarekrakha.com/#/research/).
_
'Thermal Autonomy' (TA) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria through passive means only.
Precedents for Thermal Autonomy (TA) as a metric to evaluate the passive operation of a given space can be found in the work of Brendon Levitt.
Levitt, B.; Ubbelohde, M.; Loisos, G.; Brown, N.  Thermal Autonomy as Metric and Design Process. Loisos + Ubbelohde, Alameda, California, California College of the Arts, San Francisco. 2013.
(http://www.coolshadow.com/research/Levitt_Thermal%20Autonomy%20as%20Metric%20and%20Design%20Process.pdf)
-
Provided by Honeybee 0.0.60
    
    Args:
        _comfResultsMtx: A comfort matrix (adaptive, PMV or Outdoor) output from either the 'Honeybee_Microclimate Map Analysis' component or the 'Honeybee_Read Microclimate Matrix' component.
        _degOrPMVMtx: The degreeFromTargetMtx, PMV_Mtx, or DegFromNeutralMtx from either the 'Honeybee_Microclimate Map Analysis' component or the 'Honeybee_Read Microclimate Matrix' component.
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component as surfaces may not align otherwise.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        _totalThermalEnergy_: The totalThermalEnergy output from the "Honeybee_Read EP Result" component.  If no data tree is connected here, it will be assumed that all zones are completely passive and only occupancy will be taken into accout for the Thermal Autonomy calculation.
        occupancyFiles_: Optional occupancy CSV files that will be used to set the occupied period of the Thermal Autonomy calculation.  These can be either EnergyPlus CSV schedules made with the 'Honeybee_Create CSV Schedule' component or Daysim occupancy files made with the 'Honyebee_Daysim Occupancy Generator' component (the two produce files of the same format).  This can be either a list of files that match the connected HBZones or a single occupancy file to be used for all connected zones.  By default, this component will create the occupancy peirod from the occupancy schedule assigned to the connected _HBzones so you should usually not have need for this input and should instead change the HBZone occupancy schedule before running the simulation.
        occupancyThreshold_: An optional number between 0 and 1 that sets the minimum occupancy at which a zone is considered occupied.  This is done as the default occupancy is taken from the HBZone's occupancy schedules and, in some cases this value is low enough to ignore for the sake of calculating thermal autonomy.  The default is set to 0 such that any time when the zones are occpied count towards the values calculated by this component.
        workingDir_: An optional working directory on your system. Default is set to C:\Ladybug
        fileName_: An optional file name for the result files as a string.
        writeResultFile_: Set to 1 or 'True' to have the component write all results into CSV result files and set to 0 or 'False' to not have the component write these files.  The default is set to 'True' as these simulations can be long and you usually want a copy of your results.  You may want to set it to 'False' if you are just scrolling through key hours and want the fastest run possible.  Set to 2 if you want the component to only write the results for the TCPocc and TCA matrices.
        parallel_: Set to 'True' to have the operation run with multiple cores and 'False' to run it with a single core.  Note that, because the calculation performed by this component is fairly simple, setting parallel to 'True' can sometimes increase the calculation time so it should only be used in cases where there are a large number of test points.  Because of the possibility of increaseing calculation time, the default is set to 'False' to run the operation as single-core.
        _runIt: Set boolean to "True" to run the component and calculate comfort autonomy.
    Returns:
        readMe!: ...
        ==========: ...
        occTCP_Mtx: A python matrix containing the 'Themal Comfort Percent' (TCP) values for only the occupied period of the model.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. 'Occupied Thermal Comfort Percent' (occTCP) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria.  This is essentially the same thing as the adaptComfMtx, PMVComfMtx, or outdoorComfMtx but with the unoccupied hours discounted.
        TA_Mtx: A python matrix containing the 'Thermal Autonomy' (TA) values for each of the faces of the connected _viewFactorMesh. Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. 'Thermal Autonomy' (TA) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria through passive means only.
        OverHeatedMtx: A python matrix containing the overheated hours for each of the faces of the connected _viewFactorMesh.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. Overheated hours are essentially the number of occupied hours that a point is warmer than that specified by a given set of thermal comfort acceptability criteria.
        UnderHeatedMtx: A python matrix containing the underheated hours for each of the faces of the connected _viewFactorMesh.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. Underheated hours are essentially the number of occupied hours that a point is colder than that specified by a given set of thermal comfort acceptability criteria.
        ==========: ...
        occTCP_Result: A csv file address containing the 'Themal Comfort Percent' (TCP) values for only the occupied period of the model.
        TA_Result: A csv file address containing the 'Thermal Autonomy' (TA) values for each of the faces of the connected _viewFactorMesh.
        OverHeatedResult: A csv file address containing the overheated hours for each of the faces of the connected _viewFactorMesh.
        UnderHeatedResult: A csv file address containing the underheated hours for each of the faces of the connected _viewFactorMesh.

"""

ghenv.Component.Name = "Honeybee_Thermal Autonomy Analysis"
ghenv.Component.NickName = 'ThermalAutonomy'
ghenv.Component.Message = 'VER 0.0.60\nSEP_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass


import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc
import math
import os
import System.Threading.Tasks as tasks


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance

outputsDict = {
    
0: ["readMe!", "..."],
1: ["===========", "..."],
2: ["occTCP_Mtx", "A python matrix containing the 'Themal Comfort Percent' (TCP) values for only the occupied period of the model.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. 'Occupied Thermal Comfort Percent' (occTCP) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria.  This is essentially the same thing as the adaptComfMtx, PMVComfMtx, or outdoorComfMtx but with the unoccupied hours discounted."],
3: ["TA_Mtx", "A python matrix containing the 'Thermal Autonomy' (TA) values for each of the faces of the connected _viewFactorMesh. Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. 'Thermal Autonomy' (TA) is defined here as the the percent of occupied time where a point of space meets or exceeds a given set of thermal comfort acceptability criteria through passive means only."],
4: ["OverHeatedMtx", "A python matrix containing the overheated hours for each of the faces of the connected _viewFactorMesh.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. Overheated hours are essentially the number of occupied hours that a point is warmer than that specified by a given set of thermal comfort acceptability criteria."],
5: ["UnderHeatedMtx", "A python matrix containing the underheated hours for each of the faces of the connected _viewFactorMesh.  Connect this to the 'Honeybee_Visualize Microclimate Map' component in order to display the data. Underheated hours are essentially the number of occupied hours that a point is colder than that specified by a given set of thermal comfort acceptability criteria."],
6: ["===========", "..."],
7: ["occTCP_Result", "A csv file address containing the 'Themal Comfort Percent' (TCP) values for only the occupied period of the model."],
8: ["TA_Result", "A csv file address containing the 'Thermal Autonomy' (TA) values for each of the faces of the connected _viewFactorMesh."],
9: ["OverHeatedResult", "A csv file address containing the overheated hours for each of the faces of the connected _viewFactorMesh."],
10: ["UnderHeatedResult", "A csv file address containing the underheated hours for each of the faces of the connected _viewFactorMesh."]
}


def recallHBZoneProperties(HOYs, occupancyThere):
    #Make a list of occupancy schedules to be filled.
    occupancySchList = []
    zoneNames = []
    checkZones = True
    
    #Calls the zones and the libraries from the hive.
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
    
    for zoneCount, HZone in enumerate(_HBZones):
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        zoneNames.append(zone.name)
        values = []
        if occupancyThere == False:
            zoneOccSched = zone.occupancySchedule
            zoneOccSched = zoneOccSched.upper()
            if not zoneOccSched.lower().endswith(".csv"):
                if zoneOccSched not in HBScheduleList:
                    msg = "Cannot find " + zoneOccSched + " in Honeybee schedule library."
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    checkZones = False
                else:
                    readSchedules = sc.sticky["honeybee_ReadSchedules"](zoneOccSched, 0)
                    values  = readSchedules.getScheduleValues()
            elif zoneOccSched.lower().endswith(".csv"):
                # check if csv file exists.
                if not os.path.isfile(zoneOccSched):
                    msg = "Cannot find the shchedule file: " + zoneOccSched
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    checkZones = False
                else:
                    result = open(zoneOccSched, 'r')
                    for lineCount, line in enumerate(result):
                        if lineCount < 4: pass
                        else:
                            for columnCount, column in enumerate(line.split(',')):
                                if columnCount == 4:
                                    values.append(float(column))
            try: values = lb_preparation.flattenList(values)
            except: pass
            analysisPValues = []
            for hour in HOYs:
                analysisPValues.append(values[hour-1])
            occupancySchList.append(analysisPValues)
    
    
    return checkZones, zoneNames, occupancySchList

def manageOutput():
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(11):
        if input > 6 and writeResultFile_ == 0:
            ghenv.Component.Params.Output[input].NickName = "__________"
            ghenv.Component.Params.Output[input].Name = "."
            ghenv.Component.Params.Output[input].Description = " "
        elif input > 8 and writeResultFile_ == 2:
            ghenv.Component.Params.Output[input].NickName = "__________"
            ghenv.Component.Params.Output[input].Name = "."
            ghenv.Component.Params.Output[input].Description = " "
        else:
            ghenv.Component.Params.Output[input].NickName = outputsDict[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDict[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDict[input][1]

#Create a function to check and create a Python list from a datatree
def checkCreateDataTree(dataTree, dataName, dataType):
    dataPyList = []
    for i in range(dataTree.BranchCount):
        branchList = dataTree.Branch(i)
        dataVal = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataVal.append(item)
        dataPyList.append(dataVal)
    
    #Test to see if the data has a header on it, which is necessary to know if it is the right data type.  If there's no header, the data should not be vizualized with this component.
    checkHeader = []
    dataHeaders = []
    dataNumbers = []
    for list in dataPyList:
        if str(list[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
            checkHeader.append(1)
            dataHeaders.append(list[:7])
            dataNumbers.append(list[7:])
        else:
            dataNumbers.append(list)
    
    if sum(checkHeader) == len(dataPyList):
        dataCheck2 = True
    else:
        dataCheck2 = False
        warning = "Not all of the connected " + dataName + " has a Ladybug/Honeybee header on it.  This header is necessary to generate an indoor temperture map with this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that the lengths of data in in the dataTree branches are all the same.
    dataLength = len(dataNumbers[0])
    dataLenCheck = []
    for list in dataNumbers:
        if len(list) == dataLength:
            dataLenCheck.append(1)
        else: pass
    if sum(dataLenCheck) == len(dataNumbers) and dataLength <8761:
        dataCheck4 = True
    else:
        dataCheck4 = False
        warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if dataCheck2 == True:
        #Check to be sure that all of the data headers say that they are of the same type.
        header = dataHeaders[0]
        
        headerUnits =  header[3]
        headerStart = header[5]
        headerEnd = header[6]
        simStep = str(header[4])
        headUnitCheck = []
        headPeriodCheck = []
        for head in dataHeaders:
            if dataType in head[2]:
                headUnitCheck.append(1)
            if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                headPeriodCheck.append(1)
            else: pass
        
        if sum(headPeriodCheck) == len(dataHeaders):
            dataCheck5 = True
        else:
            dataCheck5 = False
            warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if sum(headUnitCheck) == len(dataHeaders):
            dataCheck6 = True
        else:
            dataCheck6 = False
            warning = "Not all of the connected " + dataName + " data is for total thermal energy."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        #See if the data is hourly.
        if simStep == 'hourly' or simStep == 'Hourly': pass
        else:
            dataCheck6 = False
            warning = "Simulation data must be hourly."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
    else:
        dataCheck5 = False
        dataCheck6 == False
        if dataLength == 8760: annualData = True
        else: annualData = False
        simStep = 'unknown timestep'
        headerUnits = 'unknown units'
        dataHeaders = []
    
    return dataCheck5, dataCheck6, headerUnits, dataHeaders, dataNumbers, [header[5], header[6]]

def checkOccupancyFile(occupancyFile, HOYs):
    checkData5 = True
    if occupancyFile.lower().endswith(".csv"):
        # check if csv file exists.
        if not os.path.isfile(occupancyFile):
            msg = "Cannot find the shchedule file: " + occupancyFile
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            checkData5 = False
        else:
            values = []
            result = open(occupancyFile, 'r')
            for lineCount, line in enumerate(result):
                if lineCount < 4: pass
                else:
                    for columnCount, column in enumerate(line.split(',')):
                        if columnCount == 4: values.append(float(column))
            if len(values) == 8760:
                analysisPValues = []
                for hour in HOYs:
                    analysisPValues.append(values[hour-1])
            else:
                msg = "The connected occupancy file must contain 8760 values for each hour of the year."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                checkData5 = False
    else:
        msg = "The connected occupancy file must be a csv file path."
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        checkData5 = False
    
    return checkData5, analysisPValues

def checkTheInputs():
    #Set a default fileName.
    lb_defaultFolder = sc.sticky["Ladybug_DefaultFolder"]
    if fileName_ == None:
        fileName = 'unnamed'
    else: fileName = fileName_.strip()
    
    #Check the directory or set a default.
    if workingDir_: workingDir = lb_preparation.removeBlankLight(workingDir_)
    else: workingDir = lb_defaultFolder
    workingDir = os.path.join(workingDir, fileName, "ComfortAnalysis")
    workingDir = lb_preparation.makeWorkingDir(workingDir)
    
    #Check to be sure that the length of the mesh faces and result matrices match.
    checkData1 = False
    comfortType = ""
    comfortType = _comfResultsMtx[0].split(" ")[0]
    ptLen1 = len(_comfResultsMtx[1])
    ptLen3 = len(_degOrPMVMtx[1])
    meshFaceCount = []
    for mesh in _viewFactorMesh:
        meshFaceCount.append(mesh.Faces.Count)
    ptLen2 = sum(meshFaceCount)
    if ptLen1 == ptLen2 == ptLen3: checkData1 = True
    else:
        warning = "The length of data in the _comfResultsMTX and/or _degOrPMVMtx does not match the number of faces in the _viewFactorMesh."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the analysis period.
    try:
        analysisPeriod1 = (int(_comfResultsMtx[0].split(";")[-2].split(",")[0].split("(")[-1]), int(_comfResultsMtx[0].split(";")[-2].split(",")[1].split(" ")[-1]), int(_comfResultsMtx[0].split(";")[-2].split(",")[-1].split(" ")[-1].split(")")[0]))
        analysisPeriod2 = (int(_comfResultsMtx[0].split(";")[-1].split(",")[0].split("(")[-1]), int(_comfResultsMtx[0].split(";")[-1].split(",")[1].split(" ")[-1]), int(_comfResultsMtx[0].split(";")[-1].split(",")[-1].split(" ")[-1].split(")")[0]))
        analysisPeriod = [analysisPeriod1, analysisPeriod2]
    except:
        analysisPeriod = []
    
    #Check to be sure that the occupancy period of the totalThermalEnergy and that of the comfort matrix are not in conflict.
    checkData2 = True
    if analysisPeriod != []: HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
    else: HOYs = []
    if _totalThermalEnergy_.BranchCount > 0: checkData3, checkData4, totEnergyUnits, totEnergyHeaders, totEnergyNumbers, totEAnalysisPeriod = checkCreateDataTree(_totalThermalEnergy_, "_totalThermalEnergy_", "Total Thermal Energy")
    else:
        checkData3, checkData4 = True, True
        totEAnalysisPeriod = analysisPeriod
        totEnergyHeaders, totEnergyNumbers = [], []
        for zone in _HBZones:
            totEnergyHeaders.append(0)
            totEnergyNumbers.append(0)
    if analysisPeriod == totEAnalysisPeriod:
        totEnergyNumbersFinal = totEnergyNumbers
    else:
        energyHOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(totEAnalysisPeriod, 1)
        totEnergyNumbersFinal = []
        for numList in totEnergyNumbers: totEnergyNumbersFinal.append([])
        for hour in HOYs:
            foundHour = False
            for hourCount, eHour in enumerate(energyHOYs):
                if hour == eHour:
                    for zoneCount, zoneList in enumerate(totEnergyNumbersFinal): zoneList.append(totEnergyNumbers[zoneCount][hourCount])
                    foundHour = True
            if foundHour == False: checkData2 = False
        if checkData2 == False:
            warning = "Not all of the hours in the _comfResultsMtx can be found in the _totalThermalEnergy_ data tree."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    # Check if there are occupancy files attached and, if not, pull the occupancy from the HBZones.
    checkData5 = False
    if len(occupancyFiles_) == 0:
        checkData5, zoneNames, occupancySchList = recallHBZoneProperties(HOYs, False)
    elif len(occupancyFiles_) == 1:
        checkData5, zoneNames, occupancySchList = recallHBZoneProperties(HOYs, True)
        checkData5, analysisPValues = checkOccupancyFile(occupancyFiles_[0], HOYs)
        occupancySchList = []
        for zone in _HBZones: occupancySchList.append(analysisPValues)
    elif len(occupancyFiles_) == len(_HBZones):
        checkData5, zoneNames, occupancySchList = recallHBZoneProperties(HOYs, True)
        initCheckList = []
        occupancySchList = []
        for file in occupancyFiles_:
            initCheck, analysisPValues = checkOccupancyFile(file, HOYs)
            if initCheck == True: initCheckList.append(1)
            occupancySchList.append(analysisPValues)
        if sum(initCheckList) == len(occupancyFiles_): checkData5 = True
        else: checkData5 = False
    else:
        warning = "The input into the occupancyFiles_ must be either a single csv file to be used for all zones or a list of csv files that match each of the input _HBZones."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Set a default occupancy threshold.
    checkData6 = True
    occupancyThreshold = 0
    if occupancyThreshold_ == None: pass
    else:
        if occupancyThreshold_ >= 0 and occupancyThreshold <= 1: occupancyThreshold = occupancyThreshold_
        else:
            checkData6 = False
            warning = "The occupancyThreshold_ must be a value between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True: checkData = True
    else: checkData = False
    
    return checkData, fileName, workingDir, _viewFactorMesh, analysisPeriod, totEnergyHeaders, totEnergyNumbersFinal, zoneNames, occupancySchList, comfortType, occupancyThreshold


def main(viewFactorMesh, analysisPeriod, totEnergyHeaders, totEnergyNumbers, zoneNames, occupancySchList, comfortType, occupancyThreshold):
    #Set up matrices to be filled.
    occTCP_Mtx = [comfortType + ' Occupied Thermal Comfort Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    TA_Mtx = [comfortType + ' Thermal Autonomy;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    OverHeatedMtx = [comfortType + ' Over-Heated Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    UnderHeatedMtx = [comfortType + ' Under-Heated Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Create placeholders for all of the hours.
    for hour in occupancySchList[0]:
        occTCP_Mtx.append(0)
        TA_Mtx.append(0)
        OverHeatedMtx.append(0)
        UnderHeatedMtx.append(0)
   
    #Match the totalEnergy values to the HBZones.
    totEnergyNumbersMatched = []
    for name in zoneNames:
        eFound = False
        for headCount, header in enumerate(totEnergyHeaders):
            try:
                if header[2].split(' for ')[-1].upper() == name.upper():
                    eFound = True
                    totEnergyNumbersMatched.append(totEnergyNumbers[headCount])
            except: pass
        if eFound == False:
            additionalENumList = []
            for count in occupancySchList[0]: additionalENumList.append(0)
            totEnergyNumbersMatched.append(additionalENumList)
    
    #Match each of the test points with a zone using the viewFacorMesh.
    pointZoneList = []
    outDoorPtsCount = 0
    for mesh in viewFactorMesh:
        for face in mesh.Faces:
            zoneFound = False
            if face.IsQuad:
                faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), rc.Geometry.Point3d(mesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
            if face.IsTriangle:
                faceBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(mesh.Vertices[face.A]), rc.Geometry.Point3d(mesh.Vertices[face.B]), rc.Geometry.Point3d(mesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
            centPt = rc.Geometry.AreaMassProperties.Compute(faceBrep).Centroid
            for zoneCount, zone in enumerate(_HBZones):
                if zone.IsPointInside(centPt, tol, False) == True:
                    zoneFound = True
                    pointZoneList.append(zoneCount)
            if zoneFound == False:
                outDoorPtsCount += 1
                pointZoneList.append(len(_HBZones))
    
    #If there are outdoor points, append values for full-time occupancy and use of passive strategies.
    if outDoorPtsCount > 0:
        additionalENumList = []
        additionalOccSchList = []
        for count in occupancySchList[0]:
            additionalENumList.append(0)
            additionalOccSchList.append(1)
        occupancySchList.append(additionalOccSchList)
        totEnergyNumbersMatched.append(additionalENumList)
    
    #Make a list that tracks the total occupied hours for each of the points.
    occHrsNum = []
    for point in pointZoneList: occHrsNum.append(0)
    
    #Finally, compute the matrices for each hour and point.
    def calcComf(count):
        occTCP = []
        TA = []
        OverHeated = []
        UnderHeated = []
        for pointCount, pointZone in enumerate(pointZoneList):
            #Check to see if the point's zone is occupied.  Otheriswe, it does not count for anything.
            if occupancySchList[pointZone][count] > occupancyThreshold:
                occHrsNum[pointCount] += 1
                #Check to see if the point is comfortable.
                if _comfResultsMtx[count + 1][pointCount] > 0:
                    occTCP.append(1)
                    OverHeated.append(0)
                    UnderHeated.append(0)
                    #Check to see if the point's zone is being conditioned.
                    if totEnergyNumbersMatched[pointZone][count] > 0: TA.append(0)
                    else: TA.append(1)
                else:
                    occTCP.append(0)
                    TA.append(0)
                    if _degOrPMVMtx[count + 1][pointCount] > 0:
                        OverHeated.append(1)
                        UnderHeated.append(0)
                    else:
                        OverHeated.append(0)
                        UnderHeated.append(1)
            else:
                occTCP.append(0.0)
                TA.append(0.0)
                OverHeated.append(0.0)
                UnderHeated.append(0.0)
        
        occTCP_Mtx[count+1] = occTCP
        TA_Mtx[count+1] = TA
        OverHeatedMtx[count+1] = OverHeated
        UnderHeatedMtx[count+1] = UnderHeated
    
    #Run through every hour of the analysis to fill up the matrices.
    #if parallel_ == True and len(occupancySchList[0]) != 1:
    #    tasks.Parallel.ForEach(range(len(occupancySchList[0])), calcComf)
    #else:
    for hour in range(len(occupancySchList[0])):
        calcComf(hour)
    
    # Add the total occupied hours to the matrix (to be used to help calculate comfort autonomy).
    occTCP_Mtx.append(occHrsNum)
    TA_Mtx.append(occHrsNum)
    OverHeatedMtx.append(occHrsNum)
    UnderHeatedMtx.append(occHrsNum)
    
    
    return occTCP_Mtx, TA_Mtx, OverHeatedMtx, UnderHeatedMtx

def writeCSV(comfortType, fileName, directory, occTCP_Mtx, TA_Mtx, OverHeatedMtx, UnderHeatedMtx):
    #Find out the number of values in each hour.
    valLen = len(occTCP_Mtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(directory)) 
    
    #Create csv files.
    occTCPFile = fileName + comfortType + "occTCP.csv"
    TAFile = fileName + comfortType + "TA.csv"
    OverHeatedFile = fileName + comfortType + "OverHeated.csv"
    UnderHeatedFile = fileName + comfortType + "UnderHeated.csv"
    
    #Write the occTCP result file.
    occTCP_Result = os.path.join(workingDir, occTCPFile)
    occTCPCSVfile = open(occTCP_Result, 'wb')
    for lineCount, line in enumerate(occTCP_Mtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            occTCPCSVfile.write(lineStr)
        else: occTCPCSVfile.write(line + "\n")
    occTCPCSVfile.close()
    
    #Write the TA result file.
    TA_Result = os.path.join(workingDir, TAFile)
    TACSVfile = open(TA_Result, 'wb')
    for lineCount, line in enumerate(TA_Mtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            TACSVfile.write(lineStr)
        else: TACSVfile.write(line + "\n")
    TACSVfile.close()
    
    #Write the OverHeated result file.
    if writeResultFile_ != 2:
        OverHeatedResult = os.path.join(workingDir, OverHeatedFile)
        OverHeatedCSVfile = open(OverHeatedResult, 'wb')
        for lineCount, line in enumerate(OverHeatedMtx):
            lineStr = ''
            if lineCount != 0:
                for valCt, val in enumerate(line):
                    if valCt != valLen: lineStr = lineStr + str(val) + ','
                    else: lineStr = lineStr + str(val) + "\n"
                OverHeatedCSVfile.write(lineStr)
            else: OverHeatedCSVfile.write(line + "\n")
        OverHeatedCSVfile.close()
    else:
        OverHeatedResult = None
    
    #Write the UnderHeated result file.
    if writeResultFile_ != 2:
        UnderHeatedResult = os.path.join(workingDir, UnderHeatedFile)
        UnderHeatedCSVfile = open(UnderHeatedResult, 'wb')
        for lineCount, line in enumerate(UnderHeatedMtx):
            lineStr = ''
            if lineCount != 0:
                for valCt, val in enumerate(line):
                    if valCt != valLen: lineStr = lineStr + str(val) + ','
                    else: lineStr = lineStr + str(val) + "\n"
                UnderHeatedCSVfile.write(lineStr)
            else: UnderHeatedCSVfile.write(line + "\n")
        UnderHeatedCSVfile.close()
    else:
        UnderHeatedResult = None
    
    
    return occTCP_Result, TA_Result, OverHeatedResult, UnderHeatedResult




#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release') and sc.sticky.has_key('honeybee_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    checkLB = False
    print "You should let the Ladybug and Honeybee fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug and Honeybee fly first...")

#Manage the input and output.
manageOutput()

checkData = False
annualData = True
simStepPossible = True
if len(_comfResultsMtx) > 0 and len(_degOrPMVMtx) >0 and len(_viewFactorMesh) > 0 and len(_HBZones) > 0 and checkLB == True:
    if _comfResultsMtx[0] != None and _viewFactorMesh[0] != None:
        checkData, fileName, workingDir, viewFactorMesh, analysisPeriod, totEnergyHeaders, totEnergyNumbers, zoneNames, occupancySchList, comfortType, occupancyThreshold = checkTheInputs()
    
    if checkData == True and _runIt == True:
        occTCP_Mtx, TA_Mtx, OverHeatedMtx, UnderHeatedMtx = main(viewFactorMesh, analysisPeriod, totEnergyHeaders, totEnergyNumbers, zoneNames, occupancySchList, comfortType, occupancyThreshold)
        if writeResultFile_ != 0: 
            occTCP_Result, TA_Result, OverHeatedResult, UnderHeatedResult = writeCSV(comfortType, fileName, workingDir, occTCP_Mtx, TA_Mtx, OverHeatedMtx, UnderHeatedMtx)