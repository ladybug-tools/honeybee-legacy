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
        _comfResultsMtx: Any matrix output from the "Honeybee_Annual Adaptive Comfort Analysis" component or the "Honeybee_Read Indoor Comfort Result" component.
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".  These will be colored with result data.
        ===============: ...
        analysisPeriod_: Optional analysisPeriod_ to take a slice out of an annual data stream.  Note that connecting a value to "stepOfSimulation_" will override this input.
        stepOfSimulation_: Optional interger between 1 and 8761 for the hour of simulation to color the mesh with.  Connecting a value here will override the analysisPeriod_ input.
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
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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


w = gh.GH_RuntimeMessageLevel.Warning

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
    if len(_comfResultsMtx) > 0 and len(viewFactorMesh) > 0:
        dataType = _comfResultsMtx[0]
        ptLen1 = len(_comfResultsMtx[1])
        meshFaceCount = []
        for mesh in viewFactorMesh:
            meshFaceCount.append(mesh.Faces.Count)
        ptLen2 = sum(meshFaceCount)
        if ptLen1 == ptLen2: checkData2 = True
        else:
            warning = "The length of data in the comfResultsMTX does not matech the number of faces in the viewFactorMesh."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else: pass
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True: checkData = True
    else: checkData = False
    
    return checkData, viewFactorMesh, dataType


def computeComfFactor(comfResultsMtx, analysisPeriod, stepOfSimulation, lb_preparation):
    #Create a list to be filled with values of comfort.
    comfortFactorVals = []
    
    if stepOfSimulation != None:
        comfortFactorVals = comfResultsMtx[stepOfSimulation]
    elif len(analysisPeriod) > 0:
        #Get the HOYs of the analysis period
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        
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



def main(pointValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    
    #Read the data type and assign default values for mesh types.
    if dataType == 'Degrees From Target':
        legendTitle = 'C'
        dataType = dataType + ' Temperature'
        if len(legendPar_) == 0:
            numSeg = 11
            lowB = -3
            highB = 3
            customColors = [System.Drawing.Color.FromArgb(0,136,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,0,0)]
    elif dataType == 'Adaptive Comfort':
        legendTitle = '%'
        for valCount, value in enumerate(pointValues):
            pointValues[valCount] = value*100
        if len(legendPar_) == 0:
            lowB = 0
            highB = 100
            numSeg = 10
            customColors = [System.Drawing.Color.FromArgb(0,0,0), System.Drawing.Color.FromArgb(127,127,127), System.Drawing.Color.FromArgb(255,255,255)]
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
    if len(analysisPeriod_) > 0:
        startMonth = analysisPeriod_[0][0]
        endMonth = analysisPeriod_[1][0]
        startDay = analysisPeriod_[0][1]
        endDay = analysisPeriod_[1][1]
        startHour = analysisPeriod_[0][2]
        endHour = analysisPeriod_[1][2]
        titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1])
    else: titleDate = None
    
    #Create the Title.
    if stepOfSimulation_ != None: titleTxt = '\n' + dataType + '\n' + 'Hour ' + str(stepOfSimulation_) + ' of the year.'
    elif len(analysisPeriod_) > 0: titleTxt = '\n' + dataType + '\n' + titleDate
    else: titleTxt = '\n' + 'Annual ' + dataType
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
checkData, viewFactorMesh, dataType = checkTheInputs()

if checkData == True and _runIt == True and len(_comfResultsMtx) == 8761:
    resultValues = computeComfFactor(_comfResultsMtx, analysisPeriod_, stepOfSimulation_, lb_preparation)
    resultValuesInit, resultColorsInit, resultMesh, legendInit, legendBasePt = main(resultValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar_)
    
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
