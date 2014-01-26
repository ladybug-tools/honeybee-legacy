"""
Ask Me!

    Args:
        HBObjects: Any valid Honeybee object
    Returns:
        readMe!: Information about the Honeybee object
"""
ghenv.Component.Name = "Honeybee_AskMe"
ghenv.Component.NickName = 'askMe'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import scriptcontext as sc
try:
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBObjects)
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