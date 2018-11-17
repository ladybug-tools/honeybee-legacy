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
Use this component to set HBZone properties

By default these values will be automatically calculated by EnergyPlus.

-
Provided by Honeybee 0.0.64

    Args:
        _HBZones: Input HBZones.
        multiplier_: A list of zone multipliers for each zone.
        ceilingHeight_: A list of ceilings height for each zone.
        volume_: A list of zone volumes for each zone.
        inConvAlg_: A list of Inside Surface Convection Algorithm for each zone.
            Simple, TARP, CeilingDiffuser, AdaptiveConvectionAlgorithm, TrombeWall. 
        outConvAlg_: A list of Outside Surface Convection Algorithm for each zone.
            Simple, TARP, CeilingDiffuser, AdaptiveConvectionAlgorithm, TrombeWall. 
        partOfArea_: A list of Boolean for each zone. By default Zone area will
           be included in total floor area. 
    Returns:
        HBZones: Modified HBZones.
"""

ghenv.Component.Name = "Honeybee_Set Zone Properties"
ghenv.Component.NickName = 'setZoneProp'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.63\nMAR_01_2018
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os

def getValue(values, count):
    try:
        value = values[count]
    except:
        value = values[-1]
    return value


def main(HBZones):
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
    
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        
        # get the values from component inputs
        # follow Grasshopper's data match schema
        if multiplier_:
            HBZone.multiplier = getValue(multiplier_, zoneCount)
        if ceilingHeight_:
            HBZone.ceilingHeight = getValue(ceilingHeight_, zoneCount)
        if volume_:
            HBZone.volume = getValue(volume_, zoneCount)            
        if inConvAlg_:
            HBZone.insideConvectionAlgorithm = getValue(inConvAlg_, zoneCount)        
        if outConvAlg_:
            HBZone.outsideConvectionAlgorithm = getValue(outConvAlg_, zoneCount)
        if partOfArea_:
            HBZone.partOfArea = getValue(partOfArea_, zoneCount)
            
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
    
    return HBZones
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones)
    
    if results != -1:
        HBZones = results