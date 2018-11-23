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
This component generate a cumulative sky using GenCumulativeSky.exe. Only and only use it for radiation analysis (no daylighting!)
GenCumulativeSky is developed by Darren Robinson and Andrew Stone, and modified by Christoph Reinhart.
For more information, reference: http://www.solemma.net/references/PLEA2004_RobinsonAndStone.pdf

The first time you use this component, you need to be connected to the internet so the component can download GenCumulativeSky.exe to the working directory.
-
Provided by Honeybee 0.0.64
    
    Args:
        _weatherFile: epw weather file address on your system
        _analysisPeriod_: Indicates the analysis period. An annual study will be run if this input is not provided by the user
        _generateSky: Set boolean to True to run the component
    Returns:
        skyFilePath: Sky file location on the local drive
"""

ghenv.Component.Name = "Honeybee_Generate Cumulative Sky"
ghenv.Component.NickName = 'genCumSky'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import os
import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh


def main(weatherFile, analysisPeriod):
    
    def cumSkystr(calFile):
        skyStr = "#Cumulative Sky Definition\n" + \
                 "void brightfunc skyfunc\n" + \
                 "2 skybright " + calFile + "\n" + \
                 "0\n" + \
                 "0\n" + \
                 "skyfunc glow sky_glow\n" + \
                 "0\n" + \
                 "0\n" + \
                 "4 1 1 1 0\n" + \
                 "sky_glow source sky\n" + \
                 "0\n" + \
                 "0\n" + \
                 "4 0 0 1 180\n"
        return skyStr
        
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
            
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        # make working directory
        workingDir = lb_preparation.makeWorkingDir(sc.sticky["Honeybee_DefaultFolder"])
        
        # make sure the directory has been created
        if workingDir == -1: return -1
        
        workingDrive = workingDir[0:1]
        
        # GenCumulativeSky
        lb_preparation.downloadGenCumulativeSky(workingDir)
        if not os.path.isfile(workingDir + '\GenCumulativeSky.exe'):
            warning = 'Download failed!!! You need GenCumulativeSky.exe to use this component.' + \
                      '\nPlease check your internet connection, and try again!'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let the Ladybug fly...")
        return -1
    
    if weatherFile != None and weatherFile[-3:] == 'epw':
        # import data from epw file data
        locName, lat, lngt, timeZone, elev, locationStr = lb_preparation.epwLocation(weatherFile)
        newLocName = lb_preparation.removeBlank(locName)
        if len(list(newLocName)) > 15:
            newName = list(newLocName)[:-15]
            newLocName = ''.join(newName)
    else:
        print "epwWeatherFile address is not a valid .epw file"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "epwWeatherFile address is not a valid .epw file")
        return -1
    
    # make new folder for each city
    subWorkingDir = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\cumulativeSkies\\", newLocName)
    subWorkingDir = lb_preparation.makeWorkingDir(subWorkingDir)
    # print 'Current working directory is set to: ', subWorkingDir
    # copy .epw file to sub-directory
    lb_preparation.copyFile(weatherFile, subWorkingDir + "\\" + newLocName + '.epw')
    
    # generate the batch file
    # this part should be optimized for Honeybee - no need to do diffuse anymore
    batchStr = lb_preparation.genCumSkyStr(analysisPeriod, subWorkingDir, workingDir, newLocName, lat, lngt, timeZone)
    
    # write and run the batch file
    batchFileName = subWorkingDir + '\\' + newLocName + '_cumulativeSky.bat'
    batchFile = open(batchFileName, "w")
    batchFile.write(batchStr)
    batchFile.close()
    os.system(batchFileName)
    
    # call file address
    calFile = subWorkingDir + "\\" + newLocName + '_1.cal'
    
    #write the sky file
    # read the analysis period to name the file
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
    
    
    outputFile = subWorkingDir + "\\cumulativeSky_" + "_".join([str(stMonth), str(stDay), str(stHour), str(endMonth), str(endDay), str(endHour)])  + ".sky"
    
    skystr = cumSkystr(calFile)
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skystr)
    skyFile.close()
    
    return outputFile
    
if _generateSky and _weatherFile!=None:
    if not os.path.isfile(_weatherFile):
        print "Can't find the weather file at: " + _weatherFile
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Can't find the weather file at: " + _weatherFile)
    else:
        skyFilePath = main(_weatherFile, _analysisPeriod_)  
