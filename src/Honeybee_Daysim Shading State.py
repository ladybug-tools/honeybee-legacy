# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim Shading State for Advanced Dynamic Shading
-
Provided by Honeybee 0.0.54
    
    Args:
        shdHBObjects: A list of HB Objects that define the shading geometry and materials
        minIlluminance: Optional minimum illuminance in lux to open the blind. If you want the blinds to be manually controlled leave this input empty.
        maxIlluminance: Optional maximum illuminance in lux to close the blind. If you want the blinds to be manually controlled leave this input empty.
        
    Returns:
        shadingState: Shading state
"""

ghenv.Component.Name = "Honeybee_Daysim Shading State"
ghenv.Component.NickName = 'DSShadingState'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

class ShadingState(object):
    
    def __init__(self, shdHBObjects, minIlluminance, maxIlluminance):
        self.shdHBObjects = shdHBObjects
        self.minIlluminance = minIlluminance
        self.maxIlluminance = maxIlluminance
        
        if maxIlluminance==None:
            self.controlSystem = "ManualControl"
        else:
            self.controlSystem = "AutomatedThermalControl"


def main(shdHBObjects, minIll, maxIll):
    msg = None
    
    if not sc.sticky.has_key("honeybee_release"):
        msg = "You should let Honeybee fly first!"
        return msg, None
    
    # check if the objects are valid Honeybee objects
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(shdHBObjects)
    
    if len(HBObjectsFromHive)==0 or len(HBObjectsFromHive)!= len(shdHBObjects):
        msg = "At the minimum one of the shdHBObjects is not a valid Honeybee object."
        return msg, None
        
    # make sure min and max are both provided
    if (minIll== None and maxIll!=None) or (minIll!= None and maxIll==None):
        msg = "You need to either provide both minimum and maximum illuminance values so the control system will be considered as automated control\n " + \
              "or provide none of them so the system will be considered as manual."
        return msg, None
        
    return msg, ShadingState(shdHBObjects, minIll, maxIll)

if len(shdHBObjects)!=0:
    
    msg, shadingState = main(shdHBObjects, minIlluminance, maxIlluminance)
    
    if msg!=None:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
