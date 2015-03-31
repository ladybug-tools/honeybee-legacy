# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create a custom material for a window air gap, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
It is important to note that this component only creates gaps of air and not other gasses.
Also, the material out of this component represents only a single layer of air, which can be combined with the "Honeybee_EnergyPlus Glass Material" to make multi-pane windows.
If you have specifications for a whole window element and not individual panes of glass and gas, you are better-off using the "Honeybee_EnergyPlus Window Material" component instead of this one.

-
Provided by Honeybee 0.0.56
    
    Args:
        _name: A text name for your window air gap material.
        _thickness_: A number that represents the thickness of the air gap in meters.  The default is set to 0.0125 meters (1.25 cm).
    Returns:
        EPMaterial: A window air gap material that can be plugged into the "Honeybee_EnergyPlus Construction" component.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Window Air Gap"
ghenv.Component.NickName = 'EPWindowAirGap'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def main(name, thickness):
    
    if name == None: name = "AIRGAP"
    gasType = "AIR"
    if thickness == None: thickness = .0125
    
    values = [name.upper(), gasType, thickness]
    comments = ["Name", "Gas type", "Thickness {m}"]
    
    materialStr = "WindowMaterial:Gas,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !-" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !-" + str(comment)
            
    return materialStr

EPMaterial = main(_name_, _thickness_)
