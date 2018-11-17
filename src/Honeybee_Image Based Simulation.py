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
Analysis Recipie for Image-Based Analysis
-
Provided by Honeybee 0.0.64
    
    Args:
        _skyFile: Path to a radiance sky file
        _rhinoViewsName_: viewName to be rendered
        sectionPlane_: Optional view fore clipping plane. The Plane should be perpendicular to the view
        _cameraType_: [0] Perspective, [1] FishEye, [2] Parallel
        _simulationType_: [0] illuminance(lux), [1] radiation (wh), [2] luminance (Candela). Default is 2 > luminance.
        _imageWidth_: Optional input for image width in pixels
        _imageHeight_: Optional input for image height in pixels
        _radParameters_: Radiance parameters
        backupImages_: [0] No backup, [1] Backup in the same folder, [2] Backup in separate folders. Default is 0.
        
    Returns:
        analysisRecipe: Recipe for image-based simulation
"""

ghenv.Component.Name = "Honeybee_Image Based Simulation"
ghenv.Component.NickName = 'imageBasedSimulation'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def main():
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1

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
        return -1
        
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    # As much as I dislike using global variables I feel lazy to change this now
    recipe = DLAnalysisRecipe(0, _skyFile, _rhinoViewsName_, _radParameters_,
                              _cameraType_, _simulationType_, _imageWidth_,
                              _imageHeight_, sectionPlane_, backupImages_, ghenv.Component)
    
    return recipe

if _skyFile:
    
    try: int(_simulationType_)
    except: _simulationType_ = 2 #luminance
    
    recipe = main()
    
    if recipe!=-1 and recipe.skyFile != None:
        analysisRecipe = recipe



