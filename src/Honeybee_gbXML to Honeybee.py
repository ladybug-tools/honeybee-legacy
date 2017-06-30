#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools>, Chris Mackey <Chris@MackeyArchitecture.com>, and Chien Si Harriman <charriman@terabuild.com>
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

This component uses OpenStudio libraries to import the file and at this point
the component imports geometry and constrcuctions(if available). Loads, schedules,
and eventually systems can be added to the component eventually.

You also need to solve adjacencies after importing the zones.
-

Provided by Honeybee 0.0.61
    
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
ghenv.Component.Message = 'VER 0.0.61\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nSEP_09_2016
#compatibleLBVersion = VER 0.0.59\nJUL_24_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import scriptcontext as sc
import Rhino as rc


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
    
    t = ossurface.surfaceType().upper()
    if t in srfTypeDict:
        return srfTypeDict[t]

def getOSSurfaceConstructionName(s, constructionCollection):
    construction = s.construction()
    if construction.is_initialized and not construction.isNull():
        construction = construction.get()
    if not hasattr(construction, 'name'):
        print 'Construction for {} is missing. Default construction will be used.'.format(s.name())
        return None
    else:
        if not str(construction.name()) in constructionCollection:
            print 'Failed to find {} in constructions.'.format(construction.name())
            return None
        else:
            return str(construction.name())

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
    model = translator.loadModel(ops.Path(os.path.normpath(_filepath)))
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
        if str(c.name()) == 'Air Wall':
            continue
        constructionCollection[str(c.name())] = getHBConstruction(c, materials)
        for m in c.layers():
            assert str(m.handle()) in materials, \
                '"{}" material from "{}" construction is not in gbXML materials.' \
                .format(m.name(), c.name())
            materialCollection[str(m.name())] = getHBMaterial(m)
    
    
    zones = []
    
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
            construction = getOSSurfaceConstructionName(s, constructionCollection)
            if construction:
                srf.construction = construction
            hbz.addSrf(srf)
            for ss in s.subSurfaces():
                #create the surface
                fenSrf = EPFenSurface(getGeometry(ss, minZ, maxZ), 1, str(ss.name()), srf, 5)
                construction = getOSSurfaceConstructionName(ss, constructionCollection)
                if construction:
                   fenSrf.construction = construction
                srf.addChildSrf(fenSrf)
        
        zones.append(hbz)
    
    for zone in zones:
        zone.createZoneFromSurfaces()
    
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