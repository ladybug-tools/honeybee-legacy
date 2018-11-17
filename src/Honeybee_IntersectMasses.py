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
Use this component to take a list of closed breps (polysurfaces) that you intend to turn into HBZones and split their component surfaces to ensure that there are matching surfaces between each of the adjacent zones.
_
Matching surfaces and surface areas betweem adjacent zones are necessary to ensure that the conductive heat flow calculation occurs correctly across the surfaces in an energy simulation.
_
Note that the input here should be closed volumes that are adjacent to each other and touching.  They should not volumetrically overlap.
Also note that, while the component has been written in a manner that rarely fails if the input geometry obeys the provisions above, there are still some very complex cases that can be incorrect.
As such, it is recommended that you bake the output of this component and check it in Rhino before turning the breps into HBZones.  This component will get you most of the way there but these volumetric operations can be difficult to pull off with a surface modeler like Rhino so you should really check the output.
-
Provided by Honeybee 0.0.64

    Args:
        bldgMassesBefore: A list of closed breps (polysurfaces) that you intend to turn into HBZones that do not have perfectly matching surfaces between adjacent zones (this matching is needed to contruct a correct multi-zone energy model).
    Returns:
        bldgMassesAfter: The same input closed breps that have had their component surfaces split by adjacent polysurfaces to have matching surfaces between adjacent breps.  It is recommended that you bake this output and check it in Rhino before turning the breps into HBZones.
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh

tol = sc.doc.ModelAbsoluteTolerance

def isGeometricEquivalent(intersectCrv, massBrep):
    geometricEq = False
    isPlanar = True
    intersectCrvTest, intersectCrv = rc.Geometry.PolyCurve.TryGetPolyline(intersectCrv)
    
    if intersectCrvTest == True:
        intersectCrv = rc.Geometry.PolylineCurve(intersectCrv)
        
        intersectCrvVert = []
        for index in range(intersectCrv.PointCount - 1):
            intersectCrvVert.append(intersectCrv.Point(index))
        
        for srf in massBrep.Faces:
            srfBrep = srf.ToBrep()
            srfBrepVert = srfBrep.DuplicateVertices()
            
            if len(srfBrepVert) == len(intersectCrvVert):
                matchList = []
                for srfVert in srfBrepVert:
                    for intVert in intersectCrvVert:
                        if srfVert.X <= intVert.X+tol and srfVert.X >= intVert.X-tol and srfVert.Y <= intVert.Y+tol and srfVert.Y >= intVert.Y-tol and srfVert.Z <= intVert.Z+tol and srfVert.Z >= intVert.Z-tol:
                            matchList.append(1)
                
                if len(matchList) == len(srfBrepVert):
                    geometricEq = True
    
    if intersectCrv == None:
        isPlanar = False
    elif rc.Geometry.AreaMassProperties.Compute(intersectCrv) == None:
        isPlanar = False
    
    return geometricEq, isPlanar

def isSrfGeoEquivalent(intersectCrv, srf):
    geometricEq = False
    
    intersectCrvVert = []
    for crv in intersectCrv.DuplicateSegments():
        intersectCrvVert.append(crv.PointAtStart)
    
    srfBrep = srf.ToBrep()
    srfBrepVert = srfBrep.DuplicateVertices()
    
    if len(srfBrepVert) == len(intersectCrvVert):
        matchList = []
        for srfVert in srfBrepVert:
            for intVert in intersectCrvVert:
                if srfVert.X <= intVert.X+tol and srfVert.X >= intVert.X-tol and srfVert.Y <= intVert.Y+tol and srfVert.Y >= intVert.Y-tol and srfVert.Z <= intVert.Z+tol and srfVert.Z >= intVert.Z-tol:
                    matchList.append(1)
        
        if len(matchList) == len(srfBrepVert):
            geometricEq = True
    
    return geometricEq



def intersectMasses(bldgNum, building, otherBldg):
    intersectLines = rc.Geometry.Intersect.Intersection.BrepBrep(building, otherBldg, sc.doc.ModelAbsoluteTolerance)[1]
    joinedLines = rc.Geometry.Curve.JoinCurves(intersectLines, sc.doc.ModelAbsoluteTolerance)
    
    #Make sure that the intersection above was not just a single line.
    if len(joinedLines) > 0:
        joinedLine = joinedLines[0]
        try: segmentCt = joinedLine.SpanCount
        except: segmentCt = 1
        
        if segmentCt > 1:
            #Test whether the infersection is of a geometrically equivalent brep face.
            geometricEq, isPlanar = isGeometricEquivalent(joinedLine, building)
            
            #If the intersection is not geometrically equivalent to a brep face, there is likely an intersection. Use the harder core function of making a boolean difference.
            if geometricEq == False:
                if isPlanar == True:
                    # To be sure that there's no geometric equivalence, we'll do one final test to see if there are matching area and centroids.
                    jlProps = rc.Geometry.AreaMassProperties.Compute(joinedLine)
                    jlCenter = jlProps.Centroid
                    jlArea = jlProps.Area
                    faceMatchInit = False
                    for face in building.Faces:
                        faceProps = rc.Geometry.AreaMassProperties.Compute(face)
                        faceCent = faceProps.Centroid
                        faceArea = faceProps.Area
                        if faceCent.DistanceTo(jlCenter) < sc.doc.ModelAbsoluteTolerance and jlArea-faceArea < sc.doc.ModelAbsoluteTolerance and jlArea-faceArea > -sc.doc.ModelAbsoluteTolerance:
                            faceMatchInit = True
                else:
                    faceMatchInit = False
                
                if faceMatchInit == False:
                    #Try splitting the faces of the brep with the intersection curve.
                    newBldgBreps = []
                    for srf in building.Faces:
                        newBrep = srf.Split([joinedLine], sc.doc.ModelAbsoluteTolerance)
                        if newBrep.Faces.Count > building.Faces.Count:
                            if isPlanar == True:
                                faceMatch = False
                                for face in newBrep.Faces:
                                    faceProp2 = rc.Geometry.AreaMassProperties.Compute(face)
                                    faceCent2 = faceProp2.Centroid
                                    faceArea2 = faceProp2.Area
                                    if faceCent2.DistanceTo(jlCenter) < sc.doc.ModelAbsoluteTolerance and jlArea-faceArea2 < sc.doc.ModelAbsoluteTolerance and jlArea-faceArea2 > -sc.doc.ModelAbsoluteTolerance:
                                        faceMatch = True
                                if faceMatch == True:
                                    newBldgBreps.append(srf.Split([joinedLine], sc.doc.ModelAbsoluteTolerance))
                            else:
                                faceMatch = False
                                for face in newBrep.Faces:
                                    srfEq = isSrfGeoEquivalent(joinedLine, face)
                                    if srfEq == True and face.IsPlanar() == True:
                                        faceMatch = True
                                    elif srfEq == False and face.IsPlanar() == False:
                                        faceMatch = True
                                if faceMatch == True:
                                    newBldgBreps.append(srf.Split([joinedLine], sc.doc.ModelAbsoluteTolerance))
                    
                    try:
                        newBuilding = rc.Geometry.Brep.JoinBreps(newBldgBreps, sc.doc.ModelAbsoluteTolerance)[0]
                        building = newBuilding
                    except:
                        pass
    
    return building


def main(bldgMassesBefore):
    
    buildingDict = {}
    intersectedBldgs = []
    for bldgCount, bldg in enumerate(bldgMassesBefore):
        buildingDict[bldgCount] = bldg
    
    
    for bldgNum, building in buildingDict.items():
        try:
            #Intersect the geomtry with all buildings in the list after it.
            for otherBldg in  bldgMassesBefore[:bldgNum]:
                building = intersectMasses(bldgNum, building, otherBldg)
                #Update the dictionary with the new split geometry.
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
            
            #Intersect the geomtry with all buildings in the list before it.
            for otherBldg in  bldgMassesBefore[bldgNum+1:]:
                building = intersectMasses(bldgNum, building, otherBldg)
                #Update the dictionary with the new split geometry.
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
        except:
            buildingDict[bldgNum] = building
            bldgMassesBefore[bldgNum] = building
            warning = "Failed to intersect correctly.  Some output geometry may not be intersected."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            print warning
        
    for bldgNum, building in buildingDict.items():
        intersectedBldgs.append(building)
    
    if len(bldgMassesBefore) == len(intersectedBldgs):
        intersectedBldgs = bldgMassesBefore
    
    return intersectedBldgs



success = True
Hzones = False

if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): success = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): success = False
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        success = False
    
    if success == True:
        hb_hive = sc.sticky["honeybee_Hive"]()
        try:
            for HZone in _bldgMassesBefore:
                zone = hb_hive.callFromHoneybeeHive([HZone])[0]
                Hzones = True
        except: pass
    
    if Hzones == True:
        warning = "This component only works with raw Rhino brep geometry and not HBZones.  Use this component before you turn your breps into HBZones."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    warning = "You should first let Honeybee fly!"
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning)

if _bldgMassesBefore and _bldgMassesBefore[0]!=None and Hzones == False:
    bldgMassesAfter = main(_bldgMassesBefore)