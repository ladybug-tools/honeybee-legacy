#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Antonello Di Nunzio <antonellodinunzio@gmail.com> and Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generate values for Honeybee_Create CSV Schedule
-
Use this component to write schedules for EnergyPlus using LB_schedules as inputs.
-
Provided by Ladybug 0.0.62
    
    Args:
        _sun: Sunday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        _mon: Monday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        _tue: Tuesday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        _wed: Wednesday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        _thu: Thursday. Connect a list of 24 values that represent the schedule value at each hour of the day..
        _fri: Friday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        _sat: Saturday. Connect a list of 24 values that represent the schedule value at each hour of the day.
        holiday_: Optional input for holidays. Connect a list of 24 values that represent the schedule value at each hour of the day. If no value is input here, the schedule for Sunday will be used for all holidays.
        coolDesignDay_: Optional input for the cooling design day that is used to size the system. Connect a list of 24 values that represent the schedule value at each hour of the day. If no value is input here, the schedule for Monday will be used for the cooling design day.
        heatDesignDay_: Optional input for the heating design day that is used to size the system. Connect a list of 24 values that represent the schedule value at each hour of the day. If no value is input here, the schedule for Sunday will be used for the heating design day.
        ------------: ...
        epwFileForHol_: If you want to generate a list of holiday DOYs automatically connect an .epw file path on your system as a string.
        startDayOfWeek_: Set the schedule start day of the week. The default is set to "monday".
            -
            Write one of the following string:
            1) sun
            2) mon
            3) tue
            4) wed
            5) thu
            6) fri
            7) sat
        
        customHolidays_: Connect a list of DOYs (from 1 to 365) or a list of strings (example: DEC 25).
            -
            Note that this input overwrites epwFile DOYs.
        _scheduleName_: An optional name for the schedule that will be written to the memory of the document.  If no name is connected here, a uniqui ID will be generated for the schedule.
        _schedTypeLimits_: A text string from the scheduleTypeLimits output of the "Honeybee_Call From EP Schedule Library" component.  This value represents the units of the schedule input values.  The default is "Fractional" for a schedule with values that range between 0 and 1.  Other common inputs include "Temperature", "On/Off", and "ActivityLevel".
        _generateValues: Set to "True" to generate hourly values of the schedule.
        writeSchedule_: Set to "True to write the schedule to the Honeybee library such that you can assign the schedule with other Honeybee components.
    Returns:
        readMe!: ...
        ---------------: ...
        schedule: The name of the schedule that has been written to the memory of the GH document.  Connect this to any shcedule input of a Honeybee component to assign the schedule.
        holidays: Dates of the holydays.  Plug these into the holidays_ input of the "Honeybee_Energy Sim Par" component to have them counted as part of the simulation.
        ---------------: ...
        weekSchedule: The name of the weekly schedule that has been written to the memory of the GH document.  If your final intended annual schedule is composed of weeks with different schedule, you can use this output with the "Honeybee_Combined Annual Schedule" to create schedules with different weeks.
        scheduleIDFText: The text needed to tell EnergyPlus how to run the schedule.  If you are done creating/editing a shcedule with this component, you may want to make your GH document smaller by internalizing this IDF text and using the "Honeybee_Add To EnergyPlus Library" component to make sure that the schedule is added to the memory the next time you open the GH file.
        scheduleValues: The hourly schedulevalues for the entire year.  Connect these to the "Ladybug_3D Chart" component for a visual of the schedule.  If you would rather assign the schedule as a CSV schedule, you can also use these values with the "Honeybee_Create CSV Schedule" component to assign them as a csv schedule.  Note that CSV schedules will not appear in .osm files written by the OpenStudio component.
"""

ghenv.Component.Name = "Honeybee_Annual Schedule"
ghenv.Component.NickName = 'AnnualSchedule'
ghenv.Component.Message = 'VER 0.0.60\nNOV_01_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
from collections import deque
import itertools
from datetime import date
import uuid


def flatten(container):
    for i in container:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i

def fromDayToDate(day, months):
    date_day = date.fromordinal(date(2015, 1, 1).toordinal() + day) # 2015 is not leap year
    
    month, day = str(date_day).split('-')[1:]
    months_date = months[month]
    date_fromDay = months_date + ' ' + day
    
    return date_fromDay

def fromDateToDay(holiday, months):
    
    start_date = date(2015, 1, 1)
    # split
    text_month = holiday.split(' ')[0].upper()
    # reverse dict
    dict_reverse = {value: key for key, value in months.items()}
    # extract value
    int_month = int(dict_reverse[text_month])
    end_date = date(2015, int_month, int(holiday.split(' ')[1]))
    
    period = end_date - start_date
    
    day = period.days + 1
    return day

def IFDstrFromDayVals(dayValues, schName, daytype, schTypeLims):
    idfStr = 'Schedule:Day:Interval,\n' + \
        '\t' + schName + ' Day Schedule - ' + daytype + ', !- Name\n' + \
        '\t' + schTypeLims + ', !- Schedule Type Limits Name\n' + \
        '\t' + 'No,        !- Interpolate to Timestep\n'
    
    tCount = 1
    for hCount, val in enumerate(dayValues):
        if hCount+1 == len(dayValues):
            idfStr = idfStr + '\t24:00,   !- Time ' + str(tCount) + ' {hh:mm}\n' + \
                '\t' + str(val) + ';     !- Value Until Time ' + str(tCount) + '\n'
        elif val == dayValues[hCount+1]: pass
        else:
            idfStr = idfStr + '\t' + str(hCount+1) + ':00,   !- Time ' + str(tCount) + ' {hh:mm}\n' + \
                '\t' + str(val) + ',     !- Value Until Time ' + str(tCount) + '\n'
            tCount += 1
    
    return idfStr

def IFDstrForWeek(daySchedNames, schName):
    idfStr = 'Schedule:Week:Daily,\n' + \
        '\t' + schName + ' Week Schedule' + ', !- Name\n' + \
        '\t' + daySchedNames[0] + ',  !- Sunday Schedule:Day Name\n' + \
        '\t' + daySchedNames[1] + ',  !- Monday Schedule:Day Name\n' + \
        '\t' + daySchedNames[2] + ',  !- Tuesday Schedule:Day Name\n' + \
        '\t' + daySchedNames[3] + ',  !- Wednesday Schedule:Day Name\n' + \
        '\t' + daySchedNames[4] + ',  !- Thursday Schedule:Day Name\n' + \
        '\t' + daySchedNames[5] + ',  !- Friday Schedule:Day Name\n' + \
        '\t' + daySchedNames[6] + ',  !- Saturday Schedule:Day Name\n' + \
        '\t' + daySchedNames[7] + ',  !- Holiday Schedule:Day Name\n' + \
        '\t' + daySchedNames[8] + ',  !- SummerDesignDay Schedule:Day Name\n' + \
        '\t' + daySchedNames[9] + ',  !- WinterDesignDay Schedule:Day Name\n' + \
        '\t' + daySchedNames[0] + ',  !- CustomDay1 Schedule:Day Name\n' + \
        '\t' + daySchedNames[0] + ';  !- CustomDay2 Schedule:Day Name\n'
    
    return idfStr

def IFDstrForYear(weekSchedName, schName, schTypeLims):
    idfStr = 'Schedule:Year,\n' + \
        '\t' + schName + ' Year Schedule' + ', !- Name\n' + \
        '\t' + schTypeLims + ', !- Schedule Type Limits Name\n' + \
        '\t' + weekSchedName + ',  !- Schedule:Week Name\n' + \
        '\t' + '1' + ',  !- Start Month 1\n' + \
        '\t' + '1' + ',  !- Start Day 1\n' + \
        '\t' + '12' + ',  !- End Month\n' + \
        '\t' + '31' + ';  !- End Day\n'
    
    return idfStr

def main(sun, mon, tue, wed, thu, fri, sat, holiday, hdd, cdd, runIt, epwFile, weekStartWith, overwriteHolidays, scheduleName, schedTypeLimits):
    # Import the classes.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    scheduleTypeLimitsLib = sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    
    # dict of months
    months_dict = {'01':'JAN', '02':'FEB', '03':'MAR', '04':'APR', '05':'MAY', '06':'JUN',
    '07':'JUL', '08':'AUG', '09':'SEP', '10':'OCT', '11':'NOV', '12':'DEC'}
    
    # build the week
    def rotate_week(weekStartWith):
        days_of_week = {'sat':0, 'sun':1, 'mon':2, 'tue':3, 'wed':4, 'thu':5, 'fri':6}
        nums_of_week = {'7':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6}
        list_of_values = [0, 1, 2, 3, 4, 5, 6]
        d = deque(list_of_values)
        try:
            lower_key = weekStartWith.lower()
            d.rotate(-days_of_week[lower_key])
        except:
            d.rotate(-nums_of_week[weekStartWith])
        return d
        
    # default value
    if weekStartWith:
        weekStartWith = weekStartWith
    else:
        weekStartWith = 'mon'
    
    # run the funcion
    week = rotate_week(weekStartWith)
    # make a year by cutting the list
    dayWeekList = list(itertools.chain.from_iterable(itertools.repeat(week, 53)))[:365]
    
    #first loop: if epwFile is on
    if epwFile:
        #get the base code from EPW
        locationData = lb_preparation.epwLocation(epwFile)
        codeNation = lb_preparation.epwDataReader(epwFile, locationData[0])[14][1]
        code = codeNation.split("_")
        if len(code) == 3:
            country = code[2]
        elif len(code) == 2:
            country = code[1]
        else:
            country = code[1]
        print country
        
        if not overwriteHolidays:
            #only National Hoildays arranged by region
            #not found list:
            #BLZ (CENTRAL AMERICA), BRN (SOUTH PACIFIC), GUM (SOUTH PACIFIC), MHL (SOUTH PACIFIC), PLW (SOUTH PACIFIC), UMI (SOUTH PACIFIC)
            #https://energyplus.net/weather
            ###################################################
            #http://www.officeholidays.com/countries/ ------ http://www.officeholidays.com/countries/
            countries = {'USA':[0,[i for i, x in enumerate(dayWeekList) if x == 2][2],[i for i, x in enumerate(dayWeekList) if x == 2][21],184,[i for i, x in enumerate(dayWeekList) if x == 2][35],314,[i for i, x in enumerate(dayWeekList) if x == 5][46],359],
            'CAN': [0,181,[i for i, x in enumerate(dayWeekList) if x == 2][35],358,359],
            'CUB': [0,1,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,205,206,207,282,358,364],
            'GTM': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,180,257,292,304,358],
            'HND': [0,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,257,278,358],
            'MEX': [0,[i for i, x in enumerate(dayWeekList) if x == 2][4],[i for i, x in enumerate(dayWeekList) if x == 2][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,258,[i for i, x in enumerate(dayWeekList) if x == 2][46],345,358,359],
            'MTQ': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,127,[i for i, x in enumerate(dayWeekList) if x == 2][19],194,226,304,314,358],
            'NIC': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,121,169,256,257,341,358],
            'PRI': [0,5,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 2][12],127,169,327,358],
            'SLV': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,129,168,215,216,217,305,358,359],
            'VIR': [0,5,17,45,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],89,149,153,248,304,314,358,359],
            'ARG': [0,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],82,[i for i, x in enumerate(dayWeekList) if x == 6][12],91,120,144,170,188,189,[i for i, x in enumerate(dayWeekList) if x == 2][32],282,[i for i, x in enumerate(dayWeekList) if x == 2][47],341,358],
            'BOL': [0,21,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],[i for i, x in enumerate(dayWeekList) if x == 5][11],120,[i for i, x in enumerate(dayWeekList) if x == 5][20],171,305,358],
            'BRA': [0,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],[i for i, x in enumerate(dayWeekList) if x == 4][5],[i for i, x in enumerate(dayWeekList) if x == 5][11],110,120,[i for i, x in enumerate(dayWeekList) if x == 5][20],249,284,305,318,323,358],
            'CHL': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],120,140,179,196,226,261,262,303,304,341,358],
            'COL': [0,10,79,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,128,149,156,[i for i, x in enumerate(dayWeekList) if x == 2][26],200,218,226,289,[i for i, x in enumerate(dayWeekList) if x == 2][44],317,341,358],
            'ECU': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 1][12],120,143,221,281,306,358],
            'PER': [0,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],120,179,208,209,242,280,304,341,358,359],
            'PRY': [0,59,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 1][12],120,133,134,162,227,271,284,341,358,364],
            'URY': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],108,120,169,198,284,236,305,358],
            'VEN': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],108,120,174,179,185,204,226,284,304,358,359,364],
            'AUS': [0,25,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],114,358,359,360],
            'FJI': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],174,249,282,303,345,359,360],
            'MYS': [38,120,121,140,155,186,187,242,254,258,274,345,358,359],
            'NZL': [0,3,38,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],114,[i for i, x in enumerate(dayWeekList) if x == 2][22],[i for i, x in enumerate(dayWeekList) if x == 2][42],358,359,360],
            'PHL': [0,1,38,55,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],98,120,162,187,232,240,253,303,304,333,357,358,363,364],
            'SGP': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,121,140,218,220,254,302,358,359],
            'DZA': [0,120,187,253,274,283,304,345],
            'EGY': [6,24,114,120,121,187,188,189,204,253,254,255,274,278,345],
            'ETH': [6,19,60,119,120,124,147,253,255,269,345],
            'GHA': [0,64,65,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,121,144,181,186,253,263,[i for i, x in enumerate(dayWeekList) if x == 6][48],358,359],
            'KEN': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,187,253,292,345,358,359],
            'LBY': [47,120,187,188,252,253,254,255,258,274,295,345,357],
            'MAR': [0,10,120,188,210,225,231,232,253,274,309,321,345],
            'MDG': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],88,120,124,135,176,226,304,345,358],
            'SEN': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],93,120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],187,226,255,304,345,358],
            'TUN': [0,13,78,98,120,187,188,189,205,224,253,254,255,274,287,345],
            'ZAF': [0,79,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],117,120,121,166,220,266,349,358,359],
            'ZWE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],107,120,144,[i for i, x in enumerate(dayWeekList) if x == 2][31],[i for i, x in enumerate(dayWeekList) if x == 3][31],355,358,359],
            'ARE': [0,124,186,187,252,253,254,255,274,333,335,336,344],
            'BDG': [51,75,84,103,120,140,142,181,183,185,187,226,236,253,254,255,283,284,345,349,358],
            'CHN': [0,37,38,39,40,41,42,43,93,120,121,159,257,258,273,274,275,276,277,278,279],
            'IND': [25,226,274],
            'IRN': [41,71,77,78,79,80,81,89,90,110,124,141,153,154,170,177,187,211,255,263,264,283,284,324,325,350,354],
            'JPN': [0,[i for i, x in enumerate(dayWeekList) if x == 2][1],41,79,118,122,123,124,[i for i, x in enumerate(dayWeekList) if x == 2][28],222,[i for i, x in enumerate(dayWeekList) if x == 2][37],264,282,306,326,356],
            'KAZ': [0,6,59,66,79,80,81,91,98,187,241,253,334,349,352],
            'KOR': [0,37,38,39,40,59,124,133,156,226,256,257,258,275,281,358],
            'KWT': [2,55,56,124,156,157,158,252,253,254,255,274,345],
            'LKA': [14,22,34,52,65,80,[i for i, x in enumerate(dayWeekList) if x == 6][12],102,103,110,120,140,141,169,186,199,228,254,284,301,317,345,346,358],
            'MAC': [0,38,39,40,94,120,258,273,293,353],
            'MDV': [0,11,120,156,186,206,253,254,274,306,314,334,345,364],
            'MNG': [0,38,191,192,193,194,195,362],
            'NPL': [14,49],
            'PAK': [35,81,120,187,188,189,225,253,254,283,312,345,358],
            'PRK': [0,39,46,52,104,114,120,156,169,207,236,251,281,357,360],
            'SAU': [187,190,191,253,254,255,264,265],
            'THA': [0,52,95,102,103,104,121,124,126,127,139,168,169,223,296,338,345,364],
            'TWN': [0,37,38,39,40,41,42,93,120,128,257,282],
            'UZB': [0,13,66,79,98,187,243,255,273,341],
            'VNM': [0,36,37,38,39,40,105,106,119,120,121,122,244],
            'AUT': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],145,226,298,304,311,341,358,359],
            'BEL': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],201,226,304,314,358],
            'BRG': [0,61,62,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],125,141,247,248,264,265,357,358,359],
            'BIH': [0,1,120,121],
            'BLR': [0,6,7,65,66,120,128,129,183,310,358],
            'CHE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],124,212,358],
            'CYP': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][10],83,90,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][24],226,273,300,358,359],
            'CZE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,127,185,186,270,300,320,357,358,359],
            'DEU': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],275,358,359],
            'DNK': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],[i for i, x in enumerate(dayWeekList) if x == 6][16],124,[i for i, x in enumerate(dayWeekList) if x == 2][19],155,357,358,359],
            'ESP': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,226,284,304,339,341,358],
            'FIN': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,174,175,308,340,357,358,359],
            'FRA': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,127,[i for i, x in enumerate(dayWeekList) if x == 2][19],194,226,304,314,358],
            'GBR': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],121,149,359,360],
            'GRC': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][10],83,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][24],226,300,358],
            'HUN': [0,73,[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,[i for i, x in enumerate(dayWeekList) if x == 1][19],[i for i, x in enumerate(dayWeekList) if x == 2][19],231,295,304,358,359],
            'IRL': [0,75,[i for i, x in enumerate(dayWeekList) if x == 2][12],[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][22],[i for i, x in enumerate(dayWeekList) if x == 2][30],303,358,359,360],
            'ISL': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],110,120,124,[i for i, x in enumerate(dayWeekList) if x == 1][19],[i for i, x in enumerate(dayWeekList) if x == 2][19],167,212,357,358,359,364],
            'ISR': [82,113,119,131,163,225,275,276,284,289,297],
            'ITA': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][12],114,120,152,226,304,341,358,359],
            'LTU': [0,46,69,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,[i for i, x in enumerate(dayWeekList) if x == 1][22],174,186,226,304,357,358,359],
            'NLD': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],116,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],358],
            'NOR': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],136,358,359],
            'POL': [0,5,[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,122,134,145,226,304,314,358,359],
            'PRT': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],114,120,160,226,341,357,358],
            'ROU': [0,1,23,120,[i for i, x in enumerate(dayWeekList) if x == 2][17],170,226,333,334,358,359],
            'RUS': [0,3,4,5,6,53,66,120,128,163,307],
            'SRB': [0,1,6,7,45,46,[i for i, x in enumerate(dayWeekList) if x == 6][17],[i for i, x in enumerate(dayWeekList) if x == 0][17],[i for i, x in enumerate(dayWeekList) if x == 1][17],[i for i, x in enumerate(dayWeekList) if x == 2][17],128,283],
            'SVK': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,127,155,240,243,257,273,289,357,358,359],
            'SVN': [0,38,[i for i, x in enumerate(dayWeekList) if x == 2][12],116,120,121,175,226,303,304,358,359],
            'SWE': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,156,174,175,277,357,358,359,364],
            'SYR': [0,66,106,120,125,187,255,275,278,345,358],
            'TUR': [0,112,120,138,157,158,159,241,253,254,255,256,301],
            'UKR': [0,6,66,120,[i for i, x in enumerate(dayWeekList) if x == 2][17],127,128,[i for i, x in enumerate(dayWeekList) if x == 2][24],235,286,324]}
            
            if countries[country]:
                country_selected = countries[country]
            else: country_selected = [0,120,358,359] # not found countries
            
            #change id value and debug message holiday
            if len(holiday) == 24:
                holidays = country_selected
                for index in sorted(holidays, reverse=True):
                    dayWeekList[index] = 7
                print "National holidays(DOYs): "
                for item in country_selected:
                    print item+1
        else:
            # if overwriteHolidays is string
            try:
                if overwriteHolidays is not type(int):
                    overwriteHolidays = map(int, overwriteHolidays)
            except ValueError:
                customHolidays_day = []
                for item in overwriteHolidays:
                    day_date = fromDateToDay(item, months_dict)
                    customHolidays_day.append(day_date)
                overwriteHolidays = customHolidays_day
                
            country_selected = []
            for item in overwriteHolidays:
                country_selected.append(item-1)
            if len(holiday) == 24:
                holidays = country_selected
                for index in sorted(holidays, reverse=True):
                    dayWeekList[index] = 7
                print "National holidays(DOYs): "
                for item in country_selected:
                    print item+1
    #second loop: if epwFile is off and overwriteHolidays is on
    if epwFile == None and overwriteHolidays:
        # if overwriteHolidays is string
        try:
            if overwriteHolidays is not type(int):
                overwriteHolidays = map(int, overwriteHolidays)
        except ValueError:
            customHolidays_day = []
            for item in overwriteHolidays:
                day_date = fromDateToDay(item, months_dict)
                customHolidays_day.append(day_date)
            overwriteHolidays = customHolidays_day
        country_selected = []
        for item in overwriteHolidays:
            country_selected.append(item-1)
        if len(holiday) == 24:
            holidays = country_selected
            for index in sorted(holidays, reverse=True):
                dayWeekList[index] = 7
            print "National holidays(DOYs): "
            for item in country_selected:
                print item+1
    #third condition: if holiday_ is on and epw and/or overwrite are off
    if epwFile and not holiday:
        warning = "You have connected an epwFileForHol_ but not a holiday_ schedule. \nAs a result, the component doesn't know what happens on the holidays and so no holidays are written."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    elif overwriteHolidays and not holiday:
        warning = "You have connected an customHolidays_ but not a holiday_ schedule. \nAs a result, the component doesn't know what happens on the holidays and so no holidays are written."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    try:
        # nested lists for the whole year
        for n,i in enumerate(dayWeekList):
            if i==0:
                dayWeekList[n]= sat
            elif i ==1:
                dayWeekList[n]= sun
            elif i ==2:
                dayWeekList[n]= mon
            elif i ==3:
                dayWeekList[n]= tue
            elif i ==4:
                dayWeekList[n]= wed
            elif i ==5:
                dayWeekList[n]= thu
            elif i ==6:
                dayWeekList[n]= fri
            elif i ==7:
                dayWeekList[n]= holiday
                
    except: pass
    annualSchedule = list(flatten(dayWeekList))
    
    HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod([(1,1,1),(12,31,24)], 1)
    max = HOYS[len(HOYS)-1]
    min = HOYS[0]-1
    
    # Output the national holidays
    nationalHolidays = []
    if holiday and(epwFile or overwriteHolidays):
        for day in country_selected:
            nationalHolidays.append(fromDayToDate(day, months_dict))
    scheduleValues = annualSchedule[min:max]
    
    # Generate a schedule IDF string if writeSchedule_ is set to True.
    schedName = None
    daySchName = None
    weekSchedName = None
    yearSchedName = None
    daySchedCollection = []
    daySchNameCollect = []
    schedIDFStrs = []
    daySchedNames = []
    
    daySchedDict = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Sat', 6:'Fri', 7:'Hol', 8:'CDD', 9:'HDD'}
    if writeSchedule_:
        # Make a name for the schedule.
        if scheduleName == None:
            guid = str(uuid.uuid4())
            guidnumber = guid.split("-")[-1]
            schedName = 'Schedule-' + str(guidnumber)
            warning = "When writing a schedule into the schedule library, it is recommended that you give a unique _scheduleName_ to your schedule."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            schedName = scheduleName
        
        # Get the type limits for the schedule.
        if schedTypeLimits == None:
            schTypeLims = 'Fractional'
        else:
            schTypeLims = schedTypeLimits
            if schTypeLims.upper() not in scheduleTypeLimitsLib:
                warning = "Can't find the connected _schedTypeLimits_ '" + schTypeLims + "' in the Honeybee EP Schedule Library."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
            if schTypeLims.upper() == 'TEMPERATURE':
                schTypeLims = 'TEMPERATURE 1'
        
        # Write out text strings for the daily schedules
        for dCount, daySch in enumerate([sun, mon, tue, wed, thu, fri, sat, holiday, cdd, hdd]):
            if daySch not in daySchedCollection and daySch != []:
                daySchedCollection.append(daySch)
                schedIDFStrs.append(IFDstrFromDayVals(daySch, schedName, daySchedDict[dCount], schTypeLims))
                daySchName = schedName + ' Day Schedule - ' + daySchedDict[dCount]
                daySchNameCollect.append(daySchName)
            elif daySch == [] and dCount == 8:
                try:
                    daySchName = daySchNameCollect[1]
                except:
                    daySchName = daySchNameCollect[0]
                daySchNameCollect.append(daySchName)
            elif daySch == []:
                daySchName = daySchNameCollect[0]
                daySchNameCollect.append(daySchName)
            else:
                for count, sch in enumerate(daySchedCollection):
                    if daySch == sch:
                        schNum = count
                daySchName = daySchNameCollect[schNum]
            daySchedNames.append(daySchName)
        
        # Write out text strings for the weekly values.
        schedIDFStrs.append(IFDstrForWeek(daySchedNames, schedName))
        weekSchedName = schedName + ' Week Schedule'
        
        # Write out text for the annual values.
        schedIDFStrs.append(IFDstrForYear(schedName + ' Week Schedule', schedName, schTypeLims))
        yearSchedName = schedName + ' Year Schedule'
        
        # Write all of the schedules to the memory of the GH document.
        for EPObject in schedIDFStrs:
            added, name = hb_EPObjectsAux.addEPObjectToLib(EPObject, overwrite = True)
    
    return yearSchedName, nationalHolidays, scheduleValues, schedIDFStrs, weekSchedName


w = gh.GH_RuntimeMessageLevel.Warning
#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True
#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#Check the data to make sure it is the correct type
if initCheck == True and _generateValues == True:
    result = main(_sun, _mon, _tue, _wed, _thu, _fri, _sat, holiday_, heatDesignDay_, coolDesignDay_, _generateValues, epwFileForHol_, startDayOfWeek_, customHolidays_, _scheduleName_, _schedTypeLimits_)
    if result != -1:
        schedule, holidays, scheduleValues, schedIDFText, weekSchedule = result
        print '\nscheduleValues generated!'
