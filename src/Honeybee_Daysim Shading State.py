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
Daysim Shading State for Advanced Dynamic Shading
-
Provided by Honeybee 0.0.64
    
    Args:
        shdHBObjects: A list of HB Objects that define the shading geometry and materials
        minIlluminance: Optional minimum illuminance in lux to open the blind. If you want the blinds to be manually controlled leave this input empty.
        maxIlluminance: Optional maximum illuminance in lux to close the blind. If you want the blinds to be manually controlled leave this input empty.
        
    Returns:
        shadingState: Shading state
"""

ghenv.Component.Name = "Honeybee_Daysim Shading State"
ghenv.Component.NickName = 'DSShadingState'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

class ShadingState(object):
    
    def __init__(self, shdHBObjects, minIlluminance, maxIlluminance):
        self.shdHBObjects = shdHBObjects
        self.minIlluminance = minIlluminance
        self.maxIlluminance = maxIlluminance
        
        if maxIlluminance==None:
            self.controlSystem = "ManualControl"
        else:
            self.controlSystem = "AutomatedThermalControl"


def main(shdHBObjects, minIll, maxIll):
    msg = None
    
    if not sc.sticky.has_key("honeybee_release"):
        msg = "You should let Honeybee fly first!"
        return msg, None
    
    # check if the objects are valid Honeybee objects
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(shdHBObjects)
    
    if len(HBObjectsFromHive)==0 or len(HBObjectsFromHive)!= len(shdHBObjects):
        msg = "At the minimum one of the shdHBObjects is not a valid Honeybee object."
        return msg, None
        
    # make sure min and max are both provided
    if (minIll== None and maxIll!=None) or (minIll!= None and maxIll==None):
        msg = "You need to either provide both minimum and maximum illuminance values so the control system will be considered as automated control\n " + \
              "or provide none of them so the system will be considered as manual."
        return msg, None
        
    return msg, ShadingState(shdHBObjects, minIll, maxIll)

if len(shdHBObjects)!=0:
    
    msg, shadingState = main(shdHBObjects, minIlluminance, maxIlluminance)
    
    if msg!=None:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
