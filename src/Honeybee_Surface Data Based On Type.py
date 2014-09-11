# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to separate grafed lists of surface data that come out of the "Honeybee_Read EP Surface Result" component based on rough surface type.
-
Provided by Honeybee 0.0.55

    Args:
        _srfData: Any surface data out of the "Honeybee_Read EP Surface Result" component.
    Returns:
        walls = A grafted list of surface data for walls.
        windows = A grafted list of surface data for windows.
        roofs = A grafted list of surface data for to roofs.
        floors = A grafted list of surface data for to floors.
"""
ghenv.Component.Name = "Honeybee_Surface Data Based On Type"
ghenv.Component.NickName = 'srfDataByType'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc


walls = DataTree[Object]()
windows = DataTree[Object]()
roofs = DataTree[Object]()
floors = DataTree[Object]()


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
        
        if srfType == "Wall":
            for item in branchList: walls.Add(item, branchPath)
        elif srfType == "Window":
            for item in branchList: windows.Add(item, branchPath)
        elif srfType == "Roof":
            for item in branchList: roofs.Add(item, branchPath)
        elif srfType == "Floor":
            for item in branchList: floors.Add(item, branchPath)
        else: pass


checkData = False
if _srfData.BranchCount > 0 and str(_srfData) != "tree {0}":
    checkData = checkBranch()

if checkData == True: main(_srfData)