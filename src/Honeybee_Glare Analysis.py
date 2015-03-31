# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Glare Analysis

This component is using evalglare for glare calculations. Evalgalare is developed by J. Wienold at Fraunhofer ISE.
http://www.ise.fraunhofer.de/en/

Check this link for more information about glare analysis. Thanks to Christoph Reinhart, Shelby Doyle, J Alstan Jakubiec and Rashida Mogri.
http://web.mit.edu/tito_/www/Projects/Glare/GlareRecommendationsForPractice.html

-
Provided by Honeybee 0.0.56
    
    Args:
        _HDRImagePath: Path to an HDR image file
        taskPositionUV_: Task position in x and y coordinates
        taskPositionAngle_: Task position opening angle in degrees
        _runIt: Set to True to run the analysis
    Returns:
        readMe: ...
        glareCheckImage: Path to HDR image of the glare study
        DGP: Daylight glare probability. Imperceptible Glare [0.35 > DGP], Perceptible Glare [0.4 > DGP >= 0.35], Disturbing Glare [0.45 > DGP >= 0.4], Intolerable Glare [DGP >= 0.45]
        DGI: Daylight glare index
        imageWithTaskArea: Path to HDR image with task area marked with blue circle

"""

ghenv.Component.Name = "Honeybee_Glare Analysis"
ghenv.Component.NickName = 'glareAnalysis'
ghenv.Component.Message = 'VER 0.0.56\nFEB_02_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


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

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
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
    command = '/c getinfo -d ' + HDRImagePath
    out, err = runCmdAndGetTheResults(command)

    try:
        # image size
        x = float(out.split(" ")[-1].strip())
        y = float(out.split(" ")[-3].strip())
    except:
        msg = "Failed to find size of the picture. It will be set to 800.\n"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        notes += msg + "\n"
        x = y = 800
        
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
    glareNoTextImage = ".".join(HDRImagePath.split(".")[:-1]) + "_noText." + HDRImagePath.split(".")[-1]
    # run the analysis
    evalGlareLine = "/c evalglare -c " +  glareNoTextImage + " " + HDRImagePath
    glareRes, err = runCmdAndGetTheResults(evalGlareLine)
    
    if err.strip() == "error: no valid view specified":
        # since I use pcomp to merge images HDR image doesn't have HDR view information
        # adding default Honeybee view information for fish-eye camera
        evalGlareLine = "/c evalglare -vth -vv 180 -vh 180 -c " +  glareNoTextImage + " " + HDRImagePath
        glareRes, err = runCmdAndGetTheResults(evalGlareLine)
        
    
    notes += "Results for the image:\n" + glareRes + "\n"
    
    # read the results
    totalGlareResultDict, possibleNotice = readGlareResults(glareRes)
    
    # add the results to the picture
    DGP = totalGlareResultDict['dgp']
    DGI = totalGlareResultDict['dgi']
    
    textHeight = x / 25
    if textHeight < 10: textHeight = 10
    addNumbersLine = "/c " + hb_RADPath + r"\psign -h " + str(textHeight) + " -cb 0 0 0 -cf 1 1 1 DGP=" + str(DGP) + " | " + \
                     hb_RADPath + r"\pcompos " + glareNoTextImage + " 0 0 - " + str(textHeight/2) + " " + str(y) + " > " + glareCheckImage
    
    runCmdAndGetTheResults(addNumbersLine)
    
    if possibleNotice!=None: notes += "Notice: " + possibleNotice + "\n"
    
    # if task position run one image to
    if taskP:
        
        glareTaskPCheckImage = ".".join(HDRImagePath.split(".")[:-1]) + "_TPChkFile." + HDRImagePath.split(".")[-1]
        glareTaskPNoText = ".".join(HDRImagePath.split(".")[:-1]) + "_TPnoText." + HDRImagePath.split(".")[-1]
        
        
        xPixle = int(taskPX * x)
        yPixle = int(taskPY * y) # 0,0 coordinate for evalglare located at top left
        taskPA = math.radians(taskPositionAngle)
        
        TArguments = " ".join([str(xPixle), str(yPixle), "%.3f"%taskPA])
        
        evalGlareTaskPLine = "/c evalglare -c " +  glareTaskPNoText + " -T " + \
        TArguments + " " + HDRImagePath
        
        glareTaskRes, err = runCmdAndGetTheResults(evalGlareTaskPLine)
        notes += "Results for the task position:\n" + glareTaskRes + "\n"
        
        if err.strip() == "error: no valid view specified":
            # since I use pcomp to merge images HDR image doesn't have HDR view information
            # adding default Honeybee view information for fish-eye camera
            evalGlareTaskPLine = "/c evalglare -vth -vv 180 -vh 180 -c " +  glareTaskPNoText + " -T " + \
            TArguments + " " + HDRImagePath
            glareTaskRes, err = runCmdAndGetTheResults(evalGlareTaskPLine)        
        
        taskPGlareResultDict, possibleNotice = readGlareResults(glareTaskRes)
        
        # add the results to the picture
        DGP = taskPGlareResultDict['dgp']
        DGI = taskPGlareResultDict['dgi']
        
        addNumbersTLine = "/c " + hb_RADPath + r"\psign -h " + str(textHeight) + " -cb 0 0 0 -cf 1 1 1 DGP=" + str(DGP) + " | " + \
                     hb_RADPath + r"\pcompos " + glareTaskPNoText + " 0 0 - " + str(textHeight/2) + " " + str(y) + " > " + glareTaskPCheckImage
    
        runCmdAndGetTheResults(addNumbersTLine)
        
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
