#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to separate grafed lists of surface data that come out of the "Honeybee_Read EP Surface Result" component based on rough surface type.  This component separates all surface types but takes sevaral seconds to load and requires HBZones.  For a quicker splitting of data, use the "Honeybee_Surface Data Based On Type" component.
-
Provided by Honeybee 0.0.64

    Args:
        _HBZone: Honeybee Zones for which you are interested in surface data.
    Returns:
        walls: A grafted list of surface data for walls.
        interiorWalls: A grafted list of surface data for interior walls.
        airWalls: A grafted list of surface data for air walls.
        windows: A grafted list of surface data for exterior windows.
        interiorWindows: A grafted list of surface data for interior windows.
        skylights: A grafted list of surface data for skylights.
        roofs: A grafted list of surface data for roofs.
        ceilings: A grafted list of surface data for ceilings.
        floors: A grafted list of surface data for floors.
        exposedFloors: A grafted list of surface data for exposed floors.
        groundFloors: A grafted list of surface data for ground floors.
        undergroundWalls: A grafted list of surface data for underground walls.
        undergroundCeilings: A grafted list of surface data for underground ceilings.
"""
ghenv.Component.Name = "Honeybee_Surface Data Based On Type Detailed"
ghenv.Component.NickName = 'srfDataByTypeDetailed'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc


walls = DataTree[Object]()
interiorWalls = DataTree[Object]()
airWalls = DataTree[Object]()
windows = DataTree[Object]()
interiorWindows = DataTree[Object]()
skylights = DataTree[Object]()
roofs = DataTree[Object]()
ceilings = DataTree[Object]()
floors = DataTree[Object]()
exposedFloors = DataTree[Object]()
groundFloors = DataTree[Object]()
undergroundWalls = DataTree[Object]()
undergroundCeilings = DataTree[Object]()


def checkBranch():
    checkList = []
    checkData = False
    for i in range(_srfData.BranchCount):
        branchList = _srfData.Branch(i)
        try:
            branchList[2].split(" for ")
            checkList.append(1)
        except:pass
    if len(checkList) == _srfData.BranchCount:
        checkData = True
    else:
        warning = 'Connected data does not contain a vaild surface data header.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    return checkData

def getSrfNames(HBZones):
    wall = []
    interiorWall = []
    airWall = []
    window = []
    interiorWindow = []
    skylight =[]
    roof = []
    ceiling = []
    floor = []
    exposedFloor = []
    groundFloor = []
    undergroundWall = []
    undergroundCeiling = []
    
    for zone in HBZones:
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        zone = hb_hive.callFromHoneybeeHive([zone])[0]
        
        for srf in zone.surfaces:
            # WALL
            if srf.type == 0:
                if srf.BC.upper() == "SURFACE" or srf.BC.upper() == "ADIABATIC":
                    if srf.hasChild:
                        interiorWall.append(srf.name)
                        for childSrf in srf.childSrfs:
                            interiorWindow.append(childSrf.name)
                    else:
                        interiorWall.append(srf.name)
                        
                else:
                    if srf.hasChild:
                        wall.append(srf.name)
                        
                        for childSrf in srf.childSrfs:
                            window.append(childSrf.name)
                    else:
                        wall.append(srf.name)
                            
            # underground wall
            elif srf.type == 0.5:
                undergroundWall.append(srf.name)
            
            # Roof
            elif srf.type == 1:
                if srf.hasChild:
                    roof.append(srf.name)
                    for childSrf in srf.childSrfs:
                        skylight.append(childSrf.name)
                else:
                    roof.append(srf.name)
            
            # underground ceiling
            elif srf.type == 1.5:
                undergroundCeiling.append(srf.name)
                
            elif srf.type == 2: floor.append(srf.name)
            elif srf.type == 2.5: groundFloor.append(srf.name)
            elif srf.type == 2.75: exposedFloor.append(srf.name)
            elif srf.type == 3: ceiling.append(srf.name)
            elif srf.type == 4: airWall.append(srf.name)
        
        
    return wall, interiorWall, airWall, window, interiorWindow, skylight, roof, \
           ceiling, floor, exposedFloor, groundFloor, undergroundWall, \
           undergroundCeiling


def main(HBZones, srfData):
    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        return
        
    #Get the surface names from the HBZones.
    wall, interiorWall, airWall, window, interiorWindow, skylight, roof, ceiling, floor, exposedFloor, groundFloor, undergroundWall, undergroundCeiling = getSrfNames(HBZones)
    
    #Write a function to check if a name is in the list.
    def checkList(theList, dataTree, name, branchList, branchPath):
        itemFound = False
        for srf in theList:
            if srf.upper() == name:
                for item in branchList: dataTree.Add(item, branchPath)
                itemFound = True
            else: pass
        return itemFound
    
    #Go through each item in the data list and see what surface type it is a part of.
    for i in range(srfData.BranchCount):
        branchList = srfData.Branch(i)
        branchPath = srfData.Path(i)
        
        try:srfName = branchList[2].split(" for ")[-1].split(": ")[0]
        except:srfName = branchList[2].split(" for ")[-1]
        
        itemFound = checkList(wall, walls, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(interiorWall, interiorWalls, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(airWall, airWalls, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(window, windows, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(interiorWindow, interiorWindows, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(skylight, skylights, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(roof, roofs, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(ceiling, ceilings, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(floor, floors, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(exposedFloor, exposedFloors, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(groundFloor, groundFloors, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(undergroundWall, undergroundWalls, srfName, branchList, branchPath)
        if itemFound == False: itemFound = checkList(undergroundCeiling, undergroundCeilings, srfName, branchList, branchPath)
    
    
    return True

checkData = False
if _HBZones != [] and _srfData.BranchCount > 0 and str(_srfData) != "tree {0}":
    checkData = checkBranch()
if checkData == True: runSuccess = main(_HBZones, _srfData)