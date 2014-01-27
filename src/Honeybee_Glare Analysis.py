"""
Glare Analysis

This component is using evalglare for glare calculations. Evalgalare is developed by J. Wienold at Fraunhofer ISE.
http://www.ise.fraunhofer.de/en/
-
Provided by Honybee 0.0.10
    
    Args:
        _HDRImagePath: Path to an HDR image file
        taskPositionUV_: Task position in x and y coordinates
        taskPositionAngle_: Task position opening angle in degrees
        _runIt: Set to True to run the analysis
    Returns:
        readMe: ...
        glareCheckImage: Path to HDR image of the glare study
        DGP: Daylight glare probability
        DGI: Daylight glare index
        imageWithTaskArea: Path to HDR image with task area marked with blue circle

"""

ghenv.Component.Name = "Honeybee_Glare Analysis"
ghenv.Component.NickName = 'glareAnalysis'
ghenv.Component.Message = 'VER 0.0.42\nJAN_26_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import subprocess
import math

def runCmdAndGetTheResults(command, shellKey = True):
    p = subprocess.Popen(["cmd", command], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # p.kill()
    return out, err

def readGlareResults(glareRes):
    resultDict = {}
    try:
        result, possibleNotice = glareRes.split("Notice:")
    except:
        result = glareRes
        possibleNotice = None
        
    keys, values = result.strip().split(":")
    
    keys = keys.split(",")
    values = values[1:].split(" ")
    
    # remove empty strings
    for keyCount, key in enumerate(keys):
        resultDict[key.strip()] = values[keyCount].strip()
    
    return resultDict, possibleNotice

def main(HDRImagePath, taskPosition, taskPositionAngle):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        hb_DSPath = hb_folders["DSPath"]
        hb_DSCore = hb_folders["DSCorePath"]
        hb_DSLibPath = hb_folders["DSLibPath"]
        hb_EPPath = hb_folders["EPPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    # make sure the image is the result of an luminance analysis and not illuminance
    # I check for -i flag for rpict - This will work for all the Honeybee generatred renders
    # may or may not work for other cases I may want to change this to be a popup window
    # so the user can select between the options
    
    isLuminance = True
    with open(HDRImagePath, "r") as hdrFile:
        for lineCount, line in enumerate(hdrFile):
            if lineCount<10:
                if line.strip().lower().startswith("rpict"):
                    if line.find("-i") > -1:
                        isLuminance = False
                        break
            else:
                break
    
    if not isLuminance:
        warningMsg = "This image is the result of an illuminance analysis and not a luminance analysis which is needed for glare analysis!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warningMsg)
        return -1
    
    # http://www.ise.fraunhofer.de/en/downloads-englisch/software/evalglare_windows.zip/at_download/file
    notes = ""
    
    # try to find evalglare and check the version
    out, err = runCmdAndGetTheResults("/c evalglare -v")
    msg = "Failed to find evalglare.exe.\n" + \
              "Make sure you have evalglare 1.x.x installed at " + hb_RADPath +\
              "You can download evalglare from: \n" + \
              "http://www.ise.fraunhofer.de/en/downloads-englisch/software/evalglare_windows.zip/at_download/file"
    try:
        if out.split(" ")[0].strip() == "evalglare" and float(out.split(" ")[1].strip())> 1.0:
            msg = "\nThis component is using " + out.split("\n")[0] + " for glare analysis.\n"
            print msg
            notes += msg + "\n"
        else:
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
            return -1
    except:
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        return -1
        
    #task position in x and y coordinates
    taskP = False
    if taskPosition != None and taskPositionAngle != None:
        taskPX= taskPosition.X
        taskPY = taskPosition.Y
        taskPA = math.radians(taskPositionAngle)
        taskP = True
        
    
    if taskP and (taskPX > 1 or taskPY > 1):
        msg = "U and V valeus for taskPositionUV should be between 0 and 1." + \
                "%.3f"%taskPX + " and " + "%.3f"%taskPY + " are not acceptable input." + \
                "glare study will be run for the image and not the task plane"
        taskP = False
    elif taskP == True:
        msg = "Task position is provided.\n"
    elif taskP == False:
        msg = "No task position is provided. The result will be calculated for the whole scene.\n"
        
    print msg
    notes += msg + "\n"
    
    # check size and proportion of the image
    command = "/c getinfo -d " + HDRImagePath
    out, err = runCmdAndGetTheResults(command)
    
    # image size
    x = float(out.split(" ")[-1].strip())
    y = float(out.split(" ")[-3].strip())
    
    if x!=y:
        msg = "You need a fisheye HDR image for an accurate study.\nThis image seems not to  be a fisheye image which may produce inaccurate results.\n"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        notes += msg + "\n"
        
    # resize the image if needed
    if x > 800 or y > 800:
        msg = "Due to performance reasons of the evalglare code, the image should be smaller than 800x800 pixels. " + \
              "Honeybee is resizing the image...\n"
        print msg

        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        notes += msg + "\n"
        
        proportion = max(x,y)/800
        resizedImage = ".".join(HDRImagePath.split(".")[:-1]) + "_resized." + HDRImagePath.split(".")[-1]
        
        pflitLine = "/c pfilt -x/" + str(proportion) + " -y/" + str(proportion) + \
                  " " + HDRImagePath +" > " + resizedImage
        out, err = runCmdAndGetTheResults(pflitLine)
        
        x = x/proportion
        y = y/proportion
        HDRImagePath = resizedImage
    
    glareCheckImage = ".".join(HDRImagePath.split(".")[:-1]) + "_chkFile." + HDRImagePath.split(".")[-1]
    
    # run the analysis
    evalGlareLine = "/c evalglare -c " +  glareCheckImage + " " + HDRImagePath
    glareRes, err = runCmdAndGetTheResults(evalGlareLine)
    
    notes += "Results for the image:\n" + glareRes + "\n"
    
    # read the results
    totalGlareResultDict, possibleNotice = readGlareResults(glareRes)
    
    if possibleNotice!=None: notes += "Notice: " + possibleNotice + "\n"
    
    # if task position run one image to
    if taskP:
        
        glareTaskPCheckImage = ".".join(HDRImagePath.split(".")[:-1]) + "_TPChkFile." + HDRImagePath.split(".")[-1]
        
        xPixle = int(taskPX * x)
        yPixle = int(taskPY * y) # 0,0 coordinate for evalglare located at top left
        taskPA = math.radians(taskPositionAngle)
        
        TArguments = " ".join([str(xPixle), str(yPixle), "%.3f"%taskPA])
        
        evalGlareTaskPLine = "/c evalglare -c " +  glareTaskPCheckImage + " -T " + \
        TArguments + " " + HDRImagePath
        
        glareTaskRes, err = runCmdAndGetTheResults(evalGlareTaskPLine)
        notes += "Results for the task position:\n" + glareTaskRes + "\n"
        
        taskPGlareResultDict, possibleNotice = readGlareResults(glareTaskRes)
        
        if possibleNotice!=None: notes += "Notice: " + possibleNotice + "\n"
        
        return notes, glareCheckImage, totalGlareResultDict, glareTaskPCheckImage, taskPGlareResultDict
        
    else:
        return notes, glareCheckImage, totalGlareResultDict, None, None


if _HDRImagePath and _runIt:
    result = main(_HDRImagePath, taskPositionUV_, taskPositionAngle_)
    
    if result!= -1:
        readMe, glareCheckImage, totalGlareResultDict, imageWithTaskArea, taskPGlareResultDict = result
        
        if taskPGlareResultDict!=None:
            DGP = taskPGlareResultDict['dgp']
            DGI = taskPGlareResultDict['dgi']
        else:
            DGP = totalGlareResultDict['dgp']
            DGI = totalGlareResultDict['dgi']
else:
    readMe = "Provide a valid HDR Image and set _runIt to True."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning,readMe)