#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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



"""
Convert Image
-
Provided by Honeybee 0.0.64
    
    Args:
        _imageFilePath: Path to an image file(BMP, GIF, JPEG, PNG, TIFF)
        _targetImageType_: 0>"BMP", 1>"GIF", 2>"Jpeg", 3>"PNG", 4>"TIFF"
    Returns:
        convertedFilePath: New file path
"""

ghenv.Component.Name = "Honeybee_Convert IMG"
ghenv.Component.NickName = 'IMG>IMG'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
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