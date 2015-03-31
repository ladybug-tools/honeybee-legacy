# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert HDR to TIF
-
Provided by Honeybee 0.0.56
    
    Args:
        TIFFilePath: Path to the result TIFF file
        
    Returns:
        HDRFilePath: Path to an HDR image file
        
"""

ghenv.Component.Name = "Honeybee_Convert TIF to HDR"
ghenv.Component.NickName = 'TIF > HDR'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
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
    
def main(TIFFFilePath):

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
        
    # check for ra_tiff.exe
    if not os.path.isfile(hb_RADPath + "\\ra_tiff.exe"):
        msg = "Cannot find ra_tiff.exe at " + hb_RADPath + \
              "Make sure that Radiance is fully installed on your system."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return
    
    validExt = ["TIFF", "TIF"]
    if TIFFFilePath.split('.')[-1].upper() not in validExt:
        msg = "Input file is not a valid TIFF file."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return
    else:
        inputFilePath = TIFFFilePath.replace("\\" , "/")
        fileAddress = inputFilePath.replace(inputFilePath.split("/")[-1], "")
        fileName = "".join(inputFilePath.split("/")[-1].split('.')[:-1])
        outputFile = fileAddress + fileName + ".HDR"
        
    if os.path.isfile(outputFile):
        try: os.remove(outputFile)
        except:
            # rename the file
            count = 1
            while os.path.isfile(outputFile):
                outputFile = os.path.dirname(outputFile) + "\\" + \
                             os.path.basename(outputFile) + "_" + str(count)  + ".HDR"
            #msg = "Can't remove the old GIF file..."
            #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    
    hInputFilePath = outputFile.replace(".TIF", "_h.HDR")
    
    batchStr =  "SET RAYPATH=.;" + hb_RADLibPath + "\n" + \
                "PATH=" + hb_RADPath + ";$PATH\n\n"
    
    batchStr += "ra_tiff -r " + inputFilePath + " " + outputFile + \
                    "\nexit\n"
                    
    batchFileName = fileAddress + 'TIFF2HDR.BAT'
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

if _TIFFFilePath!=None: HDRFilePath = main(_TIFFFilePath)

