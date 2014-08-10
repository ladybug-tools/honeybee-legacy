"""
export geometries to idf file, and run the energy simulation

    Args:
        input1: ...
        meshSettings_: Custom mesh setting. Use Grasshopper mesh setting components
        
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Honeybee_ Run Energy Simulation"
ghenv.Component.NickName = 'runEnergySimulation'
ghenv.Component.Message = 'VER 0.0.53\nAUG_09_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import System
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import shutil

rc.Runtime.HostUtils.DisplayOleAlerts(False)


class WriteIDF(object):
    
    def __init__(self, workingDir):
        self.fileBasedSchedules = {}
        self.workingDir = workingDir
        
    def EPZone(self, zone):
        return '\nZone,\n' + \
        '\t' + zone.name + ',\n' + \
        '\t' + `zone.north` + ',\t!-Direction of Relative North {deg}\n' + \
        '\t' + `zone.origin.X` + ',\t!- X Origin {m}\n' + \
        '\t' + `zone.origin.Y` + ',\t!- Y Origin {m}\n' + \
        '\t' + `zone.origin.Z` + ',\t!- Z Origin {m}\n' + \
        '\t1;\t!- Type\n'
    
    def EPZoneSurface (self, surface):
        
        coordinates = surface.coordinates
        
        checked, coordinates= self.checkCoordinates(coordinates)
        
        if checked:
            str_1 = '\nBuildingSurface:Detailed,\n' + \
                '\t' + surface.name + ',\t!- Name\n' + \
                '\t' + surface.srfType[int(surface.type)] + ',\t!- Surface Type\n' + \
                '\t' + surface.construction + ',\t!- Construction Name\n' + \
                '\t' + surface.parent.name + ',\t!- Zone Name\n' + \
                '\t' + surface.BC + ',\t!- Outside Boundary Condition\n' + \
                '\t' + surface.BCObject.name + ',\t!- Outside Boundary Condition Object\n' + \
                '\t' + surface.sunExposure + ',\t!- Sun Exposure\n' + \
                '\t' + surface.windExposure + ',\t!- Wind Exposure\n' + \
                '\t' + surface.groundViewFactor + ',\t!- View Factor to Ground\n' + \
                '\t' + `len(coordinates)` + ',\t!- Number of Vertices\n'
        
            str_2 = '\t';
            
            for ptCount, pt in enumerate(coordinates):
                if ptCount < len (coordinates) - 1:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ',\n\t'
                else:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ';\n\n'
            
            fullString = str_1 + str_2
            
            return fullString
        
        else:
            return "\n"
            
    def checkCoordinates(self, coordinates):
        # check if coordinates are so close or duplicated
        # this is a place holder for now I just return true
        #return True, glzCoordinates
    
        def isDuplicate(pt, newPts):
            for p in newPts:
                if pt.DistanceTo(p) < 2 * sc.doc.ModelAbsoluteTolerance:
                    return True
            return False
            
        newCoordinates = [coordinates[0]]
        for pt in coordinates[1:]:
            if not isDuplicate(pt, newCoordinates):
                newCoordinates.append(pt)
            
        if len(newCoordinates) > 2:
            return True, newCoordinates
        else:
            print "One of the surfaces has less than 3 identical coordinates and is removed."
            return False,[]
                        
    def EPFenSurface (self, surface):
        glzStr = ""
        try:
            for childSrf in surface.childSrfs:
                # check surface area
                
                glzCoordinates = childSrf.coordinates
                
                checked, glzCoordinates= self.checkCoordinates(glzCoordinates)
                
                if checked:
                    str_1 = '\nFenestrationSurface:Detailed,\n' + \
                        '\t' + childSrf.name + ',\t!- Name\n' + \
                        '\t' + childSrf.srfType[childSrf.type] + ',\t!- Surface Type\n' + \
                        '\t' + childSrf.construction + ',\t!- Construction Name\n' + \
                        '\t' + childSrf.parent.name + ',\t!- Surface Name\n' + \
                        '\t' + childSrf.BCObject.name + ',\t!- Outside Boundary Condition Object\n' + \
                        '\t' + childSrf.groundViewFactor + ',\t!- View Factor to Ground\n' + \
                        '\t' + childSrf.shadingControlName + ',\t!- Shading Control Name\n' + \
                        '\t' + childSrf.frameName + ',\t!- Frame and Divider Name\n' + \
                        '\t' + `childSrf.Multiplier`+ ',\t!- Multiplier\n' + \
                        '\t' + `len(glzCoordinates)` + ',\t!- Number of Vertices\n'
                
                    str_2 = '\t';
                    for ptCount, pt in enumerate(glzCoordinates):
                        if ptCount < len (glzCoordinates) - 1:
                            str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ',\n\t'
                        else:
                            str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ';\n\n'
                    
                    glzStr += str_1 + str_2
                
                else:
                    glzStr += "\n"
        except Exception, e:
            print e
            print "Failed to write " + childSrf.name + " to idf file"
            pass
            
        return glzStr
        

    def EPShdSurface (self, surface):
        coordinatesList = surface.extractPoints()
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple: coordinatesList = [coordinatesList]
        
        fullString = ''
        for count, coordinates in enumerate(coordinatesList):
            str_1 = '\nShading:Building:Detailed,\n' + \
                    '\t' + surface.name + '_' + `count` + ',\t!- Name\n' + \
                    '\t' + surface.TransmittanceSCH + ',\t!- Transmittance Schedule Name\n' + \
                    '\t' + `len(coordinates)` + ',\t!- Number of Vertices\n'    
    
            str_2 = '\t';
            for ptCount, pt in enumerate(coordinates):
                if ptCount < len (coordinates) - 1:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ',\n\t'
                else:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ';\n\n'
            
            fullString = fullString + str_1 + str_2
        
        return fullString

    def EPZoneListStr(self, zoneListName, zones):
        str_1 = 'ZoneList,\n' + \
                '\t' + zoneListName + ',\n'
                
        str_2 = ''
        for zoneCount, zone in enumerate(zones):
            if zoneCount < len(zones) - 1:
                str_2 = str_2 + '\t' + zone.name + ',\n'
            else:
                str_2 = str_2 + '\t' + zone.name + ';\n\n'
        return str_1 + str_2
    
    def writeHVACSched0(self):
        return '\nScheduleTypeLimits, \n' + \
        '\t' + 'Control Type, !- Name\n' + \
        '\t0,                       !- Lower Limit Value\n' + \
        '\t4,                       !- Upper Limit Value\n' + \
        '\t' + 'DISCRETE;                !- Numeric Type\n'
    
    def writeHVACSched1(self):
        return '\nSchedule:Year, HVAC Operation Schedule, Control Type,\n' + \
        '\t' + 'Winter Control Type Week Sch, 1, 1, 3, 31' + ',  !- End winter\n' + \
        '\t' + 'Summer Control Type Week Sch, 4, 1, 9, 30' + ',  !- Summer\n' + \
        '\t' + 'Winter Control Type Week Sch, 10, 1, 12, 31' + ';  !- Start winter\n'
    
    def writeHVACSched2(self):
        return '\nSchedule:Day:Hourly, Summer Control Type Day Sch, Control Type,\n' + \
        '\t' + '4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4' + ';\n'
    
    def writeHVACSched3(self):
        return '\nSchedule:Day:Hourly, Winter Control Type Day Sch, Control Type,\n' + \
        '\t' + '4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4' + ';\n'
    
    def writeHVACSched4(self):
        return '\nSchedule:Week:Daily, Summer Control Type Week Sch,\n' + \
        '\t' + 'Summer Control Type Day Sch,Summer Control Type Day Sch,Summer Control Type Day Sch,' + '\n' + \
        '\t' + 'Summer Control Type Day Sch,Summer Control Type Day Sch,Summer Control Type Day Sch,' + '\n' + \
        '\t' + 'Summer Control Type Day Sch,Summer Control Type Day Sch,Summer Control Type Day Sch,' + '\n' + \
        '\t' + 'Summer Control Type Day Sch,Summer Control Type Day Sch,Summer Control Type Day Sch;'+ '\n'
    
    def writeHVACSched5(self):
        return '\nSchedule:Week:Daily, Winter Control Type Week Sch,\n' + \
        '\t' + 'Winter Control Type Day Sch,Winter Control Type Day Sch,Winter Control Type Day Sch,' + '\n' + \
        '\t' + 'Winter Control Type Day Sch,Winter Control Type Day Sch,Winter Control Type Day Sch,' + '\n' + \
        '\t' + 'Winter Control Type Day Sch,Winter Control Type Day Sch,Winter Control Type Day Sch,' + '\n' + \
        '\t' + 'Winter Control Type Day Sch,Winter Control Type Day Sch,Winter Control Type Day Sch;'+ '\n'
    
    def writeThemostat(self, name, zone):
        if zone.isConditioned:
            return '\nZoneControl:Thermostat,\n' + \
            '\t' + name + ' Thermostat' + ',  !- Thermostat Name\n' + \
            '\t' + name + ',  !- Zone Name\n' + \
            '\t' + 'HVAC Operation Schedule' + ',  !- Control Type Schedule Name\n' + \
            '\t' + 'ThermostatSetpoint:DualSetpoint' + ',  !- Control Type\n' + \
            '\t' + name + ' Thermostat Dual SP Control' + ';  !- Control Type Name\n'
        else:
            return "\n"
    
    def writeSetpoint(self, zone, name):
        if zone.isConditioned:
            return '\nThermostatSetpoint:DualSetpoint,\n' + \
            '\t' + name + ' Thermostat Dual SP Control' + ',  !- Name\n' + \
            '\t' + zone.heatingSetPtSchedule + ',  !- Heating Setpoint Temperature Schedule Name\n' + \
            '\t' + zone.coolingSetPtSchedule + ';  !- Cooling Setpoint Temperature Schedule Name\n'
        else:
            return "\n"
    
    def writeEquipConnect(self, name, zone):
        if zone.isConditioned:
            return '\nZoneHVAC:EquipmentConnections,\n' + \
            '\t' + name + ',  !- Zone Name\n' + \
            '\t' + name + " Equipment" + ',  !- Zone Conditioning Equipment List Name\n' + \
            '\t' + name + " Inlets" + ',  !- List Name: Zone Air Inlet Nodes\n' + \
            '\t' + ',  !- List Name: Zone Air Exhaust Nodes\n' + \
            '\t' + name + " Zone Air Node" + ',  !- Zone Air Node Name\n' + \
            '\t' + name + " Return Outlet" + ';  !- Zone Return Air Node Name\n'
        else:
            return "\n"
    
    def writeEquipList(self, name, zone):
        if zone.isConditioned:
            return '\nZoneHVAC:EquipmentList,\n' + \
            '\t' + name + ' Equipment' + ',  !- Name\n' + \
            '\t' + "ZoneHVAC:IdealLoadsAirSystem" + ',  !- Zone Equipment 1 Object Type\n' + \
            '\t' + name + "ZoneHVAC:IdealLoadsAirSystem" + ',  !- Zone Equipment 1 Name\n' + \
            '\t' + '1' + ',  !- Zone Equipment 1 Cooling Sequence\n' + \
            '\t' + "1" + ';  !- Zone Equipment 1 Heating or No-Load Sequence\n'
        else:
            return "\n"
    
    def writeNodeList(self, name, zone):
        if zone.isConditioned:
            return '\nNodeList,\n' + \
            '\t' + name + ' Inlets' + ',  !- List Name\n' + \
            '\t' + "Node " + name + " In" + ';  !- Node Name\n'
        else:
            return "\n"
    
    def writeIdealAirSys(self, name, zone):
        if zone.isConditioned:
            if zone.coolSupplyAirTemp == "": coolSupply = "11"
            else: coolSupply = zone.coolSupplyAirTemp
            if zone.heatSupplyAirTemp == "": heatSupply = "40"
            else: heatSupply = zone.heatSupplyAirTemp
            # print coolSupply 
            return '\nZoneHVAC:IdealLoadsAirSystem,\n' + \
            '\t' + name + "ZoneHVAC:IdealLoadsAirSystem" + ',  !- Ideal Loads Air Name\n' + \
            '\t' + ',  !- Availability Schedule Name\n' + \
            '\t' + "Node " + name + " In" + ',  !- Zone Supply Air Node Name\n' + \
            '\t' + ',  !- Zone Exhaust Air Node Name\n' + \
            '\t' + heatSupply + ',  !- Heating Supply Air Temp {C}\n' + \
            '\t' + coolSupply + ',  !- Cooling Supply Air Temp {C}\n' + \
            '\t' + ',  !- Max Heating Supply Air Humidity Ratio {kg-H2O/kg-air}\n' + \
            '\t' + ',  !- Min Cooling Supply Air Humidity Ratio {kg-H2O/kg-air}\n' + \
            '\t' + "NoLimit" + ',  !- Heating Limit\n' + \
            '\t' + ',  !- Maximum Heating Air Flow Rate {m3/s}\n' + \
            '\t' + ',  !- Maximum Sensible Heat Capacity\n' + \
            '\t' + "NoLimit" + ',  !- Cooling Limit\n' + \
            '\t' + ',  !- Maximum Cooling Air Flow Rate {m3/s}\n' + \
            '\t' + ',  !- Maximum Total Cooling Capacity\n' + \
            '\t' + ',  !- Heating Availability Schedule\n' + \
            '\t' + ',  !- Cooling Availability Schedule\n' + \
            '\t' + 'None' + ',  !- Dehumidification Control Type\n' + \
            '\t' + ',  !- Cooling Sensible Heat Ratio\n' + \
            '\t' + 'None' + ',  !- Humidification Control Type\n' + \
            '\t' + ',  !- Outside Air Object Name\n' + \
            '\t' + ',  !- Outside Air Inlet Name\n' + \
            '\t' + ',  !- Demand Controlled Ventilation Type\n' + \
            '\t' + ',  !- Outdoor Air Economizer Type\n' + \
            '\t' + ',  !- Heat Recovery Type\n' + \
            '\t' + ',  !- Seneible HEat Recovery Effectiveness\n' + \
            '\t' + ';  !- Latent HEat Recovery Effectiveness\n'
        else:
            return "\n"
    
    def EPHVACTemplate( self, name, zone):
        if zone.isConditioned:
            heatingSCHName = zone.heatingSetPtSchedule
            if zone.heatingSetPtSchedule != "":
                constantHeatingSetPoint = zone.heatingSetPtSchedule
            else:
                constantHeatingSetPoint = '' # I should add this to zones later
            
            coolingSCHName = zone.coolingSetPtSchedule
            if zone.heatingSetPtSchedule != "":
                constantCoolingSetPoint = zone.coolingSetPtSchedule
            else:
                constantCoolingSetPoint = ''
            
            return '\nHVACTemplate:Thermostat,\n' + \
                    '\t' + name + ',                    !- Name\n' + \
                    '\t' + heatingSCHName + ',          !- Heating Setpoint Schedule Name\n' + \
                    '\t' + constantHeatingSetPoint + ', !- Constant Heating Setpoint {C}\n' + \
                    '\t' + coolingSCHName + ',          !- Cooling Setpoint Schedule Name\n' + \
                    '\t' + constantCoolingSetPoint + '; !- Constant Cooling Setpoint {C}\n'
        else:
            return "\n"
            
    def EPIdealAirSystem(self, zone, thermostatName):
        if zone.isConditioned:
            return '\nHVACTemplate:Zone:IdealLoadsAirSystem,\n' + \
                '\t' + zone.name + ',\t!- Zone Name\n' + \
                '\t' + thermostatName + ';\t!- Template Thermostat Name\n\n'
        else:
            return "\n"

    def EPSiteLocation(self, epw_file):
        epwfile = open(epw_file,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        locName = csheadline[1]+'\t'+csheadline[3]
        lat = csheadline[-4]
        lngt = csheadline[-3]
        timeZone = csheadline[-2]
        elev = csheadline[-1][:-1]
        locationString = "\nSite:Location,\n" + \
            '\t' + locName + ',\n' + \
            '\t' + lat + ',    !Latitude\n' + \
            '\t' + lngt + ',   !Longitude\n' + \
            '\t' + timeZone + ', !Time Zone\n' + \
            '\t' + elev + ';   !Elevation\n'
        epwfile.close()
        return locationString

    def EPVersion(self, version = 8.1):
        return '\nVersion, ' + `version` + ';\n'
    
    def EPTimestep(self, timestep = 6):
        return '\nTimestep, ' + `timestep` + ';\n'
    
    def EPShadowCalculation(self, calculationMethod = "AverageOverDaysInFrequency", frequency = 6, maximumFigures = 1500):
        return '\nShadowCalculation,\n' + \
               '\t' + calculationMethod + ',        !- Calculation Method\n' + \
               '\t' + str(frequency) + ',        !- Calculation Frequency\n' + \
               '\t' + str(maximumFigures) + ';    !- Maximum Figures in Shadow Overlap Calculation\n'

    def EPProgramControl(self, numT = 10):
        return '\nProgramControl,\n' + \
               '\t' + `numT` + '; !- Number of Threads AllowedNumber\n'
    
    def EPBuilding(self, name= 'honeybeeBldg', north = 0, terrain = 'City',
                    loadConvergenceTol = 0.04, tempConvergenceTol = 0.4,
                    solarDis = 'FullInteriorAndExteriorWithReflections', maxWarmUpDays = 25,
                    minWarmUpDays = 6):
                    # 'FullInteriorAndExterior'
        return '\nBuilding,\n' + \
                '\t' + name + ', !- Name\n' + \
                '\t' + `north` + ', !- North Axis {deg}\n' + \
                '\t' + terrain + ', !- Terrain\n' + \
                '\t' + `loadConvergenceTol` + ', !- Loads Convergence Tolerance Value\n' + \
                '\t' + `tempConvergenceTol` + ', !- Temperature Convergence Tolerance Value {deltaC}\n' + \
                '\t' + solarDis + ', !- Solar Distribution or maybe FullExterior\n' + \
                '\t' + `maxWarmUpDays` + ', !- Maximum Number of Warmup Days\n' + \
                '\t' + `minWarmUpDays` + '; !- Minimum Number of Warmup Days\n'
    
    def EPHeatBalanceAlgorithm(self, algorithm = 'ConductionTransferFunction'):
        return '\nHeatBalanceAlgorithm, ' + algorithm + ';\n'
    
    def EPSurfaceConvectionAlgorithm(self, insideAlg = 'TARP', outsideAlg = 'DOE-2'):
        insideStr = '\nSurfaceConvectionAlgorithm:Inside, ' + insideAlg + ';\n'
        outsideStr = '\nSurfaceConvectionAlgorithm:Outside, '+ outsideAlg + ';\n'
        return insideStr + outsideStr
    
    def EPSimulationControl(self, zoneSizing = 'No', systemSizing ='No', plantSizing = 'No',
                                runForSizing = 'No', runForWeather = 'Yes'):
        booleanToText = {
                         True : "Yes",
                         False: "No",
                         "Yes": "Yes",
                         "No" : "No"
                         }
                         
        return '\nSimulationControl,\n' + \
                '\t' + booleanToText[zoneSizing] + ',    !- Do Zone Sizing Calculation\n' + \
                '\t' + booleanToText[systemSizing] + ',  !- Do System Sizing Calculation\n' + \
                '\t' + booleanToText[plantSizing] + ',   !- Do Plant Sizing Calculation\n' + \
                '\t' + booleanToText[runForSizing] + ',  !- Run Simulation for Sizing Periods\n' + \
                '\t' + booleanToText[runForWeather] + '; !- Run Simulation for Weather File Run Periods\n'
    
    def EPRunPeriod(self, name = 'annualRun', stDay = 1, stMonth = 1, endDay = 31, endMonth = 12):
        
        return '\nRunPeriod,\n' + \
               '\t' + name + ',    !- Name\n' + \
               '\t' + `stMonth` + ',   !- Begin Month\n' + \
               '\t' + `stDay` + ',    !- Begin Day of Month\n' + \
               '\t' + `endMonth` + ', !- End Month\n' + \
               '\t' + `endDay` + ',   !- End Day of Month\n' + \
               '\t' + 'UseWeatherFile,   !- Day of Week for Start Day\n' + \
               '\t' + 'Yes,              !- Use Weather File Holidays and Special Days\n' + \
               '\t' + 'Yes,              !- Use Weather File Daylight Saving Period\n' + \
               '\t' + 'No,               !- Apply Weekend Holiday Rule\n' + \
               '\t' + 'Yes,              !- Use Weather File Rain Indicators\n' + \
               '\t' + 'Yes;              !- Use Weather File Snow Indicators\n'

    def EPGeometryRules(self, stVertexPos = 'LowerLeftCorner', direction = 'CounterClockWise', coordinateSystem = 'Absolute'):
        return '\nGlobalGeometryRules,\n' + \
                '\t' + stVertexPos + ',         !- Starting Vertex Position\n' + \
                '\t' + direction + ',        !- Vertex Entry Direction\n' + \
                '\t' + coordinateSystem + ';                !- Coordinate System\n'

    def EPDesignSpecOA(self, zone):
        """
        Returns design specification for outdoor air
        """
        if zone.isConditioned:
            return "\nDesignSpecification:OutdoorAir,\n" + \
                   "\tDSOA" + zone.name + ", !- Name\n" + \
                   "\tsum, !- Outdoor Air Method\n" + \
                   "\t" + str(zone.ventilationPerPerson) + ", !- Outdoor Air Flow per Person {m3/s-person}\n" + \
                   "\t" + str(zone.ventilationPerArea) + ", !- Outdoor Air Flow per Zone Floor Area {m3/s-m2}\n" + \
                   "\t0.0; !- Outdoor Air Flow per Zone {m3/s}"
        else:
            return "\n"

    def EPZoneInfiltration(self, zone, zoneListName = None):
        """ Methods: 
            0: Flow/Zone => Design Flow Rate -- simply enter Design Flow Rate
            1: Flow/Area => Flow per Zone Floor Area - Value * Floor Area (zone) = Design Flow Rate
            2: Flow/ExteriorArea => Flow per Exterior Surface Area - Value * Exterior Surface Area (zone) = Design Flow Rate
            3: Flow/ExteriorWallArea => Flow per Exterior Surface Area - Value * Exterior Wall Surface Area (zone) = Design Flow Rate
            4: AirChanges/Hour => Air Changes per Hour - Value * Floor Volume (zone) adjusted for m3/s = Design Volume Flow Rate "Idesign" in Equation is the result.
        """
        if zoneListName == None:
            zoneListName = zone.name
        
        name = zoneListName + "_Infiltration"
        
        # Rest of the methods are not available from the interface right now
        scheduleName = zone.infiltrationSchedule
        method = 1 
        value = zone.infiltrationRatePerArea
        
        methods = {0: 'Flow/Zone',
                   1: 'Flow/Area',
                   2: 'Flow/ExteriorArea',
                   3: 'Flow/ExteriorWallArea',
                   4: 'AirChanges/Hour'}
        
        designFlowRate = ''
        flowPerZoneArea = ''
        flowPerExteriorArea = ''
        flowPerExteriorWallArea = ''
        airChangePerHour = ''
        
        if method == 0: designFlowRate = `value`
        elif method == 1: flowPerZoneArea = `value`
        elif method == 2: flowPerExteriorArea = `value`
        elif method == 3: flowPerExteriorArea = `value`
        elif method == 4: airChangePerHour = `value`
        
        return '\nZoneInfiltration:DesignFlowRate,\n' + \
                '\t' + name + ',  !- Name\n' + \
                '\t' + zoneListName + ',  !- Zone or ZoneList Name\n' + \
                '\t' + scheduleName + ',  !- Schedule Name\n' + \
                '\t' + methods[method] + ',  !- Design Flow Rate Calculation Method\n' + \
                '\t' + designFlowRate + ',   !- Design Flow Rate {m3/s}\n' + \
                '\t' + flowPerZoneArea + ',  !- Flow per Zone Floor Area {m3/s-m2}\n' + \
                '\t' + flowPerExteriorArea + ', !- Flow per Exterior Surface Area {m3/s-m2}\n' + \
                '\t' + airChangePerHour + ',    !- Air Changes per Hour\n' + \
                '\t,                        !- Constant Term Coefficient\n' + \
                '\t,                        !- Temperature Term Coefficient\n' + \
                '\t,                        !- Velocity Term Coefficient\n' + \
                '\t;                        !- Velocity Squared Term Coefficient\n'
    
    
    def EPZoneElectricEquipment(self, zone, zoneListName = None):
            
        #name = 'largeOfficeElectricEquipment', zoneListName ='largeOffices', method = 2, value = 5.8125141276385044,
        #               scheduleName = 'Large Office_BLDG_EQUIP_SCH', endUseSub = 'ElectricEquipment'):
        
        """
        Methods:
            0: EquipmentLevel => Equipment Level -- simply enter watts of equipment
            1: Watts/Area => Watts per Zone Floor Area -- enter the number to apply.  Value * Floor Area = Equipment Level
            2: Watts/Person => Watts per Person -- enter the number to apply.  Value * Occupants = Equipment Level
        """
        
        if zoneListName == None:
            zoneListName = zone.name
        name = zoneListName + 'ElectricEquipment'
        method = 1
        value = zone.equipmentLoadPerArea
        scheduleName = zone.equipmentSchedule
        endUseSub = 'ElectricEquipment'

        methods = {0: 'EquipmentLevel',
           1: 'Watts/Area',
           2: 'Watts/Person'}

        designLevel = ''
        wattPerZoneArea = ''
        wattPerPerson = ''
        
        if method == 0: designLevel = `value`
        elif method == 1: wattPerZoneArea = `value`
        elif method == 2: wattPerPerson = `value`
        
        return '\nElectricEquipment,\n' + \
        '\t' + name + ',  !- Name\n' + \
        '\t' + zoneListName + ',  !- Zone or ZoneList Name\n' + \
        '\t' + scheduleName + ',  !- Schedule Name\n' + \
        '\t' + methods[method] + ', !- Design Level Calculation Method\n' + \
        '\t' + designLevel + ', !- Design Level {W}\n' + \
        '\t' + wattPerZoneArea + ', !- Watts per Zone Floor Area {W/m2}\n' + \
        '\t' + wattPerPerson + ',   !- Watts per Person {W/person}\n' + \
        '\t,                        !- Fraction Latent\n' + \
        '\t,                        !- Fraction Radiant\n' + \
        '\t,                        !- Fraction Lost\n' + \
        '\t' + endUseSub + ';       !- End-Use Subcategory\n'

    def EPZoneLights(self, zone, zoneListName = None):
        
        #name = 'largeOfficeLights', zoneListName ='largeOffices', method = 0, value = 9.687523546064174,
        #scheduleName = 'Large Office_BLDG_LIGHT_SCH', lightingLevel = 250):
        
        if zoneListName == None:
                zoneListName = zone.name
        name = zoneListName + 'OfficeLights'
        value = zone.lightingDensityPerArea
        scheduleName = zone.lightingSchedule
        
        if scheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            scheduleName = self.fileBasedSchedules[scheduleName.upper()]
        
        if zone.daylightThreshold != "":
            method = 2
            lightingLevel = str(zone.daylightThreshold)
        else:
            method = 0
            lightingLevel = ""
        """
        Methods:
            0: Watts/Area => Watts per Zone Floor Area -- enter the number to apply.  Value * Floor Area = Equipment Level
            1: Watts/Person => Watts per Person -- enter the number to apply.  Value * Occupants = Equipment Level
        """
        
        methods = {0: 'Watts/Area',
                   1: 'Watts/Person',
                   2: 'LightingLevel'}
        
        wattPerZoneArea = ''
        wattPerPerson = ''
        
        if method == 0: wattPerZoneArea = `value`
        elif method == 1: wattPerPerson = `value`
            
        return '\nLights,\n' + \
        '\t' + name + ',  !- Name\n' + \
        '\t' + zoneListName + ',  !- Zone or ZoneList Name\n' + \
        '\t' + scheduleName + ',  !- Schedule Name\n' + \
        '\t' + methods[method] + ',       !- Design Level Calculation Method\n' + \
        '\t' + lightingLevel + ',       !- Lighting Level {W}\n' + \
        '\t' + wattPerZoneArea + ',       !- Watts per Zone Floor Area {W/m2}\n' + \
        '\t' + wattPerPerson + ',         !- Watts per Person {W/person}\n' + \
        '\t,                       !- Return Air Fraction\n' + \
        '\t,                       !- Fraction Radiant\n' + \
        '\t;                       !- Fraction Visible\n'

    
    def EPZonePeople(self, zone, zoneListName =None):
        
        # , method = 1, value = 0.053819575255912078,
        #scheduleName = 'Large Office_BLDG_OCC_SCH', activityScheduleName = 'Large Office_ACTIVITY_SCH',
        # fractionRadiant = 0.3, sensibleHeatFraction = 'autocalculate'):
            
        if zoneListName == None:
                zoneListName = zone.name
        name = zoneListName + 'OfficePeople'
        method = 1
        value = zone.numOfPeoplePerArea
        scheduleName = zone.occupancySchedule
        activityScheduleName = zone.occupancyActivitySch
        fractionRadiant = 0.3
        sensibleHeatFraction = 'autocalculate'
        
        """
        Methods:
            0: People -- simply enter number of occupants.
            1: People per Zone Floor Area -- enter the number to apply. Value * Floor Area = Number of people
            2: Zone Floor Area per Person -- enter the number to apply. Floor Area / Value = Number of people
        """
        if type(fractionRadiant) is int or type(fractionRadiant) is float: fractionRadiant = `fractionRadiant`
        if type(sensibleHeatFraction) is int or type(sensibleHeatFraction) is float: sensibleHeatFraction = `sensibleHeatFraction`
        
        methods = {0: 'People',
                   1: 'People/Area',
                   2: 'Area/Person'}
        
        numOfPeople = ''
        peoplePerArea = ''
        areaPerPerson = ''
        
        if method == 0: numOfPeople = `value`
        elif method == 1: peoplePerArea = `value`
        elif method == 2: areaPerPerson = `value`
        
        return '\nPeople,\n' + \
        '\t' + name + ',  !- Name\n' + \
        '\t' + zoneListName + ',  !- Zone or ZoneList Name\n' + \
        '\t' + scheduleName + ',  !- Number of People Schedule Name\n' + \
        '\t' + methods[method] + ', !- Number of People Calculation Method\n' + \
        '\t' + numOfPeople + ', !- Number of People\n' + \
        '\t' + peoplePerArea + ',  !- People per Zone Floor Area {person/m2}\n' + \
        '\t' + areaPerPerson + ',  !- Zone Floor Area per Person {m2/person}\n' + \
        '\t' + fractionRadiant + ',     !- Fraction Radiant\n' + \
        '\t' + sensibleHeatFraction + ',!- Sensible Heat Fraction\n' + \
        '\t' + activityScheduleName + ';!- Activity Level Schedule Name\n'
    
    def EPMaterialStr(self, materialName):
        materialData = None
        if materialName in sc.sticky ["honeybee_windowMaterialLib"].keys():
            materialData = sc.sticky ["honeybee_windowMaterialLib"][materialName]
        elif materialName in sc.sticky ["honeybee_materialLib"].keys():
            materialData = sc.sticky ["honeybee_materialLib"][materialName]
            
        if materialData!=None:
            numberOfLayers = len(materialData.keys())
            materialStr = materialData[0] + ",\n"
            
            # add the name
            materialStr =  materialStr + "  " + materialName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    materialStr =  materialStr + "  " + str(materialData[layer][0]) + ",   !- " +  materialData[layer][1] + "\n"
                else:
                    materialStr =  materialStr + "  " + str(materialData[layer][0]) + ";   !- " +  materialData[layer][1] + "\n\n"
            return materialStr
       
    def EPConstructionStr(self, constructionName):
        constructionData = None
        if constructionName in sc.sticky ["honeybee_constructionLib"].keys():
            constructionData = sc.sticky ["honeybee_constructionLib"][constructionName]
        
        if constructionData!=None:
            materials = []
            numberOfLayers = len(constructionData.keys())
            constructionStr = constructionData[0] + ",\n"
            # add the name
            constructionStr =  constructionStr + "  " + constructionName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ",   !- " +  constructionData[layer][1] + "\n"
                else:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ";   !- " +  constructionData[layer][1] + "\n\n"
                materials.append(constructionData[layer][0])
                
            return constructionStr, materials
        else:
            print "Failed to find " + constructionName + " in library."
            return None, None
            
    def EPSCHStr(self, scheduleName):
        scheduleData = None
        scheduleName= scheduleName.upper()
        if scheduleName.lower().endswith(".csv"):
            # check if the schedule is already created
            if scheduleName.upper() in self.fileBasedSchedules.keys(): return "\n"
            
            # create schedule object based on file
            # find file name and use it as schedule name
            scheduleFileName = os.path.basename(scheduleName)
            scheduleObjectName = "_".join(scheduleFileName.split(".")[:-1])
            
            # copy schedule file into working dir
            scheduleNewAddress = os.path.join(self.workingDir, scheduleFileName)
            shutil.copyfile(scheduleName, scheduleNewAddress)
            
            # put them as key, value so I can find the new name when write schedule
            self.fileBasedSchedules[scheduleName.upper()] = scheduleObjectName
            
            scheduleStr = "Schedule:File,\n" + \
                          scheduleObjectName + ",\t!- Name\n" + \
                          "Fraction,\t!- Schedule Type Limits Name\n" + \
                          scheduleNewAddress + ",\t!- File Name\n" + \
                          "5,\t!- Column Number\n" + \
                          "3,\t!- Rows To Skip\n" + \
                          "8760,\t!- Hours of Data\n" + \
                          "Comma;\t!- Column Separator\n"
            
            return scheduleStr
            
        if scheduleName in sc.sticky ["honeybee_ScheduleLib"].keys():
            scheduleData = sc.sticky ["honeybee_ScheduleLib"][scheduleName]
        elif scheduleName in sc.sticky ["honeybee_ScheduleTypeLimitsLib"].keys():
            scheduleData = sc.sticky["honeybee_ScheduleTypeLimitsLib"][scheduleName]
    
        if scheduleData!=None:
            numberOfLayers = len(scheduleData.keys())
            scheduleStr = scheduleData[0] + ",\n"
            
            # add the name
            scheduleStr =  scheduleStr  + "  " +  scheduleName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers - 1:
                    scheduleStr =  scheduleStr + "  " + scheduleData[layer][0] + ",   !- " +  scheduleData[layer][1] + "\n"
                else:
                    scheduleStr =  scheduleStr + "  " + str(scheduleData[layer][0]) + ";   !- " +  scheduleData[layer][1] + "\n\n"
            return scheduleStr
    
    def requestSrfeio(self):
        return '\nOutput:Surfaces:List,\n' + \
        '\t' + 'Details;                 !- Report Type' + '\n'

class RunIDF(object):
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0'):
        
        workingDrive = workingDir[:2]
        
        if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
        else: shIdfFileName = idfFileName
        
        if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
        
        fullPath = workingDir + shIdfFileName
        
        folderName = workingDir.replace( (workingDrive + '\\'), '')
        batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
                '\\Epl-run ' + fullPath + ' ' + fullPath + ' idf ' + epwFileAddress + ' EP N nolimit N N 0 Y'
    
        batchFileAddress = fullPath +'.bat'
        batchfile = open(batchFileAddress, 'w')
        batchfile.write(batchStr)
        batchfile.close()
        
        #execute the batch file
        os.system(batchFileAddress)
        #os.system('C:\\honeybee\\runIt.bat')
            
    def readResults(self):
        pass


sc.sticky["honeybee_WriteIDF"] = WriteIDF
sc.sticky["honeybee_RunIDF"] = RunIDF


def main(north, epwFileAddress, EPParameters, analysisPeriod, HBZones, HBContext,
         simulationOutputs, writeIdf, runEnergyPlus, workingDir, idfFileName,
         meshSettings):
    # import the classes
    w = gh.GH_RuntimeMessageLevel.Warning
    
    if not sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        print "You should first let both Ladybug and Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1
    
    # make sure epw file address is correct
    if not epwFileAddress.endswith(epwFileAddress) or not os.path.isfile(epwFileAddress):
        msg = "Wrong weather file!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_scheduleLib = sc.sticky["honeybee_DefaultScheduleLib"]()
    hb_reEvaluateHBZones= sc.sticky["honeybee_reEvaluateHBZones"]
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
    hb_EPPar = sc.sticky["honeybee_EPParameters"]()
    
    northAngle, northVector = lb_preparation.angle2north(north)
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, True)
    conversionFac = lb_preparation.checkUnits()
    
    # check for folder and idf file address
    
    # if workingDir\
    ## check for idf file to be connected
    if idfFileName == None: idfFileName = 'unnamed.idf'
    elif idfFileName[-3:] != 'idf': idfFileName = idfFileName + '.idf'
    
    # make working directory
    if workingDir: workingDir = lb_preparation.removeBlankLight(workingDir)
    else: workingDir = "c:\\ladybug"
    
    workingDir = os.path.join(workingDir, idfFileName.split(".idf")[0], "EnergyPlus")
    
    workingDir = lb_preparation.makeWorkingDir(workingDir)
    
    # make sure the directory has been created
    if workingDir == -1: return -1
    workingDrive = workingDir[0:1]
        
    hb_writeIDF = sc.sticky["honeybee_WriteIDF"](workingDir)
    hb_runIDF = sc.sticky["honeybee_RunIDF"]()
    
    # call the objects from the lib
    thermalZonesPyClasses = hb_hive.callFromHoneybeeHive(HBZones)
    
    reEvaluate = hb_reEvaluateHBZones(thermalZonesPyClasses, meshSettings)
    reEvaluate.evaluateZones()
    
    idfFileFullName = workingDir + "\\" + idfFileName
    idfFile = open(idfFileFullName, "w")
    
    ################## HEADER ###################
    print "[1 of 7] Writing simulation parameters..."
    
    # Version,8.1;
    idfFile.write(hb_writeIDF.EPVersion())
    
    # Read simulation parameters
    timestep, shadowPar, solarDistribution, simulationControl, ddyFile = hb_EPPar.readEPParams(EPParameters)
    
    # Timestep,6;
    idfFile.write(hb_writeIDF.EPTimestep(timestep))
    
    # ShadowCalculation
    idfFile.write(hb_writeIDF.EPShadowCalculation(*shadowPar))
    
    # NumThread
    idfFile.write(hb_writeIDF.EPProgramControl())
    
    # Building
    EPBuilding = hb_writeIDF.EPBuilding(idfFileName, math.degrees(northAngle),
                                        'City', 0.04, 0.4, solarDistribution,
                                        maxWarmUpDays =25, minWarmUpDays = 6)
                    
    idfFile.write(EPBuilding)
    
    # HeatBalanceAlgorithm
    idfFile.write(hb_writeIDF.EPHeatBalanceAlgorithm())
    
    # SurfaceConvectionAlgorithm
    idfFile.write(hb_writeIDF.EPSurfaceConvectionAlgorithm())
    
    # Location
    idfFile.write(hb_writeIDF.EPSiteLocation(epwFileAddress))
    
    # simulationControl
    idfFile.write(hb_writeIDF.EPSimulationControl(*simulationControl))
    
    # runningPeriod
    idfFile.write(hb_writeIDF.EPRunPeriod('customRun', stDay, stMonth, endDay, endMonth))
    
    # for now I write all the type limits but it can be cleaner
    scheduleTypeLimits = sc.sticky["honeybee_ScheduleTypeLimitsLib"]["List"]
    for scheduleTypeLimit in scheduleTypeLimits:
        try: idfFile.write(hb_writeIDF.EPSCHStr(scheduleTypeLimit))
        except: pass
    
    # Geometry rules
    idfFile.write(hb_writeIDF.EPGeometryRules())
    
    # Shading Surfaces
    if HBContext and HBContext[0]!=None:
        print "[2 of 6] Writing context surfaces..."
        # call the objects from the lib
        shadingPyClasses = hb_hive.callFromHoneybeeHive(HBContext)
        for shading in shadingPyClasses:
            #print shading.name
            #print hb_writeIDF.EPShdSurface(shading)
            idfFile.write(hb_writeIDF.EPShdSurface(shading))
    else:
        print "[2 of 6] No context surfaces..."
        
        
    #################  BODY #####################
    print "[3 of 6] Writing geometry..."
    EPConstructionsCollection = []
    EPMaterialCollection = []
    EPScheduleCollection = []
    ZoneCollectionBasedOnSchAndLoads = {} # This will be used to create zoneLists
    
    # write idf file
    for zone in thermalZonesPyClasses:
        # Zone
        idfFile.write(hb_writeIDF.EPZone(zone))
        
        # get the schedule and loads for the zone
        schedules = zone.getCurrentSchedules(True)
        loads = zone.getCurrentLoads(True)
        
        # create a unique key based on schedules and loads
        # zones with similar keys will be grouped
        key = ",".join(schedules.values() + loads.values())
        if key not in ZoneCollectionBasedOnSchAndLoads.keys():
            ZoneCollectionBasedOnSchAndLoads[key] = []
        
        ZoneCollectionBasedOnSchAndLoads[key].append(zone)
        
        # collect unique schedules
        for schedule in schedules.values():
            if schedule.upper() not in EPScheduleCollection:
                EPScheduleCollection.append(schedule.upper())
                
        for srf in zone.surfaces:
            # check if there is an energyPlus material
            if srf.EPConstruction != None:
                srf.construction = srf.EPConstruction
            # else try to find the material based on bldg type and climate zone
            # the surface will use the default construction
            if not srf.construction.upper() in EPConstructionsCollection:
                EPConstructionsCollection.append(srf.construction.upper())
            
            # Surfaces
            idfFile.write(hb_writeIDF.EPZoneSurface(srf))
            
            if srf.hasChild:
                # check the construction
                # this should be moved inside the function later
                for childSrf in srf.childSrfs:
                    # check if there is an energyPlus material
                    if childSrf.EPConstruction != None:
                        childSrf.construction = childSrf.EPConstruction
                    # else try to find the material based on bldg type and climate zone
                    # I will apply this later
                    # the surface will use the default construction
                    if not childSrf.construction.upper() in EPConstructionsCollection:
                            EPConstructionsCollection.append(childSrf.construction.upper())
                    
                # write the glazing strings
                idfFile.write(hb_writeIDF.EPFenSurface(srf))
                # else: idfFile.write(hb_writeIDF.EPNonPlanarFenSurface(srf))
        
    ################ Construction #####################
    print "[4 of 6] Writing materials and constructions..."
    
    # Write constructions
    for cnstr in EPConstructionsCollection:
        constructionStr, materials = hb_writeIDF.EPConstructionStr(cnstr)
        if constructionStr:
            idfFile.write(constructionStr)
        
            for mat in materials:
                if not mat.upper() in EPMaterialCollection:
                    materialStr = hb_writeIDF.EPMaterialStr(mat.upper())
                    if materialStr:
                        idfFile.write(materialStr)
                        EPMaterialCollection.append(mat.upper())
        
    
    ################ BODYII #####################
    print "[5 of 7] Writing schedules..."
    
    # Write Schedules
    for schedule in EPScheduleCollection:
        scheduleValues, comments = hb_EPScheduleAUX.getScheduleDataByName(schedule, ghenv.Component)
        if comments == "csv":
            # create a new schedule object based on file
            idfFile.write(hb_writeIDF.EPSCHStr(schedule))
            
            # I need to also change the name of the schedule
            # when I write the objects! Maybe I should have added them
            # when I check for the zones so I can name them based on zone names
            pass
            
        elif scheduleValues!=None:
            idfFile.write(hb_writeIDF.EPSCHStr(schedule))
            
            if scheduleValues[0].lower() == "schedule:year":
                numOfWeeklySchedules = int((len(scheduleValues)-2)/5)
                
                for i in range(numOfWeeklySchedules):
                    weekDayScheduleName = scheduleValues[5 * i + 2]
                    if weekDayScheduleName not in EPScheduleCollection:
                            EPScheduleCollection.append(weekDayScheduleName)
                    
            # collect all the schedule items inside the schedule
            elif scheduleValues[0].lower() == "schedule:week:daily":
                for value in scheduleValues[1:]:
                    if value not in EPScheduleCollection:
                        EPScheduleCollection.append(value)
    
    print "[6 of 7] Writing loads and ideal air system..."
    listCount = 0
    listName = None
    
    idfFile.write(hb_writeIDF.writeHVACSched0())
    idfFile.write(hb_writeIDF.writeHVACSched1())
    idfFile.write(hb_writeIDF.writeHVACSched2())
    idfFile.write(hb_writeIDF.writeHVACSched3())
    idfFile.write(hb_writeIDF.writeHVACSched4())
    idfFile.write(hb_writeIDF.writeHVACSched5())
    
    
    for key, zones in ZoneCollectionBasedOnSchAndLoads.items():
        
        # removed for now as apparently openstudio import idf does not like lists!
        #if len(zones) > 1:
        #    listCount += 1 
        #    # create a zone list
        #    listName = "_".join([zones[0].bldgProgram, zones[0].zoneProgram, str(listCount)])
        #    
        #    idfFile.write(hb_writeIDF.EPZoneListStr(listName, zones))
        
        
        for zone in zones:
            #zone = zones[0]
            
            if listName!=None:
                for zone in zones:
                    idfFile.write(hb_writeIDF.writeThemostat(zone.name, zone))
                    idfFile.write(hb_writeIDF.writeSetpoint(zone, zone.name))
                    idfFile.write(hb_writeIDF.writeEquipConnect(zone.name, zone))
                    idfFile.write(hb_writeIDF.writeEquipList(zone.name, zone))
                    idfFile.write(hb_writeIDF.writeNodeList(zone.name, zone))
                    idfFile.write(hb_writeIDF.writeIdealAirSys(zone.name, zone))
            else:
                idfFile.write(hb_writeIDF.writeThemostat(zone.name, zone))
                idfFile.write(hb_writeIDF.writeSetpoint(zone, zone.name))
                idfFile.write(hb_writeIDF.writeEquipConnect(zone.name, zone))
                idfFile.write(hb_writeIDF.writeEquipList(zone.name, zone))
                idfFile.write(hb_writeIDF.writeNodeList(zone.name, zone))
                idfFile.write(hb_writeIDF.writeIdealAirSys(zone.name, zone))
            
            
            #This is the old HVAC Template.  It has been replaced with one that allows humidity control and adjusting of supply temperature.
            #   HAVC System
            #if listName!=None:
            #    HAVCTemplateName = listName + "_HVAC"
            #    for zone in zones:
            #        idfFile.write(hb_writeIDF.EPIdealAirSystem(zone, HAVCTemplateName))
            #    
            #else:
            #    HAVCTemplateName = zone.name + "_HVAC"
            #    idfFile.write(hb_writeIDF.EPIdealAirSystem(zone, HAVCTemplateName))
            
            #   Thermostat
            #idfFile.write(hb_writeIDF.EPHVACTemplate(HAVCTemplateName, zone))
            #            
            
            
            #   LOADS - INTERNAL LOADS + PLUG LOADS
            idfFile.write(hb_writeIDF.EPZoneElectricEquipment(zone, listName))
        
            #   PEOPLE
            idfFile.write(hb_writeIDF.EPZonePeople(zone, listName))
        
            #   LIGHTs
            idfFile.write(hb_writeIDF.EPZoneLights(zone, listName))
        
            #   INFILTRATION
            idfFile.write(hb_writeIDF.EPZoneInfiltration(zone, listName))
            
            # Specification Outdoor Air
            idfFile.write(hb_writeIDF.EPDesignSpecOA(zone))
        
    ################## FOOTER ###################
    # write output lines
    # request surface information in the eio file.
    idfFile.write(hb_writeIDF.requestSrfeio())
    # write the outputs requested by the user.
    if simulationOutputs:
        print "[7 of 7] Writing outputs..."
        idfFile.write('\n')
        for line in simulationOutputs:
            idfFile.write(line + '\n')
    else:
        print "[7 of 7] No outputs! You usually want to get some outputs when you run an analysis. Just saying..."
        
    idfFile.close()
    
    print "...\n... idf file is successfully written to : " + idfFileFullName + "\n"
    
    ######################## RUN ENERGYPLUS SIMULATION #######################
    resultFileFullName = None
    if runEnergyPlus:
        print "Analysis is running!..."
        # write the batch file
        hb_runIDF.writeBatchFile(workingDir, idfFileName, epwFileAddress)
        resultFileFullName = idfFileFullName.replace('.idf', '.csv')
        print "...\n...\n\nDone! Read below for errors and warnings:\n\n"
    else:
        print "Set runEnergyPlus to True!"
        
    return idfFileFullName, resultFileFullName 
        

if _writeIdf == True and _epwFile and _HBZones and _HBZones[0]!=None:
    
    result = main(north_, _epwFile, _energySimPar_, _analysisPeriod_, _HBZones,
                  HBContext_, simulationOutputs_, _writeIdf, runEnergyPlus_,
                  _workingDir_, _idfFileName_, meshSettings_)
    if result!= -1:
        idfFileAddress, resultFileAddress = result
        if runEnergyPlus_:
            try:
                errorFileFullName = idfFileAddress.replace('.idf', '.err')
                errFile = open(errorFileFullName, 'r')
                for line in errFile: print line
                errFile.close()
            except:
                pass
else:
    print "At least one of the mandatory inputs in missing."