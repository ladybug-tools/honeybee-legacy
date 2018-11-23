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
Conceptual Shading Recipe for Annual Simulation with Daysim
You need to add sensor points later in the Daysim result reader.
-
Provided by Honeybee 0.0.64
    
    Args:
        This sensors will be triggered by the 50 W/m2 threshold. "When lowered the blinds transmit 25% of diffuse daylight and block all direct solar radiation."
        Read more here > http://daysim.ning.com/page/daysim-header-file-keyword-simple-dynamic-shading
        
    Returns:
        dynamicShadingGroup: Dynamic shading Group
"""

ghenv.Component.Name = "Honeybee_Conceptual Dynamic Shading Recipe"
ghenv.Component.NickName = 'conceptualDynamicSHDRecipe'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



class dynamicSHDRecipe(object):
    def __init__(self, type = 0, name = "conceptual_dynamic_shading"):
        self.type = type
        self.name = name
        self.sensorPts = None

dynamicShadingGroup = dynamicSHDRecipe(type = 0, name = "conceptual_dynamic_shading")

"""
==========================
= Shading Control System
==========================
shading 0
conceptual_dynamic_system fig.dc shade_up.ill
shade_down.ill

...
sensor_file_info 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 BG1
0 0 0 0 BG1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0
# the above defines in the sensor points
# list file where occupants sit
# (which sensors are triggered by the
# 50 W/m2 threshold)

"""
