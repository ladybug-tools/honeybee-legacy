# Created by Anton Szilasi
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to add an Energy Plus earth tube to a Zone.

An earth tube is a long, underground metal or plastic pipe through which air is drawn. During cooling season, as air travels through the pipe, it gives up some of its heat to the surrounding soil and enters the room as cooler air. Similarly, during heating season, as air travels through the pipe, it receives some of its heat from the soil and enters the room as warmer air. Simple earth tubes in EnergyPlus can be controlled by a schedule and through the specification of minimum, maximum, and delta temperatures as described below. As with infiltration and ventilation, the actual flow rate of air through the earth tube can be modified by the temperature difference between the inside and outside environment and the wind speed. The basic equation used to calculate air flow rate of earth tube in EnergyPlus is:
EarthTubeFlowRate = E*F*[A+B|Tzone-Todb|+C(Windspeed)+D(Windspeed^2)]

Where:
1. E is the maximum amount of air mass flow rate of the earth tube expected at design conditions.
2. F is the schedule that modifies the maximum design volume flow fraction between 0 and 1.
3. Tzone is the temperature of the zone which the Earthtube is attached to and Todb is the outdoor dry blub temperature as odb stands for outdoor dry blub temperature.
3. A,B,C and D are Constant term flow coefficients,Temperature Term flow coefficients, Velocity Term flow coefficients and Velocity squared term flow coefficients respectively they are set at the default values of 0.606,2.0199999E-02,5.9800001E-04 and 0.0000000E+00. In future versions the user will be able to specify these.

For more information about the Energy Plus Earthtube please see:
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-airflow.html#zoneearthtube-earth-tube

Provided by Honeybee 0.0.56

    Args:
        _HBZones: The Honeybee zones to which Earthtubes will be added to. Only one earth tube will be added to each zone.
        _epwFile: An .epw file path on your system as a text string. Used to find the ground temperature of the site so Earthtube calculations can be undertaken.
        Schedules_: This field can be a schedule or a list of schedules which correspond sequentially to the _HBZones, if no schedule is given for a zone the default schedule "ALWAYS ON" will be used.  F is the name of the schedule that modifies the maximum design volume flow rate parameter . This fraction between 0.0 and 1.0 is noted as Fschedule in the EarthTubeFlowRate equation the  .
        design_flowrates: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float (noted as Edesign in the EarthTubeFlowRate equation) is the maximum amount of air mass flow rate of the earth tube expected at design conditions the default is 0 m3/s. The flow rate is expressed in units of m3/s. The design value is modified by the schedule fraction and user specified coefficients (Open this component to see the equation).
        mincooling_temps: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the indoor temperature (in Celsius) below which the earth tube is shut off the default is -100 degrees C. This lower temperature limit is intended to avoid overcooling a space and thus result in a heating load. For example, if the user specifies a minimum temperature of 20 C, earth tube is assumed to be available if the zone air temperature is above 20 C. If the zone air temperature drops below 20C, then earth tube is automatically turned off.
        maxheating_temps: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the indoor temperature (in Celsius) above which the earth tube is shut off the default is 100 degrees C. This higher temperature limit is intended to avoid overheating a space and thus result in a cooling load.For example, if the user specifies a maximum temperature of 20 C, earth tube is assumed to be available if the zone air temperature is below 20 C. If the zone air temperature rises above 20C, then earth tube is automatically turned off.
        delta_temps: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the temperature difference (in Celsius) between the indoor and outdoor air dry-bulb temperatures below which the earth tube is shut off the default is 2 degrees C. This is to allow the earth tube to be stopped either if the temperature outside is too warm and could potentially heat the space or if the temperature outside is too cold and could potentially cool the space. For example, if the user specifies a delta temperature of 2C, earth tube is assumed to be available if the temperature difference between indoor and outdoor temperature is at least 2 C. If the outside air dry-bulb temperature is less than 2C cooler or warmer than the indoor dry-bulb temperature, then the earth tube is automatically turned off.
        earthtube_types: This field can be integer or a list of integers between 1 and 3 which correspond sequentially to the _HBZones. Each integer from 1 to 3 defines the type of earth tube as one of the following options: Natural a value of 1, Exhaust a value of 2, or Intake a value of 3. A natural earth tube is assumed to be air movement/exchange that will not consume any fan energy or is the result of natural air flow through the tube and into the building. Values for fan pressure and efficiency for a natural flow earth tube are ignored. For either Exhaust or Intake, values for fan pressure and efficiency define the fan electric consumption. For Natural and Exhaust earth tubes, the conditions of the air entering the space are assumed to be equivalent to the air which is cooled or heated by passing along the pipe. For Intake earth tubes, an appropriate amount of fan heat is added to the air stream. The default is a Natural Earthtube
        fan_Prises: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the pressure rise experienced across the fan in Pascals (N/m2) the default is 150 Pascals. This is a function ofthe fan and plays a role in determining the amount of energy consumed by the fan.
        fan_ns: This field can be a float or a list of floats between 0 and 1 which correspond sequentially to the _HBZones. Each float is the earth tube fan efficiency which is a decimal number between 0.0 and 1.0 the default is 1. This is a function of the fan and plays a role in determining the amount of energy consumed by the fan.        pipe_radii: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the radius of the earth tube(in meters) the default is 0.5 meter. This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe. If the pipe has non-circular cross section, user can use the concept of hydraulic diameter where Radius = 2*Area/Perimeter.        pipe_thicknesses: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the thickness of the earth tube wall (in meters) the default is 0.2 meters. This plays a role in determining the amountof heat transferred from the surrounding soil to the air passing along the earth tube.
        pipe_lengths: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the total length of the pipe (in meters) the default is 15 meters. This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe. As the length of the pipe becomes longer, the amount of the heat transfer becomes larger        pipe_depths: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the depth of the pipe under the ground surface (in meters) the default is 3 meters. This plays a role in determining the temperature of the soil surrounding the pipe.
        soil_condition: An integer between 1 to 4 that defines the actual condition of the soil surrounding ALL the earth tubes: HeavyAndSaturated a value of 1, HeavyAndDamp a value of 2, HeavyAndDry a value of 3 or LightAndDry a value of 4. This determines the thermal diffusivity and thermal conductivity of the surrounding soil, which play a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe. The default is 1 - HeavyAndSaturated.
        condition_groundsurface: An integer between 1 to 8 and defines the condition of the ground surface above ALL the earth tubes, Bare and wet is a value of 1, Bare and moist is a value of 2, Bare and Arid is a value of 3, Bare and dry is a value of 4, Covered and wet is a value of 5, Covered and moist is a value of 6, Covered and arid is a value of 7, Covered and dry is a value of 8 the default is 1 - Bare and wet.
        pipe_thermal_conductivity: This field can be a float or a list of floats which correspond sequentially to the _HBZones. Each float is the thermal conductivity of the pipe (in W/m-K) the default is 200 W/m-K. This plays a role in determining the amount of heat transferred from the surrounding soil to the air passing along the pipe.
        
    Returns:
        earthtube_HBZones: The Honeybee zones that have been modified by this component - these zones now contain an earth tube
"""

ghenv.Component.Name = "Honeybee_AddEarthtube"
ghenv.Component.Message = 'VER 0.0.56\nAPR_08_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os
import rhinoscriptsyntax as rs
import itertools

def checktheinputs(Schedules_,design_flowrates,mincooling_temps,maxheating_temps,delta_temps,earthtube_types,fan_Prises,fan_ns,pipe_radii,pipe_depths,soil_condition,condition_groundsurface,pipe_thermal_conductivity):
    
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
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    # Check design flow rate values
    
    for values in design_flowrates:
        if values  < 0:
            warnMsg= "The design flow rate must be equal to or greater than zero m3/s! "
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1 # Note to self just print a runtime warning DOES NOT stop the component from executing here I am making it return -1 so that main will stop executing due to ... on line ... XXX this is what Mostapha has done and its good practice.
            
    # Check the inputs of mincooling_temp and maxheating_temp
    for mincooling_temp,maxheating_temp in itertools.izip_longest(mincooling_temps,maxheating_temps):
        
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

    for pipe_depth,pipethickness,piperadius in itertools.izip_longest(pipe_depths,pipe_thicknesses,pipe_radii):
        
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
    
    for values in fan_ns:
    
        if (fan_n < 0) or (fan_n > 1):
            
            warnMsg =  "fan_n - total fan efficiency must be a decimal number between 0 and 1!"
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1
            
   # Check soil condition input
   
    if (soil_condition < 1) or (soil_condition > 4):
        
        warnMsg = "soil_condition input must be a integer of 1,2,3 or 4!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1
        
    # Check ground surface condition input
    
    if (condition_groundsurface < 1) or (condition_groundsurface > 8):
        
        warnMsg = "condition_groundsurface input must be a integer of 1,2,3,4,5,6,7 or 8!"
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

    # Check schedules by making sure that the schedules specified in Schedules_ exist lines 127 to 148 these lines of code are taken from setEPZoneSchedules component
    
    schedules = [Schedules_]
    HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
    
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
    

def main(_HBZones,Schedules_,design_flowrates,mincooling_temps,maxheating_temps,delta_temps,earthtube_types,fan_Prises,fan_ns,pipe_radii,pipe_thicknesses,pipe_lengths,pipe_depths,soil_condition,condition_groundsurface,pipe_thermal_conductivity):
    
    """This function is the heart of this component it takes all the component arguments and writes an earth tube into the IDF file for each Honeybee zone connected to this component
    
    Args:
        The arguements seen in the function definition are the same as the arguements on the panel.
            
    Returns:
        The properties of the earth tubes of the Honeybee zones connected to this component these properties are then written to an IDF file in Honeybee_ Run Energy Simulation component."""
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # Call the Honeybee zones from the hive
    
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(_HBZones)
    
    # The condition of the ground surrounding the earth tube used both writing to IDF and in CalcSoilSurfTemp preprocess
        
    def soilconditionforIDF(soil_condition):
        
        """ A function which takes the soil_condition from the panel and returns the required EnergyPlus IDF input for example an input on the panel of 1 corresponds to HeavyAndSaturated.
            
            Args:
                soil_condition: As on the panel arguement soil_condition an integer between 1 to 4 that defines the actual condition of the soil surrounding the earth tube
                
            Returns:
                soil_cond: A string which returns the EnergyPlus input which corresponds to 1,2,3 or 4 as described on the panel arguement soil_condition
                e.g 1 = "HeavyAndSaturated"
        """
    
        if soil_condition == 1:
            
            soil_cond = "HeavyAndSaturated"
            
        if soil_condition == 2:
            
            soil_cond = "HeavyAndDamp"
            
        if soil_condition == 3:
            
            soil_cond = "HeavyAndDry"
            
        if soil_condition == 4:
            
            soil_cond = "LightAndDry"  
        
        return soil_cond
        
    def calcsoilsurftempwrap(soil_condition,condition_groundsurface):
        """This function is a wrapper for the EnergyPlus auxilary CalcSoilSurfTemp.exe
        Normally the EnergyPlus user would manually open this exe and enter soil_condition and condition_groundsurface 
        the 3 outputs from the exe would then need to be put into the IDF. Since these 3 outputs from the exe depend only on the epw weather file
        This wrapper will only perform these actions everytime the weatherfile is changed.
        
        Args: soil_condition: A integer directly from the panel same as described in component arguements
            condition_groundsurface: A integer directly from the panel same as described in component arguements
            
        Returns: 
            annav: Annual Average Soil Surface Temperature C
            amp: Amplitude of Soil Surface Temperature
            phaseconstant: Phase Constant of Soil Surface Temperature
        """
        
        EPfolder = sc.sticky["honeybee_folders"]["EPPath"] 
        
        # The process for creating the wrapper is below
        
        os.chdir(EPfolder +"\PreProcess\CalcSoilSurfTemp")
        
        # 1. Write soil_condition and condition_groundsurface to a text file so it can be read by the command line
        # Create EnergyPlus file path
        
        auxfilepath = EPfolder +"PreProcess\CalcSoilSurfTemp"
        filePath = os.path.join(auxfilepath,"exeinputs.txt")
        fileWrite = open(filePath,"w")
        
        # Write soil_condition and condition_groundsurface to a text file
        
        fileWrite.write(str(soil_condition) + "\n"+ str(condition_groundsurface))
        
        fileWrite.close()
        
        # The EnergyPlus auxilary CalcSoilSurfTemp.exe takes EnergyPlus weather data epw as an arguement 
        
        epwFile = _epwFile
        
        # 2. A bat file is needed to open the exe give the epw as an arguement and feed the exe 
        #the keystrokes soil_condition and condition_groundsurface 
        
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
    
    annav,amp,phaseconstant = calcsoilsurftempwrap(soil_condition,condition_groundsurface)
    
    soil_cond = soilconditionforIDF(soil_condition)
    
    # Write the properties of the earth tube for each Honeybee zone connected to this component
    
    for zoneCount,zone in enumerate(HBObjectsFromHive):
        
        zone.earthtube = True
        
        # Writing earth tube schedules
        
        try: zone.ETschedule = Schedules_[zoneCount] # If zoneCount index in range of zoneCount
        except IndexError:
            zone.ETschedule = "ALWAYS ON" # If zoneCount index is not in range of zoneCount or there is no schedule input set to default schedule of "ALWAYS ON"
        
        # Writing earth tube design flow rate
        
        try: zone.design_flow_rate = design_flowrates[zoneCount]
        except IndexError:
            zone.design_flow_rate = 0
        
        # Writing earth tube minimum cooling temp
        try: zone.mincooltemp = mincooling_temps[zoneCount]
        except IndexError:
            zone.mincooltemp = -100
        
        # Writing earth tube maximum heating temp
        
        try: zone.maxheatingtemp = maxheating_temps[zoneCount]
        except IndexError:
            zone.maxheatingtemp = 100
        
        # Writing earth tube delta T
        
        try: zone.delta_temp = delta_temps[zoneCount]
        except IndexError:
            zone.delta_temp = 2
        
        # Writing earth tube type
        
        try: earthtube_type = earthtube_types[zoneCount]
        
        except IndexError:
            earthtube_type = 1
        
        if earthtube_type == 1:
            
            zone.et_type = "NATURAL"
            
        if earthtube_type == 2:
            
            zone.et_type = "EXHAUST"
            
        if earthtube_type == 3:
            
            zone.et_type = "INTAKE"
            
        # Writing earth tube pressure rise across the fan
        
        try: zone.fanprise = fan_Prises[zoneCount]
        
        except IndexError:
            zone.fanprise = 150

        # Writing earth tube fan efficiency
        
        try: zone.efficiency = fan_ns[zoneCount]
        
        except IndexError:
            zone.efficiency  = 1
        
        # Writing earth tube earthtube pipe radius
        
        try: zone.piperadius = pipe_radii[zoneCount]
        
        except IndexError:
            zone.piperadius  = 0.5
        
        # Writing earth tube pipe thickness
        
        try: zone.thick = pipe_thicknesses[zoneCount]
        
        except IndexError:
            zone.thick  = 0.2
        
        # Writing earth tube pipe length 
        
        try: zone.length = pipe_lengths[zoneCount]
        
        except IndexError:
            zone.length  = 15
        
        # Writing earth tube pipe thermal conductivity
        
        try: zone.thermal_k = pipe_thermal_conductivity[zoneCount]
        
        except IndexError:
            zone.thermal_k = 200
            
        # Writing earth tube depth - below ground surface
        
        try: zone.pipedepth = pipe_depths[zoneCount]
        
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
        
    # Add modified zones to dictionary
    
    
    ModifiedHBZones = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return ModifiedHBZones
    

if checktheinputs(Schedules_,design_flowrates,mincooling_temps,maxheating_temps,delta_temps,earthtube_types,fan_Prises,fan_ns,pipe_radii,pipe_depths,soil_condition,condition_groundsurface,pipe_thermal_conductivity) != -1:

    if _HBZones and _HBZones[0]!= None:
        earthtube_HBZones = main(_HBZones,Schedules_,design_flowrates,mincooling_temps,maxheating_temps,delta_temps,earthtube_types,fan_Prises,fan_ns,pipe_radii,pipe_thicknesses,pipe_lengths,pipe_depths,soil_condition,condition_groundsurface,pipe_thermal_conductivity)
