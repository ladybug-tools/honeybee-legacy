# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Intersect masses
-
Provided by Honeybee 0.0.56

    Args:
        bldgMassesBefore: ...
    Returns:
        bldgMassesAfter: ...
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
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