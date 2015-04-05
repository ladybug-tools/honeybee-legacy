# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Daysim electrical lighting control. Check this link for more information about lighting control types. http://daysim.ning.com/page/keyword-lighting-control
-
Provided by Honeybee 0.0.56
    
    Returns:
        lightingControlGroup: Lighting control Recipe
"""

ghenv.Component.Name = "Honeybee_Lighting control Recipe"
ghenv.Component.NickName = 'lightingControl'
ghenv.Component.Message = 'VER 0.0.56\nAPR_05_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Grasshopper.Kernel as gh

inputsDict = {
     
0 : ["_controlType_", "Lighting controlType: [0] Manual on/off switch, [1] Automate switch off occupancy sensor, [2] Always on during active occupancy hours, [3] Manual On/off with auto Dimming [4] Auto dimming with swith off occupancy sensor [5] Always on during active occupancy hours with auto dimming"],
1: ["sensorPoints_", "Selected list of test points that indicates where lighting sensor points are located."],
2: ["_lightingPower_", " Lighting power in watts. Default is 250 w."],
3: ["_lightingSetpoint_", "Target illuminance for the space. Default is 300 lux."],
4: ["_ballastLossFactor_", "Minimum electric dimming level in percentages."],
5: ["_standbyPower_", "Standby power in watts. Default is 3 w."],
6: ["_delayTime_", "Switch-off delay time in minutes. Default is 5 minutes."]
}

# manage component inputs

numInputs = ghenv.Component.Params.Input.Count
if _controlType_ == 0:
    for input in range(numInputs):
        if input > 2:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
else:
    for input in range(numInputs):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    
ghenv.Component.Attributes.Owner.OnPingDocument()

class LightingControl(object):
    
    def __init__(self, sensorPts, cntrlType, lightingPower = 250, lightingSetpoint = 300, ballastLossFactor = 20, standbyPower = 3, delayTime = 5):
        
        self.sensorPts = sensorPts
        self.lightingControlStr = self.getLightingControlStr(cntrlType, lightingPower, lightingSetpoint, ballastLossFactor, standbyPower, delayTime)
    
    def getLightingControlStr(self, cntrlType, lightingPower = 250, lightingSetpoint = 300, ballastLossFactor = 20, standbyPower = 3, delayTime = 5):
        
        cntrlType += 1
        
        # manual control
        lightingControlDict = {
        1 : 'manualControl',
        2 : 'onlyOffSensor',
        3 : 'onWhenOccupied',
        4 : 'dimming',
        5 : 'onlyOffSensorAndDimming',
        6 : 'onWithDimming'}
        
        lightingStr = `cntrlType` + " " + lightingControlDict[cntrlType] + " " + `lightingPower` + " 1 "
        
        if cntrlType != 1:
            lightingStr += `standbyPower` + " "
        
        if cntrlType > 3:
            lightingStr += `ballastLossFactor` + " " + `lightingSetpoint` + " "
        
        if cntrlType != 1 and cntrlType!=4:
            lightingStr += `delayTime`
        
        lightingStr += "\n"
        
        return lightingStr

try:
    lightingControlGroup = LightingControl(sensorPoints_, _controlType_, _lightingPower_, _lightingSetpoint_, _ballastLossFactor_, _standbyPower_, _delayTime_)
except:
    # controlType 0
    lightingControlGroup = LightingControl(sensorPoints_, _controlType_, _lightingPower_, 300, 20, 3, 5)
    
print lightingControlGroup.lightingControlStr
