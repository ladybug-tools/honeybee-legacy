# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component reads the results of an Adaptive Indoor Comfort Analysis.  Note that this usually takes about a minute
-
Provided by Honeybee 0.0.56
    
    Args:
        _comfResultFileAddress: Any one of the result file addresses that comes out of the Honeybee Adaptive Indoor Comfort Analysis component.
    Returns:
        comfResultsMtx: A matrix of comfort data that can be plugged into the "Visualize Comfort Results" component.
"""

ghenv.Component.Name = "Honeybee_Read Indoor Comfort Result"
ghenv.Component.NickName = 'readComfortResult'
ghenv.Component.Message = 'VER 0.0.56\nFEB_01_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
ghenv.Component.AdditionalHelpFromDocStrings = "3"


import Grasshopper.Kernel as gh


comfResultsMtx = []

if _comfResultFileAddress:
    try:
        result = open(_comfResultFileAddress, 'r')
        
        for lineCount, line in enumerate(result):
            if lineCount == 0: comfResultsMtx.append(line.split('\n')[0])
            else:
                #Pull out the data.
                hourData = []
                for columnCount, column in enumerate(line.split(',')):
                    hourData.append(float(column))
                comfResultsMtx.append(hourData)
        result.close()
    except:
        try: result.close()
        except: pass
        warn = 'Failed to parse the result file.  The csv file might not have existed when connected or the simulation did not run correctly.'+ \
                  'Try reconnecting the _resultfileAddress to this component or re-running your simulation.'
        print warn
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

