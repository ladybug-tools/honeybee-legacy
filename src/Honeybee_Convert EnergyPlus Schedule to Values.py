# This component creates a 3D chart of hourly or daily data.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com and mostapha@ladybug.tools> 
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
Use this component to make a 3D chart in the Rhino scene of any climate data or hourly simulation data.
-
Provided by Ladybug 0.0.57
    
    Args:
        _schName: Name of the EP schedule
        _weekStartDay_: An integer or text descriptor to set the schedule start day of the week. The default is set to 0 - sun - sunday.
            -
            Choose from one of the following:
            0 - sun - sunday
            1 - mon - monday
            2 - tue - tuesday
            3 - wed - wednesday
            4 - thu - thursday
            5 - fri - friday
            6 - sat - saturday
        epwFileForHol_: The file address of an EPW file on your system.  This component will automatically look up the national holidays of the country listed in the epw file and factor them into the output "values".
        customHol_: Connect a list of DOYs (from 1 to 365) or a list of strings (example: DEC 25).
            -
            These will be added to any holidays in the epwFile holidays (if connected).
    Returns:
        readMe!: ...
        values: Hourly values that define the schedule.
        holidays: Holidays that have been incorporated into the hourly values of the schedule.  Connect these to the 'holidays' output of the "Honeybee_Energy Simulation Par" component to have them factored into the simulation.
"""

ghenv.Component.Name = "Honeybee_Convert EnergyPlus Schedule to Values"
ghenv.Component.NickName = 'convertEPSCHValues'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
from collections import deque
import itertools
from datetime import date

def getNationalHols(country, weekStartWith):
    # Dictionary of national hoildays arranged by country.
    # All countries are accounted for with the exception of:
    # BLZ (CENTRAL AMERICA), BRN (SOUTH PACIFIC), GUM (SOUTH PACIFIC), MHL (SOUTH PACIFIC), PLW (SOUTH PACIFIC), UMI (SOUTH PACIFIC)
    # https://energyplus.net/weather
    ###################################################
    # Source: http://www.officeholidays.com/countries/ ------ http://www.officeholidays.com/countries/
    listOfValues = [0, 1, 2, 3, 4, 5, 6]
    week = deque(listOfValues)
    week.rotate(-weekStartWith)
    dayWeekList = list(itertools.chain.from_iterable(itertools.repeat(week, 53)))[:365]
    countries = {
    'USA':[0,[i for i, x in enumerate(dayWeekList) if x == 2][2],[i for i, x in enumerate(dayWeekList) if x == 2][21],184,[i for i, x in enumerate(dayWeekList) if x == 2][35],314,[i for i, x in enumerate(dayWeekList) if x == 5][46],359],
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
    'UKR': [0,6,66,120,[i for i, x in enumerate(dayWeekList) if x == 2][17],127,128,[i for i, x in enumerate(dayWeekList) if x == 2][24],235,286,324]
    }
    
    return countries[country]

def addHolidays(startVals, holidayValues, weekStartWith, epwFile, customHolidays, lb_preparation):
    holidayDOYs = []
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
        
        try:
            holidayDOYs = getNationalHols(country, weekStartWith)
        except:
            holidayDOYs = [0,120,358,359] # international holidays for countries not found.
        
        # Give a message to show the national holidays.
        print "National holidays(DOYs): "
        for item in holidayDOYs:
            print item+1
        print "_"
    
    # Add customHolidays.
    monthsDict = {'01':'JAN', '02':'FEB', '03':'MAR', '04':'APR', '05':'MAY', '06':'JUN',
    '07':'JUL', '08':'AUG', '09':'SEP', '10':'OCT', '11':'NOV', '12':'DEC'}
    def fromDateToDay(holiday, months):
        startDate = date(2015, 1, 1)
        textMonth = holiday.split(' ')[0].upper()
        dictReverse = {value: key for key, value in months.items()}
        intMonth = int(dictReverse[textMonth])
        endDate = date(2015, intMonth, int(holiday.split(' ')[1]))
        period = endDate - startDate
        day = period.days + 1
        return day
    
    if customHolidays != []:
        try:
            if customHolidays is not type(int):
                customHolidays = map(int, customHolidays)
        except ValueError:
            customHolidaysDOY = []
            for item in customHolidays:
                dayDate = fromDateToDay(item, monthsDict)
                customHolidaysDOY.append(dayDate)
            customHolidays = customHolidaysDOY
        
        # Give a message to show the national holidays.
        print "Custom holidays(DOYs): "
        for item in customHolidays:
            print item
            if item-1 not in holidayDOYs:
                holidayDOYs.append(item-1)
    
    # Edit the list of schedule values.
    for day in holidayDOYs:
        for interval in holidayValues:
            if day >= interval[0]-1 and day <= interval[1]-1:
                startVals[day] = interval[2]
    
    # Build up a list of holidays
    def fromDayToDate(day, months):
        dateDay = date.fromordinal(date(2015, 1, 1).toordinal() + day) # 2015 is not leap year
        month, day = str(dateDay).split('-')[1:]
        monthsDate = months[month]
        dateFromDay = monthsDate + ' ' + day
        return dateFromDay
    holidayDates = []
    for day in holidayDOYs:
        holidayDates.append(fromDayToDate(day, monthsDict))
    
    return startVals, holidayDates



def main(schName, startDayOfTheWeek, epwFile, customHol):
    # Check the start day of the week.
    daysOfWeek = {'sun':0, 'mon':1, 'tue':2, 'wed':3, 'thu':4, 'fri':5, 'sat':6,
    'sunday':0, 'monday':1, 'tuesday':2, 'wednesday':3, 'thursday':4, 'friday':5, 'saturday':6}
    
    if startDayOfTheWeek != None:
        try:
            startDayOfTheWeek = int(startDayOfTheWeek)%7
        except:
            try:
                startDayOfTheWeek = daysOfWeek[startDayOfTheWeek.lower()]
            except:
                warning = 'Input for _weekStartDay_ is not valid.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
    else:
        startDayOfTheWeek = 0
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    readSchedules = sc.sticky["honeybee_ReadSchedules"](schName, startDayOfTheWeek)
    
    values = []
    holidays = []
    dataGotten = False
    if schName.lower().endswith(".csv"):
        # check if csv file exists
        if not os.path.isfile(schName):
            msg = "Cannot find the shchedule file: " + schName
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        else:
            result = open(schName, 'r')
            lineCount = 0
            for lineCount, line in enumerate(result):
                readSchedules.schType = 'schedule:year'
                readSchedules.startHOY = 1
                readSchedules.endHOY = 8760
                if 'Daysim' in line: pass
                else:
                    if lineCount == 0:readSchedules.unit = line.split(',')[-2].split(' ')[-1].upper()
                    elif lineCount == 1: readSchedules.schName = line.split('; ')[-1].split(':')[0]
                    elif lineCount < 4: pass
                    else:
                        columns = line.split(',')
                        try:
                            values.append(float(columns[4]))
                        except:
                            values.append(float(columns[3]))
                    lineCount += 1
            values.insert(0, values.pop(-1))
            dataGotten = True
    else:
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        if schName.upper() not in HBScheduleList:
            msg = "Cannot find " + schName + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        else:
            dataGotten = True
            values = readSchedules.getScheduleValues()
    
    if dataGotten == True:
        # Check for any holidays.
        if epwFile or customHol != []:
            if len(values) == 365 and not schName.lower().endswith(".csv"):
                holidayValues = readSchedules.getHolidaySchedValues(schName)
                values, holidays = addHolidays(values, holidayValues, startDayOfTheWeek, epwFile, customHol, lb_preparation)
        
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
        
        return header + values, holidays
    else:
        return -1



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

if _schName != None:
    result = main(_schName, _weekStartDay_, epwFileForHol_, customHol_)
    if result != -1:
        values, holidays = result
