# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analysis Recipie for Vertical Sky Component

The idea Based on this discussion on RADIANCE: http://www.radiance-online.org/pipermail/radiance-general/2006-September/004017.html
-
Provided by Honeybee 0.0.53
    
    Args:
        _testPoints: Test points
        ptsVectors_: Point vectors
        uniformSky_: Set to true to run the study under a CIE uniform sky. Default is set to cloudy sky
    Returns:
        analysisRecipe: Recipe for vertical sky component
"""

ghenv.Component.Name = "Honeybee_Vertical Sky Component"
ghenv.Component.NickName = 'verticalSkyComponent'
ghenv.Component.Message = 'VER 0.0.53\nAUG_03_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

import os
import scriptcontext as sc

def genVSCSky(illuminanceValue = 1000, skyType = "-c"):

    def RADDaylightingSky(illuminanceValue, skyType):
        # gensky 12 4 +12:00 -c -B 55.866 > skies/sky_10klx.mat
        return  "# start of sky definition for vertical sky component calculation\n" + \
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
                "0 0 1 180\n" + \
                "# end of sky definition for daylighting studies\n\n"
    
    path  = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\VSCSimulationSky\\")
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


def main(skyFilePath):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return
        
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    # set radiance parameters
    hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
    quality = 0
    radPar = {}
    for key in hb_radParDict.keys():
        print key + " is set to " + str(hb_radParDict[key][quality])
        radPar[key] = hb_radParDict[key][quality]
        radPar["_ad_"] = 2400
        radPar["_as_"] = 20
        radPar["_ar_"] = 300
        radPar["_aa_"] = 0.1
        radPar["_ab_"] = 1
    
    
    # As much as I dislike using global variables I feel lazy to change this now
    simulationType = 4
    _testPoints.SimplifyPaths()
    ptsVectors_.SimplifyPaths()
    analysisRecipe = DLAnalysisRecipe(simulationType, skyFilePath, _testPoints,
                                      ptsVectors_, radPar, testMesh_)
    
        
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


# generate the sky
if uniformSky_==True:
    skyFilePath = genVSCSky(1000, "-u")
else:
    skyFilePath = genVSCSky(1000, "-c")

analysisRecipe = main(skyFilePath)




