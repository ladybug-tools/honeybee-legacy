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
Call from EP Library

-
Provided by Honeybee 0.0.59
    
    Args:
        keywords_: List of keywords to filter the list of materials
            
    Returns:
        ThermMaterials: List of THERM materials in Honeybee library.  Note that Therm materials do not contain enough information to be used for EnergyPlus.  They can only be used for THERM polygons with the "Honeybee_Create Therm Polygons" component.
        EPMaterials: List of EP materials in Honeybee library
        EPWindowMaterials: List of EP window materials in Honeybee library
        EPConstructios:  List of EP constructions in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Call from EP Construction Library"
ghenv.Component.NickName = 'callFromEPConstrLibrary'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

if sc.sticky.has_key("honeybee_release") and sc.sticky.has_key("honeybee_constructionLib"):
    
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    EPConstructions = sc.sticky ["honeybee_constructionLib"].keys()
    EPMaterials =  sc.sticky ["honeybee_materialLib"].keys()
    EPWindowMaterials = sc.sticky ["honeybee_windowMaterialLib"].keys()
    ThermMaterials = sc.sticky["honeybee_thermMaterialLib"].keys()
    
    EPConstructions.sort()
    EPMaterials.sort()
    EPWindowMaterials.sort()
    ThermMaterials.sort()
    
    if len(keywords_)!=0 and keywords_[0]!=None:
        EPConstructions = hb_EPMaterialAUX.searchListByKeyword(EPConstructions, keywords_)
        EPMaterials = hb_EPMaterialAUX.searchListByKeyword(EPMaterials, keywords_)
        EPWindowMaterials = hb_EPMaterialAUX.searchListByKeyword(EPWindowMaterials, keywords_)
        ThermMaterials = hb_EPMaterialAUX.searchListByKeyword(ThermMaterials, keywords_)
else:
    print "You should first let the Honeybee fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")