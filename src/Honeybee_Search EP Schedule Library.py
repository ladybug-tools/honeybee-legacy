#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Filter EP Schedule Library

-
Provided by Honeybee 0.0.64
    
    Args:
        keywords_: List of keywords to filter the list of materials
            
    Returns:
        EPMaterials: List of EP materials in Honeybee library
        EPWindowMaterils: List of EP window materials in Honeybee library
        EPConstructios:  List of EP constructions in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Search EP Schedule Library"
ghenv.Component.NickName = 'SearchEPSCHLibrary'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(scheduleList, HBZoneProgram, scheduleType):
    selSch =[]
    
    try: bldgProgram, zoneProgram = HBZoneProgram.split("::")
    except: bldgProgram, zoneProgram = None, None
        
    for schName in scheduleList:
       if schName.upper().find(bldgProgram.upper())!=-1 and schName.upper().find(scheduleType.upper())!=-1:
            selSch.append(schName)
    
    # check if any alternate
    exactFit = []
    if zoneProgram!="":
        for schName in selSch:
            if schName.upper().find(zoneProgram.upper())!= -1:
                exactFit.append(schName)
    else:
        exactFit = sorted(selSch, key = lambda schName: len(schName))[0]
    return exactFit, selSch

if _scheduleList:
    selSchedule, possibleAlt = main(_scheduleList, zoneProgram_, scheduleType_)
    
    selSchedules = [selSchedule] + possibleAlt