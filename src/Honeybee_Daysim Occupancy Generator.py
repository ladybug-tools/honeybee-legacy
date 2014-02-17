# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim Occupancy Generator
Daysim calculates the outputs for the hours that the space is occupied. This componet generates a csv file that will be used as the occupancy-file. Read more here: http://daysim.ning.com/page/keyword-occupancy-profile 
-
Provided by Honeybee 0.0.50
    Args:
        _occupancyPeriod_: The period that the building is actively occupid. Use Ladybug Analysis Period component to generate the input. Default is all year between 9 to 5.
        dailyOffHours_: A list of hours that building is unoccupied during the occupancy period everyday (e.g. lunch break). Default is an hour lunch break at 12. 
        weekendDays_: A list of numbers to indicate the weekend days. [0] None, [1-7] SAT to FRI. Default is 1,2 (SAT, SUN)
        _fileName_: Optional fileName for this schedule. Files will be saved to C:\Honeybee\DaysimOcc
        _writeTheOcc: Set to True to write the file
        
    Returns:
        occupancyFile: Path to occupancy file
"""

ghenv.Component.Name = "Honeybee_Daysim Occupancy Generator"
ghenv.Component.NickName = 'occupancyGenerator'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

def main(analysisPeriod, dailyOffHours, weekendDays, fileName):
    msg = None
    
    if len(analysisPeriod)==0:
        analysisPeriod = [(1, 1, 9), (12, 31, 17)]
    
    if len(dailyOffHours)==0:
        dailyOffHours = [12]
    
    if len(weekendDays)==0:
        weekendDays = [1, 2]
    elif weekendDays == 0:
        weekendDays = []
    
    # create the folder if not exist
    folder = "c:/honeybee/DysimOcc/"
    if not os.path.isdir(folder):
        os.mkdir(folder)
        
    # import the classes
    if not sc.sticky.has_key('ladybug_release'):
        msg = " You need to let Ladybug fly first!\nI know this is a Honeybee component but it actually uses Ladybug's functions."
        return msg, None
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
    # selected hourly data includes the last hour that daysim doesnt
    analysisPeriod = [(stMonth, stDay, stHour), (endMonth, endDay, endHour -1)]
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
    
    with open(fullPath, "w") as occFile:
        occFile.write(heading)
        for HOY in range(1,8761):
            d, m, t = lb_preparation.hour2Date(HOY, True)
            m += 1 #month starts from 0 in Ladybug hour2Date. I should fix this at some point
            
            DOY = int(lb_preparation.getJD(m, d))
            HOY -= 1
            
            # time correction for daylight saving
            if stOfDLSHour <= HOY <= endOfDLSHour: HOY += 1
            
            occ = 0
            # if day is not a weekend
            if not int(DOY%7) + 2 in weekendDays:
                # check if the hour is in occupied hours
                if HOY in occHours:
                    # check if the hour is the hour off
                    if not HOY%24 in dailyOffHours:
                        occ = 1
            
            t -= .5 # add half and hour to be similar to daysim
            occLine = str(m) + "," + str(d) + "," + str(t) + "," + str(occ) + "\n"
            occFile.write(occLine)
        
    return msg, fullPath


if _writeTheOcc==True:
    msg, occupancyFile = main(_occupancyPeriod_, dailyOffHours_, weekendDays_, _fileName_)
    
    if msg!=None:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)

