# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Intersect masses
-
Provided by Honeybee 0.0.55

    Args:
        bldgMassesBefore: ...
    Returns:
        bldgMassesAfter: ...
"""
ghenv.Component.Name = "Honeybee_IntersectMasses"
ghenv.Component.NickName = 'IntersectMass'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
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
        try:
            for otherBldg in  bldgMassesBefore[:bldgNum]:
                intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
                if intersectedBuilding:
                    building = intersectedBuilding[0]
                    if building.IsValid:
                        buildingDict[bldgNum] = building
                        bldgMassesBefore[bldgNum] = building
                    else:
                        pass
            for otherBldg in  bldgMassesBefore[bldgNum+1:]:
                intersectedBuilding = rc.Geometry.Brep.CreateBooleanDifference(building, otherBldg, sc.doc.ModelAbsoluteTolerance)
                if intersectedBuilding:
                    building = intersectedBuilding[0]
                    if building.IsValid:
                        buildingDict[bldgNum] = building
                        bldgMassesBefore[bldgNum] = building
                    else:
                        pass
        except:
            buildingDict[bldgNum] = building
            bldgMassesBefore[bldgNum] = building
            
    for bldgNum, building in buildingDict.items():
        intersectedBldgs.append(building)
    
    if len(bldgMassesBefore) == len(intersectedBldgs):
        intersectedBldgs = bldgMassesBefore
    
    return intersectedBldgs
            
if _bldgMassesBefore and _bldgMassesBefore[0]!=None:
    bldgMassesAfter = main(_bldgMassesBefore)

