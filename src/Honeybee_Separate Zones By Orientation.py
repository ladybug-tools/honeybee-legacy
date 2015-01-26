# By Mostapha Sadeghipour Roudsari
# sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separate zones based on orientation
-
Provided by Honeybee 0.0.55

    Args:
        _HBZones: List of HBZones
        onlyWGlz_: Only consider surfaces with glazing

    Returns:
        orientations: List of orientation vectors
        HBZones: Honeybee zones. Each branch represents a different orientation
"""


ghenv.Component.Name = 'Honeybee_Separate Zones By Orientation'
ghenv.Component.NickName = 'separateZonesByOrientation'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import uuid
import math
import Rhino as rc
import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def getOrientation(HBZone, onlyWGlz):
    
    orientationVectors = []
    for HBSrf in HBZone.surfaces:
        if HBSrf.type == 0 and HBSrf.BC.lower()=="outdoors":
            if onlyWGlz and HBSrf.hasChild:
                for glzSrf in HBSrf.childSrfs:
                    if not glzSrf.normalVector in orientationVectors:
                        orientationVectors.append(glzSrf.normalVector)
            else:
                if not HBSrf.normalVector in orientationVectors:
                        orientationVectors.append(HBSrf.normalVector)
        
    # sort based on angle to north
    orientationVectors = sorted(orientationVectors, key = lambda \
                         a: rc.Geometry.Vector3d.VectorAngle(a, rc.Geometry.Vector3d.YAxis, rc.Geometry.Plane.WorldXY))
    
    return orientationVectors


def main(HBZones, onlyWGlz):
    
    if not sc.sticky.has_key("honeybee_release"):
        print "You should first let the Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Honeybee fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    HBZones = {}
    
    for HBZone in HBZonesFromHive:
        
        orientationVectors = getOrientation(HBZone, onlyWGlz)
        
        # conver vector list to list of string so it could be used as key
        angles = []
        for vector in orientationVectors:
            angles.append(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, rc.Geometry.Vector3d.YAxis)))
            
        key = "".join(map(str, angles))
        
        if key not in HBZones.keys():
            HBZones[key] = [orientationVectors, []]
        
        HBZones[key][1].append(HBZone)
        
        
    return HBZones

if _HBZones and _HBZones!=None:
    
    orderedHBZones = main(_HBZones, onlyWGlz_)
    
    if orderedHBZones!= -1:
        keys = orderedHBZones.keys()
        keys.sort()
        
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        HBZones = DataTree[Object]()
        orientations = DataTree[Object]()
        
        for count, key in enumerate(keys):
            p = GH_Path(count)
            orientations.AddRange(orderedHBZones[key][0],p)
            
            zones = hb_hive.addToHoneybeeHive(orderedHBZones[key][1], ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
            HBZones.AddRange(zones, p)
