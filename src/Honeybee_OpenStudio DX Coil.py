# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# this component can be used to create a custom DX coil, either 1 or 2 speed
# if you specify a one speed coil, just use the high speed inputs.  The low speed
# inputs will always be ignored for 1 speed coil definitions

"""
EPlus DX Coil
-
Provided by Honeybee 0.0.55

    Args:
        _dxCoilSpeed:...
        _name:...

        _availabilitySchedule_:...
        _ratedHighSpeedTotalCooling_: ...
        _ratedHighSpeedSensibleHeatRatio_: ...
        _ratedHighSpeedSensibleHeatRatio_: ...
        _ratedHighSpeedCOP_: ...
        _ratedLowSpeedTotalCooling_ ...
        _ratedLowSpeedSensibleHeatRatio_ ...
        _ratedLowSpeedCOP ...
        _condenserType ...
        _evaporativeCondenserDescription_ ...
        _Curves_ ...
        _unitInternalStaticPressure_ ...
    Returns:
        DXCoil:...

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

ghenv.Component.Name = "Honeybee_OpenStudio DX Coil"
ghenv.Component.NickName = 'EPlusDXCoil'
ghenv.Component.Message = 'VER 0.0.55\nSEP_22_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014

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
            return

        print 'Use this component to override a default DX cooling coil'
        print 'please note: '
        print 'capacity units are in Watts at the rated condition (not including fan heat.)'
        print 'COP and SHR are dimensionless engineering units at the rated condition.'
        print 'The rated condition is: '
        print 'air entering the cooling coil a 26.7C drybulb/19.4C wetbulb, air entering the outdoor condenser coil at 35C drybulb/23.9C wetbulb'
        if _dxCoilSpeed == None:
            print 'Before you can begin....'
            print 'you must provide a coil speed to use this component'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please provide a dxCoil Speed for the coil.")
        elif _dxCoilSpeed == 1:
            print 'We are now hunting for Honeybee defaults for 2 Speed DX Coils...'
            print 'We have found the Honeybee default for 2 Speed DX Coils: '
            hb_2xDXCoil = sc.sticky['honeybee_2xDXCoilParams']().twoSpeedDXDict
            pp = pprint.PrettyPrinter(indent=4)
        
            
            if _name!=None:
                pp.pprint(hb_2xDXCoil)
                print ''
                coil = {
                'name':_name,
                'availSch':_availabilitySchedule_,
                'ratedHighSpeedAirflowRate':_ratedHighSpeedAirflowRate_,
                'ratedHighSpeedTotalCooling':_ratedHighSpeedTotalCooling_,
                'ratedHighSpeedSHR':_ratedHighSpeedSensibleHeatRatio_,
                'ratedHighSpeedCOP':_ratedHighSpeedCOP_,
                'ratedLowSpeedAirflowRate':_ratedLowSpeedAirflowRate_,
                'ratedLowSpeedTotalCooling':_ratedLowSpeedTotalCooling_,
                'ratedLowSpeedSHR':_ratedLowSpeedSensibleHeatRatio_,
                'ratedLowSpeedCOP':_ratedLowSpeedCOP_,
                'condenserType':_condenserType_,
                'evaporativeCondenserDesc':_evaporativeCondenserDescription_,
                'Curves':_Curves_
                }
                
                #test to make sure the user inputs are correct, if not kill their description
                if _condenserType_ != None and condType[_condenserType_] == "Evaporatively Cooled":
                    if _evaporativeCondenserDescription_ == None:
                        print 'You have specified an Evaporatively Cooled Condenser,'
                        print 'But have not specified an evaporative condenser description.'
                        w = gh.GH_RuntimeMessageLevel.Error
                        ghenv.Component.AddRuntimeMessage(w, "You have specified an evaporatively cooled system.  Please specify an evaporative condenser description.")
                        DXCoil = []
                        
                
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
        elif (_dxCoilSpeed == 0):
            print "Single Speed Coil"
            
            print 'We are now hunting for Honeybee defaults for 1 Speed DX Coils...'
            print 'We have found the Honeybee default for 1 Speed DX Coils: '
            hb_1xDXCoil = sc.sticky['honeybee_1xDXCoilParams']().oneSpeedDXDict
            pp = pprint.PrettyPrinter(indent=4)
    
    
    
    
    
    
    
            if _name!=None:
                pp.pprint(hb_1xDXCoil)
                print ''
                coil = {
                'name':_name,
                'availSch':_availabilitySchedule_,
                'ratedAirflowRate':_ratedHighSpeedAirflowRate_,
                'ratedTotalCooling':_ratedHighSpeedTotalCooling_,
                'ratedSHR':_ratedHighSpeedSensibleHeatRatio_,
                'ratedCOP':_ratedHighSpeedCOP_,
                'condenserType':_condenserType_,
                'evaporativeCondenserDesc':_evaporativeCondenserDescription_,
                'Curves':_Curves_
                }
                
                if _ratedLowSpeedAirflowRate_ != None:
                    print 'your low speed airflow rate definition is ignored'
                    w = gh.GH_RuntimeMessageLevel.Remark
                    ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed coil.  All low speed definitions are ignored.")
                if _ratedLowSpeedTotalCooling_ != None:
                    print 'your low speed Total cooling capacity limitation definition is ignored'
                    w = gh.GH_RuntimeMessageLevel.Remark
                    ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed coil.  All low speed definitions are ignored.")
                if _ratedLowSpeedSensibleHeatRatio_ != None:
                    print 'your low speed Sensible Heat Ratio definition is ignored'
                    w = gh.GH_RuntimeMessageLevel.Remark
                    ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed coil.  All low speed definitions are ignored.")
                if _ratedLowSpeedCOP_ != None:
                    print 'your low speed COP definition is ignored'
                    w = gh.GH_RuntimeMessageLevel.Remark
                    ghenv.Component.AddRuntimeMessage(w, "You have selected a one speed coil.  All low speed definitions are ignored.")
                #test to make sure the user inputs are correct, if not kill their description
                if _condenserType_ != None and condType[_condenserType_] == "Evaporatively Cooled":
                    if _evaporativeCondenserDescription_ == None:
                        print 'You have specified an Evaporatively Cooled Condenser,'
                        print 'But have not specified an evaporative condenser description.'
                        w = gh.GH_RuntimeMessageLevel.Error
                        ghenv.Component.AddRuntimeMessage(w, "You have specified an evaporatively cooled system.  Please specify an evaporative condenser description.")
                        DXCoil = []
                        
                
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
    
    
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        DXCoil = []
    
    return DXCoil
    
    
    
DXCoil = main()