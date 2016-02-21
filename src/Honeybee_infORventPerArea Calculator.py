# ACH 2 m3/s-m2
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Abraham Yezioro <ayez@ar.technion.ac.il> 
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
Provided by Honeybee 0.0.59
    
    Args:
        _HBZones: Honeybee zones for which you want to calculate the infiltration or ventilation rates.
        _airChangeHour: Air Changes per Hour. Given at ambien pressure. Give a value of 0.2 or higher.
        _at50PA_: Boolean. Set to true if you want to get a value at 50 Pascal. You probably want this for PassiveHouse calculations. Default is False as for ambient calculation.
    Returns:
        readMe!: Report of the calculations
        infORventPerArea: infiltrationRatePerArea or ventilationPerArea in m3/s-m2 (Cubic meters per second per square meter of floor)
"""
ghenv.Component.Name = "Honeybee_infORventPerArea Calculator"
ghenv.Component.NickName = 'ACH2m3/s-m2 Calculator'
ghenv.Component.Message = 'VER 0.0.59\nFEB_21_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
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
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
###################################
import Rhino.Geometry as rg
w = gh.GH_RuntimeMessageLevel.Warning

tol = sc.doc.ModelAbsoluteTolerance

def checkInputs():
    checkData1 = False # Check _airChangeHour
    checkData2 = False # Check _HBZones
    at50PA = 1
    if _airChangeHour:
        try:
            #if _airChangeHour >= 0.0001:
            if _airChangeHour >= 0.2:
                checkData1 = True
            else: pass
        except: pass
    else:
        print 'Give a value for airChangeHour bigger than 0.2'
    
    if _HBZones and _HBZones[0]!=None:
        checkData2 = True

    if checkData1 == True and checkData2 == True:
        checkData = True
        if _at50PA_ == True:
            at50PA = 20
        else:
            at50PA = 1
    else:
        checkData = False
        msg = "At least one of the inputs is incorrect. Fix it according to the hints of each of them."
        ghenv.Component.AddRuntimeMessage(w, msg)
    
    return checkData, at50PA

def main(HBZones, airChangeHour):
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
        
    allFloors  = []
    flrAreas   = []
    flrVolumes = []
    infORventPerArea = []
    
    # call the objects from the hive
    hb_hive = sc.sticky["honeybee_Hive"]()
    zones = hb_hive.visualizeFromHoneybeeHive(HBZones)
    
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
            infORventPerArea.append(((airChangeHour / at50PA) * flrVolumes[count] / 3600) / flrAreas[count])
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
checkData, at50PA = checkInputs()

#if _HBZones!= None:
#if _HBZones != None and checkData == True:
    #infORventPerArea, allFloors = main(_HBZones, _airChangeHour)
if _HBZones != [] and checkData == True:
    result = main(_HBZones, _airChangeHour)
    if result != -1:
        infORventPerArea, allFloors = result
