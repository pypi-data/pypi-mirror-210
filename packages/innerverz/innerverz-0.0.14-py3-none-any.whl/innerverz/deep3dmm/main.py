import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from .nets import ParametricFaceModel, ReconNet
from ..utils import check_ckpt_exist, convert_image_type, get_url_id


class Deep3DMM(nn.Module):
    def __init__(self, folder_name='deep3dmm', ckpt_name='deep3dmm.pth', BFM_name='BFM.tar.xz', force=False, device='cuda'):
        """
        Coeff Index
        --------
        coeff | identity | expression | texture | angles | gammas | translations
        --- | --- | --- | --- |--- |--- |--- 
        index | 0 ~ 79 | 80 ~ 143 | 144 ~ 223 | 224 ~ 226 | 227 ~ 253 | 253 ~ 257 | 
        
        Methods
        --------
        - forward
        - get_coeff3d
        - get_lm3d
        
        """
        super(Deep3DMM, self).__init__()
        self.device = device
        self.net_recon = ReconNet().to(self.device).eval()
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        
        ckpt=torch.load(ckpt_path, map_location=self.device)
        self.net_recon.load_state_dict(ckpt['net_recon'])
        for param in self.net_recon.parameters():
            param.requires_grad = False
        del ckpt
        self.facemodel = ParametricFaceModel(ckpt_name=BFM_name,is_train=False,device=self.device)

    def get_coeff3d(self, img):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (b, 3, 256, 256)
            - min max : (-1, 1)
            
        Output
        ---------
            - coeffs
                - dtype : tensor
                - shape : (b, 257)
        """
        img = F.interpolate(img, (256,256))
        coeffs = self.net_recon(img[:, :, 16:240, 16:240]*0.5+0.5)
        return coeffs


    def get_lm3d(self, coeffs):
        """
        Input
        ---------
            - coeffs
                get from 'get_coeff3d' function
                - dtype : tensor
                - shape : (b, 257)
                
        Output
        ---------
            - lms
                - dtype : tensor
                - shape : (b 68 2)
                - min max : (0, 256)
        """
        coeff_dict = self.facemodel.split_coeff(coeffs)
        
        # get 68 3d landmarks
        face_shape = self.facemodel.compute_shape(coeff_dict['id'], coeff_dict['exp'])
        rotation = self.facemodel.compute_rotation(coeff_dict['angle'])

        face_shape_transformed = self.facemodel.transform(face_shape, rotation, coeff_dict['trans'])
        face_vertex = self.facemodel.to_camera(face_shape_transformed)
        
        face_proj = self.facemodel.to_image(face_vertex)
        lm3d = self.facemodel.get_landmarks(face_proj)

        return lm3d


    def forward(self, img):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (b, 3, 256, 256)
            - min max : (-1, 1)
            
        Output
        ---------
            - coeffs
                - dtype : tensor
                - shape : (b, 257)
                
            - lms
                - dtype : tensor
                - shape : (b 68 2)
                - min max : (0, 256)
        """
        coeffs = self.get_coeff3d(img)
        lms = self.get_lm3d(coeffs)
        return coeffs, lms
    
 