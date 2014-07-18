# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Customize EnergyPlus Objects [NOT READY YET!]

-
Provided by Honeybee 0.0.53
    
    Args:
        schName_: Schedule name
            
    Returns:
        name:
        schedule:
        comments:
"""

ghenv.Component.Name = "Honeybee_Customize EnergyPlus Objects"
ghenv.Component.NickName = 'customizeEPObjs'
ghenv.Component.Message = 'VER 0.0.53\nJUL_18_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | WIP"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(EPObjectName, indexes, inValues):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
        return -1
    
    hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    values, comments = hb_EPScheduleAUX.getScheduleDataByName(EPObjectName.upper())
    
    if values == None:
        values, comments = hb_EPMaterialAUX.decomposeEPCnstr(EPObjectName.upper())
    
    if values == None:
        try:
            values, comments = hb_EPMaterialAUX.decomposeMaterial(EPObjectName.upper())
        except:
            pass
    
    if values == None: return
    
    # create a dictionary of index and values
    if len(indexes)==0 or (len(indexes) != len(inValues)):
        return
    
    valuesDict = {}
    
    for i, v in zip(indexes, inValues):
        valuesDict[i] = v
    
    count = 0
    originalObj = ""
    modifiedObj = ""
    
    for value, comment in zip(values, comments):
        if count == 1:
            # add name
            originalObj += `count` + " ->\t " + EPObjectName.upper() + "\t\t! Name\n" 
            
            if count in valuesDict.keys():
                modifiedObj += `count` + " ->\t " + valuesDict[count].upper() + "\t\t! Name\n"
            else:
                modifiedObj += `count` + " ->\t " + EPObjectName.upper() + "\t\t! Name\n"
        else:
            originalObj += `count` + " ->\t " + value + "\t\t!" + comment + "\n" 
            
            if count in valuesDict.keys():
                modifiedObj += `count` + " ->\t " + valuesDict[count] + "\t\t!" + comment + "\n"
            else:
                modifiedObj += `count` + " ->\t " + value + "\t\t!" + comment + "\n" 
        
        count += 1
    return originalObj, modifiedObj


if _EPObjectName:
    objects = main(_EPObjectName, indexes_, values_)
    if objects:
        originalObj, modifiedObj = objects