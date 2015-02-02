# This component creates an air temperature map based on an energy simulation output.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create an indoor air temperature map based on airTemperature output of the "Honeybee_Read EP Result" component.
_
By default, the temperature map will be created based on the average value of air temperature for each zone.
If total annual simulation data has been connected, the analysisPeriod_ input can be used to select out a specific period fo the year for coloration.
In order to color surfaces by individual hours, connecting interger values to the "stepOfSimulation_" will allow you to scroll though each step of the input data.
-
Provided by Honeybee 0.0.55
    
    Args:
        _zoneAirTemp: The airTemperature output of the "Honeybee_Read EP Result" component.
        _zoneRelHumid: The relativeHumidity output of the "Honeybee_Read EP Result" component.
        _zoneAirFlowVol: The airFlowVolume output of the "Honeybee_Read EP Result" component.
        _zoneAirHeatGain: The airHeatGainRate output of the "Honeybee_Read EP Result" component.
        ===============: ...
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".  These will be colored with air temperature data.
        _testPtZoneWeights: The testPtZoneWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with the weights of values of each zone for each of the test points.
        _testPtZoneNames: The testPtZoneNames output of the "Honeybee_Indoor View Factor Calculator" component.  This is essentially a branched data tree with the zone name of each of the test points.
        _ptHeightWeights: The ptHeightWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with weights of values for each point depending upon their height in the space and will be used to account for stratification in each zone.
        _zoneInletInfo: The zoneInletInfo output of the 'Honeybee_Indoor View Factor Calculator' component.  Tis is essentially a data tree that carries information about the height of the zone and the height of inlets through the windows and is used in the calculation of thermal stratification.
        ===============: ...
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to "stepOfSimulation_" will override this input.
        stepOfSimulation_: Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        _runIt: Set boolean to "True" to run the component and create the indoor air temperature map.
    Returns:
        readMe!: ...
        airTempMesh: A list of colored meshes showing the distribution of air temperature over each input _HBZone.
        legend: A legend for the air temperature map. Connect this output to a grasshopper "Geo" component in order to preview the legend spearately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the building with the grasshopper "move" component.
        ==========: ...
        testPtsAirTemp: The values of air temperature at each of the test points (this is what is used to  being used to color the mesh).
        testPtsRelHumid: The values of relative hunidity at each of the test points.

"""

ghenv.Component.Name = "Honeybee_Indoor Air Temperature Map"
ghenv.Component.NickName = 'AirTempMap'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


from System import Object
from System import Drawing
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc
import math



inputsDict = {
    
0: ["_zoneAirTemp", "The airTemperature output of the 'Honeybee_Read EP Result' component."],
1: ["_zoneRelHumid", "The relativeHumidity output of the 'Honeybee_Read EP Result' component."],
2: ["_zoneAirFlowVol", "The airFlowVolume output of the 'Honeybee_Read EP Result' component."],
3: ["_zoneAirHeatGain", "The totalIntHeatGain output of the 'Honeybee_Read EP Result' component."],
4: ["=============", "..."],
5: ["_viewFactorMesh", "The list of view factor meshes that comes out of the  'Honeybee_Indoor View Factor Calculator'.  These will be colored with air temperature data."],
6: ["_testPtZoneWeights", "The testPtZoneWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with the weights of values of each zone for each of the test points."],
7: ["_testPtZoneNames", "The testPtZoneNames output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a list with the names of each zone."],
8: ["_ptHeightWeights", "The ptHeightWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with weights of values for each point depending upon their height in the space and will be used to account for stratification in each zone."],
9: ["_zoneInletInfo", "The zoneInletInfo output of the 'Honeybee_Indoor View Factor Calculator' component.  Tis is essentially a data tree that carries information about the height of the zone and the height of inlets through the windows and is used in the calculation of thermal stratification."],
10: ["=============", "..."],
11: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input."],
12: ["stepOfSimulation_", "Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input."],
13: ["legendPar_", "Optional legend parameters from the Ladybug 'Legend Parameters' component."],
14: ["_runIt", "Set boolean to 'True' to run the component and create the indoor air temperature map.."]
}


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
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
            checkData2 = True
        else:
            checkData2 = False
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
            checkData4 = True
        else:
            checkData4 = False
            warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if checkData2 == True:
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
                checkData5 = True
            else:
                checkData5 = False
                warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if sum(headUnitCheck) == len(dataHeaders):
                checkData6 = True
            else:
                checkData6 = False
                warning = "Not all of the connected " + dataName + " data correct."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            #See if the data is for the whole year.
            if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
                annualData = True
            else: annualData = False
            
        else:
            checkData5 = False
            checkData6 = False
            if dataLength == 8760: annualData = True
            else: annualData = False
            simStep = 'unknown timestep'
            headerUnits = 'unknown units'
            dataHeaders = []
        
        return checkData5, checkData6, annualData, simStep, headerUnits, dataHeaders, dataNumbers
    
    
    checkData1, checkData2, annualData1, simStep1, airTempUnits, airTempDataHeaders, airTempDataNumbers = checkCreateDataTree(_zoneAirTemp, "_zoneAirTemp", "Air Temperature")
    checkData3, checkData4, annualData2, simStep2, humidityUnits, relHumidDataHeaders, relHumidDataNumbers = checkCreateDataTree(_zoneRelHumid, "_zoneRelHumid", "Relative Humidity")
    checkData14, checkData15, annualData3, simStep3, flowVolUnits, flowVolDataHeaders, flowVolDataNumbers = checkCreateDataTree(_zoneAirFlowVol, "_zoneAirFlowVol", "Air Flow Volume")
    checkData16, checkData17, annualData4, simStep4, heatGainUnits, heatGainDataHeaders, heatGainDataNumbers = checkCreateDataTree(_zoneAirHeatGain, "_zoneAirHeatGain", "Air Heat Gain Rate")
    
    #Check to be sure that the units of flowVol and heat gain are correct.
    checkData19 = True
    if flowVolUnits == "m3/s": pass
    else:
        checkData19 = False
        warning = "_zoneFlowVol must be in m3/s."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData20 = True
    if heatGainUnits == "W": pass
    else:
        checkData19 = False
        warning = "_zoneHeatGain must be in W."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that info matches between the lists.
    checkData7 = True
    if annualData1 == annualData2 == annualData3 == annualData4: annualData = annualData1
    else:
        annualData = None
        checkData7 = False
        warning = "_zoneAirTemp, _zoneRelHumid, _zoneAirFlowVol or _zoneAirHeatGain are for different time periods."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData8 = True
    if simStep1 == simStep2 == simStep3 == simStep4: simStep = simStep1
    else:
        simStep = None
        checkData8 = False
        warning = "_zoneAirTemp, _zoneRelHumid, _zoneAirFlowVol or _zoneAirHeatGain are for different simulation steps."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the list of _testPtZoneNames.
    testPtZoneNames = []
    checkData9 = True
    if len(_testPtZoneNames) > 0: testPtZoneNames = _testPtZoneNames
    else:
        checkData9 = False
        print "Connect a data tree of testPtZoneNames from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _testPtZoneWeights to py data.
    testPtZoneWeights = []
    checkData12 = True
    if _testPtZoneWeights.BranchCount != 0:
        if _testPtZoneWeights.Branch(0)[0] != None:
            for i in range(_testPtZoneWeights.BranchCount):
                zoneBranch = _testPtZoneWeights.Path(i)[0]
                branchList = _testPtZoneWeights.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: testPtZoneWeights[zoneBranch].append(dataVal)
                except:
                    testPtZoneWeights.append([])
                    testPtZoneWeights[zoneBranch].append(dataVal)
        else:
            checkData12 = False
            print "Connect a data tree of test point zone weights from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData12 = False
        print "Connect a data tree of test point zone weights from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _ptHeightWeights to py data.
    ptHeightWeights = []
    checkData13 = True
    if _ptHeightWeights.BranchCount != 0:
        if _ptHeightWeights.Branch(0)[0] != None:
            for i in range(_ptHeightWeights.BranchCount):
                zoneBranch = _ptHeightWeights.Path(i)[0]
                branchList = _ptHeightWeights.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: ptHeightWeights[zoneBranch].extend(dataVal)
                except:
                    ptHeightWeights.append([])
                    ptHeightWeights[zoneBranch].extend(dataVal)
        else:
            checkData13 = False
            print "Connect a data tree of test point height weights from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData13 = False
        print "Connect a data tree of test point height weights from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _viewFactorMesh to py data.
    viewFactorMesh = []
    checkData10 = True
    if _viewFactorMesh.BranchCount != 0:
        if _viewFactorMesh.Branch(0)[0] != None:
            for i in range(_viewFactorMesh.BranchCount):
                branchList = _viewFactorMesh.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                viewFactorMesh.append(dataVal)
        else:
            checkData10 = False
            print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData10 = False
        print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Check to be sure that the number of mesh faces and test points match.
    checkData11 = True
    if checkData10 == True and checkData12 == True:
        for zoneCount, zone in enumerate(viewFactorMesh):
            if len(zone) != 1:
                totalFaces = 0
                for meshCount, mesh in enumerate(zone):
                    totalFaces = totalFaces +mesh.Faces.Count
                if totalFaces == len(testPtZoneWeights[zoneCount]): pass
                else:
                    checkData11 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtZoneWeights do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                if zone[0].Faces.Count == len(testPtZoneWeights[zoneCount]): pass
                else:
                    checkData11 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtZoneWeights do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Convert the list of zoneInletInfo to py data.
    zoneInletInfo = []
    checkData18 = True
    if _zoneInletInfo.BranchCount != 0:
        if _zoneInletInfo.Branch(0)[0] != None:
            for i in range(_zoneInletInfo.BranchCount):
                zoneBranch = _zoneInletInfo.Path(i)[0]
                branchList = _zoneInletInfo.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: zoneInletInfo[zoneBranch].extend(dataVal)
                except:
                    zoneInletInfo.append([])
                    zoneInletInfo[zoneBranch].extend(dataVal)
        else:
            checkData18 = False
            print "Connect a data tree of zoneInletInfo from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData18 = False
        print "Connect a data tree of zoneInletInfo from the 'Honeybee_Indoor View Factor Calculator' component."
    if len(zoneInletInfo) != len(testPtZoneNames):
        checkData18 = False
        print "The length of the _testPtZoneNames list does not match the number of branches in the _zoneInletInfo."
    
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True and checkData14 == True and checkData15 == True and checkData16 == True and checkData17 == True and checkData18 == True and checkData19 == True and checkData20 == True:
        checkData = True
    else: checkData = False
    
    return checkData, annualData, simStep, airTempUnits, airTempDataHeaders, airTempDataNumbers, relHumidDataHeaders, relHumidDataNumbers, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, testPtZoneNames, testPtZoneWeights, ptHeightWeights, viewFactorMesh, zoneInletInfo

def manageInputOutput(annualData, simStep):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(15):
        if input == 10 and annualData == False:
            ghenv.Component.Params.Input[input].NickName = "___________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 11 and (simStep == "Annually" or simStep == "unknown timestep"):
            ghenv.Component.Params.Input[input].NickName = "____________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    if annualData == False: analysisPeriod = [0, 0]
    else: analysisPeriod = analysisPeriod_
    if simStep == "Annually" or simStep == "unknown timestep": stepOfSimulation = None
    else: stepOfSimulation = stepOfSimulation_
    
    return analysisPeriod, stepOfSimulation

def restoreInputOutput():
    for input in range(15):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]



def getData(pyZoneData, annualData, simStep, zoneHeaders, headerUnits, analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization):
    #Make a list to contain the data for coloring and labeling.
    dataForColoring = []
    normedZoneData = []
    coloredTitle = []
    coloredUnits = None
    
    #Add basic stuff to the title.
    coloredTitle.append(str(zoneHeaders[0][2].split("for")[0]) + " - " + headerUnits)
    coloredUnits = headerUnits
    
    #Make lists that assist with the labaeling of the rest of the title.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
    
    #If none of the analysisperiod or stepOfSim are connected, just total or average all the data.
    def getColorData1():
        for list in pyZoneData:
            dataForColoring.append(round(sum(list), 4)/len(list))
    
    if analysisPeriod == [0, 0] and stepOfSimulation == None:
        getColorData1()
        if zoneHeaders != []:
            coloredTitle.append(str(monthNames[zoneHeaders[0][5][0]-1]) + " " + str(zoneHeaders[0][5][1]) + " " + str(timeNames[zoneHeaders[0][5][2]-1]) + " - " + str(monthNames[zoneHeaders[0][6][0]-1]) + " " + str(zoneHeaders[0][6][1]) + " " + str(timeNames[zoneHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    if analysisPeriod == [] and stepOfSimulation == None:
        getColorData1()
        if zoneHeaders != []:
            coloredTitle.append(str(monthNames[zoneHeaders[0][5][0]-1]) + " " + str(zoneHeaders[0][5][1]) + " " + str(timeNames[zoneHeaders[0][5][2]-1]) + " - " + str(monthNames[zoneHeaders[0][6][0]-1]) + " " + str(zoneHeaders[0][6][1]) + " " + str(timeNames[zoneHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    elif simStep == "Annually" or simStep == "unknown timestep":
        getColorData1()
        if zoneHeaders != []:
            coloredTitle.append(str(monthNames[zoneHeaders[0][5][0]-1]) + " " + str(zoneHeaders[0][5][1]) + " " + str(timeNames[zoneHeaders[0][5][2]-1]) + " - " + str(monthNames[zoneHeaders[0][6][0]-1]) + " " + str(zoneHeaders[0][6][1]) + " " + str(timeNames[zoneHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    
    # If the user has connected a stepOfSim, make the step of sim the thing used to color zones.
    if stepOfSimulation != None:
        if stepOfSimulation < len(pyZoneData[0]):
            for list in pyZoneData:
                dataForColoring.append(round(list[stepOfSimulation], 4))
            
            if simStep == "Monthly" and annualData == True: coloredTitle.append(monthNames[stepOfSimulation])
            elif simStep == "Monthly": coloredTitle.append("Month " + str(stepOfSimulation+1) + " of Simulation")
            elif simStep == "Daily": coloredTitle.append("Day " + str(stepOfSimulation+1) + " of Simulation")
            elif simStep == "Hourly": coloredTitle.append("Hour " + str(stepOfSimulation+1) + " of Simulation")
            else: coloredTitle.append("Step " + str(stepOfSimulation+1) + " of Simulation")
        else:
            warning = "The input step of the simulation is beyond the length of the simulation."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    # If the user has connected annual data, has not hooked up a step of simulation, and has hooked up an analysis period, take data from just the analysis period.
    if annualData == True and analysisPeriod != [0,0] and analysisPeriod != [] and stepOfSimulation == None and simStep != "Annually" and simStep != "unknown timestep":
        #If the data is monthly, just take the months from the analysis period.
        if simStep == "Monthly":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startMonth:endMonth+1])/len(list[startMonth:endMonth+1]), 4))
            coloredTitle.append(str(monthNames[startMonth-1]) + " - " + str(monthNames[endMonth-1]))
        #If the data is daily, just take the days and months from the analysis period.
        elif simStep == "Daily":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            #Make a function that returns the days for a given list of months
            def getDays(monthsList, startDay, endDay):
                daysList = []
                daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                for count, month in enumerate(monthsList):
                    if count == 0 and startMonth == endMonth:
                        daysList.append(daysPerMonth[month-1] + 1 - startDay + (endDay - daysPerMonth[month-1]))
                    elif count == 0:
                        daysList.append(daysPerMonth[month-1] + 1 - startDay)
                    elif count == len(monthsList) - 1 and endDay != daysPerMonth[month-1]:
                        daysList.append(endDay)
                    else:
                        daysList.append(daysPerMonth[month-1])
                return daysList
            
            #Make a list of months leading up to the first day.
            initMonths = []
            for month in range(1, startMonth+1, 1):
                initMonths.append(month)
            initDays = getDays(initMonths, 1, startDay)
            startIndex = sum(initDays)
            
            # Make a list of days in each month of the analysis period.
            monthsList = []
            for month in range(startMonth, endMonth+1, 1):
                monthsList.append(month)
            simDays = getDays(monthsList, startDay, endDay)
            endIndex = startIndex + sum(simDays)
            
            #Get the data from the lists.
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startIndex:endIndex+1])/len(list[startIndex:endIndex+1]), 4))
            
            #Add the analysis period to the title.
            coloredTitle.append(str(monthNames[startMonth-1]) + " " + str(startDay) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay))
            
        #If the data is hourly, use the ladybug preparation functions to extract the hours from the analysis period.
        elif simStep == "Hourly":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            startHour = analysisPeriod[0][2]
            endHour = analysisPeriod[1][2]
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
            startIndex = HOYS[0]
            endIndex = HOYS[-1]
            #Get the data from the lists.
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startIndex:endIndex+1])/len(list[startIndex:endIndex+1]), 4))
            #Add the analysis period to the title.
            coloredTitle.append(str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1]))
    
    #Return all of the data
    return dataForColoring, coloredTitle, coloredUnits


def getPointValue(zoneValues, testPtZoneNames, testPtZoneWeights, dataHeaders):
    #Make a dictionary that will relate the testPtZoneNames to the zoneValues.
    zoneValueDict = {}
    
    for i in range(len(testPtZoneNames)):
        path = i
        if not zoneValueDict.has_key(path):
            zoneValueDict[path] = {}
        zoneValueDict[path]["zoneName"] = testPtZoneNames[path]
    
    #Figure out which zones in the dictionary correspond to the connected dataHeaders.
    matchedList = []
    for listCount, list in enumerate(dataHeaders):
        zName = list[2].split(" for ")[-1]
        try: zName = zName.split(":")[0]
        except: pass
        for path in zoneValueDict:
            if zoneValueDict[path]["zoneName"].upper() == zName:
                matchedList.append(1)
                zoneValueDict[path]["zoneValues"] = zoneValues[listCount]
    
    #Check if all of the data was found.
    dataCheck = True
    if len(dataHeaders) == len(zoneValueDict) and len(dataHeaders) == len(matchedList): pass
    elif len(matchedList) == 0:
        dataCheck = False
        warning = "None of the connected zoneAirTemp or zoneRelHumid could be matched with the connected zone names and weights. You should consider re-running your simulation since it is likely that the imported surface results are not for the _HBZones connected to the ViewFactor Component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else: print "Not all of the connected zoneAirTemp or zoneRelHumid could be found in the connected zone names and weights.  You may want to do a view factor calculation for all of your zones."
    
    
    #Calculate the value for each point.
    pointValues = []
    for zoneCount, pointList in enumerate(testPtZoneWeights):
        pointValues.append([])
        for pointWeight in pointList:
            pointValue = 0
            for Count, weight in enumerate(pointWeight):
                path  = Count
                weightedPointVal = weight*(zoneValueDict[path]["zoneValues"])
                pointValue = pointValue+weightedPointVal
            pointValues[zoneCount].append(pointValue)
    
    return dataCheck, pointValues

def warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, testPtZoneNames, testPtZoneWeights, zoneInletInfo):
    #First figure out which zones are connected from the testPtZoneWeights.
    adjacentList = []
    adjacentNameList = []
    for falseZone in testPtZoneWeights:
        for pt in falseZone:
            ptAdjList = []
            ptNameList = []
            for zoneCount, zone in enumerate(pt):
                if zone != 0:
                    ptAdjList.append(zoneCount)
                    ptNameList.append(testPtZoneNames[zoneCount])
            if ptAdjList not in adjacentList: adjacentList.append(ptAdjList)
            if ptNameList not in adjacentNameList: adjacentNameList.append(ptNameList)
    
    #Get a list of total heat gain for each of the grouped zones.
    #Get a list of total flow volume for each of the grouped zones.
    groupedHeatGains = []
    groupedFlowVol = []
    groupedTotalVol = []
    groupedInletArea = []
    groupedInletAreaList = []
    groupedMinHeightsInit = []
    groupedMaxHeightsInit = []
    groupedGlzHeightsInit = []
    for zoneList in adjacentList:
        zoneHeatG = 0
        zoneFlowV = 0
        zoneTotV = 0
        inletA = 0
        inletAList = []
        minHeightList = []
        maxHeightList = []
        glzHeightList = []
        for val in zoneList:
            zoneHeatG += heatGainValues[val]
            zoneFlowV += flowVolValues[val]
            zoneTotV += zoneInletInfo[val][-2]
            inletA += zoneInletInfo[val][-1]
            inletAList.append(zoneInletInfo[val][-1])
            minHeightList.append(zoneInletInfo[val][0])
            maxHeightList.append(zoneInletInfo[val][1])
            glzHeightList.append(zoneInletInfo[val][2])
        groupedHeatGains.append(zoneHeatG)
        groupedFlowVol.append(zoneFlowV)
        if inletA != 0: groupedInletArea.append(inletA)
        else: groupedInletArea.append(0.0025*zoneTotV)
        groupedInletAreaList.append(inletAList)
        groupedMinHeightsInit.append(minHeightList)
        groupedMaxHeightsInit.append(maxHeightList)
        groupedGlzHeightsInit.append(glzHeightList)
    
    #Figure out what the height of the grouped zones should be and what the average height of the windows is.
    groupedZoneHeights = []
    groupedGlzHeights = []
    groupedWinCeilDiffs = []
    for zoneCount in range(len(adjacentList)):
        if len(groupedMinHeightsInit[zoneCount]) != 1:
            groupedMinHeightsInit[zoneCount].sort()
            minHeight = groupedMinHeightsInit[zoneCount][0]
            groupedMaxHeightsInit[zoneCount].sort()
            maxHeight = groupedMaxHeightsInit[zoneCount][-1]
            roomHeight = maxHeight - minHeight
            groupedZoneHeights.append(roomHeight)
            areaWeights = []
            for area in groupedInletAreaList[zoneCount]:
                areaWeights.append(area/sum(groupedInletAreaList[zoneCount]))
            weightedGlzHeights = []
            for count, height in enumerate(groupedGlzHeightsInit[zoneCount]):
                try:
                    weightedHeight = (height - minHeight)*areaWeights[count]
                    weightedGlzHeights.append(weightedHeight)
                except:
                    weightedGlzHeights.append(0)
            weightedAvgGlzHeight = sum(weightedGlzHeights)
            groupedGlzHeights.append(weightedAvgGlzHeight)
            groupedWinCeilDiffs.append(roomHeight - weightedAvgGlzHeight)
        else:
            roomHeight = groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0]
            groupedZoneHeights.append(roomHeight)
            if groupedGlzHeightsInit[zoneCount][0] != None: glzHeight = groupedGlzHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0]
            else: glzHeight = (groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0])/2
            groupedGlzHeights.append(glzHeight)
            groupedWinCeilDiffs.append(roomHeight - glzHeight)
    
    #Calculate the Archimedes numbers and the temperature change of the grouped zones.
    tempChanges = []
    archimedesNumbers = []
    archiNumWinScale = []
    for zoneCount in range(len(adjacentList)):
        if groupedHeatGains[zoneCount] > 0:
            tempChange = (groupedHeatGains[zoneCount])/(1.2*1012*groupedFlowVol[zoneCount])
            tempChanges.append(tempChange)
            
            archiNumberNum = (9.806*0.0034*groupedHeatGains[zoneCount])*(groupedWinCeilDiffs[zoneCount]*groupedWinCeilDiffs[zoneCount]*groupedWinCeilDiffs[zoneCount])
            archiNumberDenom = (1.2*1012*groupedFlowVol[zoneCount]*groupedFlowVol[zoneCount]*(groupedFlowVol[zoneCount]/groupedInletArea[zoneCount]))
            archiNumber = archiNumberNum/archiNumberDenom
            archimedesNumbers.append(archiNumber)
            
            archiNumWinScaleNum = (9.806*0.0034*groupedHeatGains[zoneCount])*(groupedGlzHeights[zoneCount]*groupedGlzHeights[zoneCount]*groupedGlzHeights[zoneCount])
            archiNumWinScale.append(archiNumWinScaleNum/archiNumberDenom)
        else:
            tempChanges.append(0)
            archimedesNumbers.append(0)
            archiNumWinScale.append(0)
    
    #Calculate the dimensionless temperature change over the room.
    dimTempDeltas = []
    dimInterfHeights = []
    cielTemps = []
    for zoneCount in range(len(adjacentList)):
        if archimedesNumbers[zoneCount] < 59 and archimedesNumbers[zoneCount] != 0:
            #Linear stratification profile.
            dimInterfHeights.append(0)
            dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            dimTempDeltas.append(dimensionlessTempDelta)
            cielTemps.append((dimensionlessTempDelta/2)*tempChanges[zoneCount])
        elif archimedesNumbers[zoneCount] != 0:
            #Two-Layer stratification profile.
            dimensionlessInterfHeight = 0.92 - (0.18 * math.log10(archimedesNumbers[zoneCount]))
            dimInterfHeights.append(dimensionlessInterfHeight)
            dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            if dimensionlessTempDelta > 0:
                dimTempDeltas.append(dimensionlessTempDelta)
                cielTemps.append(((dimensionlessTempDelta*dimensionlessInterfHeight)/2)*tempChanges[zoneCount])
            else:
                dimTempDeltas.append(0)
                cielTemps.append(0)
                dimInterfHeights.append(0)
        else:
            dimTempDeltas.append(0)
            cielTemps.append(0)
            dimInterfHeights.append(0)
    
    #Calculate the dimensionless temperature at the dimensionless height and convert to final temperature.
    for zoneCount, zone in enumerate(pointAirTempValues):
        if archimedesNumbers[zoneCount] < 59 and dimTempDeltas[zoneCount] != 0:
            #Linear stratification profile.
            cielTemp = cielTemps[zoneCount]
            dimTempDelta = dimTempDeltas[zoneCount]
            for ptCount, ptValue in enumerate(zone):
                ptTemp = ptValue + cielTemp - dimTempDelta*tempChanges[zoneCount]*(1-ptHeightWeights[zoneCount][ptCount])
                pointAirTempValues[zoneCount][ptCount] = ptTemp
        elif dimTempDeltas[zoneCount] != 0:
            #Two-Layer stratification profile.
            cielTemp = cielTemps[zoneCount]
            dimTempDelta = dimTempDeltas[zoneCount]
            dimInterHeight = dimInterfHeights[zoneCount]
            
            for ptCount, ptValue in enumerate(zone):
                if ptHeightWeights[zoneCount][ptCount] < dimInterHeight:
                    ptTemp = ptValue + cielTemp - dimTempDelta*tempChanges[zoneCount]*(dimInterHeight - ptHeightWeights[zoneCount][ptCount])
                else:
                    ptTemp = ptValue + cielTemp
                pointAirTempValues[zoneCount][ptCount] = ptTemp
        else: pass
        
        print "Air temperature difference of " + str(tempChanges[zoneCount]*dimTempDeltas[zoneCount]) + " C."
        if archimedesNumbers[zoneCount] < 59 and archimedesNumbers[zoneCount] != 0: print "Linear stratification profile."
        elif archimedesNumbers[zoneCount] != 0 and dimTempDeltas[zoneCount] != 0: print "Two-Layer stratification profile."
        elif archimedesNumbers[zoneCount] != 0: print "Completely stratified."
        else: print "No Stratification"
        print " "
    
    
    return pointAirTempValues


def main(pointAirTempValues, viewFactorMesh, title, legendTitle, lb_preparation, lb_visualization, legendPar):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    #If there is no max and min set, make them the max and min of all the points.
    allAirTemp = []
    for list in pointAirTempValues:
        for mrt in list: allAirTemp.append(mrt)
    allAirTemp.sort()
    if lowB == "min": lowB = allAirTemp[0]
    if highB == "max": highB = allAirTemp[-1]
    
    #Get the colors for each zone.
    allColors = []
    transparentColors = []
    for zoneList in pointAirTempValues:
        colors = lb_visualization.gradientColor(zoneList, lowB, highB, customColors)
        allColors.append(colors)
        
        #Get a list of colors with alpha values as transparent
        tcolors = []
        for color in colors:
            tcolors.append(Drawing.Color.FromArgb(125, color.R, color.G, color.B))
        transparentColors.append(tcolors)
    
    #Color the view factor meshes.
    airTempMesh = []
    segmentedColors = []
    
    for zoneCount, meshList in enumerate(viewFactorMesh):
        segmentedColors.append([])
        startVal = 0
        for mesh in meshList:
            mesFaceLen = mesh.Faces.Count
            listForMesh = allColors[zoneCount][startVal:(startVal+mesFaceLen)]
            segmentedColors[zoneCount].append(listForMesh)
            startVal += mesFaceLen
    
    for zoneCount, meshList in enumerate(viewFactorMesh):
        for meshCount, mesh in enumerate(meshList):
            mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
            
            counter = 0
            for srfNum in range(mesh.Faces.Count):
                if mesh.Faces[srfNum].IsQuad:
                    mesh.VertexColors[counter + 0] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 3] = segmentedColors[zoneCount][meshCount][srfNum]
                    counter+=4
                else:
                    mesh.VertexColors[counter + 0] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[zoneCount][meshCount][srfNum]
                    counter+=3
            
            airTempMesh.append([mesh])
        else: pass
    
    #Create the legend.
    allgeo = []
    for list in viewFactorMesh: allgeo.extend(list)
    lb_visualization.calculateBB(allgeo, True)
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(allAirTemp, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Create the Title.
    titleTxt = '\n' + title[0] + '\n' + title[1]
    titleBasePt = lb_visualization.BoundingBoxPar[5]
    titleTextCurve = lb_visualization.text2srf([titleTxt], [titleBasePt], legendFont, textSize, legendBold)
    
    #Bring the legend and the title together.
    fullLegTxt = lb_preparation.flattenList(legendTextCrv + titleTextCurve)
    
    
    return transparentColors, airTempMesh, [legendSrfs, fullLegTxt], legendBasePoint



#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")


#Check the data input.
checkData = False
if _zoneAirTemp.BranchCount > 0 and str(_zoneAirTemp) != "tree {0}" and _zoneRelHumid.BranchCount > 0 and str(_zoneRelHumid) != "tree {0}" and _zoneAirFlowVol.BranchCount > 0 and str(_zoneAirFlowVol) != "tree {0}" and _zoneAirHeatGain.BranchCount > 0 and str(_zoneAirHeatGain) != "tree {0}" and checkLB == True:
    checkData, annualData, simStep, airTempUnits, airTempDataHeaders, airTempDataNumbers, relHumidDataHeaders, relHumidDataNumbers, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, testPtZoneNames, testPtZoneWeights, ptHeightWeights, viewFactorMesh, zoneInletInfo = checkTheInputs()

#Manage the inputs and outputs of the component based on the data that is hooked up.
if checkData == True:
    analysisPeriod, stepOfSimulation = manageInputOutput(annualData, simStep)
else: restoreInputOutput()

#Get the air temperature data for the zones.
dataCheck1 = False
dataCheck2 = False
if _runIt == True and checkData == True:
    airTempValues, title, legendTitle = getData(airTempDataNumbers, annualData, simStep, airTempDataHeaders, airTempUnits, analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization)
    relHumidValues, humidTitle, humidLegendTitle = getData(relHumidDataNumbers, annualData, simStep, relHumidDataHeaders, "%", analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization)
    flowVolValues, flowVolTitle, flowVolLegendTitle = getData(flowVolDataNumbers, annualData, simStep, flowVolDataHeaders, "m3/s", analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization)
    heatGainValues, heatGainTitle, heatGainLegendTitle = getData(heatGainDataNumbers, annualData, simStep, heatGainDataHeaders, "kWh", analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization)
    dataCheck1, pointAirTempValues = getPointValue(airTempValues, testPtZoneNames, testPtZoneWeights, airTempDataHeaders)
    dataCheck2, pointRelHumidValues = getPointValue(relHumidValues, testPtZoneNames, testPtZoneWeights, relHumidDataHeaders)
    if dataCheck1 == True:
        pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, testPtZoneNames, testPtZoneWeights, zoneInletInfo)


#Color the mesh with the data and get all of the other cool stuff that this component does.
if _runIt == True and checkData == True and pointAirTempValues != [] and pointRelHumidValues != [] and dataCheck1 == True and dataCheck2 == True:
    pointColorsInit, airTempMeshInit, legendInit, legendBasePt = main(pointAirTempValues, viewFactorMesh, title, legendTitle, lb_preparation, lb_visualization, legendPar_)
    
    #Unpack the legend.
    legend = []
    for count, item in enumerate(legendInit):
        if count == 0:
            legend.append(item)
        if count == 1:
            for srf in item:
                legend.append(srf)
    
    #Unpack the other data trees.
    testPtsAirTemp = DataTree[Object]()
    testPtsRelHumid = DataTree[Object]()
    airTempMesh = DataTree[Object]()
    for brCount, branch in enumerate(pointAirTempValues):
        for item in branch:testPtsAirTemp.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(pointRelHumidValues):
        for item in branch:testPtsRelHumid.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(airTempMeshInit):
        for item in branch:airTempMesh.Add(item, GH_Path(brCount))

ghenv.Component.Params.Output[3].Hidden = True
