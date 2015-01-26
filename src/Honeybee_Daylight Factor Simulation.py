# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analysis Recipie for Daylight Factor Analysis
-
Provided by Honeybee 0.0.55
    
    Args:
        _testPoints: Test points
        ptsVectors_: Point vectors
        uniformSky_: Set to true to run the study under a CIE uniform sky. Default is set to cloudy sky
        _radParameters_: Radiance parameters
    Returns:
        analysisRecipe: Recipe for daylight factor analysis
"""

ghenv.Component.Name = "Honeybee_Daylight Factor Simulation"
ghenv.Component.NickName = 'daylighFactorSimulation'
ghenv.Component.Message = 'VER 0.0.55\nNOV_08_2014'
ghenv.Component.Category = "Honeybee@DL"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.55\nNOV_08_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import Grasshopper.Kernel as gh
import scriptcontext as sc
import os

def genDFSky(illuminanceValue = 1000, skyType = "-c"):

    def RADDaylightingSky(illuminanceValue, skyType):
        # gensky 12 4 +12:00 -c -B 55.866 > skies/sky_10klx.mat
        return  "# start of sky definition for daylighting studies\n" + \
                "# horizontal sky illuminance: " + `illuminanceValue` + " lux\n" + \
                "!gensky 12 6 12:00 " + skyType + " -B " +  '%.3f'%(illuminanceValue/179) + "\n" + \
                "skyfunc glow sky_mat\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "1 1 1 0\n" + \
                "sky_mat source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "0 0 1 180\n"
        
        # For now I removed the ground. I should check what is the standard sky for LEED
        ground ="skyfunc glow ground_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "1 .8 .5 0\n" + \
                "ground_glow source ground\n" + \
                "0\n" + \
                "0\n" + \
                "4\n" + \
                "0 0 -1 180\n" + \
                "# end of sky definition for daylighting studies\n\n"
    
    path  = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\DFSimulationSky\\")
    if not os.path.isdir(path): os.mkdir(path)
    
    outputFile = path + `int(illuminanceValue)` + "_lux.sky"
    
    skyStr = RADDaylightingSky(illuminanceValue, skyType)
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile

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
        return

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

    if uniformSky_==True:
        skyFilePath = genDFSky(1000, "-u")
    else:
        skyFilePath = genDFSky(1000, "-c")
    
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    # As much as I dislike using global variables I feel lazy to change this now
    simulationType = 3
    _testPoints.SimplifyPaths()
    ptsVectors_.SimplifyPaths()
    analysisRecipe = DLAnalysisRecipe(simulationType, skyFilePath, _testPoints,
                                      ptsVectors_, _radParameters_, testMesh_, ghenv.Component)
    
        
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
    
    return analysisRecipe

analysisRecipe = main()
