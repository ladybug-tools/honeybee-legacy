"""
Radiance Parameters - Standard
-
Provided by Honybee 0.0.10
    
    Args:
        _quality: 0 > low, 1 > Medium, 2 > High
        _ab_: Number of ambient bounces. This is the maximum number of diffuse bounces computed by the indirect calculation. A value of zero implies no indirect calculation. 
        _as_: Number of ambient super-samples. Super-samples are applied only to the ambient divisions which show a significant change.

"""

ghenv.Component.Name = "Honeybee_RADParameters"
ghenv.Component.NickName = 'RADParameters'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "3 | Daylight | Recipes"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc
#low Quality =       -ps 8 -pt .15 -pj .6 -dj 0  -ds .5  -dt .5  -dc .25 -dr 0 -dp 64  -st .85 -ab 2 -aa .25 -ar 16  -ad 512  -as 128  -lr 4 -lw .05  -av 0 0 0
#medium =     -ps 4 -pt .10 -pj .9 -dj .5 -ds .25 -dt .25 -dc .5  -dr 1 -dp 256 -st .5  -ab 3 -aa .2  -ar 64  -ad 2048 -as 1024 -lr 6 -lw .01  -av 0 0 0
#high Quality = -ps 2 -pt .05 -pj .9 -dj .7 -ds .15 -dt .05 -dc .75 -dr 3 -dp 512 -st .15 -ab 4 -aa .1  -ar 128 -ad 4096 -as 1024 -lr 8 -lw .005 -av 0 0 0

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