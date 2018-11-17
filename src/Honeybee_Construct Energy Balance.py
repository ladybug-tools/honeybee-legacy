#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
This component accepst the outputs of the "Read EP Result" and the "Read EP Surface Result" components and outputs a data tree with all of the building-wide energy balance terms.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.

-
Provided by Honeybee 0.0.64
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        cooling_: The cooling load from the "Honeybee_Read EP Result" component.
        heating_: The heating load from the "Honeybee_Read EP Result" component.
        electricLight_: The electric lighting load from the "Honeybee_Read EP Result" component.
        electricEquip_: The electric equipment load from the "Honeybee_Read EP Result" component.
        fanElectric_: The electric fan load from the "Honeybee_Read EP Result" component.
        peopleGains_: The people gains from the "Honeybee_Read EP Result" component.
        totalSolarGain_: The total solar gain from the "Honeybee_Read EP Result" component.
        infiltrationEnergy_: The infiltration heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        mechVentilationEnergy_: The outdoor air heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        natVentEnergy_: The natural ventilation heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        surfaceEnergyFlow_: The surface heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Surface Result" component.
    Returns:
        readMe!: ...
        --------------------: ...
        flrNormEnergyBal: A data tree with the important building-wide energy balance terms normalized by floor area.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
        flrNormBalWStorage:  A data tree with the important building-wide energy balance terms normalized by floor area plus an additional term to represent the energy being stored in the building's mass.  If you have input all of the terms of your energy balance to this component, you storage term should be very small in relation to the other energy balance terms.  Thus, this storage term can be a good way to check whether all of your energy balance terms are accounted for.  This output can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
        --------------------: ...
        modelEnergyBalance:  A data tree with the important building-wide energy balance terms.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
        energyBalWithStorage:  A data tree with the important building-wide energy balance terms plus an additional term to represent the energy being stored in the building's mass.  If you have input all of the terms of your energy balance to this component, you storage term should be very small in relation to the other energy balance terms.  Thus, this storage term can be a good way to check whether all of your energy balance terms are accounted for.  This output can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
"""

ghenv.Component.Name = "Honeybee_Construct Energy Balance"
ghenv.Component.NickName = 'energyBalance'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_21_2016
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "5"


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc



def checkCreateDataTree(dataTree, dataName, dataType):
    #Define a variable for warnings.
    w = gh.GH_RuntimeMessageLevel.Warning
    
    #Convert the data tree to a python list.
    dataPyList = []
    for i in range(dataTree.BranchCount):
        branchList = dataTree.Branch(i)
        dataVal = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataVal.append(item)
        dataPyList.append(dataVal)
    
    #Test to see if the data has a header on it, which is necessary to know if it is the right data type.  If there's no header, the data should not be vizualized with this component.
    checkHeader = []
    dataHeaders = []
    dataNumbers = []
    for list in dataPyList:
        if str(list[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
            checkHeader.append(1)
            dataHeaders.append(list[:7])
            dataNumbers.append(list[7:])
        else:
            dataNumbers.append(list)
    
    if sum(checkHeader) == len(dataPyList):
        dataCheck1 = True
    else:
        if len(dataPyList) > 0 and dataPyList[0][0] == None: pass
        else:
            dataCheck1 = False
            warning = "Not all of the connected " + dataName + " has a Ladybug/Honeybee header on it.  This header is necessary to generate an indoor temperture map with this component."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    try:
        #Check to be sure that the lengths of data in in the dataTree branches are all the same.
        dataLength = len(dataNumbers[0])
        dataLenCheck = []
        for list in dataNumbers:
            if len(list) == dataLength:
                dataLenCheck.append(1)
            else: pass
        if sum(dataLenCheck) == len(dataNumbers) and dataLength <8761:
            dataCheck2 = True
        else:
            dataCheck2 = False
            warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if dataCheck1 == True:
            #Check to be sure that all of the data headers say that they are of the same type.
            header = dataHeaders[0]
            
            headerUnits =  header[3]
            headerStart = header[5]
            headerEnd = header[6]
            simStep = str(header[4])
            headUnitCheck = []
            headPeriodCheck = []
            nonIdealAir = False
            for head in dataHeaders:
                if dataType == 'Heating' or dataType == 'Cooling':
                    if 'Chiller' in head[2] or 'Coil' in head[2] or 'Boiler' in head[2]:
                        nonIdealAir = True
                if dataType in head[2]:
                    headUnitCheck.append(1)
                if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                    headPeriodCheck.append(1)
                else: pass
            
            if sum(headPeriodCheck) == len(dataHeaders):
                dataCheck3 = True
            else:
                dataCheck3 = False
                warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if sum(headUnitCheck) == len(dataHeaders):
                dataCheck4 = True
            else:
                dataCheck4 = False
                warning = "Not all of the connected " + dataName + " data is for the correct data type."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if nonIdealAir == True:
                dataCheck4 = False
                warning = "The HVAC system of the connected data is not Ideal Air.\n An ideal air system is necessary to reconstruct the zone-level energy balance."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if 'm2' in headerUnits or 'ft2' in headerUnits:
                dataCheck5 = False
                warning = "The data from the " + dataName + " input has been normalized by an area. \n Values need to be non-normalized for the energy balance to work."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                dataCheck5 = True
            
            if dataCheck1 == True and dataCheck2 == True and dataCheck3 == True and dataCheck4 == True and dataCheck5 == True: dataCheck = True
            else: dataCheck = False
        else:
            dataCheck = False
            headerUnits = 'unknown units'
            dataHeaders = []
            header = [None, None, None, None, None, None, None]
    except:
        dataCheck = True
        headerUnits = None
        dataHeaders = []
        dataNumbers = []
        header = [None, None, None, None, None, None, None]
    
    return dataCheck, headerUnits, dataHeaders, dataNumbers, [header[5], header[6]]


def getSrfNames(HBZones):
    wall = []
    window = []
    skylight =[]
    roof = []
    exposedFloor = []
    groundFloor = []
    undergroundWall = []
    
    for zone in HBZones:
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        zone = hb_hive.visualizeFromHoneybeeHive([zone])[0]
        
        for srf in zone.surfaces:
            if srf.BC.upper() == "OUTDOORS" or srf.BC.upper() == "GROUND":
                if srf.BC.upper() == "OUTDOORS":
                    # Wall
                    if srf.type == 0 or srf.type == 0.5:
                        if srf.hasChild:
                            wall.append(srf.name)
                            for childSrf in srf.childSrfs:
                                window.append(childSrf.name)
                        else: wall.append(srf.name)
                    #Roof
                    elif srf.type == 1 or srf.type == 3 or srf.type == 1.5:
                        if srf.hasChild:
                            roof.append(srf.name)
                            for childSrf in srf.childSrfs:
                                skylight.append(childSrf.name)
                        else: roof.append(srf.name)
                    #Floor
                    elif srf.type == 2.75 or srf.type == 2.5 or srf.type == 2:
                        if srf.hasChild:
                            exposedFloor.append(srf.name)
                            for childSrf in srf.childSrfs:
                                skylight.append(childSrf.name)
                        else: exposedFloor.append(srf.name)
                elif srf.BC.upper() == "GROUND":
                    # Wall
                    if srf.type == 0 or srf.type == 0.5:
                        if srf.hasChild:
                            undergroundWall.append(srf.name)
                            for childSrf in srf.childSrfs:
                                window.append(childSrf.name)
                        else: undergroundWall.append(srf.name)
                    #Roof
                    elif srf.type == 1 or srf.type == 3 or srf.type == 1.5 or srf.type == 2.75 or srf.type == 2.5 or srf.type == 2:
                        if srf.hasChild:
                            groundFloor.append(srf.name)
                            for childSrf in srf.childSrfs:
                                skylight.append(childSrf.name)
                        else: groundFloor.append(srf.name)
                    #Floor
                    elif srf.type == 2.75 or srf.type == 2.5 or srf.type == 2:
                        if srf.hasChild:
                            exposedFloor.append(srf.name)
                            for childSrf in srf.childSrfs:
                                skylight.append(childSrf.name)
                        else: exposedFloor.append(srf.name)
    
    return wall, window, skylight, roof, \
           exposedFloor, groundFloor, undergroundWall

def checkList(theList, dataTree, name, branchList):
    itemFound = False
    for srf in theList:
        if srf.upper() == name:
            dataTree.append(branchList)
            itemFound = True
        else: pass
    return itemFound

def sumAllLists(tree):
    if len(tree) == 1: summedList = tree[0]
    else:
        summedList = tree[0]
        for dataCount, dataList in enumerate(tree):
            if dataCount == 0: pass
            else:
                for count, item in enumerate(dataList):
                    summedList[count] = summedList[count] + item
    
    return summedList


def main(HBZones, heatingLoad, solarLoad, lightingLoad, equipLoad, fanElectric, peopleLoad, surfaceEnergyFlow, infiltrationEnergy, outdoorAirEnergy, natVentEnergy, coolingLoad):
    #Get the zone floor area.
    hb_hive = sc.sticky["honeybee_Hive"]()
    flrAreas = []
    for Hzone in HBZones:
        zone = hb_hive.visualizeFromHoneybeeHive([Hzone])[0]
        flrAreas.append(zone.getFloorArea())
    totalFlrArea = sum(flrAreas)
    
    #Check and convert the data for each of the zone data lists.
    checkData1, heatingUnits, heatingHeaders, heatingNumbers, heatingAnalysisPeriod = checkCreateDataTree(heatingLoad, "heating", "Heating")
    checkData2, solarUnits, solarHeaders, solarNumbers, solarAnalysisPeriod = checkCreateDataTree(solarLoad, "totalSolarGain_", "Solar")
    checkData3, lightingUnits, lightingHeaders, lightingNumbers, lightingAnalysisPeriod = checkCreateDataTree(lightingLoad, "electricLight_", "Lighting")
    checkData4, equipUnits, equipHeaders, equipNumbers, equipAnalysisPeriod = checkCreateDataTree(equipLoad, "electricEquip_", "Equipment")
    checkData5, peopleUnits, peopleHeaders, peopleNumbers, peopleAnalysisPeriod = checkCreateDataTree(peopleLoad, "peopleGains_", "People")
    checkData6, infiltrationUnits, infiltrationHeaders, infiltrationNumbers, infiltrationAnalysisPeriod = checkCreateDataTree(infiltrationEnergy, "infiltrationEnergy_", "Infiltration")
    checkData7, outdoorAirUnits, outdoorAirHeaders, outdoorAirNumbers, outdoorAirAnalysisPeriod = checkCreateDataTree(outdoorAirEnergy, "mechVentilationEnergy_", "Mechanical Ventilation")
    checkData8, natVentUnits, natVentHeaders, natVentNumbers, natVentAnalysisPeriod = checkCreateDataTree(natVentEnergy, "natVentEnergy_", "Natural Ventilation")
    checkData9, coolingUnits, coolingHeaders, coolingNumbers, coolingAnalysisPeriod = checkCreateDataTree(coolingLoad, "cooling", "Cooling")
    checkData10, surfaceUnits, surfaceHeaders, surfaceNumbers, surfaceAnalysisPeriod = checkCreateDataTree(surfaceEnergyFlow, "surfaceEnergyFlow_", "Surface Energy")
    checkData11, fanUnits, fanHeaders, fanNumbers, fanAnalysisPeriod = checkCreateDataTree(fanElectric, "fanElectric_", "Fan Electric")
    
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True  and checkData10 == True and checkData11 == True:
        #Get the names of the surfaces from the HBZones.
        wall, window, skylight, roof, exposedFloor, groundFloor, undergroundWall = getSrfNames(HBZones)
        
        #Organize all of the surface data by type of surface.
        opaqueEnergyFlow = []
        glazingEnergyFlow = []
        
        if len(surfaceNumbers) > 0:
            for srfCount, srfHeader in enumerate(surfaceHeaders):
                try:srfName = srfHeader[2].split(" for ")[-1].split(": ")[0]
                except:srfName = srfHeader[2].split(" for ")[-1]
                
                itemFound = checkList(wall, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(window, glazingEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(skylight, glazingEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(roof, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(exposedFloor, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(groundFloor, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(undergroundWall, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
        
        #Sum all of the zones and sufaces into one list for each energy balance term.
        if len(heatingNumbers) > 0: heatingNumbers = sumAllLists(heatingNumbers)
        if len(solarNumbers) > 0: solarNumbers = sumAllLists(solarNumbers)
        if len(lightingNumbers) > 0: lightingNumbers = sumAllLists(lightingNumbers)
        if len(equipNumbers) > 0: equipNumbers = sumAllLists(equipNumbers)
        if len(fanNumbers) > 0: fanNumbers = sumAllLists(fanNumbers)
        if len(peopleNumbers) > 0: peopleNumbers = sumAllLists(peopleNumbers)
        if len(infiltrationNumbers) > 0: infiltrationNumbers = sumAllLists(infiltrationNumbers)
        if len(outdoorAirNumbers) > 0: outdoorAirNumbers = sumAllLists(outdoorAirNumbers)
        if len(natVentNumbers) > 0: natVentNumbers = sumAllLists(natVentNumbers)
        if len(coolingNumbers) > 0: coolingNumbers = sumAllLists(coolingNumbers)
        if len(opaqueEnergyFlow) > 0: opaqueEnergyFlow = sumAllLists(opaqueEnergyFlow)
        if len(glazingEnergyFlow) > 0: glazingEnergyFlow = sumAllLists(glazingEnergyFlow)
        
        #Subtract the solar load from the glazing energy flow to get just the heat conduction through the glazing.
        for count, val in enumerate(glazingEnergyFlow):
            glazingEnergyFlow[count] = val - solarNumbers[count]
        
        #Make sure that the cooling energy is negative.
        if len(coolingNumbers) > 0:
            for count, val in enumerate(coolingNumbers):
                coolingNumbers[count] = -val
        
        #Add headers to the data number lists
        if len(heatingNumbers) > 0: heatingHeader = heatingHeaders[0][:2] + ['Heating'] + [heatingUnits] + [heatingHeaders[0][4]] + heatingAnalysisPeriod
        if len(solarNumbers) > 0: solarHeader = solarHeaders[0][:2] + ['Solar'] + [solarUnits] + [solarHeaders[0][4]] + solarAnalysisPeriod
        if len(lightingNumbers) > 0: lightingHeader = lightingHeaders[0][:2] + ['Lighting'] + [lightingUnits] + [lightingHeaders[0][4]] + lightingAnalysisPeriod
        if len(equipNumbers) > 0: equipHeader = equipHeaders[0][:2] + ['Equipment'] + [equipUnits] + [equipHeaders[0][4]] + equipAnalysisPeriod
        if len(fanNumbers) > 0: fanHeader = fanHeaders[0][:2] + ['Fan Electric'] + [fanUnits] + [fanHeaders[0][4]] + fanAnalysisPeriod
        if len(peopleNumbers) > 0: peopleHeader = peopleHeaders[0][:2] + ['People'] + [peopleUnits] + [peopleHeaders[0][4]] + peopleAnalysisPeriod
        if len(infiltrationNumbers) > 0: infiltrationHeader = infiltrationHeaders[0][:2] + ['Infiltration'] + [infiltrationUnits] + [infiltrationHeaders[0][4]] + infiltrationAnalysisPeriod
        if len(outdoorAirNumbers) > 0: outdoorAirHeader = outdoorAirHeaders[0][:2] + ['Mechanical Ventilation'] + [outdoorAirUnits] + [outdoorAirHeaders[0][4]] + outdoorAirAnalysisPeriod
        if len(natVentNumbers) > 0: natVentHeader = natVentHeaders[0][:2] + ['Natural Ventilation'] + [natVentUnits] + [natVentHeaders[0][4]] + natVentAnalysisPeriod
        if len(coolingNumbers) > 0: coolingHeader = coolingHeaders[0][:2] + ['Cooling'] + [coolingUnits] + [coolingHeaders[0][4]] + coolingAnalysisPeriod
        if len(opaqueEnergyFlow) > 0: opaqueHeader = surfaceHeaders[0][:2] + ['Opaque Conduction'] + [surfaceUnits] + [surfaceHeaders[0][4]] + surfaceAnalysisPeriod
        if len(glazingEnergyFlow) > 0: glazingHeader = surfaceHeaders[0][:2] + ['Glazing Conduction'] + [surfaceUnits] + [surfaceHeaders[0][4]] + surfaceAnalysisPeriod
        
        #Put each of the terms into one master list.    
        modelEnergyBalance = []
        modelEnergyBalanceNum = []
        if len(heatingNumbers) > 0:
            modelEnergyBalance.append(heatingHeader + heatingNumbers)
            modelEnergyBalanceNum.append(heatingNumbers)
        if len(solarNumbers) > 0:
            modelEnergyBalance.append(solarHeader + solarNumbers)
            modelEnergyBalanceNum.append(solarNumbers)
        if len(equipNumbers) > 0:
            modelEnergyBalance.append(equipHeader + equipNumbers)
            modelEnergyBalanceNum.append(equipNumbers)
        if len(fanNumbers) > 0:
            modelEnergyBalance.append(fanHeader + fanNumbers)
            modelEnergyBalanceNum.append(fanNumbers)
        if len(lightingNumbers) > 0:
            modelEnergyBalance.append(lightingHeader + lightingNumbers)
            modelEnergyBalanceNum.append(lightingNumbers)
        if len(peopleNumbers) > 0:
            modelEnergyBalance.append(peopleHeader + peopleNumbers)
            modelEnergyBalanceNum.append(peopleNumbers)
        if len(infiltrationNumbers) > 0:
            modelEnergyBalance.append(infiltrationHeader + infiltrationNumbers)
            modelEnergyBalanceNum.append(infiltrationNumbers)
        if len(outdoorAirNumbers) > 0:
            modelEnergyBalance.append(outdoorAirHeader + outdoorAirNumbers)
            modelEnergyBalanceNum.append(outdoorAirNumbers)
        if len(natVentNumbers) > 0:
            modelEnergyBalance.append(natVentHeader + natVentNumbers)
            modelEnergyBalanceNum.append(natVentNumbers)
        if len(opaqueEnergyFlow) > 0:
            modelEnergyBalance.append(opaqueHeader + opaqueEnergyFlow)
            modelEnergyBalanceNum.append(opaqueEnergyFlow)
        if len(glazingEnergyFlow) > 0:
            modelEnergyBalance.append(glazingHeader + glazingEnergyFlow)
            modelEnergyBalanceNum.append(glazingEnergyFlow)
        if len(coolingNumbers) > 0:
            modelEnergyBalance.append(coolingHeader + coolingNumbers)
            modelEnergyBalanceNum.append(coolingNumbers)
        
        #Create an energy balance list with a storage term.
        energyBalWithStorage = modelEnergyBalance[:]
        storageHeaderInit = modelEnergyBalance[0][:7]
        storageHeader = storageHeaderInit[:2] + ['Storage'] + storageHeaderInit[3:7]
        storageNumbers = sumAllLists(modelEnergyBalanceNum)
        for count, val in enumerate(storageNumbers):
            storageNumbers[count] = -val
        energyBalWithStorage.append(storageHeader + storageNumbers)
        
        #Create an energy balance normalized by floor area.
        flrNormEBal = []
        for dataList in modelEnergyBalance: flrNormEBal.append(dataList[:])
        for listcount, eBalList in enumerate(flrNormEBal):
            for valCount, val in enumerate(eBalList):
                try: flrNormEBal[listcount][valCount] = val/totalFlrArea
                except:
                    if 'kWh' in val: flrNormEBal[listcount][valCount] = 'kWh/m2'
        
        flrNormEBalWStorage = flrNormEBal[:]
        flrNormStorage = energyBalWithStorage[-1][:]
        for valCount, val in enumerate(flrNormStorage):
            try: flrNormStorage[valCount] = val/totalFlrArea
            except:
                if 'kWh' in val: flrNormStorage[valCount] = 'kWh/m2'
        flrNormEBalWStorage.append(flrNormStorage)
        
        
        return modelEnergyBalance, energyBalWithStorage, flrNormEBal, flrNormEBalWStorage
    else: return -1


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
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)



if initCheck == True and _HBZones != []:
    if heating_.BranchCount > 0 or totalSolarGain_.BranchCount > 0 or  electricLight_.BranchCount > 0 or  electricEquip_.BranchCount > 0 or  peopleGains_.BranchCount > 0 or  surfaceEnergyFlow_.BranchCount > 0 or infiltrationEnergy_.BranchCount > 0 or mechVentilationEnergy_.BranchCount > 0 or natVentEnergy_.BranchCount > 0 or cooling_.BranchCount > 0 or fanElectric_.BranchCount > 0:
        result = main(_HBZones, heating_, totalSolarGain_, electricLight_, electricEquip_, fanElectric_, peopleGains_, surfaceEnergyFlow_, infiltrationEnergy_, mechVentilationEnergy_, natVentEnergy_, cooling_)
        
        if result != -1:
            modelEnergyBalanceInit, energyBalWithStorageInit, flrNormEBalInit, flrNormEBalWStorageInit = result
            
            modelEnergyBalance = DataTree[Object]()
            energyBalWithStorage = DataTree[Object]()
            flrNormEnergyBal = DataTree[Object]()
            flrNormBalWStorage = DataTree[Object]()
            
            for dataCount, dataList in enumerate(modelEnergyBalanceInit):
                for item in dataList: modelEnergyBalance.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(energyBalWithStorageInit):
                for item in dataList: energyBalWithStorage.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(flrNormEBalInit):
                for item in dataList: flrNormEnergyBal.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(flrNormEBalWStorageInit):
                for item in dataList: flrNormBalWStorage.Add(item, GH_Path(dataCount))