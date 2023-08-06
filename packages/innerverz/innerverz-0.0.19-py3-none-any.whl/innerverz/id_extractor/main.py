import os

import torch
import torch.nn as nn
import torch.nn.functional as F

import warnings; warnings.filterwarnings('ignore')

from .nets import Backbone
from ..utils import check_ckpt_exist, get_url_id

class IdExtractor(nn.Module):
    def __init__(self, x=32, y=32, w=192, h=192 , folder_name='id_extractor', ckpt_name='currface.pth', force=False, device='cuda' ):
        """
        Methods
        --------
        forward(tesnor_img : tensor) -> id_vector : tensor
        
        data_preprocess(img_path : str) -> tensor_img : tensor
        
        compare_similarity(id_vector_1 : tensor, id_vector_2 : tensor) -> score : float
        """
        super(IdExtractor, self).__init__()
        self.device = device
        self.id_extractor = Backbone().to(self.device).eval()
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)

        self.id_extractor.load_state_dict(ckpt)
        for param in self.id_extractor.parameters():
            param.requires_grad = False
        del ckpt

        self.x, self.y, self.w, self.h = x, y, w, h

    def forward(self, tensor_img):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (b, 3, h, w)
            - min max : (-1, 1)
            
        Output
        ---------
            - type : tensor
            - shape : (b, 512)
        """
        tensor_img = F.interpolate(tensor_img, (256,256))
        tensor_img = F.interpolate(tensor_img[..., self.y:self.y+self.h, self.x:self.x+self.w], (112, 112), mode='bilinear')
        id_vector = self.id_extractor(tensor_img)
        return id_vector
    
    def compare_similarity(self, id1, id2):
        """
        Input
        ---------
            - dtype : tensor
            - shape : id1 (1, 512) / id2 (1, 512)

        Output
        ---------
            - type : float
            - min max : (0, 1)
                - similiarity score
        """
        score = torch.cosine_similarity(id1, id2, dim=1).mean().item()
        return score
    

