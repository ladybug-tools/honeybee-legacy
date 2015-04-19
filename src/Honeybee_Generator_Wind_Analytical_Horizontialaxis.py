# By Anton Szilasi
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
"""
Provided by Honeybee 0.0.56

Use this component to create your own horizontial axis wind turbine to use in Energyplus simulations. This component simulates wind turbines by using the analytical Power Calculation method - this means that 6 power coefficients need to  be specified.
Details about this power coefficients can be seen here:
    
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#field-power-coefficient-parameter

The difference between the simple and analytical method is that for the simple method, the maximum power coefficient must be calculated while in the analytical method 6 power coefficients must be specified instead of the maximum power coefficient.

-
Provided by Honeybee 0.0.56

    Args:
        template_medium_turbine: If set to True a medium sized turbine will be created with pre-set values, the turbines values can be viewed from the ReadMe! output. Template values can be changed for each input below by entering a value for each input. Otherwise if no input is given template values will be used for each input.
        template_large_turbine: If set to True a large sized turbine will be created with pre-set values, the turbines values can be viewed from the ReadMe! output. Template values can be changed for each input below by entering a value for each input. Otherwise if no input is given template values will be used for each input.
        name_: The name for this wind turbine
        name_: The name for this wind turbine
        rotor_type: This field is the type of axis of the wind turbine, a different algorithm is used in the calculation of the electrical power output of the wind turbine depending on the Rotor type. There are two types of turbines to select from, for a Horizontal axis wind turbine enter an integer input of 1 for a Vertical axis turbine enter an integer input of 2. The default is a Horizontial Axis Wind Turbine.
        powercontrol: This field is the type of rotor control for the wind turbine. This protects the system against the overloading for a system with no speed or pitch control and also to maximize the energy yield for the system. Four different control types are classified in the literature: 
        1-Fixed Speed Fixed Pitch (FSFP),
        2-Fixed Speed Variable Pitch (FSVP),
        3-Variable Speed Fixed Pitch (VSFP), and
        4-Variable Speed Variable Pitch (VSVP).
        enter an integer input of 1,2,3 and 4 to select these options respectively.
        rotor_speed: This field is the maximum rotational speed of the rotor at the rated power of the wind turbine in rev/min (revolution per minute). It is used to determine the tip speed ratio of the rotor and relative flow velocity incident on a single blade of the VAWT systems.
        rotor_diameter: This field is the diameter of the rotor (in meters ). Note that this field is not the height of the blade, but the diameter of the perpendicular circle from the vertical pole in the VAWT systems. It determines the swept area of the rotor of the HAWT systems and the chordal velocity of the VAWT systems.
        overall_height: This field is the height of the hub of the HAWT system, or of the pole of the VAWT system (in meters). It is necessary to estimate local air density and the wind speed at this particular height where the wind turbine system is installed.
        number_of_blades: This field is the number of blades of the wind turbine. The azimuth angle of the rotor of the VAWT system is determined by dividing 360 degree by this field so that the model determines the chordal velocity component and the normal velocity component of the system. The default value is 3.
        power_output: This field is the nominal power output of the wind turbine system at the rated wind speed (in W or Btu/hr). Note that the maximum power of the system should be entered with no control, i.e. FSFP control type, can physically produce. Manufacturer data sometimes describes this as peak power or rated capacity. If the local wind speed is greater than the rated wind speed, the model assumes constant power output of this field.
        rated_wind_speed: This field is the wind speed that the wind turbine system indicates the peak in the power curve (in m/s ). The system produces the maximum power at this speed and the speed of the rotor is managed based on this wind speed.
        cut_in_windspeed: This field is the lowest wind speed where the wind turbine system can be operated (in m/s). No power generation is achieved as long as the ambient wind speed is lower than this speed
        cut_out_windspeed: This field is the greatest wind speed (in m/s). When the wind speed exceeds this value, the wind turbine system needs to be stopped because of inefficiencies in the system. All systems that have either pitch or speed control must be stopped when the ambient wind speed exceeds this speed. Note that the user should input a wind speed above which physical damage to the system might be caused in the case of a FSFP system. It appears as extreme/survival/design wind speed in the literature. The system will be turned off when the ambient wind speed is over this speed.
        overall_turbine_n: This field is the overall system efficiency of the wind turbine system. It includes all the conversion losses as well as transient losses during the dynamic control when the ambient wind speed is between the rated wind speed and cut-out wind speed (see previous fields). The user also has the ability to specify delivery losses from the system to the local area. If the user does not enter a fraction, the model assumes the default value of 0.835. Note that the fraction must be between zero and one.
        max_tip_speed_ratio: This field is the maximum tip speed ratio between the rotor velocity and ambient wind velocity. The rotor speed varies with this ratio to maximize the power output when the rotor control types are variable speed ones. This field allows the user to adjust the power output from the particular system or to find the optimal tip speed ratio of the system. Optimal tip speed ratio is dependent on the number of blades. It is typically about 6, 5, and 3 for two-bladed, three-bladed, and four-bladed rotor, respectively. For the vertical axis wind turbine, it is smaller than horizontal axis wind turbine, and varies with the chord area. 
        max_power_coefficient: This is the maximum fraction of power extraction possible from the ambient wind. This value can be calculated from the power curve published in most manufacturers' specifications by using the kinetic energy equation as
        Cp = P/0.5**A*V^3  where: P = power production at the rated wind speed [W],  = density of air [kg/m3], A = swept area of rotor [m2], V = rated wind speed [m/s], Cp = power coefficient
        power_coefficients: Use a grasshopper panel set to multiline data to specify the 6 power coefficients - If none are specified the defaults outlined in the Energy Plus documentation will be used. More information can be found at: http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#field-power-coefficient-parameter
        
        local_av_windspeed: This is the local annual average wind speed that represents a representative wind profile at the location of the system (in m/s ). It is used to factor the difference in wind speed between the weather file wind data and the locally measured wind data so that the model minimizes uncertainties caused by improper wind data at the particular location. Considerable differences between the weather file wind data and the local wind data typically appear so it is important to consider this carefully in order to use accurate local wind data in the simulation. The model internally determines a multiplier and it is multiplied by the weather file wind data adjusted at the height of the system
        height_local_metrological_station: This is the height that the local wind speed is measured (in meters ). The annual average wind speed (see previous field) input by the user is internally recalculated by existing EnergyPlus functions at the height of the local station. This modified wind speed is then factored and applied to the weather file wind data. The minimum and default values are zero and 50 meters.
        turbine_cost: The cost of the turbine
        
    Returns:
        HB_windturbine: A Honeybee wind turbine to run this in an EnergyPlus system you must first add it to a Honeybee generation system - to do so connect this output to the HB_generationobjects input of the Honeybee_generationsystem component
        
"""

ghenv.Component.Name = "Honeybee_Generator_Wind_Analytical_Horizontialaxis"
ghenv.Component.NickName = 'Generator:Wind:Analytical:Horizontialaxis'
ghenv.Component.Message = 'VER 0.0.56\nAPR_04_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP" #"06 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3" #"0"
except: pass


import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import itertools


hb_hive = sc.sticky["honeybee_generationHive"]()
windgenerator = sc.sticky["wind_generator"]
EP_zone = sc.sticky["honeybee_EPZone"]
hb_hivegen = sc.sticky["honeybee_generationHive"]()

global max_power_coefficient

max_power_coefficient = None

def checktheinputs(name_,powercontrol,rotor_speed,rotor_diameter,overall_height,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,power_coefficients):
    
    if name_ == None:
        print "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!")
        return -1
        
    if (template_medium_turbine == True) and (template_large_turbine== True):
        print "Only one template can be used at a time! Please set either template_large_turbine or template_medium_turbine to true not both! "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only one template can be used at a time! Please set either template_large_turbine or template_medium_turbine to true not both!")
        return -1

    if powercontrol == None:
        print "The field powercontrol must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field powercontrol must be specified!")
        return -1

    if (powercontrol < 1) or (powercontrol > 4):
        print "The field powercontrol must be an integer between 1 and 4!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field powercontrol must be an integer between 1 and 4")
        return -1

    if rotor_speed == None:
        print "The field rotor_speed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field rotor_speed must be specified!")
        return -1
        
    if rotor_diameter == None:
        print "The field rotor_diameter must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field rotor_diameter must be specified!")
        return -1
        
    if overall_height == None:
        print "The field overall_height must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field overall_height must be specified!")
        return -1
        
    if power_output == None:
        print "The field power_output must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field power_output must be specified!")
        return -1
        
    if rated_wind_speed == None:
        print "The field rated_wind_speed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field rated_wind_speed must be specified!")
        return -1
        
    if cut_in_windspeed == None:
        print "The field cut_in_windspeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field cut_in_windspeed must be specified!")
        return -1
        
    if cut_out_windspeed == None:
        print "The field cut_out_windspeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field cut_out_windspeed must be specified!")
        return -1
        
    if max_tip_speed_ratio == None:
        print "The field max_tip_speed_ratio must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field max_tip_speed_ratio must be specified!")
        return -1
        
    if local_av_windspeed == None:
        print "The field local_av_windspeed must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field local_av_windspeed must be specified!")
        return -1

    if turbine_cost == None:
        print "The field turbine_cost must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The field turbine_cost must be specified!")
        return -1
        
    if power_coefficients != []:
        if len(power_coefficients) != 6:
            print "The analytical wind turbine requires 6 power coefficients!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The analytical wind turbine requires 6 power coefficients!")
            return -1
    
        
def main(name_,powercontrol,rotor_speed,rotor_diameter,overall_height,number_of_blades,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,power_coefficients):
        
    if number_of_blades == None:
        number_of_blades = 3
        print "The number of blades of this turbine has not been specified so the default of 3 blades will be used"
    if overall_turbine_n == None:
        overall_turbine_n = 0.835
        print "The overall efficiency of the turbine has not been specified so the default efficiency of 0.835 will be used"

    if height_local_metrological_station == None:
        height_local_metrological_station = 50
        print "The height of the metrological station was not specified so a default of 50 meters has been used"
    
    if powercontrol == 1:
        powercontrol = 'FixedSpeedFixedPitch'
        
    if powercontrol == 2:
        powercontrol = 'FixedSpeedVariablePitch'
        
    if powercontrol == 3:
        powercontrol = 'VariableSpeedFixedPitch'
        
    if powercontrol == 4:
        powercontrol = 'VariableSpeedVariablePitch'

    rotortype = 'HorizontalAxisWindTurbine'
    
    if power_coefficients == []:
        
        power_coefficients = [0.5176,116,0.4,0,5,21]
        
    print " The power control of the turbine is " + str(powercontrol)
    
    print " The rotor speed for the turbine is " + str(rotor_speed) + " rev/min"
    
    print " The rotor diameter for the  turbine is " + str(rotor_diameter) + " meters"
    
    print " The overall height for the turbine is " + str(overall_height) + " meters"
    
    print " The number of blades for the turbine is " + str(number_of_blades ) + " blades"
    
    print " The power output for the turbine is " + str(power_output) + " watts"
    
    print " The rated wind speed for the turbine is " + str(rated_wind_speed) + " m/s"
    
    print " The cut in wind speed for the turbine is " + str(cut_in_windspeed) + " m/s"
    
    print " The cut out wind speed for the turbine is " + str(cut_out_windspeed) + " m/s"
    
    print " The fraction system efficiency for the turbine is " + str(overall_turbine_n)
    
    print " The Maximum Tip Speed Ratio for the turbine is " + str(max_tip_speed_ratio)
    
    print " The Local Average Wind Speed for the turbine is " + str(local_av_windspeed) + " {m/s}"
    
    print " The Height for Local Average Wind Speed for the turbine is " + str(height_local_metrological_station) + " meters"
    
    for count,powercoefficient in enumerate(power_coefficients):
        
        print " Power coefficient " + str(count+1) + " is " + str(powercoefficient)
        
    print " The cost for the turbine is " + str(turbine_cost) + " $ US"
        
    HB_windturbines = []
    
    HB_windturbines.append(windgenerator(name_,rotortype,powercontrol,rotor_speed,rotor_diameter,overall_height,number_of_blades,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,power_coefficients))
    
    HB_windturbine = hb_hivegen.addToHoneybeeHive(HB_windturbines, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HB_windturbine
    
def checktheinputs_template(template_medium_turbine,template_large_turbine):

    if (template_medium_turbine == True) and (template_large_turbine== True):
        print "Only one template can be used at a time! Please set either template_large_turbine or template_medium_turbine to true not both! "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only one template can be used at a time! Please set either template_large_turbine or template_medium_turbine to true not both!")
        return -1
        
def checknametemplate(name_):

    if name_ == None:
        print "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this wind turbine and make sure it is not the same as another wind turbine!")
        return -1
        
        
if template_medium_turbine == True:
    
    if checknametemplate(name_) != -1:
    
        if powercontrol == None:
            powercontrol = 1
            
            
        if rotor_speed == None:
            rotor_speed = 41
            
            
        if rotor_diameter == None:
            rotor_diameter = 19
            
            
        if overall_height == None:
            overall_height = 31
            
            
        if number_of_blades == None:
            number_of_blades = 3
            
            
        if power_output == None:
            power_output = 55000
            

        if rated_wind_speed == None:
            rated_wind_speed = 11
            
            
        if cut_in_windspeed == None:
            cut_in_windspeed = 3.50
            
            
        if cut_out_windspeed == None:
            cut_out_windspeed = 25.00
            
            
        if overall_turbine_n == None:
            overall_turbine_n = 0.835
            
           
        if max_tip_speed_ratio == None:
            max_tip_speed_ratio = 8
            
            
        if max_power_coefficient == None:
            max_power_coefficient = 0.40
            
            
        if local_av_windspeed == None:
            local_av_windspeed = 6.4
            
            
        if height_local_metrological_station == None:
            height_local_metrological_station = 50
            
            
        if turbine_cost == None:
            turbine_cost = 50000
            
if template_large_turbine == True:
    
    if checknametemplate(name_) != -1:
    
        if powercontrol == None:
            powercontrol = 1
            
        if rotor_speed == None:
            rotor_speed = 15
            
        if rotor_diameter == None:
            rotor_diameter = 95
            
        if overall_height == None:
            overall_height = 90
            
        if number_of_blades == None:
            number_of_blades = 3
            
        if power_output == None:
            power_output = 250000

        if rated_wind_speed == None:
            rated_wind_speed = 12
            
        if cut_in_windspeed == None:
            cut_in_windspeed = 3.50
            
        if cut_out_windspeed == None:
            cut_out_windspeed = 25.00
            
        if overall_turbine_n == None:
            overall_turbine_n = 0.835 
           
        if max_tip_speed_ratio == None:
            max_tip_speed_ratio = 5
            
        if max_power_coefficient == None:
            max_power_coefficient = 0.35
            
        if local_av_windspeed == None:
            local_av_windspeed = 6.4
            
        if height_local_metrological_station == None:
            height_local_metrological_station = 50
            
        if turbine_cost == None:
            turbine_cost = 200000
        
        
if checktheinputs(name_,powercontrol,rotor_speed,rotor_diameter,overall_height,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,power_coefficients) != -1:
    
    HB_windturbine = main(name_,powercontrol,rotor_speed,rotor_diameter,overall_height,number_of_blades,power_output,rated_wind_speed,cut_in_windspeed,cut_out_windspeed,overall_turbine_n,max_tip_speed_ratio,max_power_coefficient,local_av_windspeed,height_local_metrological_station,turbine_cost,power_coefficients)

