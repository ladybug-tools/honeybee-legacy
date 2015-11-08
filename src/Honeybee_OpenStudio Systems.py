#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
OpenStudio Systems, without the inputs in _airSideDetails_ and _plantDetails_ default Open Studio systems will be created.
-
Provided by Honeybee 0.0.58

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
import json


ghenv.Component.Name = "Honeybee_OpenStudio Systems"
ghenv.Component.NickName = 'OSHVACSystems'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        
        
class checkHVACSystemID(object):
    """ If airside details are connected checks that _HVACSystems and _HVACSystemID in airside details are consisent will only print warn1 once but warn2 up to how many zones there are"""
    _instance = None
	
    def __new__(self,*args,**kwargs):

        self._instance = super(checkHVACSystemID,self).__new__(self)

            
    @classmethod
    def warningsForHBZone(cls,HBzone,HVACsystem,systemAirSideDetails):
	    
        if HVACsystem != systemAirSideDetails.d['HVACID']:
            
            if cls._instance == None:
                
                warn1 =  'The HVAC System specified in the connected component AirHandlerDetails and this component must be the same for each HB zone! \n'+\
                'One or several HB zones have been found that have this inconsistency. They are listed below.'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warn1)
            
            warn2 = 'Honeybee zone '+HBzone.name+' does not have the same HVACsystem defined in this component and the AirHandlerDetails component \n'+\
            'so no changes have been made to this zone in this component'
                
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warn2)
            
            return -1
	    
	    
def main(HBZones, HVACSystems,seeHVACDesc):
    # check for Honeybee
    results = {}
    systems={}
    
    if sc.sticky.has_key('honeybee_release'):
    
    # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
        # HVAC Group ID
        
        #create a single HVAC Group ID to create a unique reference to the HVAC details imported (or none if none)
        HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
        # assign the systems
        newZoneList = []
        for zoneCount, zone in enumerate(HBZonesFromHive):
            
            try: 
                #in the case where the user enters multiple HVAC Indices
                HVACIndex = HVACSystems[zoneCount]
                
                # Conduct checks here
                
                #results.append('creating HVAC descriptions for Honeybee zones (method 1)')
                #and they enter different HVAC details for each HVAC Index (not ideal, but possible)
                if (len(_airSideDetails_) > 1):
                
                    #results.append('Individual details have been supplied by user for each system, which will be assigned to each.')
                    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                    
                    if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                        
                        zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
                    
                    #results.append('HVAC detail ' +str(zoneCount+1)+ ' has been applied to this HVAC system.')
                else:
                    #there is only one detail, or no details
                    if len(_airSideDetails_) == 1:
                        
                        if len(_plantDetails_) == 1:
                            
                            if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                                
                                zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, _plantDetails_[0].d]
                                #results.append('your single HVAC detail has been applied to this HVAC system with plant description.')
                                if(seeHVACDesc):
                                    #this is simple, because there is only one airside system, so all zones will be added
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                    else:
                                        for system in results:
                                            system['zones'].append(zone.name)
                        else:
                            if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                                
                                # This code running 
                                zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, None]
                                
                                if(seeHVACDesc):
                                    #this is simple, because there is only one airside system, so all zones will be added
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                    else:
                                        for system in results:
                                            system['zones'].append(zone.name)
                    else:
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                            
                            #print _plantDetails_[0].d
                            
                            if(seeHVACDesc):
                                #this is simple, because there is only one airside system, so all zones will be added
                                if len(results)==0:
                                    newZoneList.append(zone.name)
                                    aside = _airSideDetails_[zoneCount].d
                                    aside['zones']=newZoneList
                                    results[HVACGroupID]=aside
                                    
                                else:
                                    for system in results:
                                        system['zones'].append(zone.name)
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None, None]
                            if(seeHVACDesc):
                                #this is simple, because there is only one airside system, so all zones will be added
                                if len(results)==0:
                                    newZoneList.append(zone.name)
                                    aside = _airSideDetails_[zoneCount].d
                                    aside['zones']=newZoneList
                                    results[HVACGroupID]=aside
                                else:
                                    for system in results:
                                        system['zones'].append(zone.name)
                                        
                                        
            except IndexError: 
                HVACIndex = HVACSystems[0]
                
                # Check that HVAC system inputs in airside components and this component are consisent!
                
                #results.append('creating HVAC descriptions for Honeybee zones (method 2)')
                if (len(_airSideDetails_) > 1):
                    #results.append('Individual details have been provided for the HVAC Systems, which will be applied now.')
                    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                    
                    if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                        
                        zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
                        #results.append('HVAC detail ' +str(zoneCount+1)+ ' has been applied to this HVAC system.')
                        
                else:
                    #there is only one detail, or no details
                    if len(_airSideDetails_) == 1:
                        
                        if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[0]) != -1:
                            
                            if len(_plantDetails_) == 1:
                                
                                zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,_plantDetails_[0].d]
                                #print _airSideDetails_[0].d
                                #results.append('your single HVAC detail has been applied to this HVAC system with plant description.')
                                #results.append('HVAC system unique id: ' + HVACGroupID)
                                if(seeHVACDesc):
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                        pp.pprint(results)
                                    else:
                                        for systemname,vals in results.items():
                                            print systemname
                                            vals['zones'].append(zone.name)
                            else:
                                zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,None]
                                if(seeHVACDesc):
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                    else:
                                        for system in results:
                                            system['zones'].append(zone.name)
                        else: 
                            if len(_plantDetails_) == 1:
                                zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                                if(seeHVACDesc):
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                    else:
                                        for system in results:
                                            system['zones'].append(zone.name)
                            else:
                                zone.HVACSystem = [HVACGroupID, HVACIndex, None,None]
                                if(seeHVACDesc):
                                    if len(results)==0:
                                        newZoneList.append(zone.name)
                                        aside = _airSideDetails_[zoneCount].d
                                        aside['zones']=newZoneList
                                        results[HVACGroupID]=aside
                                    else:
                                        for system in results:
                                            system['zones'].append(zone.name)
                    else:
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                            
                            #print _plantDetails_[0].d
                            
                            if(seeHVACDesc):
                                #this is simple, because there is only one airside system, so all zones will be added
                                if len(results)==0:
                                    newZoneList.append(zone.name)
                                    aside = _airSideDetails_[zoneCount].d
                                    aside['zones']=newZoneList
                                    results[HVACGroupID]=aside
                                    
                                else:
                                    for system in results:
                                        system['zones'].append(zone.name)
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None, None]
                            if(seeHVACDesc):
                                #this is simple, because there is only one airside system, so all zones will be added
                                if len(results)==0:
                                    newZoneList.append(zone.name)
                                    aside = _airSideDetails_[zoneCount].d
                                    aside['zones']=newZoneList
                                    results[HVACGroupID]=aside
                                else:
                                    for system in results:
                                        system['zones'].append(zone.name)
            
            # If no changes made, this component shouldn't output HBZones
            
            HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    else:
        results.append("You should first let Honeybee to fly...")
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")

    return HBZones,results
    
    
def checkTheInputs(_HVACSystemID):
    
    if _HVACSystems != None and _airSideDetails_ != None:
        
        print 'If air side details are entered through _airSideDetails_. The HVACSystemID must be specified in the Air Handler Detail component.\n'+ \
        'Please either disconnect the input from _HVACSystems or _airSideDetails_ and try again.'
        
        warn =  'If air side details are entered through _airSideDetails_. The HVACSystemID must be specified in the Air Handler Detail component.\n'+ \
        'Please either disconnect the input from _HVACSystems or _airSideDetails_ and try again.'
        
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
    
    
if _HBZones and _HVACSystems:
    pp = pprint.PrettyPrinter(indent=4)
    if _seeHVACDesc_ == None:
        _seeHVACDesc_ = False
        
    HBZones,out = main(_HBZones, _HVACSystems, _seeHVACDesc_)
    print "the dictionary:"
    pp.pprint(out)
    airsideDetails = dictToClass(out)

    #test to make sure it makes valid json (it does!).  Use an online json validator to be sure.
    #filename="C:\\Temp\\test.json"
    #with open(filename,'w') as outfile:
    #    json.dump(out,outfile)