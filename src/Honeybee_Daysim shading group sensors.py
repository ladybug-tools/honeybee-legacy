"""
Daysim shading group sensors
Read here for more information about 
-

    Args:
        interiorSensors_: Selected list of test points that indicates where occupants sit. If empty Daysim will consider all the test points as sensors.
        exteriorSensors_: Selected list of test points that indicates the location of the exterior sensor. Exterior sensor will be only used if you are using the glare control. If empty Daysim will consider all the test points as sensors.
    
    Returns:
        shadingGroupSensors: Shading group sensors to be used for read Daysim result
"""

ghenv.Component.Name = "Honeybee_Daysim shading group sensors"
ghenv.Component.NickName = 'shadingGroupSensors'
ghenv.Component.Message = 'VER 0.0.43\nFEB_10_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

shadingGroupSensors = interiorSensors_, exteriorSensors_