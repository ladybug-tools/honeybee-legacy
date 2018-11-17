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
Glare Control Recipe for Annual Simulation with Daysim "Based on exterior illuminance and/or position of the sun"
You need to add an external sensor later in the Daysim result reader.
-
Provided by Honeybee 0.0.64
    
    Args:
        exteriorSensor: Selected list of test points that indicates where occupants sit. If empty Daysim will consider all the test points as sensors.
        thresholdIlluminance: Threshold illuminance in lux to close the blind
        altitudeRange: Range of sun altitude that the blind should be closed as a Domain.
        azimuthRange: Range of sun azimuth that the blind should be closed as a Domain.
    Returns:
        glareControlRecipe: Recipe for glare control
"""

ghenv.Component.Name = "Honeybee_Daysim Glare Control Recipe"
ghenv.Component.NickName = 'DSGlareControl'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


# Daysim dynamic controls are very confusing to me. I don't now why the exterior and glare conrtol is not merged with
# so-called thermal control. Anyways. I had to separate (this so called) glare control from  


import scriptcontext as sc
import Grasshopper.Kernel as gh

class GlareControl(object):
    
    def __init__(self, threshold, altitudeRange, azimuthRange):
        self.threshold = threshold
        self.minAz = azimuthRange.T0
        self.maxAz = azimuthRange.T1
        self.minAltitude = altitudeRange.T0
        self.maxAltitude = altitudeRange.T1

def main(thresholdIlluminance, altitudeRange, azimuthRange):
    msg = None
    if thresholdIlluminance < 10000:
        msg = "Thershold illuminance value less than 10000 lux might be really low"
        
    return msg, GlareControl(thresholdIlluminance, altitudeRange, azimuthRange)

msg = None
if thresholdIlluminance!=None and altitudeRange!=None and azimuthRange!=None:
    msg, glareControlRecipe = main(thresholdIlluminance, altitudeRange, azimuthRange)
else:
    msg = "At the minimum one of the inputs is missing!"
    
if msg!=None:
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, msg)

"""
# Manual Control
==========================
= Shading Control System
==========================
shading -1
ReferenceOffice.dc ReferenceOffice.ill
shading_group_1
1
ManualControl state1.rad
state2.rad state2.dc state2.ill
...
"""

"""
...
# AutomatedThermalControl
==========================
= Shading Control System
==========================
shading -1
ReferenceOffice.dc ReferenceOffice.ill
shading_group_1
1
AutomatedThermalControl blank.rad
minimumIlluminance maxIlluminance SG0BS0.rad SG0BS0.dc SG0BS0.ill
...
"""
"""
...
==========================
= Shading Control System
==========================
shading -1
ReferenceOffice.dc ReferenceOffice.ill
shading_group_1
1
AutomatedThermalControlWithOccupancy stMonth stDay endMonth endDay C:\DIVA\Daylight\blank.rad
250 2500 SG0BS0.rad SG0BS0.dc SG0BS0.ill
...
"""

"""
...
==========================
= Shading Control System
==========================
shading -1
ReferenceOffice.dc ReferenceOffice.ill
shading_group_1
1
AutomatedThermalControlWithOccupancy stMonth stDay endMonth endDay C:\DIVA\Daylight\blank.rad
250 2500 SG0BS0.rad SG0BS0.dc SG0BS0.ill
...
"""

"""
shading -1
    BaseGeometryShadingUp.dc BaseGeometryShadingUp.ill
shading_group_1
    1
    AutomatedGlareControlWithOccupancy
    10000 -45 45 30 60
    06 01 08 15 EC_ClearState.rad
    300 2500 EC_TintedState.rad EC_TintedState.dc EC_TintedState.ill
    
    
shading -1
    BaseGeometryShadingUp.dc BaseGeometryShadingUp.ill
shading_group_1
    1
    AutomatedGlareControl
    10000 -45 45 30 60 EC_ClearState.rad
    300 2500 EC_TintedState.rad EC_TintedState.dc EC_TintedState.ill
"""
