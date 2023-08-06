import numpy as np
import cv2
from PIL import Image
from typing import Union


def convert_image_type(source, target='pillow'):
    assert target in ['pillow','cv2'], 'check target type!'
    
    type_str = str(type(source))
    # check image type
    if 'str' in type_str :
        source_type = 'path'
    elif 'PIL' in type_str:
        source_type = 'pillow'
    elif 'numpy' in type_str:
        source_type = 'cv2'
    
    # convert image type
    if source_type == 'path':
        if target == 'pillow':
            image = Image.open(source).convert("RGB")
        elif target == 'cv2':
            image = cv2.imread(source)
    elif source_type == 'pillow':
        if target == 'pillow':
            image = source
        elif target == 'cv2':
            image = np.array(source)[:,:,::-1]
    elif source_type == 'cv2':
        if target == 'pillow':
            image = Image.fromarray(source[:,:,::-1]).convert("RGB")
        elif target == 'cv2':
            image = source
    return image