# This component exports HBZones into an IDF file
# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to export HBZones into an IDF file, and run them through EnergyPlus.
_
The component outputs the report from the simulation, the file path of the IDF file, and the CSV result file from the EnergyPlus run.
-
Provided by Honeybee 0.0.56
    Args:
        north_: Input a vector to be used as a true North direction for the energy simulation or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _epwFile: An .epw file path on your system as a text string.
        _analysisPeriod_: An optional analysis period from the Ladybug_Analysis Period component.  If no Analysis period is given, the energy simulation will be run for the enitre year.
        +++++++++++++++: ...
        _energySimPar_: Optional Energy Simulation Parameters from the "Honeybee_Energy Simulation Par" component.  If no value is connected here, the simulation will run with the following parameters:
            1 - 6 timeSteps per hour
            2 - A shadow calculation that averages over multiple days (as opposed to running it for each timeStep)
            3 - A shadow calculation frequency of 30 (meaning that the shadow calulation is averaged over every 30 days)
            4 - A maximum of 3000 points used in the shadow calculation. (This may need to be higher if you have a lot of detailed context geometry)
            5 - An colar energy calculation that includes both interior and exterior light reflections.
            6 - A simulation including a zone sizing calculation, a system sizing calculation, a plat sizing calculation, and a full run of the energy use ofver the analysis period.  The simulation is not run for the sizing period by default.
            7 - A system sizing period that runs from the extreme periods of the weather file and not a ddy file.
            8 - City terrian.
        +++++++++++++++: ...
        _HBZones: The HBZones that you wish to write into an IDF and/or run through EnergyPlus.  These can be from any of the components that output HBZones.
        HBContext_: Optional HBContext geometry from the "Honeybee_EP Context Surfaces." component or Honeybee PV gen component.
        HB_generators: Connect the output HB_generatorsytem from the Honeybee_generationsystem component here to model EnergyPlus Photovoltaic and Wind generator systems in this simulation.
        simulationOutputs_: A list of the outputs that you would like EnergyPlus to write into the result CSV file.  This can be any set of any outputs that you would like from EnergyPlus, writen as a list of text that will be written into the IDF.  It is recommended that, if you are not expereinced with writing EnergyPlus outputs, you should use the "Honeybee_Write EP Result Parameters" component to request certain types of common outputs.  If no value is input here, this component will automatically request outputs of heating, cooling, lighting, and equipment energy use.
        +++++++++++++++: ...
        _writeIdf: Set to "True" to have the component take your HBZones and other inputs and write them into an IDF file.  The file path of the resulting file will appear in the idfFileAddress output of this component.  Note that only setting this to "True" and not setting the output below to "True" will not automatically run the IDF through EnergyPlus for you.
        runEnergyPlus_: Set to "True" to have the component run your IDF through EnergyPlus once it has finished writing it.  This will ensure that a CSV result file appears in the resultFileAddress output.
        +++++++++++++++: ...
        _workingDir_: An optional working directory to a folder on your system, into which your IDF and result files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _idfFileName_: Optional text which will be used to name your IDF and result files.  Change this to aviod over-writing results of previous energy simulations.
        +++++++++++++++: ...
        meshSettings_: Optional mesh settings for your geometry from any one of the native Grasshopper mesh setting components.  These will be used to change the meshing of curved surfaces before they are run through EnergyPlus (note that meshing of curved surfaces is done since Energyplus is not able to calculate heat flow through non-planar surfaces).  Default Grasshopper meshing is used if nothing is input here but you may want to decrease your calculation time by changing it to Coarse or increase your curvature definition (and calculation time) by making it finer.
        additionalStrings_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.  You can input additional text strings here that you would like written into the IDF.  The strings input here should be complete EnergyPlus objects that are correctly formatted.  You can input as many objects as you like in a list.  This input can be used to write objects into the IDF that are not currently supported by Honeybee.
    Returns:
        report: Check here to see a report of the EnergyPlus run, including errors.
        idfFileAddress: The file path of the IDF file that has been generated on your machine.
        resultFileAddress: The file path of the CSV result file that has been generated on your machine.  This only happens when you set "runEnergyPlus_" to "True."
"""
ghenv.Component.Name = "Honeybee_ Run Energy Simulation"
ghenv.Component.NickName = 'runEnergySimulation'
ghenv.Component.Message = 'VER 0.0.56\nAPR_18_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_28_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import System
import Grasshopper.Kernel as gh
import math
import shutil

rc.Runtime.HostUtils.DisplayOleAlerts(False)


class WriteIDF(object):
    
    # Add all HBcontext surfaces from both HBContext_ and HB generator here so that if user connects the same
    # HBcontext surfaces to both HB generator and HBcontext duplicate surfaces will be detected and an error thrown.
    
    checksurfaceduplicate = []
    zonesurfaces = []
    # Add the ID of all batteries from HB generator systems here to check for duplicate batteries.
    checkbatteryduplicate = []
    # Add the ID of all inverters from HB generator systems here to check for duplicate inverters.
    checkinverterduplicate = []
    # Add the cost of grid electcity for all the different 
    gridelectcost = []
    
    # Create a list of tuples containing each item and its cost - to conduct financial analysis 
    
    financialdata = []
    
    def __init__(self, workingDir):
        self.fileBasedSchedules = {}
        self.workingDir = workingDir
        
    def EPZone(self, zone):
        
        zoneStr = '\nZone,\n' + \
                '\t' + zone.name + ',\n' + \
                '\t' + `zone.north` + ',\t!-Direction of Relative North {deg}\n' + \
                '\t' + `zone.origin.X` + ',\t!- X Origin {m}\n' + \
                '\t' + `zone.origin.Y` + ',\t!- Y Origin {m}\n' + \
                '\t' + `zone.origin.Z` + ',\t!- Z Origin {m}\n'
                
        try:
            if zone.isPlenum:
                return zoneStr + \
                '\t1,\t!- Type\n' + \
                '\t,\t!- Multiplier\n' + \
                '\t,\t!- Ceiling Height\n' + \
                '\t,\t!- Volume\n' + \
                '\t,\t!- Floor Area\n' + \
                '\t,\t!- Zone Inside Convection Algorithm\n' + \
                '\t,\t!- Zone Outside Convection Algorithm\n' + \
                '\tNo;\t!- Part of Total Floor Area\n'                
            else:
                return zoneStr + '\t1;\t!- Type\n'
        except:
            #older versions
            return zoneStr + '\t1;\t!- Type\n'
            
    def EPZoneSurface (self, surface):
        
        coordinates = surface.coordinates
        
        checked, coordinates= self.checkCoordinates(coordinates)
        
        if int(surface.type) == 4: surface.type = 0
        
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

        scheduleName = surface.TransmittanceSCH
        if scheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            scheduleName = self.fileBasedSchedules[scheduleName.upper()]
        #print coordinatesList
        fullString = ''
        
        for count, coordinates in enumerate(coordinatesList):

            #print surface.name + " ASS NAME HERE"
            str_1 = '\nShading:Building:Detailed,\n' + \
                    '\t' + surface.name + '_' + `count` + ',\t!- Name\n' + \
                    '\t' + scheduleName + ',\t!- Transmittance Schedule Name\n' + \
                    '\t' + `len(coordinates)` + ',\t!- Number of Vertices\n'    

            str_2 = '\t';
            for ptCount, pt in enumerate(coordinates):
                if ptCount < len (coordinates) - 1:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ',\n\t'
                else:
                    str_2 = str_2 + `pt.X` + ',\n\t' + `pt.Y` + ',\n\t' + `pt.Z` + ';\n\n'
            
            fullString = fullString + str_1 + str_2
        
        return fullString
    
    def EPInternalMass(self, zone, massName, srfArea, constructionName):
        internalMassStr = '\nInternalMass,\n' + \
                    '\t' + massName + ',\t!- Name\n' + \
                    '\t' + constructionName + ',\t!- Construction Name\n' + \
                    '\t' + zone.name + ',\t!- Zone Name\n' + \
                    '\t' + str(srfArea) + ';\t!- Surface Area\n' 
        
        return internalMassStr
    
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
    
    
    def EPHVACTemplate( self, name, zone):
        if zone.isConditioned:
            heatingSetPtSchedule = zone.heatingSetPtSchedule
            coolingSetPtSchedule = zone.coolingSetPtSchedule
            
            if heatingSetPtSchedule.lower().endswith(".csv"):
                # find filebased schedule name
                heatingSetPtSchedule = self.fileBasedSchedules[heatingSetPtSchedule.upper()]            
                
            if coolingSetPtSchedule.lower().endswith(".csv"):
                # find filebased schedule name
                coolingSetPtSchedule = self.fileBasedSchedules[coolingSetPtSchedule.upper()]
                
            return '\nHVACTemplate:Thermostat,\n' + \
                    '\t' + name + ',                    !- Name\n' + \
                    '\t' + heatingSetPtSchedule + ',          !- Heating Setpoint Schedule Name\n' + \
                    '\t' + `zone.heatingSetPt` + ', !- Constant Heating Setpoint {C}\n' + \
                    '\t' + coolingSetPtSchedule + ',          !- Cooling Setpoint Schedule Name\n' + \
                    '\t' + `zone.coolingSetPt` + '; !- Constant Cooling Setpoint {C}\n'
        else:
            return "\n"
            
    def EPIdealAirSystem(self, zone, thermostatName):
        if zone.isConditioned:
            
            if zone.coolSupplyAirTemp == "": coolSupply = "13"
            else: coolSupply = zone.coolSupplyAirTemp
            if zone.heatSupplyAirTemp == "": heatSupply = "50"
            else: heatSupply = zone.heatSupplyAirTemp
            if zone.coolingCapacity == "": coolLimit = "NoLimit"
            else: coolLimit = 'LimitCapacity'
            if zone.heatingCapacity == "": heatLimit = "NoLimit"
            else: heatLimit = 'LimitCapacity'
            if zone.HVACAvailabilitySched != "ALWAYS ON":
                scheduleFileName = os.path.basename(zone.HVACAvailabilitySched)
                scheduleObjectName = "_".join(scheduleFileName.split(".")[:-1])
            else: scheduleObjectName = ""
            
            
            if zone.airSideEconomizer == 'DifferentialDryBulb':
                if coolLimit == "NoLimit" or coolLimit == "LimitFlowRate": coolLimit = 'LimitFlowRate'
                else: coolLimit = 'LimitFlowRateAndCapacity'
                maxAirFlowRate = 'autosize'
            else: maxAirFlowRate = ''
            
            if zone.heatRecovery == 'Sensible' and zone.heatRecoveryEffectiveness == '':
                zone.heatRecoveryEffectiveness = "0.7"
            
            flowPerPerson =  str(zone.ventilationPerPerson)
            flowPerZoneArea = str(zone.ventilationPerArea)
            
            
            return '\nHVACTemplate:Zone:IdealLoadsAirSystem,\n' + \
                '\t' + zone.name + ',\t!- Zone Name\n' + \
                '\t' + thermostatName + ',\t!- Template Thermostat Name\n' + \
                '\t' + scheduleObjectName + ',  !- Availability Schedule Name\n' + \
                '\t' + heatSupply + ',  !- Heating Supply Air Temp {C}\n' + \
                '\t' + coolSupply + ',  !- Cooling Supply Air Temp {C}\n' + \
                '\t' + ',  !- Max Heating Supply Air Humidity Ratio {kg-H2O/kg-air}\n' + \
                '\t' + ',  !- Min Cooling Supply Air Humidity Ratio {kg-H2O/kg-air}\n' + \
                '\t' + heatLimit + ',  !- Heating Limit\n' + \
                '\t' + ',  !- Maximum Heating Air Flow Rate {m3/s}\n' + \
                '\t' + zone.heatingCapacity + ',  !- Maximum Sensible Heat Capacity\n' + \
                '\t' + coolLimit + ',  !- Cooling Limit\n' + \
                '\t' + maxAirFlowRate + ',  !- Maximum Cooling Air Flow Rate {m3/s}\n' + \
                '\t' + zone.coolingCapacity + ',  !- Maximum Total Cooling Capacity\n' + \
                '\t' + ',  !- Heating Availability Schedule\n' + \
                '\t' + ',  !- Cooling Availability Schedule\n' + \
                '\t' + '' + ',  !- Dehumidification Control Type\n' + \
                '\t' + ',  !- Cooling Sensible Heat Ratio\n' + \
                '\t' + '' + ',  !- Dehumidification Setpoint\n' + \
                '\t' + 'None' + ',  !- Humidification Control Type\n' + \
                '\t' + '' + ',  !- Humidification Setpoint\n' + \
                '\t' + zone.outdoorAirReq + ',  !- Outdoor Air Method\n' + \
                '\t' + flowPerPerson + ',  !- Outdoor Air Flow Rate Per Person\n' + \
                '\t' + flowPerZoneArea + ',  !- Outdoor Air Flow Rate Per Floor Zone Area\n' + \
                '\t' + ',  !- Outdoor Air Flow Rate Per Zone\n' + \
                '\t' + '' + ',  !- Design Specification Outdoor Air Object Name\n' + \
                '\t' + '' + ',  !- Demand Controlled Ventilation Type\n' + \
                '\t' + zone.airSideEconomizer + ',  !- Outdoor Air Economizer Type\n' + \
                '\t' + zone.heatRecovery + ',  !- Heat Recovery Type\n' + \
                '\t' + zone.heatRecoveryEffectiveness + ',  !- Sensible Heat Recovery Effectiveness\n' + \
                '\t' + ';  !- Latent Heat Recovery Effectiveness\n'
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
    
    def EPSizingPeriod(self, weatherFilePeriod):
        sizingString = "\nSizingPeriod:WeatherFileConditionType,\n" + \
            '\t' + 'ExtremeSizing'+ weatherFilePeriod + ',\n' + \
            '\t' + weatherFilePeriod + ',    !Period Selection\n' + \
            '\t' + 'Monday' + ',   !Day of Week for Start Day\n' + \
            '\t' + 'Yes' + ', !Use Weather File Daylight Davings Period\n' + \
            '\t' + 'Yes' + ';   !Use WeatherFile Rain and Snow Indicators\n'
        return sizingString
    
    def EPSizingPeriodMonth(self, designMonth):
        sizingString = "\nSizingPeriod:WeatherFileDays,\n" + \
            '\t' + 'ExtremeSizing'+ str(designMonth) + ',\n' + \
            '\t' + str(designMonth) + ',    !Begin Month\n' + \
            '\t' + '1' + ',   !Begin Day of Month\n' + \
            '\t' + str(designMonth) + ', !End Month\n' + \
            '\t' + '28' + ', !End Day of Month\n' + \
            '\t' + '' + ', !Day of Week\n' + \
            '\t' + '' + ', !Use WeatherFile Daylight Savings Period\n' + \
            '\t' + '' + ';   !Use WeatherFile Rain and Snow Indicators\n'
        return sizingString
    
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

    def EPGeometryRules(self, stVertexPos = 'LowerLeftCorner', direction = 'CounterClockWise', coordinateSystem = 'Relative'):
        return '\nGlobalGeometryRules,\n' + \
                '\t' + stVertexPos + ',         !- Starting Vertex Position\n' + \
                '\t' + direction + ',        !- Vertex Entry Direction\n' + \
                '\t' + coordinateSystem + ';                !- Coordinate System\n'

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
        if scheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            scheduleName = self.fileBasedSchedules[scheduleName.upper()]
        
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
    
    def EPZoneAirMixing(self, zone, zoneMixName, mixFlowRate, objCount):
        return '\nZoneMixing,\n' + \
                '\t' + zone.name + zoneMixName + 'AirMix' + str(objCount) + ',  !- Name\n' + \
                '\t' + zone.name + ',  !- Zone Name\n' + \
                '\t' + 'ALWAYS ON' + ',  !- Schedule Name\n' + \
                '\t' + 'Flow/Zone' + ',  !- Design Flow Rate Calculation Method\n' + \
                '\t' + str(mixFlowRate) + ',   !- Design Flow Rate {m3/s}\n' + \
                '\t' + ',  !- Flow per Zone Floor Area {m3/s-m2}\n' + \
                '\t' + ', !- Flow per Exterior Surface Area {m3/s-m2}\n' + \
                '\t' + ',    !- Air Changes per Hour\n' + \
                '\t' + zoneMixName  + ',     !- Source Zone Name\n' + \
                '\t' + '0'  + ',     !- Delta Temperature\n' + \
                '\t,                        !- Delta Temperature Schedule Name\n' + \
                '\t,                        !- Minimum Zone Temperature Schedule Name\n' + \
                '\t,                        !- Maximum Zone Temperature Schedule Name\n' + \
                '\t,                        !- Minimum Source Zone Temperature Schedule Name\n' + \
                '\t,                        !- Maximum Source Zone Temperature Schedule Name\n' + \
                '\t,                        !- Minimum Outdoor Temperature Schedule Name\n' + \
                '\t;                        !- Maximum Outdoor Temperature Schedule Name\n'
    
    def EPNatVentSimple(self, zone, natVentCount):
        if zone.natVentSchedule[natVentCount] == None: natVentSched = 'ALWAYS ON'
        elif zone.natVentSchedule[natVentCount].upper().endswith('CSV'):
            natVentSchedFileName = os.path.basename(zone.natVentSchedule[natVentCount])
            natVentSched = "_".join(natVentSchedFileName.split(".")[:-1])
        else: natVentSched = zone.natVentSchedule[natVentCount]
        
        return '\nZoneVentilation:WindandStackOpenArea,\n' + \
                '\t' + zone.name + 'NatVent' + str(natVentCount) + ',  !- Name\n' + \
                '\t' + zone.name + ',  !- Zone Name\n' + \
                '\t' + str(zone.windowOpeningArea[natVentCount]) + ',  !- Opening Area\n' + \
                '\t' + natVentSched + ',  !- Nat Vent Schedule\n' + \
                '\t' + str(zone.natVentWindDischarge[natVentCount]) + ',   !- Opening Effectiveness\n' + \
                '\t' + str(zone.windowAngle[natVentCount]) + ',  !- Effective Angle\n' + \
                '\t' + str(zone.windowHeightDiff[natVentCount]) + ', !- Height Difference\n' + \
                '\t' + str(zone.natVentStackDischarge[natVentCount]) + ',    !- Discharge Coefficient for Opening\n' + \
                '\t' + str(zone.natVentMinIndoorTemp[natVentCount])  + ',     !- Minimum Indoor Temperature\n' + \
                '\t' + ',     !- Minimum Indoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxIndoorTemp[natVentCount])  + ',     !- Maximum Indoor Temperature\n' + \
                '\t' + ',     !- Maximum Indoor Temperature Shcedule Name\n' + \
                '\t' + '-100'  + ',     !- Delta Temperature\n' + \
                '\t' + ',     !- Delta Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMinOutdoorTemp[natVentCount])  + ',     !- Minimum Outdoor Temperature\n' + \
                '\t' + ',     !- Minimum Outdoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxOutdoorTemp[natVentCount])  + ',     !- Maximum Outdoor Temperature\n' + \
                '\t' + ',     !- Maximum Outdoor Temperature Shcedule Name\n' + \
                '\t' + '40' + ';                        !- Maximum Wind Speed\n'
    
    def EPNatVentFan(self, zone, natVentCount):
        if zone.natVentSchedule[natVentCount] == None: natVentSched = 'ALWAYS ON'
        else:
            natVentSchedFileName = os.path.basename(zone.natVentSchedule[natVentCount])
            natVentSched = "_".join(natVentSchedFileName.split(".")[:-1])
        
        return '\nZoneVentilation:DesignFlowRate,\n' + \
                '\t' + zone.name + 'NatVent' + str(natVentCount) + ',  !- Name\n' + \
                '\t' + zone.name + ',  !- Zone Name\n' + \
                '\t' + natVentSched + ',  !- Nat Vent Schedule\n' + \
                '\t' + 'Flow/Zone' + ',  !- Design Flow Rate Calculation Method\n' + \
                '\t' + str(zone.fanFlow[natVentCount]) + ',   !- Design flow rate m3/s\n' + \
                '\t' + ',  !- Design flow rate per floor area\n' + \
                '\t' + ', !- Flow Rate per person\n' + \
                '\t' + ',    !- Air chancges per hour\n' + \
                '\t' + 'Intake' + ',  !- Ventilation Type\n' + \
                '\t' + str(zone.FanPressure[natVentCount]) + ',   !- Fan Pressure Rise (Pa)\n' + \
                '\t' + str(zone.FanEfficiency[natVentCount]) + ',   !- Fan Efficiency (Pa)\n' + \
                '\t' + '1' + ',  !- Constant Term Coefficient\n' + \
                '\t' + '0' + ',  !- Temperature Term Coefficient\n' + \
                '\t' + '0' + ',  !- Velocity Term Coefficient\n' + \
                '\t' + '0' + ',  !- Velocity Squared Term Coefficient\n' + \
                '\t' + str(zone.natVentMinIndoorTemp[natVentCount])  + ',     !- Minimum Indoor Temperature\n' + \
                '\t' + ',     !- Minimum Indoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxIndoorTemp[natVentCount])  + ',     !- Maximum Indoor Temperature\n' + \
                '\t' + ',     !- Maximum Indoor Temperature Shcedule Name\n' + \
                '\t' + '-100'  + ',     !- Delta Temperature\n' + \
                '\t' + ',     !- Delta Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMinOutdoorTemp[natVentCount])  + ',     !- Minimum Outdoor Temperature\n' + \
                '\t' + ',     !- Minimum Outdoor Temperature Shcedule Name\n' + \
                '\t' + str(zone.natVentMaxOutdoorTemp[natVentCount])  + ',     !- Maximum Outdoor Temperature\n' + \
                '\t' + ',     !- Maximum Outdoor Temperature Shcedule Name\n' + \
                '\t' + '40' + ';                        !- Maximum Wind Speed\n'
    
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
        if scheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            scheduleName = self.fileBasedSchedules[scheduleName.upper()]
            
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
        if scheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            scheduleName = self.fileBasedSchedules[scheduleName.upper()]
        
        activityScheduleName = zone.occupancyActivitySch
        if activityScheduleName.lower().endswith(".csv"):
            # find filebased schedule name
            activityScheduleName = self.fileBasedSchedules[activityScheduleName.upper()]
        
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
        materialName = materialName.strip()
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
        else:
            warning = "Failed to find " + materialName + " in library."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return None
       
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
            warning = "Failed to find " + constructionName + " in library."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return None, None
            
    def EPSCHStr(self, scheduleName):
        scheduleData = None
        scheduleName= scheduleName.upper()
        if scheduleName.lower().endswith(".csv"):
            # check if the schedule is already created
            if scheduleName.upper() in self.fileBasedSchedules.keys(): return "\n"
            
            # set up default values
            schTypeLimitStr = "\n"
            schTypeLimitName = "Fraction"
            numOfHours = 8760
            
            # create schedule object based on file
            # find file name and use it as schedule name
            scheduleFileName = os.path.basename(scheduleName)
            scheduleObjectName = "_".join(scheduleFileName.split(".")[:-1])
            
            # copy schedule file into working dir
            scheduleNewAddress = os.path.join(self.workingDir, scheduleFileName)
            shutil.copyfile(scheduleName, scheduleNewAddress)
            
            # put them as key, value so I can find the new name when write schedule
            self.fileBasedSchedules[scheduleName.upper()] = scheduleObjectName
            
            # get the inputs if the schedule is generated by Honeybee
            with open(scheduleName, "r") as schFile:
                for lineCount, line in enumerate(schFile):
                    if lineCount == 3: break
                    elif lineCount == 0:
                        # try to collect information related to type limit
                        lineSeg = line.split(",")
                        if not lineSeg[0].startswith("Honeybee"): break
                        lowerLimit, upperLimit, numericType, unitType = lineSeg[1:5]
                        
                        # prepare the schedulTypeLimitObject
                        schTypeLimitName = os.path.basename(scheduleName).lower(). \
                                           replace(".", "").split("csv")[0] + "TypeLimit"
                        
                        schTypeLimitStr = "ScheduleTypeLimits,\t!Schedule Type\n" + \
                                          schTypeLimitName + ",\t! Name\n" + \
                                          lowerLimit.strip() + ",\t!- Lower Limit Value\n" + \
                                          upperLimit.strip() + ",\t!- Upper Limit Value\n" + \
                                          numericType.strip() + ",\t!- Numeric Type\n" + \
                                          unitType.strip() + ";\t!- Unit Type\n\n"
                    elif lineCount == 2:
                        # check timestep
                        try: numOfHours *= int(line.split(",")[0])
                        except: pass
            
            
            scheduleStr = schTypeLimitStr + \
                          "Schedule:File,\n" + \
                          scheduleObjectName + ",\t!- Name\n" + \
                          schTypeLimitName + ",\t!- Schedule Type Limits Name\n" + \
                          scheduleNewAddress + ",\t!- File Name\n" + \
                          "5,\t!- Column Number\n" + \
                          "4,\t!- Rows To Skip\n" + \
                          str(int(numOfHours)) + ",\t!- Hours of Data\n" + \
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
    
    def requestVarDict(self):
        return '\nOutput:VariableDictionary,\n' + \
        '\t' + 'regular;                 !- Key Field' + '\n'
        
    def EarthTube(self,zone):
    
        return '\nZoneEarthtube,\n' + \
            '\t' + zone.name + ',\t!- Zone Name\n' + \
            '\t' + str(zone.ETschedule) + ',\t!- Schedule Name\n'+\
            '\t' + str(zone.design_flow_rate) + ',\t!- Design Flow Rate {m3/s}\n'+\
            '\t' + str(zone.mincooltemp) + ',\t!- Minimum Zone Temperature when Cooling {C}\n'+\
            '\t' + str(zone.maxheatingtemp) + ',\t!- Maximum Zone Temperature when Heating {C}\n'+\
            '\t' + str(zone.delta_temp) + ',\t!- Delta Temperature {deltaC}\n'+\
            '\t' + str(zone.et_type) + ',\t!- Earthtube Type\n'+\
            '\t' + str(zone.fanprise) + ',\t!- Fan Pressure Rise {Pa}\n'+\
            '\t' + str(zone.efficiency) + ',\t!- Fan Total Efficiency\n'+\
            '\t' + str(zone.piperadius) + ',\t!- Pipe Radius {m}\n'+\
            '\t' + str(zone.thick) + ',\t!- Pipe Thickness {m}\n'+\
            '\t' + str(zone.length) + ',\t!- Pipe Length {m}\n'+\
            '\t' + str(zone.thermal_k) + ',\t!- Pipe Thermal Conductivity {W/m-K}\n'+\
            '\t' + str(zone.pipedepth) + ',\t!- Pipe Depth Under Ground Surface {m}\n'+\
            '\t' + str(zone.soil_con) + ',\t!- Soil Condition\n'+\
            '\t' + str(zone.soil_avannual) +',\t!- Average Soil Surface Temperature {C}\n'+\
            '\t' + str(zone.soil_amplitude) + ',\t!- Amplitude of Soil Surface Temperature {C}\n'+\
            '\t' + str(zone.soil_phaseconstant) + ',\t!- Phase Constant of Soil Surface Temperature {days}\n'+\
            '\t' + zone.termflow + ',\t!- Constant Term Flow Coefficient\n'+\
            '\t' + zone.tempflowco + ',\t!- Temperature Term Flow Coefficient\n'+\
            '\t' + zone.veltermflow  + ',\t!- Velocity Term Flow Coefficient\n'+\
            '\t' + zone.velsquflow  + ';\t!- Velocity Squared Term Flow Coefficient\n'
            
    def write_PVgen(self,PVgen):
    
        return '\nGenerator:Photovoltaic,\n' + \
            '\t' + str(PVgen.name) + ',\t!- Name\n' + \
            '\t' + str(PVgen.surfacename) + ',\t!- Surface Name\n'+\
            '\t' + str(PVgen.performancetype) + ',\t!- Photovoltaic Performance Object Type\n'+\
            '\t' + str(PVgen.performancename) + ',\t!- Module Performance Name\n'+\
            '\t' + str(PVgen.integrationmode) + ',\t!- Heat Transfer Integration Mode\n'+\
            '\t' + str(PVgen.NOparallel) + ',\t!- Number of Series Strings in Parallel {dimensionless}\n'+\
            '\t' + str(PVgen.NOseries) + ';\t!- Number of Modules in Series {dimensionless}\n'
    
    
    def write_PVgenperformanceobject(self,PVgen):
        
        return '\nPhotovoltaicPerformance:Simple,\n' + \
            '\t' + str(PVgen.namePVperformobject) + ',\t!- Name\n' + \
            '\t' + str(PVgen.surfaceareacells) + ',\t!- Fraction of Surface Area with Active Solar Cells {dimensionless}\n'+\
            '\t' + str(PVgen.cellefficiencyinputmode) + ',\t!- Conversion Efficiency Input Mode\n'+\
            '\t' + str(PVgen.efficiency) + ',\t!- Value for Cell Efficiency if Fixed\n'+\
            '\t' + str(PVgen.schedule) + ';\t!- Efficiency Schedule Name\n'
            
    def simple_inverter(self,inverter):
        
        return '\nElectricLoadCenter:Inverter:Simple,\n' + \
            '\t' + str(inverter.name) + ',\t!- Name\n' + \
            '\t' + "ALWAYS ON" + ',\t!- Availability Schedule Name\n' + \
            '\t' + str(inverter.zone) + ',\t!- Zone Name\n' + \
            '\t' + "0.3" + ',\t!- Radiative Fraction\n' + \
            '\t' + str(inverter.efficiency) + ';\t!- Inverter Efficiency\n'
    
    def battery_simple(self,battery):
        
        return '\nElectricLoadCenter:Storage:Simple,\n' + \
            '\t' + str(battery.name ) + ',\t!- Name\n' + \
            '\t' + "ALWAYS ON" + ',\t!- Availability Schedule Name\n' + \
            '\t' + str(battery.zonename) + ',\t!- Zone Name\n' + \
            '\t' + "0.3" + ',\t!- Radiative Fraction for Zone Heat Gains\n' + \
            '\t' + str(battery.chargingefficiency) + ',\t!- Nominal Energetic Efficiency for Charging\n'+ \
            '\t' + str(battery.dischargingeffciency) + ',\t!- Nominal Discharging Energetic Efficiency\n'+ \
            '\t' + str(battery.batterycap ) + ',\t!- Maximum Storage Capacity {J}\n'+ \
            '\t' + str(battery.maxdischarge) + ',\t!- Maximum Power for Discharging {W}\n'+ \
            '\t' + str(battery.maxcharge) + ',\t!- Maximum Power for Charging {W}\n'+ \
            '\t' + str(battery.initalcharge) + ';\t!- Initial State of Charge {J}\n'
            
    def wind_generator(self,windgenerator):
        
        def powercoefficients(windgenerator):
            if windgenerator.powercoefficients == None:
                    
                return '\t' + ''+',\t!- Power Coefficient C1\n' + \
                    '\t' + ''+',\t!- Power Coefficient C2\n' + \
                    '\t' + ''+',\t!- Power Coefficient C3\n' + \
                    '\t' + ''+',\t!- Power Coefficient C4\n' + \
                    '\t' + ''+',\t!- Power Coefficient C5\n' + \
                    '\t' + ''+';\t!- Power Coefficient C6\n'
            else:
                
                powercoefficients = []
                
                for count,powercoefficient in enumerate(windgenerator.powercoefficients):
                    
                    if count == 5: # Last power coefficient
                        powercoefficients.append('\t' + str(powercoefficient)+';\t!- Power Coefficient C'+str(count+1)+'\n')
                    else:
                        powercoefficients.append('\t' + str(powercoefficient)+',\t!- Power Coefficient C'+str(count+1)+'\n')
                return ''.join(powercoefficients)
    
        
        return '\nGenerator:WindTurbine,\n' + \
            '\t' + str(windgenerator.name)+',\t!- Name\n' + \
            '\t' + 'Always On'+',\t!- Availability Schedule Name\n' + \
            '\t' + str(windgenerator.rotortype)+',\t!- Rotor Type\n' + \
            '\t' + str(windgenerator.powercontrol)+',\t!- Power Control\n' + \
            '\t' + str(windgenerator.rotorspeed)+',\t!- Rated Rotor Speed {rev/min}\n' + \
            '\t' + str(windgenerator.rotor_diameter)+',\t!- Rotor Diameter {m}\n' + \
            '\t' + str(windgenerator.overall_height)+',\t!- Overall Height {m}\n' + \
            '\t' + str(windgenerator.numblades)+',\t!- Number of Blades\n' + \
            '\t' + str(windgenerator.powerout)+',\t!- Rated Power {W}\n' + \
            '\t' + str(windgenerator.rated_wind_speed)+',\t!- Rated Wind Speed {m/s}\n' + \
            '\t' + str(windgenerator.cut_in_windspeed)+',\t!- Cut In Wind Speed {m/s}\n' + \
            '\t' + str(windgenerator.cut_out_windspeed)+',\t!- Cut Out Wind Speed {m/s}\n' + \
            '\t' + str(windgenerator.overall_turbine_n)+',\t!- Fraction system Efficiency\n' + \
            '\t' + str(windgenerator.max_tip_speed_ratio)+',\t!- Maximum Tip Speed Ratio\n' + \
            '\t' + str(windgenerator.max_power_coefficient)+',\t!- Maximum Power Coefficient\n' + \
            '\t' + str(windgenerator.local_av_windspeed)+',\t!- Annual Local Average Wind Speed {m/s}\n' + \
            '\t' + str(windgenerator.height_local_metrological_station)+',\t!- Height for Local Average Wind Speed {m}\n' + \
            '\t' + ''+',\t!- Blade Chord Area {m2}\n' + \
            '\t' + ''+',\t!- Blade Drag Coefficient\n' + \
            '\t' + ''+',\t!- Blade Lift Coefficient\n'+\
            powercoefficients(windgenerator)
            

    def writegeneratlorlist(self,genlistname,generators):
        
        def generatorinfo(generator,generatornumber):
            
            return '\t'+str(generator.name)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Name\n'+ \
                '\t'+str(generator.type)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Object Type\n'+ \
                '\t'+str(generator.powerout)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Rated Electric Power Output {W}\n'+ \
                '\t'+'Always On,               !- Generator 1 Availability Schedule Name\n'+ \
                '\t'+',                        !- Generator 1 Rated Thermal to Electrical Power Ratio\n'
        
        def generatorinfofinal(generator,generatornumber):
            
            return '\t'+str(generator.name)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Name\n'+ \
                '\t'+str(generator.type)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Object Type\n'+ \
                '\t'+str(generator.powerout)+ ',\t!- Generator ' + str(generatornumber) + ' '+'Rated Electric Power Output {W}\n'+ \
                '\t'+'Always On,               !- Generator 1 Availability Schedule Name\n'+ \
                '\t'+';                        !- Generator 1 Rated Thermal to Electrical Power Ratio\n'
        
            # XXX change above in future so can handle schedules and thermal to electrical power ratio
            
        generatornumber = 0
        
        generatorlist = []
        
        for count,generator in enumerate(generators):
               
            generatornumber = generatornumber+1
            
            if count == (len(generators)-1): # If last generator in the generaor list need  
            
                generatorlist.append(generatorinfofinal(generator,generatornumber))
            
            else:
                generatorlist.append(generatorinfo(generator,generatornumber))
            
        return '\nElectricLoadCenter:Generators,\n' + \
            '\t' + str(genlistname) + ',\t!- Name\n' + \
            ''.join(generatorlist)
            
    def writeloadcenterdistribution(self,distribution_name,HBsystemgenerator_name,operationscheme,demandlimit,trackschedule,trackmeterschedule,busstype,inverterobject,elecstorageobject):
        
        #print inverterobject is None
        if demandlimit == None:
            demandlimit = ''
        if trackschedule == None:
            demandlimit = 'Always On'
        if trackmeterschedule == None:
            trackmeterschedule = ''
        if elecstorageobject == None:
            elecstorageobject = ''
            
        if inverterobject is None:  # Is is pointing to whether inverterobject and None are the same object, is inverterobject is None they will be,# Need to use is as have overide the __eq__ operator for inverter object 

            inverterobject  = ''
            
            return '\nElectricLoadCenter:Distribution,\n' + \
                '\t'+str(distribution_name)+ ',\t!- Name\n'+ \
                '\t'+str(HBsystemgenerator_name)+ ',\t!- Generator List Name\n'+ \
                '\t'+str(operationscheme)+ ',\t!- Generator Operation Scheme Type\n'+ \
                '\t'+str(demandlimit)+ ',\t!- Demand Limit Scheme Purchased Electric Demand Limit {W}\n'+ \
                '\t'+str(trackschedule)+ ',\t!- Track Schedule Name Scheme Schedule Name\n'+ \
                '\t'+str(trackmeterschedule)+ ',\t!- Track Meter Scheme Meter Name\n'+ \
                '\t'+str(busstype)+ ',\t!- Electrical Buss Type\n'+ \
                '\t'+str(inverterobject)+ ',\t!- Inverter Object Name\n'+ \
                '\t'+str(elecstorageobject)+ ',\t!- Electrical Storage Object Name\n'+\
                '\t'+''+';\t!- Transformer Object Name\n'
        # Had an issue with inverterobject.name when inverterobject is None, should re-work to remove reference to .name 
        # but instead at the moment use two return statements
        else:
            
            return '\nElectricLoadCenter:Distribution,\n' + \
                '\t'+str(distribution_name)+ ',\t!- Name\n'+ \
                '\t'+str(HBsystemgenerator_name)+ ',\t!- Generator List Name\n'+ \
                '\t'+str(operationscheme)+ ',\t!- Generator Operation Scheme Type\n'+ \
                '\t'+str(demandlimit)+ ',\t!- Demand Limit Scheme Purchased Electric Demand Limit {W}\n'+ \
                '\t'+str(trackschedule)+ ',\t!- Track Schedule Name Scheme Schedule Name\n'+ \
                '\t'+str(trackmeterschedule)+ ',\t!- Track Meter Scheme Meter Name\n'+ \
                '\t'+str(busstype)+ ',\t!- Electrical Buss Type\n'+ \
                '\t'+str(inverterobject.name)+ ',\t!- Inverter Object Name\n'+ \
                '\t'+str(elecstorageobject)+ ',\t!- Electrical Storage Object Name\n'+\
                '\t'+''+';\t!- Transformer Object Name\n'

    def writegeneration_system_financialdata(self,financialdata):
        
        newfinancialdata = []
        # Add ! in front of all data so EnergyPlus views it as comments
        # and add other comments so data can be easily identified and read
        
        newfinancialdata.append('\n')
        newfinancialdata.append('\t'+'! Honeybee generation system financial data'+'\n')
        
        for dataitem in financialdata:
            
            if isinstance(dataitem, basestring) == True:
                
                # All data is in tuples so if its a string its a header e.g Generation system name
                
                newfinancialdata.append('\t'+'!!!X generation system name -' + str(dataitem)+'\n')
        
            newfinancialdata.append('\t'+'!!Z '+str(dataitem)+'\n')
            
        newfinancialdata.append('\n')

        return newfinancialdata
        

class RunIDF(object):
    
    def writeBatchFile(self, workingDir, idfFileName, epwFileAddress, EPDirectory = 'C:\\EnergyPlusV8-1-0'):
        
        workingDrive = workingDir[:2]
        
        if idfFileName.EndsWith('.idf'):  shIdfFileName = idfFileName.replace('.idf', '')
        else: shIdfFileName = idfFileName
        
        if not workingDir.EndsWith('\\'): workingDir = workingDir + '\\'
        
        fullPath = workingDir + shIdfFileName
        
        folderName = workingDir.replace( (workingDrive + '\\'), '')
        batchStr = workingDrive + '\ncd\\' +  folderName + '\n' + EPDirectory + \
                '\Epl-run ' + fullPath + ' ' + fullPath + ' idf "' + epwFileAddress + '" EP N nolimit N N 0 Y'
        
        #print "this is batch string" + batchStr
        batchFileAddress = fullPath +'.bat'
        batchfile = open(batchFileAddress, 'w')
        batchfile.write(batchStr)
        batchfile.close()
        
        #execute the batch file
        os.system(batchFileAddress) 

        os.system('C:\\honeybee\\runIt.bat')
            
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
    
    units = sc.doc.ModelUnitSystem
    if `units` != 'Rhino.UnitSystem.Meters':
        msg = "Currently the EnergyPlus component only works in meters. Change the units to Meters and try again!"
        ghenv.Component.AddRuntimeMessage(w, msg)
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

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    
    # make sure epw file address is correct
    if not epwFileAddress.endswith(epwFileAddress) or not os.path.isfile(epwFileAddress):
        msg = "Wrong weather file!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    else:
        illegalChar = ["&", "%", "'", "^", "=", ","] # based on EP error message
        for c in illegalChar:
            if c in epwFileAddress:
                msg = "Illegal charecter in weather file path: " + c
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
    print "[1 of 8] Writing simulation parameters..."
    
    # Version,8.1;
    idfFile.write(hb_writeIDF.EPVersion(sc.sticky["honeybee_folders"]["EPVersion"]))
    
    # Read simulation parameters
    timestep, shadowPar, solarDistribution, simulationControl, ddyFile, terrain = hb_EPPar.readEPParams(EPParameters)
    
    # Timestep,6;
    idfFile.write(hb_writeIDF.EPTimestep(timestep))
    
    # ShadowCalculation
    idfFile.write(hb_writeIDF.EPShadowCalculation(*shadowPar))
    
    # NumThread
    idfFile.write(hb_writeIDF.EPProgramControl())
    
    # Building
    EPBuilding = hb_writeIDF.EPBuilding(idfFileName, math.degrees(northAngle), terrain, 0.04, 0.4, solarDistribution, maxWarmUpDays =25, minWarmUpDays = 6)
                    
    idfFile.write(EPBuilding)
    
    # HeatBalanceAlgorithm
    idfFile.write(hb_writeIDF.EPHeatBalanceAlgorithm())
    
    # SurfaceConvectionAlgorithm
    idfFile.write(hb_writeIDF.EPSurfaceConvectionAlgorithm())
    
    # Location
    idfFile.write(hb_writeIDF.EPSiteLocation(epwFileAddress))
    
    # SizingPeriod
    #Check if there are sizing periods in the EPW file.
    dbTemp = []
    sizeWDesignWeeks = True
    epwfile = open(_epwFile,"r")
    lnum = 1 # line number
    for line in epwfile:
        if lnum == 2:
            extremePeriods = line.split(',')
            if len(extremePeriods) < 3: sizeWDesignWeeks = False
        if lnum > 8:
            dbTemp.append(float(line.split(',')[6]))
        lnum += 1
    
    if sizeWDesignWeeks == True:
        idfFile.write(hb_writeIDF.EPSizingPeriod('WinterExtreme'))
        idfFile.write(hb_writeIDF.EPSizingPeriod('SummerExtreme'))
    else:
        # figure out a sizing period from the extreme temperatures in the weather file
        HOYs = range(8760)
        dbTemp, HOYs = zip(*sorted(zip(dbTemp, HOYs)))
        HOYMax = HOYs[-1]
        HOYMin = HOYs[0]
        d, monthMax, t = lb_preparation.hour2Date(HOYMax+1, True)
        d, monthMin, t = lb_preparation.hour2Date(HOYMin+1, True)
        if monthMax != monthMin:
            idfFile.write(hb_writeIDF.EPSizingPeriodMonth(monthMax+1))
            idfFile.write(hb_writeIDF.EPSizingPeriodMonth(monthMin+1))
        else:
            idfFile.write(hb_writeIDF.EPSizingPeriodMonth(monthMin))
    
    # simulationControl
    idfFile.write(hb_writeIDF.EPSimulationControl(*simulationControl))
    
    # runningPeriod
    idfFile.write(hb_writeIDF.EPRunPeriod('customRun', stDay, stMonth, endDay, endMonth))
    
    # for now I write all the type limits but it can be cleaner
    scheduleTypeLimits = sc.sticky["honeybee_ScheduleTypeLimitsLib"].keys()
    for scheduleTypeLimit in scheduleTypeLimits:
        try: idfFile.write(hb_writeIDF.EPSCHStr(scheduleTypeLimit))
        except: pass
    
    # Geometry rules
    idfFile.write(hb_writeIDF.EPGeometryRules())

    EPConstructionsCollection = []
    EPMaterialCollection = []
    EPScheduleCollection = []
    
    
    # Shading Surfaces
    if HBContext and HBContext[0]!=None:
        print "[2 of 8] Writing context surfaces..."
       
        # call the objects from the lib
        shadingPyClasses = hb_hive.callFromHoneybeeHive(HBContext)
       
       
    def writeHBcontext(shadingPyClasses):
        
        for shading in shadingPyClasses:
            
            # take care of shcedule
            schedule = shading.TransmittanceSCH
            if schedule!="" and schedule.upper() not in EPScheduleCollection:
                # add schedule
                scheduleValues, comments = hb_EPScheduleAUX.getScheduleDataByName(schedule, ghenv.Component)
                if comments == "csv":
                    # create a new schedule object based on file
                    # and write it to idf
                    idfFile.write(hb_writeIDF.EPSCHStr(schedule))
                else:
                    # collect shchedule name
                    EPScheduleCollection.append(schedule.upper())
                    
                hb_writeIDF.EPSCHStr(shading.TransmittanceSCH.upper())
                
            idfFile.write(hb_writeIDF.EPShdSurface(shading))
       
    # Shading Surfaces
    if HBContext and HBContext[0]!=None:
        print "[2 of 6] Writing context surfaces..."
        # call the objects from the lib
        shadingPyClasses = hb_hive.callFromHoneybeeHive(HBContext)
        
        WriteIDF.checksurfaceduplicate.extend(shadingPyClasses) # Add to a list so can check for duplicates later
        writeHBcontext(shadingPyClasses)

    else:
        print "[2 of 6] No context surfaces..."
        print "[2 of 8] No context surfaces..."

        
    #################  BODY #####################
    print "[3 of 8] Writing geometry..."
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
            if schedule != "" and schedule.upper() not in EPScheduleCollection:
                EPScheduleCollection.append(schedule.upper())
                
        for srf in zone.surfaces:
            # check if there is an energyPlus material
            
            # Add surface to a list so that zone surfaces can be checked against honeybee generator PV surfaces
            WriteIDF.zonesurfaces.append(srf.ID)

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
                    # Check if there is any shading for the window.
                    if childSrf.blindsMaterial != "" and childSrf.shadingControl != "":
                        idfFile.write(childSrf.blindsMaterial)
                        idfFile.write(childSrf.shadingControl)
                        if childSrf.shadingSchName != 'ALWAYSON':
                            EPScheduleCollection.append(childSrf.shadingSchName.upper())
                    
                # write the glazing strings
                idfFile.write(hb_writeIDF.EPFenSurface(srf))
                # else: idfFile.write(hb_writeIDF.EPNonPlanarFenSurface(srf))
        
        #If there are internal masses assigned to the zone, write them into the IDF.
        if len(zone.internalMassNames) > 0:
            for massCount, massName in enumerate(zone.internalMassNames):
                #Write the internal mass construction into the IDF if it is not there yet.
                if not zone.internalMassConstructions[massCount].upper() in EPConstructionsCollection:
                    EPConstructionsCollection.append(zone.internalMassConstructions[massCount].upper())
                
                #Write the internal mass into the IDF
                idfFile.write(hb_writeIDF.EPInternalMass(zone, massName, zone.internalMassSrfAreas[massCount], zone.internalMassConstructions[massCount]))
        
    ########### Generators - Electric load center ###########
    
    print "[4 of 8] Writing Electric Load Center - Generator specifications ..."
        
    
    if HB_generators != []:

        hb_hivegen = sc.sticky["honeybee_generationHive"]()
    
        HBsystemgenerators = hb_hivegen.callFromHoneybeeHive(HB_generators)
        
        def extracttimeperiod(simulationOutputs):
            timeperiod = simulationOutputs[-1].split(',')[-1]
            HBgeneratortimeperiod = timeperiod.replace(";","")
            return HBgeneratortimeperiod 
            
        # Extract the timestep from the incoming component simulationOutputs if its being used
        HBgeneratortimeperiod = extracttimeperiod(simulationOutputs)

        # If the user doesnt set HBgeneration_ to True in Honeybee_Generate EP output component -  
        # Facility Total Electric Demand Power and Facility Net Purchased Electric Power will be assigned by default
        # As the statement below will execute.

        if (not any('Output:Variable,*,Facility Total Electric Demand Power' in s for s in simulationOutputs)) and (not any('Output:Variable,*,Facility Net Purchased Electric Power' in s for s in simulationOutputs)):
            
            simulationOutputs.append("Output:Variable,*,Facility Net Purchased Electric Energy, RunPeriod;")
            
            simulationOutputs.append("Output:Variable,*,Facility Total Electric Demand Power, RunPeriod;")
            
            HBgeneratortimeperiod = 'RunPeriod'
            
        for HBsystemcount,HBsystemgenerator in enumerate(HBsystemgenerators):
            
            # For this HBsystemgenerator write the output so that the produced electric energy is reported.
            simulationOutputs.append("Output:Variable,"+str(HBsystemgenerator.name)+":DISTRIBUTIONSYSTEM,Electric Load Center Produced Electric Energy,"+ HBgeneratortimeperiod +";")
                
            # Define the name for the list of generators and to use in generator's list name in ElectricLoadCenter:Distribution
            if HBsystemgenerator.name == None:
                
                HBsystemgenerator_name = "generatorsystem" + str(HBsystemcount)
                
            else:
    
                HBsystemgenerator_name = str(HBsystemgenerator.name)
            
            # Write one ElectricLoadCenter:Generators for each HBsystemgenerator
            
            ### XXX still needs work to make sure names dont overlap
            idfFile.write(hb_writeIDF.writegeneratlorlist(HBsystemgenerator_name,HBsystemgenerator.PVgenerators+HBsystemgenerator.windgenerators+HBsystemgenerator.fuelgenerators)) # The writegeneratlorlist only takes 'generators' as an input so add all the different generator lists together 
            
            # Determine the type of system and write one ElectricLoadCenter:Distribution for each HBsystemgenerator
            
            distribution_name = str(HBsystemgenerator_name) + ':Distributionsystem' 
            
            # Add cost of grid electricty to list to check that all grid electricity costs are the same for all generators later
            
            WriteIDF.gridelectcost.append(HBsystemgenerator.gridelectcost)
            
            # Add a header to the financial data so that its clear financial data is from this system
            
            WriteIDF.financialdata.append(HBsystemgenerator.name)
            
            # Decide whether it is a PV, Wind or fuel generator system
            
            if HBsystemgenerator.PVgenerators != []:
                
                # Add to a list to conduct checks on consistency of context surfaces later
                
                WriteIDF.checksurfaceduplicate.extend(HBsystemgenerator.contextsurfaces) 
                
                # Write the Honeybee context sufaces
                writeHBcontext(HBsystemgenerator.contextsurfaces)
                
                # CHECK
                # If PV surfaces are part of a zone make sure that, that zone is connected to _HBZones
                # that is the PV surfaces are contained in HBsystemgenerator.HBzonesurfaces
                    
                PVsurfaceinzones = []
                
                for surface in HBsystemgenerator.HBzonesurfaces:
    
                    PVsurfaceinzones.append(surface.ID in WriteIDF.zonesurfaces)
                    
                if all(x== True for x in PVsurfaceinzones) != True:
                    
                    print "The HBzone which some PV_HBSurfaces belong to is not connected to _HBZones please connect it!  " 
                    ghenv.Component.AddRuntimeMessage(w, "The HBzone which some PV_HBSurfaces belong to is not connected to _HBZones please connect it!")
                    
                    return -1
                
                if HBsystemgenerator.simulationinverter != None:
                    
                    if HBsystemgenerator.battery != None:
                        
                        # HBsystem contains a inverter and is a DC system AND has storage
  
                        WriteIDF.financialdata.append((HBsystemgenerator.battery.cost_,"battery"))
                        
                        # Although multiple inverters may exist in HBsystemgenerator.simulationinverter 
                        # in the Honeybee generation system it has been checked that they are all the same

                        WriteIDF.financialdata.append((HBsystemgenerator.simulationinverter[0].cost_,"inverter")) 
                        
                        operationscheme = 'Baseload'
                        busstype = 'DirectCurrentWithInverterDCStorage'
                        demandlimit = ''
                        trackschedule = 'Always On'
                        trackmeterschedule = ''
                        inverterobject = HBsystemgenerator.simulationinverter[0] # All inverters are the same doesnt matter which one you pick
                        elecstorageobject = HBsystemgenerator.battery.name
                        
                        # Write HBsystemgenerator battery
                        idfFile.write(hb_writeIDF.battery_simple(HBsystemgenerator.battery))
                        
                        # Write HBsystemgenerator photovoltaic generators
                        for PVgen in HBsystemgenerator.PVgenerators:
                            
                            idfFile.write(hb_writeIDF.write_PVgen(PVgen))
                            idfFile.write(hb_writeIDF.write_PVgenperformanceobject(PVgen))
                            WriteIDF.financialdata.append((PVgen.cost_,"PV module")) # - Does the class PV_gen need an ID?
                        
                        # Write HBsystemgenerator inverters
                        idfFile.write(hb_writeIDF.simple_inverter(inverterobject))
                        
                        # Write HBsystemgenerator ElectricLoadCenter:Distribution
                        idfFile.write(hb_writeIDF.writeloadcenterdistribution(distribution_name,HBsystemgenerator_name,operationscheme,demandlimit,trackschedule,trackmeterschedule,busstype,inverterobject,elecstorageobject))
                        
                        # Check for duplicate batteries - These can cause EnergyPlus to crash
                        # Append battery ID to checkbatteryduplicate to check for duplicate batteries
                        WriteIDF.checkbatteryduplicate.append(HBsystemgenerator.battery.ID)
                        
                        # If the battery ID occurs twice in the list WriteIDF.checkbatteryduplicate it is a duplicate
                        if WriteIDF.checkbatteryduplicate.count(HBsystemgenerator.battery.ID) == 2:
                            
                            warning  = 'Duplicate battery detected! please make sure that each HB generators has its own battery \n'+ \
                            'usually this happens because one battery is connected to many PVgenerators make sure each PVgenerator has its own\n'+ \
                            'unique battery'
                            ghenv.Component.AddRuntimeMessage(w, warning)
                            print warning 
                            return -1 
                            
                        # CHECK for duplicate inverters - These can cause EnergyPlus to crash
                        # Append inverter ID to checkbatteryduplicate to check for duplicate inverter 
                        WriteIDF.checkinverterduplicate.append(inverterobject.ID)
                
                        # If the inverter ID occurs twice in the list WriteIDF.checkinverterduplicate it is a duplicate
                        if WriteIDF.checkinverterduplicate.count(inverterobject.ID) == 2:
                            warning  = 'Duplicate inverter detected! please make sure that each Honeybee PV generator has its own inverter \n'+ \
                            'usually this happens because one inverter is connected to many PVgenerators make sure each PVgenerator has its own\n'+ \
                            'unique inverter'
                            ghenv.Component.AddRuntimeMessage(w, warning)
                            print warning 
                            return -1 
                        
                    else:
                        # HBsystem contains a inverter and is a DC system there are NO batteries in the system
                        
                        WriteIDF.financialdata.append((HBsystemgenerator.simulationinverter[0].cost_,"inverter"))
                        
                        operationscheme = 'Baseload'
                        busstype = 'DirectCurrentWithInverter'
                        demandlimit = ''
                        trackschedule = 'Always On'
                        trackmeterschedule = ''
                        inverterobject = HBsystemgenerator.simulationinverter[0] # All inverters are the same doesnt matter which one you pick
                        
                        # Write HBsystemgenerator photovoltaic generators
                        for PVgen in HBsystemgenerator.PVgenerators:
                            
                            idfFile.write(hb_writeIDF.write_PVgen(PVgen))
                            idfFile.write(hb_writeIDF.write_PVgenperformanceobject(PVgen))
                            WriteIDF.financialdata.append((PVgen.cost_, "PV module")) # - Does the class PV_gen need an ID?
                        
                        # Write HBsystemgenerator inverters
                        idfFile.write(hb_writeIDF.simple_inverter(inverterobject))
                        
                        # Write HBsystemgenerator ElectricLoadCenter:Distribution
                        idfFile.write(hb_writeIDF.writeloadcenterdistribution(distribution_name,HBsystemgenerator_name,operationscheme,demandlimit,trackschedule,trackmeterschedule,busstype,inverterobject,None)) 
                        
                        # CHECK for duplicate inverters - These can cause EnergyPlus to crash
                        # Append inverter ID to checkbatteryduplicate to check for duplicate inverter 
                        WriteIDF.checkinverterduplicate.append(inverterobject.ID)
                
                        # If the inverter ID occurs twice in the list WriteIDF.checkinverterduplicate it is a duplicate
                        if WriteIDF.checkinverterduplicate.count(inverterobject.ID) == 2:
                            warning  = 'Duplicate inverter detected! please make sure that each Honeybee PV generator has its own inverter \n'+ \
                            'usually this happens because one inverter is connected to many PVgenerators make sure each PVgenerator has its own\n'+ \
                            'unique inverter'
                            ghenv.Component.AddRuntimeMessage(w, warning)
                            print warning 
                            return -1 
    
                    
            elif HBsystemgenerator.windgenerators != []:
                
                operationscheme = 'Baseload'
                busstype = 'AlternatingCurrent'
                demandlimit = ''
                trackschedule = 'Always On'
                trackmeterschedule = ''
                inverterobject = None
                elecstorageobject = None
                
                # Write HBsystemgenerator wind generators
                for windgenerator in HBsystemgenerator.windgenerators:
                    
                    idfFile.write(hb_writeIDF.wind_generator(windgenerator))
                    WriteIDF.financialdata.append((windgenerator.cost_,"Wind turbine")) # - Does the class PV_gen need an ID?
                    
                # Write HBsystemgenerator ElectricLoadCenter:Distribution
                idfFile.write(hb_writeIDF.writeloadcenterdistribution(distribution_name,HBsystemgenerator_name,operationscheme,demandlimit,trackschedule,trackmeterschedule,busstype,inverterobject,elecstorageobject))
                
               
            elif HBsystemgenerator.fuelgenerators != []: # XXX 14/04/2015 not yet implemented so always equal to []
                
                busstype = 'AlternatingCurrent'
            
        # CHECK for duplicate HBcontext surfaces this could happen if the user connects context surfaces to both HBContext_ and a HB generator system
        HBcontextsurfaces = set()
        
        for HBcontextsurface in WriteIDF.checksurfaceduplicate:
            HBcontextsurfaces.add(HBcontextsurface.ID)
            
        if len(HBcontextsurfaces) != len(WriteIDF.checksurfaceduplicate):
            
            print "Duplicate HBcontext surfaces detected! Don't connect HBcontext surfaces to both PVgen component and run E+ component HBContext_ input!"
            ghenv.Component.AddRuntimeMessage(w, "Duplicate HBcontext surfaces detected! Don't connect HBcontext surfaces to both PVgen component and run E+ component HBContext_ input!")
            
            return -1
        
        # CHECK that the cost of grid electricity is the same for all connected Honeybee generators
        
        if all(gridelectcost== WriteIDF.gridelectcost[0] for gridelectcost in WriteIDF.gridelectcost) != True:
     
            warn = 'The cost of electricity from the grid is not the same across all connected HB generation systems! \n'+ \
                    'Please make sure that the cost connected to each HB generation system is the same!'
            print warn
            ghenv.Component.AddRuntimeMessage(w, warn)
            
            return -1
        
        for data in hb_writeIDF.writegeneration_system_financialdata(WriteIDF.financialdata):
            
            idfFile.write(data)
        
        
    ################ Construction #####################
    print "[5 of 8] Writing materials and constructions..."
    
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
    print "[6 of 8] Writing schedules..."
    
    #Check if schedules need to be written for air mixing or natural ventilation.
    needToWriteMixSched = False
    for key, zones in ZoneCollectionBasedOnSchAndLoads.items():
        for zone in zones:
            if zone.natVent == True:
                for schedule in zone.natVentSchedule:
                    if schedule != None:
                        if schedule.upper() not in EPScheduleCollection: EPScheduleCollection.append(schedule)
                    else: needToWriteMixSched = True

            if zone.mixAir == True: needToWriteMixSched = True
    if needToWriteMixSched == True:
        if 'ALWAYS ON' not in EPScheduleCollection: EPScheduleCollection.append('ALWAYS ON')
    
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
    
    print "[7 of 8] Writing loads and ideal air system..."
    listCount = 0
    listName = None
    
    
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
            if zone.HVACSystem[-1]!=None:
                warning = "An HVAC system is applied to " + zone.name + \
                          ".\n" + \
                          "EnergyPlus component will replace this HVAC system with an Ideal Air Loads system.\n" + \
                          " To model advanced HVAC systems use OpenStudio component."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                print warning
            
            #   HAVC System
            if listName!=None:
                HAVCTemplateName = listName + "_HVAC"
                for zone in zones:
                    idfFile.write(hb_writeIDF.EPIdealAirSystem(zone, HAVCTemplateName))
                
            else:
                HAVCTemplateName = zone.name + "_HVAC"
                idfFile.write(hb_writeIDF.EPIdealAirSystem(zone, HAVCTemplateName))
            
            #Thermostat
            idfFile.write(hb_writeIDF.EPHVACTemplate(HAVCTemplateName, zone))
            
            
            #   LOADS - INTERNAL LOADS + PLUG LOADS
            if zone.equipmentSchedule != None:
                idfFile.write(hb_writeIDF.EPZoneElectricEquipment(zone, listName))
        
            #   PEOPLE
            if zone.occupancySchedule != None:
                idfFile.write(hb_writeIDF.EPZonePeople(zone, listName))
        
            #   LIGHTs
            idfFile.write(hb_writeIDF.EPZoneLights(zone, listName))
        
            #   INFILTRATION
            idfFile.write(hb_writeIDF.EPZoneInfiltration(zone, listName))
            
            #   AIR MIXING
            if zone.mixAir == True:
                for mixZoneCount, zoneMixName in enumerate(zone.mixAirZoneList):
                    idfFile.write(hb_writeIDF.EPZoneAirMixing(zone, zoneMixName, zone.mixAirFlowList[mixZoneCount], mixZoneCount))
            
            # EARTH TUBE
            
            if zone.earthtube == True:
                
                idfFile.write(hb_writeIDF.EarthTube(zone))
            
            #   SIMPLE NATURAL VENTILATION
            if zone.natVent == True:
                for natVentCount, natVentObj in enumerate(zone.natVentType):
                    if natVentObj == 1 or natVentObj == 2:
                        idfFile.write(hb_writeIDF.EPNatVentSimple(zone, natVentCount))
                    elif natVentObj == 3:
                        idfFile.write(hb_writeIDF.EPNatVentFan(zone, natVentCount))
    
    #Write any additional strings.
    if additionalStrings_ != []:
        idfFile.write("\n")
        for string in additionalStrings_:
            if ":" in string:
                idfFile.write("\n")
                idfFile.write("\n")
                idfFile.write(string)
            elif "!" not in string:
                idfFile.write("\n")
                idfFile.write("\n")
                idfFile.write(string)
                idfFile.write("\n")
            else:
                idfFile.write(string)
                idfFile.write("\n")
        idfFile.write("\n")
    
    ################## FOOTER ###################
    # write output lines
    # request surface information in the eio file.
    idfFile.write(hb_writeIDF.requestSrfeio())
    
    # request an output variable dictionary.
    idfFile.write(hb_writeIDF.requestVarDict())
    
    # write the outputs requested by the user.
    if simulationOutputs:
        print "[8 of 8] Writing outputs..."
        idfFile.write('\n')
        for line in simulationOutputs:
            idfFile.write(line + '\n')
            
    else:
        print "[8 of 8] No outputs! You usually want to get some outputs when you run an analysis. Just saying..."
        print "We'll just request some energy-related outputs for you that are monthly."
        outPutsDefalut = 'OutputControl:Table:Style,Comma; \n' + \
            'Output:Variable,*,Zone Ideal Loads Zone Total Cooling Energy, monthly; \n' + \
            'Output:Variable,*,Zone Ideal Loads Zone Total Heating Energy, monthly; \n' + \
            'Output:Variable,*,Zone Lights Electric Energy, monthly; \n' + \
            'Output:Variable,*,Zone Electric Equipment Electric Energy, monthly;'
        idfFile.write('\n')
        idfFile.write(outPutsDefalut + '\n')
        # Writing outputs for Honeybee generators if there are any
        
    idfFile.close()
    
    print "...\n... idf file is successfully written to : " + idfFileFullName + "\n"
    
    ######################## RUN ENERGYPLUS SIMULATION #######################
    resultFileFullName = None
    if runEnergyPlus:
        print "Analysis is running!..."
        # write the batch file
        hb_runIDF.writeBatchFile(workingDir, idfFileName, epwFileAddress, sc.sticky["honeybee_folders"]["EPPath"])
        resultFileFullName = idfFileFullName.replace('.idf', '.csv')
        try:
            print workingDir + '\eplusout.csv'
            test = open(workingDir + '\eplusout.csv', 'r')
            test.close()
            resultFileFullName = workingDir + '\eplusout.csv'
        except:
            pass
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
    
    