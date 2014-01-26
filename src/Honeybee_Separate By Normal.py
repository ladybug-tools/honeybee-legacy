import Rhino as rc
import scriptcontext as sc
import math

ghenv.Component.Name = "Honeybee_Separate By Normal"
ghenv.Component.NickName = 'separateByNormal'
ghenv.Component.Message = 'VER 0.0.42\nJAN_24_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

def separateByNormal(geometry, maximumRoofAngle = 30, maximumFloorAngle = 30):
    
    def getSrfCenPtandNormal(surface):
        MP = rc.Geometry.AreaMassProperties.Compute(surface)
        area = None
        if MP:
            centerPt = MP.Centroid
            MP.Dispose()
        else:
            print 'MP Failed'
            return
        
        bool, centerPtU, centerPtV = surface.ClosestPoint(centerPt)

        if bool: normalVector = surface.Faces[0].NormalAt(centerPtU, centerPtV)
        else: normalVector = surface.Faces[0].NormalAt(0,0)
        
        return centerPt, normalVector
    
    up = []
    down = []
    side = []
    
    # explode zone
    for i in range(geometry.Faces.Count):
        
        surface = geometry.Faces[i].DuplicateFace(False)
        # find the normal
        findNormal = getSrfCenPtandNormal(surface)
        
        if findNormal:
            normal = findNormal[1]
            angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
        else:
            angle2Z = 0
        
        if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
            up.append(surface)
        
        elif  180 - maximumFloorAngle < angle2Z < 180 + maximumFloorAngle:
            down.append(surface)
        
        else:
            side.append(surface)
    
    return up, down, side
    
    

if _geometry!=None:
    if _maxUpDecAngle_ == None: _maxUpDecAngle_ = 30
    if _maxDownDecAngle_ == None: _maxDownDecAngle_ = 30
    lookingUp, lookingDown, lookingSide = separateByNormal(_geometry, _maxUpDecAngle_, _maxDownDecAngle_)