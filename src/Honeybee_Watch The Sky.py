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
Watch The Sky
-
Provided by Honeybee 0.0.64
    
    Args:
        _skyFilePath: Path to a radiance sky file
        _imageSize_: Optional input for size of the imgae in pixles. Default value is 500 px
        _runIt: Set to true to run the analysis
    Returns:
        HDRImagePath: Path to the result HDR file
        globalHorIrradiance: Global horizontal irradiance for an upstructed test point under this sky (wh/m2) - In case you're watching the cumulative sky the number is in (KWh/m2).

"""

ghenv.Component.Name = "Honeybee_Watch The Sky"
ghenv.Component.NickName = 'watchTheSky'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import os
import shutil
import Grasshopper.Kernel as gh
import subprocess

def runCmdAndGetTheResults(command, shellKey = True):
    p = subprocess.Popen(["cmd", command], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # p.kill()
    return out, err

def rpictRenderSkyLine(viewSize, projectName, viewName):
    octFile = projectName + "_" + viewName + ".oct"
    outputFile = projectName + "_" + viewName + ".HDR"
    rpictLine = "rpict -i -t 10 -ab 1 -ad 1000 -as 20 -ar 300 -aa 0.1 " + \
                "-vth -vp 0 0 0 -vd 0 0 1 -vu 0 1 0 -vh 180 -vv 180 " + \
                "-x " + str(viewSize) + " -y " + str(viewSize) + " " + \
                octFile + " > " + outputFile + "\n"
    return rpictLine



def oconvLine(projectName, viewName, radFilesList):
    # sence files
    senceFiles = ""
    for address in radFilesList: senceFiles = senceFiles + address.replace("\\" , "/") + " "
    
    line = "oconv -f " +  senceFiles + " > " + projectName + "_" + viewName + ".oct\n"
    
    return line


def rtraceLine(projectName, viewName):
    
    octFile = projectName + "_" + viewName + ".oct"
    resultFile = projectName + "_" + viewName + ".irr"
    
    # Result will be in Wh/m^2
    # EPiSODE have a really good post on this if you want to read more:
    # http://episode-hopezh.blogspot.com/2012/05/viz-sky-generated-by-gendaylit.html?view=flipcard
    line = "echo 0 0 0 0 0 1 | rtrace -w -h -I+ -ab 1 " + octFile + " | rcalc -e "'"$1 = $1 * 0.265 + $2 * 0.670 + $3*0.065"'" > " + resultFile + "\n"
    
    return line, resultFile
    
def checkSky(skyFile):
    lines = []
    with open(skyFile, "r") as skyIn:
        for line in skyIn:
            if line.strip().startswith("!gendaylit"):
                line = line.replace("-O 0", "-O 1")
            lines.append(line)
            
    skyFileOut = skyFile.split(".")[0] + "_radAnalysis.sky"
    
    with open(skyFileOut, "w") as skyOut:
        for line in lines:
            skyOut.write(line)
    
    return skyFileOut
    
def main(skyFilePath, imageSize):
    if sc.sticky.has_key('honeybee_release'):
        
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
        
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return None, None
    
    fileNames = ["oconv.exe", "rpict.exe", "pcond.exe", "pflip.exe"]
    # check for files
    for fileName in fileNames:
        if not os.path.isfile(hb_RADPath + "\\" + fileName):
            msg = "Cannot find " + fileName + " at " + hb_RADPath + \
                  "Make sure that RADIANCE is installed on your system and try again."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return None, None
    
    
    # change the sky in case it is for gendaylit
    skyFilePath = checkSky(skyFilePath)
    
    projectName = skyFilePath.split(".")[0]
    radFile = skyFilePath.split(".")[0] + "_geometry.RAD"
    viewName = "skyView"
    
    #return the file path
    skyImageFile = projectName + "_" + viewName + ".HDR"
    hSkyImageFile = projectName + "_" + viewName + "_h.HDR" # human eye
    flippedSkyImageFile = projectName + "_" + viewName + "_f.HDR" # flipped image so it looks the same as ladybug sky view
    
    # remove the old file
    if os.path.isfile(skyImageFile):
        try: shutil.remove(skyImageFile)
        except: "Failed to remove the old sky image. The result might be wrong"
    
    # write the path string (I should check radiance to be installed on the system
    pathStr = "SET RAYPATH=.;" + hb_RADLibPath + "\nPATH=" + hb_RADPath + ";$PATH\n"
    
    # generate the rad file
    oconvL = oconvLine(projectName, viewName, [skyFilePath])
    
    rpictL = rpictRenderSkyLine(imageSize, projectName, viewName)
    
    rtraceL, resultFile = rtraceLine(projectName, viewName)
    
    # run the study
    command = "@echo off\n" + \
              "echo Generating the sky view\n" + \
              pathStr + "\n" + \
              oconvL + "\n" + \
              rpictL + "\n" + \
              rtraceL + "\n" + \
              "pcond -h+ " + skyImageFile + " > " + hSkyImageFile + "\n" + \
              "pflip -h " + hSkyImageFile + " > " + flippedSkyImageFile + "\n" + \
              "exit"

    with open(projectName + ".bat", "w") as outf:
        outf.write(command)
        
    #os.system(projectName + ".bat")
    runCmdAndGetTheResults( "/c " + projectName + ".bat")
    
    # read the result of the global horizontal irradiance
    with open(resultFile, "r") as inf:
        try:
            gHorIrr = inf.readlines()[0].strip()
        except:
            gHorIrr = "Failed to calculate!"
    
    return flippedSkyImageFile, gHorIrr
    
    
if _runIt and _skyFilePath:
    if _imageSize_ == None:
        _imageSize_ = 500 #pixles
    print "Image size:", _imageSize_
    
    results = main(_skyFilePath, _imageSize_)
    
    if results!=-1:
        HDRImagePath, globalHorIrradiance = results
