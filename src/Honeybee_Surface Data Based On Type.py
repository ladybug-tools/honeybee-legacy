# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to separate grafed lists of surface data that come out of the "Honeybee_Read EP Surface Result" component based on rough surface type.
-
Provided by Honeybee 0.0.53

    Args:
        _srfData: Any surface data out of the "Honeybee_Read EP Surface Result" component.
    Returns:
        exteriorWalls = A grafted list of surface data for exterior walls.
        interiorWalls = A grafted list of surface data for interior walls.
        exteriorWindows = A grafted list of surface data for exterior windows.
        interiorWindows = A grafted list of surface data for interior windows.
        ceilings = A grafted list of surface data for to ceilings.
        roofs = A grafted list of surface data for to roofs.
        floors = A grafted list of surface data for to floors.
        exposedFloors = A grafted list of surface data for to exposed floors.
"""
ghenv.Component.Name = "Honeybee_Surface Data Based On Type"
ghenv.Component.NickName = 'srfDataByType'
ghenv.Component.Message = 'VER 0.0.53\nAUG_09_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc


exteriorWalls = DataTree[Object]()
interiorWalls = DataTree[Object]()
exteriorWindows = DataTree[Object]()
interiorWindows = DataTree[Object]()
ceilings = DataTree[Object]()
roofs = DataTree[Object]()
floors = DataTree[Object]()
exposedFloors = DataTree[Object]()


def checkBranch():
    checkList = []
    checkData = False
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        try:
            branchList[2].split(": ")
            checkList.append(1)
        except:pass
    if len(checkList) == _srfData.BranchCount:
        checkData = True
    else:
        warning = 'Connected data does not contain a vaild surface data header.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    return checkData


def main(srfData):
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        branchPath = _srfData.Path(i)
        
        srfType = branchList[2].split(": ")[-1]
        
        if srfType == "EXTERIOR WALL":
            for item in branchList: exteriorWalls.Add(item, branchPath)
        elif srfType == "INTERIOR WALL":
            for item in branchList: interiorWalls.Add(item, branchPath)
        elif srfType == "EXTERIOR WINDOW":
            for item in branchList: exteriorWindows.Add(item, branchPath)
        elif srfType == "INTERIOR WINDOW":
            for item in branchList: interiorWindows.Add(item, branchPath)
        elif srfType == "INTERIOR CEILING":
            for item in branchList: ceilings.Add(item, branchPath)
        elif srfType == "EXTERIOR ROOF":
            for item in branchList: roofs.Add(item, branchPath)
        elif srfType == "INTERIOR FLOOR":
            for item in branchList: floors.Add(item, branchPath)
        elif srfType == "EXTERIOS FLOOR":
            for item in branchList: explosedFloors.Add(item, branchPath)
        else: pass


checkData = False
if _srfData.BranchCount > 0 and str(_srfData) != "tree {0}":
    checkData = checkBranch()

if checkData == True: main(_srfData)