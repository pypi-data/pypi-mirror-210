import os
import sys
sys.path.append('../')
import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F

import torchvision.transforms as transforms

from .nets import MyGenerator
from ..utils import check_ckpt_exist, convert_image_type, get_url_id


class HWCT(nn.Module):
    
    def __init__(self, img_size : int = 512, folder_name='head_color_transfer', ckpt_name = 'G_128_512_head_60k.pt', force=False, device='cuda'):
        '''
        Related Links
        --------
        https://github.com/jmliu88/HeSer

        Methods
        --------
        - forward
            - Input
                - source_rgb
                    - dtype : tensor
                    - shape : (b, 3, 512, 512)
                    - min max : (-1, 1)
                - target_rgb  
                    - if you only have gray scale image, you should repeat gray scale image's channel to fit amount of rgb channel amount
                    - dtype : tensor
                    - shape : (b, 3, 512, 512)
                    - min max : (-1, 1)
                - source_onehot
                    - dtype : tensor
                    - shape : (b, 19, 512, 512)
                    - min max : (0 or 1)
                - target_onehot
                    - dtype : tensor
                    - shape : (b, 19, 512, 512)
                    - min max : (0 or 1)
                - target_gray
                    - dtype : tensor
                    - shape : (b, 1, 512, 512)
                    - min max : (-1, 1)
                - target_face_mask
                    - dtype : tensor
                    - shape : (b, 1, 512, 512)
                    - min max : (0 or 1)
                
            - Output
                - result
                    - shape : (1, 3, 512, 512)
                    - min max : (-1, 1)
                - color reference map
                    - shape : (1, 3, 512, 512))
                    - min max : (-1, 1)
        
        '''
        super(HWCT, self).__init__()
        self.img_size = img_size
        self.device = device
        self.generator = MyGenerator().to(self.device)
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
       
        self.generator.load_state_dict(ckpt['model'], strict=True)
        for param in self.generator.parameters():
            param.requires_grad = False
        self.generator.eval()
        del ckpt

    def forward(self, source_rgb, target_rgb, source_onehot, target_onehot, target_gray, target_face_mask, output_size=None):
        """
        Input
        ---------
            - source_rgb
                - dtype : tensor
                - shape : (b, 3, 512, 512)
                - min max : (-1, 1)
            - target_rgb  
                - if you only have gray scale image, you should repeat gray scale image's channel to fit amount of rgb channel amount
                - dtype : tensor
                - shape : (b, 3, 512, 512)
                - min max : (-1, 1)
            - source_onehot
                - dtype : tensor
                - shape : (b, 19, 512, 512)
                - min max : (0 or 1)
            - target_onehot
                - dtype : tensor
                - shape : (b, 19, 512, 512)
                - min max : (0 or 1)
            - target_gray
                - dtype : tensor
                - shape : (b, 1, 512, 512)
                - min max : (-1, 1)
            - target_face_mask
                - dtype : tensor
                - shape : (b, 1, 512, 512)
                - min max : (0 or 1)
            
        Output
        ---------
            - result
                - shape : (1, 3, 512, 512)
                - min max : (-1, 1)
            - color reference map
                - shape : (1, 3, 512, 512))
                - min max : (-1, 1)
        """
        _, _, origin_h, origin_w = source_rgb.shape
        source_rgb = F.interpolate(source_rgb, (self.img_size, self.img_size), mode='bilinear')
        target_rgb = F.interpolate(target_rgb, (self.img_size, self.img_size), mode='bilinear')
        source_onehot = F.interpolate(source_onehot, (self.img_size, self.img_size), mode='nearest')
        target_onehot = F.interpolate(target_onehot, (self.img_size, self.img_size), mode='nearest')
        target_gray = F.interpolate(target_gray, (self.img_size, self.img_size), mode='bilinear')
        target_face_mask = F.interpolate(target_face_mask, (self.img_size, self.img_size), mode='nearest')
        
        result, color_reference_map = self.generator(source_rgb, target_rgb, source_onehot, target_onehot, target_gray, target_face_mask)
        
        if output_size == None:
            result = F.interpolate(result, (origin_h, origin_w), mode='bilinear')
            color_reference_map = F.interpolate(color_reference_map, (origin_h, origin_w), mode='bilinear')
        else:
            result = F.interpolate(result, (output_size, output_size), mode='bilinear')
            color_reference_map = F.interpolate(color_reference_map, (output_size, output_size), mode='bilinear')
        
        return result, color_reference_map
        