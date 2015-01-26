# This component assembles an analysis recipe for the annual adaptive comfort component
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to assemble a recipe for the "Honeybee_Annual Adaptive Indoor Comfort Analysis" component.
-
Provided by Honeybee 0.0.55
    
    Args:
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".
        _srfIndoorTemp: A list surfaceIndoorTemp data out of the "Honeybee_Read EP Surface Result" component.
        _testPtsViewFactor: The data tree of view factors that comes out of the "Honeybee_Indoor View Factor Calculator".  These will be used to weight the temperature effect of each surface for each of the points in the test mesh.
        _zoneSrfNames: The data tree of zone surface names that comes out of the "Honeybee_Indoor View Factor Calculator".  This is essentially a branched data tree with the names of each of the surfaces for each zone.
        ===============: ...
        _location: The location output from the "Ladybug_Import epw" component.
        _cumSkyMtxOrDirNormRad: Either the output from a GenCumulativeSkyMtx component (for high-resolution analysis) or the directNormalRadiation ouput from the "Ladybug_Import epw" component (for simple, low-resolution analsysis).
        _diffuseHorizRad: If you are running a simple analysis with Direct Normal Radiation above, you must provide the diffuseHorizaontalRadiation ouput from the "Ladybug_Import epw" component here.  Otherwise, this input is not required.
        _testPts_: ...
        _testPtSkyView_: ...
        _shadingContext_: ...
        windowTransmissivity_:An optional decimal value between 0 and 1 that represents the transmissivity of windows around the person.  This can also be a list of 8760 values between 0 and 1 that represents a list of hourly window transmissivties, in order to represent the effect of occupants pulling blinds over the windows, etc.
        ===============: ...
        _zoneAirTemp: The airTemperature output of the "Honeybee_Read EP Result" component.
        _testPtZoneWeights: The testPtZoneWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with the weights of values of each zone for each of the test points.
        _testPtZoneNames: The testPtZoneNames output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a list with the names of each zone.
        _ptHeightWeights: The ptHeightWeights output of the 'Honeybee_Indoor View Factor Calculator' component.  This is essentially a branched data tree with weights of values for each point depending upon their height in the space and will be used to account for stratification in each zone.
    Returns:
        readMe!: ...
        ===============: ...
        comfAnalysisRecipe: An analysis recipe for the "Honeybee_Annual Adaptive Indoor Comfort Analysis" component.
"""

ghenv.Component.Name = "Honeybee_Annual Comfort Analysis Recipe"
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
    #Create a function to check and create a Python list from a datatree
    def checkCreateDataTree(dataTree, dataName, dataType, srfVal):
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
            checkData2 = True
        else:
            checkData2 = False
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
            checkData4 = True
        else:
            checkData4 = False
            warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if checkData2 == True:
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
                checkData5 = True
            else:
                checkData5 = False
                warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if sum(headUnitCheck) == len(dataHeaders):
                checkData6 = True
            else:
                checkData6 = False
                warning = "Not all of the connected " + dataName + " data is for indoor surface temperture."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            #See if the data is for the whole year.
            if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
                if simStep == 'hourly' or simStep == 'Hourly': pass
                else:
                    checkData6 = False
                    warning = "Simulation data must be hourly."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                checkData6 = False
                warning = "Simulation data must be for the whole year."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
        else:
            checkData5 = False
            checkData6 == False
            if dataLength == 8760: annualData = True
            else: annualData = False
            simStep = 'unknown timestep'
            headerUnits = 'unknown units'
            dataHeaders = []
        
        return checkData5, checkData6, headerUnits, dataHeaders, dataNumbers
    
    
    checkData1, checkData2, airTempUnits, airTempDataHeaders, airTempDataNumbers = checkCreateDataTree(_zoneAirTemp, "_zoneAirTemp", "Air Temperature", False)
    checkData3, checkData4, srfTempUnits, srfTempHeaders, srfTempNumbers = checkCreateDataTree(_srfIndoorTemp, "_srfIndoorTemp", "Inner Surface Temperature", False)
    
    
    #Convert the data tree of _zoneSrfNames to py data.
    zoneSrfNames = []
    checkData5 = True
    if _zoneSrfNames.BranchCount != 0:
        if _zoneSrfNames.Branch(0)[0] != None:
            for i in range(_zoneSrfNames.BranchCount):
                branchList = _zoneSrfNames.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                zoneSrfNames.append(dataVal)
        else:
            checkData5 = False
            print "Connect a data tree of zone surface names from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData5 = False
        print "Connect a data tree of zone surface names from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _testPtsViewFactor to py data.
    testPtsViewFactor = []
    checkData6 = True
    if _testPtsViewFactor.BranchCount != 0:
        if _testPtsViewFactor.Branch(0)[0] != None:
            for i in range(_testPtsViewFactor.BranchCount):
                zoneBranch = _testPtsViewFactor.Path(i)[0]
                branchList = _testPtsViewFactor.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: testPtsViewFactor[zoneBranch].append(dataVal)
                except:
                    testPtsViewFactor.append([])
                    testPtsViewFactor[zoneBranch].append(dataVal)
        else:
            checkData6 = False
            print "Connect a data tree of test point view factors from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData6 = False
        print "Connect a data tree of test point view factors from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _viewFactorMesh to py data.
    viewFactorMesh = []
    checkData7 = True
    if checkData6 == True:
        if _viewFactorMesh.BranchCount != 0:
            if _viewFactorMesh.Branch(0)[0] != None:
                for i in range(_viewFactorMesh.BranchCount):
                    branchList = _viewFactorMesh.Branch(i)
                    dataVal = []
                    for item in branchList:
                        dataVal.append(item)
                    viewFactorMesh.append(dataVal)
            else:
                checkData7 = False
                print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
        else:
            checkData7 = False
            print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    else: checkData7 = False
    
    #Check to be sure that the number of mesh faces and test points match.
    checkData8 = True
    if checkData6 == True and checkData7 == True:
        for zoneCount, zone in enumerate(viewFactorMesh):
            if len(zone) != 1:
                totalFaces = 0
                for meshCount, mesh in enumerate(zone):
                    totalFaces = totalFaces +mesh.Faces.Count
                if totalFaces == len(testPtsViewFactor[zoneCount]): pass
                else:
                    checkData8 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtsViewFactor do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                if zone[0].Faces.Count == len(testPtsViewFactor[zoneCount]): pass
                else:
                    checkData8 = False
                    warning = "For one of the meshes in the _viewFactorMesh, the number of faces in the mesh and test points in the _testPtsViewFactor do not match.\n" + \
                    "This can sometimes happen when you have geometry created with one Rhino model tolerance and you generate a mesh off of it with a different tolerance.\n"+ \
                    "Try changing your Rhino model tolerance and seeing if it works."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the solar-related inputs to see if the effects of direct sun should be considered.
    calcSolar = False
    
    #Check to be sure the there is a _dirNormRad_ and use it to set the method of the component.
    checkData9 = True
    directSolarRad = []
    if len(_dirNormRad_) > 0:
        if _dirNormRad_ != [None]:
            try:
                if 'Direct Normal Radiation' in _dirNormRad_[2] and len(_dirNormRad_) == 8767:
                    location = _dirNormRad_[1]
                    directSolarRad = _dirNormRad_[7:]
                else:
                    checkData9 = False
                    warning = 'Weather data connected to _dirNormRad_ is not Direct Normal Radiation or is not hourly data for a full year.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                checkData9 = False
                warning = 'Invalid value for _dirNormRad_.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData9 = False
            warning = 'Null value connected for _dirNormRad_.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    # Get the diffuse Horizontal radiation.
    checkData10 = True
    diffSolarRad = []
    if len(_diffuseHorizRad_) > 0:
        if _diffuseHorizRad_ != [None]:
            if str(_diffuseHorizRad_[0]) == 'key:location/dataType/units/frequency/startsAt/endsAt':
                try:
                    if 'Diffuse Horizontal Radiation' in _diffuseHorizRad_[2] and len(_diffuseHorizRad_) == 8767:
                        diffSolarRad = _diffuseHorizRad_[7:]
                    else:
                        checkData10 = False
                        warning = 'Weather data connected to _diffuseHorizRad_ is not Diffuse Horizontal Radiation or is not hourly data for a full year.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                except:
                    checkData10 = False
                    warning = 'Invalid value for _diffuseHorizRad_.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                checkData10 = False
                warning = 'Invalid value for _diffuseHorizRad_.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData10 = False
            warning = 'Null value connected for _diffuseHorizRad_.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Pull the location data from the inputs.
    checkData11 = True
    latitude = None
    longitude = None
    timeZone = None
    if _location_ != None:
        try:
            locList = _location_.split('\n')
            for line in locList:
                if "Latitude" in line: latitude = float(line.split(',')[0])
                elif "Longitude" in line: longitude = float(line.split(',')[0])
                elif "Time Zone" in line: timeZone = float(line.split(',')[0])
        except:
            checkData11 = False
            warning = 'The connected _location_ is not a valid location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Set Default floor reflectivity and clothing absorptivity.
    floorR = 0.25
    cloA = 0.7
    
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
    
    #Convert the data tree of _testPtSkyView_ to py data.
    testPtSkyView = []
    checkData15 = True
    if _testPtSkyView_.BranchCount != 0:
        if _testPtSkyView_.Branch(0)[0] != None:
            for i in range(_testPtSkyView_.BranchCount):
                zoneBranch = _testPtSkyView_.Path(i)[0]
                branchList = _testPtSkyView_.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: testPtSkyView[zoneBranch].extend(dataVal)
                except:
                    testPtSkyView.append([])
                    testPtSkyView[zoneBranch].extend(dataVal)
        else:
            checkData15 = False
            warning = "Connect a data tree of test point sky view factors from the 'Honeybee_Indoor View Factor Calculator' component."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Convert the data tree of _shadingContext_ to py data.
    shadingContext = []
    checkData16 = True
    if _shadingContext_.BranchCount != 0:
        if _shadingContext_.Branch(0)[0] != None:
            for i in range(_shadingContext_.BranchCount):
                zoneBranch = _shadingContext_.Path(i)[0]
                branchList = _shadingContext_.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: shadingContext[zoneBranch].extend(dataVal)
                except:
                    shadingContext.append([])
                    shadingContext[zoneBranch].extend(dataVal)
        else:
            checkData16 = False
            warning = "Connect a data tree of shadingContext from the 'Honeybee_Indoor View Factor Calculator' component."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Convert the data tree of _testPts_ to py data.
    testPts = []
    checkData17 = True
    if _testPts_.BranchCount != 0:
        if _testPts_.Branch(0)[0] != None:
            for i in range(_testPts_.BranchCount):
                zoneBranch = _testPts_.Path(i)[0]
                branchList = _testPts_.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: testPts[zoneBranch].extend(dataVal)
                except:
                    testPts.append([])
                    testPts[zoneBranch].extend(dataVal)
        else:
            checkData17 = False
            warning = "Connect a data tree of testPts from the 'Honeybee_Indoor View Factor Calculator' component."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Check to see if all of the solar inputs are there in order to account for solar radiation in the rad temp calculation.
    if latitude != None and longitude != None and timeZone != None and diffSolarRad != [] and directSolarRad != [] and testPtSkyView != [] and shadingContext != [] and testPts != []:
        calcSolar = True
    elif latitude != None or longitude != None or timeZone != None or diffSolarRad != [] or directSolarRad != [] or testPtSkyView != [] or shadingContext != [] or testPts != []:
        warning = "You must connect all required solar inputs to account for direct solar radiation falling on occupants."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: print "None of the inputs for solar radiation are connected and so the generated MRT maps will only use the zone surface temperature data."
    
    
    
    # CHECKING AIR INPUTS
    
    #Check the list of _testPtZoneNames.
    testPtZoneNames = []
    checkData18 = True
    if len(_testPtZoneNames) > 0: testPtZoneNames = _testPtZoneNames
    else:
        checkData18 = False
        print "Connect a data tree of testPtZoneNames from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _testPtZoneWeights to py data.
    testPtZoneWeights = []
    checkData12 = True
    if _testPtZoneWeights.BranchCount != 0:
        if _testPtZoneWeights.Branch(0)[0] != None:
            for i in range(_testPtZoneWeights.BranchCount):
                zoneBranch = _testPtZoneWeights.Path(i)[0]
                branchList = _testPtZoneWeights.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: testPtZoneWeights[zoneBranch].append(dataVal)
                except:
                    testPtZoneWeights.append([])
                    testPtZoneWeights[zoneBranch].append(dataVal)
        else:
            checkData12 = False
            print "Connect a data tree of test point zone weights from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData12 = False
        print "Connect a data tree of test point zone weights from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _ptHeightWeights to py data.
    ptHeightWeights = []
    checkData13 = True
    if _ptHeightWeights.BranchCount != 0:
        if _ptHeightWeights.Branch(0)[0] != None:
            for i in range(_ptHeightWeights.BranchCount):
                zoneBranch = _ptHeightWeights.Path(i)[0]
                branchList = _ptHeightWeights.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                try: ptHeightWeights[zoneBranch].extend(dataVal)
                except:
                    ptHeightWeights.append([])
                    ptHeightWeights[zoneBranch].extend(dataVal)
        else:
            checkData13 = False
            print "Connect a data tree of test point height weights from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData13 = False
        print "Connect a data tree of test point height weights from the 'Honeybee_Indoor View Factor Calculator' component."
    
    
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True and checkData14 == True and checkData15 == True and checkData16 == True and checkData17 == True and checkData18 == True:
        checkData = True
    else: checkData = False
    
    return checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights



#Check the data input.
checkData = False
if _srfIndoorTemp.BranchCount > 0 and str(_srfIndoorTemp) != "tree {0}" and _viewFactorMesh.BranchCount > 0 and str(_viewFactorMesh) != "tree {0}" and _testPtsViewFactor.BranchCount > 0 and str(_testPtsViewFactor) != "tree {0}" and _zoneSrfNames.BranchCount > 0 and str(_zoneSrfNames) != "tree {0}" and _zoneAirTemp.BranchCount > 0 and str(_zoneAirTemp) != "tree {0}" and _testPtZoneWeights.BranchCount > 0 and str(_testPtZoneWeights) != "tree {0}" and len(_testPtZoneNames) > 0:
    checkData, srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights = checkTheInputs()

if checkData == True:
    comfAnalysisRecipe = [srfTempNumbers, srfTempHeaders, airTempDataNumbers, airTempDataHeaders, srfTempUnits, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR, testPtZoneNames, testPtZoneWeights, ptHeightWeights]
