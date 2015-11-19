# ACH 2 m3/s-m2
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Abraham Yezioro <ayez@ar.technion.ac.il> 
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
Use this component to transform ACH to m3/s-m2.
Plug the result to the Honeybee setEPZoneLoads component, infiltrationRatePerArea_ or  infiltrationRatePerArea_ inputs

-
Provided by Honeybee 0.0.58
    
    Args:
        _HBZones: Honeybee zones for which you want to calculate the infiltration or ventilation rates.
        _airChangeHour: Air Changes per Hour. 
    Returns:
        readMe!: Report of the calculations
        infORventPerArea: infiltrationRatePerArea or ventilationPerArea in m3/s-m2 (Cubic meters per second per square meter of floor)
"""
ghenv.Component.Name = "Honeybee infORventPerArea Calculator"
ghenv.Component.NickName = 'ACH2m3/s-m2 Calculator'
ghenv.Component.Message = 'VER 0.0.58\nNOV_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import math
import scriptcontext as sc
import Rhino as rc
import rhinoscriptsyntax as rs
import System
from System import Object
from System import Drawing
from clr import AddReference as addr
addr("Grasshopper")

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
###################################
import Rhino.Geometry as rg
w = gh.GH_RuntimeMessageLevel.Warning

tol = sc.doc.ModelAbsoluteTolerance

def checkInputs():
    checkData1 = False # Check _airChangeHour
    if _airChangeHour:
        try:
            if _airChangeHour >= 0.2:
                checkData1 = True
            else: pass
        except: pass
    else:
        print 'Give a positive value for airChangeHour'
    
    if checkData1 == True:
        checkData = True
    else:
        checkData = False
        msg = "At least one of the inputs is incorrect. Fix it according to the hints of each of them."
    
    
    return checkData

def main(HBZones, airChangeHour):
    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
            return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    allFloors  = []
    flrAreas   = []
    flrVolumes = []
    infORventPerArea = []
    
    # call the objects from the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    zones = hb_hive.callFromHoneybeeHive(HBZones)
    
    for count, HZone in enumerate(zones):
        flrArea = HZone.getFloorArea()
        flrVolume = HZone.getZoneVolume()
        #print HZone
        
        option2Volume = rc.Geometry.VolumeMassProperties.Compute(HBZones[count]).Volume
        #print option2Volume
        #data = rc.Geometry.VolumeMassProperties.Compute(srf.geometry)
        
        flrVolumes.append(flrVolume)
        flrAreas.append(flrArea)
        
        #Calculate infiltration/ventilation per area (m3/s-m2).
        try:
            infORventPerArea.append((airChangeHour * flrVolumes[count] / 3600) / flrAreas[count])
        except:
            warning = "One of the HBZones did not have any floor area.  The oringal air change values will be kept."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            infORventPerArea.append(HZone.ventilationPerArea)
        infORventPerAreaRes = 'infiltration/ventilationPerArea %.6f m3/second-m2' % (infORventPerArea[count])
    
        #print 'Area= , Volume= ', flrAreas[count], flrVolumes[count], infORventPerAreaRes
        print 'Area= %.2f Volume= %.2f %s' % (flrAreas[count], flrVolumes[count], infORventPerAreaRes)
    
    
    # OPTION 2
    for HZone in zones:
        for srf in HZone.surfaces:
            #srf.type == 2 (floors), == 2.5 (groundFloors), == 2.75 (exposedFloors)
            if int(srf.type) == 2:
                option2FlrArea = rc.Geometry.AreaMassProperties.Compute(srf.geometry).Area
                #print option2FlrArea
    #            data = rc.Geometry.AreaMassProperties.Compute(srf.geometry) 
    #            flrAreas.append(data.Area)
    #            
                allFloors.append(srf.geometry)
    
    return infORventPerArea, allFloors

#Check the inputs.
checkData = False
checkData = checkInputs()

#if _HBZones!= None:
#if _HBZones != None and checkData == True:
    #infORventPerArea, allFloors = main(_HBZones, _airChangeHour)
if _HBZones != [] and checkData == True:
    result = main(_HBZones, _airChangeHour)
    if result != -1:
        infORventPerArea, allFloors = result
