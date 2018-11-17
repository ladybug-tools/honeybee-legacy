#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component parses an .eio file from an energy simulation and brings in the sizes of all of the HVAC equipment.
-
Provided by Honeybee 0.0.64
    
    Args:
        _eioFile: The file address of the eio file that comes out of the "Honeybee_Lookup EnergyPlus Folder" component.
        keywords_: Optional keywords that will be used to search through the outputs.
    Returns:
        zonePeakLoadObjs: Text describing the meaning of the zonePeakLoadVals below.
        zonePeakLoadVals: The sum of the zone's peak sensible loads on the design days.  These are eventually used to size the HVAC equipment that delivers heating/cooling to the zones.
        zoneSizingObjs: Text describing the meaning of the zoneSizingValues below.
        zoneSizingValues: The zone's peak sensible loads multiplied by their respective design "safety" factors (set on the "Energy Simulation Par" component). These safety factors are used to slightly oversize zone heating/cooling equipment and is standard ASHRAE practice.
        systemSizingObjs: Text describing the meaning of the systemSizingVals below.
        systemSizingVals: Values denoting the size of various central HVAC system elemts (like the primary air loop flow rates).
        componentSizObjs: Text describing the meaning of the componentSizVals below.
        componentSizVals: Values denoting the size of various zone HVAC components (like zone terminal sizes, heating/cooling coil sizes, lengths of chilled beams, etc.).
        coolDesignDayLoad: The sum of the load that must be reomved from the space at every timestep of the cooling design day.
        heatDesignDayLoad: The sum of the load that must be added to the space at every timestep of the heating design day.
"""

ghenv.Component.Name = "Honeybee_Read HVAC Sizing"
ghenv.Component.NickName = 'readEio'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nMAY_02_2015
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "4"

from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Grasshopper.Kernel as gh
import scriptcontext as sc
import os


def checkInputs():
    #Check to be sure that the file exists
    initCheck = False
    if _eioFile and _eioFile != None:
        initCheck = True
        if not os.path.isfile(_eioFile):
            initCheck = False
            warning = 'The .eio file does not exist.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    return initCheck

def createHeader(loadType, zoneName):
    header = ["key:location/dataType/units/frequency/startsAt/endsAt"]
    header.append('Some Location')
    header.append(loadType + " for " + zoneName)
    header.append('W')
    header.append('TimeStep')
    header.append('NoDate')
    header.append('NoDate')
    return header

def dict2Tree(dict):
    textInfo = DataTree[Object]()
    numInfo = DataTree[Object]()
    for zCount, zone in enumerate(dict.keys()):
        for text in dict[zone][0]:
            textInfo.Add(text, GH_Path(zCount))
        for num in dict[zone][1]:
            numInfo.Add(float(num), GH_Path(zCount))
    return textInfo, numInfo

def main(keywords):
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    try:
        # Pull out the relevant information.
        zoneSizing = []
        systemSizing = []
        componentSizing = []
        result = open(_eioFile, 'r')
        for line in result:
            if line.startswith(' Zone Sizing Information'):
                zoneSizing.append(line)
            if line.startswith(' System Sizing Information'):
                systemSizing.append(line)
            if line.startswith(' Component Sizing Information'):
                componentSizing.append(line)
        
        #Filter results for keywords
        if len(keywords) > 0:
            zoneSizing = hb_EPMaterialAUX.searchListByKeyword(zoneSizing, keywords_)
            systemSizing = hb_EPMaterialAUX.searchListByKeyword(systemSizing, keywords_)
            componentSizing = hb_EPMaterialAUX.searchListByKeyword(componentSizing, keywords_)
        
        # Split the results and the values.
        peakDict = {}
        zoneDict = {}
        for zSiz in zoneSizing:
            sizInfoSplit = zSiz.split(', ')
            zName = sizInfoSplit[1]
            zText = zName + '-' + sizInfoSplit[2] + '[W]'
            znum = sizInfoSplit[4]
            zpeak = sizInfoSplit[3]
            if zName not in zoneDict.keys():
                zoneDict[zName] = [[zText],[znum]]
                peakDict[zName] = [[zText],[zpeak]]
            else:
                zoneDict[zName][0].append(zText)
                zoneDict[zName][1].append(znum)
                peakDict[zName][0].append(zText)
                peakDict[zName][1].append(zpeak)
        
        # Make a list of system sizing objects.
        sysDict = {}
        for sysSiz in systemSizing:
            sizInfoSplit = sysSiz.split(', ')
            sysName = sizInfoSplit[1]
            zText = sysName + '-' + sizInfoSplit[2]
            try:
                openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
                if int(openStudioLibFolder.split('/')[1].split('.')[-2]) > 2:
                    sysNum = sizInfoSplit[4]
                else:
                    sysNum = sizInfoSplit[3]
            except:
                sysNum = sizInfoSplit[3]
            
            if sysName not in sysDict.keys():
                sysDict[sysName] = [[zText],[sysNum]]
            else:
                sysDict[sysName][0].append(zText)
                sysDict[sysName][1].append(sysNum)
        
        # Make a list of HVAC components.
        compDict = {}
        for compSiz in componentSizing:
            sizInfoSplit = compSiz.split(', ')
            compName = sizInfoSplit[2]
            zText = compName + '-' + sizInfoSplit[3]
            compNum = sizInfoSplit[4]
            if compName not in compDict.keys():
                compDict[compName] = [[zText],[compNum]]
            else:
                compDict[compName][0].append(zText)
                compDict[compName][1].append(compNum)
        
        # Try to parse the Zsz.csv file to bring in all of the timestep load data.
        coolDesLoad = []
        heatDesLoad = []
        loadTrigger = True
        try:
            sizingLogFile = _eioFile.replace('.eio', 'Zsz.csv')
            coolCols = []
            heatCols = []
            zoneNames = []
            with open(sizingLogFile,'r') as sizingFile:
                for lCount, line in enumerate(sizingFile):
                    columns = line.split(',')
                    if lCount == 0:
                        for colCount, col in enumerate(columns):
                            if 'Des Heat Load' in col:
                                heatCols.append(colCount)
                                zoneName = col.split(':')[0]
                                zoneNames.append(zoneName)
                            elif 'Des Sens Cool Load' in col:
                                coolCols.append(colCount)
                        coolDesLoad.append(createHeader('Design Day Cooling Load', zoneName))
                        heatDesLoad.append(createHeader('Design Day Heating Load', zoneName))
                    elif 'Peak' in line:
                        loadTrigger = False
                    elif loadTrigger == True:
                        for cCount, coolCount in enumerate(coolCols):
                            coolDesLoad[cCount].append(float(columns[coolCount]))
                        for hCount, heatCount in enumerate(heatCols):
                            heatDesLoad[hCount].append(float(columns[heatCount]))
        except:
            pass
        
        # Convert the list of lists into a data tree.
        coolDesignLoad = DataTree[Object]()
        heatDesignLoad = DataTree[Object]()
        for datCount, dataList in enumerate(coolDesLoad):
            for item in dataList:
                coolDesignLoad.Add(item, GH_Path(datCount))
        for datCount, dataList in enumerate(heatDesLoad):
            for item in dataList:
                heatDesignLoad.Add(item, GH_Path(datCount))
        
        return peakDict, zoneDict, sysDict, compDict, coolDesignLoad, heatDesignLoad
    except:
        warning = 'Fauled to parse .eio file.  Make sure that it is the correct type of file.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1


#Honeybee check.
hbCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    hbCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): hbCheck = False
    except:
        hbCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


if _eioFile and hbCheck == True:
    initCheck = checkInputs()
    if initCheck == True:
        result = main(keywords_)
        if result != -1:
            peakDict, zoneDict, sysDict, compDict, coolDesignDayLoad, heatDesignDayLoad = result
            zonePeakLoadObjs, zonePeakLoadVals = dict2Tree(peakDict)
            zoneSizingObjs, zoneSizingValues = dict2Tree(zoneDict)
            systemSizingObjs, systemSizingVals = dict2Tree(sysDict)
            componentSizObjs, componentSizVals = dict2Tree(compDict)


