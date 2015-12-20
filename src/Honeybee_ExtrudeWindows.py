#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Sarith Subramaniam <sarith@sarith.in> 
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
Extrude pseudo walls from window polygons. This component has only been tested with rectangular windows.

-
Provided by Honeybee 0.0.58
    

    Args:
        _glazings: Any number of glazing polygons.
        _thickness: Thickness of the window. Can be a single number or a list of numbers. If its a list then the list should be equal to the number of glazings. Default value is 1.0.
    Returns:
        GlazingWalls: Geometric representations of glazing walls.
"""


from __future__ import print_function

ghenv.Component.Name = "Honeybee_Extrude_Windows"
ghenv.Component.NickName = 'ExtrudeWindows'
ghenv.Component.Message = 'VER 0.0.58\nDec_20_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc

if _thickness and _glazings is not None:
    
    
    #In case a single thickness value is specfied.
    try:
        if len(_thickness) ==1:
            _thickness = _thickness*len(_glazings)
    except TypeError:
        #In case the value is specified through a slider.
        _thickness = [_thickness]*len(_glazings)
        
    
    #Just to ensure that the thickness values are numbers.
    _thickness = map(float,_thickness)
    
    GlazingWalls =[]
    tol = sc.doc.ModelAbsoluteTolerance
    
    for glid,glazing in enumerate(_glazings):
        
        #Extract surface normal of the glazing, scale the surface normal to the size specified by the _thickness variable
        centroid,normal =  rs.SurfaceAreaCentroid(glazing)
        closestpoint = rs.SurfaceClosestPoint(glazing,centroid)
        surfnormal = rs.SurfaceNormal(glazing,closestpoint)
        surfnormalscaled = rs.VectorScale(surfnormal,_thickness[glid])
        
        #Use the scaled vector to loft to create individual glazing walls.
        edges = rs.DuplicateEdgeCurves(glazing)
        for segment in edges:
            segment = rs.coercecurve(segment)
            segmentCopy = segment.DuplicateCurve()
            segmentCopy.Translate(surfnormalscaled)
            srfs = rc.Geometry.Brep.CreateFromLoft([segment,segmentCopy],
            rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, \
            rc.Geometry.LoftType.Normal, False)
            GlazingWalls.extend(srfs)
    
    #combine everything together.
    WindowExtrusions = rc.Geometry.Brep.JoinBreps(GlazingWalls,tol)

else:
    raise Exception("Both the inputs are required for this component to run")