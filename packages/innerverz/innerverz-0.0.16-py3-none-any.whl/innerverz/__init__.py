"""
# Dataprocess
--------

from innerverz import Data_Process

DP = Data_Process()


# deblurrer
--------

from innerverz import DeBlurrer  

DB = DeBlurrer()    

# deca
--------

from innerverz import DECA

deca = DECA() 

# deep3dmm
--------

from innerverz import Deep3DMM

D3 = Deep3DMM()

# face_alignment(ffhq, invz)
--------

from innerverz import FaceAligner

FA = FaceAligner('ffhq')

# face color tranfser
--------

from innerverz import IWCT

iwct = IWCT()

# face enhancer
--------

from innerverz import FaceEnhancer

FE = FaceEnhancer()

# face parser
---------

from innerverz import FaceParser

FP = FaceParser()

# head color transfer
--------

from innerverz import HWCT

hwct = HWCT()

# id extractor
--------

from innerverz import IdExtractor

IE = IdExtractor()

# relighter
--------

from innerverz import ReLighter

RL = ReLighter()

# upsampler
--------
from innerverz import Upsampler

US = Upsampler()

# video_faceparser
--------

from innerverz import Video_FaceParser

V_FP = Video_FaceParser()


"""

from .deblurrer import *
from .data_process import *
from .upsampler import *
from .deep3dmm import *
from .face_alignment import *
from .head_color_transfer import *
from .id_extractor import *
from .face_parser import *
from .utils import *
from .face_color_transfer import *
from .deca import *
from .face_enhancer import *
from .relighter import *
from .video_faceparser import *