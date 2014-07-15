# Decompose EnergyPlus Material
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Filter EnergyPlus construction based on Energy modeling standards, climate zone, surface type and building program

-
Provided by Honeybee 0.0.53
    
    Args:
        _materialName: EnergyPlus material name

    Returns:
        materials: List of materials (from outside to inside)
        comments: Comments for each layer of materials if any
        UValue_SI: U value of the construction in W/m2.K
        UValue_IP: U value of the construction in Btu/hft2F
"""

ghenv.Component.Name = "Honeybee_Decompose EP Material"
ghenv.Component.NickName = 'DecomposeEPMaterial'
ghenv.Component.Message = 'VER 0.0.53\nJUL_15_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
    
def main(matName):
    if not sc.sticky["honeybee_release"]:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    # get the constuction
    try:
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if sc.sticky.has_key("honeybee_materialLib"):
        return hb_EPMaterialAUX.decomposeMaterial(matName, ghenv.Component)
        

if _materialName!=None:
    results = main(_materialName)
    
    if results!=-1:
        values, comments, UValue_SI, UValue_IP = results
        names = _materialName
        RValue_SI = 1/UValue_SI
        RValue_IP = 1/UValue_IP
    