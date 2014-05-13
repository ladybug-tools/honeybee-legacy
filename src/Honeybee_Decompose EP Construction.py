# Decompose EnergyPlus Construction
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Filter EnergyPlus construction based on Energy modeling standards, climate zone, surface type and building program

-
Provided by Honeybee 0.0.53
    
    Args:
        _cnstrName: EnergyPlus construction name

    Returns:
        materials: List of materials (from outside to inside)
        comments: Comments for each layer of materials if any
        UValue_SI: U value of the construction in W/K.m2
        UValue_IP: U value of the construction in Btu/hft2F
"""

ghenv.Component.Name = "Honeybee_Decompose EP Construction"
ghenv.Component.NickName = 'DecomposeEPConstruction'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc


def main(cnstrName):
    # Make sure Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    try:
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    return hb_EPMaterialAUX.decomposeEPCnstr(cnstrName)
    
    
if _cnstrName != None:
    data = main(_cnstrName)
    
    if data!=-1: materials, comments, UValue_SI, UValue_IP = data
