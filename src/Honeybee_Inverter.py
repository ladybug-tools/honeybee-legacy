ghenv.Component.Name = "Honeybee_Inverter"
ghenv.Component.NickName = 'Inverter'
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
    
    HB_inverter = hb_hivegen.addToHoneybeeHive([PVinverter(_invertername,inverter_cost,inverter_zone,inverter_n)], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))