#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com>, Chris Mackey <Chris@MackeyArchitecture.com>, and Chien Si Harriman <charriman@terabuild.com>
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
Use this component to export OpenStudio model to gbXML file.
-
Provided by Honeybee 0.0.60
    
    Args:
        _model: An OpenStudio model.
        _filepath: Full filepath to xml file.
        _export: Set to True to export the model.
    Returns:
        readMe!:
        success: True on success.
"""

ghenv.Component.Name = "Honeybee_OpenStudio to gbXML"
ghenv.Component.NickName = 'OpenStudioToXML'
ghenv.Component.Message = 'VER 0.0.60\nOCT_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nSEP_09_2016
#compatibleLBVersion = VER 0.0.59\nJUL_24_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import scriptcontext as sc

if sc.sticky.has_key('honeybee_release'):
    if sc.sticky["honeybee_folders"]["OSLibPath"] != None:
        # openstudio is there
        openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
        
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
        
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg1 = "You do not have OpenStudio installed on Your System.\n" + \
            "You wont be able to use this component until you install it.\n" + \
            "Download the latest OpenStudio for Windows from:\n"
        msg2 = "https://www.openstudio.net/downloads"
        print msg1
        print msg2
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False

if openStudioIsReady and _export and _filepath and _model:
    
    _filepath = _filepath.replace('\\\\', '/').replace('\\', '/')
    translator = ops.GbXMLForwardTranslator()
    _model.getFacility()
    result = translator.modelToGbXML(_model, ops.Path(os.path.normpath(_filepath)))
    errors = translator.errors()
    warnings = translator.warnings()
    if ''.join(errors):
        raise Exception('\n'.join(errors))
    for warn in warnings:
        print warn
    print 'File exported to: {}'.format(os.path.normpath(_filepath))
    success = True