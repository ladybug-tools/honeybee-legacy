#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to write your THERM polygons and boundary conditions into a therm XML that can be opened ready-to-run in THERM.
-
Provided by Honeybee 0.0.57

    Args:
        _polygons: A list of thermPolygons from one or more "Honeybee_Create Therm Polygons" components.
        _boundaries: A list of thermBoundaries from one or more "Honeybee_Create Therm Boundaries" components.
        workingDir_: An optional working directory to a folder on your system, into which you would like to write the THERM XML and results.  The default will write these files in into your Ladybug default folder.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        fileName_: An optional text string which will be used to name your THERM XML.  Change this to aviod over-writing results of previous runs of this component.
        _writeXML: Set to "True" to have the component take your connected UWGParemeters and write them into an XML file.  The file path of the resulting XML file will appear in the xmlFileAddress output of this component.  Note that only setting this to "True" and not setting the output below to "True" will not automatically run the XML through the Urban Weather Generator for you.
    Returns:
        readMe!:...
        xmlFileAddress: The file path of the therm XML file that has been generated on your machine.  Open this file in THERM to see your exported therm model.
        resultFileAddress: The location where the THERM results will be written once you open the XML file above in THERM and hit "simulate."
"""

import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid
import math

ghenv.Component.Name = 'Honeybee_Write THERM File'
ghenv.Component.NickName = 'writeTHERM'
ghenv.Component.Message = 'VER 0.0.57\nNOV_24_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nNOV_16_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning



def checkTheInputs():
    #Make sure that the connected objects are of the right type.
    
    
    #Make sure that all of the geometry is in the same plane.
    
    
    #Make sure that the Therm polygons form a single polysurface without any holes (only one set of naked edges).
    
    
    
    
    
    return False


def main():
    #From the plane that the surfaces are in in Rhino, translate them to the origin of a the Therm scene.
    #Keep track of this transformation and write it into the XML so that results can be read back onto the original geometry after running THERM.
    
    
    #Make sure that the vertices of the boundaries can be assigned to a polygon.
    
    
    
    
    return -1




#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


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
        ghenv.Component.AddRuntimeMessage(w, warning)


#If the intital check is good, run the component.
if initCheck:
    checkData = checkTheInputs()
    if checkData:
        result = main()
        if result != -1:
            output = result


