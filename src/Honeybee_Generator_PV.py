# By Anton Szilasi
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Provided by Honeybee 0.0.56

Use this component to add Energy Plus Photovoltaic generators to a Honeybee Surface, at present only Photovoltaic generators with Simple Photovoltaic performance objects are supported. Each surface can only have one Photovoltaic generator.
For each Photovoltaic generator there must be a inverter for power to be produced, if several photovoltaic generators are modelled in the same generatorsystem (Connected to the generationsystem component) these generators must have the same inverter.

For more information about Photovolatic generators please see: http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#photovoltaic-generators



-
Provided by Honeybee 0.0.56

    Args:
        _HBSurfaces: A Honeybee/context surface or a list of Honeybee/context surfaces to which one Photovolatic generator will be mounted on each surface.
        name_: An optional input, a name or a list of names of PV generators which correspond sequentially to the _HBSurfaces. Without this input PV generators will be assigned default names.
        SA_solarcells: A float or a list of floats as fraction of the fraction of the Honeybee surfaces, in the field above that are covered with Photovoltaics.
        cells_n: A float or a list of floats as a fraction of the efficiency of the Photovoltaic generator cells which correspond sequentially to _HBSurfaces.
        _integrationmode: EnergyPlus allows for different ways of integrating with other EnergyPlus heat transfer surfaces and models and calculating Photovoltaic cell temperature. This field is a integer or a list of integers sequentially to _HBSurfaces between 1 and 6 that defines the heat transfer integration mode used in the calculations as one of the following options. Decoupled a value of 1, DecoupledUllebergDynamic a value of 2, IntegratedSurfaceOutsideFace a value of 3, IntegratedTranspiredCollector a value of 4, IntegratedExteriorVentedCavity a value of 5, PhotovoltaicThermalSolarCollector a value of 6. The default is 1 the Decoupled mode. More information about each mode can be found on page 1767 and 1768 of the Energyplus Input Output reference.
        No_parallel: A integer or a list of integers sequentially to _HBSurfaces thats defines the series-wired strings of PV modules that are in parallel to form the PV generator on the surface. The product of this field and the next field will equal the total number of modules in the PV generator
        No_series: A integer or a list of integers sequentially to _HBSurfaces thats defines number of modules wired in series (on each string) to form the PV generator on the surface. The product of this field and the previous field will equal the total number of modules in the PV generator.
        _invertername: An optional input 
        inverter_n: The efficiency of the inverter as a fraction the default is 0.9  - Only one inverter can be definied per component the inverter here is common across all the PV generators from this component.
        inverter_zone: To place the inverter in a zone - (The zone will gain additional heat from the inverter) connect one Honeybee zone here.
        inverter_cost: The cost of the inverter
    
    Returns:
        PV_HBSurfaces: The Honeybee/context surfaces that have been modified by this component - these surfaces now contain PV generators to run in an Energy Plus simulation connect them to the HBContext_ input of the Honeybee_ Run Energy Simulation component to run in an EnergyPlus simulation.
        
"""

ghenv.Component.Name = "Honeybee_Generator_PV"
ghenv.Component.NickName = 'PVgen'
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


hb_hive = sc.sticky["honeybee_Hive"]()
EP_zone = sc.sticky["honeybee_EPZone"] 
PV_gen = sc.sticky["PVgen"] # Linked to class PV_gen in honeybee honeybee Note to self: ask chris how to make ["PVgen"] a class within EP_zone
hb_hivegen = sc.sticky["honeybee_generationHive"]()


def checktheinputs(_name,_HBSurfaces,SA_solarcells,cells_n,_integrationmode,No_parallel,No_series):

    """This function checks all the inputs of the component to ensure that the component is stopped if there is anything wrong with the inputs ie the 
    inputs will produce serious errors in the execution of this component.
        
        Args:
            The arguements seen in the function definition are the same as the arguements on the panel.
            
        Returns:
            If there are any issues with the inputs this function will return -1 and the component will stop"""
          
    # Check if the Honeybee hive is on the sticky
    
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    # Check if it is the latest Honeybee release 
    """
    #XXX this is returning index out of range not sure why?
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
        """
        
    # Check that Honeybee Zones are connected
        
    if len(PV_inverter) != 1:
        
        print " There can only be one inverter for each PV generator please connect only one inverter!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "There can only be one inverter for each PV generator please connect only one inverter!")
        return -1
        
    
    if (_HBSurfaces == []) or (_HBSurfaces[0] == None) :
        print "PV generators must be mounted on at least one Honeybee surface or context surface please connect a Honeybee surface to _HBSurfaces!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "PV generators must be mounted on at least one Honeybee surface or context surface please connect a Honeybee surface to _HBSurfaces!")
        return -1
        
    if (SA_solarcells == []) or (SA_solarcells[0]) == None:
        print "SA_solarcells must contain one or a number of decimal floats!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "SA_solarcells must contain one or a number of decimal floats!")
        return -1
       
    if (cells_n == []) or (cells_n[0]) == None:
        print "cells_n must contain one or a number of decimal floats!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "cells_n must contain one or a number of decimal floats!")
        return -1
        
        
    if (_integrationmode == []) or (_integrationmode[0]) == None:
        print "_integrationmode must contain one or a number of integers between 1 and 6!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "_integrationmode must contain one or a number of integers between 1 and 6!")
        return -1
        
    if (cost_module == []) or (cost_module[0]) == None:
        print "Cost of module must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Cost of module must be specified!")
        return -1
        
    for cell_n in cells_n:
            
        if (cell_n >1) or (cell_n < 0):
            
            print "All values of cells_n must be between 1 and zero as it is a efficiency!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "All values of cells_n must be between 1 and zero as it is a efficiency!")
            return -1
        
    for SA_solarcell in SA_solarcells:
        
        if (SA_solarcell >1) or (SA_solarcell < 0):
            print "SA_solarcell must be between 1 and zero as it is a fraction!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "SA_solarcell must be between 1 and zero as it is a fraction!")
            return -1
            
    for mode1 in _integrationmode:
    
        if (mode1 > 6) or (mode1 < 1):
            print "_integrationmode must be an integer between 1 and 6!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "_integrationmode must be an integer between 1 and 6!")
            return -1
            
    for PVgencount in range(len(_HBSurfaces)):
        
        try:
            _HBSurfaces[PVgencount]
        except IndexError:
            warnMsg= "Every PV generator must have a corresponding surface connected through the field _HBSurfaces! "
            print warnMsg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warnMsg)
            return -1 
    
    if (power_output == []) or (power_output[0]) == None:
        print "The power output of the module must be specified!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The power output of the module must be specified!")
        return -1
        
        
def returnmodename(mode):
    """ This function converts _integrationmode from an int on the panel to a string for the Generator:Photovoltaic Heat Transfer integration mode"""
    if mode == 1:
        return "Decoupled"
    if mode ==2:
        return "DecoupledUllebergDynamic"
    if mode ==3:
        return "IntegratedSurfaceOutsideFace"
    if mode==4:
        return "IntegratedTranspiredCollector"
    if mode==5:
        return "IntegratedExteriorVentedCavity"
    if mode==6:
        return "PhotovoltaicThermalSolarCollector"


def main(_name,_HBSurfaces,SA_solarcells,cells_n,_integrationmode,No_parallel,No_series,cost_module,power_output,PVinverter):
 
    """ This function is the heart of this component it takes all the component arguments and writes one PV generator onto each Honeybee surface connected to this component
 
     Args:
            The arguements seen in the function definition are the same as the arguements on the panel.
                
        Returns:
            The properties of the PV generators connected to this component these properties are then written to an IDF file in Honeybee_ Run Energy Simulation component.
    """
    
    HBSurfacesfromhive = hb_hive.callFromHoneybeeHive(_HBSurfaces) # Call Honeybee surfaces from hive
    
    PVgencount = 0
    
    for name,surface,SA_solarcell,celleff,mode,parallel,series,modelcost,powerout in itertools.izip_longest(_name,HBSurfacesfromhive,SA_solarcells,cells_n,_integrationmode,No_parallel,No_series,cost_module,power_output): 
        
        surface.containsPVgen = True # Set this it true so the surface can be identified in run and write IDF component
        
        surface.PVgenlist = [] # Set the PVgenlist of each surface back to empty otherwise PVgen objects will accumulate on each run
        
        namePVperform = "DefaultSimplePVperformance" + str(PVgencount)+ " " + str(surface.name) # Create a name for the PVperformance object for each PV generator - this is always created by automatically here not by the user
        
        try:
            name = name_[PVgencount]
        except IndexError:
            name = "PVgenerator" + str(PVgencount) + " " + str(surface.name) # If no name given for a PV generator assign one.
            
        try:
            SA_solarcells[PVgencount]
        except IndexError:
            
            SA_solarcell = 0.5
            print "No corresponding surface area fraction for " + str(name) +" "+ str(0.5) + " used"
            
        try:
            cells_n[PVgencount]
        except IndexError:
            
            celleff = 0.12
            print "No corresponding solar cell efficiency for " + str(name) +" "+ str(0.12) + " used"

        try:
            _integrationmode[PVgencount]
        except IndexError:
            mode = 1
            print "No corresponding integrationmode for "+ str(name) +" "+ str("Decoupled") + " used"
     
        try:
            No_parallel[PVgencount]
        except IndexError:
            
            parallel = 1
            
            print "No corresponding number of PV panels in parallel for "+ str(name) +" "+ str(parallel) + " panel/s in parallel used"

        try:
            No_series[PVgencount]
        except IndexError:
            series = 1
            print "No corresponding number of PV panels in series for "+ str(name) + " " + str(series) + " panel/s in series used"
        
        try:
            cost_module[PVgencount]
        except IndexError:
             modelcost = cost_module[0]
             print "No corresponding module cost for" + str(name) + " " + str(cost_module[0]) + " used instead"
        
        try:
            power_output[PVgencount]
        except IndexError:
            powerout = power_output[0]
            print "No corresponding power output for " + str(name) + " " + str(cost_module[0]) + " used instead"
                
        surface.PVgenlist.append(PV_gen(name,surface.name,returnmodename(mode),parallel,series,cost_module,powerout,namePVperform,SA_solarcell,celleff)) # Last three inputs are for instance method PV_performance
        
        # Assign the inverter to each PVgenerator.
        
        for PVgen in surface.PVgenlist:
            
            PVgen.inverter = PVinverter
            
        PVgencount = PVgencount+1
        
    ModifiedHBSurfaces = hb_hive.addToHoneybeeHive(HBSurfacesfromhive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return ModifiedHBSurfaces

# Call the PVinverter from the hive
PVinverter = hb_hivegen.callFromHoneybeeHive(PV_inverter)

if checktheinputs(name_,_HBSurfaces,SA_solarcells,cells_n,_integrationmode,No_parallel,No_series) != -1:
    
    PV_HBSurfaces = main(name_,_HBSurfaces,SA_solarcells,cells_n,_integrationmode,No_parallel,No_series,cost_module,power_output,PVinverter)
    