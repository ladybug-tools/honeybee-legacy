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
Use this component to separate grafed lists of surface data that come out of the "Honeybee_Read EP Surface Result" component based on rough surface type.
-
Provided by Honeybee 0.0.64

    Args:
        _srfData: Any surface data out of the "Honeybee_Read EP Surface Result" component.
    Returns:
        walls = A grafted list of surface data for walls.
        windows = A grafted list of surface data for windows.
        roofs = A grafted list of surface data for to roofs.
        floors = A grafted list of surface data for to floors.
"""
ghenv.Component.Name = "Honeybee_Surface Data Based On Type"
ghenv.Component.NickName = 'srfDataByType'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc


walls = DataTree[Object]()
windows = DataTree[Object]()
roofs = DataTree[Object]()
floors = DataTree[Object]()


def checkBranch():
    checkList = []
    checkData = False
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        try:
            branchList[2].split(": ")
            checkList.append(1)
        except:pass
    if len(checkList) == _srfData.BranchCount:
        checkData = True
    else:
        warning = 'Connected data does not contain a vaild surface data header.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    return checkData


def main(srfData):
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        branchPath = _srfData.Path(i)
        
        srfType = branchList[2].split(": ")[-1]
        
        if srfType == "Wall":
            for item in branchList: walls.Add(item, branchPath)
        elif srfType == "Window":
            for item in branchList: windows.Add(item, branchPath)
        elif srfType == "Roof":
            for item in branchList: roofs.Add(item, branchPath)
        elif srfType == "Floor":
            for item in branchList: floors.Add(item, branchPath)
        else: pass


checkData = False
if _srfData.BranchCount > 0 and str(_srfData) != "tree {0}":
    checkData = checkBranch()

if checkData == True: main(_srfData)