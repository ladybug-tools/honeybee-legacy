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
Select surfaces by type
-
Provided by Honeybee 0.0.60
    Args:
        _HBZones: Honeybee Zones
        _showWalls_: Set to true to output the walls
        _showWindows_: Set to true to output the windows
        _showAirWalls_: Set to true to output the air walls
        _showFloors_: Set to true to output the floors
        _showCeiling_: Set to true to output the cieling
        _showRoofs_: Set to true to output the roofs
    Returns:
        surfaces: Output surfaces as Grasshopper objects
        HBSurfaces: The output surfaces as Honeybee surfaces
"""
ghenv.Component.Name = "Honeybee_Select by Type"
ghenv.Component.NickName = 'selByType_'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

surfaces = []
HBSurfacestypezero = []
otherHBSurfaces = []
showCases = []
if _showWalls_ == True: 
    showCases.append(0)
    # Undergroundwall
    showCases.append(0.5)
    
if _showAirWalls_: showCases.append(4)
if _showFloors_ == True: 
    showCases.append(2)
    # For on-ground slab
    showCases.append(2.5)
    # For underground slab
    showCases.append(2.25)
    
if _showCeilings_: showCases.append(3)
if _showRoofs_: showCases.append(1)

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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)
    
    for zone in HBZoneObjects:
        
        # Extract surfaces from HBZones?
        for srf in zone.surfaces:
            print srf
            print srf.type
            try:
                if srf.type in showCases:
                    print srf
                    if srf.type == 0 and srf.hasChild:
                        surfaces.append(srf.punchedGeometry)
                        
                        HBSurfacestypezero.append(srf) # Added by Anton Szilasi for Honeybee PV generator component
                        
                    else:
                        surfaces.append(srf.geometry)

                        otherHBSurfaces.append(srf) # Added by Anton Szilasi for Honeybee PV generator component

                if _showWindows_ and srf.hasChild:
                    for childSrf in srf.childSrfs: surfaces.append(childSrf.geometry)
            except:
                pass
                
    HBSurfaces = hb_hive.addToHoneybeeHive(otherHBSurfaces, ghenv.Component)
    
    
    return surfaces,HBSurfaces
    
if _HBZones and _HBZones[0]!=None:
    results = main(_HBZones)

    if results!=-1:
        surfaces,HBSurfaces = results
