#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2015-2017, Sarith Subramaniam <sarith@sarith.in> 
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
    This component is to be used for specifying the location of luminaires for electric lighting simulations.
    -
    For external lighting applications the best option would be to use the aimingPoint_ option to specify where all the luminaires should be aimed to.
    In case luminaires are being aimed by specifying spin, tilt and orientation angles, the following conventions apply:
        1. _spin_ : specifies the rotation of a luminaire about its G0 axis.
        2. _tilt_: species the rotation of a luminaire around the Y axis.
        3. _orientation_: specifies the rotation of a luminaire around the Z axis.
    The recommended sequence of applying rotations is tilt,orientation and spin. 
    _
    The aiming conventions followed in this component are based on the IES LM-63-2002 and were tested against indoor lighting simulations with AGI32 software.


    Args:
        _ptsList: List of points/3d coordinates where the luminaires are to be located.
        _spin_: Luminaire spin angle. 
        _tilt_: Luminaire tilt angle.
        _orientation_: Luminaire rotation angle.
        aimingPoint_: Location at which the photometric axis of each luminaire should be aimed.
        customLamp_: Specify a custom lamp using the IES Custom Lamp component
    Returns:
        luminaireZone: List of coordinates and rotation angles for luminaires
        locations: List of luminaire coordinates alone. This output can be used for previewing luminaire locations.
"""



ghenv.Component.Name = "Honeybee_IES Luminaire Zone"
ghenv.Component.NickName = 'iesLuminaireZone'
ghenv.Component.Message = 'VER 0.0.58\nJAN_21_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"

try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import Rhino as rc
import math
import sys


class lumZone:
    
    def __init__(self, points, lamp):
        self.points = points
        self.lamp = lamp
    
    def __repr__(self):
        return "Honeybee.luminaireZone"

#Lambda function for setting default values.
setdefault = lambda var,defval:var if var else defval

#Set default values
_tilt_,_spin_,_orientation_ = map(lambda x: setdefault(x,0.0),(_tilt_,_spin_,_orientation_))

luminaireArray= []
locations = []
if _ptsList:
    try:
        for pt in _ptsList:
            if aimingPoint_:
                #Vector between luminaire location and aiming location
                ptVector = rc.Geometry.Vector3d(aimingPoint_-pt)
                
                #normalize the vector
                unitizeVector = rc.Geometry.Vector3d.Unitize(ptVector)

                #Create C0 and G0 vectors. c0 along x axis and g0 along negative Z.
                c0Vector = rc.Geometry.Vector3d(1,0,0)
                g0Vector = rc.Geometry.Vector3d(0,0,-1)
                 
                angleG0 =  360-math.degrees(rc.Geometry.Vector3d.VectorAngle(ptVector,g0Vector))
                
                #A hacky solution for when there is no aiming to be done.
                try:
                    angleC0 = 360 - math.degrees(rc.Geometry.Vector3d.VectorAngle(ptVector,c0Vector,rc.Geometry.Plane(0,0,1,-1)))
                except OverflowError: 
                    angleC0 = 0
    
                spinAngle,tiltAngle,orientationAngle = 0+_spin_,angleG0+_tilt_,angleC0+_orientation_

                luminaireArray.append((pt,(spinAngle,tiltAngle,orientationAngle)))
                print("Location(x,y,z):({0},{1},{2}). Aiming Angles(degrees): Spin:{3}, Tilt:{4}, Rotation:{5}".format(pt[0],pt[1],pt[2],spinAngle,tiltAngle,orientationAngle))
            else:    

                luminaireArray.append((pt,(_spin_,-_tilt_,_orientation_)))

    except:
        print(sys.exc_info())
    luminaireZone = lumZone(luminaireArray,customLamp_)
else:
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "At least one 3dpoint is required as input in _ptsList for this component to work.")