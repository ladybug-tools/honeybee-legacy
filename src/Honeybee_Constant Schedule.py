#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Antonello Di Nunzio <antonellodinunzio@gmail.com> and Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generate a schedule with a constant value or a schedule with 24 values that repeat in the same 24-hour pattern every day.
-
Provided by Ladybug 0.0.62
    
    Args:
        _value: A value or list of 24 values that will be repeated for every day of the year.
        _scheduleName: A text string representing a name for the schedule that this component will create.  This name should be unique among the schedules in your Grasshopper document to ensure that you do not overwrite other schedules.
        _schedTypeLimits_: A text string from the scheduleTypeLimits output of the "Honeybee_Call From EP Schedule Library" component.  This value represents the units of the schedule input values.  The default is "Fractional" for a schedule with values that range between 0 and 1.  Other common inputs include "Temperature", "On/Off", and "ActivityLevel".
    Returns:
        readMe!: ...
        schedule: The name of the schedule that has been written to the memory of the GH document.  Connect this to any shcedule input of a Honeybee component to assign the schedule.
        weekSched: The name of the weekly schedule that has been written to the memory of the GH document.  If your final intended annual schedule is seasonal (composed of different weekly schedules), you can use this output with the "Honeybee_Seasonal Schedule" to create such schedules.
        schedIDFText: The text needed to tell EnergyPlus how to run the schedule.  If you are done creating/editing a shcedule with this component, you may want to make your GH document smaller by internalizing this IDF text and using the "Honeybee_Add To EnergyPlus Library" component to add the schedule to the memory the next time you open the GH file.  Then you can delete this component.
"""

ghenv.Component.Name = "Honeybee_Constant Schedule"
ghenv.Component.NickName = 'ConstantSchedule'
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

def IFDstrForWeek(daySchedName, schName):
    idfStr = 'Schedule:Week:Daily,\n' + \
        '\t' + schName + ' Week Schedule' + ', !- Name\n' + \
        '\t' + daySchedName + ',  !- Sunday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Monday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Tuesday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Wednesday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Thursday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Friday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Saturday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- Holiday Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- SummerDesignDay Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- WinterDesignDay Schedule:Day Name\n' + \
        '\t' + daySchedName + ',  !- CustomDay1 Schedule:Day Name\n' + \
        '\t' + daySchedName + ';  !- CustomDay2 Schedule:Day Name\n'
    
    return idfStr

def IFDstrForYear(weekSchedName, schName, schTypeLims):
    idfStr = 'Schedule:Year,\n' + \
        '\t' + schName + ', !- Name\n' + \
        '\t' + schTypeLims + ', !- Schedule Type Limits Name\n' + \
        '\t' + weekSchedName + ',  !- Schedule:Week Name\n' + \
        '\t' + '1' + ',  !- Start Month 1\n' + \
        '\t' + '1' + ',  !- Start Day 1\n' + \
        '\t' + '12' + ',  !- End Month\n' + \
        '\t' + '31' + ';  !- End Day\n'
    
    return idfStr

def main(values, schedName, schedTypeLimits):
    # Import the classes.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    scheduleTypeLimitsLib = sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    
    # Generate a schedule IDF string if writeSchedule_ is set to True.
    daySchedCollection = []
    daySchNameCollect = []
    schedIDFStrs = []
    daySchedNames = []
    
    # Get the type limits for the schedule.
    if schedTypeLimits == None:
        schTypeLims = 'Fractional'
    else:
        schTypeLims = schedTypeLimits
        if schTypeLims.upper() == 'TEMPERATURE':
            schTypeLims = 'TEMPERATURE 1'
        if schTypeLims.upper() not in scheduleTypeLimitsLib:
            warning = "Can't find the connected _schedTypeLimits_ '" + schTypeLims + "' in the Honeybee EP Schedule Library."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    # Write out text strings for the daily schedules
    if len(values) == 1:
        values = [values[0] for x in range(24)]
    elif len(values) == 24:
        pass
    else:
        warning = "_value must be either a single value or a list of 24 values for each hour of the day."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    schedIDFStrs.append(IFDstrFromDayVals(values, schedName, 'Constant', schTypeLims))
    daySchName = schedName + ' Day Schedule - ' + 'Constant'
    
    # Write out text strings for the weekly values.
    schedIDFStrs.append(IFDstrForWeek(daySchName, schedName))
    weekSchedName = schedName + ' Week Schedule'
    
    # Write out text for the annual values.
    schedIDFStrs.append(IFDstrForYear(schedName + ' Week Schedule', schedName, schTypeLims))
    yearSchedName = schedName
    
    # Write all of the schedules to the memory of the GH document.
    for EPObject in schedIDFStrs:
        added, name = hb_EPObjectsAux.addEPObjectToLib(EPObject, overwrite = True)
    
    return yearSchedName, weekSchedName, schedIDFStrs


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
if initCheck == True:
    result = main(_value, _scheduleName, _schedTypeLimits_)
    if result != -1:
        schedule, weekSched, schedIDFText = result
        print '\nscheduleValues generated!'
