#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Provided by Honeybee 0.0.62

    Args:
        _boundaryCurve: A polyline or list of polylines that coincide with the thermPolygons that you plan to connect to the "Write Therm File" component.
        _name: An name for the boundary condition to keep track of it through the creation of the THERM model.  If no value is input here, a default unique name will be generated.
        _temperature: A numerical value that represents the temperature at the boundary in degrees Celcius.  For NFRC conditions, this temperature should be 21 C for interior boundary conditions and -18 C for exterior boundary conditions.
        _filmCoefficient: A numerical value in W/m2-K that represents the convective resistance of the air film at the boundary condition.  Alternatively, you can simply input the word 'indoor' or 'outdoor' to have the film coefficient autocalculated based on the position of geometry in the Rhino scene and an interpolation of values from Table 10 from chapter 26 of ASHRAE Fundementals 2013.
            _
            Typical film coefficient values range from 36 W/m2-K (for an exterior condition where outdoor wind strips away most convective resistance) to 2.5 W/m2-K (for a vertically-oriented interior wood/vinyl surface).
            _
            Note that, when inputting 'outdoor', the component will assume an outdoor wind speed of ~4.5 m/s (and a corresponding film coefficient of 26 W/m2-K). You may want to simulate with a lower wind speed of 3.4 m/s (filmCoefficient = 22.7 W/m2-K) or a higher wind speed of 6.7 m/s (filmCoefficient = 34.0 W/m2-K).
        emissivity_: An optional number between 0 and 1 to set an override for the emissivity along the boundary.  By default, the Grasshopper components will take the emissivity of the material that is adjacent to the boundary.  However, a value here can over-ride this value to account for coatings like those on Low-E glass or matte paint on metallic materials.
        customRadEnv_: A list of radiant environmental properties from the 'Honeybee_Custom Radiant Environment' component.  Inputting values here will create a radiant environment that is different than typical NFRC conditions.
        uFactorTag_: An optional text string to define a U-Factor tag for the boundary condition.  U-Factor tags are used tell THERM the boundary on which you would like to compute a U-Value.  The default is set to to have no U-Factor tag.  This input can be any text string.  For example "Frame", "Edge", or "Spacer."
        RGBColor_: An optional color to set the color of the boundary condition when you import it into THERM.
    Returns:
        readMe!:...
        thermBoundary: A polyline with the specified boudary condition properties, to be plugged into the "boundaries" input of the "Write Therm File" component.
"""

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid
import decimal

ghenv.Component.Name = 'Honeybee_Create Therm Boundaries'
ghenv.Component.NickName = 'createThermBoundaries'
ghenv.Component.Message = 'VER 0.0.62\nOCT_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nMAY_26_2017
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


tolerance = sc.doc.ModelAbsoluteTolerance
w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error

def main(boundaryCurve, temperature, filmCoefficient, crvName, emissivity, customRadEnv, uFactorTag, RGBColor):
    # import the classes
    hb_thermBC = sc.sticky["honeybee_ThermBC"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    #Make a list to hold the final outputs.
    HBThermBoundary = []
    
    #Check that the film coefficient makes sense.
    try: filmCoefficient = float(filmCoefficient)
    except:
        if filmCoefficient.upper() == 'INDOOR' or filmCoefficient.upper() == 'OUTDOOR':
            filmCoefficient = filmCoefficient.upper()
        else:
            warning = "The connected _filmCoefficient is not recognized. \n This input must be either a numerical value or the word 'indoor' or 'outdoor' (without quotations)."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
    #Check to be sure that any emissivity values make sense.
    if emissivity != None:
        if emissivity > 1 or emissivity < 0:
            warning = "emissivity_ must be between 0 and 1"
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
    # Read out any custon radiant envrionment.
    if customRadEnv != []:
        if len(customRadEnv) == 4:
            radTemp, envEmiss, viewFactor, heatFlux = customRadEnv
        else:
            warning = "customRadEnv_ is not valid.  Plug in the output of the 'Honeybee_Custom Radiant Environment' component."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    else:
        radTemp, envEmiss, viewFactor, heatFlux = None, None, None, None
    
    # Assign default radiation models and view factors based on NFRC.
    if viewFactor == None:
        if filmCoefficient == 'OUTDOOR':
            viewFactor = 1.0
        else:
            try:
                if float(filmCoefficient) > 10:
                    viewFactor = 1.0
                else:
                    viewFactor = None
            except:
                viewFactor = None
    else:
        try:
            viewFactor = float(viewFactor)
        except:
            try:
                if viewFactor.lower() == 'auto':
                    viewFactor = None
                else:
                    warning = "viewFactor_ is not valid.  Plug in the output of the 'Honeybee_Custom Radiant Environment' component."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                warning = "viewFactor_ is not valid.  Plug in the output of the 'Honeybee_Custom Radiant Environment' component."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
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
    HBThermBC = hb_thermBC(boundaryCurve, crvName, temperature, filmCoefficient, boundPlane, radTemp, None, RGBColor, uFactorTag, emissivity, viewFactor, envEmiss, heatFlux, ghenv)
    
    # add to the hive
    thermBoundary  = hb_hive.addToHoneybeeHive([HBThermBC], ghenv.Component)
    
    if uFactorTag != None:
        print "UFactor Tag set to: " + uFactorTag
    
    return thermBoundary

#Ladybug check.
initCheck = True
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


if initCheck == True and _boundaryCurve != None and _name != None and _temperature != None and _filmCoefficient != None:
    result= main(_boundaryCurve, _temperature, _filmCoefficient, _name, emissivity_, customRadEnv_, uFactorTag_, RGBColor_)
    
    if result!=-1:
        thermBoundary = result
