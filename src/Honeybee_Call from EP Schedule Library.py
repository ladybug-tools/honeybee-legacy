#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Call from EP Schedule Library

-
Provided by Honeybee 0.0.59
    
    Args:
        keywords_: List of keywords to filter the list of schedules
            
    Returns:
        scheduleTypeLimits: List of EP schedules in Honeybee library
        scheduleList: List of EP window schedules in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Call from EP Schedule Library"
ghenv.Component.NickName = 'callFromEPSCHLibrary'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(keywords_):
    if sc.sticky.has_key("honeybee_release") and sc.sticky.has_key("honeybee_ScheduleLib"):
        
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        scheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        scheduleTypeLimits = sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    
        scheduleList.sort()
        scheduleTypeLimits.sort()
        
        if len(keywords_)!=0 and keywords_[0]!=None:
            scheduleList = hb_EPMaterialAUX.searchListByKeyword(scheduleList, keywords_)
            scheduleTypeLimits = hb_EPMaterialAUX.searchListByKeyword(scheduleTypeLimits, keywords_)
        
        return scheduleTypeLimits, scheduleList
    else:
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
        return -1

results = main(keywords_)

if results!=-1:
    scheduleTypeLimits, scheduleList = results