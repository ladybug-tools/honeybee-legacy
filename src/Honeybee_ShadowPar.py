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
EnergyPlus Shadow Parameters
-
Provided by Honeybee 0.0.64

    Args:
        calculationMethod_: An optional text string to set the means by which the shadow calculation is run.  Choose from the following two options:
            1 - AverageOverDaysInFrequency - A shadow calculation that averages over multiple days (as opposed to running it for each timeStep).  This is the default setting.
            2 - TimestepFrequency - A shadow calculation that computes the incoming solar energy at every single timestep of the simulation.  Note that this option is only needed for certain cases and can increase execution time significantly.
        frequency_: An optional number that represents the frequency in days with which shadows are re-computed in the AverageOverDaysInFrequency calculation method.  The default is set to 30 days (meaning that the shadow calulation is performed every 30 days and this average over this period is used to represent all 30 days in the energy simulation).
        maximumFigure_: An optional number that is greater than 200, which represents the maximum number of points to be used in the shadow calculation.  The default is set to 3000 points but this may need to be increased significantly if you have a lot of small context geometry in your model.
    Returns:
        shadowPar: Shadow calculation parameters that can be plugged into the "Honeybee_Energy Simulation Par" component.
"""

ghenv.Component.Name = "Honeybee_ShadowPar"
ghenv.Component.NickName = 'shadowPar'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "10 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


def main(calculationMethod, frequency, maximumFigure):
    # I will add check for inputs later
    if calculationMethod== None:
        calculationMethod = "AverageOverDaysInFrequency"
        #"TimestepFrequency"
    if frequency == None: frequency =  30
    if maximumFigure == None: maximumFigure = 3000

    return calculationMethod, frequency, maximumFigure
    

shadowPar = main(calculationMethod_, frequency_, maximumFigure_)