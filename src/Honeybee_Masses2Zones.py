# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert Mass to Honeybee Zones
-
Provided by Honeybee 0.0.53

    Args:
        _bldgMasses: List of closed Breps
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
ghenv.Component.Message = 'VER 0.0.53\nMAY_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


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

def main(maximumRoofAngle, bldgMasses, isConditioned, projectName):
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
        
        # floor heights is now moved to a different component
        bldgsFlr2FlrHeights = []
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
                
                if floorHeights!=[0]:
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
                else:
                    thisBuilding.addZone(mass)
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
                except: thisZoneProgram = 'Office', 'OpenOffice'
                
                thisZone = hb_EPZone(zone, zoneKey, `bldgKey` + '_' + `zoneKey`, thisZoneProgram, isZoneConditioned)
                
                if zoneKey == 0: thisZone.isThisTheFirstZone = True
                elif zoneKey == numOfZones - 1: thisZone.isThisTheTopZone = True
                
                
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
    
    bldgsFloorProgram_ = []
    isConditioned_ = [True]
    
    result= main(maximumRoofAngle, _bldgMasses, isConditioned_, projectName_)
    
    if result!= []:
        if isinstance(result, list) and len(result)>1 and result[1]==-1:
            HBZones = result[0]
        elif result!=-1:
            zoneClasses = result 
            hb_hive = sc.sticky["honeybee_Hive"]()
            HBZones  = hb_hive.addToHoneybeeHive(zoneClasses, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
