# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Filter EP Schedule Library

-
Provided by Honeybee 0.0.53
    
    Args:
        keywords_: List of keywords to filter the list of materials
            
    Returns:
        EPMaterials: List of EP materials in Honeybee library
        EPWindowMaterils: List of EP window materials in Honeybee library
        EPConstructios:  List of EP constructions in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Search EP Schedule Library"
ghenv.Component.NickName = 'SearchEPSCHLibrary'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "07 | Energy | Schedule"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

def main(scheduleList, bldgProgram, zoneProgram, scheduleType):
    selSch =[]
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
    selSchedule, possibleAlt = main(_scheduleList, bldgProgram_, zoneProgram_, scheduleType_)
    
    selSchedules = [selSchedule] + possibleAlt