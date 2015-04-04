# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Genrate Custom Sky

This component generate a custom sky based on user's input
-
Provided by Honeybee 0.0.56
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _locationData: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _directNrmRad: Direct Normal Radiation in Wh/m2
        _diffuseHorRad: Diffuse Horizontal Radiation in Wh/m2
        _month: Month of the study [1-12]
        _day: Day of the study [1-31]
        _hour: Hour of the study [1-24]
    Returns:
        skyFilePath: Sky file location on the local drive
"""

ghenv.Component.Name = "Honeybee_Generate Custom Sky"
ghenv.Component.NickName = 'genCustomSky'
ghenv.Component.Message = 'VER 0.0.56\nAPR_04_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Sky"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
import math

def RADDaylightingSky(dirNrmRad, difHorRad, lat, long, timeZone, hour, day, month,  north = 0):
        
    print "Direct: " + `dirNrmRad` + "| Diffuse: " + `difHorRad`
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# location LAT: " + lat + " LON: " + long + "\n" + \
            "!gendaylit " + `month` + ' ' + `day` + ' ' + `hour` + \
            " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + \
            " -W " + `dirNrmRad` + " " + `difHorRad` + " -O " + `outputType` + \
            " | xform -rz " + str(north) + "\n" + \
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
            "0 0 -1 180\n"


def getLocationData(locationData):
    
    locationStr = locationData.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    
    newLocStr = newLocStr.replace(';', "")
    
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    return locationName, latitude, longitude, timeZone
    

def main(outputType, locationData, dirNrmRad, difHorRad, month, day, hour, north = 0):

    # import the classes
    if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key('ladybug_release'):

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
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug and Honeybee to fly...")
        return -1
    
    # check forgendaylit exist
    if not os.path.isfile(hb_RADPath + "\\gendaylit.exe"):
        msg = "Cannot find gendaylit.exe at " + hb_RADPath + \
              "Make sure that gendaylit is installed on your system."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    # import data from epw file data
    locName, lat, long, timeZone = getLocationData(locationData)
    newLocName = lb_preparation.removeBlank(locName)
        
    # make new folder for each city
    subWorkingDir = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\customSkies\\", newLocName)
    subWorkingDir = lb_preparation.makeWorkingDir(subWorkingDir)
    # print 'Current working directory is set to: ', subWorkingDir
    
    outputFile = subWorkingDir + "\\climateBasedSky@_" + `month` + "_" + `day` + "@" + ('%.2f'%hour).replace(".", "") + ".sky"

    northAngle, northVector = lb_preparation.angle2north(north)

    skyStr = RADDaylightingSky(dirNrmRad, difHorRad, lat, long, timeZone, hour, day, month, math.degrees(northAngle))
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile , `day` + "_" + `month` + "@" + ('%.2f'%hour).replace(".", "")
    
if _locationData!=None and _directNrmRad!=None and _diffuseHorRad!=None \
    and _month!=None and _day!=None and _hour!=None:
    
    outputType = 0
    result = main(outputType, _locationData, _directNrmRad, _diffuseHorRad, _month, _day, _hour, north_)
    
    if result!=-1:
        skyFilePath, skyDescription = result
