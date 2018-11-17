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
This is a component for running a previoulsy-generated .idf file through EnergyPlus.

-
Provided by Ladybug 0.0.45
    
    Args:
        _idfFilePath: The full file path to the idf file on your system that you would like to run (e.g. C:\ladybug\sample1.idf).
        _epwFileAddress: The full file path to epw weather file that you would like the simulation to run with.
        parallel_: Set to "True" to run multiple IDFs using multiple CPUs.  Note that this input is only relevant when you have plugged in a list of IDF file addresses.
        runIt_: Set to 'True' to run the simulation.  You can also connect a 2 to run the simulation in the background.
    Returns:
        report: Report!
        resultFileAddress: The address of the EnergyPlus result file.
        eioFileAddress:  The file path of the EIO file that has been generated on your machine.  This file contains information about the sizes of all HVAC equipment from the simulation.  This file is only generated when you set "runSimulation_" to "True."
        rddFileAddress: The file path of the Result Data Dictionary (.rdd) file that is generated after running the file through EnergyPlus.  This file contains all possible outputs that can be requested from the EnergyPlus model.  Use the "Honeybee_Read Result Dictionary" to see what outputs can be requested.
"""

ghenv.Component.Name = "Honeybee_Re-run IDF"
ghenv.Component.NickName = 'Re-Run IDF'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nJUL_24_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import scriptcontext as sc
import os
import shutil
import Grasshopper.Kernel as gh
import time
import subprocess
import System.Threading.Tasks as tasks

def checkTheInputs(idfFileName, epwWeatherFile):
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
    
    if not os.path.isfile(idfFileName):
        msg = "IDF file does not exist in the specified location!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    if not idfFileName.lower().endswith('.idf'):
        msg = "IDF file is not a valid IDF!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    if len(idfFileName.split('//')) == 2:
        msg = "IDF file cannot be in the root of the C:\ drive. \n Please move it into a directory."
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    # Check for white space in file path.
    if ' ' in idfFileName:
        warning = "A white space was found in the .idf file path.  EnergyPlus cannot run out of directories with white spaces.\n" + \
        "Copy the .idf file to a directory without a white space and try again."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # make sure EnergyPlus folder is found
    EPPath = sc.sticky["honeybee_folders"]["EPPath"]
    
    if EPPath == None:
        # give a warning to the user
        msg= "Honeybee cannot find a compatible EnergyPlus folder on your system.\n" + \
             "Make sure you have EnergyPlus installed on your system.\n" + \
             "You won't be able to run energy simulations without EnergyPlus.\n" +\
             "Check Honeybee_Honeybee component for more information."
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    else:
        return EPPath

def writeBatchFile(workingDir, idfFilePath, epwFileAddress, EPDirectory):
    idfFileName = idfFilePath.split('\\')[-1]
    newIDFPath = "\\".join(idfFilePath.split('\\')[:-2])
    if not newIDFPath.endswith('\\'):
        newIDFPath = newIDFPath + '\\'
    newIDFPath = newIDFPath + idfFileName
    shutil.copy(idfFilePath, newIDFPath)
    
    workingDrive = workingDir[:2]
    
    if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
    else: shIdfFileName = idfFileName
    
    if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
    
    fullPath = workingDir + shIdfFileName
    folderName = workingDir.replace((workingDrive + '\\'), '')
    folderName = "\\".join(folderName.split('\\')[:-2])
    
    batchStr = workingDrive + '\ncd\\' +  folderName + '\n"' + EPDirectory + \
                '\\Epl-run" ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'
    
    batchFileAddress = fullPath + '.bat'
    batchfile = open(batchFileAddress, 'w')
    batchfile.write(batchStr)
    batchfile.close()
    
    return batchFileAddress, newIDFPath, idfFileName

def runCmd(batchFileAddress, shellKey = True):
    batchFileAddress.replace("\\", "/")		
    p = subprocess.Popen(["cmd /c ", batchFileAddress], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)		
    out, err = p.communicate()

def runBatchFile(batchFileAddress, runInBackground):
    #execute the batch file
    if runInBackground > 1:		
        runCmd(batchFileAddress)		
    else:
        os.system(batchFileAddress)

def runParallelIDFs(idfFilePaths, epwFileAddress, runIt, parallel):
    # placeholders for final lists.
    resultFileAddress = [None for x in idfFilePaths]
    eioFileAddress = [None for x in idfFilePaths]
    rddFileAddress = [None for x in idfFilePaths]
    
    reunInBackground = runIt
    if parallel == True:
        runInBackground = 2
    
    def runEP(i):
        epPath = checkTheInputs(idfFilePaths[i], _epwFileAddress)
        if epPath != -1:
            workingDir = "\\".join(idfFilePaths[i].split('\\')[:-1])
            batchFileAddress, newIDFPath, idfFileName = writeBatchFile(workingDir, idfFilePaths[i], _epwFileAddress, epPath)
            runBatchFile(batchFileAddress, runInBackground)
            try:
                os.remove(newIDFPath)
            except:
                pass
            
            shIdfFileName = idfFileName.replace('.idf', '')
            resultFileAddress[i] = str(workingDir) + '\\' + str(shIdfFileName) + '.csv'
            eioFileAddress[i] = resultFileAddress[i].replace('.csv', '.eio')
            rddFileAddress[i] = resultFileAddress[i].replace('.csv', '.rdd')
    
    if parallel == True:
        tasks.Parallel.ForEach(range(len(idfFilePaths)), runEP)
    else:
        for x in range(len(idfFilePaths)):
            runEP(x)
    
    
    return resultFileAddress, eioFileAddress, rddFileAddress


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


if initCheck and _runIt > 0:
    if len(_idfFilePath) == 1:
        epPath = checkTheInputs(_idfFilePath[0], _epwFileAddress)
        if epPath != -1:
            workingDir = "\\".join(_idfFilePath[0].split('\\')[:-1])
            batchFileAddress, newIDFPath, idfFileName = writeBatchFile(workingDir, _idfFilePath[0], _epwFileAddress, epPath)
            print "The file is written to %s"%batchFileAddress 
            runBatchFile(batchFileAddress, _runIt)
            try:
                os.remove(newIDFPath)
            except:
                pass
            
            print '...'
            print 'RUNNING SIMULATION'
            print '...'
            
            try:
                errorFileFullName = (str(workingDir)+ '\\' +str(idfFileName)).replace('.idf', '.err')
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
            
            shIdfFileName = idfFileName.replace('.idf', '')
            resultFileAddress = str(workingDir) + '\\' + str(shIdfFileName) + '.csv'
            eioFileAddress = resultFileAddress.replace('.csv', '.eio')
            rddFileAddress = resultFileAddress.replace('.csv', '.rdd')
            print 'EnergyPlus file '+ str(shIdfFileName)+'.idf ' + 're-run successful!'
    else:
        resultFileAddress, eioFileAddress, rddFileAddress = runParallelIDFs(_idfFilePath, _epwFileAddress, _runIt, parallel_)