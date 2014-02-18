# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert Mass to Honeybee Zones
-
Provided by Honeybee 0.0.50

    Args:
        _bldgMasses: List of closed Breps
        bldgsFlr2FlrHeights_: List of buildings floor heights for the geometries
        bldgsFloorProgram_: List of building floor programs. Default schedule, construction, and HVAC system will be applied based on the program
                           In this version of Honeybee just leave it empty as it won't effect Daylighting simulation.
        isConditioned_: List of Booleans to indicate if the space is conditioned
        maximumRoofAngle_: Maximum angle from z vector that the surface will be assumed as a roof. Default is 30 degrees
        projectName_: Name of the project
        _createHoneybeeZones: Set Boolean to True to generate the zones
    Returns:
        readMe!: ...
        HBZones: Honeybee zones in case of success
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import uuid

#HBLibrariesPath = r"C:\Users\MSadeghipourroudsari\Dropbox\ladybug\honeybee\src"
#if HBLibrariesPath not in sys.path: sys.path.append(HBLibrariesPath)

#from honeybee.geometry import *
#from honeybee.honeybee import *

ghenv.Component.Name = 'Honeybee_Masses2Zones'
ghenv.Component.NickName = 'Mass2Zone'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

tolerance = sc.doc.ModelAbsoluteTolerance
import math


class Export2EP(object):
    # generate floor heights
    def getFloorHeights(self, flr2flrHeights, totalHeights, maxHeights, conversionFac = 1, firstFloorHeight = 0, rep = False):
        flrHeights = [firstFloorHeight]
        for height in flr2flrHeights:
            if '@' in height:
                floorH = float(height.split('@')[1])
                try: numOfFlr = int(height.split('@')[0])
                except:  numOfFlr = int((totalHeights - flrHeights[-1])/floorH)
            else:
                numOfFlr = 1
                floorH = float(height)
            if floorH!=0:
                if numOfFlr != 1 and rep:
                    print 'There are ' + `numOfFlr` + ' floors with height of ' + `floorH` + ' m.'
                elif rep:
                    print 'There is a floor with height of ' + `floorH` + ' m.'
                
                for floors in range(numOfFlr): flrHeights.append(flrHeights[-1] + floorH)
        #print flrHeights[-1] - maxHeights
        #if maxHeights - flrHeights[-1] < (0.5/conversionFac): flrHeights.pop()
        return flrHeights # list of floor heights
    
    def getFloorCrvs(self, buildingMass, floorHeights):
        basePoint = rc.Geometry.Point3d.Origin
        contourCrvs = []; splitters = []
        bbox = buildingMass.GetBoundingBox(True)
        for h in floorHeights:
            floorBasePt = rc.Geometry.Point3d.Add(basePoint, rc.Geometry.Vector3d(0,0,h))
            sectionPlane = rc.Geometry.Plane(floorBasePt, rc.Geometry.Vector3d.ZAxis)
            crvList = rc.Geometry.Brep.CreateContourCurves(buildingMass, sectionPlane)
            if crvList:
                #print len(crvList)
                [contourCrvs.append(crv) for crv in crvList]
                
                # This part is based on one of David Rutten's scritp
                bool, extU, extV = sectionPlane.ExtendThroughBox(bbox)
                # extend the plane for good measure
                extU.T0 -= 1.0
                extU.T1 += 1.0
                extV.T0 -= 1.0
                extV.T1 += 1.0
                splitters.append(rc.Geometry.PlaneSurface(sectionPlane, extU, extV))
                #print contourCrvs
            
        # mathc Curves Directions [I haven't really used it so far. Potentially useful]
        if len(contourCrvs)!= 0:
            refCrv = contourCrvs[0]
            crvDir = []
            for crv in contourCrvs:
                crvDir.append(rc.Geometry.Curve.DoDirectionsMatch(refCrv, crv))
            
        return contourCrvs , splitters #, crvDir
        
    def getCrvArea(self, crv, p= False):
        try:
            massP = crv.AreaMassProperties.Compute()
            area = massP.Area
            massP.Dispose()
        except:
            try:
                ghCrv = ghdoc.Objects.AddCurve(crv)
                if not rs.IsCurveClosed(ghCrv) and rs.IsCurveClosable(ghCrv):
                    ghCrv = rs.CloseCurve(ghCrv, -1)
                    print 'one open curve found and closed for area calculation...'
                elif not rs.IsCurveClosed(ghCrv):
                    endPt = rs.CurveEndPoint(ghCrv)
                    startPt = rs.CurveStartPoint(ghCrv)
                    newLine = rs.AddLine(startPt, endPt)
                    ghCrv = rs.JoinCurves([ghCrv, newLine], True)
                    print 'one open curve found and closed for area calculation...'
                area = rs.Area(ghCrv)
            
                try: rs.DeleteObject(ghCrv)
                except: pass
            except: print "can't calculate the area!"; area = 0
        if p: print area
        return area
    
    def getSrfAreaAndCenPt(self, surface, calArea = True):
        MP = rc.Geometry.AreaMassProperties.Compute(surface)
        area = None
        if MP:
            if calArea: area = MP.Area
            centerPt = MP.Centroid
            MP.Dispose()
            # cenPtU, cenPtV = rc.Geometry.Brep.
            
            try:
                bool, centerPtU, centerPtV = surface.ClosestPoint(centerPt)
                normalVector = surface.NormalAt(centerPtU, centerPtV)
            except:
                bool, centerPtU, centerPtV = surface.Faces[0].ClosestPoint(centerPt)
                normalVector = surface.Faces[0].NormalAt(centerPtU, centerPtV)
            return area, centerPt, normalVector
        return None, None, None

    def getCrvAreaAndCenPt(self, curve, calArea = True):
        MP = rc.Geometry.AreaMassProperties.Compute(curve)
        
        area = -1
        centerPt = rc.Geometry.Point3d.Origin
        if MP:
            if calArea: area = MP.Area
            centerPt = MP.Centroid
            MP.Dispose()
        
        return area, centerPt


    def checkZoneNormalsDir(self, zone):
        """check normal direction of the surfaces"""
        MP3D = rc.Geometry.AreaMassProperties.Compute(zone)
        volumeCenPt = MP3D.Centroid
        MP3D.Dispose()
        # first surface of the geometry
        testSurface = zone.Faces[0].DuplicateFace(False)
        area, srfCentPt, normal = self.getSrfAreaAndCenPt(testSurface, calArea = False)
        try:
            # make a vector from the center point of the zone to center point of the surface
            testVector = rc.Geometry.Vector3d(srfCenPt - volumeCenPt)
            # check the direction of the vectors and flip zone surfaces if needed
            if rc.Geometry.Vector3d.VectorAngle(testVector, normal)> 1: zone.Flip()
        except:
            print 'Zone normal check failed!'
            return  

    def getOffsetDist(self, cenPt, edges):
        distList = []
        [distList.append(cenPt.DistanceTo(edge.PointAtNormalizedLength(0.5))) for edge in edges]
        return min(distList)/2
    
    def OffsetCurveOnSurface(self, border, face, offsetDist):
        success = False
        glzArea = 0
        direction = 1
        # Try RhinoCommon
        glzCurve = border.OffsetOnSurface(face.Faces[0], offsetDist, tolerance)
        if glzCurve==None:
            glzCurve = border.OffsetOnSurface(face.Faces[0], -offsetDist, tolerance)
            direction = -1
        
        if glzCurve == None:
            # Magically Steve Baer's script works in many cases that RhinoCommon Fails
            # I checked the source code in gitHub and it looks exactly the same as the lines above!
            # I have no idea what am I doing wrong! [Jan 19 2013]
            print "RhinoCommon failed to offsetCurveOnSurface... Testing Steve Baer's magic!"
            rsborder = sc.doc.Objects.AddCurve(border)
            rsface = sc.doc.Objects.AddSurface(face.Faces[0])
            glzCurve = rs.OffsetCurveOnSurface(rsborder, rsface, offsetDist)
            if glzCurve==None:
                glzCurve = rs.OffsetCurveOnSurface(rsborder, rsface, -offsetDist)
                direction = -1
            rs.DeleteObjects([rsface, rsborder])
            if glzCurve!=None:
                try:
                    glzCurve =  [rs.coercecurve(glzCurve)]
                except:
                    glzCurve = [rs.coercecurve(glzCurve[0])]
                print "Magic worked!"
        
        if glzCurve!=None:
            glzCurve = glzCurve[0]
            splitter = rc.Geometry.Surface.CreateExtrusion(glzCurve, self.getSrfAreaAndCenPt(face, calArea = False)[2]).ToBrep()
            splittedSrfs = face.Split(splitter, sc.doc.ModelAbsoluteTolerance)
            try:
                glzSrf = splittedSrfs[-1]
                glzArea = glzSrf.GetArea()
                success = True
                joinedSrf = rc.Geometry.Brep.JoinBreps(splittedSrfs, tolerance)[0]
            except Exception, e:
                print "Split surface failed!\n" + `e`
                return True, glzArea, glzCurve, None
                #joinedSrf = face
        else:
            print "Magic failed! I'm not surprised! " + \
                  "I'm thinking to apply a work around for this later!"
            # bake the surface
            # dupBorder and offsetCurveOnSurface in Rhino
            # bring the result
            joinedSrf = face
        
        return success, glzArea, glzCurve, joinedSrf

    def simplifyCrv(self, crv, tol=sc.doc.ModelAbsoluteTolerance , ang_tol = sc.doc.ModelAngleToleranceRadians):
        simplifyOption = rc.Geometry.CurveSimplifyOptions.All
        simplifiedCrv = crv.Simplify(simplifyOption, tol, ang_tol)
        if simplifiedCrv == None:
            return crv; print 'Curve simplification failed!'
        return simplifiedCrv

    # copied and modified from rhinoScript (@Steve Baer @GitHub)
    def CurveDiscontinuity(self, curve, style):
        """Search for a derivatitive, tangent, or curvature discontinuity in
        a curve object.
        Parameters:
          curve_id = identifier of curve object
          style = The type of continuity to test for. The types of
              continuity are as follows:
              Value    Description
              1        C0 - Continuous function
              2        C1 - Continuous first derivative
              3        C2 - Continuous first and second derivative
              4        G1 - Continuous unit tangent
              5        G2 - Continuous unit tangent and curvature
        Returns:
          List 3D points where the curve is discontinuous
        """
        dom = curve.Domain
        t0 = dom.Min
        t1 = dom.Max
        points = []
        get_next = True
        while get_next:
            get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
            if get_next:
                points.append(curve.PointAt(t))
                t0 = t # Advance to the next parameter
        return points

    def findNearestPt(self, pt, ptList):
        def distance(point):
            return pt.DistanceTo(point)
        return sorted(ptList, key = distance)[0]

    def getCurvePoints(self, curve):
        nc = curve.ToNurbsCurve()
        if nc is None: return sc.errorhandler()  
        points = [nc.Points[i].Location for i in xrange(nc.Points.Count)]
        return points
        
    def checkCurveInList(self, crv, crvList):
        """This definition checks if a curve with the same start and end point
        is in the list """
        ptList = [crv.PointAtStart, crv.PointAtEnd]
        #crvLength = crv.Domain[1] - crv.Domain[0]
        for c in crvList:
            #if not c.Domain[1] - c.Domain[0] == crvLength: return False
            if (c.PointAtStart in ptList) and (c.PointAtEnd in ptList):
                return True
        return False


class Building(object):
    def __init__(self, brep, bldgCount):
        self.geometry = brep
        self.name = 'bldg_' + `bldgCount`
        self.num = bldgCount
        self.zoneCount = 0
        self.zones={}
        
    def addZone(self, zoneBrep):
        if zoneBrep.IsSolid:
            self.zones[self.zoneCount] = zoneBrep
            self.zoneCount += 1
        
    def removeLastZone(self):
        del self.zones[len(self.zones)-1]
        self.zoneCount -= 1
        # number correction




################################################################################

def main(maximumRoofAngle, bldgMasses, bldgsFlr2FlrHeights, isConditioned, projectName):
        # import the classes
        if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
            lb_preparation = sc.sticky["ladybug_Preparation"]()
            lb_mesh = sc.sticky["ladybug_Mesh"]()
            lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
            lb_runStudy_RAD = sc.sticky["ladybug_Export2Radiance"]()
            lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
            # hb_materilaLib = sc.sticky["honeybee_MaterialLib"]()
            hb_export2EP = Export2EP()
            
            # don't customize this part
            hb_EPZone = sc.sticky["honeybee_EPZone"]
            hb_EPSrf = sc.sticky["honeybee_EPSurface"]
            hb_EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
        
        else:
            print "You should first let both Ladybug and Honeybee to fly..."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
            return -1
        
        conversionFac = lb_preparation.checkUnits()
        
        ########################################################################
        #----------------------------------------------------------------------#
        buildingsDic = {}
        if len(bldgMasses)!=0:
            # clean the geometries 
            analysisMesh, initialMasses = lb_preparation.cleanAndCoerceList(bldgMasses)
            
            splitterSrfs = []
            for bldgCount, mass in enumerate(initialMasses):
                
                thisBuilding = Building(mass, bldgCount)
                
                # 0- split the mass vertically [well, it is actually horizontally! so confusing...]
                # 0-1 find the boundingBox
                lb_visualization.calculateBB([mass])
                
                # SPLIT MASS TO ZONES
                # 0-2 get floor curves and split surfaces based on floor heights
                # I don't use floor curves here. It is originally developed for upload Rhino2Web
                maxHeights = lb_visualization.BoundingBoxPar[-1].Z
                bldgHeights = lb_visualization.BoundingBoxPar[-1].Z - lb_visualization.BoundingBoxPar[0].Z
                floorHeights = hb_export2EP.getFloorHeights(bldgsFlr2FlrHeights, bldgHeights, maxHeights, conversionFac)
                floorCrvs, splitterSrfs = hb_export2EP.getFloorCrvs(mass, floorHeights)
                
                # well, I'm pretty sure that something like this is smarter to be written
                # as a recursive fuction but I'm not comfortable enough to write it that way
                # right now. Should be fixed later!
                restOfmass = mass
                
                for srfCount, srf in enumerate(splitterSrfs):
                    lastPiece = []
                    lastPiece.append(restOfmass)
                    pieces = restOfmass.Split(srf.ToBrep(), tolerance)
                    if len(pieces)== 2 and lb_visualization.calculateBB([pieces[0]], True)[-1].Z < lb_visualization.calculateBB([pieces[1]], True)[-1].Z:
                        try: 
                            zone = pieces[0].CapPlanarHoles(tolerance);
                            if zone!=None:
                                thisBuilding.addZone(zone)
                            restOfmass = pieces[1].CapPlanarHoles(tolerance)
                        except Exception, e:
                            print 'error 1: ' + `e`

                    elif len(pieces)== 2:
                        thisBuilding.addZone(pieces[1].CapPlanarHoles(tolerance))
                        restOfmass = pieces[0].CapPlanarHoles(tolerance)
                        try:
                            zone = pieces[1].CapPlanarHoles(tolerance)
                            if zone!=None:
                                thisBuilding.addZone(zone)
                            restOfmass = pieces[0].CapPlanarHoles(tolerance)
                        except Exception, e:
                            print 'error 2: ' + `e`
                    else:
                        if srfCount == len(splitterSrfs) - 1:
                            pass
                        else:
                            msg = 'One of the masses is causing a problem. Check HBZones output for the mass that causes the problem.'
                            print msg
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return [restOfmass, -1]
                    
                    # remove the last 
                    try:
                        if lb_visualization.calculateBB([pieces[0]], True)[-1].Z == lb_visualization.calculateBB([pieces[1]], True)[-1].Z:
                            thisBuilding.removeLastZone()
                    except:
                        pass
                try:
                    # check if the last part heights is less than minimum acceptable height
                    minZPt, cetPt, maxZPt = lb_visualization.calculateBB([restOfmass], True)
                    minHeights = 0.1
                    
                    if  maxZPt.Z - minZPt.Z < minHeights:
                        # remove the last zone
                        thisBuilding.removeLastZone()
                        thisBuilding.addZone(lastPiece[0])
                    else:
                        # if acceptable then add it to the geometry
                        if not restOfmass.IsSolid:
                            restOfmass = restOfmass.CapPlanarHoles(tolerance)
                        if restOfmass!=None:
                            thisBuilding.addZone(restOfmass)
                            
                except Exception, e:
                    print 'mass to zone partially failed!\n' + \
                          `e`
                #    pass
                
                # add this building to buildings collection
                buildingsDic[bldgCount] = thisBuilding
        
        zoneClasses = []
        # iterate through building dictionary
        for bldgKey, bldg in buildingsDic.items():
            numOfZones = len(bldg.zones)
            
            #iterate through parent zones in each building
            for zoneKey, zone in bldg.zones.items():
                try: isZoneConditioned = isConditioned[zoneKey]
                except: isZoneConditioned = True
                
                # zone programs should be generated using the bldgsFloorProgram
                try: thisZoneProgram = zonePrograms[zoneKey]
                except: thisZoneProgram = 'Medium Office'
                
                thisZone = hb_EPZone(zone, zoneKey, `bldgKey` + '_' + `zoneKey`, thisZoneProgram, isZoneConditioned)
                if zoneKey == 0: thisZone.isThisTheFirstZone = True
                if zoneKey == numOfZones - 1: thisZone.isThisTheTopZone = True
                
                # since this zone will be build based on a closed brep I use decompseZone
                # to find walls, surfaces, blah blah
                thisZone.decomposeZone(maximumRoofAngle)
                
                # append this zone to other zones
                zoneClasses.append(thisZone)
                    
        return zoneClasses
        
        ################################################################################################


if _createHoneybeeZones == True:
    
    try:  maximumRoofAngle = float(maximumRoofAngle_)
    except: maximumRoofAngle = 30
    
    result= main(maximumRoofAngle, _bldgMasses, bldgsFlr2FlrHeights_, isConditioned_, projectName_)
    
    if result!= []:
        if isinstance(result, list) and len(result)>1 and result[1]==-1:
            HBZones = result[0]
        elif result!=-1:
            zoneClasses = result 
            hb_hive = sc.sticky["honeybee_Hive"]()
            HBZones  = hb_hive.addToHoneybeeHive(zoneClasses, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
