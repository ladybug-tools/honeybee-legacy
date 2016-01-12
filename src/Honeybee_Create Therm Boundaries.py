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
        _boundaryCurve: A polyline or list of polylines that coincide with the thermPolygons that you plan to connect to the "Write Therm File" component.
        _name: An name for the boundary condition to keep track of it through the creation of the THERM model.  If no value is input here, a default unique name will be generated.
        _temperature: A numerical value that represents the temperature at the boundary in degrees Celcius.
        _filmCoefficient: Either a numerical value in W/m2-K that represents the conductivity of the air film at the boundary condition or simply input the word 'indoor' or 'outdoor' to have the film coefficient autocalculated based on the position of geometry in the Rhino scene and an interpolation of values from Table 10 from chapter 26 of ASHRAE Fundementals 2013:
            _
            Typical film coefficient values range from 26 W/m2-K (for an NFRC exterior envelope) to 2.5 W/m2-K (for an interior wood/vinyl surface).
            _
            Note that, when inputting 'outdoor', the component will assume an outdoor wind speed of 3.4 m/s (22.7 W/m2-K) and, for higher wind speeds, higher film coefficients should be input (ie. 6.7 m/s = 34.0 W/m2-K).
        uFactorTag_: An optional text string to define a U-Factor tag for the boundary condition.  U-Factor tags are used tell THERM the boundary on which you would like to compute a U-Value.  The default is set to to have no U-Factor tag.  This input can be any text string.  For example "Frame", "Edge", or "Spacer."
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
ghenv.Component.Message = 'VER 0.0.57\nJAN_12_2016'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nJAN_12_2016
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance

def main(boundaryCurve, temperature, filmCoefficient, crvName, uFactorTag, RGBColor):
    # import the classes
    hb_thermBC = sc.sticky["honeybee_ThermBC"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    #Make a list to hold the final outputs.
    HBThermBoundary = []
    
    #Check that the film coefficient makes sense.
    try: filmCoefficient = float(filmCoefficient)
    except:
        if filmCoefficient.upper() == 'INDOOR' or filmCoefficient.upper() == 'OUTDOOR': filmCoefficient = filmCoefficient.upper()
        else:
            warning = "The connected _filmCoefficient is not recognized. \n This input must be either a numerical value or the word 'indoor' or 'outdoor' (without quotations)."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
    #Check to be sure that the polyline is planar.
    boundaryCurve = rc.Geometry.PolylineCurve(boundaryCurve)
    boundPlane = None
    if boundaryCurve.IsPlanar(sc.doc.ModelAbsoluteTolerance):
        boundPlane = boundaryCurve.TryGetPlane(sc.doc.ModelAbsoluteTolerance)[-1]
    else:
        warning = "The connected boundaryCurve geometry is not planar."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # 0. check if user input a name for this polyline
    guid = str(uuid.uuid4())
    number = guid.split("-")[-1]
    
    if crvName != None:
        crvName = crvName.strip().replace(" ","_")
    else:
        # generate a random name
        crvName = "".join(guid.split("-")[:-1])
    
    #Make the therm boundary condition.
    HBThermBC = hb_thermBC(boundaryCurve, crvName, temperature, filmCoefficient, boundPlane, None, None, RGBColor, uFactorTag)
    
    # add to the hive
    thermBoundary  = hb_hive.addToHoneybeeHive([HBThermBC], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return thermBoundary

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


if initCheck == True and _boundaryCurve != None and _name != None and _temperature != None and _filmCoefficient != None:
    result= main(_boundaryCurve, _temperature, _filmCoefficient, _name, uFactorTag_, RGBColor_)
    
    if result!=-1:
        thermBoundary = result
