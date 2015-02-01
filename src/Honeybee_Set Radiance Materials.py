# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Radiance Default Materials
-
Provided by Honeybee 0.0.55

    Args:
        HBObject_: List of Honeybee zones or surfaces
        wallRADMaterial_: Optional wall material to overwrite the default walls
        windowRADMaterial_: Optional material for windows
        ceilingRADMaterial_: Optional material for ceilings
        roofRADMaterial_: Optional material for roofs
        floorRADMaterial_: Optional material for floors
        skylightRADMaterial_: Optional material for skylights
    Returns:
        modifiedHBObject: Honeybee object with updated materials

"""

ghenv.Component.Name = "Honeybee_Set Radiance Materials"
ghenv.Component.NickName = 'setRADMaterials'
ghenv.Component.Message = 'VER 0.0.55\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "01 | Daylight | Material"
#compatibleHBVersion = VER 0.0.55\nFEB_01_2015
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(HBObject, wallRADMaterial, windowRADMaterial, \
        ceilingRADMaterial, roofRADMaterial, floorRADMaterial, \
        skylightRADMaterial):
    
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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        HBObject = hb_hive.callFromHoneybeeHive([HBObject])[0]
        # check if the object is a zone or a surface
        if HBObject.objectType == "HBSurface":
            HBObjects = [HBObject]
        elif HBObject.objectType == "HBZone":
            HBObjects = HBObject.surfaces
            
    except Exception, e:
        HBObjects = None
    
    hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
    
    if HBObjects != None:
        for srf in HBObjects:
            if windowRADMaterial!=None and int(srf.type) != 1 and srf.hasChild:
                for childSrf in srf.childSrfs:
                    hb_RADMaterialAUX.assignRADMaterial(childSrf, windowRADMaterial, ghenv.Component)
            
            # check for slab on grade and roofs
            if skylightRADMaterial!=None and int(srf.type) == 1 and srf.hasChild:
                for childSrf in srf.childSrfs:
                    hb_RADMaterialAUX.assignRADMaterial(childSrf, skylightRADMaterial, ghenv.Component)
            
            if int(srf.type) == 0 and wallRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, wallRADMaterial, ghenv.Component)
            elif int(srf.type) == 1 and roofRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, roofRADMaterial, ghenv.Component)
            elif int(srf.type) == 2 and floorRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, floorRADMaterial, ghenv.Component)
            elif int(srf.type) == 3 and ceilingRADMaterial!=None:
                hb_RADMaterialAUX.assignRADMaterial(srf, ceilingRADMaterial, ghenv.Component)

        # add zones to dictionary
        HBObject  = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component.InstanceGuid.ToString())
        
        #print HBZones
        return HBObject
    
    else:
        return -1

if _HBObject:
    result = main(_HBObject, wallRADMaterial_, windowRADMaterial_, \
        ceilingRADMaterial_, roofRADMaterial_, floorRADMaterial_, \
        skylightRADMaterial_)
    if result!=-1:
        modifiedHBObject = result