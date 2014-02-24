# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Glare Control Recipe for Annual Simulation with Daysim "Based on exterior illuminance and/or position of the sun"
You need to add an external sensor later in the Daysim result reader.
-
Provided by Honeybee 0.0.51
    
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
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
