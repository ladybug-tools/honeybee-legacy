# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Airside Economizer
-
Provided by Honeybee 0.0.55

    Args:
        _uniqueName : a required field to uniquely name the economizer
        _economizerControlType_:... supply nothing and it defaults
        _controlAction_: ... Requires an integer.  See ecdict for different values to supply.  Supply nothing and it defaults to "No Economizer", i.e. - always deliver Min Fresh Air only (the OpenStudio Default)
        _maximumAirFlowRate_: ... supply nothing and it autosizes
        _minimumAirFlowRate_: ... do nothing and it autosizes
        _minimumLimitType_: ... do nothing and it defaults to Proportional Minimum (min depends on the supply air flow rate as opposed to an absolute number)
        _minimumOutdoorAirSchedule_: ... do nothing and it defaults to OS stettings
        _minimumOutdoorAirFracSchedule_: ... this overrides minOutdoorAirSchedule and minAirflowRate
        _maximumLimitDewpoint_: ... needed for when the ControlType is Fixed Dewpoint and Dry Bulb
        _sensedMinimum_: ... is the minimum of whatever the control type, at this point the system goes to minimum flow
        _sensedMaximum_: ... is the maximum of whatever the control type, at this point the system goes to minimum flow
        _economizerLockoutMethod_: ... should only used when the HVAC system is packaged DX
        _timeOfDaySchedule_: provide this to command the economizer dampers into the "closed" position at night.  Do nothing and it defaults to the OpenStudio default (always open...which is typically not what you want)
        _mechVentController_: an optional field, though highly recommended.  Open Studio provides default behavoir for this controller.
    Returns:
        airsideEconomizerParameters:...
"""

ghenv.Component.Name = "Honeybee_OpenStudio Airside Economizer Detail"
ghenv.Component.NickName = 'AirSideEconomizer'
ghenv.Component.Message = 'VER 0.0.55\nDEC_14_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import Grasshopper.Kernel as gh
import pprint

#print _economizerControlType_
#print _maximumLimitDewpoint_

def clearInputs(econocomponent):
    econocomponent['name'] = None
    econocomponent['econoControl'] = None
    econocomponent['controlAction'] = None
    econocomponent['maxAirFlowRate'] = None
    econocomponent['minAirFlowRate'] = None
    econocomponent['minLimitType'] = None
    econocomponent['minOutdoorAirSchedule'] = None
    econocomponent['minOutdoorAirFracSchedule'] = None
    econocomponent['maxLimitDewpoint'] = None
    econocomponent['sensedMin'] = None
    econocomponent['sensedMax'] = None
    econocomponent['DXlockoutMethod'] = None
    econocomponent['timeOfDaySch'] = None
    return econocomponent

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

        
        
ecdict = {
0:'Fixed Dry Bulb',
1:'Differential Dry Bulb',
2:'Fixed Enthalpy',
3:'Differential Enthalply',
4:'Electronic Enthalpy',
5:'Fixed Dewpoint and Dry Bulb',
6:'Differential Dry Bulb and Enthalpy'
}

controlActdict = {
0:'Modulate Flow',
1:'Modulate Flow with Bypass'
}

minLimitdict = {
0:'Proportional Minimum',
1:'Fixed Minimum'
}

dxLockoutdict = {
0:'No Lockout',
1:'Lockout with Heating',
2:'Lockout with Compressor'
}


if sc.sticky.has_key('honeybee_release'):
    print 'grabbed the Honeybee default AirSide Economizer Definition: '
    hb_AirsideEconomizerDef = sc.sticky['honeybee_AirsideEconomizerParams']().airEconoDict
    pp = pprint.PrettyPrinter(indent=4)
    honeyBeeDefault = (hb_AirsideEconomizerDef)
    pp.pprint(honeyBeeDefault)
    print ''
    print 'Attempting to update the Honeybee default economizer to your definition'
    #I agree with Mostapha, there should be a smarter way to read the input signals
    econocomponent={}
    econocomponent['name'] = _uniqueName
    econocomponent['econoControl'] = _economizerControlType_
    econocomponent['controlAction'] = _controlAction_
    econocomponent['maxAirFlowRate'] = _maximumAirFlowRate_
    econocomponent['minAirFlowRate'] = _minimumAirFlowRate_
    econocomponent['minLimitType'] = _minimumLimitType_
    econocomponent['minOutdoorAirSchedule'] = _minimumOutdoorAirSchedule_
    econocomponent['minOutdoorAirFracSchedule'] = _minimumOutdoorAirFracSchedule_
    econocomponent['maxLimitDewpoint'] = _maximumLimitDewpoint_
    econocomponent['sensedMin'] = _sensedMinimum_
    econocomponent['sensedMax'] = _sensedMaximum_
    econocomponent['DXLockoutMethod'] = _economizerLockoutMethod_
    econocomponent['timeOfDaySch'] = _timeOfDaySchedule_
    econocomponent['mvCtrl'] = _mechVentController_.d

    
    if _uniqueName != None:
        if (_economizerControlType_ == 5 and _maximumLimitDewpoint_== None):
            print 'Fixed Dewpoint and Dry Bulb economizer chosen without inputting dewpoint.  Please enter a dewpoint value now or your economizer definition will revert to the Honeybee defaults.'
            msg = "You have chosen Control Type Fixed Dewpoint and Dry Bulb but you haven't input a maxLimitDewpoint.  Your economizer definition will be return to the Honeybee defaults until this is corrected."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            econocomponent = clearInputs(econocomponent)
        elif _minimumOutdoorAirFracSchedule_ != None:
            if _minimumOutdoorAirSchedule_ != None:
                print 'An error has been found in your definition, EnergyPlus only acceps either a minimum air schedule or minimum outdoor air fraction schedule, not both.'
                msg = "You have chosen to provide both schedules, but you can only choose one.  Your economizer definition will return to the Honeybee defaults until this is corrected."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                econocomponent = clearInputs(econocomponent)
            else:
                print 'Warning:  choosing to use the MinimumOutdoorAirFraction schedule overrides the minimumOutdoorAir Schedule AND the minimum Airflow Rate setting.  Make sure this is what you want.'
        
        if (_economizerControlType_ == 4):
            print 'Warning: You have chosen an electronic enthalpy controller.  Honeybee currently does not support electronic enthalpy controllers.  Please make another selection for controlType.'
            print 'Your economizer definition will return to the Honeybee defaults until this is corrected.'
            econocomponent = clearInputs(econocomponent)
        elif (_economizerControlType_ != 0):
            if (_economizerControlType_ != 5):
                if( _sensedMinimum_ == None or _sensedMaximum_ == None):
                    print 'Warning: you have chosen an control Type that is not based on dry bulb.'
                    print 'The honeybee default economizer is a dry bulb economizer, and the default honeybee economizer assumes sensed min and sensed max values are based on outdoor dry bulb temperatures (C)'
                    print 'We strongly suggest you provide your own values for sensedMinimum and sensedMaximum inputs for this component.'
                    print 'If you have selected Enthalpy, units for sensedMax and sensed Min are in Joules/kg'
                    print 'Differential controllers are based upon the measured difference between exhaust and outdoor supply air streams.'
        else:
            pass

    else:
        print 'Warning: If you are going to update the default economizer to a new one, you have to provide at least a name for it.'
        print 'Until a name is provided, the airside econmizer will remain the Honeybee default.'
        msg = "If you wish to make a new Airside Economizer definition, at least provide a name for it."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)
        econocomponent = clearInputs(econocomponent)
    
    actions = []
    storedEconoPar = {}
    for key in hb_AirsideEconomizerDef.keys():
        if econocomponent.has_key(key) and econocomponent[key] != None:
            if key == 'econoControl':
                s = key + ' has been updated to ' + ecdict[econocomponent[key]]
                actions.append(s)
            elif key =='controlAction':
                s = key + ' has been updated to ' + controlActdict[econocomponent[key]]
                actions.append(s)
            elif key == 'minLimitType':
                s = key + ' has been updated to ' + minLimitdict[econocomponent[key]]
                actions.append(s)
            elif key == 'DXLockoutMethod':
                s = key + ' has been updated to ' + dxLockoutdict[econocomponent[key]]
                actions.append(s)
            else:
                s = key + ' has been updated to ' + str(econocomponent[key])
                actions.append(s)
            storedEconoPar[key] = econocomponent[key]
        else:
            s = key + ' is still set to Honeybee Default: ' + str(hb_AirsideEconomizerDef[key])
            actions.append(s)
            storedEconoPar[key] = hb_AirsideEconomizerDef[key]
    
    airsideEconomizerParameters = dictToClass(storedEconoPar)
    print 'your economizer definition: '
    pp.pprint(storedEconoPar)
    print ''
    print 'Here are all the actions completed by this component:'
    actions = sorted(actions)
    pp.pprint(actions)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    airsideEconomizerParameters = []