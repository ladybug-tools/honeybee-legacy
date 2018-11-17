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
Radiance Opaque Material

Create a Standard Radiance Opaque Material. Many thanks to Axel Jacobs for his help and all the great resources he provided at jaloxa.eu
Check out the color picker to see some great examples > http://www.jaloxa.eu/resources/radiance/colour_picker/index.shtml
-
Provided by Honeybee 0.0.64

    Args:
        _materialName: A unique name for material
        _RReflectance: Diffuse reflectance for red
        _GReflectance: Diffuse reflectance for green
        _BReflectance: Diffuse reflectance for blue
        _roughness_:  Roughness values above 0.2 are uncommon
        _specularity_: Specularity values above 0.9 is typical for metal
    Returns:
        avrgRef: Average diffuse reflectance of the material
        RADMaterial: Radiance Material string
"""

ghenv.Component.Name = "Honeybee_Radiance Metal Material"
ghenv.Component.NickName = 'radMetalMaterial'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.58\nNOV_13_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import scriptcontext as sc
import Grasshopper.Kernel as gh

# read here to understand RAD materials
# http://www.artifice.com/radiance/rad_materials.html
    
def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args: radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"


def main():
    modifier = "metal"
    
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
    
        if _materialName!=None and _RReflectance!=None and _GReflectance!=None and _BReflectance != None:
            if 0 <= _RReflectance <= 1 and 0 <= _GReflectance <= 1 and 0 <= _BReflectance <= 1:
                
                avrgRef = (0.265 * _RReflectance + 0.670 * _GReflectance + 0.065 * _BReflectance) * (1 - _specularity_) + _specularity_
                
                materialName = _materialName.Replace(" ", "_")
                #check if the name as same as value
                if materialName == str(_RReflectance):
                    materialName = "metal_" + materialName
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "We renamed the material name to "+materialName+", but we highly recommend you to give a notable name for good practice.")
                
                RADMaterial = createRadMaterial(modifier, materialName, _RReflectance, _GReflectance, _BReflectance, _specularity_, _roughness_)
                
                if _roughness_ > 0.2:
                     msg = "Roughness values above 0.2 are uncommon"
                     ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                     
                return avrgRef, RADMaterial
            else:
                msg =  "Reflectance values should be between 0 and 1"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, msg)
                return -1
        else:
             return -1
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
        

results = main()

if results!=-1 and results!=None:
    avrgRef, RADMaterial = results