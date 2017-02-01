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
Rotate Honeybee Objects

-
Provided by Honeybee 0.0.60

    Args:
        _HBObject: Honeybee surface or Honeybee zone
        _angle: Angle of rotation in degrees
        centPt_: Optional rotation point if empty object center point will be used
        axis_: Optional rotation axis as a vector. Default is Z Axis
    Returns:
        HBObjs: Transformed objects
"""
ghenv.Component.Name = "Honeybee_Rotate Honeybee"
ghenv.Component.NickName = 'rotateHBObj'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass

import scriptcontext as sc
import uuid
import Rhino as rc
import math

def main(HBObj, angle, cenPt, axis):

    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
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
    try:
        HBObject = hb_hive.callFromHoneybeeHive([HBObj])[0]
    except:
        raise TypeError("Wrong input type for _HBObj. Connect a Honeybee Surface or a HoneybeeZone to HBObject input")
    
    if cenPt== None:
        cenPt = HBObject.cenPt
    
    if not axis:
        axis = rc.Geometry.Vector3d.ZAxis
    
    angle = math.radians(angle)
    
    # create a transform
    transform = rc.Geometry.Transform.Rotation(angle, axis, cenPt)
    
    HBObject.transform(transform)
    
    HBObj = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component)

    return HBObj
    
if _HBObj and _angle:
    result = main(_HBObj, _angle, cenPt_, axis_)
    
    if result!=-1:
        HBObj = result