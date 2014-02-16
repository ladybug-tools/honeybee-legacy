"""
Read Radiance Results

    Args:
        _resultFilesAddress: A list of result files
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
ghenv.Component.Message = 'VER 0.0.43\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def readRadiationResult(resultFile):
    result = []
    resultFile = open(resultFile,"r")
    for line in resultFile:
        result.append(float(line.split('	')[0]))
    return result

def readDLResult(resultFile):
    result = []
    resultFile = open(resultFile,"r")
    for line in resultFile:
        R, G, B = line.split('	')[0:3]
        result.append(179*(.265 * float(R) + .67 * float(G) + .065 * float(B)))
    return result

def readDFResult(resultFile):
    result = []
    resultFile = open(resultFile,"r")
    for line in resultFile:
        R, G, B = line.split('	')[0:3]
        # divide by the sky horizontal illuminance = 1000
        res = 17900*(.265 * float(R) + .67 * float(G) + .065 * float(B))/1000
        if res > 100: res = 100
        result.append(res)
    return result

if _testPts and _resultFilesAddress and _analysisType and _resultFilesAddress[0]!=None:
    _testPts.SimplifyPaths()
    numOfPts = []
    numOfBranches = _testPts.BranchCount
    for branchNum in range(numOfBranches):
        numOfPts.append(len(_testPts.Branch(branchNum)))
        
    studyType = int(_analysisType.split(":")[0].strip()[0])
    
    resultValues = []
    for fileCount, resultFile in enumerate(_resultFilesAddress):
        if studyType == 0 or studyType == 2:
            #illuminance / luminance
            resultValues.extend(readDLResult(resultFile))
        elif studyType == 1:
            # radiation
            resultValues.extend(readRadiationResult(resultFile))
        elif studyType == 3 or studyType == 4:
            resultValues.extend(readDFResult(resultFile))
    
    result = DataTree[System.Object]()
    # re-branching the results
    totalPtsCount = 0
    if writeToFile_ == True:
        resFileName = "_".join(".".join(_resultFilesAddress[0].split(".")[:-1]).split("_")[:-1]) + "_result.txt"
        
        resFile = open(resFileName, "w")
        pass
        
    for branchNum in range(numOfBranches):
        p = GH_Path(branchNum)
        for ptCount in range(numOfPts[branchNum]):
            resValue = "%.2f"%resultValues[totalPtsCount]
            result.Add(resValue, p)
            if writeToFile_ == True: resFile.write(resValue + "\n")
            totalPtsCount += 1
    
    if writeToFile_ == True:
        print "Result file path: " + resFileName
        resFile.close()
    
    # add analysis type
    analysisTypesDict = {0: ["0:illuminance" , "lux"],
                         1: ["1:radiation" , "wh"],
                         1.1: ["1:cumulative radiation", "kWh"], 
                         2: ["2:luminance" , "cd/m2"],
                         3: ["3: daylight factor", "%"],
                         4: ["4: vertical sky component", "%"]}
    values = result
    unit = analysisTypesDict[studyType][1]