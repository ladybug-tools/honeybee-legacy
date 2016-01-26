# Update EP
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
Update EP construction of zone based on type

-
Provided by Honeybee 0.0.59
    
    Args:
        _HBZone: Honeybee zone
        wallEPConstruction_: Optional new construction for walls
        windowEPConstruction_: Optional new construction for windows
        roofEPConstruction_: Optional new construction for roofs
        floorEPConstruction_: Optional new construction for floors
        expFloorEPConstruction_: Optional new construction for exposed floors
        skylightEPConstruction_: Optional new construction for skylights
    Returns:
        modifiedHBZone:  Honeybee zone with updated constructions

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Construction"
ghenv.Component.NickName = 'setEPZoneCnstr'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def main(HBZone, wallEPCnst, windowEPCnst, roofEPCnst, flrEPCnst, expFlrEpCnst, \
        skylightEPCnst):
            
    # Make sure Honeybee is flying
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
    try: HBZoneObject = hb_hive.callFromHoneybeeHive([HBZone])[0]
    except Exception, e: HBZoneObject = None
    
    # here I should check for each construction to be in the library
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    
    if HBZoneObject != None:
        for srf in HBZoneObject.surfaces:
            if srf.BCObject.name == "": # not internal surfaces 
                if windowEPCnst!=None and srf.type != 1 and srf.type != 1.5 and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        hb_EPObjectsAux.assignEPConstruction(childSrf, windowEPCnst, ghenv.Component)
                
                # check for slab on grade and roofs
                if skylightEPCnst!=None and (srf.type == 1 or srf.type == 1.5) and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        hb_EPObjectsAux.assignEPConstruction(childSrf, skylightEPCnst, ghenv.Component)
                
                if srf.type == 0 and wallEPCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, wallEPCnst, ghenv.Component)
                elif srf.type == 1 and roofEPCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, roofEPCnst, ghenv.Component)
                elif srf.type == 2 and flrEPCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, flrEPCnst, ghenv.Component)
                elif srf.type == 2.75 and expFlrEpCnst!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, expFlrEpCnst, ghenv.Component)

        # add zones to dictionary
        HBZones  = hb_hive.addToHoneybeeHive([HBZoneObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBZones
    
    else:
        return -1

if _HBZone:
    result = main(_HBZone, wallEPConstruction_, windowEPConstruction_, \
        roofEPConstruction_, floorEPConstruction_, expFloorEPConstruction_, \
        skylightEPConstruction_)
    
    if result!=-1: modifiedHBZone = result