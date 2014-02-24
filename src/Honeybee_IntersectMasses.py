# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Intersect masses
-
Provided by Honeybee 0.0.51

    Args:
        bldgMassesBefore: ...
    Returns:
        bldgMassesAfter: ...
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.51\nFEB_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import scriptcontext as sc

def main(bldgMassesBefore):
    
    buildingDict = {}
    intersectedBldgs = []
    for bldgCount, bldg in enumerate(bldgMassesBefore):
        buildingDict[bldgCount] = bldg
    
    for bldgNum, building in buildingDict.items():
        for otherBldg in  bldgMassesBefore[:bldgNum]:
            intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
            if intersectedBuilding:
                building = intersectedBuilding[0]
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
                
        for otherBldg in  bldgMassesBefore[bldgNum+1:]:
            intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
            if intersectedBuilding:
                building = intersectedBuilding[0]
                buildingDict[bldgNum] = building
                bldgMassesBefore[bldgNum] = building
    
    for bldgNum, building in buildingDict.items():
        intersectedBldgs.append(building)
    
    if len(bldgMassesBefore) == len(intersectedBldgs):
        intersectedBldgs = bldgMassesBefore
    
    return intersectedBldgs
            
if _bldgMassesBefore and _bldgMassesBefore[0]!=None:
    bldgMassesAfter = main(_bldgMassesBefore)

