#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to create a THERM polygon with material properties.
-
Provided by Honeybee 0.0.58

    Args:
        _geometry: A closed planar curve or list of closed planar curves that represent the portions of a construction that have the same material type.  This input can also accept closed planar surfaces/breps/polysurfaces and even meshes!
        _material: Either the name of an EnergyPlus material from the OpenStudio library (from the "Call from EP Construction Library" component) or the output of any of the components in the "06 | Energy | Material" tab for creating materials.
        name_: An optional name for the polygon to keep track of it through the creation of the THERM model.
        RGBColor_: An optional color to set the color of the material when you import it into THERM.  All materials from the Honyebee Therm Library already possess colors but materials from the EP material lib will have a default blue color if no one is assigned here.
    Returns:
        readMe!:...
        thermPolygon: A polygon representing material properties
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid
import math

ghenv.Component.Name = 'Honeybee_Create Therm Polygons'
ghenv.Component.NickName = 'createThermPolygons'
ghenv.Component.Message = 'VER 0.0.58\nJAN_02_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nJAN_02_2015
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def getSrfCenPtandNormal(surface):
    brepFace = surface.Faces[0]
    u_domain = brepFace.Domain(0)
    v_domain = brepFace.Domain(1)
    centerU = (u_domain.Min + u_domain.Max)/2
    centerV = (v_domain.Min + v_domain.Max)/2
    
    centerPt = brepFace.PointAt(centerU, centerV)
    normalVector = brepFace.NormalAt(centerU, centerV)
    
    return centerPt, normalVector

def main(geometry, material, srfName, RGBColor):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
    
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        # don't customize this part
        hb_thermPolygon = sc.sticky["honeybee_ThermPolygon"]
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        hb_hive = sc.sticky["honeybee_Hive"]()
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    #Define a varialbe for acceptable geometry.
    geometryAccepted = False
    
    # if the input is mesh, convert it to a surface
    try:
        # check if this is a mesh
        geometry.Faces[0].IsQuad
        # convert to brep
        geometry = rc.Geometry.Brep.CreateFromMesh(geometry, False)
        geometryAccepted = True
    except:
        pass
    
    #If the input is a polyline, convert it to a surface.
    try:
        geometry = rc.Geometry.Brep.CreatePlanarBreps(geometry)
        if len(geometry) == 1:
            geometryAccepted = True
            geometry = geometry[0]
        else:
            warning = "The connected polyline geometry does not form a single closed planar surface. \n Try joining the curves into a single polyline before inputting them."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    except:
        pass
    
    #If the input has failed all tests up to this point, it is hopefully a planar brep or surface and we will just check this.
    if geometryAccepted == False:
        try:
            geometry.IsSurface
            geometryAccepted = True
        except: pass
        try:
            if geometry.HasBrepForm: geometry = geometry.ToBrep()
            geometryAccepted = True
        except: pass
    
    #If the geometry was not recognized, give a warning.
    if geometryAccepted == False:
        warning = "The connected geometry was not recgnized as a polyline, surface, brep/polysurface, or mesh."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Make a list to hold the final outputs.
    HBThermPolygons = []
    originalSrfName = srfName
    
    for faceCount in range(geometry.Faces.Count):
        #Check to be sure that the surface is planar.
        polyPlane = None
        if geometry.Faces[faceCount].IsPlanar(sc.doc.ModelAbsoluteTolerance):
            centPt, normal = getSrfCenPtandNormal(geometry)
            plane = rc.Geometry.Plane(centPt, normal)
        else:
            warning = "The connected surface geometry is not planar."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        # 0. check if user input a name for this surface
        guid = str(uuid.uuid4())
        number = guid.split("-")[-1]
        
        if srfName != None:
            if originalSrfName == None: originalSrfName = srfName
            originalSrfName = originalSrfName.strip().replace(" ","_")
            if geometry.Faces.Count != 1:
                srfName = originalSrfName + "_" + `faceCount`
            else: srfName = originalSrfName
        else:
            # generate a random name
            # the name will be overwritten for energy simulation
            srfName = "".join(guid.split("-")[:-1])
        
        # 1.3 assign a material
        if material!=None:
            # if it is just the name of the material make sure it is already defined
            if len(material.split("\n")) == 1:
                material = material.upper()
                if material in sc.sticky ["honeybee_materialLib"].keys(): pass
                elif material in sc.sticky ["honeybee_windowMaterialLib"].keys():pass
                elif material in sc.sticky["honeybee_thermMaterialLib"].keys():pass
                else:
                    warningMsg = "Can't find " + material + " in EP Material Library.\n" + \
                                "Create the material and try again."
                    print warningMsg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    return -1
            # if the material is not in the library add it to the library
            else:
                # it is a full string
                added, material = hb_EPMaterialAUX.addEPConstructionToLib(material, overwrite = True)
                material = material.upper()
                
                if not added:
                    msg = material + " is not added to the project library!"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                    return -1
        
        #Make the therm polygon.
        HBThermPolygon = hb_thermPolygon(geometry.Faces[faceCount].DuplicateFace(False), material, srfName, plane, RGBColor)
        
        if HBThermPolygon.warning != None:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, HBThermPolygon.warning)
        
        HBThermPolygons.append(HBThermPolygon)
    
    # add to the hive
    HBThermPolygon  = hb_hive.addToHoneybeeHive(HBThermPolygons, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBThermPolygon


if _geometry != None and _material != None:
    result= main(_geometry, _material, name_, RGBColor_)
    
    if result!=-1:
        thermPolygon = result
