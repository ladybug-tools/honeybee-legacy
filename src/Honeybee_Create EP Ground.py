#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to change the properties of a zone to refelct those of a ground.  This is particularly useful for setting up outdoor thermal comfort maps when you want the surface temperature of the ground to be caclated with some spatial diversity, reflecting the shadows that other objects cast upon it and the storage of heat in the ground surface.
_
The turning of a zone into a ground zone entails...
1) Setting all constructions to be indicative of a certain soil type (see the _soilTypeOrMat description for more information).
2) Setting all surfaces except the roof to have the boundary condition of 'ground', including no sun or wind exposure for these surfaces.
3) Getting rid of all loads and schedules within the zone.
_
All values for soil type are taken from the Engineering Toolbox, specifically these pages below...
Soil Conductivity - http://www.engineeringtoolbox.com/thermal-conductivity-d_429.html
Soil Density - http://www.engineeringtoolbox.com/dirt-mud-densities-d_1727.html
Soil Heat Capacity - http://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: HBZones to be turned into ground zones, representative of soil.
        _soilTypeOrMat: Either a material definition output from the 'Honeybee_EnergyPlus Opaque Material' component, the name of a material already in the library, or an integer from 0 to 6 representing the following:
            0 - Dry sand
            1 - Semi-dry sand or dust
            2 - Moits soil
            3 - Mud or soil saturated with water
            4 - Concrete
            5 - Asphalt
            6 - Solid rock or granite
    Returns:
        HBGrndZones: HBZones that have had their properties altered to be ground conditions.
"""

ghenv.Component.Name = "Honeybee_Create EP Ground"
ghenv.Component.NickName = 'createEPGround'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "08 | Energy | Set Zone Properties"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import uuid
import Grasshopper.Kernel as gh
import os


soilTypeDict = {
    
0: "Material,\nDRYSANDFORGROUND,    !Name\nRough,    !Roughness\n0.2,    !Thickness {m}\n0.33,    !Conductivity {W/m-K}\n1555,    !Density {kg/m3}\n800,    !Specific Heat {J/kg-K}\n0.85,    !Thermal Absorptance\n0.65,    !Solar Absorptance\n0.65;    !Visible Absorptance",
1: "Material,\nDRYDUSTFORGROUND,    !Name\nRough,    !Roughness\n0.2,    !Thickness {m}\n0.5,    !Conductivity {W/m-K}\n1600,    !Density {kg/m3}\n1026,    !Specific Heat {J/kg-K}\n0.9,    !Thermal Absorptance\n0.7,    !Solar Absorptance\n0.7;    !Visible Absorptance",
2: "Material,\nMOISTSOILFORGROUND,    !Name\nRough,    !Roughness\n0.2,    !Thickness {m}\n1.0,    !Conductivity {W/m-K}\n1250,    !Density {kg/m3}\n1252,    !Specific Heat {J/kg-K}\n0.92,    !Thermal Absorptance\n0.75,    !Solar Absorptance\n0.75;    !Visible Absorptance",
3: "Material,\nMUDFORGROUND,    !Name\nMediumRough,    !Roughness\n0.2,    !Thickness {m}\n1.4,    !Conductivity {W/m-K}\n1840,    !Density {kg/m3}\n1480,    !Specific Heat {J/kg-K}\n0.95,    !Thermal Absorptance\n0.8,    !Solar Absorptance\n0.8;    !Visible Absorptance",
4: "Material,\nCONCRETEFORGROUND,    !Name\nMediumRough,    !Roughness\n0.2,    !Thickness {m}\n1.73,    !Conductivity {W/m-K}\n2243,    !Density {kg/m3}\n837,    !Specific Heat {J/kg-K}\n0.9,    !Thermal Absorptance\n0.65,    !Solar Absorptance\n0.65;    !Visible Absorptance",
5: "Material,\nASPHALTFORGROUND,    !Name\nMediumRough,    !Roughness\n0.2,    !Thickness {m}\n0.75,    !Conductivity {W/m-K}\n2360,    !Density {kg/m3}\n920,    !Specific Heat {J/kg-K}\n0.93,    !Thermal Absorptance\n0.87,    !Solar Absorptance\n0.87;    !Visible Absorptance",
6: "Material,\nSOLIDROCKFORGROUND,    !Name\nMediumRough,    !Roughness\n0.2,    !Thickness {m}\n3.0,    !Conductivity {W/m-K}\n2700,    !Density {kg/m3}\n790,    !Specific Heat {J/kg-K}\n0.96,    !Thermal Absorptance\n0.55,    !Solar Absorptance\n0.55;    !Visible Absorptance"
}

def main(HBZones):
    # check for Honeybee
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
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
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Figure out what the material of the soil should be.
    hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    soilCheck = True
    try:
        soilMaterialIndex = int(_soilTypeOrMat)
        if soilMaterialIndex >= 0 or soilMaterialIndex <=6:
            soilMaterial = soilTypeDict[soilMaterialIndex]
            #Turn the soil material into a construction.
            added, materialName = hb_EPMaterialAUX.addEPConstructionToLib(soilMaterial, overwrite = True)
            materialName = materialName.upper()
            constructionStr = "Construction,\n" + materialName + "Cnstr" + ",    !- Name\n"
            constructionStr += materialName + ";    !- Layer 1" + "\n"
            constructionStr += materialName + ";    !- Layer 2" + "\n"
            constructionStr += materialName + ";    !- Layer 3" + "\n"
        else:
            soilCheck = False
            warning = '_soilTypeOrMat must be either an integer between 0 and 6 or a material from the "Honeybee_EnergyPlus Opaque Material" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    except:
        if _soilTypeOrMat != None and len(_soilTypeOrMat.split("\n")) == 1:
            materialName = _soilTypeOrMat.upper()
        elif _soilTypeOrMat!=None:
            # it is a full string
            added, materialName = hb_EPMaterialAUX.addEPConstructionToLib(_soilTypeOrMat, overwrite = True)
            materialName = materialName.upper()
        if materialName in sc.sticky ["honeybee_materialLib"].keys():
            constructionStr = "Construction,\n" + materialName + "Cnstr" + ",    !- Name\n"
            constructionStr += materialName + ";    !- Layer 1" + "\n"
            constructionStr += materialName + ";    !- Layer 2" + "\n"
            constructionStr += materialName + ";    !- Layer 3" + "\n"
        else:
            soilCheck = False
            warning = '_soilTypeOrMat must be either an integer between 0 and 6 or a material from the "Honeybee_EnergyPlus Opaque Material" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    if soilCheck == True:
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        HBObjectsFromHive = hb_hive.callFromHoneybeeHive(HBZones)
        
        schedules = []
        for zoneCount, HBZone in enumerate(HBObjectsFromHive):
            
            # add Ground to name        
            if "ground" not in HBZone.name.lower():
                HBZone.name = "Ground " + HBZone.name 
            
            # change loads to 0
            if not HBZone.isLoadsAssigned:
                HBZone.assignLoadsBasedOnProgram(ghenv.Component)
            
            HBZone.equipmentLoadPerArea = 0
            HBZone.infiltrationRatePerArea = 0
            HBZone.lightingDensityPerArea = 0
            HBZone.numOfPeoplePerArea = 0
            HBZone.ventilationPerArea = 0
            HBZone.ventilationPerPerson = 0
            
            # This is for EP component to the area won't be included in the total area
            HBZone.isPlenum = True
            
            #Alter the properties of the surfaces.
            for srf in HBZone.surfaces:
                #Change the surface to have the construction of the soil type.
                hb_EPObjectsAux.assignEPConstruction(srf, constructionStr, ghenv.Component)
                
                #If the surface is not a roof, change the boundary condition to be ground and the wind/sun exposure to be none.
                if srf.type == 1 or srf.type == 1.5:
                    if srf.BC.upper() != 'SURFACE':
                        srf.setBC('Outdoors', isUserInput= True)
                        srf.setType(1, isUserInput= True)
                        srf.setSunExposure('SunExposed')
                        srf.setWindExposure('WindExposed')
                else:
                    srf.setBC('ground', isUserInput= True)
                    srf.setType(int(srf.type) + 0.5, isUserInput= True)
                    srf.setSunExposure('NoSun')
                    srf.setWindExposure('NoWind')
            
            
        HBZones  = hb_hive.addToHoneybeeHive(HBObjectsFromHive, ghenv.Component)
        
        return HBZones
    else:
        return -1

if _HBZones != [] and _HBZones[0] != None and _soilTypeOrMat != [] and _soilTypeOrMat != None:
    results = main(_HBZones)
    
    if results != -1: HBGrndZones = results