#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Anton Szilasi - Icon by Djordje Spasic <ajszilas@gmail.com> 
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

Use this component to create a Honeybee generator system.

-
Provided by Honeybee 0.0.64

    Args:
        _GeneratorSystemName: The name of this Honeybee generation system please make it unique!
        _MaintenanceCost: The annual cost of maintaining this Honeybee generation system in US dollars (Other currencies will be available in the future)
        PVHBSurfaces_: The Honeybee/context surfaces that contain PV generators to be included in this generation system
        HBGenerationObjects_: Honeybee batteries or wind turbines to be included in this generation system 
            
    Returns:
        HBGeneratorSystem: The Honeybee generation system - connect this to the input HB_generators on the Honeybee_Run Energy Simulation component to include this generation system in an EnergyPlus simulaton
        
"""

ghenv.Component.Name = "Honeybee_generationsystem"
ghenv.Component.NickName = 'generationsystem'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import itertools

global _MaintenanceCost
_MaintenanceCost = 300


def checHBgenobjects(PVHBSurfaces_,HBGenerationObjects_):
    
    try:
        PV_generation = hb_hive.callFromHoneybeeHive(PVHBSurfaces_)
        
    except:
        
        print "Only PVHBSurfaces_ from the Honeybee_Generator_PV component can be connected to PVHBSurfaces_!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only PVHBSurfaces_ from the Honeybee_Generator_PV component can be connected to PVHBSurfaces_!")
        return -1
        
    try:
        HB_generation = hb_hivegen.callFromHoneybeeHive(HBGenerationObjects_)
        
    except:
        print "Only HB_batteries and HB_windturbines can be connected to HBGenerationObjects_!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Only HB_batteries and HB_windturbines can be connected to HBGenerationObjects_!")
        return -1

def checktheinputs(_GeneratorSystemName,PVHBSurfaces_,HBGenerationObjects_,_MaintenanceCost):
    
    if not sc.sticky.has_key("honeybee_release") or not sc.sticky.has_key("honeybee_ScheduleLib"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")

        return -1

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
        
    if _GeneratorSystemName == None:
        
        print "Please specify a name for this generator system and make sure it is not the same as another generation system!  "
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for this generator system and make sure it is not the same as another generation system!")
        return -1
    

    # If no inputs do not let the component run and output something other than Null
    # will cause problems in Run Energy Simulation 
    if PVHBSurfaces_ == [] and HBGenerationObjects_ == []:
        
        warn =  "A Honeybee generation system cannot be created without Honeybee generators! \n"+ \
        "Please connect Wind turbines to HBGenerationObjects_ or PV generators to PVHBSurfaces_ to create a Honeybee generation system."
        
        print warn
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        
        return -1
    
    # Must also check that the first item is not a none otherwise will output a HB generator
    # when the first item is None and cause Energy Plus to crash!
    try:
        if PVHBSurfaces_[0] == None:
            return -1
    except:
        pass
        
    try:
        if HBGenerationObjects_[0] == None:
            return -1
    except:
        pass
        


            
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


def main(PV_generation,HB_generation,_MaintenanceCost):
    
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
        
        #print HBgenobject
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

                                    HB_generators.append(HB_generator(_GeneratorSystemName,simulationinverters,battery,windgenerators,PVgenerators,fuelgenerators,HBgencontextsurfaces,HBzonesurfaces,_MaintenanceCost))

                                    HB_generator1 = hb_hivegen.addToHoneybeeHive(HB_generators,ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
                                    
                                    return HB_generator1
        

if checktheinputs(_GeneratorSystemName,PVHBSurfaces_,HBGenerationObjects_,_MaintenanceCost) != -1:

    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_hivegen = sc.sticky["honeybee_generationHive"]()
    HB_generator = sc.sticky["HB_generatorsystem"]
    wind_generator = sc.sticky["wind_generator"]

    if checHBgenobjects(PVHBSurfaces_,HBGenerationObjects_) != -1:
   
        PV_generation = hb_hive.callFromHoneybeeHive(PVHBSurfaces_)
        
        HB_generation = hb_hivegen.callFromHoneybeeHive(HBGenerationObjects_)

        if checkbattery(HB_generation) != -1:
        
                HBGeneratorSystem = main(PV_generation,HB_generation,_MaintenanceCost)

