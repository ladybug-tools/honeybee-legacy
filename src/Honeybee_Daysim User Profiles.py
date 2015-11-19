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
Daysim User Profiles
Read here for details: http://daysim.ning.com/page/daysim-header-file-keyword-user-profile

-
Provided by Honeybee 0.0.58

    Args:
        _lightingControl_: 0 > Passive, 1 > active
        _blindControl_:  0 > Passive, 1 > active, 3 > based on daylight glare probability
        _frequency_: Frequency of the year that this user type will use the space.
    Returns:
        userProfile: Daysim user profile
"""
ghenv.Component.Name = "Honeybee_Daysim User Profiles"
ghenv.Component.NickName = 'DSUserProfiles'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Grasshopper.Kernel as gh

msg = "A place holder for now.\nFor now all the Daysim simulations will be run for an active " + \
      "user profile.\n The implication of the user profiles is technically so easy but can be " + \
      "really confusing for the users. Need more thought."
      
      
ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
userProfile = msg
