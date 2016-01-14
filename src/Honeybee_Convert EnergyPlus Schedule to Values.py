# This component creates a 3D chart of hourly or daily data.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com and Sadeghipour@gmail.com> 
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
        _weekStDay_: Day to be considered as the start of the week. Default is Sunday.[0]: Sunday, [1]: Monday, [2]: Tuesday, [3]: Wednesday, [4]: Thursday, [5]: Friday, [6]: Saturday
    Returns:
        values: Hourly values
"""

ghenv.Component.Name = "Honeybee_Convert EnergyPlus Schedule to Values"
ghenv.Component.NickName = 'convertEPSCHValues'
ghenv.Component.Message = 'VER 0.0.58\nJAN_13_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os


def main(schName, startDayOfTheWeek):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("ladybug_release"):
        print "You should first let Ladybug and Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug and Honeybee fly...")
        return -1
    
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
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    readSchedules = sc.sticky["honeybee_ReadSchedules"](schName, startDayOfTheWeek)
    values = []
    dataGotten = False
    if schName.lower().endswith(".csv"):
        # check if csv file exists
        if not os.path.isfile(schName):
            msg = "Cannot find the shchedule file: " + schName
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
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
                        for columnCount, column in enumerate(line.split(',')):
                            if columnCount == 4:
                                values.append(float(column))
                    lineCount += 1
            dataGotten = True
    else:
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        if schName.upper() not in HBScheduleList:
            msg = "Cannot find " + schName + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            dataGotten = True
            values  = readSchedules.getScheduleValues()
    
    if dataGotten == True:
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
    else:
        return []

if _schName != None:
    try: _weekStDay_ = _weekStDay_%7
    except: _weekStDay_ = 0
    
    values = main(_schName, _weekStDay_)
