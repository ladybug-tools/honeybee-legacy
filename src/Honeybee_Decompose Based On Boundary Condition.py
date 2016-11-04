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
Decompose zone surfaces by boundary condition
-
Provided by Honeybee 0.0.60

    Args:
        _HBZone: Honeybee Zone
        
    Returns:
        outdoors: A list of surfaces which has outdoors boundary condition
        surface: A list of surfaces which has surface boundary condition
        adiabatic: A list of surfaces which has adiabatic boundary condition
        ground: A list of surfaces which has ground boundary condition
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Boundary Condition"
ghenv.Component.NickName = 'decomposeByBC'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc



def main(HBZone):
    # import the classes
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
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    outdoors = []
    surface = []
    adiabatic = []
    ground = []

    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()

    zone = hb_hive.visualizeFromHoneybeeHive([HBZone])[0]

    for srf in zone.surfaces:
        if srf.BC.lower() == "outdoors":
            if srf.hasChild:
                outdoors.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    if childSrf.BC.lower() != "adiabatic":
                        outdoors.append(childSrf.geometry)
                    else: adiabatic.append(childSrf.geometry)
            else:
                outdoors.append(srf.geometry)
        elif srf.BC.lower() == "surface":
            if srf.hasChild:
                surface.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    if childSrf.BC.lower() != "adiabatic":
                        surface.append(childSrf.geometry)
                    else: adiabatic.append(childSrf.geometry)
            else:
                surface.append(srf.geometry)
        elif srf.BC.lower() == "adiabatic":
            if srf.hasChild:
                adiabatic.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    if childSrf.BC.lower() == "adiabatic":
                        adiabatic.append(childSrf.geometry)
                    elif childSrf.BC.lower() == "outdoors":
                        outdoors.append(childSrf.geometry)
                    else: surface.append(childSrf.geometry)
            else:
                adiabatic.append(srf.geometry)
        elif srf.BC.lower() == "ground":
            ground.append(srf.geometry)
        
    return outdoors, surface, adiabatic, ground


if _HBZone!= None:
    HBSurfaces = main(_HBZone)
    
    if HBSurfaces != -1:
        outdoors = HBSurfaces[0]
        surface = HBSurfaces[1]
        adiabatic = HBSurfaces[2]
        ground = HBSurfaces[3]