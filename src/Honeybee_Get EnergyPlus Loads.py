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
Look up loads for an specific bldgProgram and zoneProgram
-
Provided by Honeybee 0.0.64

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

ghenv.Component.Name = "Honeybee_Get EnergyPlus Loads"
ghenv.Component.NickName = 'getEPLoads'
ghenv.Component.Message = 'VER 0.0.64\nOCT_24_2019'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
from pprint import pprint

def main(HBZoneProgram):
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
    
    openStudioStandardLib = sc.sticky ["honeybee_OpenStudioStandardsFile"]
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    bldgProgram, zoneProgram = HBZoneProgram.split("::")
    
    try:
        schedulesAndLoads = openStudioStandardLib['space_types']['90.1-2007']['ClimateZone 1-8'][bldgProgram][zoneProgram]
    except:
        msg = "Either your input for bldgProgram > [" + str(bldgProgram) + "] or " + \
              "the input for zoneProgram > [" + str(zoneProgram) + "] is not valid; " + \
              "or [" + str(bldgProgram) + "] and [" + str(zoneProgram) + "] is not a valid combination.\n" + \
              "Use ListSpacePrograms component to find the available programs."
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    # pprint(schedulesAndLoads)
    equipmentLoadPerArea = schedulesAndLoads['elec_equip_per_area'] * 10.763961 #Per ft^2 to Per m^2
    infiltrationRatePerArea = schedulesAndLoads['infiltration_per_area_ext'] * 0.00508001
    lightingDensityPerArea = schedulesAndLoads['lighting_w_per_area'] * 10.763961 #Per ft^2 to Per m^2
    numOfPeoplePerArea = schedulesAndLoads[ 'occupancy_per_area'] * 10.763961 /1000 #Per 1000 ft^2 to Per m^2
    ventilationPerArea = schedulesAndLoads['ventilation_per_area'] * 0.00508001 #1 ft3/min.m2 = 5.08001016E-03 m3/s.m2
    ventilationPerPerson = schedulesAndLoads[ 'ventilation_per_person'] * 0.0004719  #1 ft3/min.perosn = 4.71944743E-04 m3/s.person
    
    return equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson
    



if _zoneProgram:
    results = main(_zoneProgram)
    
    if results != -1:
        equipmentLoadPerArea, infilRatePerArea_Facade, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson = results