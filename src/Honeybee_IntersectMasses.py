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
Use this component to take a list of closed breps (polysurfaces) that you intend to turn into HBZones and split their component surfaces to ensure that there are matching surfaces between each of the adjacent zones.
_
Matching surfaces and surface areas betweem adjacent zones are necessary to ensure that the conductive heat flow calculation occurs correctly across the surfaces in an energy simulation.
_
Note that the input here should be closed volumes that are adjacent to each other and touching.  They should not volumetrically overlap.
Also note that, while the component has been written in a manner that rarely fails if the input geometry obeys the provisions above, there are still some very complex cases that can be incorrect.
As such, it is recommended that you bake the output of this component and check it in Rhino before turning the breps into HBZones.  This component will get you most of the way there but these volumetric operations can be difficult to pull off with a surface modeler like Rhino so you should really check the output.
-
Provided by Honeybee 0.0.64

    Args:
        bldgMassesBefore: A list of closed breps (polysurfaces) that you intend to turn into HBZones that do not have perfectly matching surfaces between adjacent zones (this matching is needed to contruct a correct multi-zone energy model).
    Returns:
        bldgMassesAfter: The same input closed breps that have had their component surfaces split by adjacent polysurfaces to have matching surfaces between adjacent breps.  It is recommended that you bake this output and check it in Rhino before turning the breps into HBZones.
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import copy
from collections import deque

tol = sc.doc.ModelAbsoluteTolerance


def intersectMasses(bldgNum, building, otherBldg):
    changed = False
    joinedLines = []
    done = False # keep looking until done is True

    # prevent dead loop, will break when no more intersection detected
    while(not done):
        tempBldg = building.Duplicate()
        for face1 in building.Faces:
            if face1.IsSurface:
                # if it is a untrimmed surface just find intersection lines
                intersectLines = rc.Geometry.Intersect.Intersection.BrepSurface(otherBldg, face1.DuplicateSurface(), tol)[1]
            else:
                # if it is a trimmed surface
                edgesIdx = face1.AdjacentEdges()
                edges = []
                for ix in edgesIdx:
                    edges.append(building.Edges.Item[ix])
                crv = rc.Geometry.Curve.JoinCurves(edges, tol)
                # potential bugs: multiple brep of one face?
                intersectLines = rc.Geometry.Intersect.Intersection.BrepBrep(rc.Geometry.Brep.CreatePlanarBreps(crv)[0], otherBldg, tol)[1]
            temp = rc.Geometry.Curve.JoinCurves(intersectLines, tol)
            joinedLines = [crv for crv in temp if rc.Geometry.Brep.CreatePlanarBreps(crv)]
            if len(joinedLines) > 0:
                newBrep = face1.Split(joinedLines, tol) # return None on Failure
                if not newBrep: continue
                if newBrep.Faces.Count > building.Faces.Count:
                    changed = True
                    building = newBrep
                    break
        if tempBldg.Faces.Count == building.Faces.Count:
            done = True
    return building, changed



def main(bldgMassesBefore):
    buildingDict = {}

    for bldgCount, bldg in enumerate(bldgMassesBefore):
        buildingDict[bldgCount] = bldg
    need_change = deque(buildingDict.keys())

    i = 0 # to prevent dead loop
    while(len(need_change) > 0 and i < 10e2*len(bldgMassesBefore)):
        bldgNum = need_change.pop()
        building = buildingDict[bldgNum]
        for num_other in buildingDict.keys():
            if num_other == bldgNum: continue
            otherBldg = buildingDict[num_other]
            building, changed = intersectMasses(bldgNum, building, otherBldg)
            buildingDict[bldgNum] = building
            if changed and num_other not in need_change:
                # for reinforcement of matching, not neccessary
                need_change.appendleft(num_other)
        i += 1
    return buildingDict.values()

success = True
Hzones = False

if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): success = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): success = False
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        success = False

    if success == True:
        hb_hive = sc.sticky["honeybee_Hive"]()
        try:
            for HZone in _bldgMassesBefore:
                zone = hb_hive.callFromHoneybeeHive([HZone])[0]
                Hzones = True
        except: pass

    if Hzones == True:
        warning = "This component only works with raw Rhino brep geometry and not HBZones.  Use this component before you turn your breps into HBZones."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    warning = "You should first let Honeybee fly!"
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning)

# add an compile toggle, set _compile to True to run the function
if _bldgMassesBefore and _bldgMassesBefore[0]!=None and Hzones == False and _runIt:
    bldgMassesAfter = main(_bldgMassesBefore)