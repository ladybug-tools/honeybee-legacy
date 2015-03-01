# By Chris MAckey
# Chris@MackeyArchitecture.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to change aspects of the ideal air system used in the "Honeybee_Run Energy Simulation" component.  The includes the temperature of the heating/cooling supply air, the maximum capacity of the system, demand controlled ventilation, air-side economizers, and heat recovery.
-
Provided by Honeybee 0.0.56

    Args:
        _HBZones: HBZones for which parameters of the ideal air system should be changed.
        outdoorAirReq_: By default, honeybee zones do not have a required fraction of outdoor air that must come through the mechanical system.  You can change this by inputting one of the following options:
            0 - None - No outdoor air will come through the mechanical system and the heating/cooling will be applied only through re-circulation of indoor air.  This is the default.
            1 - Maximum - The outdoor air coming through the mechnical system will be either the specified flow/m2 of zone floor area or the flow/person (depending on which is larger at a given hour).  Be warned that this can give misleading results when used with an ideal air system since this system does not differentiate between heating/cooling from outdoor air and that from a cooling/heating coil.
            2 - Sum - The outdoor air coming through the mechnical system will be the sum of the specified flow/m2 of zone floor area and the flow/person.  Be warned that this can give misleading results when used with an ideal air system since this system does not differentiate between heating/cooling from outdoor air and that from a cooling/heating coil.
        coolSuplyAirTemp_: A number or list of numbers that represent the temperature of the air used to cool the zone in degrees Celcius.  If no value is input here, the system will use air at 13 C.  This input can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        heatSupplyAirTemp_: A number or list of numbers that represent the temperature of the air used to heat the zone in degrees Celcius.  If no value is input here, the system will use air at 50 C.  This input can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxCoolingCapacity_:  A number or list of numbers that represent the maximum cooling power that the system can deliver in kiloWatts.  If no value is input here, the system will have no limit to its cooling capacity.  This input can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        maxHeatingCapacity_:  A number or list of numbers that represent the maximum heating power that the system can deliver in kiloWatts.  If no value is input here, the system will have no limit to its heating capacity.  This input can be either a single number to be applied to all connected zones or a list of numbers for each different zone.
        airSideEconomizer_: Set to "True" to have the ideal air system include an air side economizer.  This essentially means that the HVAC system will increase the outdoor air flow rate when there is a cooling load and the outdoor air temperature is below the temperature of the exhaust air.  If this input is set to "False" or left untouched, the HVAC system will constantly provide the same amount of outdoor air and will run the compressor to remove heat. This may result in cases where there is a lot of cooling energy in winter or unexpected parts of the year.  This input can be either a single boolean value to be applied to all connected zones or a list of boolean values for each different zone.  Often, to have tha sir side economizer be effective, you must also boost up the maximum air flow rate of the system above.
        heatRecovery_: Set to "True" to have the ideal air system include a heat recovery system.  This essentially means that the HVAC system will pass the outlet air through a heat exchanger with the inlet air before exhausting it, helping recover heat that would normally be lost through the exhaust.  If this input is set to "False" or left untouched, the HVAC system will simply exhaust air without having it interact with incoming air. This input can be either a single boolean value to be applied to all connected zones or a list of boolean values for each different zone.
        recoveryEffectiveness_: If the above input has been set to "True", input a number between 0 and 1 here to set the fraction of heat that is recovered by the heat recovery system.  By default, this value is 0.7.
    Returns:
        HBZones: HBZones with altered ideal air loads systems.
"""

ghenv.Component.Name = "Honeybee_Set Ideal Air Loads Parameters"
ghenv.Component.NickName = 'setEPIdealAir'
ghenv.Component.Message = 'VER 0.0.56\nFEB_28_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_28_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid


def checkTheInputs():
    #If the user puts in only one value, apply that value to all of the zones.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    if len(coolSupplyAirTemp_) == 1: coolSupplyAirTemp = duplicateData(coolSupplyAirTemp_, len(_HBZones))
    else: coolSupplyAirTemp = coolSupplyAirTemp_
    
    if len(heatSupplyAirTemp_) == 1: heatSupplyAirTemp = duplicateData(heatSupplyAirTemp_, len(_HBZones))
    else: heatSupplyAirTemp = heatSupplyAirTemp_
    
    if len(maxCoolingCapacity_) == 1: maxCoolingCapacity = duplicateData(maxCoolingCapacity_, len(_HBZones))
    else: maxCoolingCapacity = maxCoolingCapacity_
    
    if len(maxHeatingCapacity_) == 1: maxHeatingCapacity = duplicateData(maxHeatingCapacity_, len(_HBZones))
    else: maxHeatingCapacity = maxHeatingCapacity_
    
    if len(outdoorAirReq_) == 1: outdoorAirReq = duplicateData(outdoorAirReq_, len(_HBZones))
    else: outdoorAirReq = outdoorAirReq_
    
    #Check to be sure the input is correct.
    outdoorAirReqFinal = []
    checkData = True
    for outAirReq in outdoorAirReq:
        if outAirReq == "0" or outAirReq == "1" or outAirReq == "2" or outAirReq.upper() == "NONE" or outAirReq.upper() == "MAXIMUM" or outAirReq == "SUM":
            if outAirReq == "0": outdoorAirReqFinal.append("None")
            elif outAirReq == "1": outdoorAirReqFinal.append("Maximum")
            elif outAirReq == "2": outdoorAirReqFinal.append("Sum")
            else: outdoorAirReqFinal.append(outAirReq)
        else:
            checkData = False
            msg = "Invalid outdoorAirReq_ input."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    outdoorAirReq = outdoorAirReqFinal
    
    #Old options that used to be here but are misleading.
    airSideEconomizer_ = []
    heatRecovery_ = []
    recoveryEffectiveness_ = []
    
    if len(airSideEconomizer_) == 1: airSideEconomizer = duplicateData(airSideEconomizer_, len(_HBZones))
    else: airSideEconomizer = airSideEconomizer_
    
    if len(heatRecovery_) == 1: heatRecovery = duplicateData(heatRecovery_, len(_HBZones))
    else: heatRecovery = heatRecovery_
    
    if len(recoveryEffectiveness_) == 1: recoveryEffectiveness = duplicateData(recoveryEffectiveness_, len(_HBZones))
    else: recoveryEffectiveness = recoveryEffectiveness_
    
    
    return checkData, coolSupplyAirTemp, heatSupplyAirTemp, maxCoolingCapacity, maxHeatingCapacity, outdoorAirReq, airSideEconomizer, heatRecovery, recoveryEffectiveness


def main(HBZones, coolSupplyAirTemp, heatSupplyAirTemp, maxCoolingCapacity, maxHeatingCapacity, outdoorAirReq, airSideEconomizer, heatRecovery, recoveryEffectiveness):
    
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    HBZonesFromHive = hb_hive.callFromHoneybeeHive(HBZones)
    
    # assign the values
    for zoneCount, zone in enumerate(HBZonesFromHive):
        try:
            zone.coolSupplyAirTemp = str(coolSupplyAirTemp[zoneCount])
            print "Cooling supply air temperture for " + zone.name + " is set to: " + zone.coolSupplyAirTemp + ' C'
        except: pass
        
        try:
            zone.heatSupplyAirTemp = str(heatSupplyAirTemp[zoneCount])
            print "Heating supply air temperture for " + zone.name + " is set to: " + zone.heatSupplyAirTemp + ' C'
        except: pass
        
        try:
            zone.coolingCapacity = str(maxCoolingCapacity[zoneCount]*1000)
            print "Cooling capacity for " + zone.name + " is set to: " + zone.coolingCapacity + ' kWh'
        except: pass
        
        try:
            zone.heatingCapacity = str(maxHeatingCapacity[zoneCount]*1000)
            print "Heating capacity temperture for " + zone.name + " is set to: " + zone.heatingCapacity + ' kWh'
        except: pass
        
        try:
            zone.outdoorAirReq = outdoorAirReq[zoneCount]
            print zone.name + " has its outdoor air requirement set to " + outdoorAirReq[zoneCount]
        except: pass
        
        try:
            if airSideEconomizer[zoneCount] == True:
                zone.airSideEconomizer = 'DifferentialDryBulb'
                print zone.name + " will have an air side economizer."
        except: pass
        
        try:
            if heatRecovery[zoneCount] == True:
                zone.heatRecovery = 'Sensible'
                print zone.name + " will have heat recovery."
        except: pass
        
        try:
            zone.heatRecoveryEffectiveness = str(recoveryEffectiveness[zoneCount])
            print "Heat recovery effectiveness for " + zone.name + " is set to: " + zone.heatRecoveryEffectiveness
        except: pass
        
    # send the zones back to the hive
    HBZones  = hb_hive.addToHoneybeeHive(HBZonesFromHive, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
        
    return HBZones



if _HBZones:
    checkData, coolSupplyAirTemp, heatSupplyAirTemp, maxCoolingCapacity, maxHeatingCapacity, outdoorAirReq, airSideEconomizer, heatRecovery, recoveryEffectiveness = checkTheInputs()
    
    if checkData == True:
        zones = main(_HBZones, coolSupplyAirTemp, heatSupplyAirTemp, maxCoolingCapacity, maxHeatingCapacity, outdoorAirReq, airSideEconomizer, heatRecovery, recoveryEffectiveness)
        
        if zones!=-1:
            HBZones = zones




