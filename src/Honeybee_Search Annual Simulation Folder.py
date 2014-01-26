"""
Genrate Test Points
-
Provided by Honybee 0.0.10
    
    Args:
        testSurface: Test surface as a Brep
        gridSize: Size of the test grid
        distBaseSrf: Distance from base surface
    Returns:
        readMe!: ...
        testPoints: Test points
        ptsVectors: Vectors
        faceArea: Area of each mesh face
        mesh: Analysis mesh
"""

ghenv.Component.Name = "Honeybee_Search Annual Simulation Folder"
ghenv.Component.NickName = 'searchAnnualSimulationFolder'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import os
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def main(studyFolder):
    msg = str.Empty

    if studyFolder==None:
        msg = " "
        return msg, None
        
    if not os.path.isdir(studyFolder):
        msg = "Can't find " + studyFolder
        return msg, None
        
    resFiles = []
    illFilesTemp = []
    ptsFiles = []
    
    if studyFolder!=None:
        fileNames = os.listdir(studyFolder)
        fileNames.sort()
        for fileName in fileNames:
            if fileName.endswith(".res"):
                resFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.endswith(".ill") and fileName.split("_")[-2]!="space":
                illFilesTemp.append(os.path.join(studyFolder, fileName))
            elif fileName.endswith(".pts") and fileName.split("_")[-2]!="space":
                ptsFiles.append(os.path.join(studyFolder, fileName))
    
    # check if there are multiple ill files in the folder for different shading groups
    illFilesDict = {}
    for fullPath in illFilesTemp:
        fileName = os.path.basename(fullPath)
        if fileName.split("_")[:-1]!= []:
            gist = "_".join(fileName.split("_")[:-1])
        else:
            gist = fileName
        if gist not in illFilesDict.keys():
            illFilesDict[gist] = []
        illFilesDict[gist].append(fullPath)
    
    # sort the lists
    #try:
    illFiles = DataTree[System.Object]()
    for listCount, fileListKey in enumerate(illFilesDict.keys()):
        p = GH_Path(listCount)
        fileList = illFilesDict[fileListKey]
        try:
            illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1])), p)
        except:
            illFiles.AddRange(fileList, p)
            
    
    #except: pass
    try: resFiles = sorted(resFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    try: ptsFiles = sorted(ptsFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    
    return msg, [illFiles, resFiles, ptsFiles]
    

msg, results = main(studyFolder)

if msg!=str.Empty:
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    illFiles, resFiles, ptsFiles = results