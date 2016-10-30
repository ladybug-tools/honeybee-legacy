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
This is the core component for adding photometric data into a lighting simulation. 
It parses an IES photometric file to create a geometric representation of the photometric data on the Rhino viewport. 
It also calls xform and ies2rad, two programs within RADIANCE, to create a RADIANCE representation of the photometric data.
In case _writeRad is set to True and all the other input requirements are satisfied a .rad file containing photometric information will be created.
This file, accessible through radFilePath should be connected to the additionalRadFiles_ input in the Honeybee Run Daylight Simulation component.
.
.
Technical Notes:
----------------------
The parsing of IES files is based on IES LM-63-2002. 
.
This component is only compatible with Type C photometry. 
However, if Type B photometry is to be used, external programs such as the Photometric Toolbox can be used to convert Type B photometry to Type C.
.
The luminous shapes, as defined by LM-63-2002 currently compatible with this component are rectangular, circular and rectangular with luminous openings.
.
The curves drawn for creating the luminaire web is not based on interpolation. So it is possible that the curve may look irregular in case the number of vertical angles are less.
.
Suggested practices/workflow:
------------------------------------------
The _writeRad option should only be set to True once the amiming and positioning of luminaires has been confirmed.
.
In case the photometric distribution of the luminaire is not quadrilaterally symmetric, the _drawLuminaireWeb_ option should be set to True.
This will help in aiming and locating the luminaire properly.
.
In case the customLamp_ option is being used, the lumen depreciation factor of the custom lamp should be properly set for illuminance or luminance calculations.


    
    Args:
        _iesFilePath: Specify the file path for .ies photometry file.
        _luminaireZone: List of (3-d coordinate, Aiming Angle) combinations that are generated through the IES Luminaire Array component.
        _lightLossFactor_: An optional number that will be multiplied by the luminosity of the light.  This can be used to account for different light bulb luminosities or light loss from additional fixture obstructions around the light. The default is set to 1.0.
        _candelaMultiplier_: Assign a scaling value for the candela tables. This value gets multiplied by the _lightLossFactor_ value. Default is set to 1.0.
        _customLumName_: Specify a custom name for the luminaire. This input should only be used in case the manufacturer hasn't provided a value for [LUMCAT] in the photometric data.
        _drawLuminaireWeb_: Draw a geometric representation of the candela distribution of the luminaire on the Rhino viewport. If set to True then geometry normalized to unit dimensions will be drawn. If a number is provided, then geometry will be drawn and scaled to that value.
        _drawLuminaireAxes_: Draw the C0-G0 axes of the luminaire on the Rhino viewport. If set to True then axes normalized to 1.5 times the unit dimensions will be drawn. If a number is provided, then geometry will be drawn and scaled to that value.
        _drawLuminairePoly_: Draw the polygon, circle or box representing the luminous opening of the luminaire on the Rhino viewport. If set to True then geometry normalized to unit dimensions will be drawn. If a number is provided, then geometry will be drawn and scaled to that value.
        _radDir_: Custom location for the luminaire rad file. The default location is inside the Ladybug folder on your system.
        customLamp_: Specify a custom lamp using the IES Custom Lamp component
        extendLumAxesToPt_: Specify a point to which the luminaire axes should be extended to. Please note that if the aiming of the luminaire is very far way from this point then some abnormal results might be seen.
        _writeRad: Set to True to create the file for electric lighting simulation.

    Returns:
        luminaireGeo: The geometry created in the Rhino viewport for visualizing the luminaire. Can be used for generating previews.
        luminaireDetails: A description of the luminaire generated after parsing the IES file.
        luminaireList: List of luminaires and their locations and mounting angles.
        elecLightingData: Details about the luminaire, locations and lamps used in the simulation. Connect this output to the _elecLightingData input of the Honeybee_IES Project component.
        radFilePath: Location of the RAD file that should be included in the project. Connect this output to the _additionalRadFiles_ input in the Honeybee_Run_DaylightSimulation module. This output will soon be deprecated. It is recommended that you use the elecLightingData output instead.
        

"""
#Development notes:
#   Dr. Richard Mistrick from Penn State and Leland Curtis and Reinhardt Swart from SmithGroupJJR provided valuable inputs during the development of this script.
#   While Type B photometry and ILLUMDAT file formats are not supported at present, they will be supported in the future.

from __future__ import print_function
from __future__ import division

ghenv.Component.Name = "Honeybee_IES Luminaire"
ghenv.Component.NickName = 'iesLuminaire'
ghenv.Component.Message = 'VER 0.0.60\nSEP_11_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nJUL_01_2016
#compatibleLBVersion = VER 0.0.59\nJUL_01_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



import Grasshopper.Kernel as gh
import math
import Rhino as rc
import scriptcontext as sc
import copy
import os
import subprocess as sp
import sys
import time
import shutil
import datetime
import uuid

w = gh.GH_RuntimeMessageLevel.Warning


checkLadybug = sc.sticky.has_key('ladybug_release') 
checkHoneybee = sc.sticky.has_key('honeybee_release')

if not checkLadybug or not checkHoneybee:
        print ("You should first let both Ladybug and Honeybee to fly...")
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): pass
    except: pass
    radBin = sc.sticky['honeybee_folders']['RADPath']
    radLib = sc.sticky['honeybee_folders']['RADLibPath']

    #List of required executables.Add to this list as dev progressess.
    reqExe = ['ies2rad.exe','xform.exe'] 

    for filename in reqExe:
        assert filename in os.listdir(radBin),"{}, a required file, was not found in {}".format(filename,radBin)




#Define luminaire class
class Luminaire:
        """
            1. Base class for luminaire. Can handle class C type photometry currently. Add additional features later.
            2. For most purposes, this is a private class as it is only accessible through makelum function.
        """
        def __init__(self,**lumData):
            
            self.tiltInfo = lumData['tiltInfo']
            self.numLamps = lumData['numLamps'] 
            self.lumLamp = lumData['lumLamp']
            self.candMul = lumData['candMul']
            self.numVertAng = lumData['numVertAng']
            self.numHorzAng = lumData['numHorzAng']
            self.photType = lumData['photType']
            self.unitType = lumData['unitType']
            self.testDetails = lumData['testDetails']
            self.width = lumData['width']
            self.length = lumData['length']
            self.height = lumData['height']
            self.balFact = lumData['balFact']
            self.future = lumData['future']
            self.inpWatts = lumData['inpWatts']
            self.arrVertAng = lumData['arrVertAng']
            self.arrHorzAng = lumData['arrHorzAng']
            self.candelaValues = lumData['candelaValues']
            self.lumCat = lumData['lumCat']
            self.lumMan = lumData['lumMan']
            self.lumDes = lumData['lumDes']
            self.iesType = lumData['iesType']
            self.lampCat = lumData['lampCat']
            self.lampDes = lumData['lampDes']
            self.rx = 0.0
            self.ry = 0.0
            self.rz = 0.0
            self.locn = rc.Geometry.Point3d(0,0,0)

        def __str__(self):
           """
                1. Utility function that overloads the print method to produce a readable definition of the IES file.
                2. The parsing of keywords is based on IES LM-63-2002
           """
           
           #Specify the photometry and units type based on the number.
           photometryType = {1:'C',2:'B',3:'A'}[self.photType]
           unitsType = {1:'feet',2:'meters'}[self.unitType]
           
           #Mention that negative lumens imply absolute photometry.
           if round(self.lumLamp,0) == -1:
               lumens = "-1 (The photometry is absolute)"
           else:
               lumens = self.lumLamp
               
               
           #Check the luminous dimensions. Throw an exception if they aren't round or rectangular.
           width,length,height = self.width,self.length,self.height
           luminousDim = ''
           if round(width,2) == 0 and round(length,2) == 0 and round(height,2) == 0:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a point source. The IES data might be for a lamp)".format(width,length,height) 
           elif width > 0 and length > 0 and round(height,2) == 0:
               luminousDim = "{},{},{}.\nThe luminous opening is rectangular.".format(width,length,height) 
           elif width > 0 and length > 0 and height> 0:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is rectangular with luminous sides.)".format(width,length,height) 
           elif width <0 and length < 0 and round(length,2) == round(width,2) and round(height,2)==0:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is circular. {3} is the diameter of the luminous opening)".format(width,length,height,abs(width)) 
           elif width <0 and length < 0 and round(length,2) != round(width,2) and round(height,2)==0:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is elliptical. {3} and {4} are the major/minor axes of the luminous opening)".format(width,length,height,abs(width),abs(length)) 
           elif width <0 and length < 0 and height > 0 and round(length,2) == round(width,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a vertical cylinder. {3} is the diameter and {4} is the height of the luminous opening)".format(width,length,height,abs(width),abs(height)) 
           elif width <0 and length < 0 and height > 0 and round(length,2) != round(width,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a vertical elliptcal cylinder. {3} and {4} are the major/minor axes and {5} is the height of the luminous opening)".format(width,length,height,abs(width),abs(length),abs(height)) 
           elif width <0 and length < 0 and height < 0 and round(length,2) == round(width,2) and round(width,2) == round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a sphere. {3} is the diameter)".format(width,length,height,abs(width))
           elif width <0 and length < 0 and height < 0:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is an ellipsoid. {3} , {4} and {5} are the width, length and height)".format(width,length,height,abs(width),abs(length),abs(height)) 
           elif width < 0 and length > 0 and height < 0 and round(width,2) == round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a horizontal cylinder. {3} is the diameter and {4} is the length of the luminous opening)".format(width,length,height,abs(width),abs(height))
           elif width < 0 and length > 0 and height < 0 and round(width,2) != round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a horizontal elliptical cylinder. {3} and {4} are the major/minor axes and {5} is the length of the luminous opening)".format(width,length,height,abs(width),abs(height),abs(length)) 
           elif width > 0 and length < 0 and height < 0 and round(length,2) == round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a horizontal cylinder. {3} is the diameter and {4} is the length of the luminous opening)".format(width,length,height,abs(length),abs(width))
           elif width > 0 and length < 0 and height < 0 and round(length,2) != round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a horizontal elliptical cylinder. {3} and {4} are the major/minor axes and {5} is the length of the luminous opening)".format(width,length,height,abs(length),abs(height),abs(width)) 
           elif width < 0 and round(length) == 0 and height < 0 and round(width,2) == round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a vertical circle. {3} is the diameter of the luminous opening)".format(width,length,height,abs(width))
           elif width < 0 and round(length) == 0 and height < 0 and round(width,2) != round(height,2):
               luminousDim = "{0},{1},{2}.\n(The luminous opening is a vertical ellipse. {3} and {4} are the major/minor axes of the luminous opening)".format(width,length,height,abs(width),abs(height)) 
           else:
               luminousDim = "{0},{1},{2}.\n(The luminous opening is unidentified)".format(width,length,height) 
               warning = "The luminous dimensions for the specfied luminaire are ({0},{1},{2}). These are not recognized.\n" \
               "This component will still run but it will not be able to draw the light geometry in the Rhino scene".format(width,length,height)
               ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
               raise Exception("The luminous dimensions for the specfied luminaire are ({},{},{}). This format, which is neither rectangular nor circular, is not supported currently".format(width,length,height))
           
           #Check if optional comments exist in the IES file. Add them to the string if they do exist.   
           lumstring = """"""
           if self.lumCat:
               lumstring += """Luminaire Catalog Number: {}\n""".format(self.lumCat)
           if self.lumDes:
               lumstring += """Luminaire Description: {}\n""".format(self.lumDes)

           if self.lampCat:
               lumstring += """Lamp Catalog Number: {}\n""".format(self.lampCat)
 
           if self.lampDes:
               lumstring += """Lamp Description: {}\n""".format(self.lampDes)
            
           if self.testDetails:
               lumstring += """Luminaire Test Details: {}\n\n""".format(self.testDetails) 

           lumstring+= ("Luminaire Manufacturer: {0.lumMan}\n"+
                        "IES File Format Type: {0.iesType}\n"+
                        "Photometry Type: {1}\n\n"+
                        "Number of Lamps: {0.numLamps}\n"+
                        "Lumens per lamp: {3}\n"+
                        "Units Type: {2}\n"+
                        "Luminous Dimensions(width,length,height): {4}\n\n"+
                        "Number of Vertical Angles:{0.numVertAng}\n"+
                        "Vertical Angle limits:{vMin},{vMax}\n\n"+
                        "Number of Horizontal Angles: {0.numHorzAng}\n"+
                        "Horizontal Angle limits: {hMin},{hMax}\n\n"+
                        "Input Watts:   {0.inpWatts}\n"+
                        "Ballast Factor: {0.balFact}\n")
           
           vertMin,vertMax = self.arrVertAng[0],self.arrVertAng[-1]
           horzMin,horzMax = self.arrHorzAng[0],self.arrHorzAng[-1]
           lumstring = lumstring.format(self,photometryType,unitsType,lumens,luminousDim,
                                        vMin=vertMin,vMax=vertMax,
                                        hMin=horzMin,hMax=horzMax)

           return lumstring
           

class electricLightingData:
    def __init__(self,lumID,lumZone,luminaire,llf,candelaMul,customLamp,lumPath,lumFile,dirPath):
        self.lumID = lumID
        self.lumZone = lumZone
        self.luminaire = luminaire
        self.llf = llf
        self.candelaMul = candelaMul
        self.customLamp = customLamp
        self.radPath = lumPath
        self.lumFile = lumFile
        self.dirPath = dirPath
    def __repr__(self):
        return "Honeybee.electricLightingData"


#Parse IES file, Instantiate luminaire class.            
def makeLum(fileName,_customLumName_):
    """
        This function parses an IES file and then instantiates a luminaire class.   
        1. Function for parsing the IES file.
        2. Keywords are parsed first, followed by the photometric data.
    """
    #Initiate the dictionary to store 
    
    lumData = dict.fromkeys(('lumCat','lumMan','lumDes','lampCat','lampDes','iesType'),'Not specified in file.')
    
    #Step1: Parse the entire file for keywords.
    lumName = manName=lumDes=lampCat=lampDes=""
    iesType=None

    if len(fileName) == 1:
        fileName = fileName[0]
    else:
        fileName = "\n".join(fileName)
    
    #If the actual contents of the ies file are provided instead of the 
    try:
        with open(fileName) as iesData:
            iesData = iesData.readlines()
    except (SystemError,ValueError):
        iesData = fileName.split("\n")
    
    for idx,lines in enumerate(iesData):
        lineSplit = lines.split()
        
        #This if-test assigns the IES format type (eg. IESNA: LM-63-2002) to the dictionary.
        if lines.strip() and lumData['iesType'] == 'Not specified in file.':
            lumData['iesType'] = lines.strip()
        if "[LUMCAT]" in lines:
            lumData['lumCat'] = " ".join(lineSplit[1:])
            if _customLumName_:
                lumData['lumCat'] = _customLumName_.strip().replace(" ","_")

        if "MANUFAC" in lines:
            lumData['lumMan']= " ".join(lineSplit[1:])
        if "[LUMINAIRE]" in lines:
            lumData['lumDes'] = " ".join(lineSplit[1:])
        if "[LAMPCAT]" in lines:
            lumData['lampCat'] = " ".join(lineSplit[1:])
        if "[LAMP]" in lines:
            lumData['lampDes'] = " ".join(lineSplit[1:])
        
        
        #As a fail-safe, I am assiging the [TEST] value as name. I could have done this re but I thought of not adding an extra dependency.
        if "[TEST]" in lines:
            lumData['testDetails'] = " ".join(lineSplit[1:])
    
    #Updated on 03/03/2016. I didn't think this was required, however, it turns out that some manufacturers don't assign names to their luminaires.
    #Assign a luminaire catalog number if the IES file doesn't have one already. The lumcat will be assigned on the basis of _luminaireID.
    #As this is not the best solution, I am issuing a warning and asking the user to specify a name through _customLumName_.
    if lumData['lumCat'] == 'Not specified in file.':
        if _customLumName_:
                _customLumName_ = _customLumName_.strip().replace(" ","_")
                lumManName = _customLumName_
        else:
            timeStampforlumCat = time.strftime("%d%b_%H") #This time stamp should be enough to avoid any conflicts.
            lumManName =_luminaireID + "_"+timeStampforlumCat
            warningString = "The chosen photometry doesn't have a Luminaire Catalog information. So a _luminaireID-based catalog number was defined for it.\n"
            warningString += "The best way to resolve this warning would to assign a proper name for the luminaire using the _customLumName_ input"
            ghenv.Component.AddRuntimeMessage(w, warningString)
            
        lumData['lumCat'] = lumManName


    #Step2: Parse again, this time for reading photometric data.
    try:
        with open(fileName,'r') as iesFile:
            iesFile = iesFile.read()   #Read ies file.
    except (SystemError,ValueError):
        iesFile = fileName
    iesFile = iesFile.replace(',',' ') #If commas exist, replace them with spaces so that splitting is easier.
    iesFile = iesFile.split()
    
     
    #Test for tilt angles. If present inlcude them in the IES definition.
    if ("TILT=INCLUDE" in iesFile):
        tiltStart = iesFile.index("TILT=INCLUDE")
        tiltInfo = {"lmpLumGeo":False,"tiltAng":False,"tiltAngArr":False,"mulFact":False} #Dictionary to store tilt info.
        tiltInfo["lmpLumGeo"] = float(iesFile[tiltStart+1])
        tiltInfo["tiltAng"] = int(iesFile[tiltStart+2])
        tiltInfo["tiltAngArr"] = map(float,iesFile[(tiltStart+3):(tiltStart+3+tiltInfo["tiltAng"])])
        tiltInfo["mulFact"] = map(float,iesFile[(tiltStart+3+tiltInfo["tiltAng"]+1):(tiltStart+3+2*tiltInfo["tiltAng"])+1])
        fileStart = tiltStart + 2 + 2*len(tiltInfo["tiltAngArr"])
    elif ("TILT=NONE" in iesFile):
        fileStart = iesFile.index("TILT=NONE")
        tiltInfo = None

    lumData.update({'tiltInfo':tiltInfo})
    

    iesData = iesFile[fileStart+1:]
    numLamps = int(iesData[0])
    lumLamp = float(iesData[1])
    candMul = float(iesData[2])
    lumData.update({'numLamps':numLamps,'lumLamp':lumLamp,'candMul':candMul})
    
    
    numVertAng = int(iesData[3])
    numHorzAng = int(iesData[4])
    photType = int(iesData[5])
    unitType = int(iesData[6])
    lumData.update({'numVertAng':numVertAng,'numHorzAng':numHorzAng,'photType':photType,'unitType':unitType})
    
    width,length,height,balFact,future,inpWatts = map(float,iesData[7:13])
    lumData.update({'width':width,'length':length,'height':height,'balFact':balFact,'future':future,'inpWatts':inpWatts})
    
    arrVertAng = map(float,iesData[13:13+numVertAng])
    vertAngPos = 13+numVertAng    
    arrHorzAng = map(float,iesData[vertAngPos:vertAngPos+numHorzAng])
    horzAngPos = vertAngPos+numHorzAng
    lumData.update({'arrVertAng':arrVertAng,'arrHorzAng':arrHorzAng})
    
    
    candelaValues = []
    for horizontalAngles in range(numHorzAng):
        horzAngArray = []
        for verticalAngles in range(numVertAng):
            currHorzPosn = horizontalAngles*numVertAng+horzAngPos+verticalAngles
            horzAngArray.append(float(iesData[currHorzPosn]))
        candelaValues.append(horzAngArray)
    lumData.update({'candelaValues':candelaValues})
    
        
    
    luminaire = Luminaire(**lumData) #instantiate a luminaire class.
    
    return luminaire

#Create a polygon,circle or box to be drawn as a luminaire represenation in the Rhino ViewPort.
def createLumPoly(Luminaire):
    """
        Draw a rectangle or circle in the Rhino viewport. The rectanlge/circle corresponds to the luminous dimensions of the luminaire.
    """
    
    #Honeybee units are meters. So convert the rect/circle according the IES units to meters..
    fileUnit = {1:0.304,2:1}[Luminaire.unitType]
    width,length,height = fileUnit*Luminaire.width,fileUnit*Luminaire.length,fileUnit*Luminaire.height
    
    xyPlane = rc.Geometry.Plane.WorldXY
    point3d = rc.Geometry.Point3d.Origin
    LumPoly = point3d
    
    # Iplies that the luminous opening is a point.
    if round(width,2) == 0 and round(length,2) == 0 and round(height,2) == 0:
        pass
    # Implies that luminous opening is rectangular
    elif width > 0 and length > 0 and round(height,2) == 0:
        cornerA = rc.Geometry.Point3d(-length/2,-width/2,0)
        cornerB = rc.Geometry.Point3d(length/2,width/2,0)
        lumRect = rc.Geometry.Rectangle3d(xyPlane,cornerA,cornerB).ToNurbsCurve()
        LumPoly = rc.Geometry.Brep.CreatePlanarBreps([lumRect])[0]
    # Implies that luminous opening is rectangular with luminous sides.
    elif width > 0 and length > 0 and height> 0:
        yInterval = rc.Geometry.Interval(-width/2,width/2)
        xInterval = rc.Geometry.Interval(-length/2,length/2)
        zInterval = rc.Geometry.Interval(-height/2,height/2)
        LumPoly = rc.Geometry.Box(xyPlane,xInterval,yInterval,zInterval)
    # Implies that the luminous opening is a circle.    
    elif width <0 and length < 0 and round(length,2) == round(width,2) and round(height,2)==0:
        LumCirc = rc.Geometry.Circle(xyPlane,point3d,abs(-width/2)).ToNurbsCurve()
        LumPoly = rc.Geometry.Brep.CreatePlanarBreps([LumCirc])[0]
    # Implies that the luminous opening is an ellipse. 
    elif width <0 and length < 0 and round(length,2) != round(width,2) and round(height,2)==0:
        LumEllip = rc.Geometry.Ellipse(xyPlane,abs(-width/2),abs(-length/2)).ToNurbsCurve()
        LumPoly = rc.Geometry.Brep.CreatePlanarBreps([LumEllip])[0]
    # Implies the luminous opening is a vertical cylinder.
    elif width <0 and length < 0 and height > 0 and round(length,2) == round(width,2):
        LumCirc = rc.Geometry.Circle(xyPlane,point3d,abs(-width/2))
        LumPoly = rc.Geometry.Cylinder(LumCirc, height).ToBrep(True, True)
    # Implies the luminous opening is a vertical elliptcal cylinder.
    elif width <0 and length < 0 and height > 0 and round(length,2) != round(width,2):
        LumCirc = rc.Geometry.Circle(xyPlane,point3d,1)
        LumPoly = rc.Geometry.Cylinder(LumCirc, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(xyPlane,abs(width/2),abs(length/2),abs(height))
        LumPoly.Transform(transf)
        LumPoly = LumPoly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    elif width <0 and length < 0 and height < 0 and round(length,2) == round(width,2) and round(width,2) == round(height,2):
        LumPoly = rc.Geometry.Sphere(rc.Geometry.Point3d(0,0,abs(width/2)),abs(width/2))
    # Implies the luminous opening is an ellipsoid.
    elif width <0 and length < 0 and height < 0:
        LumPoly = rc.Geometry.Sphere(rc.Geometry.Point3d(0,0,abs(width/2)),1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(rc.Geometry.Point3d(0,0,abs(width/2)),rc.Geometry.Vector3d.ZAxis),abs(width/2),abs(length/2),abs(height/2))
        LumPoly.Transform(transf)
    # Implies the luminous opening is a horizontal cylinder.
    elif width < 0 and length > 0 and height < 0 and round(width,2) == round(height,2):
        LumCirc = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ,rc.Geometry.Point3d((-length/2),0,abs(-width/2)),abs(-width/2))
        LumPoly = rc.Geometry.Cylinder(LumCirc, length).ToBrep(True, True)
    # Implies the luminous opening is a horizontal elliptical cylinder.
    elif width < 0 and length > 0 and height < 0 and round(width,2) != round(height,2):
        centPt = rc.Geometry.Point3d((height/2),0,abs(height/2))
        LumCirc = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ,centPt,1)
        LumPoly = rc.Geometry.Cylinder(LumCirc, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(centPt,rc.Geometry.Vector3d.ZAxis),abs(length),abs(width/2),abs(height/2))
        LumPoly.Transform(transf)
        LumPoly = LumPoly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    # Implies the luminous opening is a horizontal cylinder.
    elif width > 0 and length < 0 and height < 0 and round(length,2) == round(height,2):
        LumCirc = rc.Geometry.Circle(rc.Geometry.Plane.WorldZX,rc.Geometry.Point3d(0,(-width/2),abs(-length/2)),abs(-length/2))
        LumPoly = rc.Geometry.Cylinder(LumCirc, width).ToBrep(True, True)
    # Implies the luminous opening is a horizontal elliptical cylinder.
    elif width > 0 and length < 0 and height < 0 and round(length,2) != round(height,2):
        centPt = rc.Geometry.Point3d(0,(-width/2),abs(height/2))
        LumCirc = rc.Geometry.Circle(rc.Geometry.Plane.WorldZX,centPt,1)
        LumPoly = rc.Geometry.Cylinder(LumCirc, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(centPt,rc.Geometry.Vector3d.ZAxis),abs(length/2),abs(width),abs(height/2))
        LumPoly.Transform(transf)
        LumPoly = LumPoly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    # Implies the luminous opening is a vertical circle.
    elif width < 0 and round(length) == 0 and height < 0 and round(width,2) == round(height,2):
        LumCirc = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ,point3d,abs(width/2)).ToNurbsCurve()
        LumPoly = rc.Geometry.Brep.CreatePlanarBreps([LumCirc])[0]
    # Implies the luminous opening is a vertical ellipse.
    elif width < 0 and round(length) == 0 and height < 0 and round(width,2) != round(height,2):
        LumCirc = rc.Geometry.Ellipse(rc.Geometry.Plane.WorldYZ,abs(width/2),abs(height/2)).ToNurbsCurve()
    
    return LumPoly


#Draw photometric web for the luminaire candela values in the Rhino viewport.
def createLumWeb(Luminaire):
    """
        Draw a photometric web for the given luminaire.
        Has been tested with Type C Photometry only.
    """
    fileUnit = {1:0.304,2:1}[Luminaire.unitType]
    candelas,vert,horz = Luminaire.candelaValues,Luminaire.arrVertAng,Luminaire.arrHorzAng
    width,length,height = fileUnit*Luminaire.width,fileUnit*Luminaire.length,fileUnit*Luminaire.height
   
    mul3d = max((abs(width),abs(length)))
    
    counter = 0
    
    #THE PURPOSE OF THIS IF STATEMENT IS TO GENERATE A 360deg(Horiz)x180deg(Vert) MATRIX OF CANDELA VALUES.
    
    #~~~~~~~If there is only one horizontal angle, then create an horizontal array after every 10 degrees..
    #~~~~~~~...and copy the same candela values for each angle.
    
    if len(horz)==1:
       horz = range(0,370,10)
       candelas = candelas*len(horz)
       
    else:
        while(horz[0])==0 and horz[-1]<360:
           counter +=1
           
           #Get the angular difference between the last angle and all the other angles so that the array can be mirrored.
           #For example, in the case of 0.0, 22.5, 45.0, 67.5, 90.0, the intervals will be 90-67.5, 90-45.0, 90-22.5 and so on.
           intervals = [horz[-1]-horz[-idx-2] for idx in range(len(horz)-1)]
           initangles = horz[:]
           
           #Create an array of new angles based on the intervals.
           initnew = [initangles[-1]+intervals[idx-1] for idx in range(1,len(initangles))]
           
           #Incorporate the new array into existing horizontal angles array.
           horz.extend(initnew)
           
           #Affect corresponding changes into the candela table.
           candelas.extend([values for values in list(reversed(candelas))[1:]])
           
           #The counter should not exceed 4 as even in the case of 0-90 symmetry, the num of iterations won't exceed 4.
           if counter>4:
            assert False,"The horizontal angles in the IES file aren't in order"
            break
        
        #This will be relevant in the case of 90-270 symmetry.
        if horz[0]>0:
            zerolimit = [horz[0]-(horz[idx]-horz[0])for idx in range(1,len(horz)) if horz[0]-(horz[idx]-horz[0])>=0][::-1]
            maxlimit = [horz[-1]+(horz[-1]-horz[-1-idx])for idx in range(1,len(horz))if horz[-1]+(horz[-1]-horz[-1-idx])<=360]
            candela0_90 = candelas[1:len(zerolimit)+1][::-1]
            candela270_360 = candelas[-len(maxlimit)-1:-1][::-1]
            horz = zerolimit+horz+maxlimit
            candelas = candela0_90+candelas+candela270_360
    
    #Convert horz and vert angle arrays to radians.
    vert = map(math.radians,vert)
    horz = map(math.radians,horz)
    
    #get max value from candela table.
    candelamax = max([max(value) for value in candelas])
    
    #Normalize candela values as per max value.
    candelas = [[value/candelamax for value in cdarr] for cdarr in candelas]
    
    #Plot 3d Points as per Candela Values, Draw Curves from the 3d Points and finally join the curves together.
    curvelist = []
    for idx1,horzAngles in enumerate(horz):
        ptgrid=[]
        for idx2,vertAngles in enumerate(vert):
            cd = mul3d*candelas[idx1][idx2]
            x = cd*math.sin(vertAngles)*math.cos(horzAngles)
            y = cd*math.sin(vertAngles)*math.sin(horzAngles)
            z = -cd*math.cos(vertAngles)

            ptgrid.append(rc.Geometry.Point3d(x,y,z))
        curvelist.append(rc.Geometry.PolyCurve.CreateControlPointCurve(ptgrid))

    curveobjectlist = [curvelist[idx:idx+2]for idx in range(len(curvelist)-1)]
    LumWeb=map(rc.Geometry.Brep.CreateEdgeSurface,curveobjectlist)
    return LumWeb


#Draw C0-G0 axes for the luminaire.
def createLumAxes(Luminaire):
    """
        Draw the C0-G0 Axes for the Luminaire as per IES LM-63-2002.
    """
    fileUnit = {1:0.304,2:1}[Luminaire.unitType]
    width,length,height = fileUnit*Luminaire.width,fileUnit*Luminaire.length,fileUnit*Luminaire.height
    
    #In case the luminaire is circular, then length will be zero and width will be negative.
    if (not length) and width <0:
        length = abs(width)

    horzAxis = rc.Geometry.Line(rc.Geometry.Point3d(0,0,0),rc.Geometry.Point3d(1.2*length/2,0,0))
    vertAxis = rc.Geometry.Line(rc.Geometry.Point3d(0,0,0),rc.Geometry.Point3d(0,0,-2*length/2))

    return [horzAxis,vertAxis]


#Transform geometry as per the IES LM-63 2002 convetions.
def transformGeometry(geometry,spin,tilt,rotate,transform,mul):
    """
        Utility function for transforming all the drawn objects.
        This function will be used to spin,tilt,rotate,transform and scale luminaireWeb, Axes and Luminaire Polygons.
    """
    
    geometry = copy.deepcopy(geometry)
    normVector = rc.Geometry.Vector3d(0,0,1)
    xyPlane = rc.Geometry.Plane(rc.Geometry.Point3d(0,0,0),normVector)
    point3d = rc.Geometry.Point3d(0,0,0)
    
    #Scale first.
    scaling = rc.Geometry.Transform.Scale(xyPlane,mul,mul,mul)
    geometry.Transform(scaling)
    
    #Spin
    vectorStart = rc.Geometry.Vector3d(0,1,0)
    vectorSpin = copy.deepcopy(vectorStart)
    vectorSpin.Rotate(math.radians(spin),rc.Geometry.Vector3d(0,0,1))
    trans = rc.Geometry.Transform.Rotation(vectorStart,vectorSpin,point3d)
    geometry.Transform(trans)
    
    #Tilt
    vectorVert = rc.Geometry.Vector3d(0,0,-1)
    vectorTilt = copy.deepcopy(vectorVert)
    vectorTilt.Rotate(math.radians(tilt),rc.Geometry.Vector3d(0,1,0))
    trans = rc.Geometry.Transform.Rotation(vectorVert,vectorTilt,point3d)
    geometry.Transform(trans)
    
    #Rotate
    vectorStart = rc.Geometry.Vector3d(0,1,0)
    vectorRotate = copy.deepcopy(vectorStart)
    vectorRotate.Rotate(math.radians(rotate),rc.Geometry.Vector3d(0,0,1))
    trans = rc.Geometry.Transform.Rotation(vectorStart,vectorRotate,point3d)
    geometry.Transform(trans)
    
    #Translate
    x,y,z=transform
    transVector = rc.Geometry.Vector3d(x,y,z)
    trans = rc.Geometry.Transform.Translation(transVector)
    geometry.Transform(trans)
    
    return geometry
    

#Create a valid, IES2RAD-compatible copy of the IES file inside the ladybug folder.
def fixIesFile(originalPathName,_radDir_):
    dirName,fileName = os.path.split(originalPathName)
    fileNameOnly,ext = os.path.splitext(fileName)
    
    fileNameFixed = fileNameOnly.replace(" ","_")
    
    if _radDir_:
        if os.path.isdir(_radDir_):
            assert " " not in _radDir_,"The value for _radDir_ should not have any spaces in it"
            dirpath = os.path.join(_radDir_,'tempIesFiles')
    else:
        dirpath = sc.sticky['Honeybee_DefaultFolder']
        dirpath = os.path.join(dirpath,'ies','tempIesFiles')
    fileNameFullFixed = os.path.join(dirpath,fileNameFixed+'.ies')

    if not os.path.exists(dirpath):
       os.mkdir(dirpath)    
    shutil.copy(originalPathName,fileNameFullFixed)
    return fileNameFullFixed

#If all the input requirements are satisfied then, proceed by drawing the luminaires inside Rhino.
if _iesFilePath and _luminaireZone and checkLadybug and checkHoneybee:
        
        
    if len(_iesFilePath)==1:
        if os.path.exists(_iesFilePath[0]):
            
            #Probably not a best practice thing. But I'd have to break a lot of code if I don't do this !
            _iesFilePath[0] = fixIesFile(_iesFilePath[0],_radDir_) 
            filePath = _iesFilePath[0]
            filenamefull=os.path.split(filePath)[1]
            filenameonly,ext = os.path.splitext(filenamefull)
            originalIesFileName = filenameonly
    
    #Store original values for later use.
    if not _customLumName_:
        _luminaireID = str(uuid.uuid4())
    else:
        _luminaireID = _customLumName_
    _luminaireIdSpecified = _luminaireID
    _iesFilePathSpecified = _iesFilePath
    
    
    #Rotations for ies2rad.
    rx=ry=rz = 0
    
    luminaire = makeLum(_iesFilePath,_customLumName_)
    luminaireDetails = str(luminaire)
    
    filenamefull,filenameonly,originalIesFileName = luminaire.lumCat+"_inGhFile",luminaire.lumCat,luminaire.lumCat
    
    #function to replace white spaces
    def repSpc(originalString):
        while " " in originalString:
            originalString = originalString.replace(" ","")
        return originalString

    filenamefull,filenameonly,originalIesFileName = map(repSpc,(filenamefull,filenameonly,originalIesFileName))


    if _luminaireID:
        filenameonly= _luminaireID
    if _radDir_:
        assert os.path.exists(_radDir_),"The specified directory {} does not exist.".format(_radDir_)
        dirpath = os.path.abspath(_radDir_)
        dirpath = os.path.join(dirpath,'ies')

    else:
#         dirpath = os.path.split(_iesFilePath)[0]
         dirpath = sc.sticky['Honeybee_DefaultFolder']
         dirpath = os.path.join(dirpath,'ies',originalIesFileName)
         
    if not os.path.exists(dirpath):
       os.mkdir(dirpath)
    
    photometryType = {1:'C',2:'B',3:'A'}[luminaire.photType]
    
    assert int(luminaire.photType)==1,"\nThe specified IES file in _iesFilePath is of Type {} photometry.\nOnly type C photometry is supported at the moment.".format(photometryType)+\
    "\nIt is possible to convert Type B photometry to Type C using freely available softwares."
    
    if not _lightLossFactor_:
        _lightLossFactor_ = 1.0
    else:
        assert 0.0<=float(_lightLossFactor_)<=1.0,"The value of Light Loss Factor should be between 0.0 and 1.0"
    
    if not _candelaMultiplier_:
        _candelaMultiplier_ = 1.0
    else:
        assert _candelaMultiplier_ >0,"Candela multiplier should be a number greater than 0"
    
    
    #Create luminaire polygon, web and axes.
    luminairePolygon = createLumPoly(luminaire)
    luminaireWeb = createLumWeb(luminaire)
    luminaireAxes = createLumAxes(luminaire)
    
    
    #Iterate through the list of luminaires and generate luminaire geometry inside Rhino for each luminaire.
    #Record the luminaire coordinates and rotation info for each luminaire.
    luminaireGeo = []
    luminaireList = []
    for idx,lumArr in enumerate(_luminaireZone):
            for index,values in enumerate(lumArr.points):
                width,height = luminaire.width,luminaire.length
                if width>height:
                    TiltVector = (1,0,0)
                else:
                    TiltVector = (0,1,0)
                
                Location,(Spin,Tilt,Rotate)=values
                
                Spin,Tilt,Rotate = map(float,(Spin,Tilt,Rotate))
                
                newluminaire = copy.deepcopy(luminaire)
                newluminaire.rx,newluminaire.ry,newluminaire.ry = rx,ry,rz
                newluminaire.locn = Location
                luminaireList.append("{}. (x,y,z):({},{},{}). (Spin,Tilt,Rotation):{}, {}, {}.".format(index+1,Location[0],Location[1],Location[2],Spin,-Tilt,Rotate))
               
               
                if _drawLuminairePoly_ is None:
                    _drawLuminairePoly_ = True           
                           
                if _drawLuminairePoly_:
                    if _drawLuminairePoly_ is True:
                        _drawLuminairePoly_ = 1
                    else:
                        _drawLuminairePoly_ = abs(_drawLuminairePoly_)
                    luminaireGeo.append(transformGeometry(luminairePolygon,Spin,Tilt,Rotate,Location,_drawLuminairePoly_))
                
                if _drawLuminaireWeb_:
                    for surfaces in luminaireWeb:
                        if _drawLuminaireWeb_ is True:
                            _drawLuminaireWeb_ = 1
                        else:
                            _drawLuminaireWeb_ = abs(_drawLuminaireWeb_)
                        luminaireGeo.append(transformGeometry(surfaces,Spin,Tilt,Rotate,Location,_drawLuminaireWeb_))
    
                if _drawLuminaireAxes_ is None:
                    _drawLuminaireAxes_ = True
    
    
                if _drawLuminaireAxes_:
                    LumAxes = luminaireAxes[:]
                    for axs in LumAxes:
                        if _drawLuminaireAxes_ is True:
                            _drawLuminaireAxes_ = 1
                        else:
                            _drawLuminaireAxes_ = abs(_drawLuminaireAxes_)
    
                        luminaireGeo.append(transformGeometry(axs,Spin,Tilt,Rotate,Location,_drawLuminaireAxes_))
                
                if extendLumAxesToPt_:
                    vertAimingLine = rc.Geometry.Line(rc.Geometry.Point3d(0,0,0),rc.Geometry.Point3d(0,0,-1))
                    vertAimingLine = transformGeometry(vertAimingLine,Spin,Tilt,Rotate,Location,1)
                    scalingFactor = vertAimingLine.ClosestParameter(extendLumAxesToPt_)
                                    
                    x1,y1,z1 = vertAimingLine.From
                    x2,y2,z2 = vertAimingLine.To
    
                    xDel,yDel,zDel = scalingFactor*(x2-x1),scalingFactor*(y2-y1),scalingFactor*(z2-z1)
                    x3,y3,z3 = x1+xDel,y1+yDel,z1+zDel
                    startPoint = rc.Geometry.Point3d(x1,y1,z1)
                    endPoint = rc.Geometry.Point3d(x3,y3,z3)
                    vertAimingLine = rc.Geometry.Line(startPoint,endPoint)
    
                    luminaireGeo.append(vertAimingLine)
    
    luminaireList = "\n".join(luminaireList)

    if _writeRad:  
        if len(_iesFilePath)==1:
            _iesFilePath = _iesFilePath[0]
            if not os.path.exists(_iesFilePath):
                newIesFile = os.path.join(dirpath,filenamefull+".ies")
                with open(newIesFile,'w') as iesFileWrite:
                    print(_iesFilePath,file=iesFileWrite,end="\n")
                _iesFilePath = os.path.join(dirpath,filenamefull+".ies")
        else:
            newIesFile = os.path.join(dirpath,filenamefull+".ies")
            with open(newIesFile,'w') as iesFileWrite:
                for lines in _iesFilePath:
                    print(lines,file=iesFileWrite,end="\n")
            _iesFilePath = os.path.join(dirpath,filenamefull+".ies")         
            
            
        winbatchstring = "SET RAYPATH=.;%s\n"%radLib
        winbatchstring += "PATH=.;%s\n"%radBin
        winbatchstring += "cd %s\n"%dirpath
        
        
        def createCustomLamp(customLampDict,batString):
            """
                Return a ies2rad string for custom lamp.
            """
            assert isinstance(customLampDict,dict),"The input for customLamp_ should be the output from the IES Custom Lamp component"
            assert ('whiteLamp' in customLampDict.keys() and 'rgbLamp' in customLampDict.keys())
            
            if customLampDict['whiteLamp']:
                lampDict = customLampDict['whiteLamp']
                tabName = os.path.join(dirpath,"{}.tab".format(filenameonly))
                tabNameOnly = os.path.join(dirpath,"{}.tab".format(filenameonly))
            
                lampName,x,y,mul = lampDict['name'],lampDict['x'],lampDict['y'],lampDict['deprFactor']
                
                with open(tabName,'w') as tabFile:
                    tabString = r"/{}/ {} {} {}".format(lampName,x,y,mul)
                    print(tabString,file=tabFile)
                batchstring = 'ies2rad -dm -o {1} -p {0} -m {2} -f {5} -t "{4}" {3}'.format(dirpath,filenameonly+batString,_lightLossFactor_*_candelaMultiplier_,_iesFilePath,lampName,tabNameOnly)

            else:
                lampDict = customLampDict['rgbLamp']
                r = lampDict['r']
                g = lampDict['g']
                b = lampDict['b']
                deprFactor = lampDict['deprFactor']
                batchstring = 'ies2rad -dm -o {1} -p {0} -m {2} -t "default" -c {4} {5} {6} {3}'.format(dirpath,filenameonly+batString,_lightLossFactor_*_candelaMultiplier_*deprFactor,_iesFilePath,r,g,b)
            return batchstring

        def createLumRadFile(zoneId,batString):
            radpath = os.path.join(dirpath,filenameonly+zoneId+'.rad')
            _luminaireID = os.path.join(dirpath,"{}_arr.rad".format(filenameonly+zoneId))
            _batchname = os.path.join(dirpath,"{}.bat".format(filenameonly+zoneId))
            
            
            with open(_batchname,'w') as batchfile:
                print(batString,file=batchfile)  
            #Run the batch file and wait for the operation to finish.
            runbatch = os.system(_batchname)
            return radpath,_luminaireID
        
        if customLamp_:
            winbatchstring += createCustomLamp(customLamp_.lamp,"")
        else:
            winbatchstring += "ies2rad -dm -o {1} -p {0} -m {2} {3}".format(dirpath,filenameonly,_lightLossFactor_*_candelaMultiplier_,_iesFilePath)    

        radpathfull,_luminaireID = createLumRadFile("",winbatchstring)
        
        
        
        with open(_luminaireID,'w') as radfile:
            print("#Radfile created by the IES Photometry tool in Honeybee/GrassHopper",file=radfile)
            
            for idx,lumArr in enumerate(_luminaireZone):
                
                if lumArr.lamp:
                    winbatchstring = "SET RAYPATH=.;%s\n"%radLib
                    winbatchstring += "PATH=.;%s\n"%radBin
                    winbatchstring += "cd %s\n"%dirpath
                    winbatchstring += createCustomLamp(lumArr.lamp.lamp,str(idx))
                    radPathVal,dummyVal = createLumRadFile(str(idx),winbatchstring)
                else:
                    radPathVal = radpathfull
                    
                    
                for index,values in enumerate(lumArr.points):
                    #Code to create photometric web and luminaire polygon.
                    width,height = luminaire.width,luminaire.length
                    if width>height:
                        TiltVector = (1,0,0)
                    else:
                        TiltVector = (0,1,0)
                    
                    Location,(Spin,Tilt,Rotate)=values
                    
                    Spin,Tilt,Rotate = map(float,(Spin,Tilt,Rotate))
                    
                    newluminaire = copy.deepcopy(luminaire)
    
                    newluminaire.rx,newluminaire.ry,newluminaire.ry = rx,ry,rz
    
                    xcor,ycor,zcor = Location
                    print("!xform -rz {} -ry {} -rz {} -t {} {} {} {}".format(Spin,Tilt,Rotate,xcor,ycor,zcor,radPathVal),file=radfile)
                    
        radFilePath = _luminaireID

        elecLightingData = electricLightingData(lumID=_luminaireIdSpecified,lumPath=_luminaireID,lumZone=_luminaireZone,
                                                luminaire=copy.deepcopy(luminaire),llf=_lightLossFactor_,candelaMul=_candelaMultiplier_,
                                                customLamp=customLamp_,lumFile=filenamefull,dirPath=dirpath)
            
elif not _iesFilePath:
    ghenv.Component.AddRuntimeMessage(w, "_iesFilePath is a required input. Please specify the filepath for an IES file.")
elif not _luminaireZone:
    ghenv.Component.AddRuntimeMessage(w, "_luminaireZone is a required input. Please connect the output of the IES Luminaire Array component to this module.")

