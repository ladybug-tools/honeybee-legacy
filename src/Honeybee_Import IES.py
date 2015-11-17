#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Import IES files

-
Provided by Honeybee 0.0.58
    
    Args:
        _iesFilePath: Filepath to a valid IES file
        newName_: Optional new name for the ies file
        modifier_: Optional number between 0 and 1 which will be "multiplied by "all output quantities. This is the best way to scale fixture brightness for different lamps, but care should be taken when this option is applied to multiple files."
        _runIt: Set to True to import the IES file
    Returns:
        HB_IES: HB IES object. Do not scale or rotate this object. Just locate it in the right place
"""

ghenv.Component.Name = "Honeybee_Import IES"
ghenv.Component.NickName = 'importIES'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import subprocess
import uuid
from pprint import pprint


class HBIESRing(object):
    
    def __init__(self, HBIES):
        
        self.objectType = "HBIES"
        self.type = HBIES.type
        self.hasChild = False
        self.name = HBIES.name        
        
        self.datFile = HBIES.datFile
        self.helpStr = HBIES.helpStr
        self.materialStr = HBIES.materialStr
        self.geometryStr = ""
        
        self.cenPt = rc.Geometry.Point3d.Origin
        self.inRadius = 0
        self.outRadius = 0
        self.normal = rc.Geometry.Vector3d.ZAxis
        
    def createGeometry(self):
        # create base plane
        plane = rc.Geometry.Plane(self.cenPt, self.normal)
        
        # create surface
        inCircle = rc.Geometry.Circle(plane, self.inRadius).ToNurbsCurve()
        outCircle = rc.Geometry.Circle(plane, self.outRadius).ToNurbsCurve()
        
        # add surface to geometry
        self.geometry= rc.Geometry.Brep.CreatePlanarBreps([inCircle, outCircle])[0]
    
    def checkIfScaledOrRotated(self, testBrep):
        bbox = testBrep.GetBoundingBox(True)
        if (bbox.Max - bbox.Min).X/2 - self.outRadius > sc.doc.ModelAbsoluteTolerance:
            return True
        
        return False
    
    def getRADGeometryStr(self, IESName, IESBrep):
        
        self.geometryStr = self.geometryStr.replace("#name", self.name, 1)
        
        center = IESBrep.GetBoundingBox(True).Center
        
        
        return self.geometryStr.replace("#name", IESName) + \
               "8\n" + \
               str(center.X) + " " + str(center.Y) + " " + str(center.Z) + "\n" + \
               str(self.normal.X) + " " + str(self.normal.Y) + " " + str(self.normal.Z) + "\n" + \
               str(self.inRadius) + " " + str(self.outRadius) + "\n"
        
    def __str__(self):
        return self.helpStr

class HBIESPlane(object):
    
    def __init__(self, HBIES):
        
        self.objectType = "HBIES"
        self.type = HBIES.type
        self.hasChild = False
        self.name = HBIES.name        
        
        self.datFile = HBIES.datFile
        self.helpStr = HBIES.helpStr
        self.materialStr = HBIES.materialStr
        self.geometryStr = ""
        
        self.pts = []
        
    def createGeometry(self):
        pts = self.pts
        
        if len(pts) == 4:
            self.geometry = rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], pts[3], sc.doc.ModelAbsoluteTolerance)
        elif len(pts) == 3:
            self.geometry = rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], sc.doc.ModelAbsoluteTolerance)
    
    def checkIfScaledOrRotated(self, testBrep):
        #find the points
        points = testBrep.DuplicateVertices()
        # create the vectors
        vectors = []
        for ptCount in range(len(points)):
            vector = rc.Geometry.Vector3d(points[ptCount] - self.pts[ptCount])
            vectors.append(vector)
        
        # if they are all parallel
        for vectorCount in range(len(vectors)-1):
            vectorAngle = rc.Geometry.Vector3d.VectorAngle(vectors[vectorCount], vectors[vectorCount + 1])
            
            if vectors[vectorCount].Length != vectors[vectorCount + 1].Length or vectorAngle > sc.doc.ModelAngleToleranceRadians:
                return True
        
        return False
    
    def getRADGeometryStr(self, IESName, IESBrep):
        
        self.geometryStr = self.geometryStr.replace("#name", self.name, 1)

        coordinates = IESBrep.DuplicateVertices()
        
        srfStr =  self.geometryStr.replace("#name", IESName) + \
                `(len(coordinates)*3)` + "\n"
            
        for  pt in coordinates:
            srfStr += '%.4f'%pt.X + '  ' + '%.4f'%pt.Y + '  ' + '%.4f'%pt.Z + '\n'
        
        return srfStr + '\n'
            
    def __str__(self):
        return self.helpStr

class HBIESSphere(object):
    
    def __init__(self, HBIES):
        
        self.objectType = "HBIES"
        self.type = HBIES.type
        self.hasChild = False
        self.name = HBIES.name        
        
        self.datFile = HBIES.datFile
        self.helpStr = HBIES.helpStr
        self.materialStr = HBIES.materialStr
        self.geometryStr = ""
        
        self.cenPt = rc.Geometry.Point3d.Origin
        self.radius = 0
        
    def createGeometry(self):
        self.geometry = rc.Geometry.Sphere(self.cenPt, self.radius).ToBrep()
    
    def checkIfScaledOrRotated(self, testBrep):
        bbox = testBrep.GetBoundingBox(True)
        if (bbox.Max - bbox.Min).X/2 - self.radius > sc.doc.ModelAbsoluteTolerance:
            return True
        
        return False
    
    def getRADGeometryStr(self, IESName, IESBrep):
        
        self.geometryStr = self.geometryStr.replace("#name", self.name, 1)
        
        center = IESBrep.GetBoundingBox(True).Center
        
        return self.geometryStr.replace("#name", IESName) + \
                "4 " + `center.X` + " " + `center.Y` + " " + `center.Z` + " " + str(self.radius) + "\n\n"
        
    def __str__(self):
        return self.helpStr


class HBIESBase(object):
    
    def __init__(self, IESName, radFile, datFile):
        
        self.name = IESName #useful to check the name
        self.IESObjects = [] #collection of objects
        
        self.readIESDATFile(datFile)
        
        # point, material string and help str
        self.readIESRADFile(radFile)
        
    def readIESDATFile(self, datFile):
        with open(datFile, "r") as inDatFile:
            self.datFile = "".join(inDatFile.readlines())
        
    def readIESRADFile(self, radFile):
        self.helpStr = "Honeybee IES Object\n"
        endWithMaterials = False
        self.materialStr = ""
        self.pts = {}
        with open(radFile, "r") as radin:
            lines = radin.readlines()
            startLines = []
            for lineCount, line in enumerate(lines):
                if line.startswith("#"):
                    self.helpStr += line
                elif line.startswith(self.name + "_light"):
                    # get the type
                    self.type = line.strip().split(" ")[1]
                    endWithMaterials = True
                    startLines.append(lineCount)
                elif not endWithMaterials:
                    self.materialStr += line
            
        # this just works for simple surfaces
        # I will write a more sophisticated function later
        if self.type == "polygon":
            for lineNum, lineCount in enumerate(startLines):
                # create new plane
                IESObject = HBIESPlane(self)
                for lCount, line in enumerate(lines[lineCount + 1:]):
                    IESObject.geometryStr += lines[lineCount + lCount].replace(self.name, "#name")
                    
                    if line.startswith(self.name + "_light"):
                        break
                    try:
                        if int(line.strip())!=0:
                            numOfPts = int(int(line.strip())/3)
                            for ptCount in range(numOfPts):
                                x, y, z = lines[lineCount + lCount + ptCount + 2].strip().split("\t")
                                point = rc.Geometry.Point3d(float(x), float(y), float(z))
                                IESObject.pts.append(point)
                    
                            # create geometry
                            IESObject.createGeometry()
                
                            # add to IES Objects
                            self.IESObjects.append(IESObject)
                            break
                    except Exception, e:
                        print e
                        pass
        elif self.type == "sphere":
            for lineNum, lineCount in enumerate(startLines):
                
                # create new sphere IES
                IESObject = HBIESSphere(self)
                
                for lCount, line in enumerate(lines[lineCount + 1:]):
                    IESObject.geometryStr += lines[lineCount + lCount].replace(self.name, "#name") + "\n"
                    
                    if line.startswith(self.name + "_light"):
                        break
                    if line.strip().startswith("4"):
                        n, x, y, z, r = line.strip().split(" ")
                        IESObject.cenPt = rc.Geometry.Point3d(float(x), float(y), float(z))
                        IESObject.radius = float(r)
                
                        # create geometry
                        IESObject.createGeometry()
                        # add to IES Objects
                        self.IESObjects.append(IESObject)
                        break
                
        elif self.type == "ring":
            for lineNum, lineCount in enumerate(startLines):
                # create a ring
                IESObject = HBIESRing(self)
                
                for lCount, line in enumerate(lines[lineCount + 1:]):
                    IESObject.geometryStr += lines[lineCount + lCount].replace(self.name, "#name") + "\n"
                    
                    if line.startswith(self.name + "_light"):
                        break
                    if line.strip().startswith("8"):
                        cenX, cenY, cenZ = lines[lineCount + lCount + 2].strip().split(" ")
                        normX, normY, normZ = lines[lineCount + lCount + 2].strip().split(" ")
                        inRadius, outRadius = lines[lineCount + lCount + 4].strip().split(" ")
                        
                        IESObject.inRadius = float(inRadius)
                        IESObject.outRadius = float(outRadius)
                        IESObject.cenPt = rc.Geometry.Point3d(float(cenX), float(cenY), float(cenZ))
                        IESObject.normal = rc.Geometry.Vector3d(float(normX), float(normY), float(normZ))
                        
                        # create geometry
                        IESObject.createGeometry()
                        
                        # add to IES Objects
                        self.IESObjects.append(IESObject)
                        break
            
        else:
            msg = self.type + " hasn't been implemented\n" + \
                  "Let us know and we will implement it."
            print msg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, msg)


def runCmdAndGetTheResults(command, shellKey = True):
    p = subprocess.Popen(["cmd", command], shell=shellKey, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # p.kill()
    return out, err

def main(iesFilePath, newName, modifier):
    
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, msg)
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
    
    if modifier!=None and not 0 <= modifier <= 1:
        msg = "Modifier should be a number between 0 and 1"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    hb_folders = sc.sticky["honeybee_folders"]
    hb_RADPath = hb_folders["RADPath"]
    hb_RADLibPath = hb_folders["RADLibPath"]
    
    # make sure this is an IES file
    if not os.path.isfile(iesFilePath) or not iesFilePath.lower().endswith(".ies"):
        msg = "input file is not a valid ies file."
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    # folder name
    dirName = os.path.dirname(iesFilePath)
    
    # IES file name and extention
    iesName = os.path.basename(iesFilePath)
    
    # check if user provided a new name
    if newName == None: newName = iesName.split(".")[0]

    # check if user provided a new name
    if modifier == None: modifier = 1.0

    # conversion line
    pathStr = "SET RAYPATH=.;" + hb_RADLibPath + "\nPATH=" + hb_RADPath + ";$PATH\n"
    ies2radLine = "ies2rad -o "
    
    # add input file
    ies2radLine += newName
    
    # add a multiplier factor
    ies2radLine += " -m " + str(modifier) + " " + iesName
    
    # write a batch file
    batchFilePath = os.path.join(dirName, newName + "_ies2rad.bat")
    with open(batchFilePath, "w") as ies2radOut:
        ies2radOut.write(pathStr)
        ies2radOut.write("cd " + dirName + "\n")
        ies2radOut.write(ies2radLine)
    
    # execute batch file
    #os.system(batchFilePath)
    runCmdAndGetTheResults( "/c " + batchFilePath)
    
    # result files
    radFile = os.path.join(dirName, newName + ".rad")
    datFile = os.path.join(dirName, newName + ".dat")
    
    if not os.path.isfile(radFile) or not os.path.isfile(datFile):
        msg = "Can't find the results at: " + radFile + ".\n" + \
              "You can run " + batchFilePath + " manually to check the error."
              
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
        
    HB_IES = HBIESBase(newName, radFile, datFile).IESObjects
    
    # add to HB Hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    HBIESSrf = []
    for HB_IESSrf in HB_IES:
        try:
            HBIESSrf.append(hb_hive.addToHoneybeeHive([HB_IESSrf], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))[0])
        except:
            pass
            
    return HBIESSrf

if _runIt:
    result = main(_iesFilePath, newName_, modifier_)
    if result!=-1: HB_IES = result