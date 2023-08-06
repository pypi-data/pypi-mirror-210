import sys
sys.path.append('./MyModel')

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

from .sub_nets import VGG19_pytorch, Blend_Net, Warp_Net

class MyGenerator(nn.Module):
    def __init__(self):
        super(MyGenerator, self).__init__()
        self.vgg19 = VGG19_pytorch()
        self.warp_net = Warp_Net()
        self.blend_net = Blend_Net(5)
        self.net_dict = {}
        
    # source color + target structure
    def forward(self, source_rgb, target_rgb, source_onehot, target_onehot, target_gray, target_face_mask):
    # def forward(self, target_gray, target_onehot, source_rgb, source_onehot):
        self.net_dict['target_rgb'] = target_rgb
        self.net_dict['target_gray'] = target_gray
        self.net_dict['target_onehot'] = target_onehot
        self.net_dict['source_rgb'] = source_rgb
        self.net_dict['source_onehot'] = source_onehot
        self.net_dict['target_face_mask'] = target_face_mask
        
        """
        Step 1 : get features
        input 0 ~ 1
        """
        with torch.no_grad():
            self.net_dict["target_rgb_features"] : list = self.vgg19(
                F.interpolate((self.net_dict["target_rgb"]+1)/2, (256,256)), ["r12", "r22", "r32", "r42", "r52"], preprocess=True
            )
            
            self.net_dict["source_rgb_features"] : list = self.vgg19(
                F.interpolate((self.net_dict["source_rgb"]+1)/2, (256,256)), ["r12", "r22", "r32", "r42", "r52"], preprocess=True
            )
            
        # "r12", "r22", "r32", "r42", "r52"
        for i, (target_feature, source_feature) in enumerate(zip(self.net_dict["target_rgb_features"], self.net_dict["source_rgb_features"])):
            self.net_dict["target_rgb_features"][i] = self._feature_normalize(target_feature)
            self.net_dict["source_rgb_features"][i] = self._feature_normalize(source_feature)
        
        """
        Step 2 : get color reference map & similarity map
        vgg relu results(source & target) -> [ Warp Net ] -> resized feature maps(source & target)(img size / 4)
        output : color reference map(color ab), similarity map(b,1,h/4,h/4)?
        """
        self.net_dict["target_rgb_features_small"], self.net_dict["source_rgb_features_small"] = self.warp_net(
            self.net_dict["target_rgb_features"][1],
            self.net_dict["target_rgb_features"][2],
            self.net_dict["target_rgb_features"][3],
            self.net_dict["target_rgb_features"][4],
            self.net_dict["source_rgb_features"][1],
            self.net_dict["source_rgb_features"][2],
            self.net_dict["source_rgb_features"][3],
            self.net_dict["source_rgb_features"][4]
        )

        # color_reference_lab(with source l)
        # b 3 h 216 384 / b 1 h 218 384
        self.get_color_map()
        self.net_dict["color_reference_innerface_rgb"] = self.net_dict["color_reference_rgb"] * self.net_dict["target_face_mask"]
        
        blend_input = torch.cat((self.net_dict["target_gray"], self.net_dict["target_face_mask"], self.net_dict["color_reference_innerface_rgb"]), dim=1)
        self.net_dict["fake_rgb"] = self.blend_net(blend_input)
        return self.net_dict["fake_rgb"], self.net_dict["color_reference_rgb"]
        
    def get_color_map(self):

            _, n_ch, origin_h, origin_w = self.net_dict['target_onehot'].shape
            b, c, h, w = self.net_dict['target_rgb_features_small'].size()
            target_mask_quater = F.interpolate(self.net_dict['target_onehot'], size=(h, w), mode='nearest')
            source_mask_quater = F.interpolate(self.net_dict['source_onehot'], size=(h, w), mode='nearest')
            source_color_quater = F.interpolate(self.net_dict['source_rgb'], size=(h, w), mode='bilinear')
            target_color_quater = F.interpolate(self.net_dict['target_rgb'], size=(h, w), mode='bilinear')
            canvas = torch.zeros_like(source_color_quater)

            # target_mask_quater[:,-1] = torch.logical_or(target_mask_quater[:,0], target_mask_quater[:,-1])

            for b_idx in range(b):
                for c_idx in range(1, n_ch):
                    target_1ch_mask, source_1ch_mask = target_mask_quater[b_idx,c_idx], source_mask_quater[b_idx,c_idx]

                    # if target_1ch_mask.sum() != 0 and source_1ch_mask.sum() == 0:
                    if target_1ch_mask.sum() != 0 and source_1ch_mask.sum() < 9 :
                        target_matrix = torch.masked_select(self.net_dict['target_rgb_features_small'][b_idx], target_1ch_mask.bool()).reshape(c, -1) # 64, pixel_num_A
                        target_matrix_bar = target_matrix - target_matrix.mean(1, keepdim=True) # 64, pixel_num_A
                        if target_1ch_mask.sum() == 1:
                            target_matrix_ = target_matrix_bar
                        else:
                            target_matrix_norm = torch.norm(target_matrix_bar, dim=0, keepdim=True)
                            target_matrix_ = target_matrix_bar / target_matrix_norm

                        source_matrix = torch.masked_select(self.net_dict['target_rgb_features_small'][b_idx], target_1ch_mask.bool()).reshape(c, -1) # 64, pixel_num_B
                        source_matrix_bar = source_matrix - source_matrix.mean(1, keepdim=True) # 64, pixel_num_B
                        if target_1ch_mask.sum() == 1:
                            source_matrix_ = source_matrix_bar
                        else:
                            source_matrix_norm = torch.norm(source_matrix_bar, dim=0, keepdim=True)
                            source_matrix_ = source_matrix_bar / source_matrix_norm
                    

                        correlation_matrix = torch.matmul(target_matrix_.transpose(0,1), source_matrix_)
                        correlation_matrix = F.softmax(correlation_matrix,dim=1)

                        source_pixels = torch.masked_select(target_color_quater[b_idx], target_1ch_mask.bool()).reshape(3,-1) # 3
                        colorized_matrix = torch.matmul(correlation_matrix, source_pixels.transpose(0,1)).transpose(0,1)

                        canvas[b_idx].masked_scatter_(target_1ch_mask.bool(), colorized_matrix) # 3 128 128
                        
                        
                    elif target_1ch_mask.sum() != 0:
                    
                    # if target_1ch_mask.sum() == 0 or target_1ch_mask.sum() == 1 or source_1ch_mask.sum() == 0 or source_1ch_mask.sum() == 1:
                    #     continue
                
                        target_matrix = torch.masked_select(self.net_dict['target_rgb_features_small'][b_idx], target_1ch_mask.bool()).reshape(c, -1) # 64, pixel_num_A
                        target_matrix_bar = target_matrix - target_matrix.mean(1, keepdim=True) # 64, pixel_num_A
                        if target_1ch_mask.sum() == 1:
                            target_matrix_ = target_matrix_bar
                        else:
                            target_matrix_norm = torch.norm(target_matrix_bar, dim=0, keepdim=True)
                            target_matrix_ = target_matrix_bar / target_matrix_norm

                        source_matrix = torch.masked_select(self.net_dict['source_rgb_features_small'][b_idx], source_1ch_mask.bool()).reshape(c, -1) # 64, pixel_num_B
                        source_matrix_bar = source_matrix - source_matrix.mean(1, keepdim=True) # 64, pixel_num_B
                        if source_1ch_mask.sum() == 1:
                            source_matrix_ = source_matrix_bar
                        else:
                            source_matrix_norm = torch.norm(source_matrix_bar, dim=0, keepdim=True)
                            source_matrix_ = source_matrix_bar / source_matrix_norm
                    
                        correlation_matrix = torch.matmul(target_matrix_.transpose(0,1), source_matrix_)
                        correlation_matrix = F.softmax(correlation_matrix,dim=1)

                        source_pixels = torch.masked_select(source_color_quater[b_idx], source_1ch_mask.bool()).reshape(3,-1) # 3
                        colorized_matrix = torch.matmul(correlation_matrix, source_pixels.transpose(0,1)).transpose(0,1)

                        canvas[b_idx].masked_scatter_(target_1ch_mask.bool(), colorized_matrix) # 3 128 128




            self.net_dict['color_reference_rgb'] = F.interpolate(canvas, size=(origin_h, origin_w), mode='bilinear').clip(-1,1)
            
    def _feature_normalize(self, feature_in):
        feature_in_norm = torch.norm(feature_in, 2, 1, keepdim=True) + sys.float_info.epsilon
        feature_in_norm = torch.div(feature_in, feature_in_norm)
        return feature_in_norm