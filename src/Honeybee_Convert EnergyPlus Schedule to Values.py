# This component creates a 3D chart of hourly or daily data.
# By Chris Mackey and Mostapha Sadeghipour Roudsari
# Chris@MackeyArchitecture.com and Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to make a 3D chart in the Rhino scene of any climate data or hourly simulation data.
-
Provided by Ladybug 0.0.57
    
    Args:
        _schName: Name of the EP schedule
        _weekStDay_: Day to be considered as the start of the week. Default is Sunday.[0]: Sunday, [1]: Monday, [2]: Tuesday, [3]: Wednesday, [4]: Thursday, [5]: Friday, [6]: Saturday
    Returns:
        values: Hourly values
"""

ghenv.Component.Name = "Honeybee_Convert EnergyPlus Schedule to Values"
ghenv.Component.NickName = 'convertEPSCHValues'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

class ReadEPSchedules(object):
    
    def __init__(self, schName, startDayOfTheWeek):
        self.hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        self.hb_EPObjectsAUX = sc.sticky["honeybee_EPObjectsAUX"]()
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.schName = schName
        self.startDayOfTheWeek = startDayOfTheWeek
        self.count = 0
        self.startHOY = 1
        self.endHOY = 24
        self.unit = "unknown"
    
    def getScheduleTypeLimitsData(self, schName):
        
        if schName == None: schName = self.schName
            
        schedule, comments = self.hb_EPScheduleAUX.getScheduleTypeLimitsDataByName(schName.upper(), ghenv.Component)
        try:
            lowerLimit, upperLimit, numericType, unitType = schedule[1:]
        except:
            lowerLimit, upperLimit, numericType = schedule[1:]
            unitType = "unknown"
        
        self.unit = unitType
        if self.unit == "unknown":
            self.unit = numericType
        
        return lowerLimit, upperLimit, numericType, unitType
    
    
    def getDayEPScheduleValues(self, schName = None):
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        typeLimitName = values[1]
        lowerLimit, upperLimit, numericType, unitType = \
                self.getScheduleTypeLimitsData(typeLimitName)
                
        numberOfDaySch = int((len(values) - 3) /2)
        
        hourlyValues = range(24)
        startHour = 0
        for i in range(numberOfDaySch):
            value = float(values[2 * i + 4])
            untilTime = map(int, values[2 * i + 3].split(":"))
            endHour = int(untilTime[0] +  untilTime[1]/60)
            for hour in range(startHour, endHour):
                hourlyValues[hour] = value
            
            startHour = endHour
        
        if numericType.strip().lower() == "district":
            hourlyValues = map(int, hourlyValues)
            
        return hourlyValues
    
    
    def getWeeklyEPScheduleValues(self, schName = None):
        """
        Schedule:Week:Daily
        ['Schedule Type', 'Sunday Schedule:Day Name', 'Monday Schedule:Day Name',
        'Tuesday Schedule:Day Name', 'Wednesday Schedule:Day Name', 'Thursday Schedule:Day Name',
        'Friday Schedule:Day Name', 'Saturday Schedule:Day Name', 'Holiday Schedule:Day Name',
        'SummerDesignDay Schedule:Day Name', 'WinterDesignDay Schedule:Day Name',
        'CustomDay1 Schedule:Day Name', 'CustomDay2 Schedule:Day Name']
        """
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        
        if self.count == 1:
            # set the last date of the schedule to one week
            self.endHOY = 24 * 7
        
        sundaySchedule = self.getScheduleValues(values[1])
        mondaySchedule = self.getScheduleValues(values[2])
        tuesdaySchedule = self.getScheduleValues(values[3])
        wednesdaySchedule = self.getScheduleValues(values[4])
        thursdaySchedule = self.getScheduleValues(values[5])
        fridaySchedule = self.getScheduleValues(values[6])
        saturdaySchedule = self.getScheduleValues(values[7])
        
        holidaySchedule = self.getScheduleValues(values[8])
        summerDesignDaySchedule = self.getScheduleValues(values[9])
        winterDesignDaySchedule = self.getScheduleValues(values[10])
        customDay1Schedule = self.getScheduleValues(values[11])
        customDay2Schedule = self.getScheduleValues(values[12])
        
        hourlyValues = [sundaySchedule, mondaySchedule, tuesdaySchedule, \
                       wednesdaySchedule, thursdaySchedule, fridaySchedule, \
                       saturdaySchedule]
        
        hourlyValues = hourlyValues[self.startDayOfTheWeek:] + \
                       hourlyValues[:self.startDayOfTheWeek]
        
        return hourlyValues
    
    
    def getConstantEPScheduleValues(self, schName):
        """
        'Schedule:Constant'
        ['Schedule Type', 'Schedule Type Limits Name', 'Hourly Value']
        """
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        typeLimitName = values[1]
        lowerLimit, upperLimit, numericType, unitType = \
                self.getScheduleTypeLimitsData(typeLimitName)
        
        hourlyValues = [float(values[2])]
        
        if numericType.strip().lower() == "district":
            hourlyValues = map(int, hourlyValues)
        return scheduleConstant
    
    
    def getYearlyEPScheduleValues(self, schName = None):
        # place holder for 365 days
        hourlyValues = range(365)
        
        # update last day of schedule
        self.endHOY = 8760
        
        if schName == None:
            schName = self.schName
        
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        
        # generate weekly schedules
        numOfWeeklySchedules = int((len(values)-2)/5)
        
        for i in range(numOfWeeklySchedules):
            weekDayScheduleName = values[5 * i + 2]
            
            startDay = int(self.lb_preparation.getJD(int(values[5 * i + 3]), int(values[5 * i + 4])))
            endDay = int(self.lb_preparation.getJD(int(values[5 * i + 5]), int(values[5 * i + 6])))
            
            # 7 list for 7 days of the week
            hourlyValuesForTheWeek = self.getScheduleValues(weekDayScheduleName)
            
            for day in range(startDay-1, endDay):
                hourlyValues[day] = hourlyValuesForTheWeek[day%7]
            
        return hourlyValues
    
    def getScheduleValues(self, schName = None):
        if schName == None:
            schName = self.schName
        if self.hb_EPObjectsAUX.isSchedule(schName):
            scheduleValues, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
            
            scheduleType = scheduleValues[0].lower()
            if self.count == 0:
                self.schType = scheduleType

            self.count += 1

            if scheduleType == "schedule:year":
                hourlyValues = self.getYearlyEPScheduleValues(schName)
            elif scheduleType == "schedule:day:interval":
                hourlyValues = self.getDayEPScheduleValues(schName)
            elif scheduleType == "schedule:week:daily":
                hourlyValues = self.getWeeklyEPScheduleValues(schName)
            elif scheduleType == "schedule:constant":
                hourlyValues = self.getConstantEPScheduleValues(schName)
            else:
                print "Honeybee doesn't support " + scheduleType + " currently." + \
                      "Email us the type and we will try to add it to Honeybee."
                      
                hourlyValues = []
            
            return hourlyValues



def main(schName, startDayOfTheWeek):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("ladybug_release"):
        print "You should first let Ladybug and Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug and Honeybee fly...")
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    readSchedules = ReadEPSchedules(schName, startDayOfTheWeek)
    values  = readSchedules.getScheduleValues()
    
    strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
    d, m, t = lb_preparation.hour2Date(readSchedules.startHOY, True)
    startDate = m+1, d, t
    
    d, m, t = lb_preparation.hour2Date(readSchedules.endHOY, True)
    endDate = m+1, d, t
    if readSchedules.endHOY%24 == 0:
        endDate = m+1, d, 24
    
    header = [strToBeFound, readSchedules.schType, readSchedules.schName, \
              readSchedules.unit, 'Hourly', startDate, endDate]
    
    try: values = lb_preparation.flattenList(values)
    except: pass
    
    return header + values

if _schName != None:
    try: _weekStDay_ = _weekStDay_%7
    except: _weekStDay_ = 0
    
    values = main(_schName, _weekStDay_)
