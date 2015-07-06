#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Remove Glazing

-
Provided by Honeybee 0.0.57

    Args:
        _HBZones: List of Honeybee Zones
        srfIndex_: Index of the surface to removeglazing
        pattern_: Pattern to remove glazings
    Returns:
        readMe!: Information about the Honeybee object
"""
ghenv.Component.Name = "Honeybee_Remove Glazing"
ghenv.Component.NickName = 'remGlz'
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

def main(HBObjects, srfIndex, pattern):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBObjects)
    
    HBObjs = range(len(HBObjectsFromHive))
    
    for count, HBO in enumerate(HBObjectsFromHive):
        if HBO.objectType == "HBZone":
            for srfCount, surface in enumerate(HBO.surfaces):
                if srfCount in srfIndex and surface.hasChild:
                    #remove the glzing
                    surface.removeAllChildSrfs()
                elif pattern[srfCount] == True and surface.hasChild:
                    print srfCount
                    #remove the glzing
                    surface.removeAllChildSrfs()
                    
        HBObjs[count] = HBO
    
    return hb_hive.addToHoneybeeHive(HBObjs, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if (_HBZones and srfIndex_!=[]) or (_HBZones and pattern_!=[]):
    HBZones = main(_HBZones, srfIndex_, pattern_)
