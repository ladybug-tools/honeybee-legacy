#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, "Write your names here..." <"Write your email address here> 
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
Export to Energy Performace Calculator (EPC)
... Add more description here

-
Provided by Honeybee 0.0.64

    Args:
        _HBZones: Honeybee Zones
    Returns:
        opaqueSrfsArea: Area of the surfaces for each direction
        glazedSrfsArea: Area of the glazing surfaces for each direction
        
"""
ghenv.Component.Name = "Honeybee_ExportEPC"
ghenv.Component.NickName = 'Export to EPC'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Grasshopper.Kernel as gh


def main(HBZones):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first Honeybee to fly...")
        return
    
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
        return
        
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # Call Honeybee zones from the lib
    HBZones = hb_hive.callFromHoneybeeHive(HBZones)
    
    # create an empty dictionary
    # the structure should be as {type : {construction: { orientation : {area of opaque : area , area of glass : area}}}
    srfData = {}
    
    # produce division angles - keep it to 8 directions for now 
    divisionAngles = rs.frange(0- (360/8), 360 -(360/8), 360/8)
    
    # iterate through faces and add them to the dictionary
    for HBZone in HBZones:
        for srfCount, HBSrf in enumerate(HBZone.surfaces):
            # let's add it to the dictionary
            # I need to know what is the type of the surface (wall, roof, ?)
            # HBSrf.type will return the type. I'm not sure how much detailed you want the type to be
            # what is the approach for surfcaes with adjacencies? Here are simple types
            # srf.type == 0 #wall, # srf.type == 1 #roof, # int(srf.type) == 2 #floor
            # print "type: ", HBSrf.type
            srfType = int(HBSrf.type)
            
            # I add the key to the dictionary if it is not there yet
            if not srfData.has_key(srfType): srfData[srfType] = {}
            
            # let's find the construction next as your workflow is based on different construction types
            # you can get it form a Honeybee surface using HBSrf.EPConstruction
            # print "EP construction: ", HBSrf.EPConstruction
            constr = HBSrf.EPConstruction
            
            if not srfData[srfType].has_key(constr):
                # create a place holder for this construction and put the initial area as 0
                srfData[srfType][constr] = {}
            
            # now let's find the direction of the surface
            # in case of roof or floor orientation doesn't really matter (or does it?)
            # so I just add it to dictionary and consider orientation as 0
            if  srfType!=0:
                direction = 0
            else:
                # otherwise we need to find the direction of the surface
                # you can use HBSrf.angle2North to get it
                # print "angle: ", HBSrf.angle2North
                # check and see where it stands, 0 will be north, 1 is NE, etc. 
                for direction in range(len(divisionAngles)-1):
                    if divisionAngles[direction]+(0.5*sc.doc.ModelAngleToleranceDegrees) <= HBSrf.angle2North%360 <= divisionAngles[direction +1]+(0.5*sc.doc.ModelAngleToleranceDegrees):
                        # here we found the direction
                        break            
            # Now that we know direction let's make an empty dictionary for that
            if not srfData[srfType][constr].has_key(direction):
                srfData[srfType][constr][direction] = {}
                srfData[srfType][constr][direction]["area"] = 0
                # in case surface has glazing then create a place holder with
                # type 5 reperesnts glazing
                if HBSrf.hasChild:
                    if not srfData.has_key(5):
                        srfData[5] = {}
                    # this is tricky here as I assume that all the glazing in the same wall
                    # has same construction and I pick the first one - we can change this later if needed
                    glzConstr = HBSrf.childSrfs[0].EPConstruction
                    if not srfData[5].has_key(glzConstr):
                        srfData[5][glzConstr] = {}
                    if not srfData[5][glzConstr].has_key(direction):
                        srfData[5][glzConstr][direction] = {}
                        srfData[5][glzConstr][direction]["area"] = 0
            
            # add the area to the current area
            # Honeybee has methods that return area for opaque and glazed area
            #print "Opaque area: ", HBSrf.getOpaqueArea()
            #print "Glazing area: ", HBSrf.getGlazingArea()
            srfData[srfType][constr][direction]["area"] += HBSrf.getOpaqueArea()
            if HBSrf.hasChild:
                srfData[5][HBSrf.childSrfs[0].EPConstruction][direction]["area"] += HBSrf.getGlazingArea()
    # return surface data
    return srfData
    # done!


srfTypeDict = {0: "Wall", 1 : "Roof", 2: "Floor", 5 : "Glazing"}
directionDict = {0: "N", 1 : "NW", 2: "W", 3: "SW", 4 : "S", 5 : "SE", 6 : "E", 7 : "NE"}
print
if len(_HBZones)!=0 and _HBZones[0]!=0:
    srfData = main(_HBZones)
    if srfData != -1:
        # now that you have the dictionary you can iterate and produce the lists that you wanted
        # you only need to remember the structure of dictionary - you can modify the structure to
        # be easier to iterate but I thought the current structure is easier to read
        
        for srfType in srfData.keys():
            for constr in srfData[srfType].keys():
                for orientation in range(8):
                    # if direction is not there it means the area is 0
                    if not srfData[srfType][constr].has_key(orientation):
                        continue
                        print " surfaces " + \
                              constr + "; facing " + \
                              directionDict[orientation] + ","+ " 0 "
                    else:
                        if srfType == 1 or srfType == 2:
                            print constr + ","+  \
                              str(srfData[srfType][constr][orientation]["area"])
                        else:
                            print constr + \
                              directionDict[orientation] + ","+ \
                              str(srfData[srfType][constr][orientation]["area"])

