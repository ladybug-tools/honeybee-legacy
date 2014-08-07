# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert a mesh to RAD file
-
Provided by Honeybee 0.0.53
    
    Args:
        _mesh: List of meshes
        _RADMaterial: Full string of rad material as the base material
        HDRTexture_: Optional file path to HDR file to be used as a texture. Use Human plugin to map HDR image on mesh
        _workingDir_: Working directory
        _radFileName_: Radiance file name
        _writeRad: Set to True to convert mesh to rad
    Returns:
        materialFile: Path to material file
        radianceFile: Path to radiance file
"""

ghenv.Component.Name = "Honeybee_MSH2RAD"
ghenv.Component.NickName = 'MSH2RAD'
ghenv.Component.Message = 'VER 0.0.53\nAUG_01_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino as rc
import Grasshopper.Kernel as gh
import shutil
import os
import scriptcontext as sc
import time


def main(mesh, radFileName, workingDir, RADMaterial, HDRTexture = None):
    
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return None, None
    
    MSHToRAD = sc.sticky["honeybee_MeshToRAD"]
    meshToRadiance = MSHToRAD(mesh, radFileName, workingDir, HDRTexture, RADMaterial)
    objFile = meshToRadiance.meshToObj()
    materialFile, radianceFile = meshToRadiance.objToRAD(objFile)
    
    return materialFile, radianceFile


if _writeRAD and _mesh and _mesh[0]!=None and _RADMaterial:
    
    materialFile, radianceFile = main(_mesh, _radFileName_, _workingDir_, _RADMaterial)
    