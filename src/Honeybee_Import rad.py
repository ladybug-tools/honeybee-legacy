#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Import a rad file to gh
This component is just a proof of concept for now and needs major modifications

-
Provided by Honeybee 0.0.64

    Args:
        _radianceFile: File path to radiance file
    Returns:
        RADMaterials: List of materials
        RADSurfaces: List of surfaces
"""
ghenv.Component.Name = "Honeybee_Import rad"
ghenv.Component.NickName = 'importRad'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
telorance = sc.doc.ModelAbsoluteTolerance


def radLine2Srf(ptCrd):
    
    def isCurveDup(crv, crvList):
        """This definition checks if a curve with the same start and end point
        is in the list """
        ptList = [crv.PointAtStart, crv.PointAtEnd]
        count = 0
        for c in crvList:
            # if len(crvList)>5: print c.PointAtStart,'           ', c.PointAtEnd, (c.PointAtStart in ptList) and (c.PointAtEnd in ptList)
            if (c.PointAtStart in ptList) and (c.PointAtEnd in ptList): count += 1
        # if len(crvList)>5: print count
        if count > 1: return True
        return False
    
    ptList = []
    for ptCount in range(0,len(ptCrd),3):
        ptList.append(rc.Geometry.Point3d(ptCrd[ptCount], ptCrd[ptCount+1], ptCrd[ptCount+2]))
    # make sure all the points are on the same plane
    #listLength = len(ptList)
    #tempPlane = rc.Geometry.Plane(ptList[0], ptList[int(1)], ptList[int(round(listLength/2))])
    ptOnPlane = ptList
    #[ptOnPlane.append(tempPlane.ClosestPoint(pt)) for pt in ptList]
    
    # it might look stupid but rc.Geometry.Polyline(ptOnPlane) doesn't work for self intersecting polylines
    if ptOnPlane[0]!= ptOnPlane[-1]: ptOnPlane.append(ptOnPlane[0])
    pl = rc.Geometry.Polyline(ptOnPlane).ToNurbsCurve()
    
    # print pl
    if showWireframe: return pl
    if len(ptOnPlane) == 5:
        srf = rc.Geometry.Brep.CreateFromCornerPoints(ptOnPlane[0], ptOnPlane[1], ptOnPlane[2],ptOnPlane[3], sc.doc.ModelAbsoluteTolerance)
        return srf
    elif len(ptOnPlane) == 4:
        srf = rc.Geometry.Brep.CreateFromCornerPoints(ptOnPlane[0], ptOnPlane[1], ptOnPlane[2], sc.doc.ModelAbsoluteTolerance)
        return srf
    
    plSeg = pl.DuplicateSegments()
    
    borderLines = []
    for seg in plSeg:
        if not isCurveDup(seg, plSeg): borderLines.append(seg)
    border = rc.Geometry.Curve.JoinCurves(borderLines)
    srf = rc.Geometry.Brep.CreatePlanarBreps(border)
    if srf: return srf[0]
    else: return pl

def removeOutputs():
    while ghenv.Component.Params.Output.Count > 1:
        ghenv.Component.Params.UnregisterOutputParameter(ghenv.Component.Params.Output[1])
        ghenv.Component.ExpireSolution(True)
        #ghenv.Component.OnSolutionExpire(True)
        ghenv.Component.Attributes.Owner.OnSolutionExpire(True)
        

radFile = _radianceFile
showWireframe = False

if radFile:
    file = open(radFile, 'r')
    fileAllJoined = ""
    #clean the idf file
    for line in file:
        if line != []:
            line = line.replace("\n",",")
            line = line.replace("\t",",")
            line = line.replace(" ",",")
            if '#' in line: line = ""
            if line != "": fileAllJoined  = fileAllJoined + line.replace(" ", ",")
    file.close()
    
    fileSeparated = []
    nfile = fileAllJoined.split(",")
    for seg in nfile:
        if seg != "": fileSeparated.append(seg)
    #print fileSeparated
    surfaces = {}
    for segCount, seg in enumerate(fileSeparated):
        # I should fix this code later! This is really poor written.
        if seg.upper() == "polygon".upper():
            material = fileSeparated[segCount - 1]
            numPt = int(fileSeparated[segCount + 4])
            ptCrd = fileSeparated[segCount + 5: segCount + 5 + numPt]
            ptCrd = [float(pt) for pt in ptCrd]
            srf = radLine2Srf(ptCrd)
            if not surfaces.has_key(material): surfaces[material] = []
            surfaces[material].append(srf)
    
    RADMaterials = DataTree[System.Object]()
    RADSurfaces = DataTree[System.Object]()
    if len(surfaces) > 0:
        # removeOutputs()
        outputNum = 0
        for mat, srfs in surfaces.items():
            RADMaterials.Add(mat, GH_Path(outputNum))
            RADSurfaces.AddRange(srfs, GH_Path(outputNum))
            outputNum+=1

#outputCount = ghenv.Component.Params.Output.Count
# if not radFile and  outputCount > 1:
#    removeOutputs()
