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
Provided by Ladybug 0.0.45
    
    Args:
        _workingDir: The working directory of the energyPlus idf.
        _idfFileName: Name of the idf file (e.g. sample1.idf).
        _epwFileAddress: Address to epw weather file.
        _EPDirectory: [Optional] where EnergyPlus is installed on your system
        _writeIt: Set to true to create the new folder with batch file
        runIt_: Set to 'True' to run the simulation.
    Returns:
        report: Report!
        resultFileAddress: The address of the EnergyPlus result file.
"""

ghenv.Component.Name = "Honeybee_Re-run IDF"
ghenv.Component.NickName = 'Re-Run IDF'
ghenv.Component.Message = 'VER 0.0.59\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import os
import shutil
import Grasshopper.Kernel as gh
import time

def checkTheInputs(EPDirectory,idfFileName):
    
    if os.path.exists(EPDirectory) == False:
        
        warning = "This component could not find the directory for EnergyPlus which is " + str(EPDirectory) +"\n"+\
        "to fix this error specify the correct directory in the input EPDirectory"
        
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        return -1

def writeBatchFile(workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-3-0'):
    workingDrive = workingDir[:2]
    
    # shorten idf file name
    if idfFileName.endswith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
    else: shIdfFileName = idfFileName
    shIdfFileName = os.path.split(shIdfFileName)[-1]
    
    #create a new folder for each idf file
    workingDir += '\\' + shIdfFileName
    workingDir = os.path.normpath(workingDir)
    if not os.path.isdir(workingDir): os.mkdir(workingDir)
    
    # copy idf file to folder
    shutil.copyfile(idfFileName, workingDir + "\\" + shIdfFileName + ".idf")
    
    # copy weather file to folder
    epwFileName = os.path.split(epwFileAddress)[-1]
    shutil.copyfile(epwFileAddress, workingDir + "\\" + epwFileName)
    
    # create full path
    fullPath = workingDir + "\\" + shIdfFileName
    
    folderName = workingDir.replace( (workingDrive + '\\'), '')
    
    batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
            '\\Epl-run ' + fullPath + ' ' + fullPath + ' idf ' + epwFileName + ' EP N nolimit N N 0 Y'
    
    batchFileAddress = fullPath +'.bat'
    batchfile = open(batchFileAddress, 'w')
    batchfile.write(batchStr)
    batchfile.close()
    return batchFileAddress
        
        
def runBatchFile(batchFileAddress):
    #execute the batch file
    os.system(batchFileAddress)






#Check to make sure that a working directory has been connected.
if str(_workingDir) != 'None' and len(list(str(_workingDir))) > 3:
    if str(_workingDir).endswith("/") or str(_workingDir).endswith('\\'): pass
    else: _workingDir = _workingDir + "\\"
    checkdata1 = True
else:
    checkdata1 = False
    print 'Please connect a valid working directory.'

#Check to make sure that an idf file address has been connected.
if str(_idfFileName) != 'None' and len(list(str(_idfFileName))) > 1:
    checkdata2 = True
else:
    checkdata2 = False
    print 'Please connect a valid idf file name.'

#Check to make sure that an epw file address has been connected.
if str(_epwFileAddress) != 'None' and len(list(str(_epwFileAddress))) > 1:
    checkdata3 = True
else:
    checkdata3 = False
    print 'Please connect a valid epw file address.'

#Check to see if runIT has been set to 'True'.
if runIt_ or _writeIt:
    checkdata4 = True
else:
    checkdata4 = False
    print 'Set runIt_ or writeIt to True to begin the simulation.'

#Check if all conditions are satisfied.
if checkdata1 and checkdata2 and checkdata3 and checkdata4:
    checkdata = True
else:
    checkdata =  False





if checkdata and checkTheInputs(_EPDirectory,_idfFileName) != -1:
    batchFileAddress = writeBatchFile(_workingDir, _idfFileName, _epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-3-0')
    print "The file is written to %s"%batchFileAddress 
    
    if runIt_:
        runBatchFile(batchFileAddress)
    
        if _idfFileName.endswith('.idf'):  shIdfFileName = _idfFileName.replace('.idf', '')
        else: shIdfFileName = _idfFileName
        resultFileAddress = str(_workingDir) + str(shIdfFileName) + '.csv'

        time = time.localtime(time.time())
        
        day = time[2]
        month = time[1]
        hour = time[3]
        minute = time[4]
        
        if len(str(minute)) == 1:
            minute = '0'+str(minute)

        print 'EnergyPlus file '+ str(shIdfFileName)+'.idf ' + 're-run successful at '+ str(hour) +':' + str(minute) + ' on '+str(day)+'/'+ str(month) + '!'