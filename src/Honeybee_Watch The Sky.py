"""
Watch The Sky
-
Provided by Honybee 0.0.10
    
    Args:
        _skyFilePath: Path to a radiance sky file
        _imageSize_: Optional input for size of the imgae in pixles. Default value is 500 px
        _runIt: Set to true to run the analysis
    Returns:
        HDRImagePath: Path to the result HDR file

"""

ghenv.Component.Name = "Honeybee_Watch The Sky"
ghenv.Component.NickName = 'watchTheSky'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "2 | Daylight | Sky"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import scriptcontext as sc
import os
import shutil
import Grasshopper.Kernel as gh

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


def main(skyFilePath, imageSize):
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return
    
    
    fileNames = ["oconv.exe", "rpict.exe", "pcond.exe", "pflip.exe"]
    # check for files
    for fileName in fileNames:
        if not os.path.isfile(hb_RADPath + "\\" + fileName):
            msg = "Cannot find " + fileName + " at " + hb_RADPath + \
                  "Make sure that RADIANCE is installed on your system and try again."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return
        
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
        
    # generate the rad file
    oconvL = oconvLine(projectName, viewName, [skyFilePath])
    
    rpictL = rpictRenderSkyLine(imageSize, projectName, viewName)
    
    # run the study
    command = "@echo off\n" + \
              "echo Generating the sky view\n" + \
              oconvL + "\n" + \
              rpictL + "\n" + \
              "pcond -h+ " + skyImageFile + " > " + hSkyImageFile + "\n" + \
              "pflip -h " + hSkyImageFile + " > " + flippedSkyImageFile + "\n" + \
              "exit"

    with open(projectName + ".bat", "w") as inf:
        inf.write(command)
        
    os.system(projectName + ".bat")
    
    return flippedSkyImageFile
    
    
if _runIt and _skyFilePath:
    if _imageSize_ == None:
        _imageSize_ = 500 #pixles
    print "Image size:", _imageSize_
    HDRImagePath = main(_skyFilePath, _imageSize_)