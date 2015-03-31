# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Ask Me!

-
Provided by Honeybee 0.0.56

    Args:
        _HBObjects: Any valid Honeybee object
    Returns:
        readMe!: Information about the Honeybee object
"""
ghenv.Component.Name = "Honeybee_AskMe"
ghenv.Component.NickName = 'askMe'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
try:
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(_HBObjects)
    for HBO in HBObjectsFromHive:
        print HBO
        #print HBO.getFloorArea()
        #print HBO.getZoneVolume()
        #for HBS in HBO.surfaces:
        #    print "----------------"
        #    #print HBS.getTotalArea()
        #    print "-----------------"
        #    print HBS
        #    print HBS.getOpaqueArea()
        #    print HBS.getWWR()
            
            
except Exception, e:
    print `e`
    pass
