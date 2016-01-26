#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Provided by Honeybee 0.0.59

    Args:
        bldgMassesBefore: A list of closed breps (polysurfaces) that you intend to turn into HBZones that do not have perfectly matching surfaces between adjacent zones (this matching is needed to contruct a correct multi-zone energy model).
    Returns:
        bldgMassesAfter: The same input closed breps that have had their component surfaces split by adjacent polysurfaces to have matching surfaces between adjacent breps.  It is recommended that you bake this output and check it in Rhino before turning the breps into HBZones.
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
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
    
    return geometricEq

def getSrfCenPtandNormal(surface):
        
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = surface.PointAt(centerU, centerV)
        normalVector = surface.NormalAt(centerU, centerV)
        
        normalVector.Unitize()
        return centerPt, normalVector


def main(bldgMassesBefore):
    
    buildingDict = {}
    intersectedBldgs = []
    for bldgCount, bldg in enumerate(bldgMassesBefore):
        buildingDict[bldgCount] = bldg
    
    
    for bldgNum, building in buildingDict.items():
        try:
            #Intersect the geomtry with all buildings in the list after it.
            for otherBldg in  bldgMassesBefore[:bldgNum]:
                intersectLines = rc.Geometry.Intersect.Intersection.BrepBrep(building, otherBldg, sc.doc.ModelAbsoluteTolerance)[1]
                joinedLines = rc.Geometry.Curve.JoinCurves(intersectLines, sc.doc.ModelAbsoluteTolerance)
                
                #Make sure that the intersection above was not just a single line.
                if len(joinedLines) > 0:
                    try: segmentCt = joinedLines[0].SegmentCount
                    except: segmentCt = 1
                    
                    if segmentCt > 1:
                            #Test whether the infersection is of a geometrically equivalent brep face.
                            geometricEq = isGeometricEquivalent(joinedLines[0], building)
                            
                            #If the intersection is not geometrically equivalent to a brep face, there is an intersection. Use the harder core function of making a boolean difference.
                            if geometricEq == False:
                                finalBuilding = None
                                intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
                                if intersectedBuilding:
                                    if intersectedBuilding[0].IsValid: finalBuilding = intersectedBuilding[0]
                                
                                #If the boolean difference has caused volumes to stick together, use the alternate function of splitting the faces with the intersection curve.
                                if finalBuilding:
                                    finalBldgVol = rc.Geometry.VolumeMassProperties.Compute(finalBuilding).Volume
                                    originalBldgVol = rc.Geometry.VolumeMassProperties.Compute(building).Volume
                                    
                                    if finalBldgVol <= originalBldgVol + (tol) and finalBldgVol >= originalBldgVol - tol:
                                        building = finalBuilding
                                    else:
                                        #Try splitting the faces of the brep with the intersection curve (this is the fastest method but doesn't always work well).
                                        newBldgBreps = []
                                        for srf in building.Faces:
                                            newBldgBreps.append(srf.Split(joinedLines, sc.doc.ModelAbsoluteTolerance))
                                        newBuilding = rc.Geometry.Brep.JoinBreps(newBldgBreps, sc.doc.ModelAbsoluteTolerance)[0]
                                        
                                        #If the splitting of the faces did not produce any extra surfaces, use a last-ditch effort of creatig a brep to split the surface.
                                        if newBuilding.Faces.Count == building.Faces.Count:
                                            if finalBldgVol <= originalBldgVol + (tol) and finalBldgVol >= originalBldgVol - tol:
                                                building = finalBuilding
                                            else:
                                                newBldgBreps = []
                                                for count, srf in enumerate(building.Faces):
                                                    centPt, normalVec = getSrfCenPtandNormal(srf)
                                                    extruIntersect = rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(joinedLines[0], normalVec))
                                                    faceSrf = srf.Split(joinedLines, sc.doc.ModelAbsoluteTolerance)
                                                    splitSrf = rc.Geometry.Brep.Split(faceSrf, extruIntersect, sc.doc.ModelAbsoluteTolerance)
                                                    if len(splitSrf) > 0: newBldgBreps.extend(splitSrf)
                                                    else: newBldgBreps.append(faceSrf)
                                                building = rc.Geometry.Brep.JoinBreps(newBldgBreps, sc.doc.ModelAbsoluteTolerance)[0]
                                        else:
                                            building = newBuilding
                
                #Update the dictionary with the new split geometry.
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
            
            #Intersect the geomtry with all buildings in the list before it.
            for otherBldg in  bldgMassesBefore[bldgNum+1:]:
                intersectLines = rc.Geometry.Intersect.Intersection.BrepBrep(building, otherBldg, sc.doc.ModelAbsoluteTolerance)[1]
                joinedLines = rc.Geometry.Curve.JoinCurves(intersectLines, sc.doc.ModelAbsoluteTolerance)
                
                #Make sure that the intersection above was not just a single line.
                if len(joinedLines) > 0:
                    try: segmentCt = joinedLines[0].SegmentCount
                    except: segmentCt = 1
                    
                    if segmentCt > 1:
                            #Test whether the infersection is of a geometrically equivalent brep face.
                            geometricEq = isGeometricEquivalent(joinedLines[0], building)
                            
                            #If the intersection is not geometrically equivalent to a brep face, there is an intersection. Use the harder core function of making a boolean difference.
                            if geometricEq == False:
                                finalBuilding = None
                                intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
                                if intersectedBuilding:
                                    if intersectedBuilding[0].IsValid: finalBuilding = intersectedBuilding[0]
                                
                                #If the boolean difference has caused volumes to stick together, use the alternate function of splitting the faces with the intersection curve.
                                if finalBuilding:
                                    finalBldgVol = rc.Geometry.VolumeMassProperties.Compute(finalBuilding).Volume
                                    originalBldgVol = rc.Geometry.VolumeMassProperties.Compute(building).Volume
                                    
                                    if finalBldgVol <= originalBldgVol + (tol) and finalBldgVol >= originalBldgVol - tol:
                                        building = finalBuilding
                                    else:
                                        #Try splitting the faces of the brep with the intersection curve (this is the fastest method but doesn't always work well).
                                        newBldgBreps = []
                                        for srf in building.Faces:
                                            newBldgBreps.append(srf.Split(joinedLines, sc.doc.ModelAbsoluteTolerance))
                                        newBuilding = rc.Geometry.Brep.JoinBreps(newBldgBreps, sc.doc.ModelAbsoluteTolerance)[0]
                                        
                                        #If the splitting of the faces did not produce any extra surfaces, use a last-ditch effort of creatig a brep to split the surface.
                                        if newBuilding.Faces.Count == building.Faces.Count:
                                            if finalBldgVol <= originalBldgVol + (tol) and finalBldgVol >= originalBldgVol - tol:
                                                building = finalBuilding
                                            else:
                                                newBldgBreps = []
                                                for count, srf in enumerate(building.Faces):
                                                    centPt, normalVec = getSrfCenPtandNormal(srf)
                                                    extruIntersect = rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(joinedLines[0], normalVec))
                                                    faceSrf = srf.Split(joinedLines, sc.doc.ModelAbsoluteTolerance)
                                                    splitSrf = rc.Geometry.Brep.Split(faceSrf, extruIntersect, sc.doc.ModelAbsoluteTolerance)
                                                    if len(splitSrf) > 0: newBldgBreps.extend(splitSrf)
                                                    else: newBldgBreps.append(faceSrf)
                                                building = rc.Geometry.Brep.JoinBreps(newBldgBreps, sc.doc.ModelAbsoluteTolerance)[0]
                                        else:
                                            building = newBuilding
                        
                #Update the dictionary with the new split geometry.
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
        except:
            buildingDict[bldgNum] = building
            bldgMassesBefore[bldgNum] = building
            
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