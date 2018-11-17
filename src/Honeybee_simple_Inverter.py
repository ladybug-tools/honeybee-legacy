#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Anton Szilasi - Icon by Djordje Spasic <ajszilas@gmail.com> 
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
Provided by Honeybee 0.0.64

Use this component to add EnergyPlus simple inverters to a Energy Plus simulation.

Find out more information about Energy Plus simple inverters here:
-
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#electricloadcenterinvertersimple

-
Provided by Honeybee 0.0.64

    Args:
        
        _inverterName: The inverter name - Make it unique from other inverters
        _inverterEfficiency_: The efficiency of the inverter by default this is 90%
        _inverterCost: The cost of the inverter in US dollars (Other currencies will be available in the future)
        _replacementTime_: Specify how often in years the inverter will need to be replaced. The default is 5 years.
        
    Returns:
        HB_inverter: Honeybee inverter- to include this inverter in a generation system connect it to the input HB_generationobjects on the Honeybee_generationsystem component 
        
"""

ghenv.Component.Name = "Honeybee_simple_Inverter"
ghenv.Component.NickName = 'simple_Inverter'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

hb_hivegen = sc.sticky["honeybee_generationHive"]()
PVinverter = sc.sticky["PVinverter"] 
inverter_zone = None
    
def checktheinputs(_inverterName,_inverterEfficiency_,_inverterCost,inverter_zone):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")

        return -1

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
    
    if _inverterCost == None:
        warnMsg= "The cost of the inverter must be specified!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1 
        
    if _inverterName== None:
        print "Please specify a name for the inverter and make sure it is not the same as another inverter!"
        w = gh.GH_RuntimeMessageLevel.Warning ## Need to create a check so that inverters cant have duplicate names!
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for the inverter and make sure it is not the same as another inverter!")
        return -1
    
    if _inverterEfficiency_ == None:
        print "No value given for inverter efficiency 0.9 used"
        
        
        
if checktheinputs(_inverterName,_inverterEfficiency_,_inverterCost,inverter_zone) != -1:
    
    if _replacementTime_ == None:
        
        _replacementTime_ = 5
        print "No value given for replacement time so this inverter will be replaced every 5 years"
    
    HB_inverter = hb_hivegen.addToHoneybeeHive([PVinverter(_inverterName,_inverterCost,inverter_zone,_inverterEfficiency_,_replacementTime_)], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))