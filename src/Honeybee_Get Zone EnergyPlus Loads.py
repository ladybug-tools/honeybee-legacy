#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Look up loads for a Honeybee Zone
-
Provided by Honeybee 0.0.66

    Args:
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        equipmentLoadPerArea:The desired equipment load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 2 W/m2 (for just a laptop or two in the zone) to 15 W/m2 for an office filled with computers and appliances.
        infilRatePerArea_Facade:The desired rate of outside air infiltration into the zone per square meter of exterior facade.  Values here should be in m3/s-m2 @4Pa(Cubic meters per second per square meter of exterior facade).  ASHRAE recommends the following general infiltration rates based on the area of the facade exposed to the outdoors:
            ------------------------------------------------------------
            Unit of following reference numbers: 
            m3/s per m2 facade @4Pa
            ------------------------------------------------------------
            0.000071 - Passive house         (0.1 cfm/sf facade @75Pa)
            0.0001 - Tight building               (0.14 cfm/sf facade @75Pa)
            0.000285 - ASHRAE 90.1-2013 (0.4 cfm/sf facade @75Pa)
            0.0003 - Average building          (0.42 cfm/sf facade @75Pa)
            0.0006 - Leaky building             (0.84 cfm/sf facade @75Pa)
        lightingDensityPerArea:The desired lighting load per square meter of floor.  Values here should be in W/m2 (Watts per square meter).  Typical values can range from 3 W/m2 for efficeint LED bulbs to 15 W/m2 for incandescent heat lamps.
        numOfPeoplePerArea:The desired number of per square meter of floor at peak occupancy.  Values here should be in ppl/m2 (People per square meter).  Typical values can range from 0.02 ppl/m2 for a lightly-occupied household to 0.5 ppl/m2 for a tightly packed auditorium.
        ventilationPerArea:The desired minimum rate of outdoor air ventilation through the mechanical system into the zone in m3/s per m2 of floor.  Values here should be in m3/s-m2 (Cubic meters per second per square meter of floor).  Often, this total value over the zone should be much lower than the ventilation per person (below).  Typical values can range from 0.0002 m3/s-m2 for lightly-occupied houses to 0.0025 m3/s-m2 for spaces like laboratories and cleanrooms where dust contamination is a major concern.
        ventilationPerPerson:The desired minimum rate of outdoor air ventilation through the mechanical system into the zone per person in the zone.  Values here should be in m3/s-person (Liters per second per person in the zone). In effect, an input here will mimic demand controlled ventilation, where the ventilation through the mechanical system will change depending upon the occupancy. Most standards suggest that you should have at least 0.001 m3/s for each person in the zone but this may be increased sometimes to avoid odors or exposure to indoor pollutants.

"""

ghenv.Component.Name = "Honeybee_Get Zone EnergyPlus Loads"
ghenv.Component.NickName = 'getHBZoneEPLoads'
ghenv.Component.Message = 'VER 0.0.66\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "HB-Legacy"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBZone):
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
    
    # get Honeybee zone
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObject = hb_hive.visualizeFromHoneybeeHive([HBZone])[0]
    
    try:
        loads = HBZoneObject.getCurrentLoads(True, ghenv.Component)
    except:
        msg = "Failed to load zone loads!"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    equipmentLoadPerArea = loads['EquipmentsLoadPerArea']
    infiltrationRatePerArea = loads['infiltrationRatePerArea']
    lightingDensityPerArea = loads['lightingDensityPerArea']
    numOfPeoplePerArea = loads[ 'numOfPeoplePerArea']
    ventilationPerArea = loads['ventilationPerArea']
    ventilationPerPerson = loads[ 'ventilationPerPerson']
    
    return equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson
    



if _HBZone:
    results = main(_HBZone)
    
    if results != -1:
        equipmentLoadPerArea, infilRatePerArea_Facade, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson = results