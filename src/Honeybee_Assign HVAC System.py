#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> , Chris Mackey <Chris@MackeyArchitecture.com>, and Chien Si Harriman <charriman@terabuild.com>
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
Use this component to assign OpenStudio Systems to your HBZones.  By default, all HBZones are assigned an Ideal Air Loads system and this component can be used to change this to a real system from the OpenStudioHVACSystemsList component.
This component is also used to adjust the features of the HVAC system using the _airDetails_, _heatingDetails_, and _coolingDetails_.  Without the inputs to these Details, template OpenStudio systems will be used.
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: The HBZones for which you want to change/adjust the HVAC system.
        _HVACSystems: A HVAC system template from the "Honeybee_HVACSystemsList" component.  ASHRAE recommends using the following baseline systems for different building types and fuel sources:
            BUILDING TYPE               FOSSIL FUEL/HYBRID/PURCHASED HEAT           ELECTRIC ONLY
            Residential                        1: PTAC | Residential                                                  2: PTHP | Residential
            Non-Res 3 Floors             3: Packaged Single Zone - AC                                   4: Packaged Single Zone - HP
            Non-Res 4-5 Floors          5: Packaged VAV w/ Reheat                                       6: Packaged VAV w/ PFP Boxes
            Non-Res >5 Floors           7: VAV w/ Reheat                                                        8: VAV w/ PFP Boxes
            Heated Only Sotrage         9: Warm Air Furnace - Gas Fired                              10: Warm Air Furnace - Electric
        _airDetails_: Parameters from the "Honeybee_HVAC Air Details" component. Use these to define the features of the ventilation component (or air side) of the HVAC system.
        _heatingDetails_: Parameters from the "Honeybee_HVAC Heating Details" component.  Use these to define the features of the heating plant (or hot water side) of the HVAC system.
        _coolingDetails_: Parameters from the "Honeybee_HVAC Cooling Details" component.  Use these to define the features of the cooling plant (or chilled water side) of the HVAC system.
    Returns:
        HBZones: HBZones that have been modified to have the assigned _HVACSystems.
"""

ghenv.Component.Name = "Honeybee_Assign HVAC System"
ghenv.Component.NickName = 'HVACSystem'
ghenv.Component.Message = 'VER 0.0.60\nNOV_18_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | HVACSystems"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import uuid

w = gh.GH_RuntimeMessageLevel.Warning


def main(HBZones, HVACIndex, hb_hvacProperties, hb_airDetail, hb_heatingDetail, hb_coolingDetail):
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    EPHvac = sc.sticky["honeybee_EPHvac"]
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    #create a single HVAC Group ID to create a unique reference to the HVAC details imported (or none if none)
    HVACGroupID = ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4())
    
    for zoneCount, zone in enumerate(HBZonesFromHive):
        
        if not zone.isConditioned:
            warning = "%s is not conditioned. Systems will not be added to this zone."%zone.name
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            continue
        elif HVACIndex < -1 or HVACIndex > len(hb_hvacProperties.sysDict.keys())-2:
            warning = "HVAC system " + str(HVACIndex) + " has not been implemented."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            continue
        
        # Assign default details.
        aDetail = None
        hDetail = None
        cDetail = None
        
        if HVACIndex != -1:
            #Check to be sure that the user has not assigned capabilties that the HVAC system does not support.
            hvacCapabil = hb_hvacProperties.thresholdCapabilities[HVACIndex]
            if hvacCapabil['recirc'] == False and zone.recirculatedAirPerArea != 0:
                warning = "HVAC system " + hb_hvacProperties.sysDict[HVACIndex] + " does not support \n" + \
                "AIR RECIRCULATION but recirculation has been assigned to the HBZones."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            if hvacCapabil['dehumidCntrl'] == False:
                if zone.humidityMax != '':
                    warning = "HVAC system " + hb_hvacProperties.sysDict[HVACIndex] + " does not support \n" + \
                    "DEHUMIDIFICATION but a maximum humidity threshold has been assigned to the HBZones."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            if hvacCapabil['humidCntrl'] == False:
                if zone.humidityMin != '':
                    warning = "HVAC system " + hb_hvacProperties.sysDict[HVACIndex] + " does not support \n" + \
                    "HUMIDIFICATION but a minimum humidity threshold has been assigned to the HBZones."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            if hvacCapabil['ventSched'] == False:
                if zone.ventilationSched != '':
                    warning = "HVAC system " + hb_hvacProperties.sysDict[HVACIndex] + " does not support \n" + \
                    "VENTILATION SCHEDULES but a ventilation schedule has been assigned to the HBZones."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            # Check for any HVAC airside details.
            try:
                if _airDetails_:
                    airDetailObj = hb_airDetail.fromTextStr(_airDetails_)
                    if airDetailObj != None:
                        capabilErrors = hb_airDetail.checkSysCompatability(airDetailObj, HVACIndex)
                        for error in capabilErrors:
                            print error
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, error)
                        aDetail = airDetailObj
                    else:
                        warning = '_airDetials_ are not valid.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                warning = '_airDetials_ are not valid.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            # Check for any heating details.
            try:
                if _heatingDetails_:
                    heatDetailObj = hb_heatingDetail.fromTextStr(_heatingDetails_)
                    if heatDetailObj != None:
                        capabilErrors = hb_heatingDetail.checkSysCompatability(heatDetailObj, HVACIndex)
                        
                        for error in capabilErrors:
                            print error
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, error)
                        hDetail = heatDetailObj
                    else:
                        warning = '_heatingDetials_ are not valid.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                warning = '_heatingDetials_ are not valid.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            # Check for any cooling details.
            try:
                if _coolingDetails_:
                    coolDetailObj = hb_coolingDetail.fromTextStr(_coolingDetails_)
                    if coolDetailObj != None:
                        capabilErrors = hb_coolingDetail.checkSysCompatability(coolDetailObj, HVACIndex)
                        
                        for error in capabilErrors:
                            print error
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, error)
                        cDetail = coolDetailObj
                    else:
                        warning = '_coolingDetials_ are not valid.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                warning = '_coolingDetials_ are not valid.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        #Assign the HVAC System to the zone.
        zone.HVACSystem = EPHvac(HVACGroupID, HVACIndex, aDetail, hDetail, cDetail)
        
        HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component)
    
    return HBZones


#Honeybee check.
initCheck = True
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
        hb_hvacProperties = sc.sticky['honeybee_hvacProperties']()
        hb_airDetail = sc.sticky["honeybee_hvacAirDetails"]
        hb_heatingDetail = sc.sticky["honeybee_hvacHeatingDetails"]
        hb_coolingDetail = sc.sticky["honeybee_hvacCoolingDetails"]
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck and len(_HBZones) > 0 and _HVACSystems != None and _HBZones[0] != None:
    HBZones = main(_HBZones, _HVACSystems, hb_hvacProperties, hb_airDetail, hb_heatingDetail, hb_coolingDetail)
