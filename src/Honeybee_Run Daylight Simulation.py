# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
export geometries to rad file, and run daylighting/energy simulation

-
Provided by Honeybee 0.0.54

    Args:
        north_: ...
        _HBObjects: List of Honeybee objects
        _analysisRecipe: An analysis recipe
        _writeRad: Write simulation files
        runRad_: Run the analysis. _writeRad should be also set to true
        _numOfCPUs_: Number of CPUs to be used for the studies. This option doesn't work for image-based analysis
        _workingDir_: Working directory on your system. Default is set to C:\Ladybug
        _radFileName_: Input the project name as a string
        meshSettings_: Custom mesh setting. Use Grasshopper mesh setting components
        additionalRadFiles_: A list of fullpath to valid radiance files which will be added to the scene
        exportInteriorWalls_: Set to False if you don't want interior walls be exported
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
ghenv.Component.Message = 'VER 0.0.54\nSEP_10_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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


ghenv.Component.Params.Output[5].NickName = "resultFiles"
ghenv.Component.Params.Output[5].Name = "resultFiles"
resultFiles = []

ghenv.Component.Params.Output[3].NickName = "results"
ghenv.Component.Params.Output[3].Name = "results"
results = []

def main(north, originalHBObjects, analysisRecipe, runRad, numOfCPUs, workingDir,
         radFileName, meshParameters, waitingTime, additionalRadFiles, overwriteResults,
         exportInteriorWalls):
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release') or not sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    units = sc.doc.ModelUnitSystem
    if `units` != 'Rhino.UnitSystem.Meters':
        msg = "Default Radiance parameters are set based on meters. Make sure to modify the parameters for document units or change the units to Meters."
        ghenv.Component.AddRuntimeMessage(w, msg)
        
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
    
    northAngle, northVector = lb_preparation.angle2north(north)
    
    if analysisRecipe:
        # read parameters
        hb_writeRADAUX.readAnalysisRecipe(analysisRecipe)
        
        # double check and make sure that the parameters are set good enough
        # for grid based simulation
        hb_writeRADAUX.checkInputParametersForGridBasedAnalysis()
        
    #conversionFac = lb_preparation.checkUnits()
    
    # check for folder
    # make working directory and/or clean the directory if needed
    subWorkingDir, radFileName = hb_writeRADAUX.prepareWorkingDir(workingDir, radFileName, overwriteResults)
    
    # export mesh
    hb_writeRADAUX.exportTestMesh(subWorkingDir, radFileName)
    
    # write analysis type to folder
    hb_writeRADAUX.exportTypeFile(subWorkingDir, radFileName)
    
    # copy the sky file to the local folder except for annual analysis
    radSkyFileName = hb_writeRADAUX.copySkyFile(subWorkingDir, radFileName)
    
    
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
                                             meshParameters, exportInteriorWalls)
    
    
    ######################## GENERATE POINT FILES #######################
    # test points should be generated if the study is grid based
    # except image-based simulation
    testPtsEachCPU, lenOfPts = hb_writeRAD.writeTestPtFile(subWorkingDir, radFileName, numOfCPUs, analysisRecipe)
            
    ######################## WRITE BATCH FILES #######################
    # if analysis type is annual this function will write hea files too
    initBatchFileName, batchFilesName, fileNames, pcompBatchFile, expectedResultFiles = \
                            hb_writeRAD.writeBatchFiles(subWorkingDir, radFileName, \
                            radSkyFileName, radFileFullName, materialFileName, \
                            numOfCPUs, testPtsEachCPU, lenOfPts, analysisRecipe, \
                            additionalRadFiles)
    
    if runRad:
        hb_writeRAD.runBatchFiles(initBatchFileName, batchFilesName, \
                                  fileNames, pcompBatchFile, waitingTime)
        
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
                  additionalRadFiles_, overwriteResults_, exportInteriorWalls_)
    
    if result!= -1:
        
        analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
        
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
            exec(resultsOutputName + "= values")
            
        elif annualResultFiles != []:
            resultFiles = annualResultFiles
            
        elif HDRFiles != []:
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
