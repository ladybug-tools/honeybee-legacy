# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
-
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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

Based on a work at https://github.com/mostaphaRoudsari/ladybug.
-
Check this link for more information about the license:
http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
-
Source code is available at:
https://github.com/mostaphaRoudsari/ladybug
-
Provided by Ladybug 0.0.45
    
    Args:
        workingDir: The working directory of the energyPlus idf.
        idfFileName: Name of the idf file (e.g. sample1.idf).
        epwFileAddress: Address to epw weather file.
        EPDirectory: [Optional] where EnergyPlus is installed on your system
        runIt: Set to 'True' to run the simulation.
    Returns:
        report: Report!
        resultFileAddress: The address of the EnergyPlus result file.
"""

ghenv.Component.Name = "Honeybee_Re-run IDF"
ghenv.Component.NickName = 'Re-Run IDF'
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import os


def writeBatchFile(workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0'):
    workingDrive = workingDir[:2]
    
    if idfFileName.endswith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
    else: shIdfFileName = idfFileName
    
    if not workingDir.endswith('\\'): workingDir += '\\'
    
    
    fullPath = workingDir + shIdfFileName
    
    folderName = workingDir.replace( (workingDrive + '\\'), '')
    batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
            '\\Epl-run ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'

    batchFileAddress = fullPath +'.bat'
    batchfile = open(batchFileAddress, 'w')
    batchfile.write(batchStr)
    batchfile.close()
    
    return batchFileAddress
        
        
def runBatchFile(batchFileAddress):
    #execute the batch file
    os.system(batchFileAddress)






#Check to make sure that a working directory has been connected.
if str(workingDir) != 'None' and len(list(str(workingDir))) > 3:
    if str(workingDir).endswith("/") or str(workingDir).endswith('\\'): pass
    else: workingDir = workingDir + "\\"
    checkdata1 = True
else:
    checkdata1 = False
    print 'Please connect a valid working directory.'

#Check to make sure that an idf file address has been connected.
if str(idfFileName) != 'None' and len(list(str(idfFileName))) > 1:
    checkdata2 = True
else:
    checkdata2 = False
    print 'Please connect a valid idf file name.'

#Check to make sure that an epw file address has been connected.
if str(epwFileAddress) != 'None' and len(list(str(epwFileAddress))) > 1:
    checkdata3 = True
else:
    checkdata3 = False
    print 'Please connect a valid epw file address.'

#Check to see if runIT has been set to 'True'.
if runIt:
    checkdata4 = True
else:
    checkdata4 = False
    print 'Set runIt to True to begin the simulation.'

#Check if all conditions are satisfied.
if checkdata1 and checkdata2 and checkdata3 and checkdata4:
    checkdata = True
else:
    checkdata =  False





if checkdata:
    batchFileAddress = writeBatchFile(workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0')
    
    runBatchFile(batchFileAddress)
    if idfFileName.endswith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
    else: shIdfFileName = idfFileName
    resultFileAddress = str(workingDir) + str(shIdfFileName) + '.csv'
    print 'EnergyPlus Re-run successful!'