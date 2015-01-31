# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add Glazing

-
Provided by Honeybee 0.0.55

    Args:
        _HBSurface: A HBSurface
        EPConstruction_: Optional EnergyPlus construction
        childEPConstruction_: Optional EnergyPlus construction for child surface
    Returns:
        readMe!:...
        HBSurface: Modified Honeybee surface
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import os
import sys
import System
import Grasshopper.Kernel as gh
import uuid

ghenv.Component.Name = 'Honeybee_Set EP Surface Construction'
ghenv.Component.NickName = 'setEPSrfCnstr'
ghenv.Component.Message = 'VER 0.0.55\nJAN_31_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.55\nJAN_31_2015
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(HBSurface, EPConstruction, childEPConstruction):
    # import the classes
    if sc.sticky.has_key('honeybee_release'):

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
            
        # don't customize this part
        hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
        
        
        # call the surface from the hive
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBSurface = hb_hive.callFromHoneybeeHive([HBSurface])[0]
        
        # change construction for parent surface
        hb_EPObjectsAux.assignEPConstruction(HBSurface, EPConstruction, ghenv.Component)
        
        # change construction for child surface if any
        if HBSurface.hasChild:
            for childSurface in HBSurface.childSrfs:
                hb_EPObjectsAux.assignEPConstruction(childSurface, childEPConstruction, ghenv.Component)
        
        # send the HB surface back to the hive
        # add to the hive
        HBSurface  = hb_hive.addToHoneybeeHive([HBSurface], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
        return HBSurface
        
    else:
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1

if _HBSurface!=None and (EPConstruction_ or childEPConstruction_) :
    
    results = main(_HBSurface, EPConstruction_, childEPConstruction_)
    
    if results != -1:
        HBSurface = results