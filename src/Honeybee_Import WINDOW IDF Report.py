#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com.com>  
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
Use this component to import an EnergyPlus window construction from LBNL WINDOW.  This construction can then be assigned to any Honebee window for an EnergyPlus model.

-
Provided by Honeybee 0.0.60
    
    Args:
        _windowIDFReport: A filepath to a 'EnergyPlus IDF' report exported by LBNL WINDOW.
    Returns:
        EPConstruction: An EnergyPlus construction that can be assigned to any window in Honeybee using components like 'Honeybee_addHBGlz', 'Honeybee_Glazing based on ratio', or 'Honeybee_Set EP Zone Construction'.

"""

ghenv.Component.Name = 'Honeybee_Import WINDOW IDF Report'
ghenv.Component.NickName = 'importWINDOWidf'
ghenv.Component.Message = 'VER 0.0.60\nOCT_08_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nSEP_09_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os


def main(windowIDFReport):
    #Check to be sure that the IDF file exists before trying to open it.
    #Check if the result file exists.
    if _windowIDFReport.lower().endswith('.idf'): windowIDFReport = _windowIDFReport
    else: windowIDFReport = _windowIDFReport + '.idf'
    if not os.path.isfile(windowIDFReport):
        warning = "Cannot find the _windowIDFReport text file. Check the location of the file on your machine."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    # import the classes
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    
    #Open the IDF and extract all of the information
    EPObjs = []
    materialTrigger = False
    materialStr = ''
    
    spectralPropTrigger = False
    spectralPropStr = ''
    
    framePropsTrigger = False
    frameProps = ''
    
    constrName = None
    spectPropsName = None
    framePropsName = None
    
    textFile = open(windowIDFReport, 'r')
    for lineCount, line in enumerate(textFile):
        if 'WindowMaterial:Glazing' in line or 'WindowMaterial:Gas' in line or 'CONSTRUCTION,' in line:
            materialTrigger = True
            if 'CONSTRUCTION,' in line: materialStr = materialStr + 'Construction,\n'
            else: materialStr = materialStr + line
        elif line == '\n':
            materialTrigger = False
            if materialStr != '': EPObjs.append(materialStr)
            materialStr = ''
            spectralPropTrigger = False
            if spectralPropStr != '': EPObjs.append(spectralPropStr)
            spectralPropStr = ''
            framePropsTrigger = False
            if frameProps != '': EPObjs.append(frameProps)
            frameProps = ''
        elif '!- Glazing System name' in line:
            constrName = line.split(',')[0].upper()
            materialStr = materialStr + line
        elif materialTrigger == True:
            materialStr = materialStr + line
        elif 'MaterialProperty:GlazingSpectralData' in line:
            spectralPropTrigger = True
            spectralPropStr = spectralPropStr + line
        elif spectralPropTrigger == True:
            spectralPropStr = spectralPropStr + line
        elif 'WindowProperty:FrameAndDivider' in line:
            framePropsTrigger = True
            frameProps = frameProps + line
        elif '!- User Supplied Frame/Divider Name' in line:
            # Overwrite the frame name to be associated with the WINDOW construction.
            framePropsName = constrName
            frameProps = frameProps + constrName + ',!- User Supplied Frame/Divider Name\n'
        elif framePropsTrigger == True:
            frameProps = frameProps + line
    textFile.close()
    
    #Add the materials and construction to the HBHive.
    for EPObject in EPObjs:
        added, name = hb_EPObjectsAux.addEPObjectToLib(EPObject, True)
        if not added:
            msg = name + " is not added to the project library!"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        else: print name + " is has been added to the project library!"
    
    # In case no frames were found, make sure any frames bearing the name of the construction are removed.
    if framePropsName == None:
        try:
            del sc.sticky["honeybee_WindowPropLib"][constrName]
        except:
            pass
    
    return constrName



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
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


#If the intital check is good, run the component.
if initCheck and _windowIDFReport:
    result = main(_windowIDFReport)
    if result != -1:
        EPConstruction = result