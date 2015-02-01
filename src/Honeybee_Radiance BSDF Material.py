# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance BSDF Material

Create RADIANCE BSDF material

-
Provided by Honeybee 0.0.56

    Args:
        _materialName: Name of material
        _XMLFilePath: File path to XML 
    Returns:
        RADMaterial: Radiance Material string
"""

ghenv.Component.Name = "Honeybee_Radiance BSDF Material"
ghenv.Component.NickName = 'radBSDFMaterial'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import os
import scriptcontext as sc
import Grasshopper.Kernel as gh

# A nice presentation on BSDF
# http://www.radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day2/GW5_BSDFFirstClass.pdf


def createBSDFMaterial(modifier, name, *args):
    # I should check the inputs here
    
    radMaterial = "void " + modifier + " " + name + "\n" + \
                  `int(len(args))`

    for arg in args:
        try: radMaterial += " " + "%.3f"%arg
        except: radMaterial += " " + str(arg)
    
    radMaterial += "\n0\n0\n"
    
    return radMaterial + "\n"

modifier = "BSDF"
function = "."

def main():
    
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
    
        if _materialName!=None and _XMLFilePath!=None:
            
            # check filepath for xml file
            if os.path.isfile(_XMLFilePath):
                
                materialName = _materialName.Replace(" ", "_")
                
                RADMaterial = createBSDFMaterial(modifier, materialName, thickness_, \
                                                _XMLFilePath.replace("\\", "/"), \
                                                _upOrientation_.X, _upOrientation_.Y, _upOrientation_.Z, function)
                
                return RADMaterial
                
            else:
                msg =  "Wrong path for XML file!"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, msg)
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        

RADMaterial = main()