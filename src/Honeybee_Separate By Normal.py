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
Separate surfaces by normal
-
Provided by Honeybee 0.0.59

    Args:
        _geometry: Brep geometries
        _maxUpDecAngle_: Maximum normal declination angle from ZAxis that should be still considerd up
        _maxDownDecAngle_: Maximum normal declination angle from ZAxis that should be still considerd down
        
    Returns:
        lookingUp: List of surfaces which are looking upward
        lookingDown: List of surfaces which are looking downward
        lookingSide: List of surfaces which are looking to the sides
"""

import Rhino as rc
import scriptcontext as sc
import math

ghenv.Component.Name = "Honeybee_Separate By Normal"
ghenv.Component.NickName = 'separateByNormal'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


def separateByNormal(geometry, maximumRoofAngle = 30, maximumFloorAngle = 30):
    
    def getSrfCenPtandNormal(surface):
        surface = surface.Faces[0]
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = surface.PointAt(centerU, centerV)
        normalVector = surface.NormalAt(centerU, centerV)
        
        normalVector.Unitize()
        return centerPt, normalVector
    
    up = []
    down = []
    side = []
    
    # explode zone
    for i in range(geometry.Faces.Count):
        
        surface = geometry.Faces[i].DuplicateFace(False)
        
        # find the normal
        findNormal = getSrfCenPtandNormal(surface)

        if findNormal:
            normal = findNormal[1]
            angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
        else:
            angle2Z = 0
        
        if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
            up.append(surface)
        
        elif  180 - maximumFloorAngle < angle2Z < 180 + maximumFloorAngle:
            down.append(surface)
        
        else:
            side.append(surface)
    
    return up, down, side
    
    

if _geometry!=None:
    if _maxUpDecAngle_ == None: _maxUpDecAngle_ = 30
    if _maxDownDecAngle_ == None: _maxDownDecAngle_ = 30
    lookingUp, lookingDown, lookingSide = separateByNormal(_geometry, _maxUpDecAngle_, _maxDownDecAngle_)
