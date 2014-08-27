# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Filter EP Schedule Library

-
Provided by Honeybee 0.0.54
    
    Args:
        keywords_: List of keywords to filter the list of materials
            
    Returns:
        EPMaterials: List of EP materials in Honeybee library
        EPWindowMaterils: List of EP window materials in Honeybee library
        EPConstructios:  List of EP constructions in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Search EP Schedule Library"
ghenv.Component.NickName = 'SearchEPSCHLibrary'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

def main(scheduleList, HBZoneProgram, scheduleType):
    selSch =[]
    
    try: bldgProgram, zoneProgram = HBZoneProgram.split("::")
    except: bldgProgram, zoneProgram = None, None
        
    for schName in scheduleList:
       if schName.upper().find(bldgProgram.upper())!=-1 and schName.upper().find(scheduleType.upper())!=-1:
            selSch.append(schName)
    
    # check if any alternate
    exactFit = []
    if zoneProgram!="":
        for schName in selSch:
            if schName.upper().find(zoneProgram.upper())!= -1:
                exactFit.append(schName)
    else:
        exactFit = sorted(selSch, key = lambda schName: len(schName))[0]
    return exactFit, selSch

if _scheduleList:
    selSchedule, possibleAlt = main(_scheduleList, zoneProgram_, scheduleType_)
    
    selSchedules = [selSchedule] + possibleAlt