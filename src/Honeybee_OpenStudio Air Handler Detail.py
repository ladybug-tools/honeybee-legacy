# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
OpenStudio Systems
-
Provided by Honeybee 0.0.55

    Args:
        jsonstream_: ...
        jsonfileloc_: ...
        _HVACSystemID:...
        _availabilitySch_: ...
        _fanPlacement_: ...
        _coolingAirflowRate_: ...
        _coolingOAFlowRate_: ...
        _heatingAirflowRate_: ...
        _heatingOAFlowRate_: ...
        _floatingAirflowRate_: ...
        _floatingOAFlowRate_: ...
        _coolingCoil_: ...
        _heatingCoil_: ...
        _fanDetail_: ...
        _airsideEconomizer_: ...
    Returns:
        energySimPar:...
"""

import scriptcontext as sc
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Air Handler Detail"
ghenv.Component.NickName = 'AirHandlerDetails'
ghenv.Component.Message = 'VER 0.0.55\nSEP_28_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import uuid
import pprint

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

def main():
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        return []
        
    hb_airHandler = sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
    print 'We have located the Honeybee default Air Handler Definition: '
    if _fanDetail_ != None:
        if _fanDetail_.d['type'] == 0:
            print 'constant volume fan definition'
            print hb_airHandler['constVolSupplyFanDef']().cvFanDict
        elif _fanDetail_.d['type'] == 1:
            print 'varvol!'
            print hb_airHandler['varVolSupplyFanDef']().vvFanDict
    print hb_airHandler['airsideEconomizer']().airEconoDict
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(hb_airHandler)
    

    
    if jsonstream_ == None and jsonfileloc_ == None:
        if(_HVACSystemID !=None):
            print 'assigning your GH values to this system.'
            sysdict = {}
            sysdict['availSch'] = _availabilitySch_
            sysdict['fanPlacement'] = _fanPlacement_
            sysdict['coolingAirflow'] = _coolingAirflowRate_
            sysdict['coolingOAflow'] = _coolingOAFlowRate_
            sysdict['heatingAirflow'] = _coolingAirflowRate_
            sysdict['heatingOAflow'] = _coolingOAFlowRate_
            sysdict['floatingAirflow'] = _coolingAirflowRate_
            sysdict['floatingOAflow'] = _coolingOAFlowRate_
            if _fanDetail_ != None:
                try:
                    if _fanDetail_.d['type'] == 0:
                        sysdict['constVolSupplyFanDef'] = _fanDetail_.d
                        sysdict['varVolSupplyFanDef'] = {}
                    elif _fanDetail_.d['type'] == 1:
                        sysdict['varVolSupplyFanDef'] = _fanDetail_.d
                        sysdict['constVolSupplyFanDef'] = {}
                except:
                    pass
            if _airsideEconomizer_ != None: sysdict['airsideEconomizer'] = _airsideEconomizer_.d
            if _coolingCoil_ != None : sysdict['coolingCoil'] = _coolingCoil_.d
        
            actions = []
            storedAHUParams = {}
            for key in sorted(hb_airHandler.keys()):
                if sysdict.has_key(key) and sysdict[key] != None:
                    if key == 'varVolSupplyFanDef' or key == 'constVolSupplyFanDef':
                        print 'changing Fan'
                        storedAHUParams[key] = sysdict[key]
                    elif key == 'airsideEconomizer':
                        print 'changing economizer'
                        storedAHUParams[key] = sysdict[key]
                    else:
                        storedAHUParams[key] = sysdict[key]
                        
                else:
                    if key == 'supplyFanDef':
                        print 'changing Fan'
                        storedAHUParams[key] = hb_airHandler[key]().cvFanDict
                    elif key == 'airsideEconomizer':
                        print 'changing economizer'
                        storedAHUParams[key] = hb_airHandler[key]().airEconoDict
                    else:
                        storedAHUParams[key] = hb_airHandler[key]
                        
            a = dictToClass(storedAHUParams)
            pp.pprint(a.d)
        else:
            print 'you are required to input an HVAC System ID'
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
            
    print sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
    return a

#likely deprecated
airHandlerDetail = main()


