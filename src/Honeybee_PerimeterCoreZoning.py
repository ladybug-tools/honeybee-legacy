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
Separate zones into perimeter and core
-
Provided by Honeybee 0.0.60

    Args:
        _bldgMasses: A Closed brep representing a building or a list of closed Breps.
        bldgsFlr2FlrHeights_: A floor height in Rhino model units or list of building floor heights for the geometries.
        perimeterZoneDepth_: A perimeter zone dpeth in Rhino model units or list of bperimeter depths for the geometries.
        _createHoneybeeZones: Set Boolean to True to split up the building mass into zones.
    Returns:
        readMe!: ...
        _splitBldgMasses: A lot of breps that correspond to the recommended means of breaking up geometry into zones for energy simulations.
"""


ghenv.Component.Name = 'Honeybee_PerimeterCoreZoning'
ghenv.Component.NickName = 'PerimeterCore'
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
    print len(HBZonesFromHive)
    interiorzones = []
    perimeterzones = []
    for zone in HBZonesFromHive:
        
        for surface in zone.surfaces:
            if surface.type == 0 and surface.BC.upper() == "OUTDOORS":
                #this is a perimeter wall
                perimeterzones.append(zone)
                break
                
        if zone not in perimeterzones:
            interiorzones.append(zone)
    
    perims  = hb_hive.addToHoneybeeHive(perimeterzones, ghenv.Component)
    ints = hb_hive.addToHoneybeeHive(interiorzones, ghenv.Component, False)
    
    return perims,ints


zones = main(_HBZones)

if zones!=-1:
    perimeters, interiors = zones