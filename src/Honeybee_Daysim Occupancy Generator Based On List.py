# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim Occupancy Generator
Daysim calculates the outputs for the hours that the space is occupied. This componet generates a csv file based on user input that will be used as the occupancy-file. Read more here: http://daysim.ning.com/page/keyword-occupancy-profile 
You can use this component to generate a Daysim schedule based of EnergyPlus schedule.

-
Provided by Honeybee 0.0.54
    Args:
        _occValues: A list of 0 and 1 that indicates the occupancy schedule. The length of the list should be equal to 8760. 
        _fileName_: Optional fileName for this schedule. Files will be saved to C:\Honeybee\DaysimOcc
        _writeTheOcc: Set to True to write the file
        
    Returns:
        occupancyFile: Path to occupancy file
"""

ghenv.Component.Name = "Honeybee_Daysim Occupancy Generator Based On List"
ghenv.Component.NickName = 'occupancyGenerator'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

def main(hourlyValues, fileName):
    msg = None
    
    if len(hourlyValues)!=8760:
        msg = "Length of occValues should be 8760 values for every hour of the year."
        return msg, None
        
    # import the classes
    if not sc.sticky.has_key('ladybug_release') or not sc.sticky.has_key('honeybee_release'):
        msg = " You need to let Ladybug and honeybee to fly first!"
        return msg, None

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

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    # create the folder if not exist
    folder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "DaysimCSVOCC\\")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    
    heading = "# Daysim occupancy file,,,\n" + \
          "# time_step 60, comment: weekdays are based on user list inputs." + \
          "daylight savings time is based on user input),,\n" + \
          "# month,day,time,occupancy (1=present/0=absent)\n"
    
    if fileName == None:
        fileName = "userDefinedOccBasedOfHourlyValues.csv"
    
    fullPath = folder + fileName
    
    with open(fullPath, "w") as occFile:
        occFile.write(heading)
        for HOY, occ in enumerate(hourlyValues):
            HOY += 1
            d, m, t = lb_preparation.hour2Date(HOY, True)
            
            m += 1 #month starts from 0 in Ladybug hour2Date. I should fix this at some point
            
            t -= .5 # add half an hour to the time to be similar to daysim
            
            if t == -.5: t = 23.5
            
            if occ > 0: occ = 1
            else: occ = 0
            
            occLine = str(m) + "," + str(d) + "," + str(t) + "," + str(occ) + "\n"
            occFile.write(occLine)
        
    return msg, fullPath


if _occValues and _writeTheOcc==True:
    
    msg, occupancyFile = main(_occValues, _fileName_)
    
    if msg!=None:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)

