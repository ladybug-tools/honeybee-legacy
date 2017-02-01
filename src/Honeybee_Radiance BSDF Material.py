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
Radiance BSDF Material

Create RADIANCE BSDF material

-
Provided by Honeybee 0.0.60

    Args:
        _materialName: Name of material for the Radiance simulation.
        _XMLFilePath: File path to XML that contains the BSDF information.
        _upOrientation_: An optional vector that sets the hemisphere that the BSDF material faces.  For materials that are symmetrical about the HBSrf plane (like non-angled venitian blinds), this can be any vector that is not perfectly normal to the HBSrf. For asymmetrical materials like angled veneitan blinds, this variable should be coordinated with the direction the HBSrfs are facing.  The default is set to (0.01, 0.01, 1.00), which should hopefully not be perpendicular to any typical HBSrf.
        thickness_: Optional parameter to set the thickness of the BSDF material.  The default is set to 0.
    Returns:
        RADMaterial: Radiance Material string
"""

ghenv.Component.Name = "Honeybee_Radiance BSDF Material"
ghenv.Component.NickName = 'radBSDFMaterial'
ghenv.Component.Message = 'VER 0.0.60\nOCT_01_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.58\nNOV_13_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

# A nice presentation on BSDF
# http://www.radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day2/GW5_BSDFFirstClass.pdf


def createBSDFMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  `int(len(args))`

    for arg in args:
        try: radMaterial += " " + "%.3f"%arg
        except: radMaterial += " " + str(arg)
    
    radMaterial += "\n0\n0\n"
    
    return radMaterial + "\n"

modifier = "BSDF"
function = "."

def main():
    
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
    
        if _materialName!=None and _XMLFilePath!=None:
            
            # check filepath for xml file
            if os.path.isfile(_XMLFilePath):
                
                materialName = _materialName.Replace(" ", "_")
                
                RADMaterial = createBSDFMaterial(modifier, materialName, thickness_, \
                                                _XMLFilePath.replace("\\", "/"), \
                                                _upOrientation_.X, _upOrientation_.Y, _upOrientation_.Z, function)
                
                return RADMaterial
                
            else:
                msg =  "Wrong path for XML file!"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, msg)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        

RADMaterial = main()