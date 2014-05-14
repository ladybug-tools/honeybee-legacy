# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Call from EP Schedule Library

-
Provided by Honeybee 0.0.53
    
    Args:
        keywords_: List of keywords to filter the list of schedules
            
    Returns:
        scheduleTypeLimits: List of EP schedules in Honeybee library
        scheduleList: List of EP window schedules in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Call from EP Schedule Library"
ghenv.Component.NickName = 'callFromEPSCHLibrary'
ghenv.Component.Message = 'VER 0.0.53\nMAY_13_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

if sc.sticky.has_key("honeybee_release") and sc.sticky.has_key("honeybee_ScheduleLib"):
    
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    scheduleList = sc.sticky["honeybee_ScheduleLib"]["List"]
    scheduleTypeLimits = sc.sticky["honeybee_ScheduleTypeLimitsLib"]["List"]

    scheduleList.sort()
    scheduleTypeLimits.sort()
    
    if len(keywords_)!=0 and keywords_[0]!=None:
        scheduleList = hb_EPMaterialAUX.searchListByKeyword(scheduleList, keywords_)
        scheduleTypeLimits = hb_EPMaterialAUX.searchListByKeyword(scheduleTypeLimits, keywords_)
        
else:
    print "You should first let the Honeybee fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")