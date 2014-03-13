# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Search Simulation Folder
-
Provided by Honeybee 0.0.51
    
    Args:
        studyFolder: Path to study folder
        refresh: Refresh the list
    Returns:
        resFiles: List of result files from grid based analysis
        illFiles: List of ill files from annual analysis
        ptsFiles: List of point files
        hdrFiles: List of hdr files
        gifFiles: List of gif files
        
"""

ghenv.Component.Name = "Honeybee_Lookup Daylighting Folder"
ghenv.Component.NickName = 'LookupFolder_Daylighting'
ghenv.Component.Message = 'VER 0.0.51\nMAR_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


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
    hdrFiles = []
    gifFiles = []
    epwFile = str.Empty
    
    if studyFolder!=None:
        fileNames = os.listdir(studyFolder)
        fileNames.sort()
        for fileName in fileNames:
            if fileName.lower().endswith(".res"):
                resFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".ill") and fileName.split("_")[-2]!="space":
                illFilesTemp.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".pts") and fileName.split("_")[-2]!="space":
                ptsFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".epw"):
                epwFile = os.path.join(studyFolder, fileName)
            elif fileName.lower().endswith(".hdr"):
                hdrFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".gif"):
                gifFiles.append(os.path.join(studyFolder, fileName))
    
    # check if there are multiple ill files in the folder for different shading groups
    illFilesDict = {}
    for fullPath in illFilesTemp:
        fileName = os.path.basename(fullPath)
        if fileName.split("_")[:-1]!= []:
            if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                # conceptual blind
                gist = "_".join(fileName.split("_")[:-2]) + "_" + fileName.split("_")[-1]
            else:
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
            if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                # conceptual blind
                if fileList[0].endswith("_down.ill"):
                    p = GH_Path(1)
                else:
                    p = GH_Path(0)
                
                illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-2])), p)
            else:
                illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1])), p)
        except:
            illFiles.AddRange(fileList, p)
            
    
    #except: pass
    try: resFiles = sorted(resFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    try: ptsFiles = sorted(ptsFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    
    return msg, [illFiles, resFiles, ptsFiles, hdrFiles, gifFiles, epwFile]
    

msg, results = main(studyFolder)

if msg!=str.Empty:
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    illFiles, resFiles, ptsFiles, hdrFiles, gifFiles, epwFile = results
