# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set Exposure for HDR
-
Provided by Honeybee 0.0.55
    
    Args:
        _HDRFilePath: Path to an HDR image file
        _exposure_: A number between 0 and 1
        _render: Set to True to render the new image
    Returns:
        outputFilePath: Path to the result HDR file

"""

ghenv.Component.Name = "Honeybee_Set Exposure for HDR"
ghenv.Component.NickName = 'setHDRExposure'
ghenv.Component.Message = 'VER 0.0.55\nDEC_16_2014'
ghenv.Component.Category = "Honeybee@DL"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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

def main(HDRFilePath, exposure):
    
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
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
    
    # check for pfilt.exe
    if not os.path.isfile(hb_RADPath + "\\pfilt.exe"):
        msg = "Cannot find pfilt.exe at " + hb_RADPath + \
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
        outputFile = fileAddress + fileName + "@exp_" + "%.3f"%exposure + ".HDR"
        
    batchStr = "SET RAYPATH=.;" + hb_RADLibPath + "n" + \
                "PATH=" + hb_RADPath + ";$PATH\n\n" + \
           "pfilt -e " + "%.3f"%exposure + " " + inputFilePath + " > " + outputFile + \
           "\nexit"
    
    batchFileName = fileAddress + 'SETEXPOSURE.BAT'
    batchFile = open(batchFileName, 'w')
    batchFile.write(batchStr)
    batchFile.close()
    #os.system("start /min /B /wait " + batchFileName)
    
    runCmdAndGetTheResults("/c " + batchFileName)
    
    return outputFile


if _HDRFilePath and _render:
    if _exposure_ == None: _exposure_ = 1
    outputFilePath = main(_HDRFilePath, _exposure_)
