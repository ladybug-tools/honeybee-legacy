# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
        runIt_: Set to 'True' to run the simulation.
    Returns:
        report: Report!
        resultFileAddress: The address of the EnergyPlus result file.
"""

ghenv.Component.Name = "Honeybee_Re-run OSM"
ghenv.Component.NickName = 'Re-Run OSM'
ghenv.Component.Message = 'VER 0.0.59\nMAY_02_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import os
import scriptcontext as sc
import time


if sc.sticky.has_key('honeybee_release'):
    
    installedOPS = [f for f in os.listdir("C:\\Program Files") if f.startswith("OpenStudio")]
    installedOPS = sorted(installedOPS, key = lambda x: int("".join(x.split(" ")[-1].split("."))), reverse = True)
    
    if len(installedOPS) != 0:
        openStudioFolder = "C:/Program Files/%s/"%installedOPS[0]
        openStudioLibFolder = "C:/Program Files/%s/CSharp/openstudio/"%installedOPS[0]
        QtFolder = "C:/Program Files/%s/Ruby/openstudio/"%installedOPS[0]
    else:
        openStudioFolder = ""
        openStudioLibFolder = ""
        QtFolder = ""

    if os.path.isdir(openStudioLibFolder) and os.path.isfile(os.path.join(openStudioLibFolder, "openStudio.dll")):
        # openstudio is there
        # add both folders to path to avoid PINVOKE exception
        if not openStudioLibFolder in os.environ['PATH'] or QtFolder not in os.environ['PATH']:
            os.environ['PATH'] = ";".join([openStudioLibFolder, QtFolder, os.environ['PATH']])
        
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
    
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
    
        import OpenStudio
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg = "Cannot find OpenStudio libraries at " + openStudioLibFolder + \
              "\nYou need to download and install OpenStudio to be able to use this component."
              
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    openStudioIsReady = False


def writeBatchFile(EPFolder, workingDir, idfFileName, epwFileAddress):
    """
    This is here as an alternate until I can get RunManager to work
    """
    EPDirectory = str(EPFolder)
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
    os.system(batchFileAddress)
    
    return fullPath + ".csv"


def main(epwFile, osmFile):
    # check inputs
    if not os.path.isfile(epwFile) or not epwFile.lower().endswith(".epw"):
        raise Exception("Can't find epw file")
    
    if not os.path.isfile(osmFile) or not osmFile.lower().endswith(".osm"):
        raise Exception("Can't find OpenStudio file")
    
    workingDir = os.path.split(osmFile)[0]
    
    rmDBPath = OpenStudio.Path(workingDir + '/runmanager.db')
    osmPath = OpenStudio.Path(osmFile)
    epwPath = OpenStudio.Path(epwFile)
    epPath = OpenStudio.Path(openStudioFolder + r'\share\openstudio\EnergyPlus-8-5-0')
    radPath = OpenStudio.Path('c:\radince\bin')
    rubyPath = OpenStudio.Path(openStudioFolder + r'\ruby-install\ruby\bin')
    outDir = OpenStudio.Path(workingDir) # I need to have extra check here to make sure name is valid
    
    wf = OpenStudio.Workflow()
    
    # add energyplus jobs
    wf.addJob(OpenStudio.JobType("ModelToIdf"))
    wf.addJob(OpenStudio.JobType("EnergyPlus"))
    
    # turn the workflow definition into a specific instance
    jobtree = wf.create(outDir, osmPath, epwPath)
    
    try:
        # make a run manager
        rm = OpenStudio.RunManager(rmDBPath, True, True, False, False)
        
        # run the job tree
        rm.enqueue(jobtree, True)
        rm.setPaused(False)
        
        # one of these two is redundant
        # I keep this
        while rm.workPending():
            time.sleep(1)
            print "Writing IDF..."
            
        # wait until done
        rm.waitForFinished()              
                    
        jobErrors = jobtree.errors()
        
        print "Errors and Warnings:"
        for msg in jobErrors.errors():
          print msg
        
        if jobErrors.succeeded():
          print "Passed!"
        else:
          print "Failed!"
        
        rm.Dispose()
        
    except:
        rm.Dispose()
    
    projectFolder = os.path.normpath(workingDir + '\\' + "\\0-UserScript")
    modifiedOsmFilePath = os.path.normpath(projectFolder + "\\eplusin.osm")
    modifiedIdfFilePath = workingDir + "in.idf"
    resultsFileAddress = writeBatchFile(epPath, workingDir, "\\ModelToIdf\\in.idf", epwFile)
    
    
    return projectFolder, modifiedIdfFilePath, resultsFileAddress



if openStudioIsReady and _runIt and _epwFileAddress and _osmFilePath:
    projectFolder, IdfFilePath, resultFileAddress = main(_epwFileAddress, _osmFilePath)