"""
Radiance Glass Material
Read more here to understand Radiance materials: http://www.artifice.com/radiance/rad_materials.html
-
Provided by Honybee 0.0.10
    
    Args:
        materialName: Unique name for this material
        RTransmittance: Transmittance for red. The value should be between 0 and 1
        GTransmittance: Transmittance for green. The value should be between 0 and 1
        BTransmittance: Transmittance for blue. The value should be between 0 and 1
        refractiveIndex: RefractiveIndex is 1.52 for glass and 1.4 for ETFE
    Returns:
        avrgTrans: Average transmittance of this glass
        RADMaterial: Radiance Material string

"""

ghenv.Component.Name = "Honeybee_Radiance Glass Material"
ghenv.Component.NickName = 'radGlassMaterial'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "1 | Daylight | Material"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import math
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh



# refractiveIndex is 1.52 for glass and 1.4 for ETFE

def getTransmissivity(transmittance):
    if transmittance != 0:
        transmissivity = (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) - 0.9166530661 ) / 0.0036261119 / transmittance
    else:
        return 0
        
    if transmissivity>1: return 1
    
    return transmissivity
    
def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args:
        radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"


modifier = "glass"

if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
    if RTransmittance!=None and GTransmittance!=None and BTransmittance!=None:
        if 0 <= RTransmittance <= 1 and 0 <= GTransmittance <= 1 and 0 <= BTransmittance <= 1:
            
            avrgTrans = (0.265 * RTransmittance + 0.670 * GTransmittance + 0.065 * BTransmittance)
            
            materialName = materialName.Replace(" ", "_")
            RADMaterial = createRadMaterial(modifier, materialName, getTransmissivity(RTransmittance), getTransmissivity(GTransmittance), getTransmissivity(BTransmittance), refractiveIndex)
        else:
            msg =  "Transmittance values should be between 0 and 1"
            e = gh.GH_RuntimeMessageLevel.Error
            ghenv.Component.AddRuntimeMessage(e, msg)
else:
    print "You should first let both Ladybug and Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")