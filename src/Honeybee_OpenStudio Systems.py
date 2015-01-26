# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
OpenStudio Systems
-
Provided by Honeybee 0.0.55

    Args:
        _HBZones:...
        _HVACSystems: ...
        _airSideDetails_: Use Honeybee_OpenStudio detail component to define the details
        _seeHVACDesc_: Set to True to see the HVAC system description
    Returns:
        HBZones:...
"""
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc
import uuid
import pprint


ghenv.Component.Name = "Honeybee_OpenStudio Systems"
ghenv.Component.NickName = 'OSHVACSystems'
ghenv.Component.Message = 'VER 0.0.55\nOCT_16_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "09 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

def main(HBZones, HVACSystems,seeHVACDesc):
    # check for Honeybee
    results = []
    
    if sc.sticky.has_key('honeybee_release'):
    
    # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
        # HVAC Group ID
        
        #create a single HVAC Group ID to create a unique reference to the HVAC details imported (or none if none)
        HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
        # assign the systems
        for zoneCount, zone in enumerate(HBZonesFromHive):
            results.append('zone: ' + str(zoneCount + 1))
            try: 
                #in the case where the user enters multiple HVAC Indices
                HVACIndex = HVACSystems[zoneCount]
                
                results.append('creating HVAC descriptions for Honeybee zones (method 1)')
                #and they enter different HVAC details for each HVAC Index (not ideal, but possible)
                if (len(_airSideDetails_) > 1):
                    results.append('Individual details have been supplied by user for each system, which will be assigned to each.')
                    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                    zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
                    results.append('HVAC detail ' +str(zoneCount+1)+ ' has been applied to this HVAC system.')
                    if(seeHVACDesc):
                        results.append(_airSideDetails_[zoneCount].d)
                else:
                    #there is only one detail, or no details
                    if len(_airSideDetails_) == 1: 
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, _plantDetails_[0].d]
                            results.append('your single HVAC detail has been applied to this HVAC system with plant description.')
                            if(seeHVACDesc):
                                results.append(_airSideDetails_[zoneCount].d)
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, None]
                            results.append('your single HVAC detail has been applied to this HVAC system without plant description.')
                    else: 
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                            results.append('honeybee defaults will be applied to this HVAC system with your plant description.')
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None, None]
                            results.append('honeybee defaults will be applied to this HVAC system and plant description.')
                results.append('HVAC system unique id: ' + HVACGroupID)
            except: 
                HVACIndex = HVACSystems[0]
                results.append('creating HVAC descriptions for Honeybee zones (method 2)')
                if (len(_airSideDetails_) > 1):
                    results.append('Individual details have been provided for the HVAC Systems, which will be applied now.')
                    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                    zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
                    results.append('HVAC detail ' +str(zoneCount+1)+ ' has been applied to this HVAC system.')
                    if(seeHVACDesc):
                        results.append(_airSideDetails_[zoneCount].d)
                else:
                    #there is only one detail, or no details
                    if len(_airSideDetails_) == 1: 
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,_plantDetails_[0].d]
                            print _airSideDetails_[0].d
                            results.append('your single HVAC detail has been applied to this HVAC system with plant description.')
                            results.append('HVAC system unique id: ' + HVACGroupID)
                            if(seeHVACDesc):
                                results.append(_airSideDetails_[0].d)
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,None]
                    else: 
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                            results.append('honeybee defaults will be used for the HVAC system and plant description.')
                            results.append('HVAC system unique id: ' + HVACGroupID)
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,None]
                            results.append('honeybee defaults will be used for the HVAC system')
                    results.append('Index: ' + str(HVACIndex) + ' applied to this zone.')
                results.append('HVAC system unique id: ' + HVACGroupID)
        # send the zones back to the hive
        HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        for zone in HBZones:
            print zone
        
    else:
        results.append("You should first let Honeybee to fly...")
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")

    return HBZones,results
    
if _HBZones and _HVACSystems:
    pp = pprint.PrettyPrinter(indent=4)
    if _seeHVACDesc_ == None:
        _seeHVACDesc_ = False
        
    HBZones,out = main(_HBZones, _HVACSystems, _seeHVACDesc_)
    for o in out:
        if type(o) is dict:
            if _seeHVACDesc_: pp.pprint(o)
        else:
            print o