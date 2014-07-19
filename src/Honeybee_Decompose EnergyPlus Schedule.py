# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Decompose Schedule

-
Provided by Honeybee 0.0.53
    
    Args:
        schName_: Schedule name
            
    Returns:
        name:
        schedule:
        comments:
"""

ghenv.Component.Name = "Honeybee_Decompose EnergyPlus Schedule"
ghenv.Component.NickName = 'decomposeEPSCH'
ghenv.Component.Message = 'VER 0.0.53\nJUL_19_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(schName):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
        return -1
    
    hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
    hb_EPObjectsAUX = sc.sticky["honeybee_EPObjectsAUX"]()
    
    if hb_EPObjectsAUX.isScheduleTypeLimits(schName):
        schedule, comments = hb_EPScheduleAUX.getScheduleTypeLimitsDataByName(schName.upper(), ghenv.Component)
    
    elif hb_EPObjectsAUX.isSchedule(schName):
        schedule, comments = hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
    
    else:
        return schName, None, None
        
    return schName, schedule, comments

if schName_!= None:
    results = main(schName_)
    
    if results!=-1:
        name, schedule, comments = results