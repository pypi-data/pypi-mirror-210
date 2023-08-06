
import os
import sys
# sys.path.append('../')
# cwd = os.path.dirname(os.path.realpath(__file__))

import cv2
import numpy as np
from PIL import Image
import scipy
from skimage.io import imread
from skimage.transform import estimate_transform, warp, resize, rescale

import torch
import torch.nn as nn
import torch.nn.functional as F

import torchvision
import torchvision.transforms as transforms

# from .models.face_detectors import FAN
from .models.encoders import ResnetEncoder
from .models.FLAME import FLAME, FLAMETex
from .models.decoders import Generator

from .utils.util import copy_state_dict, batch_orth_proj, tensor_vis_landmarks, vertex_normals
from .utils.rotation_converter import batch_euler2axis
from .utils.tensor_cropper import transform_points
from .utils.renderer import SRenderY, set_rasterizer
from ..utils import check_ckpt_exist, convert_image_type, get_url_id

class DECA(nn.Module):
    def __init__(self, folder_name='deca', ckpt_name = 'ckpt.zip', force=False, device = 'cuda'):
        """
        Related Links
        --------
        DECA : https://github.com/yfeng95/DECA
        FLAME : https://github.com/Rubikplayer/flame-fitting
        
        Methods
        ---------
        - data_preprocess
        - encode
        - decode
        - forward
        """
        super(DECA, self).__init__()
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        self.dir_folder_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)[:-4]

        self.use_tex = False
        self.extract_tex = False
        
        self.device = device
        self.iscrop = True
        self.scale = 1.25
        self.resolution_inp = 224
        self.image_size = 224
        self.uv_size = 256
        self.rasterizer_type = 'pytorch3d' # 'standard'
        
        self._create_model()
        self._setup_renderer()
        
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
        ])
        
    def _setup_renderer(self,):
        set_rasterizer(self.rasterizer_type)
        self.render = SRenderY(self.image_size, obj_filename=os.path.join(self.dir_folder_path, 'head_template.obj'), uv_size=self.uv_size, rasterizer_type=self.rasterizer_type).to(self.device)
        # face mask for rendering details
        mask = imread(os.path.join(self.dir_folder_path, 'uv_face_eye_mask.png')).astype(np.float32)/255.; mask = torch.from_numpy(mask[:,:,0])[None,None,:,:].contiguous()
        self.uv_face_eye_mask = F.interpolate(mask, [self.uv_size, self.uv_size]).to(self.device)
        mask = imread(os.path.join(self.dir_folder_path, 'uv_face_mask.png')).astype(np.float32)/255.; mask = torch.from_numpy(mask[:,:,0])[None,None,:,:].contiguous()
        self.uv_face_mask = F.interpolate(mask, [self.uv_size, self.uv_size]).to(self.device)
        # displacement correction
        fixed_dis = np.load(os.path.join(self.dir_folder_path, 'fixed_displacement_256.npy'))
        self.fixed_uv_dis = torch.tensor(fixed_dis).float().to(self.device)
        # mean texture
        mean_texture = imread(os.path.join(self.dir_folder_path, 'mean_texture.jpg')).astype(np.float32)/255.; mean_texture = torch.from_numpy(mean_texture.transpose(2,0,1))[None,:,:,:].contiguous()
        self.mean_texture = F.interpolate(mean_texture, [self.uv_size, self.uv_size]).to(self.device)
        # dense mesh template, for save detail mesh
        self.dense_template = np.load(os.path.join(self.dir_folder_path, 'texture_data_256.npy'), allow_pickle=True, encoding='latin1').item()
    
    def _bbox2point(self, left, right, top, bottom, type='bbox'):
        ''' bbox from detector and landmarks are different
        '''
        if type=='kpt68':
            old_size = (right - left + bottom - top)/2*1.1
            center = np.array([right - (right - left) / 2.0, bottom - (bottom - top) / 2.0 ])
        elif type=='bbox':
            old_size = (right - left + bottom - top)/2
            center = np.array([right - (right - left) / 2.0, bottom - (bottom - top) / 2.0  + old_size*0.12])
        else:
            raise NotImplementedError
        return old_size, center
     
    def _create_model(self):
        # set up parameters
        n_shape = 100; n_tex = 50; n_exp = 50; n_cam = 3; n_pose = 6; n_light = 27; n_detail = 128
        use_tex = True
        max_z = 0.01
        # jaw_type = 'aa'
        
        self.n_param = n_shape+n_tex+n_exp+n_pose+n_cam+n_light
        self.n_detail = n_detail
        self.n_cond = n_exp + 3 # exp + jaw pose
        
        # param_list = ['shape', 'tex', 'exp', 'pose', 'cam', 'light']
        self.num_list = [n_shape, n_tex, n_exp, n_pose, n_cam, n_light]
        self.param_dict = {
            'shape' : 100,
            'tex' : 50,
            'exp' : 50,
            'pose' : 6,
            'cam' : 3,
            'light' : 27
        }

        # encoders
        self.E_flame = ResnetEncoder(outsize=self.n_param).to(self.device) 
        self.E_detail = ResnetEncoder(outsize=self.n_detail).to(self.device)
        # decoders
        self.flame = FLAME(self.dir_folder_path).to(self.device)
        if use_tex:
            self.flametex = FLAMETex(self.dir_folder_path).to(self.device)
        self.D_detail = Generator(latent_dim=self.n_detail+self.n_cond, out_channels=1, out_scale=max_z, sample_mode = 'bilinear').to(self.device)
        
        # resume model
        model_path = os.path.join(self.dir_folder_path, 'deca_model.tar')
        if os.path.exists(model_path):
            print(f'trained model found. load {model_path}')
            checkpoint = torch.load(model_path)
            self.checkpoint = checkpoint
            copy_state_dict(self.E_flame.state_dict(), checkpoint['E_flame'])
            copy_state_dict(self.E_detail.state_dict(), checkpoint['E_detail'])
            copy_state_dict(self.D_detail.state_dict(), checkpoint['D_detail'])
        else:
            print(f'please check model path: {model_path}')
            # exit()
        # eval mode
        self.E_flame.eval()
        self.E_detail.eval()
        self.D_detail.eval()
        
    def _decompose_code(self, code, num_dict):
        ''' Convert a flattened parameter vector to a dictionary of parameters
        code_dict.keys() = ['shape', 'tex', 'exp', 'pose', 'cam', 'light']
        '''
        code_dict = {}
        start = 0
        for key in num_dict:
            end = start+int(num_dict[key])
            code_dict[key] = code[:, start:end]
            start = end
            if key == 'light':
                code_dict[key] = code_dict[key].reshape(code_dict[key].shape[0], 9, 3)
        return code_dict
    
    def _displacement2normal(self, uv_z, coarse_verts, coarse_normals):
        ''' Convert displacement map into detail normal map
        '''
        batch_size = uv_z.shape[0]
        uv_coarse_vertices = self.render.world2uv(coarse_verts).detach()
        uv_coarse_normals = self.render.world2uv(coarse_normals).detach()
    
        uv_z = uv_z*self.uv_face_eye_mask
        uv_detail_vertices = uv_coarse_vertices + uv_z*uv_coarse_normals + self.fixed_uv_dis[None,None,:,:]*uv_coarse_normals.detach()
        dense_vertices = uv_detail_vertices.permute(0,2,3,1).reshape([batch_size, -1, 3])
        uv_detail_normals = vertex_normals(dense_vertices, self.render.dense_faces.expand(batch_size, -1, -1))
        uv_detail_normals = uv_detail_normals.reshape([batch_size, uv_coarse_vertices.shape[2], uv_coarse_vertices.shape[3], 3]).permute(0,3,1,2)
        uv_detail_normals = uv_detail_normals*self.uv_face_eye_mask + uv_coarse_normals*(1.-self.uv_face_eye_mask)
        return uv_detail_normals
    
    def data_preprocess(self, image, lmk):
        # imagename = os.path.splitext(os.path.split(image_path)[-1])[0]
        # image = np.array(Image.open(image_path).convert('L'))[:, :, None].repeat(3, axis=2)
        """
        Input
        ---------
            - dtype : cv2 image, numpy array
            - shape : (h, w, 3)
            - min max : (0, 255)
            
        Output
        ---------
            - dtype : dict
                - image
                    - dtype : tensor
                    - shape : (3, 224, 224)
                    - min max : (0, 1)
                - tform
                    - dtype : tensor
                    - shape : (3, 3)
                - original_image
                    - dtype : tensor
                    - shape : (3, h, w)
                    - min max : (0, 1)
        """
        if len(image.shape) == 2:
            image = image[:,:,None].repeat(1,1,3)
        if len(image.shape) == 3 and image.shape[2] > 3:
            image = image[:,:,:3]
        
        h, w, _ = image.shape
        if self.iscrop:
            left = np.min(lmk[:,0]); right = np.max(lmk[:,0]); top = np.min(lmk[:,1]); bottom = np.max(lmk[:,1])
            bbox_type = 'kpt68'
            old_size, center = self._bbox2point(left, right, top, bottom, type=bbox_type)
                
            size = int(old_size*self.scale)
            src_pts = np.array([[center[0]-size/2, center[1]-size/2], [center[0] - size/2, center[1]+size/2], [center[0]+size/2, center[1]-size/2]])
        else:
            src_pts = np.array([[0, 0], [0, h-1], [w-1, 0]])
        
        DST_PTS = np.array([[0,0], [0,self.resolution_inp - 1], [self.resolution_inp - 1, 0]])
        tform = estimate_transform('similarity', src_pts, DST_PTS)
        
        image = image/255.

        dst_image = warp(image, tform.inverse, output_shape=(self.resolution_inp, self.resolution_inp))
        dst_image = dst_image.transpose(2,0,1)
        return {'image': torch.tensor(dst_image).float().to(self.device),
                'tform': torch.tensor(tform.params).float().to(self.device),
                'original_image': torch.tensor(image.transpose(2,0,1)).float().to(self.device),
                }
        
    def forward(self, image_dict):
        tensor_images = image_dict['image'][None,...]
        tform = image_dict['tform'][None, ...]
        tform = torch.inverse(tform).transpose(1,2)
        original_image = image_dict['original_image'][None, ...]
        
        codedict = self.encode(tensor_images)
        orig_visdict = self.decode(codedict, original_image=original_image, tform=tform)    
        orig_visdict['inputs'] = original_image   
        
        return codedict, orig_visdict        

    def encode(self, images):
        """
        Input
        ---------
        - dtype : dict
            - image
                - dtype : tensor
                - shape : (3, 224, 224)
                - min max : (0, 1)
            - tform
                - dtype : tensor
                - shape : (3, 3)
            - original_image
                - dtype : tensor
                - shape : (3, h, w)
                - min max : (0, 1)

            
        Output
        ---------
        - dtype : dict
            - shape
                - shape : (b, 100)
            - tex
                - shape : (b, 50)
            - exp
                - shape : (b, 50)
            - pose
                - shape : (b, 6)
            - cam
                - shape : (b, 3)
            - light
                - shape : (b, 9, 3)
            - images
                - shape : (b, 3, 224, 224)
                - min max : (0, 1)
            - detail
                - shape : (b, 128)
        """
        
        with torch.no_grad():
            parameters = self.E_flame(images)
            
        codedict = self._decompose_code(parameters, self.param_dict)
        codedict['images'] = images
        
        
        detailcode = self.E_detail(images)
        codedict['detail'] = detailcode
        
        return codedict
    
    def decode(self, codedict, albedo=True, original_image=None, tform=None):
        """
        Input
        ---------
        - dtype : dict
            - shape
                - shape : (b, 100)
            - tex
                - shape : (b, 50)
            - exp
                - shape : (b, 50)
            - pose
                - shape : (b, 6)
            - cam
                - shape : (b, 3)
            - light
                - shape : (b, 9, 3)
            - images
                - shape : (b, 3, 224, 224)
                - min max : (0, 1)
            - detail
                - shape : (b, 128)

        Output
        ---------
        - dtype : dict
            - inputs
                - dtype : tensor
                - shape : (b, 3, h, w)
                - min max : (0, 1)
                
            - landmarks2d
                - dtype : tensor
                - shape : (b, 3, h, w)
                - min max : (0, 1)
                
            - landmarks3d
                - dtype : tensor
                - shape : (b, 3, h, w)
                - min max : (0, 1)
                
            - shape_images
                - dtype : tensor
                - shape : (b, 3, h, w)
                - min max : (0, 1)
                
            - shape_detail_images
                - dtype : tensor
                - shape : (b, 3, h, w)
                - min max : (0, 1)
        """
        images = codedict['images']
        batch_size = images.shape[0]
        
        ## decode
        verts, _, _ = self.flame(shape_params=codedict['shape'], expression_params=codedict['exp'], pose_params=codedict['pose'])
        verts, landmarks2d, landmarks3d = self.flame(shape_params=codedict['shape'], expression_params=codedict['exp'], pose_params=codedict['pose'])
        if albedo:
            albedo = self.flametex(codedict['tex'])
        else:
            albedo = torch.zeros([batch_size, 3, self.uv_size, self.uv_size], device=images.device) 

        ## projection
        landmarks2d = batch_orth_proj(landmarks2d, codedict['cam'])[:,:,:2]; landmarks2d[:,:,1:] = -landmarks2d[:,:,1:]#; landmarks2d = landmarks2d*self.image_size/2 + self.image_size/2
        landmarks3d = batch_orth_proj(landmarks3d, codedict['cam']); landmarks3d[:,:,1:] = -landmarks3d[:,:,1:] #; landmarks3d = landmarks3d*self.image_size/2 + self.image_size/2
        trans_verts = batch_orth_proj(verts, codedict['cam']); trans_verts[:,:,1:] = -trans_verts[:,:,1:]
        opdict = {
            'verts': verts,
            'trans_verts': trans_verts,
            'landmarks2d': landmarks2d,
            'landmarks3d': landmarks3d,
        }

        # rendering
        points_scale = [self.image_size, self.image_size]
        _, _, h, w = original_image.shape
        trans_verts = transform_points(trans_verts, tform, points_scale, [h, w])
        landmarks2d = transform_points(landmarks2d, tform, points_scale, [h, w])
        landmarks3d = transform_points(landmarks3d, tform, points_scale, [h, w])
        background = None
        images = original_image

        ops = self.render(verts, trans_verts, albedo, lights= codedict['light'],h=h, w=w, background=background)
        
        # detail
        uv_z = self.D_detail(torch.cat([codedict['pose'][:,3:], codedict['exp'], codedict['detail']], dim=1))
        uv_detail_normals = self._displacement2normal(uv_z, verts, ops['normals'])
        uv_shading = self.render.add_SHlight(uv_detail_normals, codedict['light'])
        uv_texture = albedo*uv_shading

        # extract shape images
        shape_images, _, grid, alpha_images = self.render.render_shape(verts, trans_verts, lights= codedict['light'], h=h, w=w, images=background, return_grid=True)
        detail_normal_images = F.grid_sample(uv_detail_normals, grid, align_corners=False)*alpha_images
        shape_detail_images = self.render.render_shape(verts, trans_verts, lights= codedict['light'], detail_normal_images=detail_normal_images, h=h, w=w, images=background)
        
        ## extract texture
        uv_pverts = self.render.world2uv(trans_verts)
        uv_gt = F.grid_sample(images, uv_pverts.permute(0,2,3,1)[:,:,:,:2], mode='bilinear', align_corners=False)
        if self.use_tex:
            if self.extract_tex:
                uv_texture_gt = uv_gt[:,:3,:,:]*self.uv_face_eye_mask + (uv_texture[:,:3,:,:]*(1-self.uv_face_eye_mask))
            else:
                uv_texture_gt = uv_texture[:,:3,:,:]
        else:
            uv_texture_gt = uv_gt[:,:3,:,:]*self.uv_face_eye_mask + (torch.ones_like(uv_gt[:,:3,:,:])*(1-self.uv_face_eye_mask)*0.7)
        
        opdict['uv_texture_gt'] = uv_texture_gt
        visdict = {
            'inputs': images, 
            'landmarks2d': tensor_vis_landmarks(images, landmarks2d),
            'landmarks3d': tensor_vis_landmarks(images, landmarks3d),
            'shape_images': shape_images,
            'shape_detail_images': shape_detail_images,
        }
        if self.use_tex:
            visdict['rendered_images'] = ops['images']

        return visdict
