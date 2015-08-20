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

# this component can be used to create a custom DX coil, either 1 or 2 speed
# if you specify a one speed coil, just use the high speed inputs.  The low speed
# inputs will always be ignored for 1 speed coil definitions

"""
EPlus Hot Water Boiler
-
Provided by Honeybee 0.0.57

    Args:
        _name : ... provide a unique name for each boiler that you specify
        _sequence: ...is a placeholder now (defaulted always to zero.  should allow users to create multiple boilers and assign sequencing capabilities.  Must be an integer, including zero.
        _fuelType_ : ... Leave blank and the default is NaturalGas.  Choices are 0=Electricity, 1=NaturalGas, 2=PropaneGas, 3=FuelOil#1, 4=FuelOil#2, 5=Coal, 6=Diesel, 7=Gasoline, 8=OtherFuel1, 9=OtherFuel2
        _nominalCapacity_: ...If left blank, a boiler will be autosized.  However, entering a value allows the capacity to be user-defined, (the Units are in Watts).
        _sizingFactor_: ... a dimensionless number that will be multiplied by the capacity and the design water flow rate.  Usually will be something like "1.1" (a 10% increase).
        _nominalEfficiency_: ... The thermal capacity of the boiler.  A value between 0 and 1.
        _designOutletTemperature_: ... If left blank?, otherwise enter a value to specify the leaving temp at design, in Celsius
        _designWaterFlowRate_: ... If left blank ?, the water flow rate will autosize.  Otherwise enter a value to specify the design water flow rate (units are meters cubed per second) 
        _minPartLoad_ :... Specify a value for the boiler turndown.
        _maxPartLoadRatio_: ...  Specify a value for the max boiler capacity (cannot exceed 1.1)
        _optimumPartLoadRatio_ :... Specify a value for the ideal operating part load ration (between min and max part load ratio)
        _outletTempMaximum_: ... If left blank, the value is 99 degrees Celsius.  Otherwise provide your own value for the maximum temperature out of the boiler.  This value cannot exceed 99.
        _boilerFlowMode_: ... The default, if not specified, is "NotModulated".  However, there are three available choices.  "NotModulated", "ConstantFlow", and "LeavingSetpointModulated"
        _parasiticElectricLoad_: ...  The default, if not specified, is 0 (zero).  Provide a value to indicate, in Watts, how much parasitic power is consumed by the boiler by controls, fans, or pumps integral to the boiler.
        _curveTemperatureVariable_: ... There are two options: "EnteringBoiler" and "LeavingBoiler".  This value is used to control which value of hot water to use when evaluating efficiency curves (if provided).
        _Curves_ ... Not yet implemented.  Allows you to specify custom part load curves for DX coils.

    Returns:
        HotWaterBoiler:...returns the hot water boiler description
        
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Hot Water Boiler"
ghenv.Component.NickName = 'EPlusHotWaterBoiler'
ghenv.Component.Message = 'VER 0.0.57\nJUL_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

fuelDict={
0:'Electricity',
1:'NaturalGas',
2:'PropaneGas',
3:'FuelOil#1',
4:'FuelOil#2',
5:'Coal',
6:'Diesel',
7:'Gasoline',
8:'OtherFuel1',
9:'OtherFuel2'
}

def main(name,fuelType,nominalCapacity,sizingFactor,nominalEfficiency,designOutletTemperature,designWaterFlowRate,minPartLoadRatio,maxPartLoadRatio,optimumPartLoadRatio,outletTempMaximum,boilerFlowMode,parasiticElectricLoad,curveTemperatureVariable,Curves):
    print 'Use this component to override the default Hot Water Boiler Definition.'
    print 'Please note, the fuel type requires an integer to define the type.'
    print '0=Electricity'
    print '1=Natural Gas (Default if you provide nothing)'
    print '2=PropaneGas'
    print '3=FuelOil#1'
    print '4=FuelOil#2'
    print '5=Coal'
    print '6=Diesel'
    print '7=Gasoline'
    print '8=OtherFuel1'
    print '9=OtherFuel2'
    print fuelType
    if fuelType==None:
        fuelType = 1
    boilerUpdates = {}
    pp = pprint.PrettyPrinter(indent=4)
    if sc.sticky.has_key('honeybee_release'):
        #place all standard warning messages here
        pass
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return boilerUpdates
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return boilerUpdates
        
        
        if name != None:
            print 'We are hunting for the default Honeybee Boiler Description.'
            hb_hwBoiler = sc.sticky["honeybee_hwBoilerParams"]().hwBoilerDict
            pp.pprint(hb_hwBoiler)
            hwBoiler= {
            'name':name,
            'fueltype':fuelDict[fuelType],
            'nominalCapacity':nominalCapacity,
            'sizingFactor':sizingFactor,
            'nominalEfficiency':nominalEfficiency,
            'designOutletTemperature':designOutletTemperature,
            'minPartLoad':minPartLoadRatio,
            'maxPartLoadRatio':maxPartLoadRatio,
            'optimumPartLoadRatio':optimumPartLoadRatio,
            'outletTempMaximum':outletTempMaximum,
            'boilerFlowMode':boilerFlowMode,
            'parasiticElectricLoad':parasiticElectricLoad,
            'curveTemperatureVariable':curveTemperatureVariable,
            'Curves':Curves
            }
            print hwBoiler
            #update the hive
            actions = []
            updatedBoilerParams = {}
            for key in hb_hwBoiler.keys():
                if hwBoiler.has_key(key) and hwBoiler[key]!=None:
                    s=key+' has been updated to ' + str(hwBoiler[key])
                    actions.append(s)
                    updatedBoilerParams[key] = hwBoiler[key]
                else:
                    s = key + ' is still set to Honeybee Default: '+ str(hb_hwBoiler[key])
                    actions.append(s)
                    updatedBoilerParams[key] = hb_hwBoiler[key]
                    
            boilerUpdates = dictToClass(updatedBoilerParams)
            print 'Your Hot Water Boiler definition has been uploaded and ready for use.  Your definition: '
            pp.pprint(updatedBoilerParams)
            print ""
            print 'Actions complieted for your boiler definition: '
            for action in actions:
                print action
        else:
            print 'You have not provided a name, which is a required field.  Use a panel to give your boiler a unique name.'
    else:
        print "Your should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    return boilerUpdates


HotWaterBoiler = main(_name,_fuelType_,_nominalCapacity_,_sizingFactor_,_nominalEfficiency_,_designOutletTemperature_,
_designWaterFlowRate_,_minPartLoadRatio_,_maxPartLoadRatio_,_optimumPartLoadRatio_,_outletTempMaximum_,_boilerFlowMode_,
_parasiticElectricLoad_,_curveTemperatureVariable_,_Curves_)
