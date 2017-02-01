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
Use this component to turn a HBZone into a 'Plenum Zone' with no internal loads.  This is useful to appropriately assign conditions for closets, underfloor spaces, and drop ceilings.
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: HBZones that you want to turn into plenum zones.
        conditioned_: Set to 'True' if the plenum is active or is conditioned and set to 'False' to have the plenum be unconditioned.  The default is set to 'False' to have the zones unconditioned.
    Returns:
        HBZPlenumZones: HBZones that have had their loads dropped to 0 to be reflective of plenum zones.
"""

ghenv.Component.Name = "Honeybee_Create EP Plenum"
ghenv.Component.NickName = 'createEPPlenum'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os


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
    
    schedules = []
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        
        # add Plenum to name (maily for OpenStudio)
        # https://github.com/mostaphaRoudsari/Honeybee/issues/140#issuecomment-51018021
        
        if "plenum" not in HBZone.name.lower():
            HBZone.name = "Plenum " + HBZone.name 
        
        # change loads to 0
        if not HBZone.isLoadsAssigned:
            HBZone.assignLoadsBasedOnProgram(ghenv.Component)
        
        HBZone.equipmentLoadPerArea = 0
        HBZone.infiltrationRatePerArea = 0
        HBZone.lightingDensityPerArea = 0
        HBZone.numOfPeoplePerArea = 0
        HBZone.ventilationPerArea = 0
        HBZone.ventilationPerPerson = 0
        
        if conditioned_ == True:
            HBZone.isConditioned = True
        else:
            HBZone.isConditioned = False
        
        # This is for EP component so that the area won't be included in the total area
        HBZone.isPlenum = True
        
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
    
    return HBZones
    

if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones)
    
    if results != -1: HBPlenumZones = results