# By Chris Mackey
# Chris@MackeyArchitecture.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to set up simple natural ventilation for your zones.  Connected zones must have windows in order for them to naturally ventilate.
The natural ventilation works by using an area of operable window to compute an esimated airflow for the zone using a simple bouyancy orifice equation and wind-driven coefficient equation.
_
Specifically, these equations are as follows:
Ventilation Wind = Cw * Opening Area * Schedule * WindSpd 
Ventilation Stack = Cd * Opening Area * Schedule * SQRT(2*g*DH*(|(Tzone-Todb)|/Tzone)) 
Total Ventilation = SQRT((Ventilation Wind)^2 + (Ventilation Stack)^2)
-
Provided by Honeybee 0.0.55

    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.
        _minIndoorTempForNatVent: A number or list of numbers between -100 and 100 that represents the minimum indoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxIndoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the maximum indoor temperature at which to naturally ventilate.  Use this to design mixed-mode buildings where you would like occupants to shut the windows and turn on a cooling system if it gets too hot inside.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        minOutdoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the minimum outdoor temperature at which to naturally ventilate.  This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxOutdoorTempForNatVent_: A number or list of numbers between -100 and 100 that represents the minimum outdoor temperature at which to naturally ventilate.  Use this to design night flushed buildings where windows are closed for daytime temperatures and opened at night or a mixed-mode buildings where you would like occupants to shut the windows and turn on a cooling system if it gets too hot outside. This can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        fractionOfGlzAreaOperable_: A number or list of numbers between 0.0 and 1.0 that represents the fraction of the window area that is operable.  By default, it will be assumed that this is 0.5 for double-hung windows.
        fractionOfGlzHeightOperable_: A number or list of numbers between 0.0 and 1.0 that represents the fraction of the distance from the bottom of the zones windows to the top that are operable.  By default, it will be assumed that this is 1.0 assuming windows with openings at both the very top and very bottom.
        openingAreaFractionalSched_: An optional schedule to set the fraction of the window that is open at each hour.
    Returns:
        readMe:...
        HBZones: HBZones that will be naturally ventilated.
"""

ghenv.Component.Name = "Honeybee_Set EP Natural Ventilation"
ghenv.Component.NickName = 'setEPNatVent'
ghenv.Component.Message = 'VER 0.0.55\nDEC_13_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nDEC_13_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os
import Rhino as rc

w = gh.GH_RuntimeMessageLevel.Warning

def setDefaults():
    #HAve a function to duplicate data.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #Have a function to check the ranges of a list.
    def checkRange(values, lowerBound, upperBound):
        checkAllRanges = True
        for item in values:
            if item < lowerBound or item > upperBound: checkAllRanges = False
        if checkAllRanges == False:
            warning = "One of the connected values is not in the acceptable range."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        return checkAllRanges
    
    #Have a function to check that a list matches the length of HBZones.
    def checkWithHBZone(listOfValues, name):
        checkListLen = True
        if len(listOfValues) > 1:
            if len(listOfValues) == len(_HBZones): goodData = listOfValues
            else:
                checkListLen = False
                warning = "The length of the " + name + " list does not match the number of _HBZones."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        elif len(listOfValues) == 1:
            goodData = duplicateData(listOfValues, len(_HBZones))
        else: goodData = []
        
        return checkListLen, goodData
    
    
    #Check to make sure that everything matches with the HBZones.
    checkData1, minIndoorTemp = checkWithHBZone(_minIndoorTempForNatVent, "_minIndoorTempForNatVent")
    checkData2, maxIndoorTemp = checkWithHBZone(maxIndoorTempForNatVent_, "maxIndoorTempForNatVent_")
    checkData3, minOutdoorTemp = checkWithHBZone(minOutdoorTempForNatVent_, "minOutdoorTempForNatVent_")
    checkData4, maxOutdoorTemp = checkWithHBZone(maxOutdoorTempForNatVent_, "maxOutdoorTempForNatVent_")
    checkData5, fractionOfArea = checkWithHBZone(fractionOfGlzAreaOperable_, "fractionOfGlzAreaOperable_")
    checkData6, fractionOfHeight = checkWithHBZone(fractionOfGlzHeightOperable_, "fractionOfGlzHeightOperable_")
    checkData7,areaSched = checkWithHBZone(openingAreaFractionalSched_, "openingAreaFractionalSched_")
    
    #Check to make sure all data is in the right range.
    checkData8 = checkRange(minIndoorTemp, -100, 100)
    checkData9 = checkRange(maxIndoorTemp, -100, 100)
    checkData10 = checkRange(minOutdoorTemp, -100, 100)
    checkData11 = checkRange(maxOutdoorTemp, -100, 100)
    checkData12 = checkRange(fractionOfArea, 0, 1)
    checkData13 = checkRange(fractionOfHeight, 0, 1)
    
    #Check to be sure all is ok.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True:
        checkData = True
    
    return checkData, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, fractionOfArea, fractionOfHeight, areaSched

def main(HBZones, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, fractionOfArea, fractionOfHeight, areaSched):
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
    
    readMe = []
    
    # make sure area schedules are in HB schedule library.
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
    
    for schedule in areaSched: 
        if schedule!=None:
            schedule= schedule.upper()
        
        if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
            msg = "Cannot find " + schedule + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return -1
        elif schedule!=None and schedule.lower().endswith(".csv"):
            # check if csv file is existed
            if not os.path.isfile(schedule):
                msg = "Cannot find the shchedule file: " + schedule
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    for zoneCount, HBZone in enumerate(HBObjectsFromHive):
        #Get the glazed surfaces of the zone.
        windows = []
        for srf in HBZone.surfaces:
            if srf.type == 0:
                if srf.BC.upper() == "SURFACE": pass
                else:
                    if srf.hasChild:
                        for childSrf in srf.childSrfs:
                            windows.append(childSrf.geometry)
                    else: pass
            elif srf.type == 1:
                if srf.hasChild:
                    for childSrf in srf.childSrfs:
                        windows.append(childSrf.geometry)
                else:pass
        
        if len(windows) != 0:
            HBZone.natVent = True
            
            #Calculate the total glazed area of the zone.
            glazedArea = 0.0
            for srf in windows:
                glazedArea = glazedArea + rc.Geometry.AreaMassProperties.Compute(srf).Area
            
            #Calculate the height difference of the glazing across the zone.
            fullWindowBrep = rc.Geometry.Brep()
            for brep in windows:
                rc.Geometry.Brep.Append(fullWindowBrep, brep)
            glzBB = rc.Geometry.Brep.GetBoundingBox(fullWindowBrep, rc.Geometry.Plane.WorldXY)
            glzHeight = glzBB.Max.Z - glzBB.Min.Z
            
            #Assign the opening area and height to the zone.
            if fractionOfArea == []: fractArea = 0.5
            else: fractArea = fractionOfArea[zoneCount]
            HBZone.windowOpeningArea = fractArea*glazedArea
            readMe.append(HBZone.name + " has a glazed area of " + str(glazedArea) + " m2 and " + str(fractArea*glazedArea) + " m2 of it is operable.")
            
            if fractionOfHeight == []: fractHeight = 1
            else: fractHeight = fractionOfHeight[zoneCount]
            HBZone.windowHeightDiff = fractHeight*glzHeight
            readMe.append(HBZone.name + " has a glazed height of " + str(round(glzHeight, 1)) + " m and " + str(round(fractHeight*glzHeight, 1)) + " m of it is operable.")
            
            #Assign the nat vent temperature limits.
            HBZone.natVentMinIndoorTemp = minIndoorTemp[zoneCount]
            if maxIndoorTemp != []: HBZone.natVentMaxIndoorTemp = maxIndoorTemp[zoneCount]
            if minOutdoorTemp != []: HBZone.natVentMinOutdoorTemp = minOutdoorTemp[zoneCount]
            if maxOutdoorTemp != []: HBZone.natVentMaxOutdoorTemp = maxOutdoorTemp[zoneCount]
            
            #Assign the nat vent schedule,
            if areaSched != []:
                HBZone.natVentSchedule = areaSched[zoneCount]
        else:
            warning = "One of the connected HBZones does not have any windows and so natural ventilation will not be assigned."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones, readMe
    

checkData = False
if _HBZones and _HBZones[0]!=None and _minIndoorTempForNatVent and _minIndoorTempForNatVent[0]!=None:
    checkData, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, fractionOfArea, fractionOfHeight, areaSched = setDefaults()
    if checkData == True:
        results = main(_HBZones, minIndoorTemp, maxIndoorTemp, minOutdoorTemp, maxOutdoorTemp, fractionOfArea, fractionOfHeight, areaSched)
        
        if results != -1: HBZones, readMe = results