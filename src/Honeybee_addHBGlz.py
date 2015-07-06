#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Add Glazing

-
Provided by Honeybee 0.0.57

    Args:
        _HBObj: HBZone or HBSurface
        _childSurfaces: List of child surfaces 
        EPConstruction_: Optional EnergyPlus construction
        RADMaterial_: Optional RADMaterial
    Returns:
        readMe!:...
        HBObjWGLZ: Honeybee objects with assigned glazings in case of success
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid

ghenv.Component.Name = 'Honeybee_addHBGlz'
ghenv.Component.NickName = 'addHBGlz'
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


def main(HBObject, childSurfaces, EPConstruction, RADMaterial, tolerance):

    def addPotentialChildSurface(HBSurface, childSurfaces, EPConstruction, RADMaterial, tolerance):
        
        glzCount = 0
        for srfCount, srf in enumerate(childSurfaces):
            
            # check if the surface is located on the base surface
            if HBSurface.isPossibleChild(srf, tolerance):
                # if yes then create the child surface
                guid = str(uuid.uuid4())
                name = "glz_" + str(glzCount) + "_" + HBSurface.name + "_" + "".join(guid.split("-")[:-1])
                number = guid.split("-")[-1]
                glzCount += 1
                HBFenSrf = hb_EPFenSurface(srf, number, name, HBSurface, 5)
                
                # check normal direction
                if not rc.Geometry.Vector3d.VectorAngle(HBFenSrf.normalVector, HBFenSrf.parent.normalVector)<sc.doc.ModelAngleToleranceRadians:
                    HBFenSrf.geometry.Flip()
                    HBFenSrf.normalVector.Reverse()
                
                if EPConstruction:
                    # if it is just the name of the material make sure it is already defined
                    if len(EPConstruction.split("\n")) == 1:
                        # if the material is not in the library add it to the library
                        if not hb_EPObjectsAux.isEPConstruction(EPConstruction):
                            warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                                        "Add the construction to the library and try again."
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                            return
                    else:
                        # it is a full string
                        added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(EPConstruction, overwrite = True)
        
                        if not added:
                            msg = name + " is not added to the project library!"
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            print msg
                            return
                    
                    try:
                        HBFenSrf.setEPConstruction(EPConstruction)
                    except:
                        warningMsg = "You are using an old version of Honeybee_Honeybee! Update your files and try again."
                        print warningMsg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                        return -1
                    
                    
                if RADMaterial!=None:
                    addedToLib, HBFenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
                    
                    # if the material is not in the library add it to the library
                    if HBFenSrf.RadMaterial not in sc.sticky ["honeybee_RADMaterialLib"].keys():
                        addedToLib, HBFenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
    
                # add it to the base surface
                HBSurface.addChildSrf(HBFenSrf)
                HBSurface.calculatePunchedSurface()


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
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        
        
        # if any of child surfaces is mesh, convert them to a surface
        cleanChildSurfaces = []
        for srf in childSurfaces:
            try:
                # check if this is a mesh
                srf.Faces[0].IsQuad
                # convert to brep
                srf = rc.Geometry.Brep.CreateFromMesh(srf, False)
            except:
                pass
            
            # collect surfaces
            cleanChildSurfaces.append(srf)
            
        # call the surface from the hive
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBObject = hb_hive.callFromHoneybeeHive([HBObject])[0]
        
        # check if the object is a zone or a surface
        if HBObject.objectType == "HBZone":
            # add window for each surface
            for HBSurface in HBObject.surfaces:
                addPotentialChildSurface(HBSurface, childSurfaces, EPConstruction, RADMaterial, tolerance)
        else:
            # add window to the HBSurface
            addPotentialChildSurface(HBObject, childSurfaces, EPConstruction, RADMaterial, tolerance)
        
        # add to the hive
        HBObject  = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
        return HBObject
        
    else:
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1

if _HBObj!=None and len(_childSurfaces)!=0:
    
    # if tolerance_==None:
    tolerance_ = sc.doc.ModelAbsoluteTolerance
        
    results = main(_HBObj, _childSurfaces, EPConstruction_, RADMaterial_, tolerance_)
    
    if results != -1:
        HBObjWGLZ = results