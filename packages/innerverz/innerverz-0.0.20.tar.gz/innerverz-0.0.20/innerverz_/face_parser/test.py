import cv2

from innerverz_package import Data_Process

DP = Data_Process()

image_path = 'sample.png'

"""
        face alignment usage
"""
from innerverz_package import FaceAligner
FA = FaceAligner(align_style='ffhq')

cv2_image = cv2.imread(image_path)
aligned_face, tfm, tfm_inv, lms_5, lms_106, face_bool = FA.get_face(cv2_image)

face_bool, lms_106, lms_5 = FA.detect_lmk(cv2_image)

aligned_face, tfm, tfm_inv = FA.align_face_from_5(cv2_image, lms_5)

"""
        FaceParser usage
"""
from innerverz_package import FaceParser
FP = FaceParser()

ts_aligned_face = DP.image_pp(aligned_face, 512, normalize=True)
label = FP.get_label(ts_aligned_face)
pp_label = DP.vis_pp(label, normalize=False, color=False)
