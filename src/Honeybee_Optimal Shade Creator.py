# This is a component for deleting out unwanted areas of a shade after a shade benefit evaluation has been run in order to get a final shade brep.
# By Chris Mackey
# Chris@MackeyArchitecture.com
# HoneyBee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to delete out unwanted areas of a shade after a shade benefit evaluation has been run.  This will help turn your shade evaluation results into an actual shade brep based on a percentage of beneficial shade cells that you decide.

-
Provided by Honeybee 0.0.56
    
    Args:
        _shadeMesh: The shade mesh out of either of the shade benefit evaluators.
        _shadeNetEffect: The shade net effect out of either of the shade benefit evaluators.
        percentToKeep_: A number between 0 and 100 that represents the percentage of the beneficial shade cells that you would like to keep.  By default, this is set to 25% but you may want to move it down if the area of your resulting shade is very large or move it up if you want to save more energy and do not care about the area of your shade.
        levelOfPerform_: An optional number that represents the mimimum acceptable energy savings per square area unit to be included in the created shade.  An input here will override the percent input above.
    Returns:
        readMe!: ...
        energySavedByShade: The anticipated energy savings (or degree-days helped) for the shade output below.  Values should be in kWh for energy shade benefit or degrees C for comfort shade benefit.
        areaOfShade: The area of the shade brep below in model units.
        newColoredMesh: A new colored mesh with the unhelpful cells deleted out of it.
        newShadeBrep: A new shade brep that represents the most effective shade possible.
"""

ghenv.Component.Name = "Honeybee_Optimal Shade Creator"
ghenv.Component.NickName = 'ShadeCreator'
ghenv.Component.Message = 'VER 0.0.56\nMAR_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh



def checkTheInputs():
    #Check to make sure that the number of shade mesh faces matches the length of the shade New Effect.
    if _shadeMesh.Faces.Count == len(_shadeNetEffect): checkData1 = True
    else:
        checkData1 = False
        print "The number of faces in the _shadeMesh does not equal the number of values in the _shadeNetEffect.  Are you sure that you connected a mesh that matches your input data?"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The number of faces in the _shadeMesh does not equal the number of values in the _shadeNetEffect.  Are you sure that you connected a mesh that matches your input data?")
    
    #Check to see if the user has hooked up a percent to keep and, if not, set it to 50%.
    if percentToKeep_ == None:
        percent = 0.25
        checkData2 = True
    else:
        if percentToKeep_ <= 100 and percentToKeep_ >= 0:
            checkData2 = True
            percent = percentToKeep_/100
        else:
            checkData2 = False
            percent = None
            print "The percentToKeep_ must be a valude between 0 and 100."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The percentToKeep_ must be a valude between 0 and 100.")
    
    #If eveything is good, return a result that says this.
    checkData = False
    if checkData1 == True and checkData2 == True: checkData = True
    
    return checkData, percent


def main(percent):
    #Make a list to keep track of all of the faces in the test mesh.
    faceNumbers = range(len(_shadeNetEffect))
    
    #Sort the list of net effect along with the face numbers list and reverse it so the most valuable cells are at the top.
    faceNumbersSort = [x for (y,x) in sorted(zip(_shadeNetEffect, faceNumbers))]
    faceNumbersSort.reverse()
    _shadeNetEffect.sort()
    _shadeNetEffect.reverse()
    
    #Remove the faces numbers that are harmful.
    faceNumbersHarm = []
    shadeNetEffectHelp = []
    for count, num in enumerate(_shadeNetEffect):
        if num > 0: shadeNetEffectHelp.append(num)
        else: faceNumbersHarm.append(faceNumbersSort[count])
    
    # Take the specified percent of the helpful cells.
    shadeNetFinal = []
    if levelOfPerform_ == None:
        numToTake  = percent*(len(shadeNetEffectHelp))
        for count, num in enumerate(shadeNetEffectHelp):
            if count < numToTake: shadeNetFinal.append(num)
            else: faceNumbersHarm.append(faceNumbersSort[count])
    else:
        for count, num in enumerate(shadeNetEffectHelp):
            if num > levelOfPerform_: shadeNetFinal.append(num)
            else: faceNumbersHarm.append(faceNumbersSort[count])
    
    #Remove the unnecessary cells from the shade mesh.
    newMesh = _shadeMesh
    newMesh.Faces.DeleteFaces(faceNumbersHarm)
    
    #Turn the new mesh into a brep snd get the area of each face.
    meshBrep = rc.Geometry.Brep.CreateFromMesh(newMesh, True)
    if meshBrep != None:
        areaList = []
        for surface in meshBrep.Faces:
            areaList.append(rc.Geometry.AreaMassProperties.Compute(surface).Area)
        
        #Try to simplify the brep.
        try:
            edgeCrv = meshBrep.DuplicateEdgeCurves(True)
            joinedCrv = rc.Geometry.Curve.JoinCurves(edgeCrv, sc.doc.ModelAbsoluteTolerance)
            meshBrepFinal = rc.Geometry.Brep.CreatePlanarBreps(joinedCrv)
        except:
            meshBrepFinal = meshBrep
        
        #Calculate the total area and the energy saved by the new mesh.
        totalArea = sum(areaList)
        totalEnergyList = []
        for count, area in enumerate(areaList):
            totalEnergyList.append(shadeNetFinal[count]*area)
        totalEnergy = sum(totalEnergyList)
        
        return totalEnergy, totalArea, newMesh, meshBrepFinal
    else:
        return 0, 0, None, None


checkData = False
if _shadeMesh != None and _shadeNetEffect != [] and _shadeNetEffect != [None]:
    checkData, percent = checkTheInputs()

if checkData == True and _shadeMesh and _shadeNetEffect != []:
    energySavedByShade, areaOfShade, newColoredMesh, newShadeBrep = main(percent)

ghenv.Component.Params.Output[3].Hidden = True