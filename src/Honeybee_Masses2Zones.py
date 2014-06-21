# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert Mass to Honeybee Zones
-
Provided by Honeybee 0.0.53

    Args:
        _zoneMasses: List of closed Breps
        zoneNames_: List of names for zone names. Default names will be applied to zones if empty
        zonePrograms_: List of programs for zone programs. Office::OpenOffice will be applied to zones if empty
        isConditioned_: List of True/False. IdealLoadsAirSystem will be assigned to the zone if True.
        maximumRoofAngle_: Maximum angle from z vector that the surface will be assumed as a roof. Default is 30 degrees
        _createHBZones: Set Boolean to True to generate the zones
    Returns:
        readMe!: ...
        HBZones: Honeybee zones in case of success
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


ghenv.Component.Name = 'Honeybee_Masses2Zones'
ghenv.Component.NickName = 'Mass2Zone'
ghenv.Component.Message = 'VER 0.0.53\nJUN_21_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance
import math

################################################################################

def main(maximumRoofAngle, zoneMasses, zoneNames, zonePrograms, isConditioned):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    # import the classes
    # don't customize this part
    hb_EPZone = sc.sticky["honeybee_EPZone"]
    hb_EPSrf = sc.sticky["honeybee_EPSurface"]
    hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
    
    HBZones = []
    # create zones out of masses
    for zoneKey, zone in enumerate(zoneMasses):
        # zone name
        try: zoneName = zoneNames[zoneKey]
        except: zoneName = "zone_" + str(zoneKey)
        # str(uuid.uuid4())
        
        # zone programs
        try: thisZoneProgram = zonePrograms[zoneKey].split("::")
        except: thisZoneProgram = 'Office', 'OpenOffice'

        try: isZoneConditioned = isConditioned[zoneKey]
        except: isZoneConditioned = True
        
        thisZone = hb_EPZone(zone, zoneKey, zoneName, thisZoneProgram, isZoneConditioned)
        
        # assign surface types and construction based on type
        thisZone.decomposeZone(maximumRoofAngle)
        
        # append this zone to other zones
        HBZones.append(thisZone)
                
    return HBZones
        
        ################################################################################################


if _createHBZones == True:
    
    try:  maximumRoofAngle = float(maxRoofAngle_)
    except: maximumRoofAngle = 30
    
    result= main(maximumRoofAngle, _zoneMasses, zoneNames_, zonePrograms_,isConditioned_)
    
    if result!=-1:
        zoneClasses = result 
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBZones  = hb_hive.addToHoneybeeHive(zoneClasses, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
