"""
Add Glazing

    Args:
        _name_: The name of the zone as a string
        _srfType_: 0:'WALL', 1:'ROOF', 2:'FLOOR', 3:'CEILING'
        _zoneType_: Optional input for the program of this zone
        isConditioned_: Set to true if the zone is conditioned
        _HBSurfaces: A list of Honeybee Surfaces
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

ghenv.Component.Name = 'Honeybee_addHBGlz'
ghenv.Component.NickName = 'addHBGlz'
ghenv.Component.Message = 'VER 0.0.43\nFEB_03_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


def main(HBSurface, childSurfaces, EPConstruction, RADMaterial, tolerance):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        
        
        # call the surface from the hive
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBSurface = hb_hive.callFromHoneybeeHive([HBSurface])[0]
        
        for srf in childSurfaces:
            # if the input is mesh, convert it to a surface
            try:
                # check if this is a mesh
                srf.Faces[0].IsQuad
                # convert to brep
                srf = rc.Geometry.Brep.CreateFromMesh(srf, False)
            except:
                pass
            
            # check if the surface is located on the base surface
            if HBSurface.isPossibleChild(srf, tolerance):
                # if yes then create the child surface
                guid = str(uuid.uuid4())
                name = "".join(guid.split("-")[:-1])
                number = guid.split("-")[-1]
                HBFenSrf = hb_EPFenSurface(srf, number, name, HBSurface, 5)
            
                if EPConstruction:
                    HBFenSrf.EPConstruction = EPConstruction
                if RADMaterial!=None:
                    addedToLib, HBSurface.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, False)
                
                    # if the material is not in the library add it to the library
                    if HBSurface.RadMaterial not in sc.sticky ["honeybee_RADMaterialLib"].keys():
                        hb_RADMaterialAUX.analyseRadMaterials(RADMaterial, True)
                
                # add it to the base surface
                
                HBSurface.addChildSrf(HBFenSrf)
        # send the HB surface back to the hive
        # add to the hive
        HBSurface  = hb_hive.addToHoneybeeHive([HBSurface], ghenv.Component.InstanceGuid.ToString())
        
        return HBSurface
        
    else:
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1

if _HBSurface!=None and len(_childSurfaces)!=0:
    
    # if tolerance_==None:
    tolerance_ = sc.doc.ModelAbsoluteTolerance
        
    HBSrfWGLZ = main(_HBSurface, _childSurfaces, EPConstruction_, RADMaterial_, tolerance_)