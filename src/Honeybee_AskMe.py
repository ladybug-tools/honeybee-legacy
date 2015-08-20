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
Use this component to get basic information on Honeybee Objects, whether they are HBSrfs or HBZones.

-
Provided by Honeybee 0.0.57

    Args:
        _HBObjects: Any valid Honeybee object.
    Returns:
        readMe!: Information about the Honeybee object.  Connect to a panel to visualize.
"""
ghenv.Component.Name = "Honeybee_AskMe"
ghenv.Component.NickName = 'askMe'
ghenv.Component.Message = 'VER 0.0.57\nJUL_15_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
try:
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(_HBObjects)
    for HBO in HBObjectsFromHive:
        print HBO
        #print HBO.getFloorArea()
        #print HBO.getZoneVolume()
        #for HBS in HBO.surfaces:
        #    print "----------------"
        #    #print HBS.getTotalArea()
        #    print "-----------------"
        #    print HBS
        #    print HBS.getOpaqueArea()
        #    print HBS.getWWR()
            
            
except Exception, e:
    print "Honeybee has no idea what this object is! Vviiiiiiz!"
    pass
