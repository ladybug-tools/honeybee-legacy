# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim Occupancy Generator
Daysim calculates the outputs for the hours that the space is occupied. This componet generates a csv file based on user input that will be used as the occupancy-file. Read more here: http://daysim.ning.com/page/keyword-occupancy-profile 
You can use this component to generate a Daysim schedule based of EnergyPlus schedule.

-
Provided by Honeybee 0.0.53
    Args:
        _occValues: A list of 0 and 1 that indicates the occupancy schedule. The length of the list should be equal to 8760. 
        _fileName_: Optional fileName for this schedule. Files will be saved to C:\Honeybee\DaysimOcc
        _writeTheOcc: Set to True to write the file
        
    Returns:
        occupancyFile: Path to occupancy file
"""

ghenv.Component.Name = "Honeybee_Daysim Occupancy Generator Based On List"
ghenv.Component.NickName = 'occupancyGenerator'
ghenv.Component.Message = 'VER 0.0.53\nAUG_08_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
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
    
    # create the folder if not exist
    folder = "c:/honeybee/DysimOcc/"
    if not os.path.isdir(folder):
        os.mkdir(folder)
        
    # import the classes
    if not sc.sticky.has_key('ladybug_release'):
        msg = " You need to let Ladybug fly first!\nI know this is a Honeybee component but it actually uses Ladybug's functions."
        return msg, None
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    
    heading = "# Daysim occupancy file,,,\n" + \
          "# time_step 60, commnet: weekdays are based on user list inputs." + \
          "daylight savings time is based on user input),,\n" + \
          "# month,day,time,occupancy (1=present/0=absent)\n"
    
    if fileName == None:
        fileName = "userDefinedOccBasedOfHourlyValues.csv"
    
    fullPath = folder + fileName
    
    with open(fullPath, "w") as occFile:
        occFile.write(heading)
        for HOY, occ in enumerate(hourlyValues):
            
            d, m, t = lb_preparation.hour2Date(HOY, True)
            
            m += 1 #month starts from 0 in Ladybug hour2Date. I should fix this at some point
            HOY -= 1
            
            t += .5 # add half an hour to the time to be similar to daysim
            
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

