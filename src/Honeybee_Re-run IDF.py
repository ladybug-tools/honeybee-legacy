# This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# HoneyBee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This is a component for running a previoulsy-generated .idf file through EnergyPlus with a different weather file.
-
Ladybug started by Mostapha Sadeghipour Roudsari is licensed
under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
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
ghenv.Component.Message = 'VER 0.0.53\nJUL_08_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "5"


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