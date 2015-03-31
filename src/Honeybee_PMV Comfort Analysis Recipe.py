# This component assembles an analysis recipe for the annual adaptive comfort component
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to assemble an adaptive comfort recipe for the "Honeybee_Annual Indoor Comfort Analysis" component.
-
Provided by Honeybee 0.0.56
    
    Args:
        _viewFactorMesh: The data tree of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".
        _viewFactorInfo: The python list that comes out of the  "Honeybee_Indoor View Factor Calculator".
        _epwFile: The epw file that was used to run the EnergyPlus model.  This will be used to generate sun vectors and get radiation data for estimating the temperature delta for sun falling on occupants.
        ===============: ...
        _srfIndoorTemp: A list surfaceIndoorTemp data out of the "Honeybee_Read EP Surface Result" component.
        _zoneAirTemp: The airTemperature output of the "Honeybee_Read EP Result" component.
        _zoneRelHumid: The relativeHumidity output of the "Honeybee_Read EP Result" component.
        _zoneAirFlowVol: The airFlowVolume output of the "Honeybee_Read EP Result" component.
        _zoneAirHeatGain: The airHeatGainRate output of the "Honeybee_Read EP Result" component.
        metabolicRate_: A number representing the metabolic rate of the human subject in met.  If no value is input here, the component will assume a metabolic rate of 1 met, which is the metabolic rate of a seated human being.  This input can also accept a list of 8760 metabolic rates to represent how an occuant's metabolic rate might change from hour to hour.
        clothingLevel_: A number representing the clothing level of the human subject in clo.  If no value is input here, the component will assume a clothing level of 1 clo, which is roughly the insulation provided by a 3-piece suit. A person dressed in shorts and a T-shirt has a clothing level of roughly 0.5 clo and a person in a thick winter jacket can have a clothing level as high as 2 to 4 clo.  This input can also accept a list of 8760 clothing levels to represent how an occuant's clothing might change from hour to hour.
        ===============: ...
        comfortPar_: Optional comfort parameters from the "Ladybug_PMV Comfort Parameters" component.  Use this to adjust maximum and minimum acceptable humidity ratios.  These comfortPar can also change whether comfort is defined by eighty or ninety percent of people comfortable.  By default, comfort is defined as 90% of the occupants comfortable and there are no limits on humidity when there is no thermal stress.
        wellMixedAirOverride_: Set to "True" if you know that your building will have a forced air system with diffusers meant to mix the air as well as possilbe.  This will prevent the calculation from running the air stratification function and instead assume well mixed conditions.  This input can also be a list of 8760 boolean values that represent the hours of the year when a forced air system or ceiling fans are run to mix the air.  The default is set to 'False' to run the stratification calculation for every hour of the year, assuming either no a convection-based heating/cooling system
        inletHeightOverride_: An optional list of float values that match the data tree of view factor meshes and represent the height, in meters, from the bottom of the view factor mesh to the window inlet height.  This will override the default value used in the air stratification calculation, which sets the inlet height in the bottom half of the average glazing height.
        windowTransmissivity_: An optional decimal value between 0 and 1 that represents the transmissivity of windows around the person.  This can also be a list of 8760 values between 0 and 1 that represents a list of hourly window transmissivties, in order to represent the effect of occupants pulling blinds over the windows, etc. Note that you should only set a value here if you are using this component for indoor analysis where the only means by which sunlight will hit an occupant is if it comes through a window.  The default is set to 0.7, which is the trasmissivity of the default Honeybee glazing construction. 
        floorReflectivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation reflected off of the ground.  By default, this is set to 0.25, which is characteristic of most indoor floors.  You may want to increase this value for concrete or decrease it for dark carpets.
        clothingAbsorptivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation absorbed by the human body. The default is set to 0.7 for (average/brown) skin and average clothing.  You may want to increase this value for darker skin or darker clothing.
    Returns:
        readMe!: ...
        ===============: ...
        comfRecipe: An analysis recipe for the "Honeybee_Annual Indoor Comfort Analysis" component.
"""

ghenv.Component.Name = "Honeybee_PMV Comfort Analysis Recipe"
ghenv.Component.NickName = 'PMVComfRecipe'
ghenv.Component.Message = 'VER 0.0.56\nFEB_09_2015'
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


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    #Convert the data tree of _viewFactorMesh to py data.
    viewFactorMesh = []
    checkData13 = True
    if _viewFactorMesh.BranchCount != 0:
        if _viewFactorMesh.Branch(0)[0] != None:
            for i in range(_viewFactorMesh.BranchCount):
                branchList = _viewFactorMesh.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                viewFactorMesh.append(dataVal)
        else:
            checkData13 = False
            print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData13 = False
        print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    
    
    #Unpack the viewFactorInfo.
    checkData25 = True
    try:
        testPtViewFactor, zoneSrfNames, testPtSkyView, testPtBlockedVec, testPtZoneWeights, testPtZoneNames, ptHeightWeights, zoneInletInfo, zoneHasWindows = _viewFactorInfo
    except:
        testPtViewFactor, zoneSrfNames, testPtSkyView, testPtBlockedVec, testPtZoneWeights, testPtZoneNames, ptHeightWeights, zoneInletInfo, zoneHasWindows = [], [], [], [], [], [], [], [], []
        checkData25 = False
        warning = "_viewFactorInfo is not valid."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Create a function to check and create a Python list from a datatree
    def checkCreateDataTree(dataTree, dataName, dataType):
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
            dataCheck2 = True
        else:
            dataCheck2 = False
            warning = "Not all of the connected " + dataName + " has a Ladybug/Honeybee header on it.  This header is necessary to generate an indoor temperture map with this component."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        #Check to be sure that the lengths of data in in the dataTree branches are all the same.
        dataLength = len(dataNumbers[0])
        dataLenCheck = []
        for list in dataNumbers:
            if len(list) == dataLength:
                dataLenCheck.append(1)
            else: pass
        if sum(dataLenCheck) == len(dataNumbers) and dataLength <8761:
            dataCheck4 = True
        else:
            dataCheck4 = False
            warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if dataCheck2 == True:
            #Check to be sure that all of the data headers say that they are of the same type.
            header = dataHeaders[0]
            
            headerUnits =  header[3]
            headerStart = header[5]
            headerEnd = header[6]
            simStep = str(header[4])
            headUnitCheck = []
            headPeriodCheck = []
            for head in dataHeaders:
                if dataType in head[2]:
                    headUnitCheck.append(1)
                if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                    headPeriodCheck.append(1)
                else: pass
            
            if sum(headPeriodCheck) == len(dataHeaders):
                dataCheck5 = True
            else:
                dataCheck5 = False
                warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if sum(headUnitCheck) == len(dataHeaders):
                dataCheck6 = True
            else:
                dataCheck6 = False
                warning = "Not all of the connected " + dataName + " data is for indoor surface temperture."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            #See if the data is for the whole year.
            if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
                if simStep == 'hourly' or simStep == 'Hourly': pass
                else:
                    dataCheck6 = False
                    warning = "Simulation data must be hourly."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                dataCheck6 = False
                warning = "Simulation data must be for the whole year."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
        else:
            dataCheck5 = False
            dataCheck6 == False
            if dataLength == 8760: annualData = True
            else: annualData = False
            simStep = 'unknown timestep'
            headerUnits = 'unknown units'
            dataHeaders = []
        
        return dataCheck5, dataCheck6, headerUnits, dataHeaders, dataNumbers
    
    #Run all of the EnergyPlus data through the check function.
    checkData1, checkData2, airTempUnits, airTempDataHeaders, airTempDataNumbers = checkCreateDataTree(_zoneAirTemp, "_zoneAirTemp", "Air Temperature")
    checkData3, checkData4, srfTempUnits, srfTempHeaders, srfTempNumbers = checkCreateDataTree(_srfIndoorTemp, "_srfIndoorTemp", "Inner Surface Temperature")
    checkData21, checkData22, flowVolUnits, flowVolDataHeaders, flowVolDataNumbers = checkCreateDataTree(_zoneAirFlowVol, "_zoneAirFlowVol", "Air Flow Volume")
    checkData23, checkData24, heatGainUnits, heatGainDataHeaders, heatGainDataNumbers = checkCreateDataTree(_zoneAirHeatGain, "_zoneAirHeatGain", "Air Heat Gain Rate")
    checkData17, checkData18, relHumidUnits, relHumidDataHeaders, relHumidDataNumbers = checkCreateDataTree(_zoneRelHumid, "_zoneRelHumid", "Relative Humidity")
    
    #Check to be sure that the units of flowVol and heat gain are correct.
    checkData9 = True
    if flowVolUnits == "m3/s": pass
    else:
        checkData9 = False
        warning = "_zoneFlowVol must be in m3/s."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData10 = True
    if heatGainUnits == "W": pass
    else:
        checkData10 = False
        warning = "_zoneHeatGain must be in W."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData11 = True
    if airTempUnits == srfTempUnits == "C": pass
    else:
        checkData11 = False
        warning = "_zoneAirTemp and _srfIndoorTemp must be in degrees C."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    checkData19 = True
    if relHumidUnits == "%": pass
    else:
        checkData11 = False
        warning = "_zoneRelHumid must be in %."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Try to parse the weather file in order to get direct rad, diffuse rad, and location data.
    checkData5 = True
    if not os.path.isfile(_epwFile):
        checkData5 = False
        warningM = "Failed to find the file: " + str(_epwFile)
        print warningM
        ghenv.Component.AddRuntimeMessage(w, warningM)
    else:
        locationData = lb_preparation.epwLocation(_epwFile)
        location = locationData[-1]
        weatherData = lb_preparation.epwDataReader(_epwFile, locationData[0])
        directNormalRadiation = weatherData[5]
        diffuseHorizontalRadiation = weatherData[6]
    
    #Separate out the _dirNormRad, the diffuse Horizontal rad, and the location  data.
    directSolarRad = []
    diffSolarRad = []
    latitude = None
    longitude = None
    timeZone = None
    if checkData5 == True:
        directSolarRad = directNormalRadiation[7:]
        diffSolarRad = diffuseHorizontalRadiation[7:]
        locList = location.split('\n')
        for line in locList:
            if "Latitude" in line: latitude = float(line.split(',')[0])
            elif "Longitude" in line: longitude = float(line.split(',')[0])
            elif "Time Zone" in line: timeZone = float(line.split(',')[0])
    
    
    #Check to be sure that the number of mesh faces and test points match.
    checkData8 = True
    if checkData25 == True:
        for zoneCount, zone in enumerate(viewFactorMesh):
            if len(zone) != 1:
                totalFaces = 0
                for meshCount, mesh in enumerate(zone):
                    totalFaces = totalFaces +mesh.Faces.Count
                if totalFaces == len(testPtViewFactor[zoneCount]): pass
                else:
                    checkData8 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtViewFactor do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                if zone[0].Faces.Count == len(testPtViewFactor[zoneCount]): pass
                else:
                    checkData8 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtViewFactor do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Figure out the number of times to divide the sky based on the length of the blockedVec list.
    numSkyPatchDivs = 0
    checkData12 = True
    if checkData25 == True:
        if len(testPtBlockedVec[0][0]) == 145: numSkyPatchDivs = 0
        elif len(testPtBlockedVec[0][0]) == 580: numSkyPatchDivs = 1
        elif len(testPtBlockedVec[0][0]) == 2320: numSkyPatchDivs = 2
        elif len(testPtBlockedVec[0][0]) == 9280: numSkyPatchDivs = 3
        else:
            checkData12 = False
            warning = "You have an absurdly high number of view vectors from the 'Indoor View Factor' component such that it is not supported by the current component."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Check the metabolicRate_.
    checkData20 = True
    metabolicRate = []
    if metabolicRate_ != []:
        if len(metabolicRate_) == 8760:
            for val in metabolicRate_:
                metabolicRate.append(val)
        elif len(metabolicRate_) == 1:
            for count in range(8760):
                metabolicRate.append(metabolicRate_[0])
        else:
            checkData20 = False
            warning = 'metabolicRate_ must be either a list of 8760 values that correspond to hourly air mixing over the year or a single constant value for the whole year.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for count in range(8760):
            metabolicRate.append(1.0)
        print 'No value found for metabolicRate_.  The metabolic rate will be set to 1 met.'
    
    #Check the clothingLevel_.
    checkData26 = True
    clothingLevel = []
    if clothingLevel_ != []:
        if len(clothingLevel_) == 8760:
            for val in clothingLevel_:
                clothingLevel.append(val)
        elif len(clothingLevel_) == 1:
            for count in range(8760):
                clothingLevel.append(clothingLevel_[0])
        else:
            checkData26 = False
            warning = 'clothingLevel_ must be either a list of 8760 values that correspond to hourly air mixing over the year or a single constant value for the whole year.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for count in range(8760):
            clothingLevel.append(1.0)
        print 'No value found for clothingLevel_.  The clothing level will be set to 1 clo or a 3-piece suit.'
    
    #Check the floor reflectivity.
    checkData6 = True
    floorR = 0.25
    if floorReflectivity_ != None:
        if floorReflectivity_ <= 1.0 and floorReflectivity_ >= 0.0: floorR = floorReflectivity_
        else:
            checkData6 = False
            warning = 'floorReflectivity_ must be a value between 0 and 1.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'No value found for floorReflectivity_.  The reflectivity will be set to 0.25 for a typical indoor floor.'
    
    #Check the clothing absorptivity.
    checkData7 = True
    cloA = 0.7
    if cloAbsorptivity_ != None:
        if cloAbsorptivity_ <= 1.0 and cloAbsorptivity_ >= 0.0: floorR = cloAbsorptivity_
        else:
            checkData7 = False
            warning = 'cloAbsorptivity_ must be a value between 0 and 1.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'No value found for cloAbsorptivity_.  The absorptivity will be set to 0.7 for average brown skin and typical clothing.'
    
    #Check the windowTransmissivity_.
    checkData14 = True
    winTrans = []
    if windowTransmissivity_ != []:
        if len(windowTransmissivity_) == 8760:
            allGood = True
            for transVal in windowTransmissivity_:
                transFloat = float(transVal)
                if transFloat <= 1.0 and transFloat >= 0.0: winTrans.append(transFloat)
                else: allGood = False
            if allGood == False:
                checkData14 = False
                warning = 'windowTransmissivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        elif len(windowTransmissivity_) == 1:
            if windowTransmissivity_[0] <= 1.0 and windowTransmissivity_[0] >= 0.0:
                for count in range(8760):
                    winTrans.append(windowTransmissivity_[0])
            else:
                checkData14 = False
                warning = 'windowTransmissivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData14 = False
            warning = 'windowTransmissivity_ must be either a list of 8760 values that correspond to hourly changing transmissivity over the year or a single constant value for the whole year.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for count in range(8760):
            winTrans.append(0.7)
        print 'No value found for windowTransmissivity_.  The window transmissivity will be set to 0.7 for a typical double-glazed window without a low-E coating.'
    
    #Check the inletHeightOverride_.
    inletHeightOverride = []
    checkData15 = True
    if checkData25 == True and len(inletHeightOverride_) > 0:
        if len(inletHeightOverride_) == len(viewFactorMesh): inletHeightOverride = inletHeightOverride_
        else:
            checkData15 = False
            warning = 'The length of data in the inletHeightOverride_ does not match the number of branches in the data tree of the _viewFactorMesh.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Check the wellMixedAirOverride_.
    checkData16 = True
    mixedAirOverride = []
    if wellMixedAirOverride_ != []:
        if len(wellMixedAirOverride_) == 8760:
            for val in wellMixedAirOverride_:
                mixedAirOverride.append(int(val))
        elif len(wellMixedAirOverride_) == 1:
            for count in range(8760):
                mixedAirOverride.append(int(wellMixedAirOverride_[0]))
        else:
            checkData16 = False
            warning = 'wellMixedAirOverride_ must be either a list of 8760 values that correspond to hourly air mixing over the year or a single constant value for the whole year.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for count in range(8760):
            mixedAirOverride.append(0)
        print 'No value found for wellMixedAirOverride_.  The stratification calculation will be run for every hour of the year.'
    
    #If there are comfort parameters hooked up, read them out.
    checkData27 = True
    if comfortPar_ != []:
        try:
            eightyPercentComf = bool(comfortPar_[0])
            humidRatioUp = float(comfortPar_[1])
            humidRatioLow = float(comfortPar_[2])
        except:
            eightyPercentComf = False
            humidRatioUp = 0.03
            humidRatioLow = 0.0
            checkData27 = False
            warning = 'The comfortPar are not valid comfort parameters from the Ladybug_Comfort Parameters component.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        eightyPercentComf = False
        humidRatioUp = 0.03
        humidRatioLow = 0.0
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True and checkData14 == True and checkData15 == True and checkData16 == True and checkData17 == True and checkData18 == True and checkData19 == True and checkData20 == True and checkData21 == True and checkData22 == True and checkData23 == True and checkData24 == True and checkData25 == True  and checkData26 == True and checkData27 == True:
        checkData = True
    else: checkData = False
    
    return checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows



#Check to be sure that LB+HB are flying.
initCheck = False
if sc.sticky.has_key('honeybee_release') == False and sc.sticky.has_key('ladybug_release') == False:
    print "You should first let Ladybug and Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug and Honeybee fly...")
else:
    initCheck = True
    lb_preparation = sc.sticky["ladybug_Preparation"]()


#Check the data input.
checkData = False
if _viewFactorMesh.BranchCount > 0 and len(_viewFactorInfo) > 0 and _epwFile != None and _srfIndoorTemp.BranchCount > 0 and _zoneAirTemp.BranchCount > 0  and _zoneAirFlowVol.BranchCount > 0 and _zoneAirHeatGain.BranchCount > 0 and _zoneRelHumid.BranchCount > 0 and initCheck == True:
    if _viewFactorInfo[0] != None:
        checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows = checkTheInputs()

if checkData == True:
    comfRecipe = ["PMV", srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, flowVolDataHeaders, flowVolDataNumbers, heatGainDataHeaders, heatGainDataNumbers, relHumidDataHeaders, relHumidDataNumbers, clothingLevel, metabolicRate, zoneSrfNames, testPtViewFactor, viewFactorMesh, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPtBlockedVec, numSkyPatchDivs, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights, zoneInletInfo, inletHeightOverride, eightyPercentComf, humidRatioUp, humidRatioLow, mixedAirOverride, zoneHasWindows]
