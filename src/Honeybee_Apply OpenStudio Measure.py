#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Provided by Honeybee 0.0.58

    Args:
        _osmFilePath: A file path of the an OpemStdio file
        _epwWeatherFile: An .epw file path on your system as a text string.
        _OSMeasure: Loaded OpenStudio measure. Use load OpenStudio measures to load the measure to Honeybee
        _runIt: set to True to apply the measure and run the analysis
    Returns:
        projectFolder: Path to new project folder
        modifiedIdfFilePath: Path to modified EnergyPlus file
        modifiedOsmFilePath: Path to modified OpenStudio file
        resultsFileAddress: Path to .csv results file
"""

ghenv.Component.Name = "Honeybee_Apply OpenStudio Measure"
ghenv.Component.NickName = 'applyOSMeasure'
ghenv.Component.Message = 'VER 0.0.58\nJAN_21_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import scriptcontext as sc

#openStudioLibFolder = "C:\\Users\\" + os.getenv("USERNAME") + "\\Dropbox\\ladybug\\honeybee\\openStudio\\CSharp64bits"
openStudioFolder = r"C:\\Program Files\\OpenStudio 1.9.2\\"
openStudioLibFolder = openStudioFolder + r"\CSharp\openstudio"

# openstudio is there
# I need to add a function to check the version and compare with available version
openStudioIsReady = True
import clr
clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")

import sys
if openStudioLibFolder not in sys.path:
    sys.path.append(openStudioLibFolder)

import OpenStudio
import time

def createOSArgument(arg):
    
    if arg.type == 'Choice':
        chs = OpenStudio.StringVector()
        for choice in arg.choices:
            chs.Add(choice.value)
        argument = OpenStudio.OSArgument.makeChoiceArgument(arg.name, chs, arg.required, arg.model_dependent)
    
    elif arg.type == 'Boolean':
        argument = OpenStudio.OSArgument.makeBoolArgument(arg.name, arg.required, arg.model_dependent)
    
    else:
        raise Exception("%s is not Implemented")%arg.type
    
    argument.setDisplayName(arg.display_name)
    argument.setDefaultValue(arg.default_value) #I'm not sure if this is neccessary
    argument.setDescription(arg.description)
    if arg.type != 'Boolean':
        argument.setValue(str(arg.userInput))
    else:
        argument.setValue(arg.userInput)
    
    return argument

def main(epwFile, OSMeasure, osmFile):
    
    # check inputs
    if not os.path.isfile(epwFile) or not epwFile.lower().endswith(".epw"):
        raise Exception("Can't find epw file")

    try:
        measureArgs = OSMeasure.args
        measurePath = OSMeasure.path
    except:
        raise Exception("Not a valid Honeybee measure. Use load OpenStudio measure component to create one!")
    
    if not os.path.isfile(osmFile) or not osmFile.lower().endswith(".osm"):
        raise Exception("Can't find OpenStudio file")
    
    workingDir = os.path.split(osmFile)[0]
    
    rmDBPath = OpenStudio.Path(workingDir + '/runmanager.db')
    osmPath = OpenStudio.Path(osmFile)
    epwPath = OpenStudio.Path(epwFile)
    epPath = OpenStudio.Path(openStudioFolder + r'\share\openstudio\EnergyPlusV8-3-0')
    radPath = OpenStudio.Path('c:\radince\bin') #openStudioFolder + r'\share\openstudio\Radiance\bin')
    rubyPath = OpenStudio.Path(openStudioFolder + r'\ruby-install\ruby\bin')
    outDir = OpenStudio.Path(workingDir + '\\' + OSMeasure.name.replace(" ", "_")) # I need to have extra check here to make sure name is valid
    
    wf = OpenStudio.Workflow()
    
    measure = OpenStudio.BCLMeasure(OpenStudio.Path(OSMeasure.path))
    args = OpenStudio.OSArgumentVector()
    
    # check if user has input any new value
    # create them and set the value
    for arg in OSMeasure.args.values():
        if str(arg.userInput) != str(arg.default_value):
            # this argument has been updated
            # create it first - we won't need to do this once we can load arguments programmatically
            osArgument = createOSArgument(arg)
            args.Add(osArgument)
    
    # create the workflow
    rjb = OpenStudio.RubyJobBuilder(measure, args)
    rjb.setIncludeDir(OpenStudio.Path(rubyPath))
    wf.addJob(rjb.toWorkItem())
    
    # add energyplus jobs
    wf.addJob(OpenStudio.JobType("ModelToIdf"))
    wf.addJob(OpenStudio.JobType("EnergyPlus"))
    
    # set up tool info to pass to run manager
    tools = OpenStudio.ConfigOptions.makeTools(epPath, OpenStudio.Path(), radPath, rubyPath, OpenStudio.Path())
    
    # add tools to workflow, has to happen after jobs are added
    wf.add(tools)
    wf.addParam(OpenStudio.JobParam("flatoutdir"))
    
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
            print "Running simulation..."
            
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
    
    projectFolder = os.path.normpath(workingDir + '\\' + OSMeasure.name.replace(" ", "_") + "\\0-UserScript")
    modifiedOsmFilePath = os.path.normpath(projectFolder + "\\eplusin.osm")
    modifiedIdfFilePath = "" # I need to add exapnd idf to workflow to get these two
    resultsFileAddress = ""
    
    return projectFolder, modifiedIdfFilePath, modifiedOsmFilePath, resultsFileAddress


if _runIt and _epwWeatherFile and _OSMeasure and _osmFilePath:
    
    projectFolder, modifiedIdfFilePath, modifiedOsmFilePath, resultsFileAddress = main(_epwWeatherFile, _OSMeasure, _osmFilePath)