# This component creates an air temperature map based on an energy simulation output.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to produce a colored mesh from a comfResultsMtx.
-
Provided by Honeybee 0.0.64
    
    Args:
        _comfResultsMtx: Any matrix output from the 'Honeybee_Microclimate Map Analysis' component, the 'Honeybee_Thermal Comfort Autonomy Analysis' component, or the 'Honeybee_Read Microclimate Matrix' component.
        _viewFactorMesh: The list of view factor meshes that comes out of the  "Honeybee_Indoor View Factor Calculator".  These will be colored with result data.
        ===========: ...
        analysisPeriod_: Note that that connecting a value to 'stepOfSimulation_' will override this input.
        stepOfSimulation_: Optional analysisPeriod_ to take a slice out of the data stream.  Optional interger to select out a step of the simulation to color the mesh with.  Connecting a value here will override the analysisPeriod_ input.
        percentOrTotal_: Set to 'True' to have the component compute comfort values as a percent of occupied hours or all hours.  Set to 'False' to have the component compute comfort values as a total number of hours.  The default is set to 'True' to calculate comfort as a percent.  Note that this input only works for comfort matrices and not temperature ones.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        runIt_: Set boolean to "True" to run the component and produce a colored mesh from a comfResultsMtx.
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

ghenv.Component.Name = "Honeybee_Visualize Microclimate Map"
ghenv.Component.NickName = 'VisualizeMicroclimate'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nNOV_20_2015
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
    
0: ["_comfResultsMtx", "Any matrix output from the 'Honeybee_Microclimate Map Analysis' component, the 'Honeybee_Thermal Comfort Autonomy Analysis' component, or the 'Honeybee_Read Microclimate Matrix' component."],
1: ["_viewFactorMesh", "The list of view factor meshes that comes out of the  'Honeybee_Indoor View Factor Calculator'.  These will be colored with result data."],
2: ["===========", "..."],
3: ["analysisPeriod_", "Optional analysisPeriod_ to take a slice out of the data stream.  Note that that connecting a value to 'stepOfSimulation_' will override this input."],
4: ["stepOfSimulation_", "Optional interger to select out a step of the simulation to color the mesh with.  Connecting a value here will override the analysisPeriod_ input."],
5: ["percentOrTotal_", "Set to 'True' to have the component compute comfort values as a percent of occupied hours or all hours.  Set to 'False' to have the component compute comfort values as a total number of hours.  The default is set to 'True' to calculate comfort as a percent.  Note that this input only works for comfort matrices and not temperature ones."],
6: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
7: ["runIt_", "Set boolean to 'True' to run the component and visualize indoor comfort."]
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
    if len(_comfResultsMtx) > 0 and len(viewFactorMesh) > 0:
        dataType = _comfResultsMtx[0].split(";")[0]
        ptLen1 = len(_comfResultsMtx[1])
        meshFaceCount = []
        for mesh in viewFactorMesh:
            meshFaceCount.append(mesh.Faces.Count)
        ptLen2 = sum(meshFaceCount)
        if ptLen1 == ptLen2: checkData2 = True
        else:
            warning = "The length of data in the comfResultsMTX does not match the number of faces in the viewFactorMesh."
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
    
    #Check the HOY to be sure that it is in the counds of the matrix.
    checkData3 = True
    try:
        if not stepOfSimulation_ == None:
            if stepOfSimulation_ <=0 or stepOfSimulation_ > len(_comfResultsMtx):
                checkData3 = False
                warning = "stepOfSimulation_ is outside the bounds of the comfResultsMTX."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
    except: pass
    
    #Check if the matrix is special and includes the number of occupied hours to divide each summed point by.
    if 'Occupied Thermal Comfort Percent' in dataType or 'Thermal Autonomy' in dataType or 'Over-Heated Percent' in dataType or 'Under-Heated Percent' in dataType: occDataType = True
    else: occDataType = False
    
    #Check if the matrix is total-able or if it should always be viewed as an average.
    totalAble = False
    if occDataType == True or 'Thermal Comfort Percent' in dataType: totalAble = True
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True  and checkData3 == True: checkData = True
    else: checkData = False
    
    return checkData, viewFactorMesh, dataType, annualData, simStepPossible, analysisPeriod, occDataType, totalAble


def manageInputOutput(annualData, simStep, totalAble):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(8):
        if input == 3 and simStep == False:
            ghenv.Component.Params.Input[input].NickName = "__________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 4 and simStep == False:
            ghenv.Component.Params.Input[input].NickName = "___________"
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 5 and totalAble == False:
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


def computeComfValues(comfResultsMtx, analysisP, comfMtxAnalysisP, stepOfSimulation, annualData, simStepPossible, occDataType, percentOrTotal, totalAble, lb_preparation):
    #Create a list to be filled with values of comfort.
    comfortFactorVals = []
    
    if stepOfSimulation != None and simStepPossible == True:
        comfortFactorVals = comfResultsMtx[stepOfSimulation]
    elif len(analysisP) > 0 and analysisP != comfMtxAnalysisP and annualData == True:
        #Get the HOYs of the analysis period
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisP, 1)
        
        #Pick out just the hours that are in the analysis period.
        newcomfResultsMtx = []
        for lineCount, line in enumerate(comfResultsMtx):
            if lineCount in HOYS: newcomfResultsMtx.append(line)
        
        #Transpose the matrix
        newcomfResultsMtx2 = zip(*newcomfResultsMtx)
        
        if percentOrTotal == False and totalAble == True:
            for lineCount, line in enumerate(newcomfResultsMtx2):
                comfortFactorVals.append(sum(line))
        else:
            #If the dataType is meant to be divided by occupie hours, recompute the occupied hours for the analysis period.
            occMtxInit = []
            for val in comfResultsMtx[1]: occMtxInit.append(0)
            if occDataType == True:
                for line in newcomfResultsMtx:
                    for ptCt, pointVal in enumerate(line):
                        if isinstance(pointVal, int): occMtxInit[ptCt] += 1
            occMtx = [occMtxInit]
            
            #Compute the total percentage of comfortable hours.
            if occDataType == False:
                for lineCount, line in enumerate(newcomfResultsMtx2):
                    comfortFactorVals.append(sum(line)/len(line))
            else:
                occMtx2 = zip(*occMtx)
                for lineCount, line in enumerate(newcomfResultsMtx2):
                    comfortFactorVals.append(sum(line)/occMtx2[lineCount][0])
    elif len(analysisP) > 0 and analysisP != comfMtxAnalysisP and annualData == False and simStepPossible == True:
        #Check the data anlysis period and subtract the start day from each of the HOYs.
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisP, 1)
        FinalHOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod(comfMtxAnalysisP, 1)
        for hCount, hour in enumerate(HOYS):
            HOYS[hCount] = hour - FinalHOYs[0] + 1
        
        #Check to see if the hours of the requested analysis period are in the comfResultsMtx.
        periodsAlign = True
        for hour in HOYS:
            if hour < 0: periodsAlign = False
            try: comfResultsMtx[hour]
            except: periodsAlign = False
        
        if periodsAlign == False:
            warning = 'The analysis period of the confResultsMtx and that which is plugged into this component do not align.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        else:
            
            #Pick out just the hours that are in the analysis period.
            newcomfResultsMtx = []
            for lineCount, line in enumerate(comfResultsMtx):
                if lineCount in HOYS:
                    newcomfResultsMtx.append(line)
            
            #Transpose the matrix
            newcomfResultsMtx2 = zip(*newcomfResultsMtx)
            
            if percentOrTotal == False and totalAble == True:
                for lineCount, line in enumerate(newcomfResultsMtx2):
                    comfortFactorVals.append(sum(line))
            else:
                #If the dataType is meant to be divided by occupie hours, recompute the occupied hours for the analysis period.
                occMtxInit = []
                for val in comfResultsMtx[1]: occMtxInit.append(0)
                if occDataType == True:
                    for line in newcomfResultsMtx:
                        for ptCt, pointVal in enumerate(line):
                            if isinstance(pointVal, int): occMtxInit[ptCt] += 1
                occMtx = [occMtxInit]
                
                #Compute the total percentage of comfortable hours.
                if occDataType == False:
                    for lineCount, line in enumerate(newcomfResultsMtx2):
                        comfortFactorVals.append(sum(line)/len(line))
                else:
                    occMtx2 = zip(*occMtx)
                    for lineCount, line in enumerate(newcomfResultsMtx2):
                        comfortFactorVals.append(sum(line)/occMtx2[lineCount][0])
    else:
        #Transpose the matrix
        if occDataType == False: newcomfResultsMtx1 = comfResultsMtx[1:]
        else: newcomfResultsMtx1 = comfResultsMtx[1:-1]
        newcomfResultsMtx2 = zip(*newcomfResultsMtx1)
        
        if percentOrTotal == False and totalAble == True:
            for lineCount, line in enumerate(newcomfResultsMtx2):
                comfortFactorVals.append(sum(line))
        else:
            #Compute the average across the hours.
            if occDataType == False:
                for lineCount, line in enumerate(newcomfResultsMtx2):
                    comfortFactorVals.append(sum(line)/len(line))
            else:
                occMtx = [comfResultsMtx[-1]]
                occMtx2 = zip(*occMtx)
                for lineCount, line in enumerate(newcomfResultsMtx2):
                    comfortFactorVals.append(sum(line)/occMtx2[lineCount][0])
    
    
    return comfortFactorVals



def main(pointValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar, analysisPeriod, simStepPossible, annualData, percentOrTotal):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
    #Read the data type and assign default values for mesh types.
    if dataType == 'Degrees From Target' or dataType == 'Predicted Mean Vote' or dataType == 'Degrees From Neutral UTCI' or dataType == 'PET Category':
        pointValuesFinal = pointValues
        if dataType == 'Degrees From Target' or dataType == 'Degrees From Neutral UTCI': legendTitle = 'C'
        elif dataType == 'PET Category': legendTitle = 'PET Category'
        else: legendTitle = 'PMV'
        if dataType == 'Degrees From Target': dataType = dataType + ' Temperature'
        if len(legendPar_) == 0:
            if dataType == 'Degrees From Neutral UTCI': customColors = lb_visualization.gradientLibrary[9]
            else: customColors = lb_visualization.gradientLibrary[8]
            if dataType == 'Degrees From Target Temperature':
                numSeg = 11
                lowB = -5
                highB = 5
            elif dataType == 'Degrees From Neutral UTCI':
                numSeg = 12
                lowB = -32
                highB = 12
            elif dataType == 'PET Category':
                numSeg = 11
                lowB = -2
                highB = 2
            else:
                numSeg = 11
                lowB = -1
                highB = 1
        elif legendPar_[3] == []:
            if dataType == 'Degrees From Neutral UTCI': customColors = lb_visualization.gradientLibrary[9]
            else: customColors = lb_visualization.gradientLibrary[8]
    elif 'Thermal Comfort Percent' in dataType or 'Thermal Autonomy' in dataType or 'Over-Heated Percent' in dataType or 'Under-Heated Percent' in dataType:
        if percentOrTotal == False:
            if 'Percent' in dataType: dataType = dataType.split('Percent')[0] + 'Hours'
            legendTitle = 'Hours'
        else: legendTitle = '%'
        all100Comf = True
        pointValuesFinal = []
        for valCount, value in enumerate(pointValues):
            if value < 1.0: all100Comf = False
            if percentOrTotal == False:
                all100Comf = False
                pointValuesFinal.append(value)
            else: pointValuesFinal.append(value*100)
        if len(legendPar_) == 0:
            if all100Comf == False:
                if 'Thermal Comfort' in dataType or 'Thermal Autonomy' in dataType: customColors = lb_visualization.gradientLibrary[7]
                elif 'Over-Heated' in dataType: customColors = lb_visualization.gradientLibrary[10]
                else: customColors = lb_visualization.gradientLibrary[11]
            else: customColors = [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,255,255)]
        elif legendPar_[3] == []:
            if all100Comf == False:
                if 'Thermal Comfort' in dataType or 'Thermal Autonomy' in dataType: customColors = lb_visualization.gradientLibrary[7]
                elif 'Over-Heated' in dataType: customColors = lb_visualization.gradientLibrary[10]
                else: customColors = lb_visualization.gradientLibrary[11]
            else: customColors = [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,255,255)]
    else:
        pointValuesFinal = pointValues
        legendTitle = 'C'
    
    #Get the colors for each zone.
    allColors = []
    transparentColors = []
    colors = lb_visualization.gradientColor(pointValuesFinal, lowB, highB, customColors)
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
        segmentedValues.append(pointValuesFinal[colorCounter:(colorCounter+mesh.Faces.Count)])
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
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(pointValuesFinal, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Make lists that assist with the labaeling of the rest of the title.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    timeNames = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "24:00"]
    
    #If there is an analysis period, format the text for it in the legend title.
    try:
        if len(analysisPeriod_) == 0 and annualData == False:
            startMonth = analysisPeriod[0][0]
            endMonth = analysisPeriod[1][0]
            startDay = analysisPeriod[0][1]
            endDay = analysisPeriod[1][1]
            startHour = analysisPeriod[0][2]
            endHour = analysisPeriod[1][2]
            if analysisPeriod[0] != analysisPeriod[1]:
                titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1]) + " - " + str(monthNames[endMonth-1]) + " " + str(endDay) + " " + str(timeNames[endHour-1])
            else: titleDate = str(monthNames[startMonth-1]) + " " + str(startDay) + " " + str(timeNames[startHour-1])
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
        if stepOfSimulation_ != None and simStepPossible == True:
            startHOY = lb_preparation.date2Hour(startMonth, startDay, startHour)
            actualHOY = startHOY + stepOfSimulation_ - 1
            date = lb_preparation.hour2Date(actualHOY)
            titleTxt = '\n' + dataType + '\n' + date
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
totalAble = True
if len(_comfResultsMtx) > 0 and len(_viewFactorMesh) > 0:
    if _comfResultsMtx[0] != None and _viewFactorMesh[0] != None:
        checkData, viewFactorMesh, dataType, annualData, simStepPossible, analysisPeriod, occDataType, totalAble = checkTheInputs()

if annualData == False or simStepPossible == False or totalAble == False:
    manageInputOutput(annualData, simStepPossible, totalAble)
else:
    restoreInputOutput()

#In case the input/output has wiped out these terms, replace them with null values.
try: analysisPeriod_[0]
except: analysisPeriod_ = []
try: stepOfSimulation_
except: stepOfSimulation_ = None
try: percentOrTotal_
except: percentOrTotal_ = True
if runIt_ == None: runIt = True
else: runIt = runIt_

if checkData == True and runIt == True:
    resultValues = computeComfValues(_comfResultsMtx, analysisPeriod_, analysisPeriod, stepOfSimulation_, annualData, simStepPossible, occDataType, percentOrTotal_, totalAble, lb_preparation)
    if resultValues != []:
        resultValuesInit, resultColorsInit, resultMeshInit, legendInit, legendBasePt = main(resultValues, viewFactorMesh, dataType, lb_preparation, lb_visualization, legendPar_, analysisPeriod, simStepPossible, annualData, percentOrTotal_)
        
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
        resultMesh = DataTree[Object]()
        
        for brCount, branch in enumerate(resultValuesInit):
            for item in branch:resultValues.Add(item, GH_Path(brCount))
        for brCount, branch in enumerate(resultColorsInit):
            for item in branch:resultColors.Add(item, GH_Path(brCount))
        for meshCt, mesh in enumerate(resultMeshInit):
            resultMesh.Add(mesh, GH_Path(meshCt))
        
        ghenv.Component.Params.Output[4].Hidden = True
