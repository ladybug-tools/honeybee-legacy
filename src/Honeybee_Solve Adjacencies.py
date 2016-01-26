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
Solve adjacencies
-
Provided by Honeybee 0.0.59

    Args:
        _HBZones: A list of Honeybee zones for which you want to calculate whether they are next to each other.
        altConstruction_: An optional alternate EP construction to assign to all adjacent surfaces.  The default is set to be "Interior Wall", "Interior Foor" or "Interior Ceiling" or "Interior Window" depending on the type of surface that is adjacent.
        altBC_: An optional alternate boundary condition such as "Adiabatic".  The default will be "Surafce", which ensures that heat flows across each adjacent surface to a neighboring zone.
        tolerance_: The tolerance in Rhino model units that will be used determine whether two zones are adjacent to each other.  If no value is input here, the component will use the tolerance of the Rhino model document.
        removeCurrentAdjc_: If you are using this component after already solving for the adjacencies between some of the zones previously, set this to "False" in order to remeber the previously determined adcacency conditions.  If set to "True", the current adjacencies will be removed. The default is set to "False" in order to remeber your previously-set adjacencies.
        _findAdjc: Set to "True" to solve adjacencies between zones.
    Returns:
        readMe!: A report of the found adjacencies.
        HBZonesWADJ: A list of Honeybee zones with adjacencies solved.
"""
ghenv.Component.Name = "Honeybee_Solve Adjacencies"
ghenv.Component.NickName = 'solveAdjc'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid

def shootIt(rayList, geometry, tol = 0.01, bounce =1):
   # shoot a list of rays from surface to geometry
   # to find if geometry is adjacent to surface
   for ray in rayList:
        intPt = rc.Geometry.Intersect.Intersection.RayShoot(ray, geometry, bounce)
        if intPt:
            if ray.Position.DistanceTo(intPt[0]) <= tol:
                return True #'Bang!'

def updateZoneMixing(surface1, zone1, zone2):
    #Change the air mixing between the zone and other zones to "True"
    zone1.mixAir = True
    zone2.mixAir = True
    
    #Append the zone to be mixed with to the mixAirZoneList.
    zone1.mixAirZoneList.append(zone2.name)
    zone2.mixAirZoneList.append(zone1.name)
    
    #Calculate a rough flow rate of air based on the cross-sectional area of the surface between them.
    flowFactor = zone1.mixAirFlowRate
    flowRate = (rc.Geometry.AreaMassProperties.Compute(surface1.geometry).Area)*flowFactor
    
    #Append the flow rate of mixing to the mixAirFlowList
    zone1.mixAirFlowList.append(flowRate)
    zone2.mixAirFlowList.append(flowRate)
    
    #Append the flow shcedule to the mixing list.
    zone1.mixAirFlowSched.append('ALWAYS ON')
    zone2.mixAirFlowSched.append('ALWAYS ON')
    
    return flowRate

def updateAdj(surface1, surface2, altConstruction, altBC, tol):
    # change roof to ceiling
    # the same for ceiling on ground
    if int(surface1.type) == 1: surface1.setType(3) # roof + adjacent surface = ceiling
    elif int(surface2.type) == 1: surface2.setType(3)
    
    # Change different floor types to be floors between zones.
    if int(surface1.type) == 2: surface1.setType(2)
    if int(surface2.type) == 2:  surface2.setType(2)
    
    
    # If the alternate construction is set to air wall, we should also change the surface type to air wall
    try:
        if altConstruction.ToUpper() == "AIR WALL":
            surface1.setType(4)
            surface2.setType(4)
            infoMsg = "Setting the altConstruction to Air Wall will also ensure that surfaces have the air wall srfType_ and that air is mixed between zones."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, infoMsg)
    except: pass
    
    # change construction
    if altConstruction == None:
        surface1.setEPConstruction(surface1.intCnstrSet[surface1.type])
        surface2.setEPConstruction(surface1.intCnstrSet[surface2.type])
    else:
        surface1.setEPConstruction(altConstruction)
        surface2.setEPConstruction(altConstruction)
    
    # change bc
    if altBC != None:
        surface2.setBC(altBC.upper())
        surface1.setBC(altBC.upper())
        surface1.setBCObject(surface2)
        surface2.setBCObject(surface1)
    else:
        surface1.setBC('SURFACE', True)
        surface2.setBC('SURFACE', True)
        # change bc.Obj
        # used to be only a name but I changed it to an object so you can find the parent, etc.
        surface1.setBCObject(surface2)
        surface2.setBCObject(surface1)
    
    # set sun and wind exposure to no exposure
    surface2.setSunExposure('NoSun')
    surface1.setSunExposure('NoSun')
    surface2.setWindExposure('NoWind')
    surface1.setWindExposure('NoWind')
    
    # check for child objects
    if (surface1.hasChild or surface2.hasChild) and (len(surface2.childSrfs)!= len(surface1.childSrfs)):
        # give warning
        warnMsg= "Number of windows doesn't match between " + surface1.name + " and " + surface2.name + "." + \
                 " Make sure adjacent surfaces are divided correctly and have similar windows."
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return
        
    if surface1.hasChild and surface2.hasChild:
        # find child surfaces that match the other one
        for childSurface1 in surface1.childSrfs:
            for childSurface2 in surface2.childSrfs:
                if childSurface2.BCObject.name == "":
                    if childSurface1.cenPt.DistanceTo(childSurface2.cenPt) <= tol:
                        childSurface1.BCObject.name = childSurface2.name
                        childSurface2.BCObject.name = childSurface1.name
                        # change construction
                        childSurface1.setEPConstruction(surface1.intCnstrSet[5])
                        childSurface2.setEPConstruction(surface1.intCnstrSet[5])
                        # change the boundary condition
                        childSurface1.setBC('SURFACE', True)
                        childSurface2.setBC('SURFACE', True)
                        childSurface1.setBCObject(childSurface2)
                        childSurface2.setBCObject(childSurface1)
                        # set sun and wind exposure to no exposure
                        childSurface2.setSunExposure('NoSun')
                        childSurface1.setSunExposure('NoSun')
                        childSurface2.setWindExposure('NoWind')
                        childSurface1.setWindExposure('NoWind')
                        
                        print 'Interior window ' + childSurface1.BCObject.name + \
                              '\t-> is adjacent to <-\t' + childSurface2.BCObject.name + '.'
        

def notTheSameZone(targetZone, testZone):
    if hasattr(testZone, 'cenPt')and hasattr(targetZone, 'cenPt'):
        return targetZone.name != testZone.name and targetZone.cenPt.DistanceTo(testZone.cenPt) > sc.doc.ModelAbsoluteTolerance
    else:
        return targetZone.name != testZone.name
    

def main(HBZones, altConstruction, altBC, tol, remCurrent):
    
    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
            
    # extra check to be added later.
    # check altBC and altConstruction to be valid inputs
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(HBZones)
    
    # make sure there is no duplicate names
    zoneNames = []
    for HBZone in HBZoneObjects:
        if HBZone.name in zoneNames:
            #there is duplicate name
            warning = "There are duplicate names in input zones." + \
                      " Zone names cannot be duplicate.\nRename the zones and try again!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        zoneNames.append(HBZone.name)
    
    # clean current boundary condition
    if remCurrent:
        for testZone in HBZoneObjects:
            for srf in testZone.surfaces:
                if srf.BC.upper() != "GROUND":
                    srf.setBC('OUTDOORS')
                    srf.setBCObjectToOutdoors()
    
    # solve it zone by zone
    for testZone in HBZoneObjects:
        # mesh each surface and test if it will be adjacent to any surface
        # from other zones
        for srf in testZone.surfaces:
            #print srf.type, srf.BC 
            if srf.BC.upper() == 'OUTDOORS' or srf.BC.upper() == 'GROUND' or srf.BC.upper() == 'ADIABATIC':
                #Create a mesh of surface to use center points as test points
                meshPar = rc.Geometry.MeshingParameters.Default
                BrepMesh = rc.Geometry.Mesh.CreateFromBrep(srf.geometry, meshPar)[0]
                
                # calculate face normals
                BrepMesh.FaceNormals.ComputeFaceNormals()
                BrepMesh.FaceNormals.UnitizeFaceNormals()
                
                # dictionary to collect center points and rays
                raysDict = {}
                for faceIndex in range(BrepMesh.Faces.Count):
                    srfNormal = (BrepMesh.FaceNormals)[faceIndex]
                    meshSrfCen = BrepMesh.Faces.GetFaceCenter(faceIndex)
                    # move testPt backward for half of tolerance
                    meshSrfCen = rc.Geometry.Point3d.Add(meshSrfCen, -rc.Geometry.Vector3d(srfNormal)* tol /2)
                    
                    raysDict[meshSrfCen] = rc.Geometry.Ray3d(meshSrfCen, srfNormal)
                
                for targetZone in HBZoneObjects:
                    if notTheSameZone(targetZone, testZone):
                        # check ray intersection to see if this zone is next to the surface
                        if shootIt(raysDict.values(), [targetZone.geometry], tol + sc.doc.ModelAbsoluteTolerance):
                            for surface in targetZone.surfaces:
                                # check if z value of center points matches
                                #print abs(surface.cenPt.Z - srf.cenPt.Z)
                                #if abs(surface.cenPt.Z - srf.cenPt.Z) < tol:
                                # check distance with the nearest point on each surface
                                for pt in raysDict.keys():
                                    if surface.geometry.ClosestPoint(pt).DistanceTo(pt) <= tol:
                                        # extra check for normal direction
                                        normalAngle = abs(rc.Geometry.Vector3d.VectorAngle(surface.normalVector, srf.normalVector))
                                        revNormalAngle = abs(rc.Geometry.Vector3d.VectorAngle(surface.normalVector, -srf.normalVector))
                                        #print normalAngle
                                        #print revNormalAngle
                                        if normalAngle==0  or revNormalAngle <= sc.doc.ModelAngleToleranceRadians:
                                            print 'Surface ' + srf.name + ' which is a ' + srf.srfType[srf.type] + \
                                                  '\t-> is adjacent to <-\t' + surface.name + ' which is a ' + \
                                                  surface.srfType[surface.type] + '.'
                                            #if normalAngle == 0:
                                            #    msg = "Warning: Normal direction of one of the surfaces " + srf.name + ", " + surface.name + " should be reversed!"
                                            #    print msg
                                            #    w = gh.GH_RuntimeMessageLevel.Warning
                                            #    ghenv.Component.AddRuntimeMessage(w, msg)
                                            
                                            updateAdj(srf, surface, altConstruction, altBC, tol)                                        
                                            if surface.type == 4:
                                                flowRate = updateZoneMixing(surface, testZone, targetZone)
                                                print "Air has been mixed between " + testZone.name + " and " + targetZone.name + " with a flow rate of " + str(flowRate) + " m3/s."
                                            
                                            break
                    
                #if srf.type == 3 and srf.BCObject.name == '':
                #        srf.setType(1) # Roof
                #        srf.setBC(srf.srfBC[srf.type])
    
    # add zones to dictionary
    ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return ModifiedHBZones



if _findAdjc and _HBZones and _HBZones[0]!=None:
    try: tol = float(tolerance_)
    except: tol = sc.doc.ModelAbsoluteTolerance
    
    # tolrance can't be less than document tolerance
    if tol < sc.doc.ModelAbsoluteTolerance:
        tol = sc.doc.ModelAbsoluteTolerance
        
    results = main(_HBZones, altConstruction_, altBC_, tol, removeCurrentAdjc_)
    
    if results!=-1:
        HBZonesWADJ = results