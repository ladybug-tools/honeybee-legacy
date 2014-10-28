# This component creates a material for a pane of glass
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create a custom material for glass, which can be plugged into the "Honeybee_EnergyPlus Construction" component.
_
It is important to note that this component creates a material that represents a single pane of glass, which can be combined with the "Honeybee_EnergyPlus Window Air Gap" to make multi-pane windows.  If you have specifications for a whole window element and not individual panes of glass and gas, you are better-off using the "Honeybee_EnergyPlus Window Material" component
-
Provided by Honeybee 0.0.55
    
    Args:
        _name: A text name for your glass material.
        thickness_: A number that represents the thickness of the pane of glass in meters.  The default is set to 0.003 meters (3 mm).
        solarTransmittance_: A number between 0 and 1 that represents the transmittance of solar radiation through the glass at normal incidence.  The default is set to 0.837, which it typical for clear glass without a low-e coating.
        solarReflectance_: A number between 0 and 1 that represents the reflectance of solar radiation off the glass at normal incidence.  The default is set to 0.075, which is typical for clear glass without a low-e coating.
        visibleTransmittance_: A number between 0 and 1 that represents the transmittance of only visible light through the glass at normal incidence.  This is usally very close to the solarTransmittance_ for non-low-e-coated glass but can differ if the glass has a low-e coating. The default is set to 0.898, which is typical for clear glass without a low-e coating.
        visibleReflectance_: A number between 0 and 1 that represents the reflectance of only visible light off the glass at normal incidence.  This is usally very close to the solarReflectance_ for non-low-e-coated glass but can differ if the glass has a low-e coating. The default is set to 0.081, which is typical for clear glass without a low-e coating.
        emissivity_:  A number between 0 and 1 that represents the infrared hemispherical emissivity of the glass.  This number is usually pretty high for non-low-e-coated glass but can be significantly lower for low-e coated glass.  The default is set to 0.84, which is typical for clear glass without a low-e coating.
        conductivity_:  A number representing the conductivity of the glass in W/m-K. The default is set to 0.9, which is typical for clear glass without a low-e coating.
    Returns:
        EPMaterial: A glass material that can be plugged into the "Honeybee_EnergyPlus Construction" component.

"""

ghenv.Component.Name = "Honeybee_EnergyPlus Glass Material"
ghenv.Component.NickName = 'EPGlassMat'
ghenv.Component.Message = 'VER 0.0.55\nOCT_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "06 | Energy | Material | Construction"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def setDefaults():
    #Check the name.
    checkData1 = True
    if _name == None:
        checkData1 = False
        print "Connect a name for your glass material."
        materialName = None
    else: materialName = _name
    
    #Check to be sure that many of the numbers are between 0 and 1.
    checkData2 = True
    
    def checkBtwZeroAndOne(variable, default, variableName):
        if variable == None: newVariable = default
        else:
            if variable <= 1 and variable >= 0: newVariable = variable
            else:
                newVariable = 0
                checkData2 = False
                warning = variableName + " must be between 0 and 1."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        
        return newVariable
    
    solTrans = checkBtwZeroAndOne(solarTransmittance_, 0.837, "solarTransmittance_")
    solRef = checkBtwZeroAndOne(solarReflectance_, 0.075, "solarReflectance_")
    visTrans = checkBtwZeroAndOne(visibleTransmittance_, 0.898, "visibleTransmittance_")
    visRef = checkBtwZeroAndOne(visibleReflectance_, 0.081, "visibleReflectance_")
    emissivity = checkBtwZeroAndOne(emissivity_, 0.84, "emissivity_")
    
    #Check to make sure that reflectance + tansmittance does not exceed 1.
    checkData3 = True
    if solTrans+solRef > 1:
        checkData3 = False
        warning = "The sum of solarTransmittance_ and solarReflectance_ must not exceed 1."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    if visTrans+visRef > 1:
        checkData3 = False
        warning = "The sum of visibleTransmittance_ and visibleReflectance_ must not exceed 1."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Set a defaul conductivity.
    if conductivity_ == None: conductivity = 0.9
    else: conductivity = conductivity_
    
    #Set a default thickness.
    if thickness_ == None: thickness = 0.003
    else: thickness = thickness_
    
    #Make sure that all of the previous checks are good.
    if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
    else: checkData = False
    
    
    return checkData, materialName, thickness, solTrans, solRef, visTrans, visRef, emissivity, conductivity


def main(name, thickness, solTrans, solRef, visTrans, visRef, emissivity, conductivity):
    
    opticalDataType = "SpectralAverage"
    spectralDataSetName = ""
    backSolarRef = 0
    backVisRef = 0
    infraredTrans = 0
    dirtCorrection = 1
    solarDiffusing = "No"
    
    values = [name.upper(), opticalDataType, spectralDataSetName, thickness, solTrans, solRef, backSolarRef, visTrans, visRef, backVisRef, infraredTrans, emissivity, emissivity, conductivity, dirtCorrection, solarDiffusing]
    comments = ["Name", "Optical Data Type", "Window Glass Spectral Data Set Name", "Thickness {m}", "Solar Transmittance at Normal Incidence", "Front Side Solar Reflectance at Normal Incidence", "Back Side Solar Reflectance at Normal Incidence", "Visible Transmittance at Normal Incidence", "Front Side Visible Reflectance at Normal Incidence", "Back Side Visible Reflectance at Normal Incidence", "Infrared Transmittance at Normal Incidence", "Front Side Infrared Hemispherical Emissivity", "Back Side Infrared Hemispherical Emissivity", "Conductivity {W/m-K}", "Dirt Collection Factor for Solar and Visible Transmittance", "Solar Diffusing"]
    
    materialStr = "WindowMaterial:Glazing,\n"
    
    for count, (value, comment) in enumerate(zip(values, comments)):
        if count!= len(values) - 1:
            materialStr += str(value) + ",    !" + str(comment) + "\n"
        else:
            materialStr += str(value) + ";    !" + str(comment)
            
    return materialStr
    

checkData, materialName, thickness, solTrans, solRef, visTrans, visRef, emissivity, conductivity = setDefaults()
if checkData == True:
    EPMaterial = main(materialName, thickness, solTrans, solRef, visTrans, visRef, emissivity, conductivity)