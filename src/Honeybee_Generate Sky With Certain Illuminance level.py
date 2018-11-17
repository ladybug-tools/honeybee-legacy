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
Genrate a Uniform CIE Sky Based on Illuminace Value
-
Provided by Honeybee 0.0.64
    
    Args:
        _illuminanceValue : Desired value for horizontal sky illuminance in Lux
    Returns:
        skyFilePath: Sky file location on the local drive

"""

ghenv.Component.Name = "Honeybee_Generate Sky With Certain Illuminance level"
ghenv.Component.NickName = 'genSkyIlluminanceLevel'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

def RADDaylightingSky(illuminanceValue):
    
    # gensky 12 4 +12:00 -c -B 55.866 > skies/sky_10klx.mat
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# horizontal sky illuminance: " + `illuminanceValue` + " lux\n" + \
            "!gensky 12 6 12:00 -c -B " +  '%.3f'%(illuminanceValue/179) + "\n" + \
            "skyfunc glow sky_mat\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 1 1 0\n" + \
            "sky_mat source sky\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 1 180\n" + \
            "skyfunc glow ground_glow\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 .8 .5 0\n" + \
            "ground_glow source ground\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 -1 180\n" + \
            "# end of sky definition for daylighting studies\n\n"


def main(illuminanceValue):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return None, None

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    path  = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\basedOnIlluminanceLevel\\")
    
    if not os.path.isdir(path): os.mkdir(path)
    
    outputFile = path + `int(illuminanceValue)` + "_lux.sky"
    
    skyStr = RADDaylightingSky(illuminanceValue)
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile , "Sky with horizontal illuminance of: " + `illuminanceValue` + " lux"
    
if not _illuminanceValue: _illuminanceValue = 1000
results = main(_illuminanceValue)
if results != -1:
    skyFilePath, skyDescription = results