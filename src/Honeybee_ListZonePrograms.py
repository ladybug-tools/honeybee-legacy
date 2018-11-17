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
Find list of spaces for each space based on program
-
Provided by Honeybee 0.0.64

    Args:
        _bldgProgram: An index number for 
    Returns:
        bldgProgram:
        zonePrograms: Honeybee zones in case of success
"""

ghenv.Component.Name = "Honeybee_ListZonePrograms"
ghenv.Component.NickName = 'ListZonePrograms'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

path = gh.Data.GH_Path(0)

ghenv.Component.Params.Output[0].Name = "zonePrograms"
ghenv.Component.Params.Output[0].NickName = "zonePrograms"

def main(bldgProgram):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    bldgProgramName = bldgProgramDict[bldgProgram%13]
    zonePrograms = zonesProgramDict[bldgProgramName].values()
    
    return bldgProgramName, zonePrograms


if _bldgProgram!=None:
    results = main(_bldgProgram)
    
    if results!=-1:
        bldgProgram, zonePrograms = results
        
        bldgAndZonP = range(len(zonePrograms))
        for pCount, zoneProgram in enumerate(zonePrograms):
            bldgAndZonP[pCount] = "::".join([bldgProgram , zoneProgram])
            
        ghenv.Component.Params.Output[0].Name = bldgProgram + "ZonePrograms"
        ghenv.Component.Params.Output[0].NickName = bldgProgram + "ZonePrograms"
        
        #for programCount, program in enumerate(zonePrograms):
        #    ghenv.Component.Params.Output[0].AddVolatileData(path, programCount + 1, program)
        
        # not the best solution but the normal solution was missing the first item for some reason
        line  = bldgProgram + "ZonePrograms = bldgAndZonP"
        exec(line)