import os, sys
# sys.path.append('./innerverz_package/video_fraceparser')

import cv2
from tqdm import tqdm
import torch
from torch import nn
import torch.nn.functional as F
from .utils.util import get_batch_labels, get_batch_frames
from .utils.util import InputPadder
from .utils.util import warp, get_list_chunk, arrange_mask
from .nets import RAFT

from ..utils import check_ckpt_exist, convert_image_type, get_url_id
from ..face_parser import FaceParser

class Video_FaceParser(nn.Module):
    def __init__(self, window_size=7, split_amount=4, img_size=512, folder_name='video_faceparser', ckpt_name = 'raft_things.pth', force=False, device = 'cuda'):
        """
        Related Links
        --------
        https://github.com/williamyang1991/VToonify
        
        https://github.com/zllrunning/face-parsing.PyTorch
        
        
        Keywords
        --------
            - if you setting with 'split amount = 2', Whole frame will be split 2 pieces of chunks.
            - whole frame amount = window size * split amount
            
            |-------------------------------------------- whole frame ---------------------------------------------|
            
            |------------------- window size -----------------|   ...   |------------------ window size ------------------|  
            
            |-- side window --| target frame |-- side window --|   ...   |-- side window --| target frame |-- side window --|  
        
        Label Index
        --------
        
        face_parts | bg| skin | Lbrow | Rbrow | Leye | Reye | glasses | Lear | Rear | ear_ring | nose | mouth | upper_lip | lower_lip | neck | neckless | cloth | hair | hat   
        --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---  
        label_index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18  
        
        Methods
        --------
        - forward
            - image_path_list
                - dtype : list[string]
            - save_path
                - dtype : string
            - vis_save_path
                - Fill this parameters when you want to save visualized label
                - dtype : string
        
        """
        super(Video_FaceParser, self).__init__()
        # parameters
        self.device = device
        self.img_size = 512
        self.window_size = window_size
        self.side_window = self.window_size//2
        self.split_amount = split_amount
    
        self.wt = torch.exp(-(torch.arange(self.window_size).float()-self.side_window)**2/(2*((self.side_window+0.5)**2))).reshape(self.window_size,1,1,1).to(self.device)
    
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
        
        self.FP = FaceParser(device=self.device)
        
        self.raft = torch.nn.DataParallel(RAFT())
        self.raft.load_state_dict(ckpt)
        self.raft = self.raft.module
        for param in self.raft.parameters():
            param.requires_grad = False
        self.raft.eval().to(self.device)
        del ckpt
    
    def forward(self, frame_path_list, save_path, vis_save_path=None, output_size=512):
        frame_path_list = sorted(frame_path_list)
        os.makedirs(save_path, exist_ok=True)
        if vis_save_path is not None: os.makedirs(vis_save_path, exist_ok=True)
        
        for frame_path_chunk in get_list_chunk(frame_path_list, self.split_amount):
            Is_ = get_batch_frames(frame_path_chunk, self.side_window, self.img_size)

            Ps_ = get_batch_labels(Is_, self.FP, self.side_window)
            # temporal weights of the (2*args.window_size+1) frames
            parse = []
            for ii in tqdm(range(len(frame_path_chunk))):
                i = ii + self.side_window
                image2 = Is_[i-self.side_window:i+self.side_window+1].to(self.device)
                image1 = Is_[i].repeat(2*self.side_window+1,1,1,1).to(self.device)
                padder = InputPadder(image1.shape)
                image1, image2 = padder.pad(image1, image2)
                with torch.no_grad():
                    flow_low, flow_up = self.raft((image1+1)*255.0/2, (image2+1)*255.0/2, iters=20, test_mode=True)
                    output, mask = warp(torch.cat((image2, Ps_[i-self.side_window:i+self.side_window+1].to(self.device)), dim=1), flow_up)
                    
                    aligned_Is = output[:,0:3].detach()
                    aligned_Ps = output[:,3:].detach()
                    
                    # the spatial weight
                    ws = torch.exp(-((aligned_Is-image1)**2).mean(dim=1, keepdims=True)/(2*(0.2**2))) * mask[:,0:1]
                    aligned_Ps[self.side_window] = Ps_[i].to(self.device)
                    # the weight between i and i shoud be 1.0
                    ws[self.side_window,:,:,:] = 1.0
                    weights = ws*self.wt # weights = w(j,i)
                    weights = weights / weights.sum(dim=(0), keepdims=True)
                    fused_Ps = (aligned_Ps * weights).sum(dim=0, keepdims=True)
                    # parse = down(fused_Ps).detach().cpu()
                parse = fused_Ps.detach().cpu().argmax(1) #torch.argmax(torch.cat(parse, dim=0), 1)
                parse = arrange_mask(parse).squeeze().numpy()
                _parse = cv2.resize(parse, (output_size,output_size), interpolation=cv2.INTER_NEAREST)
                image_name = frame_path_chunk[ii].split('/')[-1].split('.')[0]
                cv2.imwrite(os.path.join(save_path, image_name+'.png'), _parse)
                if vis_save_path is not None: cv2.imwrite(os.path.join(vis_save_path, image_name+'.png'), (parse[:,:,None]*10+60)*.5 + (image1[0].detach().permute([1,2,0]).cpu().numpy()[:,:,::-1]*127.5+127.5)*.5)

        print('Done!')
