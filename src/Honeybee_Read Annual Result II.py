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
Read Annual Daylight Results II [Daysim]

-
Provided by Honeybee 0.0.64

    Args:
        resultFilesAddress: List of .ill files
        testPts: List of 3d Points
        workingHours: A domain that indicates start and the end hour of tha study. Default is from 8 to 17.
        lunchHours: A domain that indicates start and end of the hours off during the day
        timeStep: Timestep for the annual study. Default is 1.
        minThreshold: Minimum of desired value (default is illuminance and 300 lux)
        maxThreshold: Maximum of desired value (default is infinite)
    Returns:
        readMe!: ...
        lessThanRange: Percentage of the time that the value is less than desired value
        inTheRange: Percentage of the time that the value is between minimum and maximum Thresholds
        moreThanRange: Percentage of the time that the value is more than desired value
"""
ghenv.Component.Name = "Honeybee_Read Annual Result II"
ghenv.Component.NickName = 'readAnnualResultsII'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def isAllNone(dataList):
    for item in dataList:
        if item!=None: return False
    return True

if _runIt and (testPts.DataCount!=0 or not isAllNone(testPts.AllData())) \
   and resultFilesAddress and resultFilesAddress[0]!=None:
    
    numOfPts = 0
    testPts.SimplifyPaths()
    numOfBranches = testPts.BranchCount
    for branchNum in range(numOfBranches):
        numOfPts = numOfPts + len(testPts.Branch(branchNum))
    #print numOfPts
    # for path in range(len(testPts.Branch(branchNum))): print testPts.Branch(branchNum)[path]
    
    
    # setting up work hours
    if workingHours == None:
        stHour = 8; endHour = 17
    else:
        stHour, endHour = workingHours
        stHour, endHour = int(stHour), int(endHour)
    print 'working hours is set from ' + `stHour` + ' to ' + `endHour` + '.'
    
    # setting up lunch hours
    if lunchHours == None:
        lunchStHour = stHour + int((endHour - stHour)/2)
        lunchEndHour = lunchStHour
    else:
        lunchStHour, lunchEndHour = lunchHours
        lunchStHour, lunchEndHour = int(lunchStHour), int(lunchEndHour)
        print 'lunch hours is set from ' + `lunchStHour` + ' to ' + `lunchEndHour` + '.'
    
    # threshold values
    if not minThreshold: minThreshold = 300
    print 'Minimum threshold is set to ' + `minThreshold`
    if not maxThreshold: maxThreshold = float('+Inf')
    print 'Maximum threshold is set to ' + `maxThreshold`
    
    underValues = [0] * numOfPts
    values = [0] * numOfPts
    overValues = [0] * numOfPts
    
    # number of study hours during a year
    studyHours = ((lunchStHour - stHour) + (endHour - lunchEndHour)) * 365
    
    totalPtCount = 0
    ptsCountSoFar = 0
    for resultFile in resultFilesAddress:
        result = open(resultFile, 'r')
        for hour, line in enumerate(result):
            line = line.replace('\n', '', 10)
            lineSeg = line.Split(' ')
            #if len(lineSeg)!= len(testPts) + 4: print 'ERROR!'
            for ptCount, hourLuxValue in enumerate(lineSeg[4:]):
                if hour == 0: totalPtCount += 1
                if  stHour <= (hour + 1)%24 < lunchStHour or lunchEndHour <= (hour + 1)%24 < endHour:
                    if float(hourLuxValue) <= minThreshold: underValues[ptsCountSoFar + ptCount] += 1
                    elif minThreshold <= float(hourLuxValue) <= maxThreshold: values[ptsCountSoFar + ptCount] += 1
                    elif maxThreshold <= float(hourLuxValue): overValues[ptsCountSoFar + ptCount] += 1
        result.close()
        ptsCountSoFar = ptsCountSoFar + (len(lineSeg) - 4)
        
    
    
    # Change values to %
    for ptCount, v in enumerate(values):
        underValues[ptCount] = round((underValues[ptCount]/studyHours) * 100, 2)
        values[ptCount] = round((values[ptCount]/studyHours) * 100, 2)
        overValues[ptCount] = round((overValues[ptCount]/studyHours) * 100, 2)
    
    lessThanRange = DataTree[Object]()
    inTheRange = DataTree[Object]()    
    moreThanRange = DataTree[Object]()
    
    ptCount = 0
    for branchNum in range(numOfBranches):
        p = GH_Path(branchNum)
        for point in range(len(testPts.Branch(branchNum))):
            lessThanRange.Add(underValues[ptCount], p)
            inTheRange.Add(values[ptCount], p)
            moreThanRange.Add("%.2f"%overValues[ptCount], p)
            ptCount += 1

