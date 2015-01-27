# By Patrick Chopson and Sandeep Ahuja
# patrick.chopson@perkinswill.com and sandeep.ahuja@perkinswill.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

##!!!!!!Download the latest EPC (Monthly) and EPC Weather Converter from - http://zeroenergygreen.com/downloads/

"""
Export to Energy Performace Calculator (EPC)
+The EPC is an Excel based energy modeling software.
+Instant results no waiting for calculation results.
+Reduces a building down to “box”
+Developed for 20 years at the Georgia Institute of Technology - Building Technology Lab.
+EPC is proven to be accurate to within 5-6% of more sophisticated tools such as EnergyPlus or eQuest.
+Normative energy calculator defined by ISO 13970 and CEN 15603.
+Monthly and Hourly versions proven superior to dynamic simulation methods in ASHRAE 90.1, Appendix G.

-
Provided by Honeybee 0.0.55

    Args:
        _HBZones: Honeybee Zones
        filename: Name of the Excel EPC file
        filepath: File path to Excel EPC file
    Returns:
        EUI:  Energy Use Intensity in kWhr/m^2/yr 
        
"""
ghenv.Component.Name = "Honeybee_ExportEPC"
ghenv.Component.NickName = 'Export to EPC'
ghenv.Component.Message = 'VER 0.0.55\nOCT_17_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "12 | WIP"
#compatibleHBVersion = VER 0.0.55\nSEP_30_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Grasshopper.Kernel as gh
import math
import clr
clr.AddReference('Microsoft.Office.Interop.Excel') 
import Microsoft.Office.Interop.Excel as Excel
from System.Runtime.InteropServices import Marshal


def main(HBZones):
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first Honeybee to fly...")
        return
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this component." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return
        
    hb_hive = sc.sticky["honeybee_Hive"]()
    
    # Call Honeybee zones from the lib
    HBZones = hb_hive.callFromHoneybeeHive(HBZones)
    
    # create an empty dictionary
    # the structure should be as {type : {construction: { orientation : {area of opaque : area , area of glass : area}}}
    srfData = {}
    
    # produce division angles - keep it to 8 directions for now 
    divisionAngles = rs.frange(0- (360/8), 360 -(360/8), 360/8)
    #print divisionAngles
    
    # iterate through faces and add them to the dictionary
    for HBZone in HBZones:
        for srfCount, HBSrf in enumerate(HBZone.surfaces):
            # let's add it to the dictionary
            # I need to know what is the type of the surface (wall, roof, ?)
            # HBSrf.type will l, # srf.type == 1 #roof, # int(srf.type) == 2 #floor
            # print "type: ", HBSrf.type
            srfType = int(HBSrf.type)
            
            # I add the key to the dictionary if it is not there yet
            if not srfData.has_key(srfType): srfData[srfType] = {}
            
            # let's find the construction next as your workflow is based on different construction types
            # you can get it form a Honeybee surface using HBSrf.EPConstruction
            # print "EP construction: ", HBSrf.EPConstruction
            constr = HBSrf.EPConstruction
            
            if not srfData[srfType].has_key(constr):
                # create a place holder for this construction and put the initial area as 0
                srfData[srfType][constr] = {}
            
            # now let's find the direction of the surface
            # in case of roof or floor orientation doesn't really matter (or does it?)
            # so I just add it to dictionary and consider orientation as 0
            if  srfType!=0:
                direction = 0
            else:
                # otherwise we need to find the direction of the surface
                # you can use HBSrf.angle2North to get it
                #print "angle: ", HBSrf.angle2North
                # check and see where it stands, 0 will be north, 1 is NE, etc. 
                # print HBSrf.angle2North
                for direction in range(len(divisionAngles)-1):
                    if divisionAngles[direction]+(0.5*45) <= HBSrf.angle2North%360 <= divisionAngles[direction +1]+(0.5*45):
                        # here we found the direction
                        break            
            # Now that we know direction let's make an empty dictionary for that
            if not srfData[srfType][constr].has_key(direction):
                srfData[srfType][constr][direction] = {}
                srfData[srfType][constr][direction]["area"] = 0
                # in case surface has glazing then create a place holder with
                # type 5 reperesnts glazing
                if HBSrf.hasChild:
                    if not srfData.has_key(5):
                        srfData[5] = {}
                    # this is tricky here as I assume that all the glazing in the same wall
                    # has same construction and I pick the first one - we can change this later if needed
                    glzConstr = HBSrf.childSrfs[0].EPConstruction
                    if not srfData[5].has_key(glzConstr):
                        srfData[5][glzConstr] = {}
                    if not srfData[5][glzConstr].has_key(direction):
                        srfData[5][glzConstr][direction] = {}
                        srfData[5][glzConstr][direction]["area"] = 0 
            # add the area to the current area
            # Honeybee has methods that return area for opaque and glazed area
            #print "Opaque area: ", HBSrf.getOpaqueArea()
            #print "Glazing area: ", HBSrf.getGlazingArea()
            srfData[srfType][constr][direction]["area"] += HBSrf.getOpaqueArea()
            if HBSrf.hasChild:
                srfData[5][HBSrf.childSrfs[0].EPConstruction][direction]["area"] += HBSrf.getGlazingArea()
    # return surface data
    return srfData
    # done!
#print srfData
srfTypeDict = {0: "Wall", 1 : "Roof", 2: "Floor", 5 : "Glazing"}
directionDict = {0: "N", 1 : "NW", 2: "W", 3: "SW", 4 : "S", 5 : "SE", 6 : "E", 7 : "NE"}


#setting initial values of overall variables
roofA = []
floorA = []
glazingA = []
glazingO = []
wallsA = []
wallsO = []

#Setting intial values for glazing area orientation variables
GlazAreaSouth=0
GlazAreaSouthEast=0
GlazAreaEast=0
GlazAreaNorthEast=0
GlazAreaNorth=0
GlazAreaNorthWest=0
GlazAreaWest=0
GlazAreaSouthWest=0

#Setting intial values for opaque area orientation variables
AreaSouth=0
AreaSouthEast =0
AreaEast=0
AreaNorthEast=0
AreaNorth=0
AreaNorthWest=0
AreaWest=0
AreaSouthWest=0


#Sorting Surface Properties
if len(_HBZones)!=0 and _HBZones[0]!=0:
    srfData = main(_HBZones)
    #print srfData
    if srfData != -1:
        # now that you have the dictionary you can iterate and produce the lists that you wanted
        # you only need to remember the structure of dictionary - you can modify the structure to
        # be easier to iterate but I thought the current structure is easier to read
        for srfType in srfData.keys():
            for constr in srfData[srfType].keys():
                for orientation in range(8):
                    # if direction is not there it means the area is 0
                    if not srfData[srfType][constr].has_key(orientation):
                        continue
                        print " surfaces " + \
                              constr + "; facing " + \
                              directionDict[orientation] + ","+ " 0 "
                    else:
                        if srfType == 1:
                            roofarea = int(srfData[srfType][constr][orientation]["area"])
                            roofA.append(roofarea)
                        if srfType == 2:
                            floorarea = int(srfData[srfType][constr][orientation]["area"])
                            floorA.append(floorarea)
                        if srfType == 5:
                            glazingarea = int(srfData[srfType][constr][orientation]["area"])
                            glazingA.append(glazingarea)
                            glazingorientation = directionDict[orientation]
                            glazingO.append(glazingorientation)
                            if glazingorientation == "N":
                                GlazAreaNorth = GlazAreaNorth + glazingarea
                            if glazingorientation == "NW":
                                GlazAreaNorthWest = GlazAreaNorthWest + glazingarea
                            if glazingorientation == "W":
                                GlazAreaWest = GlazAreaWest + glazingarea
                            if glazingorientation == "SW":
                                GlazAreaSouthWest = GlazAreaSouthWest + glazingarea
                            if glazingorientation == "S":
                                GlazAreaSouth = GlazAreaSouth + glazingarea
                            if glazingorientation == "SE":
                                GlazAreaSouthEast = GlazAreaSouthEast + glazingarea
                            if glazingorientation == "E":
                                GlazAreaEast = GlazAreaEast + glazingarea
                            if glazingorientation == "NE":
                                GlazAreaNorthEast = GlazAreaNorthEast + glazingarea
                            #print glazingO
                        if srfType == 0:
                            wallsarea = int(srfData[srfType][constr][orientation]["area"])
                            wallsA.append(wallsarea)
                            wallsorientation = directionDict[orientation]
                            wallsO.append(wallsorientation)
                            if wallsorientation == "N":
                                AreaNorth = AreaNorth + wallsarea
                            if wallsorientation == "NW":
                                AreaNorthWest = AreaNorthWest + wallsarea
                            if wallsorientation == "W":
                                AreaWest = AreaWest + wallsarea
                            if wallsorientation == "SW":
                                AreaSouthWest = AreaSouthWest + wallsarea
                            if wallsorientation == "S":
                                AreaSouth = AreaSouth + wallsarea
                            if wallsorientation == "SE":
                                AreaSouthEast = AreaSouthEast + wallsarea
                            if wallsorientation == "E":
                                AreaEast = AreaEast + wallsarea
                            if wallsorientation == "NE":
                                AreaNorthEast = AreaNorthEast + wallsarea
                            #print wallsO

roofArea = roofA[0]
print roofArea
floorArea =floorA[0]
print floorArea
"""
print glazingA
print glazingO 
print wallsA 
print wallsO 
print "opaque area"
print AreaSouth
print AreaSouthEast
print AreaEast
print AreaNorthEast
print AreaNorth
print AreaNorthWest
print AreaWest
print AreaSouthWest
print "glazing area"
print GlazAreaSouth
print GlazAreaSouthEast
print GlazAreaEast
print GlazAreaNorthEast
print GlazAreaNorth
print GlazAreaNorthWest
print GlazAreaWest
"""

##Function to swap variables back and forth
def variables(roofArea, floorArea, AreaSouth, AreaSouthEast, AreaEast, AreaNorth, AreaNorthWest, AreaWest, AreaSouthWest,GlazAreaSouth, GlazAreaSouthEast, GlazAreaEast, GlazAreaNorth, GlazAreaNorthWest, GlazAreaWest, GlazAreaSouthWest):
   ##Input
   ex.Sheets("INPUT").Activate
   #overall areas
   ex.Worksheets("INPUT").Cells(58,7).Value = roofArea
   ex.Worksheets("INPUT").Cells(10,7).Value = floorArea
   #ex.Worksheets("INPUT").Cells(14,3).Value = volume
   #ex.Worksheets("INPUT").Cells(15,3).Value = height
   #opaque area
   ex.Worksheets("INPUT").Cells(50,7).Value = AreaSouth
   ex.Worksheets("INPUT").Cells(51,7).Value = AreaSouthEast
   ex.Worksheets("INPUT").Cells(52,7).Value = AreaEast
   ex.Worksheets("INPUT").Cells(53,7).Value = AreaNorthEast
   ex.Worksheets("INPUT").Cells(54,7).Value = AreaNorth
   ex.Worksheets("INPUT").Cells(55,7).Value = AreaNorthWest
   ex.Worksheets("INPUT").Cells(56,7).Value = AreaWest
   ex.Worksheets("INPUT").Cells(57,7).Value = AreaSouthWest
   #glazing area
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaSouth
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaSouthEast
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaEast
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaNorthEast
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaNorth
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaNorthWest
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaWest
   ex.Worksheets("INPUT").Cells(50,7).Value = GlazAreaSouthWest




#####Opening the EPC####
ex = Marshal.GetActiveObject("Excel.Application")
filenameActive = ex.ActiveWorkbook
print filenameActive

if filenameActive == None:
   #Getting Excel Started
   ex = Excel.ApplicationClass()
   ex.Visible = True #Set True to make file visible to user
   ex.DisplayAlerts = False #Set to ingore error
   #opening a workbook
   filepathfull = filepath +filename
   workbook = ex.Workbooks.Open(filepathfull)
   print "I did it"
   variables(roofArea, floorArea, AreaSouth, AreaSouthEast, AreaEast, AreaNorth, AreaNorthWest, AreaWest, AreaSouthWest,GlazAreaSouth, GlazAreaSouthEast, GlazAreaEast, GlazAreaNorth, GlazAreaNorthWest, GlazAreaWest, GlazAreaSouthWest)

elif filenameActive != None:
   print "I didn't do it"
   variables(roofArea, floorArea, AreaSouth, AreaSouthEast, AreaEast, AreaNorth, AreaNorthWest, AreaWest, AreaSouthWest,GlazAreaSouth, GlazAreaSouthEast, GlazAreaEast, GlazAreaNorth, GlazAreaNorthWest, GlazAreaWest, GlazAreaSouthWest)

##Result
ex.Sheets("RESULT").Activate
ResultEUI = ex.Worksheets("RESULT").Cells[42,3]
EUI = ResultEUI.Value()
#print EUI
