#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2015-2017, Sarith Subramaniam <sarith@sarith.in> 
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
This component can be used to specify a lamp of custom chromaticity, color or color temperature. 
.
If _lampName is specified from an existing list of lamps (which can be seen by hovering over the _lampName input), then the chromaticity associated with the lamp will be used.
.
In case _lampName isn't present in the list,a lamp with chromaticity corresponding to 3200K will be defined.
.
If case the custom lamp is being defined by specifying _colorTemp_ or _xCor,_yCor_, it is recommended that the lampDetails output be connected to a text panel for displaying the chromaticity and color temperature of the lamp.
.
In case of a conflict, input options on the top will override inputs below them.
-
-
Technical Notes:
----------------------
The Color Matching Functions used for calculations were obtained from Wyszecki, Gunter, and Walter Stanley Stiles. Color science. Vol. 8. New York: Wiley, 1982.
.
The calculation of CCT and Duv are based on: Ohno, Yoshi. Practical use and calculation of CCT and Duv. Leukos 10.1 (2014): 47-55.
.
CCT calculations should be within +/- 0.1 % margin of error. The Planckian Table used for calculations is based on a 1% step-size.
.
While (x,y), (u,v) or (u'v') coordinates may be specified for any valid location on the chromaticity diagram, CCT and Duv will only be displayed if the absolute value of Duv is less than or equal to 0.02.
.
.
!!WARNING !!
------------------
The colors specified in this component only affect the luminance and chromaticity of the light source. 
The color fidelity or gamut area of the source cannot be modified by this component.
So, color fidelity metrics such as CRI cannot be considered in these calculations.

    Args:
        _lampName: Specify a name for the lamp.The name can be a predefined lamp name or any other name.
        _
        The following lamp names are predefined. The values in parenthesis are the x,y 1931 chromaticity coordinates and lumen depreciation values.:
                clear metal halide    (0.396, 0.39, 0.8)
                cool white            (0.376, 0.368, 0.85)
                cool white deluxe     (0.376, 0.368, 0.85)
                deluxe cool white     (0.376, 0.368, 0.85)
                deluxe warm white     (0.44, 0.403, 0.85)
                fluorescent           (0.376, 0.368, 0.85)
                halogen               (0.4234, 0.399, 1)
                incandescent          (0.453, 0.405, 0.95)
                mercury               (0.373, 0.415, 0.8)
                metal halide          (0.396, 0.39, 0.8)
                quartz                (0.424, 0.399, 1)
                sodium                (0.569, 0.421, 0.93)
                warm white            (0.44, 0.403, 0.85)
                warm white deluxe     (0.44, 0.403, 0.85)
                xenon                 (0.324, 0.324, 1)
         _
         For example,specifying "cool white" (without the quotes) as input will set the x,y,Lumen Depreciation values to 0.376, 0.368 and 0.85 respectively. 
         _
         Specifying an arbitrary name like "lampx" will create a lamp with x,y,lumen depreciation values of 0.333,0.333 and 1 respectively. These values can then be modified by specifying _colorTemp_ or _xCor_ and _yCor_ or _rgbColors_.
         
        _colorTemp_: Specify a color temperature for the lamp.The color temperature will be used to calculate the chromatcity coordinates of the lamp on the CIE 1931 xy diagram. Lumen depreciation factor for the lamp can be set by specifying a value for the _deprFactor_ input. Valid values for color temperature are from 1000 to 25000.
        
        _xCor_: Specify a chromaticity coordinate for the lamp. The default coordinate is the x coordinate for the CIE 1931 Color Space.
        _yCor_: Specify a chromaticity coordinate for the lamp. The default coordinate is the y coordinate for the CIE 1931 Color Space.
        _colorSpace_: Specify a color space for the chromaticity coordinates. The values and their corresponding color spaces are
                     0 - CIE 1931 Color Space (default)
                     1 - CIE 1960 Color Space
                     2 - CIE 1976 Color Space
        _deprFactor_: Lamp lumen depreciation factor.
        _rgbColors_ : Specify a (r,g,b) color value using either the Grasshopper Colour Swatch (preferred) or a text panel. If the alpha value for the Colour Swatch is set to a value other than 255 then that value will be multiplied with the _deprFactor_.
    
    Returns:
        lampDetails: Information about the lamp defined as per the input parameters.
        customLamp: Connect this to the customLamp_ input in the Honeybee_IES Luminaire option.
"""        



from __future__ import division
import Grasshopper.Kernel as gh
import math
import scriptcontext as sc

ghenv.Component.Name = "Honeybee_IES Custom Lamp"
ghenv.Component.NickName = 'iesCustomLamp'
ghenv.Component.Message = 'VER 0.0.64\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Light Source"
#compatibleHBVersion = VER 0.0.56\nJUL_01_2016
#compatibleLBVersion = VER 0.0.59\nJUL_01_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



class customLampData:
    
    def __init__(self,lamp):
        self.lamp = lamp
    
    def __repr__(self):
        return "Honeybee.customLamp"


lampNames = {'clear metal halide':(.396,.39,.8),'cool white deluxe':(.376,.368,.85),'deluxe cool white':(.376,.368,.85),
            'deluxe warm white':(.440,.403,.85),'fluorescent': (.376,.368,.85),'incandescent': (.453,.405,.95),
            'mercury':(.373,.415,.8),'metal halide':(.396,.390,.8),'halogen':(.4234,.399,1),'quartz':(.424,.399,1),'sodium':(.569,.421,.93),
            'warm white deluxe':(.440,.403,.85),'xenon':(.324,.324,1),'warm white':(0.440,0.403,0.85),'cool white':(0.376,0.368,0.85)}


#CIE 1931 2deg CMFs 
#Wyszecki, Gunter, and Walter Stanley Stiles. Color science. Vol. 8. New York: Wiley, 1982. 
#Table I(3.3.1) pgs 725-735 & CS Table I(4.3.2) pgs 789-790
cmfs = {360:(0.000130,0.000004,0.000606), 361:(0.000146,0.000004,0.000681), 362:(0.000164,0.000005,0.000765), 
363:(0.000184,0.000006,0.000860), 364:(0.000207,0.000006,0.000967), 365:(0.000232,0.000007,0.001086), 
366:(0.000261,0.000008,0.001221), 367:(0.000293,0.000009,0.001373), 368:(0.000329,0.000010,0.001544), 
369:(0.000370,0.000011,0.001734), 370:(0.000415,0.000012,0.001946), 371:(0.000464,0.000014,0.002178), 
372:(0.000519,0.000016,0.002436), 373:(0.000582,0.000017,0.002732), 374:(0.000655,0.000020,0.003078), 
375:(0.000742,0.000022,0.003486), 376:(0.000845,0.000025,0.003975), 377:(0.000965,0.000028,0.004541), 
378:(0.001095,0.000032,0.005158), 379:(0.001231,0.000035,0.005803), 380:(0.001368,0.000039,0.006450), 
381:(0.001502,0.000043,0.007083), 382:(0.001642,0.000047,0.007745), 383:(0.001802,0.000052,0.008501), 
384:(0.001996,0.000057,0.009415), 385:(0.002236,0.000064,0.010550), 386:(0.002535,0.000072,0.011966), 
387:(0.002893,0.000082,0.013656), 388:(0.003301,0.000094,0.015588), 389:(0.003753,0.000106,0.017730), 
390:(0.004243,0.000120,0.020050), 391:(0.004762,0.000135,0.022511), 392:(0.005330,0.000151,0.025203), 
393:(0.005979,0.000170,0.028280), 394:(0.006741,0.000192,0.031897), 395:(0.007650,0.000217,0.036210), 
396:(0.008751,0.000247,0.041438), 397:(0.010029,0.000281,0.047504), 398:(0.011422,0.000319,0.054120), 
399:(0.012869,0.000357,0.060998), 400:(0.014310,0.000396,0.067850), 401:(0.015704,0.000434,0.074486), 
402:(0.017147,0.000473,0.081362), 403:(0.018781,0.000518,0.089154), 404:(0.020748,0.000572,0.098540), 
405:(0.023190,0.000640,0.110200), 406:(0.026207,0.000725,0.124613), 407:(0.029782,0.000826,0.141702), 
408:(0.033881,0.000941,0.161304), 409:(0.038468,0.001070,0.183257), 410:(0.043510,0.001210,0.207400), 
411:(0.048996,0.001362,0.233692), 412:(0.055023,0.001531,0.262611), 413:(0.061719,0.001720,0.294775), 
414:(0.069212,0.001935,0.330799), 415:(0.077630,0.002180,0.371300), 416:(0.086958,0.002455,0.416209), 
417:(0.097177,0.002764,0.465464), 418:(0.108406,0.003118,0.519695), 419:(0.120767,0.003526,0.579530), 
420:(0.134380,0.004000,0.645600), 421:(0.149358,0.004546,0.718484), 422:(0.165396,0.005159,0.796713), 
423:(0.181983,0.005829,0.877846), 424:(0.198611,0.006546,0.959439), 425:(0.214770,0.007300,1.039050), 
426:(0.230187,0.008087,1.115367), 427:(0.244880,0.008909,1.188497), 428:(0.258777,0.009768,1.258123), 
429:(0.271808,0.010664,1.323930), 430:(0.283900,0.011600,1.385600), 431:(0.294944,0.012573,1.442635), 
432:(0.304897,0.013583,1.494804), 433:(0.313787,0.014630,1.542190), 434:(0.321645,0.015715,1.584881), 
435:(0.328500,0.016840,1.622960), 436:(0.334351,0.018007,1.656405), 437:(0.339210,0.019214,1.685296), 
438:(0.343121,0.020454,1.709875), 439:(0.346130,0.021718,1.730382), 440:(0.348280,0.023000,1.747060), 
441:(0.349600,0.024295,1.760045), 442:(0.350147,0.025610,1.769623), 443:(0.350013,0.026959,1.776264), 
444:(0.349287,0.028351,1.780433), 445:(0.348060,0.029800,1.782600), 446:(0.346373,0.031311,1.782968), 
447:(0.344262,0.032884,1.781700), 448:(0.341809,0.034521,1.779198), 449:(0.339094,0.036226,1.775867), 
450:(0.336200,0.038000,1.772110), 451:(0.333198,0.039847,1.768259), 452:(0.330041,0.041768,1.764039), 
453:(0.326636,0.043766,1.758944), 454:(0.322887,0.045843,1.752466), 455:(0.318700,0.048000,1.744100), 
456:(0.314025,0.050244,1.733560), 457:(0.308884,0.052573,1.720858), 458:(0.303290,0.054981,1.705937), 
459:(0.297258,0.057459,1.688737), 460:(0.290800,0.060000,1.669200), 461:(0.283970,0.062602,1.647529), 
462:(0.276721,0.065278,1.623413), 463:(0.268918,0.068042,1.596022), 464:(0.260423,0.070911,1.564528), 
465:(0.251100,0.073900,1.528100), 466:(0.240848,0.077016,1.486111), 467:(0.229851,0.080266,1.439522), 
468:(0.218407,0.083667,1.389880), 469:(0.206812,0.087233,1.338736), 470:(0.195360,0.090980,1.287640), 
471:(0.184214,0.094918,1.237422), 472:(0.173327,0.099046,1.187824), 473:(0.162688,0.103367,1.138761), 
474:(0.152283,0.107885,1.090148), 475:(0.142100,0.112600,1.041900), 476:(0.132179,0.117532,0.994198), 
477:(0.122570,0.122674,0.947347), 478:(0.113275,0.127993,0.901453), 479:(0.104298,0.133453,0.856619), 
480:(0.095640,0.139020,0.812950), 481:(0.087300,0.144676,0.770517), 482:(0.079308,0.150469,0.729445), 
483:(0.071718,0.156462,0.689914), 484:(0.064581,0.162718,0.652105), 485:(0.057950,0.169300,0.616200), 
486:(0.051862,0.176243,0.582329), 487:(0.046282,0.183558,0.550416), 488:(0.041151,0.191274,0.520338), 
489:(0.036413,0.199418,0.491967), 490:(0.032010,0.208020,0.465180), 491:(0.027917,0.217120,0.439925), 
492:(0.024144,0.226735,0.416184), 493:(0.020687,0.236857,0.393882), 494:(0.017540,0.247481,0.372946), 
495:(0.014700,0.258600,0.353300), 496:(0.012162,0.270185,0.334858), 497:(0.009920,0.282294,0.317552), 
498:(0.007967,0.295051,0.301338), 499:(0.006296,0.308578,0.286169), 500:(0.004900,0.323000,0.272000), 
501:(0.003777,0.338402,0.258817), 502:(0.002945,0.354686,0.246484), 503:(0.002425,0.371699,0.234772), 
504:(0.002236,0.389288,0.223453), 505:(0.002400,0.407300,0.212300), 506:(0.002926,0.425630,0.201169), 
507:(0.003837,0.444310,0.190120), 508:(0.005175,0.463394,0.179225), 509:(0.006982,0.482940,0.168561), 
510:(0.009300,0.503000,0.158200), 511:(0.012149,0.523569,0.148138), 512:(0.015536,0.544512,0.138376), 
513:(0.019478,0.565690,0.128994), 514:(0.023993,0.586965,0.120075), 515:(0.029100,0.608200,0.111700), 
516:(0.034815,0.629346,0.103905), 517:(0.041120,0.650307,0.096667), 518:(0.047985,0.670875,0.089983), 
519:(0.055379,0.690842,0.083845), 520:(0.063270,0.710000,0.078250), 521:(0.071635,0.728185,0.073209), 
522:(0.080462,0.745464,0.068678), 523:(0.089740,0.761969,0.064568), 524:(0.099456,0.777837,0.060788), 
525:(0.109600,0.793200,0.057250), 526:(0.120167,0.808110,0.053904), 527:(0.131115,0.822496,0.050747), 
528:(0.142368,0.836307,0.047753), 529:(0.153854,0.849492,0.044899), 530:(0.165500,0.862000,0.042160), 
531:(0.177257,0.873811,0.039507), 532:(0.189140,0.884962,0.036936), 533:(0.201169,0.895494,0.034458), 
534:(0.213366,0.905443,0.032089), 535:(0.225750,0.914850,0.029840), 536:(0.238321,0.923735,0.027712), 
537:(0.251067,0.932092,0.025694), 538:(0.263992,0.939923,0.023787), 539:(0.277102,0.947225,0.021989), 
540:(0.290400,0.954000,0.020300), 541:(0.303891,0.960256,0.018718), 542:(0.317573,0.966007,0.017240), 
543:(0.331438,0.971261,0.015864), 544:(0.345483,0.976023,0.014585), 545:(0.359700,0.980300,0.013400), 
546:(0.374084,0.984092,0.012307), 547:(0.388640,0.987481,0.011302), 548:(0.403378,0.990313,0.010378), 
549:(0.418312,0.992812,0.009529), 550:(0.433450,0.994950,0.008750), 551:(0.448795,0.996711,0.008035), 
552:(0.464336,0.998098,0.007382), 553:(0.480064,0.999112,0.006785), 554:(0.495971,0.999748,0.006243), 
555:(0.512050,1.000000,0.005750), 556:(0.528296,0.999857,0.005304), 557:(0.544692,0.999305,0.004900), 
558:(0.561209,0.998326,0.004534), 559:(0.577822,0.996899,0.004202), 560:(0.594500,0.995000,0.003900), 
561:(0.611221,0.992601,0.003623), 562:(0.627976,0.989743,0.003371), 563:(0.644760,0.986444,0.003141), 
564:(0.661570,0.982724,0.002935), 565:(0.678400,0.978600,0.002750), 566:(0.695239,0.974084,0.002585), 
567:(0.712059,0.969171,0.002439), 568:(0.728828,0.963857,0.002309), 569:(0.745519,0.958135,0.002197), 
570:(0.762100,0.952000,0.002100), 571:(0.778543,0.945450,0.002018), 572:(0.794826,0.938499,0.001948), 
573:(0.810926,0.931163,0.001890), 574:(0.826825,0.923458,0.001841), 575:(0.842500,0.915400,0.001800), 
576:(0.857933,0.907006,0.001766), 577:(0.873082,0.898277,0.001738), 578:(0.887894,0.889205,0.001711), 
579:(0.902318,0.879782,0.001683), 580:(0.916300,0.870000,0.001650), 581:(0.929800,0.859861,0.001610), 
582:(0.942798,0.849392,0.001564), 583:(0.955278,0.838622,0.001514), 584:(0.967218,0.827581,0.001459), 
585:(0.978600,0.816300,0.001400), 586:(0.989386,0.804795,0.001337), 587:(0.999549,0.793082,0.001270), 
588:(1.009089,0.781192,0.001205), 589:(1.018006,0.769155,0.001147), 590:(1.026300,0.757000,0.001100), 
591:(1.033983,0.744754,0.001069), 592:(1.049860,0.732422,0.001049), 593:(1.047188,0.720004,0.001036), 
594:(1.052467,0.707497,0.001021), 595:(1.056700,0.694900,0.001000), 596:(1.059794,0.682219,0.000969), 
597:(1.061799,0.669472,0.000930), 598:(1.062807,0.656674,0.000887), 599:(1.062910,0.643845,0.000843), 
600:(1.062200,0.631000,0.000800), 601:(1.067352,0.618156,0.000761), 602:(1.058444,0.605314,0.000724), 
603:(1.055224,0.592476,0.000686), 604:(1.050977,0.579638,0.000645), 605:(1.045600,0.566800,0.000600), 
606:(1.039037,0.553961,0.000548), 607:(1.031361,0.541137,0.000492), 608:(1.022666,0.528353,0.000435), 
609:(1.013048,0.515632,0.000383), 610:(1.002600,0.503000,0.000340), 611:(0.991368,0.490469,0.000307), 
612:(0.979331,0.478030,0.000283), 613:(0.966492,0.465678,0.000265), 614:(0.952848,0.453403,0.000252), 
615:(0.938400,0.441200,0.000240), 616:(0.923194,0.429080,0.000230), 617:(0.907244,0.417036,0.000221), 
618:(0.890502,0.405032,0.000212), 619:(0.872920,0.393032,0.000202), 620:(0.854450,0.381000,0.000190), 
621:(0.835084,0.368918,0.000174), 622:(0.814946,0.356827,0.000156), 623:(0.794186,0.344777,0.000136), 
624:(0.772954,0.332818,0.000117), 625:(0.751400,0.321000,0.000100), 626:(0.729584,0.309338,0.000086), 
627:(0.707589,0.297850,0.000075), 628:(0.685602,0.286594,0.000065), 629:(0.663810,0.275625,0.000057), 
630:(0.642400,0.265000,0.000050), 631:(0.621515,0.254763,0.000044), 632:(0.601114,0.244890,0.000039), 
633:(0.581105,0.235334,0.000036), 634:(0.561398,0.226053,0.000033), 635:(0.541900,0.217000,0.000030), 
636:(0.522600,0.208162,0.000028), 637:(0.503546,0.199549,0.000026), 638:(0.484744,0.191155,0.000024), 
639:(0.466194,0.182974,0.000022), 640:(0.447900,0.175000,0.000020), 641:(0.429861,0.167224,0.000018), 
642:(0.412098,0.159646,0.000016), 643:(0.394644,0.152278,0.000014), 644:(0.377533,0.145126,0.000012), 
645:(0.360800,0.138200,0.000010), 646:(0.344456,0.131500,0.000008), 647:(0.328517,0.125025,0.000005), 
648:(0.313019,0.118779,0.000003), 649:(0.298001,0.112769,0.000001), 650:(0.283500,0.107000,0.000000), 
651:(0.269545,0.101476,0.000000), 652:(0.256118,0.096189,0.000000), 653:(0.243190,0.091123,0.000000), 
654:(0.230727,0.086265,0.000000), 655:(0.218700,0.081600,0.000000), 656:(0.207097,0.077121,0.000000), 
657:(0.195923,0.072826,0.000000), 658:(0.185171,0.068710,0.000000), 659:(0.174832,0.064770,0.000000), 
660:(0.164900,0.061000,0.000000), 661:(0.155367,0.057396,0.000000), 662:(0.146230,0.053955,0.000000), 
663:(0.137490,0.050674,0.000000), 664:(0.129147,0.047550,0.000000), 665:(0.121200,0.044580,0.000000), 
666:(0.113640,0.041759,0.000000), 667:(0.106465,0.039085,0.000000), 668:(0.099690,0.036564,0.000000), 
669:(0.093331,0.034200,0.000000), 670:(0.087400,0.032000,0.000000), 671:(0.081901,0.029963,0.000000), 
672:(0.076804,0.028077,0.000000), 673:(0.072077,0.026329,0.000000), 674:(0.067687,0.024708,0.000000), 
675:(0.063600,0.023200,0.000000), 676:(0.059807,0.021801,0.000000), 677:(0.056282,0.020501,0.000000), 
678:(0.052971,0.019281,0.000000), 679:(0.049819,0.018121,0.000000), 680:(0.046770,0.017000,0.000000), 
681:(0.043784,0.015904,0.000000), 682:(0.040875,0.014837,0.000000), 683:(0.038073,0.013811,0.000000), 
684:(0.035405,0.012835,0.000000), 685:(0.032900,0.011920,0.000000), 686:(0.030564,0.011068,0.000000), 
687:(0.028381,0.010273,0.000000), 688:(0.026345,0.009533,0.000000), 689:(0.024453,0.008846,0.000000), 
690:(0.022700,0.008210,0.000000), 691:(0.021084,0.007624,0.000000), 692:(0.019600,0.007085,0.000000), 
693:(0.018237,0.006591,0.000000), 694:(0.016987,0.006138,0.000000), 695:(0.015840,0.005723,0.000000), 
696:(0.014791,0.005343,0.000000), 697:(0.013831,0.004996,0.000000), 698:(0.012949,0.004676,0.000000), 
699:(0.012129,0.004380,0.000000), 700:(0.011359,0.004102,0.000000), 701:(0.010629,0.003838,0.000000), 
702:(0.009939,0.003589,0.000000), 703:(0.009288,0.003354,0.000000), 704:(0.008679,0.003134,0.000000), 
705:(0.008111,0.002929,0.000000), 706:(0.007582,0.002738,0.000000), 707:(0.007089,0.002560,0.000000), 
708:(0.006627,0.002393,0.000000), 709:(0.006195,0.002237,0.000000), 710:(0.005790,0.002091,0.000000), 
711:(0.005410,0.001954,0.000000), 712:(0.005053,0.001825,0.000000), 713:(0.004718,0.001704,0.000000), 
714:(0.004404,0.001590,0.000000), 715:(0.004109,0.001484,0.000000), 716:(0.003834,0.001384,0.000000), 
717:(0.003576,0.001291,0.000000), 718:(0.003334,0.001204,0.000000), 719:(0.003109,0.001123,0.000000), 
720:(0.002899,0.001047,0.000000), 721:(0.002704,0.000977,0.000000), 722:(0.002523,0.000911,0.000000), 
723:(0.002354,0.000850,0.000000), 724:(0.002197,0.000793,0.000000), 725:(0.002049,0.000740,0.000000), 
726:(0.001911,0.000690,0.000000), 727:(0.001781,0.000643,0.000000), 728:(0.001660,0.000599,0.000000), 
729:(0.001546,0.000558,0.000000), 730:(0.001440,0.000520,0.000000), 731:(0.001340,0.000484,0.000000), 
732:(0.001246,0.000450,0.000000), 733:(0.001158,0.000418,0.000000), 734:(0.001076,0.000389,0.000000), 
735:(0.001000,0.000361,0.000000), 736:(0.000929,0.000335,0.000000), 737:(0.000862,0.000311,0.000000), 
738:(0.000801,0.000289,0.000000), 739:(0.000743,0.000268,0.000000), 740:(0.000690,0.000249,0.000000), 
741:(0.000641,0.000231,0.000000), 742:(0.000595,0.000215,0.000000), 743:(0.000552,0.000199,0.000000), 
744:(0.000512,0.000185,0.000000), 745:(0.000476,0.000172,0.000000), 746:(0.000442,0.000160,0.000000), 
747:(0.000412,0.000149,0.000000), 748:(0.000383,0.000138,0.000000), 749:(0.000357,0.000129,0.000000), 
750:(0.000332,0.000120,0.000000), 751:(0.000310,0.000112,0.000000), 752:(0.000289,0.000104,0.000000), 
753:(0.000270,0.000097,0.000000), 754:(0.000252,0.000091,0.000000), 755:(0.000235,0.000085,0.000000), 
756:(0.000219,0.000079,0.000000), 757:(0.000205,0.000074,0.000000), 758:(0.000191,0.000069,0.000000), 
759:(0.000178,0.000064,0.000000), 760:(0.000166,0.000060,0.000000), 761:(0.000155,0.000056,0.000000), 
762:(0.000145,0.000052,0.000000), 763:(0.000135,0.000049,0.000000), 764:(0.000126,0.000045,0.000000), 
765:(0.000117,0.000042,0.000000), 766:(0.000110,0.000040,0.000000), 767:(0.000102,0.000037,0.000000), 
768:(0.000095,0.000034,0.000000), 769:(0.000089,0.000032,0.000000), 770:(0.000083,0.000030,0.000000), 
771:(0.000078,0.000028,0.000000), 772:(0.000072,0.000026,0.000000), 773:(0.000067,0.000024,0.000000), 
774:(0.000063,0.000023,0.000000), 775:(0.000059,0.000021,0.000000), 776:(0.000055,0.000020,0.000000), 
777:(0.000051,0.000018,0.000000), 778:(0.000048,0.000017,0.000000), 779:(0.000044,0.000016,0.000000), 
780:(0.000042,0.000015,0.000000), 781:(0.000039,0.000014,0.000000), 782:(0.000036,0.000013,0.000000), 
783:(0.000034,0.000012,0.000000), 784:(0.000031,0.000011,0.000000), 785:(0.000029,0.000011,0.000000), 
786:(0.000027,0.000010,0.000000), 787:(0.000026,0.000009,0.000000), 788:(0.000024,0.000009,0.000000), 
789:(0.000022,0.000008,0.000000), 790:(0.000021,0.000007,0.000000), 791:(0.000019,0.000007,0.000000), 
792:(0.000018,0.000006,0.000000), 793:(0.000017,0.000006,0.000000), 794:(0.000016,0.000006,0.000000), 
795:(0.000015,0.000005,0.000000), 796:(0.000014,0.000005,0.000000), 797:(0.000013,0.000005,0.000000), 
798:(0.000012,0.000004,0.000000), 799:(0.000011,0.000004,0.000000), 800:(0.000010,0.000004,0.000000), 
801:(0.000010,0.000003,0.000000), 802:(0.000009,0.000003,0.000000), 803:(0.000008,0.000003,0.000000), 
804:(0.000008,0.000003,0.000000), 805:(0.000007,0.000003,0.000000), 806:(0.000007,0.000002,0.000000), 
807:(0.000006,0.000002,0.000000), 808:(0.000006,0.000002,0.000000), 809:(0.000005,0.000002,0.000000), 
810:(0.000005,0.000002,0.000000), 811:(0.000005,0.000002,0.000000), 812:(0.000004,0.000002,0.000000), 
813:(0.000004,0.000001,0.000000), 814:(0.000004,0.000001,0.000000), 815:(0.000004,0.000001,0.000000), 
816:(0.000003,0.000001,0.000000), 817:(0.000003,0.000001,0.000000), 818:(0.000003,0.000001,0.000000), 
819:(0.000003,0.000001,0.000000), 820:(0.000003,0.000001,0.000000), 821:(0.000002,0.000001,0.000000), 
822:(0.000002,0.000001,0.000000), 823:(0.000002,0.000001,0.000000), 824:(0.000002,0.000001,0.000000), 
825:(0.000002,0.000001,0.000000), 826:(0.000002,0.000001,0.000000), 827:(0.000002,0.000001,0.000000), 
828:(0.000001,0.000001,0.000000), 829:(0.000001,0.000000,0.000000), 830:(0.000001,0.000000,0.000000)}




c1 = 3.7417749E-16
c2 = 1.4388E-2
exp = math.e
wavelengths = {wavelength:wavelength*(10**-9) for wavelength in range(360,831)}

def calcXY1931(CT):
    """
        Calculate 1931 x,y coordinates from color temperature
    """
    spectralPower560 = c1*(wavelengths[560]**(-5))*(1/(exp**(c2/(CT*wavelengths[560]))-1))
    spectralPowers = {idx:c1*(wavelengths[idx]**(-5))*(1/(exp**(c2/(CT*wavelengths[idx]))-1))/spectralPower560 for idx in range(360,831)}
    
    triX = sum([683*cmfs[idx][0]*spectralPowers[idx] for idx in range(360,831)])
    triY = sum([683*cmfs[idx][1]*spectralPowers[idx] for idx in range(360,831)])
    triZ = sum([683*cmfs[idx][2]*spectralPowers[idx] for idx in range(360,831)])
    x,y = triX/(triX+triY+triZ),triY/(triX+triY+triZ)
    x,y = map(lambda x:round(x,8),(x,y))
    return x,y

def colorCoord(a,b,year):
    """
        Take x,y or u,v or u','v coordinates along with the CIE diagram year and return all three coordinates.
    """
    coords = {1931:None,1960:None,1976:None}
    
    if year == 1931:
        coords[1931]=(a,b)
        u = (4*a)/(-2*a+12*b+3)
        v = (6*b)/(-2*a+12*b+3)
        coords[1960]=(u,v)
        coords[1976]=(u,v*1.5)
    
    if year == 1960:
        coords[1960]=(a,b)
        coords[1976]=(a,b*1.5)
        x = 9*a/(6*a-16*b*1.5+12)
        y = 4*b*1.5/(6*a-16*b*1.5+12)
        coords[1931]=(x,y)
    
    if year == 1976:
        coords[1976]=(a,b)
        coords[1960]=(a,b/1.5)
        x = 9*a/(6*a-16*b+12)
        y = 4*b/(6*a-16*b+12)
        coords[1931]=(x,y)
    
    #Round everything to four significant digits.
    for years in coords:
        coords[years]=map(lambda x:round(x,8),coords[years])
    return coords


def planckianTable(uSrc,vSrc):
    
    temp = 1000
    table = []
    counter = 1
    while temp<100000:
        temp *= 1.01
        x,y = calcXY1931(temp)
        u,v = colorCoord(x,y,1931)[1960]
        di = math.sqrt((uSrc-u)**2+(vSrc-v)**2)
        table.append((temp,u,v,di,counter))
        counter += 1
    return table

def calcCct(a,b,year):
    u,v = colorCoord(a,b,year)[1960]
    planckTable = planckianTable(u,v)
    
    #lambda function that returns -1 if the value of x is less than 0 and 1 if it is greater than 0.
    sign = lambda x:-1 if x<0 else 1
    
    #get the d values and get the location of the lowest d value.
    dTable = [col[3] for col in planckTable]
    minD = min(dTable)
    minIndex = dTable.index(minD)
    
    try:
        #extract the row of the planckian table at minimum d and also the rows above and below.
        ptPlus1 = planckTable[minIndex+1]
        ptMin = planckTable[minIndex]
        ptMinus1= planckTable[minIndex-1]
    except IndexError: #If the CCT value is too high then the minimum d will probably the last value.
        return 10000,0.1
        
    #temp,u,v,di,counter
    
    dp1 = ptPlus1[3]
    dm1 = ptMinus1[3]
    dm = ptMin[3]
    tm1,tp1,tm = ptMinus1[0],ptPlus1[0],ptMin[0]
    
    um1,vm1 = ptMinus1[1:3]
    up1,vp1 = ptPlus1[1:3]

    
    l = math.sqrt((um1-up1)**2+(vm1-vp1)**2)
    
    x = (dm1**2 - dp1**2 + l**2)/2
    
    vtx = vm1 + (vp1-vm1)*x/l
    
    signVal = sign(v-vtx)

    
    
    #Triangular solution.
    TxTri = tm1 + (tp1-tm1)*(x/l)
    DuvTri = math.sqrt(dm1**2-x**2)*signVal
    
    
    
    #Parabolic solution.
    X = (tp1-tm)*(tm1-tp1)*(tm-tm1)
    
    a = (tm1*(dp1-dm)+tm*(dm1-dp1)+tp1*(dm-dm1))*(X**-1)
    b = -((tm1**2)*(dp1-dm)+(tm**2)*(dm1-dp1)+(tp1**2)*(dm-dm1))*(X**-1)
    c = -(dm1*(tp1-tm)*tm*tp1+dm*(tm1-tp1)*tm1*tp1+dp1*(tm-tm1)*tm1*tm)*(X**-1)
   
    Tx = -b/(2*a)
    Txcor = Tx * 0.99991
    Duv = signVal*(a*Txcor**2+b*Txcor+c)
   
    if abs(Duv) < 0.002:
        return TxTri,DuvTri
    else:
        return Tx,Duv

w = gh.GH_RuntimeMessageLevel.Warning

lampData = {'whiteLamp':None,
            'rgbLamp':None}
inputData = {"lampName":False,"colorTemp":False,"xy":False,"RGB":False}

inputData['lampName']=False
if _colorTemp_:
    inputData['colorTemp']=True
if _xCor_ and _yCor_:         
    inputData['xy']=True
if  _rgbColors_:
    inputData['RGB']=True
    
if _lampName:
            _lampName = _lampName.strip()        
            if _deprFactor_ is None:
                _deprFactor_ = 1.0
            
            lamp_ = _lampName.strip()
            
            for value,replacement in (("  "," "),("'",""),('"',"")):
                while value in lamp_:
                    lamp_ = lamp_.replace(value,replacement)
            
            lampLowerCase = lamp_.lower()
            
            #In case the name is among the defined names.
            if lampLowerCase in lampNames.keys():

                lamp_ = '{}'.format(lamp_.lower())
                
                #The code with lampdata[] is meant to test which all inputs have been defined by the user. This will be used to print a report later.
                inputData['lampName']=True
                    
                    
                x,y,lumDepr = lampNames[lamp_]
                cor = colorCoord(x,y,1931)
                uv1960 = cor[1960]
                uv1976 = cor[1976]
                CCT,Duv = calcCct(x,y,1931)
                lampData['whiteLamp'] = {'name':_lampName,'x':x,'y':y,'deprFactor':_deprFactor_,'u':uv1960[0],'v':uv1960[1],"u'":uv1976[0],"v'":uv1976[1],'CCT':CCT,'Duv':Duv}
            else:
                if _colorTemp_:
                    assert 1000<=_colorTemp_<=25000,"The color temperature value should be between 1000 and 25000." 
                    
                    
                    x,y = calcXY1931(_colorTemp_)
                    lumDepr =_deprFactor_
                    cor = colorCoord(x,y,1931)
                    uv1960 = cor[1960]
                    uv1976 = cor[1976]
                    CCT,Duv = _colorTemp_,0.0
                    lampData['whiteLamp'] = {'name':_lampName,'x':x,'y':y,'deprFactor':_deprFactor_,'u':uv1960[0],'v':uv1960[1],"u'":uv1976[0],"v'":uv1976[1],'CCT':CCT,'Duv':Duv}
                elif (not _colorTemp_) and (_xCor_ and _yCor_):
                    if not _colorSpace_:
                        _colorSpace_ = 0
                    else:
                        assert _colorSpace_ in range(3),"The value for _colorSpace_ should 0, 1 or 2. 0 implies 1931 CIE Color Space, 1 implies 1960 CIE Color Space, 2 implies 1976 CIE Color Space."
                    
                    year = {0:1931,1:1960,2:1976}[_colorSpace_]
                    cor = colorCoord(_xCor_,_yCor_,year)
                    
                    x,y = cor[1931]
                    u,v = cor[1960]
                    u1,v1 = cor[1976]
                    
                    CCT,Duv = calcCct(x,y,1931)
                    if abs(Duv)>0.02:
                        CCT = "NA"
                        Duv = "NA"
                    lampData['whiteLamp'] = {'name':_lampName,'x':x,'y':y,'deprFactor':_deprFactor_,'u':u,'v':v,"u'":u1,"v'":v1,'CCT':CCT,'Duv':Duv}
                elif (not _colorTemp_) and (not (_xCor_ and _yCor_)) and _rgbColors_:
                   
                    r,g,b,a = _rgbColors_.R,_rgbColors_.G,_rgbColors_.B,_rgbColors_.A
                    r,g,b,a = map(lambda color:round(float(color)/255.0,4),(r,g,b,a))
                    lampData['rgbLamp']={'name':_lampName,'r':r,'g':g,'b':b,'deprFactor':_deprFactor_*a}
                else:
                    x,y = calcXY1931(3200)
                    cor = colorCoord(x,y,1931)
                    x,y = cor[1931]
                    u,v = cor[1960]
                    u1,v1 = cor[1976]
                    CCT,Duv = 3200,0.0
                    lampData['whiteLamp'] = {'name':_lampName,'x':x,'y':y,'deprFactor':_deprFactor_,'u':u,'v':v,"u'":u1,"v'":v1,'CCT':CCT,'Duv':Duv}
                    
            
            varDict = {'colorTemp':'_colorTemp_','xy':'_xCor_,_yCor_,_colorSpace_','RGB':'_rgbColors_','lampName':'_lampName'}
            outputs = [varDict[val] for val in inputData if inputData[val]]
            
            if len(outputs)>1:
                print("The priority of inputs is from top to bottom.\n")
            if inputData['lampName']:
                inputData.pop('lampName')
                outputs = [varDict[val] for val in inputData if inputData[val]]
                print("Since the _lampName provided by you is in the list of predefined lamps the 1931 x,y coordinates and lumen depreciation factor for {} lamp will be applied to the customLamp\n".format(_lampName.strip()))
                print("The input for _lampName_ will override the inputs for the following paramters: {}".format(" ".join(outputs)))
                
            elif inputData['colorTemp']:
                inputData.pop('colorTemp')
                outputs = [varDict[val] for val in inputData if inputData[val]]
                print("The customLamp will be defined as per the _colorTemp_ input of {}".format(_colorTemp_))
                if outputs:
                    print("The input for _colorTemp_ will override the inputs for the following paramters: {}".format(" ".join(outputs)))
            elif inputData['xy']:
                inputData.pop('colorTemp')
                inputData.pop('xy')
                outputs = [varDict[val] for val in inputData if inputData[val]]
                x,y,year = 'x','y',1931
                if _colorSpace_ == 1:
                    x,y,year = 'u','v',1960
                if _colorSpace_ == 2:
                    x,y,year = "u'","v'",1976
                    
                print("The customLamp will be defined as per the following chromaticity coordinates : ({},{}) = ({},{}) for the {} CIE Color Space.".format(x,y,_xCor_,_yCor_,year))
                if outputs:
                    print("The input for _xCor_ and _yCor_ will override the input for _rgbColors_")
            elif inputData['RGB']:
                print("The customLamp will be defined as per the input given for _rgbColors_")
            else:
                print("Since no outputs for color modification were specified a default lamp color with a Color Temperature of 3200K has been specified")
            
            lampName = [lampData[lampType]['name'] for lampType in lampData if lampData[lampType]][0]
            
            
            lampDetails = "Lamp Name: {}\n\n".format(lampName)
            
            if lampData['rgbLamp']:
                lampDetails += "Lamp Definition Type: RGB Colored lamp\n\n"
                r,g,b =lampData['rgbLamp']['r'],lampData['rgbLamp']['g'],lampData['rgbLamp']['b']
                aSwatch = _rgbColors_.A/255.0
                a = lampData['rgbLamp']['deprFactor']
                lampDetails += "R,G,B = ({:.3f},{:.3f},{:.3f})\n\n".format(r,g,b)
                lampDetails += "Lumen Depreciation Factor = {:.3f} x {:.3f} = {:.3f}".format(aSwatch,_deprFactor_,a)
            else:
                lampDetails += "Lamp Definition Type: Lamp defined as per chromaticity coordinates or color temperature.\n\n"
                if _colorTemp_:
                    lampDetails += "Color Temperature= {:.2f} (CCT will be the same as the color temperature.)\n".format(_colorTemp_)
                    lampDetails += "Duv = {:.2f}\n\n".format(float(0.0))
                else:
                    cctVal = lampData['whiteLamp']['CCT']
                    duvVal = lampData['whiteLamp']['Duv']
                    if cctVal == "NA":
                        lampDetails += "The specified color chromaticity coordinates does not lie within +/- 0.02 Duv.\n"
                        lampDetails += "Results from CCT and Duv calculations will only be displayed if the Duv is within +/- 0.02 Duv.\n"
                    else:            
                        lampDetails += "Correlated Color Temperature (CCT) = {:.2f}\n".format(float(lampData['whiteLamp']['CCT']))
                        lampDetails += "Duv = {:.6f}\n".format(float(duvVal))
                    lampDetails+="\n"
                    
                    
                lampDetails += "x,y CIE 1931 Chromaticity Coordinates = ({:.4f},{:.4f})\n\n".format(lampData['whiteLamp']['x'],lampData['whiteLamp']['y'])
                
                lampDetails += "u,v CIE 1960 Chromaticity Coordinates = ({:.4f},{:.4f})\n\n".format(lampData['whiteLamp']['u'],lampData['whiteLamp']['v'])
                
                lampDetails += "u',v' CIE 1976 Chromaticity Coordinates = ({:.4f},{:.4f})\n\n".format(lampData['whiteLamp']["u'"],lampData['whiteLamp']["v'"])
                
                lampDetails += "Lumen Depreciation Factor = {:.3f}".format(_deprFactor_)

            customLamp = customLampData(lampData)


if sc.sticky.has_key('honeybee_release'):
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): pass
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): pass
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)

