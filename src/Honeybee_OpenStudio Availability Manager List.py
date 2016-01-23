#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chien Si Harriman <charriman@terabuild.com> 
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

# this component can be used to create an availability manager list
# the availability manager list allows you to create more complex controls
# of your HVAC system
# currently honeybee only supports AvailabilityManagersLists with one availability manager contained within 
# instead of requiring you to create the AvailabilityManager elsewhere, you define it all in this component


"""
AvailabilityManagerList
-
Provided by Honeybee 0.0.59

    Args:
        _name: ... provide a unique name for this manager list (required)
        _type: ... there are two options currently available for AvailabilityManager types, 0 = Scheduled and 1 = NightCycle. (required)
        _scheduleName: ... both types of AvailabilityManager require a schedule.  Just provide a schedule name available from Honeybee.  This schedule will determine whether the manager is available for control.  By default, if left blank (recommended) the schedule will be Always On (always available).  This is what most people want.
        _controlType_: ... an optional field for NightCycle type AvailabilityManagers only.  It will be ignored for type Scheduled.  There are two options 0: StayOff and 1:CycleOnAny (the default).  If left blank, it will default (this is usually what is preferred, so leave it blank if you are not sure)
    Returns:
        availManager:...returns an object that will modify the availability manager

"""


from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Availability Manager List"
ghenv.Component.NickName = 'EPlusAvailabilityManagerList'
ghenv.Component.Message = 'VER 0.0.59\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | AirsideSystems"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


#this is to class-i-fy the dictionary
class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        
typeDict = {
0:'Scheduled',
1:'NightCycle'
}

controlTypeDict = {
0:'StayOff',
1:'CycleOnAny',
2:'Ignored'
}

def main(name,type,scheduleName,controlType):
    print 'We are setting up your Availability Manager List'
    #do all simple checking here
    returnDict={}
    if name==None:
        print 'A unique name should be provided.  Use a panel to provide one.'
        print 'This component will not continue until a name is provided.'
        msg = "Use a panel and provide a name to activate this component."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return dictToClass(returnDict)
    if type == None:
        type = 1 #it can't be none, it would throw an error
    if type > 1:
        print 'The type must be either a 0 or a 1'
        msg = "Type should be an integer with value 0 or 1."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return dictToClass(returnDict)
    if type == 0:
        if controlType != None:
            print 'the control type input is only used for manager type=1 (NightCycle).  You have specified a Scheduled AvailabilityManager, so this input is ignored.'
            controlType = 2
            msg = "controlType is ignored for AvailabilityManager type=0 (Scheduled)"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, msg)
    if controlType==None:
        controlType=1 #it can't be none, this would throw an error
    
    pp = pprint.PrettyPrinter(indent=4)
    if sc.sticky.has_key('honeybee_release'):
        #place all standard warning messages here
        pass
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return chillerUpdates
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return dictToClass(managerUpdates)
        
        
        if name != None:
            print 'We are hunting for the default Honeybee Availability Manager Description.'
            hb_manList = sc.sticky["honeybee_availManagerList"]().manListDict
            pp.pprint(hb_manList)
            manList= {
            'name':name,
            'type':typeDict[type],
            'scheduleName':scheduleName,
            'controlType':controlTypeDict[controlType],
            }
            print 'Your AvailabilityManagerList definition:'
            pp.pprint(manList)
        
            actions = []
            storedManListPar = {}
            for key in hb_manList.keys():
                if manList.has_key(key) and manList[key] != None:
                    if key == 'name':
                        s = key + ' has been updated to ' + manList[key]
                        actions.append(s)
                    elif key =='type':
                        s = key + ' has been updated to ' + manList[key]
                        actions.append(s)
                    elif key == 'scheduleName':
                        s = key + ' has been updated to ' + manList[key]
                        actions.append(s)
                    elif key == 'controlType':
                        s = key + ' has been updated to ' + manList[key]
                        actions.append(s)
                    else:
                        s = key + ' has been updated to ' + str(manList[key])
                        actions.append(s)
                    storedManListPar[key] = manList[key]
                else:
                    if key == 'name':
                        s = key + ' is still set to Honeybee Default: ' + hb_manList[key]
                        actions.append(s)
                    elif key =='type':
                        s = key + ' is still set to Honeybee Default: ' + hb_manList[key]
                        actions.append(s)
                    elif key == 'scheduleName':
                        s = key + ' is still set to Honeybee Default: ' + hb_manList[key]
                        actions.append(s)
                    elif key == 'controltype':
                        s = key + ' is still set to Honeybee Default: ' + hb_manList[key]
                        actions.append(s)
                    else:
                        s = key + ' is still set to Honeybee Default: ' + str(hb_manList[key])
                        actions.append(s)
                    storedManListPar[key] = hb_manList[key]
            
            availabilityManagerListParameters = dictToClass(storedManListPar)
            print 'your Availability Manager List definition: '
            pp.pprint(storedManListPar)
            print ''
            print 'Here are all the actions completed by this component:'
            actions = sorted(actions)
            pp.pprint(actions)
            
            return availabilityManagerListParameters
            
availabilityManagerList=main(_name,_type,_scheduleName,_controlType_)
#print availabilityManagerList.d
