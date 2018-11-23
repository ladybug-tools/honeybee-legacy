#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component reads the results of an EnergyPlus simulation from the "Export to OpenStudio" Component or any EnergyPlus result .csv file address.
_
The component is built to bring in any result that you desire from the csv using _keywords to search through all of the results in the file.  As such, this is particularly useful when you have requested atypical E+ outputs using the "Honeybee_Read Result Dictionary" component.

-
Provided by Honeybee 0.0.64
    
    Args:
        _resultFileAddress: The result file address that comes out of the "Export to OpenStudio" component.
        _keywords: keywords that will be used to bring in the results that you are interested in.  These words should be the name of the output that you are requesting or should correspond to words in the top row of the csv file.
    Returns:
        results: The result data from the csv file (formatted with a Ladybug header on it).
"""

ghenv.Component.Name = "Honeybee_Read EP Custom Result"
ghenv.Component.NickName = 'EPCustomResult'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc
import copy
import os


#Honeybee check.
hbCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    hbCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): hbCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        hbCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

#Check to be sure that the files exist.
csvExists = True
if _resultFileAddress and _resultFileAddress != None:
    if not os.path.isfile(_resultFileAddress):
        csvExists = False
        warning = 'The result file does not exist.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


#Read the location and the analysis period info from the eio file, if there is one.
#Also try to read the floor areas from this file to be used in EUI calculations.
location = "NoLocation"
start = "NoDate"
end = "NoDate"
resultCount = 0

if _resultFileAddress and csvExists == True:
    try:
        eioFileAddress = _resultFileAddress[0:-3] + "eio"
        if not os.path.isfile(eioFileAddress):
            # try to find the file from the list
            studyFolder = os.path.dirname(_resultFileAddress)
            fileNames = os.listdir(studyFolder)
            for fileName in fileNames:
                if fileName.lower().endswith("eio"):
                    eioFileAddress = os.path.join(studyFolder, fileName)
                    break
        
        eioResult = open(eioFileAddress, 'r')
        for lineCount, line in enumerate(eioResult):
            if "Site:Location," in line:
                location = line.split(",")[1].split("WMO")[0]
            elif "WeatherFileRunPeriod" in line:
                start = (int(line.split(",")[3].split("/")[0]), int(line.split(",")[3].split("/")[1]), 1)
                end = (int(line.split(",")[4].split("/")[0]), int(line.split(",")[4].split("/")[1]), 24)
            else: pass
        eioResult.close()
    except:
        try: eioResult.close()
        except: pass 
        warning = 'Your simulation probably did not run correctly. \n' + \
                  'Check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If there are no severe or fatal errors, the issue could just be that there is .eio file adjacent to the .csv _resultFileAddress. \n'+ \
                  'Check the folder of the file address you are plugging into this component and make sure that there is both a .csv and .eio file in the folder.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else: pass




# Make data tree objects for all of the outputs.
results = DataTree[Object]()

# Function to add headers.
def makeHeader(resultList, path, timestep, name, units):
    resultList.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    resultList.Add(location, GH_Path(path))
    resultList.Add(name , GH_Path(path))
    resultList.Add(units, GH_Path(path))
    resultList.Add(timestep, GH_Path(path))
    resultList.Add(start, GH_Path(path))
    resultList.Add(end, GH_Path(path))


# PARSE THE RESULT FILE.
if hbCheck and _resultFileAddress and _keywords and _resultFileAddress != None:
    # Call the class that searches.
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    # If anyone has connected the full name of the output, let's format the keyword correcly for them.
    keywords = []
    for word in _keywords:
        if word.startswith('Output:Variable,*,'):
            theWord = word.split('Output:Variable,*,')[-1].split(',')[0]
            keywords.append(theWord)
        else:
            keywords.append(word)
    
    try:
        result = open(_resultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0:
                # PARSE THE FILE HEADING
                colHeaders = []
                for column in line.split(','):
                    colHeaders.append(column)
                # SEARCH THROUGH THE FILE HEADING
                simOutputs = hb_EPMaterialAUX.searchListByKeyword(colHeaders, keywords)
                simOutLower = []
                for outp in simOutputs:
                    simOutLower.append(outp.lower())
                key = []
                path = []
                for outp in colHeaders:
                    if outp.lower() in simOutLower:
                        outpName = outp.split(' [')[0]
                        timestep = outp.split('(')[-1].split(')')[0]
                        units = outp.split('[')[-1].split(']')[0]
                        makeHeader(results, resultCount, timestep, outpName, units)
                        key.append(0)
                        path.append(resultCount)
                        resultCount += 1
                    else:
                        key.append(-1)
                        path.append(-1)
            else:
                for columnCount, column in enumerate(line.split(',')):
                    p = GH_Path(int(path[columnCount]))
                    
                    if key[columnCount] != -1:
                        results.Add(float(column), p)
        result.close()
        parseSuccess = True
    except:
        try: result.close()
        except: pass
        parseSuccess = False
        warn = 'Failed to parse the result file.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)


