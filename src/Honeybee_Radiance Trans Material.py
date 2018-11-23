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
Radiance Trans Material

This component is useful to create translucent materials. Many thanks to David Mead for his slides at:
http://radiance-online.org/community/workshops/2010-freiburg/PDF/DavidMead.pdf
-
Provided by Honeybee 0.0.64
    
    Args:
        _materialName: Unique name for this material
        _RTransmittance:
        _GTransmittance:
        _BTransmittance:
        _specularReflection: Reflected specularity; Matte = min 0, Uncoated Glass ~ .06, Satin = suggested max 0.07
        roughness: Surface roughness; Polished = 0, Low gloss = suggested max 0.02
        _diffuseTransmission: Diffuse Transmission; Opaque = 0, Transparent = 1
        _specularTransmission: Specular Transmission; Diffuse = 0, Clear = 1
    Returns:
        out: ...
        transMaterial: Radiance Material Definition

"""

ghenv.Component.Name = "Honeybee_Radiance Trans Material"
ghenv.Component.NickName = 'radTransMaterial'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



import math
import scriptcontext as sc
from clr import AddReference
import Grasshopper.Kernel as gh

import scriptcontext as sc

def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    if modifier == "trans":
        
        cr, cg, cb, rs, td, ts, roughness = args
        
        rd = (0.265 * cr + 0.670 * cg + 0.065 * cb)
        
        absorb = 1-td-ts-rd-rs
        
        if absorb < 0:
            summ = td + ts + rd + rs 
            errorMsg = "Sum of Diffuse Transmission, Specular Transmission," + \
                       "Specular Reflection and Diffuse Reflection cannot be more than 1.\n" + \
                       "Your current inputs are " + "%.3f"%td + " + %.3f"%ts + " + %.3f"%rs + " + %.3f"%rd + \
                       " = %.3f"%summ
            
            print errorMsg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, errorMsg)
            return
            
        
        # calculate the material
        A7 = ts/(td+ts)
        A6 = (td+ts) / (rd + td +ts)
        A5 = roughness
        A4 = rs
        A3 = cb/((1-rs)*(1-A6))
        A2 = cg/((1-rs)*(1-A6))
        A1 = cr/((1-rs)*(1-A6))
        
        if A3>1 or A2>1 or A1>1:
            errorMsg = "This material is physically impossible to create!\n" + \
                       "You need to adjust the inputs for diffuse reflectance values."
            print errorMsg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, errorMsg)
            return
        
        print "absorption: %.3f"%absorb
        args = A1, A2, A3, A4, A5, A6, A7
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args: radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"



if sc.sticky.has_key('honeybee_release'):
    modifier = "trans"

    if _materialName and _RDiffReflectance!=None and _GDiffReflectance!=None and _BDiffReflectance!=None and _specularReflection!=None and _diffuseTransmission!=None and _specularTransmission!=None:
        
        if _roughness_ == None: _roughness_ = 0
        
        materialName = _materialName.Replace(" ", "_")
        
        transMaterial = createRadMaterial(modifier, _materialName, _RDiffReflectance, _GDiffReflectance, _BDiffReflectance, _specularReflection, _diffuseTransmission, _specularTransmission, _roughness_)
        
    else:
        msg = "At least one of the required inputs is missing"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
