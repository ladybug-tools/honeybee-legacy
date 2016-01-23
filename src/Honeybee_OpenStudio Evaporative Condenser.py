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
Evaporative Condenser
-
Provided by Honeybee 0.0.59

    Args:
        _uniqueName : ... a required field to uniquely name the evaporative condenser
        _serviceType : ... what does the evaporator serve: 0=single speed DX, 1=two speed DX, 2=VRF, or 3=commercial refrigeration system
        _evaporativeEffectiveness_:... provide no information and the value defaults 
        _evapCondenserAirFlowRate_: ... flow rate through the evap condenser, is autosized by default 0.000144 m3/s per Watt (850 cfm/ton)
        _evapPumpPower_: ... power in Watts is autosized by default 0.004266 Watts/Watt cooling or 15 W/ton cooling
        _hiSpeedEvaporativeEffectiveness_:... Used for both one stage and two stage condensers, supply no information and the value defaults to 0.9
        _hiSpeedEevapCondenserFlowRate_: ... Used for both one stage and two stage condensers, flow rate through the evap condenser, is autosized by default 0.000144 m3/s per Watt (850 cfm/ton)
        _hiSpeedEvapPumpPower_: ... Used for both one stage and two stage condensers, power in Watts is autosized by default 0.004266 Watts/Watt cooling or 15 W/ton cooling
        _loSpeedEvaporativeEffectiveness_:... only needed for two speed condenser, supply no information and the value defaults to 0.9
        _loSpeedEevapCondenserFlowRate_: ... only needed for two speed condenser, flow rate through the evap condenser, is autosized by default 0.000144 m3/s per Watt (850 cfm/ton)
        _loSpeedEvapPumpPower_: ... only needed for two-speed condenser, power in Watts is autosized by default 0.004266 Watts/Watt cooling or 15 W/ton cooling
        _storageTank_:  the description of a storage tank used to hold the evaporative condenser water, if any
        _Curves_: this feature has not been implemented yet.
    Returns:
        evapCondenserDefinition:...description of an evaporative condenser returned for users.
"""

ghenv.Component.Name = "Honeybee_OpenStudio Evaporative Condenser"
ghenv.Component.NickName = 'EvaporativeCondenser'
ghenv.Component.Message = 'VER 0.0.59\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import Grasshopper.Kernel as gh
import pprint

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        
        


def main():
    evapCondenserDef = {}
    #put any basic error handling regarding inputs here, typically
    if _loSpeedEvaporativeEffectiveness_ != None:
        if _loSpeedEvaporativeEffectiveness_ <0 or _loSpeedEvaporativeEffectiveness_ > 1:
            print 'Evaporative effectiveness must be between 0 and 1.'
            warning = "Please enter a decimal between 0 and 1 for evaporative effectiveness."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return evapCondenserDef
    if _hiSpeedEvaporativeEffectiveness_ != None:
        if _hiSpeedEvaporativeEffectiveness_ < 0 or _hiSpeedEvaporativeEffectiveness_ > 1:
            print 'Hi Speed Evaporative effectiveness must be between 0 and 1.'
            warning = "Please enter a decimal between 0 and 1 for high speed evaporative effectiveness."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return evapCondenserDef
        
    if _serviceType == 0:
        if _loSpeedEvaporativeEffectiveness_ != None:
            print 'your low Speed Evaporative Effectiveness is Ignored'
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed Evaporative condenser.  All low speed definitions are ignored.")
        if _loSpeedEvaporativeCondAirflowRate_ != None:
            print 'your low Speed Evap Condenser Airflow Rate is Ignored'
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed Evaporative condenser.  All low speed definitions are ignored.")
        if _loSpeedEvapPumpPower_ != None:
            print 'your low Speed Evaporative Pump Power is Ignored'
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed Evaporative condenser.  All low speed definitions are ignored.")
    elif _serviceType > 1:
        warning = 'serviceType can only be an integer of 0 (for one speed dx condenser) or 1 (for two speed dx condenser'
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return evapCondenserDef
            
            
    if sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return evapCondenserDef
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return evapCondenserDef
            
        print 'Use this component to override the honeybee default evaporative condenser definition.'
        print 'This object is used to improve the efficiency of packaged DX units, and only works as an input to a DX system (DX coils, VRF, and commercial refrigeration systems.)'
        print 'It is ideally used in more dry, arid climates when the evaporative effect is most effective.'
        print 'please note: '
        print 'service type refers to what the evaporative condenser serves (single speed DX, two speed DX, VRF, or commercial refrigeration systems'
        print 'evaporative effectiveness is a dimensionless number (percentage) between 0 and 1.  The default value is 0.9'
        print 'evaporative airflow rate is in m3/s, and is the amount of air flowing through the condenser.  If you leave it blank, it will autosize to 0.000144 m3/s per Watt of rated capacity [850 cfm/ton]'
        print 'evaporative pump power is the power draw of the pump to spray the water on the evaporative condenser.  If you leave it blank, it will autosize to 0.004266 Watts per Watt of rated capacity [15 Watts/ton]'
        print ' if the service type is a 2 speed DX coil, then the high speed values are in effect.'
        print 'high speed evaporative effectiveness is just like evaporative effectiveness in its constraints, with the same default values.'
        print 'hi speed evaporative condesner airflow rate is identical to the evaporative airflow rate mentioned above, with the same default values.'
        print 'hi speed pump power is identical to evaporative pump power listed above, with the same default values.'
        print 'a storage tank can be added to this system, from which the evaporative pump draws water.'
        print 'curves, indicating the evaporative effectiveness of the system as a function of outdoor wetbulb, can be provided.  If they are provided, the evaporative effectiveness is ignored.'
        print 'currently not implemented in this Honeybee component (these inputs are placeholders):  storageTank, curves'
        
        
        if _uniqueName != None:
            
            if _serviceType == None:
                print 'you must specify a service type for this device.  0 = single speed DX coil, 1 = 2 speed DX coil.'
                print 'Please specify a service type.'
                warning = "You need to provide a service Type for your condenser description."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                return evapCondenserDef
            elif _serviceType == 0:
                print 'We are now hunting for Honeybee defaults 1 speed DX Evaporative Condensers...'
                print 'We have found the Honeybee default for 1 speed DX Evaporative Condensers: '
                hb_lspeedevapcond = sc.sticky['honeybee_lspeedevapcondParams']().lspeedevapCond
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(hb_lspeedevapcond)
                lspeedevapcond = {
                'name':_uniqueName,
                'serviceType':_serviceType,
                'evapEffectiveness':_loSpeedEvaporativeEffectiveness_,
                'evapCondAirflowRate':_loSpeedEvaporativeCondAirflowRate_,
                'evapPumpPower':_loSpeedEvapPumpPower_,
                'storageTank':_storageTank_,
                'curves':_Curves_
                }
                
                #update the hive
                actions = []
                updatedCondParams = {}
                
                for key in hb_lspeedevapcond.keys():
                    if lspeedevapcond.has_key(key) and lspeedevapcond[key] != None:
                        s = key + ' has been updated to ' + str(lspeedevapcond[key])
                        actions.append(s)
                        updatedCondParams[key] = lspeedevapcond[key]
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(hb_lspeedevapcond[key])
                        actions.append(s)
                        updatedCondParams[key] = hb_lspeedevapcond[key]
                
                evapCondenserDef = dictToClass(updatedCondParams)
                print 'your evaporative condenser definition has been uploaded and ready for use.  Your definition:'
                pp.pprint(updatedCondParams)
                print ''
                print 'actions completed for your coil definition: '
                for action in actions:
                    print action
                    
            elif _serviceType == 1:
                print 'We are now hunting for Honeybee defaults 2 speed DX Evaporative Condensers...'
                print 'We have found the Honeybee default for 2 speed DX Evaporative Condensers: '
                hb_hspeedevapcond = sc.sticky['honeybee_hspeedevapcondParams']().hspeedevapCond
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(hb_hspeedevapcond)
                
                hspeedevapcond = {
                'name':_uniqueName,
                'serviceType':_serviceType,
                'evapEffectiveness':_loSpeedEvaporativeEffectiveness_,
                'evapCondAirflowRate':_loSpeedEvaporativeCondAirflowRate_,
                'evapPumpPower':_loSpeedEvapPumpPower_,
                'hiEvapEffectiveness':_hiSpeedEvaporativeEffectiveness_,
                'hiEvapCondAirflowRate':_hiSpeedEvaporativeCondAirflowRate_,
                'hiEvapPumpPower':_hiSpeedEvapPumpPower_,
                'storageTank':_storageTank_,
                'curves':_Curves_
                }
                
                #update the hive
                actions = []
                updatedCondParams = {}
                
                for key in hb_hspeedevapcond.keys():
                    if hspeedevapcond.has_key(key) and hspeedevapcond[key] != None:
                        s = key + ' has been updated to ' + str(hspeedevapcond[key])
                        actions.append(s)
                        updatedCondParams[key] = hspeedevapcond[key]
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(hb_hspeedevapcond[key])
                        actions.append(s)
                        updatedCondParams[key] = hb_hspeedevapcond[key]
                
                evapCondenserDef = dictToClass(updatedCondParams)
                print 'your evaporative condenser definition has been uploaded and ready for use.  Your definition:'
                pp.pprint(updatedCondParams)
                print ''
                print 'actions completed for your coil definition: '
                for action in actions:
                    print action
            else:
                warning = "You need to provide service type."
                print warning
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                return evapCondenserDef
        else:
            print 'you must provide a unique name for this condenser definition.'
            
        
        return evapCondenserDef
            
evapCondenserDefinition = main()