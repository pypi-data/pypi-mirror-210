import os
cwd = os.path.dirname(os.path.realpath(__file__))

import torch
import torch.nn as nn
import numpy as np
from .nets import MyGenerator
from ..utils import check_ckpt_exist, convert_image_type, get_url_id, get_grad_mask, get_center_coord

class FaceEnhancer(nn.Module):
    def __init__(self, folder_name='face_enhancer', ckpt_name = 'ckpt.zip', ckpt_face = 'face_090_395k.pt', ckpt_eye = 'eye_012_300k.pt', ckpt_mouth = 'mouth_007_80k.pt', force=False, device = 'cuda'):
        """
        Methods
        ---------
        - forward
            - Input
                - lmks
                    - dtype : numpy array
                    - shape : (b 106 2)
                - image
                    - dtype : tensor
                    - shape : (b 3 1024 1024)
                    - min max : (-1 1)
            - Output
                - dtype : tensor
                - shape : (b 3 1024 1024)
                - min max : (-1 1)
        """
        super(FaceEnhancer, self).__init__()

        self.device = device
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        self.dir_folder_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)[:-4]
        
        self.face_enhancer = MyGenerator().to(device)
        self.eye_enhancer = MyGenerator().to(device)
        self.mouth_enhancer = MyGenerator().to(device)
        
        ckpt_pairs = [
            [self.face_enhancer, os.path.join(self.dir_folder_path, ckpt_face)],
            [self.eye_enhancer, os.path.join(self.dir_folder_path, ckpt_eye)],
            [self.mouth_enhancer, os.path.join(self.dir_folder_path, ckpt_mouth)],
        ]
        for enhancer, ckpt_path in ckpt_pairs:
            ckpt = torch.load(os.path.join(cwd, ckpt_path), map_location=device)
            enhancer.load_state_dict(ckpt['model'], strict=False)
            for param in enhancer.parameters():
                param.requires_grad = False
            enhancer.eval()
            del ckpt

        self.grad_mask = torch.from_numpy(get_grad_mask()).to(device)

    def forward(self, lmks, imgs):
        batch_num = imgs.size()[0]

        full_result = self.face_enhancer(imgs) # size: 1024, value range: [-1, 1]

        target_R_eye = torch.zeros((batch_num, 3, 256, 256), device='cuda')
        target_L_eye = torch.zeros((batch_num, 3, 256, 256), device='cuda') 
        target_Mouth = torch.zeros((batch_num, 3, 256, 256), device='cuda') 

        for idx in range(batch_num):
            L_xc, L_yc, _, _ = get_center_coord(lmks[idx], 'L_eye')
            R_xc, R_yc, _, _ = get_center_coord(lmks[idx], 'R_eye')
            M_xc, M_yc, _, _ = get_center_coord(lmks[idx], 'mouth')

            target_L_eye[idx] = full_result[idx, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128]
            target_R_eye[idx] = full_result[idx, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128]
            target_Mouth[idx] = full_result[idx, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128]

        L_eye_result = self.eye_enhancer(target_L_eye)
        R_eye_result = self.eye_enhancer(target_R_eye)
        Mouth_result = self.mouth_enhancer(target_Mouth)

        full_result[:, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128] = L_eye_result*self.grad_mask + full_result[:, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128]*(1-self.grad_mask)
        full_result[:, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128] = R_eye_result*self.grad_mask + full_result[:, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128]*(1-self.grad_mask)
        full_result[:, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128] = Mouth_result*self.grad_mask + full_result[:, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128]*(1-self.grad_mask)

        return full_result
