# Filter EnergyPlus Construction
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Search EnergyPlus construction based on Energy modeling standards, climate zone, surface type and building program

-
Provided by Honeybee 0.0.53
    
    Args:
        _EPConstrList: List of EPConstructions from Honeybee construction library
        _standard: Energy modeling standard [0:"ASHRAE 90.1", 1:"ASHRAE 189.1", 2:"CBECS 1980-2004", 3:"CBECS Before-1980"]
        climateZone_: Optional input for climate zone
        surfaceType_: Optional input for surface type > 0:'WALL', 1:'ROOF', 2:'FLOOR', 3:'CEILING', 4:'WINDOW'
        altBldgProgram_: Optional input for building type > 0:'RETAIL', 1:'OFFICE', 2:'RESIDENTIAL', 3:'HOTEL'
        constructionType_:
    Returns:
        EPSelectedConstr:  List of selected EP constructions that matches the the inputs

"""

ghenv.Component.Name = "Honeybee_Search EP Construction"
ghenv.Component.NickName = 'searchEPConstruction'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh


def main(constrList, standard, climateZone, surfaceType, bldgProgram, constructionType):
    
    # Make sure Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
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
    
    selConstruction = hb_EPMaterialAUX.filterMaterials(constrList, standard, climateZone, surfaceType, bldgProgram, constructionType, ghenv.Component)
    
    return selConstruction
    
    
if len(_EPConstrList)!=0 and _standard:
    result = main(_EPConstrList, _standard, climateZone_, surfaceType_, altBldgProgram_, constructionType_)
    if result!= -1: EPSelectedConstr = result