# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Export Honeybee Objects to OpenStudio
-
Provided by Honeybee 0.0.54
    
    Args:
        openStudioLibFolder:
    Returns:
        readMe!: ...
"""

# check for libraries
# default is C:\\Ladybug\\OpenStudio

import os
import System
import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh
import time
from pprint import pprint

#openStudioLibFolder = "C:\\Users\\" + os.getenv("USERNAME") + "\\Dropbox\\ladybug\\honeybee\\openStudio\\CSharp64bits"
if sc.sticky.has_key('honeybee_release'):
    
    openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
    
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
        msg = "Cannot find OpenStudio libraries. You can download the libraries from the link below. " + \
              "Unzip the file and copy it to " + openStudioLibFolder + " and try again. Click on the link to copy the address."
              
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        link = "https://app.box.com/s/y2sx16k98g1lfd3r47zi"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, link)
        
        #buttons = System.Windows.Forms.MessageBoxButtons.OK
        #icon = System.Windows.Forms.MessageBoxIcon.Warning
        #up = rc.UI.Dialogs.ShowMessageBox(msg + "\n" + link, "Duplicate Material Name", buttons, icon)
    
    if openStudioIsReady and sc.sticky.has_key('honeybee_release') and \
        sc.sticky.has_key("isNewerOSAvailable") and sc.sticky["isNewerOSAvailable"]:
        # check if there is an update available
        msg = "There is a newer version of OpenStudio libraries available to download! " + \
                      "We strongly recommend you to download the newer version from this link and replace it with current files at " + \
                      openStudioLibFolder +".\n" + \
                      "https://app.box.com/s/y2sx16k98g1lfd3r47zi"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    openStudioIsReady = False

ghenv.Component.Name = "Honeybee_Export To OpenStudio"
ghenv.Component.NickName = 'exportToOpenStudio'
ghenv.Component.Message = 'VER 0.0.54\nAUG_21_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


class WriteOPS(object):

    def __init__(self, EPParameters, weatherFilePath = r"C:\EnergyPlusV8-1-0\WeatherData\USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        self.hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        self.hb_EPPar = sc.sticky["honeybee_EPParameters"]()
        self.simParameters = self.hb_EPPar.readEPParams(EPParameters)
        
        if self.simParameters[4] != None: self.ddyFile = self.simParameters[4]
        else: self.ddyFile = weatherFilePath.replace(".epw", ".ddy", 1)
        
        self.constructionList = {}
        self.materialList = {}
        self.scheduleList = {}
        self.bldgTypes = {}
        self.levels = {}
        self.HVACSystemDict = {}
        self.adjacentSurfacesDict = {}
    
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
        print schName
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
                print values[0]
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
        0:'NoLockout',
        1:'LockoutWithHeating',
        2:'LockoutWithCompressor'
        }
        minLimit={
        0:'ProportionalMinimum',
        1:'FixedMinimum'
        }
        
        print 'getting oasys from the hive'
        print HVACDetails
        oaDesc = {
        'name' : HVACDetails['airsideEconomizer']['name'],
        'econoControl': HVACDetails['airsideEconomizer']['econoControl'],
        'sensedMin' : HVACDetails['airsideEconomizer']['sensedMin'],
        'sensedMax' : HVACDetails['airsideEconomizer']['sensedMax'],
        'maxLimitDewpoint' : HVACDetails['airsideEconomizer']['maxLimitDewpoint'],
        'minAirFlowRate' : HVACDetails['airsideEconomizer']['minAirFlowRate'],
        'maxAirFlowRate' : HVACDetails['airsideEconomizer']['maxAirFlowRate'],
        'minLimitType' : minLimit[HVACDetails['airsideEconomizer']['minLimitType']],
        'controlAction' : ctrlAction[HVACDetails['airsideEconomizer']['controlAction']],
        'minOASchedule' : HVACDetails['airsideEconomizer']['minOutdoorAirSchedule'],
        'minOAFracSchedule' : HVACDetails['airsideEconomizer']['minOutdoorAirFracSchedule'],
        'DXLockoutMethod' : lockout[HVACDetails['airsideEconomizer']['DXLockoutMethod']]
        }
        return oaDesc
    def updateOASys(self,econo,oactrl):
        if econo['econoControl'] == 0:
            oactrl.setEconomizerControlType("FixedDryBulb")
            if econo['sensedMin'] != None:
                mindb = econo['sensedMin']
            if econo['sensedMax'] != None:
                maxdb = econo['sensedMax']
                oactrl.setEconomizerMinimumLimitDryBulbTemperature(mindb)
                oactrl.setEconomizerMaximumLimitDryBulbTemperature(maxdb)
        elif econo['econoControl'] == 1:
            oactrl.setEconomizerControlType("DifferentialDryBulb")
        elif econo['econoControl'] == 2:
            oactrl.setEconomizerControlType("FixedEnthalpy")
            if sensedMax != None:
                maxenth = econo['sensedMax']
                oactrl.setEconomizerMaximumLimitEnthalpy(maxenth)
                #can sensed min still be dry bulb?
        elif econo['econoControl'] == 3:
            oactrl.setEconomizerControlType("DifferentialEnthalpy")
        elif econo['econoControl'] == 4:
            oactrl.setEconomizerControlType("ElectronicEnthalpy")
            #set curve in future releases
        elif econo['econoControl'] == 5:
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
        elif econo['econoControl'] == 6:
            oactrl.setEconomizerControlType("DifferentialDryBulbAndEnthalpy")
            if sensedMax != None:
                maxenth = econo['sensedMax']
                oactrl.setEconomizerMaximumLimitEnthalpy(maxenth)
        else:
            oactrl.setEconomizerControlType("NoEconomizer")
        print 'economizer control type set'
        
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
        print 'set min and max flow rates'
        #set control action
        if econo['controlAction']!=None:
            oactrl.setEconomizerControlActionType(econo['controlAction'])
        print 'set control action'
        #set minLimit type
        if econo['minLimitType']!=None:
            oactrl.setMinimumLimitType(econo['minLimitType'])
        print 'set min limit type'
        #set lockout type (applies to DX systems only)
        if econo['DXLockoutMethod'] != None:
            oactrl.setLockoutType(econo['DXLockoutMethod'])
        print 'set dx lockout method'
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
            
    def updateVVFan(self,sf,vvfan):
        if sf['motorEfficiency'] != None: 
            vvfan.setMotorEfficiency(sf['motorEfficiency'])
            print 'motor efficiency updated'
        if sf['fanEfficiency'] != None: 
            vvfan.setFanEfficiency(sf['fanEfficiency'])
            print 'fan efficiency updated'
        if sf['pressureRise'] != None: 
            vvfan.setPressureRise(sf['pressureRise'])
            print 'pressure rise updated'
        if sf['airStreamHeatPct'] != None: 
            vvfan.setMotorInAirstreamFraction(sf['airStreamHeatPct'])
            print 'motor air stream heat updated'
        if sf['maxFlowRate'] != None:
            if sf['maxFlowRate'] != 'Autosize':
                vvfan.setMaximumFlowRate(float(sf['maxFlowRate']))
                print 'max flow rate updated'
            else:
                print 'fan size remains autosized'
        if sf['minFlowFrac'] != None:
            vvfan.setFanPowerMinimumFlowFraction(sf['minFlowFrac'])
            print 'min flow frac updated'
        if sf['fanPowerCoefficient1'] != None:
            vvfan.setFanPowerCoefficient1(sf['fanPowerCoefficient1'])
            print 'Power Coefficient 1 updated'
        if sf['fanPowerCoefficient2'] != None:
            vvfan.setFanPowerCoefficient2(sf['fanPowerCoefficient2'])
            print 'Power Coefficient 2 updated'
        if sf['fanPowerCoefficient3'] != None:
            vvfan.setFanPowerCoefficient3(sf['fanPowerCoefficient3'])
            print 'Power Coefficient 3 updated'
        if sf['fanPowerCoefficient4'] != None:
            vvfan.setFanPowerCoefficient4(sf['fanPowerCoefficient4'])
            print 'Power Coefficient 4 updated'
        if sf['fanPowerCoefficient5'] != None:
            vvfan.setFanPowerCoefficient5(sf['fanPowerCoefficient5'])
            print 'Power Coefficient 5 updated'
        print 'success updating fan!'
        return vvfan
        
    def addSystemsToZones(self, model):
        
        for HAVCGroupID in self.HVACSystemDict.keys():
            #print self.HVACSystemDict.keys()
            # HAVC system index for this group and thermal zones
            systemIndex, thermalZones, HVACDetails = self.HVACSystemDict[HAVCGroupID]
            #print systemIndex
            #print len(thermalZones)
            # put thermal zones into a vector
            thermalZoneVector = ops.ThermalZoneVector(thermalZones)
            #print thermalZoneVector
            # add systems. There are 10 standard ASHRAE systems + Ideal Air Loads
            if systemIndex == 0:
                for zone in thermalZoneVector: zone.setUseIdealAirLoads(True)
            
            elif systemIndex == 1:
                #template values
                availability = sc.sticky['System_1']['availSch']
                fanplacement = sc.sticky['System_1']['fanPlacement']
                airflowinCool = sc.sticky['System_1']['coolingAirflow']
                oaflowinCool = sc.sticky['System_1']['coolingOAflow']
                airflowinHeat = sc.sticky['System_1']['heatingAirflow']
                oaflowinHeat = sc.sticky['System_1']['heatingOAflow']
                airflowinFloat = sc.sticky['System_1']['floatingAirflow']
                oaflowinFloat = sc.sticky['System_1']['floatingOAflow']
                try:
                    supplyFan = sc.sticky['System_1']['supplyFanDef']
                    print supplyFan
                    sfFanEff = supplyFan['fanEfficiency']
                    sfPressureRise = supplyFan['pressureRise']
                    sfMaxFlow = supplyFan['maxFlowRate']
                    sfMotorEff = supplyFan['motorEfficiency']
                    sfAirStreamPup = supplyFan['airStreamHeatPct']
                except:
                    pass
                #does my avail schedule exists?
                
                schedExists = False
                scheds = model.getScheduleConstants()
                print scheds
                for sched in scheds:
                    print 'here'
                    if sched.value() == str(availability): schedExists = True
                if schedExists:
                    print 'availability schedule found'
                else:
                    print 'creating availability schedule'
                    schName = 'a grasshopper schedule'
                    values = [schName,None,str(availability)]
                    availability = self.createConstantOSSchedule(schName, values, model)
                # 1: PTAC, Residential - thermalZoneVector because ZoneHVAC
                ops.OpenStudioModelHVAC.addSystemType1(model, thermalZoneVector)
                allptacs = model.getZoneHVACPackagedTerminalAirConditioners()
                #print allptacs
                for ptac in allptacs:
                    hvacHandle = ptac.handle()
                    
                    if availability != None: ptac.setAvailabilitySchedule(availability)
                    if fanplacement != None: ptac.setFanPlacement(fanplacement)
                    if airflowinCool != None:
                        ptac.setSupplyAirFlowRateDuringCoolingOperation(airflowinCool)
                    if oaflowinCool != None:
                        ptac.setOutdoorAirFlowRateDuringCoolingOperation(oaflowinCool)
                    if airflowinHeat != None:
                        ptac.setSupplyAirFlowRateDuringHeatingOperation(airflowinHeat)
                    if oaflowinHeat != None:
                        ptac.setOutdoorAirFlowRateDuringHeatingOperation(oaflowinHeat)
                    if airflowinFloat != None:
                        ptac.setSupplyAirFlowRateWhenNoCoolingorHeatingisNeeded(airflowinFloat)
                    if oaflowinFloat != None:
                        ptac.setOutdoorAirFlowRateWhenNoCoolingorHeatingisNeeded(oaflowinFloat)
                    sch = ptac.availabilitySchedule()
                    try:
                        sfname = ptac.supplyAirFan().name()
                        sf = model.getFanConstantVolumeByName(str(sfname)).get()
                        if sfFanEff != None: sf.setFanEfficiency(sfFanEff)
                        if sfPressureRise != None: sf.setPressureRise(sfPressureRise)
                        if sfMaxFlow != None: sf.setMaximumFlowRate(sfMaxFlow)
                        if sfMotorEff != None: sf.setMotorEfficiency(sfMotorEff)
                        if sfAirStreamPup != None: sf.setMotorInAirstreamFraction(sfAirStreamPup)
                        print sf
                    except:
                        print 'no supply fan defined'
                        pass
                    
                    #print sch
                    #print ptac
                #hvac.setName = "PTAC_i"

                
            elif systemIndex == 2:
                # 2: PTHP, Residential - thermalZoneVector because ZoneHVAC
                ops.OpenStudioModelHVAC.addSystemType2(model, thermalZoneVector)
                
            elif systemIndex == 3:
                print ''
                for zone in thermalZoneVector:
                    handle = ops.OpenStudioModelHVAC.addSystemType3(model).handle()
                    print handle
                    print HVACDetails
                    airloop = model.getAirLoopHVAC(handle).get()
                    airloop.addBranchForZone(zone)
                    print 'zone added to PSZ air loop'
                    oasys = airloop.airLoopHVACOutdoorAirSystem()
                    if oasys.is_initialized():
                        print 'overriding the OpenStudio airside economizer settings'
                        oactrl = oasys.get().getControllerOutdoorAir()
                        #set control type
                        #can sensed min still be dry bulb for any of these?  Future release question
                        econo = self.recallOASys(HVACDetails)
                        oactrl = self.updateOASys(econo,oactrl)
                        print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                        print ''

                    #apply fan changes
                    if len(HVACDetails['constVolSupplyFanDef']) > 0:
                        print 'overriding the OpenStudio supply fan settings'
                        x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:ConstantVolume"))
                        cvfan = model.getFanConstantVolume(x[0].handle()).get()
                        sf = self.recallCVFan(HVACDetails)
                        cvfan = self.updateCVFan(sf,cvfan)
                        print 'supply fan settings updated to supply fan name: ' + HVACDetails['constVolSupplyFanDef']['name']

                    comps = airloop.supplyComponents()
                    #the default is a single speed compressor
                    #what happens if the user changes to a 2speed compressor?
                    c = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:SingleSpeed"))
                    handle = c[0].handle()
                    coil = model.getCoilCoolingDXSingleSpeed(handle).get()
                    print type(coil)
            elif systemIndex == 4:
                for zone in thermalZoneVector:
                    handle = ops.OpenStudioModelHVAC.addSystemType4(model).handle()
                    print handle
            elif systemIndex == 5:
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType5(model).handle()
                # get the airloop
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                # add branches
                for zone in thermalZoneVector:
                    airloop.addBranchForZone(zone)

                    
                oasys = airloop.airLoopHVACOutdoorAirSystem() 
                
                if oasys.is_initialized():
                    print 'overriding the OpenStudio airside economizer settings'
                    oactrl = oasys.get().getControllerOutdoorAir()






                    #set control type
                    #can sensed min still be dry bulb for any of these?  Future release question
                    print HVACDetails
                    econo = self.recallOASys(HVACDetails)
                    oactrl = self.updateOASys(econo,oactrl)
                    print 'economizer settings updated to economizer name: ' + HVACDetails['airsideEconomizer']['name']
                    print ''
                #the fan by default is variable volume, it will never be constant volume
                x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                sf = model.getFanVariableVolume(x[0].handle()).get()
                if len(HVACDetails['varVolSupplyFanDef']) > 0:
                    print 'overriding the OpenStudio supply fan settings'
                    x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                    vvfan = model.getFanVariableVolume(x[0].handle()).get()







                    sf = self.recallVVFan(HVACDetails)
                    vvfan = self.updateVVFan(sf,vvfan)
                    print 'supply fan settings updated to supply fan name: ' + HVACDetails['varVolSupplyFanDef']['name']
                
                #the default is s two speed coil.  not sure what happens if they assign a one speed
                x = airloop.supplyComponents(ops.IddObjectType("OS:Coil:Cooling:DX:TwoSpeed"))
                coolcoil = model.getCoilCoolingDXTwoSpeed(x[0].handle()).get()
                print coolcoil.getRatedHighSpeedAirFlowRate() #OpenStudio blank
                print coolcoil.getRatedHighSpeedTotalCoolingCapacity() #OpensStudio blank
                print coolcoil.getRatedHighSpeedSensibleHeatRatio() #OpenStudio blank
                print coolcoil.getRatedHighSpeedCOP() #OpenStudio 3
                print coolcoil.getRatedLowSpeedCOP() # OpenStudio 3
                print coolcoil.getRatedLowSpeedTotalCoolingCapacity() # OpenStudio blank
                print coolcoil.getRatedLowSpeedSensibleHeatRatio() # OpenStudio 0.69
                print coolcoil.getRatedLowSpeedAirFlowRate() #OpenStudio blank
                coolcoil.setRatedHighSpeedCOP(4.5)
                coolcoil.setRatedLowSpeedCOP(3.7)
                coolcoil.setCondenserType("EvaporativelyCooled")
                coolcoil.setHighSpeedEvaporativeCondenserEffectiveness(0.9)
                coolcoil.setHighSpeedEvaporativeCondenserAirFlowRate(ops.OptionalDouble(3.5))
                coolcoil.setLowSpeedEvaporativeCondenserEffectiveness(0.85)
                coolcoil.setLowSpeedEvaporativeCondenserAirFlowRate(ops.OptionalDouble(2.0))
                    
                print "success for cooling coil"
                #x = airloop.supplyComponents(ops.IddObjectType("")


                
                
            elif systemIndex == 7:
                hvacHandle = ops.OpenStudioModelHVAC.addSystemType7(model).handle()
                # get the airloop
                airloop = model.getAirLoopHVAC(hvacHandle).get()
                # add branches
                for zone in thermalZoneVector:
                    airloop.addBranchForZone(zone)
                
                oasys = airloop.airLoopHVACOutdoorAirSystem() 
                if oasys.is_initialized():
                    oactrl = oasys.get().getControllerOutdoorAir()
                    oactrl.autosizeMinimumOutdoorAirFlowRate()
                    oactrl.setEconomizerControlType("FixedDryBulb")
                    oactrl.setEconomizerMinimumLimitDryBulbTemperature(12)
                    oactrl.setEconomizerMaximumLimitDryBulbTemperature(21)
                    oactrl.setLockoutType("LockoutWithCompressor")
                    print "Sys 7: success for economizer!"
                    
                    x = airloop.supplyComponents(ops.IddObjectType("OS:Fan:VariableVolume"))
                    fan = model.getFanVariableVolume(x[0].handle()).get()
                    
                    fan.setFanEfficiency(0.79)
                    fan.setMotorEfficiency(0.92)
                    fan.setPressureRise(1000)
                    fan.setFanPowerMinimumFlowFraction(0.2)
                    print "Sys 7:  success for fan setup"
                

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
        ventilation.setOutdoorAirFlowRate(0)
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
        try:
            if values[14].lower() == "no":
                standardGlazing.setSolarDiffusing(False)
            else:
                standardGlazing.setSolarDiffusing(True)
        except:
            pass
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
            
            # create construction
            if not self.isConstructionInLib(surface.EPConstruction):
                construction = self.getOSConstruction(surface.construction, model)
                
                # keep track of constructions
                self.addConstructionToLib(surface.EPConstruction, construction)
            else:
                construction = self.getConstructionFromLib(surface.EPConstruction)

            thisSurface.setConstruction(construction)
            thisSurface.setOutsideBoundaryCondition(surface.BC)
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
                construction = self.getConstructionFromLib(childSrf.EPConstruction)
            
            
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
            
            # generate OpenStudio points
            shdPointVectors = ops.Point3dVector();
            
            for shadingCount, ptList in enumerate(coordinates):
                for pt in ptList:
                    # add the points to an openStudio list
                    shdPointVectors.Add(ops.Point3d(pt.X,pt.Y,pt.Z))
                
                shdSurface = ops.ShadingSurface(shdPointVectors, model)
                shdSurface.setName("shdSurface_" + str(surfaceCount) + "_" + str(shadingCount))
                shdSurface.setShadingSurfaceGroup(shadingGroup)
                
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
                    print fields
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
                
                

class RunOPS(object):
    def __init__(self, model, weatherFilePath = r"C:\EnergyPlusV8-1-0\WeatherData\USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.EPPath = ops.Path(r"C:\EnergyPlusV8-1-0\EnergyPlus.exe")
        self.epwFile = ops.Path(weatherFilePath)
        self.iddFile = ops.Path(r"C:\EnergyPlusV8-1-0\Energy+.idd")
        self.model = model
        
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
        
        #DBPath = ops.Path(os.path.join(projectFolder, projectName + "_osmToidf.db"))
        
        # start run manager
        #rm = ops.RunManager(DBPath, True, True)        
        
        # create workflow
        #wf = ops.Workflow("EnergyPlus")
        
        # put in queue and let it go
        #rm.enqueue(wf.create(ops.Path(projectFolder), osmPath, self.epwFile), True)
        #rm.setPaused(False)
        
        #while rm.workPending():
        #    time.sleep(.5)
        #    print "Converting osm to idf ..."
        
        #rm.Dispose() # don't remove this as Rhino will crash if you don't dispose run manager
        
        return idfFolder, idfFilePath
        
    def runAnalysis(self, osmFile, useRunManager = False):
        
        # Preparation
        workingDir, fileName = os.path.split(osmFile)
        projectName = (".").join(fileName.split(".")[:-1])
        osmPath = ops.Path(osmFile)
        
        # create idf - I separated this job as putting them together
        # was making EnergyPlus to crash
        idfFolder, idfPath = self.osmToidf(workingDir, projectName, osmPath)
        
        if not useRunManager:
            
            resultFile = self.writeBatchFile(idfFolder, "ModelToIdf\\in.idf", self.weatherFile, EPDirectory = 'C:\\EnergyPlusV8-1-0')
            return os.path.join(idfFolder, "ModelToIdf", "in.idf"), resultFile
        
        outputPath = ops.Path(idfFolder)
        
        rmDBPath = ops.Path(os.path.join(idfFolder, projectName + ".db"))
        try:
            rm = ops.RunManager(rmDBPath, True, True)
            
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
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0'):
        """
        This is here as an alternate until I can get RunManager to work
        """
        workingDrive = workingDir[:2]
        if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
        else: shIdfFileName = idfFileName
        
        if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
        
        fullPath = workingDir + shIdfFileName
        
        folderName = workingDir.replace( (workingDrive + '\\'), '')
        batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
                '\\Epl-run ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'
    
        batchFileAddress = fullPath +'.bat'
        batchfile = open(batchFileAddress, 'w')
        batchfile.write(batchStr)
        batchfile.close()
        
        #execute the batch file
        os.system(batchFileAddress)
        
        return fullPath + "Zsz.csv"

class RunOPSRManage(object):
    def __init__(self, model, measuredict, weatherFilePath = r"C:\EnergyPlusV8-1-0\WeatherData\USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"):
        self.weatherFile = weatherFilePath # just for batch file as an alternate solution
        self.EPPath = ops.Path(r"C:\EnergyPlusV8-1-0\EnergyPlus.exe")
        self.epwFile = ops.Path(weatherFilePath)
        self.iddFile = ops.Path(r"C:\EnergyPlusV8-1-0\Energy+.idd")
        self.model = model
        self.measuredict = measuredict
        
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
        
        #DBPath = ops.Path(os.path.join(projectFolder, projectName + "_osmToidf.db"))
        
        # start run manager
        #rm = ops.RunManager(DBPath, True, True)        
        
        # create workflow
        #wf = ops.Workflow("EnergyPlus")
        
        # put in queue and let it go
        #rm.enqueue(wf.create(ops.Path(projectFolder), osmPath, self.epwFile), True)
        #rm.setPaused(False)
        
        #while rm.workPending():
        #    time.sleep(.5)
        #    print "Converting osm to idf ..."
        
        #rm.Dispose() # don't remove this as Rhino will crash if you don't dispose run manager
        
        return idfFolder, idfFilePath
        
    def runAnalysis(self, osmFile, RunSimulation = False):
        

        # Preparation
        workingDir, fileName = os.path.split(osmFile)
        projectName = (".").join(fileName.split(".")[:-1])
        osmPath = ops.Path(osmFile)
        
        
        projectFolder =os.path.join(workingDir, projectName)
        
        try: os.mkdir(projectFolder)
        except: pass
        
        try:
            # create idf - I separated this job as putting them together
            # was making EnergyPlus to crash
            #idfFolder, idfPath = self.osmToidf(workingDir, projectName, osmPath)
            zone_handles = " "
            #remote = ops.RemoteBCL()
            #remote.downloadComponent("5f126600-ca2f-4611-9121-6dfea2de49d6")
            bclfile = 'C:\\Users\\Chiensi\\BCL\\5f126600-ca2f-4611-9121-6dfea2de49d6\\e83a66c9-c8d6-4896-a979-ba75f3dacb02'
            #local = ops.LocalBCL()
            #print dir(local)
            #measure = local.getMeasure("5f126600-ca2f-4611-9121-6dfea2de49d6")
            
            #measure = component.files("rb")
            #if measure.empty == True:
            #  print 'No .rb file found'
            #  assert False
            #  return
            
            #measure_path = component.files("rb")[0]
            bclpath = ops.Path(bclfile)
            #measure_root_path = os.path.dirname(bclpath)
            #print measure_root_path
            
            bcl_measure = ops.BCLMeasure(bclpath)
            
            DBPath = ops.Path(os.path.join(projectFolder, projectName + "_osmToidf.db"))
            run_manager = ops.RunManager(DBPath,True)
            #run_manager.setPaused(true)
            
            values = []
            ruleset = ops.OpenStudioRuleset()
            #print dir(ruleset)
            
            # arguments = ruleset.getArguments(bcl_measure,model)
            arguments = ""
            zone_arg = arguments[0]
            zone_arg.setValue(zone_handles)
            values.append(zone_arg)
            
            rjb = ops.Runmanager.RubyJobBuilder(bcl_measure,values)
            #rjb.setIncludeDir(OpenStudiio::Path.new("$OpenStudio_Dir")
    
            workflow = ops.Runmanager.Workflow()
            workflow.addJob(rjb.toWorkItem())
    
            if RunSimulation:
                workflow.addJob(ops.Runmanager.JobType("ModelToIdf"))
                workflow.addJob(ops.Runmanager.JobType("EnergyPlusPreProcess"))
                workflow.addJob(ops.Runmanager.JobType("EnergyPlus"))
            
            co = ops.RunManager.ConfigOptions()
            co.fastFindEnergyPlus()
            co.findTools(False)
           
            tools = co.getTools()
            workflow.add(tools)
    
            
            job = workflow.create(projectFolder, osmPath, self.epwFile)
            run_manager.enqueue(job, false)
            run_manager.waitForFinished()
        

                
        except Exception, e:
             try: 
                run_manager.Dispose() # in case anything goes wrong it closes the rm
             except: 
                pass
             print `e`
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0'):
        """
        This is here as an alternate until I can get RunManager to work
        """
        workingDrive = workingDir[:2]
        if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
        else: shIdfFileName = idfFileName
        
        if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
        
        fullPath = workingDir + shIdfFileName
        
        folderName = workingDir.replace( (workingDrive + '\\'), '')
        batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
                '\\Epl-run ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'
    
        batchFileAddress = fullPath +'.bat'
        batchfile = open(batchFileAddress, 'w')
        batchfile.write(batchStr)
        batchfile.close()
        
        #execute the batch file
        os.system(batchFileAddress)
        return fullPath + ".csv"

def main(HBZones, HBContext, north, epwWeatherFile, analysisPeriod, simParameters, simulationOutputs, runIt, workingDir = "C:\ladybug", fileName = "openStudioModel.osm"):
    
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
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
    
    for zoneCount, zone in enumerate(HBZones):
        
        # prepare non-planar zones
        if zone.hasNonPlanarSrf or zone.hasInternalEdge:
            zone.prepareNonPlanarZone(meshingLevel = 1)
    
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
        HAVCGroupID, HVACIndex, HVACDetails = zone.HVACSystem
        
        if HAVCGroupID!= -1:
            if HAVCGroupID not in hb_writeOPS.HVACSystemDict.keys():
                # add place holder for lists 
                
                hb_writeOPS.HVACSystemDict[HAVCGroupID] = [HVACIndex,[],HVACDetails]
        
        # collect informations for systems here
        hb_writeOPS.HVACSystemDict[HAVCGroupID][1].append(thermalZone)


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
        
    
    # this should be done once for the whole model
    hb_writeOPS.setAdjacentSurfaces()
    
    # add systems
    hb_writeOPS.addSystemsToZones(model)
    
    # add shading surfaces if any
    if HBContext != []:
        shdingSurfcaes = hb_hive.callFromHoneybeeHive(HBContext)
        hb_writeOPS.OPSShdSurface(shdingSurfcaes, model)
    
    # outputs
    hb_writeOPS.setOutputs(simulationOutputs, model)
    
    #save the model
    model.save(ops.Path(fname), True)
    
    print "Model saved to: " + fname

    if runIt:
        hb_runOPS = RunOPS(model, epwWeatherFile)
        #hb_runOPSRm = RunOPSRManage(model, hb_writeOPS.HVACSystemDict, epwWeatherFile)
        #hb_runOPSRm.runAnalysis(fname, False)
        idfFile, resultFile = hb_runOPS.runAnalysis(fname, useRunManager = False)
        #this is the zone group id
                # add HVAC system

            
        return fname, idfFile, resultFile
        
    return fname, None, None

if _epwWeatherFile and _writeOSM and openStudioIsReady:
    results = main(_HBZones, HBContext_, north_, _epwWeatherFile,
                  _analysisPeriod_, _energySimPar_, simulationOutputs_,
                  runSimulation_, workingDir_, fileName_)
    
    if results!=-1:
        osmFileAddress, idfFileAddress, resultsFileAddress = results