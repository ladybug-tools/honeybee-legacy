# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Import Radiance Test Grid

-
Provided by Honeybee 0.0.56

    Args:
        input1: ...
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Honeybee_Import Pts File"
ghenv.Component.NickName = 'importPts'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass



import os
import Rhino as rc
from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

pointsF = []
vectorsF = []

def main(ptsFileAddress):
    
    for fileAddress in ptsFileAddress:
        with open(fileAddress, 'r') as pts:
            for lineCount, line in enumerate(pts):
                line = ' '.join(line.split())
                lineSeg = line.Split(' ')
                if len(lineSeg)!=6: lineSeg = line.Split('\t')
                if len(lineSeg)==6:
                    pointsF.append(rc.Geometry.Point3d(float(lineSeg[0]), float(lineSeg[1]), float(lineSeg[2])))
                    vectorsF.append(rc.Geometry.Vector3d(float(lineSeg[3]), float(lineSeg[4]), float(lineSeg[5])))
                
    # check if there is a pattern file in thr folder
    workingDir = os.path.dirname(ptsFileAddress[0])
    dirFiles = os.listdir(workingDir)
    ptnFileName = None
    for fn in dirFiles:
        if fn.endswith(".ptn"):
            ptnFileName = os.path.join(workingDir, fn)
            break
    
    if ptnFileName != None:
        with open(ptnFileName, "r") as ptnInf:
            pattern = ptnInf.readlines()[0].split(",")[:-1]
        
        pattern = map(int, pattern)
        
        # graft the data based on the pattern
        points = DataTree[Object]()
        vectors = DataTree[Object]()
        for branchCount in range(len(pattern)):
            p = GH_Path(branchCount)
            
            points.AddRange(pointsF[sum(pattern[:branchCount]): sum(pattern[:branchCount+1])], p)
            vectors.AddRange(vectorsF[sum(pattern[:branchCount]): sum(pattern[:branchCount+1])], p)
               
    else:
        # no pattern do just put them together
        points = pointsF
        vectors = vectorsF

    return points, vectors

if len(_ptsFileAddress)!=0 and _ptsFileAddress[0]!=None:
    points, vectors = main(_ptsFileAddress)