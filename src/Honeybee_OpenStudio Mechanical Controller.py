#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chien Si Harriman <charriman@terabuild.com> 
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
Mechanical Ventilation Controller
This is an optional field that overrides the economizer behavior
It adds DCV if you want it as well.
It can also be tricked into providing a mini purge cycle too if you want it.
-
Provided by Honeybee 0.0.59

    Args:
        _uniqueName : a required field to uniquely name the economizer
        _availabilitySch_ : provide the name (string) of a Honeybee schedule that is valid.  Supply nothing, and outside air will be delivered always, which is probably not what you want.
        _DCV_ : provide a toggle here.  1 means you want DCV, 0 means you don't.  The default is zero.
    Returns:
        MechanicalVentController:...returns a controller that can be added to the Airside Economizer Definition
"""

ghenv.Component.Name = "Honeybee_OpenStudio Mechanical Controller"
ghenv.Component.NickName = 'MechVentController'
ghenv.Component.Message = 'VER 0.0.59\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import Grasshopper.Kernel as gh
import pprint

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

dcvDict = {
0:False,
1:True
}

def main(uniqueName,availabilitySch,DCV):
    if availabilitySch == None:
        availabilitySch = "ALWAYS ON"
    if sc.sticky.has_key('honeybee_release'):
        mvCtrl={}
        if (_uniqueName==None):
            print 'A unique name must be provided.'
            msg = "A unique name must be provided."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            return None
        else:
            if isinstance(uniqueName,str):
                mvCtrl['name'] = uniqueName
            else:
                print 'The uniqueName input must be a string.'
                msg = "The uniqueName input must be a string."
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                return None
            if availabilitySch != None:
                if isinstance(availabilitySch,str):
                    mvCtrl['availSch'] = availabilitySch
                else:
                    print 'The availabilitySch input must be a string.'
                    msg = "The availabilitySch input must be a string."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return None
            if DCV != None:
                if isinstance(DCV,int):
                    if (DCV < 2):
                        mvCtrl['DCV'] =  dcvDict[DCV]
                    else:
                        print 'The DCV input must be an integer with value of 0 or 1.'
                        msg = "The DCV input must be an integer with value of 0 or 1."
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        return None
                else:
                    print 'The DCV input must be an integer.'
                    msg = "The DCV input must be an integer."
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    return None
            mvCtrl = dictToClass(mvCtrl)
            return mvCtrl
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
        airsideEconomizerParameters = []
MechanicalVentController = main(_uniqueName,_availabilitySch,_DCV_)
pp = pprint.PrettyPrinter(indent=4)
print "MechVentController definition:"
if MechanicalVentController != None:
    pp.pprint(MechanicalVentController.d)
else:
    print MechanicalVentController
