#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chien Si Harriman <charriman@terabuild.com> 
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
OpenStudio Systems
-
Provided by Honeybee 0.0.57

    Args:
        jsonstream_: ... For future
        jsonfileloc_: ... For future
        _HVACSystemID:... use of the integers representing a system, as found in openStudioHVACSystemsList
        _availabilitySch_: ... a Honeybee or OpenStudio schedule reference.
        _fanPlacement_: ... BlowThrough or DrawThrough
        _coolingAirflowRate_: You may enter a maximum airflow rate in cooling (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _coolingOAFlowRate_: ...You may enter a maximum outdoor airflow rate in cooling (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _heatingAirflowRate_: ...You may enter a maximum airflow rate in heating (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _heatingOAFlowRate_: ... You may enter a maximum outdoor airflow rate in cooling (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _floatingAirflowRate_: ...You may enter a maximum airflow rate when floating (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _floatingOAFlowRate_: ...You may enter a maximum outdoor airflow rate in when floating (m3/s).  Typically this is left blank, so EnergyPlus can autosize.
        _coolingCoil_: ... Provide a definition fo a cooling coil (from the Honeybee component for cooling coils).  This component currently accepts one and two speed DX coil
        _heatingCoil_: ... Provide a definition fo a heating coil (from the Honeybee component for heating coils).  This component currently does not accept heating coils
        _fanDetail_: ... Provide a definition for a fan serving your air handler(s) .  This component current accepts constant volume fans that ride the fan curve, or a VFD fan
        _airsideEconomizer_: ... Provide a definition of 5an airside economizer (from the Honeybee component with the same name.
        _availabilityManagerList_: ...Provide the output of an availability manager list component to override OpenStudio default behavior.  Do nothing and the fan system never shuts off, which is not really desired behavior.
    Returns:
        energySimPar:...output to be input into the RunOpenStudio component, provided by Honeybee.
"""

import scriptcontext as sc
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Air Handler Detail"
ghenv.Component.NickName = 'AirHandlerDetails'
ghenv.Component.Message = 'VER 0.0.57\nOCT_12_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import uuid
import pprint

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

sysDict = {
    1:'PTAC',
    2:'PTHP',
    3:'PSZ',
    4:'PSZ Air Source Heat Pump',
    5:'Packaged VAV with Reheat',
    6:'Packaged VAV with Local Fan Powered Boxes',
    7:'Variable Air Volume with Reheat',
    8:'Variable Air Volume with Fan Powered Boxes'
}

def main(fanDetail,coolingCoil,heatingCoil,airsideEconomizer,availabilityManagerList):
    #basics
    a = []
    pp = pprint.PrettyPrinter(indent=4)
    #we conduct our main error handling here.  If we find errors, pattern in
    #notify the user of the error, make a change on their behalf, note the change
    if sc.sticky.has_key('honeybee_release'):
        hb_airHandler = sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
        print 'We have located the Honeybee default Air Handler Definition: '
        
        #pp.pprint(hb_airHandler)
        print 'constant volume fan definition'
        #pp.pprint(hb_airHandler['constVolSupplyFanDef']().cvFanDict)
        print 'variable volume fan definition'
        #pp.pprint(hb_airHandler['varVolSupplyFanDef']().vvFanDict)
        print 'airside economizer definition'
        #pp.pprint(hb_airHandler['airsideEconomizer']().airEconoDict)
    
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        return a
        
    if _HVACSystemID <= 4:
        if fanDetail != None:
            print fanDetail.d['type']
            if fanDetail.d['type'] != 0:
                print "You have specified a variable volume fan for a system that is constant volume."
                print "We are changing your fan definition to constant volume."
                print "Either change your fan definition or system type to prevent this from happening in the future."
                w = gh.GH_RuntimeMessageLevel.Remark
                ghenv.Component.AddRuntimeMessage(w, "Variable Volume Fan changed to Constant Volume to Match the System Type: " +sysDict[_HVACSystemID])
                pp.pprint(fanDetail.d)
                fanDetail.d['type'] = 0
                fanDetail.d.pop('minFlowFrac',None)
                fanDetail.d.pop('fanPowerCoefficient1',None)
                fanDetail.d.pop('fanPowerCoefficient2',None)
                fanDetail.d.pop('fanPowerCoefficient3',None)
                fanDetail.d.pop('fanPowerCoefficient4',None)
                fanDetail.d.pop('fanPowerCoefficient5',None)
                print "changed to"
                pp.pprint(fanDetail.d)
        if not isinstance(coolingCoil,str):
            if coolingCoil.d['type'] == 1:
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Your cooling coil is specified as a two speed coil, but your HVAC System ID only allows for a one speed coil.  See 'out' for more information.")
                print 'You have specified a 2 Speed DX Coil.'
                print 'But you have specified system type:' +str(_HVACSystemID)
                print 'This is not allowed.  We will override your coil with the Honeybee default 1 Speed DX Coil.'
                print 'If you want to keep your coil definition, change the Cooling Coil type in the component to be zero (0) (1 speed DX)'
                if coolingCoil.d['condenserType'] == 1:
                    print 'We have kept the evaporative condenser definition that you have created.'
                    evapcond = coolingCoil.d['evaporativeCondenserDesc']
                coolingCoil = sc.sticky['honeybee_1xDXCoilParams']().oneSpeedDXDict
                coolingCoil['evaporativeCondenserDesc'] = evapcond
                coolingCoil['type']=0
                pp.pprint(coolingCoil)
                coolingCoil = dictToClass(coolingCoil)
            
    elif (_HVACSystemID == 5 or _HVACSystemID == 6):
        #we don't want a single speed coil specified for what is a 2-speed system usually.
        if not isinstance(coolingCoil,str):
            if coolingCoil.d['type'] == 0:
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Your cooling coil has been converted to the Honeybee Default 2 Speed DX Coil.  See 'out' for more information.")
                print 'You have specified a single speed DX cooling coil and applied it to Packaged Variable Volume.'
                print 'Because this is not allowed, we are converting your definition to the Honeybee default 2-speed DX coil.'
                print 'If you want to keep your coil definition, change the coilType = 1 (two speed coil).'
                if coolingCoil.d['condenserType']==1:
                    print 'We have kept the evaporative condenser definition that you have created.'
                    evapcond = coolingCoil.d['evaporativeCondenserDesc']
                #pp.pprint(coolingCoil.d)
                coolingCoil = sc.sticky['honeybee_2xDXCoilParams']().twoSpeedDXDict
                coolingCoil['evaporativeCondenserDesc'] = evapcond
                coolingCoil['type']=1
                #pp.pprint(coolingCoil)
                coolingCoil = dictToClass(coolingCoil)
        #this is under the current configuration of system types
        if fanDetail != None:
            if fanDetail.d['type'] != 1:
                print "You have specified a constant volume fan for a system that is variable volume."
                print "We are changing your fan definition to variable volume."
                print "Either change your fan definition or system type to prevent this from happening in the future."
                w = gh.GH_RuntimeMessageLevel.Remark
                ghenv.Component.AddRuntimeMessage(w, "Constant Volume Fan changed to Variable Volume to Match the System Type: " +sysDict[_HVACSystemID])
                #print fanDetail.d
                #pp.pprint(fanDetail.d)
                fanDetail.d['type'] = 1
                fanDetail.d['minFlowFrac']=hb_airHandler['varVolSupplyFanDef']().vvFanDict['minFlowFrac']
                fanDetail.d['fanPowerCoefficient1'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient1']
                fanDetail.d['fanPowerCoefficient2'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient2']
                fanDetail.d['fanPowerCoefficient3'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient3']
                fanDetail.d['fanPowerCoefficient4'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient4']
                fanDetail.d['fanPowerCoefficient5'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient5']
                print "changed to"
                #pp.pprint(fanDetail.d)
            
    #dx coil assignment errors (single speed where dual speed, etc. , using DX heating where hot water)
    
    if(_HVACSystemID !=None):

        print 'You have assigned a valid HVAC system ID.'
        print str(_HVACSystemID) + ": " + sysDict[_HVACSystemID]
        sysdict = {}
        sysdict['availSch'] = _availabilitySch_
        sysdict['fanPlacement'] = _fanPlacement_
        sysdict['coolingAirflow'] = _coolingAirflowRate_
        sysdict['coolingOAflow'] = _coolingOAFlowRate_
        sysdict['heatingAirflow'] = _coolingAirflowRate_
        sysdict['heatingOAflow'] = _coolingOAFlowRate_
        sysdict['floatingAirflow'] = _coolingAirflowRate_
        sysdict['floatingOAflow'] = _coolingOAFlowRate_
        if fanDetail != None:
            try:
                if fanDetail.d['type'] == 0:
                    print 'Upgrading Constant Volume Fan based on your requirements.'
                    sysdict['constVolSupplyFanDef'] = fanDetail.d
                    sysdict['varVolSupplyFanDef'] = {}
                elif fanDetail.d['type'] == 1:
                    print 'Upgrading Variable Volume Fan based on your requirements.'
                    sysdict['varVolSupplyFanDef'] = fanDetail.d
                    print sysdict['varVolSupplyFanDef']
                    sysdict['constVolSupplyFanDef'] = {}
            except:
                print 'could not recall fan details from the fan component.'
        else:
            if _HVACSystemID <= 4:
                print 'Constant volume fan parameters set to Honeybee default.'
                sysdict['constVolSupplyFanDef'] = sc.sticky['honeybee_constantVolumeFanParams']().cvFanDict
                sysdict['varVolSupplyFanDef'] = {}
            else:
                print 'Variable volume fan parameters set to Honeybee default.'
                sysdict['varVolSupplyFanDef'] = sc.sticky['honeybee_variableVolumeFanParams']().vvFanDict
                sysdict['constVolSupplyFanDef'] = {}
        

        if airsideEconomizer != None: 
            # There is an economizer so add it to sysdict
            
            sysdict['airsideEconomizer'] = airsideEconomizer.d

        if not isinstance(coolingCoil, str): 
            print 'upgrading cooling coil detail'

            sysdict['coolingCoil'] = coolingCoil.d
            print sysdict['coolingCoil']
        else:
            pass
        if heatingCoil != None:
            #print heatingCoil.d
            
            sysdict['heatingCoil'] = heatingCoil.d
        else:
            pass
        if availabilityManagerList != None:
            
            print 'found availMan!!!!!!!!!'
            sysdict['availabilityManagerList'] = availabilityManagerList
            print sysdict['availabilityManagerList']
            
        else:
            # Set to always On
            
            sysdict['availabilityManagerList'] = 'ALWAYS ON'
        
        actions = []
        storedAHUParams = {}
        
        for key in sorted(hb_airHandler.keys()):
            print key
            if sysdict.has_key(key):
                
                if key == 'varVolSupplyFanDef' or key == 'constVolSupplyFanDef':

                    storedAHUParams[key] = sysdict[key]
                elif key == 'airsideEconomizer':

                    storedAHUParams[key] = sysdict[key]
                else:
                    
                    storedAHUParams[key] = sysdict[key]

            else:
                if key == 'supplyFanDef':
                    storedAHUParams[key] = hb_airHandler[key]().cvFanDict
                
                elif key == 'airsideEconomizer':
                    # IF airsideEconomizer is not in sysdict there is no economizer
                    storedAHUParams[key] = None
                    # Below are defaults that Chen Si was using, they assign default values but why
                    # would you need them when there is no economizer?
                    #storedAHUParams[key] = hb_airHandler[key]().airEconoDict

                else:
                    storedAHUParams[key] = hb_airHandler[key]
        
        
        # Add availabilityManagerList to storedAHUParams
        
        
        #in the worst-case scenario, this will just send back honeybee defaults.

        a = dictToClass(storedAHUParams)
        print 'your air handler definition:'
        #pp.pprint(a.d)
    else:
        print 'you are required to input an HVAC System ID'
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You need to provide an HVAC System ID.")
            
    """
    elif jsonstream_ != None and jsonfileloc_ == None:
        #placeholder tbd
        print "Assigning Streamed Values to the template."
        sysdict.clear()
        print "Error: can't find your designated stream source."
    elif jsonstream_ == None and jsonfileloc_ != None:
        #placeholder tdb
        print "Assigning Standard JSON file values to the Template."
        sysdict.clear()
        print "Error: can't find your designated filepath."
    else:
        print "Only input a json file location or a streampath, not both!!!"
    """
        
    #print sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
    return a

#likely deprecated
airHandlerDetail = main(_fanDetail_,_coolingCoil_,_heatingCoil_,_airsideEconomizer_,_availabilityManagerList_)

#print airHandlerDetail
