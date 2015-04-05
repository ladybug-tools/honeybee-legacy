# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
    Create an HBZone from HB Surfaces
    
-
Provided by Honeybee 0.0.56

    Args:
        _name_: The name of the zone as a string
        zoneProgram_: Optional input for the program of this zone
        isConditioned_: Set to true if the zone is conditioned
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
ghenv.Component.Message = 'VER 0.0.56\nAPR_04_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def main(zoneName,  HBZoneProgram, HBSurfaces, isConditioned):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
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
    
    HBZone = hb_EPZone(None, zoneID, zoneName.strip(), (bldgProgram, zoneProgram), isConditioned)
    
    for hbSrf in HBSurfaces:
        HBZone.addSrf(hbSrf)
    
    # create the zone from the surfaces
    HBZone.createZoneFromSurfaces()
    
    HBZone  = hb_hive.addToHoneybeeHive([HBZone], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZone 

if _name != None and _HBSurfaces and _HBSurfaces[0]!=None:
    
    result= main(_name, zoneProgram_, _HBSurfaces, isConditioned_)
    
    HBZone = result
