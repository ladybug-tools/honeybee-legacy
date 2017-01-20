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
    Create an HBZone from HB Surfaces
    
-
Provided by Honeybee 0.0.60

    Args:
        _name_: The name of the zone as a string
        zoneProgram_: Optional input for the program of this zone
        isConditioned_: True/False value. This value will be applied to the ouput zone to either condition them with an Ideal Air Loads System (True) or not condition them at all (False). If no value is connected here, all zones will be conditioned with an Ideal Air Loads System by default.
        _HBSurfaces: A list of Honeybee Surfaces
    Returns:
        readMe!:...
        HBZone: Honeybee zone as the result
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid
import math

ghenv.Component.Name = 'Honeybee_createHBZones'
ghenv.Component.NickName = 'createHBZones'
ghenv.Component.Message = 'VER 0.0.60\nJAN_20_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def main(zoneName,  HBZoneProgram, HBSurfaces,standard,climateZone, isConditioned):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return
            
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPSurface"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    
    # call the surface from the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    HBSurfaces = hb_hive.callFromHoneybeeHive(HBSurfaces)
    
    # bldg program
    try: bldgProgram, zoneProgram = HBZoneProgram.split("::")
    except: bldgProgram, zoneProgram = 'Office', 'OpenOffice'
    
    # initiate the zone
    zoneID = str(uuid.uuid4())
    
    # default for isConditioned is True
    if isConditioned== None: isConditioned = True
    
    HBZone = hb_EPZone(None, zoneID, zoneName.strip().replace(" ","_"), (bldgProgram, zoneProgram), isConditioned)
    
    for hbSrf in HBSurfaces:
        HBZone.addSrf(hbSrf)
        if hbSrf.shdCntrlZoneInstructs != []:
            HBZone.daylightCntrlFract = 1
            HBZone.illumSetPt = hbSrf.shdCntrlZoneInstructs[0]
            HBZone.GlareDiscomIndex = hbSrf.shdCntrlZoneInstructs[1]
            HBZone.glareView = hbSrf.shdCntrlZoneInstructs[2]
    
    # create the zone from the surfaces
    HBZone.createZoneFromSurfaces()
    
    if not HBZone.isClosed:
        message = "All of your HBSrfs must make a closed volume."
        print message
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, message)
        
    def convertStandardIntToString(standard):
        
        if standard == 0:
            
            return '189.1-2009'
            
        if standard == 1:
            
            return '90.1-2007'
           
        if standard == 2:
            
            return '90.1-2010'
            
        if standard == 3:
            
            return 'DOE Ref 1980-2004'
            
        if standard == 4:
            
            return 'DOE Ref 2004'
            
        if standard == 5:
            
            return 'DOE Ref Pre-1980'
        
        
    def convertClimateTypetoString(climateZone):
        
        if climateZone == 0:
            
            return 'ClimateZone 1'
            
        if climateZone == 1:
            
            return 'ClimateZone 2'
           
        if climateZone == 2:
            
            return 'ClimateZone 3'
            
        if climateZone == 3:
            
            return 'ClimateZone 4'
            
        if climateZone == 4:
            
            return 'ClimateZone 5'
            
        if climateZone == 5:
            
            return 'ClimateZone 6'
            
        if climateZone == 6:
            
            return 'ClimateZone 7'
            
        if climateZone == 7:
            
            return 'ClimateZone 8'
        
    # Assign the constructions for walls, roof, slab floor etc from the OpenStudio standards
        
    if (standard != None) and (climateZone != None):
        
        # Get the construction set from the OpenStudio standards Json
        
        standard = convertStandardIntToString(standard)
        
        climateZone = convertClimateTypetoString(climateZone)
        
        print standard,climateZone,HBZone.bldgProgram
        
        constructionSetDict = HBZone.getConstructionsByStandardClimateZone(standard,climateZone).items()[0][1]
        
        # Assign it to the zone
        
        thisZone.assignConstructionSets(thisZone,constructionSetDict)
        
    HBZone = hb_hive.addToHoneybeeHive([HBZone], ghenv.Component)
    
    return HBZone 


def checkInputs(standard,climateZone):
    
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if (standard == None) and (climateZone != None):
        
        warning = "If you want to assign a default construction set \n" + \
        "you must specify BOTH the climate zone and the standard e.g ASHRAE 90.1 2007"
        "you are seeing this message because you've only assigned one"
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
        return -1
        
    if (standard != None) and (climateZone == None):
        
        warning = "If you want to assign a default construction set \n" + \
        "you must specify BOTH the climate zone and the standard e.g ASHRAE 90.1 2007 \n" + \
        "you are seeing this message because you've only assigned one"
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
        return -1
        
    # Need check if input in OpenStudio standard etc
        
        
    else:
        
        return

if _name != None and _HBSurfaces and _HBSurfaces[0]!=None:
    
    if checkInputs(standard_,climateZone_) != -1:
    
        result= main(_name, zoneProgram_, _HBSurfaces,standard_,climateZone_, isConditioned_)
        
        HBZone = result