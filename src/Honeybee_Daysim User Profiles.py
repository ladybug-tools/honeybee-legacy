# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim User Profiles
Read here for details: http://daysim.ning.com/page/daysim-header-file-keyword-user-profile

-
Provided by Honeybee 0.0.55

    Args:
        _lightingControl_: 0 > Passive, 1 > active
        _blindControl_:  0 > Passive, 1 > active, 3 > based on daylight glare probability
        _frequency_: Frequency of the year that this user type will use the space.
    Returns:
        userProfile: Daysim user profile
"""
ghenv.Component.Name = "Honeybee_Daysim User Profiles"
ghenv.Component.NickName = 'DSUserProfiles'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Grasshopper.Kernel as gh

msg = "A place holder for now.\nFor now all the Daysim simulations will be run for an active " + \
      "user profile.\n The implication of the user profiles is technically so easy but can be " + \
      "really confusing for the users. Need more thought."
      
      
ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
userProfile = msg
