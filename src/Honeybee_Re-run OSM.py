# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
        _osmFilePath: A file path of the an OpemStdio file
        _epwFileAddress: Address to epw weather file.
        _runIt: Set to "True" to have the component generate an IDF file from the OSM file and run the IDF through through EnergyPlus.  Set to "False" to not run the file (this is the default).  You can also connect an integer for the following options:
            0 = Do Not Run OSM and IDF thrrough EnergyPlus
            1 = Run the OSM and IDF through EnergyPlus with a command prompt window that displays the progress of the simulation
            2 = Run the OSM and IDF through EnergyPlus in the background (without the command line popup window).
            3 = Generate an IDF from the OSM file but do not run it through EnergyPlus
    Returns:
        report: Report!
        resultFileAddress: The address of the EnergyPlus result file.
        studyFolder: The directory in which the simulation has been run.  Connect this to the 'Honeybee_Lookup EnergyPlus' folder to bring many of the files in this directory into Grasshopper.
"""

ghenv.Component.Name = "Honeybee_Re-run OSM"
ghenv.Component.NickName = 'Re-Run OSM'
ghenv.Component.Message = 'VER 0.0.62\nJUL_28_2017'
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
    
    return workingDir, os.path.join(idfFolder, "ModelToIdf", "in.idf"), resultFile


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


if openStudioIsReady and initCheck == True and openStudioIsReady == True and _runIt > 0 and _epwFileAddress and _osmFilePath:
    fileCheck = checkTheInputs(_osmFilePath, _epwFileAddress)
    if fileCheck != -1:
        result = main(_epwFileAddress, _osmFilePath, _runIt, openStudioLibFolder)
        if result != -1:
            studyFolder, idfFileAddress, resultFileAddress = result