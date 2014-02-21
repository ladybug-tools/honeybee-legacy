# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
export geometries to rad file, and run daylighting/energy simulation

-
Provided by Honeybee 0.0.50

    Args:
        north_: ...
        _HBObjects: List of Honeybee objects
        _analysisRecipe: An analysis recipe
        _writeRad: Write simulation files
        runRad_: Run the analysis. _writeRad should be also set to true
        _numOfCPUs_: Number of CPUs to be used for the studies. This option doesn't work for image-based analysis
        _workingDir_: Working directory on your system. Default is set to C:\Ladybug
        _radFileName_: Input the project name as a string
        meshingLevel_: Level of meshing [0] Coarse [1] Smooth
        overwriteResults_: Set to False if you want the component create a copy of all the results. Default is True
        
    Returns:
        readMe!: ...
        analysisType: Type of the analysis (e.g. illuminance, luminance,...)
        resultsUnit: Unit of the results (e.g. lux, candela, wh/m2)
        radianceGeometryPath: Path to the Radiance geometry file
        HDRImageOutputPath: Path to the HDR image file
        gridBasedResultsPath: Path to the results of grid based analysis (includes all the recipes except image-based and annual)
        annualAnalysisPath: Path to the result files of annual analysis
        testPts: Test points
        done: True if the study is over
"""

ghenv.Component.Name = "Honeybee_Run Daylight Simulation"
ghenv.Component.NickName = 'runDaylightAnalysis'
ghenv.Component.Message = 'VER 0.0.50\nFEB_20_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "4 | Daylight | Daylight"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import time
import System
import shutil
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import subprocess
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path



def isTheStudyOver(fileNames):
    while True:
        cmd = 'WMIC PROCESS get Commandline' #,Processid'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmdCount = 0
        for line in proc.stdout:
            if line.strip().startswith("cmd") and line.strip().endswith(".bat"):
                fileName = line.strip().split(" ")[-1].split("\\")[-1]
                # I should check the file names and make sure they are the right files
                if fileName in fileNames:
                    cmdCount += 1
        time.sleep(0.2)
        if cmdCount == 0:
            return
        #if cmdCount > 1: return

class WriteRAD(object):
    
    def shiftList(self, list, number = 1):
        newList = []
        newList.extend(list[-number:])
        newList.extend(list[:-number])
        return newList
    
    def getsurfaceStr(self, surface, count, coordinates):
        if surface.RadMaterial != None:
            surface.construction = surface.RadMaterial
        elif not hasattr(surface, 'construction'):
            
            if not hasattr(surface, 'type'):
                # find the type based on 
                surface.type = surface.getTypeByNormalAngle()
                
            #assign the construction based on type
            surface.construction = surface.cnstrSet[surface.type]
            
        srfStr =  surface.construction.replace(" ", "_") + " polygon " + surface.name + '_' + `count` + "\n" + \
            "0\n" + \
            "0\n" + \
            `(len(coordinates)*3)` + "\n"
            
        ptStr = ''
        for  pt in coordinates:
            ptStr = ptStr + '%.4f'%pt.X + '  ' + '%.4f'%pt.Y + '  ' + '%.4f'%pt.Z + '\n'
        ptStr = ptStr + '\n'
        
        return srfStr + ptStr

    def RADSurface(self, surface):
        fullStr = ''
        # base surface coordinates
        coordinatesList = surface.extractPoints(1, True)
        
        if coordinatesList:
            if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
                coordinatesList = [coordinatesList]
                
            for count, coordinates in enumerate(coordinatesList):
                endCoordinate = rc.Geometry.Point3d.Add(coordinates[-1], rc.Geometry.Vector3d(0,0,0))
                if surface.hasChild:
                    glzCoordinateLists = surface.extractGlzPoints(True)
                    for glzCount, glzCoorList in enumerate(glzCoordinateLists):
                        # glazingStr
                        fullStr = fullStr + self.getsurfaceStr(surface.childSrfs[0], glzCount, glzCoorList)
                        
                        # shift glazing list
                        glzCoorList = self.shiftList(glzCoorList)
                        coordinates.extend(glzCoorList)
                        coordinates.append(glzCoorList[0])
                    coordinates.extend([endCoordinate, coordinates[0]])
                fullStr = fullStr + self.getsurfaceStr(surface, count, coordinates)
            return fullStr
        else:
            print "one of the surfaces is not exported correctly"
            return ""
            
    def RADNonPlanarSurface(self, surface):
        fullStr = ''
        
        # replace the geometry with the punched geometry
        # for planar surfaces with multiple openings
        try:
            if surface.punchedGeometry!=None:
                surface.geometry = surface.punchedGeometry
                surface.hasInternalEdge = True
        except:
            #print e
            # nonplanar surfaces with no openings
            pass
            
        # base surface coordinates
        coordinatesList = surface.extractPoints(1, True)
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        for count, coordinates in enumerate(coordinatesList):
            #print count
            fullStr = fullStr + self.getsurfaceStr(surface, count, coordinates)
        
        return fullStr
    
    def RADNonPlanarChildSurface(self, surface):
        fullStr = ''
        
        # I should test this function before the first release!
        # Not sure if it will work for cases generated only by surface
        # should probably check for meshed surface and mesh the geometry
        # in case it is not meshed
        
        # base surface coordinates
        coordinatesList = surface.extractGlzPoints(True)
        if type(coordinatesList[0])is not list and type(coordinatesList[0]) is not tuple:
            coordinatesList = [coordinatesList]
        for glzCount, glzCoorList in enumerate(coordinatesList):
            # glazingStr
            fullStr = fullStr + self.getsurfaceStr(surface.childSrfs[0], glzCount, glzCoorList)
        return fullStr

class WriteRADAUX(object):
    radSkyCondition = {0: '-u',
                       1: '-c',
                       2: '-i',
                       3: '+i',
                       4: '-s',
                       5: '+s'}
                       
    def getTime(self):
        
        def addZero(number):
            if len(str(number)) == 1:
                return "0" + str(number)
            else:
                return str(number)
        
        year, month, day, hour, minute, second = time.localtime()[0:6]
        
        now = addZero(hour) + "_" + addZero(minute) + "_" + addZero(second)
    
        date = addZero(year) + "_" +  addZero(month)  + "_" + addZero(day)
    
        return date + "at" + now
    
    def copyFile(self, inputFile, destinationFullpath, overwrite = False):
        if overwrite: shutil.copyfile(inputFile, destinationFullpath)
        elif not os.path.isfile(destinationFullpath): shutil.copyfile(inputFile, destinationFullpath)
    
    def RADLocation(self, epw_file):
        epwfile = open(epw_file,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        while 1>0: #remove empty cells from the end of the list if any
            try: float(csheadline[-1]); break
            except: csheadline.pop()
        locName = ''
        for hLine in range(1,4):
            if csheadline[hLine] != '-':
                locName = locName + csheadline[hLine].strip() + '_'
        locName = locName[:-1].strip()
        lat = csheadline[-4]
        lngt = csheadline[-3]
        timeZone = csheadline[-2]
        elev = csheadline[-1].strip()
        epwfile.close()
        
        return locName, lat, lngt, timeZone, elev
    
    def RADRadiationSky(self, projectName):
        return  "# start of sky definition for radiation studies\n" + \
                "void brightfunc skyfunc\n" + \
                "2 skybright " + projectName + ".cal\n" + \
                "0\n" + \
                "0\n" + \
                "skyfunc glow sky_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 1 1 0\n" + \
                "sky_glow source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 1 180\n" + \
                "# end of sky definition for radiation studies\n\n"
    
    def RADDaylightingSky(self, epwFileAddress, skyCondition, time, month, day):
        locName, lat, long, timeZone, elev = self.RADLocation(epwFileAddress)
        return  "# start of sky definition for daylighting studies\n" + \
                "# location name: " + locName + " LAT: " + lat + "\n" + \
                "!gensky " + `month` + ' ' + `day` + ' ' + `time` + ' ' + self.radSkyCondition[skyCondition] + \
                " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + "\n" + \
                "skyfunc glow sky_mat\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 1 1 0\n" + \
                "sky_mat source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 1 180\n" + \
                "skyfunc glow ground_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 .8 .5 0\n" + \
                "ground_glow source ground\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 -1 180\n" + \
                "# end of sky definition for daylighting studies\n\n"
                    
                    
    def exportView(self, viewName, radParameters, cameraType, imageSize, sectionPlane):
        
        if viewName in rs.ViewNames():
            viewName = rs.CurrentView(viewName, True)
        else:
            # change to RhinoDoc to get access to NamedViews
            sc.doc = rc.RhinoDoc.ActiveDoc
            namedViews = rs.NamedViews()
            if viewName in namedViews:
                viewName = rs.RestoreNamedView(viewName)
            else:
                viewName = None
            # change back to Grasshopper
            sc.doc = ghdoc
            viewName = rs.CurrentView(viewName, True)
        
        if viewName == None:
            print "Illegal view name!"
            viewName = "Perspective"
            
        # Read camera type 0: Perspective, 1: fisheye, 2: parallel
        try: cameraType = int(cameraType)
        except:
            if sc.doc.Views.ActiveView.ActiveViewport.IsPerspectiveProjection: cameraType = 0
            elif sc.doc.Views.ActiveView.ActiveViewport.IsParallelProjection: cameraType = 2
        
        # paralell view sizes
        viewHSizeP = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Width)
        viewVSizeP = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Height)
        
        # read image size
        viewHSize = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Width)
        viewVSize = int(sc.doc.Views.ActiveView.ActiveViewport.Size.Height)
        # print viewHSize, viewVSize
        userInputH = imageSize[0]
        userInputV = imageSize[1]
        if userInputH != None and userInputV != None:
            try:
                viewHSize = float(userInputH)
                viewVSize = float(userInputV)
            except:
                print "Illegal input for view size."
                pass
        elif userInputH == None and userInputV != None:
            try:
                viewHSize = viewHSize * (userInputV/viewVSize)
                viewVSize = float(userInputV)
            except:
                print "Illegal input for view size."
                pass
        elif userInputH != None and userInputV == None:
            try:
                viewVSize = viewVSize * (userInputH/viewHSize)
                viewHSize = float(userInputH)
            except:
                print "Illegal input for view size."
                pass
        
        # print viewHSize, viewVSize
        viewPoint = sc.doc.Views.ActiveView.ActiveViewport.CameraLocation
        viewDirection = sc.doc.Views.ActiveView.ActiveViewport.CameraDirection
        viewDirection.Unitize()
        viewUp = sc.doc.Views.ActiveView.ActiveViewport.CameraUp
        viewHA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumRightPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumLeftPlane()[1][1])
        if viewHA == 0: viewHA = 180
        viewVA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumBottomPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumTopPlane()[1][1])
        if viewVA == 0: viewVA = 180
        
        if cameraType == 2:
            # Thank you to Brent Watanabe for the great discussion, and his help in figuring this out
            # I should find the bounding box of the geometry and set X and Y based of that!
            view = "-vtl -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + \
               " -vh " + `int(viewHSizeP)` + " -vv " + `int(viewVSizeP)` + \
               " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
               
        elif cameraType == 0:
            # perspective
            view = "-vtv -vp " + \
               "%.3f"%viewPoint[0] + " " + "%.3f"%viewPoint[1] + " " + "%.3f"%viewPoint[2] + " " + \
               " -vd " + "%.3f"%viewDirection[0] + " " + "%.3f"%viewDirection[1] + " " + "%.3f"%viewDirection[2] + " " + \
               " -vu " + "%.3f"%viewUp[0] + " " +  "%.3f"%viewUp[1] + " " + "%.3f"%viewUp[2] + " " + \
               " -vh " + "%.3f"%viewHA + " -vv " + "%.3f"%viewVA + \
               " -vl 0 -vs 0 -vl 0 -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
        
        elif cameraType == 1:
            # fish eye
            view = "-vth -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + " " + \
               " -vh 180 -vv 180 -vl 0 -vs 0 -vl 0  -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`
        
        if sectionPlane!=None:
            # map the point on the plane
            pointOnPlane = sectionPlane.ClosestPoint(viewPoint)
            distance = pointOnPlane.DistanceTo(viewPoint)
            view += " -vo " + str(distance)
            
        return view + " "
    
    def oconvLine(self, octFileName, radFilesList):
        # sence files
        senceFiles = ""
        for address in radFilesList: senceFiles = senceFiles + address.replace("\\" , "/") + " "
        
        line = "oconv -f " +  senceFiles + " > " + octFileName + ".oct\n"
        
        return line

    def rpictLine(self, viewFileName, projectName, viewName, radParameters):
        line = "rpict -t 10 -i -ab " + `radParameters["_ab_"]` + \
           " -ad " + `radParameters["_ad_"]` + " -as " +  `radParameters["_as_"]` + \
           " -ar " + `radParameters["_ar_"]` + " -aa " +  `radParameters["_aa_"]` + \
           " -vf " + viewFileName + " " + projectName + ".oct > " + \
           projectName + "_" + viewName + "_RadStudy.pic\n"
        return line
    
    def rpictLineAlternate(self, view, projectName, viewName, radParameters, analysisType = 0):
        octFile = projectName + ".oct"
        ambFile = projectName + "_" + viewName + ".amb"
        unfFile = projectName + "_" + viewName + ".unf" 
        outputFile = projectName + "_" + viewName + ".HDR"
        
        if analysisType==0:
            # illuminance (lux)
            line0 = "rpict -i "
        elif analysisType==2:
            # luminance (cd)
            line0 = "rpict "
        else:
            # radiation analysis
            line0 = "rpict -i "
        
        # check got translucant materials
        # St = A6*A7*( 1  photopic average (A1,A2,A3) * A4 )
        # radParameters["_st_"]
        
        line1 = "-t 10 "+ \
                view + " -af " + ambFile +  " " + \
                " -ps " + str(radParameters["_ps_"]) + " -pt " + str(radParameters["_pt_"]) + \
                " -pj " + str(radParameters["_pj_"]) + " -dj " + str(radParameters["_dj_"]) + \
                " -ds " + str(radParameters["_ds_"]) + " -dt " + str(radParameters["_dt_"]) + \
                " -dc " + str(radParameters["_dc_"]) + " -dr " + str(radParameters["_dr_"]) + \
                " -dp " + str(radParameters["_dp_"]) + " -st " + str(radParameters["_st_"])  + \
                " -ab " + `radParameters["_ab_"]` + \
                " -ad " + `radParameters["_ad_"]` + " -as " +  `radParameters["_as_"]` + \
                " -ar " + `radParameters["_ar_"]` + " -aa " +  '%.3f'%radParameters["_aa_"] + \
                " -lr " + `radParameters["_lr_"]`  + " -lw " + '%.3f'%radParameters["_lw_"] + " -av 0 0 0 " + \
                " " + octFile + " > " + unfFile + "\n"
    
        line2 = "del " + ambFile + "\n"
        
        line3 = "pfilt -1 -r .6 -x/2 -y/2 " + unfFile + " > " + outputFile + \
                    "\nexit\n"
        
        return line0 + line1 + line2 + line0 + line1 + line3
        
        
    def falsecolorLine(self, projectName, viewName):
        line = "c:\python27\python c:\honeybee\\falsecolor2.py -i " + projectName + "_RAD_" + viewName + "_RadStudy.pic -s auto -n 10 -mask 0.1 -l kWhm-2 -z > " + projectName + "_" + viewName + "_FalseColored.pic\n" + \
           "ra_tiff " + projectName + "_" + viewName + "_FalseColored.pic " + projectName + "_" + viewName + "_FalseColored.tif\n" + \
           "ra_gif " + projectName + "_" + viewName + "_FalseColored.pic " + projectName + "_" + viewName + "_FalseColored.gif\n"
        return line

    def rtraceLine(self, projectName, octFileName, radParameters, simulationType = 0, cpuCount = 0):
        ptsFile = projectName + "_" + str(cpuCount) + ".pts"
        outputFile = projectName + "_" + str(cpuCount) + ".res"
        if simulationType == 0:
            line0 = "rtrace -I "
        elif simulationType == 2:
            line0 = "rtrace "
        else:
            print "Fix this for radiation analysis"
            line0 = "rtrace -I "
            
        line1 = " -h -ms 0.063 -dp " + str(radParameters["_dp_"]) + \
                " -ds " + str(radParameters["_ds_"]) + " -dt " + str(radParameters["_dt_"]) + \
                " -dc " + str(radParameters["_dc_"]) + " -dr " + str(radParameters["_dr_"]) + \
                " -st " + str(radParameters["_st_"]) + " -lr " + str(radParameters["_lr_"]) + \
                " -lw " + str(radParameters["_lw_"]) + " -ab " + str(radParameters["_ab_"]) + \
                " -ad " + str(radParameters["_ad_"]) + " -as " + str(radParameters["_as_"]) + \
                " -ar " + str(radParameters["_ar_"]) + " -aa " + str(radParameters["_aa_"]) + \
                " " + octFileName + ".oct < " + ptsFile + \
                " > " + outputFile + "\n"
        
        return line0 + line1
        
    def testPtsStr(self, testPoint, ptsNormal):
        return  '%.4f'%testPoint.X + '\t' + \
                '%.4f'%testPoint.Y + '\t' + \
                '%.4f'%testPoint.Z + '\t' + \
                '%.4f'%ptsNormal.X + '\t' + \
                '%.4f'%ptsNormal.Y + '\t' + \
                '%.4f'%ptsNormal.Z + '\n'
        

    def readRadiationResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile: result.append(float(line.split('	')[0])*179)
        return result
    
    def readDLResult(self, resultFile):
        result = []
        resultFile = open(resultFile,"r")
        for line in resultFile:
            R, G, B = line.split('	')[0:3]
            result.append( 179 * (.265 * float(R) + .67 * float(G) + .065 * float(B)))
        return result

class WriteDS(object):
    
    def isSensor(self, testPt, sensors):
        for pt in sensors:
            if pt.DistanceTo(testPt) < sc.doc.ModelAbsoluteTolerance:
                # this is a senor point
                return True
        # not a sensor
        return False
    
    def DSHeadingStr(self, projectName, subWorkingDir, tempFolder, hb_DSPath, cpuCount = 0):
        return   '#######################################\n' + \
                 '#DAYSIM HEADING - GENERATED BY HONEYBEE\n' + \
                 '#######################################\n' + \
                 'project_name       ' + projectName + '_' + `cpuCount` + '\n' + \
                 'project_directory  ' + subWorkingDir + '\\\n' + \
                 'bin_directory      ' + hb_DSPath + '\\bin\\\n' + \
                 'tmp_directory      ' + tempFolder + '\\\n' + \
                 'Template_File      ' + hb_DSPath + '\\template\\DefaultTemplate.htm\n'
                 
    
    def DSLocationStr(self, hb_writeRADAUX,  lb_preparation, epwFileAddress, outputUnits):
        # location information
        locName, lat, long, timeZone, elev = hb_writeRADAUX.RADLocation(epwFileAddress)
        
        return'\n\n#################################\n' + \
                  '#      LOCATION INFORMATION      \n' + \
                  '#################################\n' + \
                  'place                     ' + lb_preparation.removeBlankLight(locName) + '\n' + \
                  'latitude                  ' + lat + '\n' + \
                  'longitude                 ' + `-float(long)` + '\n' + \
                  'time_zone                 ' + `-15 * float(timeZone)` + '\n' + \
                  'site_elevation            ' + elev + '\n' + \
                  'time_step                 ' + '60\n' + \
                  'wea_data_short_file       ' + lb_preparation.removeBlankLight(locName) + '.wea\n' + \
                  'wea_data_short_file_units ' + '1\n' + \
                  'lower_direct_threshold    ' + '2\n' + \
                  'lower_diffuse_threshold   ' + '2\n' + \
                  'output_units              ' + `outputUnits[0]` + '\n', locName
    
    # building information
    def DSBldgStr(self, projectName, materialFileName, radFileFullName, adaptiveZone, dgp_image_x = 500, dgp_image_y = 500, cpuCount = 0):
        return'\n\n#################################\n' + \
                  '#      BUILDING INFORMATION      \n' + \
                  '#################################\n' + \
                  'material_file          Daysim_material_' + projectName + '.rad\n' + \
                  'geometry_file          Daysim_'+ projectName + '.rad\n' + \
                  'radiance_source_files  2, ' + materialFileName + ', ' + radFileFullName + '\n' + \
                  'sensor_file            ' + projectName + '_' + `cpuCount` + '.pts\n' + \
                  'viewpoint_file         ' + projectName + '_' + 'fakeView.vf\n' + \
                  'AdaptiveZoneApplies    ' + `adaptiveZone` + '\n' + \
                  'dgp_image_x_size       ' + `dgp_image_x` + '\n' + \
                  'dgp_image_y_size       ' + `dgp_image_y` + '\n'
    
    # radiance parameters
    def DSRADStr(self, radParameters):
        return '\n\n#################################\n' + \
                  '#       RADIANCE PARAMETERS      \n' + \
                  '#################################\n' + \
                  'ab ' + `radParameters["_ab_"]` + '\n' + \
                  'ad ' + `radParameters["_ad_"]` + '\n' + \
                  'as ' + `radParameters["_as_"]` + '\n' + \
                  'ar ' + `radParameters["_ar_"]` + '\n' + \
                  'aa ' + `radParameters["_aa_"]` + '\n' + \
                  'lr 6\n' + \
                  'st 0.1500\n' + \
                  'sj 1.0000\n' + \
                  'lw 0.0040000\n' + \
                  'dj 0.0000\n' + \
                  'ds 0.200\n' + \
                  'dr 2\n' + \
                  'dp 512\n'
                          
    def DSDynamicSimStr(self, shadingRecipes, projectName, subWorkingDir, testPts, cpuCount = 0):
        
        dynOptStr = '\n==========================\n' + \
                    '= shading control system\n' + \
                    '==========================\n'
        
        numOfDynamicShadings = 0
        # find number of dynamic shadings
        for shadingRecipe in shadingRecipes:
            if shadingRecipe.type == 2:
                numOfDynamicShadings += 1

        dynamicShdHeading ='shading -' + str(numOfDynamicShadings) + '\n' + \
                    projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '.ill\n'
        
        dynamicCounter = 0
        for recipeCount, shadingRecipe in enumerate(shadingRecipes):
            name = shadingRecipe.name
            type = shadingRecipe.type
            if type == 1:
                # no dynamic blind
                sensorPts = []
                dynamicShd ='shading ' + str(type) + ' ' + name + ' ' + projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '.ill\n' + \
                            '\n'
            elif type == 0:
                # conceptual dynamic shading
                sensors = shadingRecipe.sensorPts
                dynamicShd ='shading ' + str(type) + '\n' + \
                            name + '_' + str(recipeCount+1) + ' ' + projectName + '_' + `cpuCount` + '.dc ' + projectName + '_' + `cpuCount` + '_up.ill\n' + \
                            projectName + '_' + `cpuCount` + '_down.ill\n\n'
                            
            elif type == 2:
                dynamicCounter += 1
                dynamicShd = ""
                
                # advanced dynamic shading
                glareControlRecipe = shadingRecipe.glareControlR
                shadingStates = shadingRecipe.shadingStates
                controlSystem = shadingRecipe.controlSystem
                # sensors = shadingRecipe.sensorPts #sensors are removed from this part and will be added later for the analysis
                coolingPeriod = shadingRecipe.coolingPeriod
                
                # add the heading for the first dynamic shading group
                if dynamicCounter == 1: dynamicShd = dynamicShdHeading
                groupName = name
                
                if controlSystem == "ManualControl":
                    dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "ManualControl " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                    
                    for stateCount in range(1, len(shadingStates)):
                        dynamicShd += subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                      groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                      groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                
                elif controlSystem == "AutomatedThermalControl":
                    if glareControlRecipe!=None:
                        controlSystem = "AutomatedGlareControl"
                        exteriorSensor = glareControlRecipe.exteriorSensor
                        threshold = glareControlRecipe.threshold
                        minAz = glareControlRecipe.minAz
                        maxAz = glareControlRecipe.maxAz
                        minAlt = glareControlRecipe.minAltitude
                        maxAlt = glareControlRecipe.maxAltitude
                        
                    if len(coolingPeriod)!=0:
                        stMonth, stDay, hour = coolingPeriod[0]
                        endMonth, endDay, hour = coolingPeriod[1]
                        
                        controlSystem += "WithOccupancy"
                    
                    if controlSystem == "AutomatedThermalControl":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedThermalControl " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                # empty shading states
                                pass
                    
                    elif controlSystem == "AutomatedThermalControlWithOccupancy":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedThermalControlWithOccupancy " + \
                                  `stMonth` + " " + `stDay` + " " + `endMonth` + " " + `endDay` + " " + \
                                  subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                                
                    elif controlSystem == "AutomatedGlareControl":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedGlareControl \n" + \
                                  `int(threshold)` + " " + `int(minAz)` + " " + `int(maxAz)` + " " + \
                                  `int(minAlt)` + " " + `int(maxAlt)` + " " + subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                    
                    elif controlSystem == "AutomatedGlareControlWithOccupancy":
                        dynamicShd += groupName + '\n' + \
                                  str(len(shadingStates)-1) + '\n' + \
                                  "AutomatedGlareControlWithOccupancy \n" + \
                                  `int(threshold)` + " " + `int(minAz)` + " " + `int(maxAz)` + " " + \
                                  `int(minAlt)` + " " + `int(maxAlt)` + "\n" + \
                                  `stMonth` + " " + `stDay` + " " + `endMonth` + " " + `endDay` + " " + \
                                  subWorkingDir + "\\" + groupName + "_state_1.rad\n"
                        
                        for stateCount, shadingState in enumerate(shadingStates):
                            try:
                                dynamicShd += `int(shadingState.minIlluminance)` + " " + `int(shadingState.maxIlluminance)` + " " + \
                                          subWorkingDir + "\\" + groupName + "_state_" + str(stateCount + 1) + ".rad " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".dc " + \
                                          groupName + "_state_" + str(stateCount + 1) + '_' + `cpuCount` + ".ill\n"
                            except:
                                pass
                    
                    
            dynOptStr += dynamicShd
        
        
        # I removed the sensor point from here as it wasn't really nessecay to 
        # apply it here and it was also 
        
        #sensorInfoStr = 'sensor_file_info'
        #if type == 0 or type == 2:
        #    for pt in testPts:
        #        if self.isSensor(pt, sensors):
        #            sensorInfoStr += ' BG' + str(recipeCount+1)
        #        # if BG1_Ext
        #        # add external sensor_ This should happen inside the loop for each group
        #        # as the point maybe part of multiple shading groups
        #        else:
        #            sensorInfoStr += ' 0'
        #        
        #else:
        #    for pt in testPts: sensorInfoStr += ' 0'
        #
        #dynOptStr += sensorInfoStr
        
        #'==========================\n' + \
        #'= electric lighting system\n' + \
        #'==========================\n' + \
        #'electric_lighting_system 2\n' + \
        #'   4 manual_dimming    100 1 0.0 20 300\n' + \
        #'   1 manual_control    200 1\n' + \
        #'\n' + \
        #'sensor_file_info '
        #for pt in range(lenOfPts[cpuCount]): dynOptStr = dynOptStr + '0 '
        
        return dynOptStr + '\n'
    
    
    def resultStr(self, projectName, cpuCount):
        return  '\n\n######################\n' + \
                '# daylighting results \n' + \
                '######################\n' + \
                'daylight_autonomy_active_RGB ' + projectName + '_' + `cpuCount` + '_autonomy.DA\n' + \
                'electric_lighting ' + projectName + '_' + `cpuCount` + '_electriclighting.htm\n' + \
                'direct_sunlight_file ' + projectName  + '_' + `cpuCount` + '.dir\n' + \
                'thermal_simulation ' + projectName  + '_' + `cpuCount` + '_intgain.csv\n'


sc.sticky["honeybee_WriteRAD"] = WriteRAD
sc.sticky["honeybee_WriteRADAUX"] = WriteRADAUX
sc.sticky["honeybee_WriteDS"] = WriteDS

def main(north, HBObjects, analysisRecipe, runRad, numOfCPUs, workingDir, radFileName, meshingLevel, waitingTime, overwriteResults):
    # import the classes
    if sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        hb_writeRAD = sc.sticky["honeybee_WriteRAD"]()
        hb_writeRADAUX = sc.sticky["honeybee_WriteRADAUX"]()
        hb_RADMaterialAUX = sc.sticky["honeybee_RADMaterialAUX"]()
        hb_materilaLib = sc.sticky["honeybee_materialLib"]
        hb_scheduleLib = sc.sticky["honeybee_ScheduleLib"]
        hb_writeDS = sc.sticky["honeybee_WriteDS"]()
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        hb_dsParameters = sc.sticky["honeybee_DSParameters"]()
        
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        hb_DSPath = hb_folders["DSPath"]
        hb_DSCore = hb_folders["DSCorePath"]
        hb_DSLibPath = hb_folders["DSLibPath"]
        hb_EPPath = hb_folders["EPPath"]
        
        northAngle, northVector = lb_preparation.angle2north(north)
        
        if analysisRecipe:
            #epwFileAddress, runRadiationAnalysis_GridPts, analysisPeriod, runRadiationAnalysis_Image, rhinoViewNames, runDaylightingSimulation, skyCondition, hour, day, month, runClimateBasedSimulation, dasysimParameters = analysesRecipe
            # print runRadiationAnalysis_GridPts
            # I think it is easier to keep read the parameters here instead of having a function
            # so it is going to be easier to read
            analysisType = analysisRecipe.type
            radParameters = analysisRecipe.radParameters
            backupImages = 0 # will change to 1 or 2 in case the user set it to another number for image-based analysis
            numOfIllFiles = 1
            if radParameters==None:
                quality = 0
                radParameters = {}
                print "Default values are set for RAD parameters"
                for key in hb_radParDict.keys():
                    #print key + " is set to " + str(hb_radParDict[key][quality])
                    radParameters[key] = hb_radParDict[key][quality]
            if analysisType == 0:
                print "Image-based simulation"
                radSkyFileName = analysisRecipe.skyFile
                rhinoViewNames = analysisRecipe.viewNames
                cameraType = analysisRecipe.cameraType
                imageSize = analysisRecipe.imageSize
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                sectionPlane = analysisRecipe.sectionPlane
                backupImages = analysisRecipe.backupImages
            
            elif analysisType == 1:
                print "Grid-based Radiance simulation"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            
            elif analysisType == 2:
                print "Annual climate-based analysis"
                epwFileAddress = analysisRecipe.weatherFile 
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                
                if analysisRecipe.DSParameters == None: analysisRecipe.DSParameters = hb_dsParameters
                outputUnits = analysisRecipe.DSParameters.outputUnits
                adaptiveZone = analysisRecipe.DSParameters.adaptiveZone
                dgp_imageSize = analysisRecipe.DSParameters.dgp_imageSize
                dynamicShadingRecipes = analysisRecipe.DSParameters.DShdR
                numOfIllFiles = analysisRecipe.DSParameters.numOfIll
                
                studyFolder = analysisRecipe.studyFolder
            
            elif analysisType == 3:
                print "Daylight factor"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            elif analysisType == 4:
                print "Vertical Sky Component"
                radSkyFileName = analysisRecipe.skyFile
                testPoints = analysisRecipe.testPts
                ptsNormals = analysisRecipe.vectors
                simulationType = analysisRecipe.simulationType
                studyFolder = analysisRecipe.studyFolder
                
            # double check and make sure that the parameters are set good enough
            # for grid based simulation
            if analysisType != 0:
                print "The component is checking ad, as, ar and aa values. " + \
                      "This is just to make sure that the results are accurate enough."
                
                if radParameters["_ad_"] < 1000:
                    radParameters["_ad_"] = 1000
                    print "-ad is set to 1000."
                
                if radParameters["_as_"] < 20:
                    radParameters["_as_"] = 20
                    print "-as is set to 20."
                
                if radParameters["_ar_"] < 300:
                    # setting up the ar to 300 is tricky but I'm pretty sure in many
                    # cases there will shadings involved.
                    radParameters["_ar_"] = 300
                    print "-ar is set to 300."
                
                if radParameters["_aa_"] > 0.1:
                    # the same here. I think it is good to let the user wait a little bit more
                    # but have a result that makes sense. If you are an exprienced user and don't
                    # like this feel free to remove the if condition. Keep in mind that I only
                    # apply this for grid based analysis, so the images can be rendered with any quality
                    radParameters["_aa_"] = 0.1
                    print "-aa is set to 0.1"
                
                print "Good to go!"
        
        #stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, True)
        #conversionFac = lb_preparation.checkUnits()
        
        # if radParameters: 
        
        # check for folder and idf file address
        # make working directory
        if workingDir:
            workingDir = lb_preparation.removeBlankLight(workingDir)
        
        workingDir = lb_preparation.makeWorkingDir(workingDir)
        
        # make sure the directory has been created
        if workingDir == -1: return -1
        workingDrive = workingDir[0:1]
        
        ## check for the name of the file
        if radFileName == None: radFileName = 'unnamed'
        
        # make new folder for each study
        subWorkingDir = lb_preparation.makeWorkingDir(workingDir + "\\" + radFileName + studyFolder)
        print 'Current working directory is set to: ', subWorkingDir
        
        try:
            if os.path.exists(subWorkingDir):
                if backupImages != 0:
                    # create the backup folder and copy the images to the folder
                    imageFolder = workingDir + "\\" + radFileName + "\\imagesBackup"
                    
                    if not os.path.exists(imageFolder): os.mkdir(imageFolder)
                    
                    # copy the files into the folder
                    imageExtensions = ["JPEG", "JPG", "GIF", "TIFF", "TIF", "HDR", "PIC"]
                    timeID = hb_writeRADAUX.getTime()
                    fileNames = os.listdir(subWorkingDir)
                    
                if backupImages == 1:
                    # keep all the files in the same folder
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            newFileName = (".").join(fileName.split(".")[:-1])
                            extension = fileName.split(".")[-1]
                            newFullName = newFileName + "_" + timeID + "." + extension
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder, newFullName) , True)
                    
                elif backupImages == 2:
                    for fileName in fileNames:
                        if fileName.split(".")[-1].upper() in imageExtensions:
                            if not os.path.exists(imageFolder + "\\" + timeID):
                                os.mkdir(imageFolder + "\\" + timeID)
                            # copy the files to image backup folder with data and time added
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(imageFolder + "\\" + timeID, fileName) , True)
                
                if not overwriteResults:
                    fileNames = os.listdir(subWorkingDir)
                    
                    mainBackupFolder = subWorkingDir[:-1] + "_backup"
                    
                    counter = 0
                    backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    while os.path.isdir(backupFolder):
                        counter += 1
                        backupFolder = os.path.join(mainBackupFolder, str(counter))
                    
                    os.mkdir(backupFolder)
                    
                    for fileName in fileNames:
                        try:
                            # copy the files to image backup folder with data and time added
                            hb_writeRADAUX.copyFile(os.path.join(subWorkingDir, fileName), os.path.join(backupFolder, fileName) , True)                    
                        except:
                            pass
                    
                    print "Results of the previous study are copied to " + backupFolder
                    
                lb_preparation.nukedir(subWorkingDir, rmdir = False)
        except Exception, e:
            print 'Failed to remove the old directory.'
            print `e`
            
        
        # sky and material file
        # copy the sky file to the local folder
        if analysisType != 2:
            skyTempName = radSkyFileName.split("\\")[-1]
            skyName = skyTempName.split("/")[-1]
            
            hb_writeRADAUX.copyFile(radSkyFileName, subWorkingDir + "\\" + skyName, True)
            radSkyFileName = os.path.join(subWorkingDir, skyName)
        
        radFileFullName = subWorkingDir + "\\" + radFileName + '.rad'
        
        ######################### WRITE RAD FILES ###########################
        
        # 2.1 write the geometry file
        ########################################################################
        ######################## GENERATE THE BASE RAD FILE ####################
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBObjects = hb_hive.callFromHoneybeeHive(HBObjects)
        geoRadFile = open(radFileFullName, 'w')
        geoRadFile.write("#GENERATED BY HONEYBEE\n")
        customRADMat = {} # dictionary to collect the custom material names
        customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
        if len(HBObjects)!=0:
            for HBObj in HBObjects:
                # check if the object is zone or a surface (?)
                if HBObj.objectType == "HBZone":
                    if HBObj.hasNonPlanarSrf or HBObj.hasInternalEdge:
                        HBObj.prepareNonPlanarZone(meshingLevel)
                    
                    for srf in HBObj.surfaces:
                        # collect the custom material informations
                        if srf.RadMaterial!=None:
                            customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(srf, customRADMat, customMixFunRadMat)
                        # write the surfaces
                        
                        if srf.isPlanar and len(srf.childSrfs)<2:
                            geoRadFile.write(hb_writeRAD.RADSurface(srf))
                        else:
                            geoRadFile.write(hb_writeRAD.RADNonPlanarSurface(srf))
                            if srf.hasChild:
                                # collect the custom material informations
                                for childSrf in srf.childSrfs:
                                    if childSrf.RadMaterial!=None:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                geoRadFile.write(hb_writeRAD.RADNonPlanarChildSurface(srf))
                
                elif HBObj.objectType == "HBSurface":
                    
                    # I should wrap this in a function as I'm using it multiple times with minor changes
                    # collect the custom material informations
                    if HBObj.RadMaterial!=None:
                        try:
                            customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
                        except:
                            msg = HBObj.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                            print msg
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                            return -1
                            
                            
                    if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                        geoRadFile.write(hb_writeRAD.RADSurface(HBObj))
                    else:
                        geoRadFile.write(hb_writeRAD.RADNonPlanarSurface(HBObj))
                        if not HBObj.isChild and HBObj.hasChild:
                            # collect the custom material informations
                            for childSrf in HBObj.childSrfs:
                                if childSrf.RadMaterial!=None:
                                    try:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                    except:
                                        msg = childSrf.RadMaterial + " is not defined in the material library! Add the material to library and try again."
                                        print msg
                                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                                        return -1
                            geoRadFile.write(hb_writeRAD.RADNonPlanarChildSurface(HBObj))
                            
        geoRadFile.close()
        
        ########################################################################
        ######################## GENERATE THE BASE RAD FILE ####################
        materialFileName = subWorkingDir + "\\material_" + radFileName + '.rad'
        # This part should be fully replaced with the new method where I generate the materials from the 
        
        # 0.1 material string
        matStr =  "# start of generic materials definition(s)\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Context_Material') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Interior_Ceiling') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Interior_Floor') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Window') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Roof') + "\n" + \
            hb_RADMaterialAUX.getRADMaterialString('000_Exterior_Wall') + "\n" + \
            "# end of generic materials definition(s)\n"
    
        with open(materialFileName, 'w') as matFile:
            matFile.write(matStr)
            matFile.write("\n# start of material(s) specific to this study (if any)\n")
            for radMatName in customRADMat.keys():
                matFile.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                
                # check if the material is is trans
                if hb_RADMaterialAUX.getRADMaterialType(radMatName) == "trans":
                    
                    # get the st value
                    st = hb_RADMaterialAUX.getSTForTransMaterials(radMatName)
                    if st < radParameters["_st_"]:
                        print "Found a trans material... " + \
                              "Resetting st parameter from " + str(radParameters["_st_"]) + " to " + str(st)
                        radParameters["_st_"] = st
                    
            # write mixedfun if any
            for radMatName in customMixFunRadMat.keys():
                matFile.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
            matFile.write("# end of material(s) specific to this study (if any)\n")
            
        # add shading files for daysim advanced dynamic shadings
        dynamicCounter = 0
        if analysisRecipe.type == 2 and len(dynamicShadingRecipes)!=0:
            customRADMat = {} # dictionary to collect the custom material names
            customMixFunRadMat = {} # dictionary to collect the custom mixfunc material names
            
            for shadingRecipe in dynamicShadingRecipes:
                if shadingRecipe.type == 2:
                    
                    groupName = shadingRecipe.name
                    
                    dynamicCounter+=1
                    for stateCount, shadingState in enumerate(shadingRecipe.shadingStates):
                        
                        fileName = groupName + "_state_" + str(stateCount + 1) + ".rad"
                        
                        try:
                            radStr = ""
                            
                            shdHBObjects = hb_hive.callFromHoneybeeHive(shadingState.shdHBObjects)
                            
                            for HBObj in shdHBObjects:
                                # collect the custom material informations
                                if HBObj.RadMaterial!=None:
                                        customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(HBObj, customRADMat, customMixFunRadMat)
            
                                if HBObj.isPlanar and (not HBObj.isChild and len(HBObj.childSrfs)<2):
                                    radStr += hb_writeRAD.RADSurface(HBObj)
                                else:
                                    radStr += hb_writeRAD.RADNonPlanarSurface(HBObj)
                                    if not HBObj.isChild and HBObj.hasChild:
                                        # collect the custom material informations
                                        for childSrf in HBObj.childSrfs:
                                            if childSrf.RadMaterial!=None:
                                                customRADMat, customMixFunRadMat = hb_RADMaterialAUX.addRADMatToDocumentDict(childSrf, customRADMat, customMixFunRadMat)
                                        radStr += hb_writeRAD.RADNonPlanarChildSurface(HBObj)
                            
                            
                            # write the shading file
                            with open(subWorkingDir + "\\" + fileName, "w") as radInf:
                                radInf.write(matStr)
                                radInf.write("# material(s) specific to this study\n")
                                for radMatName in customRADMat.keys():
                                    radInf.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                # write mixedfun if any
                                for radMatName in customMixFunRadMat.keys():
                                    radInf.write(hb_RADMaterialAUX.getRADMaterialString(radMatName) + "\n")
                                radInf.write(radStr)
                                
                        except Exception, e:
                            # print `e`
                            # None object so just create an empty file
                            with open(subWorkingDir + "\\" + fileName , "w") as radInf:
                                radInf.write("#empty shading file")
                            pass
                            
        ######################## GENERATE POINT FILES #######################
        # test points should be generated if the study is grid based
        # except image-based simulation
        if analysisType != 0:
            # write a pattern file which I can use later to re-branch the points
            ptnFileName = radFileFullName.replace('.rad','.ptn')
            with open(ptnFileName, "w") as ptnFile:
                for ptList in testPoints:
                    ptnFile.write(str(len(ptList)) + ", ")
            
            # faltten the test points
            flattenTestPoints = lb_preparation.flattenList(testPoints)
            flattenPtsNormals = lb_preparation.flattenList(ptsNormals)
            numOfPoints = len(flattenTestPoints)
        
            if numOfCPUs > numOfPoints: numOfCPUs = numOfCPUs
        
            if numOfCPUs > 1: ptsEachCpu = int(numOfPoints/(numOfCPUs))
            else: ptsEachCpu = numOfPoints
        
            lenOfPts = []
            testPtsEachCPU = []
            
            for cpuCount in range(numOfCPUs):
                # write pts file
                ptsForThisCPU = []
                ptsFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.pts')
                ptsFile = open(ptsFileName, "w")
                if cpuCount + 1 != numOfCPUs:
                    for ptCount in range(cpuCount * ptsEachCpu, (cpuCount + 1) * ptsEachCpu):
                        ptsFile.write(hb_writeRADAUX.testPtsStr(flattenTestPoints[ptCount], flattenPtsNormals[ptCount]))
                        ptsForThisCPU.append(flattenTestPoints[ptCount])
                    lenOfPts.append(ptsEachCpu)
                    
                else:
                    for ptCount in range(cpuCount * ptsEachCpu, numOfPoints):
                        ptsFile.write(hb_writeRADAUX.testPtsStr(flattenTestPoints[ptCount], flattenPtsNormals[ptCount]))
                        ptsForThisCPU.append(flattenTestPoints[ptCount])
                    lenOfPts.append(numOfPoints - (cpuCount * ptsEachCpu))
                
                ptsFile.close()
                
                testPtsEachCPU.append(ptsForThisCPU)
                
        ######################## WRITE ANNUAL SIMULATION - DAYSIM #######################
        if analysisRecipe.type == 2:
            # check for Daysim to be installed on the system and available in the path
            #if not os.path.isdir("c:/DAYSIM"):
            #    print "You need to install DAYSIM at C:/DAYSIM"
            #    return -1
            
            DSResultFilesAddress = []
            
            # write the init batch files
            
            # location string
            locationStr, locName = hb_writeDS.DSLocationStr(hb_writeRADAUX, lb_preparation, epwFileAddress, outputUnits)
            newLocName = lb_preparation.removeBlankLight(locName)
            
            # copy .epw file to sub-directory
            lb_preparation.copyFile(epwFileAddress, subWorkingDir + "\\" + newLocName + '.epw')
            #lb_preparation.copyFile(epwFileAddress, subWorkingDir + "\\" + locName + '.epw')
            
            pathStr = "SET RAYPATH=.;" + hb_RADLibPath + ";" + hb_DSPath + ";" + hb_DSLibPath + ";\nPATH=" + hb_RADPath + ";" + hb_DSPath + ";" + hb_DSLibPath + ";$PATH\n"
            heaFileName = radFileFullName.replace('.rad', '_0.hea')
            initBatchFileName = radFileFullName.replace('.rad', '_InitDS.bat')
            initBatchFile = open(initBatchFileName, "w")
            initBatchFile.write(pathStr)
            initBatchStr =  'C:\n' + \
                            'CD ' + hb_DSPath + '\n' + \
                            'epw2wea  ' + subWorkingDir + "\\" + lb_preparation.removeBlankLight(locName) + '.epw ' + subWorkingDir + "\\" +  lb_preparation.removeBlankLight(locName) + '.wea\n' + \
                            ':: 1. Generate Daysim version of Radiance Files\n' + \
                            'radfiles2daysim ' + heaFileName + ' -m -g\n'
                            
            initBatchFile.write(initBatchStr)
            initBatchFile.close()
            fileNames = []
            # write the rest of the files
            for cpuCount in range(numOfCPUs):
                heaFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.hea')
                heaFile = open(heaFileName, "w")
                projectName =  radFileName
                
                tempDirName = subWorkingDir + '\\tmp_' + `cpuCount`
                heaFile.write(hb_writeDS.DSHeadingStr(projectName, subWorkingDir, tempDirName, hb_DSCore , cpuCount))
                
                # delete the files in the old temp folder
                # if os.path.exists(tempDirName): lb_preparation.nukedir(tempDirName,rmdir = False)
                tempWorkingDir = lb_preparation.makeWorkingDir(tempDirName)
                
                heaFile.write(locationStr)
                
                # fake .vf file - it should be fixed later
                fakeViewFileName = subWorkingDir + '\\' + projectName + '_' + 'fakeView.vf'
                vfFile = open(fakeViewFileName, "w")
                vfFile.write(' ')
                vfFile.close()
                
                # building string
                heaFile.write(hb_writeDS.DSBldgStr(projectName, materialFileName, radFileFullName, adaptiveZone, dgp_imageSize, dgp_imageSize, cpuCount))
                
                # radiance parameters string
                heaFile.write(hb_writeDS.DSRADStr(radParameters))
                
                # dynamic simulaion options
                # should be developed later!
                # I don't care about the occupancy since I read the result with a custom component
                # copy the sch to the folder
                #try: lb_preparation.copyFile(hb_DSCore + '\\occ\\weekdays9to5withDST.60min.occ.csv', subWorkingDir + '\\weekdays9to5withDST.60min.occ.csv')
                #except: pass
                
                heaFile.write(hb_writeDS.DSDynamicSimStr(dynamicShadingRecipes, projectName, subWorkingDir, testPtsEachCPU[cpuCount], cpuCount))
                
                # heaFile.write(hb_writeDS.resultStr(projectName, cpuCount))
                heaFile.close()

                # ill files
                DSResultFilesAddress.append(radFileFullName.replace('.rad', '_' + `cpuCount` + '.ill'))
                # 3.  write the batch file
                DSBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_DS.bat')
                DSBatchFile = open(DSBatchFileName, "w")
                
                fileNames.append(DSBatchFileName.split("\\")[-1])
                
                heaFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '.hea')
                
                #SET PATH = " + subWorkingDir + "\n" + workingDrive +"\n"
                DSBatchFile.write(pathStr)
                
                DSBatchStr = ':: Calculate Daylight Coefficient File (*.dc)\n' + \
                            'gen_dc ' + heaFileName + ' -dif\n' + \
                            'gen_dc ' + heaFileName + ' -dir\n' + \
                            'gen_dc ' + heaFileName + ' -paste\n' + \
                            '\n' + \
                            ':: Generate Illuminance Files (*.ill)\n' + \
                            'ds_illum  ' + heaFileName + '\n'
                
                DSBatchFile.write(DSBatchStr)
                            
                DSBatchFile.close()
                
            if runRad:
                os.system(initBatchFileName)
                time.sleep(waitingTime)
                for cpuCount in range(numOfCPUs):
                    # running batch file in background
                    DSBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_DS.bat')
                    # print DSBatchFileName
                    p = subprocess.Popen(r'start cmd /c ' + DSBatchFileName , shell=True)
                    time.sleep(waitingTime)
                    #p.wait()
                    #os.system(DSBatchFileName)
                # read the number of .ill files
                # and the number of .dc files
                if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                startTime = time.time()
                # print fileNames
                isTheStudyOver(fileNames)
                # check if the results are available
                files = os.listdir(subWorkingDir)
                numIll = 0
                numDc = 0
                conceptualShade = False
                conceptualShadingIllFiles = []
                for fileName in files:
                    if fileName.endswith('ill'):
                        numIll+=1
                        if fileName.endswith('_up.ill'):
                            conceptualShade = True
                            conceptualShadingIllFiles.append(os.path.join(subWorkingDir, fileName))
                            
                            
                    elif fileName.endswith('dc'): numDc+=1
                
                if conceptualShade: numDc = 2 * numDc
                if numIll!= numOfCPUs * numOfIllFiles or  numDc!= numOfCPUs * numOfIllFiles:
                    print "Failed to load the results!"
                    DSResultFilesAddress = []
                if len(conceptualShadingIllFiles) * len(DSResultFilesAddress)!=0:
                     DSResultFilesAddress = conceptualShadingIllFiles
                
                return radFileFullName, [], [], testPoints, DSResultFilesAddress, []
            else:
                return radFileFullName, [], [], testPoints, [], []
                
        ######################## NOT ANNUAL SIMULATION #######################
        
        elif analysisRecipe.type != 2:
            #if not os.path.isdir("c:/RADIANCE"):
            #    print "You need to install RADIANCE at C:/Radiance"
            #    return -1
            
            # 3.  write the batch file
            if analysisRecipe.type == 0:
                # image based
                initBatchFileName = radFileFullName.replace('.rad', '.bat')
            else:
                # not annual and not image based
                initBatchFileName = radFileFullName.replace('.rad', '_RADInit.bat')
            
            batchFile = open(initBatchFileName, "w")
            
            # write the path string (I should check radiance to be installed on the system
            pathStr = "SET RAYPATH=.;" + hb_RADLibPath + "\nPATH=" + hb_RADPath + ";$PATH\n"
            batchFile.write(pathStr)
            
            batchFile.write("c:\n")
            batchFile.write("cd " + subWorkingDir + "\n")
            
            # write OCT file
            # 3.2. oconv line
            OCTFileName = radFileName + '_RAD'
            OCTLine = hb_writeRADAUX.oconvLine(OCTFileName, [materialFileName, radSkyFileName, radFileFullName])
            batchFile.write(OCTLine)
            
            if analysisRecipe.type == 0:
                # write view files
                if len(rhinoViewNames)==0: rhinoViewNames = [sc.doc.Views.ActiveView.ActiveViewport.Name]
                # print rhinoViewNames
                HDRFileAddress = []
                for view in rhinoViewNames:
                    view = lb_preparation.removeBlank(view)
                    HDRFileAddress.append(subWorkingDir + "\\" + OCTFileName + "_" + view + ".HDR")
                    viewLine = hb_writeRADAUX.exportView(view, radParameters, cameraType, imageSize, sectionPlane)
                    # write rpict lines
                    RPICTLines = hb_writeRADAUX.rpictLineAlternate(viewLine, OCTFileName, view, radParameters, int(simulationType))
                    batchFile.write(RPICTLines)
                batchFile.close()
            else:
                batchFile.close() # close the init file
                fileNames = []
                for cpuCount in range(numOfCPUs):
                    # create a batch file
                    batchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_RAD.bat')
                    fileNames.append(batchFileName.split("\\")[-1])
                    batchFile = open(batchFileName, "w")
                    # write path files
                    batchFile.write(pathStr)
                    batchFile.write("c:\n")
                    batchFile.write("cd " + subWorkingDir + "\n")
                    
                    # 3.4. add rtrace lin
                    RTRACELine = hb_writeRADAUX.rtraceLine(radFileName, OCTFileName, radParameters, int(simulationType), cpuCount)
                    batchFile.write(RTRACELine)
                    
                    # close the file
                    batchFile.close()
            if runRad:
                # run batch file and return address  and the result
                if  analysisRecipe.type == 0:
                    os.system(initBatchFileName)
                    return radFileFullName, [], [], [], [], HDRFileAddress
                
                else:
                    RADResultFilesAddress = []
                    os.system(initBatchFileName)
                    for cpuCount in range(numOfCPUs):
                        # running batch file in background
                        RADBatchFileName = radFileFullName.replace('.rad', '_' + `cpuCount` + '_RAD.bat')
                        # print DSBatchFileName
                        p = subprocess.Popen(r'start cmd /c ' + RADBatchFileName , shell=True)
                        
                        RADResultFilesAddress.append(radFileFullName.replace('.rad', '_' + `cpuCount` + '.res'))
                        time.sleep(waitingTime)
                        
                    if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
                    
                    startTime = time.time()
                    isTheStudyOver(fileNames)
                    
                    numRes = 0
                    files = os.listdir(subWorkingDir)
                    for file in files:
                        if file.EndsWith('res'): numRes+=1
                    if numRes != numOfIllFiles * numOfCPUs:
                        print "Cannot find the results of the study"
                        RADResultFilesAddress = []
                    time.sleep(1)
                    # run all the batch files
                    
                    return radFileFullName, [], RADResultFilesAddress, testPoints, [], []
                
            else:
                # return name of the file
                if  analysisRecipe.type == 0: return radFileFullName, [], [], [], [], []
                else: return radFileFullName, [], [], testPoints, [], []
                
    else:
        print "You should first let both Ladybug and Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let both Ladybug and Honeybee to fly...")
        return -1

if _writeRad == True and len(_HBObjects)!=0 and _HBObjects[0]!=None and _analysisRecipe!=None:
    report = ""
    done = False
    waitingTime = 0.2 # waiting time between batch files in seconds
    try: numOfCPUs = int(_numOfCPUs_)
    except: numOfCPUs = 1
    
    # make sure it is not more than the number of available CPUs
    ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
    
    if numOfCPUs > ncpus:
        print "Sorry! But the number of available CPUs on your machine is " + str(ncpus) + "." + \
              "\nHoneybee set the number of CPUs to " + str(ncpus) + ".\n"
        numOfCPUs = ncpus
        
    
    
    result = main(north_, _HBObjects, _analysisRecipe, runRad_, numOfCPUs, _workingDir_, _radFileName_, meshingLevel_, waitingTime, overwriteResults_)
    
    if result!= -1:
        # RADGeoFileAddress, radiationResult, RADResultFilesAddress, testPoints, DSResultFilesAddress, HDRFileAddress = result
        radianceGeometryPath, radiationResult, gridBasedResultsPath, testPoints, annualAnalysisPath, HDRImageOutputPath = result
        
        testPts = DataTree[System.Object]()
        for i, ptList in enumerate(testPoints):
            p = GH_Path(i)
            testPts.AddRange(ptList, p)
        
        # add analysis type
        analysisTypesDict = {0: ["0: illuminance" , "lux"],
                             1: ["1: radiation" , "wh/m2"],
                             1.1: ["1.1: cumulative radiation" , "kWh/m2"],
                             2: ["2: luminance" , "cd/m2"],
                             3: ["3: daylight factor", "%"],
                             4: ["4: vertical sky component", "%"]}
        
        analysisType = _analysisRecipe.type
        
        if analysisType == 3 or analysisType == 4:
            analysisTypeKey = analysisType
        
        elif analysisType == 0 or analysisType == 1:
            analysisTypeKey = _analysisRecipe.simulationType
        
        elif analysisType == 2:
            analysisTypeKey = None
            
        try:
            analysisType, resultsUnit = analysisTypesDict[analysisTypeKey]
        except:
            analysisType, resultsUnit = "annual analysis", "var"
            
        done = True
