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
Analysis Recipie for Vertical Sky Component, which is typically used to evaluate daylight and sky access in urban areas.
_
The Vertical Sky Component (VSC) is described by the UK Building Research Establishment (BRE) as the ratio of the direct sky illuminance falling on the vertical wall at a reference point, to the simultaneous horizontal illuminance under an unobstructed sky [Littlefair, 1991]. It also states that the Standard CIE Overcast Sky model is to be used for the sky illuminance distribution. This means that the reference value for the VSC percentage is effectively the unobstructed horizontal sky component.
_
The calculation performed by this component comes from this discussion on the RADIANCE forum: http://www.radiance-online.org/pipermail/radiance-general/2006-September/004017.html
-
Provided by Honeybee 0.0.64
    
    Args:
        _testPoints: Test points
        ptsVectors_: Point vectors
        _ad_: Number of ambient divisions. "The error in the Monte Carlo calculation of indirect illuminance will be inversely proportional to the square root of this number. A value of zero implies no indirect calculation."
        uniformSky_: Set to true to run the study under a CIE uniform sky. Default is set to cloudy sky
    Returns:
        analysisRecipe: Recipe for vertical sky component
"""

ghenv.Component.Name = "Honeybee_Vertical Sky Component"
ghenv.Component.NickName = 'verticalSkyComponent'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

import os
import scriptcontext as sc

def genVSCSky(illuminanceValue = 100000, skyType = "-c"):

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


def main(ad):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        return
    
    # generate the sky
    if uniformSky_==True:
        skyFilePath = genVSCSky(100000, "-u")
    else:
        skyFilePath = genVSCSky(100000, "-c")
    
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    # set radiance parameters
    hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
    quality = 0
    radPar = {}
    for key in hb_radParDict.keys():
        print key + " is set to " + str(hb_radParDict[key][quality])
        radPar[key] = hb_radParDict[key][quality]
        radPar["_ad_"] = ad
        radPar["_as_"] = 20
        radPar["_ar_"] = 300
        radPar["_aa_"] = 0.1
        radPar["_ab_"] = 1
    
    
    # As much as I dislike using global variables I feel lazy to change this now
    simulationType = 4
    _testPoints.SimplifyPaths()
    ptsVectors_.SimplifyPaths()
    analysisRecipe = DLAnalysisRecipe(simulationType, skyFilePath, _testPoints,
                                      ptsVectors_, radPar, testMesh_, ghenv.Component)
    
        
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

try: ad = int(_ad_)
except: ad = 4800
analysisRecipe = main(ad)




