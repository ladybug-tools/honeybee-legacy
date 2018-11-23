#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com.com> 
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
Use this component to create a custon radiant environment for THERM boundary condition.  Assigning values here will create radiant conditions that are different from normal NFRC conditions (where radiant temperature equals air temperature, the emissivity of the environment is assumed to be 1, and viewFactor between the boundary and the envrionment is calculated using the geometry of the boundary).
-
Provided by Honeybee 0.0.64

    Args:
        radiantTemp_: A value in degrees Celcius that represents the radiant temperature of the environment.  If no value is plugged in here, the radiant environment will be assumed to have the same temperature as the air.
        envEmissivity_: A value between 0 and 1 that represents the emissivity of the environment. Use this ti account for environments made of atypical materials like metals. If no value is plugged in here, it will be assumed that the envrionment has an emissivity of 1.
        viewFactor_: An optional value between 0 and 1 that sets the view factor of the boundary to the surrounding exterior/interior environment.
        _
        Alternatively, you can simply input the word 'auto' and the view factor will be calculated using THERM's 'Automatic Enclosure' model, which will check the geometry of the boundary condition to see if the boundary is concave (meaning that the boundary blocks some of the view of itself to the environment).
        _
        If a view factor number is connected here, THERM's 'Blackbody Radiation' model will be used and the view factor specified will determine the radiative heat transfer.  A view factor of 1 implies that all edges of the boundary can see 100% of the exterior environment.
        _
        If this is left blank, the 'Automatic Enclosure' model will be used any time an indoor film coefficient is specified (< 10 W/m2K).  A 'Blackbody Radiation' model with a view factor of 1 will be used for all outdoor film coefficients (> 10 W/m2K).  These default boundary conditions assume compliance with the NFRC standard.
        heatFlux_: An optional numerical value in W/m2 that represents additional energy flux across the boundary condition. You can use this to account for solar flux across the exterior boundary condition.
    Returns:
        customRadEnv: A list of radiant environmental properties that can be plugged into the 'Honeybee_Create Therm Boundaries' component in order to run a THERM simulation with a atypical radiant environment.
"""

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid
import decimal

ghenv.Component.Name = 'Honeybee_Custom Radiant Environment'
ghenv.Component.NickName = 'customRadEnv'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "11 | THERM"
#compatibleHBVersion = VER 0.0.56\nMAY_26_2017
#compatibleLBVersion = VER 0.0.59\nNOV_07_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



def main(radTemp, emissivity, viewFactor, heatFlux):
    #Check to be sure that any emissivity values make sense.
    if emissivity != None:
        if emissivity > 1 or emissivity < 0:
            warning = "envEmissivity_ must be between 0 and 1"
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    
    #Check to be sure that any emissivity values make sense.
    if viewFactor != None:
        if viewFactor.lower() == 'auto':
            viewFactor = 'auto'
        else:
            try:
                viewFactor = float(viewFactor)
                if viewFactor > 1 or viewFactor < 0:
                    warning = "viewFactor_ must be between 0 and 1"
                    print warning
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
                    return -1
            except:
                warning = "viewFactor_ input is not valid."
                print warning
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                return -1
    
    return radTemp, emissivity, viewFactor, heatFlux


result = main(radiantTemp_, envEmissivity_, viewFactor_, heatFlux_)
if result != -1:
    customRadEnv = result