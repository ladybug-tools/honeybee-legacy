# Open Pollination Website
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open the Pollination page
-
Provided by Honeybee 0.0.56

    Args:
        _download: Set Boolean to True to open the Pollination page
"""
ghenv.Component.Name = "Honeybee_open Pollination"
ghenv.Component.NickName = 'OpenPollination'
ghenv.Component.Message = 'VER 0.0.56\nFEB_17_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import webbrowser as wb
import Grasshopper.Kernel as gh

if _open:
    url = 'http://mostapharoudsari.github.io/Honeybee/Pollination'
    wb.open(url,2,True)
    print 'Vviiiiiiiizzzzz!'
else:
    msg = 'Set open to true...'
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    print msg