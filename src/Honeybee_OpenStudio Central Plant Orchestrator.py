# By Chien Si Harriman
# charriman@terabuild.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# this component can be used to create a custom DX coil, either 1 or 2 speed
# if you specify a one speed coil, just use the high speed inputs.  The low speed
# inputs will always be ignored for 1 speed coil definitions

"""
EPlus Plantside Organizer
-
Provided by Honeybee 0.0.56

    Args:
        _name : ... provide a unique name for each boiler that you specify
        _hotWaterBoiler : a boiler definition that you have created
        _chiller : a chiller definition that you have created
        _coolingTower : a cooling tower definition that you have created

    Returns:
        plantDefinition:...returns an entire plant definition for your use
        
"""

from clr import AddReference
AddReference('Grasshopper')
import scriptcontext as sc
import pprint
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_OpenStudio Central Plant Orchestrator"
ghenv.Component.NickName = 'EPlusCentralPlant'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

class dictToClass(object):
    def __init__(self,pyDict):
        self.d = pyDict
        

def main(sysID, boiler,chiller,coolingTower):
    #eventually allow accommodation for more than one boiler and sequencing
    #eventually allow accommodation for more than one chiller and sequencing
    #eventually allow accommodation for more than one tower and sequencing
    if (sysID <=6 or sysID == 9 or sysID == 10):
        #only a boiler may be specified, no chiller definition
        if len(chiller) >= 1:
            print 'A chiller description is not necessary for system id: ' + str(sysID)
            print 'The chiller description will be ignored.'
            chiller=[]
        if len(coolingTower) >= 1:
            print 'A cooling tower description is not necessary for system id: ' + str(sysID)
            print 'The cooling tower description will be ignored.'
    else:
        print len(coolingTower)
        print coolingTower
        if len(coolingTower) == 0:
            print 'You have selected a system ID that requires a cooling tower.'
            print 'We will revert to the Honeybee default until you provide one.'
            hb_coolTower = dictToClass(sc.sticky["honeybee_coolingTowerParams"]().coolTowerDict)
            coolingTower = [hb_coolTower]

    centralPlant={}
    pp = pprint.PrettyPrinter(indent=4)
    if sc.sticky.has_key('honeybee_release'):
        #place all standard warning messages here
        pass
        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): 
                return boilerUpdates
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            " Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return centralPlant
    
        storedParams = {}
        try:
            if (len(boiler) >= 1):
                print boiler
                print str(len(boiler)) + " boiler definitions located."
                for bcount,b in enumerate(boiler):
                    print "Boiler " + str(bcount+1) + " being added."
                    storedParams['boiler']=b.d
            else:
                storedParams['boiler']={}
                print "No Boiler has been specified.  A blank Boiler added to plant params."
            if (len(chiller) >= 1):
                print str(len(chiller)) + " chiller definitions located."
                for ccount,c in enumerate(chiller):
                    print "Chiller " + str(ccount+1) + " being added."
                    storedParams['chiller']= c.d
            else:
                storedParams['chiller']={}
                print "No Chiller has been specified.  A blank Chiller added to plant params."
            if (len(coolingTower)) >= 1:
                print str(len(coolingTower)) + ' cooling tower definitions located.'
                for ctcount,ct in enumerate(coolingTower):
                    print 'Tower ' + str(ctcount+1) + ' being added.'
                    storedParams['coolingTower'] =ct.d
                    print ct.d
            centralPlant = dictToClass(storedParams)
            print 'Your central plant definition: '
            pp.pprint(centralPlant.d)
            return centralPlant
        except:
            storedParams['boiler']={}
            storedParams['chiller']={}
            storedParams['coolingTower']={}
            centralPlant = dictToClass(storedParams)
            print 'Central Plant could not create your central plant description.'
    else:
        print "Your should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let Honeybee to fly...")
    return centralPlant
    

plantDetails = main(_HVACSystemID, _Boiler_,_Chiller_,_CoolingTower_)