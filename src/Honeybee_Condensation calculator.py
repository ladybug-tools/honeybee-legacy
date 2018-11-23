# Condensation calculator
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2017, Abraham Yezioro <ayez@technion.ac.il> 
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
Use this component to calculate the Dew Point, Relative Humidity and Condensation on each layer of a wall. It accounts the air films (internal and external).
Sources:
http://andrew.rsmas.miami.edu/bmcnoldy/Humidity.html
http://www.ajdesigner.com/phphumidity/dewpoint_equation_dewpoint_temperature.php#ajscroll
http://forums.finehomebuilding.com/breaktime/energy-heating-insulation/dewpoint-spreadsheet
-
Provided by Honeybee 0.0.64
    
    Args:
        _cnstrName: EnergyPlus construction name
        surfaceType_: An integer value from 0 to 3 that represents one of the following surface types:
                       0 - Exterior Wall/Window
                       1 - Exterior Roof
                       2 - Exposed Floor
        _internalTemp: Indoors temperature of room
        _outTemp: Outdoors temperature of room
        _internalRelativeHumidity: Indoors relative humidity
        _basePoint_: An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0).
        _scale_: The scale of the surface type section. The default is set to 1.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        layerName_: If bakeIt_ is set to "True", input Text here corresponding to the Rhino layer onto which the resulting mesh and legend should be baked.

    Returns:
        readMe!: ...
        materials: List of materials (from outside to inside). Includes film Air layers. Ordered from Inside to Outside layers. They include Air Films.
        comments: Comments for each layer of materials if any. Ordered from Inside to Outside layers
        rWall: 
        tempWall: temperature for each layer in wall (outter edge of layer). Ordered from Inside to Outside layers
        rhWall: relative humdity for each layer in wall (outter edge of layer). Ordered from Inside to Outside layers
        dewPointWall: Dew Point for each layer in wall (outter edge of layer). Ordered from Inside to Outside layers
        condensationWall: State the status of condensation on wall (Yes or No). Ordered from Inside to Outside layers
        ::::::::::::::::::::::::::::::::::::::
        layersWallGeo: 
        resultLines: 
        resultLinesColors: 
        scaleRH_TempGeo: 
        allLabels: 
        ::::::::::::::::::::::::::::::::::::::
        finalJoinedMesh: 
        legend: 
        allLabels: 
        wallLegendCoord: 
        allDataCurves: 
        textSize: 
        decimalPlaces: 
"""
#
ghenv.Component.Name = "Honeybee_Condensation calculator"
ghenv.Component.NickName = 'HB_CondensationCalculator'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Rhino as rc
import scriptcontext as sc
import ghpythonlib.components as ghc
import math
import System
from System import Object

meshingP = rc.Geometry.MeshingParameters.Coarse
meshingP.SimplePlanes = True
lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
lb_preparation = sc.sticky["ladybug_Preparation"]()


import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def checkInputs():
    checkData = False
    surfaceType = 0
    if surfaceType_:
        try:
            surfaceType = surfaceType_
        except:
            surfaceType = 0
    
    checkData1 = False
    checkData2 = False
    checkData3 = False
    checkData4 = False
    if _cnstrName:
        try: 
            checkData1 = True
        except: pass
    else:
        warning = "Connect a valid Construction."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    if _internalTemp:
        try: checkData2 = True
        except: pass
    else:
        warning = "Connect a value for indoor temperature."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    if _outTemp != None:
        try: checkData3 = True
        except: pass
    else:
        warning = "Connect a value for outdoor temperature."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    if _internalRelativeHumidity != None:
        try: checkData4 = True
        except: pass
    else:
        warning = "Connect a value for indoor relative humidity."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    if checkData1 and checkData2 and checkData3 and checkData4:
        checkData = True
    return checkData, surfaceType

def getConstructionName(cnstrName):
    # Make sure Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

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
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    return hb_EPMaterialAUX.decomposeEPCnstr(cnstrName.upper())
    
def getMaterial(matName):
    if not sc.sticky["honeybee_release"]:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

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
    
    # get the constuction
    try:
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if sc.sticky.has_key("honeybee_materialLib"):
        result = hb_EPMaterialAUX.decomposeMaterial(matName.upper(), ghenv.Component)
        if result == -1:
            warning = "Failed to find " + matName + " in the Honeybee material library."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return result

#def calculateData():
def main(surfaceType, layerColors, sectHeight):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        # Create an instance of the lb_preparation class 
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    nameMaterial_rev    = None
    thicknessMat_rev    = None
    conductivityMat_rev = None
    rMaterial_rev       = None
    rWall_rev           = None
    newRValue           = None
    rWallCumulPerc      = None
    tempOuterEdge       = None
    dpTemp              = None
    rhOutter            = None
    condensation        = None
    
    try:  
        if surfaceType == None or surfaceType == 0 or surfaceType == 1 or surfaceType == 2:
            #Get the value of R-Value added to the air film.
            addedRout = 0.04   # Exterior wall (0.04 + 0.13)
            if surfaceType == None:    
                addedRin  = 0.13   # Exterior wall (0.04 + 0.13)
                print "Default surface type set to an exterior wall."
            elif surfaceType == 0:     addedRin  = 0.13   # Exterior wall (0.04 + 0.13)
            elif surfaceType == 1:     addedRin  = 0.10   # Roof          (0.04 + 0.10)
            elif surfaceType == 2:     addedRin  = 0.17   # Roof          (0.04 + 0.17)

        else:
            msg = "surfaceType_ must be an integer between 0 and 2."
            ghenv.Component.AddRuntimeMessage(w, msg)
            return -1
    except:
        msg = "Failed to calculate UValue and R-Value with air films."
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
        
    if _cnstrName != None:
        data = getConstructionName(_cnstrName)                  #Call getConstructionName and get the data cor this CONSTRUCTION
        
        if data!=-1:
            materials, comments, UValue_SI, UValue_IP = data    #Separate the data
            
            if UValue_SI and UValue_IP:
                R_WallValue_SI = 1/UValue_SI                    #This is the r value (no air films) for the wall
                R_WallValue_IP = 1/UValue_IP
    
            thicknessMat    = []
            conductivityMat = []
            nameMaterial    = []
            rMaterial       = []
            rWall           = []
            thicknessMat.append(0.01)
            conductivityMat.append(1 / addedRout)
            nameMaterial.append('Air Film  Out')
            rWall.append(addedRout)
            for materialName in materials:
                matData = getMaterial(materialName)
                nameMaterial.append(materialName)
        
                if matData != -1:
                    values, comments, UValue_SI, UValue_IP = matData
                    thicknessMat.append(float(values[2]))
                    conductivityMat.append(float(values[3]))
                    
                    names = materialName
                    if UValue_SI and UValue_IP:
                        RValue_SI = 1 / UValue_SI               #This is the r value (no air films) for the material layer
                        RValue_IP = 1 / UValue_IP
                        rMaterial.append(RValue_SI)
                        rWall.append(RValue_SI)
    
            thicknessMat.append(0.01)
            conductivityMat.append(1 / addedRin)
            nameMaterial.append('Air Film In')
            rWall.append(addedRin)
            newRValue = addedRout + R_WallValue_SI + addedRin
            
            ############################################    There is a need to reverse the lists becouse the calculations go from the hotter side to the cooler one (inside to outside)
            rWall_rev           = rWall[::-1]
            thicknessMat_rev    = thicknessMat[::-1]
            conductivityMat_rev = conductivityMat[::-1]
            nameMaterial_rev    = nameMaterial[::-1]
            rMaterial_rev       = rMaterial[::-1]
            ############################################
            
            deltaTemp      = _internalTemp - _outTemp
            rWallPerc      = []                                 #Percentage of influence of each wall layer according to it's r value in ralation to the r of the whole wall
            rWallCumulPerc = []                                 #Cumulative Percentage of influence of each wall layer, starting from the outside layer
            tempOuterEdge  = []                                 #Temperature of each wall layer on it's outter edge
            
            #for m in rWall:
            for m in rWall_rev:
                rWallPerc.append(m / newRValue)
            rWallCumulPerc.append(rWallPerc[0])
            tempOuterEdge.append(_internalTemp - (rWallCumulPerc[0] * deltaTemp))
            
            for y in range(1, len(rWall)):
                rWallCumulPerc.append(rWallCumulPerc[y - 1] + rWallPerc[y])
                tempOuterEdge.append(_internalTemp - (rWallCumulPerc[y] * deltaTemp))
            
            dpTemp   =     []    # Dew Point Temperature
            rhOutter =     []    # Relative Humidity Outter edge of layer
            condensation = []    # Condensation Outter edge of layer
            
            #firstDewPoint = (math.pow(_internalRelativeHumidity / 100, 1/8) * (112 + 0.9 * _internalTemp) + 0.1* _internalTemp - 112) # Other option for equation
            firstDewPoint = (243.04 * (math.log(_internalRelativeHumidity / 100) + ((17.625 * _internalTemp) / (243.04 + _internalTemp))) / \
                             (17.625 - math.log(_internalRelativeHumidity / 100) - ((17.625 * _internalTemp) / (243.04 + _internalTemp))))
            
            #for y in range(len(rWall)):
            for y in range(len(rWall_rev)):
                if y == 0:
                    rh = 100*(math.exp((17.625 * firstDewPoint) / (243.04 + firstDewPoint)) / math.exp((17.625 * tempOuterEdge[0]) / (243.04 + tempOuterEdge[0])))
                else:
                    rh = 100*(math.exp((17.625 * dpTemp[y - 1]) / (243.04 + dpTemp[y - 1])) / math.exp((17.625 * tempOuterEdge[y]) / (243.04 + tempOuterEdge[y])))
                if rh > 100: 
                    rh = 100
                    condensation.append('YES')
                else: 
                    condensation.append('NO')
                    
                rhOutter.append(rh)
                dpTemp.append(243.04 * (math.log(rhOutter[y] / 100) + ((17.625 * tempOuterEdge[y]) / (243.04 + tempOuterEdge[y]))) / \
                              (17.625 - math.log(rhOutter[y] / 100) - ((17.625 * tempOuterEdge[y]) / (243.04 + tempOuterEdge[y]))))
                              
    layersWallGeo, onlyMesh, resultLines, resultLinesColors, titleCoord, wallSectCoord, wallLegendCoord = \
                    drawSection(surfaceType, nameMaterial_rev, thicknessMat_rev, conductivityMat_rev, rWall_rev, newRValue, rWallCumulPerc, tempOuterEdge, dpTemp, \
                    rhOutter, condensation, layerColors, sectHeight)

    return layersWallGeo, onlyMesh, resultLines, resultLinesColors, titleCoord, wallSectCoord, wallLegendCoord, \
           nameMaterial_rev, thicknessMat_rev, conductivityMat_rev, rWall_rev, newRValue, rWallCumulPerc, tempOuterEdge, dpTemp, rhOutter, condensation, \
           lb_visualization, lb_preparation

def calcSectCoords(surfaceType, materials, thicknessMat, conductivityMat, rWall, newRValue, rWallCumulPerc, tempWall, dewPointWall, rhWall, condensationWall, layerColors, invWall, wFactor, sectHeight):
    vertColor       = []
    layersWallMesh  = []
    initX           = 0.0
    initY           = -(sectHeight / 4)
    vertLinks       = [(0,1,2,3)] # list of vertices order for linking into one mesh
    colMesh         = []
    onlyMesh        = []
    wallSectCoord   = []
    wallLegendCoord = []
    delta           = sectHeight / len(materials)
    titleCoord      = rc.Geometry.Point3d( invWall * initX, sectHeight + sectHeight / 15., 0.)

    for layerInd in range(len(materials)):
        vertColor.append([])
        vertColor[layerInd].append([])
        
        if conductivityMat[layerInd] < 0.09:
            tmpColor = layerColors[0] #Insulation
        elif conductivityMat[layerInd] > 5.0:
            tmpColor = layerColors[3] #AirFilm
        else:
            tmpColor = layerColors[2] #Opaque
        
        vCoord = []
        vCoord.append(rc.Geometry.Point3d( invWall * initX,                                      0.,         0.))
        vCoord.append(rc.Geometry.Point3d( invWall * (initX + thicknessMat[layerInd] * wFactor), 0.,         0.))
        vCoord.append(rc.Geometry.Point3d( invWall * (initX + thicknessMat[layerInd] * wFactor), sectHeight, 0.))
        vCoord.append(rc.Geometry.Point3d( invWall * initX,                                      sectHeight, 0.))
        vCoord.append(rc.Geometry.Point3d( invWall * initX,                                      0.,         0.))
        
        p1 = invWall * initX
        p2 = invWall * (initX + thicknessMat[layerInd] * wFactor)
        p3 = (p2 - p1) / 3.
        p4 = p1 + p3
        wallSectCoord.append(rc.Geometry.Point3d( p4, -(sectHeight / 15.), 0.))
        wallLegendCoord.append(rc.Geometry.Point3d( 0., initY, 0.))
        
        initX += thicknessMat[layerInd] * wFactor   # Advance the initX for next iteration
        initY -= delta                              # Advance the initY for next iteration
        # Wall layers mesh #########################################
        dataPolyline = rc.Geometry.PolylineCurve(vCoord)
        meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)
        # Generate the color list for all the vertices on the wall layer
        repeatedColors = []
        for face in range(meshedC.Faces.Count):
            repeatedColors.append(tmpColor)
    
        # Use ladybug functions to color the mesh
        onlyMesh.append(lb_visualization.colorMesh(repeatedColors, meshedC))
        colMesh.append( lb_visualization.colorMesh(repeatedColors, meshedC))
        colMesh.append( dataPolyline)        # This is the colored mesh for each wall layer
        ############################################################

        #Wall layers contour #######################################
        dataPolyline = rc.Geometry.PolylineCurve(vCoord)
        meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)

        # Will offset the contour of the layers so they can be colored in black, also they will have some thickness.
        layerContour = outlineCurve(dataPolyline, wFactor)
        comfortMesh = rc.Geometry.Mesh()
        comfortMesh.Append(rc.Geometry.Mesh.CreateFromBrep(layerContour)[0])
        comfortMesh.VertexColors.CreateMonotoneMesh(layerColors[4])        # This is the colored line for each wall layer
        colMesh.append(comfortMesh)
        ############################################################
        
    return colMesh, onlyMesh, titleCoord, wallSectCoord, wallLegendCoord

def calcRHCoords(surfaceType, rhWall, invWall, wFactor, sectHeight, thicknessMat):
    vertColor      = []
    layersWallMesh = []
    initX          = 0.0
    vertLinks      = [(0,1,2,3)] # list of vertices order for linking into one mesh
    colMesh        = []
    sclRH          = sectHeight / 105     # Giving 105 just in case 100%RH
    vCoord = []
    vCoord.append(rc.Geometry.Point3d( (invWall * initX) - 0.10, _internalRelativeHumidity * sclRH, 0.))    # Point for initial RH given at the input
    vCoord.append(rc.Geometry.Point3d( (invWall * initX),        _internalRelativeHumidity * sclRH, 0.))    # Point for first RH on wall
    for layerInd in range(len(rhWall)):
        vCoord.append(rc.Geometry.Point3d( invWall * (initX + thicknessMat[layerInd] * wFactor), rhWall[layerInd] * sclRH, 0.))
        initX += thicknessMat[layerInd] * wFactor   # Advance the initX for next iteration

    return vCoord
    
def calcTemp_DPCoords(surfaceType, data, invWall, wFactor, sectHeight, thicknessMat):
    vertColor      = []
    layersWallMesh = []
    initX          = 0.0
    vertLinks      = [(0,1,2,3)] # list of vertices order for linking into one mesh
    colMesh        = []
    #tempDiff       = _internalTemp + abs(_outTemp) + 1
    tempDiff       = _internalTemp - _outTemp + 1
    
    sclTemp        = sectHeight / tempDiff     # Takes the difference between inside and outside temperatures
    
    outTempFix = (_internalTemp + 1) * sclTemp
    if outTempFix >= 1.: outTempFix = outTempFix - 1.0
    else: outTempFix = -(1 - outTempFix)
    
    vCoord = []
    vCoord.append(rc.Geometry.Point3d( (invWall * initX) - 0.10, _internalTemp * sclTemp - outTempFix, 0.))    # Point for initial Temp/DP given at the input
    vCoord.append(rc.Geometry.Point3d( (invWall * initX),        _internalTemp * sclTemp - outTempFix, 0.))    # Point for first Temp/DP on wall
    
    for layerInd in range(len(data)):
        vCoord.append(rc.Geometry.Point3d( invWall * (initX + thicknessMat[layerInd] * wFactor), data[layerInd] * sclTemp - outTempFix, 0.))
        initX += thicknessMat[layerInd] * wFactor   # Advance the initX for next iteration
        
    return vCoord
    
def drawLines(vCoord, wFactor, indRes):
    #Wall layers contour #######################################
    colMesh        = []
    dataPolyline = rc.Geometry.PolylineCurve(vCoord)
    #meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)
    #print meshedC
    colMesh.append(dataPolyline)        # This is the colored mesh for each wall layer
    
    """
    # Will offset the contour of the layers so they can be colored in black, also they will have some thickness.
    layerContour = outlineCurve(dataPolyline, wFactor)
    comfortMesh = rc.Geometry.Mesh()
    comfortMesh.Append(rc.Geometry.Mesh.CreateFromBrep(layerContour)[0])
    comfortMesh.VertexColors.CreateMonotoneMesh(layerColors[4])        # This is the colored line for each wall layer
    colMesh.append(comfortMesh)
    ############################################################
    """
    
    #return colMesh
    return dataPolyline

def drawSection(surfaceType, materials, thicknessMat, conductivityMat, rWall, newRValue, rWallCumulPerc, tempWall, dewPointWall, rhWall, condensationWall, layerColors, sectHeight):
    minTemp    = min(tempWall)
    maxTemp    = max(tempWall)
    minRH      = min(rhWall)
    maxRH      = max(rhWall)
    invWall    = 1          # -(1) To draw the wall while indoors is at the right of the section. Check whay happens with Roof/Floor
    wFactor    = 4          # To change the width of the section ... Check if needed???
    #sectHeight = 1.0        # Set the height of the section
    #print 'minTemp = %.2f \tmaxTemp = %.2f ' % (minTemp, maxTemp)
    #print 'minRH = %.2f \tmaxRH = %.2f '     % (minRH, maxRH)
    #print 'internalTemp = %.1f \toutTemp = %.1f \tinternalRelativeHumidity = %.1f' % (_internalTemp, _outTemp, _internalRelativeHumidity)
    layersWallGeo, onlyMesh, titleCoord, wallSectCoord, wallLegendCoord = calcSectCoords(surfaceType, materials, thicknessMat, conductivityMat, rWall, newRValue, rWallCumulPerc, tempWall, dewPointWall, rhWall, condensationWall, layerColors, invWall, wFactor, sectHeight)
    wallRH        = calcRHCoords(surfaceType,      rhWall,       invWall, wFactor, sectHeight, thicknessMat)
    wallTemp      = calcTemp_DPCoords(surfaceType, tempWall,     invWall, wFactor, sectHeight, thicknessMat)
    wallDP        = calcTemp_DPCoords(surfaceType, dewPointWall, invWall, wFactor, sectHeight, thicknessMat)
    
    resLines     = []
    resLinesCols = []
    resLines.append(drawLines(wallRH, wFactor,   1))
    resLinesCols.append(layerColors[6])
    resLines.append(drawLines(wallTemp, wFactor,   1))
    resLinesCols.append(layerColors[5])
    resLines.append(drawLines(wallDP, wFactor,   1))
    resLinesCols.append(layerColors[7])

    return layersWallGeo, onlyMesh, resLines, resLinesCols, titleCoord, wallSectCoord, wallLegendCoord #linesRH

def outlineCurve(curve, wFactor):
    offsetFactor = 0.002 * wFactor
    offsetCrv = curve.Offset(rc.Geometry.Plane.WorldXY, offsetFactor, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
    layerContour = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])

    return layerContour

def colors():
    layerColors = [System.Drawing.Color.FromArgb(200, 200, 0),   # Insulation Materials - 0
                   System.Drawing.Color.FromArgb(50, 50, 150),   # Glass Materials      - 1
                   System.Drawing.Color.FromArgb(150, 150, 150), # Opaque Materials     - 2
                   System.Drawing.Color.FromArgb(120, 120, 220), # AirFilms             - 3
                   System.Drawing.Color.FromArgb(0, 0, 0),       # Lines                - 4
                   System.Drawing.Color.FromArgb(255, 0, 0),     # Red for temperature  - 5
                   System.Drawing.Color.FromArgb(0, 0, 255),     # Blue for RH          - 6
                   System.Drawing.Color.FromArgb(255, 153, 0)]   # Orange for DewPoint  - 7
    return layerColors
    
def drawText(titleCoord, wallSectCoord, wallLegendCoord, materials, thicknessMat, surfaceType, lb_visualization, lb_preparation):
    allLabels = []
    
    textPlane = rc.Geometry.Plane(titleCoord, rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,1,0))
    textSrfs = lb_visualization.text2srf([_cnstrName], [titleCoord], 'Verdana', 0.07, False, textPlane)
    for txt in textSrfs:
        allLabels.extend(txt)
        
    for i in range(len(thicknessMat)):
        textPlane = rc.Geometry.Plane(wallSectCoord[i], rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,1,0))
        textSrfs = lb_visualization.text2srf([str(i)], [wallSectCoord[i]], 'Verdana', 0.05, False, textPlane)
        for txt in textSrfs:
            allLabels.extend(txt)

    for i in range(len(thicknessMat)):
        textPlane = rc.Geometry.Plane(wallLegendCoord[i], rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,1,0))
        textSrfs = lb_visualization.text2srf([str(i) + '. ' + materials[i]], [wallLegendCoord[i]], 'Verdana', 0.05, False, textPlane)
        for txt in textSrfs:
            allLabels.extend(txt)
    return allLabels

def rhText(text, textPts, allLabels, surfaceType, textSize, lb_visualization, lb_preparation):
    for i in range(len(text)):
        textPlane = rc.Geometry.Plane(textPts[i], rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,1,0))
        textSrfs = lb_visualization.text2srf([text[i]], [textPts[i]], 'Verdana', textSize, False, textPlane)
        for txt in textSrfs:
            allLabels.extend(txt)
    return allLabels

def scaleRH_Temp(surfaceType, sectHeight, layerColors):
    scaleRH_TempGeo      = []
    scaleRH_TempGeoColor = []
    scaleRH_Text         = []
    scaleTemp_Text       = []
    scaleRH_TextPts      = []
    scaleTemp_TextPts    = []
    #Create a line that represents the RH/Temp axis.
    pt1 = rc.Geometry.Point3d(-0.35, 0.,         0.)
    pt2 = rc.Geometry.Point3d(-0.35, sectHeight, 0.)
    axisRH = rc.Geometry.LineCurve(pt1, pt2) # Draw a line between these two points making the horizontail axis
    scaleRH_TempGeo.append(axisRH)
    scaleRH_TempGeoColor.append(layerColors[6])
    sclRH = sectHeight / 105     # Giving 105 just in case 100%RH
    
    #Piece for Temp scale calcs
    tempDiff       = _internalTemp - _outTemp + 1
    sclTemp        = sectHeight / tempDiff     # Takes the difference between inside and outside temperatures
    outTempFix = (_internalTemp + 1) * sclTemp
    if outTempFix   >= 1.: outTempFix = outTempFix - 1.0
    else:                  outTempFix = -(1 - outTempFix)
    
    scaleRH_Text.append('RH')
    scaleTemp_Text.append('Tmp')
    scaleRH_TextPts.append( rc.Geometry.Point3d(-0.29, sectHeight + 0.015, 0.) )
    scaleTemp_TextPts.append( rc.Geometry.Point3d(-0.5, sectHeight + 0.015, 0.) )
    
    text = 0
    scRH = rc.Geometry.Curve.DivideByLength(axisRH,sclRH*10, True)
    for pt in scRH:
        pt1 = rc.Geometry.Point3d(-0.37, pt, 0.)
        pt2 = rc.Geometry.Point3d(-0.33, pt, 0.)
        scaleRH_TempGeo.append(rc.Geometry.LineCurve(pt1, pt2))
        scaleRH_TempGeoColor.append(layerColors[6])
        
        txtTemp = (pt + outTempFix) / sclTemp
        scaleTemp_Text.append( str( round(txtTemp) ) )
        
        scaleRH_Text.append(str(text) + '%')
        scaleRH_TextPts.append(     rc.Geometry.Point3d(-0.3, pt - 0.015, 0.)   )
        scaleTemp_TextPts.append(   rc.Geometry.Point3d(-0.52, pt - 0.015, 0.)   )
        text += 10
    return scaleRH_TempGeo, scaleRH_TempGeoColor, scaleRH_Text, scaleTemp_Text, scaleRH_TextPts, scaleTemp_TextPts

###########################################################################################
#Check the inputs.
checkData, surfaceType = checkInputs()

#If the inputs are good, GO and do your think
if checkData == True:
    layerColors = colors()
    sectHeight  = 1.0        # Set the height of the section
    textSize    = 0.04
    layersWallGeo, onlyMesh, resultLines, resultLinesColors, titleCoord, wallSectCoord, wallLegendCoord, \
                   materials, thicknessMat, conductivityMat, rWall, newRValue, rWallCumulPerc, tempWall, dewPointWall, rhWall, condensationWall, \
                   lb_visualization, lb_preparation = \
                   main(surfaceType, layerColors, sectHeight)
    
    allLabels = drawText(titleCoord, wallSectCoord, wallLegendCoord, materials, thicknessMat, surfaceType, lb_visualization, lb_preparation)
    
    scaleRH_TempGeo, scaleRH_TempGeoColor, scaleRH_Text, scaleTemp_Text, scaleRH_TextPts, scaleTemp_TextPts = \
                scaleRH_Temp(surfaceType, sectHeight, layerColors)      # Draw the scales of RH and Temperature/DewPoint
    allLabels = rhText(scaleRH_Text,   scaleRH_TextPts,   allLabels, surfaceType, textSize, lb_visualization, lb_preparation)
    allLabels = rhText(scaleTemp_Text, scaleTemp_TextPts, allLabels, surfaceType, textSize, lb_visualization, lb_preparation)
    
    #print 'Construction = ', _cnstrName
    ##for i in range(len(materials)):
    ##    print 'Thickness = %.3f \ttempWall = %.2f \tDewPoint = %.2f \ttrhOutter = %.2f \tcondensation = %s  \tLayer-%d = %s' % \
    ##    (thicknessMat[i], tempWall[i], dewPointWall[i], rhWall[i], condensationWall[i], i, materials[i])
        
    #Transform the geometry according to the base point and scale provided on input items.
    if _scale_ != None:
        scale = _scale_
    else: scale = 1
    if _basePoint_ != None:
        basePoint = _basePoint_
    else:
        basePoint = rc.Geometry.Point3d.Origin

    scaleFinal = rc.Geometry.Transform.Scale(basePoint, scale)
    move = rc.Geometry.Transform.Translation(basePoint.X, basePoint.Y, basePoint.Z)
    transformMtx = scaleFinal * move
    for geo in resultLines:     geo.Transform(transformMtx)
    for geo in onlyMesh:        geo.Transform(transformMtx)   # This is only for BAKE. Need to find how to check if a geometry is a mesh
    for geo in layersWallGeo:   geo.Transform(transformMtx)
    for geo in wallSectCoord:   geo.Transform(transformMtx)   # For numbering the wall layers (1, 2, 3 ..., n) below the wall section geometry
    for geo in wallLegendCoord: geo.Transform(transformMtx)   # For wall legend. One  below the other for wall section members (Name and results)
    for geo in allLabels:       geo.Transform(transformMtx)   # For wall legend. One  below the other for wall section members (Name and results)
    for geo in scaleRH_TempGeo: geo.Transform(transformMtx)   # For wall legend. One  below the other for wall section members (Name and results)
    titleCoord.Transform(transformMtx)                        # For the Construction Name


    #"""
    if bakeIt_ > 0:
        decimalPlaces = 1
        legend = None
        allLines = []
        allLines.extend(resultLines)
        allLines.extend(scaleRH_TempGeo)
        print len(resultLines), len(scaleRH_TempGeo), len(allLines)
        #Make a single mesh for all data.
        finalJoinedMesh = rc.Geometry.Mesh()
        ##for meshList in layersWallGeo:
        ##    for mesh in meshList: finalJoinedMesh.Append(mesh)
        #$#$for mesh in layersWallGeo:
        for mesh in onlyMesh:
            finalJoinedMesh.Append(mesh)
            #if mesh == rc.DocObjects.ObjectType.Mesh(32):
            #print type(mesh), mesh
            #if type(mesh) == 'Mesh':
            ###print type(mesh)
            pass
            #if mesh.IsMesh():
            #if rc.Geometry.Mesh.IsClosed(mesh):
            #    finalJoinedMesh.Append(mesh)
        #Make a single list of curves for all data.
        allDataCurves = []
        #for crvList in dataCurves:
        #    for crv in crvList: allDataCurves.append(crv)
        #    studyLayerName = 'WallSection'  #'MONTHLY_CHARTS'
        for crv in allLines: allDataCurves.append(crv)
        print len(allDataCurves)
        studyLayerName = 'Wall_Sections'
        # check the study type
        try:
            #if 'key:location/dataType/units/frequency/startsAt/endsAt' in _inputData[0]: placeName = _inputData[1]
            #else: placeName = _cnstrName        #'alternateLayerName'
            placeName     = _cnstrName        #'alternateLayerName'
        except: placeName = _cnstrName        #
        newLayerIndex, l = lb_visualization.setupLayers(None, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
        #print newLayerIndex, l
        
        #@#@if bakeIt_ == 1:   lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend, allLabels, wallLegendCoord, textSize, 'Verdana', allDataCurves, decimalPlaces, 2)
        
        #if bakeIt_ == 1:   lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allLabels, wallLegendCoord, textSize, 'Verdana', graphAxes+allDataCurves, decimalPlaces, 2)
        #else:              lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allLabels, wallLegendCoord, textSize, 'Verdana', graphAxes+allDataCurves, decimalPlaces, 2, False)
    #"""

"""    
#Hide(True)/Show(False) outputs
ghenv.Component.Params.Output[1].Hidden   = True     # materials
ghenv.Component.Params.Output[2].Hidden   = True     # comments
ghenv.Component.Params.Output[3].Hidden   = True     # rWall
ghenv.Component.Params.Output[4].Hidden   = True     # tempWall
ghenv.Component.Params.Output[5].Hidden   = False    # rhWall
ghenv.Component.Params.Output[6].Hidden   = False    # dewPointWall
ghenv.Component.Params.Output[7].Hidden   = False    # condensationWall
ghenv.Component.Params.Output[8].Hidden   = False    # ::::::::::::::::::::::::::::::::::::::
ghenv.Component.Params.Output[9].Hidden   = False    # layersWallGeo
ghenv.Component.Params.Output[10].Hidden   = False    # resultLines
ghenv.Component.Params.Output[11].Hidden   = False    # resultLinesColors
ghenv.Component.Params.Output[12].Hidden   = False    # scaleRH_TempGeo
ghenv.Component.Params.Output[13].Hidden   = False    # allLabels
ghenv.Component.Params.Output[14].Hidden   = False    # ::::::::::::::::::::::::::::::::::::::
ghenv.Component.Params.Output[15].Hidden   = False    # finalJoinedMesh
ghenv.Component.Params.Output[16].Hidden   = False    # legend
ghenv.Component.Params.Output[17].Hidden   = False    # allLabels
ghenv.Component.Params.Output[18].Hidden   = False    # wallLegendCoord
ghenv.Component.Params.Output[19].Hidden   = False    # allDataCurves
ghenv.Component.Params.Output[20].Hidden   = False    # textSize
ghenv.Component.Params.Output[21].Hidden   = False    # decimalPlaces
"""
ghenv.Component.Params.Output[9].Hidden   = False    # layersWallGeo
ghenv.Component.Params.Output[10].Hidden   = False    # resultLines
ghenv.Component.Params.Output[12].Hidden   = False    # scaleRH_TempGeo
ghenv.Component.Params.Output[13].Hidden   = False    # allLabels
ghenv.Component.Params.Output[15].Hidden   = False    # finalJoinedMesh
ghenv.Component.Params.Output[16].Hidden   = True    # legend
ghenv.Component.Params.Output[17].Hidden   = False    # allLabels
ghenv.Component.Params.Output[18].Hidden   = True    # wallLegendCoord
ghenv.Component.Params.Output[19].Hidden   = False    # allDataCurves
