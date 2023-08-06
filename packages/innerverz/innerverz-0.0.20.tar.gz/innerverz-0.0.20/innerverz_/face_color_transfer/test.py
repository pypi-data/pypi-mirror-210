import cv2
import numpy as np
from PIL import Image
import torch
from innerverz_package import Data_Process

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
        face color transfer
"""
from innerverz_package import IWCT
iwct = IWCT()
# data pp
pp_label = DP.vis_pp(label, normalize=False, color=False)
convexhull_onehot = DP.label_pp(pp_label, 'convexhull', aligned_lmk/2, 512, one_hot=True)
gray_aligned_face = DP.image_pp(aligned_face, 512, True, True)
color_aligned_face = DP.image_pp(aligned_face, 512, False, True)
convexhull_mask = DP.label_pp(pp_label, 'convexhull', aligned_lmk/2, 512, one_hot=False)
convexhull_mask = torch.where(convexhull_mask != 0, 1, 0)
color_aligned_face = color_aligned_face * convexhull_mask
gray_aligned_face = gray_aligned_face * convexhull_mask

result, color_reference_map = iwct(color_aligned_face, gray_aligned_face.repeat(1,3,1,1), convexhull_onehot, convexhull_onehot, gray_aligned_face, convexhull_mask)
_color_aligned_face = DP.vis_pp(color_aligned_face)
_result = DP.vis_pp(result)
_color_reference_map = DP.vis_pp(color_reference_map)

cv2.imwrite('pp_label.png', pp_label*10+60)
cv2.imwrite('color_alinged_face.png', _color_aligned_face)
cv2.imwrite('ct_result.png', _result)
cv2.imwrite('color_reference.png', _color_reference_map)
