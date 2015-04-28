# By Anton Szilasi
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Provided by Honeybee 0.0.56

Use this component to add EnergyPlus simple batteries to a Energy Plus simulation.

Find out more information about Energy Plus batteries here:
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#electricloadcenterstorage-battery

-
Provided by Honeybee 0.0.56

    Args:
        No_battery: To form a battery bank of a particularly battery enter the number of the batteries in the bank as an integer here the default is one.
        name_: The battery name - make it unique from other batteries
        battery_capacity: The capacity of each battery in joules
        initial_charge: The intitial charge of the batteries as a fraction 
        max_discharge: The maximum discharge rate in Watts
        max_charge: The maximum charge rate in Watts
        discharge_n: The discharging efficiency the default value is 0.7
        charge_n: The charging efficiency the default value is 0.7
        battery_cost: The cost of each battery (The total battery cost will equal this value multipled by the number of batteries) in whatever currency the user wishes - Just make it consistent with other components you are using
        replacement_time: Specify how often in years the batteries need to be replaced. The default is 4 years.
        
    Returns:
        HB_batteries: Honeybee batteries - to include these batteries in a generation system connect them to the input HB_generationobjects on the Honeybee_generationsystem component 
        
"""

ghenv.Component.Name = "Honeybee_Generator_batteries_Simple"
ghenv.Component.NickName = 'Batteries:Simple'
ghenv.Component.Message = 'VER 0.0.56\nAPR_19_2015'
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
EP_zone = sc.sticky["honeybee_EPZone"] 
simple_battery = sc.sticky["simple_battery"]

battery_zone = None

def checktheinputs(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost,battery_zone):
    
    if name_ == None:
    
        print "Please specify a name for this battery and make sure it is not the same as another battery!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this battery and make sure it is not the same as another battery!")
        return -1
    
    if battery_capacity == None:
        print "The battery capacity in joules must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The battery capacity must be specified!")
        return -1
        
    if initial_charge == None:
        print "The battery initial charge as a fraction must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The battery initial charge as a fraction must be specified")
        return -1
        
    if max_discharge == None:
        print "The maximum discharge rate of the battery in watts must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The maximum discharge rate of the battery in watts must be specified!")
        return -1
        
    if max_charge == None:
        print "The maximum charge rate of the battery in watts must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The maximum charge rate of the battery in watts must be specified!")
        return -1
        
        
    if battery_cost == None:
        print "The cost of the battery must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The cost of the battery must be specified!")
        return -1
        

def main(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost,battery_zone,replacement_time):
    
    battery = []
    
    if No_battery == None:
        No_battery = 1
        print "The number of batteries has not be specified so the number will be set to one"
        
    if name_ == None:
        name_ = "Simple:battery" # XXX Need to re-work so names cannot be duplicated!!!
            
    if discharge_n == None:
        discharge_n = 0.7
        print "The discharge efficiency has not be specified and so has been set to 0.7"
        
    if charge_n == None:
        charge_n = 0.7
        print "The charge efficiency has not be specified and so has been set to 0.7"
        
    if replacement_time == None:
        replacement_time = 4
        print "No value given for replacement time so these batteries will be replaced every 4 years"
        
    # If there are a number of batteries multiple all battery fields by that number
    charge_n = charge_n*No_battery
    discharge_n = discharge_n*No_battery
    battery_capacity = battery_capacity*No_battery
    max_discharge = max_discharge*No_battery
    max_charge = max_charge*No_battery
    initial_charge = initial_charge*No_battery
    battery_cost = battery_cost*No_battery
    
    battery.append(simple_battery(name_,battery_zone,charge_n,discharge_n,battery_capacity,max_discharge,max_charge,initial_charge,battery_cost,replacement_time))

    HB_batteries = hb_hive.addToHoneybeeHive(battery, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HB_batteries

if checktheinputs(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost,battery_zone) != -1:
    
    HB_batteries = main(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost,battery_zone,replacement_time)





"""
def main(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost,battery_zone):
    
    batterycount = 0
    
    batteries = []
    
    for numbat,name,batcap,initialq,maxdischarge,maxcharge,dischargen,chargen,batcost in itertools.izip_longest(No_battery,name_,battery_capacity,initial_charge,max_discharge,max_charge,discharge_n,charge_n,battery_cost): 
        
        try:
            numbat = No_battery[batterycount]
        except IndexError:
            numbat = 1
                
        try:
            name_[batterycount]
        except IndexError:
            name = "Battery " + str(batterycount)
            
        try:
            battery_capacity[batterycount]
        except IndexError:
            batcap = battery_capacity[0]
            
        try:
            initial_charge[batterycount]
        except IndexError:
            initialq = initial_charge[0]
            
        try:
            max_discharge[batterycount]
        except IndexError:
            maxdischarge = max_discharge[0]
            
        try:
            max_charge[batterycount]
        except IndexError:
            maxcharge = max_charge[0]
            
        try:
            discharge_n[batterycount]
        except IndexError:
            dischargen = discharge_n[0]
    
        try:
            charge_n[batterycount]
        except IndexError:
            chargen = charge_n[0]
            
        try:
            battery_cost[batterycount]
        except IndexError:
            batcost = battery_cost[0]
        
        for battery in numbat:
            
            batteries.extend(simple_battery(name,battery_zone,chargen,dischargen,batcap,maxdischarge,maxcharge,initialq))

        batterycount = batterycount+1
           
    HB_batteries = hb_hive.addToHoneybeeHive(batteries, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
"""