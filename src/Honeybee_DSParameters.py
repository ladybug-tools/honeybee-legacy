#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Analyses Recipe for Annual Daylight Simulation with Daysim
-
Provided by Honeybee 0.0.64
    
    Args:
        _outputUnits_: A list of numbers to indicate output units for test points. Defualt is 2. [1] solar irradiance (W/m2), [2] illumiance (lux) - Default is 2
        dynamicShadingGroup_1_: Use conceptual or advanced shading recipeis to define the dynamic shading. Leave it disconnected if you don't have any dynamic shading in the model
        dynamicShadingGroup_2_: Use conceptual or advanced shading recipeis to define the dynamic shading. Leave it disconnected if you don't have any dynamic shading in the model
        ............................................: Graphical separator! Leave it empty. Thanks!
        _RhinoViewsName: List of view names that you want to be considered for annual glare analysis. Be aware that annual glare analysis with Daysim can take hours to days!
        _adaptiveZone_: Set the Boolean to True if the user can adapt his/her view within the space. "The concept is based on the hypothesis that if a user is free to look in different directions or place him or herself in different positions within a space, he or she is going to pick the most comfortable one." Read more here > http://daysim.ning.com/page/daysim-header-file-deyword-adaptive-zone
        _dgp_imageSize_: The size of the image to be used for daylight glare probability in pixels. Defult value is 250 px.
        onlyRunGlareAnalysis_: Set to False if you want the component run both annual glare analysis and calculate annula illuminance levels. Default is True.
"""

ghenv.Component.Name = "Honeybee_DSParameters"
ghenv.Component.NickName = 'DSParameters'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.63\nMAY_03_2018
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



import Grasshopper.Kernel as gh
import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino as rc

class SetDSParameters:
    
    def __init__(self, outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize, onlyRunGlareAnalysis):
        
        if len(outputUnits)!=0 and outputUnits[0]!=None: self.outputUnits = outputUnits
        else: self.outputUnits = [2]
        
        self.onlyAnnualGlare = onlyRunGlareAnalysis
        self.runAnnualGlare = False
        
        validViews = []
        if RhinoViewsName!=[]:
            for viewName in RhinoViewsName:
                # check viewes
                if viewName in rs.ViewNames():
                    validViews.append(rs.CurrentView(viewName, True))
                else:
                    # change to RhinoDoc to get access to NamedViews
                    sc.doc = rc.RhinoDoc.ActiveDoc
                    namedViews = rs.NamedViews()
                    if viewName in namedViews:
                        validViews.append(rs.RestoreNamedView(viewName))
                    else:
                        warning = viewName + " is not a valid Rhino view name in this document."
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning) 
                    # change back to Grasshopper
                    sc.doc = ghdoc
                    viewName = rs.CurrentView(viewName, True)
            
        self.RhinoViewsName = validViews
        
        if self.RhinoViewsName!=[]:
            self.runAnnualGlare = True
            
        if adaptiveZone == None: adaptiveZone = False
        self.adaptiveZone = adaptiveZone
        
        if not dgp_imageSize: dgp_imageSize = 250
        self.dgp_imageSize = dgp_imageSize
        
        if dynamicSHDGroup_1 == None and dynamicSHDGroup_2==None:
            
            class dynamicSHDRecipe(object):
                def __init__(self, type = 1, name = "no_blind"):
                    self.type = type
                    self.name = name
            
            self.DShdR = [dynamicSHDRecipe(type = 1, name = "no_blind")]
            
        else:
            self.DShdR = []
            shadingGroupNames = []
            if dynamicSHDGroup_1 != None:
                self.DShdR.append(dynamicSHDGroup_1)
                shadingGroupNames.append(dynamicSHDGroup_1.name)
            if dynamicSHDGroup_2 != None:
                self.DShdR.append(dynamicSHDGroup_2)
                shadingGroupNames.append(dynamicSHDGroup_2.name)
            
            if len(shadingGroupNames) ==2 and shadingGroupNames[0] == shadingGroupNames[1]:
                msg = "Shading group names cannot be the same. Change the names and try again."
        
        # Number of ill files
        self.numOfIll = 1
        for shadingRecipe in self.DShdR:
            if shadingRecipe.name == "no_blind":
                pass
            elif shadingRecipe.name == "conceptual_dynamic_shading":
                self.numOfIll += 1
            else:
                # advanced dynamic shading
                self.numOfIll += len(shadingRecipe.shadingStates) - 1
        
        print "number of ill files = " + str(self.numOfIll)
    
    def __repr__(self):
        return "Honeybee.DaysimParameters"



def main(outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize, onlyRunGlareAnalysis = True):
    msg = None
    
    # make sure shading groups don't have similar names
    try:
        if dynamicSHDGroup_1.name == dynamicSHDGroup_2.name:
            msg = "Shading group names cannot be identical. Change one of the names and try again."
            return msg, None
    except:
        pass
    
    # make sure that shading groups are both advanced and not conceptual
    try:
        if dynamicSHDGroup_1.type * dynamicSHDGroup_2.type == 0:
            msg = "The only valid combination of multiple shading groups is two advanced dynamic shadings."
            return msg, None
    except:
        pass            
        
    DSParameters = SetDSParameters(outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize, onlyRunGlareAnalysis)
    
    return msg, DSParameters



_adaptiveZone_ = False
msg, DSParameters = main(_outputUnits_, dynamicSHDGroup_1_,  dynamicSHDGroup_2_, _RhinoViewsName, _adaptiveZone_, _dgp_imageSize_, onlyRunGlareAnalysis_)

if msg != None:
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)                

