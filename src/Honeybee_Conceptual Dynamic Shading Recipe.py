# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Conceptual Shading Recipe for Annual Simulation with Daysim
You need to add sensor points later in the Daysim result reader.
-
Provided by Honeybee 0.0.51
    
    Args:
        This sensors will be triggered by the 50 W/m2 threshold. "When lowered the blinds transmit 25% of diffuse daylight and block all direct solar radiation."
        Read more here > http://daysim.ning.com/page/daysim-header-file-keyword-simple-dynamic-shading
        
    Returns:
        dynamicShadingGroup: Dynamic shading Group
"""

ghenv.Component.Name = "Honeybee_Conceptual Dynamic Shading Recipe"
ghenv.Component.NickName = 'conceptualDynamicSHDRecipe'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
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
