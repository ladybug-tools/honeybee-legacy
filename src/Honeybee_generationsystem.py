# By Anton Szilasi
# Icon by Djordje Spasic
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""

Use this component to create a Honeybee generator system.

-
Provided by Honeybee 0.0.56

    Args:
        generatorsystem_name: The name of this Honeybee generation system please make it unique!
        maintenance_cost: The annual cost of maintaining this Honeybee generation system in whatever currency the user wishes (Just make it consisent with other components)
        PV_HBSurfaces: The Honeybee/context surfaces that contain PV generators to be included in this generation system
        HB_generationobjects: Honeybee batteries or wind turbines to be included in this generation system 
            
    Returns:
        HB_generatorsytem: The Honeybee generation system - connect this to the input HB_generators on the Honeybee_Run Energy Simulation component to include this generation system in an EnergyPlus simulaton
        
"""

ghenv.Component.Name = "Honeybee_generationsystem"
ghenv.Component.NickName = 'generationsystem'
ghenv.Component.Message = 'VER 0.0.56\nMAY_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP" #"06 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3" #"0"
except: pass

import scriptcontext as sc
hb_hive = sc.sticky["honeybee_Hive"]()
hb_hivegen = sc.sticky["honeybee_generationHive"]()
HB_generator = sc.sticky["HB_generatorsystem"]
wind_generator = sc.sticky["wind_generator"]
import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import itertools


def checHBgenobjects(PV_HBSurfaces,HB_generationobjects):
    
    try:
        PV_generation = hb_hive.callFromHoneybeeHive(PV_HBSurfaces)
        
    except:
        
        print "Only PV_HBSurfaces from the Honeybee_Generator_PV component can be connected to PV_HBSurfaces!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only PV_HBSurfaces from the Honeybee_Generator_PV component can be connected to PV_HBSurfaces!")
        return -1
        
    try:
        HB_generation = hb_hivegen.callFromHoneybeeHive(HB_generationobjects)
        
    except:
        print "Only HB_batteries and HB_windturbines can be connected to HB_generationobjects!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only HB_batteries and HB_windturbines can be connected to HB_generationobjects!")
        return -1

def checktheinputs(generatorsystem_name,PV_HBSurfaces,HB_generationobjects,maintenance_cost):
    
    if generatorsystem_name == None:
        
        print "Please specify a name for this generator system and make sure it is not the same as another generation system!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this generator system and make sure it is not the same as another generation system!")
        return -1
        
    if PV_HBSurfaces == [] and HB_generationobjects == []:
        return -1
    
    # Must also check that the first item is not a none otherwise will output a HB generator
    # when the first item is None and cause Energy Plus to crash!
    try:
        if PV_HBSurfaces[0] == None:
            return -1
    except:
        pass
        
    try:
        if HB_generationobjects[0] == None:
            return -1
    except:
        pass
        
    if maintenance_cost == None:
        
        print "Please specify the annual maintenance cost of this Honeybee generation system!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify the annual maintenance of this Honeybee generation system!")
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
        

    
    # Need a check only generators of certain types can be in the same list - AC,DC
        
       
# check only one inverter for this generation system
# Make sure that all the inverters for all the PV generators connected to this simulation are the same.


def main(PV_generation,HB_generation,maintenance_cost):
    
    simulationinverters = []  # The inverter for this generator system - (only one)
    PVgenerators = [] 
    windgenerators = []
    fuelgenerators = []
    
    HBgencontextsurfaces = []
    HBzonesurfaces = []
    
    battery = None
    HB_generators = [] # Called HB_generators even though will only ever be one Honeybee_generator
    
    # For Honeybee surfaces with PV generators attached to them append PVgenerators and inverter to HB_generator object
    # XXX rework code so PV generators and other generators can share the same input.
    
    for HBgenobject in PV_generation:
        
        if HBgenobject.containsPVgen == True:
            
            try:
                HBgenobject.type
                
                if HBgenobject.type == 6:
                    
                    HBgencontextsurfaces.append(HBgenobject)

                else:
                    
                    HBzonesurfaces.append(HBgenobject)
                    
            except AttributeError:
                pass
            
            for PVgen in HBgenobject.PVgenlist:
                
                PVgenerators.append(PVgen)
                
                # Append the inverter of each PV generator to the list
                simulationinverters.extend(PVgen.inverter)
    
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
        if all(inverter.ID == simulationinverters[0].ID for inverter in simulationinverters) == False: 
            print "Each generator system can only have one inverter servicing all the PV generators, make sure all connected PV have the same inverter! "
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Each generator system can only have one inverter servicing all the PV generators, make sure all connected PV have the same inverter!")
            return -1

    # Check for duplicate PVgenerators
    if checkduplicatesPVgenerators(PVgenerators) != -1:

    # Checking that all PV generators have the same inverter if not component will stop
        if checkinverter(simulationinverters) != -1:
            
            for HBgenobject in HB_generation:
                
                if HBgenobject.type == 'Battery:simple':  
                    # The battery for this generation system (only one)
                    
                    global battery
                    battery = HBgenobject
                    
                if HBgenobject.type == 'Generator:WindTurbine':
                    
                    windgenerators.append(HBgenobject)
                    
                # XXX if fuel generator append to fuelgenerator list
    
            # Make sure that PV generators, Wind generators and Fuel generatos CANNOT be in the same list as according to EnergyPlus documentation
        
            def PVwindandbattery(PVgenerators,windgenerators,battery):
        
                if PVgenerators == [] and windgenerators == [] and battery != None:
                    
                    print "Only a battery has been detected please connect generators to this component! "
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, "Only a battery has been detected please connect generators to this component! ")
                    return -1 
                
            def PVandwind(PVgenerators,windgenerators):
                
                if PVgenerators != [] and windgenerators != []:
                    
                    print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
                    return -1
            
            def windandfuel(windgenerators,fuelgenerators):
                
                if windgenerators != [] and fuelgenerators != []:
                    
                    print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
                    return -1
            
            def PVandfuel(PVgenerators,fuelgenerators):
                
                if PVgenerators != [] and fuelgenerators != []:
            
                    print "Please ensure that only one type of generator (PV or Wind) is connected to this component "
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, "Please ensure that only one type of generator (PV or Wind) is connected to this component ")
                    return -1
                
            def windandbat(windgenerators,battery):
                
                if windgenerators != [] and battery != None:
                    
                    print "Batteries cannot be connected to an AC system please disconnect the battery from this component!"
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, "Batteries cannot be connected to an AC system please disconnect the battery from this component!")
                    return -1
                    
            if PVwindandbattery(PVgenerators,windgenerators,battery) != -1:
                    
                    if PVandwind(PVgenerators,windgenerators) != -1:
                        
                        if windandfuel(windgenerators,fuelgenerators) != -1:
                            
                            if PVandfuel(PVgenerators,fuelgenerators) != -1:
                                
                                if windandbat(windgenerators,battery) != -1:

                                    HB_generators.append(HB_generator(generatorsystem_name,simulationinverters,battery,windgenerators,PVgenerators,fuelgenerators,HBgencontextsurfaces,HBzonesurfaces,maintenance_cost))
                                    
                                    HB_generator1 = hb_hivegen.addToHoneybeeHive(HB_generators,ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
                                    
                                    return HB_generator1
        

if checktheinputs(generatorsystem_name,PV_HBSurfaces,HB_generationobjects,maintenance_cost) != -1:   

    if checHBgenobjects(PV_HBSurfaces,HB_generationobjects) != -1:
   
        PV_generation = hb_hive.callFromHoneybeeHive(PV_HBSurfaces)
        
        HB_generation = hb_hivegen.callFromHoneybeeHive(HB_generationobjects)

        if checkbattery(HB_generation) != -1:
        
                HB_generatorsytem = main(PV_generation,HB_generation,maintenance_cost)

