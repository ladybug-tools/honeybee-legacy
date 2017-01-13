#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <sadeghipour@gmail.com> 
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
Separate zones based on orientation
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: List of HBZones
        onlyWGlz_: Only consider surfaces with glazing

    Returns:
        orientations: List of orientation vectors
        HBZones: Honeybee zones. Each branch represents a different orientation
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Orientation'
ghenv.Component.NickName = 'separateZonesByOrientation'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import uuid
import math
import Rhino as rc
import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def getOrientation(HBZone, onlyWGlz):
    
    orientationVectors = []
    for HBSrf in HBZone.surfaces:
        if HBSrf.type == 0 and HBSrf.BC.lower()=="outdoors":
            if onlyWGlz and HBSrf.hasChild:
                for glzSrf in HBSrf.childSrfs:
                    if not glzSrf.normalVector in orientationVectors:
                        orientationVectors.append(glzSrf.normalVector)
            else:
                if not HBSrf.normalVector in orientationVectors:
                    orientationVectors.append(HBSrf.normalVector)
      
    # sort based on angle to north
    orientationVectors = sorted(orientationVectors, key = lambda \
                         a: rc.Geometry.Vector3d.VectorAngle(a, rc.Geometry.Vector3d.YAxis, rc.Geometry.Plane.WorldXY))
    
    return orientationVectors


def main(HBZones, onlyWGlz):
    
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
    
    HBZones = {}
    
    for HBZone in HBZonesFromHive:
        
        orientationVectors = getOrientation(HBZone, onlyWGlz)
        
        # conver vector list to list of string so it could be used as key
        angles = []
        for vector in orientationVectors:
            angles.append(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, rc.Geometry.Vector3d.YAxis, rc.Geometry.Plane.WorldXY)))
        key = "".join(map(str, angles))
        
        if key not in HBZones.keys():
            HBZones[key] = [orientationVectors, []]
        
        HBZones[key][1].append(HBZone)
        
        
    return HBZones

if _HBZones and _HBZones!=None:
    
    orderedHBZones = main(_HBZones, onlyWGlz_)
    
    if orderedHBZones!= -1:
        keys = orderedHBZones.keys()
        keys.sort()
        
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        HBZones = DataTree[Object]()
        orientations = DataTree[Object]()
        
        for count, key in enumerate(keys):
            p = GH_Path(count)
            orientations.AddRange(orderedHBZones[key][0],p)
            
            zones = hb_hive.addToHoneybeeHive(orderedHBZones[key][1],
                                              ghenv.Component, count==0)
            HBZones.AddRange(zones, p)
