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
Radiance Parameters - Standard
Check here for more details: http://radsite.lbl.gov/radiance/refer/Notes/rpict_options.html
Read more about the parameters at: http://daysim.ning.com/
Here is my favorite presentation by John Mardaljevic: http://radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day1/JM_AmbientCalculation.pdf

-
Provided by Honeybee 0.0.64
    
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
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "03 | Daylight | Recipes"
#compatibleHBVersion = VER 0.0.56\nDEC_12_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

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

class dictToClass:
    def __init__(self, pyDict):
        self.d = pyDict
    
    def __repr__(self):
        return "Honeybee.RadianceParameters"

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
                # case for parameters with no input values -u, -i
                if key.strip()=="":
                    continue
                value = " "
                
        
        radPar["_" + key.strip()+ "_"] = value 

    return radPar


def main():
    
    if sc.sticky.has_key('honeybee_release'):
        # check honeybee version
        try:
                if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
                if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
                
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        hb_radParDict = sc.sticky["honeybee_RADParameters"]().radParDict
        hb_additionalPar = sc.sticky["honeybee_RADParameters"]().additionalRadPars
        
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
        radPar["additional"] = []
        
        for key in hb_radParDict.keys():
            
            par = key.replace("_", "") # remove _ doe a cleaner print
            
            if componentValues.has_key(key) and componentValues[key]!= None:
                print par + " = " + str(componentValues[key])
                radPar[key] = componentValues[key]
            else:
                print par + " = " + str(hb_radParDict[key][_quality])
                radPar[key] = hb_radParDict[key][_quality]
        
        # check additional parameters
        for par in hb_additionalPar:
            if par in radParFromString:
                # add additional parameter
                par  = par.replace("_", "")
                radPar["additional"].append(par)
                print par
        
        return dictToClass(radPar)


results = main()
if results!=-1:
    radParameters = results