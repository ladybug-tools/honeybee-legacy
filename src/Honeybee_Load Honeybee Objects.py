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
Load Honeybee Objects

Use this component to load Honeybee objects from a file on your system.
The valid files are created by dump Honeybee objects component.
-
Provided by Honeybee 0.0.59

    Args:
        _HBObjects: A list of Honeybee objects
        _filePath: A valid path to a file on your drive (e.g. c:\ladybug\20ZonesExample.HB)
        _load: Set to True to load the objects from the file
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Honeybee_Load Honeybee Objects"
ghenv.Component.NickName = 'loadHBObjects'
ghenv.Component.Message = 'VER 0.0.59\nFEB_05_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.58\nNOV_13_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import cPickle as pickle
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

def main(filePath, load):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1        
    if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    
    if not load: return -1
    
    if not os.path.isfile(filePath):
        raise ValueError("Can't find %s"%filePath)
    
    with open(filePath, "rb") as inf:
        return pickle.load(inf)
    

results = main(_filePath, _load)

HBObjects = results if results!= -1 else None
