# This component runs an annual comfort assessment off of EnergyPlus results
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component runs an annual adaptive comfort assessment off of EnergyPlus results and write all values into csv files.
The results in these files can be used for creating indoor comfort maps.
-
Provided by Honeybee 0.0.55
    
    Args:
        _comfAnalysisRecipe: A comfort analysis recipe out of the Honeybee_Annual Comfort Analysis Recipe" component.
        _prevailingOutdoorTemp: A number representing the average monthly outdoor temperature in degrees Celcius.  This average monthly outdoor temperature is the temperature that occupants in naturally ventilated buildings tend to adapt themselves to. For this reason, this input can also accept the direct output of dryBulbTemperature from the Import EPW component if houlry values for the full year are connected for the other inputs of this component.
        eightyPercentComf_: Set to "True" to have the comfort standard be 80 percent of occupants comfortable and set to "False" to have the comfort standard be 90 percent of all occupants comfortable.  The default is set to "True" for 90 percent, which is what most members of the building industry aim for.
        workingDir_: An optional working directory on your system. Default is set to C:\Ladybug
        fileName_: An optional file name for the result files as a string.
        _runIt: Set boolean to "True" to run the component and generate files for an annual indoor comfort assessment.
    Returns:
        readMe!: ...
        ===============: ...
        radTempMtx: A python matrix containing MRT data for every hour of the year to be plugged into the "Honeybee_Visualize Annual Comfort Results" component.
        airTempMtx: A python matrix containing air temperature data for every hour of the year to be plugged into the "Honeybee_Visualize Annual Comfort Results" component.
        operativeTempMtx: A python matrix containing operative temperature data for every hour of the year to be plugged into the "Honeybee_Visualize Annual Comfort Results" component.
        adaptComfMtx: A python matrix containing adaptive comfort data for every hour of the year to be plugged into the "Honeybee_Visualize Annual Comfort Results" component.
        degFrimTargetMtx: A python matrix containing degrees from tartget temperature data for every hour of the year to be plugged into the "Honeybee_Visualize Annual Comfort Results" component.
        ===============: ...
        radTempResult: A csv file address containing the radiant temperature resultsfor each point for every hour of the year.
        airTempResult: A csv file address containing the air temperature results for each point for every hour of the year.
        operativeTempResult: A csv file address containing the operative temperature results for each point for every hour of the year.
        adaptComfResult: A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the year.
        degFrimTargetResult: A csv file address containing the a series of numbers indicating the degrees that a certain point is from the neutral temperature for every hour of the year.

"""

ghenv.Component.Name = "Honeybee_Annual Adaptive Indoor Comfort Analysis"
ghenv.Component.NickName = 'AdaptIndoorComfAnalysis'
ghenv.Component.Message = 'VER 0.0.55\nDEC_20_2014'
ghenv.Component.Category = "Honeybee@E"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nDEC_02_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


from System import Object
from System import Drawing
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import Rhino as rc
import scriptcontext as sc
import math
import os


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    #UNPACK THE ANALYSIS RECIPE.
    srfTempNumbers = _comfAnalysisRecipe[0]
    srfTempHeaders = _comfAnalysisRecipe[1]
    airTempDataNumbers = _comfAnalysisRecipe[2]
    airTempDataHeaders = _comfAnalysisRecipe[3]
    srfTempUnits = _comfAnalysisRecipe[4]
    zoneSrfNames = _comfAnalysisRecipe[5]
    testPtsViewFactor = _comfAnalysisRecipe[6]
    viewFactorMesh = _comfAnalysisRecipe[7]
    calcSolar = _comfAnalysisRecipe[8]
    latitude = _comfAnalysisRecipe[9]
    longitude = _comfAnalysisRecipe[10]
    timeZone = _comfAnalysisRecipe[11]
    diffSolarRad = _comfAnalysisRecipe[12]
    directSolarRad = _comfAnalysisRecipe[13]
    testPtSkyView = _comfAnalysisRecipe[14]
    testPts = _comfAnalysisRecipe[15]
    shadingContext = _comfAnalysisRecipe[16]
    winTrans = _comfAnalysisRecipe[17]
    cloA = _comfAnalysisRecipe[18]
    floorR = _comfAnalysisRecipe[19]
    testPtZoneNames = _comfAnalysisRecipe[20]
    testPtZoneWeights = _comfAnalysisRecipe[21]
    ptHeightWeights = _comfAnalysisRecipe[22]
    
    
    # CHECKING GENERAL COMFORT INPUTS
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
     
    #Check lenth of the _prevailingOutdoorTemp list and evaluate the contents.
    checkData19 = False
    prevailTemp = []
    if len(_prevailingOutdoorTemp) != 0:
        try:
            if _prevailingOutdoorTemp[2] == 'Dry Bulb Temperature':
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7:751])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[751:1423])/672)], 672))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[1423:2167])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2167:2887])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2887:3631])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[3631:4351])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[4351:5095])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5095:5839])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5839:6559])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[6559:7303])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7303:8023])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[8023:])/744)], 744))
                checkData19 = True
        except: pass
        if checkData19 == False:
            if len(_prevailingOutdoorTemp) == 12:
                for item in _prevailingOutdoorTemp:
                    try:
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[0]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[1]], 672))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[2]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[3]], 720))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[4]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[5]], 720))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[6]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[7]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[8]], 720))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[9]], 744))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[10]], 720))
                        prevailTemp.extend(duplicateData([_prevailingOutdoorTemp[11]], 744))
                        checkData19 = True
                    except: pass
            elif len(_prevailingOutdoorTemp) == 1:
                try:
                    prevailTemp = duplicateData(_prevailingOutdoorTemp, 8760)
                    checkData19 = True
                except: pass
        
        if checkData19 == False:
            warning = '_prevailingOutdoorTemp input must be either a list of Air Temperature data from the Import EPW component, a list of 12 values for 12 months, or a single value to be used for the whole year.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _prevailingOutdoorTemp'
    
    
    #Set a default fileName.
    if fileName_ == None:
        fileName = 'AnnComfAnalysis'
    else: fileName = fileName_
    
    #Do a final check of everything.
    if checkData19 == True:
        checkData = True
    else: checkData = False
    
    return checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, prevailTemp, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, fileName


def calculatePointMRT(srfTempValues, zoneSrfNames, testPtsViewFactor, srfHeaders):
    #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
    srfTempDict = {}
    
    for i in range(len(zoneSrfNames)):
        for srfindex in range(len(zoneSrfNames[i])):
            pathInt = [i,srfindex]
            path = str(pathInt)
            
            if not srfTempDict.has_key(path):
                srfTempDict[path] = {}
            
            srfTempDict[path]["srfName"] = zoneSrfNames[pathInt[0]][pathInt[1]]
    
    #Figure out which surfaces in the dictionary correspond to the connected MRT srfHeaders.
    for listCount, list in enumerate(srfHeaders):
        srfName = list[2].split(" for ")[-1]
        try: srfName = srfName.split(":")[0]
        except: pass
        for path in srfTempDict:
            if srfTempDict[path]["srfName"].upper() == srfName:
                srfTempDict[path]["srfTemp"] = srfTempValues[listCount]
    
    #Calculate the MRT for each point.
    pointMRTValues = []
    for zoneCount, pointList in enumerate(testPtsViewFactor):
        pointMRTValues.append([])
        for pointViewFactor in pointList:
            pointMRT = 0
            for srfCount, srfView in enumerate(pointViewFactor):
                path  = str([zoneCount,srfCount])
                weightedSrfTemp = srfView*(srfTempDict[path]["srfTemp"])
                pointMRT = pointMRT+weightedSrfTemp
            pointMRTValues[zoneCount].append(pointMRT)
    
    
    return pointMRTValues

def calculateSolarAdjustedMRT(pointMRTValues, testPts, stepOfSimulation, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, shadingContext, winTrans, cloA, floorR, lb_sunpath, lb_comfortModels):
    #Calculate the altitude and azimuth of the hour.
    lb_sunpath.initTheClass(float(latitude), 0.0, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
    d, m, t = lb_preparation.hour2Date(stepOfSimulation, True)
    lb_sunpath.solInitOutput(m+1, d, t)
    altitude = math.degrees(lb_sunpath.solAlt)
    azimuth = math.degrees(lb_sunpath.solAz)
    if altitude > 0:
        sunVec = lb_sunpath.sunReverseVectorCalc()
    else: sunVec = None
    
    ##Calculate the diffuse, direct, and global horizontal components of the solar radiation at the hour.
    diffRad = diffSolarRad[stepOfSimulation-1]
    dirNormRad = directSolarRad[stepOfSimulation-1]
    globHorizRad = dirNormRad*(math.sin(altitude)) + diffRad
    
    #Define the Altitide and Azimuth as the SolarCal function understands it.
    azFinal = azimuth
    if azFinal > 180:
        while azFinal > 180:
            azFinal = azFinal-180
    elif azFinal < 0:
        while azFinal < 0:
            azFinal = azFinal+180
    azFinal = int(azFinal)
    
    altFinal = altitude
    if altFinal > 90: altFinal = altFinal-90
    altFinal = int(altFinal)
    
    #Compute the projected area factor and the fractional efficiency of a seated person.
    ProjAreaFac = lb_comfortModels.splineSit(azFinal, altFinal)
    fracEff = 0.696
    
    #Define a good guess of a radiative heat transfer coefficient.
    radTransCoeff = 6.012
    
    #Compute the solar adjusted temperature for each point.
    solarAdjustedPointMRTValues = []
    if sunVec != None:
        for zoneCount, zonePtsList in enumerate(pointMRTValues):
            solarAdjustedPointMRTValues.append([])
            for pointCount, pointMRT in enumerate(zonePtsList):
                #First get the sunRay.
                sunRay = rc.Geometry.Ray3d(testPts[zoneCount][pointCount], sunVec)
                
                #Next check if the sunray is blocked.
                sunBlocked = False
                for mesh in shadingContext[zoneCount]:
                    rayIntersect = rc.Geometry.Intersect.Intersection.MeshRay(mesh, sunRay)
                    if rayIntersect > 0: sunBlocked = True
                
                #If the ray was not blocked, then adjust then get rid of direct solar radiation.
                if sunBlocked == True:
                    dirRadFinal = 0.0
                    globHorizRadFinal = diffRad
                else:
                    dirRadFinal = dirNormRad
                    globHorizRadFinal = globHorizRad
                
                hourERF = ((0.5*fracEff*testPtSkyView[zoneCount][pointCount]*(diffRad + (globHorizRadFinal*floorR))+ (fracEff*ProjAreaFac*dirRadFinal))*winTrans[stepOfSimulation-1])*(cloA/0.95)
                #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                mrtDelt = (hourERF/(fracEff*radTransCoeff))
                hourMRT = mrtDelt + (pointMRT)
                solarAdjustedPointMRTValues[zoneCount].append(hourMRT)
    else:
        solarAdjustedPointMRTValues = pointMRTValues
    
    
    return solarAdjustedPointMRTValues


def getAirPointValue(zoneValues, testPtZoneNames, testPtZoneWeights, dataHeaders):
    #Make a dictionary that will relate the testPtZoneNames to the zoneValues.
    zoneValueDict = {}
    
    for i in range(len(testPtZoneNames)):
        path = i
        if not zoneValueDict.has_key(path):
            zoneValueDict[path] = {}
        zoneValueDict[path]["zoneName"] = testPtZoneNames[path]
    
    #Figure out which zones in the dictionary correspond to the connected dataHeaders.
    for listCount, list in enumerate(dataHeaders):
        zName = list[2].split(" for ")[-1]
        try: zName = zName.split(":")[0]
        except: pass
        for path in zoneValueDict:
            if zoneValueDict[path]["zoneName"].upper() == zName:
                zoneValueDict[path]["zoneValues"] = zoneValues[listCount]
    
    #Calculate the value for each point.
    pointValues = []
    for zoneCount, pointList in enumerate(testPtZoneWeights):
        pointValues.append([])
        for pointWeght in pointList:
            pointValue = 0
            for Count, weight in enumerate(pointWeght):
                path  = Count
                weightedPointVal = weight*(zoneValueDict[path]["zoneValues"])
                pointValue = pointValue+weightedPointVal
            pointValues[zoneCount].append(pointValue)
    
    return pointValues

def warpByHeight(pointAirTempValues, ptHeightWeights):
    for zoneCount, zone in enumerate(pointAirTempValues):
        for ptCount, ptValue in enumerate(zone):
            pointAirTempValues[zoneCount][ptCount] = ptValue + ptHeightWeights[zoneCount][ptCount]
    
    return pointAirTempValues


def main(srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, prevailTemp, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, lb_preparation, lb_sunpath, lb_comfortModels):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature']
    airTempMtx = ['Air Temperature']
    operativeTempMtx = ['Operative Temperature']
    adaptComfMtx = ['Adaptive Comfort']
    degFromTargetMtx = ['Degrees From Target']
    
    
    #Run through every hour of the year to fill up the matrices.
    for hour in range(1,8761):
        #Select out the relevant air and surface temperatures.
        hourSrfTemps = []
        hourAirTemps = []
        for srfVal in srfTempNumbers:
            hourSrfTemps.append(srfVal[hour-1])
        for zoneVal in airTempDataNumbers:
            hourAirTemps.append(zoneVal[hour-1])
        
        #Compute the radiant temperature.
        pointMRTValues = calculatePointMRT(hourSrfTemps, zoneSrfNames, testPtsViewFactor, srfTempHeaders)
        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, testPts, hour, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, shadingContext, winTrans, cloA, floorR, lb_sunpath, lb_comfortModels)
        pointMRTValues = lb_preparation.flattenList(pointMRTValues)
        radTempMtx.append(pointMRTValues)
        
        #Compute the air temperature.
        pointAirTempValues = getAirPointValue(hourAirTemps, testPtZoneNames, testPtZoneWeights, airTempDataHeaders)
        pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights)
        pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
        airTempMtx.append(pointAirTempValues)
        
        #Compute the operative temperature.
        pointOpTempValues = []
        for ptCount, airTemp in enumerate(pointAirTempValues):
            pointOpTempValues.append((airTemp+pointMRTValues[ptCount])/2)
        operativeTempMtx.append(pointOpTempValues)
        
        #Compute the adaptive comfort, statusOfPerson, and deg from target.
        adaptComfPointValues = []
        statusOfPersonPointValues = []
        degFromTargetPointValues = []
        
        for ptCount, airTemp in enumerate(pointAirTempValues):
            comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(airTemp, pointMRTValues[ptCount], prevailTemp[hour-1], 0.05, eightyPercentComf_)
            adaptComfPointValues.append(int(comf))
            degFromTargetPointValues.append(distFromTarget)
        
        adaptComfMtx.append(adaptComfPointValues)
        degFromTargetMtx.append(degFromTargetPointValues)
    
    
    return radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx


def writeCSV(lb_preparation, lb_defaultFolder, fileName, radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx):
    #Find out the number of values in each hour.
    valLen = len(radTempMtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(lb_defaultFolder, fileName)) 
    
    #Create a csv Files.
    radTempFile = fileName + "RadiantTemp.csv"
    airTempFile = fileName + "AirTemp.csv"
    opTempFile = fileName + "OperativeTemp.csv"
    adaptComfFile = fileName + "AdaptComf.csv"
    degFromTargetFile = fileName + "DegFromTarget.csv"
    
    #Write the radiant temperature result file.
    radTempResult = os.path.join(workingDir, radTempFile)
    radCSVfile = open(radTempResult, 'wb')
    for lineCount, line in enumerate(radTempMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            radCSVfile.write(lineStr)
        else: radCSVfile.write(line + "\n")
    radCSVfile.close()
    
    #Write the air temperature result file.
    airTempResult = os.path.join(workingDir, airTempFile)
    airCSVfile = open(airTempResult, 'wb')
    for lineCount, line in enumerate(airTempMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            airCSVfile.write(lineStr)
        else: airCSVfile.write(line + "\n")
    airCSVfile.close()
    
    #Write the operative temperature result file.
    operativeTempResult = os.path.join(workingDir, opTempFile)
    opCSVfile = open(operativeTempResult, 'wb')
    for lineCount, line in enumerate(operativeTempMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            opCSVfile.write(lineStr)
        else: opCSVfile.write(line + "\n")
    opCSVfile.close()
    
    #Write the adaptive comfort result file.
    adaptComfResult = os.path.join(workingDir, adaptComfFile)
    comfCSVfile = open(adaptComfResult, 'wb')
    for lineCount, line in enumerate(adaptComfMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            comfCSVfile.write(lineStr)
        else: comfCSVfile.write(line + "\n")
    comfCSVfile.close()
    
    #Write the deg from target result file.
    degFromTargetResult = os.path.join(workingDir, degFromTargetFile)
    degCSVfile = open(degFromTargetResult, 'wb')
    for lineCount, line in enumerate(degFromTargetMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            degCSVfile.write(lineStr)
        else: degCSVfile.write(line + "\n")
    degCSVfile.close()
    
    
    return radTempResult, airTempResult, operativeTempResult, adaptComfResult, degFromTargetResult




#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_defaultFolder = sc.sticky["Ladybug_DefaultFolder"]
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
    lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")


#Check the data input.
checkData = False
if len(_comfAnalysisRecipe) == 23 and checkLB == True:
    checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, prevailTemp, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, fileName = checkTheInputs()

if checkData == True and _runIt == True:
    radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx = main(srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, prevailTemp, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, lb_preparation, lb_sunpath, lb_comfortModels)
    radTempResult, airTempResult, operativeTempResult, adaptComfResult, degFromTargetResult = writeCSV(lb_preparation, lb_defaultFolder, fileName, radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx)
