#This is a component for calculating a rough building balance temperature from an energy simulation.
#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to calculate a rough building (or zone) balance temperatrue from a Honeybee energy simulation.  The balance point is the outdoor temperature at which your building is usually neither heating or cooling itself.  If the outdoor temperture drops below the balance temperature, your building will usually be heating itself and, if the outdoor temperture is above the balance temperature, the building will usually be cooling itself.
- 
The balance temperture concept is useful for setting things such as automated blinds and airflow shcedules since having these things controlled by hourly cooling or heating can often introduce odd behavior resulting from idiosyncrasies in the building's schedule.
This component works by taking the average combined heating/cooling values for each day and the average outdoor air temperature for each day.  The days with the smallest combined heating + cooling will have their daily mean outdoor air tempertures averaged to produce the balance temperture.
-
Provided by Honeybee 0.0.64
    
    Args:
        _thermalLoadBal: The output "thermalEnergyBalance" from the "Honeybee_Read EP Result" component.  This can be for a single zone if you select out one branch of this thermalEnergyBalance output or it can be for the whole simulated building if you connect the whole output.  Note that, in order to use this component correclty, you must run either a simulation with either an hourly or daily timestep.
        _outdoorAirTemp: The "dryBulbTemperature" output from the "Ladybug_Import epw" component.
        numDaysToAverage_: An optional number of days with a low thermal energy load that will be averaged together to yield the balance point.  This is done to help avoid anomalies introduced by variations between weekday and weekend shcedules.  The default is set to 10 but you may want to drop this down if there is little variation between weekday and weekend schedule or you might increase this number is there is a high variation.
    Returns:
        energyUsedOnBalDay: The amount of energy used on the balbnce day.  This number should be close to 0 and is mostly meant to give a sense of the accuracy of the temperature value below
        balanceTemperature: The outdoor balance temperature of the connected zone or building data.
"""

ghenv.Component.Name = "Honeybee_Balance Temperature Calculator"
ghenv.Component.NickName = 'calcBalTemperature'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
import scriptcontext as sc


def checktheInputs(lb_preparation):
    #Create a py list of the energy bal data tree.
    def createPyList(ghTree):
        pyList = []
        for i in range(ghTree.BranchCount):
            branchList = ghTree.Branch(i)
            branchval = []
            for item in branchList:
                branchval.append(item)
            pyList.append(branchval)
        return pyList
    
    energyBalPyList = createPyList(_thermalLoadBal)
    
    #Check to be sure that all of the thermal energy balance data is correct, that it is the right timestep, and get the analysis period.
    checkData1 = True
    timeStep = None
    analysisPeriod = []
    energyBalNumList = []
    
    for branch in energyBalPyList:
        if len(branch) > 0:
            if 'Thermal Load Balance' in branch[2]: pass
            else:
                checkData1 = False
                warning = 'Connected _thermaLoadBal is not valid data from the "Honeybee_Read EP Result" component.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            if checkData1 == True:
                if branch[4] == 'Hourly' or branch[4] == 'Daily': timeStep = branch[4]
                else:
                    checkData1 = False
                    warning = 'Connected _thermaLoadBal must be for a daily or an hourly timestep.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                analysisPeriod = [branch[5], branch[6]]
                energyBalNumList.append(branch[7:])
        else:
            checkData1 = False
            warning = 'One of the _thermaLoadBal branches is empty.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    
    #If there are multiple connected branches for the thermal energy balance, add them all together into one list.
    energyBalNum = []
    if len(energyBalNumList) > 1:
        for bCount, branch in enumerate(energyBalNumList):
            if bCount == 0:
                for item in branch:
                    energyBalNum.append(item)
            else:
                for count, item in enumerate(branch):
                    energyBalNum[count] = energyBalNum[count] + item
    elif len(energyBalNumList) == 1:
        energyBalNum = energyBalNumList[0]
    
    #Write a function to split the hourly data into daily chunks.
    def chunks(l, n):
        if n < 1:
            n = 1
        return [l[i:i + n] for i in range(0, len(l), n)]
    
    #If the energy balance is hourly, sum up the values for each day.
    newEnergyBalNum = []
    if timeStep == 'Hourly':
        chunkedNumList = chunks(energyBalNum, 24)
        for list in chunkedNumList:
            newEnergyBalNum.append(sum(list))
        energyBalNum = newEnergyBalNum
    
    #Check to be sure that the outdoor Air Temperature is of the correct data type and average hourly values into daily ones.
    checkData2 = True
    outAirList = []
    
    if len(_outdoorAirTemp) > 6:
        if _outdoorAirTemp[2] == 'Dry Bulb Temperature' and _outdoorAirTemp[4] == 'Hourly' and len(_outdoorAirTemp) == 8767: pass
        else:
            checkData2 = False
            warning = 'Connected _outdoorAirTemp is not valid data from the "Ladybug_Import epw" component.  Connected data must have a header on it.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        if checkData2 == True:
            outdoorAirNum = _outdoorAirTemp[7:]
            if analysisPeriod != [(1,1,1), (12,31,24)]:
                newOutAirNum = []
                HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
                for hour in HOYS:
                    newOutAirNum.append(outdoorAirNum[hour-1])
                outdoorAirNum = newOutAirNum
            
            chunkedOutAirList = chunks(outdoorAirNum, 24)
            for list in chunkedOutAirList:
                outAirList.append(sum(list)/24)
    
    #Check the number of days and set a default value of 10 if nothing is connected.
    if numDaysToAverage_ == None:
        numOfDays = 10
        print 'The number of days to average has been set to 10.'
    else: numOfDays = numDaysToAverage_
    
    checkData3 = True
    if numOfDays > len(energyBalNum):
        checkData3 = False
        warning = 'The number of days to average is greater than the length of the analysis period.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Check if everything is good.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
    
    
    return checkData, energyBalNum, outAirList, numOfDays


def main(dailyEnergyBalance, dailyOutdoorTemps, numOfDays):
    #Calculate the deviation from zero of the energy balance.
    energyDeviation = []
    for day in dailyEnergyBalance:
        if day > 0:
            energyDeviation.append(day)
        else:
            energyDeviation.append(day*-1)
    
    #Sort the list of energy values alongside that of temperatures.
    temperaturesSort = [x for (y,x) in sorted(zip(energyDeviation, dailyOutdoorTemps))]
    balTemperDays = temperaturesSort[:numOfDays]
    balanceTemperature = sum(balTemperDays)/len(balTemperDays)
    
    energyDeviation.sort()
    energyUsedOnBalDay = energyDeviation[:numOfDays]
    
    return balanceTemperature, energyUsedOnBalDay


#Import the LB Class.
initCheck = True
if sc.sticky.has_key('ladybug_release'): lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let the Ladybug fly...")


checkData = False
if _thermalLoadBal.BranchCount > 0 and _outdoorAirTemp != [] and initCheck == True:
    checkData, dailyEnergyBalance, dailyOutdoorTemps, numOfDays = checktheInputs(lb_preparation)

if checkData == True:
    balanceTemperature, energyUsedOnBalDay = main(dailyEnergyBalance, dailyOutdoorTemps, numOfDays)