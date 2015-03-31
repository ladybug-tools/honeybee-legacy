# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Import Annual Daylight Glare Probability

-
Provided by Honeybee 0.0.56

    Args:
        _dgpFile: Annual Daylight glare probability file
    Returns:
        viewPoints: Points that represents point of view of the person
        viewDirections: Vectors that represents direction of the view. Use Ladybug 
        dgpValues: Daylight glare probability values. Imperceptible Glare [0.35 > DGP], Perceptible Glare [0.4 > DGP >= 0.35], Disturbing Glare [0.45 > DGP >= 0.4], Intolerable Glare [DGP >= 0.45]
        
"""
ghenv.Component.Name = "Honeybee_Import dgp File"
ghenv.Component.NickName = 'importDGP'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import os
import scriptcontext as sc
import Rhino as rc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def importDGP(dgpFile):
    
    # check Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
        msg = "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
        
    # check the name is accurate
    if not os.path.isfile(dgpFile):
        msg = "Cannot find the .dgp file"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        return
        
    # check if there is a .vf file for views
    # first guess is that they have the same name
    vfFile = dgpFile.replace('.dgp', '.vf')
    if not os.path.isfile(vfFile):
        # try to find the file from the list
        studyFolder = os.path.dirname(vfFile)
        fileNames = os.listdir(studyFolder)
        for fileName in fileNames:
            if fileName.lower().endswith(".vf"):
                vfFile = os.path.join(studyFolder, fileName)
                break
                
    # import the views
    views = {}
    if os.path.isfile(vfFile):
        with open(vfFile, "r") as viewsF:
            for lineCount, line in enumerate(viewsF):
                try:
                    viewName = "view_" + str(lineCount)
                    views[viewName] = {}
                    Px, Py, Pz = map(float, line.split("-vp")[1].strip().split(" ")[:3])
                    views[viewName]["viewPoint"] = rc.Geometry.Point3d(Px, Py, Pz)
                    Vx, Vy, Vz = map(float, line.split("-vd")[1].strip().split(" ")[:3])
                    views[viewName]["viewDirection"] = rc.Geometry.Vector3d(Vx, Vy, Vz)
                except:
                    pass
                    
    # import dgp values
    with open(dgpFile, "r") as dgpRes:
        for line in dgpRes:
            #try:
            hourlyRes = line.split(" ")[4:]
            # for each view there should be a number
            for view, res in zip(views.keys(), hourlyRes):
                
                if "dgpValues" not in views[view].keys():
                    views[view]["dgpValues"] = []
                
                views[view]["dgpValues"].append(res)
                
    return views


if _dgpFile!=None:
    views = importDGP(_dgpFile)
    
    if views!=None:
        # graft the data based on the pattern
        viewPoints = DataTree[Object]()
        viewDirections = DataTree[Object]()
        dgpValues =  DataTree[Object]()
        
        keyCount = 0
        for key, item in views.items():
            p = GH_Path(keyCount)
            # add heading
            strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
            annualGlareHeading = [strToBeFound, "view: " + key, "Daylight Glare Probability", \
                        "%", 'Hourly', (1,1,1), (12, 31, 24)]
            
            try:
                viewPoints.Add(item["viewPoint"], p)
                viewDirections.Add(item["viewDirection"], p)
            except:
                pass # there is no vf file
            
            dgpValues.AddRange(annualGlareHeading + item["dgpValues"], p)
            keyCount+=1
