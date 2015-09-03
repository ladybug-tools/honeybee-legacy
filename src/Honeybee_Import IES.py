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
Provided by Honeybee 0.0.57
    
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
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
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


class HBIESSrf(object):
    def __init__(self, HBIES, count):
        self.objectType = "HBIES"
        self.type = HBIES.type
        self.hasChild = False
        self.name = HBIES.name
        if self.type == "polygon":
            self.pts = HBIES.pts[count]
        elif self.type == "sphere":
            self.cenPt = HBIES.cenPt
            self.radius = HBIES.radius
        self.geometry = HBIES.geometry[count]
        self.datFile = HBIES.datFile
        self.helpStr = HBIES.helpStr
        self.materialStr = HBIES.materialStr
        
    def checkIfScaledOrRotated(self, testBrep):
        if self.type == "polygon":
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
        elif self.type == "sphere":
            bbox = testBrep.GetBoundingBox(True)
            if (bbox.Max - bbox.Min).X/2 - self.radius > sc.doc.ModelAbsoluteTolerance:
                return True
            
            return False
        
        
    def __str__(self):
        return self.helpStr


class HBIESBase(object):
    
    def __init__(self, IESName, radFile, datFile):
        self.name = IESName #useful to check the name
        self.geometry = []
        self.readIESDATFile(datFile)
        # point, material string and help str
        self.readIESRADFile(radFile)
        # create geometry out of points
        # it won't work for complext IES. I need some examples for that
        if self.type == "polygon":
            self.createSrf()
        elif self.type == "sphere":
            self.createSphere()
        # make separate objects for each surface
        self.IESObjects = []
        for srfCount in range(len(self.geometry)):
            self.IESObjects.append(HBIESSrf(self, srfCount))
            
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
                    self.pts[lineNum] = []
                    for line in lines[lineCount + 1:]:
                        if line.startswith(self.name + "_light"):
                            break
                        if len(line.strip().split("\t")) == 3:
                            x, y, z = line.strip().split("\t")
                            point = rc.Geometry.Point3d(float(x), float(y), float(z))
                            self.pts[lineNum].append(point)
            
            elif self.type == "sphere":
                for lineNum, lineCount in enumerate(startLines):
                    for line in lines[lineCount + 1:]:
                        if line.startswith(self.name + "_light"):
                            break
                        if line.strip().startswith("4"):
                            n, x, y, z, r = line.strip().split(" ")
                            point = rc.Geometry.Point3d(float(x), float(y), float(z))
                            self.cenPt = point
                            self.radius = float(r)
            else:
                msg = self.type + " hasn't been implemented\n" + \
                      "Let us know and we will implement it."
                print msg
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, msg)
                
    def createSrf(self):
        for ptListKey in self.pts.keys():
            pts = self.pts[ptListKey]
            if len(pts) == 4:
                self.geometry.append(rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], pts[3], sc.doc.ModelAbsoluteTolerance))
            elif len(pts) == 3:
                self.geometry.append(rc.Geometry.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], sc.doc.ModelAbsoluteTolerance))
    
    def createSphere(self):
        self.geometry.append(rc.Geometry.Sphere(self.cenPt, self.radius).ToBrep())
        
    
    
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