# By Anton Szilasi
# For technical support or user requests contact me at
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
        idfFileAddress: The IDF file address that comes out of the WriteIDF component.
        gridelect_cost_schedule: The cost of grid connected electricty per Kwh in whatever currency the user wishes - Just make it consistent with other components you are using
        If you want to specify a flat rate just specify one value this will be used across all the hours of the year.
        Otherwise specify the grid electricity cost for 288 hours of the year that is for each hour of the day for one day in every month of the year.
        Use a list with 288 values to do this.
        feedin_tariff_schedule: The price that the utility will pay per Kwh in whatever currency the user wishes - (Just make it consistent with other components you are using) 
        for power fed back into the grid. If you want to specify a flat rate just specify one value this will be used across all the hours of the year.
        Otherwise specify the grid electricity cost for 288 hours of the year that is for each hour of the day for one day in every month of the year.
        Use a list with 288 values to do this.
    Returns:
        totalelectdemand: The total electricity demand of the facility in Watts
        netpurchasedelect: The net purchased electricity of the facility in Joules 
        - a negative value means that the facility produced surplus electricity and it was 
        sold to the grid.
        generatorproducedenergy: The electricity produced by each Honeybee generator in the facility
        financialdata: Financial data about the Honeybee generators in the facility.
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
location = "NoLocation"
start = "NoDate"
end = "NoDate"

def checktheinputs(feedin_tariff_schedule,gridelect_cost_schedule,_resultFileAddress,idfFileAddress):
    
    if _resultFileAddress == None:
        
        warn = '_resultFileAddress must be specified!'
    
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
    if idfFileAddress == None:
        
        warn = 'idfFileAddress must be specified!'
    
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
    if (feedin_tariff_schedule == []) or (feedin_tariff_schedule[0] == None):
    
        warn = 'The price of the feed in tariff per Kwh must be specified! \n' + \
        'If a flat cost is used just specify one value, this will be used for all hours of the year otherwise specify 24 hours of data for each month of the year \n' + \
        'that is 288 hours of data for the whole year'
    
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
    if (gridelect_cost_schedule == []) or (gridelect_cost_schedule[0] == None):
        
        warn = 'The cost of grid electricty per Kwh must be specified! \n' + \
        'If a flat cost is used just specify one value, this will be used for all hours of the year otherwise specify 24 hours of data for each month of the year \n' + \
        'that is 288 hours of data for the whole year'

        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
    
    if (len(gridelect_cost_schedule) >= 1) and (len(gridelect_cost_schedule) != 288):
        
        warn = 'The cost of grid electricty per Kwh must be specified! The cost of grid electricty for each hour of the day for one day in every month of the year was not found! \n' + \
        'if you want to use a flat rate just specify one value this will be used as the grid electricity cost across the year \n' + \
        'Otherwise you must specify the cost of grid electricity for  288 hours of the year, that is for each hour of the day for one day in every month of the year'

        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1
        
    if (feedin_tariff_schedule > 1) and (len(feedin_tariff_schedule) != 288):

        warn = 'The price of the feed in tariff per Kwh must be specified! The cost of grid electricty for each hour of the day for one day in every month of the year was not found! \n' + \
        'if you want to use a flat rate just specify one value this will be used as the grid electricity cost across the year \n' + \
        'Otherwise you must specify the cost of grid electricity for  288 hours of the year, that is for each hour of the day for one day in every month of the year'

        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warn)
        return -1

if _resultFileAddress != None:
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

#Make a function to add headers for datatrees
def makeHeaderdatatree(list, path, timestep, name, units):

    list.Add("key:location/dataType/units/frequency/startsAt/endsAt", GH_Path(path))
    list.Add(location, GH_Path(path))
    list.Add(name, GH_Path(path))
    list.Add(units, GH_Path(path))
    list.Add(timestep, GH_Path(path))
    list.Add(start, GH_Path(path))
    list.Add(end, GH_Path(path))
# Make a function to add headers for outputs that are not datatrees
def makeHeader(list, timestep, name, units):
    
    list.append("key:location/dataType/units/frequency/startsAt/endsAt")
    list.append(location)
    list.append(name)
    list.append(units)
    list.append(timestep)
    list.append(start)
    list.append(end)

netpurchasedelect = []
totalelectdemand = []


if checktheinputs(gridelect_cost_schedule,feedin_tariff_schedule,_resultFileAddress,idfFileAddress) != -1:
    
# 1. Read electricity generation outputs and electricity demand from IDF file

    try:
        result = open(_resultFileAddress, 'r')
        
        netpurchasedelect = []
        totalelectdemand = []
        generatorproducedenergy = DataTree[Object]()
        
        
        dict = {}
        electricloadcentername = []
        electricloadcenterrunperiod = None
        
        for lineCount,line in enumerate(result):
            
            # Read the headers of the CSVs files and create a dictonary entry in dict based on these headers
            if lineCount == 0:
    
                for columnCount, column in enumerate(line.split(',')):
                    
                    # Extract the Whole Building:Facility Net Purchased Electric Energy output from the CSV,
                    # If there is a Honeybee generation system this will alway be written as a default output
                    if 'Whole Building:Facility Net Purchased Electric Energy' in column:
                        
                        dict['Whole Building:Facility Net Purchased Electric Energy'] = columnCount
                        
                        # Get the runperiod for the net purchased electric energy
                        facilitynet_purchasedelect_runperiod = column.split('(')[-1].split(')')[0]
                        
                    # Extract the 'Whole Building:Facility Total Electric Demand Power' output from the CSV,
                    # If there is a Honeybee generation system this will alway be written as a default output
                    elif 'Whole Building:Facility Total Electric Demand Power' in column:
                        
                        dict['Whole Building:Facility Total Electric Demand Power'] = columnCount
                        
                        # Get the runperiod for the facility electric demand power
                        facilityelect_demandpower_runperiod = column.split('(')[-1].split(')')[0]
                    
                    # Extract the Electricty energy produced by each Honeybee generation system
                    elif 'DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy' in column:
                    
                        data = column.split(':')
                        
                        electricloadcentername.append(data[0])
                        
                        # Get the runperiod for each Honeybee generation system
                        electricloadcenterrunperiod = column.split('(')[-1].split(')')[0]
                        
                        dict[str(data[0])+'- DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy'] = columnCount
                        
                    else:
                        pass
            # Read the data of each header in the CSV file
            else:
                
                for rowCount, row in enumerate(line.split(',')):
                    
                    # Whole Building:Facility Net Purchased Electric Energy
                    if rowCount == dict['Whole Building:Facility Total Electric Demand Power']:
                        
                        if lineCount == 1:
                            
                            # Add the header to each output
                            makeHeader(totalelectdemand, facilityelect_demandpower_runperiod, 'Whole Building:Facility Total Electric Demand Power', 'J')
                            
                            totalelectdemand.append(round(float(row),2))
                        
                        else:
                            
                            totalelectdemand.append(round(float(row),2))
                            
                    # Whole Building:Facility Total Electric Demand Power
                    if rowCount == dict['Whole Building:Facility Net Purchased Electric Energy']:
                        
                        if lineCount == 1:
                            
                            # Add the header to each output
                            makeHeader(netpurchasedelect, facilitynet_purchasedelect_runperiod, 'Whole Building:Facility Net Purchased Electric Energy', 'J')
                            
                            netpurchasedelect.append(round(float(row),2))
                            
                        else:
                            
                            netpurchasedelect.append(round(float(row),2))
                    
                    # For each Honeybee generation system
                    for count,electricloadcenter in enumerate(electricloadcentername): 
                    
                        if rowCount == dict[str(electricloadcenter)+'- DISTRIBUTIONSYSTEM:Electric Load Center Produced Electric Energy']:
                            
                            if lineCount == 1:
                                # Add the header to each output
                                
                                makeHeaderdatatree(generatorproducedenergy, count, electricloadcenterrunperiod, 'Electric energy produced by the generator system named - '+str(electricloadcenter), 'J')
        
                                generatorproducedenergy.Add(round(float(row),2),GH_Path(count))
                            
                            else:
                                generatorproducedenergy.Add(round(float(row),2),GH_Path(count))
    
        result.close()
    
    except IOError:
    
        try: result.close()
        except: pass
        warn = 'Failed to parse the result file.  Check the folder of the file address you are plugging into this component and make sure that there is a .csv file in the folder. \n'+ \
                  'If there is no csv file or there is a file with no data in it (it is 0 kB), your simulation probably did not run correctly. \n' + \
                  'In this case, check the report out of the Run Simulation component to see what severe or fatal errors happened in the simulation. \n' + \
                  'If the csv file is there and it seems like there is data in it (it is not 0 kB), you are probably requesting an output that this component does not yet handle well. \n' + \
                  'If you report this bug of reading the output on the GH forums, we should be able to fix this component to accept the output soon.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)
        
# 2. Read financial data from the IDF file

if idfFileAddress != None:
    
    fiancialresult = open(idfFileAddress, 'r')
    
    data = []
    
    startpoint = None
    endpoint = None
    
    # Financial results can be identified in the IDF file by the lines !!!X, !!!Z and !!!!Y
    for lineCount,line in enumerate(fiancialresult):
        
        # Add this financial data to the list data.
        if (line.find('!!!!Y') != -1) or (line.find('!!!X') != -1) or (line.find('!!!Z') != -1):
            data.append(line)
            
    def cleandata(data):
        """ This function cleans the financial data written to the IDF and makes it possible to create graphs from it"""
        
        cleandata = []
        financialdata = []
    
        # Remove all un-necessary characters
    
        for dataitem in data:
            
            cleandata.append(dataitem.replace('!!!','').replace('!','').replace('\n','').replace('Z','').replace('[','').replace(']','').replace('X',''))
            
        itemCountlist = []
        
        for itemCount,item in enumerate(cleandata):
            
            if item.find('generation system name') != -1:
                
                itemCountlist.append(itemCount)
        
        for itemCount,item in enumerate(itemCountlist):
        
            try:
                financialdata.append(cleandata[itemCountlist[itemCount]:itemCountlist[itemCount+1]])
            except IndexError:
                financialdata.append(cleandata[itemCountlist[itemCount]:len(cleandata)])
                
        return financialdata
    
    # Add financial data - equipment costs and grid electricty costs and feed in tariffs to
    # financial data, datatree
    
    financialdata = DataTree[Object]()
    
    # Add a header to the equipment cost financial data
    financialdata.Add('Generator system financial data',GH_Path(0))
    
    # Clean the financial data so that it can used to create graphs and add it to the datatree
    for generatorfinancialdata in cleandata(data):
        for data in generatorfinancialdata:
            print data
            financialdata.Add(data,GH_Path(0))

    # Add grid electricity costs and feed in tariffs to the financial data - datatree
    financialdata.Add('Grid electricity costs per Kwh',GH_Path(1))
    
    for data in gridelect_cost_schedule:
    
        financialdata.Add(data,GH_Path(1))
    
    financialdata.Add('Feed in tariff costs per Kwh',GH_Path(2))
    
    for data in feedin_tariff_schedule:
    
        financialdata.Add(data,GH_Path(2))
        
    financialdata.Add(';;;',GH_Path(0))
    financialdata.Add('!!',GH_Path(1))
    financialdata.Add('##',GH_Path(2))