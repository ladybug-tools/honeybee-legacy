# glazingCreator
# The main geometry-generating parts of this component are developed by Chris Mackey
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com - mostapha@ladybug.tools> 
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
Use this component to generate windows for a HBSurface or HBZone based on a desired window-to-wall ratio. In addition to generating window geometry that corresponds with the input ratio, this component also allows you a fairly high level of control over the window geometry.
_
The first way in which you gain additional control over geometry is the option of whether you want to generate a single window for each surface, which is good for making energy simulations run fast, or you want to use the glazig ratio to create several windows distributed across the surfaces, which is often necessary to have accurate daylight simulations or high-resolution thermal maps.
If you break up the window into several ones, you also have the ability to set the distance between each of the windows along the surface.
_
If you input wall surfaces that have perfectly horizontal tops and/or bottoms, you also have access to a number of other other inputs such as window height, the sill height, and whether you want to split the glazing vertically into two windows.
-
Provided by Honeybee 0.0.64
    
    Args:
        _HBObjects: Honeybee thermal zones or surfaces for which glazing should be generated.
        _glzRatio: The fraction of the wall surface that should be glazed.  This input only accepts values between 0 and 0.95 (we don't go all of the way up to 1 because EnergyPlus does not like this).  This input can also accept lists of values and will assign different glazing ratios based on cardinal direction, starting with north and moving counter-clockwise.  Note that glazing ratio always takes priority over the windowHeight and sillHeight inputs below.
        breakUpWindow_: Set to "True" to generate a distributed set of multiple windows on walls and set to "False" to generate just a single window per rectangular wall surface.  This input can also accept lists of boolean values and will assign different 'BreakUpWindow' values based on cardinal direction, starting with north and moving counter-clockwise.  A single window for each surface is good for making energy simulations run fast while several distributed windows is often necessary to have accurate daylight simulations or high-resolution thermal maps. The default is set to "True" to generate multiple distributed windows.
        breakUpDist_: An optional number in Rhino model units that sets the distance between individual windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different sill heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios or window heights.  The default is set to 2 meters.
        windowHeight_: An optional number in Rhino model units that sets the height of your windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different window heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios. The default is set to 2 meters.
        sillHeight_: An optional number in Rhino model units that sets the distance from the floor to the bottom of your windows on rectangular surfaces when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different sill heights based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios or window heights.  The default is set to 0.8 meters (or 80 centimeters).
        splitGlzVertDist_: An optional number in Rhino model units that splits the windows on rectangular surfaces into two with a vertical distance between them equal to this input when the breakUpWindow_ input above is set to 'True'.  This input can also accept lists of values and will assign different vertical distances based on cardinal direction, starting with north and moving counter-clockwise.  Note that this input will be over-ridden at high glazing ratios, high window heights, or high sill heights.
        EPConstructions_: A optional text string of an EnergyPlus construction name that sets the material construction of the window. This input can also accept lists of values and will assign different EPconstructions based on cardinal direction, starting with north and moving counter-clockwise.  The default will assign a generic double pane window without low-e coatings.
        RADMaterials_: A optional text string of an Radiance glass material name that sets the material of the window. This input can also accept lists of values and will assign different RadMaterials based on cardinal direction, starting with north and moving counter-clockwise.
        _runIt: set runIt to True to generate the glazing
    Returns:
        readMe!: ...
        HBObjWGLZ: Newhoneybee zones that contain glazing surfaces based on the parameters above. 
"""

ghenv.Component.Name = "Honeybee_Glazing based on ratio"
ghenv.Component.NickName = 'glazingCreator'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nJAN_01_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import math
import uuid

# all this only to graft the data at the end! booooooo
import Grasshopper.Kernel as gh
import System
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

tol = sc.doc.ModelAbsoluteTolerance


def checkEPConstr(EPConstruction, hb_EPObjectsAux):
    # if it is just the name of the material make sure it is already defined
    if len(EPConstruction.split("\n")) == 1:
        # if the material is not in the library add it to the library
        if not hb_EPObjectsAux.isEPConstruction(EPConstruction):
            warningMsg = "Can't find " + EPConstruction + " in EP Construction Library.\n" + \
                        "Add the construction to the library and try again."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            return None
    else:
        # it is a full string.
        if EPConstruction.startswith('WindowMaterial:'):
            warningMsg = "Your window construction, " + EPConstruction.split('\n')[1].split(',')[0] + ", is a window material and not a full window construction.\n" + \
                        "Pass this window material through a 'Honeybee_EnergyPlus Construction' component cand connect the construction to this one."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            return None
        added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(EPConstruction, overwrite = True)
        
        if not added:
            msg = EPConstruction + " is not added to the project library!"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            print msg
            return None
    return EPConstruction

def checkRADMat(RADMaterial, hb_RADMaterialAUX):
    if len(RADMaterial.strip().split(" ")) == 1:
        if not hb_RADMaterialAUX.isMatrialExistInLibrary(RADMaterial):
            warningMsg = "Can't find " + RADMaterial + " in RAD Material Library.\n" + \
                "Add the material to the library and try again."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            return None
    return RADMaterial

def findGlzBasedOnRatio(baseSrf, glzRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor, hb_GlzGeoGeneration):
    lastSuccessfulRestOfSrf = []
    
    #Check if the surface is a planar surface
    planarBool = rc.Geometry.BrepFace.IsPlanar(baseSrf.Faces[0], tol)
    
    #Rebuild and simplify the surface to ensure best results when generating the glazing.
    edgeLinear = True
    createdNew = False
    edges = baseSrf.Edges
    joinedEdges = rc.Geometry.Curve.JoinCurves(edges)
    simplificationOpt = rc.Geometry.CurveSimplifyOptions.All
    
    joinedEdgesSimplified = []
    for crv in joinedEdges:
        joinedEdgesSimplified.append(crv.Simplify(simplificationOpt, tol, sc.doc.ModelAngleToleranceRadians))
    
    originalSrfDir = baseSrf.Faces[0].NormalAt(0,0)
    if planarBool == True:
        try:
            baseSrf = rc.Geometry.Brep.CreatePlanarBreps(joinedEdgesSimplified)[0]
            createdNew = True
        except:
            createdNew = False
    newSrfDir = baseSrf.Faces[0].NormalAt(0,0)
    
    #If the direction of the rebuilt surface is not the same as that of the original surface, flip it around.
    if createdNew == True:
        if newSrfDir.X < originalSrfDir.X + tol and newSrfDir.X > originalSrfDir.X - tol and newSrfDir.Y < originalSrfDir.Y + tol and newSrfDir.Y > originalSrfDir.Y - tol and newSrfDir.Z < originalSrfDir.Z + tol and newSrfDir.Z > originalSrfDir.Z - tol:
            pass
        else:
            baseSrf.Flip()
    else: pass
    
    
    #Check if the surface has any curved edges to it
    for crv in joinedEdgesSimplified:
        if crv != None:
            for edge in crv.DuplicateSegments():
                if rc.Geometry.BrepEdge.IsLinear(edge, tol):
                    pass
                else:
                    edgeLinear = False
        else: pass
    
    #Check if the wall surface has horizontal top and bottom curves and contains a rectangle that can be extracted such that we can apply the windowHeight and sillHeight inputs to it.
    if planarBool == True and edgeLinear == True and hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[1] == True and hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[3] == True:
        if breakUpWindow == False and baseSrf.Edges.Count == 4:
            glazing = hb_GlzGeoGeneration.createGlazingQuad(baseSrf, glzRatio, None)
        else:
            glazing = hb_GlzGeoGeneration.createGlazingThatContainsRectangle(hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[2], hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[0], baseSrf, glzRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor)
    
    #Check if the wall surface has vertical sides and contains a rectangle that can be extracted such that we can apply the windowheight and sill height inputs to it.
    elif planarBool == True and edgeLinear == True and hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[5] == True:
        if breakUpWindow == False and baseSrf.Edges.Count == 4:
            glazing = hb_GlzGeoGeneration.createGlazingQuad(baseSrf, glzRatio, None)
        else:
            glazing = hb_GlzGeoGeneration.createGlazingThatContainsRectangle(hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[4][0], hb_GlzGeoGeneration.getTopBottomCurves(baseSrf)[4][1], baseSrf, glzRatio, windowHeight, sillHeight, breakUpWindow, breakUpDist, splitVertDist, conversionFactor)
    
    #Since the surface does not seem to have a rectangle that can be extracted, check to see if it is a triangle for which we can use a simple mathematical relation.
    elif planarBool == True and baseSrf.Edges.Count == 3:
        glazing = hb_GlzGeoGeneration.createGlazingTri(baseSrf, glzRatio, None)
    
    #Since the surface does not seem to have a rectangle and is not a triangle, check to see if it is a just an odd-shaped quarilateral for which we can use a mathematical relation.
    elif planarBool == True and edgeLinear == True and baseSrf.Edges.Count == 4:
        glazing = hb_GlzGeoGeneration.createGlazingQuad(baseSrf, glzRatio, None)
    
    #Since the surface does not have a rectangle, is not a triangle, and is not a quadrilateral but still may be planar, we will break it into triangles and quads by meshing it such that we can use the previous formulas.
    elif planarBool == True and edgeLinear == True and breakUpWindow == True:
        glazing = hb_GlzGeoGeneration.createGlazingOddPlanarGeo(baseSrf, glzRatio)
    
    #If the surface fits the criteria above but the user does not want to break up the window, we will offset the curve on the surface so that we hopefully end up with just one window.
    elif planarBool == True and edgeLinear == True:
        glazing, lastSuccessfulRestOfSrf = hb_GlzGeoGeneration.createGlazingCurved(baseSrf, glzRatio, planarBool)
    
    #If everything has failed up until this point, this means that the wall geometry is likely curved.  The best way forward is just to try to offset the curve on the surface to get the window.
    else:
        glazing, lastSuccessfulRestOfSrf = hb_GlzGeoGeneration.createGlazingCurved(baseSrf, glzRatio, planarBool)
    
    
    #Check to make sure that a window has been generated and, if so, check to make sure that the window that has been generated is facing the right direction.  If not, flip it.
    if glazing == None:
        print "Failed to calculate the glazing"
        pass
    else:
        try:
            len(glazing)
        except:
            glazing = [glazing]
        
        for window in glazing:
            windowDir = window.Faces[0].NormalAt(0,0)
            if windowDir.X < originalSrfDir.X + tol and windowDir.X > originalSrfDir.X - tol and windowDir.Y < originalSrfDir.Y + tol and windowDir.Y > originalSrfDir.Y - tol and windowDir.Z < originalSrfDir.Z + tol and windowDir.Z > originalSrfDir.Z - tol:
                pass
            else:
                window.Flip()
    
    if lastSuccessfulRestOfSrf==[]:
        lastSuccessfulRestOfSrf = hb_GlzGeoGeneration.getRestOfSurfacePlanar(baseSrf, glazing)
    
    return glazing, lastSuccessfulRestOfSrf

def giveWarning(message):
    print message
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, message)

def main(windowHeight, sillHeight, glzRatio, breakUpWindow, breakUpDist, splitGlzVertDist, EPConstructions, RADMaterials):
    # check if honeybee is flying
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
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
    
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            " Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_GlzGeoGeneration = sc.sticky["honeybee_GlzGeoGeneration"]()
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBObjects)
    
    #Check constructions and RADMAterials.
    for count, constr in enumerate(EPConstructions):
        constrCheck = checkEPConstr(constr, hb_EPObjectsAux)
        if constrCheck != None:
            EPConstructions[count] = constrCheck
        else:
            return -1
    for count, mat in enumerate(RADMaterials):
        matCheck = checkRADMat(mat, hb_RADMaterialAUX)
        if matCheck != None:
            RADMaterials[count] = matCheck
        else:
            return -1
    
    #Get the conversion factor (for the future when HB is availble in other model units).
    conversionFactor = lb_preparation.checkUnits()
    
    #Set the final lists to be filled.
    joinedSrf = []
    zonesWithOpeningsGeometry =[]
    ModifiedHBZones = []
    
    #Check if the length of the glzRatio, windowHeight, and sillHeight lists are the same.
    numOfDivisions = []
    warningList = []
    listLenCheck = True
    
    if len(glzRatio) == 1:
        if len(windowHeight) != 1 and len(windowHeight) != 0: numOfDivisions.append(len(windowHeight))
        if len(sillHeight) != 1 and len(sillHeight) != 0: numOfDivisions.append(len(sillHeight))
        if len(breakUpDist) != 1 and len(breakUpDist) != 0: numOfDivisions.append(len(breakUpDist))
        if len(breakUpWindow) != 1 and len(breakUpWindow) != 0: numOfDivisions.append(len(breakUpWindow))
        if len(splitGlzVertDist) != 1 and len(splitGlzVertDist) != 0: numOfDivisions.append(len(splitGlzVertDist))
        if len(EPConstructions) != 1 and len(EPConstructions) != 0: numOfDivisions.append(len(EPConstructions))
        if len(RADMaterials) != 1 and len(RADMaterials) != 0: numOfDivisions.append(len(RADMaterials))
        if numOfDivisions != []:
            allValuesSame = True
            for val in numOfDivisions:
                if val == numOfDivisions[0]: pass
                else: allValuesSame = False
            if allValuesSame == True:
                glzRatioNew = []
                #duplicate the glazing ratio list.
                for val in range(numOfDivisions[-1]): glzRatioNew.append(glzRatio[0])
                glzRatio = glzRatioNew
            else:
                listLenCheck = False
                warning = "The lengths of the lists across your inputs do not match.  Please ensure that you put in only one value for each paremter or your values are lists with lengths that match across your inputs."
                giveWarning(warning)
    else:
        if len(windowHeight) != len(glzRatio) and len(windowHeight) != 1 and len(windowHeight) != 0: warningList.append("The number of items in the windowHeight list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single windowHeight value for all windows.")
        if len(sillHeight) != len(glzRatio) and len(sillHeight) != 1 and len(sillHeight) != 0: warningList.append("The number of items in the sillHeight list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single sillHeight value for all windows.")
        if len(breakUpDist) != len(glzRatio) and len(breakUpDist) != 1 and len(breakUpDist) != 0: warningList.append("The number of items in the breakUpDist list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single breakUpDist value for all windows.")
        if len(breakUpWindow) != len(glzRatio) and len(breakUpWindow) != 1 and len(breakUpWindow) != 0: warningList.append("The number of items in the breakUpWindow list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single breakUpWindow value for all windows.")
        if len(splitGlzVertDist) != len(glzRatio) and len(splitGlzVertDist) != 1 and len(splitGlzVertDist) != 0: warningList.append("The number of items in the splitGlzVertDist list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single splitGlzVertDist value for all windows.")
        if len(EPConstructions) != len(glzRatio) and len(EPConstructions) != 1 and len(EPConstructions) != 0: warningList.append("The number of items in the EPConstructions list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single EPConstruction value for all windows.")
        if len(RADMaterials) != len(glzRatio) and len(RADMaterials) != 1 and len(RADMaterials) != 0: warningList.append("The number of items in the RADMaterials list does not match the number in the glzRatio list. Please ensure that either your lists match or you put in a single RADMaterial value for all windows.")
        if warningList != []:
            for warning in warningList:
                giveWarning(warning)
                listLenCheck = False
    
    # find the percentage of glazing for each direction based on the input list
    angles = []
    if len(glzRatio)!=0:
        for ratio in glzRatio:
            if ratio > 0.95:
                giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are not accepted.")
                return -1
        initAngles = rs.frange(0, 360, 360/len(glzRatio))
    else: initAngles = []
    #Set up angles if the glazing ratio is greater than 1.
    if len(glzRatio) > 1:
        for an in initAngles: angles.append(an-(360/(2*len(glzRatio))))
        angles.append(360)
    else: angles = initAngles
    
    if HBZoneObjects and HBZoneObjects[0] != None and listLenCheck == True:
        # collect the surfaces
        HBSurfaces = []
        for HBObj in HBZoneObjects:
            if HBObj.objectType == "HBZone":
                for surface in HBObj.surfaces: HBSurfaces.append(surface)
            elif HBObj.objectType == "HBSurface":
                
                if not hasattr(HBObj, 'type'):
                    # find the type based on 
                    HBObj.type = HBObj.getTypeByNormalAngle()
                
                if not hasattr(HBObj, 'angle2North'):
                    # find the type based on
                    HBObj.getAngle2North()
                
                if not hasattr(HBObj, "BC"):
                    HBObj.BC = 'OUTDOORS'
                    
                HBSurfaces.append(HBObj)
                
        
        for surface in HBSurfaces:
            if surface.BC.upper() == 'OUTDOORS' and surface.type == 0:
                if surface.hasChild:
                    surface.removeAllChildSrfs()
                targetPercentage = 0
                winHeight = None
                sill = None
                breakD = None
                breakWind = True #Best variable name ever!
                splitVertDist = None
                
                if len(glzRatio) == 1: targetPercentage = glzRatio[0]
                if len(windowHeight) == 1: winHeight = windowHeight[0]
                if len(sillHeight) == 1: sill = sillHeight[0]
                if len(breakUpDist) == 1: breakD = breakUpDist[0]
                if len(breakUpWindow) == 1: breakWind = breakUpWindow[0]
                if len(splitGlzVertDist) == 1: splitVertDist = splitGlzVertDist[0]
                if len(EPConstructions) == 1: EPConstruct = EPConstructions[0]
                if len(RADMaterials) == 1: RADMat = RADMaterials[0]
                for angleCount in range(len(angles)-1):
                    if angles[angleCount]+(0.5*sc.doc.ModelAngleToleranceDegrees) <= surface.angle2North%360 <= angles[angleCount +1]+(0.5*sc.doc.ModelAngleToleranceDegrees):
                        targetPercentage = glzRatio[angleCount%len(glzRatio)]
                        if len(windowHeight) == len(glzRatio):
                            winHeight = windowHeight[angleCount%len(windowHeight)]
                        if len(sillHeight) == len(glzRatio):
                            sill = sillHeight[angleCount%len(sillHeight)]
                        if len(breakUpDist) == len(glzRatio):
                            breakD = breakUpDist[angleCount%len(breakUpDist)]
                        if len(breakUpWindow) == len(glzRatio):
                            breakWind = breakUpWindow[angleCount%len(breakUpWindow)]
                        if len(splitGlzVertDist) == len(glzRatio):
                            splitVertDist = splitGlzVertDist[angleCount%len(splitGlzVertDist)]
                        if len(EPConstructions) == len(glzRatio):
                            EPConstruct = EPConstructions[angleCount%len(EPConstructions)]
                        if len(RADMaterials) == len(glzRatio):
                            RADMat = RADMaterials[angleCount%len(RADMaterials)]
                        break
                
                if targetPercentage!=0:
                    face = surface.geometry # call surface geometry
                    
                    # This part of the code sends the parameters and surfaces to their respective methods of of galzing generation.  It is developed by Chris Mackey.
                    lastSuccessfulGlzSrf, lastSuccessfulRestOfSrf = findGlzBasedOnRatio(face, targetPercentage, winHeight, sill, breakWind, breakD, splitVertDist, conversionFactor, hb_GlzGeoGeneration)
                    
                    if lastSuccessfulGlzSrf!= None:
                        if isinstance(lastSuccessfulGlzSrf, list):
                            for glzSrfCount, glzSrf in enumerate(lastSuccessfulGlzSrf):
                                fenSrf = hb_EPFenSurface(glzSrf, surface.num, surface.name + '_glz_' + `glzSrfCount`, surface, 5, lastSuccessfulRestOfSrf)
                                try:
                                    fenSrf.setEPConstruction(EPConstruct)
                                except: pass
                                try:
                                    addedToLib, fenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMat, True)
                                except: pass
                                zonesWithOpeningsGeometry.append(glzSrf)
                                surface.addChildSrf(fenSrf)
                            if lastSuccessfulRestOfSrf==[]:
                                surface.calculatePunchedSurface()
                        else:
                            fenSrf = hb_EPFenSurface(lastSuccessfulGlzSrf, surface.num, surface.name + '_glz_0', surface, 5, lastSuccessfulRestOfSrf)
                            try:
                                fenSrf.setEPConstruction(EPConstruct)
                            except: pass
                            try:
                                addedToLib, fenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMat, True)
                            except: pass
                            zonesWithOpeningsGeometry.append(lastSuccessfulGlzSrf)
                            surface.addChildSrf(fenSrf)
                            if lastSuccessfulRestOfSrf==[]: surface.calculatePunchedSurface()
        
        #add zones to dictionary
        ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component)
        
        return zonesWithOpeningsGeometry, ModifiedHBZones
    else:
        return -1

if _runIt and _HBObjects and _HBObjects[0]:
    results = main(windowHeight_, sillHeight_, _glzRatio, breakUpWindow_, breakUpDist_, splitGlzVertDist_, EPConstructions_, RADMaterials_)
    if results!= -1:
        glazingSrf, HBObjWGLZ = results