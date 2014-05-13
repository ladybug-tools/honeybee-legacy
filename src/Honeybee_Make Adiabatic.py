# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Make Adiabatic

-
Provided by Honeybee 0.0.53

    Args:
        HBSrfs_: A list of valid Honeybee surfaces
    Returns:
        HBSrfs: Modified list of Honeybee surfaces with 
"""

ghenv.Component.Name = "Honeybee_Make Adiabatic"
ghenv.Component.NickName = 'makeAdiabatic'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBSurfaces = hb_hive.callFromHoneybeeHive(HBSrfs)
    for HBS in HBSurfaces:
        HBS.BC = "Adiabatic"
    
    HBSurfaces  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBSurfaces
    
if HBSrfs_ and HBSrfs_[0]!=None:
    HBSrfs = main(HBSrfs_)