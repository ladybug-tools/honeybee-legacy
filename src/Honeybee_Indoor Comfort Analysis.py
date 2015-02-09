# This component runs an annual comfort assessment off of EnergyPlus results
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component runs an annual comfort assessment off of EnergyPlus results and write all values into csv files.
The results in these files can be used for creating indoor comfort maps.
-
Provided by Honeybee 0.0.56
    
    Args:
        _comfAnalysisRecipe: A comfort analysis recipe out of one of the comfort recipe component.
        =============: ...
        workingDir_: An optional working directory on your system. Default is set to C:\Ladybug
        fileName_: An optional file name for the result files as a string.
        =============: ...
        analysisPeriodOrHOY_: An optional analysis period from the 'Analysis Period component' or an hour of the analysis between 1 and 8760 for which you want to conduct the analysis. If no value is connected here, the component will run for the entire analysis, which can be very long in some cases.
        =============: ...
        writeResultFile_: Set to 'True' to have the component write all results into CSV result files.  The default is set to 'True' as these simulations can be long and yuo usually want a copy of your results.  You may want to set it to 'False' if you are just scrolling through key hours and want the fastest run possible.
        parallel_: Set to "True" to run the component using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.  For this reason, the default is set to 'False.'
        _runIt: Set boolean to "True" to run the component and generate files for an annual indoor comfort assessment.
    Returns:
        readMe!: ...
        ===============: ...
        radTempMtx: A python matrix containing MRT data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component.
        airTempMtx: A python matrix containing air temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component.
        operativeTempMtx: A python matrix containing operative temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component.
        adaptComfMtx: A python matrix containing adaptive comfort data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component.
        degFromTargetMtx: A python matrix containing degrees from tartget temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component.
        ===============: ...
        radTempResult: A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis.
        airTempResult: A csv file address containing the air temperature results for each point for every hour of the analysis.
        operativeTempResult: A csv file address containing the operative temperature results for each point for every hour of the analysis.
        adaptComfResult: A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the analysis.
        degFromTargetResult: A csv file address containing the a series of numbers indicating the degrees that a certain point is from the neutral temperature for every hour of the analysis.

"""

ghenv.Component.Name = "Honeybee_Indoor Comfort Analysis"
ghenv.Component.NickName = 'IndoorComfAnalysis'
ghenv.Component.Message = 'VER 0.0.56\nFEB_07_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
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
import System.Threading.Tasks as tasks


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


outputsDictAdapt = {
    
0: ["readMe!", "..."],
1: ["===============", "..."],
2: ["radTempMtx", "A python matrix containing MRT data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
3: ["airTempMtx", "A python matrix containing air temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
4: ["operativeTempMtx", "A python matrix containing operative temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
5: ["adaptComfMtx", "A python matrix containing adaptive comfort data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
6: ["degFromTargetMtx", "A python matrix containing degrees from tartget temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
7: ["===============", "..."],
8: ["radTempResult", "A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis."],
9: ["airTempResult", "A csv file address containing the air temperature results for each point for every hour of the analysis."],
10: ["operativeTempResult", "A csv file address containing the operative temperature results for each point for every hour of the analysis."],
11: ["adaptComfResult", "A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the analysis."],
12: ["degFromTargetResult", "A csv file address containing the a series of numbers indicating the degrees that a certain point is from the neutral temperature for every hour of the analysis."]
}

outputsDictPMV = {
    
0: ["readMe!", "..."],
1: ["===============", "..."],
2: ["radTempMtx", "A python matrix containing MRT data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
3: ["airTempMtx", "A python matrix containing air temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
4: ["SET_Mtx", "A python matrix containing standard effective temperature (SET) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
5: ["PPD_Mtx", "A python matrix containing percentage of people dissatisfied (PPD) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
6: ["PMV_Mtx", "A python matrix containing predicted mean vote (PMV) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
7: ["===============", "..."],
8: ["radTempResult", "A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis."],
9: ["airTempResult", "A csv file address containing the air temperature results for each point for every hour of the analysis."],
10: ["SET_Result", "A csv file address containing the standard effective temperature (SET) results for each point for every hour of the analysis."],
11: ["PPD_Result", "A csv file address containing the percentage of people dissatisfied (PPD) results indicating whether a certain point is comfortable for every hour of the analysis."],
12: ["PMV_Result", "A csv file address containing predicted mean vote (PMV) results indicating the distance that a certain point is from the neutral temperature for every hour of the analysis."]
}


def setDefaults(lb_defaultFolder, lb_preparation):
    #Set a default fileName.
    if fileName_ == None:
        fileName = 'unnamed'
    else: fileName = fileName_.strip()
    
    #Check the directory or set a default.
    if workingDir_: workingDir = lb_preparation.removeBlankLight(workingDir_)
    else: workingDir = lb_defaultFolder
    workingDir = os.path.join(workingDir, fileName, "ComfortAnalysis")
    workingDir = lb_preparation.makeWorkingDir(workingDir)
    
    
    #Check the HOYs.
    #Make the default analyisis period for the whole analysis if the user has not input one.
    checkData1 = True
    analysisPeriod = []
    HOYs = []
    if analysisPeriodOrHOY_ == []:
        analysisPeriod = [(1, 1, 1), (12, 31, 24)]
        HOYs = range(1,8761)
    else:
        #Check if the analysis period is an hour of the analysis or an HOY
        try:
            HOYs = [int(analysisPeriodOrHOY_[0])]
            if HOYs[0] < 1 or HOYs[0] > 8760:
                checkData1 = False
                warning = 'Hour of the analysis input for analysisPeriodOrHOY_ must be either a value between 1 and 8760.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            if checkData1 == True:
                d, m, t = lb_preparation.hour2Date(HOYs[0], True)
                analysisPeriod = [(m, d, t), (m, d, t)]
        except:
            try:
                HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriodOrHOY_, 1)
                analysisPeriod = analysisPeriodOrHOY_
            except:
                checkData1 = False
                warning = 'Invalid input for analysisPeriodOrHOY_.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Do a final check of everything.
    if checkData1 == True:
        checkData = True
    else: checkData = False
    
    
    return checkData, HOYs, analysisPeriod, fileName, workingDir


def manageOutput(comfortModel):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(13):
        if input > 7 and writeResultFile_ == False:
            ghenv.Component.Params.Output[input].NickName = "__________"
            ghenv.Component.Params.Output[input].Name = "."
            ghenv.Component.Params.Output[input].Description = " "
        elif comfortModel == "Adaptive":
            ghenv.Component.Params.Output[input].NickName = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictAdapt[input][1]
        elif comfortModel == "PMV":
            ghenv.Component.Params.Output[input].NickName = outputsDictPMV[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictPMV[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictPMV[input][1]
        else:
            ghenv.Component.Params.Output[input].NickName = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictAdapt[input][1]


def processPrevailOutdoorTemp(prevailingOutdoorTemp):
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
     
    #Check the _prevailingOutdoorTemp list and evaluate the contents.
    prevailTemp = []
    if prevailingOutdoorTemp[2] == 'Dry Bulb Temperature':
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[7:751])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[751:1423])/672)], 672))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[1423:2167])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[2167:2887])/720)], 720))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[2887:3631])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[3631:4351])/720)], 720))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[4351:5095])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[5095:5839])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[5839:6559])/720)], 720))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[6559:7303])/744)], 744))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[7303:8023])/720)], 720))
        prevailTemp.extend(duplicateData([float(sum(prevailingOutdoorTemp[8023:])/744)], 744))
    
    
    return prevailTemp


def calculatePointMRT(srfTempDict, testPtsViewFactor, hour):
    #Calculate the MRT for each point.
    pointMRTValues = []
    for zoneCount, pointList in enumerate(testPtsViewFactor):
        pointMRTValues.append([])
        for pointViewFactor in pointList:
            pointMRT = 0
            for srfCount, srfView in enumerate(pointViewFactor):
                path  = str([zoneCount,srfCount])
                weightedSrfTemp = srfView*(srfTempDict[path]["srfTemp"][hour])
                pointMRT = pointMRT+weightedSrfTemp
            pointMRTValues[zoneCount].append(pointMRT)
    
    
    return pointMRTValues


def calculateSolarAdjustedMRT(pointMRTValues, stepOfSimulation, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, lb_sunpath, lb_comfortModels):
    #Calculate the altitude and azimuth of the hour.
    d, m, t = lb_preparation.hour2Date(stepOfSimulation, True)
    lb_sunpath.solInitOutput(m+1, d, t)
    altitude = math.degrees(lb_sunpath.solAlt)
    azimuth = math.degrees(lb_sunpath.solAz)
    if altitude > 0:
        sunVec = lb_sunpath.sunReverseVectorCalc()
    else: sunVec = None
    
    #Assign the sun vector to a sky patch that aligns with the testPtBlockedVec list.
    vectorskyPatches = []
    
    for vecCount, vector in enumerate([sunVec]):
        
        if sunVec != None:
            intersected = False
            ray = rc.Geometry.Ray3d(rc.Geometry.Point3d.Origin, vector)
            for patchCount, patch in enumerate(skyPatchMeshes):
                if rc.Geometry.Intersect.Intersection.MeshRay(patch, ray) >= 0:
                    vectorskyPatches.append(patchCount)
                    intersected = True
            if intersected == False:
                vectorskyPatches.append(None)
        else:
            vectorskyPatches.append(None)
    
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
                #Check if the sunray is blocked.
                if vectorskyPatches[0] != None:
                    if testPtBlockedVec[zoneCount][pointCount][vectorskyPatches[0]] == 0: sunBlocked = True
                    else: sunBlocked = False
                else: sunBlocked = True
                
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


def getAirPointValue(airTempDict, testPtZoneWeights, hour):
    #Calculate the value for each point.
    pointValues = []
    for zoneCount, pointList in enumerate(testPtZoneWeights):
        pointValues.append([])
        for pointWeght in pointList:
            pointValue = 0
            for Count, weight in enumerate(pointWeght):
                path  = Count
                weightedPointVal = weight*(airTempDict[path]["airTemp"][hour])
                pointValue = pointValue+weightedPointVal
            pointValues[zoneCount].append(pointValue)
    
    return pointValues


def warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs):
    #Get a list of total heat gain for each of the grouped zones.
    #Get a list of total flow volume for each of the grouped zones.
    groupedHeatGains = []
    groupedFlowVol = []
    for zoneList in adjacentList:
        zoneHeatG = 0
        zoneFlowV = 0
        for val in zoneList:
            zoneHeatG += heatGainValues[val]
            zoneFlowV += flowVolValues[val]
        groupedHeatGains.append(zoneHeatG)
        groupedFlowVol.append(zoneFlowV)
    
    #Calculate the Archimedes numbers and the temperature change of the grouped zones.
    tempChanges = []
    archimedesNumbers = []
    archiNumWinScale = []
    for zoneCount in range(len(adjacentList)):
        if groupedHeatGains[zoneCount] > 0.0:
            try:
                tempChange = (groupedHeatGains[zoneCount])/(1.2*1012*groupedFlowVol[zoneCount])
                tempChanges.append(tempChange)
                
                archiNumberNum = (9.806*0.0034*groupedHeatGains[zoneCount])*(groupedWinCeilDiffs[zoneCount]*groupedWinCeilDiffs[zoneCount]*groupedWinCeilDiffs[zoneCount])
                archiNumberDenom = (1.2*1012*groupedFlowVol[zoneCount]*groupedFlowVol[zoneCount]*(groupedFlowVol[zoneCount]/groupedInletArea[zoneCount]))
                archiNumber = archiNumberNum/archiNumberDenom
                archimedesNumbers.append(archiNumber)
                
                archiNumWinScaleNum = (9.806*0.0034*groupedHeatGains[zoneCount])*(groupedGlzHeights[zoneCount]*groupedGlzHeights[zoneCount]*groupedGlzHeights[zoneCount])
                archiNumWinScale.append(archiNumWinScaleNum/archiNumberDenom)
            except:
                tempChanges.append(0)
                archimedesNumbers.append(0)
                archiNumWinScale.append(0)
        else:
            tempChanges.append(0)
            archimedesNumbers.append(0)
            archiNumWinScale.append(0)
    
    #Calculate the dimensionless temperature change over the room.
    dimTempDeltas = []
    dimInterfHeights = []
    cielTemps = []
    for zoneCount in range(len(adjacentList)):
        if archimedesNumbers[zoneCount] < 59 and archimedesNumbers[zoneCount] != 0:
            #Linear stratification profile.
            dimInterfHeights.append(0)
            dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            dimTempDeltas.append(dimensionlessTempDelta)
            cielTemps.append((dimensionlessTempDelta/2)*tempChanges[zoneCount])
        elif archimedesNumbers[zoneCount] != 0:
            #Two-Layer stratification profile.
            dimensionlessInterfHeight = 0.92 - (0.18 * math.log10(archimedesNumbers[zoneCount]))
            dimInterfHeights.append(dimensionlessInterfHeight)
            dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            if dimensionlessTempDelta > 0:
                dimTempDeltas.append(dimensionlessTempDelta)
                cielTemps.append(((dimensionlessTempDelta*dimensionlessInterfHeight)/2)*tempChanges[zoneCount])
            else:
                dimTempDeltas.append(0)
                cielTemps.append(0)
                dimInterfHeights.append(0)
        else:
            dimTempDeltas.append(0)
            cielTemps.append(0)
            dimInterfHeights.append(0)
    
    #Calculate the dimensionless temperature at the dimensionless height and convert to final temperature.
    for zoneCount, zone in enumerate(pointAirTempValues):
        if archimedesNumbers[zoneCount] < 59 and dimTempDeltas[zoneCount] != 0:
            #Linear stratification profile.
            cielTemp = cielTemps[zoneCount]
            dimTempDelta = dimTempDeltas[zoneCount]
            for ptCount, ptValue in enumerate(zone):
                ptTemp = ptValue + cielTemp - dimTempDelta*tempChanges[zoneCount]*(1-ptHeightWeights[zoneCount][ptCount])
                pointAirTempValues[zoneCount][ptCount] = ptTemp
        elif dimTempDeltas[zoneCount] != 0:
            #Two-Layer stratification profile.
            cielTemp = cielTemps[zoneCount]
            dimTempDelta = dimTempDeltas[zoneCount]
            dimInterHeight = dimInterfHeights[zoneCount]
            
            for ptCount, ptValue in enumerate(zone):
                if ptHeightWeights[zoneCount][ptCount] < dimInterHeight:
                    ptTemp = ptValue + cielTemp - dimTempDelta*tempChanges[zoneCount]*(dimInterHeight - ptHeightWeights[zoneCount][ptCount])
                else:
                    ptTemp = ptValue + cielTemp
                pointAirTempValues[zoneCount][ptCount] = ptTemp
        else: pass
    
    
    return pointAirTempValues

def createSrfDict(zoneSrfNames, nameKey, datakey, srfHeaders, srfNumbers):
    srfDict = {}
    for i in range(len(zoneSrfNames)):
        for srfindex in range(len(zoneSrfNames[i])):
            pathInt = [i,srfindex]
            path = str(pathInt)
            
            if not srfDict.has_key(path):
                srfDict[path] = {}
            
            srfDict[path][nameKey] = zoneSrfNames[pathInt[0]][pathInt[1]]
    
    #Figure out which surfaces in the dictionary correspond to the connected srfHeaders.
    for listCount, list in enumerate(srfHeaders):
        srfName = list[2].split(" for ")[-1]
        try: srfName = srfName.split(":")[0]
        except: pass
        for path in srfDict:
            if srfDict[path][nameKey].upper() == srfName:
                srfDict[path][datakey] = srfNumbers[listCount]
    
    return srfDict

def createZoneDict(testPtZoneNames, nameKey, datakey, zoneHeaders, zoneNumbers):
    zoneDict = {}
    for i in range(len(testPtZoneNames)):
        path = i
        if not zoneDict.has_key(path):
            zoneDict[path] = {}
        zoneDict[path][nameKey] = testPtZoneNames[path]
    
    #Figure out which zones in the dictionary correspond to the connected dataHeaders.
    for listCount, list in enumerate(zoneHeaders):
        zName = list[2].split(" for ")[-1]
        for path in zoneDict:
            if zoneDict[path][nameKey].upper() == zName:
                zoneDict[path][datakey] = zoneNumbers[listCount]
    
    return zoneDict

def computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride):
    #Figure out which zones are connected from the testPtZoneWeights.
    adjacentList = []
    adjacentNameList = []
    for falseZone in testPtZoneWeights:
        for pt in falseZone:
            ptAdjList = []
            ptNameList = []
            for zoneCount, zone in enumerate(pt):
                if zone != 0:
                    ptAdjList.append(zoneCount)
                    ptNameList.append(testPtZoneNames[zoneCount])
            if ptAdjList not in adjacentList: adjacentList.append(ptAdjList)
            if ptNameList not in adjacentNameList: adjacentNameList.append(ptNameList)
    
    #Compute the grouped window heights and zone heights for the stratification calculation
    groupedTotalVol = []
    groupedInletArea = []
    groupedInletAreaList = []
    groupedMinHeightsInit = []
    groupedMaxHeightsInit = []
    groupedGlzHeightsInit = []
    for zoneList in adjacentList:
        zoneTotV = 0
        inletA = 0
        inletAList = []
        minHeightList = []
        maxHeightList = []
        glzHeightList = []
        for val in zoneList:
            zoneTotV += zoneInletInfo[val][-2]
            inletA += zoneInletInfo[val][-1]
            inletAList.append(zoneInletInfo[val][-1])
            minHeightList.append(zoneInletInfo[val][0])
            maxHeightList.append(zoneInletInfo[val][1])
            glzHeightList.append(zoneInletInfo[val][2])
        if inletA != 0: groupedInletArea.append(inletA)
        else: groupedInletArea.append(0.0025*zoneTotV)
        groupedInletAreaList.append(inletAList)
        groupedMinHeightsInit.append(minHeightList)
        groupedMaxHeightsInit.append(maxHeightList)
        groupedGlzHeightsInit.append(glzHeightList)
    
    #Figure out what the height of the grouped zones should be and what the average height of the windows is.
    groupedZoneHeights = []
    groupedGlzHeights = []
    groupedWinCeilDiffs = []
    for zoneCount in range(len(adjacentList)):
        if len(groupedMinHeightsInit[zoneCount]) != 1:
            groupedMinHeightsInit[zoneCount].sort()
            minHeight = groupedMinHeightsInit[zoneCount][0]
            groupedMaxHeightsInit[zoneCount].sort()
            maxHeight = groupedMaxHeightsInit[zoneCount][-1]
            roomHeight = maxHeight - minHeight
            groupedZoneHeights.append(roomHeight)
            if inletHeightOverride == []:
                areaWeights = []
                for area in groupedInletAreaList[zoneCount]:
                    areaWeights.append(area/sum(groupedInletAreaList[zoneCount]))
                weightedGlzHeights = []
                for count, height in enumerate(groupedGlzHeightsInit[zoneCount]):
                    try:
                        weightedHeight = (height - minHeight)*areaWeights[count]
                        weightedGlzHeights.append(weightedHeight)
                    except:
                        weightedGlzHeights.append(0)
                weightedAvgGlzHeight = sum(weightedGlzHeights)
                groupedGlzHeights.append(weightedAvgGlzHeight)
                groupedWinCeilDiffs.append(roomHeight - weightedAvgGlzHeight)
            else:
                groupedGlzHeights.append(inletHeightOverride[zoneCount])
                groupedWinCeilDiffs.append(roomHeight - inletHeightOverride[zoneCount])
        else:
            roomHeight = groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0]
            groupedZoneHeights.append(roomHeight)
            if inletHeightOverride == []:
                if groupedGlzHeightsInit[zoneCount][0] != None: glzHeight = groupedGlzHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0]
                else: glzHeight = (groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0])/2
                groupedGlzHeights.append(glzHeight)
                groupedWinCeilDiffs.append(roomHeight - glzHeight)
            else:
                groupedGlzHeights.append(inletHeightOverride[zoneCount])
                groupedWinCeilDiffs.append(roomHeight - inletHeightOverride[zoneCount])
    
    
    return adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs


def mainAdapt(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, eightyPercentComf, mixedAirOverride, lb_preparation, lb_sunpath, lb_comfortModels):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    operativeTempMtx = ['Operative Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    adaptComfMtx = ['Adaptive Comfort;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    degFromTargetMtx = ['Degrees From Target;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Get the prevailing outdoor temperature for the whole analysis.
    prevailTemp = processPrevailOutdoorTemp(prevailingOutdoorTemp)
    
    #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
    srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
    
    #Create a meshed sky dome to assist with direct sunlight falling on occupants.
    skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
    skyPatchMeshes = []
    for patch in skyPatches:
        verts = patch.DuplicateVertices()
        if len(verts) == 4:
            patchBrep = rc.Geometry.Brep.CreateFromCornerPoints(verts[0], verts[1], verts[2], verts[3], sc.doc.ModelAbsoluteTolerance)
        else: patchBrep = patch
        skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patchBrep, rc.Geometry.MeshingParameters.Coarse)[0])
    
    #Initiate the sun vector calculator.
    lb_sunpath.initTheClass(float(latitude), 0.0, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
    
    #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
    airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
    
    #Compute grouped zone properties for air stratification purposes.
    adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
    
    #Run through every hour of the analysis to fill up the matrices.
    calcCancelled = False
    
    try:
        def climateMap(count):
            #Ability to cancel with Esc
            if gh.GH_Document.IsEscapeKeyDown(): assert False
            
            # Get the hour.
            hour = HOYs[count]
            
            #Select out the relevant air and surface temperatures.
            flowVolValues = []
            heatGainValues = []
            for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
            for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
            
            #Compute the radiant temperature.
            pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1)
            pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, lb_sunpath, lb_comfortModels)
            pointMRTValues = lb_preparation.flattenList(pointMRTValues)
            radTempMtx[count+1] = pointMRTValues
            
            #Compute the air temperature.
            pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, hour-1)
            if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs)
            pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
            airTempMtx[count+1] = pointAirTempValues
            
            #Compute the operative temperature.
            pointOpTempValues = []
            for ptCount, airTemp in enumerate(pointAirTempValues):
                pointOpTempValues.append((airTemp+pointMRTValues[ptCount])/2)
            operativeTempMtx[count+1] = pointOpTempValues
            
            #Compute the adaptive comfort and deg from target.
            adaptComfPointValues = []
            degFromTargetPointValues = []
            
            for ptCount, airTemp in enumerate(pointAirTempValues):
                comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(airTemp, pointMRTValues[ptCount], prevailTemp[hour-1], 0.05, eightyPercentComf)
                adaptComfPointValues.append(int(comf))
                degFromTargetPointValues.append(distFromTarget)
            
            adaptComfMtx[count+1] = adaptComfPointValues
            degFromTargetMtx[count+1] = degFromTargetPointValues
    except:
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        calcCancelled = True
    
    #Create placeholders for all of the hours.
    
    for hour in HOYs:
        radTempMtx.append(0)
        airTempMtx.append(0)
        operativeTempMtx.append(0)
        adaptComfMtx.append(0)
        degFromTargetMtx.append(0)
    
    #Run through every hour of the analysis to fill up the matrices.
    try:
        if parallel_ == True and len(HOYs) != 1:
            tasks.Parallel.ForEach(range(len(HOYs)), climateMap)
        else:
            for hour in range(len(HOYs)):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                climateMap(hour)
    except:
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        calcCancelled = True
    
    if calcCancelled == False:
        return radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx
    else:
        return -1

def mainPMV(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride, lb_preparation, lb_sunpath, lb_comfortModels):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    SET_Mtx = ['Standard Effective Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PPD_Mtx = ['Percentage of People Dissatisfied;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PMV_Mtx = ['Predicted Mean Vote;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
    srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
    
    #Create a meshed sky dome to assist with direct sunlight falling on occupants.
    skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
    skyPatchMeshes = []
    for patch in skyPatches:
        verts = patch.DuplicateVertices()
        if len(verts) == 4:
            patchBrep = rc.Geometry.Brep.CreateFromCornerPoints(verts[0], verts[1], verts[2], verts[3], sc.doc.ModelAbsoluteTolerance)
        else: patchBrep = patch
        skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patchBrep, rc.Geometry.MeshingParameters.Coarse)[0])
    
    #Initiate the sun vector calculator.
    lb_sunpath.initTheClass(float(latitude), 0.0, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
    
    #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
    airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
    relHumidDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", relHumidDataHeaders, relHumidDataNumbers)
    
    #Compute grouped zone properties for air stratification purposes.
    adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
    
    #Run through every hour of the analysis to fill up the matrices.
    calcCancelled = False
    
    try:
        def climateMapPMV(count):
            #Ability to cancel with Esc
            if gh.GH_Document.IsEscapeKeyDown(): assert False
            
            # Get the hour.
            hour = HOYs[count]
            
            #Select out the relevant air and surface temperatures.
            flowVolValues = []
            heatGainValues = []
            for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
            for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
            
            #Compute the radiant temperature.
            pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1)
            pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, lb_sunpath, lb_comfortModels)
            pointMRTValues = lb_preparation.flattenList(pointMRTValues)
            radTempMtx[count+1] = pointMRTValues
            
            #Compute the air temperature.
            pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, hour-1)
            if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs)
            pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
            airTempMtx[count+1] = pointAirTempValues
            
            #Compute the relative humidity.
            pointRelHumidValues = getAirPointValue(relHumidDict, testPtZoneWeights, hour-1)
            pointRelHumidValues = lb_preparation.flattenList(pointRelHumidValues)
            
            #Compute the SET and PMV comfort.
            setPointValues = []
            ppdPointValues = []
            pmvPointValues = []
            
            for ptCount, airTemp in enumerate(pointAirTempValues):
                pmv, ppd, set, taAdj, coolingEffect = lb_comfortModels.comfPMVElevatedAirspeed(airTemp, pointMRTValues[ptCount], 0.05, pointRelHumidValues[ptCount], metabolicRate[hour-1], clothingLevel[hour-1], 0.0)
                
                setPointValues.append(set)
                ppdPointValues.append(ppd)
                pmvPointValues.append(pmv)
            
            SET_Mtx[count+1] = setPointValues
            PPD_Mtx[count+1] = ppdPointValues
            PMV_Mtx[count+1] = pmvPointValues
    except:
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        calcCancelled = True
    
    #Create placeholders for all of the hours.
    for hour in HOYs:
        radTempMtx.append(0)
        airTempMtx.append(0)
        SET_Mtx.append(0)
        PPD_Mtx.append(0)
        PMV_Mtx.append(0)
    
    #Run through every hour of the analysis to fill up the matrices.
    try:
        if parallel_ == True and len(HOYs) != 1:
            tasks.Parallel.ForEach(range(len(HOYs)), climateMapPMV)
        else:
            for hour in range(len(HOYs)):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                climateMapPMV(hour)
    except:
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        calcCancelled = True
    
    if calcCancelled == False:
        return radTempMtx, airTempMtx, SET_Mtx, PPD_Mtx, PMV_Mtx
    else:
        return -1


def writeCSVAdapt(lb_preparation, directory, fileName, radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx):
    #Find out the number of values in each hour.
    valLen = len(radTempMtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(directory)) 
    
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


def writeCSVPMV(lb_preparation, directory, fileName, radTempMtx, airTempMtx, SET_Mtx, PPD_Mtx, PMV_Mtx):
    #Find out the number of values in each hour.
    valLen = len(radTempMtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(directory)) 
    
    #Create a csv Files.
    radTempFile = fileName + "RadiantTemp.csv"
    airTempFile = fileName + "AirTemp.csv"
    SETFile = fileName + "SET.csv"
    PPDFile = fileName + "PPD.csv"
    PMVFile = fileName + "PMV.csv"
    
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
    SET_Result = os.path.join(workingDir, SETFile)
    opCSVfile = open(SET_Result, 'wb')
    for lineCount, line in enumerate(SET_Mtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            opCSVfile.write(lineStr)
        else: opCSVfile.write(line + "\n")
    opCSVfile.close()
    
    #Write the adaptive comfort result file.
    PPD_Result = os.path.join(workingDir, PPDFile)
    comfCSVfile = open(PPD_Result, 'wb')
    for lineCount, line in enumerate(PPD_Mtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            comfCSVfile.write(lineStr)
        else: comfCSVfile.write(line + "\n")
    comfCSVfile.close()
    
    #Write the deg from target result file.
    PMV_Result = os.path.join(workingDir, PMVFile)
    degCSVfile = open(PMV_Result, 'wb')
    for lineCount, line in enumerate(PMV_Mtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            degCSVfile.write(lineStr)
        else: degCSVfile.write(line + "\n")
    degCSVfile.close()
    
    
    return radTempResult, airTempResult, SET_Result, PPD_Result, PMV_Result



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


#Check the type of comfort analysis recipe connected.
recipeRecognized = False
comfortModel = None
if len(_comfAnalysisRecipe) > 0:
    if len(_comfAnalysisRecipe) == 31 and _comfAnalysisRecipe[0] == "Adaptive":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, eightyPercentComf, mixedAirOverride = _comfAnalysisRecipe
        recipeRecognized = True
    elif len(_comfAnalysisRecipe) == 36 and _comfAnalysisRecipe[0] == "PMV":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride = _comfAnalysisRecipe
        recipeRecognized = True
    else:
        warning = 'Comfort recipe not recognized.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)

#Manage the input and output.
manageOutput(comfortModel)

#Check the data input.
checkData = False
if recipeRecognized == True and checkLB == True:
    checkData, HOYs, analysisPeriod, fileName, directory = setDefaults(lb_defaultFolder, lb_preparation)

if checkData == True and _runIt == True:
    if comfortModel == "Adaptive":
        result = mainAdapt(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, eightyPercentComf, mixedAirOverride, lb_preparation, lb_sunpath, lb_comfortModels)
        if result != -1:
            radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx = result
            if writeResultFile_ != False:
                radTempResult, airTempResult, operativeTempResult, adaptComfResult, degFromTargetResult = writeCSVAdapt(lb_preparation, directory, fileName, radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx)
    elif comfortModel == "PMV":
        result = mainPMV(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride, lb_preparation, lb_sunpath, lb_comfortModels)
        if result != -1:
            radTempMtx, airTempMtx, SET_Mtx, PPD_Mtx, PMV_Mtx = result
            if writeResultFile_ != False:
                radTempResult, airTempResult, SET_Result, PPD_Result, PMV_Result = writeCSVPMV(lb_preparation, directory, fileName, radTempMtx, airTempMtx, SET_Mtx, PPD_Mtx, PMV_Mtx)
