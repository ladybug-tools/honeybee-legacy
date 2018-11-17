#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Honeybee.
#
# Copyright (c) 2015-2017, Sarith Subramaniam <sarith@sarith.in> and Chris Mackey <Chris@MackeyArchitecture.com> 
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
Ues this component to Open a file/directory in windows explorer.
This is particularly useful for understanding where the results of Energy/Daylight simulations are located on your system.

-
Args:
    _filePath: Either a File path or a Directory path that you want to open in Explorer.
        If a file-path is provided then the directory containing the file is opened.
        If a folder-path is provided then the folder containing that folder is opened.
"""

ghenv.Component.Name = "Honeybee_OpenFileDirectory"
ghenv.Component.NickName = 'fileExplorer'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import os
import subprocess

def main(location):
    if location:
        try:
            location = location.replace('"',"") #Just in case the user enters a hardcoded path.
            location = location.strip() #Remove all the whitespaces.
            assert os.path.exists(location) #Check if the path exists at all or else throw an assertion error.
            if os.path.isdir(location):
                foldername = location
            else:
                foldername = os.path.dirname(location)
            subprocess.Popen('explorer.exe ' + foldername)
            print "Success!"
        except AssertionError:
            raise Exception("The specified path %s does not exist.\nPlease check for white-spaces or other characters in your path name."%location)
        except:
            raise Exception("The input: %s is not a valid path.\nA valid path would be something like D:\Honeybee\Results."%location)
    else:
        raise Exception("Connect a file path to destination input!")

if _filePath:
    main(_filePath)
else:
    msg = "Input _filePath failed to collect data."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
