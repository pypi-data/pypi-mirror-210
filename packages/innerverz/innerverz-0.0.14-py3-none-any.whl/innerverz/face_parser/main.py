import os

import torch
import torch.nn as nn
import torch.nn.functional as F

from .nets import BiSeNet
from ..utils import check_ckpt_exist, get_url_id, get_one_hot, arrange_mask

class FaceParser(nn.Module):
    def __init__(self, folder_name='face_parser', ckpt_name = 'faceparser.pth', force=False, device = 'cuda'):
        """
        Related Links
        --------
        https://github.com/zllrunning/face-parsing.PyTorch
        
        Label Index
        --------
        
        face_parts | bg| skin | Lbrow | Rbrow | Leye | Reye | glasses | Lear | Rear | ear_ring | nose | mouth | upper_lip | lower_lip | neck | neckless | cloth | hair | hat   
        --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---  
        label_index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18  
        
        Methods
        ---------
        - get_label
        - get_onehot
        """
        
        super(FaceParser, self).__init__()

        self.device = device
        self.parsing_net = BiSeNet(n_classes=19).to(self.device)
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
        
        self.parsing_net.load_state_dict(ckpt)
        for param in self.parsing_net.parameters():
            param.requires_grad = False
        self.parsing_net.eval()
        del ckpt
    
    def get_label(self, tensor_img, output_size=512):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (b, 3, 512, 512)
            - min max : (-1, 1)
            
        Output
        ---------
            - dtype : tensor
            - shape : (b, 512, 512)
            - min max : (0, 18)
        """
        label = self.parsing_net(tensor_img)
        _label = F.interpolate(label, (output_size,output_size), mode='bilinear').max(1)[1]
        _label = arrange_mask(_label, output_size)
        return _label
    
    def get_onehot(self, tensor_img, size=512):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (b, 3, 512, 512)
            - min max : (-1, 1)
            
        Output
        ---------
            - dtype : tensor
            - shape : (b, 19, size, size)
            - min max : (0 or 1)
        """
        label = self.get_label(tensor_img, size)
        onehot = get_one_hot(label.unsqueeze(0))
        return onehot
