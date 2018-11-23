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
Analysis Recipe for Annual Daylighting Simulation
-
Provided by Honeybee 0.0.64
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _epwWeatherFile: epw weather file address on your system
        _testPoints: Test points
        ptsVectors_: Point vectors
        _radParameters_: Radiance parameters
        _DSParameters_: Daysim parameters
    Returns:
        analysisRecipe: Recipe for annual climate based daylighting simulation
"""

ghenv.Component.Name = "Honeybee_Annual Daylight Simulation"
ghenv.Component.NickName = 'annualDaylightSimulation'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh
import os
import math


def isAllNone(dataList):
    for item in dataList:
        if item!=None: return False
    return True

def main():
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release') or not sc.sticky.has_key('ladybug_release'):
        msg = "You should first let Honeybee and Ladybug to fly..."
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
        return
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    if north_!=None:
        northAngle, northVector = lb_preparation.angle2north(north_)
    else:
        northAngle = 0
        
    DLAnalysisRecipe = sc.sticky["honeybee_DLAnalysisRecipe"]
    
    analysisRecipe = DLAnalysisRecipe(2, _epwWeatherFile, _testPoints, ptsVectors_,
                                      _radParameters_, _DSParameters_, testMesh_, math.degrees(northAngle), ghenv.Component)
                                      
    if (_testPoints.DataCount==0 or isAllNone(_testPoints.AllData())) \
        and not (_DSParameters_ and _DSParameters_.runAnnualGlare \
        and _DSParameters_.onlyAnnualGlare):
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
    
    # add a single test point if it is only glare analysis so Daysim won't crash
    if (_DSParameters_ and _DSParameters_.runAnnualGlare \
        and _DSParameters_.onlyAnnualGlare):
            analysisRecipe.testPts = [[rc.Geometry.Point3d.Origin]]
            analysisRecipe.vectors = [[rc.Geometry.Vector3d.ZAxis]]
            
    if not os.path.isfile(_epwWeatherFile):
        analysisRecipe = None
        print "Can't find the weather file at: " + _epwWeatherFile
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Can't find the weather file at: " + _epwWeatherFile)

    return analysisRecipe


if _epwWeatherFile and _testPoints:
    _testPoints.SimplifyPaths()
    ptsVectors_.SimplifyPaths()

    analysisRecipe = main()