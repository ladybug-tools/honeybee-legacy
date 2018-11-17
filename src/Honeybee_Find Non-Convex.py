# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Honeybee.
#
# Copyright (c) 2013-2018, Devang Chauhan <devang@outlook.in>
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
In EnergyPlus, Solar distribution determines how EnergyPlus treats the beam solar radiation and reflectances from exterior surfaces that strike the building, and ultimately, enter the zone. There are five choices: MinimalShadowing, FullExterior and FullInteriorAndExterior, FullExteriorWithReflections, FullInteriorAndExteriorWithReflections. If you intend to use either of FullInteriorAndExterior, FullExteriorWithReflections, FullInteriorAndExteriorWithReflections, you must make sure that all your zones are convex.
_

If you encounter a severe error saying, "DetermineShadowingCombinations: There are # surfaces which are casting surfaces and are non-convex," you should find those non-convex surface in your model and turn them into convex surfaces by splitting them.

_
Spotting a non-convex surface is quite easy. While this component is here to quickly help you detect non-convex surfaces in your model, having conceptual understanding about what it means to have a no-convex surface will make you aware of such surfaces while you are creating zones. 
_
Following are a couple ways to eyeball a non-convex surface.
_
1. Imagine youre drawing lines from one vertice of a surface to all other vertices of the same surface and youre doing this for all the vertices of the surface. Now if all those lines fall totally inside the surface then its a convex surface. If any of the lines, or even a part of it falls outside of the surface then its a non-convex surface.
_
2. Imagine you are walking from one vertice of a surface to the next verice of the same surface, and you are travelling to all the vertices of the surface like that. While making this journey, you'll make turns. If all those turns that you took at vertices, are either clockwise or counter-clockwise, then the surface is convex. If at least one of the turns was in the opposite direction, meaning, if total number of turns you took were 6, and out of those, 5 times you turned clockwise (or counter-clockwise) and one time you turned counter-clockwise (or clockwise), then it is a non-convex surface.
_
3. EnergyPlus displays severe error for non-convex zones. So if any of the face of the zone is made of more than one planar surfaces, and none of those surfaces are non-convex, however, if the resultant zone is not convex then EnergyPlus will still announce a severe error. To address this, in addition to providing your breps as input to this component,  please also pass your breps through the native grasshopper Merge Faces (FMerge) component. And then provide the output of FMerge component (Simplified Brep) to the input of this component.
_
Please visit the following link to know why EnegyPlus does not like non-convex surfaces.
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-simulation-parameters.html#field-solar-distribution
-
Provided by Honeybee 0.0.64

    Args:
        _breps: A list of breps that you wish to scan for non-convex surfaces
    Returns:
        readMe!: Messages
        nonConvex: A list of non-convex surfaces, if found in breps provided.
        faultyGeometry: A list of faultyGeometry if found in breps provided. Typically these are surfaces with more edge curves than the visibale edges of the surface. If such surfaces are found in your model, please use native  grasshopper Deconstruct Brep component to analyze the faultyGeometry.

"""

ghenv.Component.Name = "Honeybee_Find Non-Convex"
ghenv.Component.NickName = 'IsConvex'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino
import Grasshopper.Kernel as gh
import scriptcontext as sc


def checkTheInputs():
    total = 0
    for brep in _breps:
        if type(brep) != Rhino.Geometry.Brep:
            total += 1
    if total > 0:
        warning = 'Please check inputs. This component only accepts breps.'
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return False
    else:
        return True


def main():
    # import the classes
    if sc.sticky.has_key('honeybee_release'):

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
        
        #Bringing NonConvexChecking class from Honeybee_Honeybee
        hb_NonConvexChecking = sc.sticky["honeybee_NonConvexChecking"]
        
        nonConvex = []
        faultyGeometry = []
        
        for brep in _breps:
            surfaces = [brep.Faces.ExtractFace(i) for i in range(brep.Faces.Count)]
            for surface in surfaces:
                if hb_NonConvexChecking(surface).isConvex()[0] == False:
                    nonConvex.append(surface)
                if hb_NonConvexChecking(surface).isConvex()[1] > 0:
                    faultyGeometry.extend(hb_NonConvexChecking(surface).isConvex()[1])
                    
        if len(nonConvex) == 0:
            print "No non-convex surfaces are found in provided brep / breps."          
        
        if len(faultyGeometry) == 0:
            print "No faulty geometry has been found in provided brep / breps."          
        
        if len(faultyGeometry) > 0:
            warning = 'Faulty geometry has been found in the brep / breps you provided. Please take analyze these faultyGeometries using native grasshopper Deconstruct Brep component and fix them.'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)        
        
        return (nonConvex , faultyGeometry)
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1    

#If the intital check is good, run the component.
checkData = checkTheInputs()
if checkData:
    result = main()
    if result != -1:
        nonConvex, faultyGeometry = result
        

