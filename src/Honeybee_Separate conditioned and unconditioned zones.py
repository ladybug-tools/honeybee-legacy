#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chien Si Harriman - Modified by Mostapha Sadeghipour Roudsari <Chien.Harriman@gmail.com> 
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
Separate zones into conditioned and unconditioned
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: List of Honeybee zones
    Returns:
        conditionedZones: List of conditioned Honeybee zones
        unconditionedZones: List of unconditioned Honeybee zones
        
"""


ghenv.Component.Name = 'Honeybee_Separate conditioned and unconditioned zones'
ghenv.Component.NickName = 'conditionedUnconditioned'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import uuid

import scriptcontext as sc
import Grasshopper.Kernel as gh


def main(HBZones):
    
    if not sc.sticky.has_key("honeybee_release"):
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
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.visualizeFromHoneybeeHive(HBZones)
    
    conditioned = []
    unconditioned = []
    for zone in HBZonesFromHive:
        if zone.isConditioned:
            conditioned.append(zone)
        else:
            unconditioned.append(zone)
            
    cond  = hb_hive.addToHoneybeeHive(conditioned, ghenv.Component)
    uncond = hb_hive.addToHoneybeeHive(unconditioned, ghenv.Component, False)
    
    return cond, uncond


zones = main(_HBZones)

if zones!=-1:
    conditionedZones, unconditionedZones = zones