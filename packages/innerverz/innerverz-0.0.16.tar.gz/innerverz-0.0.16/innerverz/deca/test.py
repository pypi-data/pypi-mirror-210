import cv2
import torch.nn.functional as F

from innerverz_package import Data_Process
from torchvision.transforms.functional import to_tensor, rgb_to_grayscale

image_path = 'sample.png'
DP = Data_Process()

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
        DECA usage
"""
from innerverz_package import DECA
deca = DECA()
image_dict = deca.data_preprocess(aligned_face, aligned_lmk)
code_dict, vis_dict = deca(image_dict)

inputs = DP.vis_pp(vis_dict['inputs'], normalize=False)
landmarks2d = DP.vis_pp(vis_dict['landmarks2d'], normalize=False)
landmarks3d = DP.vis_pp(vis_dict['landmarks3d'], normalize=False)
shape_images = DP.vis_pp(vis_dict['shape_images'], normalize=False)
shape_detail_images = DP.vis_pp(vis_dict['shape_detail_images'], normalize=False)