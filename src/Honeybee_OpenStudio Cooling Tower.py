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

# this component can be used to create a custom Cooling Tower


"""
EPlus Cooling Tower
-
Provided by Honeybee 0.0.59
As per the EnergyPlus documentation, the user has two input options...enter the
tower performance using the UFactorTimeArea + design water flow rate OR
using the nominal capacity at a given rating condition.  The second is more
intuitive as an approach, in our opinion, but as data about cooling towers becomes
more readily available, this may change.

Currently this tower model assumes people are more comfortable with the capacity method.
Further development is required for the UFactorTimesArea method [for future]

It is possible to provide details of how the wet tower consumes water [for future]

Requirements for Two-Speed Cooling Towers:
    airflow rate at high and low speeds
    fan power fraction at high and low speeds
Optional for Two-Speed Cooling Towers:
    free convection heat transfer via
    airflow rate and UA during this mode or
    a nominal capacity during this mode
Note if you are modeling a multi-cell tower, it is assumed that the 
designWaterFlowRate, designAirflowRate, FanPower at design flow rate
airflowRate in FreeConvection, Nominal Capacity, and free convection capacity
Basin Heater capacity
are for ALL CELLS

    Args:
        _name_: a unique name for the cooling tower
        _speedControl_: an integer that defines the speed control of the cooling tower 1:1-speed, 2:2-speed (default if left blank), 3:variable speed
        _inputMethod_: an integer that defines how the cooling Tower performance is entered.  0:UFactorTimesAreaAndDesignWaterFlowRate (honeybee default if left blank) , 1:NominalCapacity
        _modelType_:  used only for Variable Speed towers, an input that defines the empirical model used for the cooling tower.  Provide an integer for 0:"CoolToolsCrossFlow" (default if left blank) or 1:"YorkCalc"
        _designWB_:  used only for Variable Speed towers, an input in deg Celsius, that indicates the outdoor wet bulb at design conditions.  If left blank, the default is 25.5556 degrees Celsius (78 degrees Fahrenheit).  Minimum is 20 degrees C
        _designRange_:  used only for Variable Speed towers, an input in deg Celsius, that indicates the difference in temperature between the water entering and leaving the tower.  If left blank, the default is 5.5556 degrees Celsius (10 degrees Celsius). Must be greater than 0.
        _designApproach_:  used only for Variable Speed towers, an input in deg Celsius, that indicates how close the leaving water temperature comes to the outdoor dry bulb (it will always be greater than the outdoor dry bulb).  If left blank, the default is 3.8889 degrees Celsius (7 degrees Fahrenheit).  Must be greater than o
        _sizingFactor_:  an optional field that allows a user to specify a sizing factor for the peak load when all components are autosized.  The default if left blank is 1.15 (recommended).  Variables affected by the sizing factor can be found in the EnergyPlus documentation.
        _nominalCapacity:  the nominal capacity at highest speed (in Watts) of the cooling tower assuming 95-85F leaving/entering water temperature, air at 78F WB, 95F DB, with design water flow rate at 3 GPM/ton.  If left blank, it autosizes
        _lowSpeedCapacity_:  the capacity at low fan speed (in Watts) of the cooling tower under same operating conditions as above.  This field will be ignored if the speed is not two-speed.
        _freeConvectionCapacity_: the capacity of the cooling tower with no fans (in Watts).  If free convection mode is not modeled, then this field should be set to zero. 
        _designWaterFlowRate_:  if the input method is 0 (UFactorTimesAreaAndDesignWaterFlowRate) then this is required (value is in cubic meters per second.  If left blank, this can be autosized based on
        _airflowAtHighSpeed_:  the tower airflow rate at high speed in cubic meters per second. If this is left blank, this field will be autosized (recommended).  The airflow rate assumes 190 Pascals of fan pressure rise an 0.5 total fan efficiency
        _fanPowerAtHighSpeed_:  the fan power at high airflow rate (in Watts).  If left blank, the fan power autosized (recommended) where the power is 0.0105 times the Tower's High Speed Capacity.
        _airflowAtLowSpeed_:  the flow rate in m3/s of the tower flow rate at low speed.  If left blank, it autosized (recommended) where the airflow rate is 50% of the airflow at high speed.  The airflow entered must be less than the airflow rate at high speed.
        _fanPowerAtLowSpeed_:  the fan power, (in Watts) at the low-speed airflow rate.  It can be autosized (recommended) where the fan power is set to 16% of the high speed fan power.
        _airflowInFreeConvection_:  the airflow in cubic meters per second through the tower when no fans are on.  If left blank, it can autosize.  If inputMethod=0, honeybee will assume it defaults to 0, if inputMethod=1, the airflow rate is 10% of the airFlowRate at high speed.
        _basinHeaterCapacity_:  the capaity (in Watts) of a basin heater that comes on to prevent freezing of the basin water.  If left blank, it will autosize to 0.  The heater only comes on when the fans are off, and the temperatre falls below the setpoint temperature
        _basinHeaterSetpointTemp_:  the setpoint temperature for the basin heater (in degrees C).  The heater is active when the outdoor dry bulb temperature falls below this temperature.  Temperature must be greater than 2 degrees C.  Default if blank is 2 degrees C.
        _basinHeaterSchedule_:  if left blank, it will default (recommended) to being "always available".  However this can be overridded to make it only available at certain times.
        _numberOfCells_: an integer specifying the number of cells.  If left blank, the assumption is a single-celled cooling tower
        _cellControl_:  an integer that specifies one of two options:  0=MinimalCell OR 1=MaximalCell.  Option 0 runs as few cells as possible at maximum water flow rate, option 1 assumes maximum cells at minimum water flow rate
        _cellMinWaterFlowFraction_:  specifies the smallest fraction of the design water flow rate.  Flows less than this would result in fluid distribution problems in the tower.  By default, if left blank (recommended), the default value is 0.33
        _cellMaxWaterFlowFraction_:  specifies the allowable largest fraction of design water flow rate.  This field can be autosized, with a default value of 2.5 (recommended)
        
        [for future]_heatRejectionCapacityFactor_:  a decimal indicating the capacity of the cooling tower.  By default, the factor is 1.25 (assumes that 25% of the load is turned into compressor heat to be rejected)
        [for future]_designUFactorTimesArea: a value between 0 and 300,000 that defines, in Watts per Kelvin, the heat transfer effectiveness of the cooling Tower.  If inputType is NominalCapacity, this field will be ignored by honeybee.  Left for future because this field can be autosized.
        [for future]_freeConvAirflowFactor:  is a value that is a fraction of the autocalculated peak flow rate, that is the free convection flow rate of the tower.  Left for future because this field is set to 0.1 by EnergyPlus by default.
        [for future]_freeConvUFactorTimesArea:  a value that is a fraction of the designUFactorTimesArea.  Left for future because this field has defaults or is autosized. If inputType is NominalCapacity, this field will be ignored by honeybee. 
        [for future]_freeConvNominalCapacityRatio:  a value that is a fraction of the Nominal capacity 
        [for future]_evaporationLossMode_:  used to chose which method to model the amount of water evaporated by the cooling tower.  There are two options (LossFactor or SaturatedExit (the default used for now)
        [for future]_evaporationLossFactor_:  the rate of water evaporated from the cooling tower (percent per kelvin).  Only used if the lossMode is LossFactor.  The default if left blank is 0.2, with a range between 0.15 - 0.27 
        [for future]_driftLossPercent_:  the rate of water lost to exiting air as entrained droplets (a percentage).  If left blank, it defaults to 0.008%, where towers with drift eliminators have avalues between 0.002% - 0.2%
        [for future]_blowDownCalculation_:  specifies which method is used to determine blowdown rates to prevent scaling.  Two options, ConcentrationRation or ScheduleRate with default already provided as ConcentrationRatio
        [for future]_blowDownConcentrationRatio_:  the ratio of solids in the blowdown water to solids in the make up water.  This field is used to adjust the rate of blowdown in the tower.  Default is 3, with values between 3 and 5 allowed.
        [for future]_blowdownMakeupSchedule_: a schedule that defines the amount of water (in m3/s) flushed from the basin periodically.  Only used if blowdown calc mode is ScheduledRate
        [for future]_storageTankName_:if specified, the tower will try and take all water from this unit before attempting to use the water mains
        
        
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Cooling Tower"
ghenv.Component.NickName = 'EPlusCoolingTower'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
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
        
inputMethodDict={
    0:'UFactorTimesAreaAndDesignWaterFlowRate', 
    1:'NominalCapacity'
}

speedControlDict={
    0:'SingleSpeed',
    1:'TwoSpeed',
    2:'VariableSpeed'
}

cellControlDict={
    0:'MinimalCell',
    1:'MaximalCell',
    2:'NotRequired'
}

def main(name,speedControl,inputMethod,modelType,designWB,designRange,designApproach,sizingFactor,
        nominalCapacity,designWaterFlowRate,airflowAtHighSpeed,
        fanPowerAtHighSpeed,lowSpeedCapacity,airflowAtLowSpeed,fanPowerAtLowSpeed,freeConvectionCapacity,
        airflowInFreeConvection,basinHeaterCapacity,basinHeaterSetpointTemp,basinHeaterSchedule,
        numberOfCells,cellControl,cellMinWaterFlowFraction,cellMaxWaterFlowFraction,fanPowerRatioFlowRatioCurve):
            
    #we assume for now that the user has some proficiency and understands the input mechanism
    #in general.  However some improvements for this section of the code:
    #range checking (to ensure values entered are reasonable)
    #type checking (is integer vs float)
    print "Use this component in combination with a water cooled chiller to model a cooling tower."
    #place all warnings here regarding user input
    if speedControl == None:
        print 'you have not defined speed control.  It will be defaulted to TwoSpeed.'
        speedControl = 1
        warning="If you would like to change the default for speed control, use a slider to define an integer."
        w=gh.GH_RuntimeMessageLevel.Remark
        ghenv.Component.AddRuntimeMessage(w,warning)
    elif speedControl > 2:
        print 'the only options for speed control are 0,1,or 2.'
        print 'the speedControl will be returned to default (1:TwoSpeed fan)'
        speedControl = 1
        warning='you may only enter an integer = 0,1, or 2.  Other values are ignored'
        w=gh.GH_RuntimeMessageLevel.Remark
        ghenv.Component.AddRuntimeMessage(w,warning)
    if inputMethod == None:
        print 'you have not specified an input method.  Defaulting to 1:NominalCapacity'
        message='If you would like to change the inputMethod, use a slider to define a proper integer.'
        inputMethod = 1
        w=gh.GH_RuntimeMessageLevel.Remark
        ghenv.Component.AddRuntimeMessage(w,message)
    elif inputMethod>1:
        pass
    if cellControl == None:
        if (numberOfCells==None or numberOfCells==1):
            cellControl = 2
            print 'honeybee defining cell control method for single celled tower.'
        else:
            print 'you have not specified a cell control method.'
            print 'but you have specified more than one cell in the tower.'
            message = 'Because you have specified more than one tower cell, but no cell control strategy, we have provided a default: "Maximum Cells".'
            w=gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w,message)
            cellControl=1
        
    towerUpdates={}
    pp=pprint.PrettyPrinter(indent=4)
    
    if sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return towerUpdates
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            
        if name != None:
            print 'We are hunting for the default Honeybee cooling tower Description.'
            hb_coolTower = sc.sticky["honeybee_coolingTowerParams"]().coolTowerDict
            print 'Here is the honeybee default cooling tower description:'
            pp.pprint(hb_coolTower)
            coolingTower= {
                'name':name,
                'speedControl':speedControlDict[speedControl],
                'inputMethod':inputMethodDict[inputMethod],
                'modelType':modelType,
                'designWB':designWB,
                'designRange':designRange,
                'designApproach':designApproach,
                'sizingFactor':sizingFactor,
                'nominalCapacity':nominalCapacity,
                'designWaterFlowRate':designWaterFlowRate,
                'airflowAtHighSpeed':airflowAtHighSpeed,
                'fanPowerAtHighSpeed':fanPowerAtHighSpeed,
                'lowSpeedCapacity':lowSpeedCapacity,
                'airflowAtLowSpeed':airflowAtLowSpeed,
                'fanPowerAtLowSpeed':fanPowerAtLowSpeed,
                'freeConvectionCapacity':freeConvectionCapacity,
                'airflowInFreeConvection':airflowInFreeConvection,
                'basinHeaterCapacity':basinHeaterCapacity,
                'basinHeaterSetpoint':basinHeaterSetpointTemp,
                'basinHeaterSchedule':basinHeaterSchedule,
                'numberOfCells':numberOfCells,
                'cellControl':cellControlDict[cellControl],
                'cellMinWaterFlowFraction':cellMinWaterFlowFraction,
                'cellMaxWaterFlowFraction':cellMaxWaterFlowFraction,
                'fanPowerRatioFlowRatioCurve':fanPowerRatioFlowRatioCurve
            }
            print 'Your current cooling tower definition:'
            pp.pprint(coolingTower)
            print 'Making a new cooling tower definition, combining yours with Honeybee defaults.'
            actions=[]
            updatedCoolingTowerParams={}
            for key in hb_coolTower.keys():
                if coolingTower.has_key(key) and coolingTower[key] != None:
                    s=key+' updated to ' + str(coolingTower[key])
                    actions.append(s)
                    updatedCoolingTowerParams[key]=coolingTower[key]
                else:
                    updatedCoolingTowerParams[key]=hb_coolTower[key]
                    
            towerUpdates=dictToClass(updatedCoolingTowerParams)
            print "\n"
            print 'Actions completed: '
            for action in actions:
                print action
            print 'Here is the final cooling Tower definition: '
            pp.pprint(updatedCoolingTowerParams)
            
        else:
            print "You must provide a name for your cooling tower.  Attach a panel with a name."
            warning="You must provide a unique name for the cooling tower."
            w=gh.GH_RuntimeMessageLevel.Error
            ghenv.Component.AddRuntimeMessage(w,warning)
    else:
        print "Your should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    print towerUpdates.d
    return [towerUpdates]
    
coolingTower = main(_name,_speedControl_,_inputMethod_,_modelType_, _designWB_, _designRange_,_designApproach_,
                _sizingFactor_,_nominalCapacity,_designWaterFlowRate_,_airflowAtHighSpeed_,
                _fanPowerAtHighSpeed_,_lowSpeedCapacity_,_airflowAtLowSpeed_,_fanPowerAtLowSpeed_,
                _freeConvectionCapacity_,_airflowInFreeConvection_,_basinHeaterCapacity_,
                _basinHeaterSetpointTemp_,_basinHeaterSchedule_,_numberOfCells_,
                _cellControl_,_cellMinWaterFlowFraction_,_cellMaxWaterFlowFraction_,_fanPowerRatioflowRatioCurve_)
                
