# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Genrate a Uniform CIE Sky Based on Illuminace Value
-
Provided by Honeybee 0.0.55
    
    Args:
        _illuminanceValue : Desired value for horizontal sky illuminance in Lux
    Returns:
        skyFilePath: Sky file location on the local drive

"""

ghenv.Component.Name = "Honeybee_Generate Sky With Certain Illuminance level"
ghenv.Component.NickName = 'genSkyIlluminanceLevel'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Sky"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

def RADDaylightingSky(illuminanceValue):
    
    # gensky 12 4 +12:00 -c -B 55.866 > skies/sky_10klx.mat
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# horizontal sky illuminance: " + `illuminanceValue` + " lux\n" + \
            "!gensky 12 6 12:00 -u -B " +  '%.3f'%(illuminanceValue/179) + "\n" + \
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