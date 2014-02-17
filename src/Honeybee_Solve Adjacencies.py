# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Solve adjacencies
-
Provided by Honeybee 0.0.50

    Args:
        _HBZones: List of Honeybee zones
        _tolerance_: Tolerance value
        _findAdjc: Set to True to find the adjacencies
    Returns:
        readMe!: Report of the adjacencies
        HBZonesWADJ: List of Honeybee zones with adjacencies
"""
ghenv.Component.Name = "Honeybee_Solve Adjacencies"
ghenv.Component.NickName = 'solveAdjc'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import Rhino as rc
import scriptcontext as sc

def shootIt(rayList, geometry, tol = 0.01, bounce =1):
   # yaha! not to crash if someone pass a geometry instead of a list
   #if type(geometryList)!= list or type(geometryList)!= tuple: geometryList = [geometryList]
   for ray in rayList:
        intPt = rc.Geometry.Intersect.Intersection.RayShoot(ray, geometry, bounce)
        if intPt:
            if ray.Position.DistanceTo(intPt[0]) <= tol:
                return 'Bang!'

class OutdoorBC(object):
    def __init__(self):
        self.name = ""

def main(HBZones, tol):
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(HBZones)
    
    
    # clean bcObjects
    for testZone in HBZoneObjects:
        for srf in testZone.surfaces: srf.BCObject = OutdoorBC()  
    
    for testZone in HBZoneObjects:
        for srf in testZone.surfaces:
            BCToBeChecked = ['SURFACE', 'OUTDOORS']
            if (srf.BC.upper() in  BCToBeChecked) and srf.BCObject.name == "" and not srf.hasChild:
                
                #Create a mesh of the zone geometry.
                meshPar = rc.Geometry.MeshingParameters.Default
                BrepMesh = rc.Geometry.Mesh.CreateFromBrep(srf.geometry, meshPar)[0]
                
                #Create breps of all of the mesh faces to be used as the base for ray generation.
                rayPtBases = []
                rays = []
                srfFaceList = BrepMesh.Faces
                
                # calculate face normals
                BrepMesh.FaceNormals.ComputeFaceNormals()
                BrepMesh.FaceNormals.UnitizeFaceNormals()
                
                for face in range(BrepMesh.Faces.Count):
                    srfNormal = (BrepMesh.FaceNormals)[face] # store face normals
                    meshSrfCen = BrepMesh.Faces.GetFaceCenter(face) # store face centers
                    rayPtBases.append(meshSrfCen)
                    rays.append(rc.Geometry.Ray3d(meshSrfCen, srfNormal))
                
                for targetZone in HBZoneObjects:
                    if targetZone.name != testZone.name:
                       # check ray intersection
                       if shootIt(rays, [targetZone.geometry], 100):
                            for surface in targetZone.surfaces:
                                # check distance with the nearest point on each surface
                                for pt in rayPtBases:
                                    if surface.geometry.ClosestPoint(pt).DistanceTo(pt) <= tol:
                                        print 'Surface ' + srf.name + ' is a ' + srf.srfType[srf.type] + \
                                              '->ADJACENT TO<-' + surface.name + ' which is a ' + \
                                              surface.srfType[surface.type] + '.'
                                        if srf.type == 1: srf.type = 3 # roof + adjacent surface = ceiling
                                        elif surface.type == 1: surface.type = 3
                                        # change bc
                                        srf.BC = 'SURFACE'
                                        surface.BC = 'SURFACE'
                                        # change bc.Obj
                                        # used to be only a name but I changed it to an object so you can find the parent, etc.
                                        srf.BCObject = surface
                                        surface.BCObject = srf
                                        # sun and wind exposure
                                        surface.sunExposure = srf.srfSunExposure[2]
                                        srf.sunExposure = srf.srfSunExposure[2]
                                        surface.windExposure = surface.srfWindExposure[2]
                                        srf.windExposure = surface.srfWindExposure[2]
                                        break
                
                if srf.type == 3 and srf.BCObject.name == '':
                        srf.type = 1 # Roof
                        srf.BC = srf.srfBC[srf.type]
    
    # add zones to dictionary
    ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component.InstanceGuid.ToString())
    
    return ModifiedHBZones



if _findAdjc and _HBZones and _HBZones[0]!=None:
    try: tol = float(_tolerance_)
    except: tol = sc.doc.ModelAbsoluteTolerance
    HBZonesWADJ = main(_HBZones, tol)
