#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chien Si Harriman <> 
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
Grizzlybear exports Honeybee zones to gbXML file
-
Provided by Honeybee 0.0.60

    Args:
        EquipRange: reserved for future use
        LPDRange: reserved for future use
        bldgType: reserved for future use
        epwFileAddress: location of the EnergyPlus weather file
        rhinolocation: will be replaced with LadyBug location
        _HBZones: Input your honeybee zones
        HBContext: Input your honeybee context
        meshSettings_: Custom mesh setting. Use Grasshopper mesh setting components
        _writegbXML: Set to true to create gbxml
        _workingDir: Working directory
        fileName: choose a filename, no need to add the xml extension.  
    Returns:
        readMe!: ...
        resultFileAddress: ...
"""

ghenv.Component.Name = "Honeybee_GrizzlyBear"
ghenv.Component.NickName = 'grizzlyBear'
ghenv.Component.Message = 'VER 0.0.60\nOCT_27_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import traceback
import re
import logging
import Grasshopper.Kernel as gh
import datetime

gbXMLLibFolder = "C:\\gbXML"

gbXMLIsReady = True
if os.path.isdir(gbXMLLibFolder):
    if os.path.isfile(os.path.join(gbXMLLibFolder, "VectorMath.dll")):
        #vectormath library present
        logging.info('vector math present.')
    else:
        msg = "Cannot find Grizzly Bear Vector Math Dependency. You can download the libraries from the link below. " + \
          "Copy the file to C:\\gbXML"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        link = "https://www.dropbox.com/sh/vaklarrhw9tylg4/AABQdgKCb4qRdlI16ik8WqUya"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, link)
        gbXMLIsReady = False
    if os.path.isfile(os.path.join(gbXMLLibFolder, "gbXMLSerializer.dll")):
        #vectormath library present
        logging.info('gbXML serializer present.')
    else:
        msg = "Cannot find Grizzly Bear Serializer Dependency. You can download the libraries from the link below. " + \
          "Copy the file to C:\gbXML"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        link = 'https://www.dropbox.com/sh/vaklarrhw9tylg4/AABQdgKCb4qRdlI16ik8WqUya'
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, link)
        gbXMLIsReady = False
else:
    gbXMLIsReady = False
    # let the user know that they need to download OpenStudio libraries
    msg = "Cannot find a gbXML folder or any dependencies.  Create a folder at C:\gbXML." \
        'Then click on the link below to download dependencies.  Copy these into this folder after downloading.'
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    link = "https://www.dropbox.com/sh/vaklarrhw9tylg4/AACBaYtBPIHkNj2QC82E7jgSa"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, link)
    

if gbXMLIsReady:
    try:
        logging.basicConfig(filename=os.path.join(gbXMLLibFolder,'GBlog.txt'),filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)
        print filename
    except:
        print 'not logging'
    import shutil
    #shutil.copy2(gbXMLLibFolder+"\\gbXMLSerializer.dll","C:\\CHPrograms\\gbXMLSerializer.dll")
    
    
    import clr
    clr.AddReferenceToFileAndPath(os.path.join(gbXMLLibFolder, "gbXMLSerializer.dll"))
    #clr.AddReferenceToFileAndPath("C:\\Program Files (x86)\\OpenStudio 1.3.0\\CSharp\\openstudio\\OpenStudio.dll")
    clr.AddReferenceToFileAndPath(os.path.join(gbXMLLibFolder, "VectorMath.dll"))
    clr.AddReference("System.Xml")
    clr.AddReference("System.Core")
    clr.AddReference("System.Runtime.Remoting")
    
    import System
    import System.Xml
    import System.Xml.Serialization
    clr.ImportExtensions(System.Linq)
    clr.ImportExtensions(System.Globalization)
    from System.Collections.Generic import List
    from System import DateTime
    from System.Xml import XmlConvert
    
    from System.Globalization import CultureInfo
    
    
    import sys
    import uuid
    import math
    import copy
    
    import gbXMLSerializer as gbx
    import scriptcontext as sc
    import Rhino as rc
    import VectorMath as v
    #import OpenStudio as os


class WritegbXML(object):
    
    def __init__(self, location, zipCode):
        # import location
        locationStr = _location.split('\n')
        newLocStr = ""
        
        #clean the coments
        for line in locationStr:
            if '!' in line: newLocStr += line.split('!')[0].strip()
            else: newLocStr += line
        
        newLocStr = newLocStr.replace(';', "")
        
        site, self.locationName, self.latitude, self.longitude, timeZone, elevation = newLocStr.split(',')
        
        # zipCode
        if zipCode!=None: self.zipCode = zipCode
        else: self.zipCode = "00000"
    
    def point3DtoMemorySafeCoord(pt3d):
        
        x = pt3d.X
        y = pt3d.Y
        z = pt3d.Z
        gbmemSafeCoord = v.Vector.MemorySafe_CartCoord(x,y,z)
        logging.debug('Convert point3d to VectorMemorySafe Coord Success.')
        return gbmemSafeCoord
    
    #makes a list of list of memorysafecoordinates, for polyloops
    def point3DListtoMemorySafeCoordList(self,coordinateList):
        try:
            logging.debug('Creating Memsafecoord list from point3D list.')
            memsafelist = List[List[v.Vector.MemorySafe_CartCoord]]()
            for listcount, coordinates in enumerate(coordinateList):
                memsafepts = List[v.Vector.MemorySafe_CartCoord]()
                for pointcount,pt in enumerate(coordinates):
                    memsafept = v.Vector.MemorySafe_CartCoord(pt.X,pt.Y,pt.Z)
                    memsafepts.Add(memsafept)
                memsafelist.Add(memsafepts)
            logging.info('point3d List successfully converted to MemSafe Coord List.')
        except:
            logging.debug('Creating Memsafecoord list from point3D list.')
            memsafelist = List[List[v.Vector.MemorySafe_CartCoord]]()
            for listcount, coordinates in enumerate(coordinateList[0]):
                memsafepts = List[v.Vector.MemorySafe_CartCoord]()
                for pointcount,pt in enumerate(coordinates):
                    memsafept = v.Vector.MemorySafe_CartCoord(pt.X,pt.Y,pt.Z)
                    memsafepts.Add(memsafept)
                memsafelist.Add(memsafepts)
            logging.info('point3d List successfully converted to MemSafe Coord List.')
        return memsafelist
    
    #required to count up the shades in case they are meshed
    def getShadeCount(self,shades):
        shdct = 0
        for surfnum,shade in enumerate(shades):
                
                #coordinateList contains all the shade points for all shades
                coordinatesList = shade.extractPoints()
                #print coordinatesList
                try:
                    len(coordinatesList[0][0])
                    print 'meshed surface'
                    for subcount,ss in enumerate(coordinatesList):
                        shdct+=1
                except:
                    shdct+=1
        return shdct
    
    #takes a Honeybee space, finds the floor, then finds its area
    def findZoneFloorArea(self,surfaces):
        logging.debug('Finding floor area of all surfaces.')
        for ct,surface in enumerate(surfaces):
            print ct, surface
            coordlist = surface.coordinates ##extractPoints()
            
            try:
                memsafelist = wgb.point3DListtoMemorySafeCoordList([coordlist])
            except:
                memsafelist = wgb.point3DListtoMemorySafeCoordList(coordlist)
            
            normal = v.Vector.GetMemRHR(memsafelist[0])
            
            #get tilt
            tilt=gbx.prod.FindTilt(normal)
            
            if(tilt == 180):
                print 'found a floor!'
                z = coordlist[0][2]
                print z
                #then we have found the floor
                area = v.Vector.GetAreaofMemSafeCoords(memsafelist[0])
                logging.info('Successfully found floor and calculated area.')
                return area, z

        
    def makeLevelCoords(self,zheight):
        coordinates = []
        coordinate1=[0,0,zheight]
        coordinates.append(coordinate1)
        coordinate2=[-10,0,zheight]
        coordinates.append(coordinate2)
        coordinate3=[-10,-10,zheight]
        coordinates.append(coordinate3)
        return coordinates
        
    def isItSquare(self,memsafelist):
        logging.info('Finding if the surface is a square.')
        sqrnt = False
        perps = []
        ht = 0
        wid = 0
        if len(memsafelist) != 4:
            return sqrnt,ht,wid
        else:
            for ct,coord in enumerate(memsafelist):
                if(ct < len(memsafelist)-2):
                    v1 = v.Vector.CreateMemorySafe_Vector(memsafelist[ct],memsafelist[ct+1])
                    if ht != v.Vector.VectorMagnitude(v1):
                        ht = v.Vector.VectorMagnitude(v1)
                    v2 = v.Vector.CreateMemorySafe_Vector(memsafelist[ct+1],memsafelist[ct+2])
                    if wid != v.Vector.VectorMagnitude(v2):
                        wid = v.Vector.VectorMagnitude(v2)
                    dot = v.Vector.DotProductMag(v1,v2)
                    if(dot == 0):
                        perps.append(1)
                    else:
                        perps.append(2)
                elif (ct == len(memsafelist) - 2):
                     v1 = v.Vector.CreateMemorySafe_Vector(memsafelist[ct],memsafelist[ct+1])
                     v2 = v.Vector.CreateMemorySafe_Vector(memsafelist[ct+1],memsafelist[0])
                     dot = v.Vector.DotProductMag(v1,v2)
                     if(dot == 0):
                        perps.append(1)
                     else:
                        perps.append(2)
            if 2 in perps:
                return sqrnt, ht, wid
            else:
                sqrnt = True
                return sqrnt, ht, wid
        
    def writeShellGeo(self, surfaces, space, namingMethod = 0):
        logging.info('Writing gb shell geometry.')
        # generate gbXML Shell Geometry (for now assume zero thickness
        # assume that each surface defines a single surface (not meshed)
        sg = gbx.ShellGeometry()
        sg.unit = gbx.lengthUnitEnum.Meters
        sg.id = "sg"+space.Name
        print sg.id
        #make closed shell
        cs = gbx.ClosedShell()
        #put polyloops in closed shell
        totsurfcount = 0
        totsurfaces=[]
        for surfcount, surface in enumerate(surfaces):
            #get list of point for the surface from the HoneyBee Surface
            coordinatesList = surface.coordinates ##extractPoints()
            
            #not meshed
            coordinatesList = [coordinatesList]
            totsurfcount+=1
            totsurfaces.append(coordinatesList)
            #print "notmeshed"
        
        #print len(coordinatesList)
        #print totsurfcount
        #print len(totsurfaces)
        cs.PolyLoops = gbx.prod.makePolyLoopArray(totsurfcount)
        for plcount, allsurf in enumerate(totsurfaces):
            #get list of point for the surface from the HoneyBee Surface
            coordinatesList = allsurf
            # print coordinatesList
            if not isinstance(coordinatesList[0], list) and not isinstance(coordinatesList[0], tuple):
                coordinatesList = [coordinatesList]
            for count, coordinates in enumerate(coordinatesList):
                #print "coords",coordinates
                cs.PolyLoops[plcount].Points = gbx.BasicSerialization.makeCartesianPtArray(len(coordinates));
                for ptcount,pt in enumerate(coordinates):
                    #print pt
                    cp = wgb.makegbCartesianPt(pt)
                    #for the list holding all surface polyloops, 1 point = cp
                    cs.PolyLoops[plcount].Points[ptcount] = cp
            
        sg.ClosedShell = cs
        space.ShellGeo = sg
        logging.debug('Successfully created shell geometry for space.'+sg.id)
        return space

    def EPSCHStr(self, gb, scheduleName,ct,wknmdict):
            logging.debug('Making schedules for gb node')
            scheduleName = scheduleName.upper()
            #try:
            scheduleData = None
            if scheduleName in sc.sticky ["honeybee_ScheduleLib"].keys():
                scheduleData = sc.sticky ["honeybee_ScheduleLib"][scheduleName]
            elif scheduleName in sc.sticky ["honeybee_ScheduleTypeLimitsLib"].keys():
                scheduleData = sc.sticky["honeybee_ScheduleTypeLimitsLib"][scheduleName]
            
            if scheduleData!=None:
                numberOfLayers = len(scheduleData.keys())
                scheduleStr = scheduleData[0] + ",\n"
                #break this down with a regex to figure out if it is a year, or what 
                m = re.match('(.*)(:)(.*)',scheduleData[0])
                if m:
                    if (m.group(3) == "Year"):
                        logging.info('Found a regex match for year:'+m.group(3))
                        yrs = gbx.Schedule()
                        gb.Schedule[ct] = yrs
                        yrs.id = scheduleName.replace(" ","_")
                        startdate = ''
                        enddate = ''
                        yrarr = []
                        marr = []
                        mar = []
                        for layer in range(1, numberOfLayers):
                            d = scheduleData[layer][1]
                            if(d == '- Schedule Type Limits Name'):
                                #assign schedule type

                                mt = re.match('(Temperature)(\d*)',scheduleData[layer][0])
                                if mt:
                                    stype = mt.group(1)
                                    stype = stype.strip()
                                    yrs.type = wgb.assignScheduleTypes(stype)
                                else:
                                    stype = scheduleData[layer][0]
                                    yrs.type = wgb.assignScheduleTypes(stype)
                            elif (re.match("(- Start Month)(.*)",d)):
                                logging.info('Found Startmonth of honeybee object string.')
                                startdate = scheduleData[layer][0]+'-'
                            elif (re.match("(- Start Day)(.*)",d)):
                                startdate = startdate + scheduleData[layer][0]
                                marr.append(startdate)
                            elif (re.match("(- End Month)(.*)",d)):
                                logging.info('Found Endmonth of honeybee object string')
                                enddate = scheduleData[layer][0]+'-'
                            elif (re.match("(- End Day)(.*)",d)):
                                enddate = enddate + scheduleData[layer][0]
                                marr.append(enddate)
                                mar = copy.deepcopy(marr)
                                yrarr.append(mar)
                                marr=[]
                            elif(re.match('(.*)(:)(.*)',scheduleData[layer][1])):
                                m = re.match('(.*)(:)(.*)',scheduleData[layer][1])
                                wk = re.match('(Week Name)(.*)',m.group(3))
                                if wk:
                                    logging.info('Found weekly sch id associated with start and stops.')
                                    wknum = wk.group(2)
                                    
                                    wks = re.match('(.*)({)(.*)(})',scheduleData[layer][0])
                                    if wks:
                                        ws=gbx.WeekScheduleId()
                                        #print wks.group(3)
                                        wknms.append(wks.group(3))
                                        ws.weekScheduleIdRef = 'Week-'+str(wknms.index(wks.group(3)))
                                        
                                        #need this to properly assign the week schedule id
                                        marr.append(ws)
                        
                        yearsched = gbx.BasicSerialization.setYearScheduleArray(len(yrarr))
                        yrs.YearSchedule = yearsched
                        yrschnames = []
                        uniqueint=0
                        """
                        for i,y in enumerate(yrarr):
                            #these had to be removed because dates cannot be strings
                            #bd.val = y[1]
                            #ed.val = y[2]
                            yrsch = gbx.YearSchedule()
                            yrs.YearSchedule[i] = yrsch
                            schednm = scheduleName.replace(" ","_")+str(uniqueint)
                            if schednm in yrschnames:
                                uniqueint=uniqueint+1
                                schednm = scheduleName.replace(" ","_")+str(uniqueint)
                            yrsch.id = schednm
                            yrschnames.append(schednm)
                            bd = gbx.BeginDate()
                            ed = gbx.EndDate()
                            begmatch = re.match(r'(\d+)(-)(\d+)',y[1])
                            if begmatch:
                                provider = CultureInfo.InvariantCulture
                                
                                month = begmatch.group(1)
                                day = begmatch.group(3)
                                yr = "2014"
                                datestring = yr+"-"+month+"-"+day
                                
                                yrsch.BeginDate = DateTime.Parse(datestring)
                                
                            else:
                                month = "12"
                                day = "12"
                                yr = "1900"
                                datestring = yr+"-"+month+"-"+day
                                
                                yrsch.BeginDate = DateTime.Parse(datestring)
                            endmatch = re.match(r'(\d+)(-)(\d+)',y[2])
                            if endmatch:
                               
                                month = endmatch.group(1)
                                day = endmatch.group(3)
                                yr = "2014"
                                datestring = yr+"-"+month+"-"+day
                                
                                yrsch.EndDate = DateTime.Parse(datestring)
                            else:
                                month = "12"
                                day = "12"
                                yr = "1900"
                                datestring = yr+"-"+month+"-"+day
                                
                                yrsch.EndDate = DateTime.Parse(datestring)

                            yrsch.WeekScheduleId = y[0]
                            """
                    #this is the only type of schedule I know
                    elif (m.group(3) == "Daily"):
                        logging.info('Match for monthly schedule found in hb.')
                        wksch = gbx.WeekSchedule()
                        gb.WeekSchedule[ct] = wksch
                        wknm = re.match('(.*)({)(.*)(})',scheduleName)
                        
                        if wknm:
                            logging.info('Found the week name of Honeybee obj.')
                            try:
                                wksch.id = "Week-"+str(wknms.index(wknm.group(3)))
                                wksch.Name = wknm.group(3) 
                            except:
                                wksch.id = "Week-unknown"
                                wksch.Name = wknm.group(3) 
                        dayct = []
                        for layer in range(1, numberOfLayers):
                            nmct = []
                            d = scheduleData[layer][1]
                            sn = scheduleData[layer][0]
                            m = re.match('(.*)(Schedule:)(.*)',d)
                            if m:
                                logging.info('Week schedule information found.')
                                day = str.rstrip(m.group(1)).replace('- ','')
                                if(day=='Monday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Sunday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Tuesday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Wednesday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Thursday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Friday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Saturday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Holiday'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='SummerDesignDay'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='WinterDesignDay'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='CustomDay1'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='CustomDay2'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                                elif(day=='Daily'):
                                    nmct.append(day)
                                    nmct.append(sn)
                                    dayct.append(nmct)
                        logging.info('adding days')
                        
                        days = gbx.BasicSerialization.setDayArray(len(dayct))
                        wksch.Day = days
                        for i, day in enumerate(dayct):
                            day = gbx.Day()
                            #map dayTypeEnums
                            
                            day.dayType = wgb.mapDayTypes(dayct[i][0])
                            day.dayScheduleIdRef = dayct[i][1].replace(' ','_')
                            days[i] = day
                        logging.info('done adding days')
                        
                    elif (m.group(3) == "Interval"):
                        logging.info('daily schedule hb object found')
                        dysch = gbx.DaySchedule()
                        gb.DaySchedule[ct] = dysch
                        dysch.id = scheduleName.replace(" ","_")
                        #dysch.Name = scheduleName
                        startime = 0
                        timecount = 0
                        schv = gbx.BasicSerialization.setScheduleValuesArray(24)
                        dysch.ScheduleValue = schv
                        for layer in range(1, numberOfLayers):
                           
                            d = scheduleData[layer][1]
                            if(d == 'Schedule Type Limits Name'):
                                #assign schedule type
                                mt = re.match('(Temperature)(\d*)',scheduleData[layer][0])
                                if mt:
                                    stype = mt.group(1)
                                else:
                                    stype = scheduleData[layer][0]
                                stype = stype.strip()
                                dysch.type = wgb.assignScheduleTypes(stype)
                                
                            elif (re.match("(Time)(.*)",d)):
                                logging.info('found time in hb object for day schedule')
                                startdate = scheduleData[layer][0]
                                #this works fine for this particular convention
                                val = scheduleData[layer+1][0]
                                t = re.match('(\d+)(:)(\d+)',startdate)
                                if t:
                                    curtime = int(t.group(1))
                                   
                                    timecount = curtime - startime
                                    for i in range(0,timecount):
                                        tim = i+startime
                                        sv = gbx.ScheduleValue()
                                        sv.value = float(val)
                                        schv[tim] = sv
                                    startime = curtime
                                
                        
                    else:
                        logging.warning('Not a yearly, monthly, or daily schedule found.')

                # add the name
                #do not use
                scheduleStr =  scheduleStr  + "  " +  scheduleName + ",   !- name\n"
                
                for layer in range(1, numberOfLayers):
                    if layer < numberOfLayers - 1:
                        scheduleStr =  scheduleStr + "  " + scheduleData[layer][0] + ",   !- " +  scheduleData[layer][1] + "\n"
                    else:
                        scheduleStr =  scheduleStr + "  " + str(scheduleData[layer][0]) + ";   !- " +  scheduleData[layer][1] + "\n\n"
                
                return gb
                #except Exception,e:
                #print e
                #logging.error(sys.exc_info()[0])

    def assignScheduleTypes(self,stype):
        logging.debug('Making schedule type for schedule (Fractional, etc..')
        if (stype == 'Fraction'):
            return gbx.scheduleTypeEnum.Fraction
        elif (stype == 'Percentage'):
            return gbx.scheduleTypeEnum.Fraction
        elif (stype == 'On/Off'):
            return gbx.scheduleTypeEnum.OnOff
        elif (stype == 'Temperature'):
            return gbx.scheduleTypeEnum.Temp
        else:
            logging.warning("Unknown Yearly Schedule Type Limit:"+stype)
            return gbx.scheduleTypeEnum.Fraction
            
    def mapDayTypes(self,dayname):
        logging.debug('mapping day types for weekly schedule based on known day types')
        if dayname == "Monday":
            return gbx.dayTypeEnum.Mon
        elif dayname == "Tuesday":
            return gbx.dayTypeEnum.Tue
        elif dayname == "Wednesday":
            return gbx.dayTypeEnum.Wed
        elif dayname == "Thursday":
            return gbx.dayTypeEnum.Thu
        elif dayname == "Friday":
            return gbx.dayTypeEnum.Fri
        elif dayname == "Saturday":
            return gbx.dayTypeEnum.Sat
        elif dayname == "Sunday":
            return gbx.dayTypeEnum.Sun
        elif dayname == "All":
            return gbx.dayTypeEnum.All
        elif dayname == "Holiday":
            return gbx.dayTypeEnum.Holiday
        elif dayname == "SummerDesignDay":
            return gbx.dayTypeEnum.CoolingDesignDay
        elif dayname == "WinterDesignDay":
            return gbx.dayTypeEnum.HeatingDesignDay
        else:
            logging.warning('Unknown day type enum:'+dayname)
            return gbx.dayTypeEnum.WeekendOrHoliday


    def writegbNode(self):
        logging.debug('Writing gb node.')
        gb = gbx.gbXML()
        #write basic attributes
        gb.temperatureUnit = gbx.temperatureUnitEnum.C
        gb.lengthUnit = gbx.lengthUnitEnum.Meters
        gb.areaUnit = gbx.areaUnitEnum.SquareMeters
        gb.volumeUnit = gbx.volumeUnitEnum.CubicMeters
        gb.useSIUnitsForResults = "false"
        
        gb.version = gbx.versionEnum.FiveOneOne
        logging.info('First node gb written successfully.')
        return gb
    
    def makeSpace(self,zone,totalarea, uniqueSched,rhinolevels):
        
        logging.debug('Making gb spaces from hb zones.')
        space = gbx.Space()
        space.id = "Space_"+zone.name
        space.Name = "Space_"+zone.name
        area = gbx.Area()
        
        floorarea = 0 #zone.getFloorArea()
        if floorarea == 0 :
            floorarea,z = wgb.findZoneFloorArea(zone.surfaces)
            if z in rhinolevels:
                pass
            else:
                rhinolevels.append(z)
        
        totalarea+=floorarea
        area.val = str(floorarea)
        # print area.val
        space.spacearea = area
        logging.info("space area = " + str(space.Area))
        vol = gbx.Volume()
        vol.val = str(zone.getZoneVolume())
        space.spacevol = vol
        logging.info('space volume = ' + str(space.Volume))
        
        
        #add internal loads stuff
        logging.info('Extracting zone internal loads')
        loads =  zone.getCurrentLoads()
        intloads = loads.split('\n')
        #get loads from honeybee
        loadict = {}
        for c,load in enumerate(intloads):
            if c == 0: continue
            m = re.match(r'(.*)(:)(.*)',load)
            if m:
                loadict[m.group(1)] = m.group(3)
        #get schedules from honeybee
        logging.info('Extracting zone schedules')
        scheds = zone.getCurrentSchedules()
        intsched = scheds.split('\n')
        schedict = {}
        for s,sched in enumerate(intsched):
            if s == 0: continue
            f = re.match(r'(.*)(:)(.*)',sched)
            if f:
                schedict[f.group(1)] = f.group(3)
        
        uniqueSched = wgb.makeUniqueSched(schedict)
        #Equipments Load Per Area
        ep = gbx.EquipPowerPerArea()
        ep.unit = gbx.powerPerAreaUnitEnum.WattPerSquareMeter
        ep.epd = str(loadict['EquipmentsLoadPerArea'])
        space.EquipPowerPerArea = ep
        space.epd = float(loadict['EquipmentsLoadPerArea'])
        logging.info('Created Equipment Loads for Space')
        #infiltrationRatePerArea
        
        #lightingDensityPerArea
        lp = gbx.LightPowerPerArea()
        lp.unit = gbx.powerPerAreaUnitEnum.WattPerSquareMeter
        lp.lpd = str(loadict['lightingDensityPerArea'])
        space.LightPowerPerArea = lp
        lp.lpd = loadict['lightingDensityPerArea']
        logging.info('Created Lighting Loads for Space')
        #numOfPeoplePerArea
        pn = gbx.PeopleNumber()
        pn.unit = gbx.peopleNumberUnitEnum.SquareMPerPerson
        pn.valuefield = str(loadict['numOfPeoplePerArea'])
        space.PeopleNumber = pn
        space.peoplenum = float(loadict['numOfPeoplePerArea'])
        logging.info('Created num people for Space')
        #ventilationPerArea
        
        #I still don't have a way to deal with people heat gain
        #I could just keep an internal dictionary and map by name
        space.PeopleHeatGains = gbx.BasicSerialization.makePeopleHeatGainAray(3)
        space.totalpeoplegain = 131.8
        tph = gbx.PeopleHeatGain()
        tph.heatGainType = gbx.peopleHeatGainTypeEnum.Total
        tph.unit = gbx.peopleHeatGainUnitEnum.WattPerPerson
        tph.value = str(space.totalpeoplegain)
        space.PeopleHeatGains[0] = tph
        
        space.senspeoplegain = 73.2
        sph = gbx.PeopleHeatGain()
        sph.heatGainType = gbx.peopleHeatGainTypeEnum.Sensible
        sph.unit = gbx.peopleHeatGainUnitEnum.WattPerPerson
        sph.value = str(space.senspeoplegain)
        space.PeopleHeatGains[1] = sph
        
        space.latpeoplegain = 58.6
        lph = gbx.PeopleHeatGain()
        lph.heatGainType = gbx.peopleHeatGainTypeEnum.Latent
        lph.unit = gbx.peopleHeatGainUnitEnum.WattPerPerson
        lph.value = str(space.latpeoplegain)
        space.PeopleHeatGains[2] = lph
        logging.info('Generic people latent and sens loads have been added to Space')
        
        #schedule Keys:
        #Occupancy Schedule
        
        psched = schedict['occupancySchedule']
        psched=psched.replace('\'','')
        psched=psched.strip()
        space.peopleScheduleIdRef = psched.replace(" ","_")
        if(psched in uniqueSched): logging.info('the schedule is not unique:'+psched)
        else: uniqueSched.append(psched)

        #heatingSetPtSchedule
        #coolingSetPtSchedule
        #lightingSchedule
        lsched = schedict['lightingSchedule']
        lsched = lsched.replace('\'','')
        lsched = lsched.strip()
        space.lightScheduleIdRef = lsched.replace(" ","_")
        if(lsched in uniqueSched): logging.info('the schedule is not unique:'+lsched)
        else: uniqueSched.append(lsched)

        #equipmentSchedule
        esched = schedict['equipmentSchedule']
        esched = esched.replace('\'','')
        esched = esched.strip()
        space.equipmentScheduleIdRef = esched.replace(" ","_")
        if(esched in uniqueSched): logging.info('the schedule is not unique:'+esched)
        else: uniqueSched.append(esched)
        #infiltrationSchedule
        
        
        return space,totalarea,uniqueSched,rhinoLevels
        
    def makeUniqueSched(self,schedict):
        logging.debug('Filtering out only unique schedules so they are not duplicated.')
        uniqueSched = []
        for k,v in schedict.items():
            sched = schedict[k]
            sched=sched.replace('\'','')
            sched=sched.strip()
            if(sched in uniqueSched): logging.info('the schedule is not unique:'+sched)
            else: uniqueSched.append(sched)
        return uniqueSched
        
    
    def writelocNode(self):
        logging.debug('Writing gb location node.')
        loc = gbx.Location()
        
        loc.Name= self.locationName
        loc.Latitude= self.latitude
        loc.Longitude= self.longitude
        
        loc.ZipcodeOrPostalCode = self.zipCode
        logging.info('location node written successfully')
        return loc
        
    #returns one or multiple planar geoms
    def makegbPlanarGeoms(self,coordinatesList, namingMethod, namebase):
        logging.debug('Creating Planar Geometry')
        if namingMethod == 1:
            # these walls are only there as parent surfaces for nonplanar glazing surfaces
            srfNaming = 'count_for_glazing'
        elif type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
            srfNaming = 'no_counting'
        else:
            srfNaming = 'counting'
        
        pglist = []
        for coordscount, coordlist in enumerate(coordinatesList):
            pg = gbx.PlanarGeometry()
            pl = gbx.PolyLoop()
            pg.PolyLoop = pl
            if srfNaming == 'count_for_glazing': 
                name = namebase + '_glzP_' + coordscount
            else:
                name = namebase
            pl.Points = gbx.BasicSerialization.makeCartesianPtArray(len(coordlist))
            for pt, coord in enumerate(coordlist):
                cp = gbx.CartesianPoint()
                cp.Coordinate = gbx.BasicSerialization.makeCoordinatesArray(3)
                cp.Coordinate[0] = '%.6f' % coord.X
                cp.Coordinate[1] = '%.6f' % coord.Y
                cp.Coordinate[2] = '%.6f' % coord.Z
                pl.Points[pt] = cp
            pglist.append(pg)
        
        return pglist,name
        
    #looks through all honeybee surfaces and makes gb Surface Boundaries
    def writeSpaceBoundaries(self, surfaces, space, sharedint,uniquesurfcount,HBsurfaces):
        logging.debug('Writing Space Boundaries')
        #need to keep special track of surface that are interior, only represent once
        sbcount = 0
        sblist = []
        for surface in surfaces:
           
            surface.reEvaluateType()
            if not surface.name in sharedint:
                coordinatesList = surface.coordinates ##extractPoints()
                if not isinstance(coordinatesList[0], list) and not isinstance(coordinatesList[0], tuple):
                    coordinatesList = [coordinatesList]
                #add to list of 'found' interior surfaces the first time
                if surface.BC.lower() == "surface":
                    sharedint.append(surface.BCObject.name)
                    
                #memsafelist = wgb.point3DListtoMemorySafeCoordList(sb,coordinatesList)
                #pg = gbx.BasicSerialization.makegbPlanarGeom(memsafelist)
                #namebase = "su-"+str(uniquesurfcount)
                namebase = "su-"+surface.name
                
                pg,gbsurfname = wgb.makegbPlanarGeoms(coordinatesList,0,namebase)
                
                #for a all surfaces surface
                if isinstance(pg,list) or isinstance(pg,tuple):
                    for pgcount,apg in enumerate(pg):
                        #normal surface
                        if len(coordinatesList) == 1:
                            
                            sb = gbx.SpaceBoundary()
                            sb.surfaceIdRef = gbsurfname
                            sb.PlanarGeometry = apg
                            sblist.append(sb)
                            uniquesurfcount += 1
                            HBsurfaces[sb.surfaceIdRef] = surface
                        #meshed surface
                        else:
                            #tempsurface = copy.deepcopy(surface)
                            
                            sb = gbx.SpaceBoundary()
                            sb.surfaceIdRef = gbsurfname+"_"+str(pgcount)
                            sb.PlanarGeometry = apg
                            sblist.append(sb)
                            uniquesurfcount += 1
                            HBsurfaces[sb.surfaceIdRef] = surface
                            
            else:
                #it is an interior surface that has already been found
                pass
                
        #now add the space boundaries to the array

        #write the space boundaries only for those that are unique
        space.spbound = gbx.BasicSerialization.makeSBArray(len(sblist))
        for sbcount,createdsb in enumerate(sblist):
            space.spbound[sbcount] = createdsb
        logging.info('Space boundaries created.')
        return space,sharedint, uniquesurfcount,HBsurfaces

    def writeSurfaces(self,cmp,hbsurfacetypes,uniquesurfcount,usedconstructions,usedopening,tsc):
        logging.debug('Writing gb surfaces.')
        cmp.Surface = gbx.BasicSerialization.defSurfaceArray(tsc)
        print  'writing surfaces'
      
        gbxmlSpaces = cmp.Buildings[0].Spaces
        openingct = 0
        surfnum = 0
        for space in gbxmlSpaces:
            sbcount = 0
            
            while (sbcount < len(space.spbound)):
                logging.info('Getting honeybee surface information to translate it.')
                hbsurface = hbsurfacetypes[space.spbound[sbcount].surfaceIdRef]
                coordinatesList = hbsurface.coordinates ##.extractPoints()
                #do the work to map the coordinatesList appropriately, 
                #this will change as the honeybee object changes
                #for now, here is the test for an unmeshed surface
                
                #unmeshed surface
                #make a new surface
                logging.info("This honeybee surface is unmeshed.")
                surface = gbx.Surface()
                surface.id = space.spbound[sbcount].surfaceIdRef
                #by convention, added by MR Jan 20 2014
                LLeft = coordinatesList[0]
                memsafelist = wgb.point3DListtoMemorySafeCoordList([coordinatesList])
                normal = v.Vector.GetMemRHR(memsafelist[0])
                #get tilt
                tilt=gbx.prod.FindTilt(normal)
                cp = gbx.CartesianPoint()
                
                #this is hardcoded value and should be changed, it can cause bugs
                if tilt <= 30:
                    #roof LL is unique by gbXML convention
                    logging.debug("Found roof with tilt:"+str(tilt))
                    llr = gbx.BasicSerialization.GetLLForRoof(memsafelist[0])
                    cp = llr.cp
                   
                elif tilt == 180:
                    #floor LL is unique by gbXML convention
                    logging.debug("Found floor with tilt:"+str(tilt))
                    llf = gbx.BasicSerialization.GetLLForFloor(memsafelist[0])
                    cp = llf.cp
                else:
                    logging.debug("Assumed a wall with tilt:"+str(tilt))
                    LLeft = coordinatesList[0]
                    
                    cp = wgb.makegbCartesianPt(LLeft)
                    
                normarr = []
                normarr.append(normal.X)
                normarr.append(normal.Y)
                normarr.append(normal.Z)
                
                #get the azimuth and tilt and assign the construction yourself
                #this is a hack to get around honeybee's nested surface
                surface.surfaceType = wgb.mapSurfaceTypes(hbsurface.type)
                surface.constructionIdRef = "OpenStudio_"+hbsurface.construction.replace(" ","_")
                usedconstructions.append(hbsurface.construction)
                surface.Name = hbsurface.name
                
                #make adjacent space identifications, which depend on surf type
                parentname = hbsurface.parent.name
                try: 
                    neighborparentname = hbsurface.BCObject.parent.name
                    
                    adjSpaces = gbx.BasicSerialization.defAdjSpID(2)
                    adjSp1 = gbx.AdjacentSpaceId()
                    adjSp1.spaceIdRef = "Space_"+parentname
                    adjSpaces[0] = adjSp1
                    adjSp2 = gbx.AdjacentSpaceId()
                    adjSp2.spaceIdRef = "Space_"+neighborparentname
                    adjSpaces[1] = adjSp2
                    surface.AdjacentSpaceId = adjSpaces
                    if hbsurface.type == 0:
                        surface.surfaceType = gbx.surfaceTypeEnum.InteriorWall
                except:
                    neighborparentname = str.Empty
                    adjSpaces = gbx.BasicSerialization.defAdjSpID(1)
                    adjSp = gbx.AdjacentSpaceId()
                    adjSp.spaceIdRef = "Space_"+parentname
                    adjSpaces[0] = adjSp
                    surface.AdjacentSpaceId = adjSpaces
                    
                rg = gbx.RectangularGeometry()
                #get azimuth
                #need to add something for CADModel Azimuth eventually
                az = gbx.prod.FindAzimuth(normal)
                rg.Azimuth = '%.6f' % az
                #set the rg to the found cp
                rg.CartesianPoint = cp
                rg.Tilt = '%.6f' % tilt
                #add code to check for normal quads before making this simplification
                #get width
                area = v.Vector.GetAreaofMemSafeCoords(memsafelist[0])
                ht=0
                width=0
                try:
                    sqrnt,height,wid = wgb.isItSquare(memsafelist[0])
                    if (sqrnt):
                        ht = min(height,wid)
                        width= max(height,wid)
                        
                    else:
                        ht = 10
                        width = area/ht
                except:
                    ht = 10
                    width = area/ht
                rg.Width = '%.6f' % width
                #get height
                rg.Height = '%.6f' % ht
                surface.RectangularGeometry = rg
                pg = gbx.BasicSerialization.makegbPlanarGeom(memsafelist)
                surface.PlanarGeometry = pg
                if hbsurface.hasChild:
                    logging.debug("Making glazing surfaces.")
                    hbwindows = hbsurface.childSrfs    
                    
                    gbopenings,usedopening = wgb.makegbOpening(hbwindows,hbsurface.name, usedopening,openingct)
                    openingct+1
                    surface.Opening = gbopenings
                    
                CAD = gbx.CADObjectId()
                #this should only occur if the surface is totaly new (bad idea)
                CAD.id = str(uuid.uuid4())
                surface.CADObjectId = CAD

                cmp.Surface[surfnum] = surface
                sbcount += 1
                surfnum += 1
        #write shading devices
        
        cmp.Surface = wgb.makeShdSurface(HBContext,cmp.Surface, surfnum)
        logging.info('Making surfaces completed.')
        return cmp,usedconstructions,usedopening
        
    def makeShdSurface(self, shades, surfaceList,index):
        print 'making shades', shades
        logging.debug('Making shading surfaces.')
        #this has to be here because I may have to make both meshed and unmeshed shadings
        totalcount = 0+index
        for surfnum,shade in enumerate(shades):
            surfnum = surfnum+index
            #coordinateList contains all the shade points for all shades
            coordinatesList = shade.extractPoints() # I haven't applied reEvaluate zones to shading surfaces
            #print coordinatesList
            try:
                len(coordinatesList[0][0])
                print 'meshed surface'
                for subcount,ss in enumerate(coordinatesList):
                    surface = gbx.Surface()
                    shadeid = "su-"+str(surfnum)+"-"+str(subcount)
                    
                    surface.id = shadeid
                    memsafelist = wgb.point3DListtoMemorySafeCoordList([coordinatesList[subcount]])
                    
                    normal = v.Vector.GetMemRHR(memsafelist[0])
                    
                    LLeft = memsafelist[0][0]
                    
                    cp = gbx.CartesianPoint()
                    cp = wgb.makegbCartesianPt(LLeft)
                    normarr = []
                    normarr.append(normal.X)
                    normarr.append(normal.Y)
                    normarr.append(normal.Z)
                    #get the azimuth and tilt and assign the construction yourself
                    #this is a hack to get around honeybee's nested surface
                    surface.surfaceType = wgb.mapSurfaceTypes(shade.type)
                    surface.Name = shade.name
                    rg = gbx.RectangularGeometry()
                    #get azimuth
                    #need to add something for CADModel Azimuth eventually
                    az = gbx.prod.FindAzimuth(normal)
                    rg.Azimuth = '%.6f' % az
                    #get tilt
                    tilt=gbx.prod.FindTilt(normal)
                    #set the rg to the found cp
                    rg.CartesianPoint = cp
                    rg.Tilt = '%.6f' % tilt
                    #add code to check for normal quads before making this simplification
                    #get width
                    area = v.Vector.GetAreaofMemSafeCoords(memsafelist[0])
                    sqrnt,height,wid = wgb.isItSquare(memsafelist[0])
                    if (sqrnt):
                        ht = min(height,wid)
                        width= max(height,wid)
                    else:
                        ht = 10
                        width = area/ht
                    rg.Width = '%.6f' % width
                    #get height
                    rg.Height = '%.6f' % ht
                    surface.RectangularGeometry = rg
                    pg = gbx.BasicSerialization.makegbPlanarGeom(memsafelist)
                    surface.PlanarGeometry = pg
                    CAD = gbx.CADObjectId()
                    #this should only occur if the surface is totaly new (bad idea)
                    CAD.id = str(uuid.uuid4())
                    surface.CADObjectId = CAD
                    surfaceList[totalcount] = surface
                    totalcount+=1
                    
            except:
                surface = gbx.Surface()
                surface.id = "su-"+str(surfnum)
                #by convention, added by MR Jan 20 2014
                LLeft = coordinatesList[0]
                
                memsafelist = wgb.point3DListtoMemorySafeCoordList([coordinatesList])
                normal = v.Vector.GetMemRHR(memsafelist[0])
                #get tilt
                tilt=gbx.prod.FindTilt(normal)
                #assign lower left, no special intelligence
                cp = gbx.CartesianPoint()
                cp = wgb.makegbCartesianPt(LLeft)
                normarr = []
                normarr.append(normal.X)
                normarr.append(normal.Y)
                normarr.append(normal.Z)
                #get the azimuth and tilt and assign the construction yourself
                #this is a hack to get around honeybee's nested surface
                surface.surfaceType = wgb.mapSurfaceTypes(shade.type)
                surface.Name = shade.name
                rg = gbx.RectangularGeometry()
                #get azimuth
                #need to add something for CADModel Azimuth eventually
                az = gbx.prod.FindAzimuth(normal)
                rg.Azimuth = '%.6f' % az
                #set the rg to the found cp
                rg.CartesianPoint = cp
                rg.Tilt = '%.6f' % tilt
                #get width
                area = v.Vector.GetAreaofMemSafeCoords(memsafelist[0])
                sqrnt,height,wid = wgb.isItSquare(memsafelist[0])
                if (sqrnt):
                    ht = min(height,wid)
                    width= max(height,wid)
                else:
                    ht = 10
                    width = area/ht
                rg.Width = '%.6f' % width
                #get height
                rg.Height = '%.6f' % ht
                surface.RectangularGeometry = rg
                pg = gbx.BasicSerialization.makegbPlanarGeom(memsafelist)
                surface.PlanarGeometry = pg
                CAD = gbx.CADObjectId()
                #this should only occur if the surface is totaly new (bad idea)
                CAD.id = str(uuid.uuid4())
                surface.CADObjectId = CAD
                surfaceList[totalcount] = surface
                totalcount+=1
                
        return surfaceList


    def makegbOpening(self,hbwindows,parentsurfacename,usedopening,openingct):
        logging.debug('Making gb openings from hb openings.')
        gbopenings = gbx.BasicSerialization.defOpeningsArr(len(hbwindows))
        defaz = 0
        deftilt = 0
        defht = 10
        defllx = 0
        deflly = 0
        defllz = 0
        for count,window in enumerate(hbwindows):
            gbopen = gbx.Opening() 
            #do all naming 
            gbopen.id = "OpenStudio_"+window.name.replace(' ','_')+str(openingct)
            usedopening[window.name] = window.construction
          
            opCoordsList = window.coordinates ##.extractPoints()
            windowpts = list([opCoordsList])
            wmemsafelist = wgb.point3DListtoMemorySafeCoordList(windowpts)
            parent = window.parent
            surfCoordsList = parent.coordinates ##extractPoints()
            surfpts = list([surfCoordsList])
            smemsafelist = wgb.point3DListtoMemorySafeCoordList(surfpts)
            try:
                logging.info('getting lower left corner of window.')
                cp = gbx.BasicSerialization.GetLLForOpening(smemsafelist[0],wmemsafelist[0])
            except:
                logging.error('problem when getting lower left corner.'+ sys.exc_info()[0])
            
            parentsurfacename = parent.name
            #we will always have fixed windows until code can accomodate
            gbopen.openingType = gbx.openingTypeEnum.FixedWindow
            gbopen.Name = window.name  ##parentsurfacename+" Window-"+str(count)

            wrg = gbx.RectangularGeometry()
            try:
                wrg.CartesianPoint = cp.cp
            except:
                logging.error("problem making window Rectangular Geometry."+sys.exc_info()[0])
                
            wrg.Azimuth = '%.6f' % defaz
            #we think the default tilt will always be this way
            wrg.Tilt = '%.6f' % deftilt
            warea = window.getTotalArea()
            logging.info("Window area is: " + str(warea))

            sqrnt,height,wid = wgb.isItSquare(wmemsafelist[0])
            if (sqrnt):
                ht = min(height,wid)
                width= max(height,wid)
            else:
                ht = 10
                width = warea/ht
            wrg.Height = '%.6f' % ht
            wrg.Width = '%.6f' % width
            
            gbopen.rg = wrg
            #define planar geometry
            wpg = gbx.BasicSerialization.makegbPlanarGeom(wmemsafelist)                     
            gbopen.pg = wpg
            #add the finished product to the array
            gbopenings[count] = gbopen
        logging.info('Openings for gb successfully made.')
        return gbopenings,usedopening

    def makegbXMLevels(self,rhinolevels, bldg):
        print ('Making gbxml Levels.')
        print rhinolevels
        bldlevels = gbx.BasicSerialization.setLevelsArray(len(rhinolevels))
        bldg.bldgStories = bldlevels
        for lcount, level in enumerate(rhinolevels):
            storey = gbx.BuildingStorey()
            storey.id = 'bldg-story-'+str(lcount+1)
            storey.Name = 'Level-'+str(lcount+1)
            storey.Level = '%.6f' % level
            coordinates = wgb.makeLevelCoords(level)
            #make planar geometry
            pg = gbx.PlanarGeometry()
            pl = gbx.PolyLoop()
            pg.PolyLoop = pl
            pl.Points = gbx.BasicSerialization.makeCartesianPtArray(len(coordinates))
            
            for count,pt in enumerate(coordinates):
                cp = gbx.CartesianPoint()
                cp.Coordinate = gbx.BasicSerialization.makeCoordinatesArray(3)
                cp.Coordinate[0]='%.6f' % pt[0]
                cp.Coordinate[1]='%.6f' % pt[1]
                cp.Coordinate[2]='%.6f' % pt[2]
                #for the list holding all surface polyloops, 1 point = cp
                pl.Points[count] = cp
            storey.PlanarGeo = pg
            bldg.bldgStories[lcount] = storey
        logging.info('gbXML Levels made successfully.')
        return bldg

    def makegbCartesianPt(self,pt):
        logging.debug('Making a gb cartesian point object.')
        cp = gbx.CartesianPoint()
        cp.Coordinate = gbx.BasicSerialization.makeCoordinatesArray(3)
        try:
            cp.Coordinate[0]='%.6f' % pt.X
            cp.Coordinate[1]='%.6f' % pt.Y
            cp.Coordinate[2]='%.6f' % pt.Z
        except:
            logging.error('Error in making a cartesian point.')
        logging.info('Cartesian point made successfully.')
        return cp

    def flattenThreeDVect(self,threeDV):
        #this function always assumes the vector is derived from a special
        #relationship between the surface and the window
        twoDV = threeDV
        return twoDV
    
    def mapSurfaceTypes(self, hbsurfacetype):
        logging.debug('Mapping HB surface types to gb Surface Types.')
        #this is a hack because there are no exposed floors
        if hbsurfacetype == 2.75: 
            return gbx.surfaceTypeEnum.SlabOnGrade
        HBtoGBsurfacemap={0:gbx.surfaceTypeEnum.ExteriorWall,
                            0.5:gbx.surfaceTypeEnum.UndergroundWall,
                            1:gbx.surfaceTypeEnum.Roof,
                            1.5:gbx.surfaceTypeEnum.UndergroundCeiling,
                            2:gbx.surfaceTypeEnum.InteriorFloor,
                            2.25: gbx.surfaceTypeEnum.UndergroundSlab,
                            2.5: gbx.surfaceTypeEnum.SlabOnGrade,
                            2.57: gbx.surfaceTypeEnum.RaisedFloor,
                            3:gbx.surfaceTypeEnum.Ceiling,
                            4:gbx.surfaceTypeEnum.Air,
                            #5 is reserved for openings
                            6:gbx.surfaceTypeEnum.Shade
                            }
        try:
            HBtoGBsurfacemap[hbsurfacetype]
            return HBtoGBsurfacemap[hbsurfacetype]
        except:
            logging.error('Could not map HB surface type to gb surface type.')
    
    def writeConstructions(self, uniqueopens, uniqueconst):
        logging.debug('Writing gb Constructions.')
        constarr = gbx.BasicSerialization.defConstructionArray(len(uniqueconst))
        
        #write layers
        #a counter to keep track of unique layers
        uniquelayercount = 0
        uniquelayers = {}
        for constcount,const in enumerate(uniqueconst):
            const = const.upper()
            #write the construction
            construction = gbx.Construction()
            construction.id = 'OpenStudio_'+const.replace(' ','_')
            construction.Name = 'gbXMLConstruction_'+str(constcount)
            #there is no honeybee description for the construction
            construction.Description = "From Rhino/Honeybee."

            #add layers
            gblayerids = gbx.BasicSerialization.defLayerIdArray(len(HBConstructions[const])-1)
            
            #get unique materials
            
            layercount=1
            #this can be updated
            while(layercount< len(HBConstructions[const])):
                #don't add layers if there the construction is a window
                #don't change name if the layer already has "HBlayer in it)
                matchObj = re.match( r'(HBlayer_)(.*)', HBConstructions[const][layercount][1])
                if not matchObj:
                    layerid = 'HBlayer_'+str(constcount)+'_'+(HBConstructions[const][layercount][1]).replace(' ','_')
                    HBLayer = HBConstructions[const][layercount][0]
                
                if(uniquelayers.has_key(HBLayer)):
                    layer = gbx.LayerId();
                    layer.layerIdRef = uniquelayers[HBLayer].replace(' ','_')
                    gblayerids[layercount-1] = layer
                    layercount+=1
                else:
                    
                    layer = gbx.LayerId();
                    layer.layerIdRef = layerid
                    gblayerids[layercount-1] = layer
                    uniquelayers[HBLayer]= layerid
                    layercount+=1
                    uniquelayercount+=1
            construction.LayerId = gblayerids
            constarr[constcount] = construction
        gb.Constructions = constarr
        
        gbLayers = gbx.BasicSerialization.defLayerArray(len(uniquelayers))
        uniquematerials = {}
        
        for layercount,layer in enumerate(uniquelayers):
            gbLayer = gbx.Layer()
            gbLayer.id = uniquelayers[layer]
            
            materialIdArray = gbx.BasicSerialization.defMaterialIdArray(1)
            materialId = gbx.MaterialId()
            id = "HBmat_"+uniquelayers[layer].replace(' ','_')
            
            materialId.materialIdRef = id
            materialId.percentOfLayer = 100.0
            materialIdArray[0] = materialId
            if(id in uniquematerials):
                continue
            else:
                uniquematerials[id] = layer
            gbLayer.MaterialId = materialIdArray
            gbLayers[layercount] = gbLayer
        gb.Layers = gbLayers
        #make gbmaterials
        gbmaterialsarray = gbx.BasicSerialization.defMaterialsArray(len(uniquematerials))
        for matcount,materialid in enumerate(uniquematerials.keys()):
            materialid = materialid
            thisisglazing = False
            materialData = None
            materialName = uniquematerials[materialid]
            materialName= materialName.upper()
            if materialName in sc.sticky ["honeybee_windowMaterialLib"].keys():
                logging.info("Found some glass!!")
                thisisglazing = True
                materialData = sc.sticky ["honeybee_windowMaterialLib"]
                logging.info(materialData[materialName])
            elif materialName in sc.sticky ["honeybee_materialLib"].keys():
                materialData = sc.sticky ["honeybee_materialLib"]
            try:
                materialData[uniquematerials[materialid].upper()]
                if(uniquematerials.has_key(materialid)):
                    material = uniquematerials[materialid].upper()
                else:
                    logging.error('Could not find the material:'+str(material))
                gbmater = gbx.Material()
                gbmater.id = materialid
                gbmater.Name = material
                gbmater.Description = "A Honeybee material."
                
                #catch different types of HB materials
                if(thisisglazing):
                    if(materialData[material][0] == 'Material:AirGap'):
                        rval = gbx.RValue()
                        rval.unit =  gbx.resistanceUnitEnum.SquareMeterKPerW
                        rval.value = float(materialData[material][1][0])
                        gbmater.RValue = rval
                        
                    else:
                        #air spaces
                        pass
                elif(materialData[material][0] == 'Material:AirGap'):
                    rval = gbx.RValue()
                    rval.unit =  gbx.resistanceUnitEnum.SquareMeterKPerW
                    rval.value = float(materialData[material][1][0])
                    gbmater.RValue = rval
                    
                else:
                    thickness = gbx.Thickness()
                    thickness.unit=gbx.lengthUnitEnum.Meters
                    thickness.value = float(materialData[material][2][0])
                    
                    gbmater.Thickness = thickness
                    conductivity = gbx.Conductivity()
                    conductivity.unit = gbx.conductivityUnitEnum.WPerMeterK
                    conductivity.value = float(materialData[material][3][0])
                    gbmater.Conductivity = conductivity
                    density = gbx.Density()
                    density.unit = gbx.densityUnitEnum.KgPerCubicM
                    density.value = float(materialData[material][4][0])
                    gbmater.Density = density
                    sh = gbx.SpecificHeat()
                    sh.unit = gbx.specificHeatEnum.JPerKgK
                    sh.value = float(materialData[material][5][0])
                    gbmater.SpecificHeat = sh
                
                
                gbmaterialsarray[matcount] = gbmater
            except:
                print sys.exc_info()[0]
                logging.error("Cannot find!!!!!!!!!!!!!!!!!!!!!:" + uniquematerials[materialid])
        gb.Materials = gbmaterialsarray
        #glazing
        #for tracking the unique materials for WindowTypes
        uniqueglazing = []
        uniquegaps = []
        gbWindowType = gbx.BasicSerialization.defWindowTypeArray(len(uniqueopens))
        for opencount, opening in enumerate(uniqueopens):
            opening = opening.upper()
            gbopening = gbx.WindowType()
            gbWindowType[opencount] = gbopening
            gbopening.id = "OpenStudio_"+opening.replace(' ','_')
            gbopening.Name = opening
            gbopening.Description = "A honeybee opening."
            
            #setup the layer counting
            glazecount = 0
            gapcount = 0
            totlayercount = 1
            gbWindowType[opencount] = gbopening
            windowcat = "none"
            windowlayerct = len(HBConstructions[opening])-1
            if(windowlayerct == 1):
                windowcat = "single"
                logging.info("window is "+windowcat )
                glazecount = 1
            elif(windowlayerct == 3):
                windowcat = "double"
                logging.info("window is "+windowcat) 
                glazecount = 2
                gapcount = 1
            elif(windowlayerct == 5):
                windowcat = "triple"
                logging.info("window is "+windowcat)
                glazecount = 3
                gapcount = 2
            elif(windowlayerct == 7):
                windowcat = "quad"
                logging.info("window is "+windowcat) 
                glazecount = 4
                gapcount = 3
            windowglaze = gbx.BasicSerialization.defGlazeArray(glazecount)
            #assign to the opening instance
            gbopening.Glaze = windowglaze
            if(gapcount > 0):
                windowgap = gbx.BasicSerialization.defGapArray(gapcount)
                #assign to the opening instance
                gbopening.Gap = windowgap
            #set up the window layers
            glzlayerct = 0
            gaplayerct = 0
          
            while(totlayercount < len(HBConstructions[opening])):
                
                #glazing or air material?
                #review a very simple property, the length of dictionary
                #air gap dictionaries are only of length three
                HBGlazeLayerName = HBConstructions[opening][totlayercount][0].upper()
                
                matprops = HBGlazeMat[HBGlazeLayerName].values()
                
                if matprops[0] == 'WindowMaterial:SimpleGlazingSystem':
                    logging.info('this is a simple glazing system')
                    uval = gbx.UValue()
                    uval.unit = gbx.uValueUnitEnum.WPerSquareMeterK
                    uval.value = float(matprops[1][0])
                    gbopening.UValue = uval
                    
                    shgc = gbx.SolarHeatGainCoeff()
                    shgc.unit = gbx.unitlessUnitEnum.Fraction
                    shgc.value = float(matprops[2][0])
                    shgcarr = gbx.BasicSerialization.defSolarHeatGainArray(1)
                    shgcarr[0] = shgc
                    gbopening.SolarHeatGainCoeff = shgcarr
                    
                    vt = gbx.Transmittance()
                    vt.unit = gbx.unitlessUnitEnum.Fraction
                    vt.type = gbx.radiationWavelengthTypeEnum.Visible
                    vt.value = float(matprops[3][0])
                    gbopening.Transmittance = vt
                    break
                    

                if HBGlazeLayerName in sc.sticky ["honeybee_windowMaterialLib"].keys():
                    logging.info("successfully located layer in honeybee sticky")
                    
                    if(len(HBGlazeMat[HBGlazeLayerName]) > 3):
                        #this is as per the current honeybee approach
                        glaze = HBConstructions[opening][totlayercount][0]
                        totlayercount = totlayercount + 1
                        #add the glazing layer to the WindowType
                        #this is a predefined script for honeybee
                        glazetransarr = gbx.BasicSerialization.defTransmittanceArray(3);
                        glazereflarr = gbx.BasicSerialization.defReflectanceArray(4);
                        glazeemarr = gbx.BasicSerialization.defEmmitanceArray(2);
                        gbglaze = gbx.Glaze()
                        gbglaze.id = "honeybeeglaze_"+str(len(uniqueglazing))
                        
                        tk = gbx.Thickness()
                        gbglaze.Thickness = tk
                        #this call is based on Honeybee's inherent structure
                        tk.unit = gbx.lengthUnitEnum.Meters
                        tk.value = float(matprops[3][0])
                        
                        conduct = gbx.Conductivity()
                        gbglaze.Conductivity = conduct
                        conduct.unit = gbx.conductivityUnitEnum.WPerMeterK
                        conduct.value = float(matprops[13][0])
                        #assign to the glaze array
                        windowglaze[glzlayerct] = gbglaze
                        unit = gbx.unitlessUnitEnum.Fraction
                        vt = gbx.Transmittance()
                        glazetransarr[0] = vt
                        vt.type = gbx.radiationWavelengthTypeEnum.Visible
                        vt.unit = unit
                        vt.value = float(matprops[7][0])
                        
                        st = gbx.Transmittance()
                        glazetransarr[1] = st
                        st.type = gbx.radiationWavelengthTypeEnum.Solar
                        st.unit = unit
                        st.value = float(matprops[4][0])
                        
                        irt = gbx.Transmittance()
                        glazetransarr[2] = irt
                        irt.type = gbx.radiationWavelengthTypeEnum.IR
                        irt.unit = unit
                        irt.value = float(matprops[10][0])
                        
                        gbglaze.Transmittance = glazetransarr
                        fvr = gbx.Reflectance()
                        fvr.unit = unit
                        fvr.type = gbx.reflectanceTypeEnum.ExtVisible
                        fvr.value = float(matprops[8][0])
                        glazereflarr[0] = fvr
                        bvr = gbx.Reflectance()
                        bvr.unit = unit
                        bvr.type = gbx.reflectanceTypeEnum.IntVisible
                        bvr.value = float(matprops[9][0])
                        glazereflarr[1] = bvr
                        fsr = gbx.Reflectance()
                        fsr.unit = unit
                        fsr.type = gbx.reflectanceTypeEnum.ExtSolar
                        fsr.value = float(matprops[6][0])
                        glazereflarr[2] = fsr
                        bsr = gbx.Reflectance()
                        bsr.unit = unit
                        bsr.type = gbx.reflectanceTypeEnum.IntSolar
                        bsr.value = float(matprops[7][0])
                        glazereflarr[3] = bsr
                        gbglaze.Reflectance = glazereflarr
                        logging.info("glazing layer defined for opening type,",HBGlazeLayerName)
                        #push to the unique bin if it is unique, else continue
                        if(glaze in uniqueglazing):
                            glzlayerct+=1
                        else:
                            uniqueglazing.append(glaze)
                            glzlayerct+=1
                    else:
                        #this is a gap
                        
                        gap = HBConstructions[opening][totlayercount][0]
                        totlayercount = totlayercount + 1
                        #go ahead and define the gap for this windowtype
                        gbgap = gbx.Gap()
                        gbgap.id = "honeybeegap_"+str(len(uniquegaps))
                        try:
                            gbgap.gas = gbx.gasTypeEnum.Air
                        except Exception, e:
                            print `e`
                            
                        tk = gbx.Thickness()
                        gbgap.Thickness = tk
                        #this call is based on Honeybee's inherent structure
                        tk.unit = gbx.lengthUnitEnum.Meters
                        tk.value = float(matprops[2][0])
                        windowgap[gaplayerct] = gbgap
                        if(gap in uniquegaps):
                            gaplayerct+=1
                        else:
                            uniquegaps.append(gap)
                            gaplayerct+=1
                            
        gb.WindowTypes = gbWindowType
    


if gbXMLIsReady and _location and _writegbXML and _workingDir:
        #try:
        #instantiate gbXML object
        wgb = WritegbXML(_location, zipCode_)
        logging.debug('calling the honeybee hive.')
        if (sc.sticky["honeybee_release"] and sc.sticky.has_key("honeybee_materialLib")):
            hb_hive = sc.sticky["honeybee_Hive"]()
            HBConstructions = sc.sticky ["honeybee_constructionLib"]
            HBMaterials = sc.sticky["honeybee_materialLib"]   
            HBGlazeMat = sc.sticky["honeybee_windowMaterialLib"]
            hb_reEvaluateHBZones = sc.sticky["honeybee_reEvaluateHBZones"]
            
            
            HBZones = hb_hive.callFromHoneybeeHive(_HBZones)
            # reEvaluate zones
            reEvaluate = hb_reEvaluateHBZones(HBZones, meshSettings_)
            reEvaluate.evaluateZones()
            if HBContext_ and HBContext_[0]!=None:
                # call the objects from the lib
                HBContext = hb_hive.callFromHoneybeeHive(HBContext_)
            else:
                HBContext = []
                

        #a list to store shared interior surfaces
        sharedint = []
        #variable to store unique surface count
        uniquesurfcount = 0
        #store the surface objects as they are declared by honeybee
        HBsurfaces = {}
        
        # initiate gbXML parent node
        gb = wgb.writegbNode()
        #create campus
        id = "cmps-1"
        cmp = gbx.BasicSerialization.CreateCampus(id)
        
        #create a temporary location, this could be better, maybe geolocation?
        loc = wgb.writelocNode()
        cmp.Location = loc
        cmp.id = id
        gb.Campus = cmp
        #currently we can handle only one building, getting the area is involved...
        bldareas = [-999] #-999 says not predefined
        bldtype = [gbx.buildingTypeEnum.Office]
        buildnum = len(bldareas)
        cmp.Buildings = gbx.BasicSerialization.SetBldArray(buildnum)
        for bcount, building in enumerate(bldareas):
            bldname = "bldg-"+str(bcount)
            t = bldtype[bcount]
            cmp.Buildings[bcount] = gbx.BasicSerialization.MakeBuilding(building,bldname,t)
            #make the levels (optional - we skip it)
            cmp.Buildings[bcount].Spaces = gbx.prod.makeSpaceArray(len(HBZones))
            #this is the total area of all spaces, to be applied elsewhere
            totalarea = 0
            uniqueSched = []
            rhinoLevels = []
            for zonecounter, zone in enumerate(HBZones):
                
                if zone.hasNonPlanarSrf or zone.hasInternalEdge:
                    zone.prepareNonPlanarZone(1)
                
                # create a space, calculate total area, find all unique schedules
                space,totalarea,uniqueSched,rhinoLevels = wgb.makeSpace(zone,totalarea, uniqueSched,rhinoLevels)
                
                space = wgb.writeShellGeo(zone.surfaces, space)
                cid = gbx.CADObjectId()
                cid.id = str(uuid.uuid4())
                space.cadid = cid
                space,sharedint,uniquesurfcount,HBsurfaces = wgb.writeSpaceBoundaries(zone.surfaces, space, sharedint,uniquesurfcount,HBsurfaces)
                #gbspaces.append(space)
                cmp.Buildings[bcount].Spaces[zonecounter] = space
            cmp.Buildings[bcount].Area = totalarea
            cmp.Buildings[bcount] = wgb.makegbXMLevels(rhinoLevels,cmp.Buildings[bcount])
            

        #createsurface elements, keep track of all constructions and openings
        usedconstructions = []
        usedopening = {}
        #whether surfaces are meshed or not has already been determined
        
        shadecount = wgb.getShadeCount(HBContext)
        print "number of shades", shadecount
        totsurfct = len(HBsurfaces) + shadecount
        cmp,usedconstructions,usedopening = wgb.writeSurfaces(cmp,HBsurfaces,uniquesurfcount,usedconstructions,usedopening, totsurfct)

        #write only unique constructions and openings
        uniqueconst = set(usedconstructions)
        uniqueopens = set(usedopening.values())
        wgb.writeConstructions(uniqueopens,uniqueconst)
        
        #write only the unique schedules
        hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
        
        #make schedules
        #schedule count
        schct = 0
        #week schedule count
        wschct = 0
        #daily schedule count
        dschct = 0
        for schedule in uniqueSched:
            schedule = schedule.strip('.')
            scheduleValues, comments = hb_EPScheduleAUX.getScheduleDataByName(schedule, ghenv.Component)
            if not scheduleValues:
                logging.debug('There are no schedules in the honeybee hive.')
                continue
                
            m = re.match('(.*)(:)(.*)', scheduleValues[0])
            if m:
                
                if m.group(3) == "Year":
                    schct += 1
                elif m.group(3) == "Daily":
                    wschct += 1
                elif m.group(3) == "Interval":
                    dschct += 1
                    
            # collect all the schedule items inside the schedule
            if scheduleValues[0] == "Schedule:Week:Daily":
                for value in scheduleValues[1:]:
                    if value not in uniqueSched:
                        uniqueSched.append(value)
            # add schedules which are referenced inside other schedules to the list
            for value in scheduleValues[1:]:
                if value.startswith("Schedule:") and value not in uniqueSched:
                    uniqueSched.append(value)
        scharr = gbx.BasicSerialization.setScheduleArray(schct)
        gb.Schedule = scharr
        
        wkarr = gbx.BasicSerialization.setWeekScheduleArray(wschct)
        gb.WeekSchedule = wkarr
        dayarr = gbx.BasicSerialization.setDayScheduleArray(dschct)
        gb.DaySchedule = dayarr
        sct = 0
        wct = 0
        dct = 0
        wknms = []
        
        for schedule in uniqueSched:
            # print schedule
            schedule = schedule.strip('.')
            
            scheduleValues, comments = hb_EPScheduleAUX.getScheduleDataByName(schedule, ghenv.Component)
            if scheduleValues!=None:
                m = re.match('(.*)(:)(.*)', scheduleValues[0])
                if m:
                    
                    if m.group(3) == "Year":
                        gb = wgb.EPSCHStr(gb, schedule, sct,wknms)
                        sct += 1
                    elif m.group(3) == "Daily":
                        gb = wgb.EPSCHStr(gb, schedule, wct,wknms)
                        wct += 1
                        
                    elif m.group(3) == "Interval":
                        gb = wgb.EPSCHStr(gb, schedule, dct,wknms)
                        dct += 1

        #except NameError, e:
        #    logging.error(sys.exc_info()[0])
        #    print `e`
        #close the campus
        

        try:
            logging.info('Creating the gbxml file')
            filepath= os.path.join(_workingDir, '{}.xml'.format(fileName))
            logging.info('gbxml file created.')
            print 'gbXML File Successfully Written'
            print 'Latest updates fixed Width and Height error at surface and openings'
        except:
            logging.info('there likely is not a filename.  using default.')
            filepath=_workingDir + "test.xml"
        res = gbx.BasicSerialization.CreateXML(filepath,gb)
        resultFileAddress = filepath
