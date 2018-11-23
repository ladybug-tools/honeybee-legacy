#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mingbo Peng <mpen@mpenDesign.com>
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
Make Adiabatic

-
Provided by Honeybee 0.0.64

    Args:
        HBSrfs_: A list of valid Honeybee surfaces or zones
        byName_: A list of valid surface names
    Returns:
        HBSrfs: Modified list of Honeybee objects with 
"""

ghenv.Component.Name = "Honeybee_Make Adiabatic by Name"
ghenv.Component.NickName = 'makeAdiabaticByName'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def changeSrfType(HBSurface):
    if str(HBSurface.type).startswith('2'):
        HBSurface.setType(2, False)
    elif str(HBSurface.type).startswith('1'):
        HBSurface.setType(3, False)
    HBSurface.setEPConstruction(HBSurface.intCnstrSet[HBSurface.type])

def main(HBObjs,nameList):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjects = hb_hive.callFromHoneybeeHive(HBObjs)
    
    for HBO in HBObjects:
        if HBO.objectType == "HBZone":
            for HBS in HBO.surfaces:
                if HBS.name in nameList:
                    HBS.BC = "Adiabatic"
                    HBS.sunExposure = "NoSun"
                    HBS.windExposure = "NoWind"
                    HBS.srfBCByUser = True
                    changeSrfType(HBS)
        else:
            if HBO.name in nameList:
                HBS.BC = "Adiabatic"
                HBS.sunExposure = "NoSun"
                HBS.windExposure = "NoWind"
                HBS.srfBCByUser = True
                changeSrfType(HBS)
        
    
    HBObjects  = hb_hive.addToHoneybeeHive(HBObjects, ghenv.Component)
    
    return HBObjects
    
if HBObjs_ and HBObjs_[0]!=None and byName_ and byName_[0]!=None:
    
    HBObjs = main(HBObjs_,byName_)