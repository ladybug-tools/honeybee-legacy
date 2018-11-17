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
        _skyLightRatio: If you have input a full zone or roof surface as your HBObjects, use this input to generate skylights on the roof surfaces. A single window for each surface is good for making energy simulations run fast while several distributed windows is often necessary to have accurate daylight simulations or high-resolution thermal maps. The default is set to "True" to generate multiple distributed windows.
        breakUpSkylight_: Set to "True" to generate a distributed set of multiple windows for skylights and set to "False" to generate just a single window per roof surface.
        skyLightBreakUpDist_: An optional number in Rhino model units that sets the distance between individual skylights when the breakUpSkylight_ input above is set to 'True'.  The default is set to 3 meters.
        EPConstruction_: A optional text string of an EnergyPlus construction name that sets the material construction of the window. The default will assign a generic double pane window without low-e coatings.
        RADMaterial_: A optional text string of an Radiance glass material name that sets the material of the window.
        _runIt: set runIt to True to generate the glazing
    Returns:
        readMe!: ...
        HBObjWGLZ: Newhoneybee zones that contain glazing surfaces based on the parameters above. 
"""

ghenv.Component.Name = "Honeybee_Skylight Based on Ratio"
ghenv.Component.NickName = 'skylightCreator'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nJAN_01_2017
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
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

def findGlzBasedOnRatio(baseSrf, glzRatio, breakUpWindow, breakUpDist, conversionFactor, hb_GlzGeoGeneration):
    lastSuccessfulRestOfSrf = []
    
    #Check if the surface is a planar surface
    planarBool = rc.Geometry.BrepFace.IsPlanar(baseSrf.Faces[0], sc.doc.ModelAbsoluteTolerance)
    
    #Rebuild and simplify the surface to ensure best results when generating the glazing.
    edgeLinear = True
    createdNew = False
    edges = baseSrf.Edges
    joinedEdges = rc.Geometry.Curve.JoinCurves(edges)
    simplificationOpt = rc.Geometry.CurveSimplifyOptions.All
    
    joinedEdgesSimplified = []
    for crv in joinedEdges:
        joinedEdgesSimplified.append(crv.Simplify(simplificationOpt, sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAngleToleranceRadians))
    
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
                if rc.Geometry.BrepEdge.IsLinear(edge, sc.doc.ModelAbsoluteTolerance):
                    pass
                else:
                    edgeLinear = False
        else: pass
    
    #Check if the surface is a planar skylight that can be broken up into quads and, if so, send it through the skylight generator
    glazing, lastSuccessfulRestOfSrf = hb_GlzGeoGeneration.createSkylightGlazing(baseSrf, glzRatio, planarBool, edgeLinear, breakUpWindow, breakUpDist, conversionFactor)
    
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

def main(skyLightRatio, breakUpSkylight, skyLightBreakUpDist, EPConstruct, RADMat):
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
        return [], []
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBObjects)
    
    #Check constructions and RADMAterials.
    if EPConstruct != None:
        constrCheck = checkEPConstr(EPConstruct, hb_EPObjectsAux)
        if constrCheck != None:
            EPConstruct = constrCheck
        else:
            return -1
    if RADMat != None:
        matCheck = checkRADMat(RADMat, hb_RADMaterialAUX)
        if matCheck != None:
            RADMat = matCheck
        else:
            return -1
    
    #Get the conversion factor (for the future when HB is availble in other model units).
    conversionFactor = lb_preparation.checkUnits()
    
    #Set the final lists to be filled.
    joinedSrf = []
    zonesWithOpeningsGeometry =[]
    ModifiedHBZones = []
    
    if HBZoneObjects and HBZoneObjects[0] != None:
        # collect the surfaces
        HBSurfaces = []
        for HBObj in HBZoneObjects:
            if HBObj.objectType == "HBZone":
                for surface in HBObj.surfaces: HBSurfaces.append(surface)
            elif HBObj.objectType == "HBSurface":
                if not hasattr(HBObj, 'type'):
                    # find the type based on 
                    HBObj.type = HBObj.getTypeByNormalAngle()
                
                if not hasattr(HBObj, "BC"):
                    HBObj.BC = 'OUTDOORS'
                HBSurfaces.append(HBObj)
        
        for surface in HBSurfaces:
            if skyLightRatio!=0 and surface.BC.upper() == 'OUTDOORS' and surface.type == 1:
                if surface.hasChild:
                    surface.removeAllChildSrfs()
                
                face = surface.geometry # call surface geometry
                
                # This part of the code sends the parameters and surfaces to their respective methods of of galzing generation.  It is developed by Chris Mackey.
                lastSuccessfulGlzSrf, lastSuccessfulRestOfSrf = findGlzBasedOnRatio(face, skyLightRatio, breakUpSkylight, skyLightBreakUpDist, conversionFactor, hb_GlzGeoGeneration)
                
                if lastSuccessfulGlzSrf!= None:
                    if isinstance(lastSuccessfulGlzSrf, list):
                        for glzSrfCount, glzSrf in enumerate(lastSuccessfulGlzSrf):
                            fenSrf = hb_EPFenSurface(glzSrf, surface.num, surface.name + '_glz_' + `glzSrfCount`, surface, 5, lastSuccessfulRestOfSrf)
                            if EPConstruct != None:
                                fenSrf.setEPConstruction(EPConstruct)
                            if RADMat != None:
                                addedToLib, fenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMat, True)
                            zonesWithOpeningsGeometry.append(glzSrf)
                            surface.addChildSrf(fenSrf)
                        if lastSuccessfulRestOfSrf==[]:
                            surface.calculatePunchedSurface()
                    else:
                        fenSrf = hb_EPFenSurface(lastSuccessfulGlzSrf, surface.num, surface.name + '_glz_0', surface, 5, lastSuccessfulRestOfSrf)
                        if EPConstruct != None:
                            fenSrf.setEPConstruction(EPConstruct)
                        if RADMat != None:
                            addedToLib, fenSrf.RadMaterial = hb_RADMaterialAUX.analyseRadMaterials(RADMat, True)
                        zonesWithOpeningsGeometry.append(lastSuccessfulGlzSrf)
                        surface.addChildSrf(fenSrf)
                        if lastSuccessfulRestOfSrf==[]: surface.calculatePunchedSurface()
        
        #add zones to dictionary
        ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component)
        
    return zonesWithOpeningsGeometry, ModifiedHBZones

if _runIt and _HBObjects and _HBObjects[0]:
    results = main(_skyLightRatio, breakUpSkylight_, skyLightBreakUpDist_, EPConstruction_, RADMaterial_)
    if results!= -1:
        glazingSrf, HBObjWGLZ = results