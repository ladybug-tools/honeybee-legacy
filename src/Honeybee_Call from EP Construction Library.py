# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Call from EP Library

-
Provided by Honeybee 0.0.53
    
    Args:
        keywords_: List of keywords to filter the list of materials
            
    Returns:
        EPMaterials: List of EP materials in Honeybee library
        EPWindowMaterils: List of EP window materials in Honeybee library
        EPConstructios:  List of EP constructions in Honeybee library

"""

ghenv.Component.Name = "Honeybee_Call from EP Construction Library"
ghenv.Component.NickName = 'callFromEPConstrLibrary'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

if sc.sticky.has_key("honeybee_release") and sc.sticky.has_key("honeybee_constructionLib"):
    
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    
    EPConstructios = sc.sticky ["honeybee_constructionLib"]["List"]
    EPMaterials =  sc.sticky ["honeybee_materialLib"]["List"]
    EPWindowMaterils = sc.sticky ["honeybee_windowMaterialLib"]["List"]
    
    EPConstructios.sort()
    EPMaterials.sort()
    EPWindowMaterils.sort()
    
    if len(keywords_)!=0 and keywords_[0]!=None:
        EPConstructios = hb_EPMaterialAUX.searchListByKeyword(EPConstructios, keywords_)
        EPMaterials = hb_EPMaterialAUX.searchListByKeyword(EPMaterials, keywords_)
        EPWindowMaterils = hb_EPMaterialAUX.searchListByKeyword(EPWindowMaterils, keywords_)
        
else:
    print "You should first let the Honeybee fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")