"""
False Color
-
Provided by Honybee 0.0.10
    
    Args:
        HDRFilePath: Path to an HDR image file
        legendUnit: Unit of the legend (e.g. lux, cd/m2,...)
        conversionF: Conversion factor for the results. Default is 179.
        legendMax: Maximum bound for the legend
        colorLines: Set to True ro render the image with colored lines
        render: Set to True to render the new image
    Returns:
        outputFilePath: Path to the result HDR file
"""

ghenv.Component.Name = "Honeybee_FalseColor"
ghenv.Component.NickName = 'FalseColor'
ghenv.Component.Message = 'VER 0.0.42\nJAN_26_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(legendUnit, legendMax, conversionF):

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
    batchFile = open(batchFileName, 'w')
    batchFile.write(batchStr)
    batchFile.close()
    os.system(batchFileName)
    return outputFile


if HDRFilePath and render:
    if legendUnit == None:
        legendUnit = 'unknown'
    if conversionF == None:
        if legendUnit.upper().find('WH') > -1:
            # Honeybee runs rpict with -i+ for radiation analysis so the factor has been already considered
            # user can overwrite this in case the fcator should be considered
            conversionF = 1
        else:
            # default
            conversionF = 179
    if legendMax == None: legendMax = 'auto '
    outputFilePath = main(legendUnit, legendMax, conversionF)