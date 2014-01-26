"""
Daysim User Profiles
Read here for details: http://daysim.ning.com/page/daysim-header-file-keyword-user-profile

    Args:
        _lightingControl_: 0 > Passive, 1 > active
        _blindControl_:  0 > Passive, 1 > active, 3 > based on daylight glare probability
        _frequency_: Frequency of the year that this user type will use the space.
    Returns:
        userProfile: Daysim user profile
"""
ghenv.Component.Name = "Honeybee_Daysim User Profiles"
ghenv.Component.NickName = 'DSUserProfiles'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

import Grasshopper.Kernel as gh

msg = "A place holder for now.\nFor now all the Daysim simulations will be run for an active " + \
      "user profile.\n The implication of the user profiles is technically so easy but can be " + \
      "really confusing for the users. Need more thought."
      
      
ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
userProfile = msg