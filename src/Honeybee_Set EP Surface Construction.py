# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Add Glazing

-
Provided by Honeybee 0.0.56

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
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


def updateZoneMixing(surface1, zone1, zone2):
    #Change the air mixing between the zone and other zones to "True"
    zone1.mixAir = True
    zone2.mixAir = True
    
    #Append the zone to be mixed with to the mixAirZoneList.
    zone1.mixAirZoneList.append(zone2.name)
    zone2.mixAirZoneList.append(zone1.name)
    
    #Calculate a rough flow rate of air based on the cross-sectional area of the surface between them.
    flowFactor = zone1.mixAirFlowRate
    flowRate = (rc.Geometry.AreaMassProperties.Compute(surface1.geometry).Area)*flowFactor
    
    #Append the flow rate of mixing to the mixAirFlowList
    zone1.mixAirFlowList.append(flowRate)
    zone2.mixAirFlowList.append(flowRate)
    
    return flowRate

def checkAirWalls(construction, srf):
    if construction.ToUpper() == "AIR WALL":
        srf.setType(4, isUserInput= True)
        updateZoneMixing(srf, srf.parent, srf.BCObject.parent)


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
        
        # make sure it is not an interior wall - at some point I should find a way
        # to make this work but right now there is not a good solution to find adjacent zone
        if HBSurface.BCObject.name != "":
            msg = "Currently you can't change construction for an interior surface with this component." + \
                  "\nTry to use 1.creatHBSrf > 2.createHBZone > 3.SolveAdj as an alternate workflow."
            print msg
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, msg)
            return -1
        
        
        # change construction for parent surface
        hb_EPObjectsAux.assignEPConstruction(HBSurface, EPConstruction, ghenv.Component)
        if EPConstruction!=None and HBSurface.BCObject.name != "":
            hb_EPObjectsAux.assignEPConstruction(HBSurface.BCObject, EPConstruction, ghenv.Component)
            checkAirWalls(EPConstruction, HBSurface)
            
        # change construction for child surface if any
        if childEPConstruction!=None  and HBSurface.hasChild:
            for childSurface in HBSurface.childSrfs:
                hb_EPObjectsAux.assignEPConstruction(childSurface, childEPConstruction, ghenv.Component)
                if childSurface.BCObject.name != "":
                    hb_EPObjectsAux.assignEPConstruction(childSurface.BCObject, childEPConstruction, ghenv.Component)
                    checkAirWalls(childEPConstruction, childSurface.parent)
                    
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