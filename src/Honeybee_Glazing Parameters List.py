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


# Glazing Parameters Component
# By Chris Mackey
# Chris@MackeyArchitecture.com
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
Use this component to generate lists of glazing ratios, breakUp diatance, window heigths, sill heights, or vertical glazing splits for the four primary cardinal directions.
Depeding on your intended use of the numbers connected to this component, they should be plugged into the _glzRatio, breakUpWindow_, windowHeight_, sillHeight_, or splitGlzVertically_ inputs of the "Glazing based on ratio" component.

-
Provided by Honeybee 0.0.64

    Args:
        _northGlzParam_: Glazing parameter for the north side of a building.
        _westGlzParam_: Glazing parameter for the west side of a building.
        _southGlzParam_: Glazing parameter for the south side of a building.
        _eastGlzParam_: Glazing parameter for the east side of a building.
    Returns:
        glzParamList: A list of glazing parameters for different cardinal directions to be plugged into either the _glzRatio, breakUpWindow_, windowHeight_, sillHeight_, or splitGlzVertically_ input of the "Glazing based on ratio" component.
"""
ghenv.Component.Name = "Honeybee_Glazing Parameters List"
ghenv.Component.NickName = 'glzParamList'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

def checkParam(parameter):
    if parameter != None:
        if isinstance(parameter, (bool)): newParam = parameter
        else:
            try:
                newParam = float(parameter)
            except:
                newParam = parameter
    else: newParam = None
    return newParam

northGlzParam = checkParam(_northGlzParam_)
westGlzParam = checkParam(_westGlzParam_)
southGlzParam = checkParam(_southGlzParam_)
eastGlzParam = checkParam(_eastGlzParam_)

glzParamList = northGlzParam, westGlzParam, southGlzParam, eastGlzParam
