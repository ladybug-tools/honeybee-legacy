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
Genrate Test Points for all Floor Surfaces in Honeybee Zone
-
Provided by Honeybee 0.0.64
    
    Args:
        _HBZone: HBZone; Test points will be generated for every floor surface inside zone
        _gridSize: Size of the test grid
        _distBaseSrf: Distance from base surface
        moveTestMesh_: Set to False if you want test mesh not to move. Default is True.
    Returns:
        readMe!: ...
        testPoints: Test points
        ptsVectors: Vectors
        faceArea: Area of each mesh face
        mesh: Analysis mesh
"""

ghenv.Component.Name = "Honeybee_Generate Zone Test Points"
ghenv.Component.NickName = 'genHBZoneTestPts'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import Grasshopper.Kernel as gh
from itertools import chain
import System.Threading.Tasks as tasks
import scriptcontext as sc
import copy

def createMesh(brep, gridSize):
    ## mesh breps
    def makeMeshFromSrf(i, inputBrep):
        try:
            mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)[0]
            inputBrep.Dispose()
        except:
            print 'Error in converting Brep to Mesh...'
            pass

    # prepare bulk list for each surface
    mesh = [None] * len(brep)

    # set-up mesh parameters for each surface based on surface size
    meshParam = rc.Geometry.MeshingParameters.Default
    meshParam.MaximumEdgeLength = gridSize
    meshParam.MinimumEdgeLength = gridSize
    meshParam.GridAspectRatio = 1

    for i in range(len(mesh)): makeMeshFromSrf(i, brep[i])
    
    return mesh

def flattenList(l):return list(chain.from_iterable(l))

def getTestPts(inputMesh, movingDis, moveTestMesh= False, parallel = True):
        
        # preparing bulk lists
        testPoint = [[]] * len(inputMesh)
        srfNormals = [[]] * len(inputMesh)
        meshSrfCen = [[]] * len(inputMesh)
        meshSrfArea = [[]] * len(inputMesh)
        
        srfCount = 0
        for srf in inputMesh:
            testPoint[srfCount] = range(srf.Faces.Count)
            srfNormals[srfCount] = range(srf.Faces.Count)
            meshSrfCen[srfCount] = range(srf.Faces.Count)
            meshSrfArea[srfCount] = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                inputMesh[i].FaceNormals.ComputeFaceNormals()
                inputMesh[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(inputMesh[i].Faces.Count):
                    srfNormals[i][face] = (inputMesh[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = inputMesh[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                    tempMesh = rc.Geometry.Mesh()
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].A]) #0
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].B]) #1
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].C]) #2
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].D]) #3
                    tempMesh.Faces.AddFace(0, 1, 3, 2)
                    massData = rc.Geometry.AreaMassProperties.Compute(tempMesh)
                    meshSrfArea[i][face] = massData.Area
                    massData.Dispose()
                    tempMesh.Dispose()
                    
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(inputMesh)),srfPtCalculator)
        else:
            for i in range(len(inputMesh)):
                srfPtCalculator(i)
        
        if moveTestMesh:
            # find surfaces based on first normal in srfNormals - It is a simplification we can write a better function for this later
            for meshCount, mesh in enumerate(inputMesh):
                vector = srfNormals[meshCount][0]
                movingVec = rc.Geometry.Vector3f.Multiply(movingDis,vector)
                mesh.Translate(movingVec.X, movingVec.Y, movingVec.Z)
                
        return flattenList(testPoint), flattenList(srfNormals), flattenList(meshSrfArea), inputMesh

def getHBZoneFloorSurfaces(HBZone):
    testSurfaces = []
    
    try:
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBZone = hb_hive.callFromHoneybeeHive([HBZone])[0]

        for HBS in HBZone.surfaces:
            if int(HBS.type) == 2:
                testSrf = copy.deepcopy(HBS.geometry)
                testSrf.Flip()
                testSurfaces.append(testSrf)
        return testSurfaces
    except:
        return -1


if _HBZone!=None and _gridSize!=None and _distBaseSrf!=None:
    
    if _distBaseSrf<0:
        msg = "Distance from base should be greater than 0. Flip the input surface instead of using a negative number."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
    else:
        
        testSurfaces = getHBZoneFloorSurfaces(_HBZone)
        
        if testSurfaces!= -1:
            initMesh = createMesh(testSurfaces, _gridSize)
        
            inputMesh = []
            for m in initMesh: inputMesh.append(m)
            
            try:
                testPoints, ptsVectors, facesArea, mesh = getTestPts(inputMesh, _distBaseSrf, moveTestMesh_)
            except:
                # just for the first release
                testPoints, ptsVectors, facesArea, mesh = getTestPts(inputMesh, _distBaseSrf, False)
        else:
            msg = "Failed to find floor surfaces!"