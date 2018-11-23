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
Read Radiance Results

-
Provided by Honeybee 0.0.64

    Args:
        _resultFiles: A list of result files
        _testPts: A list of 3d test points
        _analysisType: [0] illuminance, [1] radiation, [2] luminance, [3] daylight factor, [4] vertical sky component
        writeToFile_: set to True if you want the final results be saves as a text file
    Returns:
        readMe!: ...
        unit: Unit of the results
        values: Result of the analysis
        
"""
ghenv.Component.Name = "Honeybee_Read RAD Result"
ghenv.Component.NickName = 'readRADResults'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import System
import Grasshopper.Kernel as gh
import math
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc

def main(resultFiles, analysisType):
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return

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
        return
        
    CalculateGridBasedDLAnalysisResults = sc.sticky["honeybee_GridBasedDLResults"]
    calculateResults = CalculateGridBasedDLAnalysisResults(resultFiles, analysisType)
    resultValues = calculateResults.getResults()
    
    return resultValues
    
    
if _testPts and _resultFiles and _analysisType and _resultFiles[0]!=None and not _resultFiles[0].lower().endswith("ill"):
    _testPts.SimplifyPaths()
    numOfPts = []
    numOfBranches = _testPts.BranchCount
    for branchNum in range(numOfBranches):
        numOfPts.append(len(_testPts.Branch(branchNum)))
        
    analysisType = int(_analysisType.split(":")[0].strip()[0])
    
    resultValues = main(_resultFiles, analysisType)
    
    if resultValues:
        # re-branching the results
        values = DataTree[System.Object]()
        totalPtsCount = 0
        resultValuesForFile = ""
        
        for branchNum in range(numOfBranches):
            p = GH_Path(branchNum)
            for ptCount in range(numOfPts[branchNum]):
                resValue = "%.2f"%resultValues[totalPtsCount]
                values.Add(resValue, p)
                if writeToFile_ == True: resultValuesForFile += resValue + "\n"
                totalPtsCount += 1
        
        if writeToFile_ == True:
            resFileName = "_".join(".".join(_resultFiles[0].split(".")[:-1]).split("_")[:-1]) + "_result.txt"
            with open(resFileName, "w") as resFile: 
                resFile.write(resultValuesForFile)
            print "Result file path: " + resFileName
        
        # add analysis type
        analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
        unit = analysisTypesDict[analysisType][1]
