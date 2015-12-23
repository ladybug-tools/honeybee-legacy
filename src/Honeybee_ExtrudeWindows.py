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

ghenv.Component.Name = "Honeybee_Extrude Windows"
ghenv.Component.NickName = 'extrudeWindows'
ghenv.Component.Message = 'VER 0.0.58\nDec_20_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh

if _thickness and _glazings is not None:

    #In case a single thickness value is specfied.
    if len(_thickness) ==1:
            _thickness = _thickness*len(_glazings)
    #In case multiple values are provided then ensure that the number of values equal the number of glazings.
    else:
        assert len(_thickness) == len(_glazings),"\nIn case individual thicknesses are being provided then" +\
        " the number of values should be equal to the number of _glazings"

    GlazingWalls =[]
    tol = sc.doc.ModelAbsoluteTolerance
    
    for glid,glazing in enumerate(_glazings):
        
        #Extract surface normal of the glazing, scale the surface normal to the size specified by the _thickness variable
        centroid = rc.Geometry.AreaMassProperties.Compute(glazing).Centroid
        closestPoint = rc.Geometry.Surface.ClosestPoint(glazing,centroid)[1:]
        surfNormal = rc.Geometry.Surface.NormalAt(glazing,*closestPoint)
        surfNormalScaled = surfNormal*_thickness[glid]
        

        #Use the scaled vector to loft to create individual glazing walls.
        glazingBrep = rc.Geometry.Brep.CreateFromSurface(glazing)
        edges = rc.Geometry.Brep.DuplicateEdgeCurves(glazingBrep)

        for segment in edges:
            segmentCopy = segment.DuplicateCurve()
            segmentCopy.Translate(surfNormalScaled)
            srfs = rc.Geometry.Brep.CreateFromLoft([segment,segmentCopy],
            rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, 
            rc.Geometry.LoftType.Normal, False)
            GlazingWalls.extend(srfs)
    
    #combine everything together.
    WindowExtrusions = rc.Geometry.Brep.JoinBreps(GlazingWalls,tol)

else:
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Inputs for both _glazings and _thickness are required for this component to run.")