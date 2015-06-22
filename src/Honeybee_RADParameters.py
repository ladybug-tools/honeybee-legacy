# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Radiance Parameters - Standard
Check here for more details: http://radsite.lbl.gov/radiance/refer/Notes/rpict_options.html
Read more about the parameters at: http://daysim.ning.com/
Here is my favorite presentation by John Mardaljevic: http://radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day1/JM_AmbientCalculation.pdf

-
Provided by Honeybee 0.0.56
    
    Args:
        _quality: 0 > low, 1 > Medium, 2 > High
        _ab_: Number of ambient bounces. "This is the maximum number of diffuse bounces computed by the indirect calculation. A value of zero implies no indirect calculation. "
        _ad_: Number of ambient divisions. "The error in the Monte Carlo calculation of indirect illuminance will be inversely proportional to the square root of this number. A value of zero implies no indirect calculation."
        _as_: Number of ambient super-samples. "Super-samples are applied only to the ambient divisions which show a significant change."
        _ar_: Ambient resolution. "This number will determine the maximum density of ambient values used in interpolation. Error will start to increase on surfaces spaced closer than the scene size divided by the ambient resolution. The maximum ambient value density is the scene size times the ambient accuracy."
        _aa_: Ambient accuracy. "This value will approximately equal the error from indirect illuminance interpolation. A value of zero implies no interpolation"
        additionalP_: Use this input to set other Radiance parameters as needed. You need to follow Radiance's standard syntax (e.g. -ps 1 -lw 0.01)
"""

ghenv.Component.Name = "Honeybee_RADParameters"
ghenv.Component.NickName = 'RADParameters'
ghenv.Component.Message = 'VER 0.0.56\nJUN_22_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

"""
http://radsite.lbl.gov/radiance/refer/Notes/rpict_options.html

Param   Description             Min     Fast    Accur   Max     Notes
=====   ====================    =====   =====   =====   =====   =====
-ps     pixel sampling rate     16      8       4       1
-pt     sampling threshold      1       .15     .05     0
-pj     anti-aliasing jitter    0       .6      .9      1       A
-dj     source jitter           0       0       .7      1       B
-ds     source substructuring   0       .5      .15     .02
-dt     direct thresholding     1       .5      .05     0	    C
-dc     direct certainty        0       .25     .5      1
-dr	    direct relays		    0	    1	    3	    6
-dp	    direct pretest density	32	    64	    512	    0	    C
-sj	    specular jitter		    0	    .3	    .7	    1	    A
-st	    specular threshold	    1	    .85	    .15	    0	    C
-ab	    ambient bounces		    0	    0	    2	    8
-aa	    ambient accuracy	    .5	    .2	    .15	    0	    C
-ar	    ambient resolution	    8	    32	    128	    0	    C
-ad	    ambient divisions	    0	    32	    512	    4096
-as	    ambient super-samples	0	    32	    256	    1024
-lr	    limit reflection	    0	    4	    8	    16
-lw	    limit weight		    .05	    .01	    .002	0	    C
"""

class dictToClass(object):
    def __init__(self, pyDict):
        self.d = pyDict
        

def parseRadParameters(radParString):
    """
    This function parse radiance parameters and returns a dictionary of parameters and values
    """
    
    # I'm pretty sure there is a regX method to do this in one line
    # but for now this should also do it
    
    radPar = {}
    
    if radParString == None: return radPar
    
    #split input string: each part will look like key value (eg ad 1)
    parList = radParString.split("-")
    
    for p in parList:
        key, sep, value = p.partition(" ")
        
        # convert the value to number
        try:
            value = int(value)
        except:
            try:
                value = float(value)
            except:
                continue # cases such as empty string
        
        radPar["_" + key.strip()+ "_"] = value 
    
    return radPar


if sc.sticky.has_key('honeybee_release'):

    hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
    
    
    # there should be a smarter way to read the input values
    componentValues = {
                "_ab_" : _ab_,
                "_ad_" : _ad_,
                "_as_" : _as_,
                "_ar_" : _ar_,
                "_aa_" : _aa_}
    
    
    radParFromString = parseRadParameters(additionalP_)
    
    # replace/add new parameters to componentValues
    
    for key, value in radParFromString.items():
        componentValues[key] = value
    
    radPar = {}
    
    for key in hb_radParDict.keys():
        
        par = key.replace("_", "") # remove _ doe a cleaner print
        
        if componentValues.has_key(key) and componentValues[key]!= None:
            print par + " = " + str(componentValues[key])
            radPar[key] = componentValues[key]
        else:
            print par + " = " + str(hb_radParDict[key][_quality])
            radPar[key] = hb_radParDict[key][_quality]
    
    radParameters = dictToClass(radPar)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    radParameters = []
