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
Use this component to add a custom glazing surface to a HBSurface or HBZone.

-
Provided by Honeybee 0.0.60

    Args:
        _HBObj: A HBZone or HBSurface to which you would like to add a customized glazing surface.
        _childSurfaces: A surface or list of surfaces that represent the custom window(s) that you would like to add.  Note that these surfaces should be co-planar to the connected HBSurface or one of the surfaces of the connected HBZones.
        childSurfacesName_: An optional list of names for child surfaces. If names are provided the length of names should be the same as _childSurfaces.
        EPConstruction_: An optional list of EnergyPlus constructions to set the material construction of the window added to the HBSurface or HBZone.  This can be either the name of a window construction from the OpenStudio library (coming out of the 'Honeybee_Call from EP Construction Library' component) or a custom window construction you created from the 'Honeybee_EnergyPlus Construction' component. The list should match with childSurfaces list. In case the list doesn't match the first construction will be used for all surfaces.
        RADMaterial_: An optional Radiance material to set the material of the window added to the HBSurface or HBZone.  This can be either the name of a window material from the default Radaince library (coming out of the 'Honeybee_Call from Radiance Library' component) or a custom window material you created from any of the Radiance material components (like the 'Honeybee_Radiance Glass Material' component). The list should match with childSurfaces list. In case the list doesn't match the first material will be used for all surfaces.
    Returns:
        readMe!:...
        HBObjWGLZ: The Honeybee surface or zone with assigned glazing (in case of success).
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
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

def main(HBObject, childSurfaces, childSurfacesName, EPConstructions, RADMaterials, tolerance):

    def addPotentialChildSurface(HBSurface):
        
        glzCount = 0
        for srfCount, srf in enumerate(childSurfaces):
            # check if the surface is located on the base surface
            if HBSurface.isPossibleChild(srf, tolerance):
                # if yes then create the child surface
                guid = str(uuid.uuid4())
                try:
                    name = childSurfacesName[srfCount]
                except:
                   name = HBSurface.name + "_glz_" + str(glzCount) + "_" + "".join(guid.split("-")[:-1])

                number = guid.split("-")[-1]
                glzCount += 1
                HBFenSrf = hb_EPFenSurface(srf, number, name, HBSurface, 5)
                
                # check normal direction
                if not rc.Geometry.Vector3d.VectorAngle(HBFenSrf.normalVector, HBFenSrf.parent.normalVector)<sc.doc.ModelAngleToleranceRadians:
                    HBFenSrf.geometry.Flip()
                    HBFenSrf.normalVector.Reverse()
                
                if len(EPConstructions)!=0:
                    
                    try:
                        EPConstruction = EPConstructions[srfCount]
                    except:
                        EPConstruction = EPConstructions[0]
                    
                    if EPConstruction == None: continue
                        
                    # if it is just the name of the material make sure it is already defined
                    if len(EPConstruction.split("\n")) == 1:
                        # if the material is not in the library add it to the library
                        if not hb_EPObjectsAux.isEPConstruction(EPConstruction):
                            warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                                        "Add the construction to the library and try again."
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                            return 
                    else:
                        # it is a full string.
                        if EPConstruction.startswith('WindowMaterial:'):
                            warningMsg = "Your window construction, " + EPConstruction.split('\n')[1].split(',')[0] + ", is a window material and not a full window construction.\n" + \
                                        "Pass this window material through a 'Honeybee_EnergyPlus Construction' component cand connect the construction to this one."
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                            return 
                        added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(EPConstruction, overwrite = True)
                        
                        if not added:
                            msg = EPConstruction + " is not added to the project library!"
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
                    
                
                
                if len(RADMaterials)!= 0:
                    
                    try:
                        RADMaterial = RADMaterials[srfCount]
                    except:
                        RADMaterial = RADMaterials[0]
                    
                    if RADMaterial == None: continue
                    
                    if len(RADMaterial.strip().split(" ")) == 1:
                        if not hb_RADMaterialAUX.isMatrialExistInLibrary(RADMaterial):
                            warningMsg = "Can't find " + RADMaterial + " in RAD Material Library.\n" + \
                                "Add the material to the library and try again."
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                            return
                    
                    addedToLib, HBFenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
                    materialType = hb_RADMaterialAUX.getRADMaterialType(HBFenSrf.RadMaterial)
                    if materialType == 'plastic':
                        warningMsg = HBFenSrf.RadMaterial + " is not a typical glass material. Are you sure you selected the right material?"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                        return
    
                # add it to the base surface
                HBSurface.addChildSrf(HBFenSrf)
                HBSurface.calculatePunchedSurface()


    # import the classes
    if sc.sticky.has_key('honeybee_release'):
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
            
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
        
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
        
        # check number of faces and names
        if len(childSurfacesName)!= 0:
            if len(childSurfacesName)!=len(childSurfaces):
                nameCount = len(childSurfacesName)
                srfCount = len(childSurfaces)
                raise Exception("Length of _childSurfaces [%s] should match length of childSurfacesName [%s]"%(srfCount, nameCount))
        
        # call the surface from the hive
        hb_hive = sc.sticky["honeybee_Hive"]()
        try:
            HBObject = hb_hive.callFromHoneybeeHive([HBObject])[0]
        except:
            raise TypeError("Wrong input type for _HBObj. Connect a Honeybee Surface or a HoneybeeZone to HBObject input")

        # check if the object is a zone or a surface
        if HBObject.objectType == "HBZone":
            # add window for each surface
            for HBSurface in HBObject.surfaces:
                addPotentialChildSurface(HBSurface)
        else:
            # add window to the HBSurface
            addPotentialChildSurface(HBObject)
        
        # add to the hive
        HBObject  = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component)
        
        return HBObject
        
    else:
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1

if _HBObj!=None and len(_childSurfaces) and _childSurfaces[0]!=None:
    
    # if tolerance_==None:
    tolerance_ = sc.doc.ModelAbsoluteTolerance
        
    results = main(_HBObj, _childSurfaces, childSurfacesName_, EPConstructions_, RADMaterials_, tolerance_)
    
    if results != -1:
        HBObjWGLZ = results