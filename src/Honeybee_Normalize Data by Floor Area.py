#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component takes data that has been output from a simulation and normalizes the results by the floor area of the HBZones.
-
Provided by Honeybee 0.0.60
    
    Args:
        _simData: Results from one of the Read Result components.
        HBZones_: All of the HBZones that have been run through the simulation.
    Returns:
        totNormData: The results normalized by the floor area of all connected HBZones.
        zoneNormData: The results normalized by the floor area of each of the connected HBZones.  Note that this will not be output is the connected data is not for the individual zones.
"""

ghenv.Component.Name = "Honeybee_Normalize Data by Floor Area"
ghenv.Component.NickName = 'flrNorm'
ghenv.Component.Message = 'VER 0.0.60\nSEP_25_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nMAY_02_2015
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"

from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc


def createPyTree(dataTree):
    dataPyList = []
    strPyList = []
    for i in range(dataTree.BranchCount):
        branchList = dataTree.Branch(i)
        dataVal = []
        dataStr = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataStr.append(item)
        dataPyList.append(dataVal)
        strPyList.append(dataStr)
    return dataPyList, strPyList

def sumAllDataTree(dataPyList):
    summedTree = []
    transpMtx = zip(*dataPyList)
    for datList in transpMtx:
        summedTree.append(sum(datList))
    return summedTree

def createCombHeader(existHead):
    newLabel = 'Floor Normalized ' + existHead[2].split('for')[0] + 'for Building'
    newUnits = existHead[3] + '/m2'
    newHead = existHead[:2] + [newLabel] + [newUnits] + existHead[4:]
    return newHead

def createNormHeader(existHead):
    newLabel = 'Floor Normalized ' + existHead[2]
    newUnits = existHead[3] + '/m2'
    newHead = existHead[:2] + [newLabel] + [newUnits] + existHead[4:]
    return newHead

def main(HBZones, simData):
    # Import the classes.
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # Get the floor areas of each zone.
    hbZoneAreas = []
    hbZoneNames = {}
    zones = hb_hive.visualizeFromHoneybeeHive(HBZones)
    for count, zone in enumerate(zones):
        try:
            if not HBZone.isPlenum:
                hbZoneAreas.append(zone.getFloorArea())
                hbZoneNames[zone.name.upper()] = count
        except:
            hbZoneAreas.append(zone.getFloorArea())
            hbZoneNames[zone.name.upper()] = count
    totZoneArea = sum(hbZoneAreas)
    
    # Convert the data tree into python.
    dataPyList, strPyList = createPyTree(simData)
    if len(dataPyList) == 1 and dataPyList[0] == []:
        return -1
    
    # Create a list with all data combined.
    sumPyList = sumAllDataTree(dataPyList)
    flrNrmSumList = []
    for val in sumPyList:
        flrNrmSumList.append(val/totZoneArea)
    
    #Put a header on the combined data list.
    if strPyList[0] != []:
        combHeader = createCombHeader(strPyList[0])
        combDat = combHeader + flrNrmSumList
    else:
        combDat = flrNrmSumList
    
    # Normalize any recognizable zone data.
    normZoneDat = []
    try:
        for count, branch in enumerate(strPyList):
            zName = branch[2].split('for ')[-1]
            if zName in hbZoneNames.keys():
                zoneDat = dataPyList[hbZoneNames[zName]]
                flrNormDat = createNormHeader(branch)
                for val in zoneDat:
                    flrNormDat.append(val/hbZoneAreas[hbZoneNames[zName]])
                normZoneDat.append(flrNormDat)
    except: pass
    
    return combDat, normZoneDat



#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True
#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True and _simData.BranchCount > 0 and str(_simData) != "tree {0}" and len(_HBZones) > 0 and _HBZones[0] != None:
    result = main(_HBZones, _simData)
    if result!= -1:
        totNormData, zoneNormDataInit = result
        zoneNormData = DataTree[Object]()
        for brCount, branch in enumerate(zoneNormDataInit):
            for item in branch:zoneNormData.Add(item, GH_Path(brCount))