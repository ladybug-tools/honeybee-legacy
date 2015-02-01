# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim User Profiles
Read here for details: http://daysim.ning.com/page/daysim-header-file-keyword-user-profile

-
Provided by Honeybee 0.0.56

    Args:
        _lightingControl_: 0 > Passive, 1 > active
        _blindControl_:  0 > Passive, 1 > active, 3 > based on daylight glare probability
        _frequency_: Frequency of the year that this user type will use the space.
    Returns:
        userProfile: Daysim user profile
"""
ghenv.Component.Name = "Honeybee_Daysim User Profiles"
ghenv.Component.NickName = 'DSUserProfiles'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
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
