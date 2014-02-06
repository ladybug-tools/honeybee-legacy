"""
Analysis Recipie for Image-Based Analysis
-
Provided by Honybee 0.0.10
    
    Args:
        _skyFile: Path to a radiance sky file
        _rhinoViewsName_: viewName to be rendered
        sectionPlane_: Optional view fore clipping plane. The Plane should be perpendicular to the view
        _cameraType_: [0] Perspective, [1] FishEye, [2] Parallel
        _simulationType_: [0] illuminance(lux), [1] radiation (wh), [2] luminance (Candela). Default is 2 > luminance.
        _imageWidth_: Optional input for image width in pixels
        _imageHeight_: Optional input for image height in pixels
        _radParameters_: Radiance parameters
        backupImages_: [0] No backup, [1] Backup in the same folder, [2] Backup in separate folders. Desfault is 0.
        
    Returns:
        analysisRecipe: Recipe for image-based simulation
"""

ghenv.Component.Name = "Honeybee_Image Based Simulation"
ghenv.Component.NickName = 'imageBasedSimulation'
ghenv.Component.Message = 'VER 0.0.44\nFEB_06_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import Rhino as rc
import Grasshopper.Kernel as gh

class DLAnalysisRecipe(object):
    
    def __init__(self, type, *arg):
        """
        types:
            0: image based analysis > Illuminance(lux) = 0, Radiation(kwh)   = 1,  Luminance (cd)   = 2
            1: node based analysis
            2: annual simulation (Daysim for now)
            3: daylight factor
            4: vertical sky component
        """
        self.type = type
        
        # based on the type it should return different outputs
        if type == 0:
            self.skyFile = arg[0]
            self.viewNames = arg[1]
            try: self.radParameters = arg[2].d
            except: self.radParameters = arg[2]
            self.cameraType = arg[3]
            self.simulationType = arg[4]
            self.imageSize = arg[5], arg[6]
            self.sectionPlane = arg[7]
            self.backupImages =  arg[8]
            self.studyFolder = "\\imageBasedSimulation\\"
            
        elif type == 1:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = arg[4]
            self.studyFolder = "\\gridBasedSimulation\\"
            
        elif type == 2:
            self.weatherFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.DSParameters = arg[4]
            self.studyFolder = "\\annualSimulation\\"
        
        elif type == 3:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = 0 #illuminance
            self.studyFolder = "\\DF\\"
        
        elif type == 4:
            self.skyFile = arg[0]
            self.testPts = self.convertTreeToLists(arg[1])
            self.vectors = self.convertTreeToLists(arg[2])
            try: self.radParameters = arg[3].d
            except: self.radParameters = arg[3]
            self.simulationType = 0 #illuminance
            self.studyFolder = "\\VSC\\"
        
        # double check the sky in case of grid based and image based simulations
        if type ==0 or type == 1:
            self.checkSky()
                    
    def convertTreeToLists(self, l):
        listOfLists = []
        for path in l.Paths:
            listOfLists.append(l.Branch(path))
        return listOfLists
    
    def checkSky(self):
        if self.simulationType == 1:
            # make sure the sky is either gencum or gendaylit
            # edit in case of gendaylit
            self.radSkyFile = self.skyFile.split(".")[0] + "_radAnalysis.sky"
            skyOut = open(self.radSkyFile, "w")
            genDaylit = False
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.startswith("!gensky"):
                        self.skyFile = None
                        msg = "You need to use one of the climate-based skies for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return
                    elif line.startswith("!gendaylit"):
                        line = line.replace("-O 0", "-O 1")
                        genDaylit = True
                    # write a new file
                    skyOut.write(line)
            skyOut.close()
            self.skyFile = self.radSkyFile
            if not genDaylit:
                self.simulationType = 1.1 # annual radiation analysis
        
        else:
            # make sure the sky is not from gencum
            with open(self.skyFile, "r") as skyIn:
                for line in skyIn:
                    if line.strip().startswith("2 skybright") and line.strip().endswith(".cal"):
                        self.skyFile = None
                        msg = "Cumulative sky can only be used for radiation analysis.\n" + \
                              "Change the skyFile and try again"
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return
            


if _skyFile:
    recipe = DLAnalysisRecipe(0, _skyFile, _rhinoViewsName_, _radParameters_, _cameraType_, _simulationType_, _imageWidth_, _imageHeight_, sectionPlane_, backupImages_)
    
    if recipe.skyFile != None:
        analysisRecipe = recipe


