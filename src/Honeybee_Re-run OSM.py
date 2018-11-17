# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
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
This is a component for running a previoulsy-generated .osm file through EnergyPlus.

-
Provided by Ladybug 0.0.45
    
    Args:
        _osmFilePath: A full file path to an OpenStdio Model (.osm) file.
        _epwFileAddress: A full file path to an epw weather file.
        parallel_: Set to "True" to run multiple IDFs using multiple CPUs.  Note that this input is only relevant when you have plugged in a list of OSM file addresses.
        _runIt: Set to "True" to have the component generate an IDF file from the OSM file and run the IDF through through EnergyPlus.  Set to "False" to not run the file (this is the default).  You can also connect an integer for the following options:
            0 = Do Not Run OSM and IDF thrrough EnergyPlus
            1 = Run the OSM and IDF through EnergyPlus with a command prompt window that displays the progress of the simulation
            2 = Run the OSM and IDF through EnergyPlus in the background (without the command line popup window).
            3 = Generate an IDF from the OSM file but do not run it through EnergyPlus
    Returns:
        report: Report!
        idfFileAddress: The file path of the IDF file that has been generated on your machine. This file is only generated when you set "runSimulation_" to "True."
        resultFileAddress: The address of the EnergyPlus result file.
        eioFileAddress:  The file path of the EIO file that has been generated on your machine.  This file contains information about the sizes of all HVAC equipment from the simulation.  This file is only generated when you set "runSimulation_" to "True."
        rddFileAddress: The file path of the Result Data Dictionary (.rdd) file that is generated after running the file through EnergyPlus.  This file contains all possible outputs that can be requested from the EnergyPlus model.  Use the "Honeybee_Read Result Dictionary" to see what outputs can be requested.
"""

ghenv.Component.Name = "Honeybee_Re-run OSM"
ghenv.Component.NickName = 'Re-Run OSM'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nJUL_24_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import os
import scriptcontext as sc
import shutil
import Grasshopper.Kernel as gh
import time
import subprocess
import System.Threading.Tasks as tasks

def checkTheInputs(osmFileName, epwWeatherFile):
    w = gh.GH_RuntimeMessageLevel.Warning
    if not os.path.isfile(epwWeatherFile):
        msg = "EPW weather file does not exist in the specified location!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    if not epwWeatherFile.lower().endswith('.epw'):
        msg = "EPW weather file is not a valid epw!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if not os.path.isfile(osmFileName):
        msg = "OSM file does not exist in the specified location!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    if not osmFileName.lower().endswith('.osm'):
        msg = "OSM file is not a valid OSM!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    # Check for white space in file path.
    if ' ' in osmFileName:
        warning = "A white space was found in the .osm file path.  EnergyPlus cannot run out of directories with white spaces.\n" + \
        "Copy the .osm file to a directory without a white space and try again."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    return True

def writeBatchFile(workingDir, idfFileName, epwFileAddress, EPDirectory, runInBackground = False):
    workingDrive = workingDir[:2]
    if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
    else: shIdfFileName = idfFileName
    
    if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
    
    fullPath = workingDir + shIdfFileName
    folderName = workingDir.replace( (workingDrive + '\\'), '')
    batchStr = workingDrive + '\ncd\\' +  folderName + '\n"' + EPDirectory + \
            '\\Epl-run" ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'

    batchFileAddress = fullPath +'.bat'
    batchfile = open(batchFileAddress, 'w')
    batchfile.write(batchStr)
    batchfile.close()
    
    #execute the batch file
    if runInBackground:		
        runCmd(batchFileAddress)		
    else:
        os.system(batchFileAddress)
    
    return fullPath + ".csv"

def runCmd(batchFileAddress, shellKey = True):
    batchFileAddress.replace("\\", "/")
    p = subprocess.Popen(["cmd /c ", batchFileAddress], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)		
    out, err = p.communicate()

def getEPFolder(osmDirect):
    try:
        return sc.sticky["honeybee_folders"]["EPPath"]
    except:
        raise Exception("Failed to find EnergyPlus folder.")

def osmToidf(workingDir, projectName, osmPath):
    # create a new folder to run the analysis
    projectFolder =os.path.join(workingDir, projectName)
    
    try: os.mkdir(projectFolder)
    except: pass
    
    idfFolder = os.path.join(projectFolder)
    idfFilePath = ops.Path(os.path.join(projectFolder, "ModelToIdf", "in.idf"))
    
    # load the test model
    model = ops.Model().load(ops.Path(osmPath)).get()
    forwardTranslator = ops.EnergyPlusForwardTranslator()
    workspace = forwardTranslator.translateModel(model)
    
    # remove the current object
    tableStyleObjects = workspace.getObjectsByType(ops.IddObjectType("OutputControl_Table_Style"))
    for obj in tableStyleObjects: obj.remove()
    
    tableStyle = ops.IdfObject(ops.IddObjectType("OutputControl_Table_Style"))
    tableStyle.setString(0, "CommaAndHTML")
    workspace.addObject(tableStyle)
    
    workspace.save(idfFilePath, overwrite = True)
    
    return idfFolder, idfFilePath

def main(epwFile, osmFile, runEnergyPlus, openStudioLibFolder):
    # Preparation
    workingDir, fileName = os.path.split(osmFile)
    projectName = (".").join(fileName.split(".")[:-1])
    osmPath = ops.Path(osmFile)
    
    # create idf - I separated this job as putting them together
    # was making EnergyPlus to crash
    idfFolder, idfPath = osmToidf(workingDir, projectName, osmPath)
    print 'OSM > IDF: ' + str(idfPath)
    
    if runEnergyPlus < 3:
        osmDirect = '/'.join(openStudioLibFolder.split('/')[:-3])
        resultFile = writeBatchFile(idfFolder, "ModelToIdf\\in.idf", epwFile, getEPFolder(osmDirect), runEnergyPlus > 1)
        print '...'
        print 'RUNNING SIMULATION'
        print '...'
        
        try:
            errorFileFullName = str(idfPath).replace('.idf', '.err')
            errFile = open(errorFileFullName, 'r')
            for line in errFile:
                print line
                if "**  Fatal  **" in line:
                    warning = "The simulation has failed because of this fatal error: \n" + str(line)
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
                    resultFile = None
                elif "** Severe  **" in line and 'CheckControllerListOrder' not in line:
                    comment = "The simulation has not run correctly because of this severe error: \n" + str(line)
                    c = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(c, comment)
            errFile.close()
        except:
            pass
    else:
        resultFile = None
    
    eioFile = None
    rddFile = None
    try:
        eioFile = resultFile.replace('.csv', '.eio')
        rddFile = resultFile.replace('.csv', '.rdd')
    except:
        pass
    
    return workingDir, os.path.join(idfFolder, "ModelToIdf", "in.idf"), resultFile, eioFile, rddFile

def main_parallel(epwFile, osmFiles, runEnergyPlus, parallel, openStudioLibFolder):
    # placeholders.
    idfFileAddress = [None for x in osmFiles]
    resultFileAddress = [None for x in osmFiles]
    eioFileAddress = [None for x in osmFiles]
    rddFileAddress = [None for x in osmFiles]
    
    runInBackground = False
    if parallel == True:
        runInBackground = True
    elif runEnergyPlus > 1:
        runInBackground = True
    
    def runOS(i):
        fileCheck = checkTheInputs(osmFiles[i], epwFile)
        if fileCheck != -1:
            # Preparation
            workingDir, fileName = os.path.split(osmFiles[i])
            projectName = (".").join(fileName.split(".")[:-1])
            osmPath = ops.Path(osmFiles[i])
            # create idf
            idfFolder, idfPath = osmToidf(workingDir, projectName, osmPath)
            idfFileAddress[i] = idfFolder + "ModelToIdf\\in.idf"
            
            if runEnergyPlus < 3:
                osmDirect = '/'.join(openStudioLibFolder.split('/')[:-3])
                resultFile = writeBatchFile(idfFolder, "ModelToIdf\\in.idf", epwFile, getEPFolder(osmDirect), runInBackground)
                resultFileAddress[i] = resultFile
                eioFileAddress[i] = resultFile.replace('.csv', '.eio')
                rddFileAddress[i] = resultFile.replace('.csv', '.rdd')
    
    if parallel == True:
        tasks.Parallel.ForEach(range(len(osmFiles)), runOS)
    else:
        for x in range(len(osmFiles)):
            runOS(x)
    
    return None, idfFileAddress, resultFileAddress, eioFileAddress, rddFileAddress

#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
        hb_hvacProperties = sc.sticky['honeybee_hvacProperties']()
        hb_airDetail = sc.sticky["honeybee_hvacAirDetails"]
        hb_heatingDetail = sc.sticky["honeybee_hvacHeatingDetails"]
        hb_coolingDetail = sc.sticky["honeybee_hvacCoolingDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

if sc.sticky.has_key('honeybee_release'):
    if sc.sticky["honeybee_folders"]["OSLibPath"] != None:
        # openstudio is there
        openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
        
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
        
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg1 = "You do not have OpenStudio installed on Your System.\n" + \
            "You wont be able to use this component until you install it.\n" + \
            "Download the latest OpenStudio for Windows from:\n"
        msg2 = "https://www.openstudio.net/downloads"
        print msg1
        print msg2
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False


if initCheck == True and openStudioIsReady == True and _runIt > 0:
    if len(_osmFilePath) == 1:
        fileCheck = checkTheInputs(_osmFilePath[0], _epwFileAddress)
        if fileCheck != -1:
            result = main(_epwFileAddress, _osmFilePath[0], _runIt, openStudioLibFolder)
    else:
        result = main_parallel(_epwFileAddress, _osmFilePath, _runIt, parallel_, openStudioLibFolder)
    
    if result != -1:
        studyFolder, idfFileAddress, resultFileAddress, eioFileAddress, rddFileAddress = result