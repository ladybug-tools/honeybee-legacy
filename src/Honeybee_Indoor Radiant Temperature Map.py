# This component creates a radiant temperature map based on an energy simulation output.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create an indoor MRT map based on srfIndoorTemp data out of the "Honeybee_Read EP Surface Result" component.
_
By default, the temperature map will be created based on the average value of mean radiant temperature for each surface.
If total annual simulation data has been connected, the analysisPeriod_ input can be used to select out a specific period fo the year for coloration.
In order to color surfaces by individual hours, connecting interger values to the "stepOfSimulation_" will allow you to scroll though each step of the input data.
-
Provided by Honeybee 0.0.55
    
    Args:
        _srfIndoorTemp: A list surfaceIndoorTemp data out of the "Honeybee_Read EP Surface Result" component.
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".  These will be colored with MRT data.
        _testPtsViewFactor: The data tree of view factors that comes out of the "Honeybee_Indoor View Factor Calculator".  These will be used to weight the temperature effect of each surface for each of the points in the test mesh.
        _zoneSrfNames: The data tree of zone surface names that comes out of the "Honeybee_Indoor View Factor Calculator".  This is essentially a branched data tree with the names of each of the surfaces for each zone.
        ===============: ...
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to "stepOfSimulation_" will override this input.
        stepOfSimulation_: Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        _runIt: Set boolean to "True" to run the component and create the indoor radiant temperature map.
    Returns:
        readMe!: ...
        MRTMesh: A list of colored meshes showing the distribution of radiant temperature over each input _HBZone.
        legend: A legend for the air temperature map. Connect this output to a grasshopper "Geo" component in order to preview the legend spearately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the building with the grasshopper "move" component.
        ==========: ...
        testPtsMRT: The values of mean radiant temperture (MRT) at each of the test points (this is what is used to  being used to color the mesh).
        pointColors: The colors that correspond to each of the test points.

"""

ghenv.Component.Name = "Honeybee_Indoor Radiant Temperature Map"
ghenv.Component.NickName = 'RadiantTempMap'
ghenv.Component.Message = 'VER 0.0.55\nDEC_20_2014'
ghenv.Component.Category = "Honeybee"
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



inputsDict = {
    
0: ["_srfIndoorTemp", "A list surfaceIndoorTemp data out of the 'Honeybee_Read EP Surface Result' component."],
1: ["_viewFactorMesh", "The list of view factor meshes that comes out of the  'Honeybee_Indoor View Factor Calculator'.  These will be colored with MRT data."],
2: ["_testPtsViewFactor", "The data tree of view factors that comes out of the 'Honeybee_Indoor View Factor Calculator'.  These will be used to weight the temperature effect of each surface for each of the points in the test mesh."],
3: ["_zoneSrfNames", "The data tree of zone surface names that comes out of the 'Honeybee_Indoor View Factor Calculator'.  This is essentially a branched data tree with the names of each of the surfaces for each zone."],
4: ["===============", "..."],
5: ["_location_", "..."],
6: ["_dirNormRad_", "..."],
7: ["_diffuseHorizRad_", "..."],
8: ["_testPts_", "..."],
9: ["_testPtSkyView_", "..."],
10: ["_shadingContext_", "..."],
11: ["windowTransmissivity_", "..."],
12: ["floorReflectivity_", "..."],
13: ["cloAbsorptivity_", "..."],
14: ["===============", "..."],
15: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year and the data is hourly.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input."],
16: ["stepOfSimulation_", "Optional interger for the hour of simulation to color the surfaces with.  Connecting a value here will override the analysisPeriod_ input."],
17: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
18: ["_runIt", "Set boolean to 'True' to run the component and color the zone surfaces."]
}


w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    #Create a Python list from the _srfIndoorTemp
    dataPyList = []
    for i in range(_srfIndoorTemp.BranchCount):
        branchList = _srfIndoorTemp.Branch(i)
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
        warning = "Not all of the connected _srfIndoorTemp has a Ladybug/Honeybee header on it.  This header is necessary to generate an indoor temperture map with this component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that the lengths of data in in the _srfIndoorTemp branches are all the same.
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
        warning = "Not all of the connected _srfIndoorTemp branches are of the same length or there are more than 8760 values in the list."
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
            if "Inner Surface Temperature" in head[2]:
                headUnitCheck.append(1)
            if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                headPeriodCheck.append(1)
            else: pass
        
        if sum(headPeriodCheck) == len(dataHeaders):
            checkData5 = True
        else:
            checkData5 = False
            warning = "Not all of the connected _srfIndoorTemp branches are of the same timestep or same analysis period."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if sum(headUnitCheck) == len(dataHeaders):
            checkData6 = True
        else:
            checkData6 = False
            warning = "Not all of the connected _srfIndoorTemp data is for indoor surface temperture."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        #See if the data is for the whole year.
        if header[5] == (1, 1, 1) and header[6] == (12, 31, 24):
            annualData = True
        else: annualData = False
        
    else:
        checkData5 = False
        checkData6 == False
        if dataLength == 8760: annualData = True
        else: annualData = False
        simStep = 'unknown timestep'
        headerUnits = 'unknown units'
        dataHeaders = []
    
    #Convert the data tree of _zoneSrfNames to py data.
    zoneSrfNames = []
    checkData1 = True
    if _zoneSrfNames.BranchCount != 0:
        if _zoneSrfNames.Branch(0)[0] != None:
            for i in range(_zoneSrfNames.BranchCount):
                branchList = _zoneSrfNames.Branch(i)
                dataVal = []
                for item in branchList:
                    dataVal.append(item)
                zoneSrfNames.append(dataVal)
        else:
            checkData1 = False
            print "Connect a data tree of zone surface names from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData1 = False
        print "Connect a data tree of zone surface names from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _testPtsViewFactor to py data.
    testPtsViewFactor = []
    checkData3 = True
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
            checkData3 = False
            print "Connect a data tree of test point view factors from the 'Honeybee_Indoor View Factor Calculator' component."
    else:
        checkData3 = False
        print "Connect a data tree of test point view factors from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Convert the data tree of _viewFactorMesh to py data.
    viewFactorMesh = []
    checkData7 = True
    if checkData3 == True:
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
    if checkData3 == True and checkData7 == True:
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
    
    #Check the ground reflectivity.
    checkData12 = True
    if floorReflectivity_ != None:
        if floorReflectivity_ < 1 and floorReflectivity_ > 0:
            floorR = floorReflectivity_
        else:
            floorR = None
            checkData12 = False
            warning = '_floorReflectivity_ must be a value between 0 and 1.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        floorR = 0.25
        print 'No value found for floorReflectivity_.  The ground reflectivity will be set to 0.25 for grass or light bare soil.'
    
    #Check the clothing absorptivity.
    checkData13 = True
    if cloAbsorptivity_ != None:
        if cloAbsorptivity_ < 1 and cloAbsorptivity_ > 0:
            cloA = cloAbsorptivity_
        else:
            cloA = None
            checkData13 = False
            warning = 'cloAbsorptivity_ must be a value between 0 and 1.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        cloA = 0.7
        print 'No value found for cloAbsorptivity_.  The clothing absorptivity will be set to 0.7 for (average/brown) skin and average clothing.'
    
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
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True and checkData11 == True and checkData12 == True and checkData13 == True and checkData14 == True and checkData15 == True and checkData16 == True and checkData17 == True:
        checkData = True
    else: checkData = False
    
    return checkData, annualData, simStep, dataNumbers, dataHeaders, headerUnits, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR


def manageInputOutput(annualData, simStep):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(19):
        if input == 15 and annualData == False:
            ghenv.Component.Params.Input[input].NickName = "___________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 16 and (simStep == "Annually" or simStep == "unknown timestep"):
            ghenv.Component.Params.Input[input].NickName = "____________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    if annualData == False: analysisPeriod = [0, 0]
    else: analysisPeriod = analysisPeriod_
    if simStep == "Annually" or simStep == "unknown timestep": stepOfSimulation = None
    else: stepOfSimulation = stepOfSimulation_
    
    return analysisPeriod, stepOfSimulation

def restoreInputOutput():
    for input in range(19):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def getSrfTempData(pyZoneData, annualData, simStep, srfHeaders, headerUnits, analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization):
    #Make a list to contain the data for coloring and labeling.
    dataForColoring = []
    coloredTitle = []
    coloredUnits = None
    
    #Add basic stuff to the title.
    coloredTitle.append("Mean Radiant Temperature" + " - " + headerUnits)
    coloredUnits = headerUnits
    
    #Make lists that assist with the labaeling of the rest of the title.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
    
    #If none of the analysisperiod or stepOfSim are connected, just average all the data.
    def getColorData1():
        for list in pyZoneData:
            dataForColoring.append(round(sum(list), 4)/len(list))
    if analysisPeriod == [0, 0] and stepOfSimulation == None:
        getColorData1()
        if srfHeaders != []:
            coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    if analysisPeriod == [] and stepOfSimulation == None:
        getColorData1()
        if srfHeaders != []:
            coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    elif simStep == "Annually" or simStep == "unknown timestep":
        getColorData1()
        if srfHeaders != []:
            coloredTitle.append(str(monthNames[srfHeaders[0][5][0]-1]) + " " + str(srfHeaders[0][5][1]) + " " + str(timeNames[srfHeaders[0][5][2]-1]) + " - " + str(monthNames[srfHeaders[0][6][0]-1]) + " " + str(srfHeaders[0][6][1]) + " " + str(timeNames[srfHeaders[0][6][2]-1]))
        else: coloredTitle.append("Complete Time Period That Is Connected")
    
    # If the user has connected a stepOfSim, make the step of sim the thing used to color zones.
    if stepOfSimulation != None:
        if stepOfSimulation < len(pyZoneData[0]):
            for list in pyZoneData:
                dataForColoring.append(round(list[stepOfSimulation], 4))
            
            if simStep == "Monthly" and annualData == True: coloredTitle.append(monthNames[stepOfSimulation])
            elif simStep == "Monthly": coloredTitle.append("Month " + str(stepOfSimulation+1) + " of Simulation")
            elif simStep == "Daily": coloredTitle.append("Day " + str(stepOfSimulation+1) + " of Simulation")
            elif simStep == "Hourly": coloredTitle.append("Hour " + str(stepOfSimulation+1) + " of Simulation")
            else: coloredTitle.append("Step " + str(stepOfSimulation+1) + " of Simulation")
        else:
            warning = "The input step of the simulation is beyond the length of the simulation."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    # If the user has connected annual data, has not hooked up a step of simulation, and has hooked up an analysis period, take data from just the analysis period.
    if annualData == True and analysisPeriod != [0,0] and analysisPeriod != [] and stepOfSimulation == None and simStep != "Annually" and simStep != "unknown timestep":
        #If the data is monthly, just take the months from the analysis period.
        if simStep == "Monthly":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startMonth:endMonth+1])/len(list[startMonth:endMonth+1]), 4))
            coloredTitle.append(str(monthNames[startMonth-1]) + " - " + str(monthNames[endMonth-1]))
        #If the data is daily, just take the days and months from the analysis period.
        elif simStep == "Daily":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            #Make a function that returns the days for a given list of months
            def getDays(monthsList, startDay, endDay):
                daysList = []
                daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                for count, month in enumerate(monthsList):
                    if count == 0 and startMonth == endMonth:
                        daysList.append(daysPerMonth[month-1] + 1 - startDay + (endDay - daysPerMonth[month-1]))
                    elif count == 0:
                        daysList.append(daysPerMonth[month-1] + 1 - startDay)
                    elif count == len(monthsList) - 1 and endDay != daysPerMonth[month-1]:
                        daysList.append(endDay)
                    else:
                        daysList.append(daysPerMonth[month-1])
                return daysList
            
            #Make a list of months leading up to the first day.
            initMonths = []
            for month in range(1, startMonth+1, 1):
                initMonths.append(month)
            initDays = getDays(initMonths, 1, startDay)
            startIndex = sum(initDays)
            
            # Make a list of days in each month of the analysis period.
            monthsList = []
            for month in range(startMonth, endMonth+1, 1):
                monthsList.append(month)
            simDays = getDays(monthsList, startDay, endDay)
            endIndex = startIndex + sum(simDays)
            
            #Get the data from the lists.
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startIndex:endIndex+1])/len(list[startIndex:endIndex+1]), 4))
            
            #Add the analysis period to the title.
            coloredTitle.append(str(monthNames[startMonth-1]) + " " + str(startDay) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay))
            
        #If the data is hourly, use the ladybug preparation functions to extract the hours from the analysis period.
        elif simStep == "Hourly":
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            startHour = analysisPeriod[0][2]
            endHour = analysisPeriod[1][2]
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
            startIndex = HOYS[0]
            endIndex = HOYS[-1]
            #Get the data from the lists.
            for list in pyZoneData:
                dataForColoring.append(round(sum(list[startIndex:endIndex+1])/len(list[startIndex:endIndex+1]), 4))
            #Add the analysis period to the title.
            coloredTitle.append(str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1]))
    
    
    #Return all of the data
    return dataForColoring, coloredTitle, coloredUnits


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
    tempMatchedList = []
    for listCount, list in enumerate(srfHeaders):
        srfName = list[2].split(" for ")[-1]
        try: srfName = srfName.split(":")[0]
        except: pass
        for path in srfTempDict:
            if srfTempDict[path]["srfName"].upper() == srfName:
                tempMatchedList.append(1)
                srfTempDict[path]["srfTemp"] = srfTempValues[listCount]
    
    
    #Check if all of the data was found.
    dataCheck = True
    if len(srfHeaders) == len(srfTempDict) and len(srfHeaders) == len(tempMatchedList): pass
    elif len(tempMatchedList) == 0:
        dataCheck = False
        warning = "None of the connected srfIndoorTemp could be matched with the connected surface names and view factors. You should consider re-running your simulation since it is likely that the imported surface results are not for the _HBZones connected to the ViewFactor Component."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    else: print "Not all of the connected surface data could be found in the connected surface names and view factors.  You may want to do a view factor calculation for all of your zones in order to see all of your connected surface data."
    
    
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
    
    
    return dataCheck, pointMRTValues

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


def main(pointMRTValues, viewFactorMesh, title, legendTitle, lb_preparation, lb_visualization, legendPar):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    #If there is no max and min set, make them the max and min of all the points.
    allMRT = []
    for list in pointMRTValues:
        for mrt in list: allMRT.append(mrt)
    allMRT.sort()
    if lowB == "min": lowB = allMRT[0]
    if highB == "min": highB = allMRT[-1]
    
    #Get the colors for each zone.
    allColors = []
    transparentColors = []
    for zoneList in pointMRTValues:
        colors = lb_visualization.gradientColor(zoneList, lowB, highB, customColors)
        allColors.append(colors)
        
        #Get a list of colors with alpha values as transparent
        tcolors = []
        for color in colors:
            tcolors.append(Drawing.Color.FromArgb(125, color.R, color.G, color.B))
        transparentColors.append(tcolors)
    
    #Color the view factor meshes.
    MRTMesh = []
    segmentedColors = []
    
    for zoneCount, meshList in enumerate(viewFactorMesh):
        segmentedColors.append([])
        startVal = 0
        for mesh in meshList:
            mesFaceLen = mesh.Faces.Count
            listForMesh = allColors[zoneCount][startVal:(startVal+mesFaceLen)]
            segmentedColors[zoneCount].append(listForMesh)
            startVal += mesFaceLen
    
    for zoneCount, meshList in enumerate(viewFactorMesh):
        for meshCount, mesh in enumerate(meshList):
            mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
            
            counter = 0
            for srfNum in range(mesh.Faces.Count):
                if mesh.Faces[srfNum].IsQuad:
                    mesh.VertexColors[counter + 0] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 3] = segmentedColors[zoneCount][meshCount][srfNum]
                    counter+=4
                else:
                    mesh.VertexColors[counter + 0] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[zoneCount][meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[zoneCount][meshCount][srfNum]
                    counter+=3
            
            MRTMesh.append([mesh])
        else: pass
    
    
    #Create the legend.
    allgeo = []
    for list in viewFactorMesh: allgeo.extend(list)
    lb_visualization.calculateBB(allgeo, True)
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(allMRT, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Create the Title.
    titleTxt = '\n' + title[0] + '\n' + title[1]
    titleBasePt = lb_visualization.BoundingBoxPar[5]
    titleTextCurve = lb_visualization.text2srf([titleTxt], [titleBasePt], legendFont, textSize, legendBold)
    
    #Bring the legend and the title together.
    fullLegTxt = lb_preparation.flattenList(legendTextCrv + titleTextCurve)
    
    
    return transparentColors, MRTMesh, [legendSrfs, fullLegTxt], legendBasePoint



#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
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
if _srfIndoorTemp.BranchCount > 0 and str(_srfIndoorTemp) != "tree {0}" and checkLB == True:
    checkData, annualData, simStep, pyZoneData, srfHeaders, headerUnits, zoneSrfNames, testPtsViewFactor, viewFactorMesh, calcSolar, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, testPts, shadingContext, winTrans, cloA, floorR = checkTheInputs()

#Manage the inputs and outputs of the component based on the data that is hooked up.
if checkData == True:
    analysisPeriod, stepOfSimulation = manageInputOutput(annualData, simStep)
else: restoreInputOutput()


#Get the temperature data for the surfaces.
dataCheck = False
if _runIt == True and checkData == True:
    srfTempValues, title, legendTitle = getSrfTempData(pyZoneData, annualData, simStep, srfHeaders, headerUnits, analysisPeriod, stepOfSimulation, lb_preparation, lb_visualization)
    dataCheck, pointMRTValues = calculatePointMRT(srfTempValues, zoneSrfNames, testPtsViewFactor, srfHeaders)
    if calcSolar == True and stepOfSimulation != None and annualData == True and dataCheck == True and simStep == 'Hourly':
        pointMRTValues = calculateSolarAdjustedMRT(pointMRTValues, testPts, stepOfSimulation, latitude, longitude, timeZone, diffSolarRad, directSolarRad, testPtSkyView, shadingContext, winTrans, cloA, floorR, lb_sunpath, lb_comfortModels)


#Color the surfaces with the data and get all of the other cool stuff that this component does.
if _runIt == True and checkData == True and pointMRTValues != [] and dataCheck == True:
    pointColorsInit, MRTMeshInit, legendInit, legendBasePt = main(pointMRTValues, viewFactorMesh, title, legendTitle, lb_preparation, lb_visualization, legendPar_)
    
    #Unpack the legend.
    legend = []
    for count, item in enumerate(legendInit):
        if count == 0:
            legend.append(item)
        if count == 1:
            for srf in item:
                legend.append(srf)
    
    #Unpack the other data trees.
    testPtsMRT = DataTree[Object]()
    pointColors = DataTree[Object]()
    MRTMesh = DataTree[Object]()
    for brCount, branch in enumerate(pointMRTValues):
        for item in branch:testPtsMRT.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(pointColorsInit):
        for item in branch:pointColors.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(MRTMeshInit):
        for item in branch:MRTMesh.Add(item, GH_Path(brCount))

ghenv.Component.Params.Output[3].Hidden = True