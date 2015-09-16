#Developed by: Sarith Subramniam, Penn State
#sarith@sarith.in
#Demo: https://youtu.be/KR5tRepXgRA
"""
    
    Locate a file/directory in windows explorer
    
    Args:
        Destination: File path or Directory path
        Open: Boolean value. Default is True
"""

ghenv.Component.Name = "Explorer"
ghenv.Component.NickName = 'Explorer'
ghenv.Component.Message = 'Ver Alpha\n27_July_2015'
ghenv.Component.Category = "PSUAE"
ghenv.Component.SubCategory = "2 | Utilities"

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Grasshopper.Kernel as gh
import os
import subprocess
def main(location):
    if location:
        try:
            
            location = location.replace('"',"") #Just in case the user enters a hardcoded path.
            assert os.path.exists(location) #Check if the path exists at all or else throw an assertion error.
            
            foldername = os.path.dirname(location)
            subprocess.Popen('explorer.exe '+foldername)
        except AssertionError:
            throw("The specified path %s does not exist"%location)
        except:
                throw("The input is not a valid path")            
                return -1
    else:
        throw("The input is empty")

def throw(msg):
    e = msg
    et = gh.GH_RuntimeMessageLevel.Error
    ghenv.Component.AddRuntimeMessage(et,e)


main(_Destination)
