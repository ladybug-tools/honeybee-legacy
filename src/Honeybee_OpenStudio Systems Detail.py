# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Constant Volume Fan
-
Provided by Honeybee 0.0.54

    Args:
        _fanName:
        _fanEfficiency_:...
        _pressureRise_: ...
        _maxFlowRate_: ...
        _motorEfficiency_: ...
        _motorPctInAirstream_: ...
    Returns:
        fanDefinition:...
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Systems Detail"
ghenv.Component.NickName = 'ConstantVolumeFan'
ghenv.Component.Message = 'VER 0.0.54\nAUG_21_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        

def main():
    cvFanParameters = []
    
    if sc.sticky.has_key('honeybee_release'):
        #check Honeybee version
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return  
        
        print 'you have selected a constant volume fan, this is typically used for ASHRAE system types 3 and 4'
        print 'We have found the Honeybee default Constant Volume Fan Definition: '
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
        print str(hb_flowpIP) + ' (Watts per cubic feet/second (US-IP units))'
        print ''
        print 'updating the Honeybee default constant volume to your definition.'
        
        fanComponent={}
        fanComponent['name'] = _fanName
        fanComponent['fanEfficiency'] = _fanEfficiency_
        fanComponent['pressureRise'] = _pressureRise_
        fanComponent['maxFlowRate'] = _maxFlowRate_
        fanComponent['motorEfficiency'] = _motorEfficiency_
        fanComponent['airStreamHeatPct'] = _motorPctInAirstream_
    
        if _fanName != None:
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
            
            cvFanParameters = dictToClass(storedFanParams)
            print 'your constant volume fan definition:'
            pp.pprint(storedFanParams)
            usFanTotalStaticPressure = storedFanParams['pressureRise']
            usFanEfficiency = storedFanParams['fanEfficiency']
            usMotorEfficiency = storedFanParams['motorEfficiency']
            us_flowpmetric = usFanTotalStaticPressure/(usFanEfficiency*usMotorEfficiency)
            print 'Your fan definition\'s constant volume fan power per unit flow is: ' 
            print str(us_flowpmetric) + ' (Watts per meters cubed/second (metric Units))'
            us_flowIP = us_flowpmetric/2118.879
            print str(us_flowIP) + ' (Watts per cubic feet/second (US-IP units))'
            print ''
            print 'Here are all the actions completed by this component:'
            pp.pprint(actions)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    
    return cvFanParameters

cvFanParameters = main()
