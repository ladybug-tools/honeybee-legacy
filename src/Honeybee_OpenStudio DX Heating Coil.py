# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# this component can be used to create a custom DX coil, either 1 or 2 speed
# if you specify a one speed coil, just use the high speed inputs.  The low speed
# inputs will always be ignored for 1 speed coil definitions

"""
EPlus DX Heating Coil
-
Provided by Honeybee 0.0.56

    Args:
        _dxCoilSpeed:...0 = 1 speed, 1 = 2 speed
        _name:...provide a unique coil for each one that you use

        _availabilitySchedule_:... an OpenStudio or Honeybee can be plugged in here to limit the availability of the cooling coil.
        _ratedHighSpeedTotalCooling_: ...This value is typically blank, it can be autosized (the Units are in Watts)/
        _ratedHighSpeedCOP_: ... the efficiency at design conditions for the DX coil
        _ratedLowSpeedTotalCooling_: ... This value is typically blank, it can be autosized (the Units are in Watts)/
        _ratedLowSpeedCOP_: ... the efficiency at design conditions for the DX coil
        _minimumOutdoorDryBulb_: ... If left blank, the default is -8C (17.6F) temperature when the compressor is shut off
        _outdoorDryBulbDefrostDisabled_ :... If left blank, the default is 5C (41F).  It is the temperature, below which, defrost is enabled to de-ice the heat source.
        _maxOutdoorDryBulbForCrankcase_: ... If left blank, the default is 10C (50F).  It is the temperature above which the compressor crankcase heater is disabled.
        _crankCaseHeaterCapacity_ :... If left blank, the default is zero.  It is the capacity of the compressor crankcase heater (Watts), which will turn on if below the stated temperature and the compressor is not running.
        _defrostStrategy_: ... If left blank, the default is 'ReverseCycle'.  Two options for this 'ReverseCycle', 'Resistive'.  Spelling must be correct.  It is the type of heating cycle used to melt frost accumulated on the outdoor coil.
        _defrostControl_: ... If left blank, the default is 'timed'.  Two options are 'timed' and 'on-demand'.
        _resistiveDefrostHeatCap_:  If left blank, the default in honeybee is zero.  It is the capacity in Watts of the resistive element used for defrost.
        _Curves_ ... Not yet implemented.  Allows you to specify custom part load curves for DX coils.
        _unitInternalStaticPressure_ ... (units are Pascals).  This item is rarely used, but helps to calculate EER and IEER for variable speed DX systems.  Refers to the total internal pressure of the air handler.
    Returns:
        DXCoil:...return DX coil definition

"""
#high/low speed airflow between .00004027 to .00006041 m3/s per Watt
#high/low speed airflow between .00001667 to .00003355 m3/s per Watt for DOAS
#add unit internal static air pressure?  will be used to calculate EER for variable volume fans (if not used, 773.3 W/m3/s for specific fan power
#COP hi lo default is 3

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio DX Heating Coil"
ghenv.Component.NickName = 'EPlusDXHeatingCoil'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


#this is to class-i-fy the dictionary
class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        
#this dictionary used for reporting messages to the only
condType = {
0:'Air Cooled',
1:'Evaporatively Cooled'
}



def main():
    print 'Use this component to override a default DX heating coil'
    print 'please note: '
    print 'capacity units are in Watts at the rated condition (not including fan heat.)'
    print 'COP is a dimensionless engineering units at the rated condition.'
    print 'The rated condition is: '
    print 'air entering the cooling coil a 21.11C drybulb/15.55C wetbulb, air entering the outdoor condenser coil at 8.33C drybulb/6.11C wetbulb,'
    #setup
    DXCoil = []
    pp = pprint.PrettyPrinter(indent=4)
    
    #main warnings and error checking of user input
    #if the Defrost strategy is resistive, the user should have to provide a resistive capacity
    if _defrostStrategy_ != None:
        if _defrostStrategy_ == 'Resistive':
            if _resistiveDefrostHeatCap_ == None:
                print 'You have specified a defrost strategy of Resistive, but you have not set a Defrost Heat Capacity (in Watts)'
                print 'The default resistive heater capacity in Honeybee is 0 Watts.  Please provide a resistive capacity.'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, 'Please provide a resistiveDefrostHeaterCap.  See readMe output for more details.')
        elif _defrostStrategy_ != "ReverseCycle":
            print 'The only allowable defrostStragegy inputs are "Resistive" and "ReverseCycle".  Any other inputs will be ignored.'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, 'Your defrost strategy is invalid and this component will not run.')
            return DXCoil
    if _Curves_ != None:
        print 'Custom efficiency and capacity curves will be provided in a future release of Honeybee.'
        w = gh.GH_RuntimeMessageLevel.Remark
        ghenv.Component.AddRuntimeMessage(w, 'Your curves definition will be ignored.')
        
    if _dxCoilSpeed == 0:
        if _ratedLowSpeedAirflowRate_ != None:
            message =  'All low speed settings are ignored when DX Coil is Single Speed (dxCoilSpeed=0).'
            print message
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, message)
        if _ratedLowSpeedTotalHeating_ != None:
            message =  'All low speed settings are ignored when DX Coil is Single Speed (dxCoilSpeed=0).'
            print message
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, message)
        if _ratedLowSpeedCOP_ != None:
            message =  'All low speed settings are ignored when DX Coil is Single Speed (dxCoilSpeed=0).'
            print message
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, message)
    if sc.sticky.has_key('honeybee_release'):
        #check Honeybee version
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return DXCoil

        if _dxCoilSpeed == None:
            print 'Before you can begin....'
            print 'you must provide a coil speed to use this component'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please provide a dxCoil Speed for the coil.")
        elif _dxCoilSpeed == 0:
            print 'We are now hunting for Honeybee defaults for 1 Speed DX Heating Coils...'
            
            try:
                hb_1xDXCoil = sc.sticky["honeybee_1xDXHeatingCoilParams"]().oneSpeedDXDict
                print 'We have found the Honeybee default for 1 Speed DX Heating Coils: '
            except:
                print 'We could not find the Honeybee default for 1 Speed DX Heating Coils'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Cannot locate default Honeybee 1 Speed DX Heating Coil.")
                return DXCoil

            if _name!=None:
                pp.pprint(hb_1xDXCoil)
                print ''
                coil = {
                'name':_name,
                'availSch':_availabilitySchedule_,
                'ratedAirflowRate':_ratedHighSpeedAirflowRate_,
                'ratedTotalHeating':_ratedHighSpeedTotalHeating_,
                'ratedCOP':_ratedHighSpeedCOP_,
                'minOutdoorDryBulb': _minimumOutdoorDryBulb_,
                'outdoorDBDefrostEnabled': _outdoorDryBulbDefrostDisabled_,
                'outdoorDBCrankcase': _maxOutdoorDryBulbForCrankcase_,
                'crankcaseCapacity': _crankCaseHeaterCapacity_,
                'defrostStrategy': _defrostStrategy_,
                'defrostControl': _defrostControl_,
                'resistiveDefrostCap': _resistiveDefrostHeatCap_,
                'Curves':_Curves_
                }

                #update the hive
                actions = []
                updatedCoilParams = {}
                updatedCoilParams['type'] = _dxCoilSpeed
                for key in hb_1xDXCoil.keys():
                    if coil.has_key(key) and coil[key] != None:
                        s = key + ' has been updated to ' + str(coil[key])
                        actions.append(s)
                        updatedCoilParams[key] = coil[key]
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(hb_1xDXCoil[key])
                        actions.append(s)
                        updatedCoilParams[key] = hb_1xDXCoil[key]
                        
                #two speed coil output to class
                DXCoil = dictToClass(updatedCoilParams)
                print 'your coil definition has been uploaded and ready for use.  Your coil:'
                pp.pprint(updatedCoilParams)
                print ''
                print 'actions completed for your coil definition: '
                for action in actions:
                    print action
            else:
                print 'Before you can begin....'
                print 'you must provide a unique name for the coil to use this component'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Please provide a name for this coil.")
                return DXCoil
        elif (_dxCoilSpeed == 1):
            print 'We currently only support one speed DX Heating Coils.'
            print 'Please set dxCoilSpeed to Single Speed (=0)'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Honeybee currently only supports one speed coils.")
            return DXCoil
            print 'We are now hunting for Honeybee defaults for 2 Speed DX Heating Coils...'
            
            try:
                hb_2xDXCoil = sc.sticky["honeybee_2xDXHeatingCoilParams"]().twoSpeedDXDict
                print 'We have found the Honeybee default for 2 Speed DX Heating Coils: '
            except:
                print 'We could not find the Honeybee default for 2 Speed DX Heating Coils'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Cannot locate default Honeybee 2 Speed DX Heating Coil.")
                return DXCoil
            if _name!=None:
                pp.pprint(hb_2xDXCoil)
                print ''
                coil = {
                'name':_name,
                'availSch':_availabilitySchedule_,
                'ratedHighSpeedAirflowRate':_ratedHighSpeedAirflowRate_,
                'ratedHighSpeedTotalHeating':_ratedHighSpeedTotalHeating_,
                'ratedHighSpeedCOP':_ratedHighSpeedCOP_,
                'ratedLowSpeedAirflowRate':_ratedLowSpeedAirflowRate_,
                'ratedLowSpeedTotalHeating':_ratedLowSpeedTotalHeating_,
                'ratedLowSpeedCOP':_ratedLowSpeedCOP_,
                'minOutdoorDryBulb': _minimumOutdoorDryBulb_,
                'outdoorDBDefrostEnabled': _outdoorDryBulbDefrostDisabled_,
                'outdoorDBCrankcase': _maxOutdoorDryBulbForCrankcase_,
                'crankcaseCapacity': _crankCaseHeaterCapacity_,
                'defrostStrategy': _defrostStrategy_,
                'defrostControl': _defrostControl_,
                'resistiveDefrostCap': _resistiveDefrostHeatCap_,
                'Curves':_Curves_
                }
             
                        
                
                #update the hive
                actions = []
                updatedCoilParams = {}
                updatedCoilParams['type'] = _dxCoilSpeed
                for key in hb_2xDXCoil.keys():
                    if coil.has_key(key) and coil[key] != None:
                        s = key + ' has been updated to ' + str(coil[key])
                        actions.append(s)
                        updatedCoilParams[key] = coil[key]
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(hb_2xDXCoil[key])
                        actions.append(s)
                        updatedCoilParams[key] = hb_2xDXCoil[key]
                        
                #two speed coil output to class
                DXCoil = dictToClass(updatedCoilParams)
                print 'your coil definition has been uploaded and ready for use.  Your coil:'
                pp.pprint(updatedCoilParams)
                print ''
                print 'actions completed for your coil definition: '
                for action in actions:
                    print action
            else:
                print 'Before you can begin....'
                print 'you must provide a unique name for the coil to use this component'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Please provide a name for this coil.")
            
    
    
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        
    
    return DXCoil
    
    
    
DXCoil = main()