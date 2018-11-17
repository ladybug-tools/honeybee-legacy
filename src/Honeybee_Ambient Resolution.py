#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <chris@ladybug.tools> 
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
Use this component to calculate the ambient resoluation (ar) needed to resolve a detail of a diven dimension in Rhino model units. The full geometry scene of HBObjects is needed to calculate this number accurately
The resulting ar from this component can be plugged into the Honeybee_RADParameters component.
-
Provided by Honeybee 0.0.64
    
    Args:
        _HBObjects: All of the Honeybee objects that are going to be used in the daylight simulation.
        _minDetailDim: A number in Rhino model units that represents the dimension of the smallest detail that must be resolved in the daylight simulation.
        _aa_: An optional number for Ambient Accuracy. This value should be matched between this component and the Honeybee_RADParameters component.  If no value is input here, a default of 0.25 will be used, which is the default low-resolution value for aa.
    Returns:
        ar: The abmient resolution needed to resolve a detail of the input _minDetailDim.  This can be plugged into the Honeybee_RADParameters component.
"""

ghenv.Component.Name = "Honeybee_Ambient Resolution"
ghenv.Component.NickName = 'AR'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nDEC_12_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Rhino as rc


def main(HBObjects, minDetailDim, aa):
    # Check the aa.
    if aa == None:
        aa = 0.25
    
    # Calculate a bounding box around the HBObjects.
    BBs = []
    for item in HBObjects:
        BBs.append(item.GetBoundingBox(False))
    geoBB = BBs[0]
    for BB in BBs:
        geoBB.Union(BB)
    
    # get the longest dimension.
    xDim = geoBB.Max.X - geoBB.Min.X
    yDim = geoBB.Max.Y - geoBB.Min.Y
    zDim = geoBB.Max.Z - geoBB.Min.Z
    longestDim = max([xDim, yDim, zDim])
    
    # Calculate the ambient resolution.
    aRes = int((longestDim*aa)/minDetailDim)
    
    return aRes



#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if initCheck == True:
    ar = main(_HBObjects, _minDetailDim, _aa_)