# By Anton Szilasi
# ajszilasi@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an EnergyPlus simulation from the WriteIDF Component or any EnergyPlus result .csv file address.  Note that, if you use this component without the WriteIDF component, you should make sure that a corresponding .eio file is next to your .csv file at the input address that you specify.
_
This component reads only the results related to Honeybee generation systems.  For other results related to zones, you should use the "Honeybee_Read EP Result" for HVAC use the "Honeybee_Read EP HVAC Result" component and, for results related to surfaces, you should use the "Honeybee_Read EP Surface Result" component.

-
Provided by Honeybee 0.0.56
    
    Args:
        _resultFileAddress: The result file address that comes out of the WriteIDF component.

    Returns:
        sensibleCooling: The sensible energy removed by the ideal air cooling load for each zone in kWh.
        latentCooling: The latent energy removed by the ideal air cooling load for each zone in kWh.
        sensibleHeating: The sensible energy added by the ideal air heating load for each zone in kWh.
        latentHeating: The latent energy added by the ideal air heating load for each zone in kWh.
        supplyMassFlow: The mass of supply air flowing into each zone in kg/s.
        supplyAirTemp: The mean air temperature of the supply air for each zone (degrees Celcius).
        supplyAirHumidity: The relative humidity of the supply air for each zone (%).
"""

ghenv.Component.Name = "Honeybee_Read_Honeybee_generation_system_results"
ghenv.Component.NickName = 'readEP_generation_system_results'
ghenv.Component.Message = 'VER 0.0.56\nAPR_06_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc
import copy
import os

#Read the location and the analysis period info from the eio file, if there is one.
#Also try to read the floor areas from this file to be used in EUI calculations.
location = "NoLocation"
start = "NoDate"
end = "NoDate"

if _resultFileAddress:
    try:
        eioFileAddress = _resultFileAddress[0:-3] + "eio"
        if not os.path.isfile(eioFileAddress):
            # try to find the file from the list
            studyFolder = os.path.dirname(_resultFileAddress)
            fileNames = os.listdir(studyFolder)
            for fileName in fileNames:
                if fileName.lower().endswith("eio"):
                    eioFileAddress = os.path.join(studyFolder, fileName)
                    break
                    
        eioResult = open(eioFileAddress, 'r')
        for lineCount, line in enumerate(eioResult):
            if "Site:Location," in line:
                location = line.split(",")[1].split("WMO")[0]
            elif "WeatherFileRunPeriod" in line:
                start = (int(line.split(",")[3].split("/")[0]), int(line.split(",")[3].split("/")[1]), 1)
                end = (int(line.split(",")[4].split("/")[0]), int(line.split(",")[4].split("/")[1]), 24)
        else: pass
        eioResult.close()
        
    except:
        try: eioResult.close()
        except: pass 
        warning = 'Your simulation probably did not run correctly. \n' + \
                  'Check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If there are no severe or fatal errors, the issue could just be that there is .eio file adjacent to the .csv _resultFileAddress. \n'+ \
                  'Check the folder of the file address you are plugging into this component and make sure that there is both a .csv and .eio file in the folder.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else: pass

#Make a function to add headers.
def makeHeader(list, path, timestep, name, units):

    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    list.Add(location, GH_Path(path))
    list.Add(name, GH_Path(path))
    list.Add(units, GH_Path(path))
    list.Add(timestep, GH_Path(path))
    list.Add(start, GH_Path(path))
    list.Add(end, GH_Path(path))
    

netpurchasedelect = []
totalelectdemand = []

# PARSE THE RESULT FILE.

result = open(_resultFileAddress, 'r')

netpurchasedelect = []
totalelectdemand = []
generatorproducedenergy = DataTree[Object]()


dict = {}
electricloadcentername = []
electricloadcenterrunperiod = None

for lineCount,line in enumerate(result):
    
    if lineCount == 0:
        #print line
        for columnCount, column in enumerate(line.split(',')):
            
            if 'Whole Building:Facility Net Purchased Electric Energy' in column:
                
                dict['Whole Building:Facility Net Purchased Electric Energy'] = columnCount

            elif 'Whole Building:Facility Total Electric Demand Power' in column:
                
                dict['Whole Building:Facility Total Electric Demand Power'] = columnCount
                
            elif 'DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy' in column:
            
                data = column.split(':')
                
                electricloadcentername.append(data[0])
                
                electricloadcenterrunperiod = column.split('(')[-1].split(')')[0]
                
                dict[str(data[0])+'- DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy'] = columnCount
                
            else:
                pass
    else:

        for rowCount, row in enumerate(line.split(',')):
            
            if rowCount == dict['Whole Building:Facility Total Electric Demand Power']:

                totalelectdemand.append(round(float(row),2))
                
            if rowCount == dict['Whole Building:Facility Net Purchased Electric Energy']:
                
                netpurchasedelect.append(round(float(row),2))
            
            # for loop maybe not the best for performance 
            for count,electricloadcenter in enumerate(electricloadcentername): 
            
                if rowCount == dict[str(electricloadcenter)+'- DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy']:
                    
                    print row
                    
                    if lineCount == 1:
                        # Add the header to each output
                        #print makeHeader(generatorproducedenergy, count, electricloadcenterrunperiod, 'Generator system '+str(electricloadcenter), 'J'),GH_Path(count))
                        generatorproducedenergy.Add(makeHeader(generatorproducedenergy, count, electricloadcenterrunperiod, 'Generator system '+str(electricloadcenter), 'J'),GH_Path(count))

                        generatorproducedenergy.Add(round(float(row),2),GH_Path(count))
                        
                    else:
                        generatorproducedenergy.Add(round(float(row),2),GH_Path(count))

result.close()

"""
except:
    try: result.close()
    except: pass
    warn = 'Failed to parse the result file.  Check the folder of the file address you are plugging into this component and make sure that there is a .csv file in the folder. \n'+ \
              'If there is no csv file or there is a file with no data in it (it is 0 kB), your simulation probably did not run correctly. \n' + \
              'In this case, check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
              'If the csv file is there and it seems like there is data in it (it is not 0 kB), you are probably requesting an output that this component does not yet handle well. \n' + \
              'If you report this bug of reading the output on the GH forums, we should be able to fix this component to accept the output soon.'
    print warn
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)
"""


