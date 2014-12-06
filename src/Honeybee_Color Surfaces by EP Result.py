# This component colors zone surfaces based on an energy simulation output.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to color zone surfaces based on EnergyPlus data out of the "Honeybee_Read EP Surface Result" component.
_
By default, zone surfaces will be colored based on total energy per unit surface area in the case of energy input data or colored based on average value of each surface in the case of temperature or data that is already normalized.
If total annual simulation data has been connected, the analysisPeriod_ input can be used to select out a specific period fo the year for coloration.
In order to color surfaces by individual hours/months, connecting interger values to the "stepOfSimulation_" will allow you to scroll though each step of the input data.
-
Provided by Honeybee 0.0.55
    
    Args:
        _srfData: A list surface data out of the "Honeybee_Read EP Surface Result" component.
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component as surfaces may not align otherwise.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        ===============: ...
        normalizeBySrfArea_: Set boolean to "True" in order to normalize results by the area of the surface and set to "False" to color zones based on total values for each surface.  The default is set to "True" such that colored surface communicate energy intensity rather than total energy.  Note that this input will be ignored if connected data is Temperature or values that are already normalized.
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to "stepOfSimulation_" will override this input.
        stepOfSimulation_: Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        _runIt: Set boolean to "True" to run the component and color the zone surfaces.
    Returns:
        readMe!: ...
        srfColoredMesh: A list of meshes for each surface, each of which is colored based on the input _srfData.
        zoneWireFrame: A list of curves representing the outlines of the zones.  This is particularly helpful if one wants to scroll through individual meshes but still see the outline of the building.
        legend: A legend of the surface colors. Connect this output to a grasshopper "Geo" component in order to preview the legend spearately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the building with the grasshopper "move" component.
        srfBreps: A list of breps for each zone surface. Connecting this output and the following zoneColors to a Grasshopper 'Preview' component will thus allow you to see the surfaces colored transparently.
        srfColors: A list of colors that correspond to the colors of each zone surface.  These colors include alpha values to make them slightly transparent.  Connecting the previous output and this output to a Grasshopper 'Preview' component will thus allow you to see the surfaces colored transparently.
        srfValues: The values of the input data that are being used to color the surfaces.
        normalizedSrfData: The input data normalized by the areas of each surface.
"""

ghenv.Component.Name = "Honeybee_Color Surfaces by EP Result"
ghenv.Component.NickName = 'ColorSurfaces'
ghenv.Component.Message = 'VER 0.0.55\nDEC_05_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nDEC_02_2014
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
    
0: ["_srfData", "A list surface data out of the 'Honeybee_Read EP Surface Result' component."],
1: ["_HBZones", "The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component as surfaces may not align otherwise.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data."],
2: ["===============", "..."],
3: ["normalizeBySrfArea_", "Set boolean to 'True' in order to normalize results by the area of the surface and set to 'False' to color zones based on total values for each surface.  The default is set to 'True' such that colored surface communicate energy intensity rather than total energy.  Note that this input will be ignored if connected data is Temperature or values that are already normalized."],
4: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input."],
5: ["stepOfSimulation_", "Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input."],
6: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
7: ["_runIt", "Set boolean to 'True' to run the component and color the zone surfaces."]
}

outputsDict = {
    
0: ["readMe!", "..."],
1: ["srfColoredMesh", "A list of meshes for each surface, each of which is colored based on the input _srfData."],
2: ["zoneWireFrame", "A list of curves representing the outlines of the zones.  This is particularly helpful if one wants to scroll through individual meshes but still see the outline of the building."],
3: ["legend", "A legend of the surface colors. Connect this output to a grasshopper 'Geo' component in order to preview the legend spearately in the Rhino scene."],
4: ["legendBasePt", "The legend base point, which can be used to move the legend in relation to the building with the grasshopper 'move' component."],
5: ["srfBreps", "A list of breps for each zone surface. Connecting this output and the following zoneColors to a Grasshopper 'Preview' component will thus allow you to see the surfaces colored transparently."],
6: ["srfColors", "A list of colors that correspond to the colors of each zone surface.  These colors include alpha values to make them slightly transparent.  Connecting the previous output and this output to a Grasshopper 'Preview' component will thus allow you to see the surfaces colored transparently."],
7: ["srfValues", "The values of the input data that are being used to color the surfaces."],
8: ["normalizedSrfData", "The input data normalized by the areas of each surface."]
}


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance

def copyHBZoneData():
    hb_hive = sc.sticky["honeybee_Hive"]()
    surfaceNames = []
    srfBreps = []
    zoneBreps = []
    zoneCentPts = []
    
    for HZone in _HBZones:
        zoneBreps.append(HZone)
        zoneCentPts.append(HZone.GetBoundingBox(False).Center)
        zone = hb_hive.callFromHoneybeeHive([HZone])[0]
        for srf in zone.surfaces:
            surfaceNames.append(srf.name)
            if srf.hasChild:
                srfBreps.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    surfaceNames.append(childSrf.name)
                    srfBreps.append(childSrf.geometry)
            else:
                srfBreps.append(srf.geometry)
    
    sc.sticky["Honeybee_SrfData"] = [zoneBreps, surfaceNames, srfBreps, zoneCentPts]


def checkTheInputs():
    #Create a Python list from the _srfData
    dataPyList = []
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        dataVal = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataVal.append(item)
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
        warning = "Not all of the connected _srfData has a Ladybug/Honeybee header on it.  This header is necessary to color zone surfaces with this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that the lengths of data in in the _srfData branches are all the same.
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
        warning = "Not all of the connected _srfData branches are of the same length or there are more than 8760 values in the list."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    total = False
    
    if checkData2 == True:
        #Check to be sure that all of the data headers say that they are of the same type.
        header = dataHeaders[0]
        
        headerUnits = header[3]
        headerStart = header[5]
        headerEnd = header[6]
        simStep = str(header[4])
        headUnitCheck = []
        for head in dataHeaders:
            if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                headUnitCheck.append(1)
            else: pass
        if sum(headUnitCheck) == len(dataHeaders):
            checkData5 = True
        else:
            checkData5 = False
            warning = "Not all of the connected _srfData branches are of the same data type or same analysis period.  All connected data must be of one unit type."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        #See if the data is for the whole year.
        if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
            annualData = True
        else: annualData = False
        
        #Check to see if the data is energy data and, if so, make a note that the data is normalizable by floor area and can be totalled instead of averaged.
        dataType = str(header[2])
        
        if "Normalized" in dataType:
            normable = False
            total = True
        elif "Surface Energy Loss/Gain for" in dataType: normable = True
        elif "Window Total Transmitted Solar Energy for" in dataType: normable = True
        elif "Window Transmitted Beam Energy for" in dataType: normable = True
        elif "Window Transmitted Diffuse Energy for" in dataType: normable = True
        elif "Outer Surface Temperature for" in dataType: normable = False
        elif "Inner Surface Temperature for" in dataType: normable = False
        else:
            normable = False
            warning = "Component cannot tell what data type is being connected.  Data will be averaged for each surface by default."
            print warning
    else:
        checkData5 = True
        if dataLength == 8760: annualData = True
        else: annualData = False
        simStep = 'unknown timestep'
        headerUnits = 'unknown units'
        normable = False
        dataHeaders = []
        warning = "Component cannot tell what data type is being connected.  Data will be averaged for each surface by default."
        print warning
    
    if checkData4 == True and checkData5 == True:
        checkData = True
    else: checkData = False
    
    return checkData, annualData, simStep, normable, dataNumbers, dataHeaders, headerUnits, total

def getZoneSrfs(srfHeaders, pyZoneData, hb_zoneData):
    #Bring in the HB data on the connected zones.
    zoneBreps = hb_zoneData[0]
    surfaceNames = hb_zoneData[1]
    srfBreps = hb_zoneData[2]
    
    #Figure out which surfaces in the full list for the zones correspond to the connected srfHeaders.
    finalSurfaceNames = []
    finalSrfAreas = []
    finalSrfBreps = []
    newPyZoneData = []
    newSrfHeaders = []
    for listCount, list in enumerate(srfHeaders):
        srfName = list[2].split(" for ")[-1]
        try: srfName = srfName.split(":")[0]
        except: pass
        finalSurfaceNames.append(srfName)
        for count, name in enumerate(surfaceNames):
            if srfName == name.upper():
                finalSrfBreps.append(srfBreps[count])
                finalSrfAreas.append(rc.Geometry.AreaMassProperties.Compute(srfBreps[count]).Area)
                newPyZoneData.append(pyZoneData[listCount])
                newSrfHeaders.append(srfHeaders[listCount])
    
    #Check if all of the data was found.
    dataCheck = True
    if len(srfHeaders) == len(finalSurfaceNames) and len(srfHeaders) == len(finalSrfBreps) and len(srfHeaders) == len(finalSrfAreas): pass
    elif len(finalSrfBreps) == 0:
        dataCheck = False
        warning = "None of the connected srfData could be matched with the surfaces in the connected HBZones. Note that this component does not currenlty work for curved geometry E+ simulations because the surfaces are broken up and meshed in order to run it through E+."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else: print "Not all of the connected surface data could be found in the connected zones.  You may want to connect all of your zones in order to see all of your connected surface data."
    
    return dataCheck, finalSurfaceNames, finalSrfAreas, finalSrfBreps, newPyZoneData, newSrfHeaders, zoneBreps

def manageInputOutput(annualData, simStep, srfNormalizable):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(8):
        if input == 3 and srfNormalizable == False:
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
        if output == 9 and srfNormalizable == False:
            ghenv.Component.Params.Output[output].NickName = "."
            ghenv.Component.Params.Output[output].Name = "."
            ghenv.Component.Params.Output[output].Description = " "
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
    
    if srfNormalizable == False: normByFlr = False
    else: normByFlr = normalizeBySrfArea_
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


def getData(pyZoneData, surfaceAreas, annualData, simStep, srfNormalizable, srfHeaders, headerUnits, normByFlr, analysisPeriod, stepOfSimulation, total):
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
        if normByFlr == True and srfNormalizable == True and srfHeaders != []:
            coloredTitle.append("Area Normalized " + str(srfHeaders[0][2].split("for")[0]) + " - " + headerUnits + "/" + str(sc.doc.ModelUnitSystem) + "2")
            coloredUnits = headerUnits + "/" + str(sc.doc.ModelUnitSystem) + "2"
        elif normByFlr == False and srfNormalizable == True and srfHeaders != []:
            coloredTitle.append(str(srfHeaders[0][2].split("for")[0]) + " - " + headerUnits)
            coloredUnits = headerUnits
        elif total == True:
            coloredTitle.append(str(srfHeaders[0][2].split("for")[0]) + " - " + headerUnits)
            coloredUnits = headerUnits
        elif srfNormalizable == False and srfHeaders != []:
            coloredTitle.append("Average " + str(srfHeaders[0][2].split("for")[0] + " - " + headerUnits))
            coloredUnits = headerUnits
        else:
            coloredTitle.append("Unknown Data")
            coloredUnits = "Unknown Units"
        
        #Make lists that assist with the labaeling of the rest of the title.
        monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
        
        #If it is possible to normalize the data and the value is set to True (either by user request or default), norm the data.
        if srfNormalizable == True and normByFlr == True:
            for zone, list in enumerate(pyZoneData):
                zoneNormData = []
                for item in list:
                    zoneNormData.append(item/(surfaceAreas[zone]))
                normedZoneData.append(zoneNormData)
        
        #If none of the analysisperiod or stepOfSim are connected, just total or average all the data.
        def getColorData1():
            if normByFlr == True and srfNormalizable == True:
                for list in normedZoneData:
                    dataForColoring.append(round(sum(list), 4))
            elif normByFlr == False and srfNormalizable == True:
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
            if srfHeaders != []:
                coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
            else: coloredTitle.append("Complete Time Period That Is Connected")
        if analysisPeriod == [] and stepOfSimulation == None:
            getColorData1()
            if srfHeaders != []:
                coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
            else: coloredTitle.append("Complete Time Period That Is Connected")
        elif simStep == "Annually" or simStep == "unknown timestep":
            getColorData1()
            if srfHeaders != []:
                coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
            else: coloredTitle.append("Complete Time Period That Is Connected")
        
        # If the user has connected a stepOfSim, make the step of sim the thing used to color zones.
        if stepOfSimulation != None:
            if stepOfSimulation < len(pyZoneData[0]):
                if normByFlr == True and srfNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(list[stepOfSimulation], 4))
                elif normByFlr == False and srfNormalizable == True:
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
                if normByFlr == True and srfNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startMonth:endMonth+1]), 4))
                elif normByFlr == False and srfNormalizable == True:
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
                if normByFlr == True and srfNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif normByFlr == False and srfNormalizable == True:
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
                if normByFlr == True and srfNormalizable == True:
                    for list in normedZoneData:
                        dataForColoring.append(round(sum(list[startIndex:endIndex+1]), 4))
                elif normByFlr == False and srfNormalizable == True:
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
            normalizedSrfData = DataTree[Object]()
            for listCount, list in enumerate(normedZoneData):
                normalizedSrfData.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(listCount))
                normalizedSrfData.Add(str(srfHeaders[listCount][1]), GH_Path(listCount))
                normalizedSrfData.Add("Floor Normalized " + str(srfHeaders[listCount][1]), GH_Path(listCount))
                normalizedSrfData.Add(headerUnits + "/"+ str(sc.doc.ModelUnitSystem) + "2", GH_Path(listCount))
                normalizedSrfData.Add(str(srfHeaders[listCount][4]), GH_Path(listCount))
                normalizedSrfData.Add(str(srfHeaders[listCount][5]), GH_Path(listCount))
                normalizedSrfData.Add(str(srfHeaders[listCount][6]), GH_Path(listCount))
                for num in list:
                    normalizedSrfData.Add((num), GH_Path(listCount))
        else:
            normalizedSrfData = normedZoneData
        
        #Return all of the data
        return dataForColoring, normalizedSrfData, coloredTitle, coloredUnits, lb_preparation, lb_visualization
    else:
        print "You should first let the Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [], [], [], None, None, None


def main(zoneValues, zones, srfBreps, srfHeaders, title, legendTitle, lb_preparation, lb_visualization, legendPar):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    #Get the colors
    colors = lb_visualization.gradientColor(zoneValues, lowB, highB, customColors)
    
    #Get a list of colors with alpha values as transparent
    transparentColors = []
    for color in colors:
        transparentColors.append(Drawing.Color.FromArgb(125, color.R, color.G, color.B))
    
    #Create a series of colored meshes and zone curves.
    srfMeshes = []
    zoneWires = []
    
    for count, brep in enumerate(srfBreps):
        meshSrfs = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Default)
        for mesh in meshSrfs:
            mesh.VertexColors.CreateMonotoneMesh(colors[count])
            srfMeshes.append(mesh)
    
    for brep in zones:
        wireFrame = brep.DuplicateEdgeCurves()
        for crv in wireFrame:
            zoneWires.append(crv)
    
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
    
    return transparentColors, srfBreps, srfMeshes, zoneWires, [legendSrfs, fullLegTxt], legendBasePoint




#If the HBzone data has not been copied to memory or if the data is old, get it.
initCheck = False
if _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_SrfData') == False:
    copyHBZoneData()
    hb_zoneData = sc.sticky["Honeybee_SrfData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('Honeybee_SrfData') == True:
    hb_zoneData = sc.sticky["Honeybee_SrfData"]
    checkZones = True
    if len(_HBZones) == len(hb_zoneData[0]):
        for count, brep in enumerate(_HBZones):
            boundBoxVert = brep.GetBoundingBox(False).Center
            if boundBoxVert.X <= hb_zoneData[3][count].X+tol and boundBoxVert.X >= hb_zoneData[3][count].X-tol and boundBoxVert.Y <= hb_zoneData[3][count].Y+tol and boundBoxVert.Y >= hb_zoneData[3][count].Y-tol and boundBoxVert.Z <= hb_zoneData[3][count].Z+tol and boundBoxVert.Z >= hb_zoneData[3][count].Z-tol: pass
            else:
                checkZones = False
    else: checkZones = False
    if checkZones == True: pass
    else:
        copyHBZoneData()
        hb_zoneData = sc.sticky["Honeybee_SrfData"]
    initCheck = True
elif _HBZones != [] and sc.sticky.has_key('honeybee_release') == False:
    print "You should first let Honeybee  fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    pass


#Check the data input.
checkData = False
if _srfData.BranchCount > 0 and str(_srfData) != "tree {0}" and initCheck == True:
    checkData, annualData, simStep, srfNormalizable, pyZoneData, srfHeaders, headerUnits, total = checkTheInputs()

#Manage the inputs and outputs of the component based on the data that is hooked up.
if checkData == True:
    normByFlr, analysisPeriod, stepOfSimulation = manageInputOutput(annualData, simStep, srfNormalizable)
else: restoreInputOutput()

#If the data is meant to be normalized by surface area, check the HBZones for surface names.
if checkData == True and normByFlr == None: normByFlr = True

dataCheck = False
if _runIt == True and checkData == True and _HBZones != []:
    dataCheck, surfaceNames, srfAreas, srfBreps, pyZoneData, srfHeaders, zoneBreps = getZoneSrfs(srfHeaders, pyZoneData, hb_zoneData)
    if dataCheck == True:
        srfValues, normalizedSrfData, title, legendTitle, lb_preparation, lb_visualization = getData(pyZoneData, srfAreas, annualData, simStep, srfNormalizable, srfHeaders, headerUnits, normByFlr, analysisPeriod, stepOfSimulation, total)

#Color the surfaces with the data and get all of the other cool stuff that this component does.
if _runIt == True and checkData == True and _HBZones != [] and srfValues != [] and dataCheck == True:
    srfColors, srfBreps, srfColoredMesh, zoneWireFrame, legendInit, legendBasePt = main(srfValues, _HBZones, srfBreps, srfHeaders, title, legendTitle, lb_preparation, lb_visualization, legendPar_)
    #Unpack the legend.
    legend = []
    for count, item in enumerate(legendInit):
        if count == 0:
            legend.append(item)
        if count == 1:
            for srf in item:
                legend.append(srf)

#Hide unwanted outputs
ghenv.Component.Params.Output[4].Hidden = True
ghenv.Component.Params.Output[5].Hidden = True
