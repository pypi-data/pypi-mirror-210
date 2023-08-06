import sys
from .nets import SwinIR
import torch
from torch import nn
import torch.nn.functional as F
import os
from ..utils import check_ckpt_exist, get_url_id


class Upsampler(nn.Module):
    def __init__(self, folder_name='upsampler',  ckpt_name = 'upsampler_SwinIR_large.pth', force=False, device='cuda'):
        """
        Related Links
        --------
        https://github.com/JingyunLiang/SwinIR
        
        Methods
        ---------
        - forward
            - input
                - dtype : tensor
                - shape : (b, 3, h, w)
                    - model is operated on 256*256 size, it will automactically resize
                - min max : (0 1)
            - output
                - dtype : tensor
                - shape : (b 3 1024 1024)
                - min max : (0 1)
        """
        
        super(Upsampler, self).__init__()
        self.device = device
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt =  torch.load(ckpt_path)
        self.sr_net = SwinIR(upscale=4, in_chans=3, img_size=64, window_size=8,
                         img_range=1., depths=[6, 6, 6, 6, 6, 6, 6, 6, 6], embed_dim=240,
                         num_heads=[8, 8, 8, 8, 8, 8, 8, 8, 8],
                         mlp_ratio=2, upsampler='nearest+conv', resi_connection='3conv')
        self.sr_net.load_state_dict(ckpt['params_ema'], strict=True)
        self.sr_net.to(self.device)
        for param in self.sr_net.parameters():
            param.requires_grad = False
        self.sr_net.eval()
        del ckpt
        
    def forward(self, x, output_size=None):
        W, H = x.size()[-1] ,x.size()[-2] 
        if W!=256 or H!=256:
            x = F.interpolate(x, (256,256), mode='bilinear')
        
        with torch.no_grad():
            result = self.sr_net(x)
            if output_size == None:
                _result = F.interpolate(result, (1024, 1024), mode='bilinear')
            else:
                _result = F.interpolate(result, (output_size, output_size), mode='bilinear')
            return _result
        
