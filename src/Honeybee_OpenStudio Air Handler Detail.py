# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
OpenStudio Systems
-
Provided by Honeybee 0.0.55

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
    Returns:
        energySimPar:...output to be input into the RunOpenStudio component, provided by Honeybee.
"""

import scriptcontext as sc
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Air Handler Detail"
ghenv.Component.NickName = 'AirHandlerDetails'
ghenv.Component.Message = 'VER 0.0.55\nOCT_13_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014

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

def main():
    #basics
    a = []
    pp = pprint.PrettyPrinter(indent=4)
    #we conduct our main error handling here.  If we find errors, pattern in
    #notify the user of the error, make a change on their behalf, note the change
    if _HVACSystemID <= 4:
        print _fanDetail_.d['type']
        if _fanDetail_.d['type'] != 0:
            print "You have specified a variable volume fan for a system that is constant volume."
            print "We are changing your fan definition to constant volume."
            print "Either change your fan definition or system type to prevent this from happening in the future."
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, "Variable Volume Fan changed to Constant Volume to Match the System Type: " +sysDict[_HVACSystemID])
            pp.pprint(_fanDetail_.d)
            _fanDetail_.d['type'] = 0
            _fanDetail_.d.pop('minFlowFrac',None)
            _fanDetail_.d.pop('fanPowerCoefficient1',None)
            _fanDetail_.d.pop('fanPowerCoefficient2',None)
            _fanDetail_.d.pop('fanPowerCoefficient3',None)
            _fanDetail_.d.pop('fanPowerCoefficient4',None)
            _fanDetail_.d.pop('fanPowerCoefficient5',None)
            print "changed to"
            pp.pprint(_fanDetail_.d)
    else:
        #this is under the current configuration of system types
        if _fanDetail_.d['type'] != 1:
            print "You have specified a constant volume fan for a system that is variable volume."
            print "We are changing your fan definition to variable volume."
            print "Either change your fan definition or system type to prevent this from happening in the future."
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, "Constant Volume Fan changed to Variable Volume to Match the System Type: " +sysDict[_HVACSystemID])
            print _fanDetail_.d
            pp.pprint(_fanDetail_.d)
            _fanDetail_.d['type'] = 1
            _fanDetail_.d['minFlowFrac']=hb_airHandler['varVolSupplyFanDef']().vvFanDict['minFlowFrac']
            _fanDetail_.d['fanPowerCoefficient1'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient1']
            _fanDetail_.d['fanPowerCoefficient2'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient2']
            _fanDetail_.d['fanPowerCoefficient3'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient3']
            _fanDetail_.d['fanPowerCoefficient4'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient4']
            _fanDetail_.d['fanPowerCoefficient5'] = hb_airHandler['varVolSupplyFanDef']().vvFanDict['fanPowerCoefficient5']
            print "changed to"
            pp.pprint(_fanDetail_.d)
            
    #dx coil assignment errors
    
    if sc.sticky.has_key('honeybee_release'):
        hb_airHandler = sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
        print 'We have located the Honeybee default Air Handler Definition: '
        
        pp.pprint(hb_airHandler)
        print 'constant volume fan definition'
        pp.pprint(hb_airHandler['constVolSupplyFanDef']().cvFanDict)
        print 'variable volume fan definition'
        pp.pprint(hb_airHandler['varVolSupplyFanDef']().vvFanDict)
        print 'airside economizer definition'
        pp.pprint(hb_airHandler['airsideEconomizer']().airEconoDict)
        
    
        
        if jsonstream_ == None and jsonfileloc_ == None:
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
                if _fanDetail_ != None:
                    try:
                        if _fanDetail_.d['type'] == 0:
                            print 'Upgrading Constant Volume Fan based on your requirements.'
                            sysdict['constVolSupplyFanDef'] = _fanDetail_.d
                            sysdict['varVolSupplyFanDef'] = {}
                        elif _fanDetail_.d['type'] == 1:
                            print 'Upgrading Variable Volume Fan based on your requirements.'
                            sysdict['varVolSupplyFanDef'] = _fanDetail_.d
                            sysdict['constVolSupplyFanDef'] = {}
                    except:
                        print 'could not recall fan details from the fan component.'
                else:
                    if _HVACSystemID <= 4:
                        sysdict['constVolSupplyFanDef'] = sc.sticky['honeybee_constantVolumeFanParams']().cvFanDict
                        sysdict['varVolSupplyFanDef'] = {}
                    else:
                        sysdict['varVolSupplyFanDef'] = sc.sticky['honeybee_variableVolumeFanParams']().vvFanDict
                        sysdict['constVolSupplyFanDef'] = {}
                        
                if _airsideEconomizer_ != None: 
                    sysdict['airsideEconomizer'] = _airsideEconomizer_.d
                else:
                    pass
                if _coolingCoil_ != None : 
                    sysdict['coolingCoil'] = _coolingCoil_.d
                else:
                    pass
            
                actions = []
                storedAHUParams = {}
                for key in sorted(hb_airHandler.keys()):
                    if sysdict.has_key(key) and sysdict[key] != None:
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
                            storedAHUParams[key] = hb_airHandler[key]().airEconoDict
                        else:
                            storedAHUParams[key] = hb_airHandler[key]
                #in the worst-case scenario, this will just send back honeybee defaults.
                a = dictToClass(storedAHUParams)
                print 'your air handler definition:'
                pp.pprint(a.d)
            else:
                print 'you are required to input an HVAC System ID'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "You need to provide an HVAC System ID.")
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
            
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        
    print sc.sticky["honeybee_AirHandlerParams"]().airHandlerDict
    return a

#likely deprecated
airHandlerDetail = main()


