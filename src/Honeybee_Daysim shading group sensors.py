# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim shading group sensors
Read here for more information about Daysim sensors here: http://daysim.ning.com/page/daysim-header-file-keyword-sensor-file-info-1
-
Provided by Honeybee 0.0.53

    Args:
        interiorSensors_: Selected list of test points that indicates where occupants sit. If empty Daysim will consider all the test points as sensors.
        exteriorSensors_: Selected list of test points that indicates the location of the exterior sensor. Exterior sensor will be only used if you are using the glare control. If empty Daysim will consider all the test points as sensors.
    
    Returns:
        shadingGroupSensors: Shading group sensors to be used for read Daysim result
"""

ghenv.Component.Name = "Honeybee_Daysim shading group sensors"
ghenv.Component.NickName = 'shadingGroupSensors'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


shadingGroupSensors = interiorSensors_, exteriorSensors_
