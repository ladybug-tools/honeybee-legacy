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
Radiance Glass Material
Read more here to understand Radiance materials: http://www.artifice.com/radiance/rad_materials.html
-
Provided by Honeybee 0.0.64

    Args:
        _materialName: Unique name for this material
        _RTransmittance: Transmittance for red. The value should be between 0 and 1
        _GTransmittance: Transmittance for green. The value should be between 0 and 1
        _BTransmittance: Transmittance for blue. The value should be between 0 and 1
        refractiveIndex_: RefractiveIndex is 1.52 for glass and 1.4 for ETFE
    Returns:
        avrgTrans: Average transmittance of this glass
        RADMaterial: Radiance Material string

"""

ghenv.Component.Name = "Honeybee_Radiance Glass Material"
ghenv.Component.NickName = 'radGlassMaterial'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.58\nNOV_13_2015
#compatibleLBVersion = VER 0.0.59\nNOV_11_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import math
import scriptcontext as sc
import Grasshopper.Kernel as gh



# refractiveIndex is 1.52 for glass and 1.4 for ETFE

def getTransmissivity(transmittance):
    if transmittance != 0:
        transmissivity = (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) - 0.9166530661 ) / 0.0036261119 / transmittance
    else:
        return 0
        
    if transmissivity>1: return 1
    
    return transmissivity
    
def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args:
        radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"


def main():
    modifier = "glass"
    
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
    
        if _materialName!=None and _RTransmittance!=None and _GTransmittance!=None and _BTransmittance!=None:
            if 0 <= _RTransmittance <= 1 and 0 <= _GTransmittance <= 1 and 0 <= _BTransmittance <= 1:
                
                avrgTrans = (0.265 * _RTransmittance + 0.670 * _GTransmittance + 0.065 * _BTransmittance)
                
                materialName = _materialName.strip().Replace(" ", "_")
                #check if the name as same as value
                if materialName == str(_RTransmittance):
                    materialName = "glass_" + materialName
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "We renamed the material name to "+materialName+", but we highly recommend you to give a notable name for good practice.")
                RADMaterial = createRadMaterial(modifier, materialName, getTransmissivity(_RTransmittance), getTransmissivity(_GTransmittance), getTransmissivity(_BTransmittance), refractiveIndex_)
                
                return avrgTrans, RADMaterial
            else:
                msg =  "Transmittance values should be between 0 and 1"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, msg)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

results = main()

if results!=-1 and  results!=None:
    avrgTrans, RADMaterial = results
    