"""
prepare shading/context geometries

    Args:
        northVectorOrRotation: A vector that shows North or a number that shows
                               the rotation of the North from the Y axis
        bldgMasses: List of closed Breps as thermal zones.
    Returns:
        report: ...
        thermalZones: Thermal zone's geometries for visualiza
"""

ghenv.Component.Name = 'Honeybee EP context Surfaces'
ghenv.Component.NickName = 'HB_EPContextSrf'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

tolerance = sc.doc.ModelAbsoluteTolerance
import math


def main():
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        
        # don't customize this part
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPSHDSurface = sc.sticky["honeybee_EPShdSurface"]

        ########################################################################
        #----------------------------------------------------------------------#
        shdBreps = []
        if justBoundingBox:
            for brep in shdSurfaces:
                if brep.Faces.Count>1 or not brep.Faces[0].IsPlanar(sc.doc.ModelAbsoluteTolerance):
                    shdBreps.append(brep.GetBoundingBox(True).ToBrep())
                else:
                    shdBreps.append(brep)
        else: shdBreps = shdSurfaces
        
        shadingClasses = []
        shadingMeshPreview = []
        if meshingLevel == 0:
            mp = rc.Geometry.MeshingParameters.Minimal
            mp.SimplePlanes = True
        elif 0.25 < meshingLevel <0.75:
            mp = rc.Geometry.MeshingParameters.Default
        else:
            mp = rc.Geometry.MeshingParameters.Smooth
        
        def getRadMaterialName(radMaterial):
            nameStr = radMaterial.split(" ")[2]
            name =  nameStr.split("\n")[0]
            return name
        
        for brepCount, brep in enumerate(shdBreps):
            if len(brep.DuplicateEdgeCurves(False))>1:
                meshedGeo = rc.Geometry.Mesh.CreateFromBrep(brep, mp)
                for brepFaceIndex in range(brep.Faces.Count):
                    mesh = meshedGeo[brepFaceIndex]
                    #for meshCount, mesh in enumerate(meshedGeo):
                    thisShading = hb_EPSHDSurface(brep.Faces[brepFaceIndex].ToBrep(), 1000*brepCount + brepFaceIndex, 'shdSrf_' + `brepCount` + '_' + `brepFaceIndex`)
                    for faceIndex in  range(mesh.Faces.Count):
                        thisShading.collectMeshFaces(mesh.Faces.GetFaceVertices(faceIndex))
                    if EPConstruction!=None: thisShading.EPConstruction = EPConstruction
                    if RADConstruction!=None: thisShading.RadMaterial = getRadMaterialName(RADConstruction)
                    shadingClasses.append(thisShading)
                    # shadingMeshPreview.append(thisShading.meshedFace)
                    brepFaceIndex += 1
        
        # add to the hive
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBContext  = hb_hive.addToHoneybeeHive(shadingClasses, ghenv.Component.InstanceGuid.ToString())
        return HBContext
        ################################################################################################
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
        

if shdSurfaces and shdSurfaces[0]!=None:
    # add cleaning function
    result= main()
    
    if result != -1: HBContext = result