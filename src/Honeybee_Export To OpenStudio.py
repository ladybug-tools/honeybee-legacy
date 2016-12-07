#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com>, Chris Mackey <Chris@MackeyArchitecture.com>, and Chien Si Harriman <charriman@terabuild.com>
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
Use this component to export HBZones into an OpenStudio file, and run them through EnergyPlus.
_
The component outputs the report from the simulation, the file path of the IDF file, and the CSV result file from the EnergyPlus run, and two other result files that record outputs in different formats.
-
Provided by Honeybee 0.0.60
    
    Args:
        north_: Input a vector to be used as a true North direction for the energy simulation or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _epwWeatherFile: An .epw file path on your system as a text string.
        _analysisPeriod_: An optional analysis period from the Ladybug_Analysis Period component.  If no Analysis period is given, the energy simulation will be run for the enitre year.
        +++++++++++++++: ...
        _energySimPar_: Optional Energy Simulation Parameters from the "Honeybee_Energy Simulation Par" component.  If no value is connected here, the simulation will run with the following parameters:
            1 - 6 timeSteps per hour
            2 - A shadow calculation that averages over multiple days (as opposed to running it for each timeStep)
            3 - A shadow calculation frequency of 30 (meaning that the shadow calulation is averaged over every 30 days)
            4 - A maximum of 3000 points used in the shadow calculation. (This may need to be higher if you have a lot of detailed context geometry)
            5 - An colar energy calculation that includes both interior and exterior light reflections.
            6 - A simulation including a zone sizing calculation, a system sizing calculation, a plat sizing calculation, and a full run of the energy use ofver the analysis period.  The simulation is not run for the sizing period by default.
            7 - A system sizing period that runs from the extreme periods of the weather file and not a ddy file.
            8 - City terrian.
        +++++++++++++++: ...
        _HBZones: The HBZones that you wish to write into an OSM file and/or run through EnergyPlus.  These can be from any of the components that output HBZones.
        HBContext_: Optional HBContext geometry from the "Honeybee_EP Context Surfaces." component.
        simulationOutputs_: A list of the outputs that you would like EnergyPlus to write into the result CSV file.  This can be any set of any outputs that you would like from EnergyPlus, writen as a list of text that will be written into the IDF.  It is recommended that, if you are not expereinced with writing EnergyPlus outputs, you should use the "Honeybee_Write EP Result Parameters" component to request certain types of common outputs. 
        additionalStrings_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.  You can input additional text strings here that you would like written into the IDF.  The strings input here should be complete EnergyPlus objects that are correctly formatted.  You can input as many objects as you like in a list.  This input can be used to write objects into the IDF that are not currently supported by Honeybee.
        +++++++++++++++: ...
        _writeOSM: Set to "True" to have the component take your HBZones and other inputs and write them into an OSM file.  Note that only setting this to "True" and not setting the output below to "True" will not automatically run the file through EnergyPlus for you.
        runSimulation_: Set to "True" to have the component generate an IDF file from the OSM file and run the IDF through through EnergyPlus.  Set to "False" to not run the file (this is the default).  You can also connect an integer for the following options:
            0 = Do Not Run OSM and IDF thrrough EnergyPlus
            1 = Run the OSM and IDF through EnergyPlus with a command prompt window that displays the progress of the simulation
            2 = Run the OSM and IDF through EnergyPlus in the background (without the command line popup window).
            3 = Generate an IDF from the OSM file but do not run it through EnergyPlus
        openOpenStudio_: Set to "True" to open the OSM file in the OpenStudio interface.  This is useful if you want to visualize the HVAC system in OpenStudio, you want to edit the HVAC further in OpenStudio, or just want to run the simulation from OpenStudio instead of Rhino/GH.  Note that, for this to work, you must have .osm files associated with the OpenStudio application.
        fileName_: Optional text which will be used to name your OSM, IDF and result files.  Change this to aviod over-writing results of previous energy simulations.
        workingDir_: An optional working directory to a folder on your system, into which your OSM, IDF and result files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
    Returns:
        readMe!: Check here to see a report of the EnergyPlus run, including errors.
        osmFileAddress: The file path of the OSM file that has been generated on your machine.
        idfFileAddress: The file path of the IDF file that has been generated on your machine. This file is only generated when you set "runSimulation_" to "True."
        resultFileAddress: The file path of the CSV result file that has been generated on your machine.  This file is only generated when you set "runSimulation_" to "True."
        eioFileAddress:  The file path of the EIO file that has been generated on your machine.  This file contains information about the sizes of all HVAC equipment from the simulation.  This file is only generated when you set "runSimulation_" to "True."
        rddFileAddress: The file path of the Result Data Dictionary (.rdd) file that is generated after running the file through EnergyPlus.  This file contains all possible outputs that can be requested from the EnergyPlus model.  Use the "Honeybee_Read Result Dictionary" to see what outputs can be requested.
        studyFolder: The directory in which the simulation has been run.  Connect this to the 'Honeybee_Lookup EnergyPlus' folder to bring many of the files in this directory into Grasshopper.
        model: OpenStudio model. Use this output to generate gbXML file.
"""

ghenv.Component.Name = "Honeybee_Export To OpenStudio"
ghenv.Component.NickName = 'exportToOpenStudio'
ghenv.Component.Message = 'VER 0.0.60\nDEC_05_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nSEP_09_2016
#compatibleLBVersion = VER 0.0.59\nJUL_24_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import os
import sys
import System
import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh
import time
from pprint import pprint
import shutil
import copy
import math
import subprocess
import operator

rc.Runtime.HostUtils.DisplayOleAlerts(False)

if sc.sticky.has_key('honeybee_release'):
    if sc.sticky["honeybee_folders"]["OSLibPath"] != None:
        # openstudio is there
        openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
        
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
        
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg1 = "You do not have OpenStudio installed on Your System.\n" + \
            "You wont be able to use this component until you install it.\n" + \
            "Download the latest OpenStudio for Windows from:\n"
        msg2 = "https://www.openstudio.net/downloads"
        print msg1
        print msg2
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False


class WriteOPS(object):

    def __init__(self, EPParameters, weatherFilePath):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        self.hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        self.hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        self.hb_EPPar = sc.sticky["honeybee_EPParameters"]()
        self.simParameters = self.hb_EPPar.readEPParams(EPParameters)
        
        if self.simParameters[4] != None: self.ddyFile = self.simParameters[4]
        else: self.ddyFile = weatherFilePath.replace(".epw", ".ddy", 1)
        
        self.constructionList = {}
        self.materialList = {}
        self.scheduleList = {}
        self.shdCntrlList = {}
        self.frameObjList = {}
        self.bldgTypes = {}
        self.levels = {}
        self.HVACSystemDict = {}
        self.adjacentSurfacesDict = {}
        self.thermalZonesDict = {}
        
        self.csvSchedules = []
        self.csvScheduleCount = 0
        self.shadeCntrlToReplace = []
        self.replaceShdCntrl = False
        self.windowSpectralDatasets = {}
    
    def setSimulationControls(self, model):
        solarDist = self.simParameters[2]
        simulationControls = self.simParameters[3]
        
        simControl = ops.Model.getSimulationControl(model);
        simControl.setDoZoneSizingCalculation(simulationControls[0])
        simControl.setDoSystemSizingCalculation(simulationControls[1])
        simControl.setDoPlantSizingCalculation(simulationControls[2])
        simControl.setRunSimulationforSizingPeriods(simulationControls[3])
        simControl.setRunSimulationforWeatherFileRunPeriods(simulationControls[4])
        
        simControl.setSolarDistribution(solarDist)
    
    def setShadowCalculation(self, model):
        calcMethod, freq, maxFigure = self.simParameters[1]
        shadowCalculation = ops.Model.getShadowCalculation(model)
        shadowCalculation.setMaximumFiguresInShadowOverlapCalculations(int(maxFigure))
        shadowCalculation.setSkyDiffuseModelingAlgorithm(calcMethod)
        shadowCalculation.setCalculationFrequency(int(freq))
    
    def setTimestep(self, model):
        timestepInput = self.simParameters[0]
        timestep = ops.Model.getTimestep(model)
        timestep.setNumberOfTimestepsPerHour(int(timestepInput))
    
    def setSite(self, epwFilePath, model):
        # Read the site from the EPW file.
        epwfile = open(epwFilePath,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        locName = csheadline[1]+'\t'+csheadline[3]
        lat = float(csheadline[6])
        lngt = float(csheadline[7])
        timeZone = float(csheadline[8])
        elev = float(csheadline[9][:-1])
        epwfile.close()
        
        # Get the OpenStudio Model Site.
        site = ops.Model.getSite(model)
        
        # Set the properties of the site.
        site.setName(locName)
        site.setLatitude(lat)
        site.setLongitude(lngt)
        site.setTimeZone(timeZone)
        site.setElevation(elev)
    
    def setStartDayOfWeek(self, model):
        # The ability to set the start day of week currently breaks OpenStudio's way of assigning schedules.
        # As a result, this feature of OpenStudio SDK is not being used now.
        # Instead, any specified start day of the year is assigned in the IDF after export.
        startDOW = self.simParameters[8]
        if startDOW == None:
            startDOW = "UseWeatherFile"
        
        yearDesc = ops.OpenStudioModelSimulation.getYearDescription(model)
        yds = model.getObjectsByType(ops.IddObjectType("OS:YearDescription"))
        yds[0].setString(2, startDOW)
    
    def setHolidays(self, model):
        # Even though holidays are built into OpenStudio SDK and written into the OSM,
        # it seems like they are not yet written into the IDF.
        # as a result, there is an additional function to add the holidays into the IDF later in this component.
        if self.simParameters[7] != []:
            for count, hol in enumerate(self.simParameters[7]):
                holiday = ops.RunPeriodControlSpecialDays(hol, model)
                holiday.setDuration(1)
                holiday.setSpecialDayType("Holiday")
    
    def setTerrain(self, model):
        terrain = self.simParameters[5]
        site = ops.Model.getSite(model)
        site.setTerrain(terrain)
    
    def setGroundTemps(self, model):
        grndTemps = self.simParameters[6]
        if grndTemps != []:
            opsGrndTemps = model.getSiteGroundTemperatureBuildingSurface()
            opsGrndTemps.setJanuaryGroundTemperature(grndTemps[0])
            opsGrndTemps.setFebruaryGroundTemperature(grndTemps[1])
            opsGrndTemps.setMarchGroundTemperature(grndTemps[2])
            opsGrndTemps.setAprilGroundTemperature(grndTemps[3])
            opsGrndTemps.setMayGroundTemperature(grndTemps[4])
            opsGrndTemps.setJuneGroundTemperature(grndTemps[5])
            opsGrndTemps.setJulyGroundTemperature(grndTemps[6])
            opsGrndTemps.setAugustGroundTemperature(grndTemps[7])
            opsGrndTemps.setSeptemberGroundTemperature(grndTemps[8])
            opsGrndTemps.setOctoberGroundTemperature(grndTemps[9])
            opsGrndTemps.setNovemberGroundTemperature(grndTemps[10])
            opsGrndTemps.setDecemberGroundTemperature(grndTemps[11])
    
    def setRunningPeriod(self, runningPeriod, model):
        # get the days from numbers
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.lb_preparation.readRunPeriod(runningPeriod, True)
        
        runPeriod = ops.Model.getRunPeriod(model)
        
        runPeriod.setBeginDayOfMonth(stDay)
        runPeriod.setBeginMonth(stMonth)
        runPeriod.setEndDayOfMonth(endDay)
        runPeriod.setEndMonth(endMonth)
    
    def setNorth(self, north, model):
        northAngle, northVector = self.lb_preparation.angle2north(north)
        building = ops.Model.getBuilding(model)
        building.setNorthAxis(math.degrees(northAngle))
    
    def generateStories(self, HBZones, model):
        levels = []
        for HBZone in HBZones:
            floorH = "%.3f"%HBZone.getFloorZLevel()
            if floorH not in self.levels.keys():
                levels.append(float(floorH))
        
        levels.sort()
        for floorH in levels:
            story = ops.BuildingStory(model)
            story.setNominalZCoordinate(float(floorH))
            self.levels["%.3f"%floorH] = story
        
    def setupLevels(self, zone, space):
        floorH = "%.3f"%zone.getFloorZLevel()
        space.setBuildingStory(self.levels[floorH])
        return space
    
    def setSizingFactors(self, model):
        heatSizFac = self.simParameters[9]
        coolSizFac = self.simParameters[10]
        sizParams = ops.Model.getSizingParameters(model)
        try:
            sizParams.setHeatingSizingFactor(heatSizFac)
        except:
            pass
        try:
            sizParams.setCoolingSizingFactor(coolSizFac)
        except:
            pass
    
    def addDesignDays(self, model):
        # check ddy file to be available
        ddyFile = self.ddyFile
        ddFound = False
        
        if not os.path.isfile(ddyFile):
            print "Can't find ddy file next to the EPW."
            print "Extreme values from the weather file design will be used instead."
        else:
            ddyPath = ops.Path(ddyFile)
            ddyIdf = ops.IdfFile.load(ddyPath, ops.IddFileType("EnergyPlus"))
            ddyWorkSpcae = ops.Workspace(ddyIdf.get())
            reverseTranslator = ops.EnergyPlusReverseTranslator()
            ddyModel = reverseTranslator.translateWorkspace(ddyWorkSpcae)
            designDayVector = ddyModel.getDesignDays()
            selectedDesignDays = ops.WorkspaceObjectVector()
            for dday in designDayVector:
                if dday.name().get().find(".4%")> -1 or dday.name().get().find("99.6%") > -1:
                    selectedDesignDays.Add(dday)
                    ddFound = True
            model.addObjects(selectedDesignDays)
        
        return ddFound
    
    def writeDDObjStr(self, ddName, designType, month, day, dbTemp, dbTempRange, wbTemp, enth, humidConditType, pressure, windSpeed, windDir, ashraeSkyClearness):
        ddStr =  '! ' + ddName + '\n' + \
            'SizingPeriod:DesignDay,\n' + \
            '\t' + ddName + ',     !- Name\n' + \
            '\t' + str(month) + ',      !- Month\n' + \
            '\t' + str(day) + ',      !- Day of Month\n' + \
            '\t' + designType + ',!- Day Type\n' + \
            '\t' + str(dbTemp) + ',      !- Maximum Dry-Bulb Temperature {C}\n' + \
            '\t' + str(dbTempRange) + ',      !- Daily Dry-Bulb Temperature Range {C}\n' + \
            '\t' + 'DefaultMultipliers, !- Dry-Bulb Temperature Range Modifier Type\n' + \
            '\t' + ',      !- Dry-Bulb Temperature Range Modifier Schedule Name\n' + \
            '\t' + humidConditType + ',      !- Humidity Condition Type\n' + \
            '\t' + str(wbTemp) + ',      !- Wetbulb or Dewpoint at Maximum Dry-Bulb {C}\n' + \
            '\t' + ',      !- Humidity Indicating Day Schedule Name\n' + \
            '\t' + ',      !- Humidity Ratio at Maximum Dry-Bulb {kgWater/kgDryAir}\n' + \
            '\t' + str(enth) + ',      !- Enthalpy at Maximum Dry-Bulb {J/kg}\n' + \
            '\t' + ',      !- Daily Wet-Bulb Temperature Range {deltaC}\n' + \
            '\t' + str(pressure) + ',      !- Barometric Pressure {Pa}\n' + \
            '\t' + str(windSpeed) + ',      !- Wind Speed {m/s} design conditions vs. traditional 6.71 m/s (15 mph)\n' + \
            '\t' + str(windDir) + ',      !- Wind Direction {Degrees; N=0, S=180}\n' + \
            '\t' + 'No,      !- Rain {Yes/No}\n' + \
            '\t' + 'No,      !- Snow on ground {Yes/No}\n' + \
            '\t' + 'No,      !- Daylight Savings Time Indicator\n' + \
            '\t' + 'ASHRAEClearSky' + ', !- Solar Model Indicator\n' + \
            '\t' + ',      !- Beam Solar Day Schedule Name\n' + \
            '\t' + ',      !- Diffuse Solar Day Schedule Name\n' + \
            '\t' + ',      !- ASHRAE Clear Sky Optical Depth for Beam Irradiance (taub)\n' + \
            '\t' + ',      !- ASHRAE Clear Sky Optical Depth for Diffuse Irradiance (taud)\n' + \
            '\t' + str(ashraeSkyClearness) + ';      !- Clearness {0.0 to 1.1}\n' + '\n'
        
        return ddStr
    
    def createDdyFromEPW(self, epwWeatherFile, workingDir, lb_preparation, lb_comfortModels):
        # Extract the relevant data from the EPW.
        # We need the following: dbTemp, dewPoint, rH, windSpeed, windDir, windDir, wetBulb, enthalpy
        dbTemp = []
        dewPoint = []
        rH = []
        windSpeed = []
        windDir = []
        barPress = []
        wetBulb = []
        epwfile = open(epwWeatherFile,"r")
        for count, line in enumerate(epwfile):
            if count > 7:
                dbTemp.append(float(line.split(',')[6]))
                dewPoint.append(float(line.split(',')[7]))
                rH.append(float(line.split(',')[8]))
                barPress.append(float(line.split(',')[9]))
                windSpeed.append(float(line.split(',')[21]))
                windDir.append(float(line.split(',')[20]))
        epwfile.close()
        hR, enthalpy, pP, sP = lb_comfortModels.calcHumidRatio(dbTemp, rH, barPress)
        for i, tem in enumerate(dbTemp):
            wetBulb.append(lb_comfortModels.findWetBulb(tem, rH[i], barPress[i]))
        
        # Find the conditions for the most extreme hours in the epw.  These are the 7 extreme conditions we need:
            # 1 - Winnter Design Day - Min Dry Bulb (Sensible Heating)
            # 2 - Winter Design Day - Min Dew Point (Humidification)
            # 3 - Winter Design Day = Max Wind Speed when temperature is less than 1 standard deviation of annual mean.
            # 4 - Summer Design Day - Max Dry Bulb (Sensible Cooling)
            # 5 - Summer Design Day - Max Wet Bulb (Dehumidification)
            # 6 - Summer Design Day - Max Dew Point (Dehumidification)
            # 7 - Summer Design Day - Max Enthalpy (Dehumidification)
        sortedDB, corrWB = zip(*sorted(zip(dbTemp, wetBulb)))
        minDB = sortedDB[34] # Design Condition 1
        WBforMinDB = corrWB[34]
        maxDB = sortedDB[-35] # Design Condition 4
        WBforMaxDB = corrWB[-35]
        sortedDP, corrDB = zip(*sorted(zip(dewPoint, dbTemp)))
        minDP = sortedDP[34] # Design Condition 2
        DBforMinDP = corrDB[34]
        maxDP = sortedDP[-35] # Design Condition 6
        DBforMaxDP = corrDB[-35]
        sortedWB, corresDB = zip(*sorted(zip(wetBulb, dbTemp)))
        maxWB = sortedWB[-35] # Design Condition 5
        DBforMaxWB = corresDB[-35]
        sortedEnth, correspondDB = zip(*sorted(zip(enthalpy, dbTemp)))
        maxEnth = int(sortedEnth[-35] * 1000) # Design Condition 7
        DBforMaxEnth = correspondDB[-35]
        
        coldStdDevTemp = sortedDB[1384]
        hotStdDevTemp = sortedDB[-1385]
        winSpBelowTemp = []
        windDirBelowTemp = []
        winSpAboveTemp = []
        windDirAboveTemp = []
        for i, tem in enumerate(dbTemp):
            if tem < coldStdDevTemp:
                winSpBelowTemp.append(windSpeed[i])
                windDirBelowTemp.append(windDir[i])
            elif tem > hotStdDevTemp:
                winSpAboveTemp.append(windSpeed[i])
                windDirAboveTemp.append(windDir[i])
        winSpBelowTemp.sort()
        coldMonWind = winSpBelowTemp[922]
        coldMonWinDir = int(sum(windDirBelowTemp)/len(windDirBelowTemp))
        maxWind = winSpBelowTemp[-5] # Design Condition 3
        winSpAboveTemp.sort()
        hotMonWind = winSpAboveTemp[922]
        hotMonWinDir = int(sum(windDirAboveTemp)/len(windDirAboveTemp))
        
        # Calculate a few other required values from the epw data.
        # Like average annual pressure and coldest/hottest month.
        # and average wind speed/direction during these months.
        avgEpwParPress = int(sum(barPress)/len(barPress))
        
        def binAndAvgByMonth(dataSet):
            avgMonthData = []
            binnedMonthData = []
            for mon in range(12):
                binnedMonthData.append([])
            for i, x in enumerate(dataSet):
                d, m, t = lb_preparation.hour2Date(i, True)
                binnedMonthData[m].append(x)
            for dataList in binnedMonthData:
                avgMonthData.append(sum(dataList)/len(dataList))
            return avgMonthData, binnedMonthData
        
        def partitionList(l, n):
            for i in range(0, len(l), n):
                yield l[i:i+n]
        
        avgMonTemps, binMonTemps = binAndAvgByMonth(dbTemp)
        monNums = range(12)
        avgMonTempsSort, monNumsSort = zip(*sorted(zip(avgMonTemps, monNums)))
        coldMonth = monNumsSort[0]
        hotMonth = monNumsSort[-1]
        allHotMonthTemps = binMonTemps[hotMonth]
        dayHotMonTemps = partitionList(allHotMonthTemps, 24)
        dailyTempDiff = []
        for day in dayHotMonTemps:
            day.sort()
            dailyTempDiff.append(day[-1]-day[0])
        hotDayDBTempRange = (int((sum(dailyTempDiff)/len(dailyTempDiff))*100))/100
        
        
        # Assemble a list of design condition strings to write into the ddy file.
        ddStrs = []
        ddStrs.append(self.writeDDObjStr('Ann Htg 99.6% Condns DB', 'WinterDesignDay', coldMonth+1, 21, minDB, 0, minDB, '', 'Wetbulb', avgEpwParPress, coldMonWind, coldMonWinDir, 0))
        ddStrs.append(self.writeDDObjStr('Ann Hum_n 99.6% Condns DP=>MCDB', 'WinterDesignDay', coldMonth+1, 21, DBforMinDP, 0, minDP, '', 'Dewpoint', avgEpwParPress, coldMonWind, coldMonWinDir, 0))
        ddStrs.append(self.writeDDObjStr('Ann Htg Wind 99.6% Condns WS=>MCDB', 'WinterDesignDay', coldMonth+1, 21, coldStdDevTemp, 0, coldStdDevTemp, '', 'Wetbulb', avgEpwParPress, maxWind, coldMonWinDir, 0))
        
        ddStrs.append(self.writeDDObjStr('Ann Clg .4% Condns DB=>MWB', 'SummerDesignDay', hotMonth+1, 21, maxDB, hotDayDBTempRange, WBforMaxDB, '', 'Wetbulb', avgEpwParPress, hotMonWind, hotMonWinDir, 1.2))
        ddStrs.append(self.writeDDObjStr('Ann Clg .4% Condns WB=>MDB', 'SummerDesignDay', hotMonth+1, 21, DBforMaxWB, hotDayDBTempRange, maxWB, '', 'Wetbulb', avgEpwParPress, hotMonWind, hotMonWinDir, 1.2))
        ddStrs.append(self.writeDDObjStr('Ann Clg .4% Condns DP=>MDB', 'SummerDesignDay', hotMonth+1, 21, DBforMaxDP, hotDayDBTempRange, maxDP, '', 'Dewpoint', avgEpwParPress, hotMonWind, hotMonWinDir, 1.2))
        ddStrs.append(self.writeDDObjStr('Ann Clg .4% Condns Enth=>MDB', 'SummerDesignDay', hotMonth+1, 21, DBforMaxEnth, hotDayDBTempRange, '', maxEnth, 'Enthalpy', avgEpwParPress, hotMonWind, hotMonWinDir, 1.2))
        
        # Write the design day objects into a .ddy file.
        epwFileName = epwWeatherFile.split('\\')[-1].split('.')[0]
        self.ddyFile = workingDir + '\\' + epwFileName + '.ddy'
        ddyFile = open(self.ddyFile, "w")
        for sizingObj in ddStrs:
            ddyFile.write(sizingObj)
        ddyFile.close()
    
    def isConstructionInLib(self, constructionName):
        return constructionName in self.constructionList
    
    def addConstructionToLib(self, constructionName, construction):
        self.constructionList[constructionName] = construction
    
    def getConstructionFromLib(self, constructionName):
        return self.constructionList[constructionName]
    
    def isMaterialInLib(self, materialName):
        return materialName in self.materialList.keys()
    
    def addMaterialToLib(self, materialName, material):
        self.materialList[materialName] = material
        
    def getMaterialFromLib(self, materialName):
        return self.materialList[materialName]
    
    def isScheduleInLib(self, scheduleName):
        return scheduleName in self.scheduleList.keys()
        
    def addScheduleToLib(self, scheduleName, schedule):
        self.scheduleList[scheduleName] = schedule
    
    def getScheduleFromLib(self, scheduleName):
        return self.scheduleList[scheduleName]
    
    def isShdCntrlInLib(self, shdCntrlName):
        return shdCntrlName in self.shdCntrlList.keys()
    
    def addShdCntrlToLib(self, shdCntrlName, shdCntrl):
        self.shdCntrlList[shdCntrlName] = shdCntrl
        
    def getShdCntrlFromLib(self, shdCntrlName):
        return self.shdCntrlList[shdCntrlName]
    
    def isFrameObjInLib(self, frameObjName):
        return frameObjName in self.frameObjList.keys()
    
    def addFrameObjToLib(self, frameObjName, frameObj):
        self.frameObjList[frameObjName] = frameObj
        
    def getFrameObjFromLib(self, frameObjName):
        return self.frameObjList[frameObjName]
    
    def createOSScheduleTypeLimitsFromValues(self, model, lowerLimit, upperLimit, numericType, unitType):
        typeLimit = ops.ScheduleTypeLimits(model)
        try: typeLimit.setLowerLimitValue(float(lowerLimit))
        except: pass
        try: typeLimit.setUpperLimitValue(float(upperLimit))
        except: pass
        typeLimit.setNumericType(numericType)
        try: typeLimit.setUnitType(unitType)
        except: pass
        
        return typeLimit
    
    def createOSScheduleTypeLimits(self, schdTypeLimitsName, model):
        """
        ['ScheduleTypeLimits', '0', '1', 'Continuous']
        ['Schedule Type', 'Lower Limit Value {BasedOnField A3}', 'Upper Limit Value {BasedOnField A3}', 'Numeric Type']
        """
        values, comments = self.hb_EPScheduleAUX.getScheduleTypeLimitsDataByName(schdTypeLimitsName, ghenv.Component)
        typeLimit = ops.ScheduleTypeLimits(model)
        try: typeLimit.setLowerLimitValue(float(values[1]))
        except: pass
        try: typeLimit.setUpperLimitValue(float(values[2]))
        except: pass
        typeLimit.setNumericType(values[3])
        try: typeLimit.setUnitType(values[4])
        except: pass
        
        return typeLimit
    
    def createConstantScheduleRuleset(self, ruleSetName, schName, typeLimitName, value, model):
        scheduleRuleset = ops.ScheduleRuleset(model)
        scheduleRuleset.setName(ruleSetName)
        scheduleDay = scheduleRuleset.defaultDaySchedule()
        scheduleDay.setName(schName)
        scheduleDay.setScheduleTypeLimits(self.createOSScheduleTypeLimits(typeLimitName, model))
        osUntilTime = ops.Time(1)
        scheduleDay.removeValue(osUntilTime)
        scheduleDay.addValue(osUntilTime, float(value))
        return scheduleRuleset
    
    def createConstantOSSchedule(self, schName, values, model):
        """
        'Schedule:Constant'
        ['Schedule Type', 'Schedule Type Limits Name', 'Hourly Value']
        """
        scheduleConstant = ops.ScheduleConstant(model)
        scheduleConstant.setName(schName)
        scheduleConstant.setValue(float(values[2]))
        if values[1] != None:
            typeLimitName = values[1]
            try: scheduleConstant.setScheduleTypeLimits(self.getScheduleFromLib(typeLimitName))
            except: scheduleConstant.setScheduleTypeLimits(typeLimitName)
        return scheduleConstant
        
    def createDayOSSchedule(self, schName, values, model):
        """
        Schedule:Day:Interval
        ['Schedule Type', 'Schedule Type Limits Name', 'Interpolate to Timestep', 'Time 1 {hh:mm}', 'Value Until Time 1']
        """
        scheduleDay = ops.ScheduleDay(model)
        scheduleDay.setName(schName)
        typeLimitName = values[1]
        
        scheduleDay.setScheduleTypeLimits(self.getScheduleFromLib(typeLimitName))
        
        numberOfDaySch = int((len(values) - 3) /2)

        for i in range(numberOfDaySch):
            untilTime = map(int, values[2 * i + 3].split(":"))
            fractionalTime = untilTime[0] +  untilTime[1]/60
            osUntilTime = ops.Time(fractionalTime/24)
            scheduleDay.addValue(osUntilTime, float(values[2 * i + 4]))
            
        return scheduleDay
        
    def createWeeklyOSSchedule(self, schName, values, model):
        """
        Schedule:Week:Daily
        ['Schedule Type', 'Sunday Schedule:Day Name', 'Monday Schedule:Day Name',
        'Tuesday Schedule:Day Name', 'Wednesday Schedule:Day Name', 'Thursday Schedule:Day Name',
        'Friday Schedule:Day Name', 'Saturday Schedule:Day Name', 'Holiday Schedule:Day Name',
        'SummerDesignDay Schedule:Day Name', 'WinterDesignDay Schedule:Day Name',
        'CustomDay1 Schedule:Day Name', 'CustomDay2 Schedule:Day Name']
        """
        
        
        weeklySchd = ops.ScheduleWeek(model)
        weeklySchd.setName(schName)
        
        sundaySchedule = self.getOSSchedule(values[1], model)
        weeklySchd.setSundaySchedule(sundaySchedule)
        
        mondaySchedule = self.getOSSchedule(values[2], model)
        weeklySchd.setMondaySchedule(mondaySchedule)
        
        tuesdaySchedule = self.getOSSchedule(values[3], model)
        weeklySchd.setTuesdaySchedule(tuesdaySchedule)
        
        wednesdaySchedule = self.getOSSchedule(values[4], model)
        weeklySchd.setWednesdaySchedule(wednesdaySchedule)
        
        thursdaySchedule = self.getOSSchedule(values[5], model)
        weeklySchd.setThursdaySchedule(thursdaySchedule)
        
        fridaySchedule = self.getOSSchedule(values[6], model)
        weeklySchd.setFridaySchedule(fridaySchedule)
        
        saturdaySchedule = self.getOSSchedule(values[7], model)
        weeklySchd.setSaturdaySchedule(saturdaySchedule)
        
        holidaySchedule = self.getOSSchedule(values[8], model)
        weeklySchd.setHolidaySchedule(holidaySchedule)
        
        summerDesignDaySchedule = self.getOSSchedule(values[9], model)
        weeklySchd.setSummerDesignDaySchedule(summerDesignDaySchedule)
        
        winterDesignDaySchedule = self.getOSSchedule(values[10], model)
        weeklySchd.setWinterDesignDaySchedule(winterDesignDaySchedule)
        
        customDay1Schedule = self.getOSSchedule(values[11], model)
        weeklySchd.setCustomDay1Schedule(customDay1Schedule)
        
        customDay2Schedule = self.getOSSchedule(values[12], model)
        weeklySchd.setCustomDay2Schedule(customDay2Schedule)
        
        return weeklySchd
    
    def createYearlyOSSchedule(self, schName, values, model):
        """
        "Schedule:Year"
        """
        name = schName
        typeLimitName = values[1]
        schedule = ops.ScheduleYear(model)
        schedule.setName(name)
        schedule.setScheduleTypeLimits(self.getScheduleFromLib(typeLimitName))
        
        # generate weekly schedules
        numOfWeeklySchedules = int((len(values)-2)/5)
        
        for i in range(numOfWeeklySchedules):
            weekDayScheduleName = values[5 * i + 2]
            startDate = ops.Date(ops.MonthOfYear(int(values[5 * i + 3])), int(values[5 * i + 4]))
            endDate = ops.Date(ops.MonthOfYear(int(values[5 * i + 5])), int(values[5 * i + 6]))
            
            ScheduleWeek = self.getOSSchedule(weekDayScheduleName, model)
            
            schedule.addScheduleWeek(endDate, ScheduleWeek)
            
        return schedule
    
    def getOSSchedule(self, schName, model):
        csvSched = False
        if schName.lower().endswith(".csv"):
            msg = "Currently OpenStudio component cannot use .csv file as a schedule.\n" + \
                      "The schedule: " + schName + " - will be written into the EnergyPlus IDF File after it has been written by decompressing the OS file."
            print msg
            self.csvSchedules.append(schName)
            self.csvScheduleCount += 1
            csvSched = True
        
        if csvSched == True:
            values, comments = self.hb_EPScheduleAUX.getScheduleDataByName('DEFAULTCSVPLACEHOLDER', ghenv.Component)
        else:
            values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName, ghenv.Component)
        
        if values[0].lower() != "schedule:week:daily":
            
            scheduleTypeLimitsName = values[1]
            if not self.isScheduleInLib(scheduleTypeLimitsName):
                OSScheduleTypeLimits = self.createOSScheduleTypeLimits(values[1], model)
                self.addScheduleToLib(scheduleTypeLimitsName, OSScheduleTypeLimits)
        
        if not self.isScheduleInLib(schName):
            if values[0].lower() == "schedule:year":
                OSSchedule = self.createYearlyOSSchedule(schName, values, model)
            elif values[0].lower() == "schedule:day:interval":
                OSSchedule = self.createDayOSSchedule(schName, values, model)
            elif values[0].lower() == "schedule:week:daily":
                OSSchedule = self.createWeeklyOSSchedule(schName, values, model)
            elif values[0].lower() == "schedule:constant":
                OSSchedule = self.createConstantOSSchedule(schName, values, model)
            else:
                # print values[0]
                OSSchedule = None
            
            if OSSchedule!=None:
                # add to library
                self.addScheduleToLib(schName, OSSchedule)
            return OSSchedule
        else:
            return self.getScheduleFromLib(schName)
    
    def getOSFrameObj(self, frameObjName, model):
        if not self.isFrameObjInLib(frameObjName):
            values = sc.sticky["honeybee_WindowPropLib"][frameObjName]
            
            OSFrameObj = ops.WindowPropertyFrameAndDivider(model)
            OSFrameObj.setFrameWidth(float(values[1][0]))
            OSFrameObj.setFrameConductance(float(values[4][0]))
            OSFrameObj.setRatioOfFrameEdgeGlassConductanceToCenterOfGlassConductance(float(values[5][0]))
            OSFrameObj.setFrameSolarAbsorptance(float(values[6][0]))
            OSFrameObj.setFrameVisibleAbsorptance(float(values[7][0]))
            OSFrameObj.setFrameThermalHemisphericalEmissivity(float(values[8][0]))
            
            self.addFrameObjToLib(frameObjName, OSFrameObj)
            return OSFrameObj
        else:
            return self.getFrameObjFromLib(frameObjName)
    
    def getOSShdCntrl(self, shdCntrlName, model):
        if not self.isShdCntrlInLib(shdCntrlName):
            # Make the shade control obect.
            values = self.hb_EPObjectsAux.getEPObjectDataByName(shdCntrlName)
            
            if values[2][0] != '':
                # Iniitalize for construction (for switchable glazing).
                constrName = values[2][0]
                if not self.isConstructionInLib(constrName):
                    OSConstruction = self.getOSConstruction(constrName, model)
                    self.addConstructionToLib(constrName, OSConstruction)
                else:
                    OSConstruction = self.getConstructionFromLib(constrName)
                OSShdCntrl = ops.ShadingControl(OSConstruction)
            else:
                # Iniitalize for material (for blinds and shades).
                materialName = values[8][0]
                if not self.isMaterialInLib(materialName):
                    OSMaterial = self.getOSMaterial(materialName, model)
                    self.addMaterialToLib(materialName, OSMaterial)
                else:
                    OSMaterial = self.getMaterialFromLib(materialName)
                
                OSShdCntrl = ops.ShadingControl(OSMaterial)
            
            # Shading Type
            if values[1][0] != '':
                OSShdCntrl.setShadingType(values[1][0])
            
            # Shading Control Type.
            if values[3][0] != '':
                ### Openstudio currently does not support any shading control other than OnIfHighSolarOnWindow.
                # As such, there is a workaround above for now.
                if values[3][0] == 'OnIfHighSolarOnWindow':
                    OSShdCntrl.setShadingControlType(str(values[3][0]))
                else:
                    self.replaceShdCntrl = True
            self.shadeCntrlToReplace.append([shdCntrlName, OSShdCntrl.name()])
            
            # Shading Schedule.
            if values[4][0] != '':
                osSched = self.getOSSchedule(values[4][0], model)
                OSShdCntrl.setSchedule(osSched)
            
            # Shading setpoint.
            if values[5][0] != '':
                OSShdCntrl.setSetpoint(float(values[5][0]))
            
            # Openstudio also does not support a second setpoint.  This code really doen't do anything for now.
            try:
                setP2 = float(values[11][0])
                OSShdCntrl.setDouble(12, setP2)
            except:
                pass
            
            self.addShdCntrlToLib(shdCntrlName, OSShdCntrl)
            return OSShdCntrl
        else:
            return self.getShdCntrlFromLib(shdCntrlName)
    
    def assignThermalZone(self, zone, space, model):
        thermalZone = ops.ThermalZone(model)
        ops.OpenStudioModelHVAC.setThermalZone(space, thermalZone)
        thermalZone.setName(zone.name)
        return space, thermalZone
    
    ### START OF FUNCTIONS FOR CREATING HVAC SYSTEMS FROM SCRATCH ###
    """
    These functions are a python adaptation of several functions from the OsLib_HVAC.rb.
    These ruby versions of these functions are used for many of the 
    Advanced Energy Design Guideline (AEDG) measures that have been released by NREL.
    """
    def createDefaultAEDGPump(self, model, pEfficiency, pressRise=119563):
        pump = ops.PumpVariableSpeed(model)
        pump.setRatedPumpHead(pressRise) #Pa
        pump.setMotorEfficiency(pEfficiency)
        pump.setCoefficient1ofthePartLoadPerformanceCurve(0)
        pump.setCoefficient2ofthePartLoadPerformanceCurve(0.0216)
        pump.setCoefficient3ofthePartLoadPerformanceCurve(-0.0325)
        pump.setCoefficient4ofthePartLoadPerformanceCurve(1.0095)
        return pump
    
    def createDefaultAEDGFan(self, fanType, model, airDetails):
        if fanType == 'CV':
            fan = ops.FanConstantVolume(model, model.alwaysOnDiscreteSchedule())
        elif fanType == 'VV':
            fan = ops.FanVariableVolume(model, model.alwaysOnDiscreteSchedule())
        
        if airDetails != None and airDetails.fanTotalEfficiency != 'Default': 
            fan.setFanEfficiency(airDetails.fanTotalEfficiency)
        else:
            if fanType == 'CV':
                fan.setFanEfficiency(0.6)
            else:
                fan.setFanEfficiency(0.69)
        if airDetails != None and airDetails.fanPressureRise != 'Default': 
            fan.setPressureRise(airDetails.fanPressureRise)
        else:
            if fanType == 'CV':
                fan.setPressureRise(500) #Pa
            else:
                fan.setPressureRise(1125) #Pa
        if airDetails != None and airDetails.airSysHardSize != 'Default':
            fan.setMaximumFlowRate(float(airDetails.airSysHardSize))
        else:
            fan.autosizeMaximumFlowRate()
        if airDetails != None and airDetails.fanMotorEfficiency != 'Default':
            fan.setMotorEfficiency(airDetails.fanMotorEfficiency)
        else:
            fan.setMotorEfficiency(0.9)
        fan.setMotorInAirstreamFraction(1.0)
        return fan
    
    def createDefaultAEDGWaterChiller(self, model, coolingDetails):
        # create clgCapFuncTempCurve
        clgCapFuncTempCurve = ops.CurveBiquadratic(model)
        clgCapFuncTempCurve.setCoefficient1Constant(1.07E+00)
        clgCapFuncTempCurve.setCoefficient2x(4.29E-02)
        clgCapFuncTempCurve.setCoefficient3xPOW2(4.17E-04)
        clgCapFuncTempCurve.setCoefficient4y(-8.10E-03)
        clgCapFuncTempCurve.setCoefficient5yPOW2(-4.02E-05)
        clgCapFuncTempCurve.setCoefficient6xTIMESY(-3.86E-04)
        clgCapFuncTempCurve.setMinimumValueofx(0)
        clgCapFuncTempCurve.setMaximumValueofx(20)
        clgCapFuncTempCurve.setMinimumValueofy(0)
        clgCapFuncTempCurve.setMaximumValueofy(50)
        # create eirFuncTempCurve
        eirFuncTempCurve = ops.CurveBiquadratic(model)
        eirFuncTempCurve.setCoefficient1Constant(4.68E-01)
        eirFuncTempCurve.setCoefficient2x(-1.38E-02)
        eirFuncTempCurve.setCoefficient3xPOW2(6.98E-04)
        eirFuncTempCurve.setCoefficient4y(1.09E-02)
        eirFuncTempCurve.setCoefficient5yPOW2(4.62E-04)
        eirFuncTempCurve.setCoefficient6xTIMESY(-6.82E-04)
        eirFuncTempCurve.setMinimumValueofx(0)
        eirFuncTempCurve.setMaximumValueofx(20)
        eirFuncTempCurve.setMinimumValueofy(0)
        eirFuncTempCurve.setMaximumValueofy(50)
        # create eirFuncPlrCurve
        eirFuncPlrCurve = ops.CurveQuadratic(model)
        eirFuncPlrCurve.setCoefficient1Constant(1.41E-01)
        eirFuncPlrCurve.setCoefficient2x(6.55E-01)
        eirFuncPlrCurve.setCoefficient3xPOW2(2.03E-01)
        eirFuncPlrCurve.setMinimumValueofx(0)
        eirFuncPlrCurve.setMaximumValueofx(1.2)
        # construct chiller
        chiller = ops.ChillerElectricEIR(model,clgCapFuncTempCurve,eirFuncTempCurve,eirFuncPlrCurve)
        if coolingDetails != None and coolingDetails.coolingCOP != 'Default':
            chiller.setReferenceCOP(coolingDetails.coolingCOP)
        else:
            chiller.setReferenceCOP(5.5)
        if coolingDetails != None and coolingDetails.supplyTemperature != 'Default':
            chiller.setReferenceLeavingChilledWaterTemperature(coolingDetails.supplyTemperature)
        chiller.setCondenserType("WaterCooled")
        chiller.setChillerFlowMode("ConstantFlow")
        return chiller
    
    def createDefaultAEDGAirChiller(self, model, coolingDetails):
        # create clgCapFuncTempCurve
        clgCapFuncTempCurve = ops.CurveBiquadratic(model)
        clgCapFuncTempCurve.setCoefficient1Constant(1.05E+00)
        clgCapFuncTempCurve.setCoefficient2x(3.36E-02)
        clgCapFuncTempCurve.setCoefficient3xPOW2(2.15E-04)
        clgCapFuncTempCurve.setCoefficient4y(-5.18E-03)
        clgCapFuncTempCurve.setCoefficient5yPOW2(-4.42E-05)
        clgCapFuncTempCurve.setCoefficient6xTIMESY(-2.15E-04)
        clgCapFuncTempCurve.setMinimumValueofx(0)
        clgCapFuncTempCurve.setMaximumValueofx(20)
        clgCapFuncTempCurve.setMinimumValueofy(0)
        clgCapFuncTempCurve.setMaximumValueofy(50)
        # create eirFuncTempCurve
        eirFuncTempCurve = ops.CurveBiquadratic(model)
        eirFuncTempCurve.setCoefficient1Constant(5.83E-01)
        eirFuncTempCurve.setCoefficient2x(-4.04E-03)
        eirFuncTempCurve.setCoefficient3xPOW2(4.68E-04)
        eirFuncTempCurve.setCoefficient4y(-2.24E-04)
        eirFuncTempCurve.setCoefficient5yPOW2(4.81E-04)
        eirFuncTempCurve.setCoefficient6xTIMESY(-6.82E-04)
        eirFuncTempCurve.setMinimumValueofx(0)
        eirFuncTempCurve.setMaximumValueofx(20)
        eirFuncTempCurve.setMinimumValueofy(0)
        eirFuncTempCurve.setMaximumValueofy(50)
        # create eirFuncPlrCurve
        eirFuncPlrCurve = ops.CurveQuadratic(model)
        eirFuncPlrCurve.setCoefficient1Constant(4.19E-02)
        eirFuncPlrCurve.setCoefficient2x(6.25E-01)
        eirFuncPlrCurve.setCoefficient3xPOW2(3.23E-01)
        eirFuncPlrCurve.setMinimumValueofx(0)
        eirFuncPlrCurve.setMaximumValueofx(1.2)
        # construct chiller
        chiller = ops.ChillerElectricEIR(model,clgCapFuncTempCurve,eirFuncTempCurve,eirFuncPlrCurve)
        if coolingDetails != None and coolingDetails.coolingCOP != 'Default':
            chiller.setReferenceCOP(coolingDetails.coolingCOP)
        else:
            chiller.setReferenceCOP(2.93)
        if coolingDetails != None and coolingDetails.supplyTemperature != 'Default':
            chiller.setReferenceLeavingChilledWaterTemperature(coolingDetails.supplyTemperature)
        chiller.setCondenserType("AirCooled")
        chiller.setChillerFlowMode("ConstantFlow")
        return chiller
    
    def createHotWaterPlant(self, model, hotWaterSetpointSchedule, heatingDetails, HVACCount, radLoop = False):
        hotWaterPlant = ops.PlantLoop(model)
        if radLoop == True:
            hotWaterPlant.setName("Hot Water Radiant Loop" + str(HVACCount))
        else:
            hotWaterPlant.setName("Hot Water Loop" + str(HVACCount))
        hotWaterPlant.setMaximumLoopTemperature(100)
        hotWaterPlant.setMinimumLoopTemperature(0)
        loopSizing = hotWaterPlant.sizingPlant()
        loopSizing.setLoopType("Heating")
        loopSizing.setDesignLoopExitTemperature(82)  
        loopSizing.setLoopDesignTemperatureDifference(11)
        # create a pump
        if heatingDetails != None and heatingDetails.pumpMotorEfficiency != 'Default':
            pEfficiency = heatingDetails.pumpMotorEfficiency
        else:
            pEfficiency = 0.9
        pump = self.createDefaultAEDGPump(model, pEfficiency)
        # create a boiler
        boiler = ops.BoilerHotWater(model)
        if heatingDetails != None and heatingDetails.heatingEffOrCOP != 'Default':
            boiler.setNominalThermalEfficiency(heatingDetails.heatingEffOrCOP)
        else:
            boiler.setNominalThermalEfficiency(0.9)
        
        # create a scheduled setpoint manager
        setpointManagerScheduled = ops.SetpointManagerScheduled(model,hotWaterSetpointSchedule)
        # create pipes
        pipeSupplyBypass = ops.PipeAdiabatic(model)
        pipeSupplyOutlet = ops.PipeAdiabatic(model)
        pipeDemandBypass = ops.PipeAdiabatic(model)
        pipeDemandInlet = ops.PipeAdiabatic(model)
        pipeDemandOutlet = ops.PipeAdiabatic(model)
        # connect components to plant loop
        # supply side components
        hotWaterPlant.addSupplyBranchForComponent(boiler)
        hotWaterPlant.addSupplyBranchForComponent(pipeSupplyBypass)
        pump.addToNode(hotWaterPlant.supplyInletNode())
        pipeSupplyOutlet.addToNode(hotWaterPlant.supplyOutletNode())
        setpointManagerScheduled.addToNode(hotWaterPlant.supplyOutletNode())
        # demand side components (water coils are added as they are added to airloops and zoneHVAC)
        hotWaterPlant.addDemandBranchForComponent(pipeDemandBypass)
        pipeDemandInlet.addToNode(hotWaterPlant.demandInletNode())
        pipeDemandOutlet.addToNode(hotWaterPlant.demandOutletNode())
        
        # pass back hot water plant
        return hotWaterPlant
    
    def createChilledWaterPlant(self, model, chilledWaterSetpointSchedule, coolingDetails, HVACCount, chillerType, radLoop = False):
        chilleWaterPlant = ops.PlantLoop(model)
        if radLoop == True:
            chilleWaterPlant.setName("Chilled Water Radiant Loop" + str(HVACCount))
        else:
            chilleWaterPlant.setName("Chilled Water Loop" + str(HVACCount))
        chilleWaterPlant.setMaximumLoopTemperature(98)
        chilleWaterPlant.setMinimumLoopTemperature(1)
        loopSizing = chilleWaterPlant.sizingPlant()
        loopSizing.setLoopType("Cooling")
        loopSizing.setDesignLoopExitTemperature(6.7)  
        loopSizing.setLoopDesignTemperatureDifference(6.7)
        # create a pump
        if coolingDetails != None and coolingDetails.pumpMotorEfficiency != 'Default':
            pEfficiency = coolingDetails.pumpMotorEfficiency
        else:
            pEfficiency = 0.9
        pump = self.createDefaultAEDGPump(model, pEfficiency)
        # create a chiller
        if chillerType == "WaterCooled":
            chiller = self.createDefaultAEDGWaterChiller(model, coolingDetails)
        elif chillerType == "AirCooled":
            chiller = self.createDefaultAEDGAirChiller(model, coolingDetails)
        # create a scheduled setpoint manager
        setpointManagerScheduled = ops.SetpointManagerScheduled(model, chilledWaterSetpointSchedule)
        # create pipes
        pipeSupplyBypass = ops.PipeAdiabatic(model)
        pipeSupplyOutlet = ops.PipeAdiabatic(model)
        pipeDemandBypass = ops.PipeAdiabatic(model)
        pipeDemandInlet = ops.PipeAdiabatic(model)
        pipeDemandOutlet = ops.PipeAdiabatic(model)
        # connect components to plant loop
        # supply side components
        chilleWaterPlant.addSupplyBranchForComponent(chiller)
        chilleWaterPlant.addSupplyBranchForComponent(pipeSupplyBypass)
        pump.addToNode(chilleWaterPlant.supplyInletNode())
        pipeSupplyOutlet.addToNode(chilleWaterPlant.supplyOutletNode())
        setpointManagerScheduled.addToNode(chilleWaterPlant.supplyOutletNode())
        # demand side components (water coils are added as they are added to airloops and ZoneHVAC)
        chilleWaterPlant.addDemandBranchForComponent(pipeDemandBypass)
        pipeDemandInlet.addToNode(chilleWaterPlant.demandInletNode())
        pipeDemandOutlet.addToNode(chilleWaterPlant.demandOutletNode())
        
        # pass back chilled water plant
        return chilleWaterPlant
    
    def createCondenser(self, model, chillerWaterPlant, HVACCount):
        # create condenser loop for water-cooled chiller(s)
        condenserLoop = ops.PlantLoop(model)
        condenserLoop.setName("AEDG Condenser Loop"  + str(HVACCount))
        condenserLoop.setMaximumLoopTemperature(80)
        condenserLoop.setMinimumLoopTemperature(5)
        loopSizing = condenserLoop.sizingPlant()
        loopSizing.setLoopType("Condenser")
        loopSizing.setDesignLoopExitTemperature(29.4)
        loopSizing.setLoopDesignTemperatureDifference(5.6)
        # create a pump
        pump = self.createDefaultAEDGPump(model, 0.9, pressRise=134508)
        # create a cooling tower
        tower = ops.CoolingTowerVariableSpeed(model)
        # create pipes
        pipeSupplyBypass = ops.PipeAdiabatic(model)
        pipeSupplyOutlet = ops.PipeAdiabatic(model)
        pipeDemandBypass = ops.PipeAdiabatic(model)
        pipeDemandInlet = ops.PipeAdiabatic(model)
        pipeDemandOutlet = ops.PipeAdiabatic(model)
        # create a setpoint manager
        setpointManagerFollowOA = ops.SetpointManagerFollowOutdoorAirTemperature(model)
        setpointManagerFollowOA.setOffsetTemperatureDifference(0)
        setpointManagerFollowOA.setMaximumSetpointTemperature(80)
        setpointManagerFollowOA.setMinimumSetpointTemperature(5)
        # connect components to plant loop
        # supply side components
        condenserLoop.addSupplyBranchForComponent(tower)
        condenserLoop.addSupplyBranchForComponent(pipeSupplyBypass)
        pump.addToNode(condenserLoop.supplyInletNode())
        pipeSupplyOutlet.addToNode(condenserLoop.supplyOutletNode())
        setpointManagerFollowOA.addToNode(condenserLoop.supplyOutletNode())
        # demand side components
        chillervec = chillerWaterPlant.supplyComponents(ops.IddObjectType("OS:Chiller:Electric:EIR"))
        chiller = model.getChillerElectricEIR(chillervec[0].handle()).get()
        condenserLoop.addDemandBranchForComponent(chiller)
        condenserLoop.addDemandBranchForComponent(pipeDemandBypass)
        pipeDemandInlet.addToNode(condenserLoop.demandInletNode())
        pipeDemandOutlet.addToNode(condenserLoop.demandOutletNode())
        return condenserLoop
    
    def setDemandVent(self, model, airloop):
        oasys = airloop.airLoopHVACOutdoorAirSystem()
        oactrl = oasys.get().getControllerOutdoorAir()
        controllerMv = oactrl.controllerMechanicalVentilation()
        controllerMv.setDemandControlledVentilation(True)
    
    def setOutdoorAirReq(self, airTerminal, zone):
        space = zone.spaces()[0]
        oaReq = space.designSpecificationOutdoorAir()
        airTerminal.setControlForOutdoorAir(oaReq)
    
    def createPrimaryAirLoop(self, airType, model, thermalZones, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hotWaterPlant=None, chilledWaterPlant=None, terminalOption=None, heatRecovOverride = False):
        # Create the air loop.
        airloopPrimary = ops.AirLoopHVAC(model)
        if airType == 'DOAS':
            airloopPrimary.setName("DOAS Air Loop HVAC" + str(HVACCount))
        else:
            airloopPrimary.setName("VAV Air Loop HVAC" + str(HVACCount))
        
        # Modify hard sizing
        if airDetails != None and airDetails.airSysHardSize != 'Default':
            airloopPrimary.setDesignSupplyAirFlowRate(float(airDetails.airSysHardSize))
        
        # modify system sizing properties
        sizingSystem = airloopPrimary.sizingSystem()
        # set central heating and cooling temperatures for sizing
        sizingSystem.setCentralCoolingDesignSupplyAirTemperature(12.8)
        sizingSystem.setCentralHeatingDesignSupplyAirTemperature(40) #ML OS default is 16.7
        
        # load specification
        if airType == 'DOAS':
            sizingSystem.setTypeofLoadtoSizeOn("VentilationRequirement") #DOAS
            sizingSystem.setAllOutdoorAirinCooling(True) #DOAS
            sizingSystem.setAllOutdoorAirinHeating(True) #DOAS
        else:
            sizingSystem.setTypeofLoadtoSizeOn("Sensible") #VAV
            sizingSystem.setAllOutdoorAirinCooling(False) #VAV
            sizingSystem.setAllOutdoorAirinHeating(False) #VAV
        
        airLoopComps = []
        # set availability schedule
        if airDetails != None and airDetails.HVACAvailabiltySched != 'ALWAYS ON':
            hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched, model)
            airloopPrimary.setAvailabilitySchedule(hvacAvailSch)
        else:
            airloopPrimary.setAvailabilitySchedule(model.alwaysOnDiscreteSchedule())
        
        # Check if there are any ventilation schedules on the zones.
        ventSchedTrigger = False
        recircTrigger = False
        for zone in hbZones:
            if zone.ventilationSched != '':
                ventSchedTrigger = True
            if zone.recirculatedAirPerArea != 0:
                recircTrigger = True
        
        # constant or variable speed fan
        sizingSystem.setMinimumSystemAirFlowRatio(1.0) #DCV
        if airType == 'VAV':
            fan = self.createDefaultAEDGFan('VV', model, airDetails)
        elif airDetails != None and airDetails.fanControl == 'Variable Volume':
            fan = self.createDefaultAEDGFan('VV', model, airDetails)
        elif airDetails != None and airDetails.airsideEconomizer != 'Default' and airDetails.airsideEconomizer != 'NoEconomizer':
            fan = self.createDefaultAEDGFan('VV', model, airDetails)
        elif ventSchedTrigger == True or recircTrigger == True:
            fan = self.createDefaultAEDGFan('VV', model, airDetails)
        else:
            fan = self.createDefaultAEDGFan('CV', model, airDetails)
        airLoopComps.append(fan)
        
        # create heating coil
        if hotWaterPlant != None:
            heatingCoil = ops.CoilHeatingWater(model, model.alwaysOnDiscreteSchedule())
        else:
            heatingCoil = ops.CoilHeatingGas(model, model.alwaysOnDiscreteSchedule())
        if heatingDetails != None and heatingDetails.heatingAvailSched != 'ALWAYS ON':
             heatAvailSch = self.getOSSchedule(heatingDetails.heatingAvailSched,model)
             heatingCoil.setAvailabilitySchedule(heatAvailSch)
        
        airLoopComps.append(heatingCoil)
        # create cooling coil
        if chilledWaterPlant != None:
            coolingCoil = ops.CoilCoolingWater(model, model.alwaysOnDiscreteSchedule())
            if coolingDetails != None and coolingDetails.coolingAvailSched != 'ALWAYS ON':
                 coolAvailSch = self.getOSSchedule(coolingDetails.coolingAvailSched, model)
                 coolingCoil.setAvailabilitySchedule(coolAvailSch)
            if coolingDetails != None and coolingDetails.supplyTemperature != 'Default':
                coolingCoil.setDesignInletWaterTemperature(coolingDetails.supplyTemperature)
            airLoopComps.append(coolingCoil)
        else:
            coolingCoil = ops.CoilCoolingDXSingleSpeed(model)
            coolingCoil.setRatedCOP(ops.OptionalDouble(4.0))
            if coolingDetails != None and coolingDetails.coolingAvailSched != 'ALWAYS ON':
                 coolAvailSch = self.getOSSchedule(coolingDetails.coolingAvailSched, model)
                 coolingCoil.setAvailabilitySchedule(coolAvailSch)
            airLoopComps.append(coolingCoil)
        
        # create controller outdoor air
        controllerOA = ops.ControllerOutdoorAir(model)
        controllerOA.autosizeMinimumOutdoorAirFlowRate()
        controllerOA.autosizeMaximumOutdoorAirFlowRate()
        controllerOA.setHeatRecoveryBypassControlType("BypassWhenOAFlowGreaterThanMinimum")
        if airType == 'VAV':
            controllerOA.setEconomizerControlType('DifferentialEnthalpy')
        # create outdoor air system
        systemOA = ops.AirLoopHVACOutdoorAirSystem(model, controllerOA)
        airLoopComps.append(systemOA)
        
        # create scheduled setpoint manager for airloop
        # DOAS or VAV for cooling and not ventilation
        if airType == 'VAV':
            setpointManager = ops.SetpointManagerOutdoorAirReset(model)
            setpointManager.setOutdoorLowTemperature(14.4)
            setpointManager.setOutdoorHighTemperature(21.1)
            if airDetails!= None and airDetails.heatingSupplyAirTemp != 'Default':
                setpointManager.setSetpointatOutdoorLowTemperature(airDetails.heatingSupplyAirTemp)
            else:
                setpointManager.setSetpointatOutdoorLowTemperature(15.6)
            if airDetails!= None and airDetails.coolingSupplyAirTemp != 'Default':
                setpointManager.setSetpointatOutdoorHighTemperature(airDetails.coolingSupplyAirTemp)
            else:
                setpointManager.setSetpointatOutdoorHighTemperature(12.8)
        else:
            if airDetails!= None and airDetails.heatingSupplyAirTemp != 'Default':
                suppTemp = airDetails.heatingSupplyAirTemp
            elif airDetails!= None and airDetails.coolingSupplyAirTemp != 'Default':
                suppTemp = airDetails.coolingSupplyAirTemp
            else:
                suppTemp = 20
            setpointSchedule = self.createConstantScheduleRuleset('DOAS_Temperature_Setpoint' + str(HVACCount), 'DOAS_Temperature_Setpoint_Default' + str(HVACCount), 'TEMPERATURE', suppTemp, model)
            setpointManager = ops.SetpointManagerScheduled(model, setpointSchedule)
        
        # connect components to airloop
        # find the supply inlet node of the airloop
        airloopSupplyInlet = airloopPrimary.supplyInletNode()
        # add the components to the airloop
        for count, comp in enumerate(airLoopComps):
          comp.addToNode(airloopSupplyInlet)
          if count == 1 and hotWaterPlant != None:
            hotWaterPlant.addDemandBranchForComponent(comp)
            comp.controllerWaterCoil().get().setMinimumActuatedFlow(0)
          elif count == 2 and chilledWaterPlant != None:
            chilledWaterPlant.addDemandBranchForComponent(comp)
            comp.controllerWaterCoil().get().setMinimumActuatedFlow(0)
        
        # Add airside economizer if requested
        if airDetails != None and airDetails.airsideEconomizer != 'Default':
            self.adjustAirSideEcon(airloopPrimary, airDetails)
        
        # add erv to outdoor air system either based on user input or add the default AEDG erv.
        if airDetails != None and airDetails.heatRecovery != 'Default' and airDetails.heatRecovery != 'None':
            self.addHeatRecovToModel(model, airloopPrimary, airDetails.heatRecovery, airDetails.recoveryEffectiveness, False, True)
        elif heatRecovOverride == False:
            self.addHeatRecovToModel(model, airloopPrimary, 'Enthalpy', 0.75, False, True, 0.69)
        
        # add setpoint manager to supply equipment outlet node
        setpointManager.addToNode(airloopPrimary.supplyOutletNode())
        
        # add thermal zones to airloop.
        recircAirFlowRates = []
        for zCount, zone in enumerate(thermalZones):
            zoneTotAir = self.getZoneTotalAir(hbZones[zCount])
            recircAirFlowRates.append(zoneTotAir)
            # make an air terminal for the zone
            airTerminal = None
            if terminalOption == "ChilledBeam":
                # create cooling coil
                coolingCoil = ops.CoilCoolingCooledBeam(model)
                chilledWaterPlant.addDemandBranchForComponent(coolingCoil)
                airTerminal = ops.AirTerminalSingleDuctConstantVolumeCooledBeam(model, model.alwaysOnDiscreteSchedule(), coolingCoil)
                airTerminal.setCooledBeamType('Active')
                if coolingDetails != None and coolingDetails.coolingAvailSched != 'ALWAYS ON':
                     coolAvailSch = self.getOSSchedule(coolingDetails.coolingAvailSched, model)
                     airTerminal.setAvailabilitySchedule(coolAvailSch)
            else:
                if ventSchedTrigger == True:
                    airTerminal = ops.AirTerminalSingleDuctVAVNoReheat(model, model.alwaysOnDiscreteSchedule())
                    self.setOutdoorAirReq(airTerminal, zone)
                elif airType == 'VAV':
                    airTerminal = ops.AirTerminalSingleDuctVAVNoReheat(model, model.alwaysOnDiscreteSchedule())
                elif airDetails != None and airDetails.fanControl == 'Variable Volume':
                    airTerminal = ops.AirTerminalSingleDuctVAVNoReheat(model, model.alwaysOnDiscreteSchedule())
                elif airDetails != None and airDetails.airsideEconomizer != 'Default' and airDetails.airsideEconomizer != 'NoEconomizer':
                    airTerminal = ops.AirTerminalSingleDuctVAVNoReheat(model, model.alwaysOnDiscreteSchedule())
                elif hbZones[zCount].recirculatedAirPerArea == 0:
                    airTerminal = ops.AirTerminalSingleDuctUncontrolled(model, model.alwaysOnDiscreteSchedule())
                else:
                    airTerminal = ops.AirTerminalSingleDuctVAVNoReheat(model, model.alwaysOnDiscreteSchedule())
            if hbZones[zCount].recirculatedAirPerArea != 0 and terminalOption != "ChilledBeam":
                self.sizeAirTerminalForRecirc(model, hbZones[zCount], airTerminal, zoneTotAir)
            elif hbZones[zCount].recirculatedAirPerArea != 0:
                airTerminal.setSupplyAirVolumetricFlowRate(zoneTotAir)
            elif recircTrigger == True:
                try:
                    airTerminal.setZoneMinimumAirFlowInputMethod('Constant')
                    airTerminal.autosizeMaximumAirFlowRate()
                    airTerminal.resetMinimumAirFlowFractionSchedule()
                except:
                    airTerminal.autosizeSupplyAirVolumetricFlowRate()
            
            # attach new terminal to the zone and to the airloop
            airloopPrimary.addBranchForZone(zone, airTerminal.to_StraightComponent())
        
        
        if airDetails != None and airDetails.fanControl == 'Variable Volume':
            self.setDemandVent(model, airloopPrimary)
        else:
            # create ventilation schedules and assign to OA controller for DOAS
            controllerOA.setMinimumFractionofOutdoorAirSchedule(model.alwaysOnDiscreteSchedule())
            controllerOA.setMaximumFractionofOutdoorAirSchedule(model.alwaysOnDiscreteSchedule())
        
        # Size fan for recirc if needed.
        if recircTrigger == True:
            self.sizeVAVFanForRecirc(model, airloopPrimary, recircAirFlowRates)
        
        return airloopPrimary
    
    def createVRFSystem(self, model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount):
        vrfAirConditioner = ops.AirConditionerVariableRefrigerantFlow(model)
        vrfAirConditioner.setZoneforMasterThermostatLocation(thermalZoneVector[0])
        vrfAirConditioner.setName("VRF Heat Pump - " + str(HVACCount))
        
        # Set the COP.
        if coolingDetails != None and coolingDetails.coolingCOP != 'Default':
            vrfAirConditioner.setRatedCoolingCOP(coolingDetails.coolingCOP)
        if heatingDetails != None and heatingDetails.heatingEffOrCOP != 'Default':
            vrfAirConditioner.setRatedHeatingCOP(heatingDetails.heatingEffOrCOP)
        
        if airDetails != None and airDetails.heatRecovery != 'Default' and airDetails.heatRecovery != 'None':
            vrfAirConditioner.setHeatPumpWasteHeatRecovery(True)
        else:
            vrfAirConditioner.setHeatPumpWasteHeatRecovery(False)
        
        vrfAirConditioner.setAvailabilitySchedule(model.alwaysOnDiscreteSchedule())
        if heatingDetails != None and heatingDetails.heatingAvailSched != "ALWAYS ON":
            heatAvailSch = self.getOSSchedule(heatingDetails.heatingAvailSched, model)
            vrfAirConditioner.setAvailabilitySchedule(heatAvailSch)
        if coolingDetails != None and coolingDetails.coolingAvailSched != "ALWAYS ON":
            coolAvailSch = self.getOSSchedule(coolingDetails.coolinggAvailSched, model)
            vrfAirConditioner.setAvailabilitySchedule(coolAvailSch)
        
        if coolingDetails != None and coolingDetails.chillerType == "WaterCooled":
            vrfAirConditioner.setString(56,"WaterCooled")
            cndwl = self.createCondenser(model, cwl, "VRF - " + str(HVACCount))
            cndwl.addDemandBranchForComponent(vrfAirConditioner)
        
        for zone in thermalZoneVector:
            # construct Terminal VRF Unit
            vrfTerminalUnit = ops.ZoneHVACTerminalUnitVariableRefrigerantFlow(model)		
            vrfTerminalUnit.setTerminalUnitAvailabilityschedule(model.alwaysOnDiscreteSchedule())
            vrfTerminalUnit.setOutdoorAirFlowRateDuringCoolingOperation(0)
            vrfTerminalUnit.setOutdoorAirFlowRateDuringHeatingOperation(0)
            vrfTerminalUnit.setOutdoorAirFlowRateWhenNoCoolingorHeatingisNeeded(0)
            vrfTerminalUnit.addToThermalZone(zone)
            vrfAirConditioner.addTerminal(vrfTerminalUnit)
    
    
    def createZoneEquip(self, model, thermalZones, hbZones, equipList, hotWaterPlant=None, chilledWaterPlant=None, heatOnly=False):
        radiantFloor = None
        if 'RadiantFloor' in equipList:
            # create radiant floor construction and substitute for existing floor (interior or exterior) constructions
            # create materials for radiant floor construction
            # ignore layer below insulation, which will depend on boundary condition
            insul = ops.StandardOpaqueMaterial(model,"Rough",0.0254,0.02,56.06,1210) # rigid_insulation_1in
            conc = ops.StandardOpaqueMaterial(model,"MediumRough",0.0508,2.31,2322,832) # concrete_2in
            layers= [insul, conc, conc]
            # create an empty vector to collect the materials
            materials = ops.MaterialVector()
            for OSMaterial in layers:
                # add it as a layer
                materials.Add(OSMaterial)
            radiantFloor = ops.ConstructionWithInternalSource(model)
            radiantFloor.setName('4in Radiant Slab Construction')
            radiantFloor.setLayers(materials)
            radiantFloor.setSourcePresentAfterLayerNumber(2)
            radiantFloor.setSourcePresentAfterLayerNumber(2)
        
        for zoneCount, zone in enumerate(thermalZones):
            if 'FanCoil' in equipList:
                # create fan coil
                # create fan
                fan = ops.FanOnOff(model, model.alwaysOnDiscreteSchedule())
                fan.setFanEfficiency(0.5)
                fan.setPressureRise(75) #Pa
                fan.autosizeMaximumFlowRate()
                fan.setMotorEfficiency(0.9)
                fan.setMotorInAirstreamFraction(1.0)
                # create cooling coil and connect to chilled water plant
                coolingCoil = ops.CoilCoolingWater(model, model.alwaysOnDiscreteSchedule())
                chilledWaterPlant.addDemandBranchForComponent(coolingCoil)
                coolingCoil.controllerWaterCoil().get().setMinimumActuatedFlow(0)
                # create heating coil and connect to hot water plant
                heatingCoil = ops.CoilHeatingWater(model, model.alwaysOnDiscreteSchedule())
                hotWaterPlant.addDemandBranchForComponent(heatingCoil)
                heatingCoil.controllerWaterCoil().get().setMinimumActuatedFlow(0)
                # construct fan coil
                fanCoil = ops.ZoneHVACFourPipeFanCoil(model, model.alwaysOnDiscreteSchedule(), fan, coolingCoil, heatingCoil)
                fanCoil.setMaximumOutdoorAirFlowRate(0)                                                          
                # add fan coil to thermal zone
                fanCoil.addToThermalZone(zone)
            elif "Baseboard" in equipList:
                # create baseboard heater add add to thermal zone and hot water loop
                baseboardCoil = ops.CoilHeatingWaterBaseboard(model)
                baseboardHeater = ops.ZoneHVACBaseboardConvectiveWater(model, model.alwaysOnDiscreteSchedule(), baseboardCoil)
                baseboardHeater.addToThermalZone(zone)          
                hotWaterPlant.addDemandBranchForComponent(baseboardCoil)
            elif 'RadiantFloor' in equipList:
                # create hot water coil and attach to radiant hot water loop
                heatingCoil = ops.CoilHeatingLowTempRadiantVarFlow(model, model.alwaysOnDiscreteSchedule())
                heatSetPtSch = self.getOSSchedule(hbZones[zoneCount].heatingSetPtSchedule, model)
                heatingCoil.setHeatingControlTemperatureSchedule(heatSetPtSch)
                hotWaterPlant.addDemandBranchForComponent(heatingCoil)
                # create chilled water coil and attach to radiant chilled water loop
                coolingCoil = ops.CoilCoolingLowTempRadiantVarFlow(model, model.alwaysOnDiscreteSchedule())
                coolSetPtSch = self.getOSSchedule(hbZones[zoneCount].coolingSetPtSchedule, model)
                coolingCoil.setCoolingControlTemperatureSchedule(coolSetPtSch)
                chilledWaterPlant.addDemandBranchForComponent(coolingCoil)
                if heatOnly == True:
                    coolingCoil.setMaximumColdWaterFlow(0)
                # create the hydronic system
                lowTempRadiant = ops.ZoneHVACLowTempRadiantVarFlow(model, model.alwaysOnDiscreteSchedule(), heatingCoil, coolingCoil)
                lowTempRadiant.setRadiantSurfaceType("Floors")
                lowTempRadiant.setHydronicTubingInsideDiameter(0.012)
                lowTempRadiant.setTemperatureControlType("MeanRadiantTemperature")
                
                lowTempRadiant.addToThermalZone(zone)
                # assign radiant construction to zone floor
                space = zone.spaces()[0]
                for surface in space.surfaces:
                    if surface.surfaceType() == "Floor":
                        surface.setConstruction(radiantFloor)
    
    ### END OF FUNCTIONS FOR CREATING HVAC SYSTEMS FROM SCRATCH ###
    
    ### START OF FUNCTIONS FOR EDITING HVAC SYSTEMS ###
    def updateFan(self,fan,totalEfficiency,motorEfficiency,pressureRise,airSysHardSize):
        if totalEfficiency != 'Default': 
            fan.setFanEfficiency(totalEfficiency)
        if motorEfficiency != 'Default':
            fan.setMotorEfficiency(motorEfficiency)
        if pressureRise != 'Default': 
            fan.setPressureRise(pressureRise)
        if airSysHardSize != 'Default':
            fan.setMaximumFlowRate(float(airSysHardSize))
    
    def updatePump(self, pump, pumpMotorEfficiency):
        if pumpMotorEfficiency != 'Default':
            pump.setMotorEfficiency(pumpMotorEfficiency)
    
    def updateChiller(self, model, osChiller, coolingCOP, supplyTemperature):
        if coolingCOP != 'Default':
            osChiller.setReferenceCOP(coolingCOP)
        if supplyTemperature != 'Default':
            osChiller.setReferenceLeavingChilledWaterTemperature(supplyTemperature)
   
    def updateBoiler(self, model, osboiler, heatingEffOrCOP, supplyTemperature):
        if heatingEffOrCOP != 'Default':
            osboiler.setNominalThermalEfficiency(heatingEffOrCOP)
        if supplyTemperature != 'Default':
            osboiler.setDesignWaterOutletTemperature(supplyTemperature)
    
    def updateDXCoolingCoil(self, model, coolCoil, coolingAvailSched, coolingCOP):
        if coolingAvailSched != 'ALWAYS ON':
             coolAvailSch = self.getOSSchedule(coolingAvailSched, model)
             coolCoil.setAvailabilitySchedule(coolAvailSch)
        if coolingCOP != 'Default':
            coolCoil.setRatedCOP(ops.OptionalDouble(coolingCOP))
    
    def updateDXCoolingCoilTwoSpeed(self, model, coolCoil, coolingAvailSched, coolingCOP):
        if coolingAvailSched != 'ALWAYS ON':
             coolAvailSch = self.getOSSchedule(coolingAvailSched, model)
             coolCoil.setAvailabilitySchedule(coolAvailSch)
        if coolingCOP != 'Default':
            coolCoil.setRatedHighSpeedCOP(coolingCOP)
            coolCoil.setRatedLowSpeedCOP(coolingCOP)
    
    def updateWaterCoolingCoil(delf, model, coolCoil, coolingAvailSched, supplyTemperature):
        if coolingAvailSched != 'ALWAYS ON':
             coolAvailSch = self.getOSSchedule(coolingAvailSched,model)
             coolCoil.setAvailabilitySchedule(coolAvailSch)
        if supplyTemperature != 'Default':
            coolCoil.setDesignInletWaterTemperature(supplyTemperature)
    
    def updateDXHeatingCoil(self, model, heatCoil, heatingAvailSched, heatingEffOrCOP):
        if heatingAvailSched != 'ALWAYS ON':
             heatAvailSch = self.getOSSchedule(heatingAvailSched, model)
             heatCoil.setAvailabilitySchedule(heatAvailSch)
        if heatingEffOrCOP != 'Default':
            heatCoil.setRatedCOP(heatingEffOrCOP)
    
    def updateGasHeatingCoil(self, model, heatCoil, heatingAvailSched, heatingEffOrCOP):
        if heatingAvailSched != 'ALWAYS ON':
             heatAvailSch = self.getOSSchedule(heatingAvailSched, model)
             heatCoil.setAvailabilitySchedule(heatAvailSch)
        if heatingEffOrCOP != 'Default':
            heatCoil.setGasBurnerEfficiency(heatingEffOrCOP)
    
    def updateElectricHeatingCoil(self, model, heatCoil, heatingAvailSched, heatingEffOrCOP):
        if heatingAvailSched != 'ALWAYS ON':
             heatAvailSch = self.getOSSchedule(heatingAvailSched, model)
             heatCoil.setAvailabilitySchedule(heatAvailSch)
        if heatingEffOrCOP != 'Default':
            heatCoil.setEfficiency(heatingEffOrCOP)
    
    def updateWaterHeatingCoil(self, model, heatcoil, heatingAvailSched, supplyTemperature):
        if heatingAvailSched != 'ALWAYS ON':
             heatAvailSch = self.getOSSchedule(heatingAvailSched,model)
             heatcoil.setAvailabilitySchedule(heatAvailSch)
    
    def getZoneTotalAir(self, hbZone):
        zoneFlrArea = hbZone.getFloorArea()
        totalZoneFlow = (hbZone.recirculatedAirPerArea*zoneFlrArea) +  (hbZone.ventilationPerArea*zoneFlrArea) + (hbZone.ventilationPerPerson*hbZone.numOfPeoplePerArea*zoneFlrArea)
        return totalZoneFlow
    
    def setRecircOnSingleZoneSys(self, hbZone, system, fan):
        totalZoneFlow = self.getZoneTotalAir(hbZone)
        system.setSupplyAirFlowRateDuringCoolingOperation(totalZoneFlow)
        system.setSupplyAirFlowRateDuringHeatingOperation(totalZoneFlow)
        system.setSupplyAirFlowRateWhenNoCoolingorHeatingisNeeded(totalZoneFlow)
        fan.setMaximumFlowRate(totalZoneFlow)
    
    def sizeAirTerminalForRecirc(self, model, HBZone, vavBox, zoneTotAir):
        if HBZone.ventilationSched != '':
            try:
                vavBox.setZoneMinimumAirFlowMethod('Scheduled')
            except:
                vavBox.setZoneMinimumAirFlowInputMethod('Scheduled')
            vavBox.setMaximumAirFlowRate(zoneTotAir)
            minVentSch = self.getOSSchedule(HBZone.ventilationSched,model)
            vavBox.setMinimumAirFlowFractionSchedule(minVentSch)
        else:
            try:
                vavBox.setZoneMinimumAirFlowMethod('FixedFlowRate')
            except:
                vavBox.setZoneMinimumAirFlowInputMethod('FixedFlowRate')
            vavBox.setFixedMinimumAirFlowRate(zoneTotAir)
            vavBox.setMaximumAirFlowRate(2*zoneTotAir)
    
    def sizeVAVFanForRecirc(self, model, airloop, recircAirFlowRates):
        fullHVACAirFlow = sum(recircAirFlowRates)
        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
        vvfan = model.getFanVariableVolume(x[0].handle()).get()
        vvfan.setMaximumFlowRate(fullHVACAirFlow*2)
    
    def applyVentilationSched(self, model, HBZone, vavBox, zoneTotAir):
        vavBox.setZoneMinimumAirFlowMethod('Scheduled')
        vavBox.setMaximumAirFlowRate(zoneTotAir)
        minVentSch = self.getOSSchedule(HBZone.ventilationSched,model)
        vavBox.setMinimumAirFlowFractionSchedule(minVentSch)
    
    def addDehumidController(self, model, airloop):
        # Add a humidity set point controller into the air loop.
        humidController = ops.SetpointManagerMultiZoneHumidityMaximum(model)
        humidController.setMinimumSetpointHumidityRatio(0.001)
        setPNode = airloop.supplyOutletNode()
        # I should be using the controller sensor node but trying to call it causes Rhino to crash.
        #For now, I am just using the supply outlet node, which works well aside from an error that E+ gives us.
        #setPNode = ccontroller.sensorNode().get()
        humidController.addToNode(setPNode)
        return setPNode
    
    def addChilledWaterDehumid(self, model, airloop):
        # Set the cooling coil to control humidity. 
        x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:Water"))
        cc = model.getCoilCoolingWater(x[0].handle()).get()
        ccontroller = cc.controllerWaterCoil().get()
        ccontroller.setControlVariable('TemperatureAndHumidityRatio')
        sensorNode = self.addDehumidController(model, airloop)
        ccontroller.setSensorNode(sensorNode)
    
    def addHumidifierController(self, model, airloop):
        # Add a humidity set point controller into the air loop.
        humidController = ops.SetpointManagerMultiZoneHumidityMinimum(model)
        setPNode = airloop.supplyOutletNode()
        humidController.addToNode(setPNode)
        return setPNode
    
    def addElectricHumidifier(self, model, airloop):
        humidifier = ops.HumidifierSteamElectric(model)
        supplyNode = airloop.supplyOutletNode()
        humidifier.addToNode(supplyNode)
        self.addHumidifierController(model, airloop)
    
    def addHeatRecovToModel(self, model, airloop, heatRecovery, recoveryEffectiveness, econLockout=False, aedgRecov=False, latentEff=None):
        # Create an air-to-air heat exchanger.
        heatEx = ops.HeatExchangerAirToAirSensibleAndLatent(model)
        #Set how the economizer interacts with the heat recovery.
        heatEx.setEconomizerLockout(econLockout)
        # Change the properties of the heat exchanger based on the inputs.
        if heatRecovery == 'Sensible':
            heatEx.setLatentEffectivenessat100CoolingAirFlow(0)
            heatEx.setLatentEffectivenessat100HeatingAirFlow(0)
            heatEx.setLatentEffectivenessat75CoolingAirFlow(0)
            heatEx.setLatentEffectivenessat75HeatingAirFlow(0)
        if recoveryEffectiveness != 'Default':
            heatEx.setSensibleEffectivenessat100CoolingAirFlow(recoveryEffectiveness)
            heatEx.setSensibleEffectivenessat100HeatingAirFlow(recoveryEffectiveness)
            heatEx.setSensibleEffectivenessat75CoolingAirFlow(recoveryEffectiveness)
            heatEx.setSensibleEffectivenessat75HeatingAirFlow(recoveryEffectiveness)
            if heatRecovery != 'Sensible':
                if latentEff == None:
                    heatEx.setLatentEffectivenessat100CoolingAirFlow(recoveryEffectiveness)
                    heatEx.setLatentEffectivenessat100HeatingAirFlow(recoveryEffectiveness)
                    heatEx.setLatentEffectivenessat75CoolingAirFlow(recoveryEffectiveness)
                    heatEx.setLatentEffectivenessat75HeatingAirFlow(recoveryEffectiveness)
                else:
                    heatEx.setLatentEffectivenessat100CoolingAirFlow(latentEff)
                    heatEx.setLatentEffectivenessat100HeatingAirFlow(latentEff)
                    heatEx.setLatentEffectivenessat75CoolingAirFlow(latentEff)
                    heatEx.setLatentEffectivenessat75HeatingAirFlow(latentEff)
        if aedgRecov == True:
            heatEx.setFrostControlType("ExhaustOnly")
            heatEx.setThresholdTemperature(-12.2)
            heatEx.setInitialDefrostTimeFraction(0.1670)
            heatEx.setRateofDefrostTimeFractionIncrease(0.0240)
        # Add the heat exchanger to the model.
        outdoorNode = airloop.reliefAirNode().get()
        heatEx.addToNode(outdoorNode)
    
    def addDefaultAirsideEcon(self, airloop, dehumidTrigger):
        oasys = airloop.airLoopHVACOutdoorAirSystem()
        oactrl = oasys.get().getControllerOutdoorAir()
        if dehumidTrigger is True:
            oactrl.setEconomizerControlType('DifferentialEnthalpy')
        else:
            oactrl.setEconomizerControlType('DifferentialDryBulb')
    
    def adjustAirSideEcon(self, airloop, airDetails):
        oasys = airloop.airLoopHVACOutdoorAirSystem()
        oactrl = oasys.get().getControllerOutdoorAir()
        oactrl.setEconomizerControlType(airDetails.airsideEconomizer)
    
    def swapCVFanForVV(self, model, airloop, airDetails):
        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
        cvfan = model.getFanConstantVolume(x[0].handle()).get()
        cvfan.remove()
        vvFan = self.createDefaultAEDGFan('VV', model, airDetails)
        supplyAirNode = airloop.supplyOutletNode()
        vvFan.addToNode(supplyAirNode)
    
    def adjustCVAirLoop(self, model, airloop, airDetails):
        econLockout = False
        if airDetails.HVACAvailabiltySched != 'ALWAYS ON':
            hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched, model)
            airloop.setAvailabilitySchedule(hvacAvailSch)
        if airDetails.fanTotalEfficiency != "Default" or airDetails.fanMotorEfficiency != "Default" or airDetails.fanPressureRise != "Default" or airDetails.airSysHardSize != "Default":
            x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
            cvfan = model.getFanConstantVolume(x[0].handle()).get()
            self.updateFan(cvfan,airDetails.fanTotalEfficiency,airDetails.fanMotorEfficiency,airDetails.fanPressureRise,airDetails.airSysHardSize)
        if airDetails.airSysHardSize != "Default":
            airloop.setDesignSupplyAirFlowRate(float(airDetails.airSysHardSize))
        if airDetails.fanPlacement != 'Default':
            if airDetails.fanPlacement == 'Blow Through':
                x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
                cvfan = model.getFanConstantVolume(x[0].handle()).get()
                mixAirNode = airloop.mixedAirNode().get()
                cvfan.addToNode(mixAirNode)
        if airDetails.heatingSupplyAirTemp != 'Default' or airDetails.coolingSupplyAirTemp != 'Default':
            self.updateCVLoopSupplyTemp(airloop, model, airDetails.coolingSupplyAirTemp, airDetails.heatingSupplyAirTemp)
        if airDetails.airsideEconomizer != 'Default':
            if airDetails.airsideEconomizer == 'NoEconomizer':
                econLockout = True
            self.adjustAirSideEcon(airloop, airDetails)
        else:
            self.addDefaultAirsideEcon(airloop, False)
        if airDetails.heatRecovery != 'Default' and airDetails.heatRecovery != 'None':
            self.addHeatRecovToModel(model, airloop, airDetails.heatRecovery, airDetails.recoveryEffectiveness, econLockout)
    
    def adjustVAVAirLoop(self, model, airloop, airDetails, HVACCount, dehumidTrigger, waterCoolCoil=False, fanAdjustable=True):
        econLockout = False
        if airDetails.HVACAvailabiltySched != 'ALWAYS ON':
            hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched, model)
            airloop.setAvailabilitySchedule(hvacAvailSch)
        if airDetails.fanTotalEfficiency != "Default" or airDetails.fanMotorEfficiency != "Default" or airDetails.fanPressureRise != "Default" or airDetails.airSysHardSize != "Default":
            x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
            vvfan = model.getFanVariableVolume(x[0].handle()).get()
            self.updateFan(vvfan,airDetails.fanTotalEfficiency,airDetails.fanMotorEfficiency,airDetails.fanPressureRise,airDetails.airSysHardSize)
        if airDetails.airSysHardSize != "Default":
            airloop.setDesignSupplyAirFlowRate(float(airDetails.airSysHardSize))
        if airDetails.airsideEconomizer != 'Default':
            self.adjustAirSideEcon(airloop, airDetails)
            if airDetails.airsideEconomizer == 'NoEconomizer':
                econLockout = True
        else:
            self.addDefaultAirsideEcon(airloop, dehumidTrigger)
        if airDetails.heatRecovery != 'Default' and airDetails.heatRecovery != 'None':
            self.addHeatRecovToModel(model, airloop, airDetails.heatRecovery, airDetails.recoveryEffectiveness, econLockout)
        if airDetails.fanPlacement != 'Default' and fanAdjustable == True:
            if airDetails.fanPlacement == 'Blow Through':
                x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                vvfan = model.getFanVariableVolume(x[0].handle()).get()
                mixAirNode = airloop.mixedAirNode().get()
                vvfan.addToNode(mixAirNode)
        if airDetails.coolingSupplyAirTemp != 'Default':
            self.updateLoopSupplyTemp(airloop, model, airDetails.coolingSupplyAirTemp, "Deck_Temperature_Default", "Deck_Temp", HVACCount)
            if waterCoolCoil == True:
                # Change the rating on the cooling coil.
                x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:Water"))
                hc = model.getCoilCoolingWater(x[0].handle()).get()
                hc.setDesignOutletAirTemperature(airDetails.coolingSupplyAirTemp)
    
    def adjustWaterReheatCoil(self, model, vavBox, airDetails, heatingDetails):
        if heatingDetails != None:
            if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.supplyTemperature != "Default":
                reheatCoil = vavBox.reheatCoil()
                hc = model.getCoilHeatingWater(reheatCoil.handle()).get()
                self.updateWaterHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.supplyTemperature)
    
    def adjustElectricReheatCoil(self, model, vavBox, heatingDetails):
        if heatingDetails != None:
            if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                reheatCoil = vavBox.reheatCoil()
                hc = model.getCoilHeatingElectric(reheatCoil.handle()).get()
                self.updateElectricHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
    
    def adjustHotWaterLoop(self, model, airloop, heatingDetails, HVACCount):
        if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != "Default" or heatingDetails.supplyTemperature != "Default"  or heatingDetails.pumpMotorEfficiency != "Default":
            x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Water"))
            hc = model.getCoilHeatingWater(x[0].handle()).get()
            hwl = hc.plantLoop().get()
            if heatingDetails.heatingEffOrCOP != "Default" or heatingDetails.supplyTemperature != "Default":
                boilerVec = hwl.supplyComponents(ops.IddObjectType("OS:Boiler:HotWater"))
                for boiler in boilerVec:
                    osBoiler = model.getBoilerHotWater(boiler.handle()).get()
                    self.updateBoiler(model, osBoiler, heatingDetails.heatingEffOrCOP, heatingDetails.supplyTemperature)
            if heatingDetails.pumpMotorEfficiency != "Default":
                pumpVec = hwl.supplyComponents(ops.IddObjectType("OS:Pump:VariableSpeed"))
                for pump in enumerate(pumpVec):
                    osPump = model.getPumpVariableSpeed(pump[1].handle()).get()
                    self.updatePump(osPump, heatingDetails.pumpMotorEfficiency)
            if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.supplyTemperature != "Default":
                self.updateWaterHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.supplyTemperature)
            if heatingDetails.supplyTemperature != "Default":
                self.updateLoopSupplyTemp(hwl, model, heatingDetails.supplyTemperature, "Hot_Water_Temperature_Default", "Hot_Water_Temp", HVACCount)
    
    def adjustChilledWaterLoop(self, model, airloop, coolingDetails, HVACCount):
        if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default" or coolingDetails.supplyTemperature != "Default"  or coolingDetails.pumpMotorEfficiency != "Default":
            x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:Water"))
            cc = model.getCoilCoolingWater(x[0].handle()).get()
            cwl = cc.plantLoop().get()
            if coolingDetails.coolingCOP != "Default" or coolingDetails.supplyTemperature != "Default":
                chillervec = cwl.supplyComponents(ops.IddObjectType("OS:Chiller:Electric:EIR"))
                for chiller in chillervec:
                    osChiller = model.getChillerElectricEIR(chiller.handle()).get()
                    self.updateChiller(model, osChiller, coolingDetails.coolingCOP, coolingDetails.supplyTemperature)
            if coolingDetails.pumpMotorEfficiency != "Default":
                pumpVec = cwl.supplyComponents(ops.IddObjectType("OS:Pump:VariableSpeed"))
                for pump in enumerate(pumpVec):
                    osPump = model.getPumpVariableSpeed(pump[1].handle()).get()
                    self.updatePump(osPump, coolingDetails.pumpMotorEfficiency)
            if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.supplyTemperature != "Default":
                self.updateWaterCoolingCoil(model, cc, coolingDetails.coolingAvailSched, coolingDetails.supplyTemperature)
            if coolingDetails.supplyTemperature != "Default":
                self.updateLoopSupplyTemp(cwl, model, coolingDetails.supplyTemperature, 'Chilled_Water_Temperature_Default', 'Chilled_Water_Temp', HVACCount)
    
    def updateCVLoopSupplyTemp(self, airloop, model, suppTempLow, supTempHigh):
        supplyNode = airloop.supplyOutletNode()
        spManager = supplyNode.getSetpointManagerSingleZoneReheat().get()
        if suppTempLow != 'Default':
            spManager.setMinimumSupplyAirTemperature(suppTempLow)
        if supTempHigh != 'Default':
            spManager.setMaximumSupplyAirTemperature(supTempHigh)
    
    def updateLoopSupplyTemp(self, loop, model, suppTemp, schedName, ruleSetName, HVACCount):
        #Change the cooling supply air temperature schedule.
        suppTempRuleset = self.createConstantScheduleRuleset(ruleSetName + str(HVACCount), schedName + str(HVACCount), 'TEMPERATURE', suppTemp, model)
        supplyNode = loop.supplyOutletNode()
        spManager = supplyNode.setpointManagerScheduled().get()
        spManager.setSchedule(suppTempRuleset)
    
    ### END OF FUNCTIONS FOR EDITING HVAC SYSTEMS ###
    
    
    ### START OF FUNCTION FOR ADDING HVAC SYSTEMS TO THE MODEL ###
    def addSystemsToZones(self, model):
        # Variabe to track the number of systems.
        HVACCount = 0
        for osHVAC in (sorted(self.HVACSystemDict.values(), key=operator.attrgetter('count'))):
            # HAVC system index for this group and thermal zones.
            HAVCGroupID, systemIndex, thermalZones, hbZones, airDetails, heatingDetails, coolingDetails = osHVAC.getData()
            # Put thermal zones into a vector and create a list of the thermal zone handles to help identify the zones that are a part of the HVAC system.
            thermalZoneVector = ops.ThermalZoneVector(thermalZones)
            thermalZoneHandles = []
            for tZone in thermalZones:
                thermalZoneHandles.append(str(tZone.handle()))
            
            # Variables that signal whether the zones have something definied that needs to be applied to the whole HVAC.
            recircAirFlowRates = []
            recicTrigger = False
            dehumidTrigger = False
            humidTrigger = False
            HVACCount +=1
            
            # add systems. There are 10 standard ASHRAE systems + Ideal Air Loads
            if systemIndex == -1:
                # -1: Thermostat Only (no system)
                #This is useful if someone wants to build all systems within the OpenStudio interface or apply them through a measure.
                pass
            elif systemIndex == 0:
                # 0: Ideal Air Loads
                for zoneCount, zone in enumerate(thermalZoneVector):
                    #Set the zone's use of ideal air to "True."
                    zone.setUseIdealAirLoads(True)
                    # Create the ideal air system
                    zoneIdealAir = ops.ZoneHVACIdealLoadsAirSystem(model)
                    
                    #Set the dehumidifcation / humidification based on the presence/absence of a zone humidistat.
                    dehumidTrigger = False
                    if hbZones[zoneCount].humidityMax != "":
                        dehumidTrigger = True
                        zoneIdealAir.setDehumidificationControlType("Humidistat")
                    else: zoneIdealAir.setDehumidificationControlType("None")
                    if hbZones[zoneCount].humidityMin != "":
                        zoneIdealAir.setHumidificationControlType("Humidistat")
                    else: zoneIdealAir.setHumidificationControlType("None")
                    
                    # Set an airside economizer and demand controlled ventilation by default.
                    if dehumidTrigger is True:
                        zoneIdealAir.setOutdoorAirEconomizerType('DifferentialEnthalpy')
                    else:
                        zoneIdealAir.setOutdoorAirEconomizerType('DifferentialDryBulb')
                    zoneIdealAir.setCoolingLimit('LimitFlowRate')
                    zoneIdealAir.autosizeMaximumCoolingAirFlowRate()
                    
                    # Set the airDetails.
                    if airDetails != None:
                        if airDetails.HVACAvailabiltySched != 'ALWAYS ON':
                            hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched,model)
                            zoneIdealAir.setAvailabilitySchedule(hvacAvailSch)
                        if airDetails.fanControl == 'Variable Volume':
                            zoneIdealAir.setDemandControlledVentilationType('OccupancySchedule')
                        if airDetails.heatingSupplyAirTemp != 'Default':
                            zoneIdealAir.setMaximumHeatingSupplyAirTemperature(airDetails.heatingSupplyAirTemp)
                        if airDetails.coolingSupplyAirTemp != 'Default':
                            zoneIdealAir.setMinimumCoolingSupplyAirTemperature(airDetails.coolingSupplyAirTemp)
                        if airDetails.airsideEconomizer != 'Default':
                            zoneIdealAir.setOutdoorAirEconomizerType(airDetails.airsideEconomizer)
                        if airDetails.heatRecovery != 'Default':
                            zoneIdealAir.setHeatRecoveryType(airDetails.heatRecovery)
                        if airDetails.recoveryEffectiveness != 'Default':
                            zoneIdealAir.setSensibleHeatRecoveryEffectiveness(airDetails.recoveryEffectiveness)
                            zoneIdealAir.setLatentHeatRecoveryEffectiveness(airDetails.recoveryEffectiveness)
                    
                    # Set the heatingDetails.
                    if heatingDetails != None:
                        if heatingDetails.heatingAvailSched != 'ALWAYS ON':
                            heatAvailSch = self.getOSSchedule(heatingDetails.heatingAvailSched,model)
                            zoneIdealAir.setHeatingAvailabilitySchedule(heatAvailSch)
                    
                    # Set the coolingDetails.
                    if coolingDetails != None:
                        if coolingDetails.coolingAvailSched != 'ALWAYS ON':
                            coolAvailSch = self.getOSSchedule(coolingDetails.coolingAvailSched,model)
                            zoneIdealAir.setCoolingAvailabilitySchedule(coolAvailSch)
                    
                    # Add the ideal air system to the thermal zone.
                    zoneIdealAir.addToThermalZone(zone)
                
            elif systemIndex == 1:
                # 1: PTAC, Residential
                ops.OpenStudioModelHVAC.addSystemType1(model, thermalZoneVector)
                allptacs = model.getZoneHVACPackagedTerminalAirConditioners()
                zoneCount = 0
                
                for ptac in allptacs:
                    zoneHandle = str(ptac.thermalZone().get().handle())
                    if zoneHandle in thermalZoneHandles:
                        hvacHandle = ptac.handle()
                        
                        #Set the airDetails.
                        if airDetails != None:
                            if airDetails.HVACAvailabiltySched != 'ALWAYS ON':
                                hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched, model)
                                ptac.setAvailabilitySchedule(hvacAvailSch)
                            if airDetails.fanPlacement != 'Default':
                                ptac.setFanPlacement(airDetails.fanPlacement)
                            if airDetails.fanTotalEfficiency != "Default" or airDetails.fanMotorEfficiency != "Default" or airDetails.fanPressureRise != "Default" or airDetails.airSysHardSize != "Default":
                                sfname = ptac.supplyAirFan().name()
                                cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                                self.updateFan(cvfan,airDetails.fanTotalEfficiency,airDetails.fanMotorEfficiency,airDetails.fanPressureRise,airDetails.airSysHardSize)
                        
                        #Set the heatingDetails.
                        if heatingDetails != None:
                            if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.supplyTemperature != 'Default':
                                x = ptac.heatingCoil().name()
                                hc = model.getCoilHeatingWaterByName(str(x)).get()
                                self.updateWaterHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.supplyTemperature)
                        
                        #Set the coolingDetails.
                        if coolingDetails != None:
                            if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                                ccname = ptac.coolingCoil().name()
                                cc = model.getCoilCoolingDXSingleSpeedByName(str(ccname)).get()
                                self.updateDXCoolingCoil(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
                        
                        # Set zone-specific parameters like a specified portion of recirculated air.
                        # Recirculated air also means that we have to hard-size the fan.
                        if hbZones[zoneCount].recirculatedAirPerArea != 0:
                            sfname = ptac.supplyAirFan().name()
                            cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                            self.setRecircOnSingleZoneSys(hbZones[zoneCount], ptac, cvfan)
                        zoneCount += 1
                
                #If heating details are set, change them at the level of the boiler.
                if heatingDetails != None:
                    if heatingDetails.heatingEffOrCOP != "Default" or heatingDetails.supplyTemperature != "Default"  or heatingDetails.pumpMotorEfficiency != "Default":
                        x = ptac.heatingCoil().name()
                        hc = model.getCoilHeatingWaterByName(str(x)).get()
                        hwl = hc.plantLoop().get()
                        if heatingDetails.heatingEffOrCOP != "Default" or heatingDetails.supplyTemperature != "Default":
                            boilerVec = hwl.supplyComponents(ops.IddObjectType("OS:Boiler:HotWater"))
                            for boiler in boilerVec:
                                osBoiler = model.getBoilerHotWater(boiler.handle()).get()
                                self.updateBoiler(model, osBoiler, heatingDetails.heatingEffOrCOP, heatingDetails.supplyTemperature)
                        if heatingDetails.pumpMotorEfficiency != "Default":
                            pumpVec = hwl.supplyComponents(ops.IddObjectType("OS:Pump:VariableSpeed"))
                            for pump in enumerate(pumpVec):
                                osPump = model.getPumpVariableSpeed(pump[1].handle()).get()
                                self.updatePump(osPump, heatingDetails.pumpMotorEfficiency)
                        if heatingDetails.supplyTemperature != "Default":
                            self.updateLoopSupplyTemp(hwl, model, heatingDetails.supplyTemperature, "Hot_Water_Temperature_Default", "Hot_Water_Temp", HVACCount)
                
            elif systemIndex == 2:
                # 2: PTHP, Residential
                ops.OpenStudioModelHVAC.addSystemType2(model, thermalZoneVector)
                allpthps = model.getZoneHVACPackagedTerminalHeatPumps()
                zoneCount = 0
                
                for pthp in allpthps:
                    zoneHandle = str(pthp.thermalZone().get().handle())
                    if zoneHandle in thermalZoneHandles:
                        hvacHandle = pthp.handle()
                        
                        #Set the airDetails.
                        if airDetails != None:
                            if airDetails.HVACAvailabiltySched != 'ALWAYS ON':
                                hvacAvailSch = self.getOSSchedule(airDetails.HVACAvailabiltySched, model)
                                pthp.setAvailabilitySchedule(hvacAvailSch)
                            if airDetails.fanPlacement != 'Default':
                                pthp.setFanPlacement(airDetails.fanPlacement)
                            if airDetails.fanTotalEfficiency != "Default" or airDetails.fanMotorEfficiency != "Default" or airDetails.fanPressureRise != "Default" or airDetails.airSysHardSize != "Default":
                                sfname = pthp.supplyAirFan().name()
                                cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                                self.updateFan(cvfan,airDetails.fanTotalEfficiency,airDetails.fanMotorEfficiency,airDetails.fanPressureRise,airDetails.airSysHardSize)
                        
                        #Set the heatingDetails.
                        if heatingDetails != None:
                            if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                                x = pthp.heatingCoil().handle()
                                hc = model.getCoilHeatingDXSingleSpeed(x).get()
                                self.updateDXHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
                        
                        #Set the coolingDetails.
                        if coolingDetails != None:
                            if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                                ccname = pthp.coolingCoil().name()
                                cc = model.getCoilCoolingDXSingleSpeedByName(str(ccname)).get()
                                self.updateDXCoolingCoil(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
                        
                        # Set zone-specific parameters like a specified portion of recirculated air.
                        # Recirculated air also means that we have to hard-size the fan.
                        if hbZones[zoneCount].recirculatedAirPerArea != 0:
                            sfname = pthp.supplyAirFan().name()
                            cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                            self.setRecircOnSingleZoneSys(hbZones[zoneCount], pthp, cvfan)
                        zoneCount += 1
                
            elif systemIndex == 3:
                # 3: Packaged Single Zone - AC
                for zoneCount, zone in enumerate(thermalZoneVector):
                    handle = ops.OpenStudioModelHVAC.addSystemType3(model).handle()
                    airloop = model.getAirLoopHVAC(handle).get()
                    airloop.addBranchForZone(zone)
                    
                    if hbZones[zoneCount].humidityMin != '':
                        self.addElectricHumidifier(model, airloop)
                    
                    #Set the airDetails.
                    if airDetails != None:
                        self.adjustCVAirLoop(model, airloop, airDetails)
                    else:
                        self.addDefaultAirsideEcon(airloop, False)
                    
                    #Set the heatingDetails.
                    if heatingDetails != None:
                        if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                            comps = airloop.supplyComponents()
                            hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Gas"))
                            hc = model.getCoilHeatingGas(hcs[0].handle()).get()
                            self.updateGasHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
                    
                    #Set the coolingDetails.
                    if coolingDetails != None:
                        if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                            comps = airloop.supplyComponents()
                            ccs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:SingleSpeed"))
                            cc = model.getCoilCoolingDXSingleSpeed(ccs[0].handle()).get()
                            self.updateDXCoolingCoil(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
                
            elif systemIndex == 4:
                # 4: Packaged Single Zone - HP
                for zoneCount, zone in enumerate(thermalZoneVector):
                    handle = ops.OpenStudioModelHVAC.addSystemType4(model).handle()
                    airloop = model.getAirLoopHVAC(handle).get()
                    airloop.addBranchForZone(zone)
                    
                    if hbZones[zoneCount].humidityMin != '':
                        self.addElectricHumidifier(model, airloop)
                    
                    #Set the airDetails.
                    if airDetails != None:
                        self.adjustCVAirLoop(model, airloop, airDetails)
                    else:
                        self.addDefaultAirsideEcon(airloop, False)
                    
                    #Set the heatingDetails.
                    if heatingDetails != None:
                        if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                            comps = airloop.supplyComponents()
                            hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:DX:SingleSpeed"))
                            hc = model.getCoilHeatingDXSingleSpeed(hcs[0].handle()).get()
                            self.updateDXHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
                    
                    #Set the coolingDetails.
                    if coolingDetails != None:
                        if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                            comps = airloop.supplyComponents()
                            ccs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:SingleSpeed"))
                            cc = model.getCoilCoolingDXSingleSpeed(ccs[0].handle()).get()
                            self.updateDXCoolingCoil(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
            
            elif systemIndex == 5:
                # 5: Packaged VAV w/ Reheat
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType5(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    
                    # If there is recirculated air specificed, then specify it at the level of the VAV Box.
                    zoneTotAir = self.getZoneTotalAir(hbZones[zoneCount])
                    recircAirFlowRates.append(zoneTotAir)
                    x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:VAV:Reheat"))
                    vavBox = model.getAirTerminalSingleDuctVAVReheat(x[zoneCount].handle()).get()
                    if hbZones[zoneCount].recirculatedAirPerArea != 0:
                        recicTrigger = True
                        self.sizeAirTerminalForRecirc(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    elif recicTrigger == True:
                        vavBox.setZoneMinimumAirFlowMethod('Constant')
                        vavBox.autosizeMaximumAirFlowRate()
                        vavBox.resetMinimumAirFlowFractionSchedule()
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                    
                    # If there are any ventilation schedules specified, then set the VAV Box to follow them.
                    if hbZones[zoneCount].ventilationSched != '':
                        self.applyVentilationSched(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    
                    self.adjustWaterReheatCoil(model, vavBox, airDetails, heatingDetails)
                
                #If there is recirculated air, we also have to hard size the fan to ensure that enough air can get through the system.
                if recicTrigger == True:
                    self.sizeVAVFanForRecirc(model, airloop, recircAirFlowRates)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustVAVAirLoop(model, airloop, airDetails, HVACCount, dehumidTrigger, False)
                else:
                    self.addDefaultAirsideEcon(airloop, False)
                
                # Set the heatingDetails at the level of the boiler.
                if heatingDetails != None:
                    self.adjustHotWaterLoop(model, airloop, heatingDetails, HVACCount)
                
                # Set the coolingDetails at the level of the central DX coil.
                if coolingDetails != None:
                    if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                        comps = airloop.supplyComponents()
                        ccs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:TwoSpeed"))
                        cc = model.getCoilCoolingDXTwoSpeed(ccs[0].handle()).get()
                        self.updateDXCoolingCoilTwoSpeed(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
            
            elif systemIndex == 6:
                # 6: Packaged VAV w/ PFP Boxes
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType6(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    
                    # If there is recirculated air specificed, then specify it at the level of the VAV Box.
                    zoneTotAir = self.getZoneTotalAir(hbZones[zoneCount])
                    recircAirFlowRates.append(zoneTotAir)
                    x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:ParallelPIU:Reheat"))
                    vavBox = model.getAirTerminalSingleDuctParallelPIUReheat(x[zoneCount].handle()).get()
                    if hbZones[zoneCount].recirculatedAirPerArea != 0:
                        recicTrigger = True
                        self.sizeAirTerminalForRecirc(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    elif recicTrigger == True:
                        vavBox.setZoneMinimumAirFlowMethod('Constant')
                        vavBox.autosizeMaximumAirFlowRate()
                        vavBox.resetMinimumAirFlowFractionSchedule()
                    
                    # If there are any ventilation schedules specified, then set the VAV Box to follow them.
                    if hbZones[zoneCount].ventilationSched != '':
                        self.applyVentilationSched(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                    self.adjustElectricReheatCoil(model, vavBox, heatingDetails)
                
                #If there is recirculated air, we also have to hard size the fan to ensure that enough air can get through the system.
                if recicTrigger == True:
                    self.sizeVAVFanForRecirc(model, airloop, recircAirFlowRates)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustVAVAirLoop(model, airloop, airDetails, HVACCount, False, False, False)
                else:
                    self.addDefaultAirsideEcon(airloop, False)
                
                # Set the heatingDetails at the level of the electric resistance heater.
                if heatingDetails != None:
                    if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                        comps = airloop.supplyComponents()
                        hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Electric"))
                        hc = model.getCoilHeatingElectric(hcs[0].handle()).get()
                        self.updateElectricHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
                
                # Set the coolingDetails at the level of the central DX coil.
                if coolingDetails != None:
                    if coolingDetails.coolingAvailSched != "ALWAYS ON" or coolingDetails.coolingCOP != "Default":
                        comps = airloop.supplyComponents()
                        ccs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:TwoSpeed"))
                        cc = model.getCoilCoolingDXTwoSpeed(ccs[0].handle()).get()
                        self.updateDXCoolingCoilTwoSpeed(model, cc, coolingDetails.coolingAvailSched, coolingDetails.coolingCOP)
            
            elif systemIndex == 7:
                # 7: VAV w/ Reheat
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType7(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    
                    # If there is recirculated air specificed, then specify it at the level of the VAV Box.
                    zoneTotAir = self.getZoneTotalAir(hbZones[zoneCount])
                    recircAirFlowRates.append(zoneTotAir)
                    x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:VAV:Reheat"))
                    vavBox = model.getAirTerminalSingleDuctVAVReheat(x[zoneCount].handle()).get()
                    if hbZones[zoneCount].recirculatedAirPerArea != 0:
                        recicTrigger = True
                        self.sizeAirTerminalForRecirc(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    elif recicTrigger == True:
                        vavBox.setZoneMinimumAirFlowMethod('Constant')
                        vavBox.autosizeMaximumAirFlowRate()
                        vavBox.resetMinimumAirFlowFractionSchedule()
                    
                    # If there are any ventilation schedules specified, then set the VAV Box to follow them.
                    if hbZones[zoneCount].ventilationSched != '':
                        self.applyVentilationSched(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    
                    #Check for any humidity setpoints.
                    if hbZones[zoneCount].humidityMax != '':
                        dehumidTrigger = True
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                    self.adjustWaterReheatCoil(model, vavBox, airDetails, heatingDetails)
                
                #If there is recirculated air, we also have to hard size the fan to ensure that enough air can get through the system.
                if recicTrigger == True:
                    self.sizeVAVFanForRecirc(model, airloop, recircAirFlowRates)
                # If there is a maximum humidity assigned to the zone, set the cooling coil to dehumidify the air.
                if dehumidTrigger == True:
                    self.addChilledWaterDehumid(model, airloop)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustVAVAirLoop(model, airloop, airDetails, HVACCount, dehumidTrigger, True)
                else:
                    self.addDefaultAirsideEcon(airloop, dehumidTrigger)
                
                # Set the heatingDetails at the level of the boiler.
                if heatingDetails != None:
                    self.adjustHotWaterLoop(model, airloop, heatingDetails, HVACCount)
                
                # Set the coolingDetails at the level of the chiller.
                if coolingDetails != None:
                    self.adjustChilledWaterLoop(model, airloop, coolingDetails, HVACCount)
            
            elif systemIndex == 8:
                # 8: VAV w/ PFP Boxes
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType8(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    
                    # If there is recirculated air specificed, then specify it at the level of the VAV Box.
                    zoneTotAir = self.getZoneTotalAir(hbZones[zoneCount])
                    recircAirFlowRates.append(zoneTotAir)
                    x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:ParallelPIU:Reheat"))
                    vavBox = model.getAirTerminalSingleDuctParallelPIUReheat(x[zoneCount].handle()).get()
                    if hbZones[zoneCount].recirculatedAirPerArea != 0:
                        recicTrigger = True
                        self.sizeAirTerminalForRecirc(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    elif recicTrigger == True:
                        vavBox.setZoneMinimumAirFlowMethod('Constant')
                        vavBox.autosizeMaximumAirFlowRate()
                        vavBox.resetMinimumAirFlowFractionSchedule()
                    
                    # If there are any ventilation schedules specified, then set the VAV Box to follow them.
                    if hbZones[zoneCount].ventilationSched != '':
                        self.applyVentilationSched(model, hbZones[zoneCount], vavBox, zoneTotAir)
                    
                    if hbZones[zoneCount].humidityMax != '':
                        dehumidTrigger = True
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                    self.adjustElectricReheatCoil(model, vavBox, heatingDetails)
                
                #If there is recirculated air, we also have to hard size the fan to ensure that enough air can get through the system.
                if recicTrigger == True:
                    self.sizeVAVFanForRecirc(model, airloop, recircAirFlowRates)
                # If there is a maximum humidity assigned to the zone, set the cooling coil to dehumidify the air.
                if dehumidTrigger == True:
                    self.addChilledWaterDehumid(model, airloop)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustVAVAirLoop(model, airloop, airDetails, HVACCount, dehumidTrigger, True, False)
                else:
                    self.addDefaultAirsideEcon(airloop, dehumidTrigger)
                
                # Set the heatingDetails at the level of the electric resistance heater.
                if heatingDetails != None:
                    if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                        comps = airloop.supplyComponents()
                        hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Electric"))
                        hc = model.getCoilHeatingElectric(hcs[0].handle()).get()
                        self.updateElectricHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
                
                # Set the coolingDetails at the level of the chiller.
                if coolingDetails != None:
                    self.adjustChilledWaterLoop(model, airloop, coolingDetails, HVACCount)
            
            elif systemIndex == 9:
                # 9: Warm Air Furnace - Gas Fired
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType9(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustCVAirLoop(model, airloop, airDetails)
                else:
                    self.addDefaultAirsideEcon(airloop, False)
                
                #Set the heatingDetails.
                if heatingDetails != None:
                    if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                        comps = airloop.supplyComponents()
                        hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Gas"))
                        hc = model.getCoilHeatingGas(hcs[0].handle()).get()
                        self.updateGasHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
            
            elif systemIndex == 10:
                # 10: Warm Air Furnace - Electric
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType10(model).handle()
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # Add branches for zones.
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    if hbZones[zoneCount].humidityMin != '':
                        humidTrigger = True
                
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airloop)
                
                #Set the airDetails.
                if airDetails != None:
                    self.adjustCVAirLoop(model, airloop, airDetails)
                else:
                    self.addDefaultAirsideEcon(airloop, False)
                
                # Set the heatingDetails at the level of the electric resistance heater.
                if heatingDetails != None:
                    if heatingDetails.heatingAvailSched != "ALWAYS ON" or heatingDetails.heatingEffOrCOP != 'Default':
                        comps = airloop.supplyComponents()
                        hcs = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Electric"))
                        hc = model.getCoilHeatingElectric(hcs[0].handle()).get()
                        self.updateElectricHeatingCoil(model, hc, heatingDetails.heatingAvailSched, heatingDetails.heatingEffOrCOP)
            
            elif systemIndex == 11 or systemIndex == 12 or systemIndex == 13 or systemIndex == 15:
                # Check to see if there is humidity control on any of the zones.
                for zone in hbZones:
                    if zone.humidityMax != '':
                        dehumidTrigger = True
                    if zone.humidityMin != '':
                        humidTrigger = True
                
                # Create the hot water plant.
                if heatingDetails != None and heatingDetails.supplyTemperature != 'Default':
                    suppTemp = heatingDetails.supplyTemperature
                else:
                    if systemIndex == 13 or systemIndex == 15:
                        suppTemp = 45
                    else:
                        suppTemp = 67
                if systemIndex == 13:
                    hotLoopTemp = self.createConstantScheduleRuleset('Hot_Water_Radiant_Loop_Temperature' + str(HVACCount), 'Hot_Water_Radiant_Loop_Temperature_Default' + str(HVACCount), 'TEMPERATURE', suppTemp, model)
                    hwl = self.createHotWaterPlant(model, hotLoopTemp, heatingDetails, HVACCount, True)
                else:
                    hotLoopTemp = self.createConstantScheduleRuleset('Hot_Water_Temperature' + str(HVACCount), 'Hot_Water_Temperature_Default' + str(HVACCount), 'TEMPERATURE', suppTemp, model)
                    hwl = self.createHotWaterPlant(model, hotLoopTemp, heatingDetails, HVACCount)
                
                # Create the chilled water plant.
                if coolingDetails != None and coolingDetails.supplyTemperature != 'Default':
                    suppTemp = coolingDetails.supplyTemperature
                else:
                    if systemIndex == 13:
                        suppTemp = 15
                    else:
                        suppTemp = 6.7
                if coolingDetails != None and coolingDetails.chillerType != 'Default':
                    chillType = coolingDetails.chillerType
                else:
                    chillType = "WaterCooled"
                if systemIndex == 13:
                    coolLoopTemp = self.createConstantScheduleRuleset('Chilled_Water_Radiant_Loop_Temperature' + str(HVACCount), 'Chilled_Water_Radiant_Loop_Temperature_Default' + str(HVACCount), 'TEMPERATURE', suppTemp, model)
                    cwl = self.createChilledWaterPlant(model, coolLoopTemp, coolingDetails, HVACCount, chillType, True)
                else:
                    coolLoopTemp = self.createConstantScheduleRuleset('Chilled_Water_Temperature' + str(HVACCount), 'Chilled_Water_Temperature_Default' + str(HVACCount), 'TEMPERATURE', suppTemp, model)
                    cwl = self.createChilledWaterPlant(model, coolLoopTemp, coolingDetails, HVACCount, chillType)
                if chillType == "WaterCooled":
                    cndwl = self.createCondenser(model, cwl, HVACCount)
                
                # Create air loop.
                if systemIndex == 11:
                    airLoop = self.createPrimaryAirLoop('DOAS', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hwl, cwl)
                elif systemIndex == 12:
                    airLoop = self.createPrimaryAirLoop('DOAS', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hwl, cwl, "ChilledBeam")
                elif systemIndex == 13 or systemIndex == 15:
                    hotterLoopTemp = self.createConstantScheduleRuleset('Hot_Water_Temperature' + str(HVACCount), 'Hot_Water_Temperature_Default' + str(HVACCount), 'TEMPERATURE', 67, model)
                    hotwl = self.createHotWaterPlant(model, hotterLoopTemp, heatingDetails, HVACCount)
                    if systemIndex == 13:
                        if dehumidTrigger == True:
                            coolerLoopTemp = self.createConstantScheduleRuleset('Chilled_Water_Temperature' + str(HVACCount), 'Chilled_Water_Temperature_Default' + str(HVACCount), 'TEMPERATURE', 6.7, model)
                            coolwl = self.createChilledWaterPlant(model, coolerLoopTemp, coolingDetails, HVACCount, chillType)
                            airLoop = self.createPrimaryAirLoop('DOAS', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hotwl, coolwl)
                        else:
                            airLoop = self.createPrimaryAirLoop('DOAS', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hotwl, None)
                    else:
                        airLoop = self.createPrimaryAirLoop('VAV', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hotwl, cwl)
                
                # If there is a maximum humidity assigned to the zone, set the cooling coil to dehumidify the air.
                if dehumidTrigger == True:
                    self.addChilledWaterDehumid(model, airLoop)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airLoop)
                
                if systemIndex == 11:
                    # Add the fain coil units.
                    equipList = ['FanCoil']
                    self.createZoneEquip(model, thermalZoneVector, hbZones, equipList, hwl, cwl)
                elif systemIndex == 12:
                    #Add the baseboard heating.
                    equipList = ['Baseboard']
                    self.createZoneEquip(model, thermalZoneVector, hbZones, equipList, hwl, cwl)
                elif systemIndex == 13 or systemIndex == 15:
                    #Add the radiant floors.
                    equipList = ['RadiantFloor']
                    if systemIndex == 13:
                        self.createZoneEquip(model, thermalZoneVector, hbZones, equipList, hwl, cwl)
                    elif systemIndex == 15:
                        self.createZoneEquip(model, thermalZoneVector, hbZones, equipList, hwl, cwl, True)
            
            elif systemIndex == 14:
                # Check to see if there is humidity control on any of the zones.
                for zone in hbZones:
                    if zone.humidityMax != '':
                        dehumidTrigger = True
                    if zone.humidityMin != '':
                        humidTrigger = True
                
                # Make a chilled water loop for the DOAS if it has been specified or if there is humidity control.
                cwl = None
                hwl = None
                chillTrigger = False
                if coolingDetails != None and coolingDetails.chillerType != 'Default': chillTrigger = True
                if dehumidTrigger == True or chillTrigger:
                    if coolingDetails != None and coolingDetails.chillerType != 'Default':
                        chillType = coolingDetails.chillerType
                    else:
                        chillType = "WaterCooled"
                    coolLoopTemp = self.createConstantScheduleRuleset('Chilled_Water_Temperature' + str(HVACCount), 'Chilled_Water_Temperature_Default' + str(HVACCount), 'TEMPERATURE', 6.7, model)
                    cwl = self.createChilledWaterPlant(model, coolLoopTemp, None, HVACCount, chillType)
                    if chillType == "WaterCooled":
                        cndwl = self.createCondenser(model, cwl, HVACCount)
                
                #Make a DOAS air loop.
                airLoop = self.createPrimaryAirLoop('DOAS', model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount, hwl, cwl, None, True)
                
                # If there is a maximum humidity assigned to the zone, set the cooling coil to dehumidify the air.
                if dehumidTrigger == True:
                    self.addChilledWaterDehumid(model, airLoop)
                # If there is a minimum humidity assigned to the zone, add in an electric humidifier to humidify the air.
                if humidTrigger == True:
                    self.addElectricHumidifier(model, airLoop)
                
                # Make the VRF System.
                self.createVRFSystem(model, thermalZoneVector, hbZones, airDetails, heatingDetails, coolingDetails, HVACCount)
            
            else:
                msg = "HVAC system index " + str(systemIndex) +  " is not implemented yet!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    
    ### END OF FUNCTION FOR ADDING HVAC SYSTEMS TO THE MODEL ###
    
    
    def addThermostat(self, HBZone, OSThermalZone, space, model):
        # create a dual set point
        thermostat = ops.ThermostatSetpointDualSetpoint(model)
        time24hrs = ops.Time(0,24,0,0)
        
        # assign schedules
        thermostat.setName("dualSetPtThermostat" + str(OSThermalZone.name()))
        
        heatingSetPtSchedule = self.getOSSchedule(HBZone.heatingSetPtSchedule, model)
        coolingSetPtSchedule = self.getOSSchedule(HBZone.coolingSetPtSchedule, model)
        
        if HBZone.heatingSetPt != "":
            heatingSch = ops.ScheduleRuleset(model)
            heatingSch.setName("Heating Sch")
            defaultDaySchedule = heatingSch.defaultDaySchedule()
            defaultDaySchedule.setName("Heating Sch Default")
            defaultDaySchedule.addValue(time24hrs, float(HBZone.heatingSetPt))
            thermostat.setHeatingSchedule(heatingSch)
            
        thermostat.setHeatingSetpointTemperatureSchedule(heatingSetPtSchedule)
        
        if HBZone.coolingSetPt != "":
            coolingSch = ops.ScheduleRuleset(model)
            coolingSch.setName("Cooling Sch")
            defaultDaySchedule = coolingSch.defaultDaySchedule()
            defaultDaySchedule.setName("Cooling Sch Default")
            defaultDaySchedule.addValue(time24hrs, float(HBZone.coolingSetPt))
            thermostat.setCoolingSchedule(coolingSch)
            
        thermostat.setCoolingSetpointTemperatureSchedule(coolingSetPtSchedule)
        
        OSThermalZone.setThermostatSetpointDualSetpoint(thermostat)
    
    def addHumidistat(self, HBZone, OSThermalZone, space, model):
        # create a humidistat.
        humidistat = ops.ZoneControlHumidistat(model)
        
        # name the humidistat
        humidistat.setName("humidistat" + str(space.name()))
        
        # get type limits for humidity and create them if they don't exist.
        try:
            humidTypeLimits = self.humidTypeLimits
        except:
            humidTypeLimits = self.humidTypeLimits = self.createOSScheduleTypeLimitsFromValues(model, 0, 100, 'CONTINUOUS', 'Percent')
        
        if HBZone.humidityMax != "":
            values = ["schedule:constant", humidTypeLimits, float(HBZone.humidityMax)]
            maxHumidSched = self.createConstantOSSchedule("maxHumidity" + str(space.name()), values, model)
            humidistat.setDehumidifyingRelativeHumiditySetpointSchedule(maxHumidSched)
        else:
            values = ["schedule:constant", humidTypeLimits, 100]
            maxHumidSched = self.createConstantOSSchedule("maxHumidity" + str(space.name()), values, model)
            humidistat.setDehumidifyingRelativeHumiditySetpointSchedule(maxHumidSched)
        
        if HBZone.humidityMin != "":
            values = ["schedule:constant", humidTypeLimits, float(HBZone.humidityMin)]
            minHumidSched = self.createConstantOSSchedule("minHumidity" + str(space.name()), values, model)
            humidistat.setHumidifyingRelativeHumiditySetpointSchedule(minHumidSched)
        else:
            values = ["schedule:constant", humidTypeLimits, 0]
            minHumidSched = self.createConstantOSSchedule("minHumidity" + str(space.name()), values, model)
            humidistat.setHumidifyingRelativeHumiditySetpointSchedule(minHumidSched)
        
        OSThermalZone.setZoneControlHumidistat(humidistat)
    
    def addDaylightCntrl(self, HBZone, OSThermalZone, space, model):
        zoneDayLCntrl = ops.DaylightingControl(model)
        zoneDayLCntrl.setSpace(space)
        zoneDayLCntrl.setIlluminanceSetpoint(HBZone.illumSetPt)
        zoneDayLCntrl.setMaximumAllowableDiscomfortGlareIndex(HBZone.GlareDiscomIndex)
        zoneDayLCntrl.setThetaRotationAroundYAxis(-math.radians(HBZone.glareView))
        if HBZone.illumCntrlSensorPt == None:
            HBZone.atuoPositionDaylightSensor()
        zoneDayLCntrl.setPositionXCoordinate(HBZone.illumCntrlSensorPt.X)
        zoneDayLCntrl.setPositionYCoordinate(HBZone.illumCntrlSensorPt.Y)
        zoneDayLCntrl.setPositionZCoordinate(HBZone.illumCntrlSensorPt.Z)
        OSThermalZone.setPrimaryDaylightingControl(zoneDayLCntrl)
        OSThermalZone.setFractionofZoneControlledbyPrimaryDaylightingControl(HBZone.daylightCntrlFract)
    
    def setupNameAndType(self, zone, space, model):
        space.setName('{}_space'.format(zone.name))
        
        # assign space type
        spaceTypeName = ":".join([zone.bldgProgram, zone.zoneProgram])
        
        if not spaceTypeName in self.bldgTypes.keys():
            spaceType = ops.SpaceType(model)
            spaceType.setName(spaceTypeName)
            self.bldgTypes[spaceTypeName] = spaceType
        else:
            spaceType = self.bldgTypes[spaceTypeName]
        
        space.setSpaceType(spaceType)
        
        return space
    
    def setInfiltration(self, zone, space, model):
        # infiltration
        infiltration = ops.SpaceInfiltrationDesignFlowRate(model)
        infiltration.setFlowperSpaceFloorArea(zone.infiltrationRatePerArea)
        infiltration.setSchedule(self.getOSSchedule(zone.infiltrationSchedule, model))
        infiltration.setSpace(space)
    
    def setAirMixing(self, zone, model):
        # air mixing from air walls
        targetZone = self.thermalZonesDict[zone.name]
        for mixZoneCount, zoneMixName in enumerate(zone.mixAirZoneList):
            zoneMixing = ops.ZoneMixing(targetZone)
            sourceZone = self.thermalZonesDict[zoneMixName]
            zoneMixing.setSourceZone(sourceZone)
            zoneMixing.setDesignFlowRate(zone.mixAirFlowList[mixZoneCount])
            zoneMixing.setSchedule(self.getOSSchedule(zone.mixAirFlowSched[mixZoneCount], model))
    
    def setDefaultSchedule(self, zone, space, model):
        # I'm not sure how default schedule will be useful
        # if I have to create separate definitions for people, light, equipments and infiltration!
        defSchedule = ops.DefaultScheduleSet(model)
        defSchedule.setName(zone.name + "_DefaultScheduleSet")
        defSchedule.setInfiltrationSchedule(self.getOSSchedule(zone.infiltrationSchedule, model))
        defSchedule.setLightingSchedule(self.getOSSchedule(zone.lightingSchedule, model))
        # Not all default zone types have people, or equipment.
        try:
            defSchedule.setElectricEquipmentSchedule(self.getOSSchedule(zone.equipmentSchedule, model))
        except:
            pass
        try:
            defSchedule.setHoursofOperationSchedule(self.getOSSchedule(zone.occupancySchedule, model))
        except:
            pass
        try:
            defSchedule.setPeopleActivityLevelSchedule(self.getOSSchedule(zone.occupancyActivitySch, model))
        except:
            pass
        space.setDefaultScheduleSet(defSchedule)
        return space
        
    def setPeopleDefinition(self, zone, space, model):
        if zone.numOfPeoplePerArea != 0:
            peopleDefinition = ops.PeopleDefinition(model)
            peopleDefinition.setName(zone.name + "_PeopleDefinition")
            flrArea = zone.getFloorArea()
            if flrArea != 0:
                peopleDefinition.setNumberofPeople(zone.numOfPeoplePerArea * flrArea)
                peopleDefinition.setNumberOfPeopleCalculationMethod("People/Area", flrArea)
                peopleDefinition.setPeopleperSpaceFloorArea(zone.numOfPeoplePerArea) #space.peoplePerFloorArea())
            #peopleDefinition.setFractionRadiant
            #peopleDefinition.setSensibleHeatFraction
            
            # This was so confusing to find people and people definition as two different objects
            people = ops.People(peopleDefinition)
            people.setName(zone.name + "_PeopleObject")
            people.setActivityLevelSchedule(self.getOSSchedule(zone.occupancyActivitySch, model))
            people.setNumberofPeopleSchedule(self.getOSSchedule(zone.occupancySchedule, model))
            #people.setPeopleDefinition(peopleDefinition)
            people.setSpace(space)
     
    def setInternalMassDefinition(self, zone, space, model):
        for srfNum,srfArea in enumerate(zone.internalMassSrfAreas):
            # Create internal mass definition
            internalMassDefinition = ops.InternalMassDefinition(model)
            internalMassDefinition.setName(zone.internalMassNames[srfNum]+"_Definition")
            if self.isConstructionInLib(zone.internalMassConstructions[srfNum]):
                construction = self.getConstructionFromLib(zone.internalMassConstructions[srfNum])
            else:
                construction = self.getOSConstruction(zone.internalMassConstructions[srfNum],model)
                self.addConstructionToLib(zone.internalMassConstructions[srfNum], construction)
            internalMassDefinition.setConstruction(construction)
            internalMassDefinition.setSurfaceArea(float(srfArea))
            
            # Create actual internal mass by using the definition above
            internalMass = ops.InternalMass(internalMassDefinition)
            internalMass.setName(zone.internalMassNames[srfNum])
            internalMass.setSpace(space)
    
    def setLightingDefinition(self, zone, space, model):
        
        lightsDefinition = ops.LightsDefinition(model)
        lightsDefinition.setName(zone.name + "_LightsDefinition")
        flrArea = zone.getFloorArea()
        if flrArea != 0:
            lightsDefinition.setDesignLevelCalculationMethod("Watts/Area", flrArea, space.numberOfPeople())
        lightsDefinition.setWattsperSpaceFloorArea(float(zone.lightingDensityPerArea))
        
        lights = ops.Lights(lightsDefinition)
        lights.setName(zone.name + "_LightsObject")
        lights.setSchedule(self.getOSSchedule(zone.lightingSchedule, model))
        lights.setSpace(space)
        
    def setEquipmentDefinition(self, zone, space, model):
        if zone.equipmentLoadPerArea != 0:
            electricDefinition = ops.ElectricEquipmentDefinition(model)
            electricDefinition.setName(zone.name + "_ElectricEquipmentDefinition")
            flrArea = zone.getFloorArea()
            if flrArea != 0:
                electricDefinition.setDesignLevelCalculationMethod("Watts/Area", flrArea, space.numberOfPeople())
            electricDefinition.setWattsperSpaceFloorArea(zone.equipmentLoadPerArea)
            
            electricEqipment = ops.ElectricEquipment(electricDefinition)
            electricEqipment.setName(zone.name + "_ElectricEquipmentObject")
            electricEqipment.setSchedule(self.getOSSchedule(zone.equipmentSchedule, model))
            electricEqipment.setEndUseSubcategory('ElectricEquipment')
            electricEqipment.setSpace(space)
        
    def setDesignSpecificationOutdoorAir(self, zone, space, model):
        if zone.outdoorAirReq != 'None':
            ventilation = ops.DesignSpecificationOutdoorAir(model)
            ventilation.setName(zone.name + "_DSOA")
            ventilation.setOutdoorAirMethod(zone.outdoorAirReq)
            ventilation.setOutdoorAirFlowperPerson(zone.ventilationPerPerson)
            ventilation.setOutdoorAirFlowperFloorArea(zone.ventilationPerArea)
            if zone.ventilationSched != '':
                ventSch = self.getOSSchedule(zone.ventilationSched,model)
                ventilation.setOutdoorAirFlowRateFractionSchedule(ventSch)
            space.setDesignSpecificationOutdoorAir(ventilation)
        return space
    
    def createOSStanadardOpaqueMaterial(self, HBMaterialName, values, model):
        # values = ['Roughness', 'Thickness {m}', 'Conductivity {W/m-K}', 'Density {kg/m3}', 'Specific Heat {J/kg-K}', 'Thermal Absorptance', 'Solar Absorptance', 'Visible Absorptance']
        material = ops.StandardOpaqueMaterial(model)
        material.setName(HBMaterialName)
        roughness = values[0]
        
        material.setRoughness(roughness)
        if values[1] != '':
            material.setThickness(float(values[1]))
        if values[2] != '':
            material.setConductivity(float(values[2]))
        if values[3] != '':
            material.setDensity(float(values[3]))
        if values[4] != '':
            material.setSpecificHeat(float(values[4]))
        if values[5] != '':
            material.setThermalAbsorptance(float(values[5]))
        if values[6] != '':
            material.setSolarAbsorptance(float(values[6]))
        if values[7] != '':
            material.setVisibleAbsorptance(float(values[7]))
        
        return material
    
    def createOSSimpleGlazingMaterial(self, HBMaterialName, values, model):
        """
        WindowMaterial:SimpleGlazingSystem
        ['Material Type', 'U-Factor {W/m2-K}',
        'Solar Heat Gain Coefficient',
        'Visible Transmittance']
        """
        simpleGlazing = ops.SimpleGlazing(model)
        simpleGlazing.setName(HBMaterialName)
        uFactor, SHGC, TVis = map(float, values)
        simpleGlazing.setUFactor(uFactor)
        simpleGlazing.setSolarHeatGainCoefficient(SHGC)
        simpleGlazing.setVisibleTransmittance(TVis)
        
        return simpleGlazing
    
    def createOSStandardGlazingMaterial(self, HBMaterialName, values, model):
        """
        WindowMaterial:Glazing
        ['Optical Data Type', 'Window Glass Spectral Data Set Name', 'Thickness {m}',
        'Solar Transmittance at Normal Incidence', 'Front Side Solar Reflectance at Normal Incidence',
        'Back Side Solar Reflectance at Normal Incidence', 'Visible Transmittance at Normal Incidence',
        'Front Side Visible Reflectance at Normal Incidence', 'Back Side Visible Reflectance at Normal Incidence',
        'Infrared Transmittance at Normal Incidence', 'Front Side Infrared Hemispherical Emissivity',
        'Back Side Infrared Hemispherical Emissivity', 'Conductivity {W/m-K}',
        'Dirt Correction Factor for Solar and Visible Transmittance', 'Solar Diffusing']
        """
        standardGlazing = ops.StandardGlazing(model)
        standardGlazing.setName(HBMaterialName)
        standardGlazing.setOpticalDataType(values[0])
        standardGlazing.setThickness(float(values[2]))
        try:
            # Glass material is defined by average values of transmittance and reflectance.
            standardGlazing.setSolarTransmittanceatNormalIncidence(float(values[3]))
            standardGlazing.setFrontSideSolarReflectanceatNormalIncidence(float(values[4]))
            standardGlazing.setBackSideSolarReflectanceatNormalIncidence(float(values[5]))
            standardGlazing.setVisibleTransmittanceatNormalIncidence(float(values[6]))
            standardGlazing.setFrontSideVisibleReflectanceatNormalIncidence(float(values[7]))
            standardGlazing.setBackSideVisibleReflectanceatNormalIncidence(float(values[8]))
        except:
            # Glass material is defined by detailed spectral data.
            self.windowSpectralDatasets[HBMaterialName] = values[1]
            # Ah, OpenStudio. You put this in your SDK but don't wirte it into the IDF.
            # I'll leave it here until you support it.
            standardGlazing.setWindowGlassSpectralDataSetName(values[1])
        
        standardGlazing.setInfraredTransmittanceatNormalIncidence(float(values[9]))
        standardGlazing.setFrontSideInfraredHemisphericalEmissivity(float(values[10]))
        standardGlazing.setBackSideInfraredHemisphericalEmissivity(float(values[11]))
        standardGlazing.setConductivity(float(values[12]))
        try: standardGlazing.setDirtCorrectionFactorforSolarandVisibleTransmittance(float(values[13]))
        except: pass
        
        """
        try:
            if values[14].lower() == "no":
                standardGlazing.setSolarDiffusing(False)
            else:
                standardGlazing.setSolarDiffusing(True)
        except Exception, e:
            pass
        """
        
        return standardGlazing
    
    def createOSNoMassMaterial(self, HBMaterialName, values, model):
        """
        Material:NoMass
        ['Roughness', 'Thermal Resistance {m2-K/W}', 'Thermal Absorptance', 'Solar Absorptance', 'Visible Absorptance']
        """
        nomassMaterial = ops.MasslessOpaqueMaterial(model)
        nomassMaterial.setName(HBMaterialName)
        
        roughness = values[0]
        thermalResistance, thermalAbsorptance, solarAbsorptance, visibleAbsorptance = map(float, values[1:])
        nomassMaterial.setRoughness(roughness)
        nomassMaterial.setThermalResistance(thermalResistance)
        nomassMaterial.setThermalAbsorptance(thermalAbsorptance)
        nomassMaterial.setSolarAbsorptance(solarAbsorptance)
        nomassMaterial.setVisibleAbsorptance(visibleAbsorptance)
        
        return nomassMaterial
    
    def createOSWindowGasMaterial(self, HBMaterialName, values, model):
        """
        WindowMaterial:Gas
        ['Gas Type', 'Thickness {m}']
        """
        windowGasMaterial = ops.Gas(model)
        windowGasMaterial.setName(HBMaterialName)
        windowGasMaterial.setGasType(values[0])
        windowGasMaterial.setThickness(float(values[1]))
        
        return windowGasMaterial
    
    def createOSWindowGasMixtureMaterial(self, HBMaterialName, values, model):
        """
        WindowMaterial:Gas
        ['Thickness {m}', 'Number of Gases', 'Gas 1 Type', 'Gas 1 Fraction', 'Gas 2 Type', 'Gas 2 Fraction']
        """
        windowGasMixMaterial = ops.GasMixture(model)
        windowGasMixMaterial.setName(HBMaterialName)
        windowGasMixMaterial.setThickness(float(values[0]))
        numOfGas = int(values[1])
        windowGasMixMaterial.setNumberofGasesinMixture(numOfGas)
        windowGasMixMaterial.setGas1Type(values[2])
        windowGasMixMaterial.setGas1Fraction(float(values[3]))
        windowGasMixMaterial.setGas2Type(values[4])
        windowGasMixMaterial.setGas2Fraction(float(values[5]))
        if numOfGas > 2:
            windowGasMixMaterial.setGas3Type(values[6])
            windowGasMixMaterial.setGas3Fraction(float(values[7]))
        if numOfGas > 3:
            windowGasMixMaterial.setGas4Type(values[8])
            windowGasMixMaterial.setGas4Fraction(float(values[9]))
        
        return windowGasMixMaterial
    
    def createOSAirGap(self, HBMaterialName, values, model):
        """
        Material:AirGap
        ['Thermal Resistance {m2-K/W}']
        """
        airGap = ops.AirGap(model, float(values[0]))
        return airGap
    
    def createOSBlind(self, HBMaterialName, values, model):
        """
        WindowMaterial:Blind
        [Slat Orientation, Slat Width {m}, Slat Separation {m}, Slat Thickness {m}, Slat Angle {deg}, Slat Conductivity {W/m-K},
        Slat Beam Solar Transmittance, Front Side Slat Beam Solar Reflectance, Back Side Slat Beam Solar Reflectance,
        Slat Diffuse Solar Transmittance, Front Side Slat Diffuse Solar Reflectance, Back Side Slat Diffuse Solar Reflectance,
        Slat Beam Visible Transmittance, Front Side Slat Beam Visible Reflectance, Back Side Slat Beam Visible Reflectance,
        Slat Diffuse Visible Transmittance, Front Side Slat Diffuse Visible Reflectance, Back Side Slat Diffuse Visible Reflectance,
        Slat Infrared Hemispherical Transmittance, Front Side Slat Infrared Hemispherical Emissivity, Back Side Slat Infrared Hemispherical Emissivity,
        Blind to Glass Distance {m}, Blind Top Opening Multiplier, Blind Bottom Opening Multiplier, Blind Left Side Opening Multiplier
        Blind Right Side Opening Multiplier, Minimum Slat Angle {deg}, Maximum Slat Angle {deg}]
        
        """
        windowBlindMaterial = ops.Blind(model)
        windowBlindMaterial.setName(HBMaterialName)
        windowBlindMaterial.setSlatOrientation(values[0])
        windowBlindMaterial.setSlatWidth(float(values[1]))
        windowBlindMaterial.setSlatSeparation(float(values[2]))
        windowBlindMaterial.setSlatThickness(float(values[3]))
        windowBlindMaterial.setSlatAngle(float(values[4]))
        windowBlindMaterial.setSlatConductivity(float(values[5]))
        windowBlindMaterial.setSlatBeamSolarTransmittance(float(values[6]))
        windowBlindMaterial.setFrontSideSlatBeamSolarReflectance(float(values[7]))
        windowBlindMaterial.setBackSideSlatBeamSolarReflectance(float(values[8]))
        windowBlindMaterial.setSlatDiffuseSolarTransmittance(float(values[9]))
        windowBlindMaterial.setFrontSideSlatDiffuseSolarReflectance(float(values[10]))
        windowBlindMaterial.setBackSideSlatDiffuseSolarReflectance(float(values[11]))
        windowBlindMaterial.setSlatBeamVisibleTransmittance(float(values[12]))
        windowBlindMaterial.setSlatDiffuseVisibleTransmittance(float(values[15]))
        windowBlindMaterial.setFrontSideSlatBeamVisibleReflectance(float(values[7]))
        windowBlindMaterial.setBackSideSlatBeamVisibleReflectance(float(values[7]))
        windowBlindMaterial.setFrontSideSlatDiffuseVisibleReflectance(float(values[7]))
        windowBlindMaterial.setBackSideSlatDiffuseVisibleReflectance(float(values[7]))
        windowBlindMaterial.setFrontSideSlatInfraredHemisphericalEmissivity(float(values[19]))
        windowBlindMaterial.setBackSideSlatInfraredHemisphericalEmissivity(float(values[20]))
        windowBlindMaterial.setBlindtoGlassDistance(float(values[21]))
        windowBlindMaterial.setBlindTopOpeningMultiplier(float(values[22]))
        windowBlindMaterial.setBlindBottomOpeningMultiplier(float(values[23]))
        windowBlindMaterial.setBlindLeftSideOpeningMultiplier(float(values[24]))
        windowBlindMaterial.setBlindRightSideOpeningMultiplier(float(values[25]))
        windowBlindMaterial.setMaximumSlatAngle(float(values[27]))
        
        return windowBlindMaterial
    
    def createOSShade(self, HBMaterialName, values, model):
        """
        WindowMaterial:Shade
        [Solar Transmittance, Solar Reflectance, Visible Transmittance, Visible Reflectance, 
        Infrared Hemispherical Emissivity, Infrared Transmittance, Thickness {m},Conductivity {W/m-K},
        Shade to Glass Distance {m}, Top Opening Multiplier, ottom Opening Multiplier, Left Side Opening Multiplier,
        Right Side Opening Multiplier, Airflow Permeability]
        
        """
        windowShadeMaterial = ops.Shade(model)
        windowShadeMaterial.setName(HBMaterialName)
        
        windowShadeMaterial.setSolarTransmittance(float(values[0]))
        windowShadeMaterial.setSolarReflectance(float(values[1]))
        windowShadeMaterial.setVisibleTransmittance(float(values[2]))
        windowShadeMaterial.setVisibleReflectance(float(values[3]))
        windowShadeMaterial.setThermalHemisphericalEmissivity(float(values[4]))
        windowShadeMaterial.setThermalTransmittance(float(values[5]))
        windowShadeMaterial.setThickness(float(values[6]))
        windowShadeMaterial.setConductivity(float(values[7]))
        windowShadeMaterial.setShadetoGlassDistance(float(values[8]))
        windowShadeMaterial.setTopOpeningMultiplier(float(values[9]))
        windowShadeMaterial.setBottomOpeningMultiplier(float(values[10]))
        windowShadeMaterial.setLeftSideOpeningMultiplier(float(values[11]))
        windowShadeMaterial.setRightSideOpeningMultiplier(float(values[12]))
        windowShadeMaterial.setAirflowPermeability(float(values[13]))
        
        return windowShadeMaterial
    
    def getOSMaterial(self, HBMaterialName, model):
        values, comments, UVSI, UVIP = self.hb_EPMaterialAUX.decomposeMaterial(HBMaterialName, ghenv.Component)
        
        if values[0].lower() == "material":
            # standard opaque material
            return self.createOSStanadardOpaqueMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:simpleglazingsystem":
            return self.createOSSimpleGlazingMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:glazing":
            return self.createOSStandardGlazingMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:gas":
            return self.createOSWindowGasMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:gasmixture":
            return self.createOSWindowGasMixtureMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "material:nomass":
            return self.createOSNoMassMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "material:airgap":
            return self.createOSAirGap(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:blind":
            return self.createOSBlind(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "windowmaterial:shade":
            return self.createOSShade(HBMaterialName, values[1:], model)
        
        else:
            warning =  "The material type " + values[0] + " hasn't been implemented yet!"
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
    def getOSConstruction(self, HBConstructionlName, model):
        
        # call the layers form HB library
        materialNames, comments, UVSI, UVIP = self.hb_EPMaterialAUX.decomposeEPCnstr(HBConstructionlName)
        
        # create an empty vector to collect the materials
        materials = ops.MaterialVector()
        
        for materialName in materialNames:
            # check if the material has been already produced
            if not self.isMaterialInLib(materialName):
                # create an openstudio material for EP material
                OSMaterial = self.getOSMaterial(materialName, model)
                # keep track of materials
                self.addMaterialToLib(materialName, OSMaterial)
            else:
                # material has been already created so let's just use it
                OSMaterial = self.getMaterialFromLib(materialName)
            
            # add it as a layer
            materials.Add(OSMaterial)
    
        construction = ops.Construction(model)
        construction.setName(HBConstructionlName)
        construction.setLayers(materials)
    
        return construction
    
    @staticmethod
    def checkCoordinates(coordinates):
        # check if coordinates are so close or duplicated
        # this is a place holder for now I just return true
        #return True, glzCoordinates
    
        def isDuplicate(pt, newPts):
            for p in newPts:
                if pt.DistanceTo(p) < 2 * sc.doc.ModelAbsoluteTolerance:
                    return True
            return False
            
        newCoordinates = [coordinates[0]]
        for pt in coordinates[1:]:
            if not isDuplicate(pt, newCoordinates):
                newCoordinates.append(pt)
            
        if len(newCoordinates) > 2:
            return True, newCoordinates
        else:
            print "One of the surfaces has less than 3 identical coordinates and is removed."
            return False,[]
    
    def opsZoneSurface (self, surface, model, space):
        # collect Honeybee surfaces for nonplanar cases
        # this is just for OpenStudio and not energyplus
        coordinates = surface.coordinates
        checked, coordinates= self.checkCoordinates(coordinates)
        
        if int(surface.type) == 4: surface.type = 0
        if checked:
          
            # generate OpenStudio points
            pointVectors = ops.Point3dVector();
            for pt in coordinates:
                # add the points to an openStudio list
                pointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
            
            # create surface
            thisSurface = ops.Surface(pointVectors, model);
            thisSurface.setName(surface.name);
            thisSurface.setNumberofVertices(len(coordinates));
            thisSurface.setSpace(space);
            thisSurface.setSurfaceType(surface.srfType[surface.type]);
            srfType = surface.srfType[int(surface.type)].lower().capitalize()
            if srfType.upper().Contains("ROOF") or srfType.upper().Contains("CEILING"):
                srfType = "RoofCeiling" # This is an OpenStudio type that will be converted as a roof or ceiling in idf file
            
            thisSurface.setSurfaceType(srfType);
            
            # create construction
            
            if self.isConstructionInLib(surface.EPConstruction) and surface.EPConstruction != None:
                construction = self.getConstructionFromLib(surface.EPConstruction)
            elif self.isConstructionInLib(surface.construction) and surface.EPConstruction == None:
                construction = self.getConstructionFromLib(surface.construction)
            elif surface.EPConstruction == None:
                construction = self.getOSConstruction(surface.construction, model)
                self.addConstructionToLib(surface.construction, construction)
            else:
                construction = self.getOSConstruction(surface.EPConstruction, model)
                self.addConstructionToLib(surface.EPConstruction, construction)
            
            thisSurface.setConstruction(construction)
            thisSurface.setOutsideBoundaryCondition(surface.BC.capitalize())
            if surface.BC.capitalize()!= "ADIABATIC":
                thisSurface.setSunExposure(surface.sunExposure.capitalize())
                thisSurface.setWindExposure(surface.windExposure.capitalize())
            else:
                thisSurface.setSunExposure("NOSUN")
                thisSurface.setWindExposure("NOWIND")
                
            
            # Boundary condition object
            #setAdjacentSurface(self: Surface, surface: Surface)
            if surface.BC.lower() == "surface" and surface.BCObject.name.strip()!="":
                self.adjacentSurfacesDict[surface.name] = [surface.BCObject.name, thisSurface]
            
            return thisSurface
    
    
    def OPSFenSurface (self, surface, openStudioParentSrf, model):
        
        for childSrf in surface.childSrfs:
            coordinates = childSrf.coordinates
            
            # generate OpenStudio points
            windowPointVectors = ops.Point3dVector();
            
            for pt in coordinates:
                # add the points to an openStudio list
                windowPointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
            
            # create construction
            if self.isConstructionInLib(childSrf.EPConstruction):
                construction = self.getConstructionFromLib(childSrf.EPConstruction)
            else:
                construction = self.getOSConstruction(childSrf.EPConstruction, model)
                # keep track of constructions
                self.addConstructionToLib(childSrf.EPConstruction, construction)
            
            glazing = ops.SubSurface(windowPointVectors, model)
            glazing.setName(childSrf.name)
            glazing.setSurface(openStudioParentSrf)
            glazing.setSubSurfaceType(childSrf.srfType[childSrf.type])
            glazing.setConstruction(construction)
            
            # Check if there are any frame objects associated with the window.
            try:
                frameProps = sc.sticky["honeybee_WindowPropLib"][childSrf.EPConstruction]
                opsFrameObj = self.getOSFrameObj(childSrf.EPConstruction, model)
                glazing.setWindowPropertyFrameAndDivider(opsFrameObj)
            except:
                pass
            
            # Set any shading control objects.
            try:
                shdCntrlName = childSrf.shadingControlName[0]
                opsSdhCntrl = self.getOSShdCntrl(shdCntrlName, model)
                glazing.setShadingControl(opsSdhCntrl)
            except: pass
            
            # Boundary condition object
            #setAdjacentSurface(self: Surface, surface: Surface)
            if surface.BC.lower() == "surface" and surface.BCObject.name.strip()!="":
                if childSrf.name == childSrf.BCObject.name:
                    raise Exception("Interior facing surfaces can't have the same name: %s"%childSrf.name + \
                        "\nRename one of the surfaces and try again!")
                self.adjacentSurfacesDict[childSrf.name] = [childSrf.BCObject.name, glazing]
    
    def OPSShdSurface(self, shdSurfaces, model):
        shadingGroup = ops.ShadingSurfaceGroup(model)
        
        for surfaceCount, surface in enumerate(shdSurfaces):
            coordinates = surface.extractPoints(1, False, None, 'UpperLeftCorner')
            if type(coordinates[0])is not list and type(coordinates[0]) is not tuple:
                coordinates = [coordinates]
            
            shadingSch = ""
            schedule = surface.TransmittanceSCH
            if schedule!="":
                # transmittance schedule
                shadingSch = self.getOSSchedule(schedule, model)
            
            # generate OpenStudio points
            shdPointVectors = ops.Point3dVector();
            
            for shadingCount, ptList in enumerate(coordinates):
                for pt in ptList:
                    # add the points to an openStudio list
                    shdPointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
                
                shdSurface = ops.ShadingSurface(shdPointVectors, model)
                shdSurface.setName("shdSurface_" + str(surfaceCount) + "_" + str(shadingCount))
                shdSurface.setShadingSurfaceGroup(shadingGroup)
                if shadingSch!="": shdSurface.setTransmittanceSchedule(shadingSch)
                
    
    def setAdjacentSurfaces(self):
        for surfaceName in self.adjacentSurfacesDict.keys():
            adjacentSurfaceName, OSSurface = self.adjacentSurfacesDict[surfaceName]
            try:
                adjacentOSSurface = self.adjacentSurfacesDict[adjacentSurfaceName][1]
                
                try:
                    OSSurface.setAdjacentSurface(adjacentOSSurface)
                except:
                    OSSurface.setAdjacentSubSurface(adjacentOSSurface)
            except:
                warning = "Adjacent surface " + adjacentSurfaceName + " was not found."
                print warning
    
    def setOutputVariable(self, fields, model):
        """
        Output:Variable
        """
        var, key, name, freq = fields
        outputVariable = ops.OutputVariable(name.strip(), model)
        outputVariable.setKeyValue(key.strip())
        outputVariable.setReportingFrequency(freq.strip())
    
    def setOutputMeter(self, fields, model):
        """
        Output:Meter
        """
        var, name, freq = fields
        outputMeter = ops.Meter(model)
        outputMeter.setMeterFileOnly(False)
        outputMeter.setName(name.strip())
        outputMeter.setReportingFrequency(freq.strip())
    
    def setOutputs(self, simulationOutputs, model):
        if simulationOutputs == []:
            return
        else:
            
            for output in simulationOutputs:
                try:
                    # remove comment
                    outstr = output.split("!")[0].strip()
                    # remove ; from the end
                    finalout = outstr.replace(";", "", 1)
                    # split into fields
                    fields = finalout.split(",")
                    if fields[0].strip().lower() == "output:variable":
                        self.setOutputVariable(fields, model)
                    elif fields[0].strip().lower() == "output:meter":
                        self.setOutputMeter(fields, model)
                    elif fields[0].strip().lower() == "outputcontrol:table:style":
                        pass
                        #self.setOutputControl(fields, model)
                    else:
                        msg = fields[0] + " is missing from the outputs!"
                        #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                except Exception, e:
                    print  e
                    pass
    
    def getObjToReplace(self):
        return self.csvSchedules, self.csvScheduleCount, self.shadeCntrlToReplace, self.replaceShdCntrl, self.windowSpectralDatasets

class HoneybeeHVAC(object):
    def __init__(self, ID, systemIndex, thermalZones, hbZones, airDetails, heatingDetails, coolingDetails, count):
        self.ID = ID
        self.systemIndex = systemIndex
        self.thermalZones = thermalZones
        self.hbZones = hbZones
        self.airDetails = airDetails
        self.heatingDetails = heatingDetails
        self.coolingDetails = coolingDetails
        self.count = count
    
    def getData(self):
        return [self.ID, self.systemIndex, self.thermalZones, self.hbZones, self.airDetails, self.heatingDetails, self.coolingDetails]

class EPFeaturesNotInOS(object):
    def __init__(self, workingDir):
        self.fileBasedSchedules = {}
        self.schedTypLims = []
        self.workingDir = workingDir
    
    def createCSVSchedString(self, scheduleName):
        # check if the schedule is already created
        if scheduleName.upper() in self.fileBasedSchedules.keys(): return "\n"
        # set up default values
        schTypeLimitStr = "\n"
        schTypeLimitName = "Fraction"
        numOfHours = 8760
        
        # create schedule object based on file
        # find file name and use it as schedule name
        scheduleFileName = os.path.basename(scheduleName)
        scheduleObjectName = "_".join(scheduleFileName.split(".")[:-1])
        
        # copy schedule file into working dir
        scheduleNewAddress = os.path.join(self.workingDir, scheduleFileName)
        shutil.copyfile(scheduleName, scheduleNewAddress)
        
        # put them as key, value so I can find the new name when write schedule
        self.fileBasedSchedules[scheduleName.upper()] = scheduleObjectName
        
        # get the inputs if the schedule is generated by Honeybee
        with open(scheduleName, "r") as schFile:
            for lineCount, line in enumerate(schFile):
                if lineCount == 3: break
                elif lineCount == 0:
                    # try to collect information related to type limit
                    lineSeg = line.split(",")
                    if not lineSeg[0].startswith("Honeybee"):
                        schTypeLimitStr = "ScheduleTypeLimits,\t!Schedule Type\n" + \
                                          '    FRACTION' + ",\t! Name\n" + \
                                          '    0' + ",\t!- Lower Limit Value\n" + \
                                          '    1' + ",\t!- Upper Limit Value\n" + \
                                          '    CONTINUOUS' + ";\t!- Numeric Type\n\n"
                    else:
                        lowerLimit, upperLimit, numericType, unitType = lineSeg[1:5]
                        
                        # prepare the schedulTypeLimitObject
                        schTypeLimitName = os.path.basename(scheduleName).lower(). \
                                           replace(".", "").split("csv")[0] + "TypeLimit"
                        
                        schTypeLimitStr = "ScheduleTypeLimits,\t!Schedule Type\n" + \
                                          schTypeLimitName + ",\t! Name\n" + \
                                          lowerLimit.strip() + ",\t!- Lower Limit Value\n" + \
                                          upperLimit.strip() + ",\t!- Upper Limit Value\n" + \
                                          numericType.strip() + ",\t!- Numeric Type\n" + \
                                          unitType.strip() + ";\t!- Unit Type\n\n"
                elif lineCount == 2:
                    # check timestep
                    try: numOfHours *= int(line.split(",")[0])
                    except: pass
        
        # scheduleStr writes the section Schedule:File in the EnergyPlus file
        # for custom schedules.
        if schTypeLimitName in self.schedTypLims:
            scheduleStr = ''
        else:
            scheduleStr = schTypeLimitStr
        
        scheduleStr = scheduleStr + \
            "Schedule:File,\n" + \
            scheduleObjectName + ",\t!- Name\n" + \
            schTypeLimitName + ",\t!- Schedule Type Limits Name\n" + \
            scheduleNewAddress + ",\t!- File Name\n" + \
            "5,\t!- Column Number\n" + \
            "4,\t!- Rows To Skip\n" + \
            str(int(numOfHours)) + ",\t!- Hours of Data\n" + \
            "Comma;\t!- Column Separator\n"
        
        self.schedTypLims.append(schTypeLimitName)
        
        return scheduleStr
    
    def EPNatVentSimple(self, zone, natVentCount):
        if zone.natVentSchedule[natVentCount] == None: natVentSched = 'ALWAYS ON'
        elif zone.natVentSchedule[natVentCount].upper().endswith('CSV'):
            natVentSchedFileName = os.path.basename(zone.natVentSchedule[natVentCount])
            natVentSched = "_".join(natVentSchedFileName.split(".")[:-1])
        else: natVentSched = zone.natVentSchedule[natVentCount]
        
        return '\nZoneVentilation:WindandStackOpenArea,\n' + \
                '\t' + zone.name + 'NatVent' + str(natVentCount) + ',  !- Name\n' + \
                '\t' + zone.name + ',  !- Zone Name\n' + \
                '\t' + str(zone.windowOpeningArea[natVentCount]) + ',  !- Opening Area\n' + \
                '\t' + natVentSched + ',  !- Nat Vent Schedule\n' + \
                '\t' + str(zone.natVentWindDischarge[natVentCount]) + ',   !- Opening Effectiveness\n' + \
                '\t' + str(zone.windowAngle[natVentCount]) + ',  !- Effective Angle\n' + \
                '\t' + str(zone.windowHeightDiff[natVentCount]) + ', !- Height Difference\n' + \
                '\t' + str(zone.natVentStackDischarge[natVentCount]) + ',    !- Discharge Coefficient for Opening\n' + \
                '\t' + str(zone.natVentMinIndoorTemp[natVentCount])  + ',     !- Minimum Indoor Temperature\n' + \
                '\t' + ',     !- Minimum Indoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxIndoorTemp[natVentCount])  + ',     !- Maximum Indoor Temperature\n' + \
                '\t' + ',     !- Maximum Indoor Temperature Shcedule Name\n' + \
                '\t' + '-100'  + ',     !- Delta Temperature\n' + \
                '\t' + ',     !- Delta Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMinOutdoorTemp[natVentCount])  + ',     !- Minimum Outdoor Temperature\n' + \
                '\t' + ',     !- Minimum Outdoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxOutdoorTemp[natVentCount])  + ',     !- Maximum Outdoor Temperature\n' + \
                '\t' + ',     !- Maximum Outdoor Temperature Shcedule Name\n' + \
                '\t' + '40' + ';                        !- Maximum Wind Speed\n'
    
    def EPNatVentFan(self, zone, natVentCount):
        if zone.natVentSchedule[natVentCount] == None:
            natVentSched = 'ALWAYS ON'
        elif zone.natVentSchedule[natVentCount].upper().endswith('CSV'):
            natVentSchedFileName = os.path.basename(zone.natVentSchedule[natVentCount])
            natVentSched = "_".join(natVentSchedFileName.split(".")[:-1])
        else: natVentSched = zone.natVentSchedule[natVentCount]
        
        return '\nZoneVentilation:DesignFlowRate,\n' + \
                '\t' + zone.name + 'NatVent' + str(natVentCount) + ',  !- Name\n' + \
                '\t' + zone.name + ',  !- Zone Name\n' + \
                '\t' + natVentSched + ',  !- Nat Vent Schedule\n' + \
                '\t' + 'Flow/Zone' + ',  !- Design Flow Rate Calculation Method\n' + \
                '\t' + str(zone.fanFlow[natVentCount]) + ',   !- Design flow rate m3/s\n' + \
                '\t' + ',  !- Design flow rate per floor area\n' + \
                '\t' + ', !- Flow Rate per person\n' + \
                '\t' + ',    !- Air chancges per hour\n' + \
                '\t' + 'Intake' + ',  !- Ventilation Type\n' + \
                '\t' + str(zone.FanPressure[natVentCount]) + ',   !- Fan Pressure Rise (Pa)\n' + \
                '\t' + str(zone.FanEfficiency[natVentCount]) + ',   !- Fan Efficiency (Pa)\n' + \
                '\t' + '1' + ',  !- Constant Term Coefficient\n' + \
                '\t' + '0' + ',  !- Temperature Term Coefficient\n' + \
                '\t' + '0' + ',  !- Velocity Term Coefficient\n' + \
                '\t' + '0' + ',  !- Velocity Squared Term Coefficient\n' + \
                '\t' + str(zone.natVentMinIndoorTemp[natVentCount])  + ',     !- Minimum Indoor Temperature\n' + \
                '\t' + ',     !- Minimum Indoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxIndoorTemp[natVentCount])  + ',     !- Maximum Indoor Temperature\n' + \
                '\t' + ',     !- Maximum Indoor Temperature Shcedule Name\n' + \
                '\t' + '-100'  + ',     !- Delta Temperature\n' + \
                '\t' + ',     !- Delta Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMinOutdoorTemp[natVentCount])  + ',     !- Minimum Outdoor Temperature\n' + \
                '\t' + ',     !- Minimum Outdoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxOutdoorTemp[natVentCount])  + ',     !- Maximum Outdoor Temperature\n' + \
                '\t' + ',     !- Maximum Outdoor Temperature Shcedule Name\n' + \
                '\t' + '40' + ';                        !- Maximum Wind Speed\n'
    
    def EPHoliday(self, date, count):
        
        return '\nRunPeriodControl:SpecialDays,\n' + \
                '\t' + 'Holiday' + str(count) + ',  !- Name\n' + \
                '\t' + date.split(' ' )[0] + '/' + date.split(' ')[1] + ',  !- Date\n' + \
                '\t' + '1' + ',  !- Duration\n' + \
                '\t' + 'Holiday' + ';  !- Special Day Type\n'



class RunOPS(object):
    def __init__(self, model, weatherFilePath, HBZones, simParameters, openStudioLibFolder, csvSchedules, \
            csvScheduleCount, additionalcsvSchedules, shadeCntrlToReplace, replaceShdCntrl, windowSpectralData):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.openStudioDir = "/".join(openStudioLibFolder.split("/")[:3]) + "/share/openstudio"
        self.EPFolder = self.getEPFolder()
        self.EPPath = ops.Path(self.EPFolder + "\EnergyPlus.exe")
        self.epwFile = ops.Path(weatherFilePath)
        self.iddFile = ops.Path(self.EPFolder + "\Energy+.idd")
        self.model = model
        self.HBZones = HBZones
        self.simParameters = simParameters
        self.csvSchedules = csvSchedules
        self.csvScheduleCount = csvScheduleCount
        self.additionalcsvSchedules = additionalcsvSchedules
        self.shadeCntrlToReplace = shadeCntrlToReplace
        self.replaceShdCntrl = replaceShdCntrl
        self.windowSpectralData = windowSpectralData
        self.hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    def getEPFolder(self):
        fList = os.listdir(self.openStudioDir)
        for f in fList:
            fullpath = os.path.join(self.openStudioDir, f)
            if os.path.isdir(fullpath) and f.startswith("EnergyPlus"):
                return fullpath
            else:
                raise Exception("Failed to find EnergyPlus folder at %s." % self.openStudioDir)
    
    def osmToidf(self, workingDir, projectName, osmPath):
        # create a new folder to run the analysis
        projectFolder =os.path.join(workingDir, projectName)
        
        try: os.mkdir(projectFolder)
        except: pass
        
        idfFolder = os.path.join(projectFolder)
        idfFilePath = ops.Path(os.path.join(projectFolder, "ModelToIdf", "in.idf"))
        
        forwardTranslator = ops.EnergyPlusForwardTranslator()
        workspace = forwardTranslator.translateModel(self.model)
        
        # remove the current object
        tableStyleObjects = workspace.getObjectsByType(ops.IddObjectType("OutputControl_Table_Style"))
        for obj in tableStyleObjects: obj.remove()
        
        tableStyle = ops.IdfObject(ops.IddObjectType("OutputControl_Table_Style"))
        tableStyle.setString(0, "CommaAndHTML")
        workspace.addObject(tableStyle)
        
        workspace.save(idfFilePath, overwrite = True)
        
        """
        Code added by chriswmackey to add the following capabilities that do not yet exist in OS:
        Simple Natural Ventilation
        CSV Schedules
        Additional IDF Strings
        """
        self.writeNonOSFeatures(idfFilePath, self.HBZones, self.simParameters, workingDir)
        
        
        return idfFolder, idfFilePath
    
    
    def writeNonOSFeatures(self, idfFilePath, HBZones, simParameters, workingDir):
        # Go through the lines of the exiting IDF and find and references to CSV schedules.
        wrongLineTrigger = True
        fi = open(str(idfFilePath),'r')
        fi.seek(0)
        lines=[]
        foundCSVSchedules = []
        for lineCount, line in enumerate(fi):
            if 'Schedule:' in line:
                lines.append(line)
                wrongLineTrigger = True
            elif 'CSV' in line or 'csv' in line:
                origName = line.split(',')[0]
                newName = origName.split('\\')[-1].split('.')[0]
                if origName not in foundCSVSchedules:
                    foundCSVSchedules.append(origName)
                if wrongLineTrigger ==True: lines.append(line)
                else: lines.append(line.replace(origName, newName))
            elif wrongLineTrigger == True:
                wrongLineTrigger = False
                lines.append(line)
            else:
                lines.append(line)
        fi.close()
        
        #Write in any CSV schedules.
        otherFeatureClass = EPFeaturesNotInOS(workingDir)
        for schedule in self.csvSchedules:
            lines.append(otherFeatureClass.createCSVSchedString(schedule))
        for schedule in self.additionalcsvSchedules:
            lines.append(otherFeatureClass.createCSVSchedString(schedule))
        
        # If a start day of the week is specified, change it.
        counter = 0
        swapTrigger = False
        for lCount, line in enumerate(lines):
            if 'RunPeriod,' in line:
                swapTrigger = True
            if swapTrigger == True:
                counter += 1
            if counter == 7:
                if simParameters[8] != None:
                    lines[lCount] = simParameters[8] + ',\n'
                else:
                    lines[lCount] = "UseWeatherFile" + ',\n'
        
        # Write in any Holidays.
        if simParameters[7] != []:
            for count, hol in enumerate(simParameters[7]):
                lines.append(otherFeatureClass.EPHoliday(hol, count))
        
        # Replace any incorrect shading control objects.
        if self.replaceShdCntrl == True:
            # Remove shading control objects from the file.
            newLines = []
            winPropTrigger = False
            for line in lines:
                if 'WindowProperty:ShadingControl,' in line:
                    winPropTrigger = True
                elif winPropTrigger == True and ';' in line:
                    winPropTrigger = False
                elif winPropTrigger == True: pass
                else:
                    newLines.append(line)
            lines = newLines
            
            for shdCntrlItem in self.shadeCntrlToReplace:
                # Add correct shading control objects to file.
                shdCntrlName = shdCntrlItem[0]
                values = self.hb_EPObjectsAux.getEPObjectDataByName(shdCntrlName)
                if not values[4][0].endswith('.CSV'):
                    shdCntrlStr = self.hb_EPObjectsAux.getEPObjectsStr(shdCntrlName)
                else:
                    newSchedName = os.path.basename(values[4][0]).replace('.CSV', '')
                    initStr = self.hb_EPObjectsAux.getEPObjectsStr(shdCntrlName)
                    shdCntrlStr = initStr.replace(values[4][0], newSchedName)
                    shdCntrlName = shdCntrlName.replace(values[4][0], newSchedName)
                
                shdCntrlStrList = shdCntrlStr.split(shdCntrlName)
                shdCntrlStr = shdCntrlStrList[0] + str(shdCntrlItem[1]) + shdCntrlStrList[1]
                lines.append(shdCntrlStr)
        
        # Write in any requested natural ventilation objects.
        # Find any natural ventilation objects on the Zones.
        natVentStrings = []
        for zone in HBZones:
            if zone.natVent == True:
                for natVentCount, natVentObj in enumerate(zone.natVentType):
                    if natVentObj == 1 or natVentObj == 2:
                        natVentStrings.append(otherFeatureClass.EPNatVentSimple(zone, natVentCount))
                    elif natVentObj == 3:
                        natVentStrings.append(otherFeatureClass.EPNatVentFan(zone, natVentCount))
        # Write the natural ventilation objects into the IDF.
        if len(natVentStrings) > 0:
            for line in natVentStrings:
                lines.append(line)
        
        # Write in any window spectral data.
        if self.windowSpectralData != {}:
            # First, I have to write in the name of the spectral data on the glass materials.
            glazTrigger = False
            matName = None
            for lcount, line in enumerate(lines):
                if 'WindowMaterial:Glazing' in line:
                    glazTrigger = True
                elif line == '\n':
                    glazTrigger = False
                elif glazTrigger == True and '!- Name' in line:
                    matName = line.split(',')[0].strip()
                elif glazTrigger == True and '!- Window Glass Spectral Data Set Name' in line:
                    lines[lcount] = '  ' + self.windowSpectralData[matName] + ',     !- Window Glass Spectral Data Set Name\n'
            for matName in self.windowSpectralData.keys():
                spectDatStr = self.hb_EPObjectsAux.getEPObjectsStr(self.windowSpectralData[matName])
                lines.append(spectDatStr)
        
        # Write in a request for the surface names in the .eio file.
        lines.append('\nOutput:Surfaces:List,\n')
        lines.append('\t' + 'Details;                 !- Report Type' + '\n')
        
        # Write any additional strings.
        if additionalStrings_ != []:
            lines.append("\n")
            for string in additionalStrings_:
                if ":" in string and not '!' in string:
                    lines.append("\n")
                    lines.append("\n")
                    lines.append(string)
                elif "!" not in string:
                    lines.append("\n")
                    lines.append("\n")
                    lines.append(string)
                    lines.append("\n")
                else:
                    lines.append(string)
                    lines.append("\n")
            lines.append("\n")
        
        fiw = open(str(idfFilePath),'w')
        for line in lines:
            fiw.write(line)
        fiw.close()
    
    
    def runAnalysis(self, osmFile, runEnergyPlus, useRunManager = False):
        
        # Preparation
        workingDir, fileName = os.path.split(osmFile)
        projectName = (".").join(fileName.split(".")[:-1])
        osmPath = ops.Path(osmFile)
        
        # create idf - I separated this job as putting them together
        # was making EnergyPlus to crash
        idfFolder, idfPath = self.osmToidf(workingDir, projectName, osmPath)
        print 'OSM > IDF: ' + str(idfPath)
        
        if runEnergyPlus < 3:
            if not useRunManager:
                resultFile = self.writeBatchFile(idfFolder, "ModelToIdf\\in.idf", self.weatherFile, runEnergyPlus > 1)
                return os.path.join(idfFolder, "ModelToIdf", "in.idf"), resultFile
            
            outputPath = ops.Path(idfFolder)
            
            rmDBPath = ops.Path(os.path.join(idfFolder, projectName + ".db"))
            try:
                rm = ops.RunManager(rmDBPath, True, True, False, False)
                
                # set up tool info to pass to run manager
                energyPlusTool = ops.ToolInfo(self.EPPath)
                toolInfo = ops.Tools()
                toolInfo.append(energyPlusTool)
                
                # get manager configration options
                configOptions = rm.getConfigOptions()
                
                EPRunJob = ops.JobFactory.createEnergyPlusJob(energyPlusTool, self.iddFile, idfPath,
                                                   self.epwFile, outputPath)
                
                # put in queue and let it go
                rm.enqueue(EPRunJob, True)
                rm.setPaused(False)
                
                # This make Rhino and NOT Grasshopper to crash
                # I should send this as a discussion later
                #rm.showStatusDialog()
                
                while rm.workPending():
                    time.sleep(1)
                    print "Running simulation..."
                #    print "Process Event:" + str(ops.Application.instance().processEvents())
                jobErrors = EPRunJob.errors()
                #    print jobErrors.succeeded()
                
                # print "Process: " + str(ops.Application.instance().processEvents())
                print "Errors and Warnings:"
                for msg in list(jobErrors.errors()):
                    print msg
                    
                rm.Dispose() # don't remove this as Rhino will crash if you don't dispose run manager
                
                if jobErrors.succeeded():
                    return os.path.join(idfFolder, "ModelToIdf", "in.idf"), idfFolder + "\\EnergyPlus\\epluszsz.csv"
                else:
                    return None, None
                    
            except Exception, e:
                 rm.Dispose() # in case anything goes wrong it closes the rm
                 print `e`
        else:
            return os.path.join(idfFolder, "ModelToIdf", "in.idf"), None
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress, runInBackground = False):
        """
        This is here as an alternate until I can get RunManager to work
        """
        EPDirectory = self.EPFolder
        workingDrive = workingDir[:2]
        if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
        else: shIdfFileName = idfFileName
        
        if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
        
        fullPath = workingDir + shIdfFileName
        folderName = workingDir.replace( (workingDrive + '\\'), '')
        batchStr = workingDrive + '\ncd\\' +  folderName + '\n"' + EPDirectory + \
                '\\Epl-run" ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'
    
        batchFileAddress = fullPath +'.bat'
        batchfile = open(batchFileAddress, 'w')
        batchfile.write(batchStr)
        batchfile.close()
        
        #execute the batch file
        if runInBackground:
            self.runCmd(batchFileAddress)
        else:
            os.system(batchFileAddress)
        
        return fullPath + "Zsz.csv",fullPath+".sql",fullPath+".csv", fullPath+".rdd", fullPath+".eio"
    
    def runCmd(self, batchFileAddress, shellKey = True):
        batchFileAddress.replace("\\", "/")
        p = subprocess.Popen(["cmd /c ", batchFileAddress], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)		
        out, err = p.communicate()


def main(HBZones, HBContext, north, epwWeatherFile, analysisPeriod, simParameters, simulationOutputs, runIt, openOpenStudio, workingDir = "C:\ladybug", fileName = "openStudioModel.osm"):
    # check the release
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    units = sc.doc.ModelUnitSystem
    if `units` != 'Rhino.UnitSystem.Meters':
        msg = "Currently the OpenStudio component only works in meters. Change the units to Meters and try again!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    # version check
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
     
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1    
        
    # make sure epw file address is correct
    if not os.path.isfile(epwWeatherFile):
        msg = "EPW weather file does not exist in the specified location!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    # Import all classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_reEvaluateHBZones= sc.sticky["honeybee_reEvaluateHBZones"]
    
    # Set up the folder structure.
    if fileName == None: 
         fileName = "unnamed"
    
    if workingDir == None:
        workingDir = sc.sticky["Honeybee_DefaultFolder"] 
        originalWorkDir = os.path.join(workingDir, fileName)
    else:
        originalWorkDir = copy.copy(workingDir)
    
    subWorkingDir = lb_preparation.makeWorkingDir(os.path.join(workingDir, fileName, "OpenStudio")).replace("\\\\", "\\")
    
    print 'Current working directory is set to: ', subWorkingDir
    
    # remove current folder
    try:
        lb_preparation.nukedir(subWorkingDir, rmdir = False)
    except:
        pass
    fname = os.path.join(subWorkingDir, fileName + ".osm")
    
    # initiate OpenStudio model
    model = ops.Model()
    
    hb_writeOPS = WriteOPS(simParameters, epwWeatherFile)
    
    #set runningPeriod
    hb_writeOPS.setRunningPeriod(analysisPeriod, model)
    
    # set timestep
    hb_writeOPS.setTimestep(model)
    
    # set holidays
    hb_writeOPS.setHolidays(model)
    
    # set start day of week.
    #hb_writeOPS.setStartDayOfWeek(model)
    
    # set north
    hb_writeOPS.setNorth(north, model)
    
    # set site.
    hb_writeOPS.setSite(epwWeatherFile, model)
    
    # set terrain.
    hb_writeOPS.setTerrain(model)
    
    # set ground temperatures.
    hb_writeOPS.setGroundTemps(model)
    
    # set simulation control
    hb_writeOPS.setSimulationControls(model)
    
    # set shadow calculation parameters
    hb_writeOPS.setShadowCalculation(model)
    
    # set hvac suzung factor
    hb_writeOPS.setSizingFactors(model)
    
    # add design days
    ddyFound = hb_writeOPS.addDesignDays(model)
    if ddyFound == False:
        # Create a ddy file from the information in the EPW.
        hb_writeOPS.createDdyFromEPW(epwWeatherFile, subWorkingDir, lb_preparation, lb_comfortModels)
        hb_writeOPS.addDesignDays(model)
    
    # call Honeybee objects from the hive
    HBZones = hb_hive.callFromHoneybeeHive(HBZones)
    
    reEvaluate = hb_reEvaluateHBZones(HBZones, None, "UpperLeftCorner")
    reEvaluate.evaluateZones()
    
    # generate stories
    hb_writeOPS.generateStories(HBZones, model)
    
    #Make a list of schedules to keep track of what needs to be written into the model.
    additionalSchedList = []
    additionalcsvSchedules = []
    
    for zoneCount, zone in enumerate(HBZones):
        # create a space - OpenStudio works based of space and not zone
        # Honeybee though is structured based on zones similar to EnergyPlus
        space = ops.Space(model)
        
        # assign name and type
        space = hb_writeOPS.setupNameAndType(zone, space, model)
        
        # assign level/building story to zone
        space = hb_writeOPS.setupLevels(zone, space)
        
        # schedules
        space = hb_writeOPS.setDefaultSchedule(zone, space, model)
        
        #   INFILTRATION
        hb_writeOPS.setInfiltration(zone, space, model)
        
        # set people definition
        hb_writeOPS.setPeopleDefinition(zone, space, model)
        
        # set people definition
        hb_writeOPS.setLightingDefinition(zone, space, model)
        
        # set electrical equipment
        hb_writeOPS.setEquipmentDefinition(zone, space, model)
        
        # design specification outdoor air
        space = hb_writeOPS.setDesignSpecificationOutdoorAir(zone, space, model)
        
        # assign the thermal zone
        space, thermalZone = hb_writeOPS.assignThermalZone(zone, space, model)
        
        #Keep the thermal zones in a dictionary for later.
        hb_writeOPS.thermalZonesDict[zone.name] = thermalZone
        
        #If there are internal masses assigned to the zone, write them
        if len(zone.internalMassNames) > 0:
            for massCount, massName in enumerate(zone.internalMassNames):
               hb_writeOPS.setInternalMassDefinition(zone, space, model)
        
        if zone.isConditioned:
            # add HVAC system
            HAVCGroupID = zone.HVACSystem.GroupID
            
            if HAVCGroupID!= -1:
                if HAVCGroupID not in hb_writeOPS.HVACSystemDict.keys():
                    # add place holder for lists
                    hb_writeOPS.HVACSystemDict[HAVCGroupID] = HoneybeeHVAC(HAVCGroupID, zone.HVACSystem.Index, [], [], zone.HVACSystem.airDetails, zone.HVACSystem.heatingDetails, zone.HVACSystem.coolingDetails, zoneCount)
            
            # collect the information for systems here, such as the zones in each system and the recirculation specifcations for each zone.
            hb_writeOPS.HVACSystemDict[HAVCGroupID].thermalZones.append(thermalZone)
            hb_writeOPS.HVACSystemDict[HAVCGroupID].hbZones.append(zone)
            
            # add thermostat
            hb_writeOPS.addThermostat(zone, thermalZone, space, model)
            
            # add humidistat if specified
            if zone.humidityMax != "" or zone.humidityMin != "":
                hb_writeOPS.addHumidistat(zone, thermalZone, space, model)
            
            # add daylighting controls
            if zone.daylightCntrlFract != 0:
                hb_writeOPS.addDaylightCntrl(zone, thermalZone, space, model)
        
        # write the surfaces
        for HBSrf in zone.surfaces:
            OPSSrf = hb_writeOPS.opsZoneSurface(HBSrf, model, space)
            if HBSrf.hasChild:
                    hb_writeOPS.OPSFenSurface(HBSrf, OPSSrf, model)
                    
        
        #Check other schedules.
        if zone.natVent == True:
            for ventObj in zone.natVentSchedule:
                if ventObj != None:
                    if ventObj.upper().endswith('.CSV'): additionalcsvSchedules.append(ventObj)
                    else: additionalSchedList.append(ventObj)
                elif 'ALWAYS ON' not in additionalSchedList: additionalSchedList.append('ALWAYS ON')
    
    #Add and extra schedules pulled off of the zones.
    for schedName in additionalSchedList:
        ossch = hb_writeOPS.getOSSchedule(schedName, model)
    
    # this should be done once for the whole model
    hb_writeOPS.setAdjacentSurfaces()
    
    # add systems
    hb_writeOPS.addSystemsToZones(model)
    
    # add zone air mixing objects.
    for zoneCount, zone in enumerate(HBZones):
        if zone.mixAir == True: hb_writeOPS.setAirMixing(zone, model)
    
    # outputs
    defaultOutputs = ['Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Energy, hourly;',\
        'Output:Variable,*,Cooling Coil Electric Energy, hourly;',\
        'Output:Variable,*,Chiller Electric Energy, hourly;',\
        'Output:Variable,*,Zone Ideal Loads Supply Air Total Heating Energy, hourly;',\
        'Output:Variable,*,Boiler Heating Energy, hourly;',\
        'Output:Variable,*,Heating Coil Total Heating Energy, hourly;',\
        'Output:Variable,*,Heating Coil Gas Energy, hourly;',\
        'Output:Variable,*,Heating Coil Electric Energy, hourly;',\
        'Output:Variable,*,Humidifier Electric Energy, hourly;',\
        'Output:Variable,*,Fan Electric Energy, hourly;',\
        'Output:Variable,*,Zone Ventilation Fan Electric Energy, hourly;',\
        'Output:Variable,*,Zone Lights Electric Energy, hourly;',\
        'Output:Variable,*,Zone Electric Equipment Electric Energy, hourly;',\
        'Output:Variable,*,Pump Electric Energy, hourly;',\
        'Output:Variable,*,Zone VRF Air Terminal Cooling Electric Energy, hourly;',\
        'Output:Variable,*,Zone VRF Air Terminal Heating Electric Energy, hourly;',\
        'Output:Variable,*,VRF Heat Pump Cooling Electric Energy, hourly;',\
        'Output:Variable,*,VRF Heat Pump Heating Electric Energy, hourly;']
    if simulationOutputs:
        outputs = simulationOutputs
    else:
       outputs = defaultOutputs
    hb_writeOPS.setOutputs(outputs, model)
    
    # add shading surfaces if any
    if HBContext!=[] and HBContext[0]!=None:
        shdingSurfcaes = hb_hive.callFromHoneybeeHive(HBContext)
        hb_writeOPS.OPSShdSurface(shdingSurfcaes, model)
    
    # Get the objects in the file that we need to replace or add because OpenStudio does not support them.
    csvSchedules, csvScheduleCount, shadeCntrlToReplace, replaceShdCntrl, windowSpectralData = hb_writeOPS.getObjToReplace()
    
    #save the model
    model.save(ops.Path(fname), True)
    
    print "Model saved to: " + fname
    workingDir, fileName = os.path.split(fname)
    projectName = (".").join(fileName.split(".")[:-1])
    
    if openOpenStudio:
        os.startfile(fname)
    
    if runIt > 0:
        hb_runOPS = RunOPS(model, epwWeatherFile, HBZones, hb_writeOPS.simParameters, openStudioLibFolder, csvSchedules, \
            csvScheduleCount, additionalcsvSchedules, shadeCntrlToReplace, replaceShdCntrl, windowSpectralData)
        
        idfFile, resultFile = hb_runOPS.runAnalysis(fname, runIt, useRunManager = False)
        if runIt < 3:
            try:
                errorFileFullName = idfFile.replace('.idf', '.err')
                errFile = open(errorFileFullName, 'r')
                for line in errFile:
                    print line
                    if "**  Fatal  **" in line:
                        warning = "The simulation has failed because of this fatal error: \n" + str(line)
                        w = gh.GH_RuntimeMessageLevel.Warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                        resultFile = None
                    elif "** Severe  **" in line and 'CheckControllerListOrder' not in line:
                        comment = "The simulation has not run correctly because of this severe error: \n" + str(line)
                        c = gh.GH_RuntimeMessageLevel.Warning
                        ghenv.Component.AddRuntimeMessage(c, comment)
                errFile.close()
            except:
                pass
        
        return fname, idfFile, resultFile, originalWorkDir, model
        
    return fname, None, None, originalWorkDir, model

if _HBZones and _HBZones[0]!=None and _epwWeatherFile and _writeOSM and openStudioIsReady:
    results = main(_HBZones, HBContext_, north_, _epwWeatherFile,
                  _analysisPeriod_, _energySimPar_, simulationOutputs_,
                  runSimulation_, openOpenStudio_, workingDir_, fileName_)
    if results!=-1:
        osmFileAddress, idfFileAddress, resultsFiles, studyFolder, model = results
        try:
            
            resultsFileAddress = resultsFiles[2]
            eioFileAddress = resultsFiles[4]
            rddFileAddress = resultsFiles[3]
            sqlFileAddress = resultsFiles[1]
            meterFileAddress = resultsFiles[0]
        except: resultsFileAddress = resultsFiles
