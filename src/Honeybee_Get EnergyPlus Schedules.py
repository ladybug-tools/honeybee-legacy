# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Look up schedules for an specific bldgProgram and zoneProgram
-
Provided by Honeybee 0.0.53

    Args:
        bldgProgram_:...
        zoneProgram_:...
    Returns:
        occupancySchedule:
        heatingSetPtSchedule:
        coolingSetPtSchedule:
        lightingSchedule:
        equipmentSchedule:
        infiltrationSchedule:
"""

ghenv.Component.Name = "Honeybee_Get EnergyPlus Schedules"
ghenv.Component.NickName = 'getEPSchedules'
ghenv.Component.Message = 'VER 0.0.53\nJUN_29_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass
import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBZoneProgram):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    bldgProgram, zoneProgram = HBZoneProgram.split("::")
    
    openStudioStandardLib = sc.sticky ["honeybee_OpenStudioStandardsFile"]
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
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
        
    occupancySchedule = schedulesAndLoads['occupancy_sch']
    occupancyActivitySch = schedulesAndLoads['occupancy_activity_sch'] 
    heatingSetPtSchedule = schedulesAndLoads['heating_setpoint_sch']
    coolingSetPtSchedule = schedulesAndLoads['cooling_setpoint_sch']
    lightingSchedule = schedulesAndLoads['lighting_sch']
    equipmentSchedule = schedulesAndLoads['elec_equip_sch']
    infiltrationSchedule = schedulesAndLoads['infiltration_sch']
    
    return occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule
    
    
if _zoneProgram:
    results = main(_zoneProgram)
    
    if results != -1:
        occupancySchedule, occupancyActivitySch, heatingSetPtSchedule, coolingSetPtSchedule, lightingSchedule, equipmentSchedule, infiltrationSchedule = results