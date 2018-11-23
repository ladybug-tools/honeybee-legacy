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
Refine simulation for an existing Radiance scene (.oct file)

-
Provided by Honeybee 0.0.64

    Args:
        octFile_: A valid Radiance scene file
        _analysisRecipe: An analysis recipe
        runIt_: Run the analysis
        _numOfCPUs_: Number of CPUs to be used for the studies. This option doesn't work for image-based analysis
        _workingDir_: Working directory on your system. Default is set to C:\Ladybug
        _thisRunName: Name of this run so you can recognize it later
        additionalRadFiles_: A list of fullpath to valid radiance files which will be added to the scene
        
    Returns:
        resultFiles: Result files. You need to need other components based on the type of the analysis to calculate the results
        testPts: Test points if any
        done: True if the study is over
"""

ghenv.Component.Name = "Honeybee_Refine Daylight Simulation"
ghenv.Component.NickName = 'refineDaylightAnalysis'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import time
import System
import shutil
import Grasshopper.Kernel as gh
import math
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def main(octFile, analysisRecipe, numOfCPUs, thisRunName, runIt):
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    if not sc.sticky.has_key('ladybug_release') or not sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1

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
        return -1

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_writeRAD = sc.sticky["honeybee_WriteRAD"]()
    hb_writeRADAUX = sc.sticky["honeybee_WriteRADAUX"]()
    hb_materilaLib = sc.sticky["honeybee_materialLib"]
    hb_scheduleLib = sc.sticky["honeybee_ScheduleLib"]
    hb_writeDS = sc.sticky["honeybee_WriteDS"]()
    
    if not os.path.isfile(octFile):
        msg = "Can't find " + str(octFile)
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if not octFile.lower().endswith(".oct"):
        msg = "Bad .oct file: " + str(octFile)
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if analysisRecipe.type == 2:
        msg = "You cannot run an annual analysis with this component"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
        
    if analysisRecipe:
        # read parameters
        hb_writeRADAUX.readAnalysisRecipe(analysisRecipe)
        
        # double check and make sure that the parameters are set good enough
        # for grid based simulation
        hb_writeRADAUX.checkInputParametersForGridBasedAnalysis()
        
    #conversionFac = lb_preparation.checkUnits()
    
    # check for folder
    # make working directory and/or clean the directory if needed
    workingDir, octFileName = os.path.split(octFile)
    
    radFileName = (".").join(octFileName.split(".")[:-1])
    
    subWorkingDir = os.path.join(workingDir, thisRunName)
    
    # make sure subWorkingDir is created
    if not os.path.isdir(subWorkingDir):
        os.mkdir(subWorkingDir)
    
    # copy file to folder
    newOctFileName = os.path.join(subWorkingDir, radFileName + ".oct")
    try:
        hb_writeRADAUX.copyFile(octFile, newOctFileName)
    except:
        newOctFileName = octFile
        
    # copy amb file if any
    fileNames = os.listdir(workingDir)
    for fileName in fileNames:
        if fileName.lower().endswith(".amb"):
            ambFile = os.path.join(workingDir, fileName)
            newambFile = os.path.join(subWorkingDir, radFileName + ".amb")
            hb_writeRADAUX.copyFile(ambFile, newambFile)
            break
    
    # export mesh
    hb_writeRADAUX.exportTestMesh(subWorkingDir, radFileName)
    
    # write analysis type to folder
    hb_writeRADAUX.exportTypeFile(subWorkingDir, radFileName)
    
    # copy the sky file to the local folder except for annual analysis
    radSkyFileName = hb_writeRADAUX.copySkyFile(subWorkingDir, radFileName)
    
    
    ######################## GENERATE POINT FILES #######################
    # test points should be generated if the study is grid based
    # except image-based simulation
    testPtsEachCPU, lenOfPts = hb_writeRAD.writeTestPtFile(subWorkingDir, \
                                    radFileName, numOfCPUs, analysisRecipe)
            
    ######################## WRITE BATCH FILES #######################
    # if analysis type is annual this function will write hea files too
    initBatchFileName, batchFilesName, fileNames, pcompBatchFile, expectedResultFiles = \
                            hb_writeRAD.writeBatchFiles(subWorkingDir, radFileName, \
                            radSkyFileName, "", "", numOfCPUs, testPtsEachCPU, \
                            lenOfPts, analysisRecipe, \
                            [], newOctFileName, runOverture = False)
    
    if runIt:
        hb_writeRAD.runBatchFiles(initBatchFileName, batchFilesName, \
                                  fileNames, pcompBatchFile, waitingTime)
        
        results = hb_writeRAD.collectResults(subWorkingDir, radFileName, \
                                numOfCPUs, analysisRecipe, expectedResultFiles)
            
        if analysisRecipe.type == 0:
            HDRFileAddress = results
            return [], [], HDRFileAddress, subWorkingDir
        else:
            RADResultFilesAddress = results
            return RADResultFilesAddress, analysisRecipe.testPts, [], subWorkingDir
    else:
        # return name of the file
        if  analysisRecipe.type == 0: return [], [], [], subWorkingDir
        else: return [], analysisRecipe.testPoints, [], subWorkingDir
                


if _runIt == True and _analysisRecipe!=None and _octFile!=None and _thisRunName!=None:
    
    report = ""
    done = False
    waitingTime = 0.2 # waiting time between batch files in seconds
    try: numOfCPUs = int(_numOfCPUs_)
    except: numOfCPUs = 1
    
    # make sure it is not more than the number of available CPUs
    ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
    
    if numOfCPUs > ncpus:
        print "Sorry! But the number of available CPUs on your machine is " + str(ncpus) + "." + \
              "\nHoneybee set the number of CPUs to " + str(ncpus) + ".\n"
        numOfCPUs = ncpus
    
    result = main(_octFile, _analysisRecipe, numOfCPUs, _thisRunName, _runIt)
    
    if result!= -1:
        
        analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
        
        gridBasedResultFiles, testPoints, HDRFiles, studyFolder = result
        
        testPts = DataTree[System.Object]()
        for i, ptList in enumerate(testPoints):
            p = GH_Path(i)
            testPts.AddRange(ptList, p)
        
        analysisType = _analysisRecipe.type
        
        if analysisType == 3 or analysisType == 4:
            analysisTypeKey = analysisType
        
        elif analysisType == 0 or analysisType == 1:
            analysisTypeKey = _analysisRecipe.simulationType
        
        # check and rename result files based on analysis type
        if gridBasedResultFiles != []:
            resultFiles = gridBasedResultFiles
            #get the values for the results
            CalculateGridBasedDLAnalysisResults = sc.sticky["honeybee_GridBasedDLResults"]
            calculateResults = CalculateGridBasedDLAnalysisResults(resultFiles, int(analysisType))
            values = calculateResults.getResults()
            results = values
            
        elif HDRFiles != []:
            resultFiles = HDRFiles
        
        done = True


