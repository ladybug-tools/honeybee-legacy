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
Look up schedules for an specific bldgProgram and zoneProgram
-
Provided by Honeybee 0.0.59

    Args:
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        occupancySchedule:
        heatingSetPtSchedule:
        coolingSetPtSchedule:
        lightingSchedule:
        equipmentSchedule:
        infiltrationSchedule:
"""

ghenv.Component.Name = "Honeybee_Get EnergyPlus Schedules"
ghenv.Component.NickName = 'getEPSchedules'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass
import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBZoneProgram):
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
    
    bldgProgram, zoneProgram = HBZoneProgram.split("::")
    
    openStudioStandardLib = sc.sticky ["honeybee_OpenStudioStandardsFile"]
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    try:
        schedulesAndLoads = openStudioStandardLib['space_types']['90.1-2007']['ClimateZone 1-8'][bldgProgram][zoneProgram]
    except:
        msg = "Either your input for bldgProgram > [" + str(bldgProgram) + "] or " + \
              "the input for zoneProgram > [" + str(zoneProgram) + "] is not valid; " + \
              "or [" + str(bldgProgram) + "] and [" + str(zoneProgram) + "] is not a valid combination.\n" + \
              "Use ListSpacePrograms component to find the available programs."
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
        
    occupancySchedule = schedulesAndLoads['occupancy_sch']
    occupancyActivitySch = schedulesAndLoads['occupancy_activity_sch'] 
    heatingSetPtSchedule = schedulesAndLoads['heating_setpoint_sch']
    coolingSetPtSchedule = schedulesAndLoads['cooling_setpoint_sch']
    lightingSchedule = schedulesAndLoads['lighting_sch']
    equipmentSchedule = schedulesAndLoads['elec_equip_sch']
    infiltrationSchedule = schedulesAndLoads['infiltration_sch']
    
    return occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule
    
    
if _zoneProgram:
    results = main(_zoneProgram)
    
    if results != -1:
        occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule = results