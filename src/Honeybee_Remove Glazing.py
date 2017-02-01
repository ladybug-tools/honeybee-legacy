#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> and Anton Szilasi <ajszilasi@gmail.com>
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
Remove Glazing 

-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: A list of Honeybee Zones, this component can only use Honeybee Zones
        srfIndex_: Currently not functional do not connect anything here...
        pattern_: Currently not functional do not connect anything here...
        windowName_: The names of windows to remove, you can get the names of windows from the surfaceTxtLabels output of the component Honeybee_Label Zone Surfaces.

    Returns:
        readMe!: Information about the Honeybee object

    # Pattern to remove glazings from surfaces. E.g a list of True,False will remove every second glazing assuming every surface in each Honeybee zone has a glazing.
        
"""
ghenv.Component.Name = "Honeybee_Remove Glazing"
ghenv.Component.NickName = 'remGlz'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid
import itertools

def main(HBObjects, srfIndex, pattern):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee fly..."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
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
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBObjects)
    
    HBObjs = range(len(HBObjectsFromHive))
    
    for count, HBO in enumerate(HBObjectsFromHive):
        if HBO.objectType == "HBZone":
            
            # For removing windows by Surface Index or Window Name
            for srfCount, surface in enumerate(HBO.surfaces):
                
                if windowName_ != []:
                    
                    # Remove childSrfs (Windows) which names are equal to windowName_
                
                    # Filter - Construct a list from those elements of iterable for which function returns True
                    # so we need the not!
                    
                    surface.childSrfs = list(filter(lambda window: window.name not in windowName_,surface.childSrfs))
                    
                    # Recalculate/Redraw surface geometry after windows have been removed
                    
                    surface.calculatePunchedSurface()
                
            """
                elif srfCount in srfIndex and surface.hasChild:
                    
                    #remove the glzing
                    surface.removeAllChildSrfs()
            
            def removeByPattern(surfaces):
                
                #Removes surfaces by pattern
                
                repeatPatternCount = 0
                # For removing windows by pattern
                for srfCount,surface in enumerate(HBO.surfaces):
                    
                    try:
                        
                        pattern[srfCount]
                        
                    except IndexError:
                        # SurfaceCount (The number of surfaces is greater than True or False pattern) has exceeded the number of items in the True or False pattern
                        # So repeat the True and False until all surfaces have been exhausted
                        # Do this by starting a new count. 
                        
                        if repeatPatternCount > len(pattern):
                            
                            #Reset repeatPatternCount so start the pattern again.
                            
                            repeatPatternCount = 0
                            
                            if pattern[repeatPatternCount] == True and surface.hasChild:
                                
                                surface.removeAllChildSrfs()
                            
                            repeatPatternCount = repeatPatternCount+1
                            
                        else:
                            
                            if pattern[repeatPatternCount] == True and surface.hasChild:
                                
                                surface.removeAllChildSrfs()
                            
            removeByPattern(HBO.surfaces)

            """
        else:
            
            w = gh.GH_RuntimeMessageLevel.Warning
            warning = "The "+str(HBO.objectType) + "named " + str(HBO.name) + " is not a Honeybee zone so no windows can be removed from it!"

            ghenv.Component.AddRuntimeMessage(w, warning)
        
        
        # Reassign HBO objects after they have had their surfaces removed.
        HBObjs[count] = HBO
    
    return hb_hive.addToHoneybeeHive(HBObjs, ghenv.Component)

HBZones = main(_HBZones, srfIndex_, pattern_)


if _HBZones !=[]:
    
    # Run the component
    HBZones = main(_HBZones, srfIndex_, pattern_)

if windowName_==[]:
    
    w = gh.GH_RuntimeMessageLevel.Warning
    warning = "No windows were removed as there are no inputs in windowName_ "+"\n"+\
    "the Honeybee zones have not been modified."

    ghenv.Component.AddRuntimeMessage(w, warning)
