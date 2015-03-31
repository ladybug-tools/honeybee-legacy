# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analysis Recipie for Grid-Based Analysis
-
Provided by Honeybee 0.0.56
    
    Args:
        _skyFile: Path to a radiance sky file
        _simulationType_: [0] illuminance(lux), [1] radiation (kwh), [2] luminance (Candela)
        _testPoints: Test points
        ptsVectors_: Point vectors
        _radParameters_: Radiance parameters
    Returns:
        analysisRecipe: Recipe for grid-based analysis

"""

ghenv.Component.Name = "Honeybee_Grid Based Simulation"
ghenv.Component.NickName = 'gridBasedSimulation'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def isAllNone(dataList):
    for item in dataList:
        if item!=None: return False
    return True


def main():
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    # As much as I dislike using global variables I feel lazy to change this now
    recipe = DLAnalysisRecipe(1, _skyFile, _testPoints, ptsVectors_,
                              _radParameters_, _simulationType_, testMesh_, ghenv.Component)
    
    return recipe


if _skyFile and _testPoints:
    
    _testPoints.SimplifyPaths()
    ptsVectors_.SimplifyPaths()
    
    try: int(_simulationType_)
    except: _simulationType_ = 0
    
    recipe = main()
    
    if recipe != -1 and recipe.skyFile != None:
        analysisRecipe = recipe
        if _testPoints.DataCount==0 or isAllNone(_testPoints.AllData()):
            analysisRecipe = None
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "testPoints are missing!")
        # generate the vectors if the vectors are not there
        elif len(analysisRecipe.vectors)==0:
            analysisRecipe.vectors = []
            for ptListCount, ptList in enumerate(analysisRecipe.testPts):
                analysisRecipe.vectors.append([])
                for pt in ptList:
                    analysisRecipe.vectors[ptListCount].append(rc.Geometry.Vector3d.ZAxis)
                    
