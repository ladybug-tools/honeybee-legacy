# This component colors zones based on an energy simulation output.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to color zones based on EnergyPlus data out of the "Honeybee_Read EP Result" component or zone comfort analyses out of the comfort calculator components.
_
By default, zones will be colored based on total energy per unit floor area of the zone in the case of energy input data or colored based on total average value of each zone in the case of temperature, humidity or comfort input data.
If total annual simulation data has been connected, the analysisPeriod_ input can be used to select out a specific period fo the year for coloration.
In order to color zones by individual hours/months, connecting interger values to the "stepOfSimulation_" will allow you to scroll though each step of the input data.
-
Provided by Honeybee 0.0.54
    
    Args:
        _zoneData: A list zone data out of the Read EP Result component or the comfort calculator components that have zone data hooked up to them.
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        ===============: ...
        normalizeByFloorArea_: Set boolean to "True" in order to normalize results by the floor area of the zone and set to "False" to color zones based on total zone values.  The default is set to "True" such that colored zones communicate energy intensity rather than total energy.  Note that this input will be ignored if connected data is Temperature, Humidity, a Comfort Metric, or already normalized data.
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to "stepOfSimulation_" will override this input.
        stepOfSimulation_: Optional interger for the hour of simulation to color the zones with.  Connecting a value here will override the analysisPeriod_ input.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        _runIt: Set boolean to "True" to run the component and color the zones.
    Returns:
        readMe!: ...
        zoneColoredMesh: A list of meshes for each zone, each of which is colored based on the input _zoneData.
        zoneWireFrame: A list of curves representing the outlines of the zones.  This is particularly helpful if one wants to scroll through individual zone meshes but still see the outline of the building.
        legend: A legend of the zone colors. Connect this output to a grasshopper "Geo" component in order to preview the legend spearately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the building with the grasshopper "move" component.
        zoneBreps: A list of breps for each zone. This is essentially the same as the _HBZones input. Connecting this output and the following zoneColors to a Grasshopper 'Preview' component will thus allow you to see the zones colored transparently.
        zoneColors: A list of colors that correspond to the colors of each zone.  These colors include alpha values to make them slightly transparent.  Connecting the previous output and this output to a Grasshopper 'Preview' component will thus allow you to see the zones colored transparently.
        zoneValues: The values of the input data that are being used to color the zones.
        floorNormZoneData: The input data normalized by the floor area of it corresponding zone.
"""

ghenv.Component.Name = "Honeybee_Color Zones by EP Result"
ghenv.Component.NickName = 'ColorZones'
ghenv.Component.Message = 'VER 0.0.54\nNOV_15_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc



inputsDict = {
    
0: ["_zoneData", "A list zone data out of the Read EP Result component or the comfort calculator components that have zone data hooked up to them."],
1: ["_HBZones", "The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component or zones read back into Grasshopper from the Import idf component in order to ensure alignment with the EP Result data."],
2: ["===============", "..."],
3: ["normalizeByFloorArea_", "Set boolean to 'True' in order to normalize results by the floor area of the zone and set to 'False' to color zones based on total zone values.  The default is set to 'True' such that colored zones communicate energy intensity rather than total energy.  Note that this input will be ignored if connected data is Temperature, Humidity, a Comfort Metric, or EUI (which is already normalized by floor area)."],
4: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input."],
5: ["stepOfSimulation_", "Optional interger for the hour of simulation to color the zones with.  Connecting a value here will override the analysisPeriod_ input."],
6: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
7: ["_runIt", "Set boolean to 'True' to run the component and color the zones."]
}

outputsDict = {
    
0: ["readMe!", "..."],
1: ["zoneColoredMesh", "A list of meshes for each zone, each of which is colored based on the input _zoneData."],
2: ["zoneWireFrame", "A list of curves representing the outlines of the zones.  This is particularly helpful if one wants to scroll through individual zone meshes but still see the outline of the building."],
3: ["legend", "A legend of the zone colors. Connect this output to a grasshopper 'Geo' component in order to preview the legend spearately in the Rhino scene."],
4: ["legendBasePt", "The legend base point, which can be used to move the legend in relation to the building with the grasshopper 'move' component."],
5: ["zoneBreps", "A list of breps for each zone. This is essentially the same as the _HBZones input. Connecting this output and the following zoneColors to a Grasshopper 'Preview' component will thus allow you to see the zones colored transparently."],
6: ["zoneColors", "A list of colors that correspond to the colors of each zone.  These colors include alpha values to make them slightly transparent.  Connecting the previous output and this output to a Grasshopper 'Preview' component will thus allow you to see the zones colored transparently."],
7: ["zoneValues", "The values of the input data that are being used to color the zones."],
8: ["floorNormZoneData", "The input data normalized by the floor area of it corresponding zone."]
}


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def copyHBZoneData():
    hb_hive = sc.sticky["honeybee_Hive"]()
    zoneNames = []
    zoneFloors = []
    zoneBreps = []
    zoneCentPts = []
    
    for HZone in _HBZones:
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        zoneNames.append(zone.name)
        floorGeo = []
        for srf in zone.surfaces:
            if srf.type == 2: floorGeo.append(srf.geometry)
            elif str(srf.type) == "2.5": floorGeo.append(srf.geometry)
            elif str(srf.type) == "2.75": floorGeo.append(srf.geometry)
            else: pass
        zoneFloors.append(floorGeo)
    
    sc.sticky["Honeybee_ZoneData"] = [zoneBreps, zoneNames, zoneFloors, zoneCentPts]

def checkTheInputs():
    #Create a Python list from the _zoneData
    dataPyList = []
    for i in range(_zoneData.BranchCount):
        branchList = _zoneData.Branch(i)
        dataVal = []
        for item in branchList:
            dataVal.append(item)
        dataPyList.append(dataVal)
    
    #Test to see if the data has a header on it, which is necessary to know whether to total the data or average it.  If there's no header, the data should not be vizualized with this component.
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
        warning = "Not all of the connected _zoneData has a Ladybug/Honeybee header on it.  This header is necessary to color zones with this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that the lengths of data in in the _zoneData branches are all the same.
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
        warning = "Not all of the connected _zoneData branches are of the same length or there are more than 8760 values in the list."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    total = False
    
    if checkData2 == True:
        #Check to be sure that all of the data headers say that they are of the same type.
        header = dataHeaders[0]
        
        headerUnits = header[3]
        headUnitCheck = []
        for head in dataHeaders:
            if head[3] == headerUnits:
                headUnitCheck.append(1)
            else: pass
        if sum(headUnitCheck) == len(dataHeaders):
            checkData5 = True
        else:
            checkData5 = False
            warning = "Not all of the connected _zoneData branches are of the same data type."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        #See if the data is for the whole year.
        if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
            annualData = True
        else: annualData = False
        
        #Check the simulation timestep of the data.
        simStep = str(header[4])
        
        #Check to see if the data is energy data and, if so, make a note that the data is normalizable by floor area and can be totalled instead of averaged.
        dataType = str(header[2])
        
        if "Floor Normalized" in dataType:
            normable = False
            total = True
        elif "Total Thermal Energy for" in dataType: normable = True
        elif "Total Energy for" in dataType: normable = True
        elif "Thermal Energy Balance for" in dataType: normable = True
        elif "Cooling Energy for" in dataType: normable = True
        elif "Heating Energy for" in dataType: normable = True
        elif "Electric Lighting Energy for" in dataType: normable = True
        elif "Electric Equipment Energy for" in dataType: normable = True
        elif "People Energy for" in dataType: normable = True
        elif "Total Solar Gain for" in dataType: normable = True
        elif "Solar Beam Energy for" in dataType: normable = True
        elif "Solar Diffuse Energy for" in dataType: normable = True
        elif "Infiltration Energy Loss/Gain for" in dataType: normable = True
        elif "Operative Temperature for" in dataType: normable = False
        elif "Air Temperature for" in dataType: normable = False
        elif "Radiant Temperature for" in dataType: normable = False
        elif "Zone Air Relative Humidity" in dataType: normable = False
        elif "Predicted Mean Vote" in dataType: normable = False
        elif "Percentage of People Dissatisfied" in dataType: normable = False
        elif "Standard Effective Temperature" in dataType: normable = False
        elif "Comfortable Or Not" in dataType: normable = False
        elif "Adaptive Comfort" in dataType: normable = False
        elif "Degrees from Target Temperature" in dataType: normable = False
        elif "Adaptive Target Temperature" in dataType: normable = False
        elif "Universal Thermal Climate Index" in dataType: normable = False
        elif "Outdoor Comfort" in dataType: normable = False
        elif "Sensible Cooling Energy" in dataType: normable = True
        elif "Latent Cooling Energy" in dataType: normable = True
        elif "Sensible Heating Energy" in dataType: normable = True
        elif "Latent Heating Energy" in dataType: normable = True
        elif "Supply Air Mass Flow Rate" in dataType: normable = True
        elif "Supply Air Temperature" in dataType: normable = False
        elif "Supply Air Relative Humidity" in dataType: normable = False
        else:
            normable = False
            warning = "Component cannot tell what data type is being connected.  Data will be averaged for each zone by default."
            print warning
    else:
        checkData5 = True
        if dataLength == 8760: annualData = True
        else: annualData = False
        simStep = 'unknown timestep'
        headerUnits = 'unknown units'
        normable = False
        dataHeaders = []
        warning = "Component cannot tell what data type is being connected.  Data will be averaged for each zone by default."
        print warning
    
    if checkData4 == True and checkData5 == True:
        checkData = True
    else: checkData = False
    
    return checkData, annualData, simStep, normable, dataNumbers, dataHeaders, headerUnits, total

def checkZones(zoneHeaders, pyZoneData, hb_zoneData):
    #Bring in the HB data on the connected zones and put the floors on their own list
    zoneFloors = hb_zoneData[2]
    zoneBreps = hb_zoneData[0]
    zoneNames = hb_zoneData[1]
    
    #Figure out which surfaces in the full list for the zones correspond to the connected srfHeaders.
    zoneFlrAreas = []
    newZoneFloors = []
    newPyZoneData = []
    newZoneHeaders = []
    finalZoneNames = []
    newZoneBreps = []
    
    for listCount, list in enumerate(zoneHeaders):
        zoneName = list[2].split(" for ")[-1]
        finalZoneNames.append(zoneName)
        for count, name in enumerate(zoneNames):
            if zoneName == name.upper():
                newZoneFloors.append(zoneFloors[count])
                zoneFlrAreas.append(rc.Geometry.AreaMassProperties.Compute(zoneFloors[count]).Area)
                newZoneBreps.append(zoneBreps[count])
                newZoneHeaders.append(zoneHeaders[listCount])
                newPyZoneData.append(pyZoneData[listCount])
    
    return finalZoneNames, zoneFlrAreas, newZoneFloors, newPyZoneData, newZoneHeaders, newZoneBreps

def manageInputOutput(annualData, simStep, zoneNormalizable):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(8):
        if input == 3 and zoneNormalizable == False:
            ghenv.Component.Params.Input[input].NickName = "__________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 4 and annualData == False:
            ghenv.Component.Params.Input[input].NickName = "___________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 5 and (simStep == "Annually" or simStep == "unknown timestep"):
            ghenv.Component.Params.Input[input].NickName = "____________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    for output in range(9):
        if output == 9 and zoneNormalizable == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
    
    if zoneNormalizable == False: normByFlr = False
    else: normByFlr = normalizeByFloorArea_
    if annualData == False: analysisPeriod = [0, 0]
    else: analysisPeriod = analysisPeriod_
    if simStep == "Annually" or simStep == "unknown timestep": stepOfSimulation = None
    else: stepOfSimulation = stepOfSimulation_
    
    return normByFlr, analysisPeriod, stepOfSimulation

def restoreInputOutput():
    for input in range(8):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    for output in range(9):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]


def getData(pyZoneData, zoneFlrAreas, annualData, simStep, zoneNormalizable, zoneHeaders, headerUnits, normByFlr, analysisPeriod, stepOfSimulation, total):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        #Make a list to contain the data for coloring and labeling.
        dataForColoring = []
        normedZoneData = []
        coloredTitle = []
        coloredUnits = None
        
        #Add basic stuff to the title.
        if normByFlr == True and zoneNormalizable == True and zoneHeaders != []:
            coloredTitle.append("Floor Normalized " + str(zoneHeaders[0][2].split("for")[0]) + " - " + headerUnits + "/" + str(sc.doc.ModelUnitSystem) + "2")
            coloredUnits = headerUnits + "/" + str(sc.doc.ModelUnitSystem) + "2"
        elif normByFlr == False and zoneNormalizable == True and zoneHeaders != []:
            coloredTitle.append(str(zoneHeaders[0][2].split("for")[0]) + " - " + headerUnits)
            coloredUnits = headerUnits
        elif total == True:
            coloredTitle.append(str(zoneHeaders[0][2].split("for")[0]) + " - " + headerUnits)
            coloredUnits = headerUnits
        elif zoneNormalizable == False and zoneHeaders != []:
            coloredTitle.append("Average " + str(zoneHeaders[0][2].split("for")[0] + " - " + headerUnits))
            coloredUnits = headerUnits
        else:
            coloredTitle.append("Unknown Data")
            coloredUnits = "Unknown Units"
        
        #Make lists that assist with the labaeling of the rest of the title.
        monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
        
        #If it is possible to normalize the data and the value is set to True (either by user request or default), norm the data.
        if zoneNormalizable == True and normByFlr == True:
            for zone, list in enumerate(pyZoneData):
                zoneNormData = []
                for item in list:
                    zoneNormData.append(item/(zoneFlrAreas[zone]))
                normedZoneData.append(zoneNormData)
        
        #If none of the analysisperiod or stepOfSim are connected, just total or average all the data.
        def getColorData1():
            if normByFlr == True and zoneNormalizable == True:
                for list in normedZoneData:
                    dataForColoring.append(round(sum(list), 4))
            elif normByFlr == False and zoneNormalizable == True:
                for list in pyZoneData:
                    dataForColoring.append(round(sum(list), 4))
            elif total == True:
                for list in pyZoneData:
                    dataForColoring.append(round(sum(list), 4))
            else:
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
                if normByFlr == True and zoneNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(list[stepOfSimulation], 4))
                elif normByFlr == False and zoneNormalizable == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(list[stepOfSimulation], 4))
                elif total == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(list[stepOfSimulation], 4))
                else:
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
                if normByFlr == True and zoneNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startMonth:endMonth+1]), 4))
                elif normByFlr == False and zoneNormalizable == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startMonth:endMonth+1]), 4))
                elif total == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startMonth:endMonth+1]), 4))
                else:
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
                if normByFlr == True and zoneNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif normByFlr == False and zoneNormalizable == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif total == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                else:
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
                if normByFlr == True and zoneNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif normByFlr == False and zoneNormalizable == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif total == True:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                else:
                    for list in pyZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1])/len(list[startIndex:endIndex+1]), 4))
                #Add the analysis period to the title.
                coloredTitle.append(str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1]))
        
        #If there is floor normalized zone data, turn it into a data tree object.
        if normedZoneData != []:
            floorNormData = DataTree[Object]()
            for listCount, list in enumerate(normedZoneData):
                floorNormData.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
                floorNormData.Add(str(zoneHeaders[listCount][1]), GH_Path(listCount))
                floorNormData.Add("Floor Normalized " + str(zoneHeaders[listCount][1]), GH_Path(listCount))
                floorNormData.Add(headerUnits + "/"+ str(sc.doc.ModelUnitSystem) + "2", GH_Path(listCount))
                floorNormData.Add(str(zoneHeaders[listCount][4]), GH_Path(listCount))
                floorNormData.Add(str(zoneHeaders[listCount][5]), GH_Path(listCount))
                floorNormData.Add(str(zoneHeaders[listCount][6]), GH_Path(listCount))
                for num in list:
                    floorNormData.Add((num), GH_Path(listCount))
        else:
            floorNormData = normedZoneData
        
        #Return all of the data
        return dataForColoring, floorNormData, coloredTitle, coloredUnits, lb_preparation, lb_visualization
    else:
        print "You should first let the Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [], [], [], None, None, None


def main(zoneValues, zones, zoneFloors, newZoneBreps, zoneHeaders, title, legendTitle, lb_preparation, lb_visualization, legendPar):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    #Get the colors
    colors = lb_visualization.gradientColor(zoneValues, lowB, highB, customColors)
    
    #Get a list of colors with alpha values as transparent
    transparentColors = []
    for color in colors:
        transparentColors.append(Drawing.Color.FromArgb(125, color.R, color.G, color.B))
    
    #Create a series of colored zone meshes and zone curves
    zoneMeshes = []
    zoneWires = []
    zoneCentPts = []
    zoneBreps = []
    
    joinedFloors = []
    for list in zoneFloors:
        joinedFloor = rc.Geometry.Brep.JoinBreps(list, sc.doc.ModelAbsoluteTolerance)[0]
        joinedFloors.append(joinedFloor)
    
    for count, brep in enumerate(joinedFloors):
        zoneMeshSrfs = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Default)
        joinedFloorMesh = rc.Geometry.Mesh()
        for mesh in zoneMeshSrfs:
            mesh.VertexColors.CreateMonotoneMesh(colors[count])
            joinedFloorMesh.Append(mesh)
        zoneMeshes.append(joinedFloorMesh)
    
    for brep in zones:
        wireFrame = brep.DuplicateEdgeCurves()
        for crv in wireFrame:
            zoneWires.append(crv)
        bBox = brep.GetBoundingBox(False)
        zoneCentPts.append(bBox.Center)
    
    #Create the legend.
    lb_visualization.calculateBB(zones, True)
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(zoneValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Create the Title.
    titleTxt = '\n' + title[0] + '\n' + title[1]
    titleBasePt = lb_visualization.BoundingBoxPar[5]
    titleTextCurve = lb_visualization.text2srf([titleTxt], [titleBasePt], legendFont, textSize, legendBold)
    
    #Bring the legend and the title together.
    fullLegTxt = lb_preparation.flattenList(legendTextCrv + titleTextCurve)
    
    
    return transparentColors, newZoneBreps, zoneMeshes, zoneWires, [legendSrfs, fullLegTxt], legendBasePoint




#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_ZoneData') == False:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_ZoneData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_ZoneData') == True:
    hb_zoneData = sc.sticky["Honeybee_ZoneData"]
    initCheck = True
    if len(_HBZones) == len(hb_zoneData[0]):
        for count, brep in enumerate(_HBZones):
            boundBoxVert = brep.GetBoundingBox(False).Center
            if boundBoxVert.X <= hb_zoneData[3][count].X+tol and boundBoxVert.X >= hb_zoneData[3][count].X-tol and boundBoxVert.Y <= hb_zoneData[3][count].Y+tol and boundBoxVert.Y >= hb_zoneData[3][count].Y-tol and boundBoxVert.Z <= hb_zoneData[3][count].Z+tol and boundBoxVert.Z >= hb_zoneData[3][count].Z-tol: pass
            else:
                initCheck = False
    else: initCheck = False
    if initCheck == True: pass
    else:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_ZoneData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == False:
    print "You should first let Honeybee  fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    pass



#Check the data input.
checkData = False
if _zoneData.BranchCount > 0 and str(_zoneData) != "tree {0}" and initCheck == True:
    checkData, annualData, simStep, zoneNormalizable, pyZoneData, zoneHeaders, headerUnits, total = checkTheInputs()

#Manage the inputs and outputs of the component based on the data that is hooked up.
if checkData == True:
    normByFlr, analysisPeriod, stepOfSimulation = manageInputOutput(annualData, simStep, zoneNormalizable)
else: restoreInputOutput()

#If the data is meant to be normalized by floor area, check the zones.
if checkData == True and normByFlr == None: normByFlr = True
if _runIt == True and checkData == True and _HBZones != []:
    zoneNames, zoneFlrAreas, zoneFloors, pyZoneData, zoneHeaders, newZoneBreps = checkZones(zoneHeaders, pyZoneData, hb_zoneData)
    zoneValues, floorNormZoneData, title, legendTitle, lb_preparation, lb_visualization = getData(pyZoneData, zoneFlrAreas, annualData, simStep, zoneNormalizable, zoneHeaders, headerUnits, normByFlr, analysisPeriod, stepOfSimulation, total)

#Color the zones with the data and get all of the other cool stuff that this component does.
if _runIt == True and checkData == True and _HBZones != [] and zoneValues != []:
    zoneColors, zoneBreps, zoneColoredMesh, zoneWireFrame, legendInit, legendBasePt = main(zoneValues, _HBZones, zoneFloors, newZoneBreps, zoneHeaders, title, legendTitle, lb_preparation, lb_visualization, legendPar_)
    #Unpack the legend.
    legend = []
    for count, item in enumerate(legendInit):
        if count == 0:
            legend.append(item)
        if count == 1:
            for srf in item:
                legend.append(srf)

#Hide unwanted outputs
ghenv.Component.Params.Output[5].Hidden = True
ghenv.Component.Params.Output[6].Hidden = True
