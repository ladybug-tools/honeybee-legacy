#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to import the content of a LBNL WINDOW text file report as a series of polygons and boundary conditions that can be plugged into the "Write THERM File' component.
-
Provided by Honeybee 0.0.57

    Args:
        _windowGlzSysReport: A filepath to a detailed galzing system text file report exportedby WINDOW.
        _location_: An optional point to set the location of the glazing system in the Rhino scene.  The default is set to the Rhino origin.
        _orientation_: A number from 0 to 180 to set the orientation of the glazing system in the vertical XZ plane or simply the word 'horizontal' to represent a surface laying flat in the XY plane.  The default is set to 90 to have the gazing system be perfectly vertical.
        _sightLineToGlzBottom_: A number in Rhino model units that represents the distance from the bottom of the glass pane to the end of the frame (where the 'edge of glass' starts).  The default is set to 12.7 mm.
        _spacerHeight_: A number in Rhino model units that represents the distance from the bottom of the glass pane to the end of the spacer. The default is set to 12.7 mm.
        _edgeOfGlassDim_: A number in Rhino model units that represents the distance from the start of the frame to the start of the 'center of glass' zone.  This 'edge of glass' zone typically has a U-Value that is higher than the rest of the glass. The default is set to 63.5 mm.
        _glzSystemHeight_: A number in Rhino model units that represents the height to make the glazing system in the Rhino scene.  The default is set to 150 mm.
        spacerMaterial_: An optional material that will be used to create a spacer for the glazing system.  If no material is input here, no psacer will be created.
    Returns:
        readMe!:...
        thermPolygons: The therm polygons for the glazing system.
        indoorBCs: The thermBCs that represent the interior side of the glazing system, including separate boundary conditions for the edge of frame and center of glass.  Note that a boundary condition for with the 'Frame' UFactorTag must be made separately.
        outdoorBC: A single thermBC that represents the exterior side of the glazing system.  This includes the exterior conditions taken from the report.
        indoorProperties: A list of properties for the interior boundary condition in the following order: Name, temperature, film coefficient.  These can be used to create a boundary condition for the 'Frame.'
        outdoorProperties: A list of properties for the exterior boundary condition in the following order: Name, temperature, film coefficient.  These can be used to create a boundary condition that includes the frame of the window.
"""


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import math
import uuid

ghenv.Component.Name = 'Honeybee_Import WINDOW Glz System'
ghenv.Component.NickName = 'importWINDOW'
ghenv.Component.Message = 'VER 0.0.57\nJAN_21_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | Energy | THERM"
#compatibleHBVersion = VER 0.0.56\nJAN_12_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error


def getSrfCenPtandNormal(surface):
    brepFace = surface.Faces[0]
    u_domain = brepFace.Domain(0)
    v_domain = brepFace.Domain(1)
    centerU = (u_domain.Min + u_domain.Max)/2
    centerV = (v_domain.Min + v_domain.Max)/2
    
    centerPt = brepFace.PointAt(centerU, centerV)
    normalVector = brepFace.NormalAt(centerU, centerV)
    
    return centerPt, normalVector


def checkTheInputs():
    #Import the classes.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    thermDefault = sc.sticky["honeybee_ThermDefault"]()
    
    #Check if the result file exists.
    if _windowGlzSysReport.lower().endswith('.txt'): windowGlzSysReport = _windowGlzSysReport
    else: windowGlzSysReport = _windowGlzSysReport + '.txt'
    if not os.path.isfile(windowGlzSysReport):
        warning = "Cannot find the _windowGlzSysReport text file. Check the location of the file on your machine."
        print warning
        ghenv.Component.AddRuntimeMessage(e, warning)
        return -1
    
    #Check to be sure that the orientation makes sense and derive a plane for the geometry in the Rhino scene.
    glzPlane = None
    if _location_ == None: location = rc.Geometry.Point3d.Origin
    else: location = _location_
    if _orientation_ != None:
        try:
            orientation = float(_orientation_)
            if orientation >= 0 and orientation <= 180:
                yAxis = rc.Geometry.Vector3d.YAxis
                xAxis = rc.Geometry.Vector3d.XAxis
                oreintTrans = rc.Geometry.Transform.Rotation(math.radians(orientation-90), rc.Geometry.Vector3d.YAxis, rc.Geometry.Point3d.Origin)
                yAxis.Transform(oreintTrans)
                xAxis.Transform(oreintTrans)
                glzPlane = rc.Geometry.Plane(location, xAxis, yAxis)
            else:
                warning = "_orientation_ must be between 0 and 180."
                print warning
                ghenv.Component.AddRuntimeMessage(e, warning)
                return -1
        except:
            if _orientation_.lower() == 'horizontal':
              glzPlane = rc.Geometry.Plane(location, rc.Geometry.Vector3d.XAxis, rc.Geometry.Vector3d(0,0,-1))
            else:
              warning = "Input for _orientation_ not recognized."
              print warning
              ghenv.Component.AddRuntimeMessage(e, warning)
              return -1
    elif _location_ != None:
        glzPlane = rc.Geometry.Plane(location, rc.Geometry.Vector3d.XAxis, rc.Geometry.Vector3d.YAxis)
    
    
    #Set any defaults for the dimensions of the glazing system.
    conversionFactor = lb_preparation.checkUnits()*1000
    sightLineToGlzBottom = 12.7
    if _sightLineToGlzBottom_ != None: sightLineToGlzBottom = _sightLineToGlzBottom_*conversionFactor
    spacerHeight = 12.7
    if _spacerHeight_ != None: spacerHeight = _spacerHeight_*conversionFactor
    edgeOfGlassDim = 63.5
    if _edgeOfGlassDim_ != None: edgeOfGlassDim = _edgeOfGlassDim_*conversionFactor
    glzSystemHeight = 150
    if _glzSystemHeight_ != None: glzSystemHeight = _glzSystemHeight_*conversionFactor
    
    #Check to be sure that the sum of _sightLineToGlzBottom_ and _edgeOfGlassDim_ does not exceed the _glzSystemHeight_.
    if sightLineToGlzBottom + edgeOfGlassDim > glzSystemHeight:
        warning = "The sum of _sightLineToGlzBottom_ and _edgeOfGlassDim_ exceeds the _glzSystemHeight_."
        print warning
        ghenv.Component.AddRuntimeMessage(e, warning)
        return -1
    
    #Check to be sure that the _spacerHeight_ does not exceed the _glzSystemHeight_.
    if spacerHeight > glzSystemHeight:
        warning = "The _spacerHeight_ exceeds the _glzSystemHeight_."
        print warning
        ghenv.Component.AddRuntimeMessage(e, warning)
        return -1
    
    #If there is a spacer material, check to be sure that it can be found in the library.
    material = None
    if spacerMaterial_ != None:
        # if it is just the name of the material make sure it is already defined
        if spacerMaterial_.startswith("<Material"):
            #Its a full string of a custom THERM material.
            material = thermDefault.addThermMatToLib(spacerMaterial_)
        elif len(spacerMaterial_.split("\n")) == 1:
            #Its the name of a material.
            material = spacerMaterial_.upper()
            if material in sc.sticky ["honeybee_materialLib"].keys(): pass
            elif material in sc.sticky ["honeybee_windowMaterialLib"].keys():pass
            elif material in sc.sticky["honeybee_thermMaterialLib"].keys():pass
            else:
                warningMsg = "Can't find " + material + " in EP Material Library.\n" + \
                            "Create the material and try again."
                print warningMsg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                return -1
        # if the material is not in the library add it to the library
        else:
            # it is a full string of an EP material.
            added, material = hb_EPMaterialAUX.addEPConstructionToLib(spacerMaterial_, overwrite = True)
            material = material.upper()
            if not added:
                msg = material + " is not added to the project library!"
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                print msg
                return -1
    
    
    return glzPlane, sightLineToGlzBottom, spacerHeight, edgeOfGlassDim, glzSystemHeight, material, conversionFactor, thermDefault

def main(windowGlzSysReport, glzPlane, sightLineToGlz, spacerHeight, edgeOfGlassDim, glzSystemHeight, spacerMaterial, conversionFactor, thermDefault):
    #Call the relevant classes
    hb_thermPolygon = sc.sticky["honeybee_ThermPolygon"]
    hb_thermBC = sc.sticky["honeybee_ThermBC"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    #Make a series of lists to be filled
    thermPolygons = []
    indoorBCs = []
    outdoorBC = []
    glzSysThicknesses = []
    glzSysNames = []
    glzSysKEffs = []
    glzSysEmiss = []
    indoorProps = ['WINDOW Interior']
    outdoorProps = []
    
    
    #Define some parameters to be changes while the file is open.
    materialTrigger1 = False
    materialTrigger2 = False
    envConditTrigger1 = False
    envConditTrigger2 = False
    gasTrigger = False
    firstGlzPane = True
    
    #Open the file and begin extracting the relevant bits of information.
    textFile = open(windowGlzSysReport, 'r')
    for lineCount, line in enumerate(textFile):
        if 'Layer Data for Glazing System' in line: materialTrigger1 = True
        elif 'Environmental Conditions' in line:
            materialTrigger1 = False
            envConditTrigger1 = True
            outdoorProps.append(line.split('Environmental Conditions:')[-1].strip())
        elif 'Optical Properties for Glazing System' in line: envConditTrigger1 = False
        elif 'Outside' in line and materialTrigger1 == True: materialTrigger2 = True
        elif 'Inside' in line and materialTrigger1 == True: materialTrigger2 = False
        elif materialTrigger1 == True and materialTrigger2 == True:
            if gasTrigger == False:
                tableColumns = line.split('#')
                layerName = tableColumns[0][7:].strip()
                glzSysNames.append(layerName)
                glzProps = tableColumns[-1].strip().split(' ')
                glzSysThicknesses.append(float(glzProps[0]))
                glzSysKEffs.append(float(glzProps[-1]))
                if firstGlzPane == True: glzSysEmiss.append(float(glzProps[-3]))
                else: glzSysEmiss.append(float(glzProps[-2]))
                gasTrigger = True
            else:
                layerName = line[7:22].strip().replace(' ', '_')
                glzSysNames.append(layerName)
                glzSysThicknesses.append(float(line[22:30].strip()))
                glzSysKEffs.append(float(line[73:].strip()))
                glzSysEmiss.append(0.9)
                gasTrigger = False
            firstGlzPane = False
        elif 'Uvalue' in line and envConditTrigger1 == True:
            outdoorProps.append(float(line[7:16].strip()))
            indoorProps.append(float(line[16:23].strip()))
            #Compute an outdoor film coefficient from the wind speed.
            windspeed = float(line[22:30].strip())
            if windspeed < 3.4: outdoorProps.append(22.7)
            else: outdoorProps.append((1.544*windspeed*windspeed)-(12.17*windspeed)+46.23)
            #Compute an indoor film coefficient from the orientation.
            #Turn the heat flow direction into a dimensionless value for a linear interoplation.
            if _orientation_ == None or _orientation_.lower() == 'horizontal': dimHeatFlow = 0.5
            else: dimHeatFlow = float(_orientation_)/180
            #Compute a film coefficient from the emissivity, heat flow direction, and a paramterization of AHSHRAE fundemantals.
            heatFlowFactor = (-12.443 * (math.pow(dimHeatFlow,3))) + (24.28 * (math.pow(dimHeatFlow,2))) - (16.898 * dimHeatFlow) + 8.1275
            filmCoeff = (heatFlowFactor * dimHeatFlow) + (5.81176 * glzSysEmiss[-1]) + 0.9629
            indoorProps.append(filmCoeff)
    textFile.close()
    
    
    
    #Create the window material geometry in the Rhino scene.
    initWindowGeos = []
    extrusionVec = rc.Geometry.Vector3d(0,0,glzSystemHeight)
    gasExtrusionVec = rc.Geometry.Vector3d(0,0,glzSystemHeight-spacerHeight)
    XCoord = 0
    glassPane = True
    for thickness in glzSysThicknesses:
        if glassPane == False:
            glassPane = True
            materialLine = rc.Geometry.LineCurve(rc.Geometry.Point3d(XCoord,0,spacerHeight), rc.Geometry.Point3d(XCoord+thickness,0,spacerHeight))
            materialSrf = rc.Geometry.Surface.CreateExtrusion(materialLine, gasExtrusionVec)
        else:
            glassPane = False
            materialLine = rc.Geometry.LineCurve(rc.Geometry.Point3d(XCoord,0,0), rc.Geometry.Point3d(XCoord+thickness,0,0))
            materialSrf = rc.Geometry.Surface.CreateExtrusion(materialLine, extrusionVec)
        initWindowGeos.append(rc.Geometry.Brep.CreateFromSurface(materialSrf))
        XCoord += thickness
    
    #If a spacer material is requested, add in the extra polygons for it.
    initSpacerGeos = []
    newXCoord = 0
    glassPane = True
    if spacerMaterial != None:
        for thickness in glzSysThicknesses:
            if glassPane == False:
                glassPane = True
                materialLine = rc.Geometry.LineCurve(rc.Geometry.Point3d(newXCoord,0,0), rc.Geometry.Point3d(newXCoord+thickness,0,0))
                materialSrf = rc.Geometry.Surface.CreateExtrusion(materialLine, rc.Geometry.Vector3d(0,0,spacerHeight))
                initSpacerGeos.append(rc.Geometry.Brep.CreateFromSurface(materialSrf))
            else: glassPane = False
            newXCoord += thickness
    
    #Generate the boundary condition geometries.
    outdoorBCGeo = rc.Geometry.PolylineCurve([rc.Geometry.Point3d.Origin, rc.Geometry.Point3d(0,0,glzSystemHeight)])
    indoorFrameBCGeo = rc.Geometry.PolylineCurve([rc.Geometry.Point3d(XCoord,0,sightLineToGlz), rc.Geometry.Point3d(XCoord,0,sightLineToGlz+edgeOfGlassDim)])
    indoorRemainBCGeo = rc.Geometry.PolylineCurve([rc.Geometry.Point3d(XCoord,0,sightLineToGlz+edgeOfGlassDim), rc.Geometry.Point3d(XCoord,0,glzSystemHeight)])
    
    #Transform the geometries into the corrext scale and plane.
    plane = rc.Geometry.Plane.WorldZX
    plane.Flip()
    conversionFactor = conversionFactor/1000
    conversionFactor = 1/(conversionFactor*1000)
    unitsScale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, conversionFactor, conversionFactor, conversionFactor)
    for geo in initWindowGeos: geo.Transform(unitsScale)
    for geo in initSpacerGeos: geo.Transform(unitsScale)
    outdoorBCGeo.Transform(unitsScale)
    indoorFrameBCGeo.Transform(unitsScale)
    indoorRemainBCGeo.Transform(unitsScale)
    if glzPlane != None:
        planeTransform = rc.Geometry.Transform.ChangeBasis(glzPlane, rc.Geometry.Plane.WorldXY)
        for geo in initWindowGeos: geo.Transform(planeTransform)
        for geo in initSpacerGeos: geo.Transform(planeTransform)
        outdoorBCGeo.Transform(planeTransform)
        indoorFrameBCGeo.Transform(planeTransform)
        indoorRemainBCGeo.Transform(planeTransform)
        plane.Transform(planeTransform)
    
    #Create the thermPolygons for the window materials.
    allMaterials = []
    isGlass = True
    for count, geo in enumerate(initWindowGeos):
        #Pick an RGB color for the material that is consistent with whether it is a piece of glass or a gas.
        if isGlass == True:
            RGBColor = '#00FFE5'
            isGlass = False
        else:
            RGBColor = '#ADADAD'
            isGlass = True
        #Create a material for the glass or gas.
        if glzSysNames[count].upper() not in allMaterials and glzSysNames[count].upper() not in sc.sticky["honeybee_thermMaterialLib"].keys():
            materialStr = '<Material Name=' + glzSysNames[count].upper() + ' Type=0' + ' Conductivity=' + str(glzSysKEffs[count]) + ' Absorptivity=0.5' + ' Emissivity=' + str(glzSysEmiss[count]) + ' RGBColor=' + str(RGBColor) + '/>'
            material = thermDefault.addThermMatToLib(materialStr)
            allMaterials.append(material)
        else: material = glzSysNames[count].upper()
        
        #Create the THERM polygon.
        guid = str(uuid.uuid4())
        polyName = "".join(guid.split("-")[:-1])
        HBThermPolygon = hb_thermPolygon(geo.Faces[0].DuplicateFace(False), material, polyName, plane, None)
        if HBThermPolygon.warning != None:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, HBThermPolygon.warning)
        thermPolygons.append(HBThermPolygon)
    
    
    #Create the thermPolygons for the spacers.
    if spacerMaterial != None:
        for geo in initSpacerGeos:
            #Create the THERM polygon.
            guid = str(uuid.uuid4())
            polyName = "".join(guid.split("-")[:-1])
            HBThermPolygon = hb_thermPolygon(geo.Faces[0].DuplicateFace(False), spacerMaterial, polyName, plane, None)
            if HBThermPolygon.warning != None:
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, HBThermPolygon.warning)
            thermPolygons.append(HBThermPolygon)
    
    #Add All THERM Polygons to the hive.
    thermPolygonsFinal  = hb_hive.addToHoneybeeHive(thermPolygons, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    
    #Create the THERM BCs.
    outdoorHBThermBC = hb_thermBC(outdoorBCGeo, outdoorProps[0].title(), outdoorProps[1], outdoorProps[2], plane, None, None, None, None, None)
    indoorFrameThermBC = hb_thermBC(indoorFrameBCGeo, indoorProps[0].title(), indoorProps[1], indoorProps[2], plane, None, None, None, 'Edge', None)
    indoorRemainThermBC = hb_thermBC(indoorRemainBCGeo, indoorProps[0].title(), indoorProps[1], indoorProps[2], plane, None, None, None, None, None)
    
    # ADD THERM BCs TO THE HIVE
    thermOutBoundary  = hb_hive.addToHoneybeeHive([outdoorHBThermBC], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    thermInBoundary1  = hb_hive.addToHoneybeeHive([indoorFrameThermBC], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    thermInBoundary2  = hb_hive.addToHoneybeeHive([indoorRemainThermBC], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    
    return thermPolygonsFinal, thermInBoundary1 + thermInBoundary2, thermOutBoundary, indoorProps, outdoorProps


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#If the intital check is good, run the component.
if initCheck and _windowGlzSysReport:
    checkData = checkTheInputs()
    if checkData != -1:
        glzPlane, sightLineToGlz, spacerHeight, edgeOfGlassDim, glzSystemHeight, spacerMaterial, conversionFactor, thermDefault = checkData
        result = main(_windowGlzSysReport, glzPlane, sightLineToGlz, spacerHeight, edgeOfGlassDim, glzSystemHeight, spacerMaterial, conversionFactor, thermDefault)
        if result != -1:
            thermPolygons, indoorBCs, outdoorBC, indoorProperties, outdoorProperties = result
