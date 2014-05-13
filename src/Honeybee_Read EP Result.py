# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component

-
Provided by Honeybee 0.0.53
    
    Args:
        resultFileAddress: The result file address that comes out of the WriteIDF component.
    Returns:
        report: Report!
        ====================: This is just for organizational purposes of the component.
        zoneCooling: The ideal air load cooling energy needed for each zone in kWh.
        zoneHeating: The ideal air load heating energy needed for each zone in kWh.
        zoneElectricLight: The electric lighting energy needed for each zone in kWh.
        zoneElectricEquip: The electric equipment energy needed for each zone in kWh.
        ====================: This is just for organizational purposes of the component.
        zonePeopleGains: The internal heat gains in each zone resulting from people (kWh).
        zoneBeamGains: The direct solar beam gain in each zone(kWh).
        zoneDiffGains: The diffuse solar gain in each zone(kWh).
        zoneInfiltrationLoss: The heat loss (negative) or heat gain (positive) in each zone resulting from infiltration (kWh).
        zoneWindowLoss: The heat loss (negative) or heat gain (positive) in each zone resulting from window conduction (kWh).
        surfaceOpaqueConvecLoss: The heat loss (negative) or heat gain (positive) in each zone resulting from exterior convection (kWh).
        surfaceOpaqueRadiationLoss: The heat loss (negative) or heat gain (positive) in each zone resulting from emitted/absorbed thermal radiation from the outside facade (kWh).
        surfaceOpaqueSolarGain: The heat gain in each zone resulting from solar radiation absorbed by the outside facade (kWh).
        ====================: This is just for organizational purposes of the component.
        zoneAirTemperature: The mean air temperature of each zone (degrees Celcius)
        zoneMeanRadiantTemperature: The mean radiant temperature of each zone (degrees Celcius)
        surfaceOpaqueIndoorTemp: The indoor surface temperature of each opaque surface (degrees Celcius)
        surfaceGlazIndoorTemp: The indoor surface temperature of each glazed surface (degrees Celcius)
        surfaceOpaqueOutdoorTemp: The outdoor surface temperature of each opaque surface (degrees Celcius)
        surfaceGlazOutdoorTemp: The outdoor surface temperature of each glazed surface (degrees Celcius)
"""

ghenv.Component.Name = "Honeybee_Read EP Result"
ghenv.Component.NickName = 'readIdf'
ghenv.Component.Message = 'VER 0.0.53\nMAY_12_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


zoneCooling = DataTree[Object]()
zoneHeating = DataTree[Object]()
zoneElectricLight = DataTree[Object]()
zoneElectricEquip = DataTree[Object]()
zonePeopleGains = DataTree[Object]()
zoneBeamGains = DataTree[Object]()
zoneDiffGains = DataTree[Object]()
zoneInfiltrationLoss = DataTree[Object]()
zoneWindowLoss = DataTree[Object]()
surfaceOpaqueConvecLoss = DataTree[Object]()
surfaceOpaqueRadiationLoss = DataTree[Object]()
surfaceOpaqueSolarGain = DataTree[Object]()
zoneAirTemperature = DataTree[Object]()
zoneMeanRadiantTemperature = DataTree[Object]()
surfaceOpaqueIndoorTemp = DataTree[Object]()
surfaceGlazIndoorTemp = DataTree[Object]()
surfaceOpaqueOutdoorTemp = DataTree[Object]()
surfaceGlazOutdoorTemp = DataTree[Object]()


if resultFileAddress:
    result = open(resultFileAddress, 'r')
    
    for lineCount, line in enumerate(result):
        if lineCount == 0:
            #print len(line)
            # analyse the heading
            # cooling = 0, heating = 1
            key = []; path = []
            for cloumn in line.split(','):
                if 'Zone' in cloumn.split(':') and 'Cooling' in cloumn.split(':'):
                    key.append(0)
                    path.append(cloumn.split(':')[-1].split('[')[0].split('_'))
                
                elif 'Zone' in cloumn.split(':') and 'Heating' in cloumn.split(':'):
                    key.append(1)
                    path.append(cloumn.split(':')[-1].split('[')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Lights' in cloumn:
                    key.append(2)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Equipment' in cloumn:
                    key.append(3)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'People' in cloumn:
                    key.append(4)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Beam' in cloumn:
                    key.append(5)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Diff' in cloumn:
                    key.append(6)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Infiltration' in cloumn:
                    key.append(7)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Window Heat Loss' in cloumn:
                    key.append(8)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Convection' in cloumn and len(cloumn.split('_')) == 3:
                    key.append(9)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Thermal Radiation' in cloumn and len(cloumn.split('_')) == 3:
                    key.append(10)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Solar Radiation' in cloumn and len(cloumn.split('_')) == 3:
                    key.append(11)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Air Temperature' in cloumn:
                    key.append(12)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Zone' in cloumn and 'Radiant Temperature' in cloumn:
                    key.append(13)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Inside Face Temperature' in cloumn and len(cloumn.split('_')) == 3:
                    key.append(14)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Inside Face Temperature' in cloumn and len(cloumn.split('_')) == 6:
                    key.append(15)
                    path.append([cloumn.split(':')[0].split('_')[0], cloumn.split(':')[0].split('_')[1], cloumn.split(':')[0].split('_')[2],cloumn.split(':')[0].split('_')[4], cloumn.split(':')[0].split('_')[5]])
                
                elif 'Surface' in cloumn and 'Outside Face Temperature' in cloumn and len(cloumn.split('_')) == 3:
                    key.append(16)
                    path.append(cloumn.split(':')[0].split('_'))
                
                elif 'Surface' in cloumn and 'Outside Face Temperature' in cloumn and len(cloumn.split('_')) == 6:
                    key.append(17)
                    path.append([cloumn.split(':')[0].split('_')[0], cloumn.split(':')[0].split('_')[1], cloumn.split(':')[0].split('_')[2],cloumn.split(':')[0].split('_')[4], cloumn.split(':')[0].split('_')[5]])
                
                else:
                    key.append(-1)
                    path.append(-1)
            #print key
            print path
        else:
            for cloumnCount, cloumn in enumerate(line.split(',')):
                if key[cloumnCount] == 0:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneCooling.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 1:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneHeating.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 2:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneElectricLight.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 3:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneElectricEquip.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 4:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zonePeopleGains.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 5:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneBeamGains.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 6:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneDiffGains.Add((float(cloumn)/3600000), p)
                elif key[cloumnCount] == 7:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneInfiltrationLoss.Add(((float(cloumn))*(-1)/3600000), p)
                elif key[cloumnCount] == 8:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneWindowLoss.Add(((float(cloumn))*(-1)/3600000), p)
                elif key[cloumnCount] == 9:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]))
                    surfaceOpaqueConvecLoss.Add(((float(cloumn))/3600000), p)
                elif key[cloumnCount] == 10:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]))
                    surfaceOpaqueRadiationLoss.Add(((float(cloumn))/3600000), p)
                elif key[cloumnCount] == 11:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]))
                    surfaceOpaqueSolarGain.Add(((float(cloumn))/3600000), p)
                elif key[cloumnCount] == 12:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneAirTemperature.Add(float(cloumn), p)
                elif key[cloumnCount] == 13:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]))
                    zoneMeanRadiantTemperature.Add(float(cloumn), p)
                elif key[cloumnCount] == 14:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]))
                    surfaceOpaqueIndoorTemp.Add(float(cloumn), p)
                elif key[cloumnCount] == 15:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]), int(path[cloumnCount][3]), int(path[cloumnCount][4]))
                    surfaceGlazIndoorTemp.Add(float(cloumn), p)
                elif key[cloumnCount] == 16:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]))
                    surfaceOpaqueOutdoorTemp.Add(float(cloumn), p)
                elif key[cloumnCount] == 17:
                    p = GH_Path(int(path[cloumnCount][0]), int(path[cloumnCount][1]), int(path[cloumnCount][2]), int(path[cloumnCount][3]), int(path[cloumnCount][4]))
                    surfaceGlazOutdoorTemp.Add(float(cloumn), p)
                
    result.close()