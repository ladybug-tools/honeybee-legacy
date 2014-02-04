"""
Create HBSurface
    
    Create a Honeybee surface
    
    Args:
        _geometry: List of Breps
        srfType_: Optional input for surface type > 0:'WALL', 1:'ROOF', 2:'FLOOR', 3:'CEILING', 4:'WINDOW'
        _EPConstruction_: Optional EnergyPlus construction
        _RadMaterial_: Optional Radiance Material
    Returns:
        readMe!:...
        HBZone: Honeybee zone as the result
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import uuid

ghenv.Component.Name = 'Honeybee_createHBSrfs'
ghenv.Component.NickName = 'createHBSrfs'
ghenv.Component.Message = 'VER 0.0.45\nFEB_03_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

tolerance = sc.doc.ModelAbsoluteTolerance
import math


def main(geometry, srfType, EPConstruction, RADMaterial):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    # if the input is mesh, convert it to a surface
    try:
        # check if this is a mesh
        geometry.Faces[0].IsQuad
        # convert to brep
        geometry = rc.Geometry.Brep.CreateFromMesh(geometry, False)
    except:
        pass
    
    # generate a random name
    # the name will be overwritten for energy simulation
    HBSurfaces = []
    
    for faceCount in range(geometry.Faces.Count):
        guid = str(uuid.uuid4())
        name = "".join(guid.split("-")[:-1])
        number = guid.split("-")[-1]
        
        HBSurface = hb_EPZoneSurface(geometry.Faces[faceCount].DuplicateFace(False), number, name)
        
        if srfType:
            try:
                surfaceType = int(srfType)
                if surfaceType == 4:
                    surfaceType = 5
                    warningMsg = "If you want to use this model for energy simulation, use addGlazing to add window to surfaces.\n" + \
                                 "It will be fine for Daylighting simulation though."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                
                if surfaceType in HBSurface.srfType.keys():
                    HBSurface.type = surfaceType
            except:
                surfaceType = srfType
                if surfaceType.ToUpper() in HBSurface.srfType.keys():
                    HBSurface.type = HBSurface.srfType[HBSurface.srfType[surfaceType.ToUpper()]]
        
        if srfType == None:
            # This will be recalculated 
            pass
            
        if EPConstruction!=None:
            HBSurface.EPConstruction = EPConstruction
            
        if RADMaterial!=None:
            # if the material is not in the library add it to the library
            if RADMaterial not in sc.sticky ["honeybee_RADMaterialLib"].keys():
                # if it is just the name of the material give a warning
                if len(RADMaterial.split(" ")) == 1:
                    warningMsg = "Can't find " + RADMaterial + " in RAD Material Library.\n" + \
                                "Add the material to the library and try again."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    return
                else:
                    # try to add the material to the library
                    addedToLib, HBSurface.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
            
        HBSurfaces.append(HBSurface)
    
    # add to the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBSurface  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString())
    
    return HBSurface
    
    
    

if _geometry != None:
    
    result= main(_geometry, srfType_, _EPConstruction_, _RADMaterial_)
    
    HBSurface = result