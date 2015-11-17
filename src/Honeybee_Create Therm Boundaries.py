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
Use this component to create a THERM boundary condition.
-
Provided by Honeybee 0.0.57

    Args:
        _boundaryCurves: A polyline or list of polylines that coincide with the thermPolygons that you plan to connect to the "Write Therm File" component.
        temperature_: A numerical value that represents the temperature at the boundary in degrees Celcius.
        filmCoefficient_: A numerical value in W/m2-K (or SI U-Values) that represents the conductivity of the air film at the boundary condition.  Typical values range from 26 W/m2-K (for an NFRC exterior envelope) to 2.5 W/m2-K (for an interior wood/vinyl surface).
        name_: An optional name for the boundary condition to keep track of it through the creation of the THERM model.  If no value is input here, a default unique name will be generated.
        radiantTemp_: An optional numerical value that sets the radiant temperature at the boundary condition in degrees Celcius.  If no value is input here, it will be assumed that the radiant temperature is the same as the air temperature (input above).
        radTransCoeff_: An optional numerical value in W/m2-K (or SI U-Values) that represents the radiant conductivity of the boundary condition. If no value is input here, a default of -431602080 will ve used.
        RGBColor_: An optional color to set the color of the boundary condition when you import it into THERM.
    Returns:
        readMe!:...
        thermBoundary: A polyline with the specified boudary condition properties, to be plugged into the "boundaries" input of the "Write Therm File" component.
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid
import math

ghenv.Component.Name = 'Honeybee_Create Therm Boundaries'
ghenv.Component.NickName = 'createThermBoundaries'
ghenv.Component.Message = 'VER 0.0.57\nNOV_16_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nNOV_16_2015
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def main(boundaryCurves, temperature, filmCoefficient, radiantTemp, radTransCoeff, RGBColor):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):
    
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        # don't customize this part
        hb_thermBC = sc.sticky["honeybee_ThermBC"]
        hb_hive = sc.sticky["honeybee_Hive"]()
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    
    #Make a list to hold the final outputs.
    HBThermBoundary = []
    originalSrfName = srfName
    
    for faceCount in range(geometry.Faces.Count):
        #Check to be sure that the surface is planar.
        if geometry.Faces[faceCount].IsPlanar(sc.doc.ModelAbsoluteTolerance): pass
        else:
            warning = "The connected surface geometry is not planar."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        # 0. check if user input a name for this surface
        guid = str(uuid.uuid4())
        number = guid.split("-")[-1]
        
        if srfName != None:
            if originalSrfName == None: originalSrfName = srfName
            originalSrfName = originalSrfName.strip().replace(" ","_")
            if geometry.Faces.Count != 1:
                srfName = originalSrfName + "_" + `faceCount`
            else: srfName = originalSrfName
        else:
            # generate a random name
            # the name will be overwritten for energy simulation
            srfName = "".join(guid.split("-")[:-1])
        
        # 1.3 assign a material
        if material!=None:
            # if it is just the name of the material make sure it is already defined
            if len(material.split("\n")) == 1:
                material = material.upper()
                if material in sc.sticky ["honeybee_materialLib"].keys(): pass
                elif material in sc.sticky ["honeybee_windowMaterialLib"].keys():pass
                else:
                    warningMsg = "Can't find " + material + " in EP Material Library.\n" + \
                                "Create the material and try again."
                    print warningMsg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    return -1
            # if the material is not in the library add it to the library
            else:
                # it is a full string
                added, material = hb_EPMaterialAUX.addEPConstructionToLib(material, overwrite = True)
                material = material.upper()
                
                if not added:
                    msg = material + " is not added to the project library!"
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                    return -1
        
        #Make the therm polygon.
        HBThermPolygon = hb_thermPolygon(geometry.Faces[faceCount].DuplicateFace(False), material, srfName)
        
        HBThermPolygons.append(HBThermPolygon)
    
    
    # add to the hive
    HBThermPolygon  = hb_hive.addToHoneybeeHive(HBThermPolygons, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBThermPolygon


if _boundaryCurves != None and _temperature != None and _filmCoefficient != None:
    result= main(_boundaryCurves, _temperature, _filmCoefficient, radiantTemp_, radTransCoeff_, RGBColor_)
    
    if result!=-1:
        thermBoundary = result
