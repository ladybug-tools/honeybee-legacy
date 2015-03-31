# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Mirror Material By Color
Read more here to understand Radiance materials: http://www.artifice.com/radiance/rad_materials.html
-
Provided by Honeybee 0.0.56

    Args:
        _materialName: Unique name for this material
        _color: color of the glass
    Returns:
        avrgTrans: Average transmittance of this glass
        RADMaterial: Radiance Material string

"""

ghenv.Component.Name = "Honeybee_Radiance Mirror Material By Color"
ghenv.Component.NickName = 'radMirrorMaterialByColor'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import scriptcontext as sc
import Grasshopper.Kernel as gh

# read here to understand RAD materials
# http://www.artifice.com/radiance/rad_materials.html


def getTransmissivity(transmittance):
    return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) - 0.9166530661 ) / 0.0036261119 / transmittance
    
def createRadMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  "0\n" + \
                  "0\n" + \
                  `int(len(args))`
                  
    for arg in args: radMaterial = radMaterial + (" " + "%.3f"%arg)
    
    return radMaterial + "\n"


def main():
    modifier = "mirror"
    
    if sc.sticky.has_key('honeybee_release'):
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
        if _materialName!=None and _color != None:
            RTransmittance = _color.R/255
            GTransmittance = _color.G/255
            BTransmittance = _color.B/255
            
            if 0 <= RTransmittance <= 1 and 0 <= GTransmittance <= 1 and 0 <= BTransmittance <= 1:
                avrgTrans = (0.265 * RTransmittance + 0.670 * GTransmittance + 0.065 * BTransmittance)
                
                materialName = _materialName.Replace(" ", "_")
                
                RADMaterial = createRadMaterial(modifier, materialName, RTransmittance, GTransmittance, BTransmittance)
                
                return RADMaterial
                
            else:
                msg =  "Transmittance values should be between 0 and 1"
                e = gh.GH_RuntimeMessageLevel.Error
                ghenv.Component.AddRuntimeMessage(e, msg)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

RADMaterial = main()