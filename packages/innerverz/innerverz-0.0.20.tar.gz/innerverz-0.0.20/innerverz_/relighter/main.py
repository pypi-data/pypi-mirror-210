import os
import sys
sys.path.append('../')

import torch
import torch.nn as nn
import torch.nn.functional as F


from .nets import MyGenerator

from torchvision.transforms.functional import to_tensor, rgb_to_grayscale
from ..utils import check_ckpt_exist, get_url_id

class ReLighter(nn.Module):
    def __init__(self, folder_name='relighter', ckpt_name = 'G_129k.pt', force=False, device = 'cuda'):
        """
        Input
        --------
        - masked_gray_face
            - dtype : tensor
            - shape : (b, 1, 512, 512)
            - min max (-1 1)
            
        - relight_detail_shape
            - dtype : tensor
            - shape : (b, 1, 512, 512)
            - min max : (-1 1)
            
        - code_dict
            - dtype : dict
            
        - id_param
            - dtype : tensor
            - shape : (b 512)
        
        Output
        --------
        - result
            - dtype : tensor
            - shape : (b, 1 , 512, 512)
            - min max : (-1 1)
        """
        super(ReLighter, self).__init__()
        self.device = device
        
        self.img_size = 512
        self.generator = MyGenerator().to(self.device)

        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        
        ckpt = torch.load(os.path.join(ckpt_path), map_location=self.device)
        self.generator.load_state_dict(ckpt['model'])
        for param in self.generator.parameters():
            param.requires_grad = False
        self.generator.eval()
        del ckpt

    def relight(self,):
        return

    # source light -> target light
    def forward(self, masked_gray_face, relight_detail_shape, code_dict, id_param, output_size=None):
        _, _, origin_h, origin_w = masked_gray_face.shape
        
        masked_gray_face = F.interpolate(masked_gray_face, (self.img_size, self.img_size), mode='bilinear')
        relight_detail_shape = F.interpolate(relight_detail_shape, (self.img_size, self.img_size), mode='bilinear')
        
        params = torch.cat((code_dict['light'].view(1, -1), code_dict['cam'].view(1, -1), code_dict['pose'].view(1, -1), code_dict['detail'].view(1, -1), id_param), dim=-1)
        res = self.generator(masked_gray_face, relight_detail_shape, params)
        result = (res + masked_gray_face).clip(-1,1)
        
        if output_size == None:
            _result = F.interpolate(result, (origin_h, origin_w), mode='bilinear')
            _res = F.interpolate(res, (origin_h, origin_w), mode='bilinear')
        else:
            _result = F.interpolate(result, (output_size, output_size), mode='bilinear')
            _res = F.interpolate(res, (output_size, output_size), mode='bilinear')
        
        return _result, _res
        