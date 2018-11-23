#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Provided by Honeybee 0.0.64

    Args:
        _HBObject: Honeybee surface or Honeybee zone
        _angle: Angle of rotation in degrees
        centPt_: Optional rotation point if empty object center point will be used
        axis_: Optional rotation axis as a vector. Default is Z Axis
        _name_: An optional text string that will be appended to the name of the transformed object(s).  If nothing is input here, a default unique name will be generated.
        keepAdj_: Set to 'False' to remove existing adjacencies and boundary conditions (this is useful if you plan to re-solve adjacencies after this component). If left blank or set to 'True', the component will preserve adjacencies with other zones.
    Returns:
        HBObjs: Transformed objects
"""
ghenv.Component.Name = "Honeybee_Rotate Honeybee"
ghenv.Component.NickName = 'rotateHBObj'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nJUN_15_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass

import scriptcontext as sc
import uuid
import Rhino as rc
import math

def main(HBObj, angle, cenPt, axis, name, keepAdj=False):

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
        HBObject = hb_hive.callFromHoneybeeHive(HBObj)
    except:
        raise TypeError("Wrong input type for _HBObj. Connect a Honeybee Surface or a HoneybeeZone to HBObject input")
    
    if not axis:
        axis = rc.Geometry.Vector3d.ZAxis
    if keepAdj == False:
        clearBC = True
    else:
        clearBC = False
    
    angle = math.radians(angle)
    if name == None:
        newKey = str(uuid.uuid4())[:8]
    else:
        newKey = name
    
    for HObj in HBObject:
        if cenPt== None:
            cenPt = HObj.cenPt
        transform = rc.Geometry.Transform.Rotation(angle, axis, cenPt)
        HObj.transform(transform, newKey, clearBC)
    
    HBObj = hb_hive.addToHoneybeeHive(HBObject, ghenv.Component)

    return HBObj

if _HBObj is not [] and _angle is not None:
    result = main(_HBObj, _angle, cenPt_, axis_, _name_, keepAdj_)
    
    if result!=-1:
        HBObj = result