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
Daysim shading group sensors
Read here for more information about Daysim sensors here: http://daysim.ning.com/page/daysim-header-file-keyword-sensor-file-info-1
-
Provided by Honeybee 0.0.64

    Args:
        interiorSensors_: Selected list of test points that indicates where occupants sit.
        exteriorSensors_: Selected list of test points that indicates the location of the exterior sensor. Exterior sensor will be only used if you are using the glare control.
    
    Returns:
        shadingGroupSensors: Shading group sensors to be used for read Daysim result
"""

ghenv.Component.Name = "Honeybee_Daysim shading group sensors"
ghenv.Component.NickName = 'shadingGroupSensors'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


shadingGroupSensors = interiorSensors_, exteriorSensors_
