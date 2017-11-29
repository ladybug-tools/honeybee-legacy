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
Read the results of the annual study for a all the hours of the year for all the points

-
Provided by Honeybee 0.0.62

    Args:
        _illFilesAddress: List of .ill files
        _testPoints: List of 3d Points
        _annualProfiles: Address to a valid *_intgain.csv generated by daysim.
    Returns:
        iIllumLevelsNoDynamicSHD: Illuminance values without dynamic shadings
        iIllumLevelsDynamicSHDGroupI: Illuminance values when shading group I is closed
        iIllumLevelsDynamicSHDGroupII: Illuminance values when shading group II is closed
        iIlluminanceBasedOnOccupancy: Illuminance values based on Daysim user behavior
        shadingGroupInEffect: 0: no blind, 1: shading group I, 2: shading group II
"""
ghenv.Component.Name = "Honeybee_Read All the Hourly Results from Annual Daylight Study"
ghenv.Component.NickName = 'readAllTheDSHourlyResults'
ghenv.Component.Message = 'VER 0.0.62\nNOV_18_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



import os
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def convertIllFileDaraTreeIntoSortedDictionary(illFilesAddress):
    
    # I should move this function into Honeybee_Honeybee #BadPractice!
    
    shadingGroupsCount = 0
    shadingGroups = []
    
    # get number of shading groups
    for branch in range(illFilesAddress.BranchCount):
        if illFilesAddress.Path(branch).Indices[0] not in shadingGroups:
            shadingGroups.append(illFilesAddress.Path(branch).Indices[0])
            shadingGroupsCount+=1    
    
    illFileSets = {}
    for branch in range(illFilesAddress.BranchCount):
        # sort files inside each branch if they are not sorted
        fileNames = list(illFilesAddress.Branch(branch))
        if illFilesAddress.BranchCount != 1:
            try:
                fileNames = sorted(fileNames, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
            except:
                tmpmsg = "Can't sort .ill files based on the file names. Make sure the branches are sorted correctly."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, tmpmsg)
        
        #convert data tree to a useful dictionary
        shadingGroupNumber = illFilesAddress.Path(branch).Indices[0]
        if shadingGroupNumber not in illFileSets.keys():
            illFileSets[shadingGroupNumber] = []
        
        # create a separate list for each state
        # the structure now is like llFileSets[shadingGroupNumber][[state 1], [state 2],..., [state n]]
        illFileSets[shadingGroupNumber].append(fileNames)
    
    return illFileSets

def main(illFilesAddress, testPoints, annualProfiles):
    msg = str.Empty
    
    shadingProfiles = []
    shadingGroupsCount = 0 # assume there in no shading groups
    
    #groups of groups here
    for resultGroup in  range(testPoints.BranchCount):
        shadingProfiles.append([])
    
    # print len(shadingProfiles)
    if len(annualProfiles)!=0 and annualProfiles[0]!=None:
        # check if the number of profiles matches the number of spaces (point groups)
        if testPoints.BranchCount!=len(annualProfiles):
            msg = "Number of annual profiles doesn't match the number of point groups!\n" + \
                  "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                  "In that case the component will give you the results with no dynamic shadings."
            return msg, None, None
        
        # sort the annual profiles
        # there should be an annual profile for every single space
        try:
            annualProfiles = sorted(annualProfiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
        except:
            pass
            
        # import the shading groups
        # this is a copy-paste from Daysim annual profiles
        for branchCount in range(len(annualProfiles)):
            # open the file
            filePath = annualProfiles[branchCount]
            with open(filePath, "r") as inf:
                for lineCount, line in enumerate(inf):
                    if lineCount == 3:
                        headings = line.strip().split(",")[3:]
                        resultDict = {}
                        for heading in range(len(headings)):
                            resultDict[heading] = []
                    elif lineCount> 3:
                        results = line.strip().split(",")[3:]
                        for resCount, result in enumerate(results):
                            resultDict[resCount].append(float(result))
                            
                shadingCounter = 0
                for headingCount, heading in enumerate(headings):
                    if heading.strip().startswith("blind"):
                        shadingProfiles[branchCount].append(resultDict[headingCount])
                        shadingCounter += 1
        # make sure number of ill files matches the number of the shading groups
        # and sort them to work together
        shadingGroups = []
        
        # get number of shading groups
        for branch in range(illFilesAddress.BranchCount):
            if illFilesAddress.Path(branch).Indices[0] not in shadingGroups:
                shadingGroups.append(illFilesAddress.Path(branch).Indices[0])
                shadingGroupsCount+=1
        
        for shadingProfile in shadingProfiles:
            if len(shadingProfile)!= shadingGroupsCount - 1:
                msg = "Number of annual profiles doesn't match the number of shading groups!\n" + \
                      "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                      "In that case the component will give you the results with no dynamic shadings."
                return msg, None, None
                
    elif illFilesAddress.BranchCount > 1 and illFilesAddress.BranchCount-1 != len(annualProfiles):
        tempmsg = "Annual profile files are not provided.\nThe result will be only calculated for the original case with no blinds."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, tempmsg)
    
    illFileSets = convertIllFileDaraTreeIntoSortedDictionary(illFilesAddress)
    
    # read the data for hour of the year and multiply it with the shading
    numOfPts = testPoints.DataCount
    
    # 3 place holderd for the potential 3 outputs
    # no blinds, shading group I and shading group II
    illuminanceValues = {0: [],
                         1: [],
                         2: [],
                         }
    
    # create a sublist for every shading state
    for shadingGroupCount in illFileSets.keys():
        for HOY in range(8760):
            # separate list for every hour
            illuminanceValues[shadingGroupCount].append([])
            
            # each file represnts one state of shading
            for shadingState in illFileSets[shadingGroupCount]:
                # add an empty list for each state
                illuminanceValues[shadingGroupCount][HOY].append([])
    
    totalPtCount = 0
    ptsCountSoFar = 0
    for shadingGroupCount in range(len(illFileSets.keys())):
        for shadingState, resultFiles in enumerate(illFileSets[shadingGroupCount]):
            for resultFile in resultFiles:
                result = open(resultFile, 'r')
                for HOY, line in enumerate(result):
                   line = line.replace('\n', '', 10)
                   lineSeg = line.Split(' ')
                   for hourLuxValue in lineSeg[4:]:
                      illuminanceValues[shadingGroupCount][HOY][shadingState].append(float(hourLuxValue))
                result.close()

    return msg, illuminanceValues, shadingProfiles


if _illFilesAddress.DataCount!=0 and _illFilesAddress.Branch(0)[0]!=None and _testPoints:
    
    _testPoints.SimplifyPaths()
    _illFilesAddress.SimplifyPaths()
    
    numOfPtsInEachSpace = []
    for branch in range(_testPoints.BranchCount):
        numOfPtsInEachSpace.append(len(_testPoints.Branch(branch)))
    
    msg, illuminanceValues, shadingProfiles = main(_illFilesAddress, _testPoints, annualProfiles_)

    if msg!=str.Empty:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        
    else:
        iIllumLevelsNoDynamicSHD = DataTree[Object]()
        iIllumLevelsDynamicSHDGroupI = DataTree[Object]()
        iIllumLevelsDynamicSHDGroupII = DataTree[Object]()
        iIlluminanceBasedOnOccupancy = DataTree[Object]()
        shadingGroupInEffect = DataTree[Object]()

        # for each space
        for spaceCount in range(len(numOfPtsInEachSpace)):
            for HOY in range(8760):
                p = GH_Path(spaceCount, HOY)
                stateInEffect = 0
                blindsGroupInEffect = 0
                shadingGroupInEffectForTheHour = "No blind"
                iIllumLevelsNoDynamicSHD.AddRange(illuminanceValues[0][HOY][0][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], p)
                
                if illuminanceValues[1]!=[] and len(illuminanceValues[1][HOY])!=0 and shadingProfiles[spaceCount]!=[]:
                    numberOfStates = len(illuminanceValues[1][HOY])
                    if shadingProfiles[spaceCount][0][HOY] > 0:
                        stateInEffect = int(round(numberOfStates * shadingProfiles[spaceCount][0][HOY]))
                        blindsGroupInEffect = 1
                        shadingGroupInEffectForTheHour = "Group_1_State:" + `stateInEffect`
                    
                    if numberOfStates>1:
                        for state in range(numberOfStates):
                            pp = GH_Path(spaceCount, HOY, state)
                            iIllumLevelsDynamicSHDGroupI.AddRange(illuminanceValues[1][HOY][stateInEffect-1][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], pp)
                    else:
                        iIllumLevelsDynamicSHDGroupI.AddRange(illuminanceValues[1][HOY][stateInEffect-1][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], p)
               
                if illuminanceValues[2]!=[] and len(illuminanceValues[2][HOY])!=0 and shadingProfiles[spaceCount]!=[]:
                    numberOfStates = len(illuminanceValues[2][HOY])
                    
                    if shadingProfiles[spaceCount][1][HOY] > 0:
                        stateInEffect = int(round(numberOfStates * shadingProfiles[spaceCount][1][HOY]))
                        blindsGroupInEffect = 2
                        shadingGroupInEffectForTheHour = "Group_2_State:" + `stateInEffect`
                    
                    if numberOfStates>1:
                        for state in range(numberOfStates):
                            pp = GH_Path(spaceCount, HOY, state)
                            iIllumLevelsDynamicSHDGroupII.AddRange(illuminanceValues[2][HOY][stateInEffect-1][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], pp)
                    else:
                        iIllumLevelsDynamicSHDGroupII.AddRange(illuminanceValues[2][HOY][stateInEffect-1][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], p)
                
                if stateInEffect!=0: stateInEffect-=1
                iIlluminanceBasedOnOccupancy.AddRange(illuminanceValues[blindsGroupInEffect][HOY][stateInEffect][sum(numOfPtsInEachSpace[:spaceCount]):sum(numOfPtsInEachSpace[:spaceCount+1])], p)
                
                shadingGroupInEffect.Add(shadingGroupInEffectForTheHour, p)