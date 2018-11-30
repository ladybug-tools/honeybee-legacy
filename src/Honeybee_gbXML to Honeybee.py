#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools>, Chris Mackey <Chris@MackeyArchitecture.com>, and Chien Si Harriman <charriman@terabuild.com>
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
Import gbXML files as Honeybee zones.

This component uses OpenStudio libraries to import all geometry, constrcuctions,
and boundary conditions (including adjacencies).

Loads, schedules, and HVAC systems are not currently imported by this component
and must be reassigned using Honeybee components.
-

Provided by Honeybee 0.0.64
    
    Args:
        _filepath: Full filepath to xml file.
        _zoneNames: The list of names for thermal zones that you want to be loaded
            from the file. By default the component will import all the zones.
        _import: Set to True to import the model.
    Returns:
        readMe!:
        model: OpenStudio model which is created from the gbXML file. This output
            will only be useful for advanced users to develop custom scipts.
        HBZones: List of honeybee zones.
        shadings: List of shading surfaces if any.
"""

ghenv.Component.Name = "Honeybee_gbXML to Honeybee"
ghenv.Component.NickName = 'XMLTOHB'
ghenv.Component.Message = 'VER 0.0.64\nNOV_30_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nSEP_09_2016
#compatibleLBVersion = VER 0.0.59\nJUL_24_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"

import os
import scriptcontext as sc
import Rhino as rc

# check the version of OpenStudio.
try:
    openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
except:
    pass
try:
    osVersion = openStudioLibFolder.split('-')[-1].split('/')[0]
    vernum1, vernum2 = osVersion.split('.')[0], osVersion.split('.')[1]
except:
    vernum1, vernum2= '1', '0'
vers = int(vernum1 + vernum2)


def getHBMaterial(m):
    mat = {}
    s = (o for o in str(m.idfObject()).split('\n') if o.rstrip())
    for c, i in enumerate(s):
        if c == 0:
            mat[0] = i[3:-1] # remove OS:
        elif c < 3:
            continue # name and handle
        else:
            v, cc = i.split('!')
            mat[c - 2] = v.rstrip()[:-1], cc.rstrip()    
    
    return mat


def getHBConstruction(m, materials):
    mat = {}
    s = (o for o in str(m.idfObject()).split('\n') if o.rstrip())
    for c, i in enumerate(s):
        if c == 0:
            mat[0] = i[3:-1] # remove OS:
        elif c < 4:
            continue # name and handle
        else:
            v, cc = i.split('!')
            mat[c - 3] = str(materials[v.strip()[:-1]].name()), cc.rstrip()    
    return mat


def getGeometry(ossurface, minZ=None, maxZ=None, offset=0.01):
    if minZ is not None and maxZ is not None:
        pts = [rc.Geometry.Point3d(p.x(), p.y(), p.z() + offset) if p.z() == minZ
               else rc.Geometry.Point3d(p.x(), p.y(), p.z() - offset) if p.z() == maxZ
               else rc.Geometry.Point3d(p.x(), p.y(), p.z())
               for p in ossurface.vertices()]
    else:
        pts = [rc.Geometry.Point3d(p.x(), p.y(), p.z())
               for p in ossurface.vertices()]
    
    pts.append(pts[0])
    polyline = rc.Geometry.Polyline(pts).ToNurbsCurve()
    return rc.Geometry.Brep.CreatePlanarBreps(polyline)[0]


def getHBSrfType(ossurface):
    
    srfTypeDict = {0:'WALL',
       1:'ROOF',
       2:'FLOOR',
       3:'CEILING',
       4:'WALL',
       5:'WINDOW',
       6:'SHADING',
       'WALL': 0,
       'ROOF':1,
       'ROOFCEILING': 1,
       'FLOOR': 2,
       'CEILING': 3,
       'WINDOW':5,
       'SHADING': 6}
    
    t = str(ossurface.surfaceType()).upper()
    if t in srfTypeDict:
        return srfTypeDict[t]

defaultConstructions = ["Interior Ceiling", "Interior Floor",
                        "Interior Wall", "Interior Window",
                        "Exterior Floor", "Exterior Roof", "Exterior Wall",
                        "Exterior Window"]

def getOSSurfaceConstructionName(s, constructionCollection, missingConstrCount = 0):
    construction = s.construction()
    if construction.is_initialized and not construction.isNull():
        construction = construction.get()
    if not hasattr(construction, 'name'):
        missingConstrCount += 1
        #print 'Construction for {} is missing. Default construction will be used.'.format(s.name())
        return None, missingConstrCount
    else:
        if vers < 27:
            if str(construction.name()) in defaultConstructions:
                return None, missingConstrCount
            if not str(construction.name()).upper() in constructionCollection:
                print 'Failed to find {} in constructions.'.format(construction.name())
                return None, missingConstrCount
            else:
                return str(construction.name()).upper(), missingConstrCount
        else:
            if str(construction.nameString()) in defaultConstructions:
                return None, missingConstrCount
            if not str(construction.nameString()).upper() in constructionCollection:
                print 'Failed to find {} in constructions.'.format(construction.nameString())
                return None, missingConstrCount
            else:
                return str(construction.nameString()).upper(), missingConstrCount

def updateAdj(surface1, surface2):
    # change roof to ceiling
    # the same for ceiling on ground
    if int(surface1.type) == 1: surface1.setType(3) # roof + adjacent surface = ceiling
    elif int(surface2.type) == 1: surface2.setType(3)
    
    # Change different floor types to be floors between zones.
    if int(surface1.type) == 2: surface1.setType(2)
    if int(surface2.type) == 2:  surface2.setType(2)
    
    # change construction
    if surface1.EPConstruction == None:
        surface1.setEPConstruction(surface1.intCnstrSet[surface1.type])
        surface2.setEPConstruction(surface1.intCnstrSet[surface2.type])
    else:
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        hb_EPObjectsAux.assignEPConstruction(surface1, surface1.EPConstruction, ghenv.Component)
        hb_EPObjectsAux.assignEPConstruction(surface2, surface1.EPConstruction, ghenv.Component)
    
    # change bc
    surface1.setBC('SURFACE', True)
    surface2.setBC('SURFACE', True)
    # change bc.Obj
    # used to be only a name but I changed it to an object so you can find the parent, etc.
    surface1.setBCObject(surface2)
    surface2.setBCObject(surface1)
    
    # set sun and wind exposure to no exposure
    surface2.setSunExposure('NoSun')
    surface1.setSunExposure('NoSun')
    surface2.setWindExposure('NoWind')
    surface1.setWindExposure('NoWind')
    
    # check for child objects
    if (surface1.hasChild or surface2.hasChild) and (len(surface2.childSrfs)!= len(surface1.childSrfs)):
        # give warning
        warnMsg= "Number of windows doesn't match between " + surface1.name + " and " + surface2.name + "." + \
                 " Make sure adjacent surfaces are divided correctly and have similar windows."
        print warnMsg
    
    if surface1.hasChild and surface2.hasChild:
        # find child surfaces that match the other one
        for childSurface1 in surface1.childSrfs:
            for childSurface2 in surface2.childSrfs:
                if childSurface1.cenPt.DistanceTo(childSurface2.cenPt) <= sc.doc.ModelAbsoluteTolerance:
                    childSurface1.BCObject.name = childSurface2.name
                    childSurface2.BCObject.name = childSurface1.name
                    # change construction
                    if childSurface1.EPConstruction == None:
                        childSurface1.setEPConstruction(surface1.intCnstrSet[5])
                        childSurface2.setEPConstruction(surface1.intCnstrSet[5])
                    else:
                        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
                        hb_EPObjectsAux.assignEPConstruction(childSurface1, childSurface1.EPConstruction, ghenv.Component)
                        hb_EPObjectsAux.assignEPConstruction(childSurface2, childSurface1.EPConstruction, ghenv.Component)
                    # change the boundary condition
                    childSurface1.setBC('SURFACE', True)
                    childSurface2.setBC('SURFACE', True)
                    childSurface1.setBCObject(childSurface2)
                    childSurface2.setBCObject(childSurface1)
                    # set sun and wind exposure to no exposure
                    childSurface2.setSunExposure('NoSun')
                    childSurface1.setSunExposure('NoSun')
                    childSurface2.setWindExposure('NoWind')
                    childSurface1.setWindExposure('NoWind')

if sc.sticky.has_key('honeybee_release'):

    EPZone = sc.sticky["honeybee_EPZone"]
    EPSrf = sc.sticky["honeybee_EPSurface"]
    EPZoneSurface = sc.sticky["honeybee_EPZoneSurface"]
    EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
    EPSHDSurface = sc.sticky["honeybee_EPShdSurface"]

    if sc.sticky["honeybee_folders"]["OSLibPath"] != None:
        # openstudio is there
        openStudioLibFolder = sc.sticky["honeybee_folders"]["OSLibPath"]
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder + "\\openStudio.dll")
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
        
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg1 = "You do not have OpenStudio installed on Your System.\n" + \
            "You wont be able to use this component until you install it.\n" + \
            "Download the latest OpenStudio for Windows from:\n"
        msg2 = "https://www.openstudio.net/downloads"
        print msg1
        print msg2
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
else:
    openStudioIsReady = False

if openStudioIsReady and _import and _filepath:
    
    _filepath = _filepath.replace('\\\\', '/').replace('\\', '/')
    assert os.path.isfile(_filepath), \
        'Failed to find the xml file at {}.'.format(_filepath)
    assert _filepath.lower().endswith('.xml'), \
        '{} does not end with .xml. Not a valid xml file.'.format(_filepath)
    translator = ops.GbXMLReverseTranslator()
    try:
        model = translator.loadModel(ops.Path(os.path.normpath(_filepath)))
    except TypeError:
        filepath = ops.OpenStudioUtilitiesCore.toPath(os.path.normpath(_filepath))
        if vers < 27:
            # OpenStudio 2.6.1
            model = translator.loadModel(ops.Path(filepath))
        else:
            # OpenStudio 2.7.0
            model = translator.loadModel(filepath)
    errors = translator.errors()
    warnings = translator.warnings()
    if ''.join(errors):
        raise Exception('\n'.join(errors))
    for warn in warnings:
        print warn.logMessage()
    print 'The model is imported from {}'.format(os.path.normpath(_filepath))
    success = True
    model = model.get()

    # check materials and constructions and add them to honeybee
    constructions = {str(c.handle()): c for c in model.getConstructions()}
    materials = {str(m.handle()): m for m in model.getMaterials()}
    constructionCollection = {}
    materialCollection = {}
    
    for c in constructions.itervalues():
        if str(c.name()) == 'Air Wall' or str(c.name()) in defaultConstructions:
            continue
        if vers < 27:
            constructionCollection[str(c.name()).upper()] = getHBConstruction(c, materials)
        else:
            constructionCollection[str(c.nameString()).upper()] = getHBConstruction(c, materials)
        for m in c.layers():
            if vers < 27:
                assert str(m.handle()) in materials, \
                    '"{}" material from "{}" construction is not in gbXML materials.' \
                    .format(m.name(), c.name())
                materialCollection[str(m.name()).upper()] = getHBMaterial(m)
            else:
                assert str(m.handle()) in materials, \
                    '"{}" material from "{}" construction is not in gbXML materials.' \
                    .format(m.nameString(), c.nameString())
                materialCollection[str(m.nameString()).upper()] = getHBMaterial(m)
    
    # list of final HBzones
    zones = []
    # dictionary to store boundary consition and adjacency information.
    adjDict = {}
    # number of surfaces with missing construcitons
    missingCcount = 0
    adjResetNeeded = False
    
    if not _zoneNames:
        spaces = model.getSpaces()
    else:
        spaces = tuple(s for s in model.getSpaces() if str(s.name()) in _zoneNames)
    
    
    for space in spaces:
        # create thermal zone
        zone = space.thermalZone()
        if not zone.is_initialized():
            continue
        z = zone.get()
        hbz = EPZone(None, 0, str(space.name()), program = [None, None], isConditioned = True)
        for s in space.surfaces:
            # create EP surface
            minZ = min(p.z() for p in s.vertices())
            maxZ = max(p.z() for p in s.vertices())
            srf = EPZoneSurface(getGeometry(s), 1, str(s.name()), getHBSrfType(s))
            construction, missingCcount = getOSSurfaceConstructionName(s, constructionCollection, missingCcount)
            
            if construction:
                srf.construction = construction
                srf.EPConstruction = construction
            
            # store adjacency information
            HsrfName = srf.name
            if str(s.outsideBoundaryCondition()) == 'Ground':
                adjDict[HsrfName] = ['GROUND', None]
                adjResetNeeded = True
            elif str(s.outsideBoundaryCondition()) == 'Adiabatic':
                adjDict[HsrfName] = ['ADIABATIC', None]
                adjResetNeeded = True
            elif str(s.outsideBoundaryCondition()) == 'Surface':
                adjDict[HsrfName] = ['SURFACE', str(s.adjacentSurface().get().name())]
                adjResetNeeded = True
            else:
                adjDict[HsrfName] = ['OUTDOORS', None]
            
            hbz.addSrf(srf)
            for ss in s.subSurfaces():
                #create the surface
                fenSrf = EPFenSurface(getGeometry(ss, minZ, maxZ), 1, str(ss.name()), srf, 5)
                construction, missingCcount = getOSSurfaceConstructionName(ss, constructionCollection, missingCcount)
                if construction:
                   fenSrf.construction = construction
                srf.addChildSrf(fenSrf)
        
        zones.append(hbz)
    
    # create the zones
    for zone in zones:
        zone.createZoneFromSurfaces()
    
    # try to edit the zone adjacencies to reflect what is in the gbXML.
    if adjResetNeeded == True:
        for zone in zones:
            for srf in zone.surfaces:
                try:
                    if adjDict[srf.name][0] == 'SURFACE':
                        adjSrfName = adjDict[srf.name][1]
                        aSrfFound = False
                        if adjSrfName != None:
                            # try to find the adjacent surface among the zones.
                            for azone in zones:
                                for asrf in azone.surfaces:
                                    if asrf.name == adjSrfName:
                                        aSrfFound = True
                                        updateAdj(srf, asrf)
                    elif adjDict[srf.name][0] != 'OUTDOORS':
                        srf.BC = adjDict[srf.name][0]
                        srf.setSunExposure('NoSun')
                        srf.setSunExposure('NoSun')
                except:
                    print 'Cound not set the boundary conditions correctly for surface {}'.format(srf.name)
    
    # give warnings about missing constructions.
    if missingCcount != 0:
        print '{} surfaces have missing constructions. Default construction will be used.'.format(str(missingCcount))
    
    shadings = (EPSHDSurface(getGeometry(shd), 1, str(shd.name()))
                for shd in model.getShadingSurfaces())
    
    # add construction to honeybee library
    sc.sticky ["honeybee_constructionLib"].update(constructionCollection)
    sc.sticky["honeybee_materialLib"].update(materialCollection)
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZones = hb_hive.addToHoneybeeHive(zones, ghenv.Component)
    
    
    
    try:
        shadings = hb_hive.addToHoneybeeHive(shadings, ghenv.Component, False)
    except TypeError:
        # old version of Honeybee
        shadings = hb_hive.addToHoneybeeHive(shadings, ghenv.Component)