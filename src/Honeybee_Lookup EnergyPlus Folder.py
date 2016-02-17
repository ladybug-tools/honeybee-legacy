# Lookup EnergyPlus Folder
# 
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Abraham Yezioro <ayez@ar.technion.ac.il> 
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
Search Energy Simulation Folder
-
Provided by Honeybee 0.0.59
    
    Args:
        _studyFolder: Path to base study folder. It can be a single simulation folder or a folder containing subfolders produced by parametric simulations
        _studyType: Input for Honeybee EnergyPlus study type
                    1 > Energy Plus
                    2 > OpenStudio
        refresh_: Refresh
    Returns:
        idfFileAddress: The file path of the Input Data File (idf) file that has been generated on your machine.
        csvFileAddress: The file path of the Comma-Separated Values file (csv)  result file that has been generated on your machine.
        rddFileAddress: The file path of the Report Data Dictionary (rdd) file that has been generated on your machine.
        errFileAddress: The file path of the Error (err) file that has been generated on your machine.
        eioFileAddress: The file path of the EnergyPlus Invariant Output (eio) file that has been generated on your machine.
        esoFileAddress: The file path of the EnergyPlus Simulation Output (eso) result file that has been generated on your machine.
        sqlFileAddress: The file path of the Structured Query Language (sql) result file that has been generated on your machine.
        osmFileAddress: The file path of the OpenStudio Model (osm) file that has been generated on your machine.
        
"""
ghenv.Component.Name = "Honeybee_Lookup EnergyPlus Folder"
ghenv.Component.NickName = 'LookupFolder_EnergyPlus'
ghenv.Component.Message = 'VER 0.0.59\nFEB_15_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import scriptcontext as sc
import os
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from pprint import pprint
idfFiles = []
resultFileAddress = []
scheduleCsvFiles = []
rddFiles = []
errFiles = []
eioFiles = []
esoFiles = []
sqlFiles = []
osmFiles = []


def main(studyFolder, subFoldersOS):
    msg = str.Empty
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_serializeObjects = sc.sticky["honeybee_SerializeObjects"]
    hb_readAnnualResultsAux = sc.sticky["honeybee_ReadAnnualResultsAux"]()
    ##analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
    if studyFolder==None:
        msg = " "
        return msg, None
        
    if not os.path.isdir(studyFolder):
        msg = "Can't find " + studyFolder
        return msg, None
        
    fileNames   = os.listdir(studyFolder)
    fileNames.sort()
    if subFoldersOS == "None":
        ##print 'In Main - EnergyPlus option\t', studyFolder, '\t', subFoldersOS
        for fileName in fileNames:
            if fileName.lower().endswith(".idf"):
                idfFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and "SCH" not in fileName:
                #print fileName, studyFolder
                resultFileAddress.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and "SCH" in fileName:
                #print fileName, studyFolder
                scheduleCsvFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".rdd"):
                rddFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".err"):
                errFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".eio"):
                eioFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".eso"):
                esoFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".sql"):
                sqlFiles.append(os.path.join(studyFolder, fileName))
            #elif fileName.lower().endswith(".osm"):
            #    osmFiles.append(os.path.join(studyFolder, fileName))
    else:
        fileNamesOS = os.listdir(subFoldersOS)
        fileNamesOS.sort()
        ##print 'In Main - OpenStudio option\t', studyFolder, '\t', subFoldersOS
        for fileName in fileNames:
            if fileName.lower().endswith(".osm"):
                osmFiles.append(os.path.join(studyFolder, fileName))
        for fileName in fileNamesOS:
            if fileName.lower().endswith(".idf"):
                idfFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and "SCH" not in fileName:
                #print fileName, studyFolder
                resultFileAddress.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and "SCH" in fileName:
                #print fileName, studyFolder
                scheduleCsvFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".rdd"):
                rddFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".err"):
                errFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".eio"):
                eioFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".eso"):
                esoFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".sql"):
                sqlFiles.append(os.path.join(studyFolder, fileName))
        
    return msg, [idfFiles, resultFileAddress, scheduleCsvFiles, rddFiles, errFiles, eioFiles, esoFiles, sqlFiles, osmFiles]
    
studyTypes = {
        1: "EnergyPlus",
        2: "OpenStudio"
        }
    
subFolders   = []
#subFoldersOS = []


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

w = gh.GH_RuntimeMessageLevel.Warning

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)



if _studyFolder!=None and os.path.isdir(_studyFolder) and initCheck == True:    
    # check if the type is provided
    if _studyType!=None:
        try:
    #####
            dirNames = os.listdir(_studyFolder)
            dirNames.sort()
            for dirName in dirNames: 
                ##print 'dirName1: ', dirName
                if dirName == studyTypes[_studyType]:# Check if the inputFolder has a "EnergyPlus" directory. if so use this only inputFolder
                    subFolders.append(os.path.join(_studyFolder, dirName))
                    print 'Found it ... found it in 1'
                    break
            else:
                for dirName in dirNames: # This is the name for EACH case
                    if os.path.isdir(os.path.join(_studyFolder, dirName, studyTypes[_studyType])):
                        ##aa = os.path.join(_studyFolder, dirName, studyTypes[_studyType])   ####
                        subFolders.append(os.path.join(_studyFolder, dirName, studyTypes[_studyType]))
                        ##print 'Found it ... found it in 2\t', aa    # This is the FOR block where files are found
                        
            ################################################################
            ### Now find the directories and files relevant to studyType ###
            ################################################################
            for studyTypeName in subFolders:
                studyFolder = studyTypeName
                if _studyType == 1: # EnergyPlus
                    subFoldersOS = "None"
                elif _studyType == 2: # OpenStudio
                    dirOSNames = os.listdir(studyFolder)
                    dirOSNames.sort()
                    for dirOSName in dirOSNames: 
                        if os.path.isdir(os.path.join(studyFolder, dirOSName, "ModelToIdf")):
                            subFoldersOS = os.path.join(studyFolder, dirOSName, "ModelToIdf")

                res = main(studyFolder, subFoldersOS)
                
                if res != -1:
                    msg, results = res
                    
                    if msg!=str.Empty:
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    else:
                        idfFiles, resultFileAddress, scheduleCsvFiles, rddFiles, errFiles, eioFiles, esoFiles, sqlFiles, osmFiles = results
    #####
        except:
            #warning = "Study type is not valid! Folder will be set to studyFolder"
            warning = "Please provide a valid studyType! See hint"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else:       #No StudyType provided
        print 'No StudyType provided'
        warning = "Please provide a studyType! See hint"
        ghenv.Component.AddRuntimeMessage(w, warning)
