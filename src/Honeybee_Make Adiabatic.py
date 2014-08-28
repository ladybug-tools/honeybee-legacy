# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Make Adiabatic

-
Provided by Honeybee 0.0.54

    Args:
        HBSrfs_: A list of valid Honeybee surfaces
    Returns:
        HBSrfs: Modified list of Honeybee surfaces with 
"""

ghenv.Component.Name = "Honeybee_Make Adiabatic"
ghenv.Component.NickName = 'makeAdiabatic'
ghenv.Component.Message = 'VER 0.0.54\nAUG_25_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

def main(HBSrfs):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBSurfaces = hb_hive.callFromHoneybeeHive(HBSrfs)
    for HBS in HBSurfaces:
        HBS.BC = "Adiabatic"
    
    HBSurfaces  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBSurfaces
    
if HBSrfs_ and HBSrfs_[0]!=None:
    HBSrfs = main(HBSrfs_)