# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Export Honeybee Objects to OpenStudio
-
Provided by Honeybee 0.0.53
    
    Args:
        openStudioLibFolder:
    Returns:
        readMe!: ...
"""

# check for libraries
# default is C:\\Ladybug\\OpenStudio

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
    
    
ghenv.Component.Name = "Honeybee_Get Annual SQL Data"
ghenv.Component.NickName = 'getAnnualSQLData'
ghenv.Component.Message = 'VER 0.0.55\nNOV_2_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict

def checkVals(dictionary,totaltag):
    subtotal=0.0
    storedtotal=0.0
    for key in sorted(dictionary.keys()):
        if (key!=totaltag): 
            if (type(dictionary[key]) is float):
                subtotal += dictionary[key]
        else: storedtotal = dictionary[key]
    if (subtotal==storedtotal):
        return "PASS"
    else:
        return "FAIL"
#ops.
#sqlPath = r'C:\Users\Administrator\Downloads\eplusout.sql'
pp = pprint.PrettyPrinter(indent=4)
sqlPath = _sqlFilePath
sqlFile = ops.SqlFile(ops.Path(sqlPath))
conversionFactorElec = float(str(ops.OptionalDouble(277.777778)))
outputs={}
electricity={
'units':'kilowatt-hours',
'Electricity Interior Lights':float(str(sqlFile.electricityInteriorLighting())) * conversionFactorElec,
'Electricity Exterior Lights':float(str(sqlFile.electricityExteriorLighting())) * conversionFactorElec,
'Electricity Interior Equipment':float(str(sqlFile.electricityInteriorEquipment())) * conversionFactorElec,
'Electricity Exterior Equipment':float(str(sqlFile.electricityExteriorEquipment())) * conversionFactorElec,
'Electricity Heating':float(str(sqlFile.electricityHeating())) * conversionFactorElec,
'Electricity Water Systems':float(str(sqlFile.electricityWaterSystems())) * conversionFactorElec,
'Electricity Cooling':float(str(sqlFile.electricityCooling())) * conversionFactorElec,
'Electricity Humidification':float(str(sqlFile.electricityHumidification())) * conversionFactorElec,
'Electricity Heat Recovery':float(str(sqlFile.electricityHeatRecovery())) * conversionFactorElec,
'Electricity Heat Rejection':float(str(sqlFile.electricityHeatRejection())) * conversionFactorElec,
'Electricity Refrigeration':float(str(sqlFile.electricityRefrigeration())) * conversionFactorElec,
'Electricity Generators':float(str(sqlFile.electricityGenerators())) * conversionFactorElec,
'Fan Electricity':float(str(sqlFile.electricityFans())) * conversionFactorElec,
'Pumps Electricity':float(str(sqlFile.electricityPumps())) * conversionFactorElec,
'Electricity Total End Uses':float(str(sqlFile.electricityTotalEndUses())) * conversionFactorElec
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
outputs['elec']=electricity
outputs['ng']=naturalgas
pp.pprint(outputs)
print "GJ to kWy Conversion Factor: " + str(conversionFactorElec)
print "GH to therms Conversion Factor: " + str(conversionFactorNG)
retval = checkVals(outputs['elec'],'Electricity Total End Uses')
print "Electricty test: " + retval
retval = checkVals(outputs['ng'],'Natural Gas Total End Uses')
print "Natural gas test: " + retval

allAnnualTotals = dictToClass(outputs)
annualElectricity = dictToClass(outputs['elec'])
annualNaturalgas = dictToClass(outputs['ng'])