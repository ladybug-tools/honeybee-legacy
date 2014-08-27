# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Read Radiance Results

-
Provided by Honeybee 0.0.54

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
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
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
