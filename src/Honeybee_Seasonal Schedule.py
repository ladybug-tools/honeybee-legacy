#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, 
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
Use this component to generate a seasonal schedule (aka. a schedule composed of different weekly schedules).  Using the weekSched outputs of the other schedule generating components, you can combine these to create a yearly schedule that has different week schedules for different times of the year.
-
Provided by Ladybug 0.0.62
    
    Args:
        _scheduleName: A name for the schedule that this component will create.  This name should be unique among the schedules in your Grasshopper document to ensure that you do not overwrite other schedules.
        _schedTypeLimits_: A text string from the scheduleTypeLimits output of the "Honeybee_Call From EP Schedule Library" component.  This value represents the units of the schedule input values.  The default is "Fractional" for a schedule with values that range between 0 and 1.  Other common inputs include "Temperature", "On/Off", and "ActivityLevel".
        _baseWeekSched: A text string represeting the name of a weekly schedule to use for any parts of the year not specified in the analysisPeriods below.  Such weekly schedules are output from either the "Honeybee_Constant Schedule" or the "Honeybee_Annual Schedule" components.
        _seasonWeekSched1: A text string represeting the name of a weekly schedule to use for analysisPeriod1 below.  Such weekly schedules are output from either the "Honeybee_Constant Schedule" or the "Honeybee_Annual Schedule" components.
        _analysisPeriod1: An analysis period from the Ladybug_Analysis Period that specifies when the seasonWeekSched1_ above is active.
    Returns:
        readMe!: ...
        schedule: The name of the schedule that has been written to the memory of the GH document.  Connect this to any shcedule input of a Honeybee component to assign the schedule.
        schedIDFText: The text needed to tell EnergyPlus how to run the schedule.  If you are done creating/editing a shcedule with this component, you may want to make your GH document smaller by internalizing this IDF text and using the "Honeybee_Add To EnergyPlus Library" component to add the schedule to the memory the next time you open the GH file.  Then you can delete this component.
"""

ghenv.Component.Name = "Honeybee_Seasonal Schedule"
ghenv.Component.NickName = 'Honeybee_SeasonalSchedule'
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


def IFDstrForWeek(weekSchedName, analysisPd, lastInList=False):
    idfStr = '\t' + weekSchedName + ',  !- Schedule:Week Name\n' + \
        '\t' + str(analysisPd[0][0]) + ',  !- Start Month 1\n' + \
        '\t' + str(analysisPd[0][1]) + ',  !- Start Day 1\n' + \
        '\t' + str(analysisPd[1][0]) + ',  !- End Month\n'
    if lastInList:
        idfStr = idfStr + '\t' + str(analysisPd[1][1]) + ';  !- End Day\n'
    else:
        idfStr = idfStr + '\t' + str(analysisPd[1][1]) + ',  !- End Day\n'
    
    return idfStr


def main(scheduleName, schedTypeLimits, baseWeekSched, numInputs):
    # Grab the dependencies.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    scheduleTypeLimitsLib = sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    
    # Gather all the analysis periods and schedules.
    allAnalysisPeriods = []
    allSchedules = []
    for input in range(numInputs):
        if input <= 2:
            pass
        else:
            seasonNum = int((input-1)/2)
            if input % 2 != 0:
                ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.item
                inputName = '_' + 'seasonWeekSched' + str(seasonNum)
                allSchedules.append(eval(inputName))
            else:
                ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.list
                inputName = '_' + 'analysisPeriod' + str(seasonNum)
                allAnalysisPeriods.append(eval(inputName))
    
    # Check if there are any overlaps in analysis periods.
    allDOYs = []
    startDOYs = []
    endDOYs = []
    for period in allAnalysisPeriods:
        doyStart = int(lb_preparation.getJD(period[0][0], period[0][1]))
        doyEnd = int(lb_preparation.getJD(period[1][0], period[1][1]))
        allDOYs.extend(range(doyStart, doyEnd+1))
        startDOYs.append(doyStart)
        endDOYs.append(doyEnd)
    if len(allDOYs) != len(set(allDOYs)):
        warning = 'Overlapping analysisPeriods found!\nMake sure that one analysis period does not include the other.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    # Make a list corresponding to the final schedule.
    finalWeekScheds = []
    finalAnalysisPds = []
    startDOYs, endDOYs, allAnalysisPeriods, allSchedules = zip(*sorted(zip(startDOYs, endDOYs, allAnalysisPeriods, allSchedules)))
    
    lastDOY = 1
    for count, period in enumerate(allAnalysisPeriods):
        if count == 0 and period[0] != (1,1,1):
            finalWeekScheds.append(baseWeekSched)
            d, m, t = lb_preparation.hour2Date((startDOYs[count]-1)*24, True)
            finalAnalysisPds.append([(1,1,1),(m+1,d,t)])
            finalWeekScheds.append(allSchedules[count])
            finalAnalysisPds.append(period)
            lastDOY = endDOYs[count]
        elif count == 0:
            finalWeekScheds.append(allSchedules[count])
            finalAnalysisPds.append(period)
            lastDOY = endDOYs[count]
        elif startDOYs[count] == lastDOY+1:
            finalWeekScheds.append(allSchedules[count])
            finalAnalysisPds.append(period)
            lastDOY = endDOYs[count]
        else:
            finalWeekScheds.append(baseWeekSched)
            d1, m1, t1 = lb_preparation.hour2Date((lastDOY+1)*24, True)
            d2, m2, t2 = lb_preparation.hour2Date((startDOYs[count]-1)*24, True)
            finalAnalysisPds.append([(m1+1,d1,t1),(m2+1,d2,t2)])
            finalWeekScheds.append(allSchedules[count])
            finalAnalysisPds.append(period)
            lastDOY = endDOYs[count]
    if finalAnalysisPds[-1][1] != (12,31,24):
        finalWeekScheds.append(baseWeekSched)
        d, m, t = lb_preparation.hour2Date((endDOYs[-1]+1)*24, True)
        finalAnalysisPds.append([(m+1,d,t),(12,31,24)])
    
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
    
    # Make the IDF string for the schedule.
    idfStr = 'Schedule:Year,\n' + \
        '\t' + scheduleName + ', !- Name\n' + \
        '\t' + schTypeLims + ', !- Schedule Type Limits Name\n'
    for count, weekSched in enumerate(finalWeekScheds):
        if count+1 == len(finalWeekScheds):
            idfStr = idfStr + IFDstrForWeek(weekSched, finalAnalysisPds[count], True)
        else:
            idfStr = idfStr + IFDstrForWeek(weekSched, finalAnalysisPds[count])
    
    # Add the schedule to the library.
    added, name = hb_EPObjectsAux.addEPObjectToLib(idfStr, overwrite = True)
    
    return name, idfStr





w = gh.GH_RuntimeMessageLevel.Warning
initCheck = True

# set the right names of inputs.
inputsDict = {
0: ["_scheduleName", "A name for the schedule that this component will create.  This name should be unique among the schedules in your Grasshopper document to ensure that you do not overwrite other schedules."],
1: ["_schedTypeLimits_", "A text string from the scheduleTypeLimits output of the 'Honeybee_Call From EP Schedule Library' component.  This value represents the units of the schedule input values.  The default is 'Fractional' for a schedule with values that range between 0 and 1.  Other common inputs include 'Temperature', 'On/Off', and 'ActivityLevel'."],
2: ["_baseWeekSched", "A text string represeting the name of a weekly schedule to use for any parts of the year not specified in the analysisPeriods below.  Such weekly schedules are output from either the 'Honeybee_Constant Schedule' or the 'Honeybee_Annual Schedule' components."]
}

numInputs = ghenv.Component.Params.Input.Count
if numInputs % 2 == 0:
    initCheck = False
    err = "More component inputs are needed.  Zoom in and expand the number of inputs."
    print err
    ghenv.Component.AddRuntimeMessage(w, err)

for input in range(numInputs):
    if input <= 2:
        inputName = inputsDict[input][0]
        inputDesc = inputsDict[input][1]
    else:
        seasonNum = int((input-1)/2)
        if input % 2 != 0:
            ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.item
            inputName = '_' + 'seasonWeekSched' + str(seasonNum)
            inputDesc = 'A text string represeting the name of a weekly schedule to use for analysisPeriod' + str(seasonNum) + ' below.  Such weekly schedules are output from either the "Honeybee_Constant Schedule" or the "Honeybee_Annual Schedule" components.'
        else:
            ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.list
            inputName = '_' + 'analysisPeriod' + str(seasonNum)
            inputDesc = 'An analysis period from the Ladybug_Analysis Period that specifies when the seasonWeekSched' + str(seasonNum) + '_ above is active.'
    
    ghenv.Component.Params.Input[input].NickName = inputName
    ghenv.Component.Params.Input[input].Name = inputName
    ghenv.Component.Params.Input[input].Description = inputDesc



#If Honeybee or Ladybug is not flying or is an older version, give a warning.
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


if initCheck == True:
    result = main(_scheduleName, _schedTypeLimits_, _baseWeekSched, numInputs)
    if result != -1:
        schedule, schedIDFText = result
