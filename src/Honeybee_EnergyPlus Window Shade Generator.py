# This component creates shades for Honeybee Zones
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate shades for Honeybee zone windows. The component has two main uses:
_
The first is that it can be used to assign shade objects to HBZones prior to simulation.  These shades can be dynamically controlled via a schedule.  Note that shades created this way will automatically be assigned to the zone and the windowBreps and shadeBreps outputs are just for visualization.
_
The second way to use the component is to create test shade areas for shade benefit evaluation after an energy simulation has already been run.  In this case, the component helps keep the data tree paths of heating, cooling and beam gain synced with that of the zones and windows.  For this, you would take imported EnergyPlus results and hook them up to the "zoneData" inputs and use the output "zoneDataTree" in the shade benefit evaluation.
-
Provided by Honeybee 0.0.60
    
    Args:
        _HBObjects: The HBZones or HBSurfaces out of any of the HB components that generate or alter zones.
        shadeType_: An integer to specify the type of shade that you wish to assign to the windows.  The default is set to 0 = blinds.  Choose from the following options:
            0 = Blinds - typical venetian blinds that can be either on the interior or exterior of the glass.
            1 = Shades - either a fabric roller shade or a perforated metal screen that transmits light more evenly than slatted blinds.
            2 = Swtichable Glazing - represents electrochromic glazing that can be switched on to reflect the material state of the shadeMaterial_.
        shadeMaterial_: An optional shade material from the "Honeybee_EnergyPlus Shade Material" component.  If no material is connected here, the component will automatically assign a material depending on the shade type above.  The default blinds material has 0.65 solar reflectance, 0 transmittance, 0.9 emittance, 0.25 mm thickness, 221 W/mK conductivity.
        shadeSchedule_: An optional schedule to raise and lower the shades.  If no value is connected here, the shades will assume the "ALWAYS ON" shcedule.
        shadeCntrlType_: An integer represeting the parameter that controls whether the shades are on (down) or off (up).  The default is set to 0 = OnIfScheduleAllows.  If no schedule is connected, the shades are assumed to always be down. Choose from the following options:
            0 = OnIfScheduleAllows - Shading is on if the schedule value is non-zero and is AlwaysOn if no schedule is connected.
            1 = OnIfHighSolarOnWindow - Shading is on if beam plus diffuse solar radiation incident on the window exceeds SetPoint (W/m2) below and schedule, if specified, allows shading.
            2 = OnIfHighHorizontalSolar - Shading is on if total (beam plus diffuse) horizontal solar irradiance exceeds SetPoint (W/m2) below and schedule, if specified, allows shading.
            3 = OnIfHighOutdoorAirTemperature - Shading is on if outside air temperature exceeds SetPoint (C) below and schedule, if specified, allows shading.
            4 = OnIfHighZoneAirTemperature - Shading is on if zone air temperature in the previous timestep exceeds SetPoint (C) below and schedule, if specified, allows shading.
            5 = OnIfHighZoneCooling - Shading is on if zone cooling rate in the previous timestep exceeds SetPoint (W) below and schedule, if specified, allows shading.
            6 = OnNightIfLowOutdoorTempAndOffDay - Shading is on at night if the outside air temperature is less than SetPoint (C) below and schedule, if specified, allows shading. Shading is off during the day.
            7 = OnNightIfLowInsideTempAndOffDay - Shading is on at night if the zone air temperature in the previous timestep is less than SetPoint (C) below and schedule, if specified, allows shading. Shading is off during the day.
            8 = OnNightIfHeatingAndOffDay - Shading is on at night if the zone heating rate in the previous timestep exceeds SetPoint (W) below and schedule, if specified, allows shading. Shading is off during the day.
            9 = OnNightIfLowOutdoorTempAndOnDayIfCooling - Shading is on at night if the outside air temperature is less than SetPoint (C) below. Shading is on during the day if the zone cooling rate in the previous timestep is non-zero. Night and day shading is subject to schedule, if specified.
            10 = OnNightIfHeatingAndOnDayIfCooling: Shading is on at night if the zone heating rate in the previous timestep exceeds SetPoint (W) below. Shading is on during the day if the zone cooling rate in the previous timestep is non-zero. Night and day shading is subject to schedule, if specified.
            11 = OffNightAndOnDayIfCoolingAndHighSolarOnWindow: Shading is off at night. Shading is on during the day if the solar radiation incident on the window exceeds SetPoint (W/m2) below and if the zone cooling rate in the previous timestep is non-zero. Daytime shading is subject to schedule, if specified.
            12 = OnNightAndOnDayIfCoolingAndHighSolarOnWindow: Shading is on at night. Shading is on during the day if the solar radiation incident on the window exceeds SetPoint (W/m2) below and if the zone cooling rate in the previous timestep is non-zero. Day and night shading is subject to schedule, if specified. (This Shading Control Type is the same as the previous one, except the shading is on at night rather than off.)
            13 = OnIfHighOutdoorAirTempAndHighSolarOnWindow: Shading is on if the outside air temperature exceeds the Setpoint (C) and if if the solar radiation incident on the window exceeds SetPoint 2 (W/m2).  Note that this option requires you to connect two values to the shadeSetpoint_ input below.
            14 = OnIfHighOutdoorAirTempAndHighHorizontalSolar: Shading is on if the outside air temperature exceeds the Setpoint (C) and if if the horizontal solar radiation exceeds SetPoint 2 (W/m2).  Note that this option requires you to connect two values to the shadeSetpoint_ input below.
            15 = OnIfHighGlare: Shading is on if the glare index in the zone exceeds the maximum Discomfort Glare Index (DGI) specified below.  Common maximim DGI values are 22 for Offices, 20 for Museums or Classrooms, 18 for Hospital Wards, and 16 for Art Gallereies.  In the input below, you should specify a list of 2 values that includes the DGI as a first value and a vector for the second value, which represents the direction that the occupant view is facing.  It will be assumed that the occupant is in the center of the zone by default and you can change this potition by adjusting the daylightCntrlPt_ input of the "Honeybee_Set ZoneThresholds" component.
            16 = MeetDaylightIlluminanceSetpoint: Useable only with ShadingType = SwitchableGlazing. In this case, the transmittance of the glazing is adjusted to just meet the daylight illuminance set point assinged with the "Honeybee_Set ZoneThresholds" component.  If no setpoint is assigned with this component, this component will assume a default illuminace setpoint of 300 lux. As such, there is no need to specify a setpoint below unless you also want the EC glazing to be further dimmed when there is glare in the zone, in which case the setpoint below should be a DGI value and vector representing a view as states in option 15 (OnIfHighGlare).
        shadeSetpoint_: A number that corresponds to the shadeCntrlType_ specified above.  This can be a value in (W/m2), (C) or (W) depending upon the control type.
        interiorOrExter_: Set to "True" to generate Shades on the interior and set to "False" to generate shades on the exterior.  The default is set to "False" to generate exterior shades.
        distToGlass_: A number between 0 and 1 that represents the distance between the glass and the shades in meters.  The default is set to 0 to generate the shades immediately next to the glass.
        _depth: A number representing the depth of the shade to be generated on each window.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input.
        _numOfShds: The number of shades to generated for each glazed surface.
        _distBetween: An alternate option to _numOfShds where the input here is the distance in Rhino units between each shade.
        horOrVertical_: Set to "True" to generate horizontal shades or "False" to generate vertical shades. You can also input lists of horOrVertical_ input, which will assign different orientations based on cardinal direction.
        shdAngle_: A number between -90 and 90 that represents an angle in degrees to rotate the shades.  The default is set to "0" for no rotation.  If you have vertical shades, use this to rotate them towards the South by a certain value in degrees.  If applied to windows facing East or West, tilting the shades like this will let in more winter sun than summer sun.  If you have horizontal shades, use this input to angle shades downward.  You can also put in lists of angles to assign different shade angles to different cardinal directions.
        north_: Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _runIt: Set boolean to "True" to run the component and visualize shade geometry.
        writeEPObjs_: Set boolean to "True" to generate EP Objectes that have shades and shade control assigned to them.
        zoneData1_: Optional EnergyPlus simulation data for connected HBZones_ that will be aligned with the generated windows.  Use this to align data like heating load, cooling load or beam gain for a shade benefit simulation with the generated shades.
    Returns:
        readMe!: ...
        ---------------: ...
        HBObjWShades: The conected HBObjects with shades assigned to them. With these HBObjects, there is no need to use the two geometric outputs below.  If you have produced a shade geometry that you will not be able to run through EnergyPlus, no objects will be output from here.
        ---------------: ...
        windowBreps: Breps representing each window surfaces that are being shaded.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree.
        shadeBreps: Breps representing each shade geometry.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree.  Alternatively, they can be plugged into an EnergyPlus simulation with the "Honeybee_EP Context Surfaces" component.
        ---------------: ...
        shadeMatName: The name of the shade material that has been assigned to the EPObjects.  This can be used to create EP constructions with the shade in between panes of glass.
        shadeMatIDFStr: Text strings that represent the shade material that has been assigned to the EP Objects.
        shadeCntrlIDFStr: Text strings that represent the shade control object that has been assigned to the EP Objects.
        ---------------: ...
        zoneData1Tree: Data trees of the zoneData1_, which align with the branches for each window above.
"""

ghenv.Component.Name = "Honeybee_EnergyPlus Window Shade Generator"
ghenv.Component.NickName = 'EPWindowShades'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


from System import Object
from System import Drawing
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import uuid
import math
import os
import copy

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


#### HERE ARE THE FUNCTIONS THAT SET THE INPUTS/OUTPUTS OF THE COMPONENT.
inputsDict = {
    
2: ["shadeMaterial_", "An optional shade material from the 'Honeybee_EnergyPlus Shade Material' component.  The default blinds or shade material has 0.65 solar reflectance, 0 transmittance, 0.9 emittance, 0.25 mm thickness, 221 W/mK conductivity."],
3: ["shadeSchedule_", "An optional schedule to raise and lower the shades.  If no value is connected here, the shades will assume the 'ALWAYS ON' shcedule."],
4: ["shadeCntrlType_", "An integer represeting the parameter that controls whether the shades are on (down) or off (up).  The default is set to 0 = OnIfScheduleAllows.  If no schedule is connected, the shades are assumed to always be down.  Choose from the following options: \n  0 = OnIfScheduleAllows - Shading is on if the schedule value is non-zero and is AlwaysOn if no schedule is connected. \n  1 = OnIfHighSolarOnWindow - Shading is on if beam plus diffuse solar radiation incident on the window exceeds SetPoint (W/m2) below and schedule, if specified, allows shading. \n  2 = OnIfHighHorizontalSolar - Shading is on if total (beam plus diffuse) horizontal solar irradiance exceeds SetPoint (W/m2) below and schedule, if specified, allows shading. \n  3 = OnIfHighOutdoorAirTemperature - Shading is on if outside air temperature exceeds SetPoint (C) below and schedule, if specified, allows shading. \n  4 = OnIfHighZoneAirTemperature - Shading is on if zone air temperature in the previous timestep exceeds SetPoint (C) below and schedule, if specified, allows shading. \n  5 = OnIfHighZoneCooling - Shading is on if zone cooling rate in the previous timestep exceeds SetPoint (W) below and schedule, if specified, allows shading. \n  6 = OnNightIfLowOutdoorTempAndOffDay - Shading is on at night if the outside air temperature is less than SetPoint (C) below and schedule, if specified, allows shading. Shading is off during the day. \n  7 = OnNightIfLowInsideTempAndOffDay - Shading is on at night if the zone air temperature in the previous timestep is less than SetPoint (C) below and schedule, if specified, allows shading. Shading is off during the day. \n  8 = OnNightIfHeatingAndOffDay - Shading is on at night if the zone heating rate in the previous timestep exceeds SetPoint (W) below and schedule, if specified, allows shading. Shading is off during the day. \n  9 = OnNightIfLowOutdoorTempAndOnDayIfCooling - Shading is on at night if the outside air temperature is less than SetPoint (C) below. Shading is on during the day if the zone cooling rate in the previous timestep is non-zero. Night and day shading is subject to schedule, if specified. \n  10 = OnNightIfHeatingAndOnDayIfCooling: Shading is on at night if the zone heating rate in the previous timestep exceeds SetPoint (W) below. Shading is on during the day if the zone cooling rate in the previous timestep is non-zero. Night and day shading is subject to schedule, if specified. \n  11 = OffNightAndOnDayIfCoolingAndHighSolarOnWindow: Shading is off at night. Shading is on during the day if the solar radiation incident on the window exceeds SetPoint (W/m2) below and if the zone cooling rate in the previous timestep is non-zero. Daytime shading is subject to schedule, if specified. \n  12 = OnNightAndOnDayIfCoolingAndHighSolarOnWindow: Shading is on at night. Shading is on during the day if the solar radiation incident on the window exceeds SetPoint (W/m2) below and if the zone cooling rate in the previous timestep is non-zero. Day and night shading is subject to schedule, if specified. (This Shading Control Type is the same as the previous one, except the shading is on at night rather than off.) \n  13 = OnIfHighOutdoorAirTempAndHighSolarOnWindow: Shading is on if the outside air temperature exceeds the Setpoint (C) and if if the solar radiation incident on the window exceeds SetPoint 2 (W/m2).  Note that this option requires you to connect two values to the shadeSetpoint_ input below. \n  14 = OnIfHighOutdoorAirTempAndHighHorizontalSolar: Shading is on if the outside air temperature exceeds the Setpoint (C) and if if the horizontal solar radiation exceeds SetPoint 2 (W/m2).  Note that this option requires you to connect two values to the shadeSetpoint_ input below."],
5: ["shadeSetpoint_", "A number that corresponds to the shadeCntrlType_ specified above.  This can be a value in (W/m2), (W), (C), or (DGI) depending upon the control type."],
6: ["interiorOrExter_", "Set to 'True' to generate Shades on the interior and set to 'False' to generate shades on the exterior.  The default is set to 'False' to generate exterior shades."],
7: ["distToGlass_", "A number between 0 and 1 that represents the distance between the glass and the shades in meters.  The default is set to 0 to generate the shades immediately next to the glass."],
8: ["_depth", "A number representing the depth of the shade to be generated on each window.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input."],
9: ["_numOfShds", "The number of shades to generated for each glazed surface."],
10: ["_distBetween", "An alternate option to _numOfShds where the input here is the distance in Rhino units between each shade."],
11: ["horOrVertical_", "Set to 'True' to generate horizontal shades or 'False' to generate vertical shades. You can also input lists of horOrVertical_ input, which will assign different orientations based on cardinal direction."],
12: ["shdAngle_", "A number between -90 and 90 that represents an angle in degrees to rotate the shades.  The default is set to '0' for no rotation.  If you have vertical shades, use this to rotate them towards the South by a certain value in degrees.  If applied to windows facing East or West, tilting the shades like this will let in more winter sun than summer sun.  If you have horizontal shades, use this input to angle shades downward.  You can also put in lists of angles to assign different shade angles to different cardinal directions."],
13: ["north_", "Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees)."],
14: ["_runIt", "Set boolean to 'True' to run the component and generate shades."],
15: ['writeEPObjs_', 'Set boolean to "True" to generate EP Objectes that have shades and shade control assigned to them.']
}

outputsDict = {
    
0: ["readMe!", "..."],
1: ["---------------", "..."],
2: ["HBObjWShades", "The conected HBObjects with shades assigned to them. With these HBObjects, there is no need to use the two geometric outputs below.  If you have produced a shade geometry that you will not be able to run through EnergyPlus, no objects will be output from here."],
3: ["---------------", "..."],
4: ["windowBreps", "Breps representing each window surfaces that are being shaded.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree."],
5: ["shadeBreps", "Breps representing each shade geometry.  These can be plugged into a shade benefit evaulation as each window is its own branch of a grasshopper data tree.  If you use the HBObjects above, there is no need to use this output (it is purely visual).  However, if no HBObjects are produced, these can be plugged into an EnergyPlus simulation with the 'Honeybee_EP Context Surfaces' component."],
6: ["---------------", "..."],
7: ["shadeMatName", "The name of the shade material that has been assigned to the EPObjects.  This can be used to create EP constructions with the shade in between panes of glass."],
8: ["shadeMatIDFStr", "Text strings that represent the shade material that has been assigned to the EP Objects."],
9: ["shadeCntrlIDFStr", "Text strings that represent the shade control object that has been assigned to the EP Objects."],
10: ["---------------", "..."]
}


def setComponentInputs(shadeType):
    numInputs = ghenv.Component.Params.Input.Count
    for input in range(numInputs):
        if input <= 1 or input == 4:
            pass
        elif input <= 15:
            if shadeType == 1 and input <=12 and input >= 9:
                ghenv.Component.Params.Input[input].NickName = "___________"
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            elif shadeType == 1 and input == 8:
                ghenv.Component.Params.Input[input].NickName = "airPermeability_"
                ghenv.Component.Params.Input[input].Name = "airPermeability_"
                ghenv.Component.Params.Input[input].Description = "An optional number between 0 and 1 to set the air permeability of the shade.  For example, use this to account for perforations in outdoor metal screens where air can circulate through.  The default is set to have 0 permeability."
            elif shadeType == 2 and input == 2:
                ghenv.Component.Params.Input[input].NickName = "shadeMaterial_"
                ghenv.Component.Params.Input[input].Name = "shadeMaterial_"
                ghenv.Component.Params.Input[input].Description = "An optional EP Construction that represents the Electrochromic Glazing in the shaded state.  If no construction is connected here, the component will automatically generate an EnergyPlus construction based on the existing assigned window construciton and will change the SHGC to 0.07 and VT to 0.01."
            elif shadeType == 2 and input <=12 and input >= 6:
                ghenv.Component.Params.Input[input].NickName = "____________"
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
        else:
            inputName = 'zoneData' + str(input-15) +'_'
            ghenv.Component.Params.Input[input].NickName = inputName
            ghenv.Component.Params.Input[input].Name = inputName
            ghenv.Component.Params.Input[input].Description = 'Optional EnergyPlus simulation data for connected HBZones_ that will be aligned with the generated windows.  Use this to align data like heating load, cooling load or beam gain for a shade benefit simulation with the generated shades.'
    
    numOutputs = ghenv.Component.Params.Output.Count
    for output in range(numOutputs):
        if output <= 10:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
        else:
            outputName = 'zoneData' + str(output-10) +'Tree'
            ghenv.Component.Params.Output[output].NickName = outputName
            ghenv.Component.Params.Output[output].Name = outputName
            ghenv.Component.Params.Output[output].Description = 'Data trees of ' + outputName + ', which align with the branches for each window above.'


def restoreComponentInputs():
    numInputs = ghenv.Component.Params.Input.Count
    for input in range(numInputs):
        if input <= 1 or input == 4:
            pass
        elif input <= 15:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
        else:
            inputName = 'zoneData' + str(input-15) +'_'
            ghenv.Component.Params.Input[input].NickName = inputName
            ghenv.Component.Params.Input[input].Name = inputName
            ghenv.Component.Params.Input[input].Access = gh.GH_ParamAccess.tree
    
    numOutputs = ghenv.Component.Params.Output.Count
    for output in range(numOutputs):
        if output <= 10:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
        else:
            outputName = 'zoneData' + str(output-10) +'Tree'
            ghenv.Component.Params.Output[output].NickName = outputName
            ghenv.Component.Params.Output[output].Name = outputName
            ghenv.Component.Params.Output[output].Description = 'Data trees of ' + outputName + ', which align with the branches for each window above.'


#### HERE ARE THE FUNCTIONS THAT CHECK THE INPUTS.
def checkAllInputs(zoneNames, windowNames, windowSrfs, isZone):
    #Check if the shadeType is acceptable.
    checkData1 = True
    if shadeType_ != None:
        if shadeType_ < 0 or shadeType_ > 2:
            checkData1 = False
            print "shadeType_ must be an integer from 0 to 2."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "shadeType_ must be an integer from 0 to 2.")
    
    #Check is the shadeCntrlType is acceptable.
    checkData2 = True
    if shadeCntrlType_ != None:
        if shadeCntrlType_ < 0 or shadeCntrlType_ > 16:
            checkData2 = False
            print "shadeCntrlType_ must be an integer from 0 to 16."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "shadeCntrlType_ must be an integer from 0 to 16.")
        elif shadeCntrlType_ > 0 and shadeCntrlType_ < 13:
            if len(shadeSetpoint_) != 1:
                checkData2 = False
                warning = 'To use shadeCntrlTypes 1 through 12, you must specify a single shadeSetpoint_.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        elif shadeCntrlType_ > 12 and shadeCntrlType_ < 16:
            if len(shadeSetpoint_) != 2:
                checkData2 = False
                warning = 'To use shadeCntrlTypes 13, 14 or 15, you must specify two shadeSetpoint_ values.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        if shadeCntrlType_ == 16:
            if not shadeType_ == 2:
                checkData2 = False
                warning = 'The shadeCntrlType_ 16-MeetDaylightIlluminanceSetpoint can only be used when the shadeType_ is set to 2-Switchable Glazing.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            elif len(shadeSetpoint_) == 2 or len(shadeSetpoint_) == 0:
                pass
            else:
                checkData2 = False
                warning = 'The shadeCntrlType_ 16-MeetDaylightIlluminanceSetpoint accepts either 2 setpoints for glare control or no setpoints.\n A default illuminace threshold of 300 is assumed and you can change this illuminace on the "Honeybee_Set ZoneThresholds" component.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    
    #Check if there is a shades schedule connected and, if not, set a default.
    checkData4 = True
    schedule = None
    if shadeSchedule_ == None:
        schedule = "ALWAYS ON"
        print "No shade schedule has been connected.  It will be assumed that the shades are drawn when the setpoints are met."
    else:
        schedule= shadeSchedule_.upper()
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        
        if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
            msg = "Cannot find " + schedule + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            checkData4 = False
        elif schedule!=None and schedule.lower().endswith(".csv"):
            # check if csv file is existed
            if not os.path.isfile(schedule):
                msg = "Cannot find the shchedule file: " + schedule
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                checkData4 = False
    
    
    #Create a Python list from the input data trees.
    def makePyTree(zoneData):
        dataPyList = []
        for i in range(zoneData.BranchCount):
            branchList = zoneData.Branch(i)
            dataVal = []
            for item in branchList:
                dataVal.append(item)
            dataPyList.append(dataVal)
        return dataPyList
    
    allData = []
    numInputs = ghenv.Component.Params.Input.Count
    for input in range(numInputs-16):
        varStr = 'zoneData' + str(input+1) +'_'
        theVar = eval(varStr)
        try: allData.append(makePyTree(theVar))
        except: pass
    
    
    #Test to see if the data lists have a headers on them, which is necessary to match the data to a zone or window.  If there's no header, the data cannot be coordinated with this component.
    checkData3 = True
    checkBranches = []
    allHeaders = []
    allNumbers = []
    for branch in allData:
        checkHeader = []
        dataHeaders = []
        dataNumbers = []
        for list in branch:
            if str(list[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
                checkHeader.append(1)
                dataHeaders.append(list[:7])
                dataNumbers.append(list[7:])
        
        allHeaders.append(dataHeaders)
        allNumbers.append(dataNumbers)
        
        if sum(checkHeader) == len(branch):pass
        else:
            checkData3 = False
            warning = "Not all of the connected zoneData has a Ladybug/Honeybee header on it.  This header is necessary for data input to this component."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Align all of the lists to each window.
    windowNamesFinal = []
    windowBrepsFinal = []
    alignedDataTree = []
    for item in allData: alignedDataTree.append([])
    
    for zoneCount, windowList in enumerate(windowSrfs):
        if isZone == True:
            zoneName = zoneNames[zoneCount]
        for windowCount, window in enumerate(windowList):
            windowBrepsFinal.append(window)
            windowName = windowNames[zoneCount][windowCount]
            windowNamesFinal.append(windowName)
            
            for inputDataTreeCount, branch in enumerate(allHeaders):
                #Test to see if the data is for the zone level.
                zoneData = False
                if isZone == True:
                    for listCount, header in enumerate(branch):
                        if header[2].split(' for ')[-1] == zoneName.upper():
                            alignedDataTree[inputDataTreeCount].append(allData[inputDataTreeCount][listCount])
                            zoneData = True
                
                #Test to see if the data is for the window level.
                srfData = False
                if zoneData == False:
                    for listCount, header in enumerate(branch):
                        try: winNm = header[2].split(' for ')[-1].split(': ')[0]
                        except: winNm =  header[2].split(' for ')[-1]
                        if str(winNm) == str(windowName.upper()):
                            alignedDataTree[inputDataTreeCount].append(allData[inputDataTreeCount][listCount])
                            srfData = True
    
    checkData = False
    if checkData1 == True and checkData2 == True and checkData4 == True and checkData3 == True: checkData = True
    
    return checkData, schedule, windowNamesFinal, windowBrepsFinal, alignedDataTree


def checkBlindInputs(zoneNames, windowNames, windowSrfs, isZone):
    #Check if the user has hooked up a distBetwee or numOfShds.
    if _distBetween == [] and _numOfShds == []:
        numOfShd = [1]
        print "No value is connected for number of shades.  The component will be run with one shade per window."
    else:
        numOfShd = _numOfShds
    
    #Check the depths.
    checkData2 = True
    if _depth == []:
        checkData2 = False
        print "You must provide a depth for the shades."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You must provide a depth for the shades.")
    if _numOfShds == [] and _distBetween == []:
        checkData2 = False
        print "You must provide a _numbOfShds or a _distBetween."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You must provide a _numOfShds or a _distBetween.")
    
    #Check if there is a shades material connected and, if not, set a default.
    checkData5 = True
    if shadeMaterial_ == None:
        print "No shades material has been connected. A material will be used that represents thin metal blinds: \n 0.65 solar reflectance, 0 transmittance, 0.9 emittance, 0.25 mm thickness, 221 W/mK conductivity."
        shadeMaterial = ['DEFAULTBLINDSMATERIAL', 0.65, 0, 0.9, 0.00025, 221]
    else:
        try: shadeMaterial = deconstructBlindMaterial(shadeMaterial_)
        except:
            checkData5 = False
            warning = 'Shades material is not a valid shades material from the "Honeybee_EnergyPlus Shade Material" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the inputs that are applicable to all shade options.
    checkData3, schedule, windowNamesFinal, windowBrepsFinal, alignedDataTree = checkAllInputs(zoneNames, windowNames, windowSrfs, isZone)
    
    if checkData2 == True and checkData3 == True and checkData5 == True: checkData = True
    else: checkData = False
    
    
    return checkData, windowNamesFinal, windowBrepsFinal, _depth, alignedDataTree, numOfShd, shadeMaterial, schedule

def checkShadesInputs(zoneNames, windowNames, windowSrfs, isZone):
    #Check the air permeability.
    checkData2 = True
    if airPermeability_ != []:
        for perm in airPermeability_:
            if perm < 0 or perm > 1: checkData2 = False
        if checkData2 == False:
            print "airPermeability_ must be between 0 and 1."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "airPermeability_ must be between 0 and 1.")
    
    #Check if there is a shades material connected and, if not, set a default.
    checkData5 = True
    if shadeMaterial_ == None:
        print "No shade material has been connected. A material will be used that represents cloth drapes: \n 0.3 solar reflectance, 0.05 transmittance, 0.9 emittance, 3 mm thickness, 0.1 W/mK conductivity."
        shadeMaterial = ['DEFAULTSHADESMATERIAL', 0.3, 0.05, 0.9, 0.003, 0.1]
    else:
        try: shadeMaterial = deconstructBlindMaterial(shadeMaterial_)
        except:
            checkData5 = False
            warning = 'Blinds material is not a valid shades material from the "Honeybee_EnergyPlus Shade Material" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the inputs that are applicable to all shade options.
    checkData3, schedule, windowNamesFinal, windowBrepsFinal, alignedDataTree = checkAllInputs(zoneNames, windowNames, windowSrfs, isZone)
    
    if checkData2 == True and checkData3 == True and checkData5 == True: checkData = True
    else: checkData = False
    
    
    return checkData, windowNamesFinal, windowBrepsFinal, alignedDataTree, shadeMaterial, schedule

def checkWindowInputs(zoneNames, windowNames, windowSrfs, isZone, shadeMaterial, hb_EPObjectsAux):
    #Check if there is a shades material connected and, if not, set a default.
    checkData5 = True
    if shadeMaterial == None:
        print "No shade material has been connected. A material will be used that represents typical electrochromic glazing: \n 0.07 SHGC, 0.01 visible transmittance, and a U-Value equal to the current glazing."
        shadeMaterial = 'DEFAULTELECTROCHROMIC'
    else:
        try:
            # if it is just the name of the material make sure it is already defined
            if len(shadeMaterial.split("\n")) == 1:
                # if the material is not in the library add it to the library
                if not hb_EPObjectsAux.isEPConstruction(shadeMaterial):
                    warningMsg = "Can't find " + shadeMaterial + " in EP Construction Library.\n" + \
                                "Add the construction to the library and try again."
                    print warningMsg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
                    checkData5 = False
            else:
                # it is a full string
                if "CONSTRUCTION" in shadeMaterial.upper():
                    added, shadeMaterial = hb_EPObjectsAux.addEPObjectToLib(shadeMaterial, overwrite = True)
                    
                    if not added:
                        msg = name + " is not added to the project library!"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        print msg
                        checkData5 = False
                elif "MATERIAL" in shadeMaterial.upper():
                    msg = "Your connected shadeMaterial_ is just a material and not a full construction. \n For electrochromic glazing, you must assign a full window construction here."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                    checkData5 = False
                else:
                    msg = "Your connected shadeMaterial_ is not a valid construction."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    print msg
                    checkData5 = False
        except:
            checkData5 = False
            warning = 'Connected shadeMaterial_ is not a valid EP window construction.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the inputs that are applicable to all shade options.
    checkData3, schedule, windowNamesFinal, windowBrepsFinal, alignedDataTree = checkAllInputs(zoneNames, windowNames, windowSrfs, isZone)
    
    if checkData3 == True and checkData5 == True: checkData = True
    else: checkData = False
    
    
    return checkData, windowNamesFinal, windowBrepsFinal, alignedDataTree, shadeMaterial, schedule


def deconstructBlindMaterial(material):
    matLines = material.split('\n')
    
    name = matLines[1].split(',')[0]
    reflect = float(matLines[2].split(',')[0])
    transmit = float(matLines[3].split(',')[0])
    emiss = float(matLines[4].split(',')[0])
    thickness = float(matLines[5].split(',')[0])
    conduct = float(matLines[6].split(';')[0])
    
    return [name, reflect, transmit, emiss, thickness, conduct]



#### HERE ARE THE FUNCTIONS THAT CREATE THE SHADE GEOMETRIES.
#Define a function that can get the angle to North of any surface.
def getAngle2North(normalVector):
    if north_ != None:
        northVector = north_
    else:northVector = rc.Geometry.Vector3d.YAxis
    angle =  rc.Geometry.Vector3d.VectorAngle(northVector, normalVector, rc.Geometry.Plane.WorldXY)
    finalAngle = math.degrees(angle)
    return finalAngle

# Define a function that can split up a list of values and assign it to different cardinal directions.
def getValueBasedOnOrientation(valueList, normalVector):
    angles = []
    if valueList == None or len(valueList) == 0: value = None
    if len(valueList) == 1:
        value = valueList[0]
    elif len(valueList) > 1:
        initAngles = rs.frange(0, 360, 360/len(valueList))
        for an in initAngles: angles.append(an-(360/(2*len(valueList))))
        angles.append(360)
        for angleCount in range(len(angles)-1):
            try:
                if angles[angleCount] <= (getAngle2North(normalVector))%360 <= angles[angleCount +1]:
                    targetValue = valueList[angleCount%len(valueList)]
            except:
                targetValue = valueList[0]
        value = targetValue
    return value

def analyzeGlz(glzSrf, distBetween, numOfShds, horOrVertical, lb_visualization, normalVector):
    # Helper function to check if number is near zero
    def helper_is_near_zero(num2chk, eps=1e-6):
        return abs(num2chk) < eps
    
    # find the bounding box
    bbox = glzSrf.GetBoundingBox(True)
    # Add default shading Height and numOfShd
    shadingHeight = 0.
    if numOfShds == None: numOfShd, numOfShds = 0., 0.
    if distBetween == None: distBetween = 0.
    
    if horOrVertical == None:
        horOrVertical = True
    
    if helper_is_near_zero(numOfShds) and helper_is_near_zero(distBetween):
        sortedPlanes = []
    
    elif horOrVertical == True:
        # Horizontal
        #Define a bounding box for use in calculating the number of shades to generate
        minZPt = bbox.Corner(False, True, True)
        minZPt = rc.Geometry.Point3d(minZPt.X, minZPt.Y, minZPt.Z)
        maxZPt = bbox.Corner(False, True, False)
        maxZPt = rc.Geometry.Point3d(maxZPt.X, maxZPt.Y, maxZPt.Z - sc.doc.ModelAbsoluteTolerance)
        minYPt = bbox.Corner(True, True, True)
        minYPt = rc.Geometry.Point3d(minYPt.X, minYPt.Y, minYPt.Z)
        maxYPt = bbox.Corner(True, False, True)
        maxYPt = rc.Geometry.Point3d(maxYPt.X, maxYPt.Y, maxYPt.Z - sc.doc.ModelAbsoluteTolerance)
        
        #glazing hieghts
        glzHeight = minZPt.DistanceTo(maxZPt)
        glzWidth = minYPt.DistanceTo(maxYPt)
        
        # find number of shadings
        if glzHeight == sc.doc.ModelAbsoluteTolerance:
            try:
                numOfShd = int(numOfShds)
                shadingHeight = glzWidth/numOfShd
                shadingRemainder = shadingHeight
            except:
                shadingHeight = distBetween
                shadingRemainder = (((glzWidth/distBetween) - math.floor(glzWidth/distBetween))*distBetween)
                if shadingRemainder == 0:
                    shadingRemainder = shadingHeight
        else:

            try:
                numOfShd = int(numOfShds)
                shadingHeight = glzHeight/numOfShd
                shadingRemainder = shadingHeight
            except:
                shadingHeight = distBetween
                shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
                if shadingRemainder == 0:
                    shadingRemainder = shadingHeight
        
        # find shading base planes
        planeOrigins = []
        planes = []
        try:
            #A surface that is not perfectly horizontal.
            zHeights = rs.frange(minZPt.Z + shadingRemainder, maxZPt.Z + 0.5*sc.doc.ModelAbsoluteTolerance, shadingHeight)
            X, Y, z = minZPt.X, minZPt.Y, minZPt.Z
            try:
                for Z in zHeights:
                    planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(X, Y, Z), rc.Geometry.Vector3d.ZAxis))
            except:
                # single shading
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxZPt), rc.Geometry.Vector3d.ZAxis))
            # sort the planes
            sortedPlanes = sorted(planes, key=lambda a: a.Origin.Z)
        except:
            # Perfectly horizontal surface that requires planes sorted by Y instead of Z.
            yHeights = rs.frange(minYPt.Y + shadingRemainder, maxYPt.Y + 0.5*sc.doc.ModelAbsoluteTolerance, shadingHeight)
            X, y, Z = minYPt.X, minYPt.Y, minYPt.Z
            try:
                for Y in yHeights:
                    planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(X, Y, Z), rc.Geometry.Vector3d.YAxis))
            except:
                # single shading
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxYPt), rc.Geometry.Vector3d.YAxis))
            # sort the planes
            sortedPlanes = sorted(planes, key=lambda a: a.Origin.Y)
    
    elif horOrVertical == False:
        # Vertical
        # Define a vector to be used to generate the planes
        if normalVector.X == 0 and normalVector.Y == 0:
            # Perfectly horizontal surface that requires planes sorted by X instead of Z.
            minXPt = bbox.Corner(True, True, True)
            minXPt = rc.Geometry.Point3d(minXPt.X, minXPt.Y, minXPt.Z)
            maxXPt = bbox.Corner(False, True, True)
            maxXPt = rc.Geometry.Point3d(maxXPt.X, maxXPt.Y, maxXPt.Z - sc.doc.ModelAbsoluteTolerance)
            glzWidth = minXPt.DistanceTo(maxXPt)
            
            # Find number of shadings 
            try:
                numOfShd = int(numOfShds)
                shadingHeight = glzWidth/numOfShd
                shadingRemainder = shadingHeight
            except:
                shadingHeight = distBetween
                shadingRemainder = (((glzWidth/distBetween) - math.floor(glzWidth/distBetween))*distBetween)
                if shadingRemainder == 0:
                    shadingRemainder = shadingHeight
            
            
            planeOrigins = []
            planes = []
            
            xHeights = rs.frange(minXPt.X + shadingRemainder, maxXPt.X + 0.5*sc.doc.ModelAbsoluteTolerance, shadingHeight)
            x, Y, Z = minXPt.X, minXPt.Y, minXPt.Z
            try:
                for X in xHeights:
                    planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(X, Y, Z), rc.Geometry.Vector3d.XAxis))
            except:
                # single shading
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxXPt), rc.Geometry.Vector3d.XAxis))
            # sort the planes
            sortedPlanes = sorted(planes, key=lambda a: a.Origin.X)
        else:
            planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
            planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
            
            #Define a bounding box for use in calculating the number of shades to generate
            minXYPt = bbox.Corner(True, True, True)
            minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
            maxXYPt = bbox.Corner(False, False, True)
            maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
            
            #Test to be sure that the values are parallel to the correct vector.
            testVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
            if testVec.IsParallelTo(planeVec) == 0:
                minXYPt = bbox.Corner(False, True, True)
                minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
                maxXYPt = bbox.Corner(True, False, True)
                maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
            
            #Adjust the points to ensure the creation of the correct number of shades starting from the northernmost side of the window.
            tolVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
            tolVec.Unitize()
            tolVec = rc.Geometry.Vector3d.Multiply(sc.doc.ModelAbsoluteTolerance*2, tolVec)
            
            if tolVec.X > 0 and  tolVec.Y > 0:
                tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
                norOrient = False
            if tolVec.X < 0 and  tolVec.Y > 0:
                tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
                norOrient = False
            if tolVec.X < 0 and  tolVec.Y < 0:
                tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
                norOrient = True
            else:
                tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
                norOrient = True
            
            maxXYPt = rc.Geometry.Point3d.Subtract(maxXYPt, tolVec)
            minXYPt = rc.Geometry.Point3d.Subtract(minXYPt, tolVec)
            
            #glazing distance
            glzHeight = minXYPt.DistanceTo(maxXYPt)
           
            
            # find number of shadings
            try:
                numOfShd = int(numOfShds)
                shadingHeight = glzHeight/numOfShd
                shadingRemainder = shadingHeight
            except:
                shadingHeight = distBetween
                shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
                if shadingRemainder == 0:
                    shadingRemainder = shadingHeight
            
            
            # find shading base planes
            planeOrigins = []
            planes = []
            
            pointCurve = rc.Geometry.Curve.CreateControlPointCurve([maxXYPt, minXYPt])
            divisionParams = pointCurve.DivideByLength(shadingHeight, True)
            
            # If number of shades = 0 or the distance between fins is the window length divisionParams == None
            if divisionParams == None:
                divisionParams = [0.0]

            divisionPoints = []
            for param in divisionParams:
                divisionPoints.append(pointCurve.PointAt(param))
            
            planePoints = divisionPoints
            try:
                for point in planePoints:
                    planes.append(rc.Geometry.Plane(point, planeVec))
            except:
                # single shading
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(minXYPt), planeVec))
            sortedPlanes = planes
    
    
    return sortedPlanes, shadingHeight


def makeBlind(_glzSrf, depth, numShds, distBtwn):
    rotationAngle_ = 0
    # import the classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_mesh = sc.sticky["ladybug_Mesh"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    # find the normal of the surface in the center
    # note2developer: there might be cases that the surface is not planar and
    # the normal is changing from point to point, then I should sample the test surface
    # and test the normal direction for more point
    baseSrfCenPt = rc.Geometry.AreaMassProperties.Compute(_glzSrf).Centroid
    # sometimes the center point is not located on the surface
    baseSrfCenPt = _glzSrf.ClosestPoint(baseSrfCenPt)
    
    bool, centerPtU, centerPtV = _glzSrf.Faces[0].ClosestPoint(baseSrfCenPt)
    if bool:
        normalVector = _glzSrf.Faces[0].NormalAt(centerPtU, centerPtV)
        #return rc.Geometry.Plane(baseSrfCenPt,normalVector)
    else:
        print "Couldn't find the normal of the shading surface." + \
              "\nRebuild the surface and try again!"
        return -1
    
    shadingSurfaces =[]
    
    # If multiple shading depths are given, use it to split up the glazing by cardinal direction and assign different depths to different directions.
    depth = getValueBasedOnOrientation(depth, normalVector)
    
    # If multiple number of shade inputs are given, use it to split up the glazing by cardinal direction and assign different numbers of shades to different directions.
    numShds = getValueBasedOnOrientation(numShds, normalVector)
    
    # If multiple distances between shade inputs are given, use it to split up the glazing by cardinal direction and assign different distances of shades to different directions.
    distBtwn = getValueBasedOnOrientation(distBtwn, normalVector)
    
    # If multiple horizontal or vertical inputs are given, use it to split up the glazing by cardinal direction and assign different horizontal or vertical to different directions.
    horOrVertical = getValueBasedOnOrientation(horOrVertical_, normalVector)
    
    # If multiple shdAngle_ inputs are given, use it to split up the glazing by cardinal direction and assign different shdAngle_ to different directions.
    shdAngle = getValueBasedOnOrientation(shdAngle_, normalVector)
    
    #If multiple interiorOrExter_ inputs are given, use it to split up the glazing by cardinal direction and assign different interiorOrExterior_ to different directions.
    interiorOrExter = getValueBasedOnOrientation(interiorOrExter_, normalVector)
    
    #If multiple distToGlass_ inputs are given, use it to split up the glazing by cardinal direction and assign different distToGlass_ to different directions.
    distToGlass = getValueBasedOnOrientation(distToGlass_, normalVector)
    
    # generate the planes
    planes, shadingHeight = analyzeGlz(_glzSrf, distBtwn, numShds, horOrVertical, lb_visualization, normalVector)
    
    # find the intersection crvs as the base for shadings
    intCrvs =[]
    for plane in planes:
        try: intCrvs.append(rc.Geometry.Brep.CreateContourCurves(_glzSrf, plane)[0])
        except: pass
    
    if normalVector != rc.Geometry.Vector3d.ZAxis: normalVectorPerp = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
    else: normalVectorPerp = rc.Geometry.Vector3d(0, 0, normalVector.Z)
    angleFromNorm = math.degrees(rc.Geometry.Vector3d.VectorAngle(normalVectorPerp, normalVector))
    if normalVector.Z < 0: angleFromNorm = angleFromNorm*(-1)
    
    #If the user has set the shades to generate on the interior, flip the normal vector.
    if interiorOrExter == True: normalVectorPerp.Reverse()
    else: interiorOrExter = False
    
    normalVecOrignal = rc.Geometry.Vector3d(normalVectorPerp)
    
    #If a shdAngle is provided, use it to rotate the planes by that angle
    if shdAngle != None:
        if normalVectorPerp.X == 0 and normalVectorPerp.Y == 0:
            planeVec = rc.Geometry.Vector3d.ZAxis
            if horOrVertical == True or horOrVertical == None:
                horOrVertical = True
                planeVec.Rotate(1.570796, rc.Geometry.Vector3d.YAxis)
                normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
            elif horOrVertical == False:
                planeVec.Rotate(1.570796, rc.Geometry.Vector3d.XAxis)
                normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
        else:
            if horOrVertical == True or horOrVertical == None:
                horOrVertical = True
                planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
                planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
                normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
            elif horOrVertical == False:
                planeVec = rc.Geometry.Vector3d.ZAxis
                try:
                    if getAngle2North(normalVectorPerp) < 180:
                        normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
                    else: normalVectorPerp.Rotate((shdAngle*-0.01745329), planeVec)
                except:
                    normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
    else:
        shdAngle = 0
        if horOrVertical == None: horOrVertical = True
    
    #Make EP versions of some of the outputs.
    EPshdAngleInint = angleFromNorm+shdAngle
    if EPshdAngleInint >= 0: EPshdAngle = 90 - EPshdAngleInint
    else: EPshdAngle = 90 + (EPshdAngleInint)*-1
    if EPshdAngle > 180 or EPshdAngle < 0:
        warning = "The input shdAngle_ value will cause EnergyPlus to crash."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if horOrVertical == True: EPSlatOrient = 'Horizontal'
    else: EPSlatOrient = 'Vertical'
    if interiorOrExter == True: EPinteriorOrExter = 'InteriorBlind'
    else: EPinteriorOrExter = 'ExteriorBlind'
    
    #Generate the shade curves based on the planes and extrusion vectors
    if intCrvs !=[]:
        for c in intCrvs:
            try:
                shdSrf = rc.Geometry.Surface.CreateExtrusion(c, float(depth) * normalVectorPerp).ToBrep()
                shadingSurfaces.append(shdSrf)
            except: pass
    
    #If the user has specified a distance to move the shades, move them along the normal vector.
    if distToGlass != None: pass
    else: distToGlass = 0.01
    
    transVec = normalVecOrignal
    transVec.Unitize()
    finalTransVec = rc.Geometry.Vector3d.Multiply(distToGlass, transVec)
    shadesTransform =  rc.Geometry.Transform.Translation(finalTransVec)
    
    for shdSrf in shadingSurfaces:
        shdSrf.Transform(shadesTransform)
    
    # Check the EPshdAngle.
    if EPshdAngle == 0.0: EPshdAngle = 1.0
    elif EPshdAngle == 180.0: EPshdAngle = 179.0
    
    #Get the EnergyPlus distance to glass.
    assignEPCheckInit = True
    EPDistToGlass = distToGlass + (depth)*(0.5)*math.sin(math.radians(EPshdAngle))
  
    if EPDistToGlass < (depth)*(0.5): EPDistToGlass = (depth)*(0.5)
    if EPDistToGlass < 0.01: EPDistToGlass = 0.01
    elif EPDistToGlass > 1:
        assignEPCheckInit = False
        warning = "The input distToGlass_ value is so large that it will cause EnergyPlus to crash."
        print warning
    
    #Check the depth and the shadingHeight to see if E+ will crash.
    if depth > 1:
        assignEPCheckInit = False
        warning = "NHBObjWShades will not be generated.  shadeBreps will still be produced and you can account for these shades using a 'Honeybee_EP Context Surfaces' component."
        print warning
    if shadingHeight > 1:
        assignEPCheckInit = False
        warning = "HBObjWShades will not be generated.  shadeBreps will still be produced and you can account for these shades using a 'Honeybee_EP Context Surfaces' component."
        print warning
    
    
    return shadingSurfaces, EPSlatOrient, depth, shadingHeight, EPshdAngle, EPDistToGlass, EPinteriorOrExter, assignEPCheckInit

def makeShade(_glzSrf):
    rotationAngle_ = 0
    # import the classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_mesh = sc.sticky["ladybug_Mesh"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    # find the normal of the surface in the center
    # note2developer: there might be cases that the surface is not planar and
    # the normal is changing from point to point, then I should sample the test surface
    # and test the normal direction for more point
    baseSrfCenPt = rc.Geometry.AreaMassProperties.Compute(_glzSrf).Centroid
    # sometimes the center point is not located on the surface
    baseSrfCenPt = _glzSrf.ClosestPoint(baseSrfCenPt)
    
    bool, centerPtU, centerPtV = _glzSrf.Faces[0].ClosestPoint(baseSrfCenPt)
    if bool:
        normalVector = _glzSrf.Faces[0].NormalAt(centerPtU, centerPtV)
        #return rc.Geometry.Plane(baseSrfCenPt,normalVector)
    else:
        print "Couldn't find the normal of the shading surface." + \
              "\nRebuild the surface and try again!"
        return -1
    
    shadingSurfaces =[]
    
    # If multiple airPermeability_ inputs are given, use it to split up the glazing by cardinal direction and assign different airPermeability_ to different directions.
    airPermea = getValueBasedOnOrientation(airPermeability_, normalVector)
    
    #If multiple interiorOrExter_ inputs are given, use it to split up the glazing by cardinal direction and assign different interiorOrExterior_ to different directions.
    interiorOrExter = getValueBasedOnOrientation(interiorOrExter_, normalVector)
    
    #If multiple distToGlass_ inputs are given, use it to split up the glazing by cardinal direction and assign different distToGlass_ to different directions.
    try:
        distToGlass = float(getValueBasedOnOrientation(distToGlass_, normalVector))
    except:
        distToGlass = None
    if distToGlass == None: distToGlass = 0.2
    
    #Generate the shade geometry based on the offset distance.
    if interiorOrExter == True: distToGlass = -distToGlass
    try:
        shdSrf = rc.Geometry.Surface.Offset(_glzSrf.Faces[0], distToGlass, sc.doc.ModelAbsoluteTolerance)
        shadingSurfaces.append(shdSrf)
    except: pass
    
    
    #Make EP versions of some of the outputs.
    if interiorOrExter == True: EPinteriorOrExter = 'InteriorShade'
    else: EPinteriorOrExter = 'ExteriorShade'
    
    #Get the EnergyPlus distance to glass.
    assignEPCheckInit = True
    if distToGlass < 0 : EPDistToGlass = -distToGlass
    else: EPDistToGlass = distToGlass
    if EPDistToGlass < 0.01: EPDistToGlass = 0.01
    elif EPDistToGlass > 1:
        assignEPCheckInit = False
        warning = "The input distToGlass_ value is so large that it will cause EnergyPlus to crash."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return shadingSurfaces, airPermea, EPDistToGlass, EPinteriorOrExter, assignEPCheckInit


#### HERE ARE THE FUNCTIONS THAT CREATE THE ENERGYPLUS OBJECTS.
shdCntrlDict = {
0: 'OnIfScheduleAllows',
1: 'OnIfHighSolarOnWindow',
2: 'OnIfHighHorizontalSolar',
3: 'OnIfHighOutdoorAirTemperature',
4: 'OnIfHighZoneAirTemperature',
5: 'OnIfHighZoneCooling',
6: 'OnNightIfLowOutdoorTempAndOffDay',
7: 'OnNightIfLowInsideTempAndOffDay',
8: 'OnNightIfHeatingAndOffDay',
9: 'OnNightIfLowOutdoorTempAndOnDayIfCooling',
10: 'OnNightIfHeatingAndOnDayIfCooling',
11: 'OffNightAndOnDayIfCoolingAndHighSolarOnWindow',
12: 'OnNightAndOnDayIfCoolingAndHighSolarOnWindow',
13: 'OnIfHighOutdoorAirTempAndHighSolarOnWindow',
14: 'OnIfHighOutdoorAirTempAndHighHorizontalSolar',
15: 'OnIfHighGlare',
16: 'MeetDaylightIlluminanceSetpoint'
}


def createEPBlindMat(shadeMaterial, EPSlatOrient, depth, shadingHeight, EPshdAngle, distToGlass, name):
    EPBlindMat = "WindowMaterial:Blind,\n" + \
        '\t' + name + ',           !- Name\n' + \
        '\t' + EPSlatOrient + ',              !- Slat Orientation\n' + \
        '\t' + str(depth) + ',                     !- Slat Width {m}\n' + \
        '\t' + str(shadingHeight) +',                     !- Slat Separation {m}\n' + \
        '\t' + str(shadeMaterial[4]) + ',                 !- Slat Thickness {m}\n' + \
        '\t' + str(EPshdAngle) + ',                      !- Slat Angle {deg}\n' + \
        '\t' + str(shadeMaterial[5]) + ',                     !- Slat Conductivity {W/m-K}\n' + \
        '\t' + str(shadeMaterial[2]) + ',                        !- Slat Beam Solar Transmittance\n' + \
        '\t' + str(shadeMaterial[1]) + ',                    !- Front Side Slat Beam Solar Reflectance\n' + \
        '\t' + str(shadeMaterial[1]) + ',                    !- Back Side Slat Beam Solar Reflectance\n' + \
        '\t' + str(shadeMaterial[2]) + ',                        !- Slat Diffuse Solar Transmittance\n' + \
        '\t' + str(shadeMaterial[1]) + ',                    !- Front Side Slat Diffuse Solar Reflectance\n' + \
        '\t' + str(shadeMaterial[1]) + ',                    !- Back Side Slat Diffuse Solar Reflectance\n' + \
        '\t' + str(shadeMaterial[2]) + ',                       !- Slat Beam Visible Transmittance\n' + \
        '\t' + ',                        !- Front Side Slat Beam Visible Reflectance\n' + \
        '\t' + ',                        !- Back Side Slat Beam Visible Reflectance\n' + \
        '\t' + str(shadeMaterial[2]) + ',                        !- Slat Diffuse Visible Transmittance\n' + \
        '\t' + ',                        !- Front Side Slat Diffuse Visible Reflectance\n' + \
        '\t' + ',                        !- Back Side Slat Diffuse Visible Reflectance\n' + \
        '\t' + ',                        !- Slat Infrared Hemispherical Transmittance\n' + \
        '\t' + str(shadeMaterial[3]) + ',                     !- Front Side Slat Infrared Hemispherical Emissivity\n' + \
        '\t' + str(shadeMaterial[3]) + ',                     !- Back Side Slat Infrared Hemispherical Emissivity\n' + \
        '\t' + str(distToGlass) + ',                    !- Blind to Glass Distance {m}\n' + \
        '\t' + '1.0,                     !- Blind Top Opening Multiplier\n' + \
        '\t' + '1.0,                        !- Blind Bottom Opening Multiplier\n' + \
        '\t' + '1.0,                     !- Blind Left Side Opening Multiplier\n' + \
        '\t' + '1.0,                     !- Blind Right Side Opening Multiplier\n' + \
        '\t' + ',                        !- Minimum Slat Angle {deg}\n' + \
        '\t' + '180;                     !- Maximum Slat Angle {deg}\n'
    
    return EPBlindMat

def createEPShadeMat(shadeMaterial, airPerm, distToGlass, name):
    if airPerm == None: airPerm = 0
    #If air permeability is non-zero, determine infrared transmittance from it.
    infraredTrans = airPerm
    emissivity = (1-airPerm)*shadeMaterial[3]
    
    EPShadeMat = "WindowMaterial:Shade,\n" + \
        '\t' + name + ",                        !- Name\n" + \
        '\t' + str(shadeMaterial[2]) + ",                        !- Solar Transmittance {dimensionless}\n" + \
        '\t' + str(shadeMaterial[1]) + ",                        !- Solar Reflectance {dimensionless}\n" + \
        '\t' + str(shadeMaterial[2]) + ",                        !- Visible Transmittance {dimensionless}\n" + \
        '\t' + str(shadeMaterial[1]) + ",                        !- Visible Reflectance {dimensionless}\n" + \
        '\t' + str(emissivity) + ",                        !- Infrared Hemispherical Emissivity {dimensionless}\n" + \
        '\t' + str(infraredTrans) + ",                        !- Infrared Transmittance {dimensionless}\n" + \
        '\t' + str(shadeMaterial[4]) + ",                        !- Thickness {m}\n" + \
        '\t' + str(shadeMaterial[5]) + ",                        !- Conductivity {W/m-K}\n" + \
        '\t' + str(distToGlass) + ",                    !- Shade to Glass Distance {m}\n" + \
        '\t' + "1.0,                     !- Top Opening Multiplier\n" + \
        '\t' + "1.0,                     !- Bottom Opening Multiplier\n" + \
        '\t' + "1.0,                     !- Left-Side Opening Multiplier\n" + \
        '\t' + "1.0,                     !- Right-Side Opening Multiplier\n" + \
        '\t' + str(airPerm) + ";                        !- Airflow Permeability {dimensionless}\n"
    
    return EPShadeMat

def createEPWindowMat(shadeMaterial, name, winUValue):
    
    EPWindowMat ='WindowMaterial:SimpleGlazingSystem,\n' + \
        '\t' + name + ',    !Name\n' + \
        '\t' + str(winUValue) + ',    !U Value\n' + \
        '\t' + '0.07' + ',    !Solar Heat Gain Coeff\n' + \
        '\t' + '0.01' + ';    !Visible Transmittance\n' + \
        '\n'
    
    EPWindowConstr = 'Construction,\n' + \
        '\t' + name + ',    !- Name\n' + \
        '\t' + name + ';    !- Layer 1\n'+ \
        '\n'
    
    
    return EPWindowMat, EPWindowConstr

def createEPBlindControlName(shadeMaterial, schedule, EPinteriorOrExter, winConstrName = None):
    #Check if we are working with swtichable glazing, in which case, we need to specify the window construction instead of a shadeMaterial.
    shadeConstr = ''
    shadeName = shadeMaterial
    if shadeType_ == 2:
        shadeConstr = copy.copy(winConstrName)
        shadeName = ''
    
    #Check the schedule
    if schedule == 'ALWAYS ON' and shadeCntrlType_ != 0:
        schedCntrlType = 'AlwaysOn'
        schedCntrl = 'No'
        schedName = ''
    elif schedule.upper().endswith('CSV'):
        schedName = schedule
        schedCntrlType = 'OnIfScheduleAllows'
        schedCntrl = 'Yes'
    else:
        schedName = schedule
        schedCntrlType = 'OnIfScheduleAllows'
        schedCntrl = 'Yes'
    
    #Check the setpoint and shading control.
    setPoint = ''
    setPoint2 = ''
    try:
        schedCntrlType = shdCntrlDict[shadeCntrlType_]
    except:
        pass
    
    if shadeCntrlType_ != 0 and shadeCntrlType_ != None and shadeCntrlType_ <= 14:
        setPoint = str(float(shadeSetpoint_[0]))
        if shadeCntrlType_ >= 13: setPoint2 = str(float(shadeSetpoint_[1]))
    
    EPBlindControlName = 'ShadeCntrl'+ '-' + EPinteriorOrExter+ '-' + shadeConstr+ '-' + schedCntrlType+ '-' +  schedName + '-' + setPoint+ '-' + schedCntrl+ '-' + shadeName+ '-' + setPoint2
    
    return EPBlindControlName, EPinteriorOrExter, shadeConstr, schedCntrlType, schedName, setPoint, schedCntrl, shadeName, setPoint2

def createEPBlindCntrlStr(blindCntrlName, EPinteriorOrExter, shadeConstr, schedCntrlType, schedName, setPoint, schedCntrl, shadeName, setPoint2, glareCntrl = 'No'):
    EPBlindControl = 'WindowProperty:ShadingControl,\n' + \
        '\t' + blindCntrlName +',            !- Name\n' + \
        '\t' + EPinteriorOrExter + ',           !- Shading Type\n' + \
        '\t' + shadeConstr + ',                        !- Construction with Shading Name\n' + \
        '\t' + schedCntrlType + ',                !- Shading Control Type\n' + \
        '\t' + schedName + ',                        !- Schedule Name\n' + \
        '\t' + setPoint+ ',                        !- Setpoint {W/m2, W or deg C}\n' + \
        '\t' + schedCntrl + ',                      !- Shading Control Is Scheduled\n' + \
        '\t' + glareCntrl + ',                      !- Glare Control Is Active\n' + \
        '\t' + shadeName + ',           !- Shading Device Material Name\n' + \
        '\t' + 'FixedSlatAngle,          !- Type of Slat Angle Control for Blinds\n'
        
    
    if setPoint2 == '':
        EPBlindControl = EPBlindControl + '\t' + ';                        !- Slat Angle Schedule Name\n'
    else:
        EPBlindControl = EPBlindControl + '\t' + ',                        !- Slat Angle Schedule Name\n'
        EPBlindControl = EPBlindControl + '\t' + setPoint2 + ';                      !- Setpoint 2 {W/m2 or deg C}\n'
    
    return EPBlindControl


#### HERE IS THE MAIN FUNCTION.
def main():
    if _HBObjects != [] and sc.sticky.has_key('honeybee_release') == True and sc.sticky.has_key('ladybug_release') == True:
        #Import the classes
        hb_EPZone = sc.sticky["honeybee_EPZone"]
        hb_EPSrf = sc.sticky["honeybee_EPSurface"]
        hb_EPFenSurface = sc.sticky["honeybee_EPFenSurface"]
        hb_hive = sc.sticky["honeybee_Hive"]()
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        EPWindowMaterials = sc.sticky ["honeybee_windowMaterialLib"].keys()
        EPWindowProperties = sc.sticky["honeybee_WindowPropLib"].keys()
        
        #Make the lists that will be filled up
        zoneNames = []
        windowNames = []
        windowSrfs = []
        windowObjects = []
        isZoneList = []
        assignEPCheck = True
        checkData = False
        HBObjWShades = []
        EPSlatOrientList = []
        depthList = []
        shadingHeightList = []
        EPshdAngleList = []
        distToGlassList = []
        EPinteriorOrExterList = []
        shadings = []
        compShadeMats = []
        compShadeMatsStr = []
        compShadeCntrls = []
        compShadeCntrlsStr = []
        ModifiedHBZones = []
        blindMatNames = []
        
        #Call the objects from the hive.
        HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBObjects)
        
        #Find out what the object is and make sure that we can run it through this component's functions.
        for object in HBZoneObjects:
            if object.objectType == "HBZone":
                isZoneList.append(1)
                zoneNames.append(object.name)
                winBreps = []
                winNames = []
                for srf in object.surfaces:
                    if srf.hasChild:
                        if srf.BC == 'OUTDOORS' or srf.BC == 'Outdoors':
                            if srf.isPlanar == True:
                                for childSrf in srf.childSrfs:
                                    windowObjects.append(childSrf)
                                    winNames.append(childSrf.name)
                                    winBreps.append(childSrf.geometry)
                            else: print "One surface with a window is not planar. EenergyPlus shades will not be assigned to this window."
                        else: print "One surface with a window does not have an outdoor boundary condition. EenergyPlus shades will not be assigned to this window."
                windowNames.append(winNames)
                windowSrfs.append(winBreps)
            elif object.objectType == "HBSurface":
                isZoneList.append(0)
                warning = "Note that, when using this component for individual surfaces, you should make sure that the direction of the surface is facing the outdoors in order to be sure that your shades are previewing correctly."
                print warning
                
                if not hasattr(object, 'type'):
                    # find the type based on 
                    object.type = object.getTypeByNormalAngle()
                if not hasattr(object, 'angle2North'):
                    # find the type based on
                    object.getAngle2North()
                if not hasattr(object, "BC"):
                    object.BC = 'OUTDOORS'
                
                if object.hasChild:
                    if object.BC != 'OUTDOORS' and object.BC != 'Outdoors':
                        assignEPCheck = False
                        warning = "The boundary condition of the input object must be outdoors.  E+ cannot create shades for indoor windows."
                        print warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                    elif object.isPlanar == False:
                        assignEPCheck = False
                        warning = "The surface must not be curved.  With the way that honeybee meshes curved surfaces for E+, the program would just freak out."
                        print warning
                        ghenv.Component.AddRuntimeMessage(w, warning)
                    else:
                        for childSrf in object.childSrfs:
                            windowObjects.append(childSrf)
                            windowNames.append([childSrf.name])
                            windowSrfs.append([childSrf.geometry])
        
        #Make sure that all HBObjects are of the same type.
        checkSameType = True
        if sum(isZoneList) == len(_HBObjects): isZone = True
        elif sum(isZoneList) == 0: isZone = False
        else:
            checkSameType = False
            warning = "This component currently only supports inputs that are all HBZones or all HBSrfs but not both. For now, just grab another component for each of these inputs."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            isZone = False
        
        if shadeType_ == 0 or shadeType_ == None:
            #Check the inputs and make sure that we have everything that we need to generate the shades.  Set defaults on things that are not connected.
            if checkSameType == True:
                checkData, windowNames, windowSrfsInit, depths, alignedDataTree, numOfShd, shadeMaterial, schedule = checkBlindInputs(zoneNames, windowNames, windowSrfs, isZone)
            else: checkData == False
            
            #Generate the shades.
            if checkData == True:
                for window in windowSrfsInit:
                    shadeBreps, EPSlatOrient, depth, shadingHeight, EPshdAngle, distToGlass, EPinteriorOrExter, assignEPCheckInit = makeBlind(window, depths, numOfShd, _distBetween)
                    shadings.append(shadeBreps)
                    EPSlatOrientList.append(EPSlatOrient)
                    depthList.append(depth)
                    shadingHeightList.append(shadingHeight)
                    EPshdAngleList.append(EPshdAngle)
                    distToGlassList.append(distToGlass)
                    EPinteriorOrExterList.append(EPinteriorOrExter)
                    if assignEPCheckInit == False: assignEPCheck = False
                
                #Create the EnergyPlus shades material and assign it to the windows with shades.
                if assignEPCheck == True and writeEPObjs_ == True:
                    for count, windowObj in enumerate(windowObjects):
                        blindMatName = shadeMaterial[0] + '-' + str(EPSlatOrientList[count]) + '-' + str(depthList[count]) + '-' + str(shadingHeightList[count]) + '-' + str(EPshdAngleList[count])+ '-' + str(distToGlassList[count])
                        blindMatNames.append(blindMatName)
                        if blindMatName.upper() not in compShadeMats:
                            blindMatStr = createEPBlindMat(shadeMaterial, EPSlatOrientList[count], depthList[count], shadingHeightList[count], EPshdAngleList[count], distToGlassList[count], blindMatName)
                            added, name = hb_EPObjectsAux.addEPObjectToLib(blindMatStr, True)
                            compShadeMats.append(blindMatName.upper())
                            compShadeMatsStr.append(blindMatStr)
        
        elif shadeType_ == 1:
            #Check the inputs and make sure that we have everything that we need to generate the shades.  Set defaults on things that are not connected.
            if checkSameType == True:
                checkData, windowNames, windowSrfsInit, alignedDataTree, shadeMaterial, schedule = checkShadesInputs(zoneNames, windowNames, windowSrfs, isZone)
            else: checkData == False
            
            #Generate the shades.
            if checkData == True:
                for window in windowSrfsInit:
                    shadeBreps, airPerm, distToGlass, EPinteriorOrExter, assignEPCheckInit = makeShade(window)
                    shadings.append(shadeBreps)
                    depthList.append(airPerm)
                    distToGlassList.append(distToGlass)
                    EPinteriorOrExterList.append(EPinteriorOrExter)
                    if assignEPCheckInit == False: assignEPCheck = False
                
                #Create the EnergyPlus shades material and assign it to the windows with shades.
                if assignEPCheck == True and writeEPObjs_ == True:
                    for count, windowObj in enumerate(windowObjects):
                        blindMatName = shadeMaterial[0] + '-' + str(depthList[count]) + '-' + str(distToGlassList[count])
                        blindMatNames.append(blindMatName)
                        if blindMatName.upper() not in compShadeMats:
                            blindMatStr = createEPShadeMat(shadeMaterial, depthList[count], distToGlassList[count], blindMatName)
                            added, name = hb_EPObjectsAux.addEPObjectToLib(blindMatStr, True)
                            compShadeMats.append(blindMatName.upper())
                            compShadeMatsStr.append(blindMatStr)
        
        elif shadeType_ == 2:
            #Check the inputs and make sure that we have everything that we need to generate the shades.  Set defaults on things that are not connected.
            if checkSameType == True:
                checkData, windowNames, windowSrfsInit, alignedDataTree, windowMaterial, schedule = checkWindowInputs(zoneNames, windowNames, windowSrfs, isZone, shadeMaterial_, hb_EPObjectsAux)
            else: checkData == False
            
            if checkData == True and writeEPObjs_ == True:
                #Create the EnergyPlus shades material and assign it to the windows with shades.
                for count, windowObj in enumerate(windowObjects):
                    if windowMaterial == 'DEFAULTELECTROCHROMIC':
                        materials, comments, winUval, UValue_IP = hb_EPMaterialAUX.decomposeEPCnstr(windowObj.EPConstruction.upper())
                        blindMatName = windowMaterial + '-' + str(round(winUval*100000)/100000)
                    else:
                        blindMatName = windowMaterial
                    
                    blindMatNames.append('')
                    if blindMatName.upper() not in compShadeMats:
                        if windowMaterial == 'DEFAULTELECTROCHROMIC':
                            blindMatStr, blindMatConstr = createEPWindowMat(windowMaterial, blindMatName, winUval)
                            added, name = hb_EPObjectsAux.addEPObjectToLib(blindMatStr, True)
                            added, name = hb_EPObjectsAux.addEPObjectToLib(blindMatConstr, True)
                            compShadeMatsStr.append(blindMatConstr)
                        else:
                            materials, comments, winUval, UValue_IP = hb_EPMaterialAUX.decomposeEPCnstr(windowMaterial.upper())
                            blindMatStr = 'Construction,\n'
                            for mcount, mat in enumerate(materials):
                                blindMatStr = blindMatStr + mat + comments[mcount] +'\n'
                        compShadeMats.append(blindMatName.upper())
                        compShadeMatsStr.append(blindMatStr)
        
        if checkData == True and assignEPCheck == True and writeEPObjs_ == True:
            for count, windowObj in enumerate(windowObjects):
                if shadeType_ == 2:
                    blindCntrlName, EPinteriorOrExter, shadeConstr, schedCntrlType, schedName, setPoint, schedCntrl, shadeName, setPoint2 = createEPBlindControlName(windowMaterial, schedule, 'SwitchableGlazing', blindMatName)
                else:
                    blindCntrlName, EPinteriorOrExter, shadeConstr, schedCntrlType, schedName, setPoint, schedCntrl, shadeName, setPoint2 = createEPBlindControlName(blindMatNames[count], schedule, EPinteriorOrExterList[count])
                if blindCntrlName.upper() not in compShadeCntrls:
                    glrCntrl = 'No'
                    if schedCntrlType == 'OnIfHighGlare' or schedCntrlType == 'MeetDaylightIlluminanceSetpoint':
                        if len(shadeSetpoint_) == 2:
                            glrCntrl = 'Yes'
                    blindCntrlStr = createEPBlindCntrlStr(blindCntrlName, EPinteriorOrExter, shadeConstr, schedCntrlType, schedName, setPoint, schedCntrl, shadeName, setPoint2, glrCntrl)
                    
                    added, name = hb_EPObjectsAux.addEPObjectToLib(blindCntrlStr, True)
                    compShadeCntrls.append(blindCntrlName.upper())
                    compShadeCntrlsStr.append(blindCntrlStr)
                
                windowObj.shadingControlName.append(blindCntrlName)
                windowObj.shadingSchName.append(schedule)
                windowObj.shadeMaterialName.append(blindMatName)
            
            # If glare control or illuminance control is specified, change the zone's daylighting control.
            if schedCntrlType == 'OnIfHighGlare' or schedCntrlType == 'MeetDaylightIlluminanceSetpoint':
                for object in HBZoneObjects:
                    if object.objectType == "HBZone":
                        object.daylightCntrlFract = 1
                        if len(shadeSetpoint_) == 2:
                            object.GlareDiscomIndex = float(shadeSetpoint_[0])
                            object.glareView = abs(getAngle2North(shadeSetpoint_[-1]) - 360)
                        if schedCntrlType == 'MeetDaylightIlluminanceSetpoint':
                            object.illumSetPt = 300
                    else:
                        illumSetPt = 100000
                        glareDiscomIndex = 22
                        glareView = 0
                        if len(shadeSetpoint_) == 2:
                            glareDiscomIndex = float(shadeSetpoint_[0])
                            glareView = abs(getAngle2North(shadeSetpoint_[-1]) - 360)
                        if schedCntrlType == 'MeetDaylightIlluminanceSetpoint':
                            illumSetPt = 300
                        object.shdCntrlZoneInstructs = [illumSetPt,glareDiscomIndex,glareView]
            
            ModifiedHBZones  = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component)
        
        if checkData == True:
            return checkData, windowSrfsInit, shadings, alignedDataTree, ModifiedHBZones, compShadeMats, compShadeMatsStr, compShadeCntrlsStr
        else:
            return -1
    else:
        print "You should first let both Honeybee and Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Honeybee and Ladybug fly...")
        return -1


#Read the shadeType input to determine the component inputs.
if shadeType_ != None:
    setComponentInputs(shadeType_)
else:
    restoreComponentInputs()


#Run the main functions.
checkData = False
if _HBObjects != [] and _runIt == True:
    result = main()
    if result != -1 and result != None:
        checkData, windowSrfsInit, shadings, alignedDataTree, HBObjWShades, shadeMatName, shadeMatIDFStr, shadeCntrlIDFStr = result


#Unpack the data trees.
if checkData == True:
    windowBreps = DataTree[Object]()
    shadeBreps = DataTree[Object]()
    zoneData1Tree = DataTree[Object]()
    zoneData2Tree = DataTree[Object]()
    zoneData3Tree = DataTree[Object]()
    
    for count, brep in enumerate(windowSrfsInit):
        windowBreps.Add(brep, GH_Path(count))
    
    for count, brepList in enumerate(shadings):
        for brep in brepList: shadeBreps.Add(brep, GH_Path(count))
    
    for treeCount, finalTree in enumerate(alignedDataTree):
        if treeCount == 0:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData1Tree.Add(twig, GH_Path(bCount))
        elif treeCount == 1:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData2Tree.Add(twig, GH_Path(bCount))
        elif treeCount == 2:
            for bCount, branch in enumerate(finalTree):
                for twig in branch: zoneData3Tree.Add(twig, GH_Path(bCount))

ghenv.Component.Params.Output[2].Hidden = True