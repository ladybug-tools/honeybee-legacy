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
Convert HDR to TIF
-
Provided by Honeybee 0.0.64
    
    Args:
        _HDRFilePath: Path to an HDR image file
        adjustExposure_: "Mimic human visual response in the output. The goal of this process is to produce output that correlates strongly with a persons subjective impression of a scene."
        
    Returns:
        TIFFilePath: Path to the result TIFF file
"""

ghenv.Component.Name = "Honeybee_Convert HDR to TIF"
ghenv.Component.NickName = 'HDR > TIF'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
import subprocess

def runCmdAndGetTheResults(command, shellKey = True):
    p = subprocess.Popen(["cmd", command], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # p.kill()
    return out, err
    
def main(HDRFilePath):

    # import the classes
    if sc.sticky.has_key('honeybee_release'):

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return
            
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
        
    # check for ra_tiff.exe
    if not os.path.isfile(hb_RADPath + "\\ra_tiff.exe"):
        msg = "Cannot find ra_tiff.exe at " + hb_RADPath + \
              "Make sure that Radiance is fully installed on your system."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return
    
    validExt = ["HDR", "PIC"]
    if HDRFilePath.split('.')[-1].upper() not in validExt:
        msg = "Input file is not a valid HDR file."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return
    else:
        inputFilePath = HDRFilePath.replace("\\" , "/")
        fileAddress = inputFilePath.replace(inputFilePath.split("/")[-1], "")
        fileName = "".join(inputFilePath.split("/")[-1].split('.')[:-1])
        outputFile = fileAddress + fileName + ".TIF"
        
    if os.path.isfile(outputFile):
        try: os.remove(outputFile)
        except:
            # rename the file
            count = 1
            while os.path.isfile(outputFile):
                outputFile = os.path.dirname(outputFile) + "\\" + \
                             os.path.basename(outputFile) + "_" + str(count)  + ".TIF"
            #msg = "Can't remove the old GIF file..."
            #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    
    hInputFilePath = outputFile.replace(".TIF", "_h.HDR")
    
    batchStr =  "SET RAYPATH=.;" + hb_RADLibPath + "\n" + \
                "PATH=" + hb_RADPath + ";$PATH\n\n"
    if adjustExposure_:
        batchStr += "pcond -h+ " + inputFilePath + " > " + hInputFilePath + "\n" + \
                    "ra_tiff " + hInputFilePath + " " + outputFile + \
                    "\nexit\n"
    else:
        batchStr += "ra_tiff " + inputFilePath + " " + outputFile + \
                    "\nexit\n"
                    
    batchFileName = fileAddress + 'HDR2TIFF.BAT'
    batchFile = open(batchFileName, 'w')
    batchFile.write(batchStr)
    batchFile.close()

    # os.system("start /min /B /wait " + batchFileName)
    runCmdAndGetTheResults("/c " + batchFileName)
    
    if os.path.isfile(outputFile):
        return outputFile
    else:
        msg = "Failed to genearate the .gif file. Open the bat file with a text editor " + \
              "and change the last line from exit to pause. Then run it again and see what is the error.\n" + \
              "here is the file address: " + batchFileName
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return

if _HDRFilePath!=None:
    TIFFFilePath = main(_HDRFilePath)

