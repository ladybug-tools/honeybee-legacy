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
This component reads the results of an Adaptive Indoor Comfort Analysis.  Note that this usually takes about a minute
-
Provided by Honeybee 0.0.64
    
    Args:
        _comfResultFileAddress: Any one of the result file addresses that comes out of the 'Honeybee_Microclimate Map Analysis' component or the 'Honeybee_Thermal Comfort Autonomy Analysis' component.
    Returns:
        comfResultsMtx: A matrix of comfort data that can be plugged into the "Visualize Comfort Results" component.
"""

ghenv.Component.Name = "Honeybee_Read Microclimate Matrix"
ghenv.Component.NickName = 'readMicroclimateMtx'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "6"


import Grasshopper.Kernel as gh


comfResultsMtx = []

if _comfResultFileAddress:
    try:
        result = open(_comfResultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0: comfResultsMtx.append(line.split('\n')[0])
            else:
                #Pull out the data.
                hourData = []
                for columnCount, column in enumerate(line.split(',')):
                    hourData.append(float(column))
                comfResultsMtx.append(hourData)
        result.close()
    except:
        try: result.close()
        except: pass
        warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
                  'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

