# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

# Glazing Parameters Component
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate lists of glazing ratios, window heigths, and sill heights for different cardinal directions to be plugged into the glzRatio, windowHeight, and sillHeight inputs of the "Glazing based on ratio" component.

-
Provided by Honeybee 0.0.50

    Args:
        northGlzRatio: Glazing ratio for the north side of a building.
        westGlzRatio: Glazing ratio for the west side of a building.
        southGlzRatio: Glazing ratio for the south side of a building.
        eastGlzRatio: Glazing ratio for the east side of a building.
        --------------------: ...
        northWindowHeight: Height of the window on the north side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        westWindowHeight: Height of the window on the west side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        southWindowHeight: Height of the window on the south side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        eastWindowHeight: Height of the window on the east side of a building in model units (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios).
        --------------------: ...
        northSillHeight: Distance from the floor to the bottom of the window for the north side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        westSillHeight: Distance from the floor to the bottom of the window for the west side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        southSillHeight: Distance from the floor to the bottom of the window for the south side of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
        eastSillHeight: Distance from the floor to the bottom of the window for the eastside of a building (only applicable to bldg surfaces that contain rectangular geometry; this input will be over-ridden at high glazing ratios or window heights).
    Returns:
        readMe!: ...
        glzRatioList: A list of glazing ratios for different cardinal directions to be plugged into the glzRatio input of the "Glazing based on ratio" component.
        windowHeightList: A list of window heights for different cardinal directions to be plugged into the windowHeight input of the "Glazing based on ratio" component.
        sillHeightList: A list of window sill heights for different cardinal directions to be plugged into the sillHeight input of the "Glazing based on ratio" component.
"""
ghenv.Component.Name = "Honeybee_Glazing Parameters List"
ghenv.Component.NickName = 'glzParamList'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

def giveWarning(message):
    print message
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, message)
        
def checkRatio(ratio):
    if ratio == None: return 0
    elif ratio > 0.95:
        giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are nota accepted.")
        return 0
    elif ratio < 0:
        giveWarning("Please ensure that your glazing ratio is between 0.0 and 0.95. glazing ratios outside of this are nota accepted.")
        return 0
    else: return ratio
    
northRatio = checkRatio(northGlzRatio)
westRatio = checkRatio(westGlzRatio)
southRatio = checkRatio(southGlzRatio)
eastRatio = checkRatio(eastGlzRatio)

def checkWinHeight(height):
    if height == None: return 0
    elif height < sc.doc.ModelAbsoluteTolerance:
        giveWarning("Please put in window height values that are above your model's tolerance.")
        return 0
    else: return height

northHeight = checkWinHeight(northWindowHeight)
westHeight = checkWinHeight(westWindowHeight)
southHeight = checkWinHeight(southWindowHeight)
eastHeight = checkWinHeight(eastWindowHeight)

def checkSillHeight(height):
    if height == None: return 0
    elif height < sc.doc.ModelAbsoluteTolerance:
        giveWarning("Please put in sill height values that are above your model's tolerance.")
        return 0
    else: return height

northSill = checkSillHeight(northSillHeight)
westSill = checkSillHeight(westSillHeight)
southSill = checkSillHeight(southSillHeight)
eastSill = checkSillHeight(eastSillHeight)



glzRatioList = northRatio, westRatio, southRatio, eastRatio
windowHeightList = northHeight, westHeight, southHeight, eastHeight
sillHeightList = northSill, westSill, southSill, eastSill
