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
Move Honeybee Objects

-
Provided by Honeybee 0.0.59

    Args:
        _HBObject: Honeybee surface or Honeybee zone
        _vector: Transform vector
    Returns:
        HBObjs: Transformed objects
"""
ghenv.Component.Name = "Honeybee_Move Honeybee"
ghenv.Component.NickName = 'moveHBObj'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import scriptcontext as sc
import uuid
import Rhino as rc


def main(HBObj, vector):

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
    
    # create a transform
    transform = rc.Geometry.Transform.Translation(_vector)
    #transform = rc.Geometry.Transform.Rotation(3.14, rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
    
    HBObject.transform(transform)
    
    HBObj = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

    return HBObj
    
if _HBObj and _vector:
    result = main(_HBObj, _vector)
    
    if result!=-1:
        HBObj = result