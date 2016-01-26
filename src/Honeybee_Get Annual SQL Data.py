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
Export Honeybee Objects to OpenStudio
-
Provided by Honeybee 0.0.59
    
    Args:
        openStudioLibFolder:
    Returns:
        readMe!: ...
"""

# check for libraries
# default is C:\\Ladybug\\OpenStudio


ghenv.Component.Name = "Honeybee_Get Annual SQL Data"
ghenv.Component.NickName = 'getAnnualSQLData'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "13 | WIP"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import os
import System
import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh
import time
import pprint

if sc.sticky.has_key('honeybee_release'):
    
    openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
    
    if os.path.isdir(openStudioLibFolder) and os.path.isfile(os.path.join(openStudioLibFolder, "openStudio.dll")):
        # openstudio is there
        # I need to add a function to check the version and compare with available version
        openStudioIsReady = True
        import clr
        clr.AddReferenceToFileAndPath(openStudioLibFolder+"\\openStudio.dll")
    
        import sys
        if openStudioLibFolder not in sys.path:
            sys.path.append(openStudioLibFolder)
    
        import OpenStudio as ops
    else:
        openStudioIsReady = False
        # let the user know that they need to download OpenStudio libraries
        msg = "Cannot find OpenStudio libraries. You can download the libraries from the link below. " + \
              "Unzip the file and copy it to " + openStudioLibFolder + " and try again. Click on the link to copy the address."
              
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        
        link = "https://app.box.com/s/y2sx16k98g1lfd3r47zi"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, link)
        
        #buttons = System.Windows.Forms.MessageBoxButtons.OK
        #icon = System.Windows.Forms.MessageBoxIcon.Warning
        #up = rc.UI.Dialogs.ShowMessageBox(msg + "\n" + link, "Duplicate Material Name", buttons, icon)
    
    if openStudioIsReady and sc.sticky.has_key('honeybee_release') and \
        sc.sticky.has_key("isNewerOSAvailable") and sc.sticky["isNewerOSAvailable"]:
        # check if there is an update available
        msg = "There is a newer version of OpenStudio libraries available to download! " + \
                      "We strongly recommend you to download the newer version from this link and replace it with current files at " + \
                      openStudioLibFolder +".\n" + \
                      "https://app.box.com/s/y2sx16k98g1lfd3r47zi"
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    openStudioIsReady = False
    
    


class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

class elecSqlVals:

    def __init__(self,sqlFile):
        elecSqlVals.intlighting = str(sqlFile.electricityInteriorLighting())
        elecSqlVals.extlighting = str(sqlFile.electricityExteriorLighting())
        elecSqlVals.intequip = str(sqlFile.electricityInteriorEquipment())
        elecSqlVals.extequip = str(sqlFile.electricityExteriorEquipment())
        elecSqlVals.heating = str(sqlFile.electricityHeating())
        elecSqlVals.watersystems = str(sqlFile.electricityWaterSystems())
        elecSqlVals.cooling = str(sqlFile.electricityCooling())
        elecSqlVals.humidity = str(sqlFile.electricityHumidification())
        elecSqlVals.hr = str(sqlFile.electricityHeatRecovery())
        elecSqlVals.heatrej = str(sqlFile.electricityHeatRejection())
        elecSqlVals.refrig = str(sqlFile.electricityRefrigeration())
        elecSqlVals.generators = str(sqlFile.electricityGenerators())
        elecSqlVals.fans = str(sqlFile.electricityFans())
        elecSqlVals.pumps = str(sqlFile.electricityPumps())
        elecSqlVals.totalenduses = str(sqlFile.electricityTotalEndUses())
    
class waterSqlVals:
    intlighting=None
    extlighting=None
    intequip=None
    extequip=None
    elecHeating=None
    elecWaterSystems=None
    elecCooling=None
    elecHumidity=None
    elecHR=None
    elecHeatRej=None
    elecRefrig=None
    elecGenerators=None
    elecFans=None
    elecPumps=None
    elecTotalEndUses=None
    
    def __init__(self,sqlFile):
        waterSqlVals.intlighting = str(sqlFile.waterInteriorLighting())
        waterSqlVals.extlighting = str(sqlFile.waterExteriorLighting())
        waterSqlVals.intequip = str(sqlFile.waterInteriorEquipment())
        waterSqlVals.extequip = str(sqlFile.waterExteriorEquipment())
        waterSqlVals.heating = str(sqlFile.waterHeating())
        waterSqlVals.watersystems = str(sqlFile.waterWaterSystems())
        waterSqlVals.cooling = str(sqlFile.waterCooling())
        waterSqlVals.humidity = str(sqlFile.waterHumidification())
        waterSqlVals.hr = str(sqlFile.waterHeatRecovery())
        waterSqlVals.heatrej = str(sqlFile.waterHeatRejection())
        waterSqlVals.refrig = str(sqlFile.waterRefrigeration())
        waterSqlVals.generators = str(sqlFile.waterGenerators())
        waterSqlVals.fans = str(sqlFile.waterFans())
        waterSqlVals.pumps = str(sqlFile.waterPumps())
        waterSqlVals.total = str(sqlFile.waterTotalEndUses())
def checkVals(dictionary,totaltag):
    subtotal=0.0
    storedtotal=0.0
    for key in sorted(dictionary.keys()):
        if (key!=totaltag): 
            if (type(dictionary[key]) is float):
                subtotal += dictionary[key]
        else: storedtotal = dictionary[key]
    if (subtotal==storedtotal):
        return "PASS: "+"calculated: "+str(subtotal)+", E+: " + str(storedtotal)
    else:
        return "FAIL: "+"calculated: "+str(subtotal)+", E+: " + str(storedtotal)
#ops.
#sqlPath = r'C:\Users\Administrator\Downloads\eplusout.sql'

def main(sqlPath):
    pp = pprint.PrettyPrinter(indent=4)
    sqlPath = _sqlFilePath
    print sqlPath
    sqlFile = ops.SqlFile(ops.Path(sqlPath))
    print sqlFile
    conversionFactorElec = float(str(ops.OptionalDouble(277.777778)))
    outputs={}
    electricity = {}
    naturalgas={}
    try:
        print 'starting'
        elecVals = elecSqlVals(sqlFile)
        waterVals = waterSqlVals(sqlFile)
        electricity={
        'units':'kilowatt-hours',
        'Electricity Interior Lights':float(elecVals.intlighting) * conversionFactorElec,
        'Electricity Exterior Lights':float(elecVals.extlighting) * conversionFactorElec,
        'Electricity Interior Equipment':float(elecVals.intequip) * conversionFactorElec,
        'Electricity Exterior Equipment':float(elecVals.extequip) * conversionFactorElec,
        'Electricity Heating':float(elecVals.heating) * conversionFactorElec,
        'Electricity Water Systems':float(elecVals.watersystems) * conversionFactorElec,
        'Electricity Cooling':float(elecVals.cooling) * conversionFactorElec,
        'Electricity Humidification':float(elecVals.humidity) * conversionFactorElec,
        'Electricity Heat Recovery':float(elecVals.hr) * conversionFactorElec,
        'Electricity Heat Rejection':float(elecVals.heatrej) * conversionFactorElec,
        'Electricity Refrigeration':float(elecVals.refrig) * conversionFactorElec,
        'Electricity Generators':float(elecVals.generators) * conversionFactorElec,
        'Fan Electricity':float(elecVals.fans) * conversionFactorElec,
        'Pumps Electricity':float(elecVals.pumps) * conversionFactorElec,
        'Electricity Total End Uses':float(elecVals.totalenduses) * conversionFactorElec
        }
        conversionFactorNG = 9.480434
        naturalgas={
        'units':'therms',
        'Natural Gas Heating':float(str(sqlFile.naturalGasHeating())) * conversionFactorNG,
        'Natural Gas Cooling':float(str(sqlFile.naturalGasCooling())) * conversionFactorNG,
        'Natural Gas Interior Lighting':float(str(sqlFile.naturalGasInteriorLighting())) * conversionFactorNG,
        'Natural Gas Exterior Lighting':float(str(sqlFile.naturalGasExteriorLighting())) * conversionFactorNG,
        'Natural Gas Interior Equipment':float(str(sqlFile.naturalGasInteriorEquipment())) * conversionFactorNG,
        'Natural Gas Exterior Equipment':float(str(sqlFile.naturalGasExteriorEquipment())) * conversionFactorNG,
        'Natural Gas Fans':float(str(sqlFile.naturalGasFans())) * conversionFactorNG,
        'Natural Gas Pumps':float(str(sqlFile.naturalGasPumps())) * conversionFactorNG,
        'Natural Gas Heat Rejection':float(str(sqlFile.naturalGasHeatRejection())) * conversionFactorNG,
        'Natural Gas Humidification':float(str(sqlFile.naturalGasHumidification())) * conversionFactorNG,
        'Natural Gas Heat Recovery':float(str(sqlFile.naturalGasHeatRecovery())) * conversionFactorNG,
        'Natural Gas Water Systems':float(str(sqlFile.naturalGasWaterSystems())) * conversionFactorNG,
        'Natural Gas Refrigeration':float(str(sqlFile.naturalGasRefrigeration())) * conversionFactorNG,
        'Natural Gas Generators':float(str(sqlFile.naturalGasGenerators())) * conversionFactorNG,
        'Natural Gas Total End Uses':float(str(sqlFile.naturalGasTotalEndUses())) * conversionFactorNG,
        }
        conversionFactorPropane = 9.480434
        propane={
        'units':'therms',
        #'Propane Heating':float(str(sqlFile.propaneHeating())) * conversionFactorPropane
        }
        conversionFactorWater = 1
        water={
        'units':'m3',
        'Water Interior Lights':float(waterVals.intlighting)* conversionFactorWater,
        'Water Exterior Lights':float(waterVals.extlighting) * conversionFactorWater,
        'Water Interior Equipment':float(waterVals.intequip) * conversionFactorWater,
        'Water Exterior Equipment':float(waterVals.extequip) * conversionFactorWater,
        'Water Heating':float(waterVals.heating) * conversionFactorWater,
        'Water Water Systems':float(waterVals.watersystems) * conversionFactorWater,
        'Water Cooling':float(waterVals.cooling) * conversionFactorWater,
        'Water Humidification':float(waterVals.humidity) * conversionFactorWater,
        'Water Heat Recovery':float(waterVals.hr) * conversionFactorWater,
        'Water Heat Rejection':float(waterVals.heatrej) * conversionFactorWater,
        'Water Refrigeration':float(waterVals.refrig) * conversionFactorWater,
        'Water Generators':float(waterVals.generators) * conversionFactorWater,
        'Fan Water':float(waterVals.fans) * conversionFactorWater,
        'Pumps Water':float(waterVals.pumps) * conversionFactorWater,
        'Water Total End Uses':float(waterVals.total) * conversionFactorWater
        }
        
        outputs['elec']=electricity
        outputs['ng']=naturalgas
        outputs['water']=water
        pp.pprint(outputs)
        print "GJ to kWy Conversion Factor: " + str(conversionFactorElec)
        print "GH to therms Conversion Factor: " + str(conversionFactorNG)
        print "m3 to m3 Conversion Factor: " + str(conversionFactorWater)
        retval = checkVals(outputs['elec'],'Electricity Total End Uses')
        print "Electricty test: " + retval
        retval = checkVals(outputs['ng'],'Natural Gas Total End Uses')
        print "Natural gas test: " + retval
        retval = checkVals(outputs['water'],'Water Total End Uses')
        print "Water test: " + retval
        
        allAnnualTotals = dictToClass(outputs)
        annualElectricity = dictToClass(electricity)
        annualNaturalGas = dictToClass(naturalgas)
        annualWater = dictToClass(water)
        sqlFile.close()
        print "Closing sql file..."
        print "Is Sqlite file still open?", sqlFile.connectionOpen()
        return allAnnualTotals, annualElectricity, annualNaturalGas, annualWater
    except Exception, e:
        print e
    

if _sqlFilePath != None:
    filext = os.path.splitext(_sqlFilePath)[1]
    if (filext == ".sql"):
        allAnnualTotals, annualElectricity, annualNaturalGas, annualWater = main(_sqlFilePath)
    
    else:
        print "You must specify a filepath with a sqlite file extension (.sql).  Please try again."
        allAnnualTotals = dictToClass({}).d
    
