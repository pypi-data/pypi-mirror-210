import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from ..utils import check_ckpt_exist, convert_image_type, get_url_id
from .nets import MyGenerator

class DeBlurrer(nn.Module):
    def __init__(self, size=1024, folder_name='deblurrer', ckpt_name='G_1024_65000.pt', force=False, device='cuda'):
        super(DeBlurrer, self).__init__()
        self.device = device
        self.size = size
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
        
        self.deblurrer = MyGenerator().to(self.device)
        self.deblurrer.load_state_dict(ckpt['model'])
        for param in self.deblurrer.parameters():
            param.requires_grad = False
        self.deblurrer.eval()
        del ckpt

    def forward(self, tensor_image, output_size=None):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
            
            
        Output
        ---------
            - dtype : tensor
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
        """
        _, _, origin_h, origin_w = tensor_image.shape
        tensor_image = F.interpolate(tensor_image, (self.size, self.size), mode='bilinear')
        fake, fake_res, edge = self.deblurrer(tensor_image)
        if output_size == None:
            _fake = F.interpolate(fake, (origin_h, origin_w), mode='bilinear')
            _fake_res = F.interpolate(fake_res, (origin_h, origin_w), mode='bilinear')
            _edge = F.interpolate(edge, (origin_h, origin_w), mode='bilinear')
        else:
            _fake = F.interpolate(fake, (output_size, output_size), mode='bilinear')
            _fake_res = F.interpolate(fake_res, (output_size, output_size), mode='bilinear')
            _edge = F.interpolate(edge, (output_size, output_size), mode='bilinear')
        return _fake, _fake_res, _edge
