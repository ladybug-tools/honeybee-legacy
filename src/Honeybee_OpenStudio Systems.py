#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to assign OpenStudio Systems to your HBZones.  By default, all HBZones are assigned an Ideal Air Loads system and this component can be used to change this to a real system from the OpenStudioHVACSystemsList component.
This component is also used to adjust the features of the HVAC system using the _airSideDetails_ and _plantDetails_ respectively.  Without the inputs in _airSideDetails_ and _plantDetails_, template Open Studio systems will be used.
-
Provided by Honeybee 0.0.59

    Args:
        _HBZones: The HBZones for which you want to change/adjust the HVAC system.
        _HVACSystems: A HVAC system template from the "Honeybee_OpenStudioHVACSystemsList" component.  ASHRAE recommends using the following baseline systems for different building types and fuel sources:
            BUILDING TYPE               FOSSIL FUEL/HYBRID/PURCHASED HEAT            ELECTRIC ONLY
            Residential                 1: PTAC | Residential                                   2: PTHP | Residential
            Non-Res 3 Floors            3: Packaged Single Zone - AC                            4: Packaged Single Zone - HP
            Non-Res 4-5 Floors          5: Packaged VAV w/ Reheat                               6: Packaged VAV w/ PFP Boxes
            Non-Res >5 Floors           7: VAV w/ Reheat                                        8: VAV w/ PFP Boxes
            Heated Only Sotrage         9: Warm Air Furnace - Gas Fired                         10: Warm Air Furnace - Electric
        _airSideDetails_: Parameters from the "Honeybee_OpenStudio Air Handler Detail" component that define the features of the air side (or ventilation side) of the HVAC system.
        _plantDetails_: Parameters from the "Honeybee_OpenStudio Plant Details" component that define the features of the plant (or water side) of the HVAC system.
    Returns:
        HBZones: HBZones that have been modified to have the assigned _HVACSystems.
"""

import Grasshopper.Kernel as gh
import scriptcontext as sc
import uuid
import pprint
import json


ghenv.Component.Name = "Honeybee_OpenStudio Systems"
ghenv.Component.NickName = 'OSHVACSystems'
ghenv.Component.Message = 'VER 0.0.59\nAPR_20_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nJAN_12_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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

def main(HBZones, HVACSystems):
    # check for Honeybee
    results = {}
    systems={}
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    #create a single HVAC Group ID to create a unique reference to the HVAC details imported (or none if none)
    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
    # assign the systems
    newZoneList = []
    for zoneCount, zone in enumerate(HBZonesFromHive):
        
        if not zone.isConditioned:
            warning = "%s is not conditioned. Systems will not be added to this zone."%zone.name
            results[zone.name] = warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            continue
        
        try: 
            #in the case where the user enters multiple HVAC Indices
            HVACIndex = HVACSystems[zoneCount]
            
            #If they enter different HVAC details for each HVAC Index (not ideal, but possible).
            if (len(_airSideDetails_) > 1):
                HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                    zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
            else:
                #there is only one detail, or no details
                if len(_airSideDetails_) == 1:
                    if len(_plantDetails_) == 1:
                        if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, _plantDetails_[0].d]
                    else:
                        if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d, None]
                else:
                    if len(_plantDetails_) == 1:
                        zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                    else:
                        zone.HVACSystem = [HVACGroupID, HVACIndex, None, None]
        except IndexError: 
            HVACIndex = HVACSystems[0]
            # Check that HVAC system inputs in airside components and this component are consisent!
            if (len(_airSideDetails_) > 1):
                HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
                if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[zoneCount]) != -1:
                    zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[zoneCount].d]
            else:
                #there is only one detail, or no details
                if len(_airSideDetails_) == 1:
                    if checkHVACSystemID.warningsForHBZone(zone,HVACIndex,_airSideDetails_[0]) != -1:
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,_plantDetails_[0].d]
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, _airSideDetails_[0].d,None]
                    else: 
                        if len(_plantDetails_) == 1:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                        else:
                            zone.HVACSystem = [HVACGroupID, HVACIndex, None,None]
                else:
                    if len(_plantDetails_) == 1:
                        zone.HVACSystem = [HVACGroupID, HVACIndex, None,_plantDetails_[0].d]
                    else:
                        zone.HVACSystem = [HVACGroupID, HVACIndex, None, None]
            
            if len(results)==0:
                newZoneList.append(zone.name)
                try:
                    aside = _airSideDetails_[zoneCount].d
                    aside['zones']=newZoneList
                    results[HVACGroupID]=aside
                except: pass
            else:
                for system in results:
                    system['zones'].append(zone.name)
            
            HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones,results


#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck and _HBZones and _HVACSystems:
    HBZones,out = main(_HBZones, _HVACSystems)
    
    pp = pprint.PrettyPrinter(indent=4)
    print "HVAC Description:"
    pp.pprint(out)
