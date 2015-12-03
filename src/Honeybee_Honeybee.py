# This is the heart of the Honeybee
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
This component carries all of Honeybee's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!

-
Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
You should have received a copy of the GNU General Public License
along with Honeybee; If not, see <http://www.gnu.org/licenses/>.

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

Source code is available at: https://github.com/mostaphaRoudsari/Honeybee

-
Provided by Honeybee 0.0.57
    
    Args:
        defaultFolder_: Optional input for Honeybee default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: Current Honeybee mood!!!
"""

ghenv.Component.Name = "Honeybee_Honeybee"
ghenv.Component.NickName = 'Honeybee'
ghenv.Component.Message = 'VER 0.0.57\nSEP_10_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import math
import shutil
import sys
import os
import System.Threading.Tasks as tasks
import System
import time
from itertools import chain
import datetime
import json
import copy
import urllib2 as urllib
import cPickle as pickle
import subprocess
import uuid


PI = math.pi

rc.Runtime.HostUtils.DisplayOleAlerts(False)

class CheckIn():
    
    def __init__(self, defaultFolder, folderIsSetByUser = False):
        
        self.folderIsSetByUser = folderIsSetByUser
        self.letItFly = True
        
        if defaultFolder:
            # user is setting up the folder
            defaultFolder = os.path.normpath(defaultFolder) + os.sep
            
            # check if path has white space
            if (" " in defaultFolder):
                msg = "Default file path can't have white space. Please set the path to another folder." + \
                      "\nHoneybee failed to fly! :("
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                sc.sticky["Honeybee_DefaultFolder"] = ""
                self.letItFly = False
                return
            else:
                # create the folder if it is not created
                if not os.path.isdir(defaultFolder):
                    try: os.mkdir(defaultFolder)
                    except:
                        msg = "Cannot create default folder! Try a different filepath" + \
                              "\nHoneybee failed to fly! :("
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        sc.sticky["Honeybee_DefaultFolder"] = ""
                        self.letItFly = False
                        return
            
            # looks fine so let's set it up
            sc.sticky["Honeybee_DefaultFolder"] = defaultFolder
            self.folderIsSetByUser = True
        
        #set up default pass
        if not self.folderIsSetByUser:
            if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
                # folder already exists so it is all fine
                sc.sticky["Honeybee_DefaultFolder"] = "c:\\ladybug\\"
            elif os.access(os.path.dirname("c:\\"), os.F_OK):
                #the folder does not exists but write privileges are given so it is fine
                sc.sticky["Honeybee_DefaultFolder"] = "c:\\ladybug\\"
            else:
                # let's use the user folder
                username = os.getenv("USERNAME")
                # make sure username doesn't have space
                if (" " in username):
                    msg = "User name on this system: " + username + " has white space." + \
                          " Default fodelr cannot be set.\nUse defaultFolder_ to set the path to another folder and try again!" + \
                          "\nHoneybee failed to fly! :("
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    sc.sticky["Honeybee_DefaultFolder"] = ""
                    self.letItFly = False
                    return
                
                sc.sticky["Honeybee_DefaultFolder"] = os.path.join("C:\\Users\\", username, "AppData\\Roaming\\Ladybug\\")
                
    def getComponentVersion(self):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}        
        # convert component version to standard versioning
        ver, verDate = ghenv.Component.Message.split("\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
        
    def isNewerVersionAvailable(self, currentVersion, availableVersion):
        # print int(availableVersion.replace(".", "")), int(currentVersion.replace(".", ""))
        return int(availableVersion.replace(".", "")) > int(currentVersion.replace(".", ""))
    
    def checkForUpdates(self, LB= True, HB= True, OpenStudio = True, template = True):
        
        url = "https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/versions.txt"
        versionFile = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "versions.txt")
        client = System.Net.WebClient()
        client.DownloadFile(url, versionFile)
        with open("c:/ladybug/versions.txt", "r")as vf:
            versions= eval("\n".join(vf.readlines()))
            
        if LB:
            ladybugVersion = versions['Ladybug']
            currentLadybugVersion = self.getComponentVersion() # I assume that this function will be called inside Ladybug_ladybug Component
            if self.isNewerVersionAvailable(currentLadybugVersion, ladybugVersion):
                msg = "There is a newer version of Ladybug available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        if HB:
            honeybeeVersion = versions['Honeybee']
            currentHoneybeeVersion = self.getComponentVersion() # I assume that this function will be called inside Honeybee_Honeybee Component
            if self.isNewerVersionAvailable(currentHoneybeeVersion, honeybeeVersion):
                msg = "There is a newer version of Honeybee available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        if OpenStudio:
            # This should be called inside OpenStudio component which means Honeybee is already flying
            # check if the version file exist
            openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
            versionFile = os.path.join(openStudioLibFolder, "osversion.txt")
            isNewerOSAvailable= False
            if not os.path.isfile(versionFile):
                isNewerOSAvailable= True
            else:
                # read the file
                with open(versionFile) as verFile:
                    currentOSVersion= eval(verFile.read())['version']
            
            OSVersion = versions['OpenStudio']
            
            if isNewerOSAvailable or self.isNewerVersionAvailable(currentOSVersion, OSVersion):
                sc.sticky["isNewerOSAvailable"] = True
            else:
                sc.sticky["isNewerOSAvailable"] = False
                
        if template:
            honeybeeDefaultFolder = sc.sticky["Honeybee_DefaultFolder"]
            templateFile = os.path.join(honeybeeDefaultFolder, 'OpenStudioMasterTemplate.idf')
            
            # check file doesn't exist then it should be downloaded
            if not os.path.isfile(templateFile):
                return True
            
            # find the version
            try:
                with open(templateFile) as tempFile:
                    currentTemplateVersion = eval(tempFile.readline().split("!")[-1].strip())["version"]
            except Exception, e:
                return True
            
            # finally if the file exist and already has a version, compare the versions
            templateVersion = versions['Template']
            return self.isNewerVersionAvailable(currentTemplateVersion, templateVersion)
        

checkIn = CheckIn(defaultFolder_)


class versionCheck(object):
    
    def __init__(self):
        self.version = self.getVersion(ghenv.Component.Message)
    
    def getVersion(self, LBComponentMessage):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        try: ver, verDate = LBComponentMessage.split("\n")
        except: ver, verDate = LBComponentMessage.split("\\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
    
    def isCurrentVersionNewer(self, desiredVersion):
        return int(self.version.replace(".", "")) >= int(desiredVersion.replace(".", ""))
    
    def isCompatible(self, LBComponent):
        code = LBComponent.Code
        # find the version that is supposed to be flying
        try:
            version = code.split("compatibleHBVersion")[1].split("=")[1].split("\n")[0].strip()
        except Exception, e:
            print e
            self.giveWarning(LBComponent)
            return False
            
        desiredVersion = self.getVersion(version)
        
        if not self.isCurrentVersionNewer(desiredVersion):
            self.giveWarning(LBComponent)
            return False
        
        return True
        
    def giveWarning(self, GHComponent):
        warningMsg = "You need a newer version of Honeybee to use this compoent." + \
                     "Use updateHoneybee component to update userObjects.\n" + \
                     "If you have already updated userObjects drag Honeybee_Honeybee component " + \
                     "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)


class hb_findFolders():
    
    def __init__(self):
        self.RADPath, self.RADFile = self.which('rad.exe')
        self.EPPath, self.EPFile = self.which('EnergyPlus.exe')
        self.DSPath, self.DSFile = self.which('gen_dc.exe')
        
    
    def which(self, program):
        """
        Check for path. Modified from this link:
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
        """
        def is_exe(fpath):
            #print fpath
            #if fpath.upper().find("EnergyPlus") > 0:
            #    print fpath
            # Avoid Radiance and Daysim that comes with DIVA as it has a different
            # structure which doesn't match the standard Daysim
            if fpath.upper().find("DIVA")<0:
                # if the user has DIVA installed the component may find DIVA version
                # of RADIANCE and DAYISM which can cause issues because of the different
                # structure of folders in DIVA
                return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
            
            else:
                return False
                
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return path, exe_file
        return None, None


class PrepareTemplateEPLibFiles(object):
    """
    Download Template files and check for available libraries for EnergyPlus
    """
    def __init__(self, downloadTemplate = False, workingDir = sc.sticky["Honeybee_DefaultFolder"]):
        
        if not sc.sticky.has_key("honeybee_constructionLib"): sc.sticky ["honeybee_constructionLib"] = {}
        if not sc.sticky.has_key("honeybee_materialLib"): sc.sticky ["honeybee_materialLib"] = {}
        if not sc.sticky.has_key("honeybee_windowMaterialLib"): sc.sticky ["honeybee_windowMaterialLib"] = {}
        if not sc.sticky.has_key("honeybee_ScheduleLib"): sc.sticky["honeybee_ScheduleLib"] = {}
        if not sc.sticky.has_key("honeybee_ScheduleTypeLimitsLib"): sc.sticky["honeybee_ScheduleTypeLimitsLib"] = {}
        if not sc.sticky.has_key("honeybee_thermMaterialLib"): sc.sticky["honeybee_thermMaterialLib"] = {}
        
        self.downloadTemplate = downloadTemplate
        self.workingDir = workingDir
        
    def downloadFile(self, url, workingDir):
        localFilePath = workingDir + '/' + url.split('/')[-1]
        client = System.Net.WebClient()
        client.DownloadFile(url, localFilePath)
    
    def cleanHBLib(self):
        sc.sticky ["honeybee_constructionLib"] = {}
        sc.sticky ["honeybee_materialLib"] = {}
        sc.sticky ["honeybee_windowMaterialLib"] = {}
        sc.sticky["honeybee_ScheduleLib"] = {}
        sc.sticky["honeybee_ScheduleTypeLimitsLib"] = {}
        sc.sticky["honeybee_thermMaterialLib"] = {}
    
    def downloadTemplates(self):
        
        workingDir = self.workingDir
        
        # create the folder if it is not there
        if not os.path.isdir(workingDir): os.mkdir(workingDir)
        
        # create a backup from users library
        templateFile = os.path.join(workingDir, 'OpenStudioMasterTemplate.idf')
        bckupfile = os.path.join(workingDir, 'OpenStudioMasterTemplate_' + str(int(time.time())) +'.idf')
        
        # download template file
        if self.downloadTemplate or not os.path.isfile(templateFile):
            # create a backup from users library
            try: shutil.copyfile(templateFile, bckupfile)
            except: pass
            
            try:
                ## download File
                print 'Downloading OpenStudioMasterTemplate.idf to ', workingDir
                updatedLink = "https://github.com/mostaphaRoudsari/Honeybee/raw/master/resources/OpenStudioMasterTemplate.idf"
                self.downloadFile(updatedLink, workingDir)
                # clean current library
                self.cleanHBLib()
            except:
                print 'Download failed!!! You need OpenStudioMasterTemplate.idf to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
                return -1
        else:
            pass
        
        if not os.path.isfile(workingDir + '\OpenStudioMasterTemplate.idf'):
            iplibPath = ghenv.Script.GetStandardLibPath()
            print 'Download failed!!! You need OpenStudioMasterTemplate.idf to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
            return -1
        else:
            libFilePaths = [os.path.join(workingDir, 'OpenStudioMasterTemplate.idf')]
            
        # download openstudio standards
        if not os.path.isfile(workingDir + '\OpenStudio_Standards.json'):
            try:
                ## download File
                print 'Downloading OpenStudio_Standards.json to ', workingDir
                self.downloadFile(r'https://github.com/mostaphaRoudsari/Honeybee/raw/master/resources/OpenStudio_Standards.json', workingDir)
            except:
                print 'Download failed!!! You need OpenStudio_Standards.json to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
                return -1
        else:
            pass
        
        
        if not os.path.isfile(workingDir + '\OpenStudio_Standards.json'):
            print 'Download failed!!! You need OpenStudio_Standards.json to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
            return -1
        else:
            # load the json file
            filepath = os.path.join(workingDir, 'OpenStudio_Standards.json')
            try:
                with open(filepath) as jsondata:
                    openStudioStandardLib = json.load(jsondata)
                
                sc.sticky ["honeybee_OpenStudioStandardsFile"] = openStudioStandardLib
                print "Standard template file is loaded!\n"
            except:
                print 'Download failed!!! You need OpenStudio_Standards.json to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
                return -1
        
        # add cutom library
        customEPLib = os.path.join(workingDir,"userCustomEPLibrary.idf")
        
        if not os.path.isfile(customEPLib):
            # create an empty file
            with open(customEPLib, "w") as outf:
                outf.write("!Honeybee custom EnergyPlus library\n")
        
        if os.path.isfile(customEPLib):
            libFilePaths.append(customEPLib)
        
        return libFilePaths
        
        
class HB_GetEPLibraries(object):
    
    def __init__(self):
        pass
    
    def cleanHBLib(self, construction = True, schedule = True):
        if construction:
            sc.sticky ["honeybee_constructionLib"] = {}
            sc.sticky ["honeybee_materialLib"] = {}
            sc.sticky ["honeybee_windowMaterialLib"] = {}
            sc.sticky["honeybee_thermMaterialLib"] = {}
        if schedule:
            sc.sticky["honeybee_ScheduleLib"] = {}
            sc.sticky["honeybee_ScheduleTypeLimitsLib"] = {}
    
    def createEPObject(self, openFile, resultDict, key, scheduleType = None):
            
        # store the data into the dictionary
        recounter = 0
        for lineCount, line in enumerate(openFile):
            if line.strip().startswith("!") or line.strip()=="":
                recounter -= 1
                continue
            if lineCount + recounter == 0:
                nameKey = line.split("!")[0].strip()[:-1].strip().upper()
                if nameKey in resultDict[key].keys():
                    # this means the material is already in the lib
                    # I can rename it but for now I rather to give a warning
                    # and break the loop
                    warning = key + ": " + nameKey + " is already existed in the libaray. " + \
                              "Rename one of the " + nameKey + " and try again."
                    print warning
                    break
                else:
                    # add the material to the library
                    resultDict[key][nameKey] = {}
                    if scheduleType!=None: resultDict[key][nameKey][0] = scheduleType
                    
            else:
                objValue = line.split("!")[0].strip()
                try: objDescription = line.split("!")[1].strip()
                except:  objDescription = ""
                objKey = lineCount + recounter #+ '_' + line.split("!-")[1].strip()
    
                if objValue.endswith(","):
                    resultDict[key][nameKey][objKey] = objValue[:-1], objDescription
                elif objValue.endswith(";"):
                    resultDict[key][nameKey][objKey] = objValue[:-1], objDescription
                    break
        return resultDict
        
    def loadEPConstructionsAndMaterials(self, idfFilePaths, cleanCurrentLib = True):
        
        if cleanCurrentLib:
            self.cleanHBLib(True, False)
            
        # add current library here
        resultDict = {"Material": sc.sticky["honeybee_materialLib"],
                      "WindowMaterial": sc.sticky["honeybee_windowMaterialLib"],
                      "Construction": sc.sticky ["honeybee_constructionLib"]}
            
        print "Loading EP construction library..."
        
        EPKeys = ["Material", "WindowMaterial", "Construction"]
        for libFilePath in idfFilePaths:
            with open(libFilePath, 'r') as inf:
                for line in inf:
                    for key in EPKeys:
                        if line.lower().strip().startswith(key.lower() + ",") \
                            or line.lower().strip().startswith(key.lower() + ":"):
                            resultDict = self.createEPObject(inf, resultDict, key, line.strip()[:-1])
        
        # add them to libraries
        sc.sticky ["honeybee_constructionLib"] = resultDict["Construction"]
        sc.sticky ["honeybee_materialLib"] = resultDict["Material"]
        sc.sticky ["honeybee_windowMaterialLib"] = resultDict["WindowMaterial"]
        
        print str(len(sc.sticky["honeybee_constructionLib"].keys())) + " EPConstructions are loaded available in Honeybee library"
        print str(len(sc.sticky["honeybee_materialLib"].keys())) + " EPMaterials are now loaded in Honeybee library"
        print str(len(sc.sticky["honeybee_windowMaterialLib"].keys())) + " EPWindowMaterial are loaded in Honeybee library"
    
    
    def loadEPSchedules(self, idfFilePaths, cleanCurrentLib = True):
        if cleanCurrentLib:
            self.cleanHBLib(False, True)
            
        schedulesDict = {"ScheduleTypeLimits": sc.sticky["honeybee_ScheduleTypeLimitsLib"],
                         "Schedule": sc.sticky["honeybee_ScheduleLib"]
                        }
        
        print "\nLoading EP schedules..."
        EPKeys = ["ScheduleTypeLimits", "Schedule"]
        for libFilePath in libFilePaths:
            with open(libFilePath, 'r') as inf:
                for line in inf:
                    for key in EPKeys:
                        if line.lower().strip().startswith(key.lower() + ",") \
                           or line.lower().strip().startswith(key.lower() + ":"):
                            schedulesDict = self.createEPObject(inf, schedulesDict, key, line.strip()[:-1])
                            break
                        
        sc.sticky["honeybee_ScheduleLib"] = schedulesDict["Schedule"]
        sc.sticky["honeybee_ScheduleTypeLimitsLib"] = schedulesDict["ScheduleTypeLimits"]

        print str(len(sc.sticky["honeybee_ScheduleLib"].keys())) + " schedules are loaded available in Honeybee library"
        print str(len(sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys())) + " schedule type limits are now loaded in Honeybee library"        
        


class RADMaterialAux(object):
    
    def __init__(self, reloadRADMaterial = False):
            
        self.radMatTypes = ["plastic", "glass", "trans", "metal", "mirror", "mixedfunc", "dielectric", "transdata", "light", "glow"]
        
        if reloadRADMaterial:
            
            # initiate the library
            if not sc.sticky.has_key("honeybee_RADMaterialLib"): sc.sticky ["honeybee_RADMaterialLib"] = {}
            
            # add default materials to the library
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Context_Material', .35, .35, .35, 0, 0.05), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Interior_Ceiling', .80, .80, .80, 0, 0.05), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Interior_Floor', .2, .2, .2, 0, 0.05), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Exterior_Floor', .2, .2, .2, 0, 0.05), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('glass', 'Exterior_Window', .60, .60, .60), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('glass', 'Interior_Window', .60, .60, .60), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Exterior_Roof', .80, .80, .80, 0, 0.05), True, True) # it is actually a ceiling in most of cases
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Exterior_Wall', .50, .50, .50, 0, 0.05), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', 'Interior_Wall', .50, .50, .50, 0, 0.05), True, True)
            
            # import user defined RAD library
            RADLibraryFile = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "HoneybeeRadMaterials.mat")
            if os.path.isfile(RADLibraryFile):
                self.importRADMaterialsFromFile(RADLibraryFile)
            else:
                if not os.path.isdir(sc.sticky["Honeybee_DefaultFolder"]):
                    os.mkdir(sc.sticky["Honeybee_DefaultFolder"])
                with open(RADLibraryFile, "w") as outf:
                    outf.write("#Honeybee Radiance Material Library\n")
            
            # let the user do it for now
            # update the list of the materials in the call from library components
            #for component in ghenv.Component.OnPingDocument().Objects:
            #    if  type(component)== type(ghenv.Component) and component.Name == "Honeybee_Call from Radiance Library":
            #        pass
            #        #component.ExpireSolution(True)
            
            print "Loading RAD default materials..." + \
                  `len(sc.sticky ["honeybee_RADMaterialLib"].keys())` + " RAD materials are loaded\n"
            
    def duplicateMaterialWarning(self, materialName, newMaterialString):
        returnYN = {'YES': True, 'NO': False}
        buttons = System.Windows.Forms.MessageBoxButtons.YesNo
        icon = System.Windows.Forms.MessageBoxIcon.Warning
        try:
            currentMaterialString = self.getRADMaterialString(materialName)
        except:
            currentMaterialString = materialName
            isAdded, materialName = self.analyseRadMaterials(materialName, False)
            
        msg = materialName + " already exists in the library:\n\n" + \
            currentMaterialString + "\n" + \
            "Do you want to overwrite the current material with this new definition?\n\n" + \
            newMaterialString + "\n\n" + \
            "Tip: If you are not sure what to do select No and change the material name."
        up = rc.UI.Dialogs.ShowMessageBox(msg, "Duplicate Material Name", buttons, icon)
        return returnYN[up.ToString().ToUpper()]
    
    def addRADMatToDocumentDict(self, HBSrf, currentMatDict, currentMixedFunctionsDict):
        """
        this function collects the materials for a single run and 
        """
        # check if the material is already added
        materialName = HBSrf.RadMaterial
        if not materialName in currentMatDict.keys():
            # find material type
            materialType = sc.sticky ["honeybee_RADMaterialLib"][materialName].keys()[0]
            
            # check if this is a mixed function
            if materialType == "mixfunc":
                # add mixedFunction
                currentMixedFunctionsDict[materialName] =  materialName
                
                # find the base materials for the mixed function
                material1 = sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType][0][0]
                material2 = sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType][0][1]
                
                for matName in [material1, material2]:
                    if not matName in currentMatDict.keys():
                        currentMatDict[matName] = matName
            else:
                # add to the dictionary
                currentMatDict[materialName] = materialName
        
        return currentMatDict, currentMixedFunctionsDict
    
    def createRadMaterialFromParameters(self, modifier, name, *args):
        
        def getTransmissivity(transmittance):
            return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) - 0.9166530661 ) / 0.0036261119 / transmittance
        
        # I should check the inputs here
        radMaterial = "void " + modifier + " " + name + "\n" + \
                      "0\n" + \
                      "0\n" + \
                      `int(len(args))`
                      
        for arg in args:
            if modifier == "glass":
                radMaterial = radMaterial + (" " + "%.3f"%getTransmissivity(arg))
            else:
                radMaterial = radMaterial + (" " + "%.3f"%arg)
        
        return radMaterial + "\n"
    
    def analyseRadMaterials(self, radMaterialString, addToDocLib = False, overwrite = True):
        """
        import a RAD material string and convert it into Honeybee rad library and return the name
        """
        cleanedRadMaterialString = self.cleanRadMaterials(radMaterialString)
        
        lineSegments = cleanedRadMaterialString.split(" ")
        
        if len(lineSegments) == 1:
            # this is just the name
            # to be used for applying material to surfaces
            return 0, lineSegments[0]
        else:
            #print lineSegments
            materialType = lineSegments[1]
            materialName = lineSegments[2]
            
            if addToDocLib:
                if not overwrite and materialName in sc.sticky ["honeybee_RADMaterialLib"]:
                    upload = self.duplicateMaterialWarning(materialName, radMaterialString)
                    if not upload:
                        return 0, materialName
                sc.sticky ["honeybee_RADMaterialLib"][materialName] = {materialType: {}}
            
                counters = []
                materialProp = lineSegments[3:]
                
                #first counter is the first member of the list
                counter = 0
                counters.append(0)
                
                while counter < len(materialProp):
                    counter += int(materialProp[counter]) + 1
                    try:
                        counters.append(counter)
                    except:
                        pass
                        # print cleanedRadMaterialString
                        # print counter
                # print counters
                
                for counter, count in enumerate(counters[1:]):
                    matStr = materialProp[counters[counter] + 1: count]
                    sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType][counter] = matStr
            else:
                return 0, materialName
                
            return 1, materialName
    
    def cleanRadMaterials(self, radMaterialString):
        """
        inputs rad material string, remove comments, spaces, etc and returns
        a single line string everything separated by a single space
        """
        
        matStr = ""
        lines = radMaterialString.split("\n")
        for line in lines:
            if not line.strip().startswith("#"):
                line = line.replace("\t", " ")
                lineSeg = line.split(" ")
                for seg in lineSeg:
                    if seg.strip()!="":
                        matStr += seg + " "
        return matStr[:-1] # remove the last space
    
    def getRADMaterialString(self, materialName):
        """
        create rad material string from the HB material dictionary based
        """
        materialType = sc.sticky ["honeybee_RADMaterialLib"][materialName].keys()[0]
        matStr = "void " + materialType + " " + materialName + "\n"
        
        for lineCount in sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType].keys():
            properties = sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType][lineCount]
            matStr += str(len(properties)) + " " + " ".join(properties) + "\n"
        
        return matStr
    
    def getRADMaterialType(self, materialName):
        materialType = sc.sticky ["honeybee_RADMaterialLib"][materialName].keys()[0]
        return materialType
    
    def getRADMaterialParameters(self, materialName):
        materialType = self.getRADMaterialType(materialName)
        
        lastLine = len(sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType].keys()) - 1
        
        properties = sc.sticky ["honeybee_RADMaterialLib"][materialName][materialType][lastLine]
        
        return properties
    
    def getSTForTransMaterials(self, materialName):
        properties = self.getRADMaterialParameters(materialName)
        properties = map(float, properties)
        # check got translucant materials
        PHAverage = 0.265 * properties[0] + 0.670 * properties[1] + 0.065 * properties[2]
        
        st = properties[5] * properties[6] * (1 - PHAverage * properties[3])
        return st
    
    def importRadMatStr(self, firstline, inRadf):
        matStr = firstline
        for line in inRadf:
            if not line.strip().startswith("void"):
                if not line.strip().startswith("#") and line.strip()!= "":
                    matStr += line
            else:
                isAdded, materialName = self.analyseRadMaterials(matStr, True, True)
                
                # import the rest of the file to the honeybee library
                self.importRadMatStr(line, inRadf)
        
        # import the last file
        isAdded, materialName = self.analyseRadMaterials(matStr, True, True)
        
    def importRADMaterialsFromFile(self, radFilePath):
        with open(radFilePath, "r") as inRadf:
            for line in inRadf:
                if line.strip().startswith("void"):
                    if line.split(" ")[1].strip() in self.radMatTypes:
                        matStr = self.importRadMatStr(line, inRadf)
    
    def searchRadMaterials(self, keywords, materialTypes):
        keywords = [kw.strip().upper() for kw in keywords]
        materialTypes = [mt.strip().upper() for mt in materialTypes]
        
        materials = []
        
        for radMaterial in sc.sticky["honeybee_RADMaterialLib"].keys():
            materialName = radMaterial.ToUpper()
            materialType = sc.sticky["honeybee_RADMaterialLib"][radMaterial].keys()[0].ToUpper()
            
            if len(materialTypes)==0 or materialType.ToUpper()in materialTypes:
                
                if len(keywords)!= 0 and not "*" in keywords:
                    for keyword in keywords:
                        
                        if materialName.find(keyword)!= -1 or keyword.find(materialName)!= -1:
                            materials.append(radMaterial)
                else:
                    materials.append(radMaterial)
        
        return materials
    
    def addToGlobalLibrary(self, RADMaterial, RADLibraryFile = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "HoneybeeRadMaterials.mat")):
        
        added, materialName = self.analyseRadMaterials(RADMaterial, False)
        
        # read the global library file
        if not os.path.isfile(RADLibraryFile):
            # create a single line for the library
            with open(RADLibraryFile, "w") as inf:
                inf.write("#Honeybee Radiance Global Material Library\n\n")
        
        def addToExistingMaterials(firstline, inRadf, targetMaterialName):
            matStr = firstline
            thisLine = ""
            # collect material string
            for thisLine in inRadf:
                if not thisLine.strip().startswith("void"):
                    # avoid comment lines and empty lines
                    if not thisLine.strip().startswith("#") and thisLine.strip()!= "":
                        matStr += thisLine
                else:
                    break
            
            # get the material name
            isAdded, materialName = self.analyseRadMaterials(matStr, False)
            
            # print materialName
            
            if materialName == targetMaterialName:
                self.found = True
                # ask the user if he wants to overwrite it with the new one
                writeTheNewMaterial= self.duplicateMaterialWarning(matStr, RADMaterial)
                
                if writeTheNewMaterial:
                    # update the file
                    self.outFileStr += RADMaterial + "\n"
                else:
                    # keep the current material
                    self.outFileStr += matStr + "\n"
            else:
                # keep this material
                self.outFileStr += matStr + "\n"
            
            # import the rest of the file to the honeybee library
            if thisLine.strip().startswith("void"):
                addToExistingMaterials(thisLine, inRadf, targetMaterialName)
            
        # open the file and read the materials
        self.outFileStr = ""
        self.found = False
        
        with open(RADLibraryFile, "r") as inRadf:
            for line in inRadf:
                if line.strip().startswith("void"):
                    if line.split(" ")[1].strip() in self.radMatTypes:
                        # check if the name is already existed and add it to the
                        # file if the user wants to overwrite the file.
                        addToExistingMaterials(line, inRadf, materialName)
                else:
                    self.outFileStr += line
        
        if self.found == False:
                # the material is just new so let's just add it to the end of the file
                print materialName + " is added to global library"
                self.outFileStr += RADMaterial + "\n"
        # write the new file
        # this is not the most efficient way of read and write a file in Python
        # but as far as the file is not huge it is fine! Someone may want to fix this
        # print self.outFileStr
        with open(RADLibraryFile, "w") as inRadf:
            inRadf.write(self.outFileStr)
    
    def assignRADMaterial(self, HBSurface, RADMaterial, component):
        # 1.4 assign RAD Material
        if RADMaterial!=None:
            # if it is just the name of the material make sure it is already defined
            if len(RADMaterial.split(" ")) == 1:
                # if the material is not in the library add it to the library
                if RADMaterial not in sc.sticky ["honeybee_RADMaterialLib"].keys():
                    warningMsg = "Can't find " + RADMaterial + " in RAD Material Library.\n" + \
                                "Add the material to the library and try again."
                    component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    return
                
                try:
                    HBSurface.setRADMaterial(RADMaterial)
                    print "HBSurface Radiance Material has been set to " + RADMaterial
                except Exception, e:
                    print e
                    warningMsg = "Failed to assign RADMaterial to " + HBSurface.name
                    print warningMsg
                    component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    return
                
                addedToLib = True
            else:
                
                # try to add the material to the library
                addedToLib, HBSurface.RadMaterial = self.analyseRadMaterials(RADMaterial, True)
                
            if addedToLib==False:
                warningMsg = "Failed to add " + RADMaterial + " to the Library."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                return

class DLAnalysisRecipe(object):
    
    def __init__(self, type, *arg):
        """
        types:
            0: image based analysis > Illuminance(lux) = 0, Radiation(kwh)   = 1,  Luminance (cd)   = 2
            1: node based analysis
            2: annual simulation (Daysim for now)
            3: daylight factor
            4: vertical sky component
        """
        self.type = type
        
        self.component = arg[-1]
        
        # based on the type it should return different outputs
        if type == 0:
            self.skyFile = arg[0]
            self.viewNames = arg[1]
            try: self.radParameters = arg[2].d
            except: self.radParameters = arg[2]
            self.cameraType = arg[3]
            self.simulationType = arg[4]
            self.imageSize = arg[5], arg[6]
            self.sectionPlane = arg[7]
            self.backupImages =  arg[8]
            self.studyFolder = "\\imageBasedSimulation\\"
            
        elif type == 1:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = arg[4]
            self.testMesh = self.convertTreeToLists(arg[5])
            self.studyFolder = "\\gridBasedSimulation\\"
            
        elif type == 2:
            self.weatherFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.DSParameters = arg[4]
            self.testMesh = self.convertTreeToLists(arg[5])
            self.northDegrees = arg[6]
            self.studyFolder = "\\annualSimulation\\"
        
        elif type == 3:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = 0 #illuminance
            self.testMesh = self.convertTreeToLists(arg[4])
            self.studyFolder = "\\DF\\"
        
        elif type == 4:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.testMesh = self.convertTreeToLists(arg[4])
            self.simulationType = 0 #illuminance
            self.studyFolder = "\\VSC\\"
        
        # double check the sky in case of grid based and image based simulations
        if type ==0 or type == 1:
            self.checkSky()
                    
    def convertTreeToLists(self, l):
        listOfLists = []
        for path in l.Paths:
            listOfLists.append(l.Branch(path))
        return listOfLists
    
    def checkSky(self):
        if self.simulationType == 1:
            # make sure the sky is either gencum or gendaylit
            # edit in case of gendaylit
            self.radSkyFile = self.skyFile.split(".")[0] + "_radAnalysis.sky"
            skyOut = open(self.radSkyFile, "w")
            genDaylit = False
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.startswith("!gensky"):
                        self.skyFile = None
                        msg = "You need to use one of the climate-based skies for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return
                    elif line.startswith("!gendaylit"):
                        line = line.replace("-O 0", "-O 1")
                        genDaylit = True
                    # write a new file
                    skyOut.write(line)
            skyOut.close()
            self.skyFile = self.radSkyFile
            if not genDaylit:
                self.simulationType = 1.1 # annual radiation analysis
        
        else:
            # make sure the sky is not from gencum
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.strip().startswith("2 skybright") and line.strip().endswith(".cal"):
                        self.skyFile = None
                        msg = "Cumulative sky can only be used for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return


class hb_MSHToRAD(object):
    
    def __init__(self, mesh, fileName = None, workingDir = None, bitmap = None, radMaterial = None):
        
        if fileName == None:
            fileName = "unnamed"
        
        self.name = fileName
        
        if workingDir == None:
            workingDir = sc.sticky["Honeybee_DefaultFolder"]
        
        workingDir = os.path.join(workingDir, fileName, "MSH2RADFiles")
        if not os.path.isdir(workingDir): os.mkdir(workingDir)
        self.workingDir = workingDir
        
        self.mesh = mesh
        
        self.pattern = bitmap
        if self.pattern != None:
            # create material name based on bitmap
            bitmapFileName = os.path.basename(self.pattern)
            self.matName = ".".join(bitmapFileName.split(".")[:-1])
            #copy the image into same folder
            try:
                shutil.copyfile(self.pattern, os.path.join(self.workingDir, bitmapFileName))
            except:
                pass
        else:
            self.matName = "radMaterial"
            
            if radMaterial != None:
                try:
                    self.matName = radMaterial.split("\n")[0].split(" ")[2]
                except: # Exception, e:
                    # print `e`
                    # not a standard radiance material
                    pass
            
        self.RADMaterial = radMaterial
        
    def meshToObj(self):
        objFilePath = os.path.join(self.workingDir, self.name + ".obj")
        
        with open(objFilePath, "w") as outfile:
            
            # objTxt = "# OBJ file written by TurtlePyMesh\n\n"
            outfile.write("# OBJ file written by TurtlePyMesh\n\n")
            
            # add material file name
            mtlFile = self.name + ".mtl"
            #objTxt += "mtllib " + mtlFile + "\n"
            outfile.write("mtllib " + mtlFile + "\n")
            
            for count, Tmesh in enumerate(self.mesh):
                # add object name - for this version I keep it all as a single object
                #objTxt += "o object_" + str(count + 1) + "\n"
                outfile.write("o object_" + str(count + 1) + "\n")
                
                # add material name - for now brick as test
                #objTxt += "usemtl " + matName + "\n"
                outfile.write("usemtl " + self.matName + "\n")
                
                if Tmesh.Normals.Count == 0:
                    Tmesh.Normals.ComputeNormals()
                    
                # add vertices
                for v in Tmesh.Vertices:
                    XYZ = v.X, v.Y, v.Z
                    XYZ = map(str, XYZ)
                    vString = " ".join(XYZ)
                    #objTxt += "v "  + vString + "\n"
                    outfile.write("v "  + vString + "\n")
                # add texture vertices
                for vt in Tmesh.TextureCoordinates:
                    XY = vt.X, vt.Y
                    XY = map(str, XY)
                    vtString = " ".join(XY)
                    #objTxt += "vt "  + vtString + "\n"
                    outfile.write("vt "  + vtString + "\n")
                # add normals
                for vn in Tmesh.Normals:
                    XYZ = vn.X, vn.Y, vn.Z
                    XYZ = map(str, XYZ)
                    vnString = " ".join(XYZ)
                    # objTxt += "vn "  + vnString + "\n"
                    outfile.write("vn "  + vnString + "\n")
                # add faces
                # vertices number is global so the number should be added together
                fCounter = 0
                
                if count > 0:
                    for meshCount in range(count):
                        fCounter += self.mesh[meshCount].Vertices.Count
                
                # print fCounter
                if self.pattern != None:
                    for face in Tmesh.Faces:
                        # objTxt += "f " + "/".join(3*[`face.A  + fCounter + 1`]) + " " + "/".join(3*[`face.B + fCounter + 1`]) + " " + "/".join(3*[`face.C + fCounter + 1`])
                        outfile.write("f " + "/".join(3*[`face.A  + fCounter + 1`]) + " " + "/".join(3*[`face.B + fCounter + 1`]) + " " + "/".join(3*[`face.C + fCounter + 1`]))
                        if face.IsQuad:
                            #objTxt += " " + "/".join(3*[`face.D + fCounter + 1`])
                            outfile.write(" " + "/".join(3*[`face.D + fCounter + 1`]))
                            
                        #objTxt += "\n"
                        outfile.write("\n")
                else:
                    for face in Tmesh.Faces:
                        outfile.write("f " + "//".join(2 * [`face.A  + fCounter + 1`]) + \
                                      " " + "//".join(2 * [`face.B + fCounter + 1`]) + \
                                      " " + "//".join(2 * [`face.C + fCounter + 1`]))
                        
                        if face.IsQuad:
                            outfile.write(" " + "//".join( 2 * [`face.D + fCounter + 1`]))
                            
                        #objTxt += "\n"
                        outfile.write("\n")
                        
        # This method happened to be so slow!
        #    with open(objFile, "w") as outfile:
        #        outfile.writelines(objTxt)
        
        return objFilePath
    
    def getPICImageSize(self):
        with open(self.pattern, "rb") as inf:
            for count, line in enumerate(inf):
                #print line
                if line.strip().startswith("-Y") and line.find("-X"):
                    Y, YSize, X, XSize = line.split(" ")
                    return XSize, YSize
    
    def objToRAD(self, objFile):
        # prepare file names
        radFile = objFile.replace(".obj", ".rad")
        mshFile = objFile.replace(".obj", ".msh")
        batFile = objFile.replace(".obj", ".bat")        
        
        path, fileName = os.path.split(radFile)
        matFile = os.path.join(path, "material_" + fileName)
        
        try:
            materialType = self.RADMaterial.split("\n")[0].split(" ")[1]
            materialTale = "\n".join(self.RADMaterial.split("\n")[1:])
        except Exception, e:
            # to be added here: if material is not full string then get it from the library
            print "material error..." + `e`
            return        
        
        # create material file
        if self.pattern != None:
            
            # find aspect ratio
            try:
                X, Y= self.getPICImageSize()
                ar = str(int(X)/int(Y))
            except Exception, e:
                ar = str(1)
            
            # mesh has a pattern
            patternName = ".".join(os.path.basename(self.pattern).split(".")[:-1])
            
            materialStr = "void colorpict " + patternName + "_pattern\n" + \
                  "7 red green blue " + self.pattern + " . (" + ar + "*(Lu-floor(Lu))) (Lv-floor(Lv)) \n" + \
                  "0\n" + \
                  "1 1\n" + \
                  patternName + "_pattern " + materialType + " " + patternName + "\n" + \
                  materialTale
        else:
            materialStr = "void "  + materialType + " " + self.matName + "\n" + \
                  materialTale  
                  
        # write material to file
        with open(matFile, "w") as outfile:
            outfile.write(materialStr)
        
        # create rad file
        
        if self.pattern != None:
            cmd = "c:\\radiance\\bin\\obj2mesh -a " + matFile + " " + objFile + " > " +  mshFile
            
            with open(batFile, "w") as outfile:
                outfile.write(cmd)
                #outfile.write("\npause")
                
            os.system(batFile)
            
            radStr = "void mesh painting\n" + \
                     "1 " + mshFile + "\n" + \
                     "0\n" + \
                     "0\n"
            
            with open(radFile, "w") as outfile:
                outfile.write(radStr)
        else:
            # use object to rad
            #create a fake mtl file - material will be overwritten by radiance material
            mtlFile = objFile.replace(".obj", ".mtl")
            
            mtlStr = "# Honeybee\n" + \
                     "newmtl " + self.matName + "\n" + \
                     "Ka 0.0000 0.0000 0.0000\n" + \
                     "Kd 1.0000 1.0000 1.0000\n" + \
                     "Ks 1.0000 1.0000 1.0000\n" + \
                     "Tf 0.0000 0.0000 0.0000\n" + \
                     "d 1.0000\n" + \
                     "Ns 0\n"
            
            with open(mtlFile, "w") as mtlf:
                mtlf.write(mtlStr)
            
            # create a map file
            #mapFile = objFile.replace(".obj", ".map")
            #with open(mapFile, "w") as mapf:
            #    mapf.write(self.matName + " (Object \"" + self.matName + "\");")
            #cmd = "c:\\radiance\\bin\\obj2rad -m " + mapFile + " " + objFile + " > " +  radFile
            
            cmd = "c:\\radiance\\bin\\obj2rad -f " + objFile + " > " +  radFile
            
            with open(batFile, "w") as outfile:
                outfile.write(cmd)
                #outfile.write("\npause")
                
            os.system(batFile)
            
        time.sleep(.2)
    
        return matFile, radFile

class hb_WriteRAD(object):
    
    def __init__(self, component = ghenv.Component):
        
        self.component = component
        
        self.hb_writeRADAUX = sc.sticky["honeybee_WriteRADAUX"]()
        self.hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.hb_writeDS = sc.sticky["honeybee_WriteDS"]()
        
        self.hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        
        hb_folders = sc.sticky["honeybee_folders"]
        self.hb_RADPath = hb_folders["RADPath"]
        self.hb_RADLibPath = hb_folders["RADLibPath"]
        self.hb_DSPath = hb_folders["DSPath"]
        self.hb_DSCore = hb_folders["DSCorePath"]
        self.hb_DSLibPath = hb_folders["DSLibPath"]
        
        
    def writeRADAndMaterialFiles(self, originalHBObjects, subWorkingDir, radFileName, \
                                 analysisRecipe, meshParameters, exportInteriorWalls):
        
        # initiate RAD Parameters
        if analysisRecipe.radParameters==None:
            quality = 0
            analysisRecipe.radParameters = {}
            print "Default values are set for RAD parameters"
            for key in self.hb_radParDict.keys():
                #print key + " is set to " + str(hb_radParDict[key][quality])
                analysisRecipe.radParameters[key] = self.hb_radParDict[key][quality]
        
        # collect information from analysis recipe
        radParameters = analysisRecipe.radParameters
        simulationType = analysisRecipe.type
        
        radFileFullName = os.path.join(subWorkingDir, radFileName + '.rad')
        
        IESObjects = {}
        IESCount = 0    
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBObjects = hb_hive.callFromHoneybeeHive(originalHBObjects)
        
        geoRadFile = open(radFileFullName, 'w')
        geoRadFile.write("#GENERATED BY HONEYBEE\n")
        customRADMat = {} # dictionary to collect the custom material names
        customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
        surfaceList = []
        if len(HBObjects)!=0:
            for objCount, HBObj in enumerate(HBObjects):
                # check if the object is zone or a surface (?)
                if HBObj.objectType == "HBZone":
                    if HBObj.hasNonPlanarSrf or HBObj.hasInternalEdge:
                        HBObj.prepareNonPlanarZone(meshParameters)
                    
                    for srf in HBObj.surfaces:
                        # check if an interior wall
                        if not exportInteriorWalls and self.hb_writeRADAUX.isSrfAirWall(srf):
                            continue
                        
                        # if it is an interior wall and the other wall is already written
                        # then don't write this wall
                        if self.hb_writeRADAUX.isSrfInterior(srf) and srf.BCObject.name in surfaceList:
                            continue
                        
                        surfaceList.append(srf.name)
                        
                        # collect the custom material informations
                        if srf.RadMaterial!=None:
                            customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(srf, customRADMat, customMixFunRadMat)
                        # write the surfaces
                        if srf.isPlanar and len(srf.childSrfs)<2:
                            geoRadFile.write(self.RADSurface(srf))
                        else:
                            geoRadFile.write(self.RADNonPlanarSurface(srf))
                        
                        if srf.hasChild:
                            # collect the custom material informations
                            for childSrf in srf.childSrfs:
                                if childSrf.RadMaterial!=None:
                                    customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                    
                            if not srf.isPlanar or len(srf.childSrfs) > 1:
                                geoRadFile.write(self.RADNonPlanarChildSurface(srf))
                            
                            
                elif HBObj.objectType == "HBSurface":
                    
                    # I should wrap this in a function as I'm using it multiple times with minor changes
                    # collect the custom material informations
                    if HBObj.RadMaterial!=None:
                        try:
                            customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
                        except:
                            msg = HBObj.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                            print msg
                            self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return -1
                            
                    # check for material in child surfaces
                    if not HBObj.isChild and HBObj.hasChild:
                        # collect the custom material informations
                        for childSrf in HBObj.childSrfs:
                            if childSrf.RadMaterial!=None:
                                try:
                                    customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                except:
                                    msg = childSrf.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                                    print msg
                                    self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                                    return -1                    

                    if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                        # check for rad material
                        geoRadFile.write(self.RADSurface(HBObj))
                    else:
                        geoRadFile.write(self.RADNonPlanarSurface(HBObj))
                        if not HBObj.isChild and HBObj.hasChild:
                            geoRadFile.write(self.RADNonPlanarChildSurface(HBObj))
                
                elif HBObj.objectType == "HBIES":
                    IESCount += 1
                    IESObjcIsFine = True
                    # check if the object has been move or scaled
                    if HBObj.checkIfScaledOrRotated(originalHBObjects[objCount]):
                        IESObjcIsFine = False
                        msg = "IES luminaire " + HBObj.name + " is scaled or rotated" + \
                              " and cannot be added to the scene."
                        print msg
                        self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    
                    # check if the material name is already exist
                    if HBObj.name in customRADMat.keys():
                        IESObjcIsFine = False
                        msg = "IES luminaire " + HBObj.name + " cannot be added to the scene.\n" + \
                                  "A material with the same name already exist."
                        print msg
                        self.component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    
                    # if it is all fine then write the geometry
                    if IESObjcIsFine:
                        IESName = HBObj.name + "_" + str(IESCount)
                        geoRadFile.write( HBObj.getRADGeometryStr(IESName, originalHBObjects[objCount]))
                        # downlight_light polygon downlight.d
                        # add to IES Objects list so I can add the materials to the list later
                        if HBObj.name not in IESObjects.keys():
                            IESObjects[HBObj.name] = HBObj
                    
        geoRadFile.close()
        
        ########################################################################
        ######################## GENERATE THE BASE RAD FILE ####################
        materialFileName = subWorkingDir + "\\material_" + radFileName + '.rad'
        # This part should be fully replaced with the new method where I generate the materials from the 
        
        # 0.1 material string
        matStr =  "# start of generic materials definition(s)\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Context_Material') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Interior_Ceiling') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Interior_Floor') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Exterior_Floor') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Exterior_Window') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Interior_Window') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Exterior_Roof') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Exterior_Wall') + "\n" + \
            self.hb_RADMaterialAUX.getRADMaterialString('Interior_Wall') + "\n" + \
            "# end of generic materials definition(s)\n"
    
        with open(materialFileName, 'w') as matFile:
            matFile.write(matStr)
            matFile.write("\n# start of material(s) specific to this study (if any)\n")
            for radMatName in customRADMat.keys():

                matFile.write(self.hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")

                # check if the material is is trans
                if self.hb_RADMaterialAUX.getRADMaterialType(radMatName) == "trans":
                    # get the st value
                    st = self.hb_RADMaterialAUX.getSTForTransMaterials(radMatName)

                    if st < radParameters["_st_"]:
                        print "Found a trans material... " + \
                              "Resetting st parameter from " + str(radParameters["_st_"]) + " to " + str(st)
                        radParameters["_st_"] = st
                    
            # write mixedfun if any
            for radMatName in customMixFunRadMat.keys():
                matFile.write(self.hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
            
            # write IES material if any
            if len(IESObjects.keys())!= 0:
                for IESName in IESObjects.keys():
                    IESObj = IESObjects[IESName]
                    # write material file
                    matFile.write(IESObj.materialStr)
                    
                    # add dat file to folder
                    datFileName = subWorkingDir + "\\" + IESName + '.dat'
                    with open(datFileName, "w") as outDat:
                        outDat.write(IESObj.datFile)
                    
            matFile.write("# end of material(s) specific to this study (if any)\n")
    
        
        # export dayism shading geometries as radFiles
        # this is only useful for dynamic shadings
        dynamicCounter = 0
        if simulationType == 2:
            dynamicShadingRecipes = analysisRecipe.DSParameters.DShdR
            
            if  len(dynamicShadingRecipes) == 0: return radFileFullName, materialFileName
            
            customRADMat = {} # dictionary to collect the custom material names
            customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
            
            for shadingRecipe in dynamicShadingRecipes:
                
                if shadingRecipe.type == 2:
                    
                    groupName = shadingRecipe.name
                    
                    dynamicCounter+=1
                    for stateCount, shadingState in enumerate(shadingRecipe.shadingStates):
                        
                        fileName = groupName + "_state_" + str(stateCount + 1) + ".rad"
                        
                        try:
                            radStr = ""
                            
                            shdHBObjects = hb_hive.callFromHoneybeeHive(shadingState.shdHBObjects)
                            
                            for HBObj in shdHBObjects:
                                # collect the custom material informations
                                if HBObj.RadMaterial!=None:
                                        customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
            
                                if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                                    radStr += self.RADSurface(HBObj)
                                else:
                                    radStr += self.RADNonPlanarSurface(HBObj)
                                    if not HBObj.isChild and HBObj.hasChild:
                                        # collect the custom material informations
                                        for childSrf in HBObj.childSrfs:
                                            if childSrf.RadMaterial!=None:
                                                customRADMat, customMixFunRadMat = self.hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                        radStr += self.RADNonPlanarChildSurface(HBObj)
                            
                            
                            # write the shading file
                            with open(subWorkingDir + "\\" + fileName, "w") as radInf:
                                radInf.write(matStr)
                                radInf.write("# material(s) specific to this study\n")
                                for radMatName in customRADMat.keys():
                                    radInf.write(self.hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                # write mixedfun if any
                                for radMatName in customMixFunRadMat.keys():
                                    radInf.write(self.hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                radInf.write(radStr)
                                
                        except Exception, e:
                            # print `e`
                            # None object so just create an empty file
                            with open(subWorkingDir + "\\" + fileName , "w") as radInf:
                                radInf.write("#empty shading file")
                            pass    
    
        return radFileFullName, materialFileName
    
    def writeTestPtFile(self, subWorkingDir, radFileName, numOfCPUs, analysisRecipe):
        
        if analysisRecipe.type == 0: return [], [] #image-based simulation
        
        testPoints = analysisRecipe.testPts
        ptsNormals = analysisRecipe.vectors
        
        # write a pattern file which I can use later to re-branch the points
        ptnFileName = os.path.join(subWorkingDir, radFileName + '.ptn')
        
        with open(ptnFileName, "w") as ptnFile:
            for ptList in testPoints:
                ptnFile.write(str(len(ptList)) + ", ")
        
        # faltten the test points
        flattenTestPoints = self.lb_preparation.flattenList(testPoints)
        flattenPtsNormals = self.lb_preparation.flattenList(ptsNormals)
        numOfPoints = len(flattenTestPoints)
    
        if numOfCPUs > numOfPoints: numOfCPUs = numOfPoints

        if numOfCPUs > 1:
            ptsEachCpu = int(numOfPoints/(numOfCPUs))
            remainder = numOfPoints%numOfCPUs
        else:		
            ptsEachCpu = numOfPoints		
            remainder = 0
    
        lenOfPts = []
        
        for cpuCount in range(numOfCPUs):		
            if cpuCount < remainder:		
                lenOfPts.append(ptsEachCpu+1)		
            else:		
                lenOfPts.append(ptsEachCpu)
        
        testPtsEachCPU = []
        
        for cpuCount in range(numOfCPUs):
            # write pts file
            ptsForThisCPU = []
            ptsFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '.pts')
            
            ptsFile = open(ptsFileName, "w")

            for ptCount in range(sum(lenOfPts[:cpuCount]), sum(lenOfPts[:cpuCount+1])):
                ptsFile.write(self.hb_writeRADAUX.testPtsStr(flattenTestPoints[ptCount], flattenPtsNormals[ptCount]))
                ptsForThisCPU.append(flattenTestPoints[ptCount])

            ptsFile.close()
            
            testPtsEachCPU.append(ptsForThisCPU)        
            
        return testPtsEachCPU, lenOfPts
    
    def writeBatchFiles(self, subWorkingDir, radFileName, radSkyFileName, \
                        radFileFullName, materialFileName, \
                        numOfCPUs, testPtsEachCPU, \
                        lenOfPts, analysisRecipe, additionalRadFiles, \
                        readyOCTFile = None, runOverture = True):
        
        batchFiles = []
        fileNames = [] # list of only names of the files
        pcompFileName = ""
        
        # initiate RAD Parameters
        if analysisRecipe.radParameters==None:
            quality = 0
            analysisRecipe.radParameters = {}
            print "Default values are set for RAD parameters"
            for key in self.hb_radParDict.keys():
                #print key + " is set to " + str(hb_radParDict[key][quality])
                analysisRecipe.radParameters[key] = self.hb_radParDict[key][quality]
        
        if analysisRecipe.type == 2: # annual daylight analysis - Daysim
            # read parameters
            runAnnualGlare = analysisRecipe.DSParameters.runAnnualGlare
            onlyAnnualGlare = analysisRecipe.DSParameters.onlyAnnualGlare
            annualGlareViews = analysisRecipe.DSParameters.RhinoViewsName
            outputUnits = analysisRecipe.DSParameters.outputUnits
            adaptiveZone = analysisRecipe.DSParameters.adaptiveZone
            dgp_imageSize = analysisRecipe.DSParameters.dgp_imageSize
            dynamicShadingRecipes = analysisRecipe.DSParameters.DShdR
            numOfIllFiles = analysisRecipe.DSParameters.numOfIll
            northAngleRotation = analysisRecipe.northDegrees
            
            # empty list for result file names
            DSResultFilesAddress = []
            
            # location string
            epwFileAddress = analysisRecipe.weatherFile
            
            locationStr, locName = self.hb_writeDS.DSLocationStr(self.hb_writeRADAUX, self.lb_preparation, epwFileAddress)
            
            newLocName = self.lb_preparation.removeBlankLight(locName)
            newLocName = newLocName.replace("/", "_")
            
            # copy .epw file to sub-directory
            self.lb_preparation.copyFile(epwFileAddress, subWorkingDir + "\\" + newLocName + '.epw')
            
            pathStr = "SET RAYPATH=.;" + self.hb_RADLibPath + ";" + self.hb_DSPath + ";" + \
                      self.hb_DSLibPath + ";\nPATH=" + self.hb_RADPath + ";" + \
                      self.hb_DSPath + ";" + self.hb_DSLibPath + ";$PATH\n"
            
            heaFileName = os.path.join(subWorkingDir, radFileName + '_0.hea')
            
            initBatchFileName = os.path.join(subWorkingDir, radFileName + '_InitDS.bat')
            
            initBatchFile = open(initBatchFileName, "w")
            initBatchFile.write(pathStr)
            initBatchStr =  'C:\n' + \
                            'CD ' + self.hb_DSPath + '\n' + \
                            'epw2wea  ' + subWorkingDir + "\\" + self.lb_preparation.removeBlankLight(locName) + '.epw ' + subWorkingDir + "\\" +  self.lb_preparation.removeBlankLight(locName) + '.wea\n' + \
                            ':: 1. Generate Daysim version of Radiance Files\n' + \
                            'radfiles2daysim ' + heaFileName + ' -m -g\n'
            
            # rotate scene if angle is not 0!
            if northAngleRotation!=0:
                initBatchStr += \
                ':: 1.5. Roate geometry and test points\n' + \
                'rotate_scene ' + heaFileName + '\n'
            
            if runAnnualGlare:
                initBatchStr += \
                ':: 2. Generate Values for annual glare\n' + \
                'gen_dgp_profile ' + heaFileName
                
            initBatchFile.write(initBatchStr)
            initBatchFile.close()
            
            # annual glare only needs one headeing file and will run on a single cpu
            if runAnnualGlare: # and onlyAnnualGlare:
                numOfCPUs = 1
                
            # write the rest of the files
            for cpuCount in range(numOfCPUs):
                heaFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '.hea')
                heaFile = open(heaFileName, "w")
                projectName =  radFileName
                
                tempDirName = subWorkingDir + '\\tmp_' + `cpuCount`
                heaFile.write(self.hb_writeDS.DSHeadingStr(projectName, subWorkingDir, tempDirName, self.hb_DSCore , cpuCount))
                
                # delete the files in the old temp folder
                tempWorkingDir = self.lb_preparation.makeWorkingDir(tempDirName)
                
                heaFile.write(locationStr)
                
                heaFile.write(self.hb_writeDS.DSAnalysisUnits(outputUnits, lenOfPts[cpuCount]))
                
                # write view for annual glare if any
                glareViewFileName = subWorkingDir + '\\' + projectName + '_' + 'annualGlareView.vf'
                vfFile = open(glareViewFileName, "w")
                vfFile.write('')
                for view in annualGlareViews:
                    viewLine = self.hb_writeRADAUX.exportView(view, analysisRecipe.radParameters, 1, [dgp_imageSize, dgp_imageSize])
                    # I'm not sure why Daysim view file needs rview Perspective at the start line
                    vfFile.write("rview Perspective " + viewLine + "\n")
                vfFile.close()
                
                # building string
                heaFile.write(self.hb_writeDS.DSBldgStr(projectName, materialFileName, radFileFullName, \
                                                        adaptiveZone, dgp_imageSize, dgp_imageSize, cpuCount, \
                                                        northAngleRotation, additionalRadFiles))
                
                # radiance parameters string
                heaFile.write(self.hb_writeDS.DSRADStr(analysisRecipe.radParameters))
                
                # dynamic simulaion options
                heaFile.write(self.hb_writeDS.DSDynamicSimStr(dynamicShadingRecipes, projectName, subWorkingDir, testPtsEachCPU[cpuCount], cpuCount))
                
                # heaFile.write(hb_writeDS.resultStr(projectName, cpuCount))
                heaFile.close()
                
                if not(runAnnualGlare and onlyAnnualGlare):
                    # ill files
                    DSResultFilesAddress.append(os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '.ill'))
                    # 3.  write the batch file
                    DSBatchFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '_DS.bat')
                    DSBatchFile = open(DSBatchFileName, "w")
                    
                    fileNames.append(DSBatchFileName.split("\\")[-1])
                    
                    heaFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '.hea')
                    
                    #SET PATH = " + subWorkingDir + "\n" + workingDrive +"\n"
                    DSBatchFile.write(pathStr)
                    
                    DSBatchStr = ':: Calculate Daylight Coefficient File (*.dc)\n' + \
                                'gen_dc ' + heaFileName + ' -dif\n' + \
                                'gen_dc ' + heaFileName + ' -dir\n' + \
                                'gen_dc ' + heaFileName + ' -paste\n' + \
                                '\n' + \
                                ':: Generate Illuminance Files (*.ill)\n' + \
                                'ds_illum  ' + heaFileName + '\n'
                    
                    DSBatchFile.write(DSBatchStr)
                                
                    DSBatchFile.close()        
                    
                    batchFiles.append(DSBatchFileName)
        
            return initBatchFileName, batchFiles, fileNames, pcompFileName, DSResultFilesAddress
        
        ######################## NOT ANNUAL SIMULATION #######################
        # 3.  write the batch file
        HDRFileAddress = []
        if analysisRecipe.type == 0:
            self.rhinoViewNames = analysisRecipe.viewNames
            # image based
            initBatchFileName = os.path.join(subWorkingDir, radFileName + '_IMGInit.bat')
            if readyOCTFile ==None:
                OCTFileName = radFileName + '_IMG'
            else:
                OCTFileName = (".").join(os.path.basename(readyOCTFile).split(".")[:-1])
            
        else:
            # not annual and not image based
            initBatchFileName = os.path.join(subWorkingDir, radFileName + '_RADInit.bat')
            if readyOCTFile ==None:
                OCTFileName = radFileName + '_RAD'
            else:
                OCTFileName = (".").join(os.path.basename(readyOCTFile).split(".")[:-1])
            
        
        # create the batch file that initiate the simulation
        with open(initBatchFileName, "w") as batchFile:
            # write the path string (I should check radiance to be installed on the system
            pathStr = "SET RAYPATH=.;" + self.hb_RADLibPath + "\nPATH=" + self.hb_RADPath + ";$PATH\n"
            batchFile.write(pathStr)
            
            batchFile.write("c:\n")
            batchFile.write("cd " + subWorkingDir + "\n")
            
            # write OCT file
            # 3.2. oconv line
            sceneRadFiles = [materialFileName, radSkyFileName, radFileFullName]
            
            if additionalRadFiles:
                for additionalFile in additionalRadFiles:
                    if additionalFile!=None:
                        sceneRadFiles.append(additionalFile)
                
            OCTLine = self.hb_writeRADAUX.oconvLine(OCTFileName, sceneRadFiles)
            if readyOCTFile ==None: batchFile.write(OCTLine)
            
            if analysisRecipe.type == 0:
                # add overture line in case it is an image-based analysis
                view = sc.doc.Views.ActiveView.ActiveViewport.Name
                
                viewLine = self.hb_writeRADAUX.exportView(view, analysisRecipe.radParameters, analysisRecipe.cameraType, imageSize = [64, 64])
                        
                # write rpict lines
                overtureLine = self.hb_writeRADAUX.overtureLine(viewLine, OCTFileName, view, analysisRecipe.radParameters, int(analysisRecipe.type))
                if runOverture: batchFile.write(overtureLine)
            
        if analysisRecipe.type == 0:
            # write view files
            if len(self.rhinoViewNames)==0:
                self.rhinoViewNames = [sc.doc.Views.ActiveView.ActiveViewport.Name]
            
            #recalculate vh and vv
            nXDiv = int(math.sqrt(numOfCPUs))

            while numOfCPUs%nXDiv !=0 and nXDiv < numOfCPUs:
                nXDiv += 1
            
            nYDiv = numOfCPUs/nXDiv

            fileNames = []
            HDRPieces = {}
            for cpuCount in range(numOfCPUs):
                # create a batch file
                batchFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '_IMG.bat')
                batchFiles.append(batchFileName)
                
                fileNames.append(batchFileName.split("\\")[-1])
                batchFile = open(batchFileName, "w")
                # write path files
                batchFile.write(pathStr)
                batchFile.write("c:\n")
                batchFile.write("cd " + subWorkingDir + "\n")
                
                # calculate vs and vl for thi cpu
                try: vs = (((cpuCount%nXDiv)/(nXDiv-1)) - 0.5) * (nXDiv - 1)
                except: vs = 0
                    
                try: vl = ((int(cpuCount/nXDiv)/(nYDiv-1)) - 0.5) * (nYDiv - 1)
                except: vl = 0
                
                # print vs, vl
                for view in self.rhinoViewNames:
                    view = self.lb_preparation.removeBlank(view)
                    
                    if cpuCount == 0:
                        HDRFileAddress.append(subWorkingDir + "\\" + OCTFileName + "_" + view + ".HDR")
                        HDRPieces[OCTFileName + "_" + view + ".HDR"] = []
                    
                    # collect name of the pieces of the picture
                    HDRPieces[OCTFileName + "_" + view + ".HDR"].append(OCTFileName + "_" + view + "_" + `cpuCount` + ".HDR")
                    
                    viewLine = self.hb_writeRADAUX.exportView(view, analysisRecipe.radParameters, analysisRecipe.cameraType, \
                                                              analysisRecipe.imageSize, analysisRecipe.sectionPlane, \
                                                              nXDiv, nYDiv, vs, vl)
                    
                    # write rpict lines
                    RPICTLines = self.hb_writeRADAUX.rpictLine(viewLine, OCTFileName, view, analysisRecipe.radParameters, int(analysisRecipe.simulationType), cpuCount)
                    batchFile.write(RPICTLines)                    
                    
                # close the file
                batchFile.close()
                
                # PCOMP to merge images into a single HDR
                pcompFileName = os.path.join(subWorkingDir, radFileName + '_PCOMP.bat')
                                
                with open(pcompFileName, "w") as pcompFile:
                    
                    # write path files
                    pcompFile.write(pathStr)
                    pcompFile.write("c:\n")
                    pcompFile.write("cd " + subWorkingDir + "\n")
                    
                    for mergedName, pieces in HDRPieces.items():
                        
                        pcomposLine = "pcompos -a " + `nXDiv` + " "
                        # pieces.reverse()
                        for piece in pieces:
                            pcomposLine += piece + " "
                        pcomposLine += " > " + mergedName + "\n"
                        
                        pcompFile.write(pcomposLine)
            
            return initBatchFileName, batchFiles, fileNames, pcompFileName, HDRFileAddress
                        
        else:
            fileNames = []
            RADResultFilesAddress = []
            for cpuCount in range(numOfCPUs):
                # create a batch file
                batchFileName = os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '_RAD.bat')
                batchFiles.append(batchFileName)
                
                RADResultFilesAddress.append(os.path.join(subWorkingDir, radFileName + '_' + `cpuCount` + '.res'))
                
                fileNames.append(batchFileName.split("\\")[-1])
                batchFile = open(batchFileName, "w")
                # write path files
                batchFile.write(pathStr)
                batchFile.write("c:\n")
                batchFile.write("cd " + subWorkingDir + "\n")
                
                # 3.4. add rtrace lin
                RTRACELine = self.hb_writeRADAUX.rtraceLine(radFileName, OCTFileName, analysisRecipe.radParameters, int(analysisRecipe.simulationType), cpuCount)
                batchFile.write(RTRACELine)
                
                # close the file
                batchFile.close()
            
            
            return initBatchFileName, batchFiles, fileNames, pcompFileName, RADResultFilesAddress
        
    
    def runBatchFiles(self, initBatchFileName, batchFileNames, fileNames, \
                      pcompBatchFile, waitingTime, runInBackground = False):
        
        def isTheStudyOver(fileNames):
            while True:
                cmd = 'WMIC PROCESS get Commandline' #,Processid'
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                cmdCount = 0
                for line in proc.stdout:
                    if (line.strip().startswith("C:\\Windows\\system32\\cmd") or line.strip().startswith("cmd")) \
                        and line.strip().endswith(".bat"):
                        fileName = line.strip().split(" ")[-1].split("/")[-1]
                        # I should check the file names and make sure they are the right files
                        if fileName in fileNames:
                            cmdCount += 1
                time.sleep(0.2)
                if cmdCount == 0:
                    return
        
        def executeBatchFiles(batchFileNames, waitingTime, runInBackground):
            cmd = ''
            if not runInBackground: cmd = 'start cmd /c '
            
            for batchFileName in batchFileNames:
                batchFileName = batchFileName.replace("\\", "/")
                p = subprocess.Popen(cmd + batchFileName , shell=True)
                time.sleep(waitingTime)

        if runInBackground:
            subprocess.Popen(initBatchFileName, shell=True)
        else:
            os.system(initBatchFileName)
            
        time.sleep(waitingTime)
        executeBatchFiles(batchFileNames, waitingTime, runInBackground)
        isTheStudyOver(fileNames)
        if pcompBatchFile!="":
            os.system(pcompBatchFile) # put all the files together
        
    def collectResults(self, subWorkingDir, radFileName, numOfCPUs, analysisRecipe, expectedResultFiles):
        
        if analysisRecipe.type == 2:
            #annual simulation
            runAnnualGlare = analysisRecipe.DSParameters.runAnnualGlare
            onlyAnnualGlare = analysisRecipe.DSParameters.onlyAnnualGlare
            numOfIllFiles = analysisRecipe.DSParameters.numOfIll
            annualGlareViews = analysisRecipe.DSParameters.RhinoViewsName
            DSResultFilesAddress = []
            
            if not(runAnnualGlare and onlyAnnualGlare):
                # read the number of .ill files
                # and the number of .dc files
                if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                startTime = time.time()
                
                # check if the results are available
                files = os.listdir(subWorkingDir)
                numIll = 0
                numDc = 0
                for file in files:
                    if file.EndsWith('ill'):
                        DSResultFilesAddress.append(os.path.join(subWorkingDir, file))
                        numIll+=1
                    elif file.EndsWith('dc'):
                        numDc+=1
                if numIll!= numOfCPUs * numOfIllFiles or  numDc!= numOfCPUs * numOfIllFiles:
                    print "Can't find the results for the study"
                    DSResultFilesAddress = []
            
            # check for results of annual glare analysis if any
            annualGlareResults = {}
            for view in annualGlareViews:
                if view not in annualGlareResults.keys():
                    annualGlareResults[view] = []
                    
            dgpFile = os.path.join(subWorkingDir, radFileName + '_0.dgp')
            
            if runAnnualGlare and os.path.isfile(dgpFile):
                with open(dgpFile, "r") as dgpRes:
                    for line in dgpRes:
                        try:
                            hourlyRes = line.split(" ")[4:]
                            # for each view there should be a number
                            for view, res in zip(annualGlareViews, hourlyRes):
                                annualGlareResults[view].append(res.strip())
                        except:
                            pass
                            
            return DSResultFilesAddress, annualGlareResults
        
        elif analysisRecipe.type == 0:
            # image-based analysis
            return expectedResultFiles
        
        else:
            RADResultFilesAddress = expectedResultFiles
            # grid-based analysis
            numRes = 0
            files = os.listdir(subWorkingDir)
            for file in files:
                if file.EndsWith('res'): numRes+=1
            if numRes != numOfCPUs:
                print "Cannot find the results of the study"
                RADResultFilesAddress = []
            time.sleep(1)
            return RADResultFilesAddress
        
    def shiftList(self, list, number = 1):
        newList = []
        newList.extend(list[-number:])
        newList.extend(list[:-number])
        return newList
    
    def getsurfaceStr(self, surface, count, coordinates):
        if surface.RadMaterial != None:
            surface.construction = surface.RadMaterial
        elif not hasattr(surface, 'construction'):
            
            if not hasattr(surface, 'type'):
                # find the type based on 
                surface.type = surface.getTypeByNormalAngle()
                
            #assign the construction based on type
            surface.construction = surface.cnstrSet[surface.type]
            
        srfStr =  surface.construction.replace(" ", "_") + " polygon " + surface.name + '_' + `count` + "\n" + \
            "0\n" + \
            "0\n" + \
            `(len(coordinates)*3)` + "\n"
            
        ptStr = ''
        for  pt in coordinates:
            ptStr = ptStr + '%.4f'%pt.X + '  ' + '%.4f'%pt.Y + '  ' + '%.4f'%pt.Z + '\n'
        ptStr = ptStr + '\n'
        
        # check for polygons with only two points.
        # Yes! it is possible. Import a model from REVIT/SketchUp and create some breps out of it
        # and you will get some!
        if len(coordinates) < 3:
            comment = " Polygon " + surface.name + " has less than 3 vertices and is removed by Honeybee.\n"
            return "#" + comment
        
        return srfStr + ptStr

    def RADSurface(self, surface):
        fullStr = ''
        # base surface coordinates
        coordinatesList = surface.extractPoints(1, True)
        
        if coordinatesList:
            if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
                coordinatesList = [coordinatesList]
                
            for count, coordinates in enumerate(coordinatesList):
                endCoordinate = rc.Geometry.Point3d.Add(coordinates[-1], rc.Geometry.Vector3d(0,0,0))
                if surface.hasChild:
                    glzCoordinateLists = surface.extractGlzPoints(True)
                    for glzCount, glzCoorList in enumerate(glzCoordinateLists):
                        # glazingStr
                        fullStr = fullStr + self.getsurfaceStr(surface.childSrfs[0], glzCount, glzCoorList)
                        
                        # shift glazing list
                        glzCoorList = self.shiftList(glzCoorList)
                        coordinates.extend(glzCoorList)
                        coordinates.append(glzCoorList[0])
                    coordinates.extend([endCoordinate, coordinates[0]])
                fullStr = fullStr + self.getsurfaceStr(surface, count, coordinates)
            return fullStr
        else:
            print "one of the surfaces is not exported correctly"
            return ""
            
    def RADNonPlanarSurface(self, surface):
        fullStr = ''
        
        # replace the geometry with the punched geometry
        # for planar surfaces with multiple openings
        try:
            if surface.punchedGeometry!=None:
                surface.geometry = surface.punchedGeometry
                surface.hasInternalEdge = True
        except:
            #print e
            # nonplanar surfaces with no openings
            pass
            
        # base surface coordinates
        coordinatesList = surface.extractPoints(1, True)

        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        for count, coordinates in enumerate(coordinatesList):
            #print count
            fullStr = fullStr + self.getsurfaceStr(surface, count, coordinates)
        
        return fullStr
    
    def RADNonPlanarChildSurface(self, surface):
        fullStr = ''
        
        # I should test this function before the first release!
        # Not sure if it will work for cases generated only by surface
        # should probably check for meshed surface and mesh the geometry
        # in case it is not meshed
        
        # base surface coordinates
        coordinatesList = surface.extractGlzPoints(True)
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        for glzCount, glzCoorList in enumerate(coordinatesList):
            # glazingStr
            fullStr = fullStr + self.getsurfaceStr(surface.childSrfs[0], glzCount, glzCoorList)
        return fullStr
            
class hb_WriteRADAUX(object):
    
    def __init__(self):
        self.hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.hb_serializeObjects = sc.sticky["honeybee_SerializeObjects"]
        self.hb_dsParameters = sc.sticky["honeybee_DSParameters"]()
        
        self.radSkyCondition = {0: '-u',
                       1: '-c',
                       2: '-i',
                       3: '+i',
                       4: '-s',
                       5: '+s'}
        
        self.DLAnalaysisTypes = {0: ["0: illuminance" , "lux"],
                      1: ["1: radiation" , "wh/m2"],
                      1.1: ["1.1: cumulative radiation" , "kWh/m2"],
                      2: ["2: luminance" , "cd/m2"],
                      3: ["3: DF", "%"],
                      4: ["4: VSC", "%"],
                      5: ["5: annual analysis", "var"]}
        
    def readAnalysisRecipe(self, analysisRecipe):
        
        self.analysisType = analysisRecipe.type
        self.radParameters = analysisRecipe.radParameters
        self.backupImages = 0 # will change to 1 or 2 in case the user set it to another number for image-based analysis
        self.numOfIllFiles = 1
        
        if self.radParameters==None:
            quality = 0
            self.radParameters = {}
            print "Default values are set for RAD parameters"
            for key in self.hb_radParDict.keys():
                #print key + " is set to " + str(hb_radParDict[key][quality])
                self.radParameters[key] = self.hb_radParDict[key][quality]
        
        if self.analysisType == 0:
            print "Image-based simulation"
            self.radSkyFileName = analysisRecipe.skyFile
            self.rhinoViewNames = analysisRecipe.viewNames
            self.cameraType = analysisRecipe.cameraType
            self.imageSize = analysisRecipe.imageSize
            self.simulationType = analysisRecipe.simulationType
            self.studyFolder = analysisRecipe.studyFolder
            self.sectionPlane = analysisRecipe.sectionPlane
            self.backupImages = analysisRecipe.backupImages
        
        elif self.analysisType == 1:
            print "Grid-based Radiance simulation"
            self.radSkyFileName = analysisRecipe.skyFile
            self.testPoints = analysisRecipe.testPts
            self.ptsNormals = analysisRecipe.vectors
            self.simulationType = analysisRecipe.simulationType
            self.studyFolder = analysisRecipe.studyFolder
            self.testMesh = analysisRecipe.testMesh
            
        elif self.analysisType == 2:
            print "Annual climate-based analysis"
            self.epwFileAddress = analysisRecipe.weatherFile 
            self.testPoints = analysisRecipe.testPts
            self.ptsNormals = analysisRecipe.vectors
            self.testMesh = analysisRecipe.testMesh
            
            if analysisRecipe.DSParameters == None:
                analysisRecipe.DSParameters = self.hb_dsParameters
                
            self.runAnnualGlare = analysisRecipe.DSParameters.runAnnualGlare
            self.onlyAnnualGlare = analysisRecipe.DSParameters.onlyAnnualGlare
            self.annualGlareViews = analysisRecipe.DSParameters.RhinoViewsName
            self.outputUnits = analysisRecipe.DSParameters.outputUnits
            self.adaptiveZone = analysisRecipe.DSParameters.adaptiveZone
            self.dgp_imageSize = analysisRecipe.DSParameters.dgp_imageSize
            self.dynamicShadingRecipes = analysisRecipe.DSParameters.DShdR
            self.numOfIllFiles = analysisRecipe.DSParameters.numOfIll
            
            self.studyFolder = analysisRecipe.studyFolder
        
        elif self.analysisType == 3:
            print "Daylight factor"
            self.radSkyFileName = analysisRecipe.skyFile
            self.testPoints = analysisRecipe.testPts
            self.ptsNormals = analysisRecipe.vectors
            self.simulationType = analysisRecipe.simulationType
            self.studyFolder = analysisRecipe.studyFolder
            self.testMesh = analysisRecipe.testMesh
            
        elif self.analysisType == 4:
            print "Vertical Sky Component"
            self.radSkyFileName = analysisRecipe.skyFile
            self.testPoints = analysisRecipe.testPts
            self.ptsNormals = analysisRecipe.vectors
            self.simulationType = analysisRecipe.simulationType
            self.studyFolder = analysisRecipe.studyFolder
            self.testMesh = analysisRecipe.testMesh
    
    def checkInputParametersForGridBasedAnalysis(self):
        
        if self.analysisType == 0:
            # this is an image-based analysis
            return
        
        print "The component is checking ad, as, ar and aa values. " + \
              "This is just to make sure that the results are accurate enough."
        
        if self.radParameters["_ad_"] < 1000:
            self.radParameters["_ad_"] = 1000
            print "-ad is set to 1000."
        
        if self.radParameters["_as_"] < 20:
            self.radParameters["_as_"] = 20
            print "-as is set to 20."
        
        if self.radParameters["_ar_"] < 300:
            # setting up the ar to 300 is tricky but I'm pretty sure in many
            # cases there will shadings involved.
            self.radParameters["_ar_"] = 300
            print "-ar is set to 300."
        
        if self.radParameters["_aa_"] > 0.1:
            # the same here. I think it is good to let the user wait a little bit more
            # but have a result that makes sense. If you are an exprienced user and don't
            # like this feel free to remove the if condition. Keep in mind that I only
            # apply this for grid based analysis, so the images can be rendered with any quality
            self.radParameters["_aa_"] = 0.1
            print "-aa is set to 0.1"
            
        print "Good to go!"
    
    def prepareWorkingDir(self, workingDir, radFileName = None, overwriteResults = True, analysisRecipe = None):
        
        if analysisRecipe == None:
            studyFolder = self.studyFolder
            analysisType = self.analysisType
            
            if analysisType == 0:
                backupImages = self.backupImages
            
        else:
            studyFolder = analysisRecipe.studyFolder
            analysisType = analysisRecipe.type
            if analysisType == 0:
                backupImages = analysisRecipe.backupImages
            
            
        if workingDir:
            workingDir = self.lb_preparation.removeBlankLight(workingDir)
        else:
            workingDir = sc.sticky["Honeybee_DefaultFolder"]
        
        workingDir = self.lb_preparation.makeWorkingDir(workingDir)
        
        # make sure the directory has been created
        if workingDir == -1: return -1
        workingDrive = workingDir[0:1]
        
        ## check for the name of the file
        if radFileName == None: radFileName = 'unnamed'
        
        # make sure radfile name is a valid address
        keepcharacters = ('.','_')
        radFileName = "".join([c for c in radFileName if c.isalnum() or c in keepcharacters]).rstrip()
        
        # make new folder for each study
        subWorkingDir = self.lb_preparation.makeWorkingDir(workingDir + "\\" + radFileName + studyFolder).replace("\\\\", "\\")
        print 'Current working directory is set to: ', subWorkingDir
        
        if os.path.exists(subWorkingDir):
            if analysisType == 0:
                # for image-based analysis there is an option to backup the images
                if backupImages != 0:
                    # create the backup folder and copy the images to the folder
                    imageFolder = workingDir + "\\" + radFileName + "\\imagesBackup"
                    
                    if not os.path.exists(imageFolder): os.mkdir(imageFolder)
                    
                    # copy the files into the folder
                    imageExtensions = ["JPEG", "JPG", "GIF", "TIFF", "TIF", "HDR", "PIC"]
                    timeID = self.getTime()
                    fileNames = os.listdir(subWorkingDir)
                    
                if backupImages == 1:
                    # keep all the files in the same folder
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            newFileName = (".").join(fileName.split(".")[:-1])
                            extension = fileName.split(".")[-1]
                            newFullName = newFileName + "_" + timeID + "." + extension
                            self.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder, newFullName) , True)
                    
                elif backupImages == 2:
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            if not os.path.exists(imageFolder + "\\" + timeID):
                                os.mkdir(imageFolder + "\\" + timeID)
                            # copy the files to image backup folder with data and time added
                            self.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder + "\\" + timeID, fileName) , True)
            try:
                if not overwriteResults:
                    fileNames = os.listdir(subWorkingDir)
                    
                    mainBackupFolder = subWorkingDir[:-1] + "_backup"
                    
                    counter = 0
                    backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    while os.path.isdir(backupFolder):
                        counter += 1
                        backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    os.mkdir(backupFolder)
                    
                    for fileName in fileNames:
                        try:
                            # copy the files to image backup folder with data and time added
                            self.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(backupFolder, fileName) , True)                    
                        except:
                            pass
                    
                    print "Results of the previous study are copied to " + backupFolder
                    
                self.lb_preparation.nukedir(subWorkingDir, rmdir = False)
                
            except Exception, e:
                print 'Failed to remove the old directory.'
                print `e`
            
        return subWorkingDir, radFileName
    
    def exportTestMesh(self, subWorkingDir, radFileName, analysisRecipe = None):
        
        if analysisRecipe != None:
            analysisType = analysisRecipe.type
            if analysisType ==0: return
            testMesh = analysisRecipe.testMesh
        else:
            analysisType = self.analysisType
            if analysisType ==0: return
            testMesh = self.testMesh
            
        # try to write mesh file if any
        if analysisType != 0 and testMesh !=[]:
            meshFilePath = os.path.join(subWorkingDir, radFileName + ".msh")
            serializer = self.hb_serializeObjects(meshFilePath, testMesh)
            serializer.saveToFile()

    def exportTypeFile(self, subWorkingDir, radFileName, analysisRecipe):
        
        analysisType = analysisRecipe.type
        
        if analysisType == 3 or analysisType == 4:
            analysisTypeKey = analysisType
        
        elif analysisType == 0 or analysisType == 1:
            analysisTypeKey = analysisRecipe.simulationType
        
        elif analysisType == 2:
            # annual analysis
            analysisTypeKey = 5
                
        # try to write mesh file if any
        typeFile = os.path.join(subWorkingDir, radFileName + ".typ")
        
        with open(typeFile, "w") as typf:
            typf.write(str(analysisTypeKey))
    
    
    def copySkyFile(self, subWorkingDir, radFileName, analysisRecipe = None):
        
        if analysisRecipe != None:
            analysisType = analysisRecipe.type
            if analysisType == 2: return
            radSkyFileName = analysisRecipe.radSkyFileName
        else:
            analysisType = self.analysisType
            if analysisType == 2: return
            radSkyFileName = self.radSkyFileName
      
        skyTempName = radSkyFileName.split("\\")[-1]
        skyName = skyTempName.split("/")[-1]
        
        self.copyFile(radSkyFileName, subWorkingDir + "\\" + skyName, True)
        radSkyFileName = os.path.join(subWorkingDir, skyName)
        
        return radSkyFileName
        
    def getTime(self):
        
        def addZero(number):
            if len(str(number)) == 1:
                return "0" + str(number)
            else:
                return str(number)
        
        year, month, day, hour, minute, second = time.localtime()[0:6]
        
        now = addZero(hour) + "_" + addZero(minute) + "_" + addZero(second)
    
        date = addZero(year) + "_" +  addZero(month)  + "_" + addZero(day)
    
        return date + "at" + now
    
    def copyFile(self, inputFile, destinationFullpath, overwrite = False):
        if overwrite: shutil.copyfile(inputFile, destinationFullpath)
        elif not os.path.isfile(destinationFullpath): shutil.copyfile(inputFile, destinationFullpath)
    
    def RADLocation(self, epw_file):
        epwfile = open(epw_file,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        while 1>0: #remove empty cells from the end of the list if any
            try: float(csheadline[-1]); break
            except: csheadline.pop()
        locName = ''
        for hLine in range(1,4):
            if csheadline[hLine] != '-':
                locName = locName + csheadline[hLine].strip() + '_'
        locName = locName[:-1].strip()
        lat = csheadline[-4]
        lngt = csheadline[-3]
        timeZone = csheadline[-2]
        elev = csheadline[-1].strip()
        epwfile.close()
        
        return locName, lat, lngt, timeZone, elev
    
    def RADRadiationSky(self, projectName):
        return  "# start of sky definition for radiation studies\n" + \
                "void brightfunc skyfunc\n" + \
                "2 skybright " + projectName + ".cal\n" + \
                "0\n" + \
                "0\n" + \
                "skyfunc glow sky_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 1 1 0\n" + \
                "sky_glow source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 1 180\n" + \
                "# end of sky definition for radiation studies\n\n"
    
    def RADDaylightingSky(self, epwFileAddress, skyCondition, time, month, day):
        locName, lat, long, timeZone, elev = self.RADLocation(epwFileAddress)
        return  "# start of sky definition for daylighting studies\n" + \
                "# location name: " + locName + " LAT: " + lat + "\n" + \
                "!gensky " + `month` + ' ' + `day` + ' ' + `time` + ' ' + self.radSkyCondition[skyCondition] + \
                " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + "\n" + \
                "skyfunc glow sky_mat\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 1 1 0\n" + \
                "sky_mat source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 1 180\n" + \
                "skyfunc glow ground_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 .8 .5 0\n" + \
                "ground_glow source ground\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 -1 180\n" + \
                "# end of sky definition for daylighting studies\n\n"
                    
                    
    def exportView(self, viewName, radParameters, cameraType, imageSize, sectionPlane = None, nXDiv = 1, nYDiv = 1, vs = 0, vl = 0):
        
        if viewName in rs.ViewNames():
            viewName = rs.CurrentView(viewName, True)
        else:
            # change to RhinoDoc to get access to NamedViews
            sc.doc = rc.RhinoDoc.ActiveDoc
            namedViews = rs.NamedViews()
            if viewName in namedViews:
                viewName = rs.RestoreNamedView(viewName)
            else:
                viewName = None
            # change back to Grasshopper
            sc.doc = ghdoc
            viewName = rs.CurrentView(viewName, True)
        
        if viewName == None:
            print "Illegal view name!"
            viewName = "Perspective"
            
        # Read camera type 0: Perspective, 1: fisheye, 2: parallel
        try: cameraType = int(cameraType)
        except:
            if sc.doc.Views.ActiveView.ActiveViewport.IsPerspectiveProjection: cameraType = 0
            elif sc.doc.Views.ActiveView.ActiveViewport.IsParallelProjection: cameraType = 2
        
        # paralell view sizes
        viewHSizeP = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Width)
        viewVSizeP = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Height)
        
        # read image size
        viewHSize = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Width)
        viewVSize = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Height)
        # print viewHSize, viewVSize
        userInputH = imageSize[0]
        userInputV = imageSize[1]
        if userInputH != None and userInputV != None:
            try:
                viewHSize = float(userInputH)
                viewVSize = float(userInputV)
            except:
                print "Illegal input for view size."
                pass
        elif userInputH == None and userInputV != None:
            try:
                viewHSize = viewHSize * (userInputV/viewVSize)
                viewVSize = float(userInputV)
            except:
                print "Illegal input for view size."
                pass
        elif userInputH != None and userInputV == None:
            try:
                viewVSize = viewVSize * (userInputH/viewHSize)
                viewHSize = float(userInputH)
            except:
                print "Illegal input for view size."
                pass
        
        # print viewHSize, viewVSize
        viewPoint = sc.doc.Views.ActiveView.ActiveViewport.CameraLocation
        viewDirection = sc.doc.Views.ActiveView.ActiveViewport.CameraDirection
        viewDirection.Unitize()
        viewUp = sc.doc.Views.ActiveView.ActiveViewport.CameraUp
        
        viewUp.Unitize()
        try:
            viewHA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumRightPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumLeftPlane()[1][1])
        except:
            viewHA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumRightPlane()[1].Normal, sc.doc.Views.ActiveView.ActiveViewport.GetFrustumLeftPlane()[1].Normal)
        
        if viewHA == 0: viewHA = 180
        try:
            viewVA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumBottomPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumTopPlane()[1][1])
        except:
            viewVA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumBottomPlane()[1].Normal, sc.doc.Views.ActiveView.ActiveViewport.GetFrustumTopPlane()[1].Normal)
        
        if viewVA == 0: viewVA = 180
        PI = math.pi
        
        if cameraType == 2:
            # Thank you to Brent Watanabe for the great discussion, and his help in figuring this out
            # I should find the bounding box of the geometry and set X and Y based of that!
            if nXDiv != 1:
                viewHSizeP = viewHSizeP/nXDiv
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVSizeP = viewVSizeP/nYDiv
                viewVSize = viewVSize/nYDiv
                
            view = "-vtl -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + \
               " -vh " + `int(viewHSizeP)` + " -vv " + `int(viewVSizeP)` + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + \
               " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
               
        elif cameraType == 0:
            # perspective
            
            # recalculate vh and vv
            if nXDiv != 1:
                viewHA = (2.*180./PI)*math.atan(((PI/180./2.) * viewHA)/nXDiv)
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVA = (2.*180./PI)*math.atan(math.tan((PI/180./2.)*viewVA)/nYDiv)
                viewVSize = viewVSize/nYDiv
            
            view = "-vtv -vp " + \
               "%.3f"%viewPoint[0] + " " + "%.3f"%viewPoint[1] + " " + "%.3f"%viewPoint[2] + " " + \
               " -vd " + "%.3f"%viewDirection[0] + " " + "%.3f"%viewDirection[1] + " " + "%.3f"%viewDirection[2] + " " + \
               " -vu " + "%.3f"%viewUp[0] + " " +  "%.3f"%viewUp[1] + " " + "%.3f"%viewUp[2] + " " + \
               " -vh " + "%.3f"%viewHA + " -vv " + "%.3f"%viewVA + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
        
        elif cameraType == 1:
            # fish eye
            # recalculate vh and vv
            viewHA = 180
            viewVA = 180
            if nXDiv != 1:
                viewHA = (2.*180./PI)*math.asin(math.sin((PI/180./2.)*viewHA)/nXDiv)
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVA = (2.*180./PI)*math.asin(math.sin((PI/180./2.)*viewVA)/nYDiv)
                viewVSize = viewVSize/nYDiv
            
            view = "-vth -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + " " + \
               " -vh " + "%.3f"%viewHA + " -vv " + "%.3f"%viewVA + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
        
        if sectionPlane!=None:
            # map the point on the plane
            pointOnPlane = sectionPlane.ClosestPoint(viewPoint)
            distance = pointOnPlane.DistanceTo(viewPoint)
            view += " -vo " + str(distance)
            
        return view + " "
    
    def oconvLine(self, octFileName, radFilesList):
        # sence files
        r = 1024 * 2
        senceFiles = ""
        for address in radFilesList: senceFiles = senceFiles + address.replace("\\" , "/") + " "
        
        line = "oconv -r " + str(r) + " -f " +  senceFiles + " > " + octFileName + ".oct\n"
        
        return line
    
    def overtureLine(self, view, projectName, viewName, radParameters, analysisType = 0):
        octFile = projectName + ".oct"
        ambFile = projectName + ".amb" #amb file is view independent and can be used globally
        unfFile = projectName + ".unf" 
        
        if analysisType==0:
            # illuminance (lux)
            line0 = "rpict -i "
        elif analysisType==2:
            # luminance (cd)
            line0 = "rpict "
        else:
            # radiation analysis
            line0 = "rpict -i "
        
        line1 = "-t 10 "+ \
                view + " -af " + ambFile +  " " + \
                " -ps " + str(radParameters["_ps_"]) + " -pt " + str(radParameters["_pt_"]) + \
                " -pj " + str(radParameters["_pj_"]) + " -dj " + str(radParameters["_dj_"]) + \
                " -ds " + str(radParameters["_ds_"]) + " -dt " + str(radParameters["_dt_"]) + \
                " -dc " + str(radParameters["_dc_"]) + " -dr " + str(radParameters["_dr_"]) + \
                " -dp " + str(radParameters["_dp_"]) + " -st " + str(radParameters["_st_"])  + \
                " -ab " + `radParameters["_ab_"]` + \
                " -ad " + `radParameters["_ad_"]` + " -as " +  `radParameters["_as_"]` + \
                " -ar " + `radParameters["_ar_"]` + " -aa " +  '%.3f'%radParameters["_aa_"] + \
                " -lr " + `radParameters["_lr_"]`  + " -lw " + '%.3f'%radParameters["_lw_"] + " -av 0 0 0 " + \
                " " + octFile + " > " + unfFile + "\n"
    
        line2 = "del " + unfFile + "\n"
        
        return line0 + line1 + line2

    def rpictLine(self, view, projectName, viewName, radParameters, analysisType = 0, cpuCount = 0):
        octFile = projectName + ".oct"
        ambFile = projectName + ".amb" #amb file is view independent and can be used globally
        unfFile = projectName + "_" + viewName + "_" + `cpuCount` + ".unf" 
        outputFile = projectName + "_" + viewName + "_" + `cpuCount` + ".HDR"
        
        if analysisType==0:
            # illuminance (lux)
            line0 = "rpict -i "
        elif analysisType==2:
            # luminance (cd)
            line0 = "rpict "
        else:
            # radiation analysis
            line0 = "rpict -i "
        
        line1 = "-t 10 "+ \
                view + " -af " + ambFile +  " " + \
                " -ps " + str(radParameters["_ps_"]) + " -pt " + str(radParameters["_pt_"]) + \
                " -pj " + str(radParameters["_pj_"]) + " -dj " + str(radParameters["_dj_"]) + \
                " -ds " + str(radParameters["_ds_"]) + " -dt " + str(radParameters["_dt_"]) + \
                " -dc " + str(radParameters["_dc_"]) + " -dr " + str(radParameters["_dr_"]) + \
                " -dp " + str(radParameters["_dp_"]) + " -st " + str(radParameters["_st_"])  + \
                " -ab " + `radParameters["_ab_"]` + \
                " -ad " + `radParameters["_ad_"]` + " -as " +  `radParameters["_as_"]` + \
                " -ar " + `radParameters["_ar_"]` + " -aa " +  '%.3f'%radParameters["_aa_"] + \
                " -lr " + `radParameters["_lr_"]`  + " -lw " + '%.3f'%radParameters["_lw_"] + " -av 0 0 0 " + \
                " " + octFile + " > " + unfFile + "\n"
    
        line2 = "pfilt -1 -r .6 -x/2 -y/2 " + unfFile + " > " + outputFile + "\n"
        
        return line0 + line1 + line2
        
        
    def falsecolorLine(self, projectName, viewName):
        line = "c:\python27\python c:\honeybee\\falsecolor2.py -i " + projectName + "_RAD_" + viewName + "_RadStudy.pic -s auto -n 10 -mask 0.1 -l kWhm-2 -z > " + projectName + "_" + viewName + "_FalseColored.pic\n" + \
           "ra_tiff " + projectName + "_" + viewName + "_FalseColored.pic " + projectName + "_" + viewName + "_FalseColored.tif\n" + \
           "ra_gif " + projectName + "_" + viewName + "_FalseColored.pic " + projectName + "_" + viewName + "_FalseColored.gif\n"
        return line

    def rtraceLine(self, projectName, octFileName, radParameters, simulationType = 0, cpuCount = 0):
        ptsFile = projectName + "_" + str(cpuCount) + ".pts"
        outputFile = projectName + "_" + str(cpuCount) + ".res"
        if simulationType == 0:
            line0 = "rtrace -I "
        elif simulationType == 2:
            line0 = "rtrace "
        else:
            # print "Fix this for radiation analysis"
            line0 = "rtrace -I "
            
        line1 = " -h -dp " + str(radParameters["_dp_"]) + \
                " -ds " + str(radParameters["_ds_"]) + " -dt " + str(radParameters["_dt_"]) + \
                " -dc " + str(radParameters["_dc_"]) + " -dr " + str(radParameters["_dr_"]) + \
                " -st " + str(radParameters["_st_"]) + " -lr " + str(radParameters["_lr_"]) + \
                " -lw " + str(radParameters["_lw_"]) + " -ab " + str(radParameters["_ab_"]) + \
                " -ad " + str(radParameters["_ad_"]) + " -as " + str(radParameters["_as_"]) + \
                " -ar " + str(radParameters["_ar_"]) + " -aa " + str(radParameters["_aa_"]) + \
                " " + octFileName + ".oct < " + ptsFile + \
                " > " + outputFile + "\n"
        
        return line0 + line1
        
    def testPtsStr(self, testPoint, ptsNormal):
        return  '%.4f'%testPoint.X + '\t' + \
                '%.4f'%testPoint.Y + '\t' + \
                '%.4f'%testPoint.Z + '\t' + \
                '%.4f'%ptsNormal.X + '\t' + \
                '%.4f'%ptsNormal.Y + '\t' + \
                '%.4f'%ptsNormal.Z + '\n'
        

    def readRadiationResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile: result.append(float(line.split('	')[0])*179)
        return result
    
    def readDLResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile:
            R, G, B = line.split('	')[0:3]
            result.append( 179 * (.265 * float(R) + .67 * float(G) + .065 * float(B)))
        return result
    
    def isSrfAirWall(self, HBSrf):
        # This can be tricky since some of interior walls may or may not be air walls
        if HBSrf.type == 4:
            return True
        else:
            return False
    
    def isSrfInterior(self, HBSrf):
        # This can be tricky since some of interior walls may or may not be air walls
        if HBSrf.type == 0 and HBSrf.BC.lower() == "surface":
            return True
        else:
            return False
        
class hb_WriteDS(object):
    
    def isSensor(self, testPt, sensors):
        for pt in sensors:
            if pt.DistanceTo(testPt) < sc.doc.ModelAbsoluteTolerance:
                # this is a senor point
                return True
        # not a sensor
        return False
    
    def DSHeadingStr(self, projectName, subWorkingDir, tempFolder, hb_DSPath, cpuCount = 0):
        return   '#######################################\n' + \
                 '#DAYSIM HEADING - GENERATED BY HONEYBEE\n' + \
                 '#######################################\n' + \
                 'project_name       ' + projectName + '_' + `cpuCount` + '\n' + \
                 'project_directory  ' + subWorkingDir + '\\\n' + \
                 'bin_directory      ' + hb_DSPath + '\\bin\\\n' + \
                 'tmp_directory      ' + tempFolder + '\\\n' + \
                 'Template_File      ' + hb_DSPath + '\\template\\DefaultTemplate.htm\n'
                 
    
    def DSLocationStr(self, hb_writeRADAUX,  lb_preparation, epwFileAddress):
        # location information
        locName, lat, long, timeZone, elev = hb_writeRADAUX.RADLocation(epwFileAddress)
        locName = locName.replace("/", "_")
        
        return'\n\n#################################\n' + \
                  '#      LOCATION INFORMATION      \n' + \
                  '#################################\n' + \
                  'place                     ' + lb_preparation.removeBlankLight(locName) + '\n' + \
                  'latitude                  ' + lat + '\n' + \
                  'longitude                 ' + `-float(long)` + '\n' + \
                  'time_zone                 ' + `-15 * float(timeZone)` + '\n' + \
                  'site_elevation            ' + elev + '\n' + \
                  'time_step                 ' + '60\n' + \
                  'wea_data_short_file       ' + lb_preparation.removeBlankLight(locName) + '.wea\n' + \
                  'wea_data_short_file_units ' + '1\n' + \
                  'lower_direct_threshold    ' + '2\n' + \
                  'lower_diffuse_threshold   ' + '2\n', locName
        
    def DSAnalysisUnits(self, outputUnits, pointsCount):
        # I notice that setting output_units to 1 return all 0 results and not the radiation values
        # however assigning type 2 for each point using sensor_file_unit works! I think this is a bug
        # in Daysim that I should report to the email list next week when I come back from Chicago.
        
        outputUnits = outputUnits[0]
        
        if outputUnits == 2:
            return 'output_units              ' + `outputUnits` + '\n'
        
        elif outputUnits == 1:
            
            outputStr = "sensor_file_unit"
            
            for pt in range(pointsCount): outputStr += " 2"
            
            return outputStr +"\n"
            
    # building information
    def DSBldgStr(self, projectName, materialFileName, radFileFullName, adaptiveZone, \
                  dgp_image_x = 500, dgp_image_y = 500, cpuCount = 0, northAngle = 0, additionalFileNames = []):
        
        # add additional rad files to scene
        radFilesLength = str(2 + len(additionalFileNames))
        radFileNames = ", ".join([radFilesLength, materialFileName, radFileFullName] + additionalFileNames)
        
        return'\n\n#################################\n' + \
                  '#      BUILDING INFORMATION      \n' + \
                  '#################################\n' + \
                  'material_file          Daysim_material_' + projectName + '.rad\n' + \
                  'geometry_file          Daysim_'+ projectName + '.rad\n' + \
                  'radiance_source_files  ' + radFileNames + '\n' + \
                  'sensor_file            ' + projectName + '_' + `cpuCount` + '.pts\n' + \
                  'viewpoint_file         ' + projectName + '_' + 'annualGlareView.vf\n' + \
                  'AdaptiveZoneApplies    ' + `adaptiveZone` + '\n' + \
                  'dgp_image_x_size       ' + `dgp_image_x` + '\n' + \
                  'dgp_image_y_size       ' + `dgp_image_y` + '\n' + \
                  'scene_rotation_angle ' + `northAngle` + '\n'
    
    # radiance parameters
    def DSRADStr(self, radParameters):
        return '\n\n#################################\n' + \
                  '#       RADIANCE PARAMETERS      \n' + \
                  '#################################\n' + \
                  'ab ' + `radParameters["_ab_"]` + '\n' + \
                  'ad ' + `radParameters["_ad_"]` + '\n' + \
                  'as ' + `radParameters["_as_"]` + '\n' + \
                  'ar ' + `radParameters["_ar_"]` + '\n' + \
                  'aa ' + `radParameters["_aa_"]` + '\n' + \
                  'lr 6\n' + \
                  'st 0.1500\n' + \
                  'sj 1.0000\n' + \
                  'lw 0.0040000\n' + \
                  'dj 0.0000\n' + \
                  'ds 0.200\n' + \
                  'dr 2\n' + \
                  'dp 512\n'
                          
    def DSDynamicSimStr(self, shadingRecipes, projectName, subWorkingDir, testPts, cpuCount = 0):
        
        dynOptStr = '\n==========================\n' + \
                    '= shading control system\n' + \
                    '==========================\n'
        
        numOfDynamicShadings = 0
        # find number of dynamic shadings
        for shadingRecipe in shadingRecipes:
            if shadingRecipe.type == 2:
                numOfDynamicShadings += 1

        dynamicShdHeading ='shading -' + str(numOfDynamicShadings) + '\n' + \
                    projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '.ill\n'
        
        dynamicCounter = 0
        for recipeCount, shadingRecipe in enumerate(shadingRecipes):
            name = shadingRecipe.name
            type = shadingRecipe.type
            if type == 1:
                # no dynamic blind
                sensorPts = []
                dynamicShd ='shading ' + str(type) + ' ' + name + ' ' + projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '.ill\n' + \
                            '\n'
            elif type == 0:
                # conceptual dynamic shading
                sensors = shadingRecipe.sensorPts
                dynamicShd ='shading ' + str(type) + '\n' + \
                            name + '_' + str(recipeCount+1) + ' ' + projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '_up.ill\n' + \
                            projectName + '_' + `cpuCount` + '_down.ill\n\n'
                            
            elif type == 2:
                dynamicCounter += 1
                dynamicShd = ""
                
                # advanced dynamic shading
                glareControlRecipe = shadingRecipe.glareControlR
                shadingStates = shadingRecipe.shadingStates
                controlSystem = shadingRecipe.controlSystem
                # sensors = shadingRecipe.sensorPts #sensors are removed from this part and will be added later for the analysis
                coolingPeriod = shadingRecipe.coolingPeriod
                
                # add the heading for the first dynamic shading group
                if dynamicCounter == 1: dynamicShd = dynamicShdHeading
                groupName = name
                
                if controlSystem == "ManualControl":
                    dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "ManualControl " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                    
                    for stateCount in range(1, len(shadingStates)):
                        dynamicShd += subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                      groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                      groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                
                elif controlSystem == "AutomatedThermalControl":
                    if glareControlRecipe!=None:
                        controlSystem = "AutomatedGlareControl"
                        exteriorSensor = glareControlRecipe.exteriorSensor
                        threshold = glareControlRecipe.threshold
                        minAz = glareControlRecipe.minAz
                        maxAz = glareControlRecipe.maxAz
                        minAlt = glareControlRecipe.minAltitude
                        maxAlt = glareControlRecipe.maxAltitude
                        
                    if len(coolingPeriod)!=0:
                        stMonth, stDay, hour = coolingPeriod[0]
                        endMonth, endDay, hour = coolingPeriod[1]
                        
                        controlSystem += "WithOccupancy"
                    
                    if controlSystem == "AutomatedThermalControl":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedThermalControl " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                # empty shading states
                                pass
                    
                    elif controlSystem == "AutomatedThermalControlWithOccupancy":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedThermalControlWithOccupancy " + \
                                  `stMonth` + " " + `stDay` + " " + `endMonth` + " " + `endDay` + " " + \
                                  subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                                
                    elif controlSystem == "AutomatedGlareControl":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedGlareControl \n" + \
                                  `int(threshold)` + " " + `int(minAz)` + " " + `int(maxAz)` + " " + \
                                  `int(minAlt)` + " " + `int(maxAlt)` + " " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                    
                    elif controlSystem == "AutomatedGlareControlWithOccupancy":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedGlareControlWithOccupancy \n" + \
                                  `int(threshold)` + " " + `int(minAz)` + " " + `int(maxAz)` + " " + \
                                  `int(minAlt)` + " " + `int(maxAlt)` + "\n" + \
                                  `stMonth` + " " + `stDay` + " " + `endMonth` + " " + `endDay` + " " + \
                                  subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                    
                    
            dynOptStr += dynamicShd
        
        
        # I removed the sensor point from here as it wasn't really nessecay to 
        # apply it here and it was also 
        
        #sensorInfoStr = 'sensor_file_info'
        #if type == 0 or type == 2:
        #    for pt in testPts:
        #        if self.isSensor(pt, sensors):
        #            sensorInfoStr += ' BG' + str(recipeCount+1)
        #        # if BG1_Ext
        #        # add external sensor_ This should happen inside the loop for each group
        #        # as the point maybe part of multiple shading groups
        #        else:
        #            sensorInfoStr += ' 0'
        #        
        #else:
        #    for pt in testPts: sensorInfoStr += ' 0'
        #
        #dynOptStr += sensorInfoStr
        
        #'==========================\n' + \
        #'= electric lighting system\n' + \
        #'==========================\n' + \
        #'electric_lighting_system 2\n' + \
        #'   4 manual_dimming    100 1 0.0 20 300\n' + \
        #'   1 manual_control    200 1\n' + \
        #'\n' + \
        #'sensor_file_info '
        #for pt in range(lenOfPts[cpuCount]): dynOptStr = dynOptStr + '0 '
        
        return dynOptStr + '\n'
    
    
    def resultStr(self, projectName, cpuCount):
        return  '\n\n######################\n' + \
                '# daylighting results \n' + \
                '######################\n' + \
                'daylight_autonomy_active_RGB ' + projectName + '_' + `cpuCount` + '_autonomy.DA\n' + \
                'electric_lighting ' + projectName + '_' + `cpuCount` + '_electriclighting.htm\n' + \
                'direct_sunlight_file ' + projectName  + '_' + `cpuCount` + '.dir\n' + \
                'thermal_simulation ' + projectName  + '_' + `cpuCount` + '_intgain.csv\n'


class hb_ReadAnnualResultsAux(object):
    
    def sortIllFiles(self, illFilesTemp):
        """
        This function sorts a list of *.ill for an annual study
        and put them in different branches based on shading groups and blind states
        ---------------------------------------------------------------------------
        {0}
        .ill files with no dynamic blinds. When there is no dynamic blinds or when
        there are advanced dynamic blind these files should look like:
            workingDir + ProjectName + "_" + CPUCount + ".ill"
        and should be sorted based on CPUCount.
        In case of conceptualBlinds the files will look like:
            workingDir + ProjectName + "_" + CPUCount + "_up.ill"
            
        {1,0}
         Branches with two numbers contain .ill files for shading groups with different
         states. First number represents the shading group (which starts from 1) and
         second number represents the state. For instance {1,0} includes .ill files
         for first shading group and the first state of the blinds which is the most
         open state. In case of simple blinds the file should look like:
            workingDir + ProjectName + "_" + CPUCount + "_down.ill"
         for advanced dynamic blinds the file should looks like:
             workingDir + ProjectName + "_" shadingGroupName + "_state_" + stateCount+ "_" + CPUCount + ".ill"
        """
        
        # check if there are multiple ill files in the folder for different shading groups
        illFilesDict = {}
        
        for fullPath in illFilesTemp:
            fileName = os.path.basename(fullPath)
            
            if fileName.split("_")[:-1]!= []:
                if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                    # conceptual blind
                    stateName = "_".join(fileName.split("_")[:-2]) + "_" + fileName.split("_")[-1]
                    if fileName.endswith("_up.ill"):
                        groupName = -1
                        stateName = "up"
                        stateNumber = 0
                    else:
                        groupName = "conceptualBlinds"
                        stateName = "down"
                        stateNumber = 0
                        
                elif fileName.Contains("_state_"):
                    # dynamic blinds with several states
                    groupName = "_".join(fileName.split("_")[:-3])
                    stateName = "_".join(fileName.split("_")[-3:-1])
                    stateNumber = fileName.split("_")[-2]
                else:
                    groupName = -1
                    stateName = "_".join(fileName.split("_")[:-1])
                    stateNumber = -1 # no states
            else:
                groupName = -1
                stateName = fileName
                stateNumber = -1 # no states
            
            # create an empty dictionary
            if groupName not in illFilesDict.keys():
                illFilesDict[groupName] = {}
            
            # create an empty dictionary for each state
            if stateName not in illFilesDict[groupName].keys():
                illFilesDict[groupName][stateName] = []
            
            # append the file to the list
            illFilesDict[groupName][stateName].append(fullPath)
        
        # sort the keys
        illFiles = DataTree[System.Object]()
        shadingGroupCount = 0
        
        for key, fileListDict in illFilesDict.items():
            stateCount = 0
            shadingGroupCount+=1
            for state, fileList in fileListDict.items():
                if key== -1:
                    p = GH_Path(0)
                    shadingGroupCount-=1
                else:
                    p = GH_Path(shadingGroupCount, stateCount)
                    stateCount+=1
                    
                try:
                    if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                        # conceptual blind
                        if fileList[0].endswith("_down.ill"):
                            p = GH_Path(1,0)
                        else:
                            p = GH_Path(0)
                        
                        illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-2])), p)
                    else:
                        illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1])), p)
                        
                except Exception, e:
                    # failed to sort!
                    illFiles.AddRange(fileList, p)
        
        return illFiles
    
class hb_EnergySimulatioParameters(object):
    
    def readEPParams(self, EPParameters):
        
        if EPParameters == [] or len(EPParameters)!=15:
            timestep = 6
            
            shadowPar = ["AverageOverDaysInFrequency", 30, 3000]
            
            solarDistribution = "FullInteriorAndExteriorWithReflections"
            
            simulationControl = [True, True, True, False, True, 25, 6]
            
            ddyFile = None
            
            terrain = 'City'
            
            grndTemps = []
        
        else:
            timestep = int(EPParameters[0])
            
            shadowPar = EPParameters[1:4]
            
            solarDistribution = EPParameters[4]
            
            simulationControl = EPParameters[5:12]
            
            ddyFile = EPParameters[12]
            
            terrain = EPParameters[13]
            
            grndTemps = EPParameters[14]
        
        return timestep, shadowPar, solarDistribution, simulationControl, ddyFile, terrain, grndTemps

class EPMaterialAux(object):
    
    def __init__(self):
        self.energyModelingStandards = {"0" : "ASHRAE 90.1-2004",
                                        "1" : "ASHRAE 90.1-2007",
                                        "2" : "ASHRAE 90.1-2010",
                                        "3" : "ASHRAE 189.1",
                                        "4" : "CBECS 1980-2004",
                                        "5" : "CBECS Before-1980",
                                        "ASHRAE9012004" : "ASHRAE 90.1-2004",
                                        "ASHRAE9012007" : "ASHRAE 90.1-2007",
                                        "ASHRAE9012010" : "ASHRAE 90.1-2010",
                                        "ASHRAE1891" : "ASHRAE 189.1",
                                        "CBECS19802004" : "CBECS 1980-2004",
                                        "CBECSBEFORE1980" : "CBECS Before-1980"}
    
    def calcEPMaterialUValue(self, materialObj, GHComponent = None):
        
        materialType = materialObj[0]
        
        if materialType.lower() == "windowmaterial:simpleglazingsystem":
            UValueSI = float(materialObj[1][0])
            
        elif materialType.lower() == "windowmaterial:glazing":
            thickness = float(materialObj[3][0])
            conductivity = float(materialObj[13][0])
            UValueSI = conductivity/thickness
            
        elif materialType.lower() == "material:nomass":
            # Material:NoMass is defined by R-Value and not U-Value
            UValueSI = 1 / float(materialObj[2][0])
            
        elif materialType.lower() == "material":
            thickness = float(materialObj[2][0])
            conductivity = float(materialObj[3][0])
            UValueSI = conductivity/thickness
        
        elif materialType.lower() == "material:airgap":
            UValueSI = 1 / float(materialObj[1][0])
            #print materialObj
            #print UValueSI
        
        elif materialType.lower() == "material:airgap":
            UValueSI = 1 / float(materialObj[1][0])
        
        elif materialType.lower() == "windowmaterial:gas":
            thickness = float(materialObj[2][0])
            if materialObj[1][0].lower() == "air":
                # conductivity = 0.1603675
                # considering ('0.18' for 'Thermal Resistance {m2-K/W}')
                UValueSI = 5.55555555556
            else:
                warningMsg = "Honeybee can't calculate the UValue for " + materialObj[1][0] + ".\n" + \
                    "Let us know if you think it is really neccesary and we will add it to the list. :)"
                if GHComponent!=None:
                    w = gh.GH_RuntimeMessageLevel.Warning
                    GHComponent.AddRuntimeMessage(w, warningMsg)
                    
                    print materialObj
        else:
            warningMsg = "Honeybee currently doesn't support U-Value calculation for " + materialType + ".\n" +\
                "Let us know if you think it is really neccesary and we will add it to the list. :)"
            if GHComponent!=None:
                w = gh.GH_RuntimeMessageLevel.Warning
                GHComponent.AddRuntimeMessage(w, warningMsg)
        
            # http://bigladdersoftware.com/epx/docs/8-0/input-output-reference/page-010.html
            UValueSI = -1
        
        return UValueSI
    
    def calcEPConstructionUValue(self, constructionObj, GHComponent=None):
        # find material layers
        uValues = []
        for layer in constructionObj.keys()[1:]:
            materialName, comment = constructionObj[layer]
            try: values, comments, UValueSI, UValueIP = self.decomposeMaterial(materialName, GHComponent)
            except: UValueSI = -1
            uValues.append(UValueSI)
        
        # calculate cumulative UValue
        totalRValue = 0
        for uValue in uValues:
            totalRValue += 1/uValue
        
        return 1/totalRValue
    
    def convertUValueToIP(self, UValueSI):
        return  0.176110 * UValueSI
    
    def convertUValueToSI(self, UValueIP):
        return  5.678263 * UValueIP
    
    def decomposeMaterial(self, matName, GHComponent = None):
        try:
            try:
                materialObj = sc.sticky["honeybee_materialLib"][matName.upper()]
            except:
                materialObj = sc.sticky["honeybee_windowMaterialLib"][matName.upper()]
                
            comments = []
            values = []
            
            #print matName
            for layer in materialObj.keys():
                try:
                    value, comment = materialObj[layer]
                    # print value + ',\t!-' + comment + "\n"
                    values.append(value)
                    comments.append(comment)
                except:
                    value = materialObj[layer]
                    values.append(value)
                    comments.append('Material Type')
            
            UValueSI = self.calcEPMaterialUValue(materialObj, GHComponent)
            UValueIP = self.convertUValueToIP(UValueSI)
            
            return values, comments, UValueSI, UValueIP
            
        except Exception, e:
            print `e`
            print "Failed to find " + matName + " in the Honeybee material library."
            return -1
    
    def decomposeEPCnstr(self, cnstrName, GHComponent = None):
        try:
            constructionObj = sc.sticky ["honeybee_constructionLib"][cnstrName.upper()]
            comments = []
            materials = []
            
            # print cnstrName
            for layer in constructionObj.keys():
                try:
                    material, comment = constructionObj[layer]
                    materials.append(material)
                    comments.append(comment)
                except:
                    material = constructionObj[layer]
                    materials.append(material)
                    comments.append("!- Material Type")
            
            # place holder
            UValue_SI = self.calcEPConstructionUValue(constructionObj, GHComponent)
            UValue_IP = self.convertUValueToIP(UValue_SI)
            
            return materials[1:], comments[1:], UValue_SI, UValue_IP
    
        except Exception, e:
            print `e`
            print "Failed to find " + cnstrName + " in the Honeybee construction library."
            return -1
       
    def searchListByKeyword(self, inputList, keywords):
        """ search inside a list of strings for keywords """
        
        def checkMultipleKeywords(name, keywordlist):
            for kw in keywordlist:
                if name.find(kw)== -1:
                    return False
            return True
            
        kWords = []
        for kw in keywords:
            kWords.append(kw.strip().upper().split(" "))
            
        selectedItems = []
        alternateOptions = []
        
        for item in inputList:
            if len(kWords)!= 0 and not "*" in keywords:
                for keyword in kWords:
                    if len(keyword) > 1 and checkMultipleKeywords(item.ToUpper(), keyword):
                        selectedItems.append(item)
                    elif len(keyword) == 1 and item.ToUpper().find(keyword[0])!= -1:
                        selectedItems.append(item)
            else:
                selectedItems.append(item)
    
        return selectedItems
    
    def filterMaterials(self, constrList, standard, climateZone, surfaceType, bldgProgram, keywords, sourceComponent):
        hb_EPTypes = EPTypes()
        
        w = gh.GH_RuntimeMessageLevel.Warning
        
        try:
            standard = str(standard).upper().Replace(" ", "").Replace("-", "").Replace(".", "")
            standard = self.energyModelingStandards[standard]
            
        except:
            msg = "The input for standard is not valid. Standard is set to ASHRAE 90.1"
            sourceComponent.AddRuntimeMessage(w, msg)
            standard = "ASHRAE 90.1"
        
        selConstr =[]
        
        filtConstr =self.searchListByKeyword(constrList, keywords)
        
        
        for cnstrName in filtConstr:
           if cnstrName.upper().find(standard.upper())!=-1 and cnstrName.upper().find(surfaceType.upper())!=-1:
                # check for climate zone
                if climateZone!="":
                    clmZones = []
                    # split by space " "
                    possibleAlt, zoneCode = cnstrName.split(" ")[-2:]
                    clmZoneList = zoneCode.split("-")
                    if len(clmZoneList) != 1:
                        try:
                            clmZoneRange = range(int(clmZoneList[0]), int(clmZoneList[1]) + 1)
                            for clmZone in clmZoneRange: clmZones.append(str(clmZone))
                        except:
                            clmZones = [clmZoneList[0], clmZoneList[1]]
                    else:
                        clmZones = clmZoneList
                        
                    if climateZone in clmZones:
                        selConstr.append(cnstrName)
                    elif climateZone[0] in clmZones:
                        # cases like 3a that is included in 3
                        selConstr.append(cnstrName)
                else:
                    selConstr.append(cnstrName)

        return selConstr

    def isEPMaterialObjectAlreadyExists(self, name):
        """
        Check if material or construction exist
        """
        if name in sc.sticky ["honeybee_constructionLib"].keys(): return True
        if name in sc.sticky ["honeybee_materialLib"].keys(): return True
        if name in sc.sticky ["honeybee_windowMaterialLib"].keys(): return True
        
        return False
    
    def getEPObjectsStr(self, objectName):
        """
        This function should work for materials, and counstructions
        """
        objectData = None
        if objectName in sc.sticky ["honeybee_windowMaterialLib"].keys():
            objectData = sc.sticky ["honeybee_windowMaterialLib"][objectName]
        elif objectName in sc.sticky ["honeybee_materialLib"].keys():
            objectData = sc.sticky ["honeybee_materialLib"][objectName]
        elif objectName in sc.sticky ["honeybee_constructionLib"].keys():
            objectData = sc.sticky ["honeybee_constructionLib"][objectName]
        
        if objectData!=None:
            numberOfLayers = len(objectData.keys())
            # add material/construction type
            # print objectData
            objectStr = objectData[0] + ",\n"
            
            # add the name
            objectStr =  objectStr + "  " + objectName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    objectStr =  objectStr + "  " + str(objectData[layer][0]) + ",   !- " +  objectData[layer][1] + "\n"
                else:
                    objectStr =  objectStr + "  " + str(objectData[layer][0]) + ";   !- " +  objectData[layer][1] + "\n\n"
            return objectStr
            
    def getObjectKey(self, EPObject):
        
        EPKeys = ["Material", "WindowMaterial", "Construction"]
    
        # check if it is a full string
        for key in EPKeys:
            if EPObject.strip().startswith(key):
                return key
    
    def addEPConstructionToLib(self, EPMaterial, overwrite = False):
        
        key = self.getObjectKey(EPMaterial)
        
        if key == None:
            return None, None
        
        HBLibrarieNames = {
                       "Construction" : "honeybee_constructionLib",
                       "Material" : "honeybee_materialLib",
                       "WindowMaterial" : "honeybee_windowMaterialLib"
                       }
        
        # find construction/material name
        name = EPMaterial.split("\n")[1].split("!")[0].strip()[:-1].upper()
        
        if name in sc.sticky[HBLibrarieNames[key]].keys():
            #overwrite = True
            if not overwrite:
                # ask user if they want to overwrite it
                add = self.duplicateEPMaterialWarning(name, EPMaterial)
                if not add: return False, name
        
        # add material/construction to the lib
        # create an empty dictoinary for the material
        sc.sticky[HBLibrarieNames[key]][name] = {}
        
        lines = EPMaterial.split("\n")

        # store the data into the dictionary
        for lineCount, line in enumerate(lines):
            
            objValue = line.split("!")[0].strip()
            try: objDescription = line.split("!")[1].strip()
            except:  objDescription = ""
            if lineCount == 0:
                sc.sticky[HBLibrarieNames[key]][name][lineCount] = objValue[:-1]
            elif lineCount == 1:
                pass # name is already there as the key
            elif objValue.endswith(","):
                sc.sticky[HBLibrarieNames[key]][name][lineCount-1] = objValue[:-1], objDescription
            elif objValue.endswith(";"):
                sc.sticky[HBLibrarieNames[key]][name][lineCount-1] = objValue[:-1], objDescription
                break
        
        # add name to list
        # sc.sticky [HBLibrarieNames[key]]["List"].append(name)
        
        return True, name
    
    def duplicateEPMaterialWarning(self, objectName, newMaterialString):
        # this function is duplicate with duplicateEPObject warning and should be removed at some point
        returnYN = {'YES': True, 'NO': False}
        buttons = System.Windows.Forms.MessageBoxButtons.YesNo
        icon = System.Windows.Forms.MessageBoxIcon.Warning
        
        currentMaterialString = self.getEPObjectsStr(objectName)
            
        msg = objectName + " already exists in the library:\n\n" + \
            currentMaterialString + "\n" + \
            "Do you want to overwrite the current with this new definition?\n\n" + \
            newMaterialString + "\n\n" + \
            "Tip: If you are not sure what to do select No and change the name."
        
        up = rc.UI.Dialogs.ShowMessageBox(msg, "Duplicate Material Name", buttons, icon)
        return returnYN[up.ToString().ToUpper()]

class EPScheduleAux(object):
    
    def getScheduleDataByName(self, schName, component = None):

        if schName.lower().endswith(".csv"):
            # Check for the file
            if not os.path.isfile(schName):
                msg = "Failed to find the schedule file: " + schName
                print msg
                if component is not None:
                    component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return None, None
                
            return schName, "csv"
            
        try:
            scheduleObj = sc.sticky["honeybee_ScheduleLib"][schName.upper()]
        except Exception, e:
            
            if schName != "NONE":
                msg = "Failed to find " + schName + " in the Honeybee schedule library."
                print msg
                if component is not None:
                    component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
            return None, None
            
        comments = []
        values = []
        
        for layer in scheduleObj.keys():
            try:
                material, comment = scheduleObj[layer]
                values.append(material)
                comments.append(comment)
            except:
                scheduleType = scheduleObj[layer]
                values.append(scheduleType)
                comments.append("Schedule Type")
        
        return values, comments
    
    def getScheduleTypeLimitsDataByName(self, schName, component = None):
        try:
            scheduleObj = sc.sticky["honeybee_ScheduleTypeLimitsLib"][schName.upper()]
        except Exception, e:
            
            if schName != "NONE":
                msg = "Failed to find " + schName + " in the Honeybee schedule type limits library."
                print msg
                if component is not None:
                    component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
            return None, None
            
        comments = []
        values = []
        
        for layer in scheduleObj.keys():
            try:
                material, comment = scheduleObj[layer]
                values.append(material)
                comments.append(comment)
            except:
                scheduleType = scheduleObj[layer]
                values.append(scheduleType)
                comments.append("Schedule Type")
        
        return values, comments

class EPObjectsAux(object):
    
    def isEPMaterial(self, matName):
        return matName.upper() in sc.sticky["honeybee_materialLib"].keys() or \
               matName.upper() in sc.sticky["honeybee_windowMaterialLib"].keys()
    
    def isEPConstruction(self, matName):
        return matName.upper() in sc.sticky["honeybee_constructionLib"].keys()
    
    def isSchedule(self, scheduleName):
        return scheduleName.upper() in sc.sticky["honeybee_ScheduleLib"].keys()
    
    def isScheduleTypeLimits(self, scheduleName):
        return scheduleName.upper() in sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    
    def customizeEPObject(self, EPObjectName, indexes, inValues):
        hb_EPScheduleAUX = EPScheduleAux()
        hb_EPMaterialAUX = EPMaterialAux()
        
        if self.isSchedule(EPObjectName):
            values, comments = hb_EPScheduleAUX.getScheduleDataByName(EPObjectName.upper())
        
        elif self.isScheduleTypeLimits(EPObjectName):
            values, comments = hb_EPScheduleAUX.getScheduleTypeLimitsDataByName(EPObjectName.upper())
        elif self.isEPConstruction(EPObjectName):
            values, comments, uSI, uIP = hb_EPMaterialAUX.decomposeEPCnstr(EPObjectName.upper())
        
        elif self.isEPMaterial(EPObjectName):
            values, comments, uSI, uIP = hb_EPMaterialAUX.decomposeMaterial(EPObjectName.upper())
        else:
            return
        
        # create a dictionary of index and values
        if len(indexes)==0 or (len(indexes) != len(inValues)):
            return
        
        valuesDict = {}
        
        for i, v in zip(indexes, inValues):
            valuesDict[i] = v
        
        count = 0
        originalObj = ""
        modifiedObj = ""
        
        for value, comment in zip(values, comments):
            if count == len(values):
                separator = ";"
            else:
                separator = ","
                
            if count == 1:
                # add name
                originalObj += "[" + `count` + "]\t" + EPObjectName.upper() + " ! Name\n" 
                
                if count in valuesDict.keys():
                    # update the value
                    modifiedObj += valuesDict[count].upper() + separator + "   ! Name\n"
                
                else:
                    # keep original
                    modifiedObj += EPObjectName.upper() + separator + "    ! Name\n"
                
                count = 2
                
            originalObj += "[" + `count` + "]\t " + value + "   !" + comment + "\n" 
            
            if count in valuesDict.keys():
                modifiedObj += valuesDict[count] + separator + "   !" + comment + "\n"
            else:
                modifiedObj += value + separator + "   !" + comment + "\n" 
                
            count += 1
        
        return originalObj, modifiedObj
    
    def getObjectKey(self, EPObject):
        
        EPKeys = ["Material", "WindowMaterial", "Construction", "ScheduleTypeLimits", "Schedule"]
        
        # check if it is a full string
        for key in EPKeys:
            if EPObject.strip().startswith(key):
                return key
    
    def addEPObjectToLib(self, EPObject, overwrite = False):
        
        key = self.getObjectKey(EPObject)
        
        if key == None:
            return None, None
        
        HBLibrarieNames = {
                       "Construction" : "honeybee_constructionLib",
                       "Material" : "honeybee_materialLib",
                       "WindowMaterial" : "honeybee_windowMaterialLib",
                       "Schedule": "honeybee_ScheduleLib",
                       "ScheduleTypeLimits" : "honeybee_ScheduleTypeLimitsLib"
                       }
        
        # find construction/material name
        name = EPObject.split("\n")[1].split("!")[0].strip()[:-1].upper()
        
        if name in sc.sticky[HBLibrarieNames[key]].keys():
            #overwrite = True
            if not overwrite:
                # ask user if they want to overwrite it
                add = self.duplicateEPObjectWarning(name, EPObject)
                if not add: return False, name
        
        # add material/construction to the lib
        # create an empty dictoinary for the material
        sc.sticky[HBLibrarieNames[key]][name] = {}
        
        lines = EPObject.split("\n")

        # store the data into the dictionary
        for lineCount, line in enumerate(lines):
            
            objValue = line.split("!")[0].strip()
            try: objDescription = line.split("!")[1].strip()
            except:  objDescription = ""
            if lineCount == 0:
                sc.sticky[HBLibrarieNames[key]][name][lineCount] = objValue[:-1]
            elif lineCount == 1:
                pass # name is already there as the key
            elif objValue.endswith(","):
                sc.sticky[HBLibrarieNames[key]][name][lineCount-1] = objValue[:-1], objDescription
            elif objValue.endswith(";"):
                sc.sticky[HBLibrarieNames[key]][name][lineCount-1] = objValue[:-1], objDescription
                break
        
        # add name to list
        #sc.sticky [HBLibrarieNames[key]]["List"].append(name)
        
        return True, name
    
    def getEPObjectDataByName(self, objectName):
        objectData = None
        
        objectName = objectName.upper()
        
        if objectName in sc.sticky ["honeybee_windowMaterialLib"].keys():
            objectData = sc.sticky ["honeybee_windowMaterialLib"][objectName]
        elif objectName in sc.sticky ["honeybee_materialLib"].keys():
            objectData = sc.sticky ["honeybee_materialLib"][objectName]
        elif objectName in sc.sticky ["honeybee_constructionLib"].keys():
            objectData = sc.sticky ["honeybee_constructionLib"][objectName]
        elif objectName in sc.sticky["honeybee_ScheduleLib"].keys():
            objectData = sc.sticky ["honeybee_ScheduleLib"][objectName]
        elif objectName in sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys():
            objectData = sc.sticky ["honeybee_ScheduleTypeLimitsLib"][objectName]

        return objectData
    
    def getEPObjectsStr(self, objectName):
        """
        This function should work for materials, and counstructions
        """
        
        objectData = self.getEPObjectDataByName(objectName)
        
        if objectData!=None:
            numberOfLayers = len(objectData.keys())
            # add material/construction type
            # print objectData
            objectStr = objectData[0] + ",\n"
            
            # add the name
            objectStr =  objectStr + "  " + objectName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    objectStr =  objectStr + "  " + str(objectData[layer][0]) + ",   !- " +  objectData[layer][1] + "\n"
                else:
                    objectStr =  objectStr + "  " + str(objectData[layer][0]) + ";   !- " +  objectData[layer][1] + "\n\n"
            return objectStr
            
    def duplicateEPObjectWarning(self, objectName, newMaterialString):
        returnYN = {'YES': True, 'NO': False}
        buttons = System.Windows.Forms.MessageBoxButtons.YesNo
        icon = System.Windows.Forms.MessageBoxIcon.Warning
        
        currentMaterialString = self.getEPObjectsStr(objectName)
            
        msg = objectName + " already exists in the library:\n\n" + \
            currentMaterialString + "\n" + \
            "Do you want to overwrite the current with this new definition?\n\n" + \
            newMaterialString + "\n\n" + \
            "Tip: If you are not sure what to do select No and change the name."
        
        up = rc.UI.Dialogs.ShowMessageBox(msg, "Duplicate Material Name", buttons, icon)
        
        return returnYN[up.ToString().ToUpper()]
        
    def assignEPConstruction(self, HBSrf, EPConstruction, component):

        if not EPConstruction: return
        
        # if it is just the name of the material make sure it is already defined
        if len(EPConstruction.split("\n")) == 1:
            # if the material is not in the library add it to the library
            if not self.isEPConstruction(EPConstruction):
                warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                            "Add the construction to the library and try again."
                component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                return
        else:
            # it is a full string
            added, EPConstruction = self.addEPObjectToLib(EPConstruction, overwrite = True)
    
            if not added:
                msg = name + " cannot be added to the project library! Make sure it is an standard EP construction."
                component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                print msg
                return
        
        try:
            HBSrf.setEPConstruction(EPConstruction)
        except Exception, e:
            warningMsg = "Failed to assign new EPConstruction to " + HBSrf.name + "."
            print warningMsg
            component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            return
    

class ReadEPSchedules(object):
    
    def __init__(self, schName, startDayOfTheWeek):
        self.hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        self.hb_EPObjectsAUX = sc.sticky["honeybee_EPObjectsAUX"]()
        self.lb_preparation = sc.sticky["ladybug_Preparation"]()
        self.schName = schName
        self.startDayOfTheWeek = startDayOfTheWeek
        self.count = 0
        self.startHOY = 1
        self.endHOY = 24
        self.unit = "unknown"
    
    def getScheduleTypeLimitsData(self, schName):
        
        if schName == None: schName = self.schName
            
        schedule, comments = self.hb_EPScheduleAUX.getScheduleTypeLimitsDataByName(schName.upper(), ghenv.Component)
        try:
            lowerLimit, upperLimit, numericType, unitType = schedule[1:]
        except:
            lowerLimit, upperLimit, numericType = schedule[1:]
            unitType = "unknown"
        
        self.unit = unitType
        if self.unit == "unknown":
            self.unit = numericType
        
        return lowerLimit, upperLimit, numericType, unitType
    
    
    def getDayEPScheduleValues(self, schName = None):
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        typeLimitName = values[1]
        lowerLimit, upperLimit, numericType, unitType = \
                self.getScheduleTypeLimitsData(typeLimitName)
                
        numberOfDaySch = int((len(values) - 3) /2)
        
        hourlyValues = range(24)
        startHour = 0
        for i in range(numberOfDaySch):
            value = float(values[2 * i + 4])
            untilTime = map(int, values[2 * i + 3].split(":"))
            endHour = int(untilTime[0] +  untilTime[1]/60)
            for hour in range(startHour, endHour):
                hourlyValues[hour] = value
            
            startHour = endHour
        
        if numericType.strip().lower() == "district":
            hourlyValues = map(int, hourlyValues)
            
        return hourlyValues
    
    
    def getWeeklyEPScheduleValues(self, schName = None):
        """
        Schedule:Week:Daily
        ['Schedule Type', 'Sunday Schedule:Day Name', 'Monday Schedule:Day Name',
        'Tuesday Schedule:Day Name', 'Wednesday Schedule:Day Name', 'Thursday Schedule:Day Name',
        'Friday Schedule:Day Name', 'Saturday Schedule:Day Name', 'Holiday Schedule:Day Name',
        'SummerDesignDay Schedule:Day Name', 'WinterDesignDay Schedule:Day Name',
        'CustomDay1 Schedule:Day Name', 'CustomDay2 Schedule:Day Name']
        """
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        
        if self.count == 1:
            # set the last date of the schedule to one week
            self.endHOY = 24 * 7
        
        sundaySchedule = self.getScheduleValues(values[1])
        mondaySchedule = self.getScheduleValues(values[2])
        tuesdaySchedule = self.getScheduleValues(values[3])
        wednesdaySchedule = self.getScheduleValues(values[4])
        thursdaySchedule = self.getScheduleValues(values[5])
        fridaySchedule = self.getScheduleValues(values[6])
        saturdaySchedule = self.getScheduleValues(values[7])
        
        holidaySchedule = self.getScheduleValues(values[8])
        summerDesignDaySchedule = self.getScheduleValues(values[9])
        winterDesignDaySchedule = self.getScheduleValues(values[10])
        customDay1Schedule = self.getScheduleValues(values[11])
        customDay2Schedule = self.getScheduleValues(values[12])
        
        hourlyValues = [sundaySchedule, mondaySchedule, tuesdaySchedule, \
                       wednesdaySchedule, thursdaySchedule, fridaySchedule, \
                       saturdaySchedule]
        
        hourlyValues = hourlyValues[self.startDayOfTheWeek:] + \
                       hourlyValues[:self.startDayOfTheWeek]
        
        return hourlyValues
    
    
    def getConstantEPScheduleValues(self, schName):
        """
        'Schedule:Constant'
        ['Schedule Type', 'Schedule Type Limits Name', 'Hourly Value']
        """
        
        if schName == None:
            schName = self.schName
            
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        typeLimitName = values[1]
        lowerLimit, upperLimit, numericType, unitType = \
                self.getScheduleTypeLimitsData(typeLimitName)
        
        hourlyValues = [float(values[2])]
        
        if numericType.strip().lower() == "district":
            hourlyValues = map(int, hourlyValues)
        return scheduleConstant
    
    
    def getYearlyEPScheduleValues(self, schName = None):
        # place holder for 365 days
        hourlyValues = range(365)
        
        # update last day of schedule
        self.endHOY = 8760
        
        if schName == None:
            schName = self.schName
        
        values, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
        
        # generate weekly schedules
        numOfWeeklySchedules = int((len(values)-2)/5)
        
        for i in range(numOfWeeklySchedules):
            weekDayScheduleName = values[5 * i + 2]
            
            startDay = int(self.lb_preparation.getJD(int(values[5 * i + 3]), int(values[5 * i + 4])))
            endDay = int(self.lb_preparation.getJD(int(values[5 * i + 5]), int(values[5 * i + 6])))
            
            # 7 list for 7 days of the week
            hourlyValuesForTheWeek = self.getScheduleValues(weekDayScheduleName)
            
            for day in range(startDay-1, endDay):
                hourlyValues[day] = hourlyValuesForTheWeek[day%7]
            
        return hourlyValues
    
    def getScheduleValues(self, schName = None):
        if schName == None:
            schName = self.schName
        if self.hb_EPObjectsAUX.isSchedule(schName):
            scheduleValues, comments = self.hb_EPScheduleAUX.getScheduleDataByName(schName.upper(), ghenv.Component)
            
            scheduleType = scheduleValues[0].lower()
            if self.count == 0:
                self.schType = scheduleType

            self.count += 1

            if scheduleType == "schedule:year":
                hourlyValues = self.getYearlyEPScheduleValues(schName)
            elif scheduleType == "schedule:day:interval":
                hourlyValues = self.getDayEPScheduleValues(schName)
            elif scheduleType == "schedule:week:daily":
                hourlyValues = self.getWeeklyEPScheduleValues(schName)
            elif scheduleType == "schedule:constant":
                hourlyValues = self.getConstantEPScheduleValues(schName)
            else:
                print "Honeybee doesn't support " + scheduleType + " currently." + \
                      "Email us the type and we will try to add it to Honeybee."
                      
                hourlyValues = []
            
            return hourlyValues

class EPTypes(object):
    def __init__(self):
        self.srfType = {0:'WALL',
                   0.5: 'UndergroundWall',
                   1:'ROOF',
                   1.5: 'UndergroundCeiling',
                   2:'FLOOR',
                   2.25: 'UndergroundSlab',
                   2.5: 'SlabOnGrade',
                   2.75: 'ExposedFloor',
                   3:'CEILING',
                   4:'AIRWALL',
                   5:'WINDOW',
                   6:'SHADING',
                   'WALL': 'WALL',
                   'ROOF':'ROOF',
                   'FLOOR': 'FLOOR',
                   'CEILING': 'CEILING',
                   'WINDOW':'WINDOW',
                   'SHADING': 'SHADING'}
            
        self.bldgTypes = {0:'OFFICE',
                   'OFFICE':'OFFC',
                   1:'RETAIL',
                   'RETAIL':'RETAIL',
                   2:'APT',
                   'MIDRISEAPARTMENT':'APT',
                   3:'PRIMSCH',
                   'PRIMARYSCHOOL':'PRIMSCH',
                   4:'SECSCH',
                   'SECONDARYSCHOOL':'SECSCH',
                   5:'SMLHOTL',
                   'SMALLHOTEL':'SMLHOTL',
                   6:'LRGHTL',
                   'LARGEHOTEL':'LRGHTL',
                   7:'HOSP',
                   'HOSPITAL':'HOSP',
                   8:'OUTPT',
                   'OUTPATIENT':'OUTPT',
                   9:'WARE',
                   'WAREHOUSE':'WARE',
                   10:'MARKET',
                   'SUPERMARKET':'MARKET',
                   11:'FULLREST',
                   'FULLSERVICERESTAURANT':'FULLREST',
                   12:'QUICKREST',
                   'QUICKSERVICERESTAURANT':'QUICKREST'
                   }
                #Restaurant(Full Service)  = "FullServiceRestaurant"
                #Restaurant(Quick Service) = "QuickServiceRestaurant"
                #Mid-rise Apartment        = "Mid-riseApartment"
                #Hospital                  = "Hospital"
                #Small Office              = "Small Office"
                #Medium Office             = "Medium Office"
                #Large Office              = "Large Office"
                #Small Hotel               = "SmallHotel"
                #Large Hotel               = "LargeHotel"
                #Primary School            = "PrimarySchool"
                #Secondary School          = "SecondarySchool"
                #Strip Mall                = "StripMall"
                #Retail                    = "Retail"
                #Warehouse                 = "Warehouse"

class materialLibrary(object):
    
    def __init__(self):
        self.zoneProgram = {0: 'RETAIL',
                1: 'OFFICE',
                2: 'RESIDENTIAL',
                3: 'HOTEL'}
                
        self.zoneConstructionSet =  {0: 'RETAIL_CON',
                        1: 'OFFICE_CON',
                        2: 'RESIDENTIAL_CON',
                        3: 'HOTEL_CON'}
                   
        self.zoneInternalLoad = {0: 'RETAIL_INT_LOAD',
                    1: 'OFFICE_INT_LOAD',
                    2: 'RESIDENTIAL_INT_LOAD',
                    3: 'HOTEL_INT_LOAD'}

        self.zoneSchedule =  {0: 'RETAIL_SCH',
                 1: 'OFFICE_SCH',
                 2: 'RESIDENTIAL_SCH',
                 3: 'HOTEL_SCH'}
             
        self.zoneThermostat =  {0: 'RETAIL_SCH',
                   1: 'OFFICE_SCH',
                   2: 'RESIDENTIAL_SCH',
                   3: 'HOTEL_SCH'}

class scheduleLibrary(object):
    
    # schedule library should be updated to functions
    # so it can be used to generate schedueles
    def __init__(self):
        
        self.ScheduleTypeLimits = '\n' + \
        'ScheduleTypeLimits,\n' + \
        '\tFraction,                !- Name\n' + \
        '\t0,                       !- Lower Limit Value\n' + \
        '\t1,                       !- Upper Limit Value\n' + \
        '\tCONTINUOUS;              !- Numeric Type\n' + \
        '\n' + \
        'ScheduleTypeLimits,\n' + \
        '\tOn/Off,                  !- Name\n' + \
        '\t0,                       !- Lower Limit Value\n' + \
        '\t1,                       !- Upper Limit Value\n' + \
        '\tDISCRETE;                !- Numeric Type\n' + \
        '\n' + \
        'ScheduleTypeLimits,\n' + \
        '\tTemperature,             !- Name\n' + \
        '\t-60,                     !- Lower Limit Value\n' + \
        '\t200,                     !- Upper Limit Value\n' + \
        '\tCONTINUOUS;              !- Numeric Type\n' + \
        '\n' + \
        'ScheduleTypeLimits,\n' + \
        '\tControl Type,            !- Name\n' + \
        '\t0,                       !- Lower Limit Value\n' + \
        '\t4,                       !- Upper Limit Value\n' + \
        '\tDISCRETE;                !- Numeric Type\n' + \
        '\n' + \
        'ScheduleTypeLimits,\n' + \
        '\tAny Number;              !- Name\n'
        
        self.largeOfficeEquipmentSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_BLDG_EQUIP_SCH,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: Weekdays,           !- Field 2\n' + \
            '\tUntil: 08:00,            !- Field 3\n' + \
            '\t0.40,                    !- Field 4\n' + \
            '\tUntil: 12:00,            !- Field 5\n' + \
            '\t0.90,                    !- Field 6\n' + \
            '\tUntil: 13:00,            !- Field 7\n' + \
            '\t0.80,                    !- Field 8\n' + \
            '\tUntil: 17:00,            !- Field 9\n' + \
            '\t0.90,                    !- Field 10\n' + \
            '\tUntil: 18:00,            !- Field 11\n' + \
            '\t0.80,                    !- Field 12\n' + \
            '\tUntil: 20:00,            !- Field 13\n' + \
            '\t0.60,                    !- Field 14\n' + \
            '\tUntil: 22:00,            !- Field 15\n' + \
            '\t0.50,                    !- Field 16\n' + \
            '\tUntil: 24:00,            !- Field 17\n' + \
            '\t0.40,                    !- Field 18\n' + \
            '\tFor: Saturday,           !- Field 19\n' + \
            '\tUntil: 06:00,            !- Field 20\n' + \
            '\t0.30,                    !- Field 21\n' + \
            '\tUntil: 08:00,            !- Field 22\n' + \
            '\t0.4,                     !- Field 23\n' + \
            '\tUntil: 14:00,            !- Field 24\n' + \
            '\t0.5,                     !- Field 25\n' + \
            '\tUntil: 17:00,            !- Field 26\n' + \
            '\t0.35,                    !- Field 27\n' + \
            '\tUntil: 24:00,            !- Field 28\n' + \
            '\t0.30,                    !- Field 29\n' + \
            '\tFor: SummerDesignDay,    !- Field 30\n' + \
            '\tUntil: 24:00,            !- Field 31\n' + \
            '\t1.0,                     !- Field 32\n' + \
            '\tFor: WinterDesignDay,    !- Field 33\n' + \
            '\tUntil: 24:00,            !- Field 34\n' + \
            '\t0.0,                     !- Field 35\n' + \
            '\tFor: AllOtherDays,       !- Field 36\n' + \
            '\tUntil: 24:00,            !- Field 37\n' + \
            '\t0.30;                    !- Field 38\n'
        
        self.largeOfficeElevatorsSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_BLDG_ELEVATORS,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 04:00,            !- Field 3\n' + \
            '\t0.05,                    !- Field 4\n' + \
            '\tUntil: 05:00,            !- Field 5\n' + \
            '\t0.10,                    !- Field 6\n' + \
            '\tUntil: 06:00,            !- Field 7\n' + \
            '\t0.20,                    !- Field 8\n' + \
            '\tUntil: 07:00,            !- Field 9\n' + \
            '\t0.40,                    !- Field 10\n' + \
            '\tUntil: 09:00,            !- Field 11\n' + \
            '\t0.50,                    !- Field 12\n' + \
            '\tUntil: 10:00,            !- Field 13\n' + \
            '\t0.35,                    !- Field 14\n' + \
            '\tUntil: 16:00,            !- Field 15\n' + \
            '\t0.15,                    !- Field 16\n' + \
            '\tUntil: 17:00,            !- Field 17\n' + \
            '\t0.35,                    !- Field 18\n' + \
            '\tUntil: 19:00,            !- Field 19\n' + \
            '\t0.50,                    !- Field 20\n' + \
            '\tUntil: 21:00,            !- Field 21\n' + \
            '\t0.40,                    !- Field 22\n' + \
            '\tUntil: 22:00,            !- Field 23\n' + \
            '\t0.30,                    !- Field 24\n' + \
            '\tUntil: 23:00,            !- Field 25\n' + \
            '\t0.20,                    !- Field 26\n' + \
            '\tUntil: 24:00,            !- Field 27\n' + \
            '\t0.10;                    !- Field 28\n'
            
        self.largeOfficeOccupancySchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_BLDG_OCC_SCH,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: SummerDesignDay,    !- Field 2\n' + \
            '\tUntil: 06:00,            !- Field 3\n' + \
            '\t0.0,                     !- Field 4\n' + \
            '\tUntil: 22:00,            !- Field 5\n' + \
            '\t1.0,                     !- Field 6\n' + \
            '\tUntil: 24:00,            !- Field 7\n' + \
            '\t0.05,                    !- Field 8\n' + \
            '\tFor: Weekdays,           !- Field 9\n' + \
            '\tUntil: 06:00,            !- Field 10\n' + \
            '\t0.0,                     !- Field 11\n' + \
            '\tUntil: 07:00,            !- Field 12\n' + \
            '\t0.1,                     !- Field 13\n' + \
            '\tUntil: 08:00,            !- Field 14\n' + \
            '\t0.2,                     !- Field 15\n' + \
            '\tUntil: 12:00,            !- Field 16\n' + \
            '\t0.95,                    !- Field 17\n' + \
            '\tUntil: 13:00,            !- Field 18\n' + \
            '\t0.5,                     !- Field 19\n' + \
            '\tUntil: 17:00,            !- Field 20\n' + \
            '\t0.95,                    !- Field 21\n' + \
            '\tUntil: 18:00,            !- Field 22\n' + \
            '\t0.7,                     !- Field 23\n' + \
            '\tUntil: 20:00,            !- Field 24\n' + \
            '\t0.4,                     !- Field 25\n' + \
            '\tUntil: 22:00,            !- Field 26\n' + \
            '\t0.1,                     !- Field 27\n' + \
            '\tUntil: 24:00,            !- Field 28\n' + \
            '\t0.05,                    !- Field 29\n' + \
            '\tFor: Saturday,           !- Field 30\n' + \
            '\tUntil: 06:00,            !- Field 31\n' + \
            '\t0.0,                     !- Field 32\n' + \
            '\tUntil: 08:00,            !- Field 33\n' + \
            '\t0.1,                     !- Field 34\n' + \
            '\tUntil: 14:00,            !- Field 35\n' + \
            '\t0.5,                     !- Field 36\n' + \
            '\tUntil: 17:00,            !- Field 37\n' + \
            '\t0.1,                     !- Field 38\n' + \
            '\tUntil: 24:00,            !- Field 39\n' + \
            '\t0.0,                     !- Field 40\n' + \
            '\tFor: AllOtherDays,       !- Field 41\n' + \
            '\tUntil: 24:00,            !- Field 42\n' + \
            '\t0.0;                     !- Field 43\n'
            
        self.largeOfficeWorkEffSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_WORK_EFF_SCH,  !- Name\n' + \
            '\tOn/Off,                  !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 24:00,            !- Field 3\n' + \
            '\t0.0;                     !- Field 4\n'
            
        self.largeOfficeInfiltrationSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_INFIL_QUARTER_ON_SCH,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: Weekdays SummerDesignDay,  !- Field 2\n' + \
            '\tUntil: 06:00,            !- Field 3\n' + \
            '\t1.0,                     !- Field 4\n' + \
            '\tUntil: 22:00,            !- Field 5\n' + \
            '\t0.25,                    !- Field 6\n' + \
            '\tUntil: 24:00,            !- Field 7\n' + \
            '\t1.0,                     !- Field 8\n' + \
            '\tFor: Saturday WinterDesignDay,  !- Field 9\n' + \
            '\tUntil: 06:00,            !- Field 10\n' + \
            '\t1.0,                     !- Field 11\n' + \
            '\tUntil: 18:00,            !- Field 12\n' + \
            '\t0.25,                    !- Field 13\n' + \
            '\tUntil: 24:00,            !- Field 14\n' + \
            '\t1.0,                     !- Field 15\n' + \
            '\tFor: Sunday Holidays AllOtherDays,  !- Field 16\n' + \
            '\tUntil: 24:00,            !- Field 17\n' + \
            '\t1.0;                     !- Field 18\n'
            
        self.largeOfficeClothingSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_CLOTHING_SCH,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 04/30,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 24:00,            !- Field 3\n' + \
            '\t1.0,                     !- Field 4\n' + \
            '\tThrough: 09/30,          !- Field 5\n' + \
            '\tFor: AllDays,            !- Field 6\n' + \
            '\tUntil: 24:00,            !- Field 7\n' + \
            '\t0.5,                     !- Field 8\n' + \
            '\tThrough: 12/31,          !- Field 9\n' + \
            '\tFor: AllDays,            !- Field 10\n' + \
            '\tUntil: 24:00,            !- Field 11\n' + \
            '\t1.0;                     !- Field 12\n'
            
        self.alwaysOffSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tAlways_Off,              !- Name\n' + \
            '\tOn/Off,                  !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 24:00,            !- Field 3\n' + \
            '\t0;                       !- Field 4\n'
            
        self.largeOfficeHeatingSetPtSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_HTGSETP_SCH,!- Name\n' + \
            '\tTemperature,             !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: Weekdays,           !- Field 2\n' + \
            '\tUntil: 06:00,            !- Field 3\n' + \
            '\t15.6,                    !- Field 4\n' + \
            '\tUntil: 22:00,            !- Field 5\n' + \
            '\t21.0,                    !- Field 6\n' + \
            '\tUntil: 24:00,            !- Field 7\n' + \
            '\t15.6,                    !- Field 8\n' + \
            '\tFor SummerDesignDay,     !- Field 9\n' + \
            '\tUntil: 24:00,            !- Field 10\n' + \
            '\t15.6,                    !- Field 11\n' + \
            '\tFor: Saturday,           !- Field 12\n' + \
            '\tUntil: 06:00,            !- Field 13\n' + \
            '\t15.6,                    !- Field 14\n' + \
            '\tUntil: 18:00,            !- Field 15\n' + \
            '\t21.0,                    !- Field 16\n' + \
            '\tUntil: 24:00,            !- Field 17\n' + \
            '\t15.6,                    !- Field 18\n' + \
            '\tFor: WinterDesignDay,    !- Field 19\n' + \
            '\tUntil: 24:00,            !- Field 20\n' + \
            '\t21.0,                    !- Field 21\n' + \
            '\tFor: AllOtherDays,       !- Field 22\n' + \
            '\tUntil: 24:00,            !- Field 23\n' + \
            '\t15.6;                    !- Field 24\n'
            
        self.largeOfficeCoolingSetPtSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_CLGSETP_SCH,!- Name\n' + \
            '\tTemperature,             !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: Weekdays SummerDesignDay,  !- Field 2\n' + \
            '\tUntil: 06:00,            !- Field 3\n' + \
            '\t26.7,                    !- Field 4\n' + \
            '\tUntil: 22:00,            !- Field 5\n' + \
            '\t24.0,                    !- Field 6\n' + \
            '\tUntil: 24:00,            !- Field 7\n' + \
            '\t26.7,                    !- Field 8\n' + \
            '\tFor: Saturday,           !- Field 9\n' + \
            '\tUntil: 06:00,            !- Field 10\n' + \
            '\t26.7,                    !- Field 11\n' + \
            '\tUntil: 18:00,            !- Field 12\n' + \
            '\t24.0,                    !- Field 13\n' + \
            '\tUntil: 24:00,            !- Field 14\n' + \
            '\t26.7,                    !- Field 15\n' + \
            '\tFor WinterDesignDay,     !- Field 16\n' + \
            '\tUntil: 24:00,            !- Field 17\n' + \
            '\t26.7,                    !- Field 18\n' + \
            '\tFor: AllOtherDays,       !- Field 19\n' + \
            '\tUntil: 24:00,            !- Field 20\n' + \
            '\t26.7;                    !- Field 21\n'
        
        self.largeOfficeActivitySchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_ACTIVITY_SCH,  !- Name\n' + \
            '\tAny Number,              !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 24:00,            !- Field 3\n' + \
            '\t120;                     !- Field 4\n'
        
        self.alwaysOnSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tAlways_On,               !- Name\n' + \
            '\tOn/Off,                  !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: AllDays,            !- Field 2\n' + \
            '\tUntil: 24:00,            !- Field 3\n' + \
            '\t1;                       !- Field 4\n'
        
        self.largeOfficeLightingSchedule = '\n' + \
            'Schedule:Compact,\n' + \
            '\tLarge Office_BLDG_LIGHT_SCH,  !- Name\n' + \
            '\tFraction,                !- Schedule Type Limits Name\n' + \
            '\tThrough: 12/31,          !- Field 1\n' + \
            '\tFor: Weekdays,           !- Field 2\n' + \
            '\tUntil: 05:00,            !- Field 3\n' + \
            '\t0.05,                    !- Field 4\n' + \
            '\tUntil: 07:00,            !- Field 5\n' + \
            '\t0.1,                     !- Field 6\n' + \
            '\tUntil: 08:00,            !- Field 7\n' + \
            '\t0.3,                     !- Field 8\n' + \
            '\tUntil: 17:00,            !- Field 9\n' + \
            '\t0.9,                     !- Field 10\n' + \
            '\tUntil: 18:00,            !- Field 11\n' + \
            '\t0.7,                     !- Field 12\n' + \
            '\tUntil: 20:00,            !- Field 13\n' + \
            '\t0.5,                     !- Field 14\n' + \
            '\tUntil: 22:00,            !- Field 15\n' + \
            '\t0.3,                     !- Field 16\n' + \
            '\tUntil: 23:00,            !- Field 17\n' + \
            '\t0.1,                     !- Field 18\n' + \
            '\tUntil: 24:00,            !- Field 19\n' + \
            '\t0.05,                    !- Field 20\n' + \
            '\tFor: Saturday,           !- Field 21\n' + \
            '\tUntil: 06:00,            !- Field 22\n' + \
            '\t0.05,                    !- Field 23\n' + \
            '\tUntil: 08:00,            !- Field 24\n' + \
            '\t0.1,                     !- Field 25\n' + \
            '\tUntil: 14:00,            !- Field 26\n' + \
            '\t0.5,                     !- Field 27\n' + \
            '\tUntil: 17:00,            !- Field 28\n' + \
            '\t0.15,                    !- Field 29\n' + \
            '\tUntil: 24:00,            !- Field 30\n' + \
            '\t0.05,                    !- Field 31\n' + \
            '\tFor: SummerDesignDay,    !- Field 32\n' + \
            '\tUntil: 24:00,            !- Field 33\n' + \
            '\t1.0,                     !- Field 34\n' + \
            '\tFor: WinterDesignDay,    !- Field 35\n' + \
            '\tUntil: 24:00,            !- Field 36\n' + \
            '\t0.0,                     !- Field 37\n' + \
            '\tFor: AllOtherDays,       !- Field 38\n' + \
            '\tUntil: 24:00,            !- Field 39\n' + \
            '\t0.05;                    !- Field 40\n'

class BuildingProgramsLib(object):
    def __init__(self):
        
        self.bldgPrograms = {
                0 : 'Office',
                1 : 'Retail',
                2 : 'MidriseApartment',
                3 : 'PrimarySchool',
                4 : 'SecondarySchool',
                5 : 'SmallHotel',
                6 : 'LargeHotel',
                7 : 'Hospital',
                8 : 'Outpatient',
                9 : 'Warehouse',
                10 : 'SuperMarket',
                11 : 'FullServiceRestaurant',
                12 : 'QuickServiceRestaurant',
                'Office' : 'Office',
                'Retail' : 'Retail',
                'MidriseApartment' : 'MidriseApartment',
                'PrimarySchool' : 'PrimarySchool',
                'SecondarySchool' : 'SecondarySchool',
                'SmallHotel' : 'SmallHotel',
                'LargeHotel' : 'LargeHotel',
                'Hospital' : 'Hospital',
                'Outpatient' : 'Outpatient',
                'Warehouse' : 'Warehouse',
                'SuperMarket' : 'SuperMarket',
                'FullServiceRestaurant' : 'FullServiceRestaurant',
                'QuickServiceRestaurant' : 'QuickServiceRestaurant'}
        
        self.zonePrograms = { "MidriseApartment" : {
                                            0: "Apartment",
                                            1: "Office",
                                            2: "Corridor",
                                            },
                    'Outpatient' : {
                                    0: "IT_Room",
                                    1: "ProcedureRoom",
                                    2: "Conference",
                                    3: "MedGas",
                                    4: "Janitor",
                                    5: "Cafe",
                                    6: "OR",
                                    7: "PhysicalTherapy",
                                    8: "Lobby",
                                    9: "Xray",
                                    10: "MRI_Control",
                                    11: "Toilet",
                                    12: "Elec/MechRoom",
                                    13: "Stair",
                                    14: "PACU",
                                    15: "Anesthesia",
                                    16: "MRI",
                                    17: "CleanWork",
                                    18: "NurseStation",
                                    19: "PreOp",
                                    20: "Lounge",
                                    21: "BioHazard",
                                    22: "Office",
                                    23: "Hall",
                                    24: "Soil Work",
                                    25: "DressingRoom",
                                    26: "Exam",
                                    27: "LockerRoom",
                                    },
                    'LargeHotel'  : {
                                    0: "Storage",
                                    1: "Mechanical",
                                    2: "Banquet",
                                    3: "GuestRoom",
                                    4: "Laundry",
                                    5: "Retail",
                                    6: "Kitchen",
                                    7: "Cafe",
                                    8: "Corridor",
                                    9: "Lobby"
                                    },
                    'FullServiceRestaurant' : {
                                    0: "Kitchen",
                                    1: "Dining"
                                    },
                    'PrimarySchool' : {
                                    0: "Mechanical",
                                    1: "Library",
                                    2: "Cafeteria",
                                    3: "Gym",
                                    4: "Restroom",
                                    5: "Office",
                                    6: "Classroom",
                                    7: "Kitchen",
                                    8: "Corridor",
                                    9: "Lobby"
                                    },
                    'SmallHotel' : {
                                    0: "Storage",
                                    1: "GuestLounge",
                                    2: "Mechanical",
                                    3: "StaffLounge",
                                    4: "PublicRestroom",
                                    5: "GuestRoom",
                                    6: "Exercise",
                                    7: "Laundry",
                                    8: "Meeting",
                                    9: "Office",
                                    10: "Stair",
                                    11: "Corridor"
                                    },
                    'SuperMarket' : {
                                    0: "Sales/Produce",
                                    1: "DryStorage",
                                    2: "Office",
                                    3: "Deli/Bakery"
                                    },
                    'SecondarySchool' : {
                                    0: "Mechanical",
                                    1: "Library",
                                    2: "Auditorium",
                                    3: "Cafeteria",
                                    4: "Gym",
                                    5: "Restroom",
                                    6: "Office",
                                    7: "Classroom",
                                    8: "Kitchen",
                                    9: "Corridor",
                                    10: "Lobby"
                                    },
                    'Retail' : {
                                    0: "Back_Space",
                                    1: "Point_of_Sale",
                                    2: "Entry",
                                    3: "Retail"
                                    },
                    'Hospital' : {
                                    0: "ER_Trauma",
                                    1: "PatCorridor",
                                    2: "ICU_PatRm",
                                    3: "ER_NurseStn",
                                    4: "ICU_Open",
                                    5: "NurseStn",
                                    6: "PhysTherapy",
                                    7: "ICU_NurseStn",
                                    8: "Radiology",
                                    9: "Dining",
                                    10: "PatRoom",
                                    11: "OR",
                                    12: "Office",
                                    13: "Kitchen",
                                    14: "Lab",
                                    15: "ER_Exam",
                                    16: "ER_Triage",
                                    17: "Corridor",
                                    18: "Lobby"
                                    },
                    'Office' : {
                                    0: "BreakRoom",
                                    1: "Storage",
                                    2: "Vending",
                                    3: "OpenOffice",
                                    4: "ClosedOffice",
                                    5: "Conference",
                                    6: "PrintRoom",
                                    7: "Restroom",
                                    8: "Elec/MechRoom",
                                    9: "IT_Room",
                                    10: "Stair",
                                    11: "Corridor",
                                    12: "Lobby"
                                    },
                    'Warehouse' : {
                                    0: "Office",
                                    1: "Fine",
                                    2: "Bulk"
                                    },
                    'QuickServiceRestaurant' : {
                                    0: "Kitchen",
                                    1: "Dining"
                                    }
                    }

class EPSurfaceLib(object):
    # I think I can remove this now
    def __init__(self):
        # 4 represents an Air Wall
        self.srfType = {0:'WALL',
               1:'ROOF',
               2:'FLOOR',
               3:'CEILING',
               4:'AIRWALL',
               5:'WINDOW'}
        
        # surface construction should change later
        # to be based on the zone program
        self.srfCnstr = {0:'Exterior_Wall',
                1:'Exterior_Roof',
                2:'Exterior_Floor',
                3:'Interior_Floor',
                4:'Air_Wall',
                5:'Exterior_Window'}
         
        self.srfBC = {0:'Outdoors',
                 1:'Outdoors',
                 2: 'Outdoors',
                 3: 'Adiabatic',
                 4: 'surface',
                 5: 'Outdoors'}
        
        self.srfSunExposure = {0:'SunExposed',
                 1:'SunExposed',
                 2:'SunExposed',
                 3:'NoSun',
                 4:'NoSun',
                 5:'SunExposed',}
    
        self.srfWindExposure = {0:'WindExposed',
                  1:'WindExposed',
                  2:'WindExposed',
                  3:'NoWind',
                  4:'NoWind',
                  5:'WindExposed'}

class EPZone(object):
    """This calss represents a honeybee zone that will be used for energy and daylighting
    simulatios"""
    
    def __init__(self, zoneBrep, zoneID, zoneName, program = [None, None], isConditioned = True):
        self.north = 0
        self.objectType = "HBZone"
        self.origin = rc.Geometry.Point3d.Origin
        self.geometry = zoneBrep
        
        self.num = zoneID
        self.name = zoneName
        self.hasNonPlanarSrf = False
        self.hasInternalEdge = False
        
        #Air Mixing with Adjacent Zones
        self.mixAir = False
        self.mixAirZoneList = []
        self.mixAirFlowList = []
        self.mixAirFlowRate = 0.0963
        self.mixAirFlowSched = []
        
        #Natural Ventilation Properties
        self.natVent = False
        self.natVentType = []
        self.natVentMinIndoorTemp = []
        self.natVentMaxIndoorTemp = []
        self.natVentMinOutdoorTemp = []
        self.natVentMaxOutdoorTemp = []
        self.windowOpeningArea = []
        self.windowHeightDiff = []
        self.natVentSchedule = []
        self.natVentWindDischarge = []
        self.natVentStackDischarge = []
        self.windowAngle = []
        self.fanFlow = []
        self.FanEfficiency = []
        self.FanPressure = []
        
        #Zone Internal Masses (or Furniture)
        self.internalMassNames = []
        self.internalMassSrfAreas = []
        self.internalMassConstructions = []
        
        #Zone Surfaces
        self.surfaces = []
        
        #Zone Thresholds
        self.daylightThreshold = ""
        self.coolingSetPt= ""
        self.heatingSetPt= ""
        self.coolingSetback= ""
        self.heatingSetback= ""
        
        #Ideal Air System Properties
        self.outdoorAirReq = "Sum"
        self.coolSupplyAirTemp= ""
        self.heatSupplyAirTemp= ""
        self.coolingCapacity= ""
        self.heatingCapacity= ""
        self.airSideEconomizer= 'DifferentialDryBulb'
        self.heatRecovery= ""
        self.heatRecoveryEffectiveness= ""
        self.HVACAvailabilitySched = "ALWAYS ON"
        
        if zoneBrep != None:
            self.isClosed = self.geometry.IsSolid
        else:
            self.isClosed = False
        if self.isClosed:
            try:
                planarTrigger = self.checkZoneNormalsDir()
            except Exception, e:
                print 'Checking normal directions failed:\n' + `e`
        
        self.bldgProgram = program[0]
        self.zoneProgram = program[1]
        
        # assign schedules
        self.assignScheduleBasedOnProgram()
        # assign loads
        self.assignLoadsBasedOnProgram()
        
        if isConditioned: self.HVACSystem = ["GroupI", 0, None, None] # assign ideal loads as default
        else: self.HVACSystem = ["NoHVAC", -1, None, None] # no system        
        
        self.isConditioned = isConditioned
        self.isThisTheTopZone = False
        self.isThisTheFirstZone = False
        
        # Earthtube
        self.earthtube = False
        
        # PV - A Honeybee zone can hold more than one photovoltaic generator for this reason we use a list 
        # of all PV generators linked to this instance of the zone.
        
        # XXX self.PVgenlist = []
    
    def assignScheduleBasedOnProgram(self, component = None):
        # create an open office is the program is not assigned
        if self.bldgProgram == None: self.bldgProgram = "Office"
        if self.zoneProgram == None: self.zoneProgram = "OpenOffice"
        
        openStudioStandardLib = sc.sticky ["honeybee_OpenStudioStandardsFile"]
        
        try:
            schedulesAndLoads = openStudioStandardLib['space_types']['90.1-2007']['ClimateZone 1-8'][self.bldgProgram][self.zoneProgram]
        except:
            msg = "Either your input for bldgProgram > [" + self.bldgProgram + "] or " + \
                  "the input for zoneProgram > [" + self.zoneProgram + "] is not valid.\n" + \
                  "Use ListSpacePrograms component to find the available programs."
            print msg
            if component != None:
                component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return
        
        self.occupancySchedule = schedulesAndLoads['occupancy_sch']
        self.occupancyActivitySch = schedulesAndLoads['occupancy_activity_sch']
        self.heatingSetPtSchedule = schedulesAndLoads['heating_setpoint_sch']
        self.coolingSetPtSchedule = schedulesAndLoads['cooling_setpoint_sch']
        self.lightingSchedule = schedulesAndLoads['lighting_sch']
        self.equipmentSchedule = schedulesAndLoads['elec_equip_sch']
        self.infiltrationSchedule = schedulesAndLoads['infiltration_sch']
        
        # find all the patameters and assign them to 
        self.isSchedulesAssigned = True
    
    def assignLoadsBasedOnProgram(self, component=None):
        # create an open office is the program is not assigned
        if self.bldgProgram == None: self.bldgProgram = "Office"
        if self.zoneProgram == None: self.zoneProgram = "OpenOffice"
        
        openStudioStandardLib = sc.sticky ["honeybee_OpenStudioStandardsFile"]
        
        try:
            schedulesAndLoads = openStudioStandardLib['space_types']['90.1-2007']['ClimateZone 1-8'][self.bldgProgram][self.zoneProgram]
            
        except:
            msg = "Either your input for bldgProgram > [" + self.bldgProgram + "] or " + \
                  "the input for zoneProgram > [" + self.zoneProgram + "] is not valid.\n" + \
                  "Use ListSpacePrograms component to find the available programs."
            print msg
            if component != None:
                component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return
            
        # numbers in OpenStudio standard library are in IP and I have to convert them to SI!
        self.equipmentLoadPerArea = schedulesAndLoads['elec_equip_per_area'] * 10.763961 #Per ft^2 to Per m^2
        self.infiltrationRatePerArea = schedulesAndLoads['infiltration_per_area_ext'] * 0.00508001 #1 ft3/min.m2 = 5.08001016E-03 m3/s.m2
        self.lightingDensityPerArea = schedulesAndLoads['lighting_w_per_area'] * 10.763961 #Per ft^2 to Per m^2
        self.numOfPeoplePerArea = schedulesAndLoads[ 'occupancy_per_area'] * 10.763961 /1000 #Per 1000 ft^2 to Per m^2
        self.ventilationPerArea = schedulesAndLoads['ventilation_per_area'] * 0.00508001 #1 ft3/min.m2 = 5.08001016E-03 m3/s.m2
        self.ventilationPerPerson = schedulesAndLoads['ventilation_per_person'] * 0.0004719  #1 ft3/min.perosn = 4.71944743E-04 m3/s.person
        
        self.isLoadsAssigned = True
    
    def getCurrentSchedules(self, returnDictionary = False, component = None):
        # assign the default is there is no schedule assigned 
        if not self.isSchedulesAssigned:
            self.assignScheduleBasedOnProgram(component)
        
        if not returnDictionary:
            report = " Schedule list:\n" + \
            "occupancySchedule: " + str(self.occupancySchedule) + "\n" + \
            "occupancyActivitySch: " + str(self.occupancyActivitySch) + "\n" + \
            "heatingSetPtSchedule: " + str(self.heatingSetPtSchedule) + "\n" + \
            "coolingSetPtSchedule: " + str(self.coolingSetPtSchedule) + "\n" + \
            "lightingSchedule: " + str(self.lightingSchedule) + "\n" + \
            "equipmentSchedule: " + str(self.equipmentSchedule) + "\n" + \
            "infiltrationSchedule: " + str(self.infiltrationSchedule)+ "\n" + \
            "HVACAvailabilitySched: " + str(self.HVACAvailabilitySched) + "."
            
            return report
        
        else:
            scheduleDict = {"occupancySchedule" : str(self.occupancySchedule),
                            "occupancyActivitySch" : str(self.occupancyActivitySch),
                            "heatingSetPtSchedule" :str(self.heatingSetPtSchedule),
                            "coolingSetPtSchedule" : str(self.coolingSetPtSchedule),
                            "lightingSchedule" : str(self.lightingSchedule),
                            "equipmentSchedule" : str(self.equipmentSchedule),
                            "infiltrationSchedule" : str(self.infiltrationSchedule),
                            "HVACAvailabilitySched" : str(self.HVACAvailabilitySched)}
            
            return scheduleDict

    def getCurrentLoads(self,  returnDictionary = False, component = None):
        
        # assign the default is there is no schedule assigned
        if not self.isLoadsAssigned:
            self.assignLoadsBasedOnProgram(component)
        
        if not returnDictionary:
            report = " Internal Loads [SI]:\n" + \
            "EquipmentsLoadPerArea: " + "%.4f"%self.equipmentLoadPerArea + "\n" + \
            "infiltrationRatePerArea: " + "%.4f"%self.infiltrationRatePerArea + "\n" + \
            "lightingDensityPerArea: " + "%.4f"%self.lightingDensityPerArea + "\n" + \
            "numOfPeoplePerArea: " + "%.4f"%self.numOfPeoplePerArea + "\n" + \
            "ventilationPerPerson: " + "%.4f"%self.ventilationPerPerson + "\n" + \
            "ventilationPerArea: " + "%.4f"%self.ventilationPerArea + "."
            
            return report        
            
        else:
            
            loadsDict = {"EquipmentsLoadPerArea" : "%.4f"%self.equipmentLoadPerArea,
                         "infiltrationRatePerArea" : "%.4f"%self.infiltrationRatePerArea,
                         "lightingDensityPerArea" : "%.4f"%self.lightingDensityPerArea,
                         "numOfPeoplePerArea" : "%.4f"%self.numOfPeoplePerArea,
                         "ventilationPerArea" : "%.4f"%self.ventilationPerArea,
                         "ventilationPerPerson" : "%.4f"%self.ventilationPerPerson}
            
            return loadsDict
            
    def joinMesh(self, meshList):
        joinedMesh = rc.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh
    
    def checkZoneNormalsDir(self):
        
        def checkSrfNormal(HBSrf, anchorPts, nVecs, planarTrigger):
            #Find the corresponding surface in the closed zone geometry.
            for count, cenpt in enumerate(anchorPts):
                #If the center points are the same, then these two represent the same surface.
                if cenpt == HBSrf.cenPt:
                    if nVecs[count] != HBSrf.normalVector:
                        print "Normal direction for " + HBSrf.name + " is fixed by Honeybee!"
                        HBSrf.geometry.Flip()
                        HBSrf.normalVector.Reverse()
                        HBSrf.basePlane.Flip()
                        try: HBSrf.punchedGeometry.Flip()
                        except: pass
                        if HBSrf.hasChild and HBSrf.isPlanar:
                            for childSrf in HBSrf.childSrfs:
                                if childSrf.normalVector != nVecs[count]:
                                    print "Normal direction for " + childSrf.name + " is fixed by Honeybee!"
                                    childSrf.geometry.Flip()
                                    childSrf.normalVector.Reverse()
                                    childSrf.basePlane.Flip()
                        elif HBSrf.hasChild:
                            for childSrf in HBSrf.childSrfs:
                                # print childSrf.normalVector
                                childSrf.cenPt = rc.Geometry.AreaMassProperties.Compute(childSrf.geometry).Centroid
                                uv = childSrf.geometry.Faces[0].ClosestPoint(childSrf.cenPt)
                                childSrf.normalVector = childSrf.geometry.Faces[0].NormalAt(uv[1], uv[2])
                                #If the childSrfs are differing by more than 45 degrees, there's something wrong and we should flip them.
                                vecAngleDiff = math.degrees(rc.Geometry.Vector3d.VectorAngle(nVecs[count], childSrf.normalVector))
                                if vecAngleDiff > 45:
                                    print "Normal direction for " + childSrf.name + " is fixed by Honeybee!"
                                    childSrf.geometry.Flip()
                                    childSrf.normalVector.Reverse()
        
        
        # find center point, it won't be used in this function!
        MP3D = rc.Geometry.AreaMassProperties.Compute(self.geometry)
        self.cenPt = MP3D.Centroid
        MP3D.Dispose()
        
        #Extract the center points and normal vectors from the closed brep geometry.
        planarTrigger = False
        anchorPts = []
        nVecs = []
        closedBrepGeo = self.geometry
        for surface in closedBrepGeo.Faces:
            if surface.IsPlanar and surface.IsSurface:
                u_domain = surface.Domain(0)
                v_domain = surface.Domain(1)
                centerU = (u_domain.Min + u_domain.Max)/2
                centerV = (v_domain.Min + v_domain.Max)/2
                anchorPts.append(surface.PointAt(centerU, centerV))
                nVecs.append(surface.NormalAt(centerU, centerV))
            else:
                planarTrigger = True
                centroid = rc.Geometry.AreaMassProperties.Compute(surface).Centroid
                uv = surface.ClosestPoint(centroid)
                anchorPts.append(surface.PointAt(uv[1], uv[2]))
                nVecs.append(surface.NormalAt(uv[1], uv[2]))
        
        for HBSrf in self.surfaces:
            checkSrfNormal(HBSrf, anchorPts, nVecs, planarTrigger)
        
        return planarTrigger
    
    def decomposeZone(self, maximumRoofAngle = 30):
        # this method is useufl when the zone is going to be constructed from a closed brep
        # materials will be applied based on the zones construction set
        
        #This check fails for any L-shaped zone so it has been disabled.  We check the normals well elsewhere.
        def getGHSrfNormal(GHSrf):
            cenPt, normalVector = self.getSrfCenPtandNormal(surface)
            return normalVector, GHSrf
            
        # explode zone
        for i in range(self.geometry.Faces.Count):
            
            surface = self.geometry.Faces[i].DuplicateFace(False)
            
            # check surface Normal
            normal, surface = getGHSrfNormal(surface)
            
            angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            
            if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
                # roof is the right assumption
                # it will change to ceiling after solveAdj if it is a ceiling
                surafceType = 1 #roof
                #if self.isThisTheTopZone: surafceType = 1 #roof
                #else:  surafceType = 3 # ceiling
            
            elif  160 < angle2Z <200:
                surafceType = 2 # floor
            
            else: surafceType = 0 #wall
            
            
            HBSurface = hb_EPZoneSurface(surface, i, self.name + '_Srf_' + `i`, self, surafceType)

            self.addSrf(HBSurface)
            
            
    def createZoneFromSurfaces(self, maximumRoofAngle = 30):
        # this method recreate the geometry from the surfaces
        srfs = []
        # check if surface has a type
        for srf in self.surfaces:
            srf.parent = self
            
            # check planarity and set it for parent zone
            if not srf.isPlanar:
                self.hasNonPlanarSrf = True
            if srf.hasInternalEdge:
                self.hasInternalEdge = True
            
            # also chek for interal Edges
            
            surface = srf.geometry.Faces[0].DuplicateFace(False)
            #print surface
            srfs.append(surface)
            try:
                surfaceType = srf.type
            except:
                srf.type = srf.getTypeByNormalAngle()
            
            srf.reEvaluateType(True)
            
            # check for child surfaces
            if srf.hasChild: srf.calculatePunchedSurface()
            
            # assign construction
            srf.construction = srf.cnstrSet[srf.type]
            if srf.EPConstruction == "":
                # if it is not already assigned by user then use default based on type
                srf.EPConstruction = srf.construction
            
        try:
            self.geometry = rc.Geometry.Brep.JoinBreps(srfs, sc.doc.ModelAbsoluteTolerance)[0]
            self.isClosed = self.geometry.IsSolid
            if self.isClosed:
                planarTrigger = False
                try:
                    planarTrigger = self.checkZoneNormalsDir()
                except Exception, e:
                    print '0_Check Zone Normals Direction Failed:\n' + `e`
                if planarTrigger == True:
                    MP3D = rc.Geometry.AreaMassProperties.Compute(self.geometry)
                    self.cenPt = MP3D.Centroid
                    MP3D.Dispose()
            else:
                MP3D = rc.Geometry.AreaMassProperties.Compute(self.geometry)
                self.cenPt = MP3D.Centroid
                MP3D.Dispose()
        except Exception, e:
            print " Failed to create the geometry from the surface:\n" + `e`
        
    def getSrfCenPtandNormal(self, surface):
        brepFace = surface.Faces[0]
        if brepFace.IsPlanar and brepFace.IsSurface:
            u_domain = brepFace.Domain(0)
            v_domain = brepFace.Domain(1)
            centerU = (u_domain.Min + u_domain.Max)/2
            centerV = (v_domain.Min + v_domain.Max)/2
            
            centerPt = brepFace.PointAt(centerU, centerV)
            normalVector = brepFace.NormalAt(centerU, centerV)
        else:
            centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
            uv = brepFace.ClosestPoint(centroid)
            centerPt = brepFace.PointAt(uv[1], uv[2])
            normalVector = brepFace.NormalAt(uv[1], uv[2])
        
        return centerPt, normalVector

    def addSrf(self, srf):
        self.surfaces.append(srf)
    
    def updateConstructionSet(newProgramCode, level = 1):
        """level defines the level of the construction set
        0: low performance; 1: normal; 2: high performance"""
        self.constructionSet = constructionSet[newProgramCode]
    
    def cleanMeshedFaces(self):
        for srf in self.surfaces: srf.disposeCurrentMeshes()
    
    def prepareNonPlanarZone(self, meshingParameters = None, isEnergyPlus = False):
        # clean current meshedFaces
        self.cleanMeshedFaces()
        # collect walls and windows, and roofs
        srfsToBeMeshed = []
        for srf in self.surfaces:
            #clean the meshedFaces if any
            
            # if surface is planar just collect the surface
            if srf.isPlanar or not srf.hasChild: srfsToBeMeshed.append(srf.geometry)
            # else collect the punched wall and child surfaces
            else:
                for fenSrf in srf.childSrfs:
                   srfsToBeMeshed.append(fenSrf.geometry)
                   srfsToBeMeshed.append(fenSrf.parent.punchedGeometry)
                   
        # join surfaces
        joinedBrep = rc.Geometry.Brep.JoinBreps(srfsToBeMeshed, sc.doc.ModelAbsoluteTolerance)[0]
        
        # mesh the geometry
        if meshingParameters == None or type(meshingParameters)!= rc.Geometry.MeshingParameters:
            mp = rc.Geometry.MeshingParameters.Default; disFactor = 3
        else:
            disFactor = 1
            mp = meshingParameters
        meshedGeo = rc.Geometry.Mesh.CreateFromBrep(joinedBrep, mp)
        
        for mesh in meshedGeo:
            # generate quad surfaces for EnergyPlus model
            # if isEnergyPlus:
            #     angleTol = sc.doc.ModelAngleToleranceRadians
            #     minDiagonalRatio = .875
            #     #print mesh.Faces.ConvertTrianglesToQuads(angleTol, minDiagonalRatio)
            #     mesh.Faces.ConvertTrianglesToQuads(angleTol, minDiagonalRatio)
            
            mesh.FaceNormals.ComputeFaceNormals()
            #mesh.FaceNormals.UnitizeFaceNormals()
        
            for faceIndex in  range(mesh.Faces.Count):
                normal = mesh.FaceNormals[faceIndex]
                cenPt = mesh.Faces.GetFaceCenter(faceIndex)
                ##check mesh normal direction
                reverseList = False
                ## make a vector from the center point of the zone to center point of the surface
                testVector = rc.Geometry.Vector3d(cenPt - self.cenPt)
                ## check the direction of the vectors and flip zone surfaces if needed
                if rc.Geometry.Vector3d.VectorAngle(testVector, normal)> 1:
                    normal.Reverse()
                    reverseList = True
                ## create a ray
                #ray = rc.Geometry.Ray3d(cenPt, normal)
                for srf in self.surfaces:
                    if srf.isPlanar or not srf.hasChild:
                        ## shoot a ray from the center of the mesh to each surface
                        #intPt = rc.Geometry.Intersect.Intersection.RayShoot(ray, [srf.geometry], 1) 
                        #if intPt:
                        if cenPt.DistanceTo(srf.geometry.ClosestPoint(cenPt))<0.05 * disFactor:
                            srf.collectMeshFaces(mesh.Faces.GetFaceVertices(faceIndex), reverseList) ## if hit then add this face to that surface
                            break
                    else:
                        for fenSrf in srf.childSrfs:
                            #intPt = rc.Geometry.Intersect.Intersection.RayShoot(ray, [fenSrf.geometry], 1) 
                            #if intPt:
                            if cenPt.DistanceTo(fenSrf.geometry.ClosestPoint(cenPt))<0.05 * disFactor:
                                fenSrf.collectMeshFaces(mesh.Faces.GetFaceVertices(faceIndex), reverseList); break
                            #intPt = rc.Geometry.Intersect.Intersection.RayShoot(ray, [fenSrf.parent.punchedGeometry], 1)
                            #if intPt:
                            if cenPt.DistanceTo(fenSrf.parent.punchedGeometry.ClosestPoint(cenPt))<0.05 * disFactor:
                                srf.collectMeshFaces(mesh.Faces.GetFaceVertices(faceIndex), reverseList); break
    
    def getFloorArea(self):
        totalFloorArea = 0
        for HBSrf in self.surfaces:
            if int(HBSrf.type) == 2:
                totalFloorArea += HBSrf.getTotalArea()
        return totalFloorArea
    
    def getZoneVolume(self):
        return self.geometry.GetVolume()
    
    def getFloorZLevel(self):
        # useful for gbXML export
        minZ = float("inf")
        for HBSrf in self.surfaces:
            if int(HBSrf.type) == 2:
                #get the center point
                centerPt, normalVector = HBSrf.getSrfCenPtandNormalAlternate()
                
                if centerPt.Z < minZ: minZ = centerPt.Z
        return minZ
    
    def setName(self, newName):
        self.name = newName
    
    def __str__(self):
        try:
            return 'Zone name: ' + self.name + \
               '\nZone program: ' + self.bldgProgram + "::" + self.zoneProgram + \
               '\n# of surfaces: ' + `len(self.surfaces)` + \
               '\n-------------------------------------'
        except:
            return 'Zone name: ' + self.name + \
               '\nZone program: Unknown' + \
               '\n# of surfaces: ' + `len(self.surfaces)` + \
               '\n-----------------------------------'

class HB_generatorsystem(object):
    
    def __init__(self,generatorsystem_name,simulationinverter,battery,windgenerators,PVgenerators,fuelgenerators,contextsurfaces,HBzonesurfaces,maintenance_cost):
        
        self.name = generatorsystem_name
        
        if simulationinverter == []:
        
            self.simulationinverter = None
        else:
            self.simulationinverter = simulationinverter
        
        self.maintenance_cost = maintenance_cost
        self.contextsurfaces = contextsurfaces
        self.HBzonesurfaces = HBzonesurfaces
        self.battery = battery
        self.windgenerators = windgenerators # Category includes Generator:WindTurbine
        self.PVgenerators = PVgenerators # Category includes Generator:Photovoltaic
        self.fuelgenerators = fuelgenerators # Category includes Generators:Mircoturbine,Generator:Combustion Turbine,Generator:InternalCombustionEngine

        
class Wind_gen(object):
    
    def __init__(self,name_,rotortype,powercontrol,rotor_speed,rotor_diameter,overall_height,number_of_blades,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,powercoefficients):
        
        self.name = name_
        self.type = 'Generator:WindTurbine'
        self.rotortype = rotortype
        self.powercontrol = powercontrol
        self.numblades = number_of_blades
        self.rotorspeed = rotor_speed
        self.rotor_diameter = rotor_diameter
        self.overall_height = overall_height
        self.powerout = power_output
        self.rated_wind_speed = rated_wind_speed
        self.cut_in_windspeed = cut_in_windspeed
        self.cut_out_windspeed = cut_out_windspeed
        self.overall_turbine_n = overall_turbine_n
        self.max_tip_speed_ratio = max_tip_speed_ratio
        
        self.local_av_windspeed = local_av_windspeed
        self.height_local_metrological_station = height_local_metrological_station
        self.cost_ = turbine_cost
        
        if (powercoefficients != None) or (powercoefficients != []) :
            # Wind turbine is analaytical wind turbine
            self.powercoefficients = powercoefficients
        else:
            self.powercoefficients = None
        
        if max_power_coefficient == None:
            # Only simple wind turbine 
            self.max_power_coefficient = ''
        else: 
            self.max_power_coefficient = max_power_coefficient
        
        
        
class PV_gen(object):
    
    # XXX possible generator types
    """
    Generator:InternalCombustionEngine
    Generator:CombustionTurbine
    Generator:Photovoltaic
    Generator:FuelCell
    Generator:MicroCHP
    Generator:MicroTurbine
    Generator:WindTurbine
    """
    
    def __init__(self,_name,surfacename_,_integrationmode,No_parallel,No_series,costper_module,powerout,namePVperform,SA_solarcells,cell_n,performance_type = "PhotovoltaicPerformance:Simple"):
        
        self.name = _name
        self.surfacename = surfacename_
        self.type = 'Generator:Photovoltaic'
        self.performancetype = performance_type
        self.performancename =  namePVperform # One Photovoltaic performance object is made for each PV object so names are the same
        self.integrationmode = _integrationmode
        self.NOparallel = No_parallel
        self.NOseries = No_series
        
        # Cost and power out of the Generator is the cost and power of each module by the number of modules in each generator
        # number in series by number in parallel.
        
        self.cost_ = costper_module*No_series*No_parallel
        self.powerout = powerout*No_series*No_parallel
        
        self.inverter = None # Define the inverter for this PV generator all PVgenerations being used in the same - run energy simulation must have the same inverter
    
        self.PV_performance(namePVperform,SA_solarcells,cell_n)
        
    def PV_performance(self,namePVperformobject,SA_solarcells = 0.5 ,cell_n = 0.12,cell_efficiencyinputmode = "Fixed", schedule_ = "always on"):
    
        self.namePVperformobject = namePVperformobject
        self.surfaceareacells = SA_solarcells
        self.cellefficiencyinputmode = cell_efficiencyinputmode
        self.efficiency = cell_n
        self.schedule = schedule_
    
class PVinverter(object):
    
    def __init__(self,inverter_name,inverter_cost,inverter_zone,inverter_n,replacement_time):
   
        if inverter_zone == None:
            inverter_zone = ""
        if inverter_n == None:
            inverter_n = 0.9
            
        self.name = inverter_name
        self.cost_ = inverter_cost
        self.efficiency = inverter_n
        self.zone = inverter_zone
        self.replacementtime = replacement_time
        self.ID = str(uuid.uuid4())
        
    # Need to be able to compare inverters to make sure that only one inverter is servicing all the PV in the system
    # For some reason the class ID of the inverters was changing when putting in the hive this is a more fool proof way of comparing them.
    # Note the zone that the inverter is attached to is not considered.
    
    def __hash__(self):
        return hash(self.ID)
       
    def __eq__( self, other ):
        return self.ID == self.ID
        
    def __ne__(self,other):
        return self.ID != self.ID
    
class simple_battery(object):
    
    def __init__(self,_name,zone_name,n_charging,n_discharging,battery_capacity,max_discharging,max_charging,initial_charge,bat_cost,replacement_time):
        
        
        if zone_name == None:
            zone_name = ""
            
        self.name = _name
        self.type = 'Battery:simple'
        self.zonename = zone_name
        self.chargingefficiency = n_charging
        self.dischargingeffciency = n_discharging
        self.batterycap = battery_capacity
        self.maxcharge = max_charging
        self.maxdischarge = max_discharging
        self.initalcharge = initial_charge
        self.cost_ = bat_cost
        
        self.replacementtime = replacement_time
        self.ID = str(uuid.uuid4())
        

class hb_reEvaluateHBZones(object):
    """
    This class check Honeybee zones once more and zones with nonplanar surfaces
    or non-rectangualr glazings recreates the surfaces so the output zones will
    be all zones with planar surfaces, and they can be exported with two functions
    for planar EPSurfaces and planar fenestration.
    
    It also assigns the right boundary condition object to each sub surface
    and checks duplicate names for zones and surfaces and give a warning
    to user to get them fixed.
    """
    
    def __init__(self, inHBZones, meshingParameters):
        # import the classes
        self.hb_EPZone = sc.sticky["honeybee_EPZone"]
        self.hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        self.hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        self.hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        
        self.fakeSurface = rc.Geometry.Brep.CreateFromCornerPoints(
                                            rc.Geometry.Point3d(0,0.5,0),
                                            rc.Geometry.Point3d(-0.5,-0.5,0),
                                            rc.Geometry.Point3d(0.5,-0.5,0),
                                            sc.doc.ModelAbsoluteTolerance)
        self.originalHBZones = inHBZones
        self.meshingParameters = meshingParameters
        #self.triangulate = triangulate
        self.zoneNames = []
        self.srfNames = []
        self.modifiedSrfsNames= []
        self.modifiedGlzSrfsNames = []
        self.adjcGlzSrfCollection = []
        self.adjcSrfCollection = {} #collect adjacent surfaces for nonplanar surfaces
    
    def checkSrfNameDuplication(self, surface):
        if surface.name in self.srfNames:
            warning = "Duplicate surface name!"
            name = surface.name
            while name in self.srfNames:
                name += "_Dup"
                
            surface.name = name
            print warning + " Name is changed to: " + surface.name
            
        self.srfNames.append(surface.name)            
        
        if not surface.isChild and surface.hasChild:
            for child in surface.childSrfs:
                self.checkSrfNameDuplication(child)
                    
    def checkNameDuplication(self, HBZone):
        
        if HBZone.name in self.zoneNames:
            warning = "Duplicate zone name!"
            name = HBZone.name
            while name in self.zoneNames:
                name += "_Dup"
            
            HBZone.name = name            
            print warning + " Name is changed to: " + HBZone.name
            
        self.zoneNames.append(HBZone.name)
        
        for surface in HBZone.surfaces:
            self.checkSrfNameDuplication(surface)
    
    def prepareNonPlanarZones(self, HBZone):
        # prepare nonplanar zones
        if  HBZone.hasNonPlanarSrf or  HBZone.hasInternalEdge:
             HBZone.prepareNonPlanarZone(self.meshingParameters)
    
    
    def createSurface(self, pts):
        """
        # it takes so long if I generate the geometry
        
        if len(pts) == 3:
            return rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], sc.doc.ModelAbsoluteTolerance)
        elif len(pts) == 4:
            return rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], pts[3], sc.doc.ModelAbsoluteTolerance)
        else:
            # create a planar surface
            pts.append(pts[0])
            pl = rc.Geometry.Polyline(pts).ToNurbsCurve()
            return rc.Geometry.Brep.CreatePlanarBreps([pl])[0]
        """
        return self.fakeSurface
        
    def evaluateZones(self):
        for HBZone in self.originalHBZones:
            self.checkNameDuplication(HBZone)
            self.prepareNonPlanarZones(HBZone)
            
            modifiedSurfaces = []
            for surface in HBZone.surfaces:
                srfs = self.checkZoneSurface(surface)
                try: modifiedSurfaces.extend(srfs)
                except: modifiedSurfaces.append(srfs)
            
            # replace surfaces with new ones
            HBZone.surfaces = []
            for HBSrf in modifiedSurfaces:
                HBZone.surfaces.append(HBSrf)
    
    def createSubSurfaceFromBaseSrf(self, surface, newSurfaceName, count, coordinates, glazingBase = False, nameAddition = None):
        
        # pass the wrong geometry for now. I assume creating planar surface from
        # coordinates will be computationally heavy and at this point geometry doesn't
        # matter, since I have the coordinates.
        newSurface = self.hb_EPZoneSurface(self.createSurface(coordinates),
                                           count, newSurfaceName, surface.parent, surface.type)
        newSurface.coordinates = coordinates
        newSurface.type = surface.type # protect the surface from reEvaluate
        newSurface.construction = surface.construction
        newSurface.EPConstruction = surface.EPConstruction
        newSurface.BC = surface.BC
        newSurface.sunExposure = surface.sunExposure
        newSurface.windExposure = surface.windExposure
        newSurface.groundViewFactor = surface.groundViewFactor
        
        if surface.BC.upper() == 'SURFACE':
            adjcSurface = surface.BCObject
            
            if not glazingBase:
                newAdjcSurfaceName = adjcSurface.name + "_srfP_" + `count`
            else:
                try: newAdjcSurfaceName = adjcSurface.name + str(nameAddition)
                except: newAdjcSurfaceName = adjcSurface.name + "_"
                
            newAdjcSurface = self.hb_EPZoneSurface(self.createSurface(coordinates),
                                           count, newAdjcSurfaceName, adjcSurface.parent, adjcSurface.type)
            # reverse the order of points
            restOfcoordinates = list(coordinates[1:])
            restOfcoordinates.reverse()
            newAdjcSurface.coordinates = [coordinates[0]] + restOfcoordinates
            newAdjcSurface.type = adjcSurface.type
            newAdjcSurface.construction = adjcSurface.construction
            newAdjcSurface.EPConstruction = adjcSurface.EPConstruction
            newAdjcSurface.BC = adjcSurface.BC
            newAdjcSurface.sunExposure = adjcSurface.sunExposure
            newAdjcSurface.windExposure = adjcSurface.windExposure
            newAdjcSurface.groundViewFactor = adjcSurface.groundViewFactor
        
            # assign boundary objects
            newSurface.BCObject = newAdjcSurface
            newAdjcSurface.BCObject = newSurface
            
            self.adjcSrfCollection[adjcSurface.name].append(newAdjcSurface)
            
        return newSurface
    
    def createSubGlzSurfaceFromBaseSrf(self, baseChildSurface, parentSurface, glzSurfaceName, count, coordinates):
        
        newFenSrf = self.hb_EPFenSurface(self.createSurface(coordinates),
                                    count, glzSurfaceName, parentSurface, 5, punchedWall = None)
        
        newFenSrf.coordinates = coordinates
        newFenSrf.type = baseChildSurface.type
        newFenSrf.construction = baseChildSurface.construction
        newFenSrf.EPConstruction = baseChildSurface.EPConstruction
        newFenSrf.parent = parentSurface
        newFenSrf.groundViewFactor = baseChildSurface.groundViewFactor
        newFenSrf.shadingControlName = baseChildSurface.shadingControlName
        newFenSrf.frameName = baseChildSurface.frameName
        newFenSrf.Multiplier = baseChildSurface.Multiplier
        newFenSrf.blindsMaterial = baseChildSurface.blindsMaterial
        newFenSrf.shadingControl = baseChildSurface.shadingControl
        newFenSrf.shadingSchName = baseChildSurface.shadingSchName
        
        # Will be overwritten later if needed
        newFenSrf.BCObject = baseChildSurface.BCObject
        newFenSrf.BCObject = baseChildSurface.BCObject
        
        return newFenSrf
        
    def getInsetGlazingCoordinates(self, glzCoordinates):
        # find the coordinates
        def averagePts(ptList):
            pt = rc.Geometry.Point3d(0,0,0)
            for p in ptList: pt = pt + p
            return rc.Geometry.Point3d(pt.X/len(ptList), pt.Y/len(ptList), pt.Z/len(ptList))
            
        distance = 2 * sc.doc.ModelAbsoluteTolerance
        # offset was so slow so I changed the method to this
        pts = []
        for pt in glzCoordinates:
            pts.append(rc.Geometry.Point3d(pt.X, pt.Y, pt.Z))
        cenPt = averagePts(pts)
        insetPts = []
        for pt in pts:
            movingVector = rc.Geometry.Vector3d(cenPt-pt)
            movingVector.Unitize()
            newPt = rc.Geometry.Point3d.Add(pt, movingVector * 2 * sc.doc.ModelAbsoluteTolerance)
            insetPts.append(newPt)
        
        return insetPts
            
    def checkChildSurfaces(self, surface):
        
        def isRectangle(ptList):
            vector1 = rc.Geometry.Vector3d(ptList[0] - ptList[1])
            vector2 = rc.Geometry.Vector3d(ptList[1] - ptList[2])
            vector3 = rc.Geometry.Vector3d(ptList[2] - ptList[3])
            vector4 = rc.Geometry.Vector3d(ptList[3] - ptList[0])
            
            if ptList[0].DistanceTo(ptList[2]) != ptList[1].DistanceTo(ptList[3]) or \
               math.degrees(rc.Geometry.Vector3d.VectorAngle(vector1, vector2))!= 90 or \
               math.degrees(rc.Geometry.Vector3d.VectorAngle(vector3, vector4))!= 90:
                return False
            else:
                return True
        
        def isAntiClockWise(pts, faceNormal):
            
            def crossProduct(vector1, vector2):
                return vector1.X * vector2.X + vector1.Y * vector2.Y + vector1.Z * vector2.Z
            
            # check if the order if clock-wise
            vector0 = rc.Geometry.Vector3d(pts[1]- pts[0])
            vector1 = rc.Geometry.Vector3d(pts[-1]- pts[0])
            ptsNormal = rc.Geometry.Vector3d.CrossProduct(vector0, vector1)
            
            # in case points are anti-clockwise then normals should be parallel
            if crossProduct(ptsNormal, faceNormal) > 0:
                return True
            return False
        
        # get glaing coordinates- coordinates will be returned as lists of lists
        glzCoordinates = surface.extractGlzPoints()
        
        # make sure order is right
        for coorList in glzCoordinates:
            if not isAntiClockWise(coorList, surface.normalVector):
                coorList.reverse()
        
        glzSrfs = []
        if surface.isPlanar:
            for count, coordinates in enumerate(glzCoordinates):
                try: child = surface.childSrfs[count]
                except: child = surface.childSrfs[0]
                
                # if len(surface.childSrfs) == len(glzCoordinates): #not hasattr(glzCoordinates, '__iter__'):
                if len(glzCoordinates)== 1: #not hasattr(glzCoordinates, '__iter__'):
                    # single rectangular glazing - All should be fine
                    # also the adjacent surface will be fine by itself
                    child.coordinates = coordinates
                    self.modifiedGlzSrfsNames.append(child.name)
                else:
                    # surface is planar but glazing is not rectangular
                    # and so it is meshed now and is multiple glazing
                    if len(surface.childSrfs) == len(glzCoordinates):
                        # multiple rectangle windows
                        glzSurfaceName = child.name
                    else:
                        # multiple non-rectangle rectangle window
                        # this naming should be fixed and be based on original surface
                        glzSurfaceName = surface.name + "_glz_" + `count`
                    
                    # create glazing surface
                    HBGlzSrf = self.createSubGlzSurfaceFromBaseSrf(child, surface, glzSurfaceName, count, coordinates)
                    
                    # create adjacent glazingin case needed
                    if surface.BC.upper() == 'SURFACE':
                        # add glazing to adjacent surface
                        if count == 0:
                            adjcSrf = surface.BCObject
                            childSrfsNames = []
                            for childSurface in adjcSrf.childSrfs:  childSrfsNames.append(childSurface.name)
                            adjcSrf.childSrfs = []
                        
                        # add glazing to adjacent surface
                        adjcSrf = surface.BCObject
                        if len(surface.childSrfs) == len(glzCoordinates):
                            glzAdjcSrfName = childSrfsNames[count]
                        else:
                            glzAdjcSrfName = adjcSrf.name + "_glz_" + `count`
                            
                        adjcGlzPt = glzCoordinates[1:]
                        adjcGlzPt.reverse()
                        adjcGlzPt = [glzCoordinates[0]] + adjcGlzPt
                    
                        adjHBGlzSrf = self.createSubGlzSurfaceFromBaseSrf(child, adjcSrf, glzAdjcSrfName, count, adjcGlzPt)
                        
                        # overwrite BC Object
                        adjHBGlzSrf.BCObject = HBGlzSrf
                        HBGlzSrf.BCObject = adjHBGlzSrf
                        
                        adjcSrf.addChildSrf(adjHBGlzSrf)
                    
                    # collect surfaces
                    glzSrfs.append(HBGlzSrf)
            
            # add to parent surface
            if len(glzCoordinates) != 1:
                surface.removeAllChildSrfs()
                surface.addChildSrf(glzSrfs)
          
        else:
            
            # convert nonplanar surface to planar wall surfaces with offset glazing
            # and treat them similar to other surfaces except the fact that if it has
            # another surface next to it the surface should be generated regardless of
            # being single geometry or not
            newSurfaces =[]
            count = 0
            baseChildSrf = surface.childSrfs[0]
            
                
            for count, glzCoordinate in enumerate(glzCoordinates):
                # check if the points are recetangle
                if len(glzCoordinate) == 3 or isRectangle(glzCoordinate):
                    insetGlzCoordinates = [glzCoordinate]
                else:
                    # triangulate
                    insetGlzCoordinates = [glzCoordinate[:3], [glzCoordinate[0],glzCoordinate[2],glzCoordinate[3]]]
                    
                for glzCount, insetGlzCoordinate in enumerate(insetGlzCoordinates):
                    
                    # self.modifiedGlzSrfsNames.append(child.name)
                    # create new Honeybee surfaces as parent surface for glass face
                    if len(insetGlzCoordinates) == 1:
                        newSurfaceName = surface.name + '_glzP_' + `count`
                    else:
                        newSurfaceName = surface.name + '_glzP_' + `count` + '_' + `glzCount`
                        
                    newSurface = self.createSubSurfaceFromBaseSrf(surface, newSurfaceName, count, insetGlzCoordinate, glazingBase = True, nameAddition = '_glzP_' + `count` + '_' + `glzCount`)
                    
                    # collect them here so it will have potential new BC
                    newSurfaces.append(newSurface)
                    
                    # create glazing coordinate and add it to the parent surface
                    insetPts = self.getInsetGlazingCoordinates(insetGlzCoordinate)

                    # create new window and go for it
                    glzSurfaceName = newSurface.name + "_glz_" + `count`
                    
                    HBGlzSrf = self.createSubGlzSurfaceFromBaseSrf(baseChildSrf, newSurface, glzSurfaceName, count, insetPts)
                    
                    if surface.BC.upper() == 'SURFACE':
                        # add glazing to adjacent surface
                        if count == 0:
                            adjcSrf = newSurface.BCObject
                            adjcSrf.childSrfs = []
                        
                        # add glazing to adjacent surface
                        adjcSrf = newSurface.BCObject
                        glzAdjcSrfName = adjcSrf.name + "_glz_" + `count`
                            
                        adjcGlzPt = insetPts[1:]
                        adjcGlzPt.reverse()
                        adjcGlzPt = [insetPts[0]] + adjcGlzPt

                        adjHBGlzSrf = self.createSubGlzSurfaceFromBaseSrf(baseChildSrf, adjcSrf, glzAdjcSrfName, count, adjcGlzPt)
                        
                        # overwrite BC Object
                        adjHBGlzSrf.BCObject = HBGlzSrf
                        HBGlzSrf.BCObject = adjHBGlzSrf
                        
                        adjcSrf.addChildSrf(adjHBGlzSrf)
                        
                    # add to parent surface
                    newSurface.addChildSrf(HBGlzSrf)                        
            
            return newSurfaces
        
    def checkZoneSurface(self, surface):
        if not hasattr(surface, 'coordinates'):
            coordinatesL = surface.extractPoints()
        else:
            coordinatesL = surface.coordinates
        
        # case 0 : it is a planar surface so it is all fine
        if not hasattr(coordinatesL[0], '__iter__'):
            # it is a single surface so just let it go to the modified list
            surface.coordinates = coordinatesL
            self.modifiedSrfsNames.append(surface.name)
            if  not surface.isChild and surface.hasChild:
                self.checkChildSurfaces(surface)
                
            return surface
            
        # case 1 : it is not planar
        else:
            
            # case 1-1 : surface is a nonplanar surface and adjacent to another surface
            # sub surfaces has been already generated based on the adjacent surface
            if surface.BC.upper() == 'SURFACE' and surface.name in self.adjcSrfCollection.keys():
                    # print "collecting sub surfaces for surface " + surface.name
                    # surface has been already generated by the other adjacent surface
                    self.modifiedSrfsNames.append(surface.name)
                    return self.adjcSrfCollection[surface.name]
                    
            # case 1-2 : surface is a nonplanar surface and adjacent to another surface
            # and hasn't been generated so let's generate this surface and the adjacent one
            elif surface.BC.upper() == 'SURFACE':
                adjcSurface= surface.BCObject
                # find adjacent zone and create the surfaces
                # create a place holder for the surface
                # the surfaces will be collected inside the function
                self.adjcSrfCollection[adjcSurface.name] = []
                
            self.modifiedSrfsNames.append(surface.name)
            newSurfaces = []
            for count, coordinates in enumerate(coordinatesL):
                # create new Honeybee surfaces
                # makes sense to copy the original surface here but since
                # copy.deepcopy fails on a number of systems I just create
                # a new surface and assign necessary data to write the surface
                
                newSurfaceName = surface.name + "_srfP_" + `count`
                
                newSurface = self.createSubSurfaceFromBaseSrf(surface, newSurfaceName, count, coordinates)
                
                newSurfaces.append(newSurface)
                
            # nonplanar surface
            if  not surface.isChild and surface.hasChild:
                
                glzPSurfaces = self.checkChildSurfaces(surface)
                
                if glzPSurfaces != None:
                    newSurfaces += glzPSurfaces
                    
            return newSurfaces

class hb_EPSurface(object):
    
    def __init__(self, surface, srfNumber, srfID, *arg):
        """EP surface Class
            surface: surface geometry as a Brep
            srfNumber: a unique number that is only for this surface
            srfID: the unique name for this surface
            *arg is parentZone for EPZoneClasses
            *arg is parentSurface for child surfaces"""
        
        self.objectType = "HBSurface"
        self.geometry = surface
        self.num = srfNumber
        
        self.name = srfID
        
        self.ID = str(uuid.uuid4())
        
        self.isPlanar = self.checkPlanarity()
        self.hasInternalEdge = self.checkForInternalEdge()
        self.meshedFace = rc.Geometry.Mesh()
        self.RadMaterial = None
        self.EPConstruction = None # this gets overwritten below
        
        self.cenPt, self.normalVector = self.getSrfCenPtandNormalAlternate()
        
        self.basePlane = rc.Geometry.Plane(self.cenPt, self.normalVector)
        
        # define if type and BC is defined by user and should be kept
        self.srfTypeByUser = False
        self.srfBCByUser = False
        
        # PV - A Honeybee surface can hold one PV generator
        
        self.PVgenlist = []
        
        # Does this Honeybee surface contain a PV generator?
        
        self.containsPVgen = False
        
        # 4 represents an Air Wall
        self.srfType = {0:'WALL',
           0.5: 'UndergroundWall',
           1:'ROOF',
           1.5: 'UndergroundCeiling',
           2:'FLOOR',
           2.25: 'UndergroundSlab',
           2.5: 'SlabOnGrade',
           2.75: 'ExposedFloor',
           3:'CEILING',
           4:'AIRWALL',
           5:'WINDOW',
           6:'SHADING',
           'WALL': 'WALL',
           'ROOF':'ROOF',
           'FLOOR': 'FLOOR',
           'CEILING': 'CEILING',
           'WINDOW':'WINDOW',
           'SHADING': 'SHADING'}
           
        self.cnstrSet = {0:'Exterior Wall',
                0.5: 'Exterior Wall',
                1: 'Exterior Roof',
                1.5: 'Exterior Roof',
                2:'Interior Floor',
                2.25: 'Exterior Floor',
                2.5: 'Exterior Floor',
                2.75: 'Exterior Floor',
                3:'Interior Ceiling',
                4:'Air Wall',
                5:'Exterior Window',
                6:'Interior Wall'}
        
        self.intCnstrSet = {
                0:'Interior Wall',
                0.5: 'Exterior Wall',
                1:'Exterior Roof',
                1.5:'Exterior Roof',
                2:'Interior Floor',
                2.25: 'Exterior Floor',
                2.5: 'Exterior Floor',
                2.75: 'Exterior Floor',
                3:'Interior Ceiling',
                4:'Air Wall',
                5:'Interior Window',
                6:'Interior Wall'}
        
        self.srfBC = {0:'Outdoors',
                     0.5: 'ground',
                     1:'Outdoors',
                     1.5: 'ground',
                     2: 'outdoors', # this will be changed to surface once solveAdjacency is used 
                     2.25: 'ground',
                     2.5: 'ground',
                     2.75: 'outdoors',
                     3: 'outdoors', # this will be changed to surface once solveAdjacency is used 
                     4: 'surface',
                     5: 'Outdoors',
                     6: 'surface'}
         
        self.srfSunExposure = {0:'SunExposed',
                     0.5:'NoSun',
                     1:'SunExposed',
                     1.5:'NoSun', 
                     2:'NoSun',
                     2.25: 'NoSun',
                     2.5: 'NoSun',
                     2.75: 'SunExposed',
                     3:'NoSun',
                     4:'NoSun',
                     6: 'NoSun'}
             
        self.srfWindExposure = {0:'WindExposed',
                     0.5:'NoWind',
                     1:'WindExposed',
                     1.5:'NoWind',
                     2:'NoWind',
                     2.25:'NoWind',
                     2.5:'NoWind',
                     2.75:'WindExposed',
                     3:'NoWind',
                     4:'NoWind',
                     6:'NoWind'}
        
        self.numOfVertices = 'autocalculate'
        
        if len(arg) == 0:
            # minimum surface
            # A minimum surface is a surface that will be added to a zone later
            # or is a surface that will only be used for daylighting simulation
            # so the concept of parent zone/surface is irrelevant
            self.parent = None
            self.reEvaluateType(True)
        elif len(arg) == 1:
            # represents an opening. The parent is the parent surafce
            # honeybee only supports windows (and not doors) at this point so
            # the type is always the same (window)
            self.parent = arg[0]
        elif len(arg) == 2:
            # represents a normal EP surface
            # parent is a parent zone and the type differs case by case
            self.parent = arg[0] # parent zone
            self.type = arg[1] # surface type (e.g. wall, roof,...)
            self.BC = self.srfBC[self.type] # initial BC based on type
            # check for special conditions(eg. slab underground, slab on ground
            
            self.reEvaluateType(True) # I should give this another thought
            
            # this should be fixed to be based on zone type
            # I can remove default constructions at some point
            self.construction = self.cnstrSet[int(self.type)]
            self.EPConstruction = self.construction
            
    def checkPlanarity(self):
        # planarity tolerance should change for different 
        return self.geometry.Faces[0].IsPlanar(1e-3)
    
    def checkForInternalEdge(self):
        edges = self.geometry.DuplicateEdgeCurves(True)
        edgesJoined = rc.Geometry.Curve.JoinCurves(edges)
        if len(edgesJoined)>1:
            return True
        else:
            return False
    
    class outdoorBCObject(object):
        """
        BCObject for surfaces with outdoor BC
        """
        def __init__(self, name = ""):
            self.name = name
    
    def getAngle2North(self):
        types = [0, 4, 5] # vertical surfaces
        northVector = rc.Geometry.Vector3d.YAxis
        
        # rotate north based on the zone north vector
        try: northVector.Rotate(math.radians(self.parent.north), rc.Geometry.Vector3d.ZAxis)
        except: pass
        
        normalVector = self.getSrfCenPtandNormalAlternate()[1]
        if self.type in types:
            angle =  rc.Geometry.Vector3d.VectorAngle(northVector, normalVector, rc.Geometry.Plane.WorldXY)
        #if normalVector.X < 0: angle = (2* math.pi) - angle
        else: angle = 0
        self.angle2North = math.degrees(angle)
    
    def findDiscontinuity(self, curve, style):
        # copied and modified from rhinoScript (@Steve Baer @GitHub)
        """Search for a derivatitive, tangent, or curvature discontinuity in
        a curve object.
        Parameters:
          curve_id = identifier of curve object
          style = The type of continuity to test for. The types of
              continuity are as follows:
              Value    Description
              1        C0 - Continuous function
              2        C1 - Continuous first derivative
              3        C2 - Continuous first and second derivative
              4        G1 - Continuous unit tangent
              5        G2 - Continuous unit tangent and curvature
        Returns:
          List 3D points where the curve is discontinuous
        """
        dom = curve.Domain
        t0 = dom.Min
        t1 = dom.Max
        points = []
        get_next = True
        while get_next:
            get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
            if get_next:
                points.append(curve.PointAt(t))
                t0 = t # Advance to the next parameter
        return points
    
    def extractMeshPts(self, mesh, triangulate = False):
        coordinatesList = []
        for face in  range(mesh.Faces.Count):
            # get each mesh surface vertices
            if mesh.Faces.GetFaceVertices(face)[3] != mesh.Faces.GetFaceVertices(face)[4]:
                meshVertices = mesh.Faces.GetFaceVertices(face)[1:5]
                # triangulation
                if triangulate or not self.isRectangle(meshVertices):
                    coordinatesList.append(meshVertices[:3])
                    coordinatesList.append([meshVertices[0], meshVertices[2], meshVertices[3]])
                else:
                    coordinatesList.append(list(meshVertices))
            else:
                meshVertices = mesh.Faces.GetFaceVertices(face)[1:4]
                coordinatesList.append(list(meshVertices))
        
        # check order of the points
        for coorCount, coorList in enumerate(coordinatesList):
            # check if clockWise and reverse the list in case it is not
            if not self.isAntiClockWise(coorList):
                try: coorList.reverse()
                except:
                    try: coordinatesList[coorCount] = [coorList[3], coorList[2], coorList[1], coorList[0]]
                    except: coordinatesList[coorCount] = [coorList[2], coorList[1], coorList[0]]
        #coordinatesList.reverse()
        return coordinatesList
        
    
    def isAntiClockWise(self, pts):
        
        def crossProduct(vector1, vector2):
            return vector1.X * vector2.X + vector1.Y * vector2.Y + vector1.Z * vector2.Z
        
        # check if the order if clock-wise
        vector0 = rc.Geometry.Vector3d(pts[1]- pts[0])
        vector1 = rc.Geometry.Vector3d(pts[-1]- pts[0])
        ptsNormal = rc.Geometry.Vector3d.CrossProduct(vector0, vector1)
        
        # in case points are anti-clockwise then normals should be parallel
        if crossProduct(ptsNormal, self.basePlane.Normal) > 0:
            return True
        return False

    
    def extractPoints(self, method = 1, triangulate = False, meshPar = None):
        # if not self.meshedFace.IsValid:
        # meshed surface will be generated regardless
        # to make sure it won't fail for surfaces with multiple openings
        if meshPar == None:
            if self.isPlanar:
                meshPar = rc.Geometry.MeshingParameters.Coarse
                meshPar.SimplePlanes = True
            else:
                meshPar = rc.Geometry.MeshingParameters.Smooth
                
        self.meshedFace = rc.Geometry.Mesh.CreateFromBrep(self.geometry, meshPar)[0]
        
        if self.meshedFace.IsValid or self.hasInternalEdge:
            if self.isPlanar and not self.hasInternalEdge:
                plSegments = self.meshedFace.GetNakedEdges()
                segments = []
                [segments.append(seg.ToNurbsCurve()) for seg in plSegments]
            else:
                return self.extractMeshPts(self.meshedFace,triangulate)
        else:
            segments = self.geometry.DuplicateEdgeCurves(True)
        
        joinedBorder = rc.Geometry.Curve.JoinCurves(segments)
            
        if method == 0:
            pts = []
            [pts.append(seg.PointAtStart) for seg in segments]
        else:
            pts = []
            pts.append(joinedBorder[0].PointAtStart)
            restOfpts = self.findDiscontinuity(joinedBorder[0], style = 4)
            # for some reason restOfPts returns no pt!
            try: pts.extend(restOfpts)
            except: pass
            try: centPt, normalVector = self.getSrfCenPtandNormalAlternate()
            except:  centPt, normalVector = self.parent.getSrfCenPtandNormal(self.geometry)
        
        basePlane = rc.Geometry.Plane(centPt, normalVector)
        
        # inclusion test
        if str(joinedBorder[0].Contains(centPt, basePlane)).lower() != "inside":
            # average points
            cumPt = rc.Geometry.Point3d(0,0,0)
            for pt in pts: cumPt += pt
            centPt = cumPt/len(pts)
            # move basePlane to the new place
            basePlane = rc.Geometry.Plane(centPt, normalVector)
        
        # sort based on parameter on curve
        pointsSorted = sorted(pts, key =lambda pt: joinedBorder[0].ClosestPoint(pt)[1])
            
        
        # check if clockWise and reverse the list in case it is
        if not self.isAntiClockWise(pointsSorted):
            pointsSorted.reverse()
        

        # in case the surface still doesn't have a type
        # it happens for radiance surfaces. For EP it won't happen
        # as it has been already assigned based on the zone
        if not hasattr(self, 'type'):
            self.Type = self.getTypeByNormalAngle()
        
        ## find UpperRightCorner point
        ## I'm changin this to find the LowerLeftCorner point
        ## instead as it is how gbXML needs it
        
        # check the plane
        srfType = self.getTypeByNormalAngle()
        rotationCount = 0
        if srfType == 0:
            # vertical surface
            while basePlane.YAxis.Z <= sc.doc.ModelAbsoluteTolerance and rotationCount < 3:
                # keep rotating for 90 degrees
                basePlane.Rotate(math.radians(90), basePlane.ZAxis)
                rotationCount += 1
                
        elif srfType == 1 or  srfType == 3:            
            # roof + ceiling
            while basePlane.YAxis.Y <=  sc.doc.ModelAbsoluteTolerance and rotationCount < 3:
                # keep rotating for 90 degrees
                basePlane.Rotate(math.radians(90), basePlane.ZAxis)
                rotationCount += 1
                
        elif srfType == 2:
            # floor
            while basePlane.YAxis.Y >= sc.doc.ModelAbsoluteTolerance and rotationCount < 3:
                # keep rotating for 90 degrees
                basePlane.Rotate(math.radians(90), basePlane.ZAxis)
                rotationCount += 1
                
        # remap point on the new plane
        remPts = []
        for pt in pointsSorted: remPts.append(basePlane.RemapToPlaneSpace(pt)[1])
        
        # find UpperRightCorner point (x>0 and max y)
        firstPtIndex = None
        #for ptIndex, pt in enumerate(remPts):
        #    if pt.X > 0 and pt.Y > 0 and firstPtIndex == None:
        #        firstPtIndex = ptIndex #this could be the point
        #    elif pt.X > 0 and pt.Y > 0:
        #        if pt.Y > remPts[firstPtIndex].Y: firstPtIndex = ptIndex
        
        for ptIndex, pt in enumerate(remPts):
            if pt.X < 0 and pt.Y < 0 and firstPtIndex == None:
                firstPtIndex = ptIndex #this could be the point
            elif pt.X < 0 and pt.Y < 0:
                if pt.Y < remPts[firstPtIndex].Y: firstPtIndex = ptIndex
        
        
        if firstPtIndex!=None and firstPtIndex!=0:
            pointsSorted = pointsSorted[firstPtIndex:] + pointsSorted[:firstPtIndex]
        
        return list(pointsSorted)
    
    def isRectangle(self, ptList):
        vector1 = rc.Geometry.Vector3d(ptList[0] - ptList[1])
        vector2 = rc.Geometry.Vector3d(ptList[1] - ptList[2])
        vector3 = rc.Geometry.Vector3d(ptList[2] - ptList[3])
        vector4 = rc.Geometry.Vector3d(ptList[3] - ptList[0])
        
        if ptList[0].DistanceTo(ptList[2]) != ptList[1].DistanceTo(ptList[3]) or \
           math.degrees(rc.Geometry.Vector3d.VectorAngle(vector1, vector2))!= 90 or \
           math.degrees(rc.Geometry.Vector3d.VectorAngle(vector3, vector4))!= 90:
            return False
        else:
            return True
        
        
    def extractGlzPoints(self, RAD = False, method = 2):
        glzCoordinatesList = []
        for glzSrf in self.childSrfs:
            sortedPoints = glzSrf.extractPoints()
            # check numOfPoints
            if len(sortedPoints) < 4 or (self.isPlanar and RAD==True):
                glzCoordinatesList.append(sortedPoints) #triangle
            elif len(sortedPoints) == 4 and self.isPlanar and self.isRectangle(sortedPoints):
                glzCoordinatesList.append(sortedPoints) #rectangle
            else:
                if method == 1:
                    sortedPoints.append(sortedPoints[0])
                    border = rc.Geometry.Polyline(sortedPoints)
                    mesh = rc.Geometry.Mesh.CreateFromClosedPolyline(border)
                elif method == 2:
                    mp = rc.Geometry.MeshingParameters.Smooth
                    mesh = rc.Geometry.Mesh.CreateFromBrep(glzSrf.geometry, mp)[0]
                if mesh:
                    # Make sure non-rectangular shapes with 4 edges will be triangulated
                    if len(sortedPoints) == 4 and self.isPlanar: triangulate= True
                    else: triangulate= False
                    
                    try: glzCoordinatesList.extend(self.extractMeshPts(mesh, triangulate))
                    except: glzCoordinatesList.append(self.extractMeshPts(mesh, triangulate))
                    
        return glzCoordinatesList
    
    def collectMeshFaces(self, meshVertices, reverseList = False):
        mesh = rc.Geometry.Mesh()
        if meshVertices[3]!= meshVertices[4:]:
            mesh.Vertices.Add(meshVertices[1]) #0
            mesh.Vertices.Add(meshVertices[2]) #1
            mesh.Vertices.Add(meshVertices[3]) #2
            mesh.Vertices.Add(meshVertices[4]) #3
            if not reverseList: mesh.Faces.AddFace(0, 1, 2, 3)
            else: mesh.Faces.AddFace(0, 1, 2, 3)
        else:
            mesh.Vertices.Add(meshVertices[1]) #0
            mesh.Vertices.Add(meshVertices[2]) #1
            mesh.Vertices.Add(meshVertices[3]) #2
            if not reverseList: mesh.Faces.AddFace(0, 1, 2)
            else: mesh.Faces.AddFace(0, 1, 2)
        
        self.meshedFace.Append(mesh)
        #print self.meshedFace.Faces.Count
    
    def disposeCurrentMeshes(self):
        if self.meshedFace.Faces.Count>0:
            self.meshedFace.Dispose()
            self.meshedFace = rc.Geometry.Mesh()
        if self.hasChild:
            for fenSrf in self.childSrfs:
                if fenSrf.meshedFace.Faces.Count>0:
                    fenSrf.meshedFace.Dispose()
                    fenSrf.meshedFace = rc.Geometry.Mesh()
    
    def getSrfCenPtandNormalAlternate(self):
        brepFace = self.geometry.Faces[0]
        if brepFace.IsPlanar and brepFace.IsSurface:
            u_domain = brepFace.Domain(0)
            v_domain = brepFace.Domain(1)
            centerU = (u_domain.Min + u_domain.Max)/2
            centerV = (v_domain.Min + v_domain.Max)/2
            
            centerPt = brepFace.PointAt(centerU, centerV)
            normalVector = brepFace.NormalAt(centerU, centerV)
        else:
            centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
            uv = brepFace.ClosestPoint(centroid)
            centerPt = brepFace.PointAt(uv[1], uv[2])
            normalVector = brepFace.NormalAt(uv[1], uv[2])
        
        return centerPt, normalVector
    
    def isUnderground(self, wall = False):
        """
        check if this surface is underground
        """
        # extract points
        coordinatesList = self.extractPoints()
        # create a list of list
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        
        for ptList in coordinatesList:
            for pt in ptList:
                if not wall and pt.Z - rc.Geometry.Point3d.Origin.Z >= sc.doc.ModelAbsoluteTolerance: return False
                elif pt.Z >= sc.doc.ModelAbsoluteTolerance: return False
        return True
        
    def isOnGrade(self):
        """
        check if this surface is underground
        """
        # extract points
        coordinatesList = self.extractPoints()
        # create a list of list
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        
        for ptList in coordinatesList:
            for pt in ptList:
                if abs(pt.Z - rc.Geometry.Point3d.Origin.Z) >= sc.doc.ModelAbsoluteTolerance: return False
        return True
        
    def reEvaluateType(self, overwrite= True):
        """
        Find special surface types
        """
        if not overwrite and hasattr(self, "type"): return self.type
        
        if self.srfTypeByUser: return self.type
        
        if self.srfBCByUser: return self.type
        
        # find initial type it has no type yet
        if not hasattr(self, "type"):
            self.type = self.getTypeByNormalAngle()
            self.BC = "OUTDOORS"
            
        if self.type == 0:
            if self.isUnderground(True):
                self.type += 0.5 #UndergroundWall
                self.BC = "GROUND"
                
        elif self.type == 1:
            # A roof underground will be assigned as UndergroundCeiling!
            if self.isUnderground():
                self.type += 0.5 #UndergroundCeiling
                self.BC = "GROUND"
            elif self.BC.upper() == "SURFACE":
                self.type == 3 # ceiling
            
        elif self.type == 2:
            # floor
            if self.isOnGrade():
                self.type += 0.5 #SlabOnGrade
                self.BC = "GROUND"
            elif self.isUnderground():
                self.type += 0.25 #UndergroundSlab
                self.BC = "GROUND"
            elif self.BC.upper() != "SURFACE":
                self.type += 0.75 #Exposed floor
        
        # update boundary condition based on new type
        self.BC = self.srfBC[self.type]
        
    def getTypeByNormalAngle(self, maximumRoofAngle = 30):
        # find the normal
        try: findNormal = self.getSrfCenPtandNormalAlternate()
        except: findNormal = self.parent.getSrfCenPtandNormal(self.geometry) #I should fix this at some point - Here just for shading surfaces for now
        
        if findNormal:
            try:
                normal = findNormal[1]
                angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            except:
                print self
                print rc.Geometry.AreaMassProperties.Compute(self.geometry).Centroid
                angle2Z = 0
        else:
            #print findNormal
            angle2Z = 0
        
        if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
            try:
                if self.isThisTheTopZone:
                    return 1 #roof
                else:
                    return 3 # ceiling
            except:
                return 1 #roof
                
        elif  160 < angle2Z <200:
            return 2 # floor
        
        else:
            return 0 #wall
    
    def getTotalArea(self):
        return self.geometry.GetArea()
    
    def setType(self, type, isUserInput = False):
        self.type = type
        self.srfTypeByUser = isUserInput
    
    def setBC(self, BC, isUserInput = False):
        self.BC = BC
        self.srfBCByUser = isUserInput
    
    def setBCObject(self, BCObject):
        self.BCObject = BCObject
    
    def setBCObjectToOutdoors(self):
        self.BCObject = self.outdoorBCObject()
    
    def setEPConstruction(self, EPConstruction):
        self.EPConstruction = EPConstruction
    
    def setRADMaterial(self, RADMaterial):
        self.RadMaterial = RADMaterial
    
    def setName(self, newName, isUserInput = False):
        self.name = newName
        self.srfNameByUser = isUserInput
        
    def setSunExposure(self, exposure = 'NoSun'):
        self.sunExposure = exposure
    
    def setWindExposure(self, exposure = 'NoWind'):
        self.windExposure = exposure
    

    def __str__(self):
        try:
            return 'Surface name: ' + self.name + '\nSurface number: ' + str(self.num) + \
                   '\nThis surface is a ' + str(self.srfType[self.type]) + "."
        except:
            return 'Surface name: ' + self.name + '\n' + 'Surface number: ' + str(self.num) + \
                   '\nSurface type is not assigned. Honeybee thinks this is a ' + str(self.srfType[self.getTypeByNormalAngle()]) + "."


class hb_EPZoneSurface(hb_EPSurface):
    """..."""
    def __init__(self, surface, srfNumber, srfName, *args):
        """This function initiates the class for an EP surface.
            surface: surface geometry as a Brep
            srfNumber: a unique number that is only for this surface
            srfName: the unique name for this surface
            parentZone: class of the zone that this surface belongs to"""
        if len(args)==2:
            parentZone, surafceType = args
            hb_EPSurface.__init__(self, surface, srfNumber, srfName, parentZone, surafceType)
            self.getAngle2North()
            
            self.BCObject = self.outdoorBCObject()

        else:
            hb_EPSurface.__init__(self, surface, srfNumber, srfName)
            
            # Check for possible surface type and assign the BC based on that
            # This will be re-evaluated in write idf file
            srfType = self.getTypeByNormalAngle()
            self.BC = self.srfBC[srfType]
            self.BCObject = self.outdoorBCObject()
            self.sunExposure = self.srfSunExposure[srfType]
            self.windExposure = self.srfWindExposure[srfType]
            self.getAngle2North()
            
        
        if hasattr(self, 'parent') and self.parent!=None:
            # in both of this cases the zone should be meshed
            if not self.isPlanar:
                self.parent.hasNonPlanarSrf = True
            if self.hasInternalEdge:
                self.parent.hasInternalEdge = True
        
        if hasattr(self, 'type'):
            self.sunExposure = self.srfSunExposure[self.type]
            self.windExposure = self.srfWindExposure[self.type]
        
        self.groundViewFactor = 'autocalculate'
        self.hasChild = False
        self.isChild = False
        self.childSrfs = []
    
    def isPossibleChild(self, chidSrfCandidate, tolerance = sc.doc.ModelAbsoluteTolerance):
        # check if all the vertices has 0 distance with the base surface
        segments = chidSrfCandidate.DuplicateEdgeCurves(True)
        pts = []
        [pts.append(seg.PointAtStart) for seg in segments]
        
        for pt in pts:
            ptOnSrf = self.geometry.ClosestPoint(pt)
            if pt.DistanceTo(ptOnSrf) > tolerance: return False
        
        # check the area of the child surface and make sure is smaller than base surface
        #if self.geometry.GetArea() <= chidSrfCandidate.GetArea():
        #    print "The area of the child surface cannot be larger than the area of the parent surface!"
        #    return False
        
        # all points are located on the surface and the area is less so it is all good!
        return True
    
    def addChildSrf(self, childSurface, percentage = 40):
        # I should copy/paste the function here so I can run it as
        # a method! For now I just collect them here together....
        # use the window function
        try: self.childSrfs.extend(childSurface)
        except: self.childSrfs.append(childSurface)
        self.hasChild = True
        pass
    
    def calculatePunchedSurface(self):
        
        def checkCrvArea(crv):
            try:
                area = rc.Geometry.AreaMassProperties.Compute(crv).Area
            except:
                area = 0
            
            return area > sc.doc.ModelAbsoluteTolerance
        
        def checkCrvsPts(crv):
            # in some cases crv generates a line with similar points
            pts = []
            pts.append(crv.PointAtStart)
            restOfpts = self.findDiscontinuity(crv, style = 4)
            # for some reason restOfPts returns no pt!
            try: pts.extend(restOfpts)
            except: pass
            
            def isDuplicate(pt, newPts):
                for p in newPts:
                    # print pt.DistanceTo(p)
                    if pt.DistanceTo(p) < 2 * sc.doc.ModelAbsoluteTolerance:
                        return True
                return False
                
            newPts = [pts[0]]
            for pt in pts[1:]:
                if not isDuplicate(pt, newPts):
                    newPts.append(pt)
                    if len(newPts) > 2:
                        return True
            return False
            
        glzCrvs = []
        childSrfs = []
        for glzSrf in self.childSrfs:
            glzEdges = glzSrf.geometry.DuplicateEdgeCurves(True)
            jGlzCrv = rc.Geometry.Curve.JoinCurves(glzEdges)[0]
            # in some cases glazing based on percentage generates very small glazings
            # here I check and remove them
            
            # check area of curve
            try:
                if self.isPlanar:
                    area = rc.Geometry.AreaMassProperties.Compute(jGlzCrv).Area
                else:
                    area = rc.Geometry.AreaMassProperties.Compute(glzSrf.geometry).Area
            except:
                # in case area calulation fails
                # let it go anyways!
                area = 10 * sc.doc.ModelAbsoluteTolerance
            
            if  area > sc.doc.ModelAbsoluteTolerance and checkCrvsPts(jGlzCrv):
                
                # check normal direction of child surface and base surface
                # print math.degrees(rc.Geometry.Vector3d.VectorAngle(glzSrf.normalVector, self.normalVector))
                
                childSrfs.append(glzSrf)
                glzCrvs.append(jGlzCrv)
            else:
                print "A very tiny glazing is removed from " + self.name+ "."
                
        self.childSrfs = childSrfs
        
        baseEdges = self.geometry.DuplicateEdgeCurves(True)
        
        jBaseCrv = rc.Geometry.Curve.JoinCurves(baseEdges)
        
        # convert array to list
        jBaseCrvList = list(jBaseCrv)
        
        try:
            if self.isPlanar:
                # works for planar surfaces
                punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(glzCrvs + jBaseCrvList)
                
                if len(punchedGeometries) == 1:
                    self.punchedGeometry = punchedGeometries[0]
                else:
                    # curves are not in the same plane so let's
                    # project the curves on surface plane
                    srfPlane = rc.Geometry.Plane(self.cenPt, self.normalVector)
                    PGlzCrvs = []
                    for curve in glzCrvs + jBaseCrvList:
                        pCrv = rc.Geometry.Curve.ProjectToPlane(curve, srfPlane)
                        if checkCrvArea:
                            PGlzCrvs.append(pCrv)
                    
                    punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(PGlzCrvs)
                    # in some cases glazing with very minor areas are generated
                    # which causes multiple surfaces
                    self.punchedGeometry = punchedGeometries[-1]
            else:
                # split the base geometry - Good luck!
                splitBrep = self.geometry.Faces[0].Split(glzCrvs, sc.doc.ModelAbsoluteTolerance)
                
                #splitBrep.Faces.ShrinkFaces()
                
                for srfCount in range(splitBrep.Faces.Count):
                    surface = splitBrep.Faces.ExtractFace(srfCount)
                    edges = surface.DuplicateEdgeCurves(True)
                    joinedEdges = rc.Geometry.Curve.JoinCurves(edges)
                    
                    if len(joinedEdges)>1:
                        self.punchedGeometry = surface
                                        
        except Exception, e:
            self.punchedGeometry = None
            self.hasChild = False
            self.childSrfs = []
            print "Failed to calculate opaque part of the surface. " + \
                  "Glazing is removed from " + self.name

    def getOpaqueArea(self):
        if self.hasChild:
            try:
                return self.punchedGeometry.GetArea()
            except:
                self.calculatePunchedSurface()
                return self.punchedGeometry.GetArea()
        else:
            return self.getTotalArea()
    
    def getGlazingArea(self):
        if self.hasChild:
            glzArea = 0
            for childSrf in self.childSrfs:
                glzArea += childSrf.getTotalArea()
            return glzArea
        else:
            return 0
    
    def getWWR(self):
        return self.getGlazingArea()/self.getTotalArea()
        
    def removeAllChildSrfs(self):
        self.childSrfs = []
        self.hasChild = False
        self.calculatePunchedSurface()

class hb_EPShdSurface(hb_EPSurface):
    def __init__(self, surface, srfNumber, srfName):
        hb_EPSurface.__init__(self, surface, srfNumber, srfName, self)
        
        self.PVgenlist = None
        
        self.containsPVgen = None
        self.TransmittanceSCH = ''
        self.isChild = False
        self.hasChild = False
        self.construction = 'Exterior Wall' # just added here to get the minimum surface to work
        self.EPConstruction = 'Exterior Wall' # just added here to get the minimum surface to work
        self.childSrfs = [self] # so I can use the same function as glazing to extract the points
        self.type = 6
        
        pass
  
    def getSrfCenPtandNormal(self, surface):
        brepFace = surface.Faces[0]
        if brepFace.IsPlanar and brepFace.IsSurface:
            u_domain = brepFace.Domain(0)
            v_domain = brepFace.Domain(1)
            centerU = (u_domain.Min + u_domain.Max)/2
            centerV = (v_domain.Min + v_domain.Max)/2
            
            centerPt = brepFace.PointAt(centerU, centerV)
            normalVector = brepFace.NormalAt(centerU, centerV)
        else:
            centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
            uv = brepFace.ClosestPoint(centroid)
            centerPt = brepFace.PointAt(uv[1], uv[2])
            normalVector = brepFace.NormalAt(uv[1], uv[2])
        
        return centerPt, normalVector

class hb_EPFenSurface(hb_EPSurface):
    """..."""
    def __init__(self, surface, srfNumber, srfName, parentSurface, surafceType, punchedWall = None):
        """This function initiates the class for an EP surface.
            surface: surface geometry as a Brep
            srfNumber: a unique number that is only for this surface
            srfName: the unique name for this surface
            parentZone: class of the zone that this surface belongs to"""
        hb_EPSurface.__init__(self, surface, srfNumber, srfName, parentSurface, surafceType)
        
        self.blindsMaterial = ""
        self.shadingControl = ""
        self.shadingSchName = ""
        
        if not self.isPlanar:
            try:
                self.parent.parent.hasNonplanarSrf = True
            except:
                # surface is not part of a zone yet.
                pass

        # calculate punchedWall
        self.parent.punchedGeometry = punchedWall
        self.shadingControlName = ''
        self.frameName = ''
        self.Multiplier = 1
        self.BCObject = self.outdoorBCObject()
        self.groundViewFactor = 'autocalculate'
        self.isChild = True # is it really useful?


class generationhb_hive(object):
    # A hive that only accepts Honeybee generation objects
    
    def addToHoneybeeHive(self, genObjects, GHComponentID):
        
        if not sc.sticky.has_key('HBHivegeneration'): sc.sticky['HBHivegeneration'] = {}
        
        generationobjectkeys = []
        
        if isinstance(genObjects, tuple):
            
            key = GHComponentID
            
            sc.sticky['HBHivegeneration'][key] = genObjects
            
            generationobjectkeys.append(key)
            
            return generationobjectkeys
        
        else:
            
            
            for genObject in genObjects:
    
                key = GHComponentID
                
                sc.sticky['HBHivegeneration'][key] = genObject
                
                generationobjectkeys.append(key)
     
            return generationobjectkeys
        
    def callFromHoneybeeHive(self, HBObjectslist):
        
        generationobjects = []
            
        for HBObjectkey in HBObjectslist:
            
            genobject =  sc.sticky['HBHivegeneration'][HBObjectkey]
            generationobjects.append(genobject)
        
        return generationobjects

class thermPolygon(object):
    def __init__(self, surfaceGeo, material, srfName, RGBColor):
        #Set the name and material.
        self.objectType = "ThermPolygon"
        self.hasChild = False
        self.name = srfName
        
        #Check if the material exists in the THERM Library and, if not, add it.
        if material in sc.sticky["honeybee_thermMaterialLib"].keys():
            if sc.sticky["honeybee_thermMaterialLib"][material]["RGBColor"] == RGBColor: pass
            else: material = self.makeThermMatFromEPMat(material+str(RGBColor), RGBColor)
        else:
            material = self.makeThermMatFromEPMat(material, RGBColor)
        self.material = material
        
        #Extract the segments of the polyline and make sure none of them are curved.
        segm = surfaceGeo.DuplicateEdgeCurves()
        self.segments = []
        for seg in segm:
            if seg.IsLinear: self.segments.append(seg)
            else:
                rc.Geometry.Curve.ToPolyline(0,0,0.1,0,0,sc.doc.ModelAbsoluteTolerance,0,0,True)
                self.segments.append(seg)
        #Build a new Polygon from the segments.
        self.polylineGeo = rc.Geometry.Curve.JoinCurves(self.segments, sc.doc.ModelAbsoluteTolerance)[0]
        
        #Build surface geometry and extract the vertices.
        self.geometry = rc.Geometry.Brep.CreatePlanarBreps(self.polylineGeo)[0]
        self.vertices = []
        for vertex in self.geometry.DuplicateVertices():
            self.vertices.append(vertex)
        
        #Make note of the plane in which the surface lies.
        self.plane = self.geometry.Faces[0].TryGetPlane(sc.doc.ModelAbsoluteTolerance)
        
        return self.geometry
    
    def makeThermMatFromEPMat(self, material, RGBColor):
        #Make a sub-dictionary for the material.
        sc.sticky["honeybee_thermMaterialLib"][material] = {}
        
        #Create the material with just default values.
        sc.sticky["honeybee_thermMaterialLib"][material]["Material Name"] = 0
        sc.sticky["honeybee_thermMaterialLib"][material]["Type"] = 0
        sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] = None
        sc.sticky["honeybee_thermMaterialLib"][material]["Absorptivity"] = 0.5
        sc.sticky["honeybee_thermMaterialLib"][material]["Emissivity"] = 0.9
        sc.sticky["honeybee_thermMaterialLib"][material]["RGBColor"] = RGBColor
        
        #Unpack values from the decomposed material to replace the defaults.
        hb_EPMaterialAUX = EPMaterialAux()
        values, comments, UValueSI, UValueIP = hb_EPMaterialAUX.decomposeMaterial(material)
        
        for count, comment in enumerate(comments):
            if "CONDUCTIVITY" in comment.upper(): sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] = float(values[count])
            if "EMISSIVITY" in comment.upper(): sc.sticky["honeybee_thermMaterialLib"][material]["Emissivity"] = float(values[count])
        
        #If there is no conductivity found, it might be an air material, in which case we set the value.
        if values[0] == "WindowMaterial:Gas":
            sc.sticky["honeybee_thermMaterialLib"][material]["Type"] = 1
            sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] = 0.435449
            sc.sticky["honeybee_thermMaterialLib"][material]["CavityModel"] = 5
        elif sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] == None:
            #This is a no-mass material and we are not going to be able to figure out a conductivity. The best we can do is give a warning.
            if values[0] == "WindowMaterial:SimpleGlazingSystem": sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] = values[2]*0.01
            elif values[0] == "WindowMaterial:NoMass": sc.sticky["honeybee_thermMaterialLib"][material]["Conductivity"] = values[3]/0.01
            warning = "You have connected a No-Mass material and, as a result, Honeybee can not figure out what conductivity the material has. \n " +\
            "Honeybee is going to assume that the No-mass material is vert thin with a thickness of 1 cm but we might be completely off.  n\ " +\
            "Try connecting a material with mass or make you own THERM material."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        return material


class hb_Hive(object):
    
    class CopyClass(object):
        pass
    
    def addToHoneybeeHive(self, HBObjects, GHComponentID):
        # check if the honeybeedictionary already existed
        # if not create the dictionary
        # eventually this should be generated as soon as they user let the bee fly
        if not sc.sticky.has_key('HBHive'): sc.sticky['HBHive'] = {}
        geometries = []
        childGeometries = []
        
        for HBObject in HBObjects:
            key = GHComponentID + HBObject.name
            
            sc.sticky['HBHive'][key] = HBObject
            
            # assuming that all the HBOBjects has a geometry! I assume they do
            
            try:
                if HBObject.objectType != "HBZone" and HBObject.hasChild:
                    if HBObject.punchedGeometry == None:
                        HBObject.calculatePunchedSurface()
                    geo = HBObject.punchedGeometry.Duplicate()
                    geometry = geo.Duplicate()
                    for childObject in HBObject.childSrfs:
                        # for now I only return the childs as geometries and not objects
                        # it could cause some confusion for the users that I will try to
                        # address later
                        childGeometries.append(childObject.geometry.Duplicate())
                    # join geometries into a single surface
                    geometry = rc.Geometry.Brep.JoinBreps([geometry] + childGeometries, sc.doc.ModelAbsoluteTolerance)[0]
                
                elif HBObject.objectType == "HBZone":
                    geo = HBObject.geometry
                    geometry = geo.Duplicate()
                    srfs = []
                    zoneHasChildSrf = False
                    for HBSrf in HBObject.surfaces:
                        if HBSrf.hasChild:
                            zoneHasChildSrf = True
                            srfs.append(HBSrf.punchedGeometry.Duplicate())
                            for childObject in HBSrf.childSrfs:
                                # for now I only return the childs as geometries and not objects
                                # it could cause some confusion for the users that I will try to
                                # address later
                                srfs.append(childObject.geometry.Duplicate())
                        else:
                            srfs.append(HBSrf.geometry.Duplicate())
                            
                    if zoneHasChildSrf:
                        geometry = rc.Geometry.Brep.JoinBreps(srfs, sc.doc.ModelAbsoluteTolerance)[0]
                        
                else:
                    geo = HBObject.geometry
                    geometry = geo.Duplicate()
                geometry.UserDictionary.Set('HBID', key)
                geometries.append(geometry)
            except Exception, e:
                print "Reached the maximum array size for UserDictionary: " + `e`
                    
        # return geometry with the ID
        return geometries
        
    def callFromHoneybeeHive(self, geometryList):
        HBObjects = []
        for geometry in geometryList:
            try:
                key = geometry.UserDictionary['HBID']
                if sc.sticky['HBHive'].has_key(key):
                    try:
                        HBObject = sc.sticky['HBHive'][key]
                        # after the first round meshedFace makes copy.deepcopy crash
                        # so I need to regenerate meshFaces
                        if HBObject.objectType == "HBZone":
                            for surface in HBObject.surfaces:
                                newMesh = rc.Geometry.Mesh()
                                newMesh.Append(surface.meshedFace)
                                surface.meshedFace = newMesh
                        elif HBObject.objectType == "HBSurface": 
                            newMesh = rc.Geometry.Mesh()
                            newMesh.Append(HBObject.meshedFace)
                            HBObject.meshedFace = newMesh
                        
                        HBObjects.append(copy.deepcopy(HBObject))
                        
                    except Exception, e:
                        print `e`
                        print "Failed to copy the object. Returning the original objects...\n" +\
                        "This can cause strange behaviour!"
                        HBObjects.append(sc.sticky['HBHive'][key])
            except:
                pass
                
        return HBObjects

class hb_RADParameters(object):
    def __init__(self):
        self.radParDict = {
        "_ab_": [2, 3, 6],
        "_ad_": [512, 2048, 4096],
        "_as_": [128, 2048, 4096],
        "_ar_": [16, 64, 128],
        "_aa_": [.25, .2, .1],
        "_ps_": [8, 4, 2],
        "_pt_": [.15, .10, .05],
        "_pj_": [.6, .9, .9],
        "_dj_": [0, .5, .7],
        "_ds_": [.5, .25, .05],
        "_dt_": [.5, .25, .15],
        "_dc_": [.25, .5, .75],
        "_dr_": [0, 1, 3],
        "_dp_": [64, 256, 512],
        "_st_": [.85, .5, .15],
        "_lr_": [4, 6, 8],
        "_lw_": [.05, .01, .005],
        "_av_": [0, 0, 0],
        "xScale": [1, 2, 6],
        "yScale": [1, 2, 6]
        }

class hb_DSParameters(object):
    
    def __init__(self, outputUnits = [2], dynamicSHDGroup_1 = None,  dynamicSHDGroup_2 = None, RhinoViewsName = [] , adaptiveZone = False, dgp_imageSize = 250, onlyRunGlareAnalysis = True):
        
        if len(outputUnits)!=0 and outputUnits[0]!=None: self.outputUnits = outputUnits
        else: self.outputUnits = [2]
        
        self.onlyAnnualGlare = onlyRunGlareAnalysis
        self.runAnnualGlare = False
        
        self.RhinoViewsName = RhinoViewsName
        if RhinoViewsName != []:
            self.runAnnualGlare = True
        
        if adaptiveZone == None: adaptiveZone = False
        self.adaptiveZone = adaptiveZone
        
        if not dgp_imageSize: dgp_imageSize = 250
        self.dgp_imageSize = dgp_imageSize
        
        if dynamicSHDGroup_1 == None and dynamicSHDGroup_2==None:
            
            class dynamicSHDRecipe(object):
                def __init__(self, type = 1, name = "no_blind"):
                    self.type = type
                    self.name = name
            
            self.DShdR = [dynamicSHDRecipe(type = 1, name = "no_blind")]
            
        else:
            self.DShdR = []
            if dynamicSHDGroup_1 != None: self.DShdR.append(dynamicSHDGroup_1)
            if dynamicSHDGroup_2 != None: self.DShdR.append(dynamicSHDGroup_2)
        
        # Number of ill files
        self.numOfIll = 1
        for shadingRecipe in self.DShdR:
            if shadingRecipe.name == "no_blind":
                pass
            elif shadingRecipe.name == "conceptual_dynamic_shading":
                self.numOfIll += 1
            else:
                # advanced dynamic shading
                self.numOfIll += len(shadingRecipe.shadingStates) - 1
        
        # print "number of ill files = " + str(self.numOfIll)

class CalculateGridBasedDLAnalysisResults(object):
    """
    calculate results of any grid based analysis
    analysisType: [0] illuminance, [1] radiation, [2] luminance, [3] daylight factor, [4] vertical sky component
    """
    def __init__(self, resultFiles, analysisType):
        self.analysisType = analysisType
        self.resultFiles = resultFiles
        
    def getResults(self):
        resultValues = []
        studyType= self.analysisType
        for fileCount, resultFile in enumerate(self.resultFiles):
            if studyType == 0 or studyType == 2:
                #illuminance / luminance
                resultValues.extend(self.readDLResult(resultFile))
            elif studyType == 1:
                # radiation
                resultValues.extend(self.readRadiationResult(resultFile))
            elif studyType == 3 or studyType == 4:
                resultValues.extend(self.readDFResult(resultFile))
        
        return resultValues
    
    def readRadiationResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile:
            result.append(float(line.split('	')[0]))
        return result
    
    def readDLResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile:
            R, G, B = line.split('	')[0:3]
            result.append(179*(.265 * float(R) + .67 * float(G) + .065 * float(B)))
        return result
    
    def readDFResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile:
            R, G, B = line.split('	')[0:3]
            # divide by the sky horizontal illuminance = 1000
            res = 17900*(.265 * float(R) + .67 * float(G) + .065 * float(B))/1000
            if res > 100: res = 100
            result.append(res)
        return result

class SerializeObjects(object):
    
    def __init__(self, filePath, data = None):
        self.filePath = filePath
        self.data = data
    
    def saveToFile(self):
        with open(self.filePath, 'wb') as outf:
            pickle.dump(self.data, outf)
    
    def readFromFile(self):
        with open(self.filePath, 'rb') as inf:
            self.data = pickle.load(inf)

class hb_hwBoilerParams(object):
    def __init__(self):
        self.hwBoilerDict = {
        'name':'honeybeeHotWaterBoiler',
        'fueltype':1,
        'nominalCapacity':'Autosize',
        'sizingFactor':1.25,
        'nominalEfficiency':0.80,
        'designOutletTemperature':80,
        'designWaterFlowRate':'Autosize',
        'minPartLoad':0.15,
        'maxPartLoadRatio':1.1,
        'optimumPartLoadRatio':0.50,
        'outletTempMaximum':95,
        'boilerFlowMode':'NotModulated',
        'parasiticElectricLoad':0,
        'curveTemperatureVariable':'LeavingBoiler',
        'Curves':None
        }

class hb_availManagerParams(object):
    def __init__(self):
        self.manListDict= {
        'name':'honeybee default AvailabilityManagerList',
        'type':'NightCycle',
        'scheduleName':'ALWAYS ON',
        'controlType':'CycleOnAny'
        }

class hb_chillerEIRParams(object):
    def __init__(self):
        self.chillerDict= {
            'name':'honeybee Default Chiller',
            'rCapacity':'Autosize',
            'rCOP':5.5,
            'rLeavingChWt':6.667,
            'rEnteringCWT':29.44,
            'rChWFlowRate':'Autosize',
            'rCWFlowRate':'Autosize',
            'minPartLoadRatio':0.1,
            'maxPartLoadRatio':1.0,
            'optimumPartLoadRatio':1.0,
            'minUnloadingRatio':0.2,
            'condenserType':0,
            'condenserFanPowerRatio':None,
            'fracOfCompressorPowerRej':1.0,
            'chillerFlowMode':0,
            'sizingFactor':1.15,
            'Curves':None
            }
            
class hb_coolingTowerParams(object):
    def __init__(self):
        self.coolTowerDict= {
            'name':'honeybee default cooling tower',
            'speedControl':'OneSpeed',
            'inputMethod':'NominalCapacity',
            'modelType':'CoolToolsCrossFlow',
            'designWB':25.5556,
            'designRange':5.5556,
            'designApproach':3.8889,
            'sizingFactor':1.15,
            'nominalCapacity':'Autosized',
            'designWaterFlowRate':'Autosized',
            'airflowAtHighSpeed':'Autosized',
            'fanPowerAtHighSpeed':'Autosized',
            'lowSpeedCapacity':'Autosized',
            'airflowAtLowSpeed':'Autosized',
            'fanPowerAtLowSpeed':'Autosized',
            'freeConvectionCapacity':'Autosized',
            'airflowInFreeConvection':'Autosized',
            'basinHeaterCapacity':0,
            'basinHeaterSetpoint':2,
            'basinHeaterSchedule':None,
            'numberOfCells':1,
            'cellControl':'NotNeeded',
            'cellMinWaterFlowFraction':0.33,
            'cellMaxWaterFlowFraction':2.5,
            'fanPowerRatioFlowRatioCurve':None
        }

class hb_airsideEconoParams(object):
    def __init__(self):
        self.airEconoDict = {
        'name':'honeybeeDefaultEconomizer',
        'econoControl':'FixedDryBulb',
        'controlAction':'Modulate Flow',
        'maxAirFlowRate':'Autosize',
        'minAirFlowRate':'Autosize',
        'minLimitType':'Proportional Minimum',

        'minOutdoorAirSchedule':None,
        'minOutdoorAirFracSchedule':None,
        'maxLimitDewpoint':None,
        'sensedMin':12,
        'sensedMax':22,
        'DXLockoutMethod':None,
        'timeOfDaySch':'ALWAYS ON',
        'mvCtrl':None,
        'availManagerList':None
        }

class hb_constVolFanParams(object):
    def __init__(self):
        self.cvFanDict = {
        'name':'honeybeeConstVolFan',
        'type':0,
        'fanEfficiency':0.6,
        'pressureRise':892.9,
        'maxFlowRate':'Autosize',
        'motorEfficiency':0.825,
        'airStreamHeatPct':100.0
        }

class hb_varVolFanParams(object):
    def __init__(self):
        self.vvFanDict = {
        'name':'honeybeeConstVolFan',
        'type':1,
        'fanEfficiency':0.6,
        'pressureRise':892.9,
        'maxFlowRate':'Autosize',
        'motorEfficiency':0.825,
        'airStreamHeatPct':100.0,
        'minFlowFrac':0.2,
        'fanPowerCoefficient1':0.04076,
        'fanPowerCoefficient2':0.08804,
        'fanPowerCoefficient3':-0.07292,
        'fanPowerCoefficient4':0.94373,
        'fanPowerCoefficient5':0.00000
        }
        
class hb_AirHandlerParams(object):
    def __init__(self):
        self.airHandlerDict = {
        'availSch':None,
        'fanPlacement':'DrawThrough',
        'coolingAirflow':'Autosize',
        'coolingOAflow':'Autosize',
        'heatingAirflow': 'Autosize',
        'heatingOAflow': 'Autosize',
        'floatingAirflow':'Autosize',
        'floatingOAflow':'Autosize',
        'constVolSupplyFanDef':hb_constVolFanParams,
        'varVolSupplyFanDef':hb_varVolFanParams,
        'airsideEconomizer':hb_airsideEconoParams,
        'coolingCoil': None,
        'heatingCoil': None,
        'evaporativeCondenser': None,
        'availabilityManagerList':None
        }

class hb_2xDXCoilParams(object):
    def __init__(self):
        self.twoSpeedDXDict = {
        'name':'honeybee Default 2 Speed DX Coil',
        'availSch':'OpenStudio Default',
        'ratedHighSpeedAirflowRate':'Autosize',
        'ratedHighSpeedTotalCooling':'Autosize',
        'ratedHighSpeedSHR':'Autosize',
        'ratedHighSpeedCOP':3.0,
        'ratedLowSpeedAirflowRate':'Autosize',
        'ratedLowSpeedTotalCooling':'Autosize',
        'ratedLowSpeedSHR':'Autosize',
        'ratedLowSpeedCOP':3.0,
        'condenserType':'AirCooled',
        'evaporativeCondenserDesc':None,
        'Curves':None
        }
        
class hb_2xDXHeatingCoilParams(object):
    def __init__(self):
        self.twoSpeedDXDict = {
        'name':'honeybee Default 2 Speed DX Heating Coil',
        'availSch':'OpenStudio Default',
        'ratedHighSpeedAirflowRate':'Autosize',
        'ratedHighSpeedTotalHeating':'Autosize',
        'ratedHighSpeedCOP':4.0,
        'ratedLowSpeedAirflowRate':'Autosize',
        'ratedLowSpeedTotalCooling':'Autosize',
        'ratedLowSpeedCOP':5.0,
        'minOutdoorDryBulb':-8,
        'outdoorDBDefrostEnabled': 5,
        'outdoorDBCrankcase':10,
        'crankcaseCapacity': 0,
        'defrostStrategy':'reverse-cycle',
        'defrostControl':'timed',
        'resistiveDefrostCap':0,
        'Curves': None
        }

class hb_1xDXCoilParams(object):
    def __init__(self):
        self.oneSpeedDXDict = {
        'name':'honeybee Default 1 Speed DX Coil',
        'availSch':'OpenStudio Default',
        'ratedAirflowRate':'Autosize',
        'ratedTotalCooling':'Autosize',
        'ratedSHR':'Autosize',
        'ratedCOP':3.0,
        'condenserType':'Air Cooled',
        'evaporativeCondenserDesc':None,
        'Curves':None
        }

class hb_1xDXHeatingCoilParams(object):
    def __init__(self):
        self.oneSpeedDXDict = {
        'name':'honeybee Default 1 speed DX Heating Coil',
        'availSch':'OpenStudio Default',
        'ratedAirflowRate':'Autosize',
        'ratedTotalHeating':'Autosize',
        'ratedCOP':3.0,
        'minOutdoorDryBulb': -8,
        'outdoorDBDefrostEnabled': 5,
        'outdoorDBCrankcase':10,
        'crankcaseCapacity': 0,
        'defrostStrategy':'reverse-cycle',
        'defrostControl':'timed',
        'resistiveDefrostCap':0,
        'Curves': None
        }
        
class hb_lspeedEvapCondParams(object):
    def __init__(self):
            self.lspeedevapCond = {
            'name':'honeybee default 1 speed DX condenser',
            'serviceType':0,
            'evapEffectiveness':0.9,
            'evapCondAirflowRate':'Autosize',
            'evapPumpPower':'Autosize',
            'storageTank':None,
            'curves':None
            }

class hb_hspeedEvapCondParams(object):
    def __init__(self):
        self.hspeedevapCond = {
        'name':'honeybee default 1 speed DX condenser',
        'serviceType':0,
        'evapEffectiveness':0.9,
        'evapCondAirflowRate':'Autosize',
        'evapPumpPower':'Autosize',
        'hiEvapEffectiveness':0.9,
        'hiEvapCondAirflowRate':'Autosize',
        'hiEvapPumpPower':'Autosize',
        'storageTank':None,
        'curves':None
        }

letItFly = True

def checkGHPythonVersion(target = "0.6.0.3"):
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

try:
    downloadTemplate = checkIn.checkForUpdates(LB= False, HB= True, OpenStudio = True, template = True)
except:
    # no internet connection
    downloadTemplate = False

GHPythonTargetVersion = "0.6.0.3"

try:
    if not checkGHPythonVersion(GHPythonTargetVersion):
        assert False
except:
    msg =  "Honeybee failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    checkIn.letItFly = False
    sc.sticky["honeybee_release"] = False

if checkIn.letItFly:
    if not sc.sticky.has_key("honeybee_release") or True:
        w = gh.GH_RuntimeMessageLevel.Warning
        sc.sticky["honeybee_release"] = versionCheck()
        folders = hb_findFolders()
        
        sc.sticky["honeybee_folders"] = {}
        
        if folders.RADPath == None:
            if os.path.isdir("c:\\radiance\\bin\\"):
                folders.RADPath = "c:\\radiance\\bin\\"
            else:
                msg= "Honeybee cannot find RADIANCE folder on your system.\n" + \
                     "Make sure you have RADIANCE installed on your system.\n" + \
                     "You won't be able to run daylighting studies without RADIANCE.\n" + \
                     "A good place to install RADIANCE is c:\\radiance"
                ghenv.Component.AddRuntimeMessage(w, msg)
                folders.RADPath = ""
        
        if  folders.RADPath.find(" ") > -1:
            msg =  "There is a white space in RADIANCE filepath: " + folders.RADPath + "\n" + \
                   "Please install RADIANCE in a valid address (e.g. c:\\radiance)"
            ghenv.Component.AddRuntimeMessage(w, msg)
            folders.RADPath = ""
            
        # I should replace this with python methods in os library
        # looks stupid!
        if folders.RADPath.endswith("\\"): segmentNumber = -2
        else: segmentNumber = -1
        hb_RADLibPath = "\\".join(folders.RADPath.split("\\")[:segmentNumber]) + "\\lib"
        
        sc.sticky["honeybee_folders"]["RADPath"] = folders.RADPath
        sc.sticky["honeybee_folders"]["RADLibPath"] = hb_RADLibPath
            
        if folders.DSPath == None:
            if os.path.isdir("c:\\daysim\\bin\\"):
                folders.DSPath = "c:\\daysim\\bin\\"
            else:
                msg= "Honeybee cannot find DAYSIM folder on your system.\n" + \
                     "Make sure you have DAYISM installed on your system.\n" + \
                     "You won't be able to run annual climate-based daylighting studies without DAYSIM.\n" + \
                     "A good place to install DAYSIM is c:\\DAYSIM"
                ghenv.Component.AddRuntimeMessage(w, msg)
                folders.DSPath = ""
        
        if folders.DSPath.find(" ") > -1:
            msg =  "There is a white space in DAYSIM filepath: " + folders.DSPath + "\n" + \
                   "Please install Daysism in a valid address (e.g. c:\\daysim)"
            ghenv.Component.AddRuntimeMessage(w, msg)
            folders.DSPath = ""
            
        if folders.DSPath.endswith("\\"): segmentNumber = -2
        else: segmentNumber = -1
        hb_DSCore = "\\".join(folders.DSPath.split("\\")[:segmentNumber])
        hb_DSLibPath = "\\".join(folders.DSPath.split("\\")[:segmentNumber]) + "\\lib"
        
        sc.sticky["honeybee_folders"]["DSPath"] = folders.DSPath
        sc.sticky["honeybee_folders"]["DSCorePath"] = hb_DSCore
        sc.sticky["honeybee_folders"]["DSLibPath"] = hb_DSLibPath
    
        # supported versions for EnergyPlus
        EPVersions = ["V8-3-0", "V8-2-10", "V8-2-9", "V8-2-8", "V8-2-7", "V8-2-6", \
                      "V8-2-5", "V8-2-4", "V8-2-3", "V8-2-2", "V8-2-1", "V8-2-0", \
                      "V8-1-5", "V8-1-4", "V8-1-3", "V8-1-2", "V8-1-1", "V8-1-0"]
                      
        
        if folders.EPPath != None:
            # Honeybee has already found EnergyPlus make sure it's an acceptable version
            EPVersion = os.path.split(folders.EPPath)[-1].split("EnergyPlus")[-1]
            
            if EPVersion not in EPVersions:
                #Not an acceptable version so remove it from the path
                folders.EPPath = None
            
        if folders.EPPath == None:
            for EPVersion in EPVersions:
                if os.path.isdir("C:\EnergyPlus" + EPVersion + "\\"):
                    folders.EPPath = "C:\EnergyPlus" + EPVersion + "\\"

                    break
            
            if folders.EPPath == None:
                # give a warning to the user
                
                msg= "Honeybee cannot find a compatible EnergyPlus folder on your system.\n" + \
                     "Make sure you have EnergyPlus installed on your system.\n" + \
                     "You won't be able to run energy simulations without EnergyPlus.\n" +\
                     "Honeybee supports following versions:\n"
                
                versions = ", ".join(EPVersions)
                
                msg += versions
                
                ghenv.Component.AddRuntimeMessage(w, msg)
                
            
        sc.sticky["honeybee_folders"]["EPPath"] = folders.EPPath  

        sc.sticky["honeybee_folders"]["EPVersion"] = EPVersion.replace("-", ".")[1:]
        sc.sticky["honeybee_RADMaterialAUX"] = RADMaterialAux
        
        # set up radiance materials
        sc.sticky["honeybee_RADMaterialAUX"](True)
        
        # Download EP libraries
        templateFilesPrep = PrepareTemplateEPLibFiles(downloadTemplate)
        libFilePaths = templateFilesPrep.downloadTemplates()
        
        if libFilePaths != -1:
            EPLibs = HB_GetEPLibraries()
            EPLibs.loadEPConstructionsAndMaterials(libFilePaths)
            EPLibs.loadEPSchedules(libFilePaths)
        else:
            msg = "Failed to load EP constructions! You won't be able to run analysis with Honeybee!\n" + \
                      "Download the files from address below and copy them to: " + sc.sticky["Honeybee_DefaultFolder"] + \
                      "\nhttps://github.com/mostaphaRoudsari/Honeybee/tree/master/resources"
            print msg
            ghenv.Component.AddRuntimeMessage(w, msg)
            
            
        sc.sticky["honeybee_Hive"] = hb_Hive
        sc.sticky["honeybee_generationHive"] = generationhb_hive
        sc.sticky["honeybee_GetEPLibs"] = HB_GetEPLibraries
        sc.sticky["honeybee_DefaultMaterialLib"] = materialLibrary
        sc.sticky["honeybee_DefaultScheduleLib"] = scheduleLibrary
        sc.sticky["honeybee_DefaultSurfaceLib"] = EPSurfaceLib
        sc.sticky["honeybee_EPMaterialAUX"] = EPMaterialAux
        sc.sticky["honeybee_EPScheduleAUX"] = EPScheduleAux
        sc.sticky["honeybee_EPObjectsAUX"] = EPObjectsAux
        sc.sticky["honeybee_ReadSchedules"] = ReadEPSchedules
        sc.sticky["honeybee_BuildingProgramsLib"] = BuildingProgramsLib
        sc.sticky["honeybee_EPTypes"] = EPTypes()
        sc.sticky["honeybee_EPZone"] = EPZone
        sc.sticky["honeybee_ThermPolygon"] = thermPolygon
        sc.sticky["PVgen"] = PV_gen
        sc.sticky["PVinverter"] = PVinverter
        sc.sticky["HB_generatorsystem"] = HB_generatorsystem
        sc.sticky["wind_generator"] = Wind_gen
        sc.sticky["simple_battery"] = simple_battery
        sc.sticky["honeybee_reEvaluateHBZones"] = hb_reEvaluateHBZones
        sc.sticky["honeybee_AirsideEconomizerParams"] = hb_airsideEconoParams
        sc.sticky["honeybee_constantVolumeFanParams"] = hb_constVolFanParams
        sc.sticky["honeybee_variableVolumeFanParams"] = hb_varVolFanParams
        sc.sticky["honeybee_AirHandlerParams"] = hb_AirHandlerParams
        sc.sticky["honeybee_2xDXCoilParams"] = hb_2xDXCoilParams
        sc.sticky["honeybee_2xDXHeatingCoilParams"] = hb_2xDXHeatingCoilParams
        sc.sticky["honeybee_1xDXCoilParams"] = hb_1xDXCoilParams
        sc.sticky["honeybee_1xDXHeatingCoilParams"] = hb_1xDXHeatingCoilParams
        sc.sticky["honeybee_lspeedevapcondParams"] = hb_lspeedEvapCondParams
        sc.sticky["honeybee_hspeedevapcondParams"] = hb_hspeedEvapCondParams
        sc.sticky["honeybee_hwBoilerParams"] = hb_hwBoilerParams
        sc.sticky["honeybee_chillerEIRParams"] = hb_chillerEIRParams
        sc.sticky["honeybee_coolingTowerParams"] = hb_coolingTowerParams
        sc.sticky["honeybee_availManagerList"] = hb_availManagerParams
        sc.sticky["honeybee_EPSurface"] = hb_EPSurface
        sc.sticky["honeybee_EPShdSurface"] = hb_EPShdSurface
        sc.sticky["honeybee_EPZoneSurface"] = hb_EPZoneSurface
        sc.sticky["honeybee_EPFenSurface"] = hb_EPFenSurface
        sc.sticky["honeybee_DLAnalysisRecipe"] = DLAnalysisRecipe
        sc.sticky["honeybee_MeshToRAD"] = hb_MSHToRAD
        sc.sticky["honeybee_WriteRAD"] = hb_WriteRAD
        sc.sticky["honeybee_WriteRADAUX"] = hb_WriteRADAUX
        sc.sticky["honeybee_WriteDS"] = hb_WriteDS
        sc.sticky["honeybee_RADParameters"] = hb_RADParameters
        sc.sticky["honeybee_DSParameters"] = hb_DSParameters
        sc.sticky["honeybee_ReadAnnualResultsAux"] = hb_ReadAnnualResultsAux
        sc.sticky["honeybee_EPParameters"] = hb_EnergySimulatioParameters
        sc.sticky["honeybee_SerializeObjects"] = SerializeObjects
        sc.sticky["honeybee_GridBasedDLResults"] = CalculateGridBasedDLAnalysisResults
        sc.sticky["honeybee_DLAnalaysisTypes"] = {0: ["0: illuminance" , "lux"],
                                                  1: ["1: radiation" , "wh/m2"],
                                                  1.1: ["1.1: cumulative radiation" , "kWh/m2"],
                                                  2: ["2: luminance" , "cd/m2"],
                                                  3: ["3: DF", "%"],
                                                  4: ["4: VSC", "%"],
                                                  5: ["5: annual analysis", "var"]}
                                                 
        # done! sharing the happiness.
        print "Hooohooho...Flying!!\nVviiiiiiizzz..."