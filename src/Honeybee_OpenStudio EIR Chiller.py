# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# this component can be used to create a custom DX coil, either 1 or 2 speed
# if you specify a one speed coil, just use the high speed inputs.  The low speed
# inputs will always be ignored for 1 speed coil definitions

"""
EPlus EIR Chiller
-
Provided by Honeybee 0.0.55

    Args:
        _name : ... provide a unique name for each chiller that you specify
        _rCapacity_: ....r=Reference condition chiller capacity (in Watts), if left blank, the capacity is autosized.
        _rCOP_ : ...r=Reference COP at design conditions (includes energy of the copressor only)
        _rLeavingChWt_: ...r=Reference Leaving Chilled Water Temp (in degrees Celsius).  If left blank, the default temperature is 6.67 degrees Celsius.
        _rEnteringCWT_: ... r=Reference Leaving Condenser Water Temp (in degrees Celsius).  If left blank, the default temperature is 29.4 degrees Celsius
        _rChWFlowRate_: ... r=Reference Chilled Water Flow Rate (in Meters Cubed Per Second). If left blank, the default flow rate is autosized.
        _rCWFlowRate_: ... r=Reference Condenser Water Flow Rate (in Meters Cubed Per Second). If left blank, the default flow rate is autosized.
        _minPartLoadRatio_ :... the minimum part load ratio of the chiller.  If left blank, the default value is 0.1.  Range 0.05 <= minPLR <= 0.25
        _maxPartLoadRatio_: ...  the maximum part load ratio of the chiller.  If left blank, the default value is 1.0.  Range 1 <= maxPLR <= 1.2
        _optimumPartLoadRatio_ :... the optimum part load ratio of the chiller.  If left blank, the default value is 1.0.  Range 0.05 <= maxPLR <= 1.2. Must be >= min and <= max.
        _minUnloadingRatio_: ... The PLR at which the chiller has to be falsely loaded to meet the actual load (usually by hot gas bypass).  If left blank, default is 0.2.
        _condenserType_: ... 0=WaterCooled, 1=AirCooled, 2=EvaporativelyCooled.  If left blank, the condenser is WaterCooled.  Ratio of CondenserFanPower to Reference compressor power (W/W).
        _condenserFanPowerRatio_: ...  Used only when condenserType is AirCooled or EvaporativelyCooled.  Dimensionless ratio Watts of fan power per Watt of Cooling at Design Conditions
        _fracOfCompressorPowerRej_: ... If hermetic compressor, value should be 1.0 (the default).  If open compressor, the motor efficiency. 0.0<=frac<=1.0 
        _chillerFlowMode_: ... 0:NotModulated (default), 1:ConstantFlow (constant volume pumping system), 2:LeavingSetpointModulated (vary flow to match temp setpoint)
        _sizingFactor_: use only when the capacities and flow rates are autosized.  Default is 1.0  1.0 <=sizingFactor<=1.3
        _Curves_: ... Not yet implemented.  Allows you to specify custom part load curves for chiller performance coils.

    Returns:
        ChillerDesc:...returns the chiller description
        
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio EIR Chiller"
ghenv.Component.NickName = 'EPlusEIRChiller'
ghenv.Component.Message = 'VER 0.0.55\nDEC_22_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

condenserDict={
0:'WaterCooled',
1:'AirCooled',
2:'EvaporativelyCooled'
}

flowModeDict={
0:'NotModulated',
1:'ConstantFlow',
2:'LeavingSetpointModulated'
}

def main(name,rCapacity,rCOP,rLeavingChWt,rEnteringCWT,rChWFlowRate,rCWFlowRate,minPartLoadRatio,maxPartLoadRatio,optimumPartLoadRatio,minUnloadingRatio,condenserType,condenserFanPowerRatio,fracOfCompressorPowerRej,chillerFlowMode,sizingFactor,Curves):
    print 'Use this component to override the default Chiller EIR Definition.'
    if sizingFactor != None:
        if sizingFactor < 1.0 or sizingFactor > 1.3:
            sizingFactor = 1.15
            warning = "You have declared a sizingFactor that is out of range." + \
            "  We have reset the sizingFactor to the honeybee default. " + \
            ": 1.15"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            chillerFlowMode = 0
            print 'sizingFactor reset to 1.15'
    if chillerFlowMode != None:
        if chillerFlowMode < 0 or chillerFlowMode > 2:
            warning = "You have declared a chillerFlowMode that is out of range." + \
            "  We have reset the chillerFlowMode to the honeybee default. " + \
            ": 0 (NotModulated)"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            chillerFlowMode = 0
        if not isinstance(chillerFlowMode,int):
            nmode=int(chillerFlowMode)
            chillerFlowMode = nmode
            warning = 'chillerFlowMode must be an integer.' + \
            '  chillerFlowMode reset to: ' + str(chillerFlowMode)
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, warning)
            print 'chillerFlowMode must be an integer'
            print 'chillerFlowMode set to: ' + str(chillerFlowMode)
    if minPartLoadRatio != None:
        if minPartLoadRatio < 0.05 or minPartLoadRatio > 0.25:
            warning = "You have declared a minPartLoadRatio that is out of range." + \
            "  We have reset the minPartLoadRatio to the honeybee default. " + \
            ": 0.1"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            minPartLoadRatio = None
    if maxPartLoadRatio != None:
        if maxPartLoadRatio < 1.0 or maxPartLoadRatio > 1.3:
            warning = "You have declared a maxPartLoadRatio that is out of range." + \
            "  We have reset the maxPartLoadRatio to the honeybee default. " + \
            ": 1.0"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            minPartLoadRatio = None
    if condenserType==None:
        condenserType = 0
    if chillerFlowMode == None:
        chillerFlowMode = 0
    if condenserType != 0:
        if condenserFanPowerRatio == None:
            warning = "You have not provided a condenserFanPowerRatio." + \
            "  Although you have declared a condenserType = " + condenserDict[condenserType] + \
            ".  We have used a default 0.012 W/W."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            condenserFanPowerRatio = 0.012
    chillerUpdates = {}
    pp = pprint.PrettyPrinter(indent=4)
    if sc.sticky.has_key('honeybee_release'):
        #place all standard warning messages here
        pass
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return chillerUpdates
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return chillerUpdates
        
        
        if name != None:
            print 'We are hunting for the default Honeybee Boiler Description.'
            hb_chiller = sc.sticky["honeybee_chillerEIRParams"]().chillerDict
            pp.pprint(hb_chiller)
            chiller= {
            'name':name,
            'rCapacity':rCapacity,
            'rCOP':rCOP,
            'rLeavingChWt':rLeavingChWt,
            'rEnteringCWT':rEnteringCWT,
            'rChWFlowRate':rChWFlowRate,
            'rCWFlowRate':rCWFlowRate,
            'minPartLoadRatio':minPartLoadRatio,
            'maxPartLoadRatio':maxPartLoadRatio,
            'optimumPartLoadRatio':optimumPartLoadRatio,
            'minUnloadingRatio':minUnloadingRatio,
            'condenserType':condenserDict[condenserType],
            'condenserFanPowerRatio':condenserFanPowerRatio,
            'fracOfCompressorPowerRej':fracOfCompressorPowerRej,
            'chillerFlowMode':flowModeDict[chillerFlowMode],
            'sizingFactor':sizingFactor,
            'Curves':Curves
            }
            print 'Your chiller definition:'
            pp.pprint(chiller)
            #update the hive
            actions = []
            updatedChillerParams = {}
            for key in hb_chiller.keys():
                if chiller.has_key(key) and chiller[key]!=None:
                    s=key+' has been updated to ' + str(chiller[key])
                    actions.append(s)
                    updatedChillerParams[key] = chiller[key]
                else:
                    s = key + ' is still set to Honeybee Default: '+ str(hb_chiller[key])
                    actions.append(s)
                    updatedChillerParams[key] = hb_chiller[key]
                    
            if updatedChillerParams['optimumPartLoadRatio'] < updatedChillerParams['minPartLoadRatio']:
                print 'The optimum part load ratio is less than the minPartLoadRatio.'
                print 'The optimum part load ratio has been reset to the honeybee default=1.0'
                updatedChillerParams['optimumPartLoadRatio']=1.0
                s='optimumPartLoadRatio has been reset to ' + str(1.0)
                actions.append(s)
                w=gh.GH_RuntimeMessageLevel.Remark
                ghenv.Component.AddRuntimeMessage(w, "optimumPartLoadRatio out of range.")
            if updatedChillerParams['optimumPartLoadRatio'] > updatedChillerParams['maxPartLoadRatio']:
                print 'The optimum part load ratio is greater than the maxPartLoadRatio.'
                print 'The optimum part load ratio has been reset to the honeybee default=1.0'
                updatedChillerParams['optimumPartLoadRatio']=1.0
                s='optimumPartLoadRatio has been reset to ' + str(1.0)
                actions.append(s)
                w=gh.GH_RuntimeMessageLevel.Remark
                ghenv.Component.AddRuntimeMessage(w, "optimumPartLoadRatio out of range.")
            chillerUpdates = dictToClass(updatedChillerParams)
            print 'Your chiller definition has been updated based on your definition and honeybee defaults: '
            pp.pprint(updatedChillerParams)
            print ""
            print 'Actions complieted for your chiller definition: '
            for action in actions:
                print action
        else:
            print 'You have not provided a name, which is a required field.  Use a panel to give your chiller a unique name.'
            print 'Before you can begin....'
            print 'you must provide a unique name for the chiller to use this component'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please provide a name for your chiller.")
    else:
        print "Your should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    return chillerUpdates


ChillerDesc = main(_name,_rCapacity_,_rCOP_,_rLeavingChWt_,_rEnteringCWT_,_rChWFlowRate_,_rCWFlowRate_,_minPartLoadRatio_,_maxPartLoadRatio_,_optimumPartLoadRatio_,_minUnloadingRatio_,_condenserType_,_condenserFanPowerRatio_,_fracOfCompressorPowerRej_,_chillerFlowMode_,_sizingFactor_,_Curves_)