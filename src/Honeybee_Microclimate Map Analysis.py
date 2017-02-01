# This component runs an annual comfort assessment off of EnergyPlus results
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component runs an annual comfort assessment off of EnergyPlus results and write all values into csv files.
The results in these files can be used for creating indoor comfort maps.
-
Provided by Honeybee 0.0.60
    
    Args:
        _comfAnalysisRecipe: A comfort analysis recipe out of one of the comfort recipe component.
        =============: ...
        workingDir_: An optional working directory on your system. Default is set to C:\Ladybug
        fileName_: An optional file name for the result files as a string.
        =============: ...
        analysisPeriodOrHOY_: An analysis period from the 'Ladybug Analysis Period' component or an hour of the analysis between 1 and 8760 for which you want to conduct the analysis. If no value is connected here, the component will run for only noon on the winter solstice.  A single HOY is used by default as longer analysis periods can take a very long time.
        =============: ...
        writeResultFile_: Set to 1 or 'True' to have the component write all results into CSV result files and set to 0 or 'False' to not have the component write these files.  The default is set to 'True' as these simulations can be long and you usually want a copy of your results.  You may want to set it to 'False' if you are just scrolling through key hours and want the fastest run possible.  Set to 2 if you want the component to only write the results of the last two matrices (comfort results and degFromTarget).
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

ghenv.Component.Name = "Honeybee_Microclimate Map Analysis"
ghenv.Component.NickName = 'MicroclimateMap'
ghenv.Component.Message = 'VER 0.0.60\nOCT_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nJUN_07_2016
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
5: ["PMVComfMtx", "A python matrix containing PMV comfort data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
6: ["PMV_Mtx", "A python matrix containing predicted mean vote (PMV) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
7: ["===============", "..."],
8: ["radTempResult", "A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis."],
9: ["airTempResult", "A csv file address containing the air temperature results for each point for every hour of the analysis."],
10: ["SET_Result", "A csv file address containing the standard effective temperature (SET) results for each point for every hour of the analysis."],
11: ["PMVComfResult", "A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the analysis."],
12: ["PMV_Result", "A csv file address containing predicted mean vote (PMV) results indicating the distance that a certain point is from the neutral temperature for every hour of the analysis."]
}

outputsDictUTCI = {
    
0: ["readMe!", "..."],
1: ["===============", "..."],
2: ["radTempMtx", "A python matrix containing MRT data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
3: ["airTempMtx", "A python matrix containing air temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
4: ["UTCI_Mtx", "A python matrix containing universal thermal climate index (UTCI) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
5: ["OutdoorComfMtx", "A python matrix containing outdoor (UTCI) comfort data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
6: ["DegFromNeutralMtx", "A python matrix containing the degrees from the neutral UTCI value of 20 C for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
7: ["===============", "..."],
8: ["radTempResult", "A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis."],
9: ["airTempResult", "A csv file address containing the air temperature results for each point for every hour of the analysis."],
10: ["UTCI_Result", "A csv file address containing universal thermal climate index (UTCI) results for each point for every hour of the analysis."],
11: ["OutdoorComfResult", "A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the analysis."],
12: ["DegFromNeutralResult", "A csv file address containing the degrees from the neutral UTCI value of 20 C indicating the distance that a certain point is from the neutral temperature for every hour of the analysis."]
}

outputsDictPET = {
    
0: ["readMe!", "..."],
1: ["===============", "..."],
2: ["radTempMtx", "A python matrix containing MRT data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
3: ["airTempMtx", "A python matrix containing air temperature data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
4: ["PET_Mtx", "A python matrix containing physiological equivalent temperature (PET) data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
5: ["PET_ComfMtx", "A python matrix containing PET comfort data for every hour of the analysis to be plugged into the 'Honeybee_Visualize Annual Comfort Results' component."],
6: ["PET_CategoryMtx", "A python matrix containing the categories of PET. These are either: -4 = Very Cold, -3 = Cold, -2 = Cool, -1 = Slightly Cool, 0 = Comfortable, 1 = Slightly Warm, 2 = Warm, 3 = Hot, 4 = Very Hot"],
7: ["===============", "..."],
8: ["radTempResult", "A csv file address containing the radiant temperature resultsfor each point for every hour of the analysis."],
9: ["airTempResult", "A csv file address containing the air temperature results for each point for every hour of the analysis."],
10: ["PET_Result", "A csv file address containing physiological equivalent temperature (PET) results for each point for every hour of the analysis."],
11: ["PETComfResult", "A csv file address containing the a series of 0's and 1's indicating whether a certain point is comfortable for every hour of the analysis."],
12: ["PETCategoryResult", "A csv file address containing the categories of PET.   These are either: -4 = Very Cold, -3 = Cold, -2 = Cool, -1 = Slightly Cool, 0 = Comfortable, 1 = Slightly Warm, 2 = Warm, 3 = Hot, 4 = Very Hot"]
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
        analysisPeriod = [(12, 21, 12), (12, 21, 12)]
        HOYs = [8508]
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
                analysisPeriod = [(m+1, d, t), (m+1, d, t)]
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
        if input > 7 and writeResultFile_ == 0:
            ghenv.Component.Params.Output[input].NickName = "__________"
            ghenv.Component.Params.Output[input].Name = "."
            ghenv.Component.Params.Output[input].Description = " "
        elif input > 7 and input < 11 and writeResultFile_ == 2:
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
        elif comfortModel == "UTCI":
            ghenv.Component.Params.Output[input].NickName = outputsDictUTCI[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictUTCI[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictUTCI[input][1]
        elif comfortModel == "PET":
            ghenv.Component.Params.Output[input].NickName = outputsDictPET[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictPET[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictPET[input][1]
        else:
            ghenv.Component.Params.Output[input].NickName = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Name = outputsDictAdapt[input][0]
            ghenv.Component.Params.Output[input].Description = outputsDictAdapt[input][1]

#Define a function to duplicate data
def duplicateData(data, calcLength):
    dupData = []
    for count in range(calcLength):
        dupData.append(data[0])
    return dupData


def processPrevailOutdoorTemp(prevailingOutdoorTemp, avgMonthOrRunMean):
    #Check the prevailingOutdoorTemp list and evaluate the contents.
    prevailTemp = []
    coldTimes = []
    if avgMonthOrRunMean == True:
        #Calculate the monthly average temperatures.
        monthPrevailList = [float(sum(prevailingOutdoorTemp[7:751])/744), float(sum(prevailingOutdoorTemp[751:1423])/672), float(sum(prevailingOutdoorTemp[1423:2167])/744), float(sum(prevailingOutdoorTemp[2167:2887])/720), float(sum(prevailingOutdoorTemp[2887:3631])/744), float(sum(prevailingOutdoorTemp[3631:4351])/720), float(sum(prevailingOutdoorTemp[4351:5095])/744), float(sum(prevailingOutdoorTemp[5095:5839])/744), float(sum(prevailingOutdoorTemp[5839:6559])/720), float(sum(prevailingOutdoorTemp[6559:7303])/744), float(sum(prevailingOutdoorTemp[7303:8023])/720), float(sum(prevailingOutdoorTemp[8023:])/744)]
        hoursInMonth = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
        for monthCount, monthPrevailTemp in enumerate(monthPrevailList):
            prevailTemp.extend(duplicateData([monthPrevailTemp], hoursInMonth[monthCount]))
            if monthPrevailTemp < 10: coldTimes.append(monthCount)
    else:
        #Calculate a running mean temperature.
        alpha = 0.8
        divisor = 1 + alpha + math.pow(alpha,2) + math.pow(alpha,3) + math.pow(alpha,4) + math.pow(alpha,5)
        dividend = (sum(prevailingOutdoorTemp[-24:-1] + [prevailingOutdoorTemp[-1]])/24) + (alpha*(sum(prevailingOutdoorTemp[-48:-24])/24)) + (math.pow(alpha,2)*(sum(prevailingOutdoorTemp[-72:-48])/24)) + (math.pow(alpha,3)*(sum(prevailingOutdoorTemp[-96:-72])/24)) + (math.pow(alpha,4)*(sum(prevailingOutdoorTemp[-120:-96])/24)) + (math.pow(alpha,5)*(sum(prevailingOutdoorTemp[-144:-120])/24))
        startingTemp = dividend/divisor
        if startingTemp < 10: coldTimes.append(0)
        outdoorTemp = prevailingOutdoorTemp[7:]
        startingMean = sum(outdoorTemp[:24])/24
        dailyRunMeans = [startingTemp]
        dailyMeans = [startingMean]
        prevailTemp.extend(duplicateData([startingTemp], 24))
        startHour = 24
        for count in range(364):
            dailyMean = sum(outdoorTemp[startHour:startHour+24])/24
            dailyRunMeanTemp = ((1-alpha)*dailyMeans[-1]) + alpha*dailyRunMeans[-1]
            if dailyRunMeanTemp < 10: coldTimes.append(count+1)
            prevailTemp.extend(duplicateData([dailyRunMeanTemp], 24))
            dailyRunMeans.append(dailyRunMeanTemp)
            dailyMeans.append(dailyMean)
            startHour +=24
    
    
    return prevailTemp, coldTimes


def calculatePointMRT(srfTempDict, testPtsViewFactor, hour, originalHour, outdoorClac, outSrfTempDict, outdoorNonSrfViewFac, prevailingOutdoorTemp):
    #Calculate the MRT for each point.
    pointMRTValues = []
    for zoneCount, pointList in enumerate(testPtsViewFactor):
        if outdoorClac == False or zoneCount != len(testPtsViewFactor)-1:
            pointMRTValues.append([])
            for pointViewFactor in pointList:
                pointMRT = 0
                for srfCount, srfView in enumerate(pointViewFactor):
                    path  = str([zoneCount,srfCount])
                    weightedSrfTemp = srfView*(srfTempDict[path]["srfTemp"][hour])
                    pointMRT = pointMRT+weightedSrfTemp
                pointMRTValues[zoneCount].append(round(pointMRT, 3))
        else:
            pointMRTValues.append([])
            for ptCount, pointViewFactor in enumerate(pointList):
                pointMRT = 0
                for srfCount, srfView in enumerate(pointViewFactor):
                    path  = str([zoneCount,srfCount])
                    weightedSrfTemp = srfView*(outSrfTempDict[path]["srfTemp"][hour])
                    pointMRT = pointMRT+weightedSrfTemp
                weightedSrfTemp = outdoorNonSrfViewFac[ptCount]*prevailingOutdoorTemp[originalHour]
                pointMRT = pointMRT+weightedSrfTemp
                pointMRT = pointMRT / (sum(pointViewFactor) + outdoorNonSrfViewFac[ptCount])
                pointMRTValues[zoneCount].append(round(pointMRT, 3))
    
    return pointMRTValues

def computeHourShadeDrawing(hour, testPtSkyView, testPtBlockedVec, winShdDict, testPtBlockName, outdoorClac):
    #Build a new testPtBlockedVec that checks with the window transmissivity status.
    newTestPtBlockedVec = []
    newTestPtSkyView = []
    for zoneCount, zone in enumerate(testPtBlockedVec):
        newTestPtBlockedVec.append([])
        newTestPtSkyView.append([])
        for ptCount, vecList in enumerate(zone):
            newVecList = []
            for vecCount, transmiss in enumerate(vecList):
                if transmiss == 0: newVecList.append(transmiss)
                else:
                    newTransmissWinList = testPtBlockName[zoneCount][ptCount][vecCount]
                    transFactor = 1
                    try:
                        for window in newTransmissWinList:
                            transFactor = transFactor * winShdDict[window][hour-1]
                    except: pass
                    newVecList.append(transFactor)
            newTestPtBlockedVec[zoneCount].append(newVecList)
            newTestPtSkyView[zoneCount].append(sum(newVecList)/len(newVecList))
    
    return newTestPtSkyView, newTestPtBlockedVec

def computeSkyTemp(La):
    # formula by Man-ENvironment heat EXchange model (MENEX_2005)
    skyTemp = (((La) / (0.95*5.667*(10**(-8))))**(0.25)) - 273
    
    return skyTemp

def calculateSolarAdjustedMRT(pointMRTValues, stepOfSimulation, originalHour, diffSolarRad, directSolarRad, globHorizRadList, count, sunVecInfo, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, outHorizInfrared, lb_comfortModels):
    #Pull out the correct sun vector.
    sunVec = sunVecInfo[0][count]
    altitude = sunVecInfo[1][count]
    azimuth = sunVecInfo[2][count]
    
    #Assign the sun vector to a sky patch that aligns with the testPtBlockedVec list.
    vectorskyPatches = []
    
    if sunVec != None:
        intersected = False
        ray = rc.Geometry.Ray3d(rc.Geometry.Point3d.Origin, sunVec)
        for patchCount, patch in enumerate(skyPatchMeshes):
            if rc.Geometry.Intersect.Intersection.MeshRay(patch, ray) >= 0:
                vectorskyPatches.append(patchCount)
                intersected = True
        if intersected == False:
            vectorskyPatches.append(None)
    else:
        vectorskyPatches.append(None)
    
    
    ##Calculate the diffuse, direct, and global horizontal components of the solar radiation at the hour.
    diffRad = diffSolarRad[originalHour-1]
    dirNormRad = directSolarRad[originalHour-1]
    globHorizRad = globHorizRadList[originalHour-1]
    outdoorHorizInfrared = outHorizInfrared[originalHour-1]
    
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
    
    # If outdoor conditions are requested, then compute the sky temperature.
    if outdoorClac == True:
        skyTemp = computeSkyTemp(outdoorHorizInfrared)
    
    #Compute the solar adjusted temperature for each point.
    solarAdjustedPointMRTValues = []
    if sunVec != None:
        for zoneCount, zonePtsList in enumerate(pointMRTValues):
            if zoneHasWindows[zoneCount] != 0:
                solarAdjustedPointMRTValues.append([])
                for pointCount, pointMRT in enumerate(zonePtsList):
                    #Check if the sunray is blocked.
                    if vectorskyPatches[0] != None:
                        if testPtBlockedVec[zoneCount][pointCount][vectorskyPatches[0]] == 0: sunBlocked = True
                        else: sunBlocked = False
                    else: sunBlocked = True
                    
                    #If the ray was not blocked, then adjust then get rid of direct solar radiation.
                    #Note that, while the direct radiation is multiplied by the specific window transmissivity here, the diffuse window transmissivity is already accounted for in the sky view.
                    if sunBlocked == True:
                        dirRadFinal = 0.0
                        globHorizRadFinal = diffRad
                    else:
                        dirRadFinal = dirNormRad*(testPtBlockedVec[zoneCount][pointCount][vectorskyPatches[0]])
                        globHorizRadFinal = globHorizRad
                    
                    if outdoorClac == False or zoneCount != len(pointMRTValues)-1:
                        hourERF = ((0.5*fracEff*testPtSkyView[zoneCount][pointCount]*(diffRad + (globHorizRadFinal*floorR[zoneCount][pointCount]))+ (fracEff*ProjAreaFac*dirRadFinal))*winTrans[originalHour-1])*(cloA/0.95)
                        mrtDelt = (hourERF/(fracEff*radTransCoeff))
                        hourMRT = mrtDelt + pointMRT
                    else:
                        hourERF = ((0.5*fracEff*testPtSkyView[zoneCount][pointCount]*(diffRad + (globHorizRadFinal*floorR[zoneCount][pointCount]))+ (fracEff*ProjAreaFac*dirRadFinal)))*(cloA/0.95)
                        mrtDelt = (hourERF/(fracEff*radTransCoeff))
                        hourMRT = mrtDelt + (skyTemp*(testPtSkyView[zoneCount][pointCount]/2) + pointMRT*(1-(testPtSkyView[zoneCount][pointCount]/2)))
                    
                    solarAdjustedPointMRTValues[zoneCount].append(round(hourMRT, 3))
            else:
                solarAdjustedPointMRTValues.append([])
                for pointCount, pointMRT in enumerate(zonePtsList):
                    solarAdjustedPointMRTValues[zoneCount].append(round(pointMRT, 3))
    else:
        solarAdjustedPointMRTValues = pointMRTValues
    
    return solarAdjustedPointMRTValues


def getAirPointValue(airTempDict, testPtZoneWeights, testPtsViewFactor, hour, originalHour, outdoorClac, prevailingOutdoorTemp):
    #Calculate the value for each point.
    pointValues = []
    for zoneCount, pointList in enumerate(testPtsViewFactor):
        if outdoorClac == False or zoneCount != len(testPtsViewFactor)-1:
            pointValues.append([])
            for pointWeght in testPtZoneWeights[zoneCount]:
                pointValue = 0
                for Count, weight in enumerate(pointWeght):
                    path  = Count
                    weightedPointVal = weight*(airTempDict[path]["airTemp"][hour])
                    pointValue = pointValue+weightedPointVal
                pointValues[zoneCount].append(round(pointValue, 3))
        else:
            pointValues.append([])
            for pointWeght in pointList:
                pointValue = prevailingOutdoorTemp[originalHour]
                pointValues[zoneCount].append(round(pointValue, 3))
    
    return pointValues


def warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, outdoorClac, prevailingOutdoorTemp):
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
            try: dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            except: dimensionlessTempDelta = 0.58
            dimTempDeltas.append(dimensionlessTempDelta)
            cielTemps.append((dimensionlessTempDelta/2)*tempChanges[zoneCount])
        elif archimedesNumbers[zoneCount] != 0:
            #Two-Layer stratification profile.
            dimensionlessInterfHeight = 0.92 - (0.18 * math.log10(archimedesNumbers[zoneCount]))
            dimInterfHeights.append(dimensionlessInterfHeight)
            
            try: dimensionlessTempDelta = 0.58 - (0.14 * math.log10(archiNumWinScale[zoneCount]))
            except: dimensionlessTempDelta = 0
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
        if len(zone) != 0:
            if outdoorClac == False or zoneCount != len(pointAirTempValues)-1:
                if archimedesNumbers[zoneCount] < 59 and dimTempDeltas[zoneCount] != 0:
                    #Linear stratification profile.
                    cielTemp = cielTemps[zoneCount]
                    dimTempDelta = dimTempDeltas[zoneCount]
                    for ptCount, ptValue in enumerate(zone):
                        ptTemp = ptValue + cielTemp - dimTempDelta*tempChanges[zoneCount]*(1-ptHeightWeights[zoneCount][ptCount])
                        pointAirTempValues[zoneCount][ptCount] = round(ptTemp, 3)
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
                        pointAirTempValues[zoneCount][ptCount] = round(ptTemp, 3)
                else: pass
            else: pass
        else:
            pass
    
    
    return pointAirTempValues

def createShdDict(shdHeaders, shdNumbers, zoneWindowTransmiss, zoneWindowNames):
    #Create the dictionary and a starting calculation length.
    shdDict = {}
    calcLen = 1
    
    #Add any windows with changing transmittance to the list.
    for headerCt, header in enumerate(shdHeaders):
        windowName = header[2].split(" for ")[-1].split(":")[0].upper()
        shdDict[windowName] = shdNumbers[headerCt]
        calcLen = len(shdNumbers[headerCt])
    
    #Add any windows with static transmittance to the list.
    for zC, zone in enumerate(zoneWindowNames):
        for winCt, win in enumerate(zone):
            if not shdDict.has_key(win.upper()):
                shdDict[win.upper()] = duplicateData([zoneWindowTransmiss[zC][winCt]], calcLen)
    
    return shdDict

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
        foundIt = False
        for path in srfDict:
            if srfDict[path][nameKey].upper() == srfName:
                srfDict[path][datakey] = srfNumbers[listCount]
                foundIt = True
        if foundIt == False:
            print "Surface temperature for Surface: " + srfName + " not found in the EP results."
    
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
    
    if len(adjacentList) != len(testPtZoneWeights):
        for zonecount, zoneList in enumerate(testPtZoneWeights):
            if zoneList == []:
                adjacentList.insert(zonecount, [])
                adjacentNameList.insert(zonecount, [])
    
    #Compute the grouped window heights and zone heights for the stratification calculation
    groupedTotalVol = []
    groupedTotalVolList = []
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
        volList = []
        for val in zoneList:
            zoneTotV += zoneInletInfo[val][-2]
            volList.append(zoneInletInfo[val][-2])
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
        groupedTotalVol.append(zoneTotV)
        groupedTotalVolList.append(volList)
    
    #Figure out what the height of the grouped zones should be and what the average height of the windows is.
    groupedZoneHeights = []
    groupedGlzHeights = []
    groupedWinCeilDiffs = []
    for zoneCount in range(len(adjacentList)):
        if len(groupedMinHeightsInit[zoneCount]) != 0:
            if len(groupedMinHeightsInit[zoneCount]) != 1:
                groupedMinHeightsInit[zoneCount].sort()
                minHeight = groupedMinHeightsInit[zoneCount][0]
                groupedMaxHeightsInit[zoneCount].sort()
                maxHeight = groupedMaxHeightsInit[zoneCount][-1]
                roomHeight = maxHeight - minHeight
                groupedZoneHeights.append(roomHeight)
                if inletHeightOverride == []:
                    areaWeights = []
                    for areaCount, area in enumerate(groupedInletAreaList[zoneCount]):
                        try:
                            areaWeights.append(area/sum(groupedInletAreaList[zoneCount]))
                        except:
                            areaWeights.append(groupedTotalVolList[zoneCount][areaCount]/groupedTotalVol[zoneCount])
                    weightedGlzHeights = []
                    for count, height in enumerate(groupedGlzHeightsInit[zoneCount]):
                        try:
                            weightedHeight = (height)*areaWeights[count]
                            weightedGlzHeights.append(weightedHeight)
                        except:
                            weightedGlzHeights.append(0)
                    weightedAvgGlzHeight = sum(weightedGlzHeights)
                    if weightedAvgGlzHeight == 0:
                        #If the glazing height is 0, this means that the grouped zones have no windows so take the average height of the zone.
                        weightedAvgGlzHeight = roomHeight*0.5
                    groupedGlzHeights.append(weightedAvgGlzHeight - minHeight)
                    groupedWinCeilDiffs.append(maxHeight - weightedAvgGlzHeight)
                else:
                    groupedGlzHeights.append(inletHeightOverride[zoneCount] - minHeight)
                    groupedWinCeilDiffs.append(maxHeight - inletHeightOverride[zoneCount])
            else:
                roomHeight = groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0]
                groupedZoneHeights.append(roomHeight)
                if inletHeightOverride == []:
                    if groupedGlzHeightsInit[zoneCount][0] != None:
                        glzHeight = groupedGlzHeightsInit[zoneCount][0]
                    else: glzHeight = (groupedMaxHeightsInit[zoneCount][0] - groupedMinHeightsInit[zoneCount][0])/2
                    groupedGlzHeights.append(glzHeight - groupedMinHeightsInit[zoneCount][0])
                    groupedWinCeilDiffs.append(groupedMaxHeightsInit[zoneCount][0] - glzHeight)
                else:
                    groupedGlzHeights.append(inletHeightOverride[zoneCount] - groupedMinHeightsInit[zoneCount][0])
                    groupedWinCeilDiffs.append(groupedMaxHeightsInit[zoneCount][0] - inletHeightOverride[zoneCount])
        else:
            groupedZoneHeights.append(0)
            groupedGlzHeights.append(0)
            groupedWinCeilDiffs.append(0)
    
    
    return adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, groupedTotalVol


def mainAdapt(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, ASHRAEorEN, comfClass, avgMonthOrRunMean, levelOfConditioning, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, dataAnalysisPeriod, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, outHorizInfrared, northAngle, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    operativeTempMtx = ['Operative Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    adaptComfMtx = ['Adaptive Thermal Comfort Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    degFromTargetMtx = ['Degrees From Target;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Check the data anlysis period and subtract the start day from each of the HOYs.
    originalHOYs = []
    if dataAnalysisPeriod != [(1,1,1),(12,31,24)]:
        FinalHOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod(dataAnalysisPeriod, 1)
        for hCount, hour in enumerate(HOYs):
            originalHOYs.append(hour)
            if hour - FinalHOYs[0] >= 0: HOYs[hCount] = hour - FinalHOYs[0]
            else: HOYs[hCount] = hour - FinalHOYs[0] + 8760
    else: FinalHOYs = originalHOYs = HOYs
    
    #Check to be sure that the requested analysis period and the analysis period of the connected data align.
    periodsAlign = True
    hrStart = originalHOYs[0]
    hrEnd = originalHOYs[-1]
    if hrStart in FinalHOYs and hrEnd in FinalHOYs: pass
    else: periodsAlign = False
    if periodsAlign == False:
        warning = 'The analysis period of the energy simulation data and the analysisPeriodOrHOY_ plugged into this component do not align.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    else:
        #Create placeholders for all of the hours.
        months = []
        dayNums = []
        for hour in HOYs:
            radTempMtx.append(0)
            airTempMtx.append(0)
            operativeTempMtx.append(0)
            adaptComfMtx.append(0)
            degFromTargetMtx.append(0)
            d, m, t = lb_preparation.hour2Date(hour, True)
            if m not in months: months.append(m)
            if avgMonthOrRunMean == False:
                day = int(lb_preparation.getJD(m, d))
                if day not in dayNums: dayNums.append(day)
        
        #Get the prevailing outdoor temperature for the whole analysis.
        prevailTemp, coldTimes = processPrevailOutdoorTemp(prevailingOutdoorTemp, avgMonthOrRunMean)
        
        #Check to see if there are any times when the prevailing temperature is too cold and give a comment that we are using a non-standard model.
        monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        if ASHRAEorEN == True: modelName = "ASHRAE 55"
        else: modelName = "EN-15251"
        if coldTimes != []:
            if avgMonthOrRunMean == True:
                coldMsg = "The following months were too cold for the official " + modelName + " standard and have used a correlation from recent research:"
                for month in months:
                    if month in coldTimes:
                        coldMsg += '\n'
                        coldMsg += monthNames[month]
                print coldMsg
            else:
                totalColdInPeriod = []
                for day in dayNums:
                    if day in coldTimes: totalColdInPeriod.append(day)
                if totalColdInPeriod != []:
                    coldMsg = "There were " + str(len(totalColdInPeriod)) + " days of the analysis period when the outdoor temperatures were too cold for the official " + modelName + "standard. \n A correlation from recent research has been used in these cases."
                    print coldMsg
        
        
        #Make sure that the EPW Data does not include headers.
        prevailingOutdoorTemp = prevailingOutdoorTemp[7:]
        outWindSpeed = outWindSpeed[7:]
        
        #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
        srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
        
        #Make a dictionary for outdoor srfNames and temperatures.
        if outdoorClac == True:
            outSrfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", outSrfTempHeaders, outSrfTempNumbers)
        else: outSrfTempDict = {}
        
        #If there are different hourly window transmissivities for different windows, make a dictionary for the shades and make a neutral winTrans list to cancel out the usual way window transmissivity is factored in.
        neutralWinTransList = []
        winShdDict = {}
        if allWindowShadesSame == False:
            for hr in range(8760): neutralWinTransList.append(1)
            winShdDict = createShdDict(winStatusHeaders, winTrans, zoneWindowTransmiss, zoneWindowNames)
        
        #Make sure that there are windows in the model and, if so, generate solar outputs.
        if sum(zoneHasWindows) != 0:
            #Create a meshed sky dome to assist with direct sunlight falling on occupants.
            skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
            skyPatchMeshes = []
            for patch in skyPatches:
                skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patch, rc.Geometry.MeshingParameters.Coarse)[0])
            
            #Initiate the sun vector calculator.
            lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
            
            #Calculate the altitude and azimuth of the different hours.
            sunVecs = []
            altitudes = []
            azimuths = []
            for hour in originalHOYs:
                d, m, t = lb_preparation.hour2Date(hour, True)
                lb_sunpath.solInitOutput(m+1, d, t)
                altitude = math.degrees(lb_sunpath.solAlt)
                azimuth = math.degrees(lb_sunpath.solAz)
                if altitude > 0:
                    sunVec = lb_sunpath.sunReverseVectorCalc()
                else: sunVec = None
                sunVecs.append(sunVec)
                altitudes.append(altitude)
                azimuths.append(azimuth)
            sunVecInfo = [sunVecs, altitudes, azimuths]
        
        #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
        airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
        
        #Compute grouped zone properties for air stratification purposes.
        adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, groupedZoneVols = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
        
        #Compute a generalizable "projected area" to estimate the zone's starting wind speed.
        #Note that this projection should ideally be done perpendicularly to the direction of air flow but, since we don't really know the direction of air flow in the zone, we will compute it generally over the whole volume.
        projectedAreas = []
        for zoneVol in groupedZoneVols:
            projLen = math.pow(zoneVol, 1/3)
            projArea = projLen*projLen
            projectedAreas.append(projArea)
        
        #Run through every hour of the analysis to fill up the matrices.
        calcCancelled = False
        try:
            def climateMap(count):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                
                # Get the hour.
                hour = HOYs[count]
                originalHour = originalHOYs[count]
                
                #Select out the relevant flow vol and heat gain values.
                flowVolValues = []
                heatGainValues = []
                for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
                for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
                
                #Compute the radiant temperature.
                pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outSrfTempDict, outdoorNonSrfViewFac, prevailingOutdoorTemp)
                if sum(zoneHasWindows) != 0:
                    if allWindowShadesSame == True: pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, outHorizInfrared, lb_comfortModels)
                    else:
                        #To factor in the effect of blocked sunlight, I have to re-make the testPtSkyView and the testPtBlockedVec to reflect the conditions for the given hour.
                        hourTestPtSkyView, hourTestPtBlockedVec = computeHourShadeDrawing(hour, testPtSkyView, testPtBlockedVec, winShdDict, testPtBlockName, outdoorClac)
                        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, hourTestPtSkyView, hourTestPtBlockedVec, neutralWinTransList, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, outHorizInfrared, lb_comfortModels)
                pointMRTValues = lb_preparation.flattenList(pointMRTValues)
                radTempMtx[count+1] = pointMRTValues
                
                #Compute the air temperature.
                pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, prevailingOutdoorTemp)
                if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, outdoorClac, prevailingOutdoorTemp)
                pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
                airTempMtx[count+1] = pointAirTempValues
                
                #Compute the operative temperature.
                pointOpTempValues = []
                for ptCount, airTemp in enumerate(pointAirTempValues):
                    pointOpTempValues.append((airTemp+pointMRTValues[ptCount])/2)
                operativeTempMtx[count+1] = pointOpTempValues
                
                #Compute the wind speed.
                pointWindSpeedValues = []
                for pointListCount, pointList in enumerate(testPtsViewFactor):
                    if outdoorClac == False or pointListCount != len(testPtsViewFactor)-1:
                        for val in pointList:
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = flowVolValues[pointListCount]/projectedAreas[pointListCount]
                                pointWindSpeedValues.append(windFlowVal)
                    else:
                        for valCount, val in enumerate(pointList):
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = lb_wind.powerLawWind(outWindSpeed[originalHour-1], outdoorPtHeightWeights[valCount], d, a, 270, 0.14)
                                pointWindSpeedValues.append(windFlowVal)
                
                #Compute the adaptive comfort and deg from target.
                adaptComfPointValues = []
                degFromTargetPointValues = []
                
                for ptCount, airTemp in enumerate(pointAirTempValues):
                    if ASHRAEorEN == True: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(airTemp, pointMRTValues[ptCount], prevailTemp[originalHour-1], pointWindSpeedValues[ptCount], comfClass, levelOfConditioning)
                    else: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(airTemp, pointMRTValues[ptCount], prevailTemp[originalHour-1], pointWindSpeedValues[ptCount], comfClass, levelOfConditioning)
                    adaptComfPointValues.append(int(comf))
                    degFromTargetPointValues.append(distFromTarget)
                
                adaptComfMtx[count+1] = adaptComfPointValues
                degFromTargetMtx[count+1] = degFromTargetPointValues
            
            #Run through every hour of the analysis to fill up the matrices.
            if parallel_ == True and len(HOYs) != 1:
                tasks.Parallel.ForEach(range(len(HOYs)), climateMap)
            else:
                for hour in range(len(HOYs)):
                    #Ability to cancel with Esc
                    #if gh.GH_Document.IsEscapeKeyDown(): assert False
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

def mainPMV(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, PPDComfortThresh, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    SET_Mtx = ['Standard Effective Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PMVComfMtx = ['PMV Thermal Comfort Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PMV_Mtx = ['Predicted Mean Vote;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Check the data anlysis period and subtract the start day from each of the HOYs.
    originalHOYs = []
    if dataAnalysisPeriod != [(1,1,1),(12,31,24)]:
        FinalHOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod(dataAnalysisPeriod, 1)
        for hCount, hour in enumerate(HOYs):
            originalHOYs.append(hour)
            if hour - FinalHOYs[0] >= 0: HOYs[hCount] = hour - FinalHOYs[0]
            else: HOYs[hCount] = hour - FinalHOYs[0] + 8760
    else: FinalHOYs = originalHOYs = HOYs
    
    #Check to be sure that the requested analysis period and the analysis period of the connected data align.
    periodsAlign = True
    hrStart = originalHOYs[0]
    hrEnd = originalHOYs[-1]
    if hrStart in FinalHOYs and hrEnd in FinalHOYs: pass
    else: periodsAlign = False
    if periodsAlign == False:
        warning = 'The analysis period of the energy simulation data and the analysisPeriodOrHOY_ plugged into this component do not align.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    else:
        #Create placeholders for all of the hours.
        for hour in HOYs:
            radTempMtx.append(0)
            airTempMtx.append(0)
            SET_Mtx.append(0)
            PMVComfMtx.append(0)
            PMV_Mtx.append(0)
        
        #Make sure that the EPW Data does not include headers.
        outDryBulbTemp = outDryBulbTemp[7:]
        outRelHumid = outRelHumid[7:]
        outWindSpeed = outWindSpeed[7:]
        
        #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
        srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
        
        #Make a dictionary for outdoor srfNames and temperatures.
        if outdoorClac == True:
            outSrfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", outSrfTempHeaders, outSrfTempNumbers)
        else: outSrfTempDict = {}
        
        #If there are different shade statuses for the different windows, make a neutral winTrans list for this case.
        neutralWinTransList = []
        winShdDict = {}
        if allWindowShadesSame == False:
            for hr in range(8760): neutralWinTransList.append(1)
            winShdDict = createShdDict(winStatusHeaders, winTrans, zoneWindowTransmiss, zoneWindowNames)
        
        #Make sure that there are windows in the model and a good reason to generate solar outputs.
        if sum(zoneHasWindows) != 0:
            #Create a meshed sky dome to assist with direct sunlight falling on occupants.
            skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
            skyPatchMeshes = []
            for patch in skyPatches:
                skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patch, rc.Geometry.MeshingParameters.Coarse)[0])
            
            #Initiate the sun vector calculator.
            lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
            
            #Calculate the altitude and azimuth of the different hours.
            sunVecs = []
            altitudes = []
            azimuths = []
            for hour in originalHOYs:
                d, m, t = lb_preparation.hour2Date(hour, True)
                lb_sunpath.solInitOutput(m+1, d, t)
                altitude = math.degrees(lb_sunpath.solAlt)
                azimuth = math.degrees(lb_sunpath.solAz)
                if altitude > 0:
                    sunVec = lb_sunpath.sunReverseVectorCalc()
                else: sunVec = None
                sunVecs.append(sunVec)
                altitudes.append(altitude)
                azimuths.append(azimuth)
            sunVecInfo = [sunVecs, altitudes, azimuths]
        
        #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
        airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
        relHumidDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", relHumidDataHeaders, relHumidDataNumbers)
        
        #Compute grouped zone properties for air stratification purposes.
        adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, groupedZoneVols = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
        
        #Compute a generalizable "projected area" to estimate the zone's starting wind speed.
        #Note that this projection should ideally be done perpendicularly to the direction of air flow but, since we don't really know the direction of air flow in the zone, we will compute it generally over the whole volume.
        projectedAreas = []
        for zoneVol in groupedZoneVols:
            projLen = math.pow(zoneVol, 1/3)
            projArea = projLen*projLen
            projectedAreas.append(projArea)
        
        #Run through every hour of the analysis to fill up the matrices.
        calcCancelled = False
        try:
            def climateMapPMV(count):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                
                # Get the hour.
                hour = HOYs[count]
                originalHour = originalHOYs[count]
                
                #Select out the relevant air and surface temperatures.
                flowVolValues = []
                heatGainValues = []
                for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
                for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
                
                #Compute the radiant temperature.
                pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outSrfTempDict, outdoorNonSrfViewFac, outDryBulbTemp)
                if sum(zoneHasWindows) != 0:
                    if allWindowShadesSame == True: pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                    else:
                        #To factor in the effect of blocked sunlight, I have to re-make the testPtSkyView and the testPtBlockedVec to reflect the conditions for the given hour.
                        hourTestPtSkyView, hourTestPtBlockedVec = computeHourShadeDrawing(hour, testPtSkyView, testPtBlockedVec, winShdDict, testPtBlockName, outdoorClac)
                        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, hourTestPtSkyView, hourTestPtBlockedVec, neutralWinTransList, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                pointMRTValues = lb_preparation.flattenList(pointMRTValues)
                radTempMtx[count+1] = pointMRTValues
                
                #Compute the air temperature.
                pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outDryBulbTemp)
                if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, outdoorClac, outDryBulbTemp)
                pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
                airTempMtx[count+1] = pointAirTempValues
                
                #Compute the relative humidity.
                pointRelHumidValues = getAirPointValue(relHumidDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outRelHumid)
                pointRelHumidValues = lb_preparation.flattenList(pointRelHumidValues)
                
                #Compute the wind speed.
                pointWindSpeedValues = []
                for pointListCount, pointList in enumerate(testPtsViewFactor):
                    if outdoorClac == False or pointListCount != len(testPtsViewFactor)-1:
                        for val in pointList:
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = flowVolValues[pointListCount]/projectedAreas[pointListCount]
                                pointWindSpeedValues.append(windFlowVal)
                    else:
                        for valCount, val in enumerate(pointList):
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = lb_wind.powerLawWind(outWindSpeed[originalHour-1], outdoorPtHeightWeights[valCount], d, a, 270, 0.14)
                                pointWindSpeedValues.append(windFlowVal)
                
                #Compute the SET and PMV comfort.
                setPointValues = []
                pmvComfPointValues = []
                pmvPointValues = []
                
                for ptCount, airTemp in enumerate(pointAirTempValues):
                    try:
                        pmv, ppd, set, taAdj, coolingEffect = lb_comfortModels.comfPMVElevatedAirspeed(airTemp, pointMRTValues[ptCount], pointWindSpeedValues[ptCount], pointRelHumidValues[ptCount], metabolicRate[originalHour-1], clothingLevel[originalHour-1], 0.0)
                    except:
                        print 'These conditions caused a failure of the PMV model convergence: Ta = ' + str(airTemp) + "; Tr = " + str(pointMRTValues[ptCount]) + "; Vel = " + str(pointWindSpeedValues[ptCount]) + "; RH = " + str(pointRelHumidValues[ptCount]) + "; met = " + str(metabolicRate[originalHour-1]) + "; clo= " + str(clothingLevel[originalHour-1])
                        pmv, ppd, set, taAdj, coolingEffect = 0.0, 5.0, 21.0, 0.0, 0.0
                    
                    setPointValues.append(set)
                    if humidRatioUp != 0.03 or humidRatioLow != 0.0:
                        HR, EN, vapPress, satPress = lb_comfortModels.calcHumidRatio(airTemp, pointRelHumidValues[ptCount], 101325)
                        if ppd < PPDComfortThresh and HR < humidRatioUp and HR > humidRatioLow: comfortableOrNot.append(1)
                        else: comfortableOrNot.append(0)
                    else:
                        if ppd < PPDComfortThresh: pmvComfPointValues.append(1)
                        else: pmvComfPointValues.append(0)
                    pmvPointValues.append(pmv)
                
                SET_Mtx[count+1] = setPointValues
                PMVComfMtx[count+1] = pmvComfPointValues
                PMV_Mtx[count+1] = pmvPointValues
            
            #Run through every hour of the analysis to fill up the matrices.
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
            return radTempMtx, airTempMtx, SET_Mtx, PMVComfMtx, PMV_Mtx
        else:
            return -1

def mainUTCI(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    UTCI_Mtx = ['Universal Thermal Climate Index;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    OutdoorComfMtx = ['Outdoor Thermal Comfort Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    DegFromNeutralMtx = ['Degrees From Neutral UTCI;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Check the data anlysis period and subtract the start day from each of the HOYs.
    originalHOYs = []
    if dataAnalysisPeriod != [(1,1,1),(12,31,24)]:
        FinalHOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod(dataAnalysisPeriod, 1)
        for hCount, hour in enumerate(HOYs):
            originalHOYs.append(hour)
            if hour - FinalHOYs[0] >= 0: HOYs[hCount] = hour - FinalHOYs[0]
            else: HOYs[hCount] = hour - FinalHOYs[0] + 8760
    else: FinalHOYs = originalHOYs = HOYs
    
    #Check to be sure that the requested analysis period and the analysis period of the connected data align.
    periodsAlign = True
    hrStart = originalHOYs[0]
    hrEnd = originalHOYs[-1]
    if hrStart in FinalHOYs and hrEnd in FinalHOYs: pass
    else: periodsAlign = False
    if periodsAlign == False:
        warning = 'The analysis period of the energy simulation data and the analysisPeriodOrHOY_ plugged into this component do not align.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    else:
        #Create placeholders for all of the hours.
        for hour in HOYs:
            radTempMtx.append(0)
            airTempMtx.append(0)
            UTCI_Mtx.append(0)
            OutdoorComfMtx.append(0)
            DegFromNeutralMtx.append(0)
        
        #Make sure that the EPW Data does not include headers.
        outDryBulbTemp = outDryBulbTemp[7:]
        outRelHumid = outRelHumid[7:]
        outWindSpeed = outWindSpeed[7:]
        
        #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
        try: srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
        except: srfTempDict = {}
        
        #Make a dictionary for outdoor srfNames and temperatures.
        if outdoorClac == True: outSrfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", outSrfTempHeaders, outSrfTempNumbers)
        else: outSrfTempDict = {}
        
        #If there are different shade statuses for the different windows, make a neutral winTrans list for this case.
        neutralWinTransList = []
        winShdDict = {}
        if allWindowShadesSame == False:
            for hr in range(8760): neutralWinTransList.append(1)
            winShdDict = createShdDict(winStatusHeaders, winTrans, zoneWindowTransmiss, zoneWindowNames)
        
        #Make sure that there are windows in the model and a good reason to generate solar outputs.
        if sum(zoneHasWindows) != 0:
            #Create a meshed sky dome to assist with direct sunlight falling on occupants.
            skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
            skyPatchMeshes = []
            for patch in skyPatches:
                skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patch, rc.Geometry.MeshingParameters.Coarse)[0])
            
            #Initiate the sun vector calculator.
            lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
            
            #Calculate the altitude and azimuth of the different hours.
            sunVecs = []
            altitudes = []
            azimuths = []
            for hour in originalHOYs:
                d, m, t = lb_preparation.hour2Date(hour, True)
                lb_sunpath.solInitOutput(m+1, d, t)
                altitude = math.degrees(lb_sunpath.solAlt)
                azimuth = math.degrees(lb_sunpath.solAz)
                if altitude > 0:
                    sunVec = lb_sunpath.sunReverseVectorCalc()
                else: sunVec = None
                sunVecs.append(sunVec)
                altitudes.append(altitude)
                azimuths.append(azimuth)
            sunVecInfo = [sunVecs, altitudes, azimuths]
        
        #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
        try: airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
        except: airTempDict = {}
        try: relHumidDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", relHumidDataHeaders, relHumidDataNumbers)
        except: relHumidDict = {}
        
        #Compute grouped zone properties for air stratification purposes.
        adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, groupedZoneVols = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
        
        #Compute a generalizable "projected area" to estimate the zone's starting wind speed.
        #Note that this projection should ideally be done perpendicularly to the direction of air flow but, since we don't really know the direction of air flow in the zone, we will compute it generally over the whole volume.
        projectedAreas = []
        for zoneVol in groupedZoneVols:
            projLen = math.pow(zoneVol, 1/3)
            projArea = projLen*projLen
            projectedAreas.append(projArea)
        
        #Run through every hour of the analysis to fill up the matrices.
        calcCancelled = False
        try:
            def climateMapUTCI(count):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                
                # Get the hour.
                hour = HOYs[count]
                originalHour = originalHOYs[count]
                
                #Select out the relevant air and surface temperatures.
                flowVolValues = []
                heatGainValues = []
                for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
                for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
                
                #Compute the radiant temperature.
                pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outSrfTempDict, outdoorNonSrfViewFac, outDryBulbTemp)
                if sum(zoneHasWindows) != 0:
                    if allWindowShadesSame == True: pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                    else:
                        #To factor in the effect of blocked sunlight, I have to re-make the testPtSkyView and the testPtBlockedVec to reflect the conditions for the given hour.
                        hourTestPtSkyView, hourTestPtBlockedVec = computeHourShadeDrawing(hour, testPtSkyView, testPtBlockedVec, winShdDict, testPtBlockName, outdoorClac)
                        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, hourTestPtSkyView, hourTestPtBlockedVec, neutralWinTransList, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                pointMRTValues = lb_preparation.flattenList(pointMRTValues)
                radTempMtx[count+1] = pointMRTValues
                
                #Compute the air temperature.
                pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outDryBulbTemp)
                if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, outdoorClac, outDryBulbTemp)
                pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
                airTempMtx[count+1] = pointAirTempValues
                
                #Compute the relative humidity.
                pointRelHumidValues = getAirPointValue(relHumidDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outRelHumid)
                pointRelHumidValues = lb_preparation.flattenList(pointRelHumidValues)
                
                #Compute the wind speed.
                pointWindSpeedValues = []
                for pointListCount, pointList in enumerate(testPtsViewFactor):
                    if outdoorClac == False or pointListCount != len(testPtsViewFactor)-1:
                        for val in pointList:
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = flowVolValues[pointListCount]/projectedAreas[pointListCount]
                                pointWindSpeedValues.append(windFlowVal)
                    else:
                        for valCount, val in enumerate(pointList):
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = lb_wind.powerLawWind(outWindSpeed[originalHour-1], outdoorPtHeightWeights[valCount], d, a, 270, 0.14)
                                pointWindSpeedValues.append(windFlowVal)
                
                # The wind speeds computed above are for a height above the ground at the point of comfort evaluation.
                # However, UTCI's polynomial approximation was written to use a meteorolical wind speed at a height above this point of evaulation (10 meters above the ground).
                # The UTCI model assumes this meteorological wind speed is 1.5 times the speed of wind at occumant height (1.1 meters above the ground).
                # http://www.utci.org/isb/meeting.php
                # So we will do the same before calculating UTCI.
                pointWindSpeedValues = [x * 1.5 for x in pointWindSpeedValues]
                
                #Compute the UTCI and comfort.
                utciPointValues = []
                outdoorComfPointValues = []
                degNeutralPointValues = []
                
                for ptCount, airTemp in enumerate(pointAirTempValues):
                    utci, comf, condition, stressVal = lb_comfortModels.comfUTCI(airTemp, pointMRTValues[ptCount], pointWindSpeedValues[ptCount], pointRelHumidValues[ptCount])
                    utciPointValues.append(utci)
                    outdoorComfPointValues.append(comf)
                    degNeutralPointValues.append(utci-20)
                
                UTCI_Mtx[count+1] = utciPointValues
                OutdoorComfMtx[count+1] = outdoorComfPointValues
                DegFromNeutralMtx[count+1] = degNeutralPointValues
            
            #Run through every hour of the analysis to fill up the matrices.
            if parallel_ == True and len(HOYs) != 1:
                tasks.Parallel.ForEach(range(len(HOYs)), climateMapUTCI)
            else:
                for hour in range(len(HOYs)):
                    #Ability to cancel with Esc
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    climateMapUTCI(hour)
        except:
            print "The calculation has been terminated by the user!"
            e = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
            calcCancelled = True
        
        
        if calcCancelled == False:
            return radTempMtx, airTempMtx, UTCI_Mtx, OutdoorComfMtx, DegFromNeutralMtx
        else:
            return -1

def mainPET(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtsViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, bodyCharacteristics, climate, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind):
    #Set up matrices to be filled.
    radTempMtx = ['Radiant Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    airTempMtx = ['Air Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PET_Mtx = ['Physiological Equivalent Temperature;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PET_ComfMtx = ['PET Thermal Comfort Percent;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    PET_CategoryMtx = ['PET Category;' + str(analysisPeriod[0]) + ";" + str(analysisPeriod[1])]
    
    #Check the data anlysis period and subtract the start day from each of the HOYs.
    originalHOYs = []
    if dataAnalysisPeriod != [(1,1,1),(12,31,24)]:
        FinalHOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod(dataAnalysisPeriod, 1)
        for hCount, hour in enumerate(HOYs):
            originalHOYs.append(hour)
            if hour - FinalHOYs[0] >= 0: HOYs[hCount] = hour - FinalHOYs[0]
            else: HOYs[hCount] = hour - FinalHOYs[0] + 8760
    else: FinalHOYs = originalHOYs = HOYs
    
    #Check to be sure that the requested analysis period and the analysis period of the connected data align.
    periodsAlign = True
    hrStart = originalHOYs[0]
    hrEnd = originalHOYs[-1]
    if hrStart in FinalHOYs and hrEnd in FinalHOYs: pass
    else: periodsAlign = False
    if periodsAlign == False:
        warning = 'The analysis period of the energy simulation data and the analysisPeriodOrHOY_ plugged into this component do not align.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    else:
        #Create placeholders for all of the hours.
        for hour in HOYs:
            radTempMtx.append(0)
            airTempMtx.append(0)
            PET_Mtx.append(0)
            PET_ComfMtx.append(0)
            PET_CategoryMtx.append(0)
        
        #Make sure that the EPW Data does not include headers.
        outDryBulbTemp = outDryBulbTemp[7:]
        outRelHumid = outRelHumid[7:]
        outWindSpeed = outWindSpeed[7:]
        
        #Make a dictionary that will relate the zoneSrfNames to the srfTempValues.
        try: srfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", srfTempHeaders, srfTempNumbers)
        except: srfTempDict = {}
        
        #Make a dictionary for outdoor srfNames and temperatures.
        if outdoorClac == True: outSrfTempDict = createSrfDict(zoneSrfNames, "srfName", "srfTemp", outSrfTempHeaders, outSrfTempNumbers)
        else: outSrfTempDict = {}
        
        #If there are different shade statuses for the different windows, make a neutral winTrans list for this case.
        neutralWinTransList = []
        winShdDict = {}
        if allWindowShadesSame == False:
            for hr in range(8760): neutralWinTransList.append(1)
            winShdDict = createShdDict(winStatusHeaders, winTrans, zoneWindowTransmiss, zoneWindowNames)
        
        #Make sure that there are windows in the model and a good reason to generate solar outputs.
        if sum(zoneHasWindows) != 0:
            #Create a meshed sky dome to assist with direct sunlight falling on occupants.
            skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, numSkyPatchDivs, .5)
            skyPatchMeshes = []
            for patch in skyPatches:
                skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patch, rc.Geometry.MeshingParameters.Coarse)[0])
            
            #Initiate the sun vector calculator.
            lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
            
            #Calculate the altitude and azimuth of the different hours.
            sunVecs = []
            altitudes = []
            azimuths = []
            for hour in originalHOYs:
                d, m, t = lb_preparation.hour2Date(hour, True)
                lb_sunpath.solInitOutput(m+1, d, t)
                altitude = math.degrees(lb_sunpath.solAlt)
                azimuth = math.degrees(lb_sunpath.solAz)
                if altitude > 0:
                    sunVec = lb_sunpath.sunReverseVectorCalc()
                else: sunVec = None
                sunVecs.append(sunVec)
                altitudes.append(altitude)
                azimuths.append(azimuth)
            sunVecInfo = [sunVecs, altitudes, azimuths]
        
        #Make a dictionary that will relate the testPtZoneNames to the air temperatures.
        try: airTempDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", airTempDataHeaders, airTempDataNumbers)
        except: airTempDict = {}
        try: relHumidDict = createZoneDict(testPtZoneNames, "zoneName", "airTemp", relHumidDataHeaders, relHumidDataNumbers)
        except: relHumidDict = {}
        
        #Compute grouped zone properties for air stratification purposes.
        adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, groupedZoneVols = computeGroupedRoomProperties(testPtZoneWeights, testPtZoneNames, zoneInletInfo, inletHeightOverride)
        
        #Compute a generalizable "projected area" to estimate the zone's starting wind speed.
        #Note that this projection should ideally be done perpendicularly to the direction of air flow but, since we don't really know the direction of air flow in the zone, we will compute it generally over the whole volume.
        projectedAreas = []
        for zoneVol in groupedZoneVols:
            projLen = math.pow(zoneVol, 1/3)
            projArea = projLen*projLen
            projectedAreas.append(projArea)
        
        #Run through every hour of the analysis to fill up the matrices.
        calcCancelled = False
        try:
            def climateMapPET(count):
                #Ability to cancel with Esc
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                
                # Get the hour.
                hour = HOYs[count]
                originalHour = originalHOYs[count]
                
                #Select out the relevant air and surface temperatures.
                flowVolValues = []
                heatGainValues = []
                for zoneVal in flowVolDataNumbers: flowVolValues.append(zoneVal[hour-1])
                for zoneVal in heatGainDataNumbers: heatGainValues.append(zoneVal[hour-1])
                
                #Compute the radiant temperature.
                pointMRTValues = calculatePointMRT(srfTempDict, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outSrfTempDict, outdoorNonSrfViewFac, outDryBulbTemp)
                if sum(zoneHasWindows) != 0:
                    if allWindowShadesSame == True: pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, testPtSkyView, testPtBlockedVec, winTrans, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                    else:
                        #To factor in the effect of blocked sunlight, I have to re-make the testPtSkyView and the testPtBlockedVec to reflect the conditions for the given hour.
                        hourTestPtSkyView, hourTestPtBlockedVec = computeHourShadeDrawing(hour, testPtSkyView, testPtBlockedVec, winShdDict, testPtBlockName, outdoorClac)
                        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, hour, originalHour, diffSolarRad, directSolarRad, globHorizRad, count, sunVecInfo, hourTestPtSkyView, hourTestPtBlockedVec, neutralWinTransList, cloA, floorR, skyPatchMeshes, zoneHasWindows, outdoorClac, horizInfraredRadiation, lb_comfortModels)
                pointMRTValues = lb_preparation.flattenList(pointMRTValues)
                radTempMtx[count+1] = pointMRTValues
                
                #Compute the air temperature.
                pointAirTempValues = getAirPointValue(airTempDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outDryBulbTemp)
                if mixedAirOverride[hour-1] == 0: pointAirTempValues = warpByHeight(pointAirTempValues, ptHeightWeights, flowVolValues, heatGainValues, adjacentList, adjacentNameList, groupedInletArea, groupedZoneHeights, groupedGlzHeights, groupedWinCeilDiffs, outdoorClac, outDryBulbTemp)
                pointAirTempValues = lb_preparation.flattenList(pointAirTempValues)
                airTempMtx[count+1] = pointAirTempValues
                
                #Compute the relative humidity.
                pointRelHumidValues = getAirPointValue(relHumidDict, testPtZoneWeights, testPtsViewFactor, hour-1, originalHour-1, outdoorClac, outRelHumid)
                pointRelHumidValues = lb_preparation.flattenList(pointRelHumidValues)
                
                #Compute the wind speed.
                pointWindSpeedValues = []
                for pointListCount, pointList in enumerate(testPtsViewFactor):
                    if outdoorClac == False or pointListCount != len(testPtsViewFactor)-1:
                        for val in pointList:
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = flowVolValues[pointListCount]/projectedAreas[pointListCount]
                                pointWindSpeedValues.append(windFlowVal)
                    else:
                        for valCount, val in enumerate(pointList):
                            try:
                                if allWindSpeedsSame == 1: pointWindSpeedValues.append(winSpeedNumbers[originalHour-1])
                                elif allWindSpeedsSame == 0: pointWindSpeedValues.append(winSpeedNumbers[pointListCount][originalHour-1])
                                elif allWindSpeedsSame == -1: pointWindSpeedValues = winSpeedNumbers[originalHour-1]
                            except:
                                windFlowVal = lb_wind.powerLawWind(outWindSpeed[originalHour-1], outdoorPtHeightWeights[valCount], d, a, 270, 0.14)
                                pointWindSpeedValues.append(windFlowVal)
                
                #Compute the UTCI and comfort.
                petPointValues = []
                petComfPointValues = []
                petCategoryValues = []
                
                for ptCount, airTemp in enumerate(pointAirTempValues):
                    petObj = lb_comfortModels.physiologicalEquivalentTemperature(airTemp, pointMRTValues[ptCount], pointRelHumidValues[ptCount], pointWindSpeedValues[ptCount], bodyCharacteristics['age'], bodyCharacteristics['sex'], bodyCharacteristics['heightM'], bodyCharacteristics['weight'], bodyCharacteristics['bodyPosition'], bodyCharacteristics['Mmets'], bodyCharacteristics['Icl'][originalHour])
                    respiration = petObj.inkoerp()
                    coreTemperature, radiationBalance, convection, waterVaporDiffusion = petObj.berech()
                    petObj.pet()
                    skinTemperature, totalHeatLoss, skinSweating, internalHeat, sweatEvaporation, PET = petObj.tsk, petObj.wsum, petObj.wetsk, petObj.h, petObj.esw, petObj.tx
                    effectPET, comfortablePET = petObj.thermalCategories(climate)
                    
                    petPointValues.append(PET)
                    petComfPointValues.append(comfortablePET)
                    petCategoryValues.append(effectPET)
                
                PET_Mtx[count+1] = petPointValues
                PET_ComfMtx[count+1] = petComfPointValues
                PET_CategoryMtx[count+1] = petCategoryValues
            
            #Run through every hour of the analysis to fill up the matrices.
            if parallel_ == True and len(HOYs) != 1:
                tasks.Parallel.ForEach(range(len(HOYs)), climateMapPET)
            else:
                for hour in range(len(HOYs)):
                    #Ability to cancel with Esc
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    climateMapPET(hour)
        except:
            print "The calculation has been terminated by the user!"
            e = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
            calcCancelled = True
        
        
        if calcCancelled == False:
            return radTempMtx, airTempMtx, PET_Mtx, PET_ComfMtx, PET_CategoryMtx
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
    if writeResultFile_ != 2:
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
    else:
        radTempResult = None
    
    #Write the air temperature result file.
    if writeResultFile_ != 2:
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
    else:
        airTempResult = None
    
    #Write the operative temperature result file.
    if writeResultFile_ != 2:
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
    else:
        operativeTempResult = None
    
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


def writeCSVPMV(lb_preparation, directory, fileName, radTempMtx, airTempMtx, SET_Mtx, PMVComfMtx, PMV_Mtx):
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
    if writeResultFile_ != 2:
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
    else:
        radTempResult = None
    
    #Write the air temperature result file.
    if writeResultFile_ != 2:
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
    else:
        airTempResult = None
    
    #Write the operative temperature result file.
    if writeResultFile_ != 2:
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
    else:
        SET_Result = None
    
    #Write the adaptive comfort result file.
    PPD_Result = os.path.join(workingDir, PPDFile)
    comfCSVfile = open(PPD_Result, 'wb')
    for lineCount, line in enumerate(PMVComfMtx):
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

def writeCSVUTCI(lb_preparation, directory, fileName, radTempMtx, airTempMtx, UTCI_Mtx, OutdoorComfMtx, DegFromNeutralMtx):
    #Find out the number of values in each hour.
    valLen = len(radTempMtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(directory)) 
    
    #Create a csv Files.
    radTempFile = fileName + "RadiantTemp.csv"
    airTempFile = fileName + "AirTemp.csv"
    UTCIFile = fileName + "UTCI.csv"
    OutdoorComfFile = fileName + "OutdoorComf.csv"
    DegFromNeutralFile = fileName + "DegFromTarget.csv"
    
    #Write the radiant temperature result file.
    if writeResultFile_ != 2:
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
    else:
        radTempResult = None
    
    #Write the air temperature result file.
    if writeResultFile_ != 2:
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
    else:
        airTempResult = None
    
    #Write the operative temperature result file.
    if writeResultFile_ != 2:
        UTCI_Result = os.path.join(workingDir, UTCIFile)
        opCSVfile = open(UTCI_Result, 'wb')
        for lineCount, line in enumerate(UTCI_Mtx):
            lineStr = ''
            if lineCount != 0:
                for valCt, val in enumerate(line):
                    if valCt != valLen: lineStr = lineStr + str(val) + ','
                    else: lineStr = lineStr + str(val) + "\n"
                opCSVfile.write(lineStr)
            else: opCSVfile.write(line + "\n")
        opCSVfile.close()
    else:
        UTCI_Result = None
    
    #Write the adaptive comfort result file.
    OutdoorComfResult = os.path.join(workingDir, OutdoorComfFile)
    comfCSVfile = open(OutdoorComfResult, 'wb')
    for lineCount, line in enumerate(OutdoorComfMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            comfCSVfile.write(lineStr)
        else: comfCSVfile.write(line + "\n")
    comfCSVfile.close()
    
    #Write the deg from target result file.
    DegFromNeutralResult = os.path.join(workingDir, DegFromNeutralFile)
    degCSVfile = open(DegFromNeutralResult, 'wb')
    for lineCount, line in enumerate(DegFromNeutralMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            degCSVfile.write(lineStr)
        else: degCSVfile.write(line + "\n")
    degCSVfile.close()
    
    
    return radTempResult, airTempResult, UTCI_Result, OutdoorComfResult, DegFromNeutralResult

def writeCSVPET(lb_preparation, directory, fileName, radTempMtx, airTempMtx, PET_Mtx, PET_ComfMtx, PET_CategoryMtx):
    #Find out the number of values in each hour.
    valLen = len(radTempMtx[-1])-1
    
    #Set up a working directory.
    workingDir = lb_preparation.makeWorkingDir(os.path.join(directory)) 
    
    #Create a csv Files.
    radTempFile = fileName + "RadiantTemp.csv"
    airTempFile = fileName + "AirTemp.csv"
    PETFile = fileName + "PET.csv"
    PETComfFile = fileName + "PETComf.csv"
    PETCategoryFile = fileName + "PETCategory.csv"
    
    #Write the radiant temperature result file.
    if writeResultFile_ != 2:
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
    else:
        radTempResult = None
    
    #Write the air temperature result file.
    if writeResultFile_ != 2:
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
    else:
        airTempResult = None
    
    #Write the operative temperature result file.
    if writeResultFile_ != 2:
        PET_Result = os.path.join(workingDir, PETFile)
        opCSVfile = open(PET_Result, 'wb')
        for lineCount, line in enumerate(PET_Mtx):
            lineStr = ''
            if lineCount != 0:
                for valCt, val in enumerate(line):
                    if valCt != valLen: lineStr = lineStr + str(val) + ','
                    else: lineStr = lineStr + str(val) + "\n"
                opCSVfile.write(lineStr)
            else: opCSVfile.write(line + "\n")
        opCSVfile.close()
    else:
        PET_Result = None
    
    #Write the adaptive comfort result file.
    PET_ComfResult = os.path.join(workingDir, PETComfFile)
    comfCSVfile = open(PET_ComfResult, 'wb')
    for lineCount, line in enumerate(PETComfMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            comfCSVfile.write(lineStr)
        else: comfCSVfile.write(line + "\n")
    comfCSVfile.close()
    
    #Write the deg from target result file.
    PET_CategoryResult = os.path.join(workingDir, PETCategoryFile)
    degCSVfile = open(PET_CategoryResult, 'wb')
    for lineCount, line in enumerate(PETCategoryMtx):
        lineStr = ''
        if lineCount != 0:
            for valCt, val in enumerate(line):
                if valCt != valLen: lineStr = lineStr + str(val) + ','
                else: lineStr = lineStr + str(val) + "\n"
            degCSVfile.write(lineStr)
        else: degCSVfile.write(line + "\n")
    degCSVfile.close()
    
    
    return radTempResult, airTempResult, PET_Result, PET_ComfResult, PET_CategoryResult


#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_defaultFolder = sc.sticky["Ladybug_DefaultFolder"]
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
    lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
    lb_wind = sc.sticky["ladybug_WindSpeed"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")


#Check the type of comfort analysis recipe connected.
recipeRecognized = False
comfortModel = None
if len(_comfAnalysisRecipe) > 0:
    if len(_comfAnalysisRecipe) == 54 and _comfAnalysisRecipe[0] == "Adaptive":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, ASHRAEorEN, comfClass, avgMonthOrRunMean, levelOfConditioning, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, dataAnalysisPeriod, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, horizInfraredRadiation, northAngle = _comfAnalysisRecipe
        recipeRecognized = True
    elif len(_comfAnalysisRecipe) == 58 and _comfAnalysisRecipe[0] == "PMV":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, PPDComfortThresh, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation = _comfAnalysisRecipe
        recipeRecognized = True
    elif len(_comfAnalysisRecipe) == 53 and _comfAnalysisRecipe[0] == "UTCI":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation = _comfAnalysisRecipe
        recipeRecognized = True
    elif len(_comfAnalysisRecipe) == 55 and _comfAnalysisRecipe[0] == "PET":
        comfortModel, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, bodyCharacteristics, climate, horizInfraredRadiation = _comfAnalysisRecipe
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
        result = mainAdapt(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, prevailingOutdoorTemp, ASHRAEorEN, comfClass, avgMonthOrRunMean, levelOfConditioning, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, dataAnalysisPeriod, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, horizInfraredRadiation, northAngle, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind)
        if result != -1:
            radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx = result
            if writeResultFile_ != 0:
                radTempResult, airTempResult, operativeTempResult, adaptComfResult, degFromTargetResult = writeCSVAdapt(lb_preparation, directory, fileName, radTempMtx, airTempMtx, operativeTempMtx, adaptComfMtx, degFromTargetMtx)
    elif comfortModel == "PMV":
        result = mainPMV(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, PPDComfortThresh, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind)
        if result != -1:
            radTempMtx, airTempMtx, SET_Mtx, PMVComfMtx, PMV_Mtx = result
            if writeResultFile_ != 0:
                radTempResult, airTempResult, SET_Result, PMVComfResult, PMV_Result = writeCSVPMV(lb_preparation, directory, fileName, radTempMtx, airTempMtx, SET_Mtx, PMVComfMtx, PMV_Mtx)
    elif comfortModel == "UTCI":
        result = mainUTCI(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind)
        if result != -1:
            radTempMtx, airTempMtx, UTCI_Mtx, OutdoorComfMtx, DegFromNeutralMtx = result
            if writeResultFile_ != 0:
                radTempResult, airTempResult, UTCI_Result, OutdoorComfResult, DegFromNeutralResult = writeCSVUTCI(lb_preparation, directory, fileName, radTempMtx, airTempMtx, UTCI_Mtx, OutdoorComfMtx, DegFromNeutralMtx)
    elif comfortModel == "PET":
        result = mainPET(HOYs, analysisPeriod, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, globHorizRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, mixedAirOverride, zoneHasWindows, outdoorClac, outSrfTempHeaders, outSrfTempNumbers, outdoorNonSrfViewFac, outDryBulbTemp, outRelHumid, outWindSpeed, d, a, outdoorPtHeightWeights, allWindowShadesSame, winStatusHeaders, testPtBlockName, zoneWindowTransmiss, zoneWindowNames, allWindSpeedsSame, winSpeedNumbers, dataAnalysisPeriod, northAngle, bodyCharacteristics, climate, horizInfraredRadiation, lb_preparation, lb_sunpath, lb_comfortModels, lb_wind)
        if result != -1:
            radTempMtx, airTempMtx, PET_Mtx, PET_ComfMtx, PET_CategoryMtx = result
            if writeResultFile_ != 0:
                radTempResult, airTempResult, PET_Result, PET_ComfResult, PET_CategoryResult = writeCSVPET(lb_preparation, directory, fileName, radTempMtx, airTempMtx, PET_Mtx, PET_ComfMtx, PET_CategoryMtx)
