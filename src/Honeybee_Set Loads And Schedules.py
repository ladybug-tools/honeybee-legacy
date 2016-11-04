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
Set schedules and loads for zones based on program 
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: A HBZone or list of HBZones for which you want to change the program (including schedules and loads).
        zonePrograms_: The zone program that you want to assign to the HBZones.  This should be a value from the "Honeybee_ListZonePrograms" component.  This input can also be a list of programs tha aligns with the input HBZones.
    Returns:
        currentSchedules: The schedules that have been assigned to the zones.
        currentLoads: The loads that have been assigned to the zones
        HBZones: HBZones that have had their program set to the input zonePrograms_.
"""

ghenv.Component.Name = "Honeybee_Set Loads And Schedules"
ghenv.Component.NickName = 'SetLoadsAndSchedules'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

def main(HBZones, zonePrograms):
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
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    currentSchedules = []
    currentLoads = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        # zone programs
        try: bldgProgram, zoneProgram = zonePrograms[zoneCount].split("::")
        except: pass
        
        # make sure the combination is valid before changing it for the zone
        if bldgProgram!=None and bldgProgram not in bldgProgramDict.values():
            msg = "bldgProgram > [" + bldgProgram + "] is not a valid input.\n" + \
                  "Use ListSpacePrograms component to find the available programs."
            print msg
            if component != None:
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        if zoneProgram!=None:
            try:
                if zoneProgram not in zonesProgramDict[bldgProgram].values():
                    msg = "zoneProgram > [" + zoneProgram + "] is not a valid zone program for " + bldgProgram + ".\n" + \
                      "Use ListSpacePrograms component to find the available programs."
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
            except:
                msg = "Either your input for bldgProgram > [" + str(bldgProgram) + "] or " + \
                      "the input for zoneProgram > [" + str(zoneProgram) + "] is not valid.\n" + \
                      "Use ListSpacePrograms component to find the available programs."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
                
        HBZone.bldgProgram = bldgProgram
        HBZone.zoneProgram = zoneProgram
        HBZone.assignScheduleBasedOnProgram(ghenv.Component)
        HBZone.assignLoadsBasedOnProgram(ghenv.Component)
        if HBZone.isSchedulesAssigned:
            currentSchedules.append(HBZone.getCurrentSchedules())
        if HBZone.isLoadsAssigned:
            currentLoads.append(HBZone.getCurrentLoads())
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
    
    return currentSchedules, currentLoads, HBZones


if _HBZones:
    results = main(_HBZones, zonePrograms_)
    
    if results != -1:
        currentSchedules, currentLoads, HBZones = results