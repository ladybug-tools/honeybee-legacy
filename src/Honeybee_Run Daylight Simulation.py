# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
export geometries to rad file, and run daylighting/energy simulation

-
Provided by Honeybee 0.0.53

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
ghenv.Component.Message = 'VER 0.0.54\nAUG_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import time
import System
import shutil
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import subprocess
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path



def isTheStudyOver(fileNames):
    while True:
        cmd = 'WMIC PROCESS get Commandline' #,Processid'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmdCount = 0
        for line in proc.stdout:
            if line.strip().startswith("cmd") and line.strip().endswith(".bat"):
                fileName = line.strip().split(" ")[-1].split("\\")[-1]
                # I should check the file names and make sure they are the right files
                if fileName in fileNames:
                    cmdCount += 1
        time.sleep(0.2)
        if cmdCount == 0:
            return
        #if cmdCount > 1: return

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
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        hb_writeRAD = sc.sticky["honeybee_WriteRAD"]()
        hb_writeRADAUX = sc.sticky["honeybee_WriteRADAUX"]()
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        hb_materilaLib = sc.sticky["honeybee_materialLib"]
        hb_scheduleLib = sc.sticky["honeybee_ScheduleLib"]
        hb_writeDS = sc.sticky["honeybee_WriteDS"]()
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        hb_dsParameters = sc.sticky["honeybee_DSParameters"]()
        hb_serializeObjects = sc.sticky["honeybee_SerializeObjects"]
        
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        hb_DSPath = hb_folders["DSPath"]
        hb_DSCore = hb_folders["DSCorePath"]
        hb_DSLibPath = hb_folders["DSLibPath"]
        hb_EPPath = hb_folders["EPPath"]
        
        northAngle, northVector = lb_preparation.angle2north(north)
        
        
        if analysisRecipe:
            #epwFileAddress, runRadiationAnalysis_GridPts, analysisPeriod, runRadiationAnalysis_Image, rhinoViewNames, runDaylightingSimulation, skyCondition, hour, day, month, runClimateBasedSimulation, dasysimParameters = analysesRecipe
            # print runRadiationAnalysis_GridPts
            # I think it is easier to keep read the parameters here instead of having a function
            # so it is going to be easier to read
            analysisType = analysisRecipe.type
            radParameters = analysisRecipe.radParameters
            backupImages = 0 # will change to 1 or 2 in case the user set it to another number for image-based analysis
            numOfIllFiles = 1
            if radParameters==None:
                quality = 0
                radParameters = {}
                print "Default values are set for RAD parameters"
                for key in hb_radParDict.keys():
                    #print key + " is set to " + str(hb_radParDict[key][quality])
                    radParameters[key] = hb_radParDict[key][quality]
            if analysisType == 0:
                print "Image-based simulation"
                radSkyFileName = analysisRecipe.skyFile
                rhinoViewNames = analysisRecipe.viewNames
                cameraType = analysisRecipe.cameraType
                imageSize = analysisRecipe.imageSize
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                sectionPlane = analysisRecipe.sectionPlane
                backupImages = analysisRecipe.backupImages
            
            elif analysisType == 1:
                print "Grid-based Radiance simulation"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            
            elif analysisType == 2:
                print "Annual climate-based analysis"
                epwFileAddress = analysisRecipe.weatherFile 
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                
                if analysisRecipe.DSParameters == None:
                    analysisRecipe.DSParameters = hb_dsParameters
                    
                runAnnualGlare = analysisRecipe.DSParameters.runAnnualGlare
                onlyAnnualGlare = analysisRecipe.DSParameters.onlyAnnualGlare
                annualGlareViews = analysisRecipe.DSParameters.RhinoViewsName
                outputUnits = analysisRecipe.DSParameters.outputUnits
                adaptiveZone = analysisRecipe.DSParameters.adaptiveZone
                dgp_imageSize = analysisRecipe.DSParameters.dgp_imageSize
                dynamicShadingRecipes = analysisRecipe.DSParameters.DShdR
                numOfIllFiles = analysisRecipe.DSParameters.numOfIll
                
                studyFolder = analysisRecipe.studyFolder
            
            elif analysisType == 3:
                print "Daylight factor"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            elif analysisType == 4:
                print "Vertical Sky Component"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            # double check and make sure that the parameters are set good enough
            # for grid based simulation
            if analysisType != 0:
                print "The component is checking ad, as, ar and aa values. " + \
                      "This is just to make sure that the results are accurate enough."
                
                if radParameters["_ad_"] < 1000:
                    radParameters["_ad_"] = 1000
                    print "-ad is set to 1000."
                
                if radParameters["_as_"] < 20:
                    radParameters["_as_"] = 20
                    print "-as is set to 20."
                
                if radParameters["_ar_"] < 300:
                    # setting up the ar to 300 is tricky but I'm pretty sure in many
                    # cases there will shadings involved.
                    radParameters["_ar_"] = 300
                    print "-ar is set to 300."
                
                if radParameters["_aa_"] > 0.1:
                    # the same here. I think it is good to let the user wait a little bit more
                    # but have a result that makes sense. If you are an exprienced user and don't
                    # like this feel free to remove the if condition. Keep in mind that I only
                    # apply this for grid based analysis, so the images can be rendered with any quality
                    radParameters["_aa_"] = 0.1
                    print "-aa is set to 0.1"
                    
                print "Good to go!"

        #conversionFac = lb_preparation.checkUnits()

        # check for folder
        # make working directory
        if workingDir:
            workingDir = lb_preparation.removeBlankLight(workingDir)
        else:
            workingDir = sc.sticky["Honeybee_DefaultFolder"]
        
        workingDir = lb_preparation.makeWorkingDir(workingDir)
        
        # make sure the directory has been created
        if workingDir == -1: return -1
        workingDrive = workingDir[0:1]
        
        ## check for the name of the file
        if radFileName == None: radFileName = 'unnamed'
        
        # make sure radfile name is a valid address
        keepcharacters = ('.','_')
        radFileName = "".join([c for c in radFileName if c.isalnum() or c in keepcharacters]).rstrip()
        
        # make new folder for each study
        subWorkingDir = lb_preparation.makeWorkingDir(workingDir + "\\" + radFileName + studyFolder).replace("\\\\", "\\")
        print 'Current working directory is set to: ', subWorkingDir
        
        try:
            if os.path.exists(subWorkingDir):
                if backupImages != 0:
                    # create the backup folder and copy the images to the folder
                    imageFolder = workingDir + "\\" + radFileName + "\\imagesBackup"
                    
                    if not os.path.exists(imageFolder): os.mkdir(imageFolder)
                    
                    # copy the files into the folder
                    imageExtensions = ["JPEG", "JPG", "GIF", "TIFF", "TIF", "HDR", "PIC"]
                    timeID = hb_writeRADAUX.getTime()
                    fileNames = os.listdir(subWorkingDir)
                    
                if backupImages == 1:
                    # keep all the files in the same folder
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            newFileName = (".").join(fileName.split(".")[:-1])
                            extension = fileName.split(".")[-1]
                            newFullName = newFileName + "_" + timeID + "." + extension
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder, newFullName) , True)
                    
                elif backupImages == 2:
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            if not os.path.exists(imageFolder + "\\" + timeID):
                                os.mkdir(imageFolder + "\\" + timeID)
                            # copy the files to image backup folder with data and time added
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder + "\\" + timeID, fileName) , True)
                
                if not overwriteResults:
                    fileNames = os.listdir(subWorkingDir)
                    
                    mainBackupFolder = subWorkingDir[:-1] + "_backup"
                    
                    counter = 0
                    backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    while os.path.isdir(backupFolder):
                        counter += 1
                        backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    os.mkdir(backupFolder)
                    
                    for fileName in fileNames:
                        try:
                            # copy the files to image backup folder with data and time added
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(backupFolder, fileName) , True)                    
                        except:
                            pass
                    
                    print "Results of the previous study are copied to " + backupFolder
                    
                lb_preparation.nukedir(subWorkingDir, rmdir = False)
                
        except Exception, e:
            print 'Failed to remove the old directory.'
            print `e`
        
        # try to write mesh file if any
        if analysisType != 0 and analysisRecipe.testMesh !=[]:
            meshFilePath = os.path.join(subWorkingDir, radFileName + ".msh")
            serializer = hb_serializeObjects(meshFilePath, analysisRecipe.testMesh)
            serializer.saveToFile()
        
        # write analysis type to folder
        typeFile = os.path.join(subWorkingDir, radFileName + ".typ")
        with open(typeFile, "w") as typf:
            typf.write(str(analysisRecipe.type))
        
        # sky and material file
        # copy the sky file to the local folder
        if analysisType != 2:
            skyTempName = radSkyFileName.split("\\")[-1]
            skyName = skyTempName.split("/")[-1]
            
            hb_writeRADAUX.copyFile(radSkyFileName, subWorkingDir + "\\" + skyName, True)
            radSkyFileName = os.path.join(subWorkingDir, skyName)
        
        radFileFullName = subWorkingDir + "\\" + radFileName + '.rad'
        
        ######################### WRITE RAD FILES ###########################
        
        # 2.1 write the geometry file
        ########################################################################
        ######################## GENERATE THE BASE RAD FILE ####################
        
        # call the objects from the lib
        IESObjects = {}
        IESCount = 0
        
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBObjects = hb_hive.callFromHoneybeeHive(originalHBObjects)
        
        geoRadFile = open(radFileFullName, 'w')
        geoRadFile.write("#GENERATED BY HONEYBEE\n")
        customRADMat = {} # dictionary to collect the custom material names
        customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
        if len(HBObjects)!=0:
            for objCount, HBObj in enumerate(HBObjects):
                # check if the object is zone or a surface (?)
                if HBObj.objectType == "HBZone":
                    if HBObj.hasNonPlanarSrf or HBObj.hasInternalEdge:
                        HBObj.prepareNonPlanarZone(meshParameters)
                    
                    for srf in HBObj.surfaces:
                        # check if an interior wall
                        if not exportInteriorWalls and hb_writeRADAUX.isSrfInterior(srf):
                            continue
                            
                        # collect the custom material informations
                        if srf.RadMaterial!=None:
                            customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(srf, customRADMat, customMixFunRadMat)
                        # write the surfaces
                        if srf.isPlanar and len(srf.childSrfs)<2:
                            geoRadFile.write(hb_writeRAD.RADSurface(srf))
                        else:
                            geoRadFile.write(hb_writeRAD.RADNonPlanarSurface(srf))
                            if srf.hasChild:
                                # collect the custom material informations
                                for childSrf in srf.childSrfs:
                                    if childSrf.RadMaterial!=None:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                geoRadFile.write(hb_writeRAD.RADNonPlanarChildSurface(srf))
                
                elif HBObj.objectType == "HBSurface":
                    
                    # I should wrap this in a function as I'm using it multiple times with minor changes
                    # collect the custom material informations
                    if HBObj.RadMaterial!=None:
                        try:
                            customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
                        except:
                            msg = HBObj.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                            print msg
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return -1
                            
                            
                    if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                        geoRadFile.write(hb_writeRAD.RADSurface(HBObj))
                    else:
                        geoRadFile.write(hb_writeRAD.RADNonPlanarSurface(HBObj))
                        if not HBObj.isChild and HBObj.hasChild:
                            # collect the custom material informations
                            for childSrf in HBObj.childSrfs:
                                if childSrf.RadMaterial!=None:
                                    try:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                    except:
                                        msg = childSrf.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                                        print msg
                                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                                        return -1
                            geoRadFile.write(hb_writeRAD.RADNonPlanarChildSurface(HBObj))
                
                elif HBObj.objectType == "HBIES":
                    IESCount += 1
                    IESObjcIsFine = True
                    # check if the object has been move or scaled
                    if HBObj.checkIfScaledOrRotated(originalHBObjects[objCount]):
                        IESObjcIsFine = False
                        msg = "IES luminaire " + HBObj.name + " is scaled or rotated" + \
                              " and cannot be added to the scene."
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    
                    # check if the material name is already exist
                    if HBObj.name in customRADMat.keys():
                        IESObjcIsFine = False
                        msg = "IES luminaire " + HBObj.name + " cannot be added to the scene.\n" + \
                                  "A material with the same name already exist."
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    
                    # if it is all fine then write the geometry
                    if IESObjcIsFine:
                        geoRadFile.write(hb_writeRAD.getIESSurfaceStr(originalHBObjects[objCount], HBObj.name, IESCount))
                        # downlight_light polygon downlight.d
                        # add to IES Objects list so I can add the materials to the list later
                        if HBObj.name not in IESObjects.keys():
                            IESObjects[HBObj.name] = HBObj
                    
        geoRadFile.close()
        
        ########################################################################
        ######################## GENERATE THE BASE RAD FILE ####################
        materialFileName = subWorkingDir + "\\material_" + radFileName + '.rad'
        # This part should be fully replaced with the new method where I generate the materials from the 
        
        # 0.1 material string
        matStr =  "# start of generic materials definition(s)\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Context_Material') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Interior_Ceiling') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Interior_Floor') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Exterior_Floor') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Exterior_Window') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Interior_Window') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Exterior_Roof') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Exterior_Wall') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('Interior_Wall') + "\n" + \
            "# end of generic materials definition(s)\n"
    
        with open(materialFileName, 'w') as matFile:
            matFile.write(matStr)
            matFile.write("\n# start of material(s) specific to this study (if any)\n")
            for radMatName in customRADMat.keys():
                matFile.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                
                # check if the material is is trans
                if hb_RADMaterialAUX.getRADMaterialType(radMatName) == "trans":
                    
                    # get the st value
                    st = hb_RADMaterialAUX.getSTForTransMaterials(radMatName)
                    if st < radParameters["_st_"]:
                        print "Found a trans material... " + \
                              "Resetting st parameter from " + str(radParameters["_st_"]) + " to " + str(st)
                        radParameters["_st_"] = st
                    
            # write mixedfun if any
            for radMatName in customMixFunRadMat.keys():
                matFile.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
            
            # write IES material if any
            if len(IESObjects.keys())!= 0:
                for IESName in IESObjects.keys():
                    IESObj = IESObjects[IESName]
                    # write material file
                    matFile.write(IESObj.materialStr)
                    
                    # add dat file to folder
                    datFileName = subWorkingDir + "\\" + IESName + '.dat'
                    with open(datFileName, "w") as outDat:
                        outDat.write(IESObj.datFile)
                    
            matFile.write("# end of material(s) specific to this study (if any)\n")
        
        
        # add shading files for daysim advanced dynamic shadings
        dynamicCounter = 0
        if analysisRecipe.type == 2 and len(dynamicShadingRecipes)!=0:
            customRADMat = {} # dictionary to collect the custom material names
            customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
            
            for shadingRecipe in dynamicShadingRecipes:
                if shadingRecipe.type == 2:
                    
                    groupName = shadingRecipe.name
                    
                    dynamicCounter+=1
                    for stateCount, shadingState in enumerate(shadingRecipe.shadingStates):
                        
                        fileName = groupName + "_state_" + str(stateCount + 1) + ".rad"
                        
                        try:
                            radStr = ""
                            
                            shdHBObjects = hb_hive.callFromHoneybeeHive(shadingState.shdHBObjects)
                            
                            for HBObj in shdHBObjects:
                                # collect the custom material informations
                                if HBObj.RadMaterial!=None:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
            
                                if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                                    radStr += hb_writeRAD.RADSurface(HBObj)
                                else:
                                    radStr += hb_writeRAD.RADNonPlanarSurface(HBObj)
                                    if not HBObj.isChild and HBObj.hasChild:
                                        # collect the custom material informations
                                        for childSrf in HBObj.childSrfs:
                                            if childSrf.RadMaterial!=None:
                                                customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                        radStr += hb_writeRAD.RADNonPlanarChildSurface(HBObj)
                            
                            
                            # write the shading file
                            with open(subWorkingDir + "\\" + fileName, "w") as radInf:
                                radInf.write(matStr)
                                radInf.write("# material(s) specific to this study\n")
                                for radMatName in customRADMat.keys():
                                    radInf.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                # write mixedfun if any
                                for radMatName in customMixFunRadMat.keys():
                                    radInf.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                radInf.write(radStr)
                                
                        except Exception, e:
                            # print `e`
                            # None object so just create an empty file
                            with open(subWorkingDir + "\\" + fileName , "w") as radInf:
                                radInf.write("#empty shading file")
                            pass
                            
        ######################## GENERATE POINT FILES #######################
        # test points should be generated if the study is grid based
        # except image-based simulation
        if analysisType != 0:
            # write a pattern file which I can use later to re-branch the points
            ptnFileName = radFileFullName.replace('.rad','.ptn')
            with open(ptnFileName, "w") as ptnFile:
                for ptList in testPoints:
                    ptnFile.write(str(len(ptList)) + ", ")
            
            # faltten the test points
            flattenTestPoints = lb_preparation.flattenList(testPoints)
            flattenPtsNormals = lb_preparation.flattenList(ptsNormals)
            numOfPoints = len(flattenTestPoints)
        
            if numOfCPUs > numOfPoints: numOfCPUs = numOfCPUs
        
            if numOfCPUs > 1: ptsEachCpu = int(numOfPoints/(numOfCPUs))
            else: ptsEachCpu = numOfPoints
        
            lenOfPts = []
            testPtsEachCPU = []
            
            for cpuCount in range(numOfCPUs):
                # write pts file
                ptsForThisCPU = []
                ptsFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.pts')
                ptsFile = open(ptsFileName, "w")
                if cpuCount + 1 != numOfCPUs:
                    for ptCount in range(cpuCount * ptsEachCpu, (cpuCount + 1) * ptsEachCpu):
                        ptsFile.write(hb_writeRADAUX.testPtsStr(flattenTestPoints[ptCount], flattenPtsNormals[ptCount]))
                        ptsForThisCPU.append(flattenTestPoints[ptCount])
                    lenOfPts.append(ptsEachCpu)
                    
                else:
                    for ptCount in range(cpuCount * ptsEachCpu, numOfPoints):
                        ptsFile.write(hb_writeRADAUX.testPtsStr(flattenTestPoints[ptCount], flattenPtsNormals[ptCount]))
                        ptsForThisCPU.append(flattenTestPoints[ptCount])
                    lenOfPts.append(numOfPoints - (cpuCount * ptsEachCpu))
                
                ptsFile.close()
                
                testPtsEachCPU.append(ptsForThisCPU)
                
        ######################## WRITE ANNUAL SIMULATION - DAYSIM #######################
        if analysisRecipe.type == 2:
            # check for Daysim to be installed on the system and available in the path
            #if not os.path.isdir("c:/DAYSIM"):
            #    print "You need to install DAYSIM at C:/DAYSIM"
            #    return -1
            
            DSResultFilesAddress = []
            
            # write the init batch files
            
            # location string
            locationStr, locName = hb_writeDS.DSLocationStr(hb_writeRADAUX, lb_preparation, epwFileAddress)
            newLocName = lb_preparation.removeBlankLight(locName)
            
            # copy .epw file to sub-directory
            lb_preparation.copyFile(epwFileAddress, subWorkingDir + "\\" + newLocName + '.epw')
            #lb_preparation.copyFile(epwFileAddress, subWorkingDir + "\\" + locName + '.epw')
            
            pathStr = "SET RAYPATH=.;" + hb_RADLibPath + ";" + hb_DSPath + ";" + hb_DSLibPath + ";\nPATH=" + hb_RADPath + ";" + hb_DSPath + ";" + hb_DSLibPath + ";$PATH\n"
            heaFileName = radFileFullName.replace('.rad', '_0.hea')
            initBatchFileName = radFileFullName.replace('.rad', '_InitDS.bat')
            initBatchFile = open(initBatchFileName, "w")
            initBatchFile.write(pathStr)
            initBatchStr =  'C:\n' + \
                            'CD ' + hb_DSPath + '\n' + \
                            'epw2wea  ' + subWorkingDir + "\\" + lb_preparation.removeBlankLight(locName) + '.epw ' + subWorkingDir + "\\" +  lb_preparation.removeBlankLight(locName) + '.wea\n' + \
                            ':: 1. Generate Daysim version of Radiance Files\n' + \
                            'radfiles2daysim ' + heaFileName + ' -m -g\n'
                            
            if runAnnualGlare:
                initBatchStr += \
                ':: 2. Generate Values for annual glare\n' + \
                'gen_dgp_profile ' + heaFileName
                
            initBatchFile.write(initBatchStr)
            initBatchFile.close()
            
            fileNames = []
            # annual glare only needs one headeing file and will run on a single cpu
            if runAnnualGlare and onlyAnnualGlare:
                numOfCPUs = 1
                
            # write the rest of the files
            for cpuCount in range(numOfCPUs):
                heaFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.hea')
                heaFile = open(heaFileName, "w")
                projectName =  radFileName
                
                tempDirName = subWorkingDir + '\\tmp_' + `cpuCount`
                heaFile.write(hb_writeDS.DSHeadingStr(projectName, subWorkingDir, tempDirName, hb_DSCore , cpuCount))
                
                # delete the files in the old temp folder
                # if os.path.exists(tempDirName): lb_preparation.nukedir(tempDirName,rmdir = False)
                tempWorkingDir = lb_preparation.makeWorkingDir(tempDirName)
                
                heaFile.write(locationStr)
                
                heaFile.write(hb_writeDS.DSAnalysisUnits(outputUnits, lenOfPts[cpuCount]))
                
                # write view for annual glare if any
                fakeViewFileName = subWorkingDir + '\\' + projectName + '_' + 'annualGlareView.vf'
                vfFile = open(fakeViewFileName, "w")
                vfFile.write('')
                for view in annualGlareViews:
                    viewLine = hb_writeRADAUX.exportView(view, radParameters, 1, [dgp_imageSize, dgp_imageSize])
                    # I'm not sure why Daysim view file needs rview Perspective at the start line
                    vfFile.write("rview Perspective " + viewLine + "\n")
                vfFile.close()
                
                # building string
                heaFile.write(hb_writeDS.DSBldgStr(projectName, materialFileName, radFileFullName, adaptiveZone, dgp_imageSize, dgp_imageSize, cpuCount))
                
                # radiance parameters string
                heaFile.write(hb_writeDS.DSRADStr(radParameters))
                
                # dynamic simulaion options
                # should be developed later!
                # I don't care about the occupancy since I read the result with a custom component
                # copy the sch to the folder
                #try: lb_preparation.copyFile(hb_DSCore + '\\occ\\weekdays9to5withDST.60min.occ.csv', subWorkingDir + '\\weekdays9to5withDST.60min.occ.csv')
                #except: pass
                
                heaFile.write(hb_writeDS.DSDynamicSimStr(dynamicShadingRecipes, projectName, subWorkingDir, testPtsEachCPU[cpuCount], cpuCount))
                
                # heaFile.write(hb_writeDS.resultStr(projectName, cpuCount))
                heaFile.close()
                
                if not(runAnnualGlare and onlyAnnualGlare):
                    # ill files
                    DSResultFilesAddress.append(radFileFullName.replace('.rad', '_' + `cpuCount` + '.ill'))
                    # 3.  write the batch file
                    DSBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_DS.bat')
                    DSBatchFile = open(DSBatchFileName, "w")
                    
                    fileNames.append(DSBatchFileName.split("\\")[-1])
                    
                    heaFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.hea')
                    
                    #SET PATH = " + subWorkingDir + "\n" + workingDrive +"\n"
                    DSBatchFile.write(pathStr)
                    
                    DSBatchStr = ':: Calculate Daylight Coefficient File (*.dc)\n' + \
                                'gen_dc ' + heaFileName + ' -dif\n' + \
                                'gen_dc ' + heaFileName + ' -dir\n' + \
                                'gen_dc ' + heaFileName + ' -paste\n' + \
                                '\n' + \
                                ':: Generate Illuminance Files (*.ill)\n' + \
                                'ds_illum  ' + heaFileName + '\n'
                    
                    DSBatchFile.write(DSBatchStr)
                                
                    DSBatchFile.close()
                
            if runRad:
                os.system(initBatchFileName)
                time.sleep(waitingTime)
                if not(runAnnualGlare and onlyAnnualGlare):
                    for cpuCount in range(numOfCPUs):
                        # running batch file in background
                        DSBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_DS.bat')
                        # print DSBatchFileName
                        p = subprocess.Popen(r'start cmd /c ' + DSBatchFileName , shell=True)
                        time.sleep(waitingTime)
                        #p.wait()
                        #os.system(DSBatchFileName)
                    # read the number of .ill files
                    # and the number of .dc files
                    if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                    startTime = time.time()
                    # print fileNames
                    isTheStudyOver(fileNames)
                    # check if the results are available
                    files = os.listdir(subWorkingDir)
                    numIll = 0
                    numDc = 0
                    for file in files:
                        if file.EndsWith('ill'): numIll+=1
                        elif file.EndsWith('dc'): numDc+=1
                    if numIll!= numOfCPUs * numOfIllFiles or  numDc!= numOfCPUs * numOfIllFiles:
                        print "Can't find the results for the study"
                        DSResultFilesAddress = []
                
                annualGlareResults = []
                dgpFile = radFileFullName.replace('.rad', '_0.dgp')
                if runAnnualGlare and os.path.isfile(dgpFile):
                    # put the heading together
                    strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
                    annualGlareResults = [strToBeFound, "", "Daylight Glare Probability", \
                                "%", 'Hourly', (1,1,1), (12, 31, 24)]
                                
                    with open(dgpFile, "r") as dgpRes:
                        for line in dgpRes:
                            try: annualGlareResults.append(line.split(" ")[-1].strip())
                            except: pass
                return radFileFullName, annualGlareResults, [], testPoints, DSResultFilesAddress, [], subWorkingDir
            else:
                return radFileFullName, [], [], testPoints, [], [], subWorkingDir
                
        ######################## NOT ANNUAL SIMULATION #######################
        
        elif analysisRecipe.type != 2:
            #if not os.path.isdir("c:/RADIANCE"):
            #    print "You need to install RADIANCE at C:/Radiance"
            #    return -1
            
            # 3.  write the batch file
            if analysisRecipe.type == 0:
                # image based
                initBatchFileName = radFileFullName.replace('.rad', '_IMGInit.bat')
            else:
                # not annual and not image based
                initBatchFileName = radFileFullName.replace('.rad', '_RADInit.bat')
            
            with open(initBatchFileName, "w") as batchFile:
            
                # write the path string (I should check radiance to be installed on the system
                pathStr = "SET RAYPATH=.;" + hb_RADLibPath + "\nPATH=" + hb_RADPath + ";$PATH\n"
                batchFile.write(pathStr)
                
                batchFile.write("c:\n")
                batchFile.write("cd " + subWorkingDir + "\n")
                
                # write OCT file
                # 3.2. oconv line
                OCTFileName = radFileName + '_RAD'
                
                sceneRadFiles = [materialFileName, radSkyFileName, radFileFullName]
                if additionalRadFiles:
                    sceneRadFiles += additionalRadFiles
                    
                OCTLine = hb_writeRADAUX.oconvLine(OCTFileName, sceneRadFiles)
                batchFile.write(OCTLine)
                
                # add overture line in case it is an image-based analysis
                view = sc.doc.Views.ActiveView.ActiveViewport.Name
                
                viewLine = hb_writeRADAUX.exportView(view, radParameters, cameraType, imageSize = [64, 64])
                        
                # write rpict lines
                overtureLine = hb_writeRADAUX.overtureLine(viewLine, OCTFileName, view, radParameters, int(simulationType))
                batchFile.write(overtureLine)
                
            if analysisRecipe.type == 0:
                # write view files
                if len(rhinoViewNames)==0:
                    rhinoViewNames = [sc.doc.Views.ActiveView.ActiveViewport.Name]
                # print rhinoViewNames
                
                #recalculate vh and vv
                nXDiv = int(math.sqrt(numOfCPUs))

                while numOfCPUs%nXDiv !=0 and nXDiv < numOfCPUs:
                    nXDiv += 1
                
                nYDiv = numOfCPUs/nXDiv

                fileNames = []
                HDRPieces = {}
                HDRFileAddress = []
                for cpuCount in range(numOfCPUs):
                    # create a batch file
                    batchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_IMG.bat')
                    fileNames.append(batchFileName.split("\\")[-1])
                    batchFile = open(batchFileName, "w")
                    # write path files
                    batchFile.write(pathStr)
                    batchFile.write("c:\n")
                    batchFile.write("cd " + subWorkingDir + "\n")
                    
                    # calculate vs and vl for thi cpu
                    try: vs = (((cpuCount%nXDiv)/(nXDiv-1)) - 0.5) * (nXDiv - 1)
                    except: vs = 0
                        
                    try: vl = ((int(cpuCount/nXDiv)/(nYDiv-1)) - 0.5) * (nYDiv - 1)
                    except: vl = 0
                    
                    # print vs, vl
                    for view in rhinoViewNames:
                        
                        view = lb_preparation.removeBlank(view)
                        
                        if cpuCount == 0:
                            HDRFileAddress.append(subWorkingDir + "\\" + OCTFileName + "_" + view + ".HDR")
                            HDRPieces[OCTFileName + "_" + view + ".HDR"] = []
                        
                        # collect name of the pieces of the picture
                        HDRPieces[OCTFileName + "_" + view + ".HDR"].append(OCTFileName + "_" + view + "_" + `cpuCount` + ".HDR")
                        
                        viewLine = hb_writeRADAUX.exportView(view, radParameters, cameraType, imageSize, sectionPlane, nXDiv, nYDiv, vs, vl)
                        
                        # write rpict lines
                        RPICTLines = hb_writeRADAUX.rpictLine(viewLine, OCTFileName, view, radParameters, int(simulationType), cpuCount)
                        batchFile.write(RPICTLines)                    
                        
                    # close the file
                    batchFile.close()
                
            else:
                fileNames = []
                for cpuCount in range(numOfCPUs):
                    # create a batch file
                    batchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_RAD.bat')
                    fileNames.append(batchFileName.split("\\")[-1])
                    batchFile = open(batchFileName, "w")
                    # write path files
                    batchFile.write(pathStr)
                    batchFile.write("c:\n")
                    batchFile.write("cd " + subWorkingDir + "\n")
                    
                    # 3.4. add rtrace lin
                    RTRACELine = hb_writeRADAUX.rtraceLine(radFileName, OCTFileName, radParameters, int(simulationType), cpuCount)
                    batchFile.write(RTRACELine)
                    
                    # close the file
                    batchFile.close()
            if runRad:
                # run batch file and return address  and the result
                if  analysisRecipe.type == 0:
                    os.system(initBatchFileName)
                    
                    for cpuCount in range(numOfCPUs):
                        # running batch file in background
                        IMGBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_IMG.bat')
                        # print DSBatchFileName
                        p = subprocess.Popen(r'start cmd /c ' + IMGBatchFileName , shell=True)
                        time.sleep(waitingTime)
                        
                    if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                    
                    startTime = time.time()
                    isTheStudyOver(fileNames)
                    
                    # merge images into a single HDR
                    pcompFileName = radFileFullName.replace('.rad', '_PCOMP.bat')
                    
                    with open(pcompFileName, "w") as pcompFile:
                        # write path files
                        pcompFile.write(pathStr)
                        pcompFile.write("c:\n")
                        pcompFile.write("cd " + subWorkingDir + "\n")
                        
                        for mergedName, pieces in HDRPieces.items():
                            
                            pcomposLine = "pcompos -a " + `nXDiv` + " "
                            # pieces.reverse()
                            for piece in pieces:
                                pcomposLine += piece + " "
                            pcomposLine += " > " + mergedName + "\n"
                            
                            pcompFile.write(pcomposLine)
                    
                    subprocess.Popen(r'start cmd /c ' + pcompFileName , shell=True)
                    
                    return radFileFullName, [], [], [], [], HDRFileAddress, subWorkingDir
                
                else:
                    RADResultFilesAddress = []
                    os.system(initBatchFileName)
                    for cpuCount in range(numOfCPUs):
                        # running batch file in background
                        RADBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_RAD.bat')
                        # print DSBatchFileName
                        p = subprocess.Popen(r'start cmd /c ' + RADBatchFileName , shell=True)
                        
                        RADResultFilesAddress.append(radFileFullName.replace('.rad', '_' + `cpuCount` + '.res'))
                        time.sleep(waitingTime)
                        
                    if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                    
                    startTime = time.time()
                    isTheStudyOver(fileNames)
                    
                    numRes = 0
                    files = os.listdir(subWorkingDir)
                    for file in files:
                        if file.EndsWith('res'): numRes+=1
                    if numRes != numOfIllFiles * numOfCPUs:
                        print "Cannot find the results of the study"
                        RADResultFilesAddress = []
                    time.sleep(1)
                    # run all the batch files
                    
                    return radFileFullName, [], RADResultFilesAddress, testPoints, [], [], subWorkingDir
                
            else:
                # return name of the file
                if  analysisRecipe.type == 0: return radFileFullName, [], [], [], [], [], subWorkingDir
                else: return radFileFullName, [], [], testPoints, [], [], subWorkingDir
                
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1


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
        
        if annualGlareResults!=[]:
            ghenv.Component.Params.Output[3].NickName = "dgp_values"
            ghenv.Component.Params.Output[3].Name = "dgp_values"
            dgp_values = annualGlareResults
        
        done = True

        ghenv.Component.Params.Output[5].NickName = filesOutputName
        ghenv.Component.Params.Output[5].Name = filesOutputName
        exec(filesOutputName + "= resultFiles")
        time.sleep(.2)
