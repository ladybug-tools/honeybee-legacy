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

ghenv.Component.Name = "Honeybee_Make Adiabatic By Type"
ghenv.Component.NickName = 'makeAdiabaticByType'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh

def main(HBZones, walls, roofs, floors, ceilings):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    types = []
    if walls: types.append(0)
    if roofs: types.append(1)
    if floors: types.append(2)
    if ceilings: types.append(3)
    
    for HBO in HBObjectsFromHive:
        
        for HBS in HBO.surfaces:
            if int(HBS.type) in types and not HBS.hasChild:
                HBS.BC = "Adiabatic"
                HBS.sunExposure = "NoSun"
                HBS.windExposure = "NoWind"
    
    HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    
    return HBZones
    
    
if HBZones_ and HBZones_[0]!=None:
    HBZones = main(HBZones_, walls_, roofs_, floors_, ceilings_)