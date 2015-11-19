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
Use this component to make certain surface types of a zone adiabatic.

-
Provided by Honeybee 0.0.58

    Args:
        _HBZones: HBZones for which some surface types will be turned to adiabatic.
        walls_: Set to 'True' to have this surface type turned adiabatic.
        undergroundWalls_: Set to 'True' to have this surface type turned adiabatic.
        roofs_: Set to 'True' to have this surface type turned adiabatic.
        undergroundCeilings_: Set to 'True' to have this surface type turned adiabatic.
        floors_: Set to 'True' to have this surface type turned adiabatic.
        undergroundSlabs_: Set to 'True' to have this surface type turned adiabatic.
        groundFloors_: Set to 'True' to have this surface type turned adiabatic.
        exposedFloors_: Set to 'True' to have this surface type turned adiabatic.
        ceilings_: Set to 'True' to have this surface type turned adiabatic.
        airWalls_: Set to 'True' to have this surface type turned adiabatic.
        windows_: Set to 'True' to have this surface type turned adiabatic.
        interiorWalls_: Set to 'True' to have this surface type turned adiabatic.
        interiorWindows_: Set to 'True' to have this surface type turned adiabatic.
    Returns:
        HBZones: Modified HBZones with their surfaces made adiabatic that have a 'True' boolean connected to this component.
"""

ghenv.Component.Name = "Honeybee_Make Adiabatic By Type"
ghenv.Component.NickName = 'makeAdiabaticByType'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

def main(HBZones):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    types = []
    intTypes = []
    if walls_: types.append(0)
    if undergroundWalls_: types.append(0.5)
    if roofs_: types.append(1)
    if undergroundCeilings_: types.append(1.5)
    if floors_: types.append(2)
    if undergroundSlabs_: types.append(2.25)
    if groundFloors_: types.append(2.5)
    if exposedFloors_: types.append(2.75)
    if ceilings_: types.append(3)
    if airWalls_: types.append(4)
    if windows_: types.append(5)
    
    if interiorWalls_: intTypes.append(0)
    if interiorWindows_: intTypes.append(5)
    if floors_: intTypes.append(2)
    if airWalls_: intTypes.append(4)
    if ceilings_: intTypes.append(3)
    
    for HBO in HBObjectsFromHive:
        
        for HBS in HBO.surfaces:
            if HBS.BC != 'Surface':
                if HBS.type in types:
                    HBS.BC = "Adiabatic"
                    HBS.sunExposure = "NoSun"
                    HBS.windExposure = "NoWind"
                if HBS.hasChild and 5 in types:
                    for childSrf in HBS.childSrfs:
                        childSrf.BC = "Adiabatic"
                        childSrf.sunExposure = "NoSun"
                        childSrf.windExposure = "NoWind"
            else:
                if HBS.type in intTypes:
                    HBS.BC = "Adiabatic"
                    HBS.sunExposure = "NoSun"
                    HBS.windExposure = "NoWind"
                if HBS.hasChild and 5 in intTypes:
                    for childSrf in HBS.childSrfs:
                        childSrf.BC = "Adiabatic"
                        childSrf.sunExposure = "NoSun"
                        childSrf.windExposure = "NoWind"
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones
    
    
if _HBZones and _HBZones[0] != None:
    HBZones = main(_HBZones)