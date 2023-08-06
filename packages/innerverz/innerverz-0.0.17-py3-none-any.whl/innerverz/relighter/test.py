import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn.functional as F

from innerverz_package import Data_Process
from torchvision.transforms.functional import to_tensor, rgb_to_grayscale

DP = Data_Process()

image_path = 'sample.png'
pil_image = Image.open(image_path)
ts_image = DP.image_pp(pil_image, 512, normalize=True)


"""
        face alignment usage
"""
from innerverz_package import FaceAligner
FA = FaceAligner(align_style='ffhq')

cv2_image = cv2.imread(image_path)
aligned_face, tfm, tfm_inv, lms_5, lms_106, face_bool = FA.get_face(cv2_image)

face_bool, lms_106, lms_5 = FA.detect_lmk(cv2_image)

aligned_face, tfm, tfm_inv = FA.align_face_from_5(cv2_image, lms_5)

aligned_lmk = FA.affine_transform(lms_106, tfm)

    
"""
        FaceParser usage
"""
from innerverz_package import FaceParser
FP = FaceParser()

ts_aligned_face = DP.image_pp(aligned_face, 512, normalize=True)
label = FP.get_label(ts_aligned_face)
pp_label = DP.vis_pp(label, normalize=False, color=False)

"""
            Relighting usage
"""
from innerverz_package import ReLighter
RL = ReLighter()

from innerverz_package import IdExtractor
IE = IdExtractor()

from innerverz_package import DECA
deca = DECA()

ts_aligned_face = DP.image_pp(aligned_face, 512, normalize=True)
id_vector = IE(ts_aligned_face)

# pp
color_aligned_face = DP.image_pp(aligned_face, 512, False, True, False, 'cpu')
convexhull_label = DP.label_pp(pp_label, 'convexhull', aligned_lmk/2, 512, one_hot=False, batch=False, device='cpu')
convexhull_mask = np.where(convexhull_label.squeeze() != 0 ,1 , 0)
color_aligned_face = np.array(cv2.resize(aligned_face,(512,512)) * convexhull_mask[:,:,None])
convexhull_mask = torch.tensor(convexhull_mask).unsqueeze(0).unsqueeze(0).to('cuda')

# deca
source_image_dict = deca.data_preprocess(color_aligned_face, aligned_lmk/2)
source_tensor_images = source_image_dict['image'][None,...]
source_code_dict = deca.encode(source_tensor_images)

target_image_dict = deca.data_preprocess(color_aligned_face, aligned_lmk/2)
target_tensor_images = target_image_dict['image'][None,...]
target_code_dict = deca.encode(target_tensor_images)

target_code_dict['light'] = source_code_dict['light']

tform = target_image_dict['tform'][None, ...]
tform = torch.inverse(tform).transpose(1,2)
vis_dict = deca.decode(target_code_dict, original_image=target_image_dict['original_image'][None, ...] ,tform=tform)

target_masked_gray_face = rgb_to_grayscale((F.interpolate(target_image_dict['original_image'].unsqueeze(0).to('cuda'), (512, 512), mode='bilinear') - .5) * 2)
_target_masked_gray_face = target_masked_gray_face * convexhull_mask
relight_detail_shape = rgb_to_grayscale((F.interpolate(vis_dict['shape_detail_images'], (512,512), mode='bilinear') - .5) * 2, num_output_channels=1)
_relight_detail_shape = relight_detail_shape * convexhull_mask

relight_result, res_result = RL(_target_masked_gray_face, _relight_detail_shape, target_code_dict, id_vector)
_relight_result = DP.vis_pp(relight_result, True, True)
_res_result = DP.vis_pp(res_result, True, True)