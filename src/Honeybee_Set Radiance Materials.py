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
Radiance Default Materials
-
Provided by Honeybee 0.0.60

    Args:
        HBObject_: List of Honeybee zones or surfaces
        wallRADMaterial_: Optional wall material to overwrite the default walls
        windowRADMaterial_: Optional material for windows
        ceilingRADMaterial_: Optional material for ceilings
        roofRADMaterial_: Optional material for roofs
        floorRADMaterial_: Optional material for floors
        skylightRADMaterial_: Optional material for skylights
    Returns:
        modifiedHBObject: Honeybee object with updated materials

"""

ghenv.Component.Name = "Honeybee_Set Radiance Materials"
ghenv.Component.NickName = 'setRADMaterials'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBObject, wallRADMaterial, windowRADMaterial, \
        ceilingRADMaterial, roofRADMaterial, floorRADMaterial, \
        skylightRADMaterial):
    
    # Make sure Honeybee is flying
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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        HBObject = hb_hive.callFromHoneybeeHive([HBObject])[0]
        # check if the object is a zone or a surface
        if HBObject.objectType == "HBSurface":
            HBObjects = [HBObject]
        elif HBObject.objectType == "HBZone":
            HBObjects = HBObject.surfaces
            
    except Exception, e:
        HBObjects = None
    
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
    
    if HBObjects != None:
        for srf in HBObjects:
            if windowRADMaterial!=None and int(srf.type) != 1 and srf.hasChild:
                for childSrf in srf.childSrfs:
                    hb_RADMaterialAUX.assignRADMaterial(childSrf, windowRADMaterial, ghenv.Component)
            
            # check for slab on grade and roofs
            if skylightRADMaterial!=None and int(srf.type) == 1 and srf.hasChild:
                for childSrf in srf.childSrfs:
                    hb_RADMaterialAUX.assignRADMaterial(childSrf, skylightRADMaterial, ghenv.Component)
            
            if int(srf.type) == 0 and wallRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, wallRADMaterial, ghenv.Component)
            elif int(srf.type) == 1 and roofRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, roofRADMaterial, ghenv.Component)
            elif int(srf.type) == 2 and floorRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, floorRADMaterial, ghenv.Component)
            elif int(srf.type) == 3 and ceilingRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, ceilingRADMaterial, ghenv.Component)

        # add zones to dictionary
        HBObject  = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component)
        
        #print HBZones
        return HBObject
    
    else:
        return -1

if _HBObject:
    result = main(_HBObject, wallRADMaterial_, windowRADMaterial_, \
        ceilingRADMaterial_, roofRADMaterial_, floorRADMaterial_, \
        skylightRADMaterial_)
    if result!=-1:
        modifiedHBObject = result