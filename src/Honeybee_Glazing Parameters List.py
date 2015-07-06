#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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


# Glazing Parameters Component
# By Chris Mackey
# Chris@MackeyArchitecture.com
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to generate lists of glazing ratios, window heigths, and sill heights for different cardinal directions to be plugged into the glzRatio, windowHeight, and sillHeight inputs of the "Glazing based on ratio" component.

-
Provided by Honeybee 0.0.57

    Args:
        _northGlzRatio_: Glazing ratio for the north side of a building.
        _westGlzRatio_: Glazing ratio for the west side of a building.
        _southGlzRatio_: Glazing ratio for the south side of a building.
        _eastGlzRatio_: Glazing ratio for the east side of a building.
        --------------------: ...
        _northWindowHeight_: Height of the window on the north side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        _westWindowHeight_: Height of the window on the west side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        _southWindowHeight_: Height of the window on the south side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        _eastWindowHeight_: Height of the window on the east side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        --------------------: ...
        _northSillHeight_: Distance from the floor to the bottom of the window for the north side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        _westSillHeight_: Distance from the floor to the bottom of the window for the west side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        _southSillHeight_: Distance from the floor to the bottom of the window for the south side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        _eastSillHeight_: Distance from the floor to the bottom of the window for the eastside of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
    Returns:
        readMe!: ...
        glzRatioList: A list of glazing ratios for different cardinal directions to be plugged into the glzRatio input of the "Glazing based on ratio" component.
        windowHeightList: A list of window heights for different cardinal directions to be plugged into the windowHeight input of the "Glazing based on ratio" component.
        sillHeightList: A list of window sill heights for different cardinal directions to be plugged into the sillHeight input of the "Glazing based on ratio" component.
"""
ghenv.Component.Name = "Honeybee_Glazing Parameters List"
ghenv.Component.NickName = 'glzParamList'
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

def giveWarning(message):
    print message
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, message)
        
def checkRatio(ratio):
    if ratio == None: return 0
    elif ratio > 0.95:
        giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are nota accepted.")
        return 0
    elif ratio < 0:
        giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are nota accepted.")
        return 0
    else: return ratio
    
northRatio = checkRatio(_northGlzRatio_)
westRatio = checkRatio(_westGlzRatio_)
southRatio = checkRatio(_southGlzRatio_)
eastRatio = checkRatio(_eastGlzRatio_)

def checkWinHeight(height):
    if height == None: return 0
    elif height < sc.doc.ModelAbsoluteTolerance:
        giveWarning("Please put in window height values that are above your model's tolerance.")
        return 0
    else: return height

northHeight = checkWinHeight(_northWindowHeight_)
westHeight = checkWinHeight(_westWindowHeight_)
southHeight = checkWinHeight(_southWindowHeight_)
eastHeight = checkWinHeight(_eastWindowHeight_)

def checkSillHeight(height):
    if height == None: return 0
    elif height < sc.doc.ModelAbsoluteTolerance:
        giveWarning("Please put in sill height values that are above your model's tolerance.")
        return 0
    else: return height

northSill = checkSillHeight(_northSillHeight_)
westSill = checkSillHeight(_westSillHeight_)
southSill = checkSillHeight(_southSillHeight_)
eastSill = checkSillHeight(_eastSillHeight_)



glzRatioList = northRatio, westRatio, southRatio, eastRatio
windowHeightList = northHeight, westHeight, southHeight, eastHeight
sillHeightList = northSill, westSill, southSill, eastSill
