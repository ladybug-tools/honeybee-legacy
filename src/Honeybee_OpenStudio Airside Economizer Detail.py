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
Airside Economizer
-
Provided by Honeybee 0.0.57

    Args:
        _uniqueName : a required field to uniquely name the economizer
        _economizerControlType_:... requires an integer specifying the type of economizer 0:FixedDryBulb(default),1:DifferentialDryBulb,2:FixedEnthalpy,3:DifferentialEnthalpy,4:ElectronicEnthalpy,5:FixedDewPointAndDryBulb,6:DifferentialDryBulbAndEnthalpy,7:NoEconomizer
        _controlAction_: ... Requires an integer.  See ecdict for different values to supply.  Supply nothing and it defaults to "ModulateFlow"
        _maximumAirFlowRate_: ... supply nothing and it will Autosize (recommended)
        _minimumAirFlowRate_: ... do nothing and it will Autosize (recommended)
        _minimumLimitType_: ... do nothing and it defaults to Proportional Minimum (min depends on the supply air flow rate as opposed to an absolute number)
        _minimumOutdoorAirSchedule_: ... This is a schedule with values between 0 and 1, and it is multiplied by the minimumAirFlowRate.  It is usually left blank, but can be used to fine tune the economizer during warm-up time or after hours.
        _minimumOutdoorAirFracSchedule_: ... this overrides minOutdoorAirSchedule and minAirflowRate.  It is a schedule between 0 and 1.  It is often used to create a 100% outside air system.
        _maximumOutdoorAirFracSchedule_: ... this is a schedule between 0 and 1.  It is often used to create a recirculating outside air system such as that in patient rooms.
        _maximumLimitDewpoint_: ... needed for when the ControlType is Fixed Dewpoint and Dry Bulb.  Otherwise leave blank
        _sensedMinimum_: ... is the minimum of whatever the control type, at this point the system goes to minimum flow
        _sensedMaximum_: ... is the maximum of whatever the control type, at this point the system goes to minimum flow
        _economizerLockoutMethod_: ... should only used when the HVAC system is packaged DX
        _timeOfDaySchedule_: this field is only used when the outdoor flow rate is based on a schedule.  It is rare for a normal economizer to have this value set.  If so, apply the name of a schedule.
        _mechVentController_: an optional field, though highly recommended.  Open Studio provides default behavoir for this controller.
        _availabilityManagerList_ : allows you to toggle between different AvailabilityManagers.  Right now, we simply allow you to create a list that has only one AvailabilityManager, and the type of manager can be ScheduledOrNightCycle
    Returns:
        airsideEconomizer: An airside economizer detail that can be plugged into the "Honeybee_Air Handling Unit Detail" component.
"""

ghenv.Component.Name = "Honeybee_OpenStudio Airside Economizer Detail"
ghenv.Component.NickName = 'AirSideEconomizer'
ghenv.Component.Message = 'VER 0.0.57\nOCT_24_2015'
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
    econocomponent['maxOutdoorAirFracSchedule'] = None
    econocomponent['maxLimitDewpoint'] = None
    econocomponent['sensedMin'] = None
    econocomponent['sensedMax'] = None
    econocomponent['DXlockoutMethod'] = None
    econocomponent['timeOfDaySch'] = None
    econocomponent['mvCtrl'] = None
    econocomponent['availManagerList'] = None
    return econocomponent

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

ecdict = {
0:'FixedDryBulb',
1:'DifferentialDryBulb',
2:'FixedEnthalpy',
3:'DifferentialEnthalply',
4:'ElectronicEnthalpy',
5:'FixedDewpointandDryBulb',
6:'DifferentialDryBulbandEnthalpy',
7:'NoEconomizer'
}

controlActdict = {
0:'ModulateFlow',
1:'ModulateFlowwithBypass'
}

minLimitdict = {
0:'ProportionalMinimum',
1:'FixedMinimum'
}

dxLockoutdict = {
0:'NoLockout',
1:'LockoutwithHeating',
2:'LockoutwithCompressor'
}


def main():
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
    econocomponent['econoControl'] = ecdict[_economizerControlType_]
    econocomponent['controlAction'] = controlActdict[_controlAction_]
    econocomponent['maxAirFlowRate'] = _maximumAirFlowRate_
    econocomponent['minAirFlowRate'] = _minimumAirFlowRate_
    econocomponent['minLimitType'] = minLimitdict[_minimumLimitType_]
    econocomponent['minOutdoorAirSchedule'] = _minimumOutdoorAirSchedule_
    econocomponent['minOutdoorAirFracSchedule'] = _minimumOutdoorAirFracSchedule_
    econocomponent['maxOutdoorAirFracSchedule'] = _maximumOutdoorAirFracSchedule_
    econocomponent['maxLimitDewpoint'] = _maximumLimitDewpoint_
    econocomponent['sensedMin'] = _sensedMinimum_
    econocomponent['sensedMax'] = _sensedMaximum_
    econocomponent['DXLockoutMethod'] = dxLockoutdict[_economizerLockoutMethod_]
    econocomponent['timeOfDaySch'] = _timeOfDaySchedule_
    if _mechVentController_ != None:
        econocomponent['mvCtrl'] = _mechVentController_.d
    else:
        econocomponent['mvCtrl'] = _mechVentController_
    if _availabilityManagerList_ != None:
        econocomponent['availManagerList'] = _availabilityManagerList_.d
    else:
        econocomponent['availManagerList'] = _availabilityManagerList_
    
    
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
                print 'We strongly suggest you provide your own values for sensedMinimum and sensedMaximum inputs for this component.'
                print 'If you have selected Enthalpy, units for sensedMax and sensed Min are in Joules/kg'
                print 'Differential controllers are based upon the measured difference between exhaust and outdoor supply air streams.'
    else:
        pass
    
    actions = []
    storedEconoPar = {}
    for key in hb_AirsideEconomizerDef.keys():
        if econocomponent.has_key(key) and econocomponent[key] != None:
            if key == 'econoControl':
                s = key + ' has been updated to ' + econocomponent[key]
                actions.append(s)
            elif key =='controlAction':
                s = key + ' has been updated to ' + econocomponent[key]
                actions.append(s)
            elif key == 'minLimitType':
                s = key + ' has been updated to ' + econocomponent[key]
                actions.append(s)
            elif key == 'DXLockoutMethod':
                s = key + ' has been updated to ' + econocomponent[key]
                actions.append(s)
            else:
                s = key + ' has been updated to ' + str(econocomponent[key])
                actions.append(s)
            storedEconoPar[key] = econocomponent[key]
        else:
            if key == 'econoControl':
                s = key + ' is still set to Honeybee Default: ' + hb_AirsideEconomizerDef[key]
                actions.append(s)
            elif key =='controlAction':
                s = key + ' is still set to Honeybee Default: ' + hb_AirsideEconomizerDef[key]
                actions.append(s)
            elif key == 'minLimitType':
                s = key + ' is still set to Honeybee Default: ' + hb_AirsideEconomizerDef[key]
                actions.append(s)
            elif key == 'DXLockoutMethod':
                s = key + ' is still set to Honeybee Default: ' + hb_AirsideEconomizerDef[key]
                actions.append(s)
            else:
                s = key + ' is still set to Honeybee Default: ' + str(hb_AirsideEconomizerDef[key])
                actions.append(s)
            storedEconoPar[key] = hb_AirsideEconomizerDef[key]
    
    airsideEconomizer = dictToClass(storedEconoPar)
    print 'your economizer definition: '
    pp.pprint(storedEconoPar)
    print ''
    print 'Here are all the actions completed by this component:'
    actions = sorted(actions)
    pp.pprint(actions)
    
    return airsideEconomizer




initCheck = True
if sc.sticky.has_key('honeybee_release'): pass
else:
    initCheck = False
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    airsideEconomizer = []

if initCheck == True and _uniqueName != None:
    airsideEconomizer = main()
elif _uniqueName == None:
    msg = "Provide a name for your economizer."
    print msg