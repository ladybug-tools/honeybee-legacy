#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Provided by Honeybee 0.0.58
    
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
        +++++++++++++++: ...
        _writeOSM: Set to "True" to have the component take your HBZones and other inputs and write them into an OSM file.  The file path of the resulting OSM file will appear in the osmFileAddress output of this component.  Note that only setting this to "True" and not setting the output below to "Tru"e will not automatically run the file through EnergyPlus for you.
        runSimulation_: Set to "True" to have the component run your OSM file through EnergyPlus once it has finished writing it.  This will ensure that a CSV result file appears in the resultFileAddress output.
        fileName_: Optional text which will be used to name your OSM, IDF and result files.  Change this to aviod over-writing results of previous energy simulations.
        workingDir_: An optional working directory to a folder on your system, into which your OSM, IDF and result files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
    Returns:
        report: Check here to see a report of the EnergyPlus run, including errors.
        osmFileAddress: The file path of the OSM file that has been generated on your machine.
        idfFileAddress: The file path of the IDF file that has been generated on your machine. This only happens when you set "runSimulation_" to "True."
        resultFileAddress: The file path of the CSV result file that has been generated on your machine.  This only happens when you set "runSimulation_" to "True."
        sqlFileAddress: The file path of the SQL result file that has been generated on your machine. This only happens when you set "runSimulation_" to "True."
        meterFileAddress: The file path of the building's meter result file that has been generated on your machine. This only happens when you set "runSimulation_" to "True."
"""

ghenv.Component.Name = "Honeybee_Export To OpenStudio"
ghenv.Component.NickName = 'exportToOpenStudio'
ghenv.Component.Message = 'VER 0.0.58\nJAN_13_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nOCT_31_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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

rc.Runtime.HostUtils.DisplayOleAlerts(False)

if sc.sticky.has_key('honeybee_release'):
    
    installedOPS = [f for f in os.listdir("C:\\Program Files") if f.startswith("OpenStudio")]
    installedOPS = sorted(installedOPS, key = lambda x: int("".join(x.split(" ")[-1].split("."))), reverse = True)
    
    openStudioLibFolder = "C:/Program Files/%s/CSharp/openstudio/"%installedOPS[0]
    
    if os.path.isdir(openStudioLibFolder) and os.path.isfile(os.path.join(openStudioLibFolder, "openStudio.dll")):
        # openstudio is there
        # I need to add a function to check the version and compare with available version
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
        msg = "Cannot find OpenStudio libraries at " + openStudioLibFolder + \
              "\nYou need to download and install OpenStudio to be able to use this component."
              
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    
#    if openStudioIsReady and sc.sticky.has_key('honeybee_release') and \
#        sc.sticky.has_key("isNewerOSAvailable") and sc.sticky["isNewerOSAvailable"]:
#        # check if there is an update available
#        msg1 = "There is a newer version of OpenStudio libraries available to download! " + \
#                      "We strongly recommend you to download the newer version from this link and replace it with current files at " + \
#                      openStudioLibFolder +"."
#        msg2 = "https://dl.dropboxusercontent.com/u/16228160/Honeybee/OpenStudio.zip"
#        print msg1
#        print msg2
#        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
#        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False


class WriteOPS(object):

    def __init__(self, EPParameters, weatherFilePath):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        self.hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        self.hb_EPPar = sc.sticky["honeybee_EPParameters"]()
        self.simParameters = self.hb_EPPar.readEPParams(EPParameters)
        
        if self.simParameters[4] != None: self.ddyFile = self.simParameters[4]
        else: self.ddyFile = weatherFilePath.replace(".epw", ".ddy", 1)
        
        self.constructionList = sc.sticky ["honeybee_constructionLib"]
        self.materialList = {}
        self.scheduleList = {}
        self.bldgTypes = {}
        self.levels = {}
        self.HVACSystemDict = {}
        self.adjacentSurfacesDict = {}
        
        self.csvSchedules = []
        self.csvScheduleCount = 0
    
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
        building.setNorthAxis(northAngle)
    
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
    
    def addDesignDays(self, model):
        ddyFile = self.ddyFile
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
                
        model.addObjects(selectedDesignDays)
        
    def isConstructionInLib(self, constructionName):
        return constructionName in self.constructionList.keys()
    
    def addConstructionToLib(self, constructionName, construction):
        self.constructionList[constructionName] = construction
    
    def getConstructionFromLib(self, constructionName, model):
        return self.getOSConstruction(constructionName.upper(), model)
    
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
            sscheduleConstant.setScheduleTypeLimits(self.getScheduleFromLib(typeLimitName))
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
                #print 'here ' + scheduleTypeLimitsName
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
    
    def assignThermalZone(self, zone, space, model):
        thermalZone = ops.ThermalZone(model)
        ops.OpenStudioModelHVAC.setThermalZone(space, thermalZone)
        #thermalZone.setName("thermalZone_" + zone.name)
        # This is a temporary change to make the component work with the current result reader
        # Will change it to what it used to be later
        thermalZone.setName(zone.name)
        return space, thermalZone
    
        
        
    def recallAvailManager(self,HVACDetails):
        return HVACDetails['availabilityManagerList']
    
    def updateAvailManager(self,availManager,OSComponent, model):
        #avail manager is the user's definition
        #OS component is the OpenStudio object being updated
        #print availManager
        #print type(OSComponent) - AirLoopHVAC
        #get the availability List Manager
        #set the avail manager list name
        #set the schedule of the availability manager
        #set the night cycle controls, when applicable
        if availManager != None:
            # availManager should be a dict.
            
            if availManager['type'] == 'NightCycle':
                try:
                    OSComponent.setNightCycleControlType(availManager['controlType'])
                    print 'set night cycle availability manager to: '+ availManager['type'] 
                except:
                    print 'Error: OSComponent '+str(OSComponent)+' cannot set night cycle availability manager!!'
            elif availManager['type'] == 'Scheduled':
                try:
                    availSch = self.getOSSchedule(availManager['scheduleName'], model)
                    OSComponent.setAvailabilitySchedule(availSch)
                    print 'set availability manager to: '+availManager['type'] 
                except:
                    print 'Error: OSComponent '+str(OSComponent)+' cannot set night cycle availability manager!!'
        
        return OSComponent
        
    def recallOASys(self,HVACDetails):
        #do not modify these strings unless EnergyPlus strings change
        contrlType = {
        0:'FixedDryBulb',
        1:'DifferentialDryBulb',
        2:'FixedEnthalpy',
        3:'DifferentialEnthalpy',
        4:'ElectronicEnthalpy',
        5:'FixedDewPointAndDryBulb',
        6:'DifferentialDryBulbAndEnthalpy',
        7:'NoEconomizer'
        }
        
        ctrlAction={
        0:'ModulateFlow',
        1:'MinimumFlowWithBypass'
        }
        lockout={
        None:'NoLockout',
        0:'NoLockout',
        1:'LockoutWithHeating',
        2:'LockoutWithCompressor'
        }
        minLimit={
        0:'ProportionalMinimum',
        1:'FixedMinimum'
        }
        
        # XXX I think this is superfluous code
        if HVACDetails == None: return
        
        'airsideEconomizer'
        oaDesc = {
        'name' : HVACDetails['airsideEconomizer']['name'],
        'econoControl': HVACDetails['airsideEconomizer']['econoControl'],
        'sensedMin' : HVACDetails['airsideEconomizer']['sensedMin'],
        'sensedMax' : HVACDetails['airsideEconomizer']['sensedMax'],
        'maxLimitDewpoint' : HVACDetails['airsideEconomizer']['maxLimitDewpoint'],
        'minAirFlowRate' : HVACDetails['airsideEconomizer']['minAirFlowRate'],
        'maxAirFlowRate' : HVACDetails['airsideEconomizer']['maxAirFlowRate'],
        'minLimitType' : HVACDetails['airsideEconomizer']['minLimitType'],
        'controlAction' : HVACDetails['airsideEconomizer']['controlAction'],
        'minOASchedule' : HVACDetails['airsideEconomizer']['minOutdoorAirSchedule'],
        'minOAFracSchedule' : HVACDetails['airsideEconomizer']['minOutdoorAirFracSchedule'],
        'maxOAFracSchedule' : HVACDetails['airsideEconomizer']['maxOutdoorAirFracSchedule'],
        'DXLockoutMethod' : HVACDetails['airsideEconomizer']['DXLockoutMethod'],
        'timeOfDaySch':HVACDetails['airsideEconomizer']['timeOfDaySch'],
        'mvCtrl':HVACDetails['airsideEconomizer']['mvCtrl']
        }
        return oaDesc
        
    def updateOASys(self,econo,oactrl,model):
        if econo == None: return
        if econo['econoControl'] == "FixedDryBulb":
            oactrl.setEconomizerControlType("FixedDryBulb")
            if econo['sensedMin'] != None:
                mindb = econo['sensedMin']
            if econo['sensedMax'] != None:
                maxdb = econo['sensedMax']
                oactrl.setEconomizerMinimumLimitDryBulbTemperature(mindb)
                oactrl.setEconomizerMaximumLimitDryBulbTemperature(maxdb)
        elif econo['econoControl'] == "DifferentialDryBulb":
            oactrl.setEconomizerControlType("DifferentialDryBulb")
        elif econo['econoControl'] == "FixedEnthalpy":
            oactrl.setEconomizerControlType("FixedEnthalpy")
            if sensedMax != None:
                maxenth = econo['sensedMax']
                oactrl.setEconomizerMaximumLimitEnthalpy(maxenth)
                #can sensed min still be dry bulb?
        elif econo['econoControl'] == "DifferentialEnthalpy":
            oactrl.setEconomizerControlType("DifferentialEnthalpy")
        elif econo['econoControl'] == "ElectronicEnthalpy":
            oactrl.setEconomizerControlType("ElectronicEnthalpy")
            #set curve in future releases
        elif econo['econoControl'] == "FixedDewpointAndDryBulb":
            oactrl.setEconomizerControlType("FixedDewpointAndDryBulb")
            if econo['sensedMin'] != None:
                mindb = econo['sensedMin']
                oactrl.setEconomizerMinimumLimitDryBulbTemperature(mindb)
            if econo['sensedMax'] != None:
                maxdb = econo['sensedMax']
                oactrl.setEconomizerMaximumLimitDryBulbTemperature(maxdb)
            if econo['maxLimitDewpoint'] != None:
                maxdp = econo['maxLimitDewpoint']
                oactrl.setEconomizerMaximumLimitDewpointTemperature(maxdp)
        elif econo['econoControl'] == "DifferentialDryBulbAndEnthalpy":
            oactrl.setEconomizerControlType("DifferentialDryBulbAndEnthalpy")
            if sensedMax != None:
                maxenth = econo['sensedMax']
                oactrl.setEconomizerMaximumLimitEnthalpy(maxenth)
        else:
            oactrl.setEconomizerControlType("NoEconomizer")
        #economizer control type set
        
        #set min and max flows
        if econo['minAirFlowRate']=='Autosize' or econo['minAirFlowRate']==None:
            oactrl.autosizeMinimumOutdoorAirFlowRate()
        else:
            minFlow = econo['minAirFlowRate']
            oactrl.setMinimumOutdoorAirFlowRate(minFlow)
        if econo['maxAirFlowRate']=='Autosize' or econo['maxAirFlowRate']==None:
            oactrl.autosizeMaximumOutdoorAirFlowRate()
        else:
            maxFlow = econo['maxAirFlowRate']
            oactrl.setMaximumOutdoorAirFlowRate(maxFlow)
        # set min and max flow rates'
        #set control action
        if econo['controlAction']!=None:
            oactrl.setEconomizerControlActionType(econo['controlAction'])
        #set control action
        #set minLimit type
        if econo['minLimitType']!=None:
            oactrl.setMinimumLimitType(econo['minLimitType'])
        # set min limit type
        #set lockout type (applies to DX systems only)
        if econo['DXLockoutMethod'] != None:
            oactrl.setLockoutType(econo['DXLockoutMethod'])
        # set dx lockout method
        if econo['timeOfDaySch'] != None:
            # updating economizer time of day schedule
            ossch = self.getOSSchedule(econo['timeOfDaySch'],model)
            oactrl.setTimeofDayEconomizerControlSchedule(ossch)
        
        if econo['mvCtrl'] != None:
            print 'updating mechanical ventilation controller'
            mv = oactrl.controllerMechanicalVentilation()
            ossch = self.getOSSchedule(econo['mvCtrl']['availSch'],model)
            mv.setAvailabilitySchedule(ossch)
            mv.setName(econo['mvCtrl']['name'])
            mv.setDemandControlledVentilation(econo['mvCtrl']['DCV'])
        if econo['minOASchedule'] != None:
            print 'updating minOA schedule'
            minOASch = self.getOSSchedule(econo['minOASchedule'],model)
            oactrl.setMinimumOutdoorAirSchedule(minOASch)
        if econo['minOAFracSchedule'] != None:
            print 'updating minOAFrac schedule'
            maxOASch = self.getOSSchedule(econo['minOAFracSchedule'],model)
            oactrl.setMinimumFractionofOutdoorAirSchedule(maxOASch)
        if econo['maxOAFracSchedule'] != None:
            print 'updating maxOAFrac schedule'
            maxOASch = self.getOSSchedule(econo['maxOAFracSchedule'],model)
            oactrl.setMinimumFractionofOutdoorAirSchedule(maxOASch)
        
        print "success for economizer!"
        return oactrl
        
    def recallCVFan(self,HVACDetails):
        print 'getting supply fan from the hive'
        sfdesc = {
        'name':HVACDetails['constVolSupplyFanDef']['name'],
        'motorEfficiency':HVACDetails['constVolSupplyFanDef']['motorEfficiency'],
        'fanEfficiency':HVACDetails['constVolSupplyFanDef']['fanEfficiency'],
        'pressureRise':HVACDetails['constVolSupplyFanDef']['pressureRise'],
        'airStreamHeatPct':HVACDetails['constVolSupplyFanDef']['airStreamHeatPct'],
        'maxFlowRate':HVACDetails['constVolSupplyFanDef']['maxFlowRate']
        }
        return sfdesc
        
    def recallEvapCondenser(self,condenserDetails):
        print 'getting your evaporative condenser details'
        evapC = {
            'name':condenserDetails['name'],
            'evapEffectiveness':condenserDetails['evapEffectiveness'],
            'evapCondAirflowRate':condenserDetails['evapCondAirflowRate'],
            'evapPumpPower':condenserDetails['evapPumpPower'],
            'storageTank':condenserDetails['storageTank'],
            'curves':condenserDetails['curves']
            }
        if condenserDetails['serviceType'] == 1:
            evapC['hiEvapEffectiveness'] = condenserDetails['hiEvapEffectiveness']
            evapC['hiEvapCondAirflowRate'] = condenserDetails['hiEvapCondAirflowRate']
            evapC['hiEvapPumpPower'] = condenserDetails['hiEvapPumpPower']
        return evapC
            
        
        
    def updateDXHeatingCoil(self,hbhc,modelhc):
    
        #right now, this only works for a one speed coil
        #will need to add something about type to distinguish between other coils
        if hbhc['type'] == 0:
            if hbhc['ratedAirflowRate'] != None:
                if hbhc['ratedAirflowRate'] != 'Autosize':
                    modelhc.setRatedAirFlowRate(hbhc['ratedAirflowRate'])
                    print 'coil rated airflow rate now set to: ' + str(hbhc['ratedAirflowRate'])
            if hbhc['ratedTotalHeating'] != None:
                if hbhc['ratedTotalHeating'] != 'Autosize':
                    modelhc.setRatedTotalHeatingCapacity(hbhc['ratedTotalHeating'])
                    print 'coil rated total heating capacity now set to: ' + str(hbhc['ratedTotalHeating'])
            if hbhc['ratedCOP'] != None:
                modelhc.setRatedCOP(hbhc['ratedCOP'])
                print 'coil rated COP now set to: ' + str(hbhc['ratedCOP'])
        elif hbhc['type'] == 1:
            pass
            #OpenStudio currently does not support 2Speed DX Coils.
        if hbhc['minOutdoorDryBulb'] != None:
            modelhc.setMinimumOutdoorDryBulbTemperatureforCompressorOperation(hbhc['minOutdoorDryBulb'])
            print "min outdoor dry bulb for compressor operation set: " + str(hbhc['minOutdoorDryBulb'])
        if hbhc['outdoorDBDefrostEnabled'] != None:
            modelhc.setMaximumOutdoorDryBulbTemperatureforDefrostOperation(hbhc['outdoorDBDefrostEnabled'])
            print 'the temperature at which the coil goes into defrost mode is: ' + str(hbhc['outdoorDBDefrostEnabled'])
        if hbhc['outdoorDBCrankcase'] != None:
            modelhc.setMaximumOutdoorDryBulbTemperatureforCrankcaseHeaterOperation(hbhc['outdoorDBCrankcase'])
            print "max crankcase temperature set to: " + str(hbhc['outdoorDBCrankcase'])
        if hbhc['crankcaseCapacity'] != None:
            modelhc.setCrankcaseHeaterCapacity(hbhc['crankcaseCapacity'])
            print 'crankcase capacity of coil now set to: ' + str(hbhc['crankcaseCapacity'])
        if hbhc['defrostStrategy'] != None:
            modelhc.setDefrostStrategy(hbhc['defrostStrategy'])
            print "defrost strategy updated to: " + hbhc['defrostStrategy']
        if hbhc['defrostControl'] != None:
            modelhc.setDefrostControl(hbhc['defrostControl'])
            print "defrost control updated to: " +hbhc['defrostControl']
        if hbhc['resistiveDefrostCap'] != None:
            modelhc.setResistiveDefrostHeaterCapacity(hbhc['resistiveDefrostCap'])
            print "resistiveDefrostHeaterCapacity set to: " + str(hbhc['resistiveDefrostCap'])
        #curves for future will be defined here
        

        return modelhc
    
    def updateCVFan(self,sf,cvfan):
        if sf['motorEfficiency'] != None: 
            cvfan.setMotorEfficiency(sf['motorEfficiency'])
            print 'motor efficiency updated'
        if sf['fanEfficiency'] != None: 
            cvfan.setFanEfficiency(sf['fanEfficiency'])
            print 'fan efficiency updated'
        if sf['pressureRise'] != None: 
            cvfan.setPressureRise(sf['pressureRise'])
            print 'pressure rise updated'
        if sf['airStreamHeatPct'] != None: 
            cvfan.setMotorInAirstreamFraction(sf['airStreamHeatPct'])
            print 'motor air stream heat updated'
        if sf['maxFlowRate'] != None:
            if sf['maxFlowRate'] != 'Autosize':
                cvfan.setMaximumFlowRate(float(sf['maxFlowRate']))
                print 'max flow rate updated'
            else:
                print 'fan size remains autosized'
        print 'success updating fan!'
        return cvfan
    
    def recallBoiler(self,plantDetails):
        return plantDetails['boiler']
    
    def recallChiller(self,plantDetails):
        return plantDetails['chiller']
        
    def recallCoolingTower(self,plantDetails):
        return plantDetails['coolingTower']
        
    def updateCoolingTower(self,utower,ostower):
        #universal commands across all three cooling towers
        ostower.setName(utower['name']) #defaults to a name always
        ostower.setNumberofCells(utower['numberOfCells']) #defaults to 1
        ostower.setSizingFactor(utower['sizingFactor']) # defaults to 1.0
        ostower.setBasinHeaterCapacity(utower['basinHeaterCapacity']) #this is zero by default
        #basin heater availablity schedule to be done in future
        ostower.setBasinHeaterSetpointTemperature(utower['basinHeaterSetpoint']) #this is 2 by default
        #all blowdown controls to be added at a later time
        if utower['cellControl'] != 'NotRequired':
            ostower.setCellControl(utower['cellControl'])
        ostower.setCellMaximumWaterFlowRateFraction(utower['cellMaxWaterFlowFraction']) #2.5 by default
        ostower.setCellMinimumWaterFlowRateFraction(utower['cellMinWaterFlowFraction']) #0.3 by default
        if utower['airflowAtHighSpeed'] != "Autosized":
            ostower.setDesignAirFlowRate(utower['airflowAtHighSpeed']) #design air flow rate
        if utower['fanPowerAtHighSpeed'] != "Autosized":
            ostower.setDesignFanPower(utower['fanPowerAtHighSpeed'])
        if utower['designWaterFlowRate'] != "Autosized":
            ostower.setDesignWaterFlowRate(utower['designWaterFlowRate'])
        if utower['speedControl'] == 'SingleSpeed':
            if utower['airflowInFreeConvection'] != 'Autosized':
                ostower.setAirFlowRateinFreeConvectionRegime(utower['airflowInFreeConvection']) #autosized by default
            #ostower.setCapacityControl(FanCycling or FluidBypass)  needs to be added to honeybee model before implementation
            #setFreeConvectionCapacity?
            #setNominalCapacity
            #setPerformanceInputMethod
            #setUFactorTimesAreaValueatDesignAirFlowRate
            #setUFactorTimesAreaValueatFreeConvectionAirFlowRate
        elif utower['speedControl'] == 'TwoSpeed':
            pass
        elif utower['speedControl'] == 'VariableSpeed':
            #setDesignApproachTemperature to be done...this is specific to vfd cooling towers
            #setDesignInletAirWetBulbTemperature appears specific to vfd tower
            #setDesignRangeTemperature appears specific to VFD
            #drift loss and evaporation loss later
            #setFanPowerRatioFunctionofAirFlowRateRatioCurve for future
            #setFractionofTowerCapacityinFreeConvectionRegime for future
            #setMinimumAirFlowRateRatio for future (vfd specific?)
            pass
        print ostower
        return ostower
        
    def updateChiller(self,uchiller,oschiller):
        #print oschiller
        #print uchiller
        oschiller.setName(uchiller['name'])
        oschiller.setCondenserType(uchiller['condenserType'])
        if uchiller['condenserFanPowerRatio']!=None:
            oschiller.setCondenserFanPowerRatio(uchiller['condenserFanPowerRatio'])
        oschiller.setMaximumPartLoadRatio(uchiller['maxPartLoadRatio'])
        oschiller.setOptimumPartLoadRatio(uchiller['optimumPartLoadRatio'])
        oschiller.setMinimumPartLoadRatio(uchiller['minPartLoadRatio'])
        oschiller.setMinimumUnloadingRatio(uchiller['minUnloadingRatio'])
        oschiller.setSizingFactor(uchiller['sizingFactor'])
        oschiller.setReferenceCOP(uchiller['rCOP'])
        if uchiller['rCWFlowRate'] != 'Autosize':
            oschiller.setReferenceCondenserFluidFlowRate(uchiller['rCWFlowRate'])
        if uchiller['rChWFlowRate'] != 'Autosize':
            oschiller.setReferenceChilledWaterFlowRate(uchiller['rCWFlowRate'])
        oschiller.setReferenceLeavingChilledWaterTemperature(uchiller['rLeavingChWt'])
        oschiller.setReferenceEnteringCondenserFluidTemperature(uchiller['rEnteringCWT'])
        oschiller.setChillerFlowMode(uchiller['chillerFlowMode'])
        return oschiller
        
    def updateBoiler(self,uboil,osboiler):
        
        osboiler.setFuelType(uboil['fueltype'])
        osboiler.setMinimumPartLoadRatio(uboil['minPartLoad'])
        osboiler.setMaximumPartLoadRatio(uboil['maxPartLoadRatio'])
        osboiler.setOptimumPartLoadRatio(uboil['optimumPartLoadRatio'])
        osboiler.setWaterOutletUpperTemperatureLimit(uboil['outletTempMaximum'])
        osboiler.setBoilerFlowMode(uboil['boilerFlowMode'])
        osboiler.setParasiticElectricLoad(uboil['parasiticElectricLoad'])
        if uboil['nominalCapacity'] == 'Autosize':
            osboiler.autosizeNominalCapacity()
        else:
            osboiler.setNominalCapacity(uboil['nominalCapacity'])
        osboiler.setNominalThermalEfficiency(uboil['nominalEfficiency'])
        osboiler.setDesignWaterOutletTemperature(uboil['designOutletTemperature'])
        if uboil['designWaterFlowRate'] == 'Autosize':
            osboiler.autosizeDesignWaterFlowRate()
        else:
            osboiler.setDesignWaterFlowRate(uboil['designWaterFlowRate'])
        osboiler.setSizingFactor(uboil['sizingFactor'])
        return osboiler
    #using a recall function is optional.  It is only designed to make reading the code easier
    def recallVVFan(self,HVACDetails):
        print 'getting supply fan from the hive'
        
        sfdesc = {
        'name':HVACDetails['varVolSupplyFanDef']['name'],
        'motorEfficiency':HVACDetails['varVolSupplyFanDef']['motorEfficiency'],
        'fanEfficiency':HVACDetails['varVolSupplyFanDef']['fanEfficiency'],
        'pressureRise':HVACDetails['varVolSupplyFanDef']['pressureRise'],
        'airStreamHeatPct':HVACDetails['varVolSupplyFanDef']['airStreamHeatPct'],
        'maxFlowRate':HVACDetails['varVolSupplyFanDef']['maxFlowRate'],
        'minFlowFrac':HVACDetails['varVolSupplyFanDef']['minFlowFrac'],
        'fanPowerCoefficient1':HVACDetails['varVolSupplyFanDef']['fanPowerCoefficient1'],
        'fanPowerCoefficient2':HVACDetails['varVolSupplyFanDef']['fanPowerCoefficient2'],
        'fanPowerCoefficient3':HVACDetails['varVolSupplyFanDef']['fanPowerCoefficient3'],
        'fanPowerCoefficient4':HVACDetails['varVolSupplyFanDef']['fanPowerCoefficient4'],
        'fanPowerCoefficient5':HVACDetails['varVolSupplyFanDef']['fanPowerCoefficient5']
        }
        return sfdesc
    #using a recall function is optional.  It is only designed to make reading the code easier
    def recallCoolingCoil(self,HVACDetails):
        #this function works for both 1speed and 2speed coils
        #if once speed, the LowSpead values are just ignored
        #sort of a dummy worker
        if HVACDetails['coolingCoil']['type'] == 0:
            print 'getting 1-speed DX cooling coil details from the hive'
            
            ccdesc = {
            'type': HVACDetails['coolingCoil']['type'],
            'name': HVACDetails['coolingCoil']['name'],
            'availSch':HVACDetails['coolingCoil']['availSch'],
            'ratedHighSpeedAirflowRate': HVACDetails['coolingCoil']['ratedAirflowRate'],
            'ratedHighSpeedTotalCooling':HVACDetails['coolingCoil']['ratedTotalCooling'],
            'ratedHighSpeedSHR':HVACDetails['coolingCoil']['ratedSHR'],
            'ratedHighSpeedCOP': HVACDetails['coolingCoil']['ratedCOP'],
            'condenserType': HVACDetails['coolingCoil']['condenserType'],
            'evaporativeCondenserDesc': HVACDetails['coolingCoil']['evaporativeCondenserDesc'],
            'Curves': HVACDetails['coolingCoil']['Curves']
            }
        else:
            print 'getting 2-speed DX cooling coil details from the hive'
            ccdesc = {
            'type': HVACDetails['coolingCoil']['type'],
            'name': HVACDetails['coolingCoil']['name'],
            'availSch':HVACDetails['coolingCoil']['availSch'],
            'ratedHighSpeedAirflowRate': HVACDetails['coolingCoil']['ratedHighSpeedAirflowRate'],
            'ratedHighSpeedTotalCooling': HVACDetails['coolingCoil']['ratedHighSpeedTotalCooling'],
            'ratedHighSpeedSHR': HVACDetails['coolingCoil']['ratedHighSpeedSHR'],
            'ratedHighSpeedCOP': HVACDetails['coolingCoil']['ratedHighSpeedCOP'],
            'ratedLowSpeedAirflowRate': HVACDetails['coolingCoil']['ratedLowSpeedAirflowRate'],
            'ratedLowSpeedTotalCooling': HVACDetails['coolingCoil']['ratedLowSpeedTotalCooling'],
            'ratedLowSpeedSHR': HVACDetails['coolingCoil']['ratedLowSpeedSHR'],
            'ratedLowSpeedCOP': HVACDetails['coolingCoil']['ratedLowSpeedCOP'],
            'condenserType': HVACDetails['coolingCoil']['condenserType'],
            'evaporativeCondenserDesc': HVACDetails['coolingCoil']['evaporativeCondenserDesc'],
            'Curves': HVACDetails['coolingCoil']['Curves']
            }
        return ccdesc
    
    
    def updateVVFan(self,sf,vvfan):
        if sf['motorEfficiency'] != None: 
            vvfan.setMotorEfficiency(sf['motorEfficiency'])
            # motor efficiency updated
        if sf['fanEfficiency'] != None: 
            vvfan.setFanEfficiency(sf['fanEfficiency'])
            #fan efficiency updated
        if sf['pressureRise'] != None: 
            vvfan.setPressureRise(sf['pressureRise'])
            # pressure rise updated
        if sf['airStreamHeatPct'] != None: 
            vvfan.setMotorInAirstreamFraction(sf['airStreamHeatPct'])
            #motor air stream heat updated
        if sf['maxFlowRate'] != None:
            if sf['maxFlowRate'] != 'Autosize':
                vvfan.setMaximumFlowRate(float(sf['maxFlowRate']))
                #max flow rate updated
            else: pass
            #fan size remains autosized
        if sf['minFlowFrac'] != None:
            vvfan.setFanPowerMinimumFlowRateInputMethod('Fraction')
            vvfan.setFanPowerMinimumFlowFraction(sf['minFlowFrac'])
            # min flow frac updated
        if sf['fanPowerCoefficient1'] != None:
            vvfan.setFanPowerCoefficient1(sf['fanPowerCoefficient1'])
            # Power Coefficient 1 updated
        if sf['fanPowerCoefficient2'] != None:
            vvfan.setFanPowerCoefficient2(sf['fanPowerCoefficient2'])
            # Power Coefficient 2 updated
        if sf['fanPowerCoefficient3'] != None:
            vvfan.setFanPowerCoefficient3(sf['fanPowerCoefficient3'])
            # Power Coefficient 3 updated
        if sf['fanPowerCoefficient4'] != None:
            vvfan.setFanPowerCoefficient4(sf['fanPowerCoefficient4'])
            # Power Coefficient 4 updated
        if sf['fanPowerCoefficient5'] != None:
            vvfan.setFanPowerCoefficient5(sf['fanPowerCoefficient5'])
            #Power Coefficient 5 updated
        print 'success updating fan!'
        return vvfan
    
    
    def updateCoolingCoil(self,cc,coolcoil):
        #works equally well for 1speed and 2speed DX coils.  
        #it is a dumb worker, if it sees None, it doesn't do anything
        if cc['type'] == 1:
            if cc['name'] != None:
                #the name can't be added to openstudio
                pass
            if cc['ratedHighSpeedCOP'] != None:
                coolcoil.setRatedHighSpeedCOP(cc['ratedHighSpeedCOP'])
                print 'updated high speed rated COP'
            if cc['ratedHighSpeedSHR'] != None and cc['ratedHighSpeedSHR'] != 'Autosize':
                coolcoil.setRatedHighSpeedSensibleHeatRatio(ops.OptionalDouble(cc['ratedHighSpeedSHR']))
                print 'updated high speed rated sensible heat ratio'
            if cc['ratedHighSpeedAirflowRate'] != None:
                if cc['ratedHighSpeedAirflowRate'] != 'Autosize':
                    coolcoil.setRatedHighSpeedAirFlowRate(ops.OptionalDouble(cc['ratedHighSpeedAirflowRate']))
                    print 'updated high speed design flow rate'
            if cc['ratedHighSpeedTotalCooling'] != None:
                if cc['ratedHighSpeedTotalCooling'] != 'Autosize':
                    coocoil.setRatedHighSpeedTotalCooling(ops.OptionalDouble(cc['ratedHighSpeedTotalCooling']))
                    print 'updated high speed total cooling'
            if cc['ratedLowSpeedCOP'] != None:
                coolcoil.setRatedLowSpeedCOP(cc['ratedLowSpeedCOP'])
                print 'updated low speed rated COP'
            if cc['ratedLowSpeedSHR'] != None and cc['ratedLowSpeedSHR'] != 'Autosize':
                coolcoil.setRatedLowSpeedSensibleHeatRatio(ops.OptionalDouble(cc['ratedLowSpeedSHR']))
            if cc['ratedLowSpeedAirflowRate'] != None:
                if cc['ratedLowSpeedAirflowRate'] != 'Autosize':
                    coolcoil.setRatedLowSpeedAirFlowRate(ops.OptionalDouble(cc['ratedLowSpeedAirflowRate']))
                    print 'updated high speed design flow rate'
            if cc['ratedLowSpeedTotalCooling'] != None:
                if cc['ratedLowSpeedTotalCooling'] != 'Autosize':
                    coocoil.setRatedLowSpeedTotalCooling(ops.OptionalDouble(cc['ratedLowSpeedTotalCooling']))
                    print 'updated high speed total cooling'
            if cc['condenserType'] != None:
                #evaporatively cooled
                if cc['condenserType'] == 1:
                    coolcoil.setCondenserType("EvaporativelyCooled")
                    if cc['evaporativeCondenserDesc'] != None:
                        #recallthe evaporativeCondenser Description from the 
                        print 'an evaporative condenser has been detected'
                        evC = self.recallEvapCondenser(cc['evaporativeCondenserDesc'].d)
                        print evC
                        coolcoil.setHighSpeedEvaporativeCondenserEffectiveness(evC['hiEvapEffectiveness'])
                        if evC['hiEvapCondAirflowRate'] != 'Autosize':
                            coolcoil.setHighSpeedEvaporativeCondenserAirFlowRate(ops.OptionalDouble(evC['hiEvapCondAirflowRate']))
                        if evC['hiEvapPumpPower'] != 'Autosize':
                            coolcoil.setHighSpeedEvaporativeCondenserPumpRatedPowerConsumption(ops.OptionalDouble(evC['hiEvapPumpPower']))
                        
                        coolcoil.setLowSpeedEvaporativeCondenserEffectiveness(evC['evapEffectiveness'])
                        if evC['evapCondAirflowRate'] != 'Autosize':
                            coolcoil.setLowSpeedEvaporativeCondenserAirFlowRate(ops.OptionalDouble(evC['evapCondAirflowRate']))
                        if evC['evapPumpPower'] != 'Autosize':
                            coolcoil.setLowSpeedEvaporativeCondenserPumpRatedPowerConsumption(ops.OptionalDouble(evC['hiEvapPumpPower']))
                        #curves and storage tank still need updating
                        print 'evaporative condenser description updated'
                else:
                    coolcoil.setCondenserType("AirCooled")
            if cc['Curves'] != None:
                #have not had a chance to work on this yet
                pass
        elif cc['type'] == 0:
            #this is a single speed coil for the future
            if cc['name'] != None:
                #the name can't be added to openstudio
                pass
            if cc['ratedCOP'] != None:
                coolcoil.setRatedCOP(ops.OptionalDouble(cc['ratedCOP']))
                print 'updated rated COP'
            if cc['ratedSHR'] != None and cc['ratedSHR'] != 'Autosize':
                coolcoil.setRatedSensibleHeatRatio(ops.OptionalDouble(cc['ratedSHR']))
                print 'updated rated sensible heat ratio'
            if cc['ratedAirflowRate'] != None:
                
                if cc['ratedAirflowRate'] != 'Autosize':
                    coolcoil.setRatedAirFlowRate(ops.OptionalDouble(cc['ratedAirflowRate']))
                    print 'updated design flow rate'
            if cc['ratedTotalCooling'] != None:
                
                if cc['ratedTotalCooling'] != 'Autosize':
                    coocoil.setRatedTotalCooling(ops.OptionalDouble(cc['ratedTotalCooling']))
                    print 'updated total cooling'
            if cc['condenserType'] != None:
                #evaporatively cooled
                if cc['condenserType'] == 1:
                    coolcoil.setCondenserType("EvaporativelyCooled")
                    if cc['evaporativeCondenserDesc'] != None:
                        #recallthe evaporativeCondenser Description from the 
                        print 'an evaporative condenser has been detected'
                        evC = self.recallEvapCondenser(cc['evaporativeCondenserDesc'].d)
                        print evC
                        coolcoil.setEvaporativeCondenserEffectiveness(ops.OptionalDouble(evC['evapEffectiveness']))
                        if evC['evapCondAirflowRate'] != 'Autosize':
                            coolcoil.setEvaporativeCondenserAirFlowRate(ops.OptionalDouble(evC['evapCondAirflowRate']))
                        if evC['evapPumpPower'] != 'Autosize':
                            coolcoil.setEvaporativeCondenserPumpRatedPowerConsumption(ops.OptionalDouble(evC['evapPumpPower']))
                        print 'evaporative condenser description updated'
                else:
                    coolcoil.setCondenserType("AirCooled")
            if cc['Curves'] != None:
                #have not had a chance to work on this yet
                
                pass
        return coolcoil
        
    def addSystemsToZones(self, model):
        
        for HAVCGroupID in self.HVACSystemDict.keys():
            
            # HAVC system index for this group and thermal zones
            systemIndex, thermalZones, HVACDetails,plantDetails,zoneRecircAir,zoneTotalAir = self.HVACSystemDict[HAVCGroupID]
            # put thermal zones into a vector
            thermalZoneVector = ops.ThermalZoneVector(thermalZones)
            # add systems. There are 10 standard ASHRAE systems + Ideal Air Loads
            if systemIndex == 0 or systemIndex == -1:
                for zone in thermalZoneVector: zone.setUseIdealAirLoads(True)
            
            elif systemIndex == 1:
                
                # 1: PTAC, Residential - thermalZoneVector because ZoneHVAC
                ops.OpenStudioModelHVAC.addSystemType1(model, thermalZoneVector)
                allptacs = model.getZoneHVACPackagedTerminalAirConditioners()
                
                for zoneCount, ptac in enumerate(allptacs):
                    hvacHandle = ptac.handle()
                    
                    #Set general air system parameters.
                    if HVACDetails != None:
                        #if HVACDetails['availSch'] != None: ptac.setAvailabilitySchedule(HVACDetails['availSch'])
                        if HVACDetails['fanPlacement'] != None: ptac.setFanPlacement(HVACDetails['fanPlacement'])
                        
                        sch = ptac.availabilitySchedule()
                        if len(HVACDetails['constVolSupplyFanDef']) > 0:
                            print 'overriding the OpenStudio supply fan settings'
                            sfname = ptac.supplyAirFan().name()
                            cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                            sf = self.recallCVFan(HVACDetails)
                            cvfan = self.updateCVFan(sf,cvfan)
                            print 'supply fan settings updated to supply fan name: ' + HVACDetails['constVolSupplyFanDef']['name']
                        else:
                            print 'no supply fan defined'
                            pass
                        if HVACDetails['coolingCoil'] != None:
                            print 'overriding the OpenStudio cooling coil settings.'
                            ccname = ptac.coolingCoil().name()
                            cc = model.getCoilCoolingDXSingleSpeedByName(str(ccname)).get()
                            print cc
                            coolcoil = self.updateCoolingCoil(HVACDetails['coolingCoil'],cc)
                    
                    #Set zone-specific parameters like a specified portion of recirculated air.
                    if zoneRecircAir[zoneCount] != 0:
                        ptac.setSupplyAirFlowRateDuringCoolingOperation(zoneTotalAir[zoneCount])
                        ptac.setSupplyAirFlowRateDuringHeatingOperation(zoneTotalAir[zoneCount])
                        ptac.setSupplyAirFlowRateWhenNoCoolingorHeatingisNeeded(zoneTotalAir[zoneCount])
                        print "Secified recirculation air for " +  str(thermalZoneVector[zoneCount].name()) + " to a value of " + str(zoneRecircAir[zoneCount]) + " m3/s per m2 of floor."
                    
                    #Set plant details.
                    if plantDetails != None:
                        if plantDetails['boiler'] != None:
                            x = ptac.heatingCoil().name()
                            hc = model.getCoilHeatingWaterByName(str(x)).get()
                            hwl = hc.plantLoop().get()
                            boilervec = hwl.supplyComponents(ops.IddObjectType("OS:Boiler:HotWater"))
                            for bc,boiler in enumerate(boilervec):
                                #sequencing, is this possible?
                                #below's example has no sequencing capabilities
                                if len(plantDetails['boiler']) > 0:
                                    osboiler = model.getBoilerHotWater(boiler.handle()).get()
                                    uboil = self.recallBoiler(plantDetails)
                                    osboiler = self.updateBoiler(uboil,osboiler)
                
            elif systemIndex == 2:
                # 2: PTHP, Residential - thermalZoneVector because ZoneHVAC
                ops.OpenStudioModelHVAC.addSystemType2(model, thermalZoneVector)
                allpthps = model.getZoneHVACPackagedTerminalHeatPumps()
                
                for zoneCount, pthp in enumerate(allpthps):
                    hvacHandle = pthp.handle()
                    
                    #Set general air system parameters.
                    if HVACDetails != None:
                        #if HVACDetails['availSch'] != None: pthp.setAvailabilitySchedule(HVACDetails['availSch'])
                        if HVACDetails['fanPlacement'] != None: pthp.setFanPlacement(HVACDetails['fanPlacement'])
                        sch = pthp.availabilitySchedule()
                        if HVACDetails['constVolSupplyFanDef'] != None:
                            print 'overriding the OpenStudio supply fan settings'
                            sfname = pthp.supplyAirFan().name()
                            cvfan = model.getFanConstantVolumeByName(str(sfname)).get()
                            sf = self.recallCVFan(HVACDetails)
                            cvfan = self.updateCVFan(sf,cvfan)
                            print 'supply fan settings updated to supply fan name: ' + HVACDetails['constVolSupplyFanDef']['name']
                        
                        if HVACDetails['heatingCoil'] != None:
                            print 'overriding the OpenStudio DX heating coil settings'
                            modelhandle = pthp.heatingCoil().handle()
                            modelhc = model.getCoilHeatingDXSingleSpeed(modelhandle).get()
                            hbhc = HVACDetails['heatingCoil']
                            modelhc = self.updateDXHeatingCoil(hbhc,modelhc)
                            print modelhc
                        
                        if HVACDetails['coolingCoil'] != None:
                            print 'overriding the OpenStudio cooling coil settings.'
                            ccname = pthp.coolingCoil().name()
                            cc = model.getCoilCoolingDXSingleSpeedByName(str(ccname)).get()
                            print cc
                            coolcoil = self.updateCoolingCoil(HVACDetails['coolingCoil'],cc)
                    
                    #Set zone-specific parameters like a specified portion of recirculated air.
                    if zoneRecircAir[zoneCount] != 0:
                        pthp.setSupplyAirFlowRateDuringCoolingOperation(zoneTotalAir[zoneCount])
                        pthp.setSupplyAirFlowRateDuringHeatingOperation(zoneTotalAir[zoneCount])
                        pthp.setSupplyAirFlowRateWhenNoCoolingorHeatingisNeeded(zoneTotalAir[zoneCount])
                        print "Secified recirculation air for " +  str(thermalZoneVector[zoneCount].name()) + " to a value of " + str(zoneRecircAir[zoneCount]) + " m3/s per m2 of floor."
                
            elif systemIndex == 3:
                print 'Making ASHRAE System Type 3'
                for zone in thermalZoneVector:
                    handle = ops.OpenStudioModelHVAC.addSystemType3(model).handle()
                    #print HVACDetails
                    
                    if HVACDetails != None:
                        #print handle
                        #print HVACDetails
                        airloop = model.getAirLoopHVAC(handle).get()
                        airloop.addBranchForZone(zone)
                        print 'zone added to PSZ air loop'
                        oasys = airloop.airLoopHVACOutdoorAirSystem()
                        
                        
                        if (oasys.is_initialized()== True) and (HVACDetails['airsideEconomizer'] != None):
                            print 'overriding the OpenStudio airside economizer settings'
                            oactrl = oasys.get().getControllerOutdoorAir()
                            #set control type
                            #can sensed min still be dry bulb for any of these?  Future release question
                            
                            
                            econo = self.recallOASys(HVACDetails)
                            oactrl = self.updateOASys(econo,oactrl,model)
                            print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                            print ''
                        
                        #apply fan changes
                        print HVACDetails['constVolSupplyFanDef']
                        if HVACDetails['constVolSupplyFanDef'] != None:
                            print 'overriding the OpenStudio supply fan settings'
                            
                            x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
                            cvfan = model.getFanConstantVolume(x[0].handle()).get()
                            sf = self.recallCVFan(HVACDetails)
                            cvfan = self.updateCVFan(sf,cvfan)
                            print 'supply fan settings updated to supply fan name: ' + HVACDetails['constVolSupplyFanDef']['name']
    
                        if HVACDetails['coolingCoil'] != None:
                            print 'overriding the OpenStudio 1-stage cooling DX cooling coil defaults.'

                            comps = airloop.supplyComponents()
                            #the default is a single speed compressor
                            #what happens if the user changes to a 2speed compressor?
                            c = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:SingleSpeed"))
                            handle = c[0].handle()
                            coolcoil = model.getCoilCoolingDXSingleSpeed(handle).get()
                            coolcoil = self.updateCoolingCoil(HVACDetails['coolingCoil'],coolcoil)
                    
            elif systemIndex == 4:
                for zone in thermalZoneVector:
                    handle = ops.OpenStudioModelHVAC.addSystemType4(model).handle()

                    if HVACDetails != None:
                        #print handle
                        #print HVACDetails
                        airloop = model.getAirLoopHVAC(handle).get()
                        airloop.addBranchForZone(zone)
                        print 'zone added to PSZ-HP air loop'
                        oasys = airloop.airLoopHVACOutdoorAirSystem()
                        
                        print HVACDetails['airsideEconomizer']
                        
                        if oasys.is_initialized() and HVACDetails['airsideEconomizer'] != None:
                            print 'overriding the OpenStudio airside economizer settings'
                            oactrl = oasys.get().getControllerOutdoorAir()
                            #set control type
                            #can sensed min still be dry bulb for any of these?  Future release question
                            econo = self.recallOASys(HVACDetails)
                            oactrl = self.updateOASys(econo,oactrl,model)
                            print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                            print ''

                        #apply fan changes
                        print HVACDetails['constVolSupplyFanDef']
                        if HVACDetails['constVolSupplyFanDef'] != 0:
                            print 'overriding the OpenStudio supply fan settings'

                            x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
                            cvfan = model.getFanConstantVolume(x[0].handle()).get()
                            sf = self.recallCVFan(HVACDetails)
                            cvfan = self.updateCVFan(sf,cvfan)
                            print 'supply fan settings updated to supply fan name: ' + HVACDetails['constVolSupplyFanDef']['name']
    
                        if HVACDetails['coolingCoil'] != None:
                            print 'overriding the OpenStudio 1-stage cooling DX cooling coil defaults.'

                            comps = airloop.supplyComponents()
                            #the default is a single speed compressor
                            #what happens if the user changes to a 2speed compressor?
                            c = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:SingleSpeed"))
                            handle = c[0].handle()
                            coolcoil = model.getCoilCoolingDXSingleSpeed(handle).get()

                            coolcoil = self.updateCoolingCoil(HVACDetails['coolingCoil'],coolcoil)
                            
                        if HVACDetails['heatingCoil'] != None:
                            print 'overriding the OpenStudio DX heating coil settings'
                            #print airloop
                            hc = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:DX:SingleSpeed"))
                            handle = hc[0].handle()
                            modelhc = model.getCoilHeatingDXSingleSpeed(handle).get()

                            hbhc = HVACDetails['heatingCoil']
                            modelhc = self.updateDXHeatingCoil(hbhc,modelhc)
                            print 'New Heating Coil Definition:'
                            print modelhc
                    
            elif systemIndex == 5:
                
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType5(model).handle()
                # get the airloop
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                
                # add branches
                for zoneCount, zone in enumerate(thermalZoneVector):
                    airloop.addBranchForZone(zone)
                    
                    #If there is recirculated air specificed, then specify it.
                    if zoneRecircAir[zoneCount] != 0:
                        x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:VAV:Reheat"))
                        vavBox = model.getAirTerminalSingleDuctVAVReheat(x[zoneCount].handle()).get()
                        vavBox.setZoneMinimumAirFlowMethod('FixedFlowRate')
                        vavBox.setFixedMinimumAirFlowRate(zoneTotalAir[zoneCount])
                        vavBox.setMaximumAirFlowRate(zoneTotalAir[zoneCount])
                        print "Secified recirculation air for " +  str(zone.name()) + " to a value of " + str(zoneRecircAir[zoneCount]) + " m3/s per m2 of floor."
                
                
                #modify the airLoopAvailabilityManager and the underlying availabilitySchedule
                if(HVACDetails != None):
                    if HVACDetails['availSch'] != None:
                        availSch = self.getOSSchedule(HVACDetails['availSch'], model)
                        airloop.setAvailabilitySchedule(availSch)
                    if HVACDetails['availabilityManagerList'] != 'ALWAYS ON':
                        airloop = self.updateAvailManager(HVACDetails['availabilityManagerList'],airloop, model)
                    
                    availManager=self.recallAvailManager(HVACDetails)
                    oasys = airloop.airLoopHVACOutdoorAirSystem()
                    
                    
                    if (oasys.is_initialized()== True) and (HVACDetails['airsideEconomizer'] != None):
                        print 'overriding the OpenStudio airside economizer settings'
                        oactrl = oasys.get().getControllerOutdoorAir()
                        #set control type
                        #can sensed min still be dry bulb for any of these?  Future release question
                        econo = self.recallOASys(HVACDetails)
                        oactrl = self.updateOASys(econo,oactrl,model)
                        print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                        print ''
                    #the fan by default is variable volume, it will never be constant volume
                    x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                    sf = model.getFanVariableVolume(x[0].handle()).get()
                    if HVACDetails['varVolSupplyFanDef'] != None:
                        print 'overriding the OpenStudio supply fan settings'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                        vvfan = model.getFanVariableVolume(x[0].handle()).get()
                        sf = self.recallVVFan(HVACDetails)
                        vvfan = self.updateVVFan(sf,vvfan)
                        print 'supply fan settings updated to supply fan name: ' + HVACDetails['varVolSupplyFanDef']['name']
                        print ''
                    
                    #the default is s two speed coil.  not sure what happens if they assign a one speed
                    if HVACDetails['coolingCoil'] != None:
                        print 'overriding the OpenStudio 2-stage cooling DX cooling coil defaults.'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:TwoSpeed"))
                        coolcoil = model.getCoilCoolingDXTwoSpeed(x[0].handle()).get()

                        coolcoil = self.updateCoolingCoil(HVACDetails['coolingCoil'],coolcoil)
                        print "success for cooling coil"
                        print ''
                        #x = airloop.supplyComponents(ops.IddObjectType("")
                    print 'updated packaged dx system!'
                    print ''
                    print 'overriding the OpenStudio hot water boiler description'
                if plantDetails != None:
                    if plantDetails['boiler'] != None:
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Water"))
                        hc = model.getCoilHeatingWater(x[0].handle()).get()
                        hwl = hc.plantLoop().get()
                        print type(hwl)
                        boilervec = hwl.supplyComponents(ops.IddObjectType("OS:Boiler:HotWater"))
                        for bc,boiler in enumerate(boilervec):
                            #sequencing, is this possible?
                            #below's example has no sequencing capabilities
                            if len(plantDetails['boiler']) > 0:
                                osboiler = model.getBoilerHotWater(boiler.handle()).get()
                                uboil = self.recallBoiler(plantDetails)
                                osboiler = self.updateBoiler(uboil,osboiler)
                                
            elif systemIndex == 6:
                print HVACDetails['availSch']
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType6(model).handle()
                
                # get the airloop
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                # add branches 
                for zone in thermalZoneVector:
                    airloop.addBranchForZone(zone)
                    
                if HVACDetails!=None:
                    
                    if HVACDetails['availSch'] != None:
                        availSch = self.getOSSchedule(HVACDetails['availSch'], model)
                        airloop.setAvailabilitySchedule(availSch)
                    
                    if HVACDetails['availabilityManagerList'] != 'ALWAYS ON':
                        airloop = self.updateAvailManager(HVACDetails['availabilityManagerList'],airloop, model)
                    
                if plantDetails!=None:
                    
                    print HVACDetails['availabilityManagerList']
                
            elif systemIndex == 7:
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType7(model).handle()
                
                # get the airloop
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                
                # add branches and fan box parameters
                recicTrigger = False
                for zoneCount, zone in enumerate(thermalZoneVector):
                    #Add a branch for the zone
                    airloop.addBranchForZone(zone)
                    
                    #If there is outdoor or recirculated air specificed, then the autosize feature of the terminal can fail to bring in the required airflow rate.
                    #So we must hard size it.
                    if zoneTotalAir[zoneCount] != 0:
                        autoCalcFailTrigger = True
                        x = airloop.demandComponents(ops.IddObjectType("OS:AirTerminal:SingleDuct:VAV:Reheat"))
                        vavBox = model.getAirTerminalSingleDuctVAVReheat(x[zoneCount].handle()).get()
                        maxAirflow = 4*float(zoneTotalAir[zoneCount])
                        vavBox.setMaximumAirFlowRate(maxAirflow)
                        vavBox.setConstantMinimumAirFlowFraction(0.25)
                        print "Secified recirculation air for " +  str(zone.name()) + " to a value of " + str(zoneRecircAir[zoneCount]) + " m3/s per m2 of floor."
                
                #If outdoor or recirculated air has been specified, we need to set the size of the supply fan because autosize will likely make the fan too small.
                if autoCalcFailTrigger == True:
                    fullHVACAirFlow = sum(zoneTotalAir)
                    if HVACDetails != None:
                        if HVACDetails['varVolSupplyFanDef'] != {}:
                            if HVACDetails['varVolSupplyFanDef']['maxFlowRate'] == 'Autosize': HVACDetails['varVolSupplyFanDef']['maxFlowRate'] = fullHVACAirFlow*4
                        else:
                            hb_varVolFan = sc.sticky['honeybee_variableVolumeFanParams']().vvFanDict
                            hb_varVolFan['maxFlowRate'] = fullHVACAirFlow*4
                            HVACDetails['varVolSupplyFanDef'] = hb_varVolFan
                    else:
                        sf = sc.sticky['honeybee_variableVolumeFanParams']().vvFanDict
                        sf['maxFlowRate'] = fullHVACAirFlow*4
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                        vvfan = model.getFanVariableVolume(x[0].handle()).get()
                        vvfan = self.updateVVFan(sf,vvfan)
                
                
                if HVACDetails != None:
                    #Update the availability manager.
                    if HVACDetails['availabilityManagerList'] != 'ALWAYS ON':
                        airloop = self.updateAvailManager(HVACDetails['availabilityManagerList'],airloop, model)
                    
                    #Edit the outdoor air sys.
                    oasys = airloop.airLoopHVACOutdoorAirSystem() 
                    if (oasys.is_initialized()== True) and (HVACDetails['airsideEconomizer'] != None):
                        print 'overriding the OpenStudio airside economizer settings'
                        oactrl = oasys.get().getControllerOutdoorAir()
                        #set control type
                        #can sensed min still be dry bulb for any of these?  Future release question
                        econo = self.recallOASys(HVACDetails)
                        oactrl = self.updateOASys(econo,oactrl,model)
                        print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                        print ''
                    
                    if HVACDetails['varVolSupplyFanDef'] != {}:
                        print 'overriding the OpenStudio supply fan settings'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                        vvfan = model.getFanVariableVolume(x[0].handle()).get()
                        sf = self.recallVVFan(HVACDetails)
                        vvfan = self.updateVVFan(sf,vvfan)
                        print 'supply fan settings updated to supply fan name: ' + HVACDetails['varVolSupplyFanDef']['name']
                        print ''
                
                if plantDetails!=None:
                    #I think the idea here is to see if there is a hot water plant update(not sure how)
                    if len(plantDetails['boiler']) > 0:
                        print 'overriding the OpenStudio hot water boiler description'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Heating:Water"))
                        hc = model.getCoilHeatingWater(x[0].handle()).get()
                        hwl = hc.plantLoop().get()
                        print type(hwl)
                        boilervec = hwl.supplyComponents(ops.IddObjectType("OS:Boiler:HotWater"))
                        for bc,boiler in enumerate(boilervec):
                            #sequencing, is this possible?
                            #below's example has no sequencing capabilities
                            osboiler = model.getBoilerHotWater(boiler.handle()).get()
                            uboil = self.recallBoiler(plantDetails)
                            osboiler = self.updateBoiler(uboil,osboiler)
                    if len(plantDetails['chiller']) > 0:
                        print 'overrideing OpenStudio chiller description'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:Water"))
                        cc = model.getCoilCoolingWater(x[0].handle()).get()
                        print cc
                        chl = cc.plantLoop().get()
                        print type(chl)
                        chillervec = chl.supplyComponents(ops.IddObjectType("OS:Chiller:Electric:EIR"))
                        for ccount,chiller in enumerate(chillervec):
                            #sequencing, is this possible?
                            oschiller = model.getChillerElectricEIR(chiller.handle()).get()
                            print oschiller
                            uchiller = self.recallChiller(plantDetails)
                            print uchiller
                            oschiller = self.updateChiller(uchiller,oschiller) 
                            if uchiller['condenserType'] == 'WaterCooled':
                                towervec = model.getCoolingTowerSingleSpeeds() #get all towers on the loop (1 by default)
                                print towervec
                                for tcount, tower in enumerate(towervec):
                                    print 'here'
                                    print type(tower)
                                    #the tower is by default a single speed tower
                                    ostower = model.getCoolingTowerSingleSpeed(tower.handle()).get()
                                    print ostower
                                    cwl = ostower.plantLoop().get()
                                    print cwl
                                    node = cwl.supplyOutletNode()
                                    print node
                                    if len(plantDetails['coolingTower']) > 0:
                                        utower = self.recallCoolingTower(plantDetails)
                                        print utower
                                        if utower["speedControl"]=="SingleSpeed":
                                            print "updating single speed cooling tower"
                                            ostower = self.updateCoolingTower(utower, ostower) #we are all good and don't need to remove the existing CT
                                        elif utower["speedControl"]=="TwoSpeed":
                                            print "upgrading cooling tower to two speed"
                                            newostower = ops.CoolingTowerTwoSpeed(model) # this is not working
                                        elif utower["speedControl"]=="VariableSpeed":
                                            print "upgrading cooling tower to variable speed"
                                            newostower = ops.CoolingTowerVariableSpeed(model) # this seems to work
                                            newostower.addToNode(node)
                                            ostower.remove()
                                            newostower = self.updateCoolingTower(utower,newostower)
                                            print newostower
                            elif uchiller['condenserType'] == 'AirCooled':
                                #we are going to make the chiller air cooled, and rip out the cooling tower
                                print 'You have specified an air cooled chiller.  Creating your chiller.'
                                towervec = model.getCoolingTowerSingleSpeeds() #get all towers on the loop (1 by default)
                                print towervec
                                for tcount, tower in enumerate(towervec):
                                    print 'here'
                                    print type(tower)
                                    #the tower is by default a single speed tower
                                    ostower = model.getCoolingTowerSingleSpeed(tower.handle()).get()
                                    print ostower
                                    cwl = ostower.plantLoop().get()
                                    print cwl
                                    node = cwl.supplyOutletNode()
                                    print node
                                    print 'Removing cooling tower.'
                                    ostower.remove()
                                    print 'Cooling tower removed.'
                                    print 'Condenser loop unneeded.'
                                    cwl.remove()
                                    print 'Condenser loop removed.'
            else:
                msg = "HVAC system index " + str(systemIndex) +  " is not implemented yet!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
    
    
    def addThermostat(self, HBZone, OSThermalZone, space, model):
        # create a dual set point
        thermostat = ops.ThermostatSetpointDualSetpoint(model)
        time24hrs = ops.Time(0,24,0,0)
        
        # assign schedules
        thermostat.setName("dualSetPtThermostat" + str(space.name()))
        
        heatingSetPtSchedule = self.getOSSchedule(HBZone.heatingSetPtSchedule, model)
        coolingSetPtSchedule = self.getOSSchedule(HBZone.coolingSetPtSchedule, model)
        
        if HBZone.heatingSetPt != "":
            #msg = "Currently you need to change the HeatingSetPt inside the shcedule: " + HBZone.heatingSetPtSchedule
            #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            #heatingSetPtSchedule.addValue(time24hrs, HBZone.heatingSetPt)
            # overwrite the existing schedule
            heatingSch = ops.ScheduleRuleset(model)
            heatingSch.setName("Heating Sch")
            defaultDaySchedule = heatingSch.defaultDaySchedule()
            defaultDaySchedule.setName("Heating Sch Default")
            defaultDaySchedule.addValue(time24hrs, float(HBZone.heatingSetPt))
            thermostat.setHeatingSchedule(heatingSch)
            
        thermostat.setHeatingSetpointTemperatureSchedule(heatingSetPtSchedule)
        
        if HBZone.coolingSetPt != "":
            # I'm not sure if this is the right way of assigning the set points
            # in combination with thermostat setpoint schedule
            coolingSch = ops.ScheduleRuleset(model)
            coolingSch.setName("Cooling Sch")
            defaultDaySchedule = coolingSch.defaultDaySchedule()
            defaultDaySchedule.setName("Cooling Sch Default")
            defaultDaySchedule.addValue(time24hrs, float(HBZone.coolingSetPt))
            thermostat.setCoolingSchedule(coolingSch)
            
        thermostat.setCoolingSetpointTemperatureSchedule(coolingSetPtSchedule)
        
        OSThermalZone.setThermostatSetpointDualSetpoint(thermostat)
        
    def setupNameAndType(self, zone, space, model):
        space.setName(zone.name)
        
        # assign space type
        spaceTypeName = ":".join([zone.bldgProgram, zone.zoneProgram])
        
        if not spaceTypeName in self.bldgTypes.keys():
            spaceType = ops.SpaceType(model)
            spaceType.setName(spaceTypeName)
            self.bldgTypes[spaceTypeName] = spaceType
        else:
            spaceType = self.bldgTypes[spaceTypeName]
            print 'the space type is:' + str(spaceType)
            
        
        space.setSpaceType(spaceType)
        
        return space

    def setInfiltration(self, zone, space, model):
        # infiltration
        infiltration = ops.SpaceInfiltrationDesignFlowRate(model)
        infiltration.setFlowperSpaceFloorArea(zone.infiltrationRatePerArea)
        infiltration.setSchedule(self.getOSSchedule(zone.infiltrationSchedule, model))
        infiltration.setSpace(space)
    
    def setDefaultSchedule(self, zone, space, model):
        # I'm not sure how default schedule will be useful
        # if I have to create separate definitions for people, light, equipments and infiltration!
        defSchedule = ops.DefaultScheduleSet(model)
        
        defSchedule.setName(zone.name + "_DefaultScheduleSet")
        defSchedule.setElectricEquipmentSchedule(self.getOSSchedule(zone.equipmentSchedule, model))
        defSchedule.setHoursofOperationSchedule(self.getOSSchedule(zone.occupancySchedule, model))
        defSchedule.setInfiltrationSchedule(self.getOSSchedule(zone.infiltrationSchedule, model))
        defSchedule.setLightingSchedule(self.getOSSchedule(zone.lightingSchedule, model))
        defSchedule.setPeopleActivityLevelSchedule(self.getOSSchedule(zone.occupancyActivitySch, model))
        space.setDefaultScheduleSet(defSchedule)
        return space
        
    def setPeopleDefinition(self, zone, space, model):
        peopleDefinition = ops.PeopleDefinition(model)
        peopleDefinition.setName(zone.name + "_PeopleDefinition")
        peopleDefinition.setNumberofPeople(zone.numOfPeoplePerArea * zone.getFloorArea())
        peopleDefinition.setNumberOfPeopleCalculationMethod("People/Area", zone.getFloorArea())
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
        
    def setLightingDefinition(self, zone, space, model):
        lightsDefinition = ops.LightsDefinition(model)
        lightsDefinition.setName(zone.name + "_LightsDefinition")
        if zone.daylightThreshold != "":
            lightsDefinition.setDesignLevelCalculationMethod('LightingLevel', zone.getFloorArea(), space.numberOfPeople())
            lightsDefinition.setLightingLevel(int(zone.daylightThreshold))
        else:
            lightsDefinition.setDesignLevelCalculationMethod("Watts/Area", zone.getFloorArea(), space.numberOfPeople())
            lightsDefinition.setWattsperSpaceFloorArea(int(zone.lightingDensityPerArea))

        lights = ops.Lights(lightsDefinition)
        lights.setName(zone.name + "_LightsObject")
        lights.setSchedule(self.getOSSchedule(zone.lightingSchedule, model))
        lights.setSpace(space)
        
    def setEquipmentDefinition(self, zone, space, model):
        electricDefinition = ops.ElectricEquipmentDefinition(model)
        electricDefinition.setName(zone.name + "_ElectricEquipmentDefinition")
        electricDefinition.setDesignLevelCalculationMethod("Watts/Area", zone.getFloorArea(), space.numberOfPeople())
        electricDefinition.setWattsperSpaceFloorArea(zone.equipmentLoadPerArea)
        
        electricEqipment = ops.ElectricEquipment(electricDefinition)
        electricEqipment.setName(zone.name + "_ElectricEquipmentObject")
        electricEqipment.setSchedule(self.getOSSchedule(zone.equipmentSchedule, model))
        electricEqipment.setEndUseSubcategory('ElectricEquipment')
        electricEqipment.setSpace(space)
        
    def setDesignSpecificationOutdoorAir(self, zone, space, model):
        
        ventilation = ops.DesignSpecificationOutdoorAir(model)
        ventilation.setName(zone.name + "_DSOA")
        ventilation.setOutdoorAirMethod("Sum")
        ventilation.setOutdoorAirFlowperPerson(zone.ventilationPerPerson)
        ventilation.setOutdoorAirFlowperFloorArea(zone.ventilationPerArea)
        #ventilation.setOutdoorAirFlowRate(0)
        space.setDesignSpecificationOutdoorAir(ventilation)
        return space
    
    def createOSStanadardOpaqueMaterial(self, HBMaterialName, values, model):
        # values = ['Roughness', 'Thickness {m}', 'Conductivity {W/m-K}', 'Density {kg/m3}', 'Specific Heat {J/kg-K}', 'Thermal Absorptance', 'Solar Absorptance', 'Visible Absorptance']
        material = ops.StandardOpaqueMaterial(model)
        material.setName(HBMaterialName)
        
        roughness = values[0]
        numericalProperties = map(float, values[1:])
        
        material.setRoughness(roughness)
        material.setThickness(numericalProperties[0])
        material.setConductivity(numericalProperties[1])
        material.setDensity(numericalProperties[2])
        material.setSpecificHeat(numericalProperties[3])
        material.setThermalAbsorptance(numericalProperties[4])
        material.setSolarAbsorptance(numericalProperties[5])
        material.setVisibleAbsorptance(numericalProperties[6])
        
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
        standardGlazing.setWindowGlassSpectralDataSetName(values[1])
        standardGlazing.setThickness(float(values[2]))
        standardGlazing.setSolarTransmittanceatNormalIncidence(float(values[3]))
        standardGlazing.setFrontSideSolarReflectanceatNormalIncidence(float(values[4]))
        standardGlazing.setBackSideSolarReflectanceatNormalIncidence(float(values[5]))
        standardGlazing.setVisibleTransmittanceatNormalIncidence(float(values[6]))
        standardGlazing.setFrontSideVisibleReflectanceatNormalIncidence(float(values[7]))
        standardGlazing.setBackSideVisibleReflectanceatNormalIncidence(float(values[8]))
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
        
    def createOSAirGap(self, HBMaterialName, values, model):
        """
        Material:AirGap
        ['Thermal Resistance {m2-K/W}']
        """
        airGap = ops.AirGap(model, float(values[0]))
        return airGap
        
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
            
        elif values[0].lower() == "material:nomass":
            return self.createOSNoMassMaterial(HBMaterialName, values[1:], model)
        
        elif values[0].lower() == "material:airgap":
            return self.createOSAirGap(HBMaterialName, values[1:], model)
        else:
            print "This type of material hasn't been implemented yet!"
            print values[0]
            print values
            print comments
        
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
    
    def opsZoneSurface (self, surface, model, space, namingMethod = 0, coordinatesList = False):
        # collect Honeybee surfaces for nonplanar cases
        # this is just for OpenStudio and not energyplus
        hbSurfaces = []
        
        if not coordinatesList: coordinatesList = surface.extractPoints()
        
        # print surface
        if namingMethod == 1:
            # these walls are only there as parent surfaces for nonplanar glazing surfaces
            srfNaming = 'count_for_glazing'
        elif type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
            srfNaming = 'no_counting'
        else:
            srfNaming = 'counting'
        
        fullString = ''
        for count, coordinates in enumerate(coordinatesList):
            if srfNaming == 'count_for_glazing': surfaceName = surface.name + '_glzP_' + `count`
            elif srfNaming == 'counting': surfaceName = surface.name + '_' + `count`
            elif srfNaming == 'no_counting': surfaceName = surface.name
            
            # generate OpenStudio points
            pointVectors = ops.Point3dVector();
            
            for pt in coordinates:
                # add the points to an openStudio list
                pointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
            
            # create surface
            thisSurface = ops.Surface(pointVectors, model);
            thisSurface.setName(surfaceName);
            thisSurface.setSpace(space);
            thisSurface.setSurfaceType(surface.srfType[surface.type]);
            srfType = surface.srfType[int(surface.type)].lower().capitalize()
            if srfType.upper().Contains("ROOF") or srfType.upper().Contains("CEILING"):
                srfType = "RoofCeiling" # This is an OpenStudio type that will be converted as a roof or ceiling in idf file
                
            thisSurface.setSurfaceType(srfType);
            
            # create construction
            if surface.EPConstruction == None:
                construction = self.getConstructionFromLib(surface.construction, model)
            elif not self.isConstructionInLib(surface.EPConstruction):
                construction = self.getOSConstruction(surface.construction, model)
                # keep track of constructions
                self.addConstructionToLib(surface.EPConstruction, construction)
            else:
                construction = self.getConstructionFromLib(surface.EPConstruction, model)
            
            thisSurface.setConstruction(construction)
            thisSurface.setOutsideBoundaryCondition(surface.BC.capitalize())
            thisSurface.setSunExposure(surface.sunExposure)
            thisSurface.setWindExposure(surface.windExposure)
            
            # Boundary condition object
            #setAdjacentSurface(self: Surface, surface: Surface)
            if surface.BC.lower() == "surface" and surface.BCObject.name.strip()!="":
                self.adjacentSurfacesDict[surface.name] = [surface.BCObject.name, thisSurface]
            
            hbSurfaces.append(thisSurface)
        
        if len(hbSurfaces)==1: return thisSurface
        else: return hbSurfaces
    
    def OPSNonePlanarFenSurface(self, surface, openStudioParentSrf, model, space):
        glzCoordinateLists = surface.extractGlzPoints()
        
        #draw the base surface
        parentSurfaces = self.opsZoneSurface (surface, model, space, namingMethod = 1, coordinatesList = glzCoordinateLists)
        
        def averagePts(ptList):
            pt = rc.Geometry.Point3d(0,0,0)
            for p in ptList: pt = pt + p
            return rc.Geometry.Point3d(pt.X/len(ptList), pt.Y/len(ptList), pt.Z/len(ptList))
            
        distance = 2 * sc.doc.ModelAbsoluteTolerance
        cornerStyle = rc.Geometry.CurveOffsetCornerStyle.None
        # offset was so slow so I changed the method to this
        #insetCoordinates = []
        for surfaceCount, coordinates in enumerate(glzCoordinateLists):
            pts = []
            for pt in coordinates: pts.append(rc.Geometry.Point3d(pt.X, pt.Y, pt.Z))
            cenPt = averagePts(pts)
            insetPts = []
            for pt in pts:
                movingVector = rc.Geometry.Vector3d(cenPt-pt)
                movingVector.Unitize()
                newPt = rc.Geometry.Point3d.Add(pt, movingVector * 2 * sc.doc.ModelAbsoluteTolerance)
                insetPts.append(newPt)
            
            #insetCoordinates.append(insetPts)
            parentSurface = parentSurfaces[surfaceCount]
            glzSurfaceName = "glz_" + str(parentSurface.name()).replace("_glazP", "", 1)
            
            self.OPSFenSurface (surface, parentSurface, model, parentNamingMethod = 1, glzCoordinatesList = [insetPts], glzingSurfaceName = glzSurfaceName)
        
            
    def OPSFenSurface (self, surface, openStudioParentSrf, model, parentNamingMethod = 0, glzCoordinatesList = False, glzingSurfaceName = ""):
        
        if not glzCoordinatesList: glzCoordinatesList = surface.extractGlzPoints()
        
        
        for count, coordinates in enumerate(glzCoordinatesList):
            
            try: childSrf = surface.childSrfs[count]
            except:  childSrf = surface.childSrfs[0]
            
            # generate OpenStudio points
            windowPointVectors = ops.Point3dVector();
            
            for pt in coordinates:
                # add the points to an openStudio list
                windowPointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
            # print coordinates
            # create construction
            if not self.isConstructionInLib(childSrf.EPConstruction):
                construction = self.getOSConstruction(childSrf.EPConstruction, model)
                # keep track of constructions
                self.addConstructionToLib(childSrf.EPConstruction, construction)
            else:
                construction = self.getConstructionFromLib(childSrf.EPConstruction, model)
            
            
            glazing = ops.SubSurface(windowPointVectors, model)
            if glzingSurfaceName == "": glazing.setName(childSrf.name + '_' + `count`)
            else: glazing.setName(glzingSurfaceName)
            glazing.setSurface(openStudioParentSrf)
            glazing.setSubSurfaceType(childSrf.srfType[childSrf.type])
            glazing.setConstruction(construction)
    
    def OPSShdSurface(self, shdSurfaces, model):
        shadingGroup = ops.ShadingSurfaceGroup(model)
        
        for surfaceCount, surface in enumerate(shdSurfaces):
            coordinates = surface.extractPoints()
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
            adjacentOSSurface = self.adjacentSurfacesDict[adjacentSurfaceName][1]
            OSSurface.setAdjacentSurface(adjacentOSSurface)
    
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
        print name
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
        return self.csvSchedules, self.csvScheduleCount

class EPFeaturesNotInOS(object):
    def __init__(self, workingDir):
        self.fileBasedSchedules = {}
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
        scheduleStr = schTypeLimitStr + \
                      "Schedule:File,\n" + \
                      scheduleObjectName + ",\t!- Name\n" + \
                      schTypeLimitName + ",\t!- Schedule Type Limits Name\n" + \
                      scheduleNewAddress + ",\t!- File Name\n" + \
                      "5,\t!- Column Number\n" + \
                      "4,\t!- Rows To Skip\n" + \
                      str(int(numOfHours)) + ",\t!- Hours of Data\n" + \
                      "Comma;\t!- Column Separator\n"
        
        return scheduleStr
    
    def EPZoneAirMixing(self, zone, zoneMixName, mixFlowRate, objCount):
        if zone.mixAirFlowSched[objCount].upper() == 'ALWAYS ON':
            mixingSched = 'ALWAYS ON'		
        elif zone.mixAirFlowSched[objCount].upper().endswith('CSV'):		
            mixingSchedFileName = os.path.basename(zone.mixAirFlowSched[objCount])		
            mixingSched = "_".join(mixingSchedFileName.split(".")[:-1])		
        else: mixingSched = zone.mixAirFlowSched[objCount]
        
        return '\nZoneMixing,\n'+\
            '\t' + zone.name + zoneMixName + 'AirMix' + str(objCount) + ',  !- Name\n' + \
            '\t' + zone.name + ',  !- Zone Name\n' + \
            '\t' + mixingSched + ',  !- Schedule Name\n' + \
            '\t' + 'Flow/Zone' + ',  !- Design Flow Rate Calculation Method\n' + \
            '\t' + str(mixFlowRate) + ',   !- Design Flow Rate {m3/s}\n' + \
            '\t' + ',  !- Flow per Zone Floor Area {m3/s-m2}\n' + \
            '\t' + ', !- Flow per Exterior Surface Area {m3/s-m2}\n' + \
            '\t' + ',    !- Air Changes per Hour\n' + \
            '\t' + zoneMixName  + ',     !- Source Zone Name\n' + \
            '\t' + '0'  + ',     !- Delta Temperature\n' + \
            '\t,                        !- Delta Temperature Schedule Name\n' + \
            '\t,                        !- Minimum Zone Temperature Schedule Name\n' + \
            '\t,                        !- Maximum Zone Temperature Schedule Name\n' + \
            '\t,                        !- Minimum Source Zone Temperature Schedule Name\n' + \
            '\t,                        !- Maximum Source Zone Temperature Schedule Name\n' + \
            '\t,                        !- Minimum Outdoor Temperature Schedule Name\n' + \
            '\t;                        !- Maximum Outdoor Temperature Schedule Name\n'
    
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
        if zone.natVentSchedule[natVentCount] == None: natVentSched = 'ALWAYS ON'
        else:
            natVentSchedFileName = os.path.basename(zone.natVentSchedule[natVentCount])
            natVentSched = "_".join(natVentSchedFileName.split(".")[:-1])
        
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



class RunOPS(object):
    def __init__(self, model, weatherFilePath, HBZones, csvSchedules, \
            csvScheduleCount, additionalcsvSchedules, openStudioLibFolder):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.openStudioDir = "/".join(openStudioLibFolder.split("/")[:3]) + "/share/openstudio"
        self.EPFolder = self.getEPFolder()
        self.EPPath = ops.Path(self.EPFolder + "\EnergyPlus.exe")
        self.epwFile = ops.Path(weatherFilePath)
        self.iddFile = ops.Path(self.EPFolder + "\Energy+.idd")
        self.model = model
        self.HBZones = HBZones
        self.csvSchedules = csvSchedules
        self.csvScheduleCount = csvScheduleCount
        self.additionalcsvSchedules = additionalcsvSchedules
    
    def getEPFolder(self):
        print self.openStudioDir
        fList = os.listdir(self.openStudioDir)
        for f in fList:
            fullpath = os.path.join(self.openStudioDir, f)
            if os.path.isdir(fullpath) and f.startswith("EnergyPlusV"):
                return fullpath
    
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
        
        ####Code added by chriswmackey to add natural ventilation parameters into the OpenStudio Model 
        self.writeNonOSFeatures(idfFilePath, self.HBZones, workingDir)
        
        
        """
        CHarriman added code to always add monthly reports to idf for ease of use in SQL
        on Nov 8 2014
        """
        #Monthly code added based on
        #git site:https://github.com/NREL/OpenStudio/blob/develop/openstudiocore/src/runmanager/lib/EnergyPlusPreProcessJob.cpp#L202
        makeMonthly = True
        if makeMonthly:
            self.writeIDFWithMonthly(idfFilePath)
        
        
        return idfFolder, idfFilePath
    
    
    def writeNonOSFeatures(self, idfFilePath, HBZones, workingDir):
        #Grab the lines of the exiting IDF.
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
                for columnCount, column in enumerate(line.split('.')):
                    if columnCount == 0:
                        origName = column + '.csv'
                        newName = column
                newName = '  ' + newName.split('\\')[-1]
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
            print schedule
            lines.append(otherFeatureClass.createCSVSchedString(schedule))
        
        natVentStrings = []
        for zone in HBZones:
            if zone.natVent == True:
                for natVentCount, natVentObj in enumerate(zone.natVentType):
                    if natVentObj == 1 or natVentObj == 2:
                        natVentStrings.append(otherFeatureClass.EPNatVentSimple(zone, natVentCount))
                    elif natVentObj == 3:
                        natVentStrings.append(otherFeatureClass.EPNatVentFan(zone, natVentCount))
        
        if len(natVentStrings) > 0:
            for line in natVentStrings:
                lines.append(line)
        
        lines.append('\nOutput:Surfaces:List,\n')
        lines.append('\t' + 'Details;                 !- Report Type' + '\n')
        
        fiw = open(str(idfFilePath),'w')
        for line in lines:
            fiw.write(line)
        fiw.close()
    
    
    def writeIDFWithMonthly(self, idfFilePath):
        fi = open(str(idfFilePath),'r')
        fi.seek(0)
        prepare=False
        count = 0
        lines=[]
        for line in fi:
            if line.strip() != 'Output:SQLite,':
                if (prepare):
                    count+=1;
                    if (count==2):
                        lines.append("\n")
                        lines.append("Output:Table:Monthly," + "\n")
                        lines.append("    Building Energy Performance - Electricity,  !- Name"+ "\n")
                        lines.append("    2,                       !- Digits After Decimal"+ "\n")
                        lines.append("    InteriorLights:Electricity,  !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    ExteriorLights:Electricity,  !- Variable or Meter 2 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 2"+ "\n")
                        lines.append("    InteriorEquipment:Electricity,  !- Variable or Meter 3 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 3"+ "\n")
                        lines.append("    ExteriorEquipment:Electricity,  !- Variable or Meter 4 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 4"+ "\n")
                        lines.append("    Fans:Electricity,        !- Variable or Meter 5 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 5"+ "\n")
                        lines.append("    Pumps:Electricity,       !- Variable or Meter 6 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 6"+ "\n")
                        lines.append("    Heating:Electricity,     !- Variable or Meter 7 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 7"+ "\n")
                        lines.append("    Cooling:Electricity,     !- Variable or Meter 8 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 8"+ "\n")
                        lines.append("    HeatRejection:Electricity,  !- Variable or Meter 9 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 9"+ "\n")
                        lines.append("    Humidifier:Electricity,  !- Variable or Meter 10 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 10"+ "\n")
                        lines.append("    HeatRecovery:Electricity,!- Variable or Meter 11 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 11"+ "\n")
                        lines.append("    WaterSystems:Electricity,!- Variable or Meter 12 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 12"+ "\n")
                        lines.append("    Cogeneration:Electricity,!- Variable or Meter 13 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 13"+ "\n")
                        lines.append("    Refrigeration:Electricity,!- Variable or Meter 14 Name"+ "\n")
                        lines.append("    SumOrAverage;            !- Aggregation Type for Variable or Meter 14"+ "\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+ "\n")
                        lines.append("  Building Energy Performance - Natural Gas,  !- Name"+ "\n")
                        lines.append("    2,                       !- Digits After Decimal"+ "\n")
                        lines.append("    InteriorEquipment:Gas,   !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    ExteriorEquipment:Gas,   !- Variable or Meter 2 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 2"+ "\n")
                        lines.append("    Heating:Gas,             !- Variable or Meter 3 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 3"+ "\n")
                        lines.append("    Cooling:Gas,             !- Variable or Meter 4 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 4"+ "\n")
                        lines.append("    WaterSystems:Gas,        !- Variable or Meter 5 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 5"+ "\n")
                        lines.append("    Cogeneration:Gas,        !- Variable or Meter 6 Name"+ "\n")
                        lines.append("    SumOrAverage;            !- Aggregation Type for Variable or Meter 6"+ "\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+ "\n")
                        lines.append("  Building Energy Performance - District Heating,  !- Name"+ "\n")
                        lines.append("    2,                       !- Digits After Decimal"+ "\n")
                        lines.append("    InteriorLights:DistrictHeating,  !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    ExteriorLights:DistrictHeating,  !- Variable or Meter 2 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 2"+ "\n")
                        lines.append("    InteriorEquipment:DistrictHeating,  !- Variable or Meter 3 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 3"+ "\n")
                        lines.append("    ExteriorEquipment:DistrictHeating,  !- Variable or Meter 4 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 4"+ "\n")
                        lines.append("    Fans:DistrictHeating,        !- Variable or Meter 5 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 5"+ "\n")
                        lines.append("    Pumps:DistrictHeating,       !- Variable or Meter 6 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 6"+ "\n")
                        lines.append("    Heating:DistrictHeating,     !- Variable or Meter 7 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 7"+ "\n")
                        lines.append("    Cooling:DistrictHeating,     !- Variable or Meter 8 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 8"+ "\n")
                        lines.append("    HeatRejection:DistrictHeating,  !- Variable or Meter 9 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 9"+ "\n")
                        lines.append("    Humidifier:DistrictHeating,  !- Variable or Meter 10 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 10"+ "\n")
                        lines.append("    HeatRecovery:DistrictHeating,!- Variable or Meter 11 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 11"+ "\n")
                        lines.append("    WaterSystems:DistrictHeating,!- Variable or Meter 12 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 12"+ "\n")
                        lines.append("    Cogeneration:DistrictHeating,!- Variable or Meter 13 Name"+ "\n")
                        lines.append("    SumOrAverage;            !- Aggregation Type for Variable or Meter 13"+ "\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+ "\n")
                        lines.append("  Building Energy Performance - District Cooling,  !- Name"+ "\n")
                        lines.append("    2,                       !- Digits After Decimal"+ "\n")
                        lines.append("    InteriorLights:DistrictCooling,  !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    ExteriorLights:DistrictCooling,  !- Variable or Meter 2 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 2"+ "\n")
                        lines.append("    InteriorEquipment:DistrictCooling,  !- Variable or Meter 3 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 3"+ "\n")
                        lines.append("    ExteriorEquipment:DistrictCooling,  !- Variable or Meter 4 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 4"+ "\n")
                        lines.append("    Fans:DistrictCooling,        !- Variable or Meter 5 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 5"+ "\n")
                        lines.append("    Pumps:DistrictCooling,       !- Variable or Meter 6 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 6"+ "\n")
                        lines.append("    Heating:DistrictCooling,     !- Variable or Meter 7 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 7"+ "\n")
                        lines.append("    Cooling:DistrictCooling,     !- Variable or Meter 8 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 8"+ "\n")
                        lines.append("    HeatRejection:DistrictCooling,  !- Variable or Meter 9 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 9"+ "\n")
                        lines.append("    Humidifier:DistrictCooling,  !- Variable or Meter 10 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 10"+ "\n")
                        lines.append("    HeatRecovery:DistrictCooling,!- Variable or Meter 11 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 11"+ "\n")
                        lines.append("    WaterSystems:DistrictCooling,!- Variable or Meter 12 Name"+ "\n")
                        lines.append("    SumOrAverage,            !- Aggregation Type for Variable or Meter 12"+ "\n")
                        lines.append("    Cogeneration:DistrictCooling,!- Variable or Meter 13 Name"+ "\n")
                        lines.append("    SumOrAverage;            !- Aggregation Type for Variable or Meter 13"+ "\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+ "\n")
                        lines.append("  Building Energy Performance - Electricity Peak Demand,  !- Name"+ "\n")
                        lines.append("    2,                       !- Digits After Decimal"+ "\n")
                        lines.append("    Electricity:Facility,  !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    Maximum,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    InteriorLights:Electricity,  !- Variable or Meter 1 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 1"+ "\n")
                        lines.append("    ExteriorLights:Electricity,  !- Variable or Meter 2 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 2"+ "\n")
                        lines.append("    InteriorEquipment:Electricity,  !- Variable or Meter 3 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 3"+ "\n")
                        lines.append("    ExteriorEquipment:Electricity,  !- Variable or Meter 4 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 4"+ "\n")
                        lines.append("    Fans:Electricity,        !- Variable or Meter 5 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 5"+ "\n")
                        lines.append("    Pumps:Electricity,       !- Variable or Meter 6 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 6"+ "\n")
                        lines.append("    Heating:Electricity,     !- Variable or Meter 7 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 7"+ "\n")
                        lines.append("    Cooling:Electricity,     !- Variable or Meter 8 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 8"+ "\n")
                        lines.append("    HeatRejection:Electricity,  !- Variable or Meter 9 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 9"+ "\n")
                        lines.append("    Humidifier:Electricity,  !- Variable or Meter 10 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 10"+ "\n")
                        lines.append("    HeatRecovery:Electricity,!- Variable or Meter 11 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 11"+ "\n")
                        lines.append("    WaterSystems:Electricity,!- Variable or Meter 12 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 12"+ "\n")
                        lines.append("    Cogeneration:Electricity,!- Variable or Meter 13 Name"+ "\n")
                        lines.append("    ValueWhenMaximumOrMinimum;            !- Aggregation Type for Variable or Meter 13"+ "\n")
                        lines.append("Output:Table:Monthly,"+"\n")
                        lines.append("  Building Energy Performance - Natural Gas Peak Demand,  !- Name"+"\n")
                        lines.append("    2,                       !- Digits After Decimal"+"\n")
                        lines.append("    Gas:Facility,  !- Variable or Meter 1 Name"+"\n")
                        lines.append("    Maximum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    InteriorEquipment:Gas,   !- Variable or Meter 1 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    ExteriorEquipment:Gas,   !- Variable or Meter 2 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 2"+"\n")
                        lines.append("    Heating:Gas,             !- Variable or Meter 3 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 3"+"\n")
                        lines.append("    Cooling:Gas,             !- Variable or Meter 4 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 4"+"\n")
                        lines.append("    WaterSystems:Gas,        !- Variable or Meter 5 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 5"+"\n")
                        lines.append("    Cogeneration:Gas,        !- Variable or Meter 6 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum;            !- Aggregation Type for Variable or Meter 6"+"\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+"\n")
                        lines.append("  Building Energy Performance - District Heating Peak Demand,  !- Name"+"\n")
                        lines.append("    2,                       !- Digits After Decimal"+"\n")
                        lines.append("    DistrictHeating:Facility,  !- Variable or Meter 1 Name"+"\n")
                        lines.append("    Maximum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    InteriorLights:DistrictHeating,  !- Variable or Meter 1 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    ExteriorLights:DistrictHeating,  !- Variable or Meter 2 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 2"+"\n")
                        lines.append("    InteriorEquipment:DistrictHeating,  !- Variable or Meter 3 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 3"+"\n")
                        lines.append("    ExteriorEquipment:DistrictHeating,  !- Variable or Meter 4 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 4"+"\n")
                        lines.append("    Fans:DistrictHeating,        !- Variable or Meter 5 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 5"+"\n")
                        lines.append("    Pumps:DistrictHeating,       !- Variable or Meter 6 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 6"+"\n")
                        lines.append("    Heating:DistrictHeating,     !- Variable or Meter 7 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 7"+"\n")
                        lines.append("    Cooling:DistrictHeating,     !- Variable or Meter 8 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 8"+"\n")
                        lines.append("    HeatRejection:DistrictHeating,  !- Variable or Meter 9 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 9"+"\n")
                        lines.append("    Humidifier:DistrictHeating,  !- Variable or Meter 10 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 10"+"\n")
                        lines.append("    HeatRecovery:DistrictHeating,!- Variable or Meter 11 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 11"+"\n")
                        lines.append("    WaterSystems:DistrictHeating,!- Variable or Meter 12 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 12"+"\n")
                        lines.append("    Cogeneration:DistrictHeating,!- Variable or Meter 13 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum;            !- Aggregation Type for Variable or Meter 13"+"\n")
                        lines.append("\n")
                        lines.append("Output:Table:Monthly,"+"\n")
                        lines.append("  Building Energy Performance - District Cooling Peak Demand,  !- Name"+"\n")
                        lines.append("    2,                       !- Digits After Decimal"+"\n")
                        lines.append("    DistrictCooling:Facility,  !- Variable or Meter 1 Name"+"\n")
                        lines.append("    Maximum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    InteriorLights:DistrictCooling,  !- Variable or Meter 1 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 1"+"\n")
                        lines.append("    ExteriorLights:DistrictCooling,  !- Variable or Meter 2 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 2"+"\n")
                        lines.append("    InteriorEquipment:DistrictCooling,  !- Variable or Meter 3 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 3"+"\n")
                        lines.append("    ExteriorEquipment:DistrictCooling,  !- Variable or Meter 4 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 4"+"\n")
                        lines.append("    Fans:DistrictCooling,        !- Variable or Meter 5 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 5"+"\n")
                        lines.append("    Pumps:DistrictCooling,       !- Variable or Meter 6 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 6"+"\n")
                        lines.append("    Heating:DistrictCooling,     !- Variable or Meter 7 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 7"+"\n")
                        lines.append("    Cooling:DistrictCooling,     !- Variable or Meter 8 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 8"+"\n")
                        lines.append("    HeatRejection:DistrictCooling,  !- Variable or Meter 9 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 9"+"\n")
                        lines.append("    Humidifier:DistrictCooling,  !- Variable or Meter 10 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 10"+"\n")
                        lines.append("    HeatRecovery:DistrictCooling,!- Variable or Meter 11 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 11"+"\n")
                        lines.append("    WaterSystems:DistrictCooling,!- Variable or Meter 12 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum,            !- Aggregation Type for Variable or Meter 12"+"\n")
                        lines.append("    Cogeneration:DistrictCooling,!- Variable or Meter 13 Name"+"\n")
                        lines.append("    ValueWhenMaximumOrMinimum;            !- Aggregation Type for Variable or Meter 13"+"\n")
                        lines.append("\n")
                    else:
                        lines.append(line)
                else: 
                    lines.append(line)
            else:
                prepare=True;
                lines.append(line)
        
        fi.close()
        fiw = open(str(idfFilePath),'w')
        for line in lines:
            fiw.write(line)
        fiw.close()
    
    
    def runAnalysis(self, osmFile, useRunManager = False):
        
        # Preparation
        workingDir, fileName = os.path.split(osmFile)
        projectName = (".").join(fileName.split(".")[:-1])
        osmPath = ops.Path(osmFile)
        
        # create idf - I separated this job as putting them together
        # was making EnergyPlus to crash
        idfFolder, idfPath = self.osmToidf(workingDir, projectName, osmPath)
        print 'IDF had been created from the OSM: ' + str(idfPath)
        
        if not useRunManager:
            
            resultFile = self.writeBatchFile(idfFolder, "ModelToIdf\\in.idf", self.weatherFile)
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
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress):
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
        os.system(batchFileAddress)
        return fullPath + "Zsz.csv",fullPath+".sql",fullPath+".csv"


def main(HBZones, HBContext, north, epwWeatherFile, analysisPeriod, simParameters, simulationOutputs, runIt, workingDir = "C:\ladybug", fileName = "openStudioModel.osm"):
    
    # import the classes
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
    if not epwWeatherFile.endswith(epwWeatherFile) or not os.path.isfile(epwWeatherFile):
        msg = "Wrong weather file!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    
    if workingDir == None: workingDir = sc.sticky["Honeybee_DefaultFolder"] 
    
    if fileName == None: fileName = "unnamed"
    
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
    
    # set north
    hb_writeOPS.setNorth(north, model)
    
    # set timestep
    hb_writeOPS.setTimestep(model)
    
    # set simulation control
    hb_writeOPS.setSimulationControls(model)
    
    # set shadow calculation parameters
    hb_writeOPS.setShadowCalculation(model)
    
    # add design DAY
    hb_writeOPS.addDesignDays(model)
    
    # call Honeybee objects from the hive
    HBZones = hb_hive.callFromHoneybeeHive(HBZones)
    
    # generate stories
    hb_writeOPS.generateStories(HBZones, model)
    
    #Make a list of schedules to keep track of what needs to be written into the model.
    additionalSchedList = []
    additionalcsvSchedules = []
    
    for zoneCount, zone in enumerate(HBZones):
        
        # prepare non-planar zones
        if zone.hasNonPlanarSrf or zone.hasInternalEdge:
            zone.prepareNonPlanarZone()
    
        # create a space - OpenStudio works based of space and not zone
        # Honeybee though is structured based on zones similar to EnergyPlus
        space = ops.Space(model)
        
        # assign name and type
        space = hb_writeOPS.setupNameAndType(zone, space, model)
        
        # assign level/building story to zone
        space = hb_writeOPS.setupLevels(zone, space)
        
        # schedules
        
        space = hb_writeOPS.setDefaultSchedule(zone, space, model)
        
        # infiltration
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
        
        # add HVAC system
        HAVCGroupID, HVACIndex, HVACDetails, plantDetails = zone.HVACSystem
        
        # print HAVCGroupID,HVACIndex,HVACDetails,plantDetails
        
        if HAVCGroupID!= -1:
            if HAVCGroupID not in hb_writeOPS.HVACSystemDict.keys():
                # add place holder for lists 
                
                hb_writeOPS.HVACSystemDict[HAVCGroupID] = [HVACIndex,[],HVACDetails,plantDetails, [], []]
        
        # collect informations for systems here, such as the zones in each system and the recirculation specifcations for each zone.
        hb_writeOPS.HVACSystemDict[HAVCGroupID][1].append(thermalZone)
        hb_writeOPS.HVACSystemDict[HAVCGroupID][4].append(zone.recirculatedAirPerArea)
        zoneFlrArea = zone.getFloorArea()
        totalZoneFlow = (zone.recirculatedAirPerArea*zoneFlrArea) +  (zone.ventilationPerArea*zoneFlrArea) + (zone.ventilationPerPerson*zone.numOfPeoplePerArea*zoneFlrArea)
        hb_writeOPS.HVACSystemDict[HAVCGroupID][5].append(totalZoneFlow)
        
        # add thermostat
        thermalZone = hb_writeOPS.addThermostat(zone, thermalZone, space, model)
        
        # write the surfaces
        for HBSrf in zone.surfaces:
            
            OPSSrf = hb_writeOPS.opsZoneSurface(HBSrf, model, space, namingMethod = 0, coordinatesList = False)
            
            if HBSrf.hasChild:
                if HBSrf.isPlanar:
                    hb_writeOPS.OPSFenSurface(HBSrf, OPSSrf, model)
                else:
                    hb_writeOPS.OPSNonePlanarFenSurface(HBSrf, OPSSrf, model, space)
        
        
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
    
    # add shading surfaces if any
    if HBContext != []:
        shdingSurfcaes = hb_hive.callFromHoneybeeHive(HBContext)
        hb_writeOPS.OPSShdSurface(shdingSurfcaes, model)
    
    # outputs
    if simulationOutputs:
        csvSchedules, csvScheduleCount = hb_writeOPS.setOutputs(simulationOutputs, model)
    else:
        csvSchedules = []
        csvScheduleCount = 0
    
    #save the model
    model.save(ops.Path(fname), True)
    
    print "Model saved to: " + fname
    workingDir, fileName = os.path.split(fname)
    projectName = (".").join(fileName.split(".")[:-1])
    
    
    if runIt:
        hb_runOPS = RunOPS(model, epwWeatherFile, HBZones, csvSchedules, \
            csvScheduleCount, additionalcsvSchedules, openStudioLibFolder)
            
        idfFile, resultFile = hb_runOPS.runAnalysis(fname, useRunManager = False)
        
        try:
            errorFileFullName = idfFile.replace('.idf', '.err')
            errFile = open(errorFileFullName, 'r')
            for line in errFile:
                print line
                if "**  Fatal  **" in line:
                    warning = "The simulation has failed because of this fatal error: \n" + str(line)
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
                    resultFileAddress = None
                elif "** Severe  **" in line:
                    comment = "The simulation has not run correctly because of this severe error: \n" + str(line)
                    c = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(c, comment)
            errFile.close()
        except:
            pass
        
        return fname, idfFile, resultFile
        
    return fname, None, None

if _epwWeatherFile and _writeOSM and openStudioIsReady:
    results = main(_HBZones, HBContext_, north_, _epwWeatherFile,
                  _analysisPeriod_, _energySimPar_, simulationOutputs_,
                  runSimulation_, workingDir_, fileName_)
    print results
    if results!=-1:
        osmFileAddress, idfFileAddress, resultsFiles = results
        try:
            resultsFileAddress = resultsFiles[2]
            sqlFileAddress = resultsFiles[1]
            meterFileAddress = resultsFiles[0]
        except: resultsFileAddress = resultsFiles
