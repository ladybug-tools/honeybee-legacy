#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Anton Szilasi <ajszilas@gmail.com> 
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
Use this component to add an Energy Plus earth tube to a Zone.

An earth tube is a long, underground metal or plastic pipe through which air is drawn. During cooling season, as air travels through the pipe, it gives up some of its heat to the surrounding soil and enters the room as cooler air. Similarly, during heating season, as air travels through the pipe, it receives some of its heat from the soil and enters the room as warmer air. Simple earth tubes in EnergyPlus can be controlled by a schedule and through the specification of minimum, maximum, and delta temperatures as described below. As with infiltration and ventilation, the actual flow rate of air through the earth tube can be modified by the temperature difference between the inside and outside environment and the wind speed. The basic equation used to calculate air flow rate of earth tube in EnergyPlus is:
EarthTubeFlowRate = E*F*[A+B|Tzone-Todb|+C(Windspeed)+D(Windspeed^2)]
-
Where:
1. E is the maximum amount of air mass flow rate of the earth tube expected at design conditions.
-
2. F is the schedule that modifies the maximum design volume flow fraction between 0 and 1.
-
3. Tzone is the temperature of the zone which the Earthtube is attached to and Todb is the outdoor dry blub temperature as odb stands for outdoor dry blub temperature.
-
4. A,B,C and D are Constant term flow coefficients,Temperature Term flow coefficients, Velocity Term flow coefficients and Velocity squared term flow coefficients respectively they are set at the default values of 0.606,2.0199999E-02,5.9800001E-04 and 0.0000000E+00. In future versions the user will be able to specify these.
-
For more information about the Energy Plus Earthtube please see:
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-airflow.html#zoneearthtube-earth-tube
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: The Honeybee zones to which Earthtubes will be added to. Only one earth tube will be added to each zone.
        _epwFile: An .epw file path on your system as a text string. Used to find the ground temperature of the site so Earthtube calculations can be undertaken.
        schedules_: This field can be a schedule or a list of schedules which correspond sequentially to the _HBZones. If no schedule is given for a zone the default schedule "ALWAYS ON" will be used.
        -
        F is the name of the schedule that modifies the maximum design volume flow rate parameter . This fraction between 0.0 and 1.0 is noted as Fschedule in the EarthTubeFlowRate equation the  .
        _designFlowrates: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float (noted as Edesign in the EarthTubeFlowRate equation) is the maximum amount of air mass flow rate of the earth tube expected at design conditions the default is 0 m3/s.
        If no flow rate is given for a zone the default will be used.
        -
        The flow rate is expressed in units of m3/s. The design value is modified by the schedule fraction and user specified coefficients (Open this component to see the equation).
        _mincoolingTemps_: This field can be a float or a list of floats which correspond sequentially to the _HBZones.
        -
        Each float is the indoor temperature (in Celsius) below which the earth tube is shut off the default is -100 degrees C. This lower temperature limit is intended to avoid overcooling a space and thus result in a heating load.
        -
        For example, if the user specifies a minimum temperature of 20 C, earth tube is assumed to be available if the zone air temperature is above 20 C. If the zone air temperature drops below 20C, then earth tube is automatically turned off.
        If no temperature is given for a zone the default will be used.
        _maxheatingTemps_: 
        This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the indoor temperature (in Celsius) above which the earth tube is shut off the default is 100 degrees C.
        -
        This higher temperature limit is intended to avoid overheating a space and thus result in a cooling load.For example, if the user specifies a maximum temperature of 20 C, earth tube is assumed to be available if the zone air temperature is below 20 C. 
        -
        If the zone air temperature rises above 20C, then earth tube is automatically turned off. If no temperature is given for a zone the default will be used.
        
        _deltaTemps_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the temperature difference (in Celsius) between the indoor and outdoor air dry-bulb temperatures below which the earth tube is shut off the default is 2 degrees C.
        
        -
        This is to allow the earth tube to be stopped either if the temperature outside is too warm and could potentially heat the space or if the temperature outside is too cold and could potentially cool the space. For example, if the user specifies a delta temperature of 2C, earth tube is assumed to be available if the temperature difference between indoor and outdoor temperature is at least 2 C
        -
        If the outside air dry-bulb temperature is less than 2C cooler or warmer than the indoor dry-bulb temperature, then the earth tube is automatically turned off.
        If no temperature is given for a zone the default will be used.
        _earthTubeTypes_: This field can be integer or a list of integers between 1 and 3 which correspond sequentially to the _HBZones. Each integer from 1 to 3 defines the type of earth tube as one of the following options: Natural a value of 1, Exhaust a value of 2, or Intake a value of 3. 
        -
        A natural earth tube is assumed to be air movement/exchange that will not consume any fan energy or is the result of natural air flow through the tube and into the building. Values for fan pressure and efficiency for a natural flow earth tube are ignored. For either Exhaust or Intake, values for fan pressure and efficiency define the fan electric consumption. 
        -
        For Natural and Exhaust earth tubes, the conditions of the air entering the space are assumed to be equivalent to the air which is cooled or heated by passing along the pipe.
        -
        For Intake earth tubes, an appropriate amount of fan heat is added to the air stream. The default is a Natural Earthtube and this will be used if no earth tube type is given for the zone.
        _fanPrises_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the pressure rise experienced across the fan in Pascals (N/m2) the default is 150 Pascals which will be used if no value is given for a zone.
        -
        This is a function of the fan and plays a role in determining the amount of energy consumed by the fan.
        _fanEfficiencies_: This field can be a float or a list of floats between 0 and 1 which correspond sequentially to the _HBZones. Each float is the earth tube fan efficiency which is a decimal number between 0.0 and 1.0 the default is 1 which will be used if no value is given for a zone.
        -
        This is a function of the fan and plays a role in determining the amount of energy consumed by the fan.        _pipeRadii_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the radius of the earth tube(in meters) the default is 0.5 meter which will be used if no value is given for a zone. This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe. 
        -
        If the pipe has non-circular cross section, user can use the concept of hydraulic diameter where Radius = 2*Area/Perimeter.        _pipeThicknesses_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the thickness of the earth tube wall (in meters) the default is 0.2 meters which will be used if no value is given for a zone. 
        -
        This plays a role in determining the amountof heat transferred from the surrounding soil to the air passing along the earth tube.
        _pipeLengths_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the total length of the pipe (in meters) the default is 15 meters which will be used if no value is given for a zone. 
        -
        This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe. As the length of the pipe becomes longer, the amount of the heat transfer becomes larger        _pipeDepths_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the depth of the pipe under the ground surface (in meters) the default is 3 meters which will be used if no value is given for a zone. 
        -
        This plays a role in determining the temperature of the soil surrounding the pipe.
        _soilCondition_: An integer between 1 to 4 that defines the actual condition of the soil surrounding ALL the earth tubes: HeavyAndSaturated a value of 1, HeavyAndDamp a value of 2, HeavyAndDry a value of 3 or LightAndDry a value of 4. 
        -
        This determines the thermal diffusivity and thermal conductivity of the surrounding soil, which play a role in determining the amount of heat transferred from the surrounding soil to the air passing along ALL the pipes.
        -
        The default is 1 - HeavyAndSaturated.
        _conditionGroundSurface_: An integer between 1 to 8 and defines the condition of the ground surface above ALL the earth tubes.
        -
        Bare and wet is a value of 1, Bare and moist is a value of 2, Bare and Arid is a value of 3, Bare and dry is a value of 4, Covered and wet is a value of 5, 
        -
        Covered and moist is a value of 6, Covered and arid is a value of 7, Covered and dry is a value of 8 the default is 1 - Bare and wet.
        _pipeThermalConductivity_: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the thermal conductivity of the pipe (in W/m-K) the default is 200 W/m-K. 
        -
        This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along ALL the earth tubes.
        
    Returns:
        Readme: Details of the earth tubes created.
        earthTubeHBZones: The Honeybee zones that have been modified by this component - these zones now contain an earth tube
"""

ghenv.Component.Name = "Honeybee_AddEarthtube"
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP" #"08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import Grasshopper
import os
import rhinoscriptsyntax as rs
import itertools


readmedatatree = Grasshopper.DataTree[object]()

def checktheinputs(schedules_,_designFlowrates,_mincoolingTemps_,_maxheatingTemps_,_deltaTemps_,_earthTubeTypes_,_fanPrises_,_fanEfficiencies_,_pipeRadii_,_pipeDepths_,_soilCondition_,_conditionGroundSurface_,_pipeThermalConductivity_):
    
    """This function checks all the inputs of the component to ensure that the component is stopped if there is anything wrong with the inputs
        
        Args:
            The arguements seen in the function definition are the same as the arguements on the panel.
            
        Returns:
            If there are any issues with the inputs this function will return -1 and the component will stop as per the code on line 315 else this function will return None"""
          
    # Check if the Honeybee hive is on the sticky
    
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    # Check if it is the latest Honeybee release 
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    # Check design flow rate values
    
    for values in _designFlowrates:
        if values  < 0:
            warnMsg= "The design flow rate must be equal to or greater than zero m3/s! "
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1 # Note to self just print a runtime warning DOES NOT stop the component from executing here I am making it return -1 so that main will stop executing due to ... on line ... XXX this is what Mostapha has done and its good practice.
            
    # Check the inputs of mincooling_temp and maxheating_temp
    for mincooling_temp,maxheating_temp in itertools.izip_longest(_mincoolingTemps_,_maxheatingTemps_):
        
        if mincooling_temp == None:
            mincooling_temp = -100
        if maxheating_temp == None:
            maxheating_temp = 100
            
        if mincooling_temp > maxheating_temp:
            
            warnMsg= "The minimum zone temperature when cooling cannot be greater than the maximum zone temperature when heating!"
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1
        
    # Check that Pipe Depth Under Ground Surface is greater than 3*Pipe Radius otherwise EnergyPlus will create an error

    for pipe_depth,pipethickness,piperadius in itertools.izip_longest(_pipeDepths_,_pipeThicknesses_,_pipeRadii_):
        
        if pipe_depth == None:
            pipe_depth = 3
        if pipethickness == None:
            pipethickness = 0.2
        if piperadius == None:
            piperadius = 0.5
        
        if (pipe_depth*3)+pipethickness <= piperadius:
            
            warnMsg= "Pipe Depth Under Ground Surface must be greater than 3*Pipe Radius + Pipe Thickness"
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1

    # Check fan efficiency input
    
    for values in _fanEfficiencies_:
    
        if (fan_n < 0) or (fan_n > 1):
            
            warnMsg =  "fan_n - total fan efficiency must be a decimal number between 0 and 1!"
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1
            
   # Check soil condition input
   
    if (_soilCondition_ < 1) or (_soilCondition_ > 4):
        
        warnMsg = "_soilCondition_ input must be a integer of 1,2,3 or 4!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1
        
    # Check ground surface condition input
    
    if (_conditionGroundSurface_ < 1) or (_conditionGroundSurface_ > 8):
        
        warnMsg = "_conditionGroundSurface_ input must be a integer of 1,2,3,4,5,6,7 or 8!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1
        
    # Check that Honeybee Zones are connected
    
    if _HBZones == [] or _HBZones[0] == None :
        
        warnMsg = "Please connect Honeybee Zones to _HBZones!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1
    
    # Check that a epw file is connected
    
    if _epwFile == None:
        
        warnMsg = "Please connect a epw file to _epwFile!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1
        
        
    if not _epwFile and not _epwFile.endswith('.epw') and not _epwFile != 'C:\Example.epw':
        
        warnMsg = "Please connect a valid epw"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1

    # Check schedules by making sure that the schedules specified in schedules_ exist lines 127 to 148 these lines of code are taken from setEPZoneSchedules component
    
    schedules = [schedules_]
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
    
    print HBScheduleList
    
    for scheduleList in schedules:
        for schedule in scheduleList: 
            
            if schedule!=None:
                schedule= schedule.upper()
            
            # If schedule is not contained within a CSV file that is the schedule wasn't created by the user using the component Honeybee_Create CSV schedule
            
            if schedule!=None and not schedule.lower().endswith(".csv") and schedule not in HBScheduleList:
                msg = "Cannot find " + schedule + " in Honeybee schedule library."
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return -1
            
            # If schedule is contained within a CSV file created by the user using the component Honeybee_Create CSV schedule
            
            elif schedule!=None and schedule.lower().endswith(".csv"):
                
                # check if csv file exists
                
                if not os.path.isfile(schedule):
                    msg = "Cannot find the schedule file: " + schedule
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return -1
    

def main(_HBZones,schedules_,_designFlowrates,_mincoolingTemps_,_maxheatingTemps_,_deltaTemps_,_earthTubeTypes_,_fanPrises_,_fanEfficiencies_,_pipeRadii_,_pipeThicknesses_,_pipeLengths_,_pipeDepths_,_soilCondition_,_conditionGroundSurface_,_pipeThermalConductivity_):
    
    """This function is the heart of this component it takes all the component arguments and writes an earth tube into the IDF file for each Honeybee zone connected to this component
    
    Args:
        The arguements seen in the function definition are the same as the arguements on the panel.
            
    Returns:
        The properties of the earth tubes of the Honeybee zones connected to this component these properties are then written to an IDF file in Honeybee_ Run Energy Simulation component."""
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # Call the Honeybee zones from the hive
    
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(_HBZones)
    
    # The condition of the ground surrounding the earth tube used both writing to IDF and in CalcSoilSurfTemp preprocess
        
    def soilconditionforIDF(_soilCondition_):
        
        """ A function which takes the _soilCondition_ from the panel and returns the required EnergyPlus IDF input for example an input on the panel of 1 corresponds to HeavyAndSaturated.
            
            Args:
                _soilCondition_: As on the panel arguement _soilCondition_ an integer between 1 to 4 that defines the actual condition of the soil surrounding the earth tube
                
            Returns:
                soil_cond: A string which returns the EnergyPlus input which corresponds to 1,2,3 or 4 as described on the panel arguement _soilCondition_
                e.g 1 = "HeavyAndSaturated"
        """
    
        if _soilCondition_ == 1:
            
            soil_cond = "HeavyAndSaturated"
            
        if _soilCondition_ == 2:
            
            soil_cond = "HeavyAndDamp"
            
        if _soilCondition_ == 3:
            
            soil_cond = "HeavyAndDry"
            
        if _soilCondition_ == 4:
            
            soil_cond = "LightAndDry"  
        
        return soil_cond
        
    def calcsoilsurftempwrap(_soilCondition_,_conditionGroundSurface_):
        """This function is a wrapper for the EnergyPlus auxilary CalcSoilSurfTemp.exe
        Normally the EnergyPlus user would manually open this exe and enter _soilCondition_ and _conditionGroundSurface_ 
        the 3 outputs from the exe would then need to be put into the IDF. Since these 3 outputs from the exe depend only on the epw weather file
        This wrapper will only perform these actions everytime the weatherfile is changed.
        
        Args: _soilCondition_: A integer directly from the panel same as described in component arguements
            _conditionGroundSurface_: A integer directly from the panel same as described in component arguements
            
        Returns: 
            annav: Annual Average Soil Surface Temperature C
            amp: Amplitude of Soil Surface Temperature
            phaseconstant: Phase Constant of Soil Surface Temperature
        """
        
        EPfolder = sc.sticky["honeybee_folders"]["EPPath"] 
        
        # The process for creating the wrapper is below
        
        os.chdir(EPfolder +"\PreProcess\CalcSoilSurfTemp")
        
        # 1. Write _soilCondition_ and _conditionGroundSurface_ to a text file so it can be read by the command line
        # Create EnergyPlus file path
        
        auxfilepath = EPfolder +"PreProcess\CalcSoilSurfTemp"
        filePath = os.path.join(auxfilepath,"exeinputs.txt")
        fileWrite = open(filePath,"w")
        
        # Write _soilCondition_ and _conditionGroundSurface_ to a text file
        
        fileWrite.write(str(_soilCondition_) + "\n"+ str(_conditionGroundSurface_))
        
        fileWrite.close()
        
        # The EnergyPlus auxilary CalcSoilSurfTemp.exe takes EnergyPlus weather data epw as an arguement 
        
        epwFile = _epwFile
        
        # 2. A bat file is needed to open the exe give the epw as an arguement and feed the exe 
        #the keystrokes _soilCondition_ and _conditionGroundSurface_ 
        
        filePath1 = os.path.join(auxfilepath,"runwrapper.bat")
        
        fileWrite1 = open(filePath1,"w")
        
        fileWrite1.write(EPfolder+"PreProcess\CalcSoilSurfTemp\CalcSoilSurfTemp.exe "+ epwFile +" < "+EPfolder+"PreProcess\CalcSoilSurfTemp\exeinputs.txt")
        
        fileWrite1.close()
        
        # Run the batch script
        
        os.system(filePath1)
        
        def rchop(thestring, ending):
            return thestring[len(ending):]
        
        filePath2 = os.path.join(auxfilepath,"CalcSoilSurfTemp.out")
        
        calcsoilsurftempout = open(filePath2,"r")
        
        count = 0
        
        for line in calcsoilsurftempout:
        
            if count == 1:
                annav = float(rchop(line, "Annual Average Soil Surface Temperature   "))
            if count == 2:
                amp = float(rchop(line, "Amplitude of Soil Surface Temperature   "))
            if count == 3:
                phaseconstant = float(rchop(line, "Phase Constant of Soil Surface Temperature "))
            count = count+1
            
        calcsoilsurftempout.close()
            
        # Delete the bat and textfile
        
        os.remove(filePath)
        
        #os.remove(filePath2) # XXX should delete bat file but not working???
        
        return annav,amp,phaseconstant
            
    # Create a wrapper for the EnergyPlus auxilary CalcSoilSurfTemp.exe
    
    annav,amp,phaseconstant = calcsoilsurftempwrap(_soilCondition_,_conditionGroundSurface_)
    
    soil_cond = soilconditionforIDF(_soilCondition_)
    
    # Write the properties of the earth tube for each Honeybee zone connected to this component
    
    for zoneCount,zone in enumerate(HBObjectsFromHive):
        
        zone.earthtube = True
        
        # Writing earth tube schedules
        
        try: zone.ETschedule = schedules_[zoneCount] # If zoneCount index in range of zoneCount
        except IndexError:
            zone.ETschedule = "ALWAYS ON" # If zoneCount index is not in range of zoneCount or there is no schedule input set to default schedule of "ALWAYS ON"
        
        # Writing earth tube design flow rate
        
        try: zone.design_flow_rate = _designFlowrates[zoneCount]
        except IndexError:
            zone.design_flow_rate = 0
        
        # Writing earth tube minimum cooling temp
        try: zone.mincooltemp = _mincoolingTemps_[zoneCount]
        except IndexError:
            zone.mincooltemp = -100
        
        # Writing earth tube maximum heating temp
        
        try: zone.maxheatingtemp = _maxheatingTemps_[zoneCount]
        except IndexError:
            zone.maxheatingtemp = 100
        
        # Writing earth tube delta T
        
        try: zone.delta_temp = _deltaTemps_[zoneCount]
        except IndexError:
            zone.delta_temp = 2
        
        # Writing earth tube type
        
        try: earthtube_type = _earthTubeTypes_[zoneCount]
        
        except IndexError:
            earthtube_type = 1
        
        if earthtube_type == 1:
            
            zone.et_type = "NATURAL"
            
        if earthtube_type == 2:
            
            zone.et_type = "EXHAUST"
            
        if earthtube_type == 3:
            
            zone.et_type = "INTAKE"
            
        # Writing earth tube pressure rise across the fan
        
        try: zone.fanprise = _fanPrises_[zoneCount]
        
        except IndexError:
            zone.fanprise = 150

        # Writing earth tube fan efficiency
        
        try: zone.efficiency = _fanEfficiencies_[zoneCount]
        
        except IndexError:
            zone.efficiency  = 1
        
        # Writing earth tube earthtube pipe radius
        
        try: zone.piperadius = _pipeRadii_[zoneCount]
        
        except IndexError:
            zone.piperadius  = 0.5
        
        # Writing earth tube pipe thickness
        
        try: zone.thick = _pipeThicknesses_[zoneCount]
        
        except IndexError:
            zone.thick  = 0.2
        
        # Writing earth tube pipe length 
        
        try: zone.length = _pipeLengths_[zoneCount]
        
        except IndexError:
            zone.length  = 15
        
        # Writing earth tube pipe thermal conductivity
        
        try: zone.thermal_k = _pipeThermalConductivity_[zoneCount]
        
        except IndexError:
            zone.thermal_k = 200
            
        # Writing earth tube depth - below ground surface
        
        try: zone.pipedepth = _pipeDepths_[zoneCount]
        
        except IndexError:
            zone.pipedepth = 3
        
        # Writing the soil condition 
        
        zone.soil_con = soil_cond
        
        # Writing zone Average Soil Surface Temperature,Amplitude of Soil Surface Temperature
        # & Phase Constant of Soil Surface Temperature respectively
        
        zone.soil_avannual = annav
        
        zone.soil_amplitude = amp
        
        zone.soil_phaseconstant = phaseconstant
        
        # XXX Add constants A,B,C,D use the following values for now add functionality to change in future
        
        zone.termflow = '0.6060000'
        zone.tempflowco = '2.0199999E-02'
        zone.veltermflow = '5.9800001E-04'
        zone.velsquflow = '0.0000000E+00'
        
    
        message = "Honeybee zone "+ str(zone.name) + " now has an earthtube with the following specifications: \n" + "A operation schedule named " + str(zone.ETschedule) +"\n" + "A design flowrate of " + str(zone.design_flow_rate) +" m3/s "+" \n" + "The minimum zone temperature when cooling is " + str(zone.mincooltemp) + " C " + \
        " \n" + "The maximum zone temperature when heating is " + str(zone.maxheatingtemp)+ " C " + " \n" + "The temperature difference between the indoor and outdoor air dry-bulb temperatures below which the earth tube is shut off is " + str(zone.delta_temp) + " C " +" \n" + "The earthtube type is " + str(zone.et_type) + \
        " \n" + "The fan pressure rise across a fan in the earth tube " + str(zone.fanprise) + " Pa " + " \n" + "The efficiency of the fan is (decimal) " + str(zone.efficiency) +" \n" + "The radius of the earth tube is " +str(zone.piperadius) + " m "+ " \n" + "The length of the earth tube is " + str(zone.length) + " m" +" \n" \
        "The thermal conductivity of the earthtube is " + str(zone.thermal_k) + " W/mC " + " \n" + "The pipe depth under the ground surface is " + str(zone.pipedepth) + " m "
            
        readmedatatree.Add(message,gh.Data.GH_Path(zoneCount))
        
    # Add modified zones to dictionary

    ModifiedHBZones = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component4)
    
    return ModifiedHBZones
    



if checktheinputs(schedules_,_designFlowrates,_mincoolingTemps_,_maxheatingTemps_,_deltaTemps_,_earthTubeTypes_,_fanPrises_,_fanEfficiencies_,_pipeRadii_,_pipeDepths_,_soilCondition_,_conditionGroundSurface_,_pipeThermalConductivity_) != -1:

    if _HBZones and _HBZones[0]!= None:
        earthTubeHBZones = main(_HBZones,schedules_,_designFlowrates,_mincoolingTemps_,_maxheatingTemps_,_deltaTemps_,_earthTubeTypes_,_fanPrises_,_fanEfficiencies_,_pipeRadii_,_pipeThicknesses_,_pipeLengths_,_pipeDepths_,_soilCondition_,_conditionGroundSurface_,_pipeThermalConductivity_)
        
        # Create the output Datatree
        Readme = readmedatatree