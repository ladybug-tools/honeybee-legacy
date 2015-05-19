# Created By Anton Szilasi
# Icon by Djordje Spasic
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Provided by Honeybee 0.0.56

Use this component to add EnergyPlus simple inverters to a Energy Plus simulation.

Find out more information about Energy Plus simple inverters here:
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#electricloadcenterinvertersimple

-
Provided by Honeybee 0.0.56

    Args:
        
        _invertername: The inverter name - Make it unique from other inverters
        inverter_n: The efficiency of the inverter by default this is 90%
        inverter_cost: The cost the inverter in whatever currency the user wishes - Just make it consistent with other components you are using
        replacement_time: Specify how often in years the inverter will need to be replaced. The default is 5 years.
        
    Returns:
        HB_inverter: Honeybee inverter- to include this inverter in a generation system connect it to the input HB_generationobjects on the Honeybee_generationsystem component 
        
"""

ghenv.Component.Name = "Honeybee_simple_Inverter"
ghenv.Component.NickName = 'simple_Inverter'
ghenv.Component.Message = 'VER 0.0.56\nAPR_23_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP" #"06 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3" #"0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

hb_hivegen = sc.sticky["honeybee_generationHive"]()
PVinverter = sc.sticky["PVinverter"] 
inverter_zone = None
    
def checktheinputs(_invertername,inverter_n,inverter_cost,inverter_zone):
    
    if inverter_cost == None:
        warnMsg= "The cost of the inverter must be specified!"
        print warnMsg
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnMsg)
        return -1 
        
    if _invertername== None:
        print "Please specify a name for the inverter and make sure it is not the same as another inverter!"
        w = gh.GH_RuntimeMessageLevel.Warning ## Need to create a check so that inverters cant have duplicate names!
        ghenv.Component.AddRuntimeMessage(w, "Please specify a name for the inverter and make sure it is not the same as another inverter!")
        return -1
    
    if inverter_n == None:
        print "No value given for inverter efficiency 0.9 used"
        
        
        
if checktheinputs(_invertername,inverter_n,inverter_cost,inverter_zone) != -1:
    
    if replacement_time == None:
        
        replacement_time = 5
        print "No value given for replacement time so this inverter will be replaced every 5 years"
    
    HB_inverter = hb_hivegen.addToHoneybeeHive([PVinverter(_invertername,inverter_cost,inverter_zone,inverter_n,replacement_time)], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))