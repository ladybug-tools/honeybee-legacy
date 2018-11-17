# Decompose EnergyPlus Construction
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey and Abraham Yezioro <Chris@MackeyArchitecture.com, ayez@ar.technion.ac.il> 
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
Use this component to account for air films in the U-Value and R-Value of any decomposed Honeybee construction or material.
Note that EnergyPlus has its own means of calculating the effects of air films on either side of a construction but, here, we provide an apporximate method based on an input surfaceType_.

-
Provided by Honeybee 0.0.64
    
    Args:
        _uValue_SI: The U-Value_SI out of either the "Honeybee_Decompose EP Construction" or the "Honeybee_Decompose EP Material."
        surfaceType_: An integer value from 0 to 3 that represents one of the following surface types:
                       0 - Exterior Wall/Window
                       1 - Interior Wall/Window
                       2 - Exterior Roof
                       3 - Exposed Interior Floor
    Returns:
        materials: List of materials (from outside to inside)
        comments: Comments for each layer of materials if any
        UValue_SI: U value of the construction in W/m2.K
        UValue_IP: U value of the construction in Btu/hft2F
"""

ghenv.Component.Name = "Honeybee_R-Value With Air Films"
ghenv.Component.NickName = 'RValueAirFilms'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning

def main(_uValue_SI, surfaceType_):
    # Make sure Honeybee is flying
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    try:  
        if surfaceType_ == None or surfaceType_ == 0 or surfaceType_ == 1 or surfaceType_ == 2 or surfaceType_ == 3:
            #Get the value of R-Value added to the air film.
            if surfaceType_ == None:
                addedR = 0.17
                print "Default surface type set to an exterior wall."
            elif surfaceType_ == 0: addedR = 0.17
            elif surfaceType_ == 1: addedR = 0.26
            elif surfaceType_ == 2: addedR = 0.14
            elif surfaceType_ == 3: addedR = 0.21
            
            #Caluculate the new values.
            RValue_SI = 1/_uValue_SI
            newRValue_SI = RValue_SI + addedR
            newUValue_SI = 1/newRValue_SI
            newRValue_IP = newRValue_SI * 5.678263337
            newUValue_IP = 1/newRValue_IP
            
            return newUValue_SI, newUValue_IP, newRValue_SI, newRValue_IP
        else:
            msg = "surfaceType_ must be an integer between 0 and 1."
            ghenv.Component.AddRuntimeMessage(w, msg)
            return -1
    except:
        msg = "Failed to calculate UValue and R-Value with air films."
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    return None
    
    
if _uValue_SI != None:
    data = main(_uValue_SI, surfaceType_)
    
    if data!=-1:
        UValue_SI_wAir, UValue_IP_wAir, RValue_SI_wAir, RValue_IP_wAir = data
