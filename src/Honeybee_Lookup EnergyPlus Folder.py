# Lookup EnergyPlus Folder
# 
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Abraham Yezioro <ayez@ar.technion.ac.il> and Chris Mackey <chris@ladybug.tools>
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
Provided by Honeybee 0.0.64
    
    Args:
        _studyFolder: Path to base study folder. It can be a single simulation folder or a folder containing subfolders produced by parametric simulations
        studyType_: Input for Honeybee EnergyPlus study type:
                    1 > Energy Plus
                    2 > OpenStudio
        refresh_: Refresh
    Returns:
        idfFiles: The file path of the Input Data File (idf) file that has been generated on your machine.
        osmFiles: The file path of the OpenStudio Model (osm) file that has been generated on your machine.
        resultFileAddress: The file path of the Comma-Separated Values file (csv)  result file that has been generated on your machine.
        scheduleCsvFiles: The file paths to any CSV schedules in the study folder.
        rddFiles: The file path of the Report Data Dictionary (rdd) file that has been generated on your machine.
        errFiles: The file path of the Error (err) file that has been generated on your machine.
        eioFiles: The file path of the EnergyPlus Invariant Output (eio) file that has been generated on your machine.
        esoFiles: The file path of the EnergyPlus Simulation Output (eso) result file that has been generated on your machine.
        sqlFiles: The file path of the Structured Query Language (sql) result file that has been generated on your machine.
"""
ghenv.Component.Name = "Honeybee_Lookup EnergyPlus Folder"
ghenv.Component.NickName = 'LookupFolder_EnergyPlus'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
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
        for fileName in fileNames:
            if fileName.lower().endswith(".idf"):
                idfFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and not "SCH" in fileName and not "INTGAIN" in fileName and not fileName.endswith("Table.csv"):
                resultFileAddress.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and ("SCH" in fileName or "INTGAIN" in fileName):
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
    elif subFoldersOS == "OS":
        for fileName in os.listdir(studyFolder):
            if fileName.lower().endswith(".osm"):
                osmFiles.append(os.path.join(studyFolder, fileName))
    else:
        fileNamesOS = os.listdir(subFoldersOS)
        fileNamesOS.sort()
        for fileName in fileNames:
            if fileName.lower().endswith(".osm"):
                osmFiles.append(os.path.join(studyFolder, fileName))
        for fileName in fileNamesOS:
            if fileName.lower().endswith(".idf"):
                idfFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and not "SCH" in fileName and not "INTGAIN" in fileName and not fileName.endswith("Table.csv"):
                resultFileAddress.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".csv") and not fileName.endswith("sz.csv") and ("SCH" in fileName or "INTGAIN" in fileName):
                scheduleCsvFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".rdd"):
                rddFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".err"):
                errFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".eio"):
                eioFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".eso"):
                esoFiles.append(os.path.join(subFoldersOS, fileName))
            elif fileName.lower().endswith(".sql"):
                sqlFiles.append(os.path.join(subFoldersOS, fileName))
        
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
    if studyType_ == None:
        studyType_ = 2
    try:
        dirNames = os.listdir(_studyFolder)
        dirNames.sort()
        for dirName in dirNames: 
            ##print 'dirName1: ', dirName
            if dirName == studyTypes[studyType_]:# Check if the inputFolder has a "EnergyPlus" directory. if so use this only inputFolder
                subFolders.append(os.path.join(_studyFolder, dirName))
                print 'Found it ... found it in 1'
                break
        else:
            for dirName in dirNames: # This is the name for EACH case
                if os.path.isdir(os.path.join(_studyFolder, dirName, studyTypes[studyType_])):
                    ##aa = os.path.join(_studyFolder, dirName, studyTypes[studyType_])   ####
                    subFolders.append(os.path.join(_studyFolder, dirName, studyTypes[studyType_]))
                    ##print 'Found it ... found it in 2\t', aa    # This is the FOR block where files are found
                    
        ################################################################
        ### Now find the directories and files relevant to studyType ###
        ################################################################
        for studyTypeName in subFolders:
            studyFolder = studyTypeName
            subFoldersOS = "OS"
            if studyType_ == 1: # EnergyPlus
                subFoldersOS = "None"
            elif studyType_ == 2: # OpenStudio
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
    except:
        warning = "Please provide a valid studyType! See hint"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
