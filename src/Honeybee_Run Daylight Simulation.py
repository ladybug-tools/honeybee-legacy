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
export geometries to rad file, and run daylighting/energy simulation

-
Provided by Honeybee 0.0.64

    Args:
        north_: ...
        _HBObjects: List of Honeybee objects
        _analysisRecipe: An analysis recipe
        _writeRad: Write simulation files
        runRad_: Run the analysis. _writeRad should be also set to true. Set to 2 if you want the analysis to run in background. This option is useful for parametric runs when you don't want to see command shells.
        _numOfCPUs_: Number of CPUs to be used for the studies. This option doesn't work for image-based analysis
        _workingDir_: Working directory on your system. Default is set to C:\Ladybug
        _radFileName_: Input the project name as a string
        meshSettings_: Custom mesh setting. Use Grasshopper mesh setting components
        additionalRadFiles_: A list of fullpath to valid radiance files which will be added to the scene
        exportAirWalls_: Set to True if you want to export air walls as surfaces and False if you don't want air walls be exported.  The default is set to False.
        overwriteResults_: Set to False if you want the component create a copy of all the results. Default is True
        
    Returns:
        readMe!: ...
        analysisType: Type of the analysis (e.g. illuminance, luminance,...)
        resultsUnit: Unit of the results (e.g. lux, candela, wh/m2)
        radianceFile: Path to the Radiance geometry file
        HDRFiles: Path to the HDR image file
        gridBasedResultsFiles: Path to the results of grid based analysis (includes all the recipes except image-based and annual)
        annualResultFiles: Path to the result files of annual analysis
        testPts: Test points
        done: True if the study is over
"""

ghenv.Component.Name = "Honeybee_Run Daylight Simulation"
ghenv.Component.NickName = 'runDaylightAnalysis'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nDEC_21_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import os
import time
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


ghenv.Component.Params.Output[5].NickName = "resultFiles"
ghenv.Component.Params.Output[5].Name = "resultFiles"
resultFiles = []

ghenv.Component.Params.Output[3].NickName = "results"
ghenv.Component.Params.Output[3].Name = "results"
results = []

def main(north, originalHBObjects, analysisRecipe, runRad, numOfCPUs, workingDir, radFileName, meshParameters, waitingTime, additionalRadFiles, overwriteResults, exportAirWalls):
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
    hb_writeRAD = sc.sticky["honeybee_WriteRAD"](ghenv.Component)
    hb_writeRADAUX = sc.sticky["honeybee_WriteRADAUX"]()
    hb_materilaLib = sc.sticky["honeybee_materialLib"]
    hb_scheduleLib = sc.sticky["honeybee_ScheduleLib"]
    hb_writeDS = sc.sticky["honeybee_WriteDS"]()
    hb_folders = sc.sticky["honeybee_folders"]
    
    northAngle, northVector = lb_preparation.angle2north(north)
    if analysisRecipe:
        # read parameters
        hb_writeRADAUX.readAnalysisRecipe(analysisRecipe)
        
        # make sure Radiance and Daysim are installed correctly
        if analysisRecipe.type==2:
            # It's an annual analysis so Daysim needs to be installed
            DSPath = hb_folders["DSPath"]
            if DSPath=="":
                msg= "Honeybee cannot find a Daysim folder on your system.\n" + \
                    "Make sure you have Daysim installed on your system.\n" + \
                    "You won't be able to run annual daylight simulations without Daysim.\n" +\
                    "Check Honeybee_Honeybee component for more information."
                
                w = gh.GH_RuntimeMessageLevel.Warning
                print msg
                ghenv.Component.AddRuntimeMessage(w, msg)
                return -1
        else:
            # Radiance needs to be installed correctly
            RADPath = hb_folders["RADPath"]
            if RADPath=="":
                msg= "Honeybee cannot find a RADIANCE folder on your system.\n" + \
                    "Make sure you have RADIANCE installed on your system.\n" + \
                    "You won't be able to run annual daylight simulations without RADIANCE.\n" +\
                    "Check Honeybee_Honeybee component for more information."
                
                w = gh.GH_RuntimeMessageLevel.Warning
                print msg
                ghenv.Component.AddRuntimeMessage(w, msg)
                return -1                
            
        # double check and make sure that the parameters are set good enough
        # for grid based simulation
        hb_writeRADAUX.checkInputParametersForGridBasedAnalysis()
        analysisRecipe.radParameters =  hb_writeRADAUX.radParameters
        
    #conversionFac = lb_preparation.checkUnits()
    
    # check for folder
    # make working directory and/or clean the directory if needed
    subWorkingDir, radFileName = hb_writeRADAUX.prepareWorkingDir(workingDir, radFileName, overwriteResults)
    
    # export mesh
    hb_writeRADAUX.exportTestMesh(subWorkingDir, radFileName)
    
    # write analysis type to folder
    hb_writeRADAUX.exportTypeFile(subWorkingDir, radFileName, analysisRecipe)
    
    # copy the sky file to the local folder except for annual analysis
    radSkyFileName = hb_writeRADAUX.copySkyFile(subWorkingDir, radFileName)
    
    #Set a defalut of False for exporting Air Walls.
    if exportAirWalls == None: exportAirWalls = False
    
    ######################### WRITE RAD FILES ###########################
    # 2.1 write the geometry file
    ########################################################################
    ######################## GENERATE THE BASE RAD FILE ####################
    
    # I'm not sure how do I take care of file names for dynamic shadings
    # inside this function. For now I just leave it as it is and I will move
    # it to write DS later
    
    radFileFullName, materialFileName = \
        hb_writeRAD.writeRADAndMaterialFiles(originalHBObjects, subWorkingDir, \
                                             radFileName, analysisRecipe, \
                                             meshParameters, exportAirWalls)
    
    
    ######################## GENERATE POINT FILES #######################
    # test points should be generated if the study is grid based
    # except image-based simulation
    testPtsEachCPU, lenOfPts = hb_writeRAD.writeTestPtFile(subWorkingDir, radFileName, numOfCPUs, analysisRecipe)
    
    if len(testPtsEachCPU)!=0: # make sure it is a grid based analysis
        numOfCPUs = len(testPtsEachCPU) #in case number of CPUs are more than number of test points
    
    ######################## WRITE BATCH FILES #######################
    # if analysis type is annual this function will write hea files too
    initBatchFileName, batchFilesName, fileNames, pcompBatchFile, expectedResultFiles = \
                            hb_writeRAD.writeBatchFiles(subWorkingDir, radFileName, \
                            radSkyFileName, radFileFullName, materialFileName, \
                            numOfCPUs, testPtsEachCPU, lenOfPts, analysisRecipe, \
                            additionalRadFiles)
    
    if runRad:
        hb_writeRAD.runBatchFiles(initBatchFileName, batchFilesName, \
                                  fileNames, pcompBatchFile, waitingTime, runRad > 1)
        
        results = hb_writeRAD.collectResults(subWorkingDir, radFileName, \
                                numOfCPUs, analysisRecipe, expectedResultFiles)
        
        if analysisRecipe.type == 2:
            DSResultFilesAddress, annualGlareResults = results
            return radFileFullName, annualGlareResults, [], analysisRecipe.testPts, DSResultFilesAddress, [], subWorkingDir
            
        elif analysisRecipe.type == 0:
            HDRFileAddress = results
            return radFileFullName, [], [], [], [], HDRFileAddress, subWorkingDir
        else:
            RADResultFilesAddress = results
            return radFileFullName, [], RADResultFilesAddress, analysisRecipe.testPts, [], [], subWorkingDir
    else:
        # return name of the file
        if  analysisRecipe.type == 0: return radFileFullName, [], [], [], [], [], subWorkingDir
        else: return radFileFullName, [], [], analysisRecipe.testPts, [], [], subWorkingDir
                


if _writeRad == True and _analysisRecipe!=None and ((len(_HBObjects)!=0 and _HBObjects[0]!=None) or  additionalRadFiles_!=[]):
    north_ = 0 # place holder for now until I implement it to the code.
    
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
        
    
    
    result = main(north_, _HBObjects, _analysisRecipe, runRad_, numOfCPUs, \
                  _workingDir_, _radFileName_, meshSettings_, waitingTime, \
                  additionalRadFiles_, overwriteResults_, exportAirWalls_)
    
    if result!= -1:
        
        analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
        hb_readAnnualResultsAux = sc.sticky["honeybee_ReadAnnualResultsAux"]()
        
        # RADGeoFileAddress, radiationResult, RADResultFilesAddress, testPoints, DSResultFilesAddress, HDRFileAddress = result
        radGeoFile, annualGlareResults, gridBasedResultFiles, testPoints, annualResultFiles, HDRFiles, studyFolder = result
        
        testPts = DataTree[System.Object]()
        for i, ptList in enumerate(testPoints):
            p = GH_Path(i)
            testPts.AddRange(ptList, p)

        analysisType = _analysisRecipe.type
        
        if analysisType == 3 or analysisType == 4:
            analysisTypeKey = analysisType
        
        elif analysisType == 0 or analysisType == 1:
            analysisTypeKey = _analysisRecipe.simulationType
        
        elif analysisType == 2:
            # annual analysis
            analysisTypeKey = None
            
        try:
            analysisType, resultsUnit = analysisTypesDict[analysisTypeKey]
            
        except:
            analysisType, resultsUnit = "annual analysis", "var"
        
        resultsOutputName = analysisType.split(":")[-1].strip().replace(" ", "_") + "_values"
        filesOutputName = analysisType.split(":")[-1].strip().replace(" ", "_") + "_files"
        
        # check and rename result files based on analysis type
        if gridBasedResultFiles != []:
            resultFiles = gridBasedResultFiles
            #get the values for the results
            CalculateGridBasedDLAnalysisResults = sc.sticky["honeybee_GridBasedDLResults"]
            calculateResults = CalculateGridBasedDLAnalysisResults(resultFiles, int(analysisType.split(":")[0].strip()[0]))
            values = calculateResults.getResults()
            ghenv.Component.Params.Output[3].NickName = resultsOutputName
            ghenv.Component.Params.Output[3].Name = resultsOutputName
            
            # branch values based on test points
            # this is really ugly - should fix it later
            numOfPts = []
            numOfBranches = testPts.BranchCount
            for branchNum in range(numOfBranches):
                numOfPts.append(len(testPts.Branch(branchNum)))
            
            exec(resultsOutputName + "= DataTree[System.Object]()")
            totalPtsCount = 0
            try:
                for branchNum in range(numOfBranches):
                    p = GH_Path(branchNum)
                    for ptCount in range(numOfPts[branchNum]):
                        resValue = "%.2f"%values[totalPtsCount]
                        exec(resultsOutputName + ".Add(resValue, p)")
                        totalPtsCount += 1
                
            except:
                # Failed to load the results - check the error log
                errFile = os.path.join(studyFolder + "error.log")
                errMsg = ""
                with open(errFile, 'r') as err:
                    errLines = err.readlines()
                
                for line in errLines:
                    if line.strip() == "" or line.strip().startswith("***"): continue
                    errMsg += line + "\n"
                    
                errMsg = "Failed to read the results!\n" + errMsg
                print errMsg
                raise Exception(errMsg)
                
        elif annualResultFiles != []:
            # sort ill files
            resultFiles = hb_readAnnualResultsAux.sortIllFiles(annualResultFiles)
            
        elif HDRFiles != []:
            # check the error log
            errFile = os.path.join(studyFolder + "error.log")
            errMsg = ""
            warnMsg = ""
            with open(errFile, 'r') as err:
                errLines = err.readlines()
            
            for line in errLines:
                if line.strip() == "" or line.strip().startswith("***"): continue
                if line.strip().startswith("rpict: ") and line.strip().endswith("hours"): continue
                if line.strip().startswith("rpict: ") and line.strip().find("warning")!=-1:
                    warnMsg += line + "\n"
                    continue
                    
                errMsg += line + "\n"
            
            if errMsg != "": 
                print errMsg
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, errMsg)
                
            if warnMsg != "":
                print warnMsg
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warnMsg)
                
            resultFiles = HDRFiles
        
        if annualGlareResults!=[] and annualGlareResults!={}:
            ghenv.Component.Params.Output[3].NickName = "dgp_values"
            ghenv.Component.Params.Output[3].Name = "dgp_values"
            dgp_values = DataTree[System.Object]()
            keyCount = 0
            for key, item in annualGlareResults.items():
                p = GH_Path(keyCount)
                # add heading
                strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
                annualGlareHeading = [strToBeFound, "view: " + key, "Daylight Glare Probability", \
                            "%", 'Hourly', (1,1,1), (12, 31, 24)]
                if len(item)!=0:
                    item = annualGlareHeading + item
                dgp_values.AddRange(item, p)
                keyCount+=1
        
        done = True

        ghenv.Component.Params.Output[5].NickName = filesOutputName
        ghenv.Component.Params.Output[5].Name = filesOutputName
        exec(filesOutputName + "= resultFiles")
        time.sleep(.2)
