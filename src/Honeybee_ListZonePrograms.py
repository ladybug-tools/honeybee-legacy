# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Find list of spaces for each space based on program
-
Provided by Honeybee 0.0.55

    Args:
        _bldgProgram: An index number for 
    Returns:
        bldgProgram:
        zonePrograms: Honeybee zones in case of success
"""

ghenv.Component.Name = "Honeybee_ListZonePrograms"
ghenv.Component.NickName = 'ListZonePrograms'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "05 | Energy | Building Program"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

path = gh.Data.GH_Path(0)

ghenv.Component.Params.Output[0].Name = "zonePrograms"
ghenv.Component.Params.Output[0].NickName = "zonePrograms"

def main(bldgProgram):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    BuildingPrograms = sc.sticky["honeybee_BuildingProgramsLib"]()
    bldgProgramDict = BuildingPrograms.bldgPrograms
    zonesProgramDict = BuildingPrograms.zonePrograms
    
    bldgProgramName = bldgProgramDict[bldgProgram%13]
    zonePrograms = zonesProgramDict[bldgProgramName].values()
    
    return bldgProgramName, zonePrograms


if _bldgProgram!=None:
    results = main(_bldgProgram)
    
    if results!=-1:
        bldgProgram, zonePrograms = results
        
        bldgAndZonP = range(len(zonePrograms))
        for pCount, zoneProgram in enumerate(zonePrograms):
            bldgAndZonP[pCount] = "::".join([bldgProgram , zoneProgram])
            
        ghenv.Component.Params.Output[0].Name = bldgProgram + "ZonePrograms"
        ghenv.Component.Params.Output[0].NickName = bldgProgram + "ZonePrograms"
        
        #for programCount, program in enumerate(zonePrograms):
        #    ghenv.Component.Params.Output[0].AddVolatileData(path, programCount + 1, program)
        
        # not the best solution but the normal solution was missing the first item for some reason
        line  = bldgProgram + "ZonePrograms = bldgAndZonP"
        exec(line)