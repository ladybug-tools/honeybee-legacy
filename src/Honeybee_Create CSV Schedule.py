#This is a component for writing out .csv sechedules for EnergyPlus.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to write custom .csv schedules for EnergyPlus using a list of numbers that you have in grasshopper.  This can be used to make custom infiltration shcedules based on indoor thermal comdort (to mimic opening of windows), shading transparency shedules based on glare or thermal comfort, etc.

-
Provided by Honeybee 0.0.64
    
    Args:
        _values: The values to be written into the .csv schedule.
        units_: Text for the units of the input values above.  The default is "Dimensionless" for a fractional schedule.  Possible inputs include "Dimensionless", "Temperature", "DeltaTemperature", "PrecipitationRate", "Angle", "ConvectionCoefficient", "ActivityLevel", "Velocity", "Capacity", "Power", "Availability", "Percent", "Control", and "Mode".
        analysisPeriod_: If your input units do not represent a full year, use this input to specify the period of the year that the schedule applies to.
        _scheduleName: Input a name for your schedule here.  The default is "unnamedSchedule".
        _writeFile: Set to "True" to generate the .csv schedule.
    Returns:
        readMe!: ...
        csvSchedule: The file path of the created .csv schedule.  Plug this into the "Honeybee_Set EnergyPlus Zone Schedules" to apply the schedule to a zone.
"""

ghenv.Component.Name = "Honeybee_Create CSV Schedule"
ghenv.Component.NickName = 'csvSchedule'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os


def checkTheInputs():
    #Import the LB Class.
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        #Check the units and set default units to fractional.
        checkData1 = True
        if units_ == None:
            units = "Dimensionless"
        else:
            if units_ == "Dimensionless": units = units_
            elif units_ == "Temperature": units = units_
            elif units_ == "DeltaTemperature": units = units_
            elif units_ == "PrecipitationRate": units = units_
            elif units_ == "Angle": units = units_
            elif units_ == "ConvectionCoefficient": units = units_
            elif units_ == "ActivityLevel": units = units_
            elif units_ == "Velocity": units = units_
            elif units_ == "Capacity": units = units_
            elif units_ == "Power": units = units_
            elif units_ == "Availability": units = units_
            elif units_ == "Percent": units = units_
            elif units_ == "Control": units = units_
            elif units_ == "Mode": units = units_
            else:
                checkData1 = False
                warning = "The input units_ are not valid units for input into EnergyPlus."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        #Set the numeric type to continuous.
        numericType = "Continuous"
        
        #Get a list of all HOYs, months, and days of the year based on the input timestep.
        def drange(start, stop, step):
            r = start
            while r < stop:
                yield r
                r += step
        
        totalHOYS = []
        i = drange(0, 8760, 1)
        HOYSinit = ["%g" % x for x in i]
        for item in HOYSinit: totalHOYS.append(float(item)+1)
        
        totalMonths = []
        totalDays = []
        for hour in totalHOYS:
            date = lb_preparation.hour2Date(hour, True)
            totalDays.append(date[0])
            totalMonths.append(date[1])
        
        #If there is an analysis period, check the HOYs of it.
        if analysisPeriod_ != []:
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
        else:
            HOYS = totalHOYS
        
        #Check if the length of the values aligns with the analysis period and time step.
        checkData2 = True
        if len(_values) != len(HOYS):
            checkData2 = False
            warning = "The length of the list of connected values does not align with the analysisPeriod_.  Note that the default list length for connected values is 8760 (one for each hour of the year)."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        #If the values list is not for the whole year, insert 0 values for the time period that it is missing.
        csvValues = []
        counter = 0
        sHour = set(HOYS)
        if checkData2 == True:
            for count, hour in enumerate(totalHOYS):
                if hour in sHour:
                    csvValues.append(_values[counter])
                    counter += 1
                else:
                    csvValues.append(0.0)
        
        #Set a default schedule name.
        if _scheduleName == None: scheduleName = "SCHunnamedSchedule.csv"
        else: scheduleName = "SCH" + _scheduleName.strip()
        
        #If everything is good, return one value to represent this.
        if checkData1 == True and checkData2 == True: checkData = True
        else: checkData = False
        
        return checkData, units, numericType, totalHOYS, totalDays, totalMonths, csvValues, scheduleName
    else:
        print "You should first let the Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let the Ladybug fly...")
        return False, None, None, [], [], [], [], None, 1


def main(units, numericType, totalHOYS, totalDays, totalMonths, csvValues, scheduleName):
    #Find the Ladybug default folder.
    lb_defaultFolder = sc.sticky["Ladybug_DefaultFolder"]
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    workingDir = lb_preparation.makeWorkingDir(os.path.join(lb_defaultFolder, "EPCSVSchedules")) 
    
    
    #Create a csvFile.
    if not scheduleName.strip().lower().endswith(".csv"): scheduleName += ".csv"
    
    filePath = os.path.join(workingDir, scheduleName)
    
    csvfile = open(filePath, 'wb')
    
    #Create a file header.
    header = "Honeybee Schedule file (to be used in combination with a thermal simulation program)," + " , , " + numericType + ", " + units + "\n" +\
    "Schedule file address:" + filePath + "; " + scheduleName + ": This is a custom schedule created by the user.,,,Occupied Hours: N/A" + "\n" + \
    "1" + ",,,,Values [" + "units" + "],N/A" + "\n" + \
    "month, day, hour, values" + "\n"
    
    csvfile.write(header)
    
    for count, item in enumerate(csvValues):
        time = ((totalHOYS[count] -1 )%24) + .5
        line = str(totalMonths[count]) + ", " + str(totalDays[count]) + ", " + str(time) + ", ," + str(item) + "\n"
        csvfile.write(line)
    
    csvfile.close()
    
    return filePath


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


checkData = False
if initCheck == True:
    checkData, units, numericType, totalHOYS, totalDays, totalMonths, csvValues, scheduleName = checkTheInputs()

if checkData == True and _writeFile == True:
    csvSchedule = main(units, numericType, totalHOYS, totalDays, totalMonths, csvValues, scheduleName)