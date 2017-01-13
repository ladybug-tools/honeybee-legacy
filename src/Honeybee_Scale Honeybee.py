ghenv.Component.Name = "Honeybee_Scale Honeybee"
ghenv.Component.NickName = 'scaleHBObj'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import scriptcontext as sc
import uuid
import Rhino as rc

"""
Scale Honeybee Objects Non-Uniformly
-
Provided by Honeybee 0.0.60
    Args:
        _HBObj: Honeybee surface or Honeybee zone
        P: Base Plane
        X: Scaling factor in {x} direction
        Y: Scaling factor in {y} direction
        Z: Scaling factor in {z} direction
    Returns:
        HBObjs: Transformed objects
"""


def main(HBObj, P,X,Y,Z):

    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        HBObject = hb_hive.callFromHoneybeeHive([HBObj])[0]
    except:
        raise TypeError("Wrong input type for _HBObj. Connect a Honeybee Surface or a HoneybeeZone to HBObject input")
    
    if not P:
        
        P = rc.Geometry.Plane(rc.Geometry.Point3d(0,0,0),rc.Geometry.Vector3d(0,0,1))
        
    if not X:
        
        X = 1
        
    if not Y:
        
        Y = 1
        
    if not Z:
        
        Z = 1
    
    # create a NU scale
    
    NUscale = rc.Geometry.Transform.Scale(P,X,Y,Z)
    
    #transform = rc.Geometry.Transform.Rotation(3.14, rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
    
    HBObject.transform(NUscale)
    
    HBObj = hb_hive.addToHoneybeeHive([HBObject], ghenv.Component)

    return HBObj
    
if _HBObj:
    result = main(_HBObj, P,X,Y,Z)
    
    if result!=-1:
        HBObj = result