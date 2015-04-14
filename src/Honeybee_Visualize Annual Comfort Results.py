# This component creates an air temperature map based on an energy simulation output.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to produce a colored mesh from a comfResultsMtx.
-
Provided by Honeybee 0.0.56
    
    Args:
        _comfResultsMtx: Any matrix output from the 'Honeybee_Annual Comfort Analysis' component or the 'Honeybee_Read Indoor Comfort Result' component.
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".  These will be colored with result data.
        ===========: ...
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input.
        stepOfSimulation_: Optional interger to select out a step of the simulation to color the mesh with.  Connecting a value here will override the analysisPeriod_ input.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        _runIt: Set boolean to "True" to run the component and produce a colored mesh from a comfResultsMtx.
    Returns:
        readMe!: ...
        ==========: ...
        resultMesh: A list of colored meshes showing the results form the comfResultsMtx.
        legend: A legend for the colored mesh. Connect this output to a grasshopper "Geo" component in order to preview the legend spearately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend with the grasshopper "move" component.
        ==========: ...
        resultValues: The values of results that are being used to color the results.
        resultColors: The colors used for each mesh face.

"""

ghenv.Component.Name = "Honeybee_Visualize Annual Comfort Results"
ghenv.Component.NickName = 'VisualizeComfort'
ghenv.Component.Message = 'VER 0.0.56\nAPR_12_2015'
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


w = gh.GH_RuntimeMessageLevel.Warning


inputsDict = {
    
0: ["_comfResultsMtx", "Any matrix output from the 'Honeybee_Annual Comfort Analysis' component or the 'Honeybee_Read Indoor Comfort Result' component."],
1: ["_viewFactorMesh", "The list of view factor meshes that comes out of the  'Honeybee_Indoor View Factor Calculator'.  These will be colored with result data."],
2: ["===========", "..."],
3: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that this will only work if the connected data is for a full year.  Otherwise, this input will be ignored. Also note that connecting a value to 'stepOfSimulation_' will override this input."],
4: ["stepOfSimulation_", "Optional interger to select out a step of the simulation to color the mesh with.  Connecting a value here will override the analysisPeriod_ input."],
5: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
6: ["_runIt", "Set boolean to 'True' to run the component and visualize indoor comfort."]
}


def checkTheInputs():
    #Convert the data tree of _viewFactorMesh to py data.
    viewFactorMesh = []
    checkData1 = True
    if len(_viewFactorMesh) != 0:
        viewFactorMesh = _viewFactorMesh
    else:
        checkData1 = False
        print "Connect a data tree of view factor meshes from the 'Honeybee_Indoor View Factor Calculator' component."
    
    #Check to be sure that the length of the test points and the mesh faces match.
    checkData2 = False
    dataType = None
    vertOrFace = False
    if len(_comfResultsMtx) > 0 and len(viewFactorMesh) > 0:
        dataType = _comfResultsMtx[0].split(";")[0]
        ptLen1 = len(_comfResultsMtx[1])
        meshFaceCount = []
        for mesh in viewFactorMesh:
            meshFaceCount.append(mesh.Faces.Count)
        ptLen2 = sum(meshFaceCount)
        if ptLen1 == ptLen2: checkData2 = True
        else:
            meshVertCount = []
            for mesh in viewFactorMesh:
                meshVertCount.append(mesh.Vertices.Count)
            ptLen2 = sum(meshVertCount)
            if ptLen1 == ptLen2:
                checkData2 = True
                vertOrFace = True
            else:
                warning = "The length of data in the comfResultsMTX does not matech the number of faces in the viewFactorMesh."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    else: pass
    
    #Check the analysis period.
    try:
        analysisPeriod1 = (int(_comfResultsMtx[0].split(";")[-2].split(",")[0].split("(")[-1]), int(_comfResultsMtx[0].split(";")[-2].split(",")[1].split(" ")[-1]), int(_comfResultsMtx[0].split(";")[-2].split(",")[-1].split(" ")[-1].split(")")[0]))
        analysisPeriod2 = (int(_comfResultsMtx[0].split(";")[-1].split(",")[0].split("(")[-1]), int(_comfResultsMtx[0].split(";")[-1].split(",")[1].split(" ")[-1]), int(_comfResultsMtx[0].split(";")[-1].split(",")[-1].split(" ")[-1].split(")")[0]))
        analysisPeriod = [analysisPeriod1, analysisPeriod2]
    except:
        analysisPeriod = []
    if _comfResultsMtx[0].split(";")[-2] == "(1, 1, 1)" and _comfResultsMtx[0].split(";")[-1] == "(12, 31, 24)": annualData = True
    else: annualData = False
    if len(_comfResultsMtx[1:]) == 1: simStepPossible = False
    else: simStepPossible = True
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True: checkData = True
    else: checkData = False
    
    return checkData, viewFactorMesh, dataType, annualData, simStepPossible, analysisPeriod, vertOrFace


def manageInputOutput(annualData, simStep):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(7):
        if input == 3 and annualData == False:
            ghenv.Component.Params.Input[input].NickName = "__________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 4 and simStep == False:
            ghenv.Component.Params.Input[input].NickName = "___________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

def restoreInputOutput():
    for input in range(7):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def computeComfFactor(comfResultsMtx, analysisP, stepOfSimulation, annualData, simStepPossible, lb_preparation):
    #Create a list to be filled with values of comfort.
    comfortFactorVals = []
    
    if stepOfSimulation != None and simStepPossible == True:
        comfortFactorVals = comfResultsMtx[stepOfSimulation]
    elif len(analysisP) > 0 and annualData == True:
        #Get the HOYs of the analysis period
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisP, 1)
        
        #Pick out just the hours that are in the analysis period.
        newcomfResultsMtx = []
        for lineCount, line in enumerate(comfResultsMtx):
            if lineCount in HOYS: newcomfResultsMtx.append(line)
        comfResultsMtx = newcomfResultsMtx
        
        #Transpose the matrix
        comfResultsMtx = comfResultsMtx[1:]
        comfResultsMtx = zip(*comfResultsMtx)
        
        #Compute the total percentage of comfortable hours.
        for lineCount, line in enumerate(comfResultsMtx):
            comfortFactorVals.append(sum(line)/len(line))
    else:
        #Transpose the matrix
        comfResultsMtx = comfResultsMtx[1:]
        comfResultsMtx = zip(*comfResultsMtx)
        
        #Compute the total percentage of comfortable hours.
        for lineCount, line in enumerate(comfResultsMtx):
            comfortFactorVals.append(sum(line)/len(line))
    
    return comfortFactorVals



def main(pointValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar, analysisPeriod, simStepPossible, annualData, vertOrFace):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    defaultCustomColor1 = System.Drawing.Color.FromArgb(255, 75, 107, 169)
    defaultCustomColor2 = System.Drawing.Color.FromArgb(255, 234, 38, 0)
    
    #Read the data type and assign default values for mesh types.
    if dataType == 'Degrees From Target' or dataType == 'Predicted Mean Vote':
        if dataType == 'Degrees From Target': legendTitle = 'C'
        else: legendTitle = 'PMV'
        if dataType == 'Degrees From Target': dataType = dataType + ' Temperature'
        if len(legendPar_) == 0:
            customColors = [System.Drawing.Color.FromArgb(0,136,255), System.Drawing.Color.FromArgb(200,225,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,230,230), System.Drawing.Color.FromArgb(255,0,0)]
            print dataType
            if dataType == 'Degrees From Target Temperature':
                numSeg = 11
                lowB = -5
                highB = 5
            else:
                numSeg = 11
                lowB = -2
                highB = 2
        elif customColors[0] == defaultCustomColor1 and customColors[-1] == defaultCustomColor2:
            customColors = [System.Drawing.Color.FromArgb(0,136,255), System.Drawing.Color.FromArgb(200,225,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,230,230), System.Drawing.Color.FromArgb(255,0,0)]
    elif dataType == 'Adaptive Comfort' or dataType == 'Percentage of People Dissatisfied':
        legendTitle = '%'
        if dataType == 'Adaptive Comfort':
            for valCount, value in enumerate(pointValues):
                pointValues[valCount] = value*100
        if len(legendPar_) == 0:
            lowB = 0
            highB = 100
            numSeg = 11
            if dataType == 'Adaptive Comfort': customColors = [System.Drawing.Color.FromArgb(0,0,0), System.Drawing.Color.FromArgb(127,127,127), System.Drawing.Color.FromArgb(255,255,255)]
            else: customColors = [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(127,127,127), System.Drawing.Color.FromArgb(0,0,0)]
        elif customColors[0] == defaultCustomColor1 and customColors[-1] == defaultCustomColor2:
            if dataType == 'Adaptive Comfort': customColors = [System.Drawing.Color.FromArgb(0,0,0), System.Drawing.Color.FromArgb(127,127,127), System.Drawing.Color.FromArgb(255,255,255)]
            else: customColors = [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(127,127,127), System.Drawing.Color.FromArgb(0,0,0)]
    else:
        legendTitle = 'C'
    
    #Get the colors for each zone.
    allColors = []
    transparentColors = []
    colors = lb_visualization.gradientColor(pointValues, lowB, highB, customColors)
    allColors.append(colors)
    
    #Get a list of colors with alpha values as transparent
    for color in colors:
        transparentColors.append(Drawing.Color.FromArgb(125, color.R, color.G, color.B))
    
    #Color the view factor meshes.
    resultMesh = []
    segmentedColors = []
    segmentedTanspColors = []
    segmentedValues = []
    
    if vertOrFace == True:
        colorCounter = 0
        for meshCount, mesh in enumerate(viewFactorMesh):
            mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
            resultMesh.append(mesh)
            segmentedColors.append(colors[colorCounter:(colorCounter+mesh.Vertices.Count)])
            segmentedTanspColors.append(transparentColors[colorCounter:(colorCounter+mesh.Vertices.Count)])
            segmentedValues.append(pointValues[colorCounter:(colorCounter+mesh.Vertices.Count)])
            colorCounter+=mesh.Vertices.Count
        
        for meshCount, mesh in enumerate(resultMesh):
            counter = 0
            for vertNum in range(mesh.Vertices.Count):
                mesh.VertexColors[counter] = segmentedColors[meshCount][vertNum]
                counter+=1
    else:
        colorCounter = 0
        for meshCount, mesh in enumerate(viewFactorMesh):
            mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
            resultMesh.append(mesh)
            segmentedColors.append(colors[colorCounter:(colorCounter+mesh.Faces.Count)])
            segmentedTanspColors.append(transparentColors[colorCounter:(colorCounter+mesh.Faces.Count)])
            segmentedValues.append(pointValues[colorCounter:(colorCounter+mesh.Faces.Count)])
            colorCounter+=mesh.Faces.Count
        
        for meshCount, mesh in enumerate(resultMesh):
            counter = 0
            for srfNum in range(mesh.Faces.Count):
                if mesh.Faces[srfNum].IsQuad:
                    mesh.VertexColors[counter + 0] = segmentedColors[meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[meshCount][srfNum]
                    mesh.VertexColors[counter + 3] = segmentedColors[meshCount][srfNum]
                    counter+=4
                else:
                    mesh.VertexColors[counter + 0] = segmentedColors[meshCount][srfNum]
                    mesh.VertexColors[counter + 1] = segmentedColors[meshCount][srfNum]
                    mesh.VertexColors[counter + 2] = segmentedColors[meshCount][srfNum]
                    counter+=3
    
    #Create the legend.
    lb_visualization.calculateBB(resultMesh, True)
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(pointValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Make lists that assist with the labaeling of the rest of the title.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
    
    
    #If there is an analysis period, format the text for it in the legend title.
    try:
        if len(analysisPeriod_) == 0 or annualData == False:
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            startHour = analysisPeriod[0][2]
            endHour = analysisPeriod[1][2]
            if analysisPeriod[0] != analysisPeriod[1]:
                titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1])
            else: titleDate = str(monthNames[startMonth]) + " " + str(startDay) + " " + str(timeNames[startHour-1])
        else:
            startMonth = analysisPeriod_[0][0]
            endMonth = analysisPeriod_[1][0]
            startDay = analysisPeriod_[0][1]
            endDay = analysisPeriod_[1][1]
            startHour = analysisPeriod_[0][2]
            endHour = analysisPeriod_[1][2]
            titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1])
    except:
        startMonth = analysisPeriod[0][0]
        endMonth = analysisPeriod[1][0]
        startDay = analysisPeriod[0][1]
        endDay = analysisPeriod[1][1]
        startHour = analysisPeriod[0][2]
        endHour = analysisPeriod[1][2]
        if analysisPeriod[0] != analysisPeriod[1]:
            titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1])
        else: titleDate = str(monthNames[startMonth]) + " " + str(startDay) + " " + str(timeNames[startHour-1])
    
    #Create the Title.
    try:
        if stepOfSimulation_ != None and simStepPossible == True: titleTxt = '\n' + dataType + '\n' + 'Hour ' + str(stepOfSimulation_) + ' of simulation.'
        elif len(analysisPeriod) > 0: titleTxt = '\n' + dataType + '\n' + titleDate
        else: titleTxt = '\n' + 'Average ' + dataType
    except:
        titleTxt = '\n' + 'Average ' + dataType
    titleBasePt = lb_visualization.BoundingBoxPar[5]
    titleTextCurve = lb_visualization.text2srf([titleTxt], [titleBasePt], legendFont, textSize, legendBold)
    
    #Bring the legend and the title together.
    fullLegTxt = lb_preparation.flattenList(legendTextCrv + titleTextCurve)
    
    
    return segmentedValues, segmentedTanspColors, resultMesh, [legendSrfs, fullLegTxt], legendBasePoint





#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")

checkData = False
annualData = True
simStepPossible = True
if len(_comfResultsMtx) > 0 and len(_viewFactorMesh) > 0:
    if _comfResultsMtx[0] != None and _viewFactorMesh[0] != None:
        checkData, viewFactorMesh, dataType, annualData, simStepPossible, analysisPeriod, vertOrFace = checkTheInputs()

if annualData == False or simStepPossible == False:
    manageInputOutput(annualData, simStepPossible)
else:
    restoreInputOutput()

if checkData == True and _runIt == True:
    try: resultValues = computeComfFactor(_comfResultsMtx, analysisPeriod_, stepOfSimulation_, annualData, simStepPossible, lb_preparation)
    except: resultValues = computeComfFactor(_comfResultsMtx, [], None, annualData, simStepPossible, lb_preparation)
    resultValuesInit, resultColorsInit, resultMesh, legendInit, legendBasePt = main(resultValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar_, analysisPeriod, simStepPossible, annualData, vertOrFace)
    
    #Unpack the legend.
    legend = []
    for count, item in enumerate(legendInit):
        if count == 0:
            legend.append(item)
        if count == 1:
            for srf in item:
                legend.append(srf)
    
    #Unpack the other data trees.
    resultValues = DataTree[Object]()
    resultColors = DataTree[Object]()
    
    for brCount, branch in enumerate(resultValuesInit):
        for item in branch:resultValues.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(resultColorsInit):
        for item in branch:resultColors.Add(item, GH_Path(brCount))
    
    ghenv.Component.Params.Output[4].Hidden = True
