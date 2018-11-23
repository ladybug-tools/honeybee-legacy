#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Convert a mesh to RAD file
-
Provided by Honeybee 0.0.64
    
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
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nSEP_26_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return None, None
    
    MSHToRAD = sc.sticky["honeybee_MeshToRAD"]
    meshToRadiance = MSHToRAD(mesh, radFileName, workingDir, HDRTexture, RADMaterial)
    objFile = meshToRadiance.meshToObj()
    materialFile, radianceFile = meshToRadiance.objToRAD(objFile)
    
    return materialFile, radianceFile


if _writeRAD and _mesh and _mesh[0]!=None and _RADMaterial:
    
    materialFile, radianceFile = main(_mesh, _radFileName_, _workingDir_, _RADMaterial)
    