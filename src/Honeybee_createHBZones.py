# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
    Create an HBZone from HB Surfaces
    
-
Provided by Honeybee 0.0.51

    Args:
        _name_: The name of the zone as a string
        _zoneType_: Optional input for the program of this zone
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
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import uuid
import math

ghenv.Component.Name = 'Honeybee_createHBZones'
ghenv.Component.NickName = 'createHBZones'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def main(zoneName, zoneProgram, HBSurfaces, isConditioned):
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_runStudy_RAD = sc.sticky["ladybug_Export2Radiance"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        # don't customize this part
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPZoneSurface = sc.sticky["honeybee_EPSurface"]
        
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()
    
    # call the surface from the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    HBSurfaces = hb_hive.callFromHoneybeeHive(HBSurfaces)
    
    # initiate the zone
    zoneID = str(uuid.uuid4())
    HBZone = hb_EPZone(None, zoneID, zoneName, zoneProgram, isConditioned)
    
    for hbSrf in HBSurfaces:
        HBZone.addSrf(hbSrf)
    
    # create the zone from the surfaces
    HBZone.createZoneFromSurfaces()
    
    HBZone  = hb_hive.addToHoneybeeHive([HBZone], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZone 

if _name_ != None and _HBSurfaces and _HBSurfaces[0]!=None:
    
    result= main(_name_, _zoneType_, _HBSurfaces, isConditioned_)
    
    HBZone = result
