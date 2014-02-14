"""
False Color
-
Provided by Honybee 0.0.10
    
    Args:
        _HDRFilePath: Path to an HDR image file
        legendUnit_: Unit of the legend (e.g. lux, cd/m2,...)
        conversionF_: Conversion factor for the results. Default is 179.
        legendMax_: Maximum bound for the legend
        colorLines_: Set to True ro render the image with colored lines
        _render: Set to True to render the new image
    Returns:
        outputFilePath: Path to the result HDR file
"""

ghenv.Component.Name = "Honeybee_FalseColor"
ghenv.Component.NickName = 'FalseColor'
ghenv.Component.Message = 'VER 0.0.44\nFEB_14_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
import subprocess

def runCmdAndGetTheResults(command, shellKey = True):
    p = subprocess.Popen(["cmd", command], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # p.kill()
    return out, err

def getHDRSimulationType(HDRImagePath):
    #_simulationType_:
    #    [0] illuminance(lux), [1] radiation (wh), [2] luminance (Candela)

    with open(HDRImagePath, "r") as hdrFile:
        for lineCount, line in enumerate(hdrFile):
            if lineCount<10:
                if line.strip().lower().startswith("oconv"):
                    # check if the skytype could be radiation based on the sky type
                    if line.strip().lower().find("cumulativesky")>-1:
                        # annual radiation analysis
                        return 1
                    elif line.strip().lower().find("radanalysis")>-1:
                        # hourly radiation analysis
                        return 1.5
                    elif line.strip().split(" ")[-1].lower().startswith("c:/ladybug/skylib") or line.strip().lower.endswith(sky):
                        return 2.5 #this is a sky
                if line.strip().lower().startswith("rpict"):
                    if line.find("-i") > -1:
                        # is 0 or 1
                        return 0
            else:
                return 2 #luminance


def main(HDRFilePath, legendUnit, legendMax, conversionF, colorLines):

    # import the classes
    if sc.sticky.has_key('honeybee_release'):
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    # check for pfilt.exe
    if not os.path.isfile(hb_RADPath + "\\falsecolor2.exe"):
        msg = "Cannot find falsecolor2.exe at " + hb_RADPath + \
              "Make sure that falsecolor2 is installed on your system."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return
        
    validExt = ["HDR", "PIC"]
    if HDRFilePath.split('.')[-1].upper() not in validExt:
        msg = "Input file is not a valid HDR file."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        return
    else:
        inputFilePath = HDRFilePath.replace("\\" , "/")
        fileAddress = inputFilePath.replace(inputFilePath.split("/")[-1], "")
        fileName = "".join(inputFilePath.split("/")[-1].split('.')[:-1])
        if colorLines: outputFile = fileAddress + fileName + "@fc_cl.HDR"
        else: outputFile = fileAddress + fileName + "@fc.HDR"
    
    # check and remove the file if existed
    if os.path.isfile(outputFile):
        try: os.remove(outputFile)
        except: print "---"
    
    batchStr_head = "SET RAYPATH=.;" + hb_RADLibPath + "\n" + \
                    "PATH=" + hb_RADPath + ";$PATH\n\n"
    if not colorLines:
        batchStr_body = "falsecolor2 -i " + inputFilePath + " -s " + str(legendMax) + \
                        " -n 10 -mask 0.1 -l " + legendUnit + " -m " + str(conversionF) + \
                        " -z > " + outputFile + "\nexit"
    else:
        batchStr_body = "falsecolor2 -i " + inputFilePath + " -s " + str(legendMax) + \
                        " -p " +  inputFilePath + " -n 10 -cl -l " + legendUnit + " -m " + str(conversionF) + \
                        " -z > " + outputFile + "\nexit"
    
    batchStr = batchStr_head + batchStr_body
    batchFileName = fileAddress + 'FALSECLR.BAT'
    
        # check and remove the file if existed
    if os.path.isfile(batchFileName):
        try: os.remove(batchFileName)
        except: print "---"
        
    batchFile = open(batchFileName, 'w')
    batchFile.write(batchStr)
    batchFile.close()
    # os.system(batchFileName)
    
    runCmdAndGetTheResults("/c " + batchFileName)
    return outputFile


if _HDRFilePath and _render:
    # check the simulation type
    simulationType = getHDRSimulationType(_HDRFilePath)
    
    if simulationType == 0:
        #[0] illuminance(lux)
        legendUnit = "lux"
        conversionF = 179
    elif simulationType == 1:
        #[1] annual radiation (kwh),
        legendUnit = "kWh/m2"
        conversionF = 1
    elif simulationType == 1.5:
        #[1] radiation (wh),
        legendUnit = "Wh/m2"
        conversionF = 1
    elif simulationType == 2.5:
        #[1] radiation (wh),
        legendUnit = "w/sr/m2"
        conversionF = 179
    else:
        #[2] luminance (Candela)
        legendUnit = "cd/m2"
        conversionF = 179
    
    if legendUnit_!=None: legendUnit = legendUnit_
    
    if conversionF_!=None: conversionF = conversionF_
    
    if legendMax_ == None: legendMax_ = 'auto '
    
    outputFilePath = main(_HDRFilePath, legendUnit, legendMax_, conversionF, colorLines_)