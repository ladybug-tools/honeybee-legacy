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
Use this component to break down the geometry of your zone by the surface type.  This is useful for previewing your zones in the rhino scene and making sure that each surface of your zones has the correct surface type.
-
Provided by Honeybee 0.0.64

    Args:
        _HBZone: Honeybee Zones for which you want to preview the different surface types.
    Returns:
        walls: A list of the exterior walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        interiorWalls: A list of the interior walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        airWalls: A list of the air walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        windows: A list of windows of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        interiorWindows: A list of interior windows of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        skylights: A list of skylights of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        roofs: A list of roofs of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        ceilings: A list of ceilings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        floors: A list of floors of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        exposedFloors: A list of floors exposed to the outside air as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        groundFloors: A list of ground floors of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundWalls: A list of underground walls of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundSlabs: A list of underground floor slabs of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        undergroundCeilings: A list of underground ceilings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
        shadings: A list of shadings of your zones as breps.  Connect to a Grasshopper "Preview" component to add color to the breps.
"""
ghenv.Component.Name = "Honeybee_Decompose Based On Type"
ghenv.Component.NickName = 'decomposeByType'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc



def main(HBZone):
    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
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
        
    walls = []
    interiorWalls = []
    windows = []
    interiorWindows = []
    skylights =[]
    roofs = []
    ceilings = []
    floors = []
    exposedFloors = []
    groundFloors = []
    undergroundWalls = []
    undergroundSlabs = []
    undergroundCeilings = []
    shadings = []
    airWalls = []

    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()

    zone = hb_hive.visualizeFromHoneybeeHive([HBZone])[0]

    for srf in zone.surfaces:
        # WALL
        if srf.type == 0:
            if srf.BC.upper() == "SURFACE" or srf.BC.upper() == "ADIABATIC":
                if srf.hasChild:
                    interiorWalls.append(srf.punchedGeometry)
                    for childSrf in srf.childSrfs:
                        interiorWindows.append(childSrf.geometry)
                else:
                    interiorWalls.append(srf.geometry)
                    
            else:
                if srf.hasChild:
                    walls.append(srf.punchedGeometry)
                    
                    for childSrf in srf.childSrfs:
                        windows.append(childSrf.geometry)
                else:
                    walls.append(srf.geometry)
                        
        # underground wall
        elif srf.type == 0.5:
            undergroundWalls.append(srf.geometry)
        
        # Roof
        elif srf.type == 1:
            if srf.hasChild:
                roofs.append(srf.punchedGeometry)
                for childSrf in srf.childSrfs:
                    skylights.append(childSrf.geometry)
            else:
                roofs.append(srf.geometry)
        
        # underground ceiling
        elif srf.type == 1.5:
            undergroundCeilings.append(srf.geometry)
            
        elif srf.type == 2: floors.append(srf.geometry)
        elif srf.type == 2.25: undergroundSlabs.append(srf.geometry)
        elif srf.type == 2.5: groundFloors.append(srf.geometry)
        elif srf.type == 2.75: exposedFloors.append(srf.geometry)
        elif srf.type == 3: ceilings.append(srf.geometry)
        elif srf.type == 4: airWalls.append(srf.geometry)
        elif srf.type == 6: shadings.append(srf.geometry)
        
        
    return walls, interiorWalls, airWalls, windows, interiorWindows, skylights, roofs, \
           ceilings, floors, exposedFloors, groundFloors, undergroundWalls, \
           undergroundSlabs, undergroundCeilings, shadings


#    # add to the hive
#    hb_hive = sc.sticky["honeybee_Hive"]()
#    HBSurface  = hb_hive.addToHoneybeeHive(HBSurfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))

if _HBZone!= None:
    HBSurfaces = main(_HBZone)
    
    if HBSurfaces != -1:
        walls = HBSurfaces[0]
        interiorWalls = HBSurfaces[1]
        airWalls = HBSurfaces[2]
        windows = HBSurfaces[3]
        interiorWindows = HBSurfaces[4]
        skylights = HBSurfaces[5]
        roofs = HBSurfaces[6]
        ceilings = HBSurfaces[7]
        floors = HBSurfaces[8]
        exposedFloors = HBSurfaces[9]
        groundFloors = HBSurfaces[10]
        undergroundWalls = HBSurfaces[11]
        undergroundSlabs = HBSurfaces[12]
        undergroundCeilings = HBSurfaces[13]
        shadings = HBSurfaces[14]