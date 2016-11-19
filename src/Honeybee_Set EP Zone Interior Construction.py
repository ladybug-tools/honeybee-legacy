# Set EP Zones Interior Construction
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
Set EP Zones Interior Construction

-
Provided by Honeybee 0.0.60
    
    Args:
        _HBZones: Honeybee zones
        intWallEPConstruction_: Optional new construction for interior walls
        intWindowEPConstruction_: Optional new construction for interior windows 
        intFloorEPConstruction_: Optional new construction for interior floors
        intCeilingEPConstruction_: Optional new construction for interior ceilings.  If no value is connected here but a value is connected for interior floors, the intCeiling construction will be assumed to be the same as the intFloor construction above.
    Returns:
        modifiedHBZones:  Honeybee zone with updated constructions

"""

ghenv.Component.Name = "Honeybee_Set EP Zone Interior Construction"
ghenv.Component.NickName = 'setEPZoneIntCnstr'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh


def updateZoneMixing(surface1, zone1, zone2):
    #Change the air mixing between the zone and other zones to "True"
    zone1.mixAir = True
    zone2.mixAir = True
    
    #Append the zone to be mixed with to the mixAirZoneList.
    zone1.mixAirZoneList.append(zone2.name)
    zone2.mixAirZoneList.append(zone1.name)
    
    #Calculate a rough flow rate of air based on the cross-sectional area of the surface between them.
    flowFactor = zone1.mixAirFlowRate
    flowRate = (rc.Geometry.AreaMassProperties.Compute(surface1.geometry).Area)*flowFactor
    
    #Append the flow rate of mixing to the mixAirFlowList
    zone1.mixAirFlowList.append(flowRate)
    zone2.mixAirFlowList.append(flowRate)
    
    #Append the flow shcedule to the mixing list.
    zone1.mixAirFlowSched.append('ALWAYS ON')
    zone2.mixAirFlowSched.append('ALWAYS ON')
    
    return flowRate

def checkAirWalls(construction, srf):
    if construction.ToUpper() == "AIR WALL":
        srf.setType(4, isUserInput= True)
        updateZoneMixing(srf, srf.parent, srf.BCObject.parent)

def matchLists(input, length):
    il = len(input)
    if il == 0:
        return tuple(None for i in range(length))
    else:
        return tuple(input[i] if i < il else input[-1] for i in range(length))
        
def main(HBZones, wallEPCnst, windowEPCnst, flrEPCnst, cielConstr):
    
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
    HBZoneObjects = hb_hive.callFromHoneybeeHive(HBZones)
    
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    modifiedObjects = []
    l = len(HBZoneObjects)
    wallEPCnst = matchLists(wallEPCnst, l)
    windowEPCnst = matchLists(windowEPCnst, l)
    flrEPCnst = matchLists(flrEPCnst, l)
    cielConstr = matchLists(cielConstr, l)
    
    for count, HBZoneObject in enumerate(HBZoneObjects):
        for srf in HBZoneObject.surfaces:
            if srf.BC.lower() == "surface" or srf.BC.lower() == "adiabatic": # only internal surfaces
                if windowEPCnst[count]!=None and srf.hasChild:
                    for childSrf in srf.childSrfs:
                        hb_EPObjectsAux.assignEPConstruction(childSrf, windowEPCnst[count], ghenv.Component)
                        if srf.BC.lower() == "surface":
                            hb_EPObjectsAux.assignEPConstruction(childSrf.BCObject, windowEPCnst[count], ghenv.Component)
                            if windowEPCnst[count].ToUpper() == "AIR WALL":
                                updateZoneMixing(childSrf, srf.parent, srf.BCObject.parent)
                if srf.type == 0 and wallEPCnst[count]!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, wallEPCnst[count], ghenv.Component)
                    if srf.BC.lower() == "surface" or srf.BC.lower() == "adiabatic":
                        if srf.BC.lower() == "surface":
                            hb_EPObjectsAux.assignEPConstruction(srf.BCObject, wallEPCnst[count], ghenv.Component)
                        else:
                            hb_EPObjectsAux.assignEPConstruction(srf, wallEPCnst[count], ghenv.Component)
                        checkAirWalls(wallEPCnst[count], srf)
                elif (srf.type == 3 and cielConstr[count]!=None) or (srf.type == 1 and srf.BC.lower() == "adiabatic" and cielConstr[count]!=None):
                    hb_EPObjectsAux.assignEPConstruction(srf, cielConstr[count], ghenv.Component)
                    if srf.BC.lower() == "surface" or srf.BC.lower() == "adiabatic":
                        if srf.BC.lower() == "surface":
                            hb_EPObjectsAux.assignEPConstruction(srf.BCObject, cielConstr[count], ghenv.Component)
                        else:
                            hb_EPObjectsAux.assignEPConstruction(srf, cielConstr[count], ghenv.Component)
                        checkAirWalls(cielConstr[count], srf)
                elif (srf.type == 2 or srf.type == 3) and flrEPCnst[count]!=None:
                    hb_EPObjectsAux.assignEPConstruction(srf, flrEPCnst[count], ghenv.Component)
                    if srf.BC.lower() == "surface" or srf.BC.lower() == "adiabatic":
                        if srf.BC.lower() == "surface":
                            hb_EPObjectsAux.assignEPConstruction(srf.BCObject, flrEPCnst[count], ghenv.Component)
                        else:
                            hb_EPObjectsAux.assignEPConstruction(srf, flrEPCnst[count], ghenv.Component)
                        checkAirWalls(flrEPCnst[count], srf)
            
        modifiedObjects.append(HBZoneObject)
    # add zones to dictionary
    HBZones  = hb_hive.addToHoneybeeHive(modifiedObjects, ghenv.Component)
    
    #print HBZones
    return HBZones

if _HBZones:
    result = main(_HBZones, intWallEPConstruction_, intWindowEPConstruction_, \
            intFloorEPConstruction_, intCeilingEPConstruction_)
    if result!=-1: modifiedHBZones = result