#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2016, Duncan Cox <duncanjamescox@gmail.com> 
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
Use this component to set the orientation(s) of the glazing.

-
Provided by Honeybee 0.0.64

    Args:
        _orientation: The orientation/s that you'd like to add glazing to.
        _ratio: The window to wall ratio.
    Returns:
        glzRatio: A list of glazing orientations that can be plugged into (glazingCreator).
"""

ghenv.Component.Name = 'Honeybee_orientHBGlz'
ghenv.Component.NickName = 'orientHBGlz'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nNOV_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

o_list = ['north', 'west', 'south', 'east']
glzRatio = [0,0,0,0]
for a in _orientation:
  try:   
    i = o_list.index(a.lower())
  except ValueError:
    print "%s is not a valid orientation." % str(a)
  finally:
    # input is valid, let's assign the direction
    glzRatio[i] = _ratio







