# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Look up loads for an specific bldgProgram and zoneProgram
-
Provided by Honeybee 0.0.53

    Args:
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        equipmentLoadPerArea:
        infiltrationRatePerArea:
        lightingDensityPerArea:
        numOfPeoplePerArea:
        ventilationPerArea:
        ventilationPerPerson:
"""

ghenv.Component.Name = "Honeybee_Get EnergyPlus Loads"
ghenv.Component.NickName = 'getEPLoads'
ghenv.Component.Message = 'VER 0.0.53\nJUN_29_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
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
        equipmentLoadPerArea, infiltrationRatePerArea, lightingDensityPerArea, numOfPeoplePerArea, ventilationPerArea, ventilationPerPerson = results