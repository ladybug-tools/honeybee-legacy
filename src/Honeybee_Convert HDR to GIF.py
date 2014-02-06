
"""
Convert HDR to GIF
-
Provided by Honybee 0.0.10
    
    Args:
        HDRFilePath: Path to an HDR image file
        adjustExposure_: "Mimic human visual response in the output. The goal of this process is to produce output that correlates strongly with a persons subjective impression of a scene."
    Returns:
        GIFFilePath: Path to the result GIF file
"""

ghenv.Component.Name = "Honeybee_Convert HDR to GIF"
ghenv.Component.NickName = 'HDR > GIF'
ghenv.Component.Message = 'VER 0.0.46\nFEB_06_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

def main():
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
    
    # check for ra_gif exist
    if not os.path.isfile(hb_RADPath + "\\ra_gif.exe"):
        msg = "Cannot find rad_gif.exe at " + hb_RADPath + \
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
        outputFile = fileAddress + fileName + ".GIF"
        
    if os.path.isfile(outputFile):
        try: os.remove(outputFile)
        except:
            # rename the file
            count = 1
            while os.path.isfile(outputFile):
                outputFile = os.path.dirname(outputFile) + "\\" + \
                             os.path.basename(outputFile) + "_" + str(count)  + ".GIF"
            #msg = "Can't remove the old GIF file..."
            #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    
    hInputFilePath = outputFile.replace(".GIF", "_h.HDR")
    
    batchStr =  "SET RAYPATH=.;" + hb_RADLibPath + "n" + \
                "PATH=" + hb_RADPath + ";$PATH\n\n"
    
    if adjustExposure_:
        batchStr += "pcond -h+ " + inputFilePath + " > " + hInputFilePath + "\n" + \
                    "ra_gif " + hInputFilePath + " " + outputFile + \
                    "\nexit\n"
    else:
        batchStr += "ra_gif " + inputFilePath + " " + outputFile + \
                    "\nexit\n"
                    
    batchFileName = fileAddress + 'HDR2GIF.BAT'
    batchFile = open(batchFileName, 'w')
    batchFile.write(batchStr)
    batchFile.close()
    
    os.system("start /min /B /wait " + batchFileName)
    return outputFile


if HDRFilePath: GIFFilePath = main()
