# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.


"""
Convert Image
-
Provided by Honeybee 0.0.55
    
    Args:
        _imageFilePath: Path to an image file(BMP, GIF, JPEG, PNG, TIFF)
        _targetImageType_: 0>"BMP", 1>"GIF", 2>"Jpeg", 3>"PNG", 4>"TIFF"
    Returns:
        convertedFilePath: New file path
"""

ghenv.Component.Name = "Honeybee_Convert IMG"
ghenv.Component.NickName = 'IMG>IMG'
ghenv.Component.Message = 'VER 0.0.55\nSEP_11_2014'
ghenv.Component.Category = "Honeybee@DL"
ghenv.Component.SubCategory = "05 | WIP"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import clr
clr.AddReference("System.Drawing")

from System.Drawing import Image
from System.Drawing.Imaging import ImageFormat
import os

imageFromat = { 0 : ImageFormat.Bmp,
1 : ImageFormat.Gif,
2 : ImageFormat.Jpeg,
3 : ImageFormat.Png,
4 : ImageFormat.Tiff,
}

imageExt = { 0 : "BMP",
1 : "GIF",
2 : "Jpeg",
3 : "PNG",
4 : "TIFF",
}

def main(imageFilePath, targetImageType):
    try:
        filePath, ext = os.path.splitext(imageFilePath)
        img = Image.FromFile(imageFilePath)
        
        targetEx = imageExt[targetImageType%5]
        
        # make sure target ext is not same as input!
        if targetEx.lower()!= ext[1:].lower():
            outputFilePath = ".".join([filePath, targetEx])
            img.Save(outputFilePath, imageFromat[targetImageType%5])
        
            return outputFilePath
            
    except Exception, e:
        return "something went wrong: " + str(e)
        
if _imageFilePath:
    convertedFilePath = main(_imageFilePath, _targetImageType_)