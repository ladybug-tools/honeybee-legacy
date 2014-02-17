# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analyses Recipe for Annual Daylight Simulation with Daysim
-
Provided by Honeybee 0.0.50
    
    Args:
        outputUnits: A list of numbers to indicate output units for test points. Defualt is 2. [0] visible irradiance(W/m2), [1] solar irradiance (W/m2), [2] illumiance (lux)
        dynamicShadingGroup_1: Use conceptual or advanced shading recipeis to define the dynamic shading. Leave it disconnected if you don't have any dynamic shading in the model
        dynamicShadingGroup_2: Use conceptual or advanced shading recipeis to define the dynamic shading. Leave it disconnected if you don't have any dynamic shading in the model
        ............................................: Graphical separator! Leave it empty. Thanks!
        RhinoViewsName: List of view names that you want to be considered for annual glare analysis. Be aware that annual glare analysis with Daysim can take hours to days!
        adaptiveZone: Set the Boolean to True if the user can adapt his/her view within the space. "The concept is based on the hypothesis that if a user is free to look in different directions or place him or herself in different positions within a space, he or she is going to pick the most comfortable one." Read more here > http://daysim.ning.com/page/daysim-header-file-deyword-adaptive-zone
        dgp_imageSize: The size of the image to be used for daylight glare probability in pixels. Defult value is 250 px.
"""

ghenv.Component.Name = "Honeybee_DSParameters"
ghenv.Component.NickName = 'DSParameters'
ghenv.Component.Message = 'VER 0.0.50\nFEB_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


import Grasshopper.Kernel as gh

class SetDSParameters:
    
    def __init__(self, outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize):
        
        if len(outputUnits)!=0 and outputUnits[0]!=None: self.outputUnits = outputUnits
        else: self.outputUnits = [2]
        
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



def main(outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize):
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
        
    DSParameters = SetDSParameters(outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize)
    
    return msg, DSParameters




msg, DSParameters = main(outputUnits, dynamicSHDGroup_1,  dynamicSHDGroup_2, RhinoViewsName, adaptiveZone, dgp_imageSize)
if len(RhinoViewsName)!= 0:
    
    warnMsg = "View based glare analysis hasn't been implemented yet!\nWill be implemented soon. =)"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warnMsg)                
    
if msg != None:
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, msg)                

