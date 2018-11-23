#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Daysim Occupancy Generator
Daysim calculates the outputs for the hours that the space is occupied. This componet generates a csv file that will be used as the occupancy-file. Read more here: http://daysim.ning.com/page/keyword-occupancy-profile 
-
Provided by Honeybee 0.0.64
    Args:
        _occupancyPeriod_: The period that the building is actively occupid. Use Ladybug Analysis Period component to generate the input. Default is all year between 9 to 5.
        dailyOffHours_: A list of hours that building is unoccupied during the occupancy period everyday (e.g. lunch break). Default is an hour lunch break at 12. If you don't want any off hours input -1.
        weekendDays_: A list of numbers to indicate the weekend days. [0] None, [1-7] SAT to FRI. Default is 1,2 (SAT, SUN)
        _fileName_: Optional fileName for this schedule. Files will be saved to C:\Honeybee\DaysimOcc
        _writeTheOcc: Set to True to write the file
        
    Returns:
        occupancyFile: Path to occupancy file
"""

ghenv.Component.Name = "Honeybee_Daysim Occupancy Generator"
ghenv.Component.NickName = 'occupancyGenerator'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

def main(analysisPeriod, dailyOffHours, weekendDays, fileName):
    msg = None
    
    if len(analysisPeriod)==0:
        analysisPeriod = [(1, 1, 9), (12, 31, 17)]
    
    if len(dailyOffHours)==0:
        dailyOffHours = [12]
    elif dailyOffHours== [-1]:
        dailyOffHours = []
    
    
    if len(weekendDays)==0:
        weekendDays = [1, 2]
    elif weekendDays == 0:
        weekendDays = []
    
    # create the folder if not exist
    
    # import the classes
    if not sc.sticky.has_key('ladybug_release') or not sc.sticky.has_key('honeybee_release'):
        msg = " You need to let Ladybug and honeybee to fly first!"
        return msg, None

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
        
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    # create the folder if not exist
    folder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "DaysimCSVOCC\\")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
    # selected hourly data includes the last hour that daysim doesnt
    analysisPeriod = [(stMonth, stDay, stHour+1), (endMonth, endDay, endHour)]
    occHours = lb_preparation.selectHourlyData(range(1,8761), analysisPeriod)
    stOfDLSHour = lb_preparation.date2Hour(3, 12, 1)
    endOfDLSHour = lb_preparation.date2Hour(11, 5, 1)
    
    
    heading = "# Daysim occupancy file,,,\n" + \
          "# time_step 60, commnet: weekdays " + `stHour` + " to " + `endHour` + ", " + `len(dailyOffHours)` + " hour(s) break," + \
          "daylight savings time lasts from 2nd Sunday of March to the first Sunday of November (weather file starts on Monday),,\n" + \
          "# month,day,time,occupancy (1=present/0=absent)\n"
    
    if fileName == None:
        fileName = "userDefinedOcc_" + `stHour` + "to" + `endHour` + ".csv"
    
    fullPath = folder + fileName
    
    if not fullPath.lower().endswith('.csv'):
        fullPath += '.csv'
        
    with open(fullPath, "w") as occFile:
        occFile.write(heading)
        for HOY in range(1,8761):
            
            d, m, t = lb_preparation.hour2Date(HOY, True)
            m += 1 #month starts from 0 in Ladybug hour2Date. I should fix this at some point
            
            DOY = int(lb_preparation.getJD(m, d))
            
            # time correction for daylight saving
            if stOfDLSHour <= HOY <= endOfDLSHour: HOY += 1
            
            occ = 0
            # if day is not a weekend
            if not int(DOY%7) + 1 in weekendDays:
                # check if the hour is in occupied hours
                if HOY in occHours:
                    # check if the hour is the hour off
                    if not HOY%24 in dailyOffHours:
                        occ = 1
            t -= .5 # add half and hour to be similar to daysim
            if t == -.5: t = 23.5
            
            occLine = str(m) + "," + str(d) + "," + str(t) + "," + str(occ) + "\n"
            occFile.write(occLine)
        
    return msg, fullPath


if _writeTheOcc==True:
    results = main(_occupancyPeriod_, dailyOffHours_, weekendDays_, _fileName_)
    
    if results!=-1:
        msg, occupancyFile = results
        
        if msg!=None:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, msg)

