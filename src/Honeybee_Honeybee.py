# This is the heart of the Honeybee
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component carries all of Honeybee's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!
-
Honeybee started by Mostapha Sadeghipour Roudsari is licensed
under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
Based on a work at https://github.com/mostaphaRoudsari/Honeybee.
-
Check this link for more information about the license:
http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
-
Source code is available at:
https://github.com/mostaphaRoudsari/Honeybee
-
Provided by Honeybee 0.0.51
    
    Args:
        letItFly: Set Boolean to True to let the Honeybee fly!
    Returns:
        report: Current Honeybee mood!!!
"""

ghenv.Component.Name = "Honeybee_Honeybee"
ghenv.Component.NickName = 'Honeybee'
ghenv.Component.Message = 'VER 0.0.52\nMAR_14_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import shutil
import sys
import os
import System.Threading.Tasks as tasks
import System
import time
from itertools import chain
import datetime
import copy
PI = math.pi

rc.Runtime.HostUtils.DisplayOleAlerts(False)

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

class hb_GetEPConstructions():
    
    def __init__(self, workingDir = "c:\\ladybug"):
        
        def downloadFile(url, workingDir):
            import urllib
            webFile = urllib.urlopen(url)
            localFile = open(workingDir + '/' + url.split('/')[-1], 'wb')
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()
        
        # create the folder if it is not there
        if not os.path.isdir(workingDir): os.mkdir(workingDir)
        
        # download template file
        if not os.path.isfile(workingDir + '\OpenStudioMasterTemplate.idf'):
            try:
                ## download File
                print 'Downloading OpenStudioMasterTemplate.idf to ', workingDir
                downloadFile(r'https://dl.dropboxusercontent.com/u/16228160/honeybee/OpenStudioMasterTemplate.idf', workingDir)
            except:
                print 'Download failed!!! You need OpenStudioMasterTemplate.idf to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
        else:
            pass
        
        if not os.path.isfile(workingDir + '\OpenStudioMasterTemplate.idf'):
            print 'Download failed!!! You need OpenStudioMasterTemplate.idf to use honeybee.' + \
                '\nPlease check your internet connection, and try again!'
            return -1
        else:
            libFilePaths = [workingDir + '\OpenStudioMasterTemplate.idf']
            # print 'Download complete!'
        
        if os.path.isfile("c:/ladybug/userCustomLibrary.idf"):
            libFilePaths.append("c:/ladybug/userCustomLibrary.idf")
        
        
        
        def createObject(openFile, resultDict, key, scheduleType = None):
            # This function creates a dictionary from EPObjects
            if key not in resultDict.keys():
                # create an empty dictionary for the key
                resultDict[key] = {}
            # store the data into the dictionary
            for lineCount, line in enumerate(inf):
                if lineCount == 0:
                    nameKey = line.split("!-")[0].strip()[:-1]
                    
                    if nameKey in resultDict[key].keys():
                        # this means the material is already in the lib
                        # I can rename it but for now I rather to give a warning
                        # and break the loop
                        warning = "The " + key + ": " + nameKey + " is already existed in the libaray.\n" + \
                                  "You need to rename this " + key + "."
                        print warning
                        break
                    else:
                        # add the material to the library
                        resultDict[key][nameKey] = {}
                        if scheduleType!=None: resultDict[key][nameKey][0] = scheduleType
                        
                else:
                    objValue = line.split("!-")[0].strip()
                    try: objDescription = line.split("!-")[1].strip()
                    except:  objDescription = ""
                    objKey = lineCount #+ '_' + line.split("!-")[1].strip()
        
                    if objValue.endswith(","):
                        resultDict[key][nameKey][objKey] = objValue[:-1], objDescription
                    elif objValue.endswith(";"):
                        resultDict[key][nameKey][objKey] = objValue[:-1], objDescription
                        break
            return resultDict
        
        if not sc.sticky.has_key("honeybee_constructionLib"):
            print "Loading EP construction library"
            resultDict = {}
            EPKeys = ["Material", "WindowMaterial", "Construction"]
            for libFilePath in libFilePaths:
                with open(libFilePath, 'r') as inf:
                    for line in inf:
                        for key in EPKeys:
                            if line.strip().startswith(key):
                                resultDict = createObject(inf, resultDict, key, line.strip()[:-1])
                outputs = { "Material" : [],
                            "WindowMaterial" : [],
                            "Construction" : []}
                
                for EPKey in EPKeys:
                    if EPKey in resultDict.keys():
                        try:
                            for key in resultDict[EPKey].keys(): outputs[EPKey].append(key)
                            print  `len(resultDict[EPKey].keys())` + " " + EPKey.lower() + " found in " + libFilePath
                        except:
                            outputs[key] = " 0 " + EPKey.lower() + " found in " + libFilePath
                
                materialList = outputs["Material"]
                windowMat =  outputs["WindowMaterial"]
                constrList = outputs["Construction"]
                
                sc.sticky ["honeybee_constructionLib"] = resultDict["Construction"]
                sc.sticky ["honeybee_materialLib"] = resultDict["Material"]
                sc.sticky ["honeybee_windowMaterialLib"] = resultDict["WindowMaterial"]
                sc.sticky ["honeybee_constructionLib"]["List"] = outputs["Construction"]
                sc.sticky ["honeybee_materialLib"]["List"] = outputs["Material"]
                sc.sticky ["honeybee_windowMaterialLib"]["List"] = outputs["WindowMaterial"]
                
        if not sc.sticky.has_key("honeybee_ScheduleLib") or True:
            print "\nLoading EP schedules..."
            EPKeys = ["ScheduleTypeLimits", "Schedule"]
            schedulesDict = {}
            for libFilePath in libFilePaths:
                with open(libFilePath, 'r') as inf:
                    for line in inf:
                        for key in EPKeys:
                            if line.strip().startswith(key):
                                schedulesDict = createObject(inf, schedulesDict, key, line.strip()[:-1])
                                break
                
                scheduleOutputs = { "Schedule" : [],
                            "ScheduleTypeLimits" : []}
                            
                for EPKey in EPKeys:
                    if EPKey in schedulesDict.keys():
                        try:
                            for key in schedulesDict[EPKey].keys(): scheduleOutputs[EPKey].append(key)
                            print  `len(schedulesDict[EPKey].keys())` + " " + EPKey.lower() + " found in " + libFilePath
                        except:
                            scheduleOutputs[key] = " 0 " + EPKey.lower() + " found in " + libFilePath
                
                sc.sticky["honeybee_ScheduleLib"] = schedulesDict["Schedule"]
                sc.sticky["honeybee_ScheduleTypeLimitsLib"] = schedulesDict["ScheduleTypeLimits"]
                sc.sticky["honeybee_ScheduleLib"]["List"] = scheduleOutputs["Schedule"]
                sc.sticky["honeybee_ScheduleTypeLimitsLib"]["List"] = scheduleOutputs["ScheduleTypeLimits"]
            print "\n"

class RADMaterialAux(object):
    
    def __init__(self, reloadRADMaterial = False):
            
        self.radMatTypes = ["plastic", "glass", "trans", "metal", "mirror", "mixedfunc", "dielectric", "transdata", "light", "glow"]
        
        if reloadRADMaterial:
            
            # initiate the library
            if not sc.sticky.has_key("honeybee_RADMaterialLib"): sc.sticky ["honeybee_RADMaterialLib"] = {}
            
            # add default materials to the library
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', '000_Context_Material', .35, .35, .35, 0, 0.1), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', '000_Interior_Ceiling', .80, .80, .80, 0, 0.1), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', '000_Interior_Floor', .2, .2, .2, 0, 0.1), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('glass', '000_Exterior_Window', .60, .60, .60), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', '000_Exterior_Roof', .35, .35, .35, 0, 0.1), True, True)
            self.analyseRadMaterials(self.createRadMaterialFromParameters('plastic', '000_Exterior_Wall', .50, .50, .50, 0, 0.1), True, True)
            
            # import user defined RAD library
            RADLibraryFile = r"c:\ladybug\HoneybeeRadMaterials.mat"
            if os.path.isfile(RADLibraryFile):
                self.importRADMaterialsFromFile(RADLibraryFile)
            else:
                if not os.path.isdir("c:\\ladybug"):
                    os.mkdir("c:\\ladybug")
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
    
    def addToGlobalLibrary(self, RADMaterial, RADLibraryFile = r"c:\ladybug\HoneybeeRadMaterials.mat"):
        
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
                   
        # construction str
        self.cnstrStr ='\n' +\
            'Construction,\n' +\
            '\t000_Exterior_Wall,        !- Name\n' +\
            '\t000_M01 100mm brick,      !- Outside Layer\n' +\
            '\t000_M15 200mm heavyweight concrete,  !- Layer 2\n' +\
            '\t000_I02 50mm insulation board,  !- Layer 3\n' +\
            '\t000_F04 Wall air space resistance,  !- Layer 4\n' +\
            '\t000_G01a 19mm gypsum board;  !- Layer 5\n\n' +\
            '\n' +\
            'Construction,\n' +\
            '\t000_Exterior_Floor,       !- Name\n' +\
            '\t000_I02 50mm insulation board,  !- Outside Layer\n' +\
            '\t000_M15 200mm heavyweight concrete;  !- Layer 2\n\n' +\
            '\n' +\
            'Construction,\n' +\
            '\t000_Exterior_Roof,        !- Name\n' +\
            '\t000_M11 100mm lightweight concrete,  !- Outside Layer\n' +\
            '\t000_F05 Ceiling air space resistance,  !- Layer 2\n' +\
            '\t000_F16 Acoustic tile;    !- Layer 3\n\n' + \
            '\n' +\
            'Construction,\n' +\
            '\t000_Exterior_Window,      !- Name\n' +\
            '\t000_Clear 3mm,            !- Outside Layer\n' +\
            '\t000_Air 13mm,             !- Layer 2\n' +\
            '\t000_Clear 3mm;            !- Layer 3\n' +\
            '\n' +\
            'Construction,\n' + \
            '\t000_Interior_Floor,      !- Name\n' + \
            '\t000_F16 Acoustic tile,   !- Outside Layer\n' + \
            '\t000_F05 Ceiling air space resistance,  !- Layer 2\n' + \
            '\t000_M11 100mm lightweight concrete;  !- Layer 3\n' + \
            '\n' + \
            'Construction,\n' + \
            '\t000_Interior_Ceiling,      !- Name\n' + \
            '\t000_M11 100mm lightweight concrete,   !- Outside Layer\n' + \
            '\t000_F05 Ceiling air space resistance,  !- Layer 2\n' + \
            '\t000_F16 Acoustic tile;  !- Layer 3\n' + \
            '\n' + \
            'Construction,\n' + \
            '\tAir Wall,                !- Name\n' + \
            '\tAir Wall_Material;       !- Outside Layer\n'
            
            #idfFile.write(cnstrStr)
            #print cnstrStr
            
        self.materialStr = '\n' + \
            'Material,\n' +\
            '\t000_M01 100mm brick,      !- Name\n' +\
            '\tMediumRough,              !- Roughness\n' +\
            '\t0.1016,                   !- Thickness {m}\n' +\
            '\t0.89,                     !- Conductivity {W/m-K}\n' +\
            '\t1920,                     !- Density {kg/m3}\n' +\
            '\t790;                      !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'Material:AirGap,\n' +\
            '\t000_F04 Wall air space resistance,  !- Name\n' +\
            '\t0.15;                     !- Thermal Resistance {m2-K/W}\n' +\
            '\n' +\
            'Material,\n' +\
            '\t000_G01a 19mm gypsum board,  !- Name\n' +\
            '\tMediumSmooth,             !- Roughness\n' +\
            '\t0.019,                    !- Thickness {m}\n' +\
            '\t0.16,                     !- Conductivity {W/m-K}\n' +\
            '\t800,                      !- Density {kg/m3}\n' +\
            '\t1090;                     !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'Material,\n' +\
            '\t000_I02 50mm insulation board,  !- Name\n' +\
            '\tMediumRough,              !- Roughness\n' +\
            '\t0.0508,                   !- Thickness {m}\n' +\
            '\t0.03,                     !- Conductivity {W/m-K}\n' +\
            '\t43,                       !- Density {kg/m3}\n' +\
            '\t1210;                     !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'Material,\n' +\
            '\t000_M15 200mm heavyweight concrete,  !- Name\n' +\
            '\tMediumRough,              !- Roughness\n' +\
            '\t0.2032,                   !- Thickness {m}\n' +\
            '\t1.95,                     !- Conductivity {W/m-K}\n' +\
            '\t2240,                     !- Density {kg/m3}\n' +\
            '\t900;                      !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'Material,\n' +\
            '\t000_M11 100mm lightweight concrete,  !- Name\n' +\
            '\tMediumRough,              !- Roughness\n' +\
            '\t0.1016,                   !- Thickness {m}\n' +\
            '\t0.53,                     !- Conductivity {W/m-K}\n' +\
            '\t1280,                     !- Density {kg/m3}\n' +\
            '\t840;                      !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'Material:AirGap,\n' +\
            '\t000_F05 Ceiling air space resistance,  !- Name\n' +\
            '\t0.18;                     !- Thermal Resistance {m2-K/W}\n' +\
            '\n' +\
            'Material,\n' +\
            '\t000_F16 Acoustic tile,    !- Name\n' +\
            '\tMediumSmooth,             !- Roughness\n' +\
            '\t0.0191,                   !- Thickness {m}\n' +\
            '\t0.06,                     !- Conductivity {W/m-K}\n' +\
            '\t368,                      !- Density {kg/m3}\n' +\
            '\t590;                      !- Specific Heat {J/kg-K}\n' +\
            '\n' +\
            'WindowMaterial:Glazing,\n' +\
            '\t000_Clear 3mm,            !- Name\n' +\
            '\tSpectralAverage,          !- Optical Data Type\n' +\
            '\t,                         !- Window Glass Spectral Data Set Name\n' +\
            '\t0.003,                    !- Thickness {m}\n' +\
            '\t0.837,                    !- Solar Transmittance at Normal Incidence\n' +\
            '\t0.075,                    !- Front Side Solar Reflectance at Normal Incidence\n' +\
            '\t0.075,                    !- Back Side Solar Reflectance at Normal Incidence\n' +\
            '\t0.898,                    !- Visible Transmittance at Normal Incidence\n' +\
            '\t0.081,                    !- Front Side Visible Reflectance at Normal Incidence\n' +\
            '\t0.081,                    !- Back Side Visible Reflectance at Normal Incidence\n' +\
            '\t0,                        !- Infrared Transmittance at Normal Incidence\n' +\
            '\t0.84,                     !- Front Side Infrared Hemispherical Emissivity\n' +\
            '\t0.84,                     !- Back Side Infrared Hemispherical Emissivity\n' +\
            '\t0.9;                      !- Conductivity {W/m-K}\n' +\
            '\n' +\
            'WindowMaterial:Gas,\n' +\
            '\t000_Air 13mm,             !- Name\n' +\
            '\tAir,                      !- Gas Type\n' +\
            '\t0.0127;                   !- Thickness {m}\n' +\
            '\n' + \
            'Material,\n' +\
            '\tAir Wall_Material,       !- Name\n' +\
            '\tMediumSmooth,            !- Roughness\n' +\
            '\t0.01,                    !- Thickness {m}\n' +\
            '\t0.59999999999999998,     !- Conductivity {W/m-K}\n' +\
            '\t800,                     !- Density {kg/m3}\n' +\
            '\t1000,                    !- Specific Heat {J/kg-K}\n' +\
            '\t0.94999999999999996,     !- Thermal Absorptance\n' +\
            '\t0.69999999999999996,     !- Solar Absorptance\n' +\
            '\t0.69999999999999996;     !- Visible Absorptance\n' +\
            '\n'
            ###
            

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
    

class EPSurfaceLib(object):
    
    def __init__(self):
        # 4 represents an Air Wall
        self.srfType = {0:'WALL',
               1:'ROOF',
               2:'FLOOR',
               3:'CEILING',
               4:'WALL',
               5:'WINDOW'}
        
        # surface construction should change later
        # to be based on the zone program
        self.srfCnstr = {0:'000_Exterior_Wall',
                1:'000_Exterior_Roof',
                2:'000_Exterior_Floor',
                3:'000_Interior_Floor',
                4:'Air_Wall',
                5:'000_Exterior_Window'}
         
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
    
    def __init__(self, zoneBrep, zoneID, zoneName, zoneProgram, isConditioned = True):
        self.north = 0
        self.objectType = "HBZone"
        self.origin = rc.Geometry.Point3d.Origin
        self.geometry = zoneBrep
        self.surfaces = []
        if zoneBrep != None:
            self.isClosed = self.geometry.IsSolid
        else:
            self.isClosed = False
        if self.isClosed:
            try:
                self.checkZoneNormalsDir()
            except Exception, e:
                print '0_Check Zone Normals Direction Failed:\n' + `e`
        self.num = zoneID
        self.name = zoneName
        self.hasNonPlanarSrf = False
        self.hasInternalEdge = False
        self.program = zoneProgram

        self.isConditioned = isConditioned
        self.isThisTheTopZone = False
        self.isThisTheFirstZone = False
        
    def checkZoneNormalsDir(self):
        """check normal direction of the surfaces"""
        MP3D = rc.Geometry.AreaMassProperties.Compute(self.geometry)
        self.cenPt = MP3D.Centroid
        MP3D.Dispose()
        # first surface of the geometry
        testSurface = self.geometry.Faces[0].DuplicateFace(False)
        srfCenPt, normal = self.getSrfCenPtandNormal(testSurface)
        
        try:
            # make a vector from the center point of the zone to center point of the surface
            testVector = rc.Geometry.Vector3d(srfCenPt - self.cenPt)
            # check the direction of the vectors and flip zone surfaces if needed
            if rc.Geometry.Vector3d.VectorAngle(testVector, normal)> 1: self.geometry.Flip()
        except Exception, e:
            print 'Zone normal check failed!\n' + `e`
            return 
        
    def decomposeZone(self, maximumRoofAngle = 30):
        # this method is useufl when the zone is going to be constructed from a closed brep
        # materials will be applied based on the zones construction set

        # explode zone
        for i in range(self.geometry.Faces.Count):
            
            surface = self.geometry.Faces[i].DuplicateFace(False)
            # find the normal
            findNormal = self.getSrfCenPtandNormal(surface)
            if findNormal:
                normal = findNormal[1]
                angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            else:
                #print findNormal
                #print self.geometry
                angle2Z = 0
            
            if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
                if self.isThisTheTopZone: surafceType = 1 #roof
                else:  surafceType = 3 # ceiling
            
            elif  160 < angle2Z <200:
                surafceType = 2 # floor
            
            else: surafceType = 0 #wall
            self.addSrf(hb_EPZoneSurface(surface, i, self.name + '_' + `i`, self, surafceType))
    
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
            
            # check for child surfaces
            if srf.hasChild: srf.calculatePunchedSurface()
        try:
            self.geometry = rc.Geometry.Brep.JoinBreps(srfs, sc.doc.ModelAbsoluteTolerance)[0]
            self.isClosed = self.geometry.IsSolid
            if self.isClosed:
                try:
                    self.checkZoneNormalsDir()
                except Exception, e:
                    print '0_Check Zone Normals Direction Failed:\n' + `e`
        except Exception, e:
            print " Failed to create the geometry from the surface:\n" + `e`
        
    def getSrfCenPtandNormal(self, surface):
        
        surface = surface.Faces[0]
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = surface.PointAt(centerU, centerV)
        normalVector = surface.NormalAt(centerU, centerV)
        
        normalVector.Unitize()
        return centerPt, normalVector

    def addSrf(self, srf):
        self.surfaces.append(srf)
    
    def updateConstructionSet(newProgramCode, level = 1):
        """level defines the level of the construction set
        0: low performance; 1: normal; 2: high performance"""
        self.constructionSet = constructionSet[newProgramCode]
    
    def cleanMeshedFaces(self):
        for srf in self.surfaces: srf.disposeCurrentMeshes()
    
    def prepareNonPlanarZone(self, meshingLevel = 0, isEnergyPlus = False):
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
        if meshingLevel == 0: mp = rc.Geometry.MeshingParameters.Default; disFactor = 3
        if meshingLevel == 1: mp = rc.Geometry.MeshingParameters.Smooth; disFactor = 1
        if isEnergyPlus:
            mp.JaggedSeams = True
        
        meshedGeo = rc.Geometry.Mesh.CreateFromBrep(joinedBrep, mp)
        
        for mesh in meshedGeo:
            if isEnergyPlus:
                angleTol = sc.doc.ModelAngleToleranceRadians
                minDiagonalRatio = .875
                #print mesh.Faces.ConvertTrianglesToQuads(angleTol, minDiagonalRatio)
                mesh.Faces.ConvertTrianglesToQuads(angleTol, minDiagonalRatio)
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
            if HBSrf.type == 2:
                totalFloorArea += HBSrf.getTotalArea()
        return totalFloorArea
    
    def getZoneVolume(self):
        return self.geometry.GetVolume()
    
    def getFloorZLevel(self):
        # useful for gbXML export
        minZ = float("inf")
        for HBSrf in self.surfaces:
            if HBSrf.type == 2:
                #get the center point
                centerPt, normalVector = HBSrf.getSrfCenPtandNormalAlternate()
                
                if centerPt.Z < minZ: minZ = centerPt.Z
        return minZ
    
    
    def __str__(self):
        try:
            return 'Zone name: ' + self.name + \
               '\nZone program: ' + self.program + \
               '\n# of surfaces: ' + `len(self.surfaces)` + \
               '\n-------------------------------------'
        except:
            return 'Zone name: ' + self.name + \
               '\nZone program: Unknown' + \
               '\n# of surfaces: ' + `len(self.surfaces)` + \
               '\n-------------------------------------'
            

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
        self.isPlanar = self.checkPlanarity()
        self.hasInternalEdge = self.checkForInternalEdge()
        
        if len(arg) == 0:
            # minimum surface
            # A minimum surface is a surface that will be added to a zone later
            # or is a surface that will only be used for daylighting simulation
            # so the concept of parent zone/surface is irrelevant
            self.parent = None
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
            
        self.meshedFace = rc.Geometry.Mesh()
        self.EPConstruction = None
        self.RadMaterial = None
        
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
           4:'WALL',
           5:'WINDOW',
           6:'SHADING',
           'WALL': 0,
           'ROOF':1,
           'FLOOR': 2,
           'CEILING': 3,
           'WINDOW':5,
           'SHADING': 6}
           
        self.cnstrSet = {0:'000 Exterior Wall',
                1:'000 Exterior Roof',
                2:'000 Interior Floor',
                3:'000 Interior Ceiling',
                4:'Air Wall',
                5:'000 Exterior Window',
                6:'000 Interior Wall'}
        
        # Floor and ceiling are set to Adiabatic for now
        self.srfBC = {0:'Outdoors',
         1:'Outdoors',
         2: 'surface',
         3: 'surface',
         4: 'surface',
         5: 'Outdoors',
         6: 'surface'}
         
        self.srfSunExposure = {0:'SunExposed',
             1:'SunExposed',
             2:'NoSun',
             3:'NoSun',
             4:'NoSun'}
             
        self.srfWindExposure = {0:'WindExposed',
              1:'WindExposed',
              2:'NoWind',
              3:'NoWind',
              4:'NoWind'}
        
        # should be fixed later
        #self.construction = setSrfCnstr(self.type, parentZone.constructionSet)
        if len(arg) == 2: self.construction = self.cnstrSet[self.type]
        self.numOfVertices = 'autocalculate'
    
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
                if triangulate:
                    coordinatesList.append(meshVertices[:3])
                    coordinatesList.append([meshVertices[0], meshVertices[2], meshVertices[3]])
                else:
                    coordinatesList.append(list(meshVertices))
            else:
                meshVertices = mesh.Faces.GetFaceVertices(face)[1:4]
                coordinatesList.append(list(meshVertices))
        #print len(coordinatesList)
        #coordinatesList.reverse()
        return coordinatesList
    
    def extractPoints(self, method = 1, triangulate = False):
        
        if not self.meshedFace.IsValid:
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
        
        # sort based on parameter on curve
        pointsSorted = sorted(pts, key =lambda pt: joinedBorder[0].ClosestPoint(pt)[1])
        
        def isClockWise(pts, basePlane):
            vector0 = rc.Geometry.Vector3d(pts[0]- basePlane.Origin)
            vector1 = rc.Geometry.Vector3d(pts[1]- basePlane.Origin)
            vector2 =  rc.Geometry.Vector3d(pts[-1]- basePlane.Origin)
            if rc.Geometry.Vector3d.VectorAngle(vector0, vector1, basePlane) < rc.Geometry.Vector3d.VectorAngle(vector0, vector2, basePlane):
                return True
            return False
            
        # check if clockWise and reverse the list in case it is
        if not isClockWise(pointsSorted, basePlane): pointsSorted.reverse()
        

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


    def extractGlzPoints(self, RAD = False, method = 2):
        glzCoordinatesList = []
        for glzSrf in self.childSrfs:
            sortedPoints = glzSrf.extractPoints()
            # check numOfPoints
            if len(sortedPoints) < 4 or (self.isPlanar and RAD==True):
                glzCoordinatesList.append(sortedPoints) #triangle
            elif len(sortedPoints) == 4 and self.isPlanar and abs(sortedPoints[0].DistanceTo(sortedPoints[2]) - sortedPoints[1].DistanceTo(sortedPoints[3]))< sc.doc.ModelAbsoluteTolerance:
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
                    glzCoordinatesList = self.extractMeshPts(mesh)
                    
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
        surface = self.geometry.Faces[0]
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = surface.PointAt(centerU, centerV)
        normalVector = surface.NormalAt(centerU, centerV)
        
        normalVector.Unitize()
        
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
        This method extract the type of the surface.
        I'm adding this method for gbXML export for now, however this will be 
        eventually what I will use for other components in HB
        """
        
        if not overwrite and hasinstance(self, "type"): return self.type
        
        # get the surface type based on normal
        #self.type = self.getTypeByNormalAngle()
        
        if self.type == 0:
            if self.isUnderground(True): self.type += 0.5 #UndergroundWall
        
        elif self.type == 1:
            # A roof underground will be assigned as UndergroundCeiling!
            if self.isUnderground(): self.type += 0.5 #UndergroundCeiling
            elif self.BC.upper() == "SURFACE": self.type == 3 # ceiling
            
        elif self.type == 2:
            # floor
            if self.isOnGrade(): self.type += 0.5 #SlabOnGrade
            elif self.isUnderground(): self.type += 0.25 #UndergroundSlab
            elif self.BC.upper() != "SURFACE":
                self.type += 0.75 #UndergroundSlab
        pass
        
    
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
            # set the boundary condition
            # it only works for simple geometries for now and should be replaced
            # by a smarter intersection process. I tried multiple ways and none of
            # them were promising...
            self.BC = self.srfBC[self.type]
            self.BCObject = ''
            if self.type ==2 and parentZone.isThisTheFirstZone:
                self.BC = 'GROUND'
                self.BCObject = ''
        else:
            hb_EPSurface.__init__(self, surface, srfNumber, srfName)
            
        
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
        if self.geometry.GetArea() <= chidSrfCandidate.GetArea():
            print "The area of the child surface cannot be larger than the area of the parent surface!"
            return False
        
        # all points are located on the surface and the area is less so it is all good!
        return True
    
    def addChildSrf(self, childSurface, percentage = 40):
        # I should copy/paste the function here so I can run it as
        # a method! For now I just collect them here together....
        # use the window function
        self.childSrfs.append(childSurface)
        self.hasChild = True
        pass
    
    def calculatePunchedSurface(self):
        glzCrvs = []
        for glzSrf in self.childSrfs:
            glzEdges = glzSrf.geometry.DuplicateEdgeCurves(True)
            jGlzCrv = rc.Geometry.Curve.JoinCurves(glzEdges)[0]
            glzCrvs.append(jGlzCrv)
        
        baseEdges = self.geometry.DuplicateEdgeCurves(True)
        
        jBaseCrv = rc.Geometry.Curve.JoinCurves(baseEdges)
        
        # convert array to list
        jBaseCrvList = []
        for crv in jBaseCrv: jBaseCrvList.append(crv)

        try:
            if self.isPlanar:
                # works for planar surfaces
                punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(glzCrvs + jBaseCrvList)
                if len(punchedGeometries) == 1: self.punchedGeometry = punchedGeometries[0]
                else:
                    # project the curves on top of base surface
                    srfNormal = self.getSrfCenPtandNormalAlternate()[1]
                    glzCrvsArray = rc.Geometry.Curve.ProjectToBrep(glzCrvs, [self.geometry], srfNormal, sc.doc.ModelAbsoluteTolerance)
                    glzCrvs = []
                    for crv in glzCrvsArray: glzCrvs.append(crv)
                    
                    punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(glzCrvs + jBaseCrvList)
                
                if len(punchedGeometries)>1:
                    crvDif = rc.Geometry.Curve.CreateBooleanDifference(jBaseCrvList[0], glzCrvs)
                    punchedGeometries = rc.Geometry.Brep.CreatePlanarBreps(crvDif)
                
                self.punchedGeometry = punchedGeometries[0]
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
            print "Failed to calculate opaque part of the surface:\n" + `e`

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

class hb_EPShdSurface(hb_EPSurface):
    def __init__(self, surface, srfNumber, srfName):
        hb_EPSurface.__init__(self, surface, srfNumber, srfName, self)
        self.TransmittanceSCH = ''
        self.isChild = False
        self.hasChild = False
        self.construction = '000 Exterior Wall' # just added here to get the minimum surface to work
        self.EPConstruction = '000 Exterior Wall' # just added here to get the minimum surface to work
        self.childSrfs = [self] # so I can use the same function as glazing to extract the points
        self.type = 6
        pass
    
    def getSrfCenPtandNormal(self, surface):
        # I'm not sure if we need this method
        # I will remove this later
        surface = surface.Faces[0]
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = surface.PointAt(centerU, centerV)
        normalVector = surface.NormalAt(centerU, centerV)
        
        normalVector.Unitize()
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
        
        if not self.isPlanar:
            try:
                self.parent.parent.hasNonplanarSrf = True
            except:
                # surface is not part of a zone yet.
                pass
        
        # this is a class that I only wrote to assign a fake object for surfaces
        # with outdoor boundaryCondition
        class OutdoorBC(object):
            def __init__(self):
                self.name = ""
        
        # calculate punchedWall
        self.parent.punchedGeometry = punchedWall
        self.shadingControlName = ''
        self.frameName = ''
        self.Multiplier = 1
        self.BCObject = OutdoorBC()
        self.groundViewFactor = 'autocalculate'
        self.isChild = True # is it really useful?
        
        
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
                        HBObjects.append(copy.deepcopy(sc.sticky['HBHive'][key]))
                    except:
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
    
    def __init__(self, outputUnits = [2], dynamicSHDGroup_1 = None,  dynamicSHDGroup_2 = None, RhinoViewsName = [] , adaptiveZone = False, dgp_imageSize = 250):
        
        if len(outputUnits)!=0 and outputUnits[0]!=None: self.outputUnits = outputUnits
        else: self.outputUnits = [2]
        
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


def checkGHPythonVersion(target = "0.6.0.3"):
    
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

letItFly = True

def checkGHPythonVersion(target = "0.6.0.3"):
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

GHPythonTargetVersion = "0.6.0.3"

if not checkGHPythonVersion(GHPythonTargetVersion):
    msg =  "Honeybee failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    letItFly = False
    sc.sticky["honeybee_release"] = False

if letItFly:
    if not sc.sticky.has_key("honeybee_release") or True:
        w = gh.GH_RuntimeMessageLevel.Warning
        sc.sticky["honeybee_release"] = True
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
        
        if folders.DSPath.endswith("\\"): segmentNumber = -2
        else: segmentNumber = -1
        hb_DSCore = "\\".join(folders.DSPath.split("\\")[:segmentNumber])
        hb_DSLibPath = "\\".join(folders.DSPath.split("\\")[:segmentNumber]) + "\\lib"
        
        sc.sticky["honeybee_folders"]["DSPath"] = folders.DSPath
        sc.sticky["honeybee_folders"]["DSCorePath"] = hb_DSCore
        sc.sticky["honeybee_folders"]["DSLibPath"] = hb_DSLibPath
    
        if folders.EPPath == None:
            EPVersion = "V7-2-0"
            if os.path.isdir("C:\EnergyPlus" + EPVersion + "\\"):
                folders.EPPath = "C:\EnergyPlus" + EPVersion + "\\"
            else:
                msg= "Honeybee cannot find EnergyPlus" + EPVersion + " folder on your system.\n" + \
                     "Make sure you have EnergyPlus" + EPVersion + " installed on your system.\n" + \
                     "You won't be able to run energy simulations without EnergyPlus.\n" + \
                     "A good place to install EnergyPlus is c:\\EnergyPlus" + EPVersion
                # I remove the warning for now until EP plugins are available
                # It confuses the users
                #ghenv.Component.AddRuntimeMessage(w, msg)
                folders.EPPath = ""
                
        sc.sticky["honeybee_folders"]["EPPath"] = folders.EPPath
        
        sc.sticky["honeybee_RADMaterialAUX"] = RADMaterialAux

        # set up radiance materials
        sc.sticky["honeybee_RADMaterialAUX"](True)
        
        try: hb_GetEPConstructions()
        except: print "Failed to load EP constructions!"
        
        sc.sticky["honeybee_Hive"] = hb_Hive
        sc.sticky["honeybee_DefaultMaterialLib"] = materialLibrary
        sc.sticky["honeybee_DefaultScheduleLib"] = scheduleLibrary
        sc.sticky["honeybee_DefaultSurfaceLib"] = EPSurfaceLib
        sc.sticky["honeybee_EPZone"] = EPZone
        sc.sticky["honeybee_EPSurface"] = hb_EPSurface
        sc.sticky["honeybee_EPShdSurface"] = hb_EPShdSurface
        sc.sticky["honeybee_EPZoneSurface"] = hb_EPZoneSurface
        sc.sticky["honeybee_EPFenSurface"] = hb_EPFenSurface
        sc.sticky["honeybee_RADParameters"] = hb_RADParameters
        sc.sticky["honeybee_DSParameters"] = hb_DSParameters
        
        # done! sharing the happiness.
        print "Hooohooho...Flying!!\nVviiiiiiizzz..."
