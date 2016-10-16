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
This component converts a comfort result matrix into a Grasshopper Data Tree with numerical values.
-
Provided by Honeybee 0.0.60
    
    Args:
        _comfResultsMtx: A matrix of comfort data that
    Returns:
        comfResultsTree: A Grasshopper Data Tree of comfort data with numerical float values.
"""

ghenv.Component.Name = "Honeybee_Matrix to Data Tree"
ghenv.Component.NickName = 'mtx2DataTree'
ghenv.Component.Message = 'VER 0.0.60\nOCT_16_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "6"

from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

comfResultsTree = DataTree[Object]()
cullLast = False

if _comfResultsMtx != [] and _comfResultsMtx[0] != None:
    try:
        for bCount, dataList in enumerate(_comfResultsMtx):
            p = GH_Path(bCount-1)
            if bCount == 0:
                if "Over-Heated Percent" in dataList or "Under-Heated Percent" in dataList or "Occupied Thermal Comfort Percent" in dataList or "Thermal Autonomy" in dataList:
                    cullLast = True
            elif cullLast == True and bCount == len(_comfResultsMtx)-1:
                pass
            else:
                for item in dataList:
                    comfResultsTree.Add(item, p)
    except:
        warn = 'Failed to convert the matrix.  Make sure that you are connecting up the Mtx and not another type of input.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

