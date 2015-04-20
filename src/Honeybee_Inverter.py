# By Anton Szilasi
# For technical support or user requests contact me at
# ajszilas@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Provided by Honeybee 0.0.56

Use this component to create simple inverters to be included in Photovoltaic systems. 

Find out more about simple inverters here:
http://bigladdersoftware.com/epx/docs/8-2/input-output-reference/group-electric-load-center.html#electricloadcenterinvertersimple
-
Provided by Honeybee 0.0.56

    Args:
        _invertername: The name of the inverter
        inverter_n: An optional input - the efficiency of the inverter converting DC electricity to AC electricity. The default efficiency is 90%
        inverter_cost: The cost of the inverter in whatever currency the user wishes - Just make it consistent with other components you are using

    Returns:
        HB_inverter: The Honeybee inverter to use it in a EnergyPlus simulation connect it to the PV_inverter input of the Honeybee_Generator_PV component
        
"""

ghenv.Component.Name = "Honeybee_Inverter"
ghenv.Component.NickName = 'Inverter'
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
    
    HB_inverter = hb_hivegen.addToHoneybeeHive([PVinverter(_invertername,inverter_n,inverter_cost,inverter_zone)], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))