# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert a mesh to RAD file
-
Provided by Honeybee 0.0.53
    
    Args:
        _mesh: List of meshes
        _RADMaterial: Full string of rad material as the base material
        HDRTexture_: Optional file path to HDR file to be used as a texture. Use Human plugin to map HDR image on mesh
        _workingDir_: Working directory
        _radFileName_: Radiance file name
        _writeRad: Set to True to convert mesh to rad
    Returns:
        materialFile: Path to material file
        radianceFile: Path to radiance file
"""

ghenv.Component.Name = "Honeybee_MSH2RAD"
ghenv.Component.NickName = 'MSH2RAD'
ghenv.Component.Message = 'VER 0.0.53\nAUG_01_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino as rc
import Grasshopper.Kernel as gh
import shutil
import os
import scriptcontext as sc
import time


class MSHToRAD(object):
    
    def __init__(self, mesh, fileName = None, workingDir = None, bitmap = None, radMaterial = None):
        
        if fileName == None:
            fileName = "unnamed"
        
        self.name = fileName
        
        if workingDir == None:
            workingDir = sc.sticky["Honeybee_DefaultFolder"]
        
        workingDir = os.path.join(workingDir, fileName, "MSH2RADFiles")
        if not os.path.isdir(workingDir): os.mkdir(workingDir)
        self.workingDir = workingDir
        
        self.mesh = mesh
        
        self.pattern = bitmap
        if self.pattern != None:
            # create material name based on bitmap
            bitmapFileName = os.path.basename(self.pattern)
            self.matName = ".".join(bitmapFileName.split(".")[:-1])
            #copy the image into same folder
            shutil.copyfile(self.pattern, os.path.join(self.workingDir, bitmapFileName))
        
        else:
            self.matName = "radMaterial"
            
        self.RADMaterial = radMaterial
        
    def meshToObj(self):
        objFilePath = os.path.join(self.workingDir, self.name + ".obj")
        
        with open(objFilePath, "w") as outfile:
            
            # objTxt = "# OBJ file written by TurtlePyMesh\n\n"
            outfile.write("# OBJ file written by TurtlePyMesh\n\n")
            
            # add material file name
            mtlFile = self.name + ".mtl"
            #objTxt += "mtllib " + mtlFile + "\n"
            outfile.write("mtllib " + mtlFile + "\n")
            
            for count, Tmesh in enumerate(self.mesh):
                # add object name - for this version I keep it all as a single object
                #objTxt += "o object_" + str(count + 1) + "\n"
                outfile.write("o object_" + str(count + 1) + "\n")
                
                # add material name - for now brick as test
                #objTxt += "usemtl " + matName + "\n"
                outfile.write("usemtl " + self.matName + "\n")
                
                # add vertices
                for v in Tmesh.Vertices:
                    XYZ = v.X, v.Y, v.Z
                    XYZ = map(str, XYZ)
                    vString = " ".join(XYZ)
                    #objTxt += "v "  + vString + "\n"
                    outfile.write("v "  + vString + "\n")
                # add texture vertices
                for vt in Tmesh.TextureCoordinates:
                    XY = vt.X, vt.Y
                    XY = map(str, XY)
                    vtString = " ".join(XY)
                    #objTxt += "vt "  + vtString + "\n"
                    outfile.write("vt "  + vtString + "\n")
                # add normals
                for vn in Tmesh.Normals:
                    XYZ = vn.X, vn.Y, vn.Z
                    XYZ = map(str, XYZ)
                    vnString = " ".join(XYZ)
                    # objTxt += "vn "  + vnString + "\n"
                    outfile.write("vn "  + vnString + "\n")
                # add faces
                # vertices number is global so the number should be added together
                fCounter = 0
                
                if count > 0:
                    for meshCount in range(count):
                        fCounter += self.mesh[meshCount].Vertices.Count
                
                # print fCounter
                if self.pattern != None:
                    for face in Tmesh.Faces:
                        # objTxt += "f " + "/".join(3*[`face.A  + fCounter + 1`]) + " " + "/".join(3*[`face.B + fCounter + 1`]) + " " + "/".join(3*[`face.C + fCounter + 1`])
                        outfile.write("f " + "/".join(3*[`face.A  + fCounter + 1`]) + " " + "/".join(3*[`face.B + fCounter + 1`]) + " " + "/".join(3*[`face.C + fCounter + 1`]))
                        if face.IsQuad:
                            #objTxt += " " + "/".join(3*[`face.D + fCounter + 1`])
                            outfile.write(" " + "/".join(3*[`face.D + fCounter + 1`]))
                            
                        #objTxt += "\n"
                        outfile.write("\n")
                else:
                    for face in Tmesh.Faces:
                        outfile.write("f " + "//".join(2 * [`face.A  + fCounter + 1`]) + \
                                      " " + "//".join(2 * [`face.B + fCounter + 1`]) + \
                                      " " + "//".join(2 * [`face.C + fCounter + 1`]))
                        
                        if face.IsQuad:
                            outfile.write(" " + "//".join( 2 * [`face.D + fCounter + 1`]))
                            
                        #objTxt += "\n"
                        outfile.write("\n")
                        
        # This method happened to be so slow!
        #    with open(objFile, "w") as outfile:
        #        outfile.writelines(objTxt)
        
        return objFilePath
    
    def getPICImageSize(self):
        with open(self.pattern, "rb") as inf:
            for count, line in enumerate(inf):
                #print line
                if line.strip().startswith("-Y") and line.find("-X"):
                    Y, YSize, X, XSize = line.split(" ")
                    return XSize, YSize
    
    def objToRAD(self, objFile):
        # prepare file names
        radFile = objFile.replace(".obj", ".rad")
        mshFile = objFile.replace(".obj", ".msh")
        batFile = objFile.replace(".obj", ".bat")        
        
        path, fileName = os.path.split(radFile)
        matFile = os.path.join(path, "material_" + fileName)
        
        try:
            materialType = self.RADMaterial.split("\n")[0].split(" ")[1]
            materialTale = "\n".join(self.RADMaterial.split("\n")[1:])
        except Exception, e:
            # to be added here: if material is not full string then get it from the library
            print "material error..." + `e`
            return        
        
        # create material file
        if self.pattern != None:
            
            # find aspect ratio
            try:
                X, Y= self.getPICImageSize()
                ar = str(int(X)/int(Y))
            except Exception, e:
                ar = str(1)
            
            # mesh has a pattern
            patternName = ".".join(os.path.basename(self.pattern).split(".")[:-1])
            
            materialStr = "void colorpict " + patternName + "_pattern\n" + \
                  "7 red green blue " + self.pattern + " . (" + ar + "*(Lu-floor(Lu))) (Lv-floor(Lv)) \n" + \
                  "0\n" + \
                  "1 1\n" + \
                  patternName + "_pattern " + materialType + " " + patternName + "\n" + \
                  materialTale
        else:
            materialStr = "void "  + materialType + " " + self.matName + "\n" + \
                  materialTale  
                  
        # write material to file
        with open(matFile, "w") as outfile:
            outfile.write(materialStr)
        
        # create rad file
        
        if self.pattern != None:
            cmd = "c:\\radiance\\bin\\obj2mesh -a " + matFile + " " + objFile + " > " +  mshFile
            
            with open(batFile, "w") as outfile:
                outfile.write(cmd)
                #outfile.write("\npause")
                
            os.system(batFile)
            
            radStr = "void mesh painting\n" + \
                     "1 " + mshFile + "\n" + \
                     "0\n" + \
                     "0\n"
            
            with open(radFile, "w") as outfile:
                outfile.write(radStr)
        else:
            # use object to rad
            #create a fake mtl file - material will be overwritten by radiance material
            mtlFile = objFile.replace(".obj", ".mtl")
            
            mtlStr = "# Honeybee\n" + \
                     "newmtl " + self.matName + "\n" + \
                     "Ka 0.0000 0.0000 0.0000\n" + \
                     "Kd 1.0000 1.0000 1.0000\n" + \
                     "Ks 1.0000 1.0000 1.0000\n" + \
                     "Tf 0.0000 0.0000 0.0000\n" + \
                     "d 1.0000\n" + \
                     "Ns 0\n"
            
            with open(mtlFile, "w") as mtlf:
                mtlf.write(mtlStr)
            
            # create a map file
            #mapFile = objFile.replace(".obj", ".map")
            #with open(mapFile, "w") as mapf:
            #    mapf.write(self.matName + " (Object \"" + self.matName + "\");")
            #cmd = "c:\\radiance\\bin\\obj2rad -m " + mapFile + " " + objFile + " > " +  radFile
            
            cmd = "c:\\radiance\\bin\\obj2rad " + objFile + " > " +  radFile
            
            with open(batFile, "w") as outfile:
                outfile.write(cmd)
                #outfile.write("\npause")
                
            os.system(batFile)
            
        time.sleep(.2)
    
        return matFile, radFile

def main(mesh, radFileName, workingDir, RADMaterial, HDRTexture = None):
    
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return None, None
        
    meshToRadiance = MSHToRAD(mesh, radFileName, workingDir, HDRTexture, RADMaterial)
    objFile = meshToRadiance.meshToObj()
    materialFile, radianceFile = meshToRadiance.objToRAD(objFile)
    
    return materialFile, radianceFile


if _writeRAD and _mesh and _mesh[0]!=None and _RADMaterial:
    
    materialFile, radianceFile = main(_mesh, _radFileName_, _workingDir_, _RADMaterial)
    