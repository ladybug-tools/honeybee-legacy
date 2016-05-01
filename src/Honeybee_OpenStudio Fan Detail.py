#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chien Si Harriman <charriman@terabuild.com> 
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
Energy Plus Fan Definition
-
Provided by Honeybee 0.0.59

    Args:
        _fanType:... 0 = Constant Volume, 1 = Variable Volume
        _fanName:... Provide a Unique name for the fan
        _fanEfficiency_:... the fan blade mechanical efficiency, value must be between 0 and 1
        _pressureRise_: ... total static pressure of the fan, Pascals
        _maxFlowRate_: ... the peak flow rate of the fan, if left blank, this value autosizes
        _motorEfficiency_: ... the motor efficiency of the fan, value must be between 0 and 1
        _motorPctInAirstream_: ... percent of heat liberated by fan to the airstream, default is 100 percent
        _minFanFlowFraction_:... the minimum airflow fraction of the fan, value must be between 0 and 1
        _fanPowerCoeff1_:... power curve coefficiencts for Variable Volume Fans
        _fanPowerCoeff2_:... power curve coefficiencts for Variable Volume Fans
        _fanPowerCoeff3_:... power curve coefficiencts for Variable Volume Fans
        _fanPowerCoeff4_:... power curve coefficiencts for Variable Volume Fans
        _fanPowerCoeff5_:... power curve coefficiencts for Variable Volume Fans
    Returns:
        fanDefinition:... updated fan definition returned by this component
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Fan Detail"
ghenv.Component.NickName = 'EPlusFan'
ghenv.Component.Message = 'VER 0.0.59\nAPR_30_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        

def main():
    fanUpdates = []
    if sc.sticky.has_key('honeybee_release'):
        if (_fanType == None):
            print 'You must define a fan type, either constant volume or variable volume.'
            msg = "Without a fan type, this component cannot work."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        elif (_fanType == 1):
            print 'you have selected a variable volume fan, this is typically used for ASHRAE system types 5 and 7'
            print 'We have found the Honeybee default Variable Volume Fan Definition: '
            hb_varVolFan = sc.sticky['honeybee_variableVolumeFanParams']().vvFanDict
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(hb_varVolFan)
            #calculate the power per unit flow
            hbFanTotalStaticPressure = hb_varVolFan['pressureRise']
            hbFanEfficiency = hb_varVolFan['fanEfficiency']
            hbMotorEfficiency = hb_varVolFan['motorEfficiency']
            hb_flowpmetric = hbFanTotalStaticPressure/(hbFanEfficiency*hbMotorEfficiency)
            print 'The honeybee variable volume fan power per unit flow is: '
            print str(hb_flowpmetric) + ' (Watts per meters cubed/second (metric Units))'
            hb_flowpIP = hb_flowpmetric / 2118.879
            print str(hb_flowpIP) + ' (Watts per cubic feet/minute (US-IP units))'
            print ''
            print 'updating the Honeybee default variable volume to your definition.'
            #this is the local version saved in rhino/the component
            fanComponent={}
            fanComponent['name'] = _fanName
            fanComponent['type'] = _fanType
            fanComponent['fanEfficiency'] = _fanEfficiency_
            fanComponent['pressureRise'] = _pressureRise_
            fanComponent['maxFlowRate'] = _maxFlowRate_
            fanComponent['motorEfficiency'] = _motorEfficiency_
            fanComponent['airStreamHeatPct'] = _motorPctInAirstream_
            fanComponent['minFlowFrac'] = _minFanFlowFraction_
            fanComponent['fanPowerCoefficient1'] = _fanPowerCoeff1_
            fanComponent['fanPowerCoefficient2'] = _fanPowerCoeff2_
            fanComponent['fanPowerCoefficient3'] = _fanPowerCoeff3_
            fanComponent['fanPowerCoefficient4'] = _fanPowerCoeff4_
            fanComponent['fanPowerCoefficient5'] = _fanPowerCoeff5_
        
            if _fanName != None and _fanType != None:
                actions = []
                storedFanParams = {}
                for key in hb_varVolFan.keys():
                    if fanComponent.has_key(key) and fanComponent[key] != None:
                        #here the honeybee sticky has been updated
                        s = key + ' has been updated to ' + str(fanComponent[key])
                        actions.append(s)
                        storedFanParams[key] = fanComponent[key]
                    else:
                        #here we couldn't find the key in the dict, so everything remains the same
                        s = key + ' is still set to Honeybee Default: ' + str(fanComponent[key])
                        actions.append(s)
                        storedFanParams[key] = hb_varVolFan[key]
                
                fanUpdates = dictToClass(storedFanParams)
                print 'your variable volume fan definition:'
                pp.pprint(storedFanParams)
                usFanTotalStaticPressure = storedFanParams['pressureRise']
                usFanEfficiency = storedFanParams['fanEfficiency']
                usMotorEfficiency = storedFanParams['motorEfficiency']
                us_flowpmetric = usFanTotalStaticPressure/(usFanEfficiency*usMotorEfficiency)
                print 'Your fan definition\'s variable volume fan power per unit flow is: ' 
                print str(us_flowpmetric) + ' (Watts per meters cubed/second (metric Units))'
                us_flowIP = us_flowpmetric/2118.879
                print str(us_flowIP) + ' (Watts per cubic feet/minute (US-IP units))'
                print ''
                print 'Here are all the actions completed by this component:'
                pp.pprint(actions)
            else:
                print 'You must define a fan name.'
                msg = "Without a fan name, the component will not update your fan description."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        elif _fanType == 0:
            #this is a constant volume fan
            print "Constant volume fan"
            hb_constVolFan = sc.sticky['honeybee_constantVolumeFanParams']().cvFanDict
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(hb_constVolFan)
            #calculate the power per unit flow
            hbFanTotalStaticPressure = hb_constVolFan['pressureRise']
            hbFanEfficiency = hb_constVolFan['fanEfficiency']
            hbMotorEfficiency = hb_constVolFan['motorEfficiency']
            hb_flowpmetric = hbFanTotalStaticPressure/(hbFanEfficiency*hbMotorEfficiency)
            print 'The honeybee constant volume fan power per unit flow is: '
            print str(hb_flowpmetric) + ' (Watts per meters cubed/second (metric Units))'
            hb_flowpIP = hb_flowpmetric / 2118.879
            print str(hb_flowpIP) + ' (Watts per cubic feet/minute (US-IP units))'
            print ''
            print 'updating the Honeybee default constant volume to your definition.'
            
            fanComponent={}
            fanComponent['name'] = _fanName
            fanComponent['type'] = _fanType
            fanComponent['fanEfficiency'] = _fanEfficiency_
            fanComponent['pressureRise'] = _pressureRise_
            fanComponent['maxFlowRate'] = _maxFlowRate_
            fanComponent['motorEfficiency'] = _motorEfficiency_
            fanComponent['airStreamHeatPct'] = _motorPctInAirstream_
            
            if _fanName != None and _fanType != None:
                actions = []
                storedFanParams = {}
                for key in hb_constVolFan.keys():
                    if fanComponent.has_key(key) and fanComponent[key] != None:
                        s = key + ' has been updated to ' + str(fanComponent[key])
                        actions.append(s)
                        storedFanParams[key] = fanComponent[key]
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(fanComponent[key])
                        actions.append(s)
                        storedFanParams[key] = hb_constVolFan[key]
                
                fanUpdates = dictToClass(storedFanParams)
                print 'your constant volume fan definition:'
                pp.pprint(storedFanParams)
                usFanTotalStaticPressure = storedFanParams['pressureRise']
                usFanEfficiency = storedFanParams['fanEfficiency']
                usMotorEfficiency = storedFanParams['motorEfficiency']
                us_flowpmetric = usFanTotalStaticPressure/(usFanEfficiency*usMotorEfficiency)
                print 'Your fan definition\'s constant volume fan power per unit flow is: ' 
                print str(us_flowpmetric) + ' (Watts per meters cubed/second (metric Units))'
                us_flowIP = us_flowpmetric/2118.879
                print str(us_flowIP) + ' (Watts per cubic feet/minute (US-IP units))'
                print ''
                print 'Here are all the actions completed by this component:'
                pp.pprint(actions)
            else:
                print 'You must define a fan name.'
                msg = "Without a fan name, the component will not update your fan description."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    return fanUpdates


fanParameters = main()