#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com>
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
Scale Honeybee Objects Non-Uniformly
-
Provided by Honeybee 0.0.64
    Args:
        _HBObj: Honeybee surface or Honeybee zone
        _plane_: Base Plane
        _X_: Scaling factor in {x} direction
        _Y_: Scaling factor in {y} direction
        _Z_: Scaling factor in {z} direction
        _name_: An optional text string that will be appended to the name of the transformed object(s).  If nothing is input here, a default unique name will be generated.
        keepAdj_: Set to 'False' to remove existing adjacencies and boundary conditions (this is useful if you plan to re-solve adjacencies after this component). If left blank or set to 'True', the component will preserve adjacencies with other zones.
    Returns:
        HBObj: Transformed objects
"""


ghenv.Component.Name = "Honeybee_Scale Honeybee"
ghenv.Component.NickName = 'scaleHBObj'
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


def main(HBObj, P,X,Y,Z, name, keepAdj=False):

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
    
    if not P:
        P = rc.Geometry.Plane(rc.Geometry.Plane.WorldXY)
    if not X:
        X = 1
    if not Y:
        Y = 1
    if not Z:
        Z = 1
    if keepAdj == False:
        clearBC = True
    else:
        clearBC = False
    
    # create a NU scale
    NUscale = rc.Geometry.Transform.Scale(P,X,Y,Z)
    if name == None:
        newKey = str(uuid.uuid4())[:8]
    else:
        newKey = name
    
    for HObj in HBObject:
        HObj.transform(NUscale, newKey, clearBC)
    
    HBObj = hb_hive.addToHoneybeeHive(HBObject, ghenv.Component)
    
    return HBObj


if _HBObj:
    result = main(_HBObj, _plane_, _X_, _Y_, _Z_, _name_, keepAdj_)
    
    if result!=-1:
        HBObj = result