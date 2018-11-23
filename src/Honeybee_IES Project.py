#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2015-2017, Sarith Subramaniam <sarith@sarith.in> 
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
This component is meant for summarizing the details of all the luminaires used in a simulation.

    Args:
        _elecLightingData: Connect the elecLightingData output of the Honeybee_IES Luminaire component here.
        outputsToExcel_: Set this input to True if the outputs are to be written to a MS Excel compatible .csv file.
        _excelFileLoc_: Specify a directory to which the MS Excel file should be saved to.

    Returns:
        radFilePaths: List of .rad files corresponding to the luminaires to be used in the simulation. Connect this to the additionalRadFiles_ input of Honeybee_Run Daylight Simulation component.
        billOfQuantity: The bill of quantity of the luminaires used for simulation.
        luminaireSchedule: List of luminaires, their location and aiming angles.
        lumScheduleDetailed: A more detailed luminaire schedule that includes information about custom lamps (if any) used in the simulation.


"""
from __future__ import print_function
import operator as op
import sys
import copy
import os
import scriptcontext as sc


ghenv.Component.Name = "Honeybee_IES Project"
ghenv.Component.NickName = 'iesProject'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nJUL_01_2016
#compatibleLBVersion = VER 0.0.59\nJUL_01_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

#lambda for formatting numbers for display:
numFrm = lambda x: "{:.2f}".format(round(x,2))


if sc.sticky.has_key('honeybee_release'):
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): pass
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): pass
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)



class LampInfo:
    def __init__(self,lampName,CCT,duv,x,y,u,v,u1,v1,r,g,b,deprFactor,lampType):
        """
            Class for defining lamp. 
        """
        self.lampName = lampName
        self.CCT = CCT
        self.duv = duv
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.u1 = u1
        self.v1 = v1
        self.r = r
        self.g = g
        self.b = b
        self.deprFactor = deprFactor
        self.lampType = lampType
               


def getLampInfo(lamp):
    """
        Function to parse the definition of lamp-data.
    """
    if lamp:
        if lamp['whiteLamp']:
            details = lamp['whiteLamp']
            lampName = details['name']
            try:
                CCT = numFrm(details["CCT"])
            except TypeError:
                CCT = "NC"
            try:                
                duv = numFrm(details["Duv"])
            except TypeError:
                duv = "NC"
            x = numFrm(details["x"])
            y = numFrm(details["y"])
            u = numFrm(details["u"])
            v = numFrm(details["v"])
            u1 = numFrm(details["u'"])
            v1 = numFrm(details["v'"])
            r = "NA"
            g = "NA"
            b = "NA"
            deprFactor = details['deprFactor']
            lampType = "White_Lamp"
        else:    
            details = lamp['rgbLamp']
            lampName = details['name']
            CCT = "NA"
            x = "NA"
            y = "NA"
            u = "NA"
            v = "NA"
            u1 = "NA"
            v1 = "NA"
            duv = "NA"
            r = numFrm(details["r"])
            g = numFrm(details["g"])
            b = numFrm(details["b"])
            deprFactor = details['deprFactor']
            lampType = "RGB_Lamp"
    else:
            lampName = "ND"
            CCT = "ND"
            x = "ND"
            y = "ND"
            u = "ND"
            v = "ND"
            u1 = "ND"
            v1 = "ND"
            duv = "ND"
            r = "ND"
            g = "ND"
            b = "ND"
            deprFactor = 1.0
            lampType = "ND"
    return LampInfo(lampName,CCT,duv,x,y,u,v,u1,v1,r,g,b,deprFactor,lampType)


class LocInfo:
    """
        Class for aggregating the data from luminaire, lamp and location data into a single unit.
    """
    def __init__(self,lumCat,lumMan,lumFile,lumWattRated,lumWattMult,lumID,xLoc,yLoc,zLoc,spin,tilt,rotate,canMult,LLF,lamp):
        self.lumCat = lumCat
        self.lumMan = lumMan
        self.lumFile = lumFile
        self.lumWattRated = lumWattRated
        self.lumWattMult = lumWattMult
        self.lumID = lumID
        self.xLoc = xLoc
        self.yLoc = yLoc
        self.zLoc = zLoc
        self.spin = spin
        self.tilt = tilt
        self.rotate = rotate
        self.canMult = canMult 
        self.LLF = LLF
        self.lamp = lamp
        

#There needs to be a place for storing all the output csv and excel files. I am going to use the last dirPath to store these files.
dirPath = None 
radFilePaths = []
lumList = []
lumIdTest = []

lumCat = []

#Lists for storing luminaire catalog names which can later be used for creating lists.
lumSch = []



#Lists for 
if _elecLightingData:
    for lightFixture in _elecLightingData:
        if lightFixture:
            radFilePaths.append(lightFixture.radPath) #Add the name of the rad file to a list.
            boqData = []

            #Test for duplicate lumIDs.
            assert lightFixture.lumID not in lumIdTest,"There are two or more luminaires of the same _luminaireID in this project. Each luminaire should have an unique _luminaireID"
            lumIdTest.append(lightFixture.lumID)

            lumCat.append(lightFixture.luminaire.lumCat)

            if outputsToExcel_ and not _excelFileLoc_:
                _excelFileLoc_ = lightFixture.dirPath
            
            
            for zone in lightFixture.lumZone:
                lampInfo = None

                if zone.lamp:
                    lampInfo = zone.lamp.lamp

                elif lightFixture.customLamp:
                    lampInfo = lightFixture.customLamp.lamp

                for point in zone.points:
                    pt,angles = point
                    x,y,z = map(numFrm,pt)
                    spin,tilt,rotate = map(numFrm,angles)
                    lampDetails = getLampInfo(lampInfo)
                    multFactor = lightFixture.luminaire.balFact * lightFixture.luminaire.candMul*lightFixture.llf*lightFixture.candelaMul*lampDetails.deprFactor
                    locData = LocInfo(lumCat = lightFixture.luminaire.lumCat,lumMan=lightFixture.luminaire.lumMan,lumFile = lightFixture.lumFile,lumWattRated=lightFixture.luminaire.inpWatts,
                                      lumWattMult = lightFixture.luminaire.inpWatts*multFactor,lumID =lightFixture.lumID,xLoc=x,yLoc=y,zLoc=z,spin=spin,tilt=tilt,rotate=rotate,
                                      canMult = lightFixture.candelaMul,LLF=lightFixture.llf,lamp=lampDetails)
                    lumSch.append(locData)                  
    
    lumSch = sorted(lumSch,key=op.attrgetter('lumCat','lumID'))
    catList = []
    billOfQuantity =[["Luminaire","Manufacturer","FileName","Quantity","RatedPower/Luminaire","TotalPower","TotalPower(Rated)"]]
    luminaireSchedule = [["Luminaire","Luminaire ID","x","y","z","Spin","Tilt","Rotate","Power"]]
    lumScheduleDetailed =[["Luminaire","Luminaire ID","x","y","z","Spin","Tilt","Rotate","LLF","CandelaMultiplier","RatedPower","Power","LampName","LampType","CCT","Duv","1931x",
                      "1931y","1960u","1960v","1976u'","1976v'","r","g","b","LampDeprFactor"]]
                      

    for lum in lumSch:

        schVal = [lum.lumCat,lum.lumID,lum.xLoc,lum.yLoc,lum.zLoc,lum.spin,lum.tilt,lum.rotate,lum.lumWattMult]
        schValDetailed = [lum.lumCat,lum.lumID,lum.xLoc,lum.yLoc,lum.zLoc,lum.spin,lum.tilt,lum.rotate,lum.LLF,lum.canMult,lum.lumWattRated,lum.lumWattMult,lum.lamp.lampName,lum.lamp.lampType,
                               lum.lamp.CCT,lum.lamp.duv,lum.lamp.x,lum.lamp.y,lum.lamp.u,lum.lamp.v,lum.lamp.u1,lum.lamp.v1,lum.lamp.r,lum.lamp.g,lum.lamp.b,lum.lamp.deprFactor]
                               
        
        #This for loop cleans and converts everything to a string/print ready format.
        for values in [schVal,schValDetailed]:
            for idx,val in enumerate(values):
                try:
                    values[idx] = numFrm(val)
                except:
                    values[idx] = val
                    
        luminaireSchedule.append(schVal)
        lumScheduleDetailed.append(schValDetailed)
        
        if lum.lumCat not in catList:
            catList.append(lum.lumCat)
            billOfQuantity.append([lum.lumCat,lum.lumMan,lum.lumFile,1,lum.lumWattRated,lum.lumWattMult,lum.lumWattRated])
        else:
            billOfQuantity[len(billOfQuantity)-1][3] +=1
            billOfQuantity[len(billOfQuantity)-1][-2] +=lum.lumWattMult
            billOfQuantity[len(billOfQuantity)-1][-1] +=lum.lumWattRated
    
    for lists in (billOfQuantity,luminaireSchedule,lumScheduleDetailed):
            for idx,value in enumerate(lists):
                value = map(str,value)
                lists[idx] = ",".join(value)
    
    if outputsToExcel_:
        boqFileName = os.path.join(_excelFileLoc_,"billOfQuantity.csv")
        lumSchFileName = os.path.join(_excelFileLoc_,"luminaireSchedule.csv")
        lumSchDetFileName = os.path.join(_excelFileLoc_,"luminaireScheduleDetailed.csv")
        
        nameData = ((billOfQuantity,boqFileName),(luminaireSchedule,lumSchFileName),(lumScheduleDetailed,lumSchDetFileName))
        
        for (data,name) in nameData:
            with open(name,'w') as dataFile:
                for lines in data:
                    print(lines,file=dataFile)
        billOfQuantity,luminaireSchedule,lumScheduleDetailed = boqFileName,lumSchFileName,lumSchDetFileName      
