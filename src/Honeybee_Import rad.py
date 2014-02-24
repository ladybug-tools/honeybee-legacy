# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Import a rad file to gh
This component is just a proof of concept for now and needs major modifications

-
Provided by Honeybee 0.0.51

    Args:
        input1: ...
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Honeybee_Import rad"
ghenv.Component.NickName = 'importRad'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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
    
    RADMaterialList = DataTree[System.Object]()
    geometries = DataTree[System.Object]()
    if len(surfaces) > 0:
        # removeOutputs()
        outputNum = 0
        for mat, srfs in surfaces.items():
            RADMaterialList.Add(mat, GH_Path(outputNum))
            geometries.AddRange(srfs, GH_Path(outputNum))
            outputNum+=1

#outputCount = ghenv.Component.Params.Output.Count
# if not radFile and  outputCount > 1:
#    removeOutputs()
