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
This component applies an OpenStudio measure to an OpenStudio file. The component will eventually be integrated to Export to OpenStudio component.
Read more about OpenStudio measures here: http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/
You can download several measures from here: https://bcl.nrel.gov/nrel/types/measure

Many thanks to NREL team for their support during the process. See (https://github.com/mostaphaRoudsari/Honeybee/issues/214) and (https://github.com/mostaphaRoudsari/Honeybee/issues/290)for just two examples!
-
Provided by Honeybee 0.0.62

    Args:
        _osmFilePath: A file path of the an OpemStdio file
        _epwWeatherFile: An .epw file path on your system as a text string.
        _OSMeasures: Any number of OpenStudio measures that you want to apply to your OepnStudio model. Use the "Honeybee_Load OpenStudio Measure" component to load a measure into Grasshopper
        _runIt: Set to "True" to have the component generate an IDF file from the OSM file and run the IDF through through EnergyPlus.  Set to "False" to not run the file (this is the default).  You can also connect an integer for the following options:
            0 = Do Not Run OSM and IDF thrrough EnergyPlus
            1 = Run the OSM and IDF through EnergyPlus with a command prompt window that displays the progress of the simulation
            2 = Run the OSM and IDF through EnergyPlus in the background (without the command line popup window).
            3 = Generate an IDF from the OSM file but do not run it through EnergyPlus
    Returns:
        readMe!: ...
        osmFileAddress: The file path of the OSM file that has been generated on your machine.
        idfFileAddress: The file path of the IDF file that has been generated on your machine. This file is only generated when you set "runSimulation_" to "True."
        eioFileAddress:  The file path of the EIO file that has been generated on your machine.  This file contains information about the sizes of all HVAC equipment from the simulation.  This file is only generated when you set "runSimulation_" to "True."
        rddFileAddress: The file path of the Result Data Dictionary (.rdd) file that is generated after running the file through EnergyPlus.  This file contains all possible outputs that can be requested from the EnergyPlus model.  Use the "Honeybee_Read Result Dictionary" to see what outputs can be requested.
        studyFolder: The directory in which the simulation has been run.  Connect this to the 'Honeybee_Lookup EnergyPlus' folder to bring many of the files in this directory into Grasshopper.
"""

ghenv.Component.Name = "Honeybee_Apply OpenStudio Measure"
ghenv.Component.NickName = 'applyOSMeasure'
ghenv.Component.Message = 'VER 0.0.62\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nJUL_25_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import os
import shutil

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
        
        import OpenStudio
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

def runCmd(self, batchFileAddress, shellKey = True):
    batchFileAddress.replace("\\", "/")
    p = subprocess.Popen(["cmd /c ", batchFileAddress], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)		
    out, err = p.communicate()


def main(runIt, epwFile, OSMeasures, osmFile):
    
    # check inputs
    if not os.path.isfile(epwFile) or not epwFile.lower().endswith(".epw"):
        raise Exception("Can't find epw file")
    
    if not os.path.isfile(osmFile) or not osmFile.lower().endswith(".osm"):
        raise Exception("Can't find OpenStudio file")
    
    for OSMeasure in OSMeasures:
        try:
            measureArgs = OSMeasure.args
            measurePath = OSMeasure.path
        except:
            raise Exception("Not a valid Honeybee measure. \nUse the Honeybee_Load OpenStudio Measure component to create one!")
    
    # Set up the paths to the files
    osmName = os.path.split(osmFile)[-1].split('.osm')[0]
    workingDir = os.path.split(osmFile)[0]
    oswAddress = workingDir + '\\' + 'workflow.osw'
    osmPath = OpenStudio.Path(osmFile)
    epwPath = OpenStudio.Path(epwFile)
    oswPath = OpenStudio.Path(oswAddress)
    
    # Create the workflow JSON.
    wf = OpenStudio.WorkflowJSON()
    wf.setOswPath(oswPath)
    wf.setSeedFile(osmPath)
    wf.setWeatherFile(epwPath)
    
    # Add the measures to the workflow.
    workflowSteps = []
    for OSMeasure in OSMeasures:
        # Copy measure files to a folder next to the OSM.
        measureName = OSMeasure.path.split('\\')[-1]
        destDir = workingDir + '\\measures\\' + measureName + '\\'
        if os.path.isdir(destDir):
            shutil.rmtree(destDir)
        shutil.copytree(OSMeasure.path, destDir)
        
        # Create the measure step
        measure = OpenStudio.MeasureStep(measureName)
        for arg in OSMeasure.args.values():
            if str(arg.userInput) != str(arg.default_value):
                measure.setArgument(arg.name, str(arg.userInput))
        workflowSteps.append(measure)
    
    # Set the workflow steps and save the JSON.
    stepVector = OpenStudio.WorkflowStepVector(workflowSteps)
    wf.setWorkflowSteps(stepVector)
    wf.save()
    
    # Write the batch file
    workingDrive = workingDir[:2].upper()
    osExePath = '/'.join(openStudioLibFolder.split('/')[:-2]) +'/bin/'
    osExePath = osExePath.replace('/', '\\')
    osExePath = osExePath.replace((workingDrive + '\\'), '')
    
    if runIt != 3:
        batchStr = workingDrive + '\ncd\\' +  osExePath + '\n"' + 'openstudio.exe"' + ' run -w ' + oswAddress
    else:
        batchStr = workingDrive + '\ncd\\' +  osExePath + '\n"' + 'openstudio.exe"' + ' run -m ' + oswAddress
    batchFileAddress = workingDir + '\\' + osmName.replace(" ", "_") +'.bat'
    batchfile = open(batchFileAddress, 'w')
    batchfile.write(batchStr)
    batchfile.close()
    
    #execute the batch file
    if runIt == 2:
        self.runCmd(batchFileAddress)
    else:
        os.system(batchFileAddress)
    
    # Get all of the resulting files.
    runDir = workingDir + '\\' + 'run\\'
    osmFileAddress = runDir + 'in.osm'
    idfFileAddress = runDir + 'in.idf'
    eioFileAddress = runDir + 'eplusout.eio'
    rddFileAddress = runDir + 'eplusout.rdd'
    
    return osmFileAddress, idfFileAddress, eioFileAddress, rddFileAddress, runDir

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

if openStudioIsReady and initCheck == True and _runIt > 0:
    result = main(_runIt, _epwWeatherFile, _OSMeasures, _osmFilePath)
    if result != -1:
        osmFileAddress, idfFileAddress, eioFileAddress, rddFileAddress, studyFolder = result