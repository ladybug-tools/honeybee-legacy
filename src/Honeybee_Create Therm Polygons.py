#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to create a THERM polygon with material properties.
-
Provided by Honeybee 0.0.60

    Args:
        _geometry: A closed planar curve or list of closed planar curves that represent the portions of a construction that have the same material type.  This input can also accept closed planar surfaces/breps/polysurfaces and even meshes!
        _material: Either the name of an EnergyPlus material from the OpenStudio library (from the "Call from EP Construction Library" component) or the output of any of the components in the "06 | Energy | Material" tab for creating materials.
        RGBColor_: An optional color to set the color of the material when you import it into THERM.  All materials from the Honyebee Therm Library already possess colors but materials from the EP material lib will have a default blue color if no one is assigned here.
    Returns:
        readMe!:...
        thermPolygon: A polygon representing material properties
"""

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid
import decimal

ghenv.Component.Name = 'Honeybee_Create Therm Polygons'
ghenv.Component.NickName = 'createThermPolygons'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance
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


def main(geometry, material, RGBColor):
    # import the classes
    hb_thermPolygon = sc.sticky["honeybee_ThermPolygon"]
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    thermDefault = sc.sticky["honeybee_ThermDefault"]()
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    #Define a varialbe for acceptable geometry.
    geometryAccepted = False
    
    # if the input is mesh, convert it to a surface
    try:
        # check if this is a mesh
        geometry.Faces[0].IsQuad
        # convert to brep
        geometry = rc.Geometry.Brep.CreateFromMesh(geometry, False)
        geometryAccepted = True
    except:
        pass
    
    #If the input is a polyline, convert it to a surface.
    try:
        geometry = rc.Geometry.Brep.CreatePlanarBreps(geometry)
        if len(geometry) == 1:
            geometryAccepted = True
            geometry = geometry[0]
        else:
            warning = "The connected polyline geometry does not form a single closed planar surface. \n Try joining the curves into a single polyline before inputting them."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    except:
        pass
    
    #If the input has failed all tests up to this point, it is hopefully a planar brep or surface and we will just check this.
    if geometryAccepted == False:
        try:
            geometry.IsSurface
            geometryAccepted = True
        except: pass
        try:
            if geometry.HasBrepForm: geometry = geometry.ToBrep()
            geometryAccepted = True
        except: pass
    
    #If the geometry was not recognized, give a warning.
    if geometryAccepted == False:
        warning = "The connected geometry was not recognized as a polyline, surface, brep/polysurface, or mesh."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Make a list to hold the final outputs.
    HBThermPolygons = []
    
    for faceCount in range(geometry.Faces.Count):
        #Check to be sure that the surface is planar.
        polyPlane = None
        if geometry.Faces[faceCount].IsPlanar(sc.doc.ModelAbsoluteTolerance):
            centPt, normal = getSrfCenPtandNormal(geometry)
            plane = rc.Geometry.Plane(centPt, normal)
        else:
            warning = "The connected surface geometry is not planar."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        #Assign a material
        if material!=None:
            # if it is just the name of the material make sure it is already defined
            if material.startswith("<Material"):
                #Its a full string of a custom THERM material.
                material = thermDefault.addThermMatToLib(material)
            elif len(material.split("\n")) == 1:
                #Its the name of a material.
                material = material.upper()
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
                added, material = hb_EPMaterialAUX.addEPConstructionToLib(material, overwrite = True)
                material = material.upper()
                
                if not added:
                    msg = material + " is not added to the project library!"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                    return -1
        
        #Make the therm polygon.
        guid = str(uuid.uuid4())
        polyName = "".join(guid.split("-")[:-1])
        HBThermPolygon = hb_thermPolygon(geometry.Faces[faceCount].DuplicateFace(False), material, polyName, plane, RGBColor)
        
        if HBThermPolygon.warning != None:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, HBThermPolygon.warning)
        
        HBThermPolygons.append(HBThermPolygon)
    
    # add to the hive
    HBThermPolygon  = hb_hive.addToHoneybeeHive(HBThermPolygons, ghenv.Component)
    
    return HBThermPolygon


#Honeybee check.
initCheck = True
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

#If the Rhino model tolerance is not fine enough for THERM modelling, give a warning.
if initCheck == True:
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    conversionFactor = lb_preparation.checkUnits()*1000
    d = decimal.Decimal(str(sc.doc.ModelAbsoluteTolerance))
    numDecPlaces = abs(d.as_tuple().exponent)
    numConversionFacPlaces = len(list(str(int(conversionFactor))))-1
    numDecPlaces = numDecPlaces - numConversionFacPlaces
    if numDecPlaces < 2:
        zeroText = ''
        for val in range(abs(2-numDecPlaces)): zeroText = zeroText + '0'
        correctDecimal = '0.' + zeroText + str(sc.doc.ModelAbsoluteTolerance).split('.')[-1]
        warning = "Your Rhino model tolerance is coarser than the default tolerance for THERM. \n It is recommended that you decrease your Rhino model tolerance to " + correctDecimal + " " + str(sc.doc.ModelUnitSystem) + " \n by typing 'units' in the Rhino command bar and adding decimal places to the 'tolerance'."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True and _geometry != None and _material != None:
    result= main(_geometry, _material, RGBColor_)
    
    if result!=-1:
        thermPolygon = result
