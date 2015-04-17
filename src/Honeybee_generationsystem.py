import scriptcontext as sc
hb_hive = sc.sticky["honeybee_Hive"]()
hb_hivegen = sc.sticky["honeybee_generationHive"]()
HB_generator = sc.sticky["HB_generatorsystem"]
wind_generator = sc.sticky["wind_generator"]

ghenv.Component.Name = "Honeybee_generationsystem"
ghenv.Component.NickName = 'generationsystem'
ghenv.Component.Message = 'VER 0.0.56\nAPR_17_2015'
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

PV_generation = hb_hive.callFromHoneybeeHive(PV_HBSurfaces)
HB_generation = hb_hivegen.callFromHoneybeeHive(HB_generationobjects)

def checktheinputs(generatorsystem_name):
    
    if generatorsystem_name == None:
        
        print "Please specify a name for this generator system and make sure it is not the same as another generation system!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this generator system and make sure it is not the same as another generation system!")
        return -1


def checkbattery(HB_generation):
    
    # Check that there is only one battery connected to this component
    batterycount = 0
    
    for HBgenobject in HB_generation: 
        
        if HBgenobject.type == 'Battery:simple': 
            
            batterycount = batterycount +1 
            
        """
        if isinstance(HBgenobject,sc.sticky["battery"]): # XXX need to create ElectricLoadCenter:Storage:Battery
            
            batterycount = batterycount +1
        """
            
    if batterycount > 1:
        print "There can only be one battery for each generation system. Please make sure only one battery is connected to this component"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "There can only be one battery for each generation system! Please make sure only one battery is connected to this component")
        return -1
        
    if gridelect_cost == None:
        
        print "The cost of grid electricty per Kwh must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The cost of grid electricty per Kwh must be specified!")
        return -1

    ### Need a check only generators of certain types can be in the same list - AC,DC
        
       
# check only one inverter for this generation system
# Make sure that all the inverters for all the PV generators connected to this simulation are the same.


def main(PV_generation,HB_generation):
    
    simulationinverters = []  # The inverter for this generator system - (only one)
    PVgenerators = [] 
    windgenerators = []
    fuelgenerators = []
    
    battery = None
    HB_generators = [] # Called HB_generators even though will only ever be one Honeybee_generator
    
    # For Honeybee surfaces with PV generators attached to them append PVgenerators and inverter to HB_generator object
    # XXX rework code so PV generators and other generators can share the same input.
    
    for HBgenobject in PV_generation:
            
        if HBgenobject.containsPVgen == True:
            
            for PVgen in HBgenobject.PVgenlist:
                
                PVgenerators.append(PVgen)
                
                # Append the inverter of each PV generator to the list
                simulationinverters.append(PVgen.inverter) 

    def checkduplicatesPVgenerators(PVgenerators):
        
        seen = set(PVgenerators)
        uniq = []
        for PVgen in PVgenerators:
            if PVgen not in seen:
                uniq.append(x)
                seen.add(x)
                
        if len(PVgenerators) != len(seen):
            print "Duplicate PVgenerators detected,Please make sure you are not connecting the same PV generators twice!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Duplicate PVgenerators detected,Please make sure you are not connecting the same PV generators twice! ")
            return -1
            
    
    def checkinverter(simulationinverters): 
        if all(inverter == simulationinverters[0] for inverter in simulationinverters) == False: 
            print "Each generator system can only have one inverter servicing all the PV generators, make sure all connected PV have the same inverter! "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Each generator system can only have one inverter servicing all the PV generators, make sure all connected PV have the same inverter!")
            return -1
    
    # Check for duplicate PVgenerators
    if checkduplicatesPVgenerators(PVgenerators) != -1:

    # Checking that all PV generator inverters have the same inverter
        if checkinverter(simulationinverters) != -1:
            
            for HBgenobject in HB_generation:
                
                if HBgenobject.type == 'Battery:simple':  
                    # The battery for this generation system (only one)
                    
                    global battery
                    battery = HBgenobject
                    
                if HBgenobject.type == 'Generator:WindTurbine':
                    
                    windgenerators.append(HBgenobject)
                    
                #if fuel generator append to fuelgenerator list
    
        # Make sure that PV generators, Wind generators and Fuel generatos CANNOT be in the same list as according to EnergyPlus documentation
        
        if PVgenerators == [] and windgenerators == [] and battery != None:
            
            print "Only a battery has been detected please connect generators to this component! "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Only a battery has been detected please connect generators to this component! ")
        
        if PVgenerators != [] and windgenerators != []:
            
            print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
        
        elif windgenerators != [] and fuelgenerators != []:
            
            print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
        
        elif PVgenerators != [] and fuelgenerators != []:
    
            print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
        
        if windgenerators != [] and battery != None:
            
            print "Batteries cannot be connected to an AC system please disconnect the battery from this component!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Batteries cannot be connected to an AC system please disconnect the battery from this component!")
        
        # If only one type of generator is present continue....
        else:
    
            HB_generators.append(HB_generator(generatorsystem_name,simulationinverters,battery,windgenerators,PVgenerators,fuelgenerators,gridelect_cost))
            
            HB_generator1 = hb_hivegen.addToHoneybeeHive(HB_generators,ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
            
            return HB_generator1
        
if checktheinputs(generatorsystem_name) != -1:
    
    if checkbattery(HB_generation) != -1:
    
        HB_generator = main(PV_generation,HB_generation)

