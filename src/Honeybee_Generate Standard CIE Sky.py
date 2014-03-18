# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Genrate Standard CIE Sky
-
Provided by Honeybee 0.0.51
    
    Args:
        _weatherFile: epw file location on your system as a string
        _hour: Input a number to indicate hour
        _day: Input a number to indicate day
        _month: Input a number to indicate month
        _skyType: CIE Sky Type [0] Sunny with sun, [1] sunny without sun, [2] intermediate with sun, [3] intermediate without sun, [4] cloudy sky, [5] uniform sky
    Returns:
        skyFilePath: Sky file location on the local drive

"""

ghenv.Component.Name = "Honeybee_Generate Standard CIE Sky"
ghenv.Component.NickName = 'genStandardCIESky'
ghenv.Component.Message = 'VER 0.0.52\nMAR_17_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "2 | Daylight | Sky"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh


def date2Hour(month, day, hour):
    # fix the end day
    numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    JD = numOfDays[int(month)-1] + int(day)
    return (JD - 1) * 24 + hour

def getRadiationValues(epw_file, HOY):
    epwfile = open(epw_file,"r")
    for lineCount, line in enumerate(epwfile):
        if lineCount == int(HOY + 8 - 1):
            dirRad = (float(line.split(',')[14]))
            difRad = (float(line.split(',')[15]))
    epwfile.close()
    return dirRad, difRad

skyDict = {
0 : ('+s', 'sunnyWSun'),
1 : ('-s', 'sunnyNoSun'),
2 : ('+i', 'intermWSun'),
3 : ('-i', 'intermNoSun'),
4 : ('-c', 'cloudySky'), 
5 : ('-u', 'uniformSky')
}

def RADDaylightingSky(epwFileAddress, skyType, locName, lat, lngt, timeZone, hour, day, month):
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# location name: " + locName + " LAT: " + lat + "\n" + \
            "!gensky " + `month` + ' ' + `day` + ' ' + `hour` + ' ' + skyDict[skyType][0] + \
            " -a " + lat + " -o " + `-float(lngt)` + " -m " + `-float(timeZone) * 15` + "\n" + \
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


def main(weatherFile, month, day, hour, skyType):
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
    
    if weatherFile != None and weatherFile[-3:] == 'epw':
        if not os.path.isfile(weatherFile):
            print "Can't find the weather file at: " + weatherFile
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Can't find the weather file at: " + weatherFile)
            return -1
        # import data from epw file data
        locName, lat, lngt, timeZone, elev, locationStr = lb_preparation.epwLocation(weatherFile)
        newLocName = lb_preparation.removeBlank(locName)
    else:
        print "epwWeatherFile address is not a valid .epw file"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "epwWeatherFile address is not a valid .epw file")
        return -1
        
    # make new folder for each city
    subWorkingDir = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\CIESkies\\", newLocName)
    subWorkingDir = lb_preparation.makeWorkingDir(subWorkingDir)
    # print 'Current working directory is set to: ', subWorkingDir
    
    outputFile = subWorkingDir + "\\CIE_" + skyDict[skyType][1] + "_sky_"+ `month` + \
                "_" + `day` + "@" + ('%.2f'%hour).replace(".", "") + ".sky"
    
    skyStr = RADDaylightingSky(weatherFile, skyType, newLocName, lat, lngt, timeZone, hour, day, month)
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile , `day` + "_" + `month` + "@" + ('%.2f'%hour).replace(".", "")
    
if _weatherFile!=None and _month!=None and _day!=None and _hour!=None:
    if _skyType == None: _skyType = 5
    result = main(_weatherFile, _month, _day, _hour, _skyType)
    
    if result!=-1:
       skyFilePath, skyDescription = result
