# This component assigns internal masses to zones
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to assign internal thermal masses to zones, which can be used to account for the effects of furniture inside zones or massive building components like hearths and chimneys.
_
The component accepts either surfaces of Rhino geometry (representing furniture or building elements) or a numerical value of the mass's surface area.  Several of these components can be used in a series to descibe internal masses (or furniture) made of different materials).
_
Note that internal masses assigned this way cannot "see" solar radiation that may potentially hit them and, as such, caution should be taken when using this component with internal mass objects that are not always in shade.
Masses are only factored into the the thermal calculations of the zone by undergoing heat transfer with the indoor air.
-
Provided by Honeybee 0.0.60

    Args:
        _HBZones: HBZones for which internal masses are to be assigned.
        internalMassName_: An optional text name for the internal mass.  This can be useful for keeping track of different internal mass types if you use several of this component in series.
        _srfsOrSrfArea: A list of Rhino breps representing the surfaces of internal masses (or furniture) that are exposed to the air of the zone.  Alternatively, this can be a number or list of numbers representing the surface area of the internal masses (or furniture) that are exposed to the zone air.
            _
            In the case of breps representing the surfaces of internal masses, this component is smart enough to know which zone the surfaces are in.  However, all surfaces must lie COMPLETELY inside a single zone and cannot span between zones or span outside the building.  If you have an object that lies between two zones, please split it in two along the boundary between the zones.
            _
            In the case of numbers representing the the surface area of the internal masses, inputs can be either a single number (which will be used to put internal masses into all zones using the specified surface area), or it can be a list of numbers that matches the input zones, which can be used to assign different levels of mass surface area to different zones.
        _EPConstruction: An EnergyPlus Construction that represents the type of material that the thermal mass is composed of.  This can be either a construction from the "Call from EP Construction Library" component or a custom construction from the "EnergyPlus Construction" component.
    Returns:
        HBZones: HBZones with internal masses assigned.
"""

ghenv.Component.Name = "Honeybee_Add Internal Mass to Zone"
ghenv.Component.NickName = 'addInternalMass'
ghenv.Component.Message = 'VER 0.0.60\nNOV_04_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import uuid
import Rhino as rc
import rhinoscriptsyntax as rs

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    #Call the necessary HB functions from the hive.
    hb_hive = sc.sticky["honeybee_Hive"]()
    hb_EPObjectsAux = sc.sticky["honeybee_EPObjectsAUX"]()
    
    #Have a function to duplicate data.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #Create lists to be filled.
    srfAreas = []
    
    #Check to see if the input in the _srfsOrSrfArea is a number of geometry.
    checkData1 = False
    try:
        #Object is a surface area number.
        srfArea = float(_srfsOrSrfArea[0])
        srfMethod = 1
        
        #Number is a single value to applied to all connected zones.
        if len(_srfsOrSrfArea) == 1:
            srfAreas = duplicateData([float(_srfsOrSrfArea[0])], len(_HBZones))
            checkData1 = True
        #Number is list of numbers that match the connected zones.
        elif len(_srfsOrSrfArea) == len(_HBZones):
            srfMethod = 0
            for item in _srfsOrSrfArea:
                srfAreas.append(float(item))
            checkData1 = True
        else:
            warning = "Numerical inputs for _srfsOrSrfArea must be either a list that matches the number of HBZones or a single value to be applied to all HBZones."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    except:
        try:
            #Object is a set of surfaces.
            srfBreps = []
            srfVerts = []
            for item in _srfsOrSrfArea:
                srfBrep = [rs.coercegeometry(srfBrep) for srfBrep in [item]][0]
                srfVert = srfBrep.DuplicateVertices()
                srfBreps.append(srfBrep)
                srfVerts.append(srfVert)
            
            checkData1 = True
            
            #Create a list to hold the total surface areas inside each zone.
            brepZoneCount = []
            for zone in _HBZones:
                brepZoneCount.append(0)
                srfAreas.append(0)
            
            #Test to see if any of the breps lie completely inside a zone.
            for count, brep in enumerate(srfBreps):
                brepZoneCounter = brepZoneCount[:]
                for zoneCount, zone in enumerate(_HBZones):
                    for vertex in srfVerts[count]:
                        if zone.IsPointInside(rc.Geometry.Point3d(vertex), tol, False):
                            brepZoneCounter[zoneCount] += 1
                    if brepZoneCounter[zoneCount] == len(srfVerts[count]):
                        #The surface is completely inside the zone.
                        area = rc.Geometry.AreaMassProperties.Compute(brep).Area
                        srfAreas[zoneCount] += area
                
                #Give a warning if a surface was not found to lie completely inside any zone.
                if len(srfVerts[count]) not in brepZoneCounter:
                    checkData1 = False
                    warning = "One of the surfaces input to _srfsOrSrfArea does not lie completely in a single HBZone. \n All surfaces must lie COMPLETELY inside a single zone and cannot span between zones or span outside the building. \n If you have an object that lies between two zones, please split it in two along the boundary between the zones."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
        except:
            warning = "Input for _srfsOrSrfArea is invalid."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to be sure that the EPConstruction is in the library or can be added to the library.
    checkData2 = True
    # if it is just the name of the material make sure it is already defined
    if len(_EPConstruction.split("\n")) == 1:
        # if the material is not in the library add it to the library
        if not hb_EPObjectsAux.isEPConstruction(_EPConstruction):
            warningMsg = "Can't find " + _EPConstruction + " in EP Construction Library.\n" + \
                        "Add the construction to the library and try again."
            print warningMsg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warningMsg)
            checkData2 = False
        else:
            EPConstruction = _EPConstruction
    else:
        # It is a full string
        added, EPConstruction = hb_EPObjectsAux.addEPObjectToLib(_EPConstruction, overwrite = True)
        
        if not added:
            msg = _EPConstruction + " is not added to the project library!"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            print msg
            checkData2 = False
    
    #Check to be sure that the HBZones are valid HBZones.
    checkData3 = True
    try:
        HBZones = hb_hive.callFromHoneybeeHive(_HBZones)
    except:
        HBZones = []
        checkData3 = False
        warning = "Connected _HBZones are not valid."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check to see if there is an internalMassName_ attached.
    massNames = []
    if internalMassName_ != None:
        for zone in HBZones:
            massName = zone.name + "-" + internalMassName_
            massNames.append(massName)
    else:
        for zone in HBZones:
            massName = zone.name + "-" + "Mass" + str(len(zone.internalMassNames))
            massNames.append(massName)
    
    #Check to be sure that everything is ok.
    if checkData1 == True and checkData2 == True and checkData3 == True:
        checkData = True
    else: checkData = False
    
    
    return checkData, HBZones, srfAreas, EPConstruction, massNames


def main(HBZones, srfAreas, EPConstruction, massNames):
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    
    # assign the values
    for zoneCount, zone in enumerate(HBZones):
        if srfAreas[zoneCount] != 0:
            zone.internalMassNames.append(massNames[zoneCount])
            zone.internalMassSrfAreas.append(srfAreas[zoneCount])
            zone.internalMassConstructions.append(EPConstruction)
            message = zone.name + " has been assigned an internal mass with an area of (" + str(round(srfAreas[zoneCount],2)) + " Square " + str(sc.doc.ModelUnitSystem) + ") and a construction of " + str(EPConstruction)
            print message
    
    # send the zones back to the hive
    HZonesFinal  = hb_hive.addToHoneybeeHive(HBZones, ghenv.Component)
    
    return HZonesFinal




#If Honeybee is not flying, give a warning.
initCheck = False
if sc.sticky.has_key('honeybee_release') == True:
    initCheck = True
else:
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")


#Run the Component
checkData = False
if _HBZones != [] and _srfsOrSrfArea != [] and _EPConstruction != None and initCheck == True:
    if _HBZones[0] != None:
        checkData, HBZonesFromHive, srfAreas, EPConstruction, massNames = checkTheInputs()
        
        if checkData == True:
            zones = main(HBZonesFromHive, srfAreas, EPConstruction, massNames)
            
            if zones!=-1:
                HBZones = zones




