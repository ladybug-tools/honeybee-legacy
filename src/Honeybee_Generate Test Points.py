"""
Genrate Test Points
-
Provided by Honybee 0.0.50
    
    Args:
        testSurface: Test surface as a Brep
        gridSize: Size of the test grid
        distBaseSrf: Distance from base surface
    Returns:
        readMe!: ...
        testPoints: Test points
        ptsVectors: Vectors
        faceArea: Area of each mesh face
        mesh: Analysis mesh
"""

ghenv.Component.Name = "Honeybee_Generate Test Points"
ghenv.Component.NickName = 'genTestPts'
ghenv.Component.Message = 'VER 0.0.43\nFEB_09_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import Rhino as rc
import Grasshopper.Kernel as gh
from itertools import chain
import System.Threading.Tasks as tasks

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

def getTestPts(inputMesh, movingDis, parallel = True):
        
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
        
        return flattenList(testPoint), flattenList(srfNormals), flattenList(meshSrfArea)


if testSurface!=None and gridSize!=None and distBaseSrf!=None:
    
    if distBaseSrf<0:
        msg = "Distance from base should be greater than 0. Flip the input surface instead of using a negative number."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
    else:
        initMesh = createMesh([testSurface], gridSize)
    
        inputMesh = []
        for m in initMesh: inputMesh.append(m)
    
        testPoints, ptsVectors, facesArea = getTestPts(inputMesh, distBaseSrf)
        mesh = inputMesh
