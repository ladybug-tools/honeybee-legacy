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
Look up loads for a Honeybee Zone
-
Provided by Honeybee 0.0.64

    Args:
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        equipmentLoadPerArea: Per m^2
        infiltrationRatePerArea: Per m^2
        lightingDensityPerArea: Per m^2
        numOfPeoplePerArea: Per m^2
        ventilationPerArea: m3/s.m2
        ventilationPerPerson: m3/s.person
"""

ghenv.Component.Name = "Honeybee_Get Zone EnergyPlus Loads"
ghenv.Component.NickName = 'getHBZoneEPLoads'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBZone):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

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
    
    # get Honeybee zone
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObject = hb_hive.visualizeFromHoneybeeHive([HBZone])[0]
    
    try:
        loads = HBZoneObject.getCurrentLoads(True, ghenv.Component)
    except:
        msg = "Failed to load zone loads!"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    equipmentLoadPerArea = loads['EquipmentsLoadPerArea']
    infiltrationRatePerArea = loads['infiltrationRatePerArea']
    lightingDensityPerArea = loads['lightingDensityPerArea']
    numOfPeoplePerArea = loads[ 'numOfPeoplePerArea']
    ventilationPerArea = loads['ventilationPerArea']
    ventilationPerPerson = loads[ 'ventilationPerPerson']
    
    return equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson
    



if _HBZone:
    results = main(_HBZone)
    
    if results != -1:
        equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson = results