# Decompose EnergyPlus Construction
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Filter EnergyPlus construction based on Energy modeling standards, climate zone, surface type and building program

-
Provided by Honeybee 0.0.55
    
    Args:
        _cnstrName: EnergyPlus construction name

    Returns:
        materials: List of materials (from outside to inside)
        comments: Comments for each layer of materials if any
        UValue_SI: U value of the construction in W/m2.K
        UValue_IP: U value of the construction in Btu/hft2F
"""

ghenv.Component.Name = "Honeybee_Decompose EP Construction"
ghenv.Component.NickName = 'DecomposeEPConstruction'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    try:
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    return hb_EPMaterialAUX.decomposeEPCnstr(cnstrName.upper())
    
    
if _cnstrName != None:
    data = main(_cnstrName)
    
    if data!=-1:
        materials, comments, UValue_SI, UValue_IP = data
        
        if UValue_SI and UValue_IP:
            RValue_SI = 1/UValue_SI
            RValue_IP = 1/UValue_IP
