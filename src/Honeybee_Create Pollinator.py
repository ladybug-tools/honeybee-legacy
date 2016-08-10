# create csv file of parametric analysis results
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Craet Pollinator (Put parametric results together)
-
Provided by Honeybee 0.0.60

    Args:
        _parameters: Input and output parameters in separate branches
        _values: List of values for each input or output parameter
        _workingDir_: Optional workingDir
        _fileName_: Optional filename
    
    Returns:
        pollinator: .csv file that can be loaded and visualized in Pollination.
                    Use OpenPollination to open pollination web page.
"""
ghenv.Component.Name = "Honeybee_Create Pollinator"
ghenv.Component.NickName = 'createPollinator'
ghenv.Component.Message = 'VER 0.0.60\nAUG_10_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(parameters, values, workingDir, fileName):
    
    if workingDir == None:
        workingDir = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "pollinators")
    
    if fileName == None:
        fileName = "pollinator.csv"
        
    # create folder
    if not os.path.isdir(workingDir):
        os.mkdir(workingDir)
    
    filePath = os.path.join(workingDir, fileName)
    
    with open(filePath, "w") as outf:
        
        # write heading
        for headingCount in range(parameters.BranchCount-1):
            outf.write(parameters.Branch(headingCount)[0] + ",")
        outf.write(parameters.Branch(headingCount + 1)[0])
        outf.write("\n")
        #write values
        numberOfCases = int(values.DataCount/values.BranchCount)
        
        for caseNumber in range(numberOfCases):
            for headingCount in range(parameters.BranchCount-1):
                outf.write(values.Branch(headingCount)[caseNumber]+ ",")
            outf.write(values.Branch(headingCount + 1)[caseNumber])
            outf.write("\n")
    
    return filePath


if _parameters.DataCount!=0 and _values.DataCount!=0:
    pollinator =  main(_parameters, _values, _workingDir_, _fileName_)