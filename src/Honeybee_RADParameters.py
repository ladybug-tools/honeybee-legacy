"""
Radiance Parameters - Standard
Check here for more details: http://radsite.lbl.gov/radiance/refer/Notes/rpict_options.html
Read more about the parameters at: http://daysim.ning.com/
Here is my favorite presentation by John Mardaljevic: http://radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day1/JM_AmbientCalculation.pdf

-
Provided by Honybee 0.0.50
    
    Args:
        _quality: 0 > low, 1 > Medium, 2 > High
        _ab_: Number of ambient bounces. "This is the maximum number of diffuse bounces computed by the indirect calculation. A value of zero implies no indirect calculation. "
        _ad_: Number of ambient divisions. "The error in the Monte Carlo calculation of indirect illuminance will be inversely proportional to the square root of this number. A value of zero implies no indirect calculation."
        _as_: Number of ambient super-samples. "Super-samples are applied only to the ambient divisions which show a significant change."
        _ar_: Ambient resolution. "This number will determine the maximum density of ambient values used in interpolation. Error will start to increase on surfaces spaced closer than the scene size divided by the ambient resolution. The maximum ambient value density is the scene size times the ambient accuracy."
        _aa_: Ambient accuracy. "This value will approximately equal the error from indirect illuminance interpolation. A value of zero implies no interpolation"

"""

ghenv.Component.Name = "Honeybee_RADParameters"
ghenv.Component.NickName = 'RADParameters'
ghenv.Component.Message = 'VER 0.0.45\nFEB_10_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

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
        
if sc.sticky.has_key('honeybee_release'):
    hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
    
    # there should be a smarter way to read the input values
    componentValues = {
                "_ab_" : _ab_,
                "_ad_" : _ad_,
                "_as_" : _as_,
                "_ar_" : _ar_,
                "_aa_" : _aa_}
    
    radPar = {}
    for key in hb_radParDict.keys():
        if componentValues.has_key(key) and componentValues[key]!= None:
            print key + " is set to " + str(componentValues[key])
            radPar[key] = componentValues[key]
        else:
            print key + " is set to " + str(hb_radParDict[key][_quality])
            radPar[key] = hb_radParDict[key][_quality]
    
    radParameters = dictToClass(radPar)
else:
    print "You should first let Honeybee to fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    radParameters = []